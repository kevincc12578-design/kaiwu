"""Focused regressions for parsing, rule evaluation and case state."""
from __future__ import annotations

import json
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Barrier, Event, Thread
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import ProxyHandler, build_opener

from PIL import Image
import yaml

from verification_env import VerificationRun


def _expect_http_error(operation, status: int, message: str) -> None:
    try:
        operation()
    except HTTPError as error:
        with error:
            payload = json.load(error)
        assert error.code == status, (error.code, payload)
        assert payload["status"] == "ERROR", payload
        assert message.casefold() in payload["message"].casefold(), payload
    else:
        raise AssertionError(f"Expected HTTP {status} for {message}")


def _reject_non_object_json(run: VerificationRun) -> None:
    _expect_http_error(lambda: run.post_json("/api/parse/url", []), 400, "JSON")


def _reject_invalid_case_mutation(run: VerificationRun) -> None:
    _expect_http_error(lambda: run.get_json("/api/case/audit_absent_case/bundle"), 404, "case")
    _expect_http_error(
        lambda: run.post_json("/api/case/audit_absent_case/confirm_assumption", {"action": "confirm_all"}),
        404, "case",
    )
    assert not (run.root / "cases/audit_absent_case").exists()
    _expect_http_error(
        lambda: run.post_json("/api/case/code_xr_uiux/confirm_assumption", {"action": "unrecognized"}),
        400, "action",
    )
    _expect_http_error(
        lambda: run.post_json("/api/case/code_xr_uiux/confirm_assumption", {"assumption_id": "unknown"}),
        400, "assumption",
    )


def _report_image_input_errors(run: VerificationRun) -> None:
    absent = run.root / "absent.png"
    invalid = run.root / "invalid.png"
    invalid.write_bytes(b"not an image")
    _expect_http_error(
        lambda: run.post_json("/api/parse/image", {"image_path": str(absent)}), 404, "image",
    )
    _expect_http_error(
        lambda: run.post_json("/api/parse/image", {"image_path": str(invalid)}), 400, "image",
    )


def _reject_unavailable_page(run: VerificationRun) -> None:
    case_id = "audit_unavailable_page"
    _expect_http_error(
        lambda: run.post_json("/api/parse/url", {
            "case_id": case_id,
            "url": f"{run.base_url}/cases/absent_audit_page.html",
        }), 400, "404",
    )
    assert not (run.root / "cases" / case_id).exists()


def _round_trip_import_update(run: VerificationRun) -> None:
    import adaptive_eu_engine as engine
    import ai_tools_mcp
    from parsers import web_url_parser

    case_id = "audit_import_replacement"
    original_url = f"{run.base_url}/cases/weeksync_paper_web/app/index.html"
    replacement_url = f"{run.base_url}/cases/axiom_hud_web/app/index.html"
    imported = run.post_json("/api/parse/url", {"case_id": case_id, "url": original_url})
    assert imported["category_info"]["category_id"] == "collab_planner"
    case_dir = run.root / "cases" / case_id
    note = case_dir / "audit_notes.txt"
    note.write_text("local case notes", encoding="utf-8")
    signed = run.post_json(f"/api/case/{case_id}/confirm_assumption", {"action": "confirm_all"})
    assert signed["admission_status"] == "RELEASE_READY"
    retried = run.post_json("/api/parse/url", {"case_id": case_id, "url": original_url})
    assert retried["bundle"]["admission_status"] == "RELEASE_READY"
    original = (case_dir / "parsed_case.json").read_bytes()
    original_app = (case_dir / "app/index.html").read_bytes()
    build_files = web_url_parser._build_imported_app_files

    def fail_after_writing(**options):
        build_files(**options)
        raise OSError("simulated case output error")

    with patch.object(web_url_parser, "_build_imported_app_files", side_effect=fail_after_writing):
        try:
            web_url_parser.parse_web_url(replacement_url, case_id=case_id)
        except OSError as error:
            assert "simulated case output error" in str(error), error
        else:
            raise AssertionError("A partial import was reported as successful")

    assert (case_dir / "parsed_case.json").read_bytes() == original, "the original import metadata changed"
    assert (case_dir / "app/index.html").read_bytes() == original_app, "the original stage changed"
    with patch.object(engine, "build_case_bundle", side_effect=OSError("simulated bundle write error")):
        try:
            ai_tools_mcp.import_web_case(replacement_url, case_id)
        except OSError as error:
            assert "simulated bundle write error" in str(error), error
        else:
            raise AssertionError("A failed bundle publication was reported as successful")
    assert (case_dir / "parsed_case.json").read_bytes() == original
    assert (case_dir / "app/index.html").read_bytes() == original_app
    replacement = run.post_json("/api/parse/url", {"case_id": case_id, "url": replacement_url})
    assert replacement["category_info"]["category_id"] == "data_hud"
    saved = run.get_json(f"/api/case/{case_id}/bundle")
    assert saved["case_info"]["category_id"] == "data_hud"
    assert saved["admission_status"] == "PROVISIONAL"
    assert (case_dir / "app/index.html").read_bytes() != original_app
    assert note.read_text(encoding="utf-8") == "local case notes"


def _static_assets_wait_for_case_publication(run: VerificationRun) -> None:
    import server
    from parsers import CASE_FILES_LOCK

    path = run.root / "cases" / "audit_publication.txt"
    path.write_text("under construction", encoding="utf-8")
    started = Event()

    class ObservedHandler(server.KaiwuHTTPRequestHandler):
        def _send_static(self, base_dir, rel_path):
            started.set()
            super()._send_static(base_dir, rel_path)

    with ThreadingHTTPServer(("127.0.0.1", 0), ObservedHandler) as httpd:
        thread = Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        opener = build_opener(ProxyHandler({}))

        def fetch():
            with opener.open(f"http://127.0.0.1:{httpd.server_port}/cases/audit_publication.txt", timeout=5) as response:
                return response.read()

        try:
            with ThreadPoolExecutor(max_workers=1) as pool:
                with CASE_FILES_LOCK:
                    pending = pool.submit(fetch)
                    assert started.wait(timeout=5), "the static request did not reach the handler"
                    try:
                        pending.result(timeout=0.35)
                    except TimeoutError:
                        pass
                    path.write_text("published", encoding="utf-8")
                assert pending.result(timeout=5) == b"published"
        finally:
            httpd.shutdown()
            thread.join(timeout=5)


def _keep_frame_timeline_when_sampling(run: VerificationRun) -> None:
    from parsers.video_frame_parser import parse_local_video

    frames = run.root / "audit_frames"
    frames.mkdir()
    for index, (color, size) in enumerate((("black", (96, 64)), ("red", (192, 128)), ("white", (96, 64)))):
        with Image.new("RGB", size, color) as image:
            image.save(frames / f"frame_{index}.png")

    result = parse_local_video(str(frames), max_samples=2, output_dir=str(run.root / "audit_video"))
    assert result["duration_sec"] == 2.7, result["duration_sec"]
    assert result["sampled_count"] == 2, result["sampled_count"]
    assert result["segments"][-1]["t1"] == 2.7, result["segments"]

    one_frame = parse_local_video(str(frames), max_samples=1, output_dir=str(run.root / "audit_one_frame"))
    assert one_frame["duration_sec"] == 2.7 and one_frame["keyframe_count"] == 1, one_frame
    assert one_frame["segments"][0]["t0"] == 0 and one_frame["segments"][0]["t1"] == 2.7, one_frame


def _reject_invalid_video_inputs(run: VerificationRun) -> None:
    from parsers.video_frame_parser import parse_local_video

    frames = run.root / "audit_mixed_frames"
    frames.mkdir()
    output = str(run.root / "audit_mixed_output")
    _expect_http_error(
        lambda: run.post_json("/api/parse/video", {"source_path": str(frames)}), 400, "frame",
    )
    for index, size in enumerate(((96, 64), (64, 96))):
        with Image.new("RGB", size, "black") as image:
            image.save(frames / f"frame_{index}.png")

    _expect_http_error(
        lambda: run.post_json("/api/parse/video", {"source_path": str(frames), "max_samples": 0}),
        400, "max_samples",
    )
    try:
        parse_local_video(str(frames), output_dir=output)
    except ValueError as error:
        assert "aspect ratio" in str(error), str(error)
    else:
        raise AssertionError("Mixed aspect ratios should have an explicit error")


def _decode_direct_video(run: VerificationRun) -> None:
    fixture = Path(__file__).resolve().parent / "fixtures" / "kaiwu-motion-sample.webm"
    clip = run.root / "motion sample.webm"
    shutil.copyfile(fixture, clip)
    result = run.post_json("/api/parse/video", {
        "source_path": str(clip), "max_samples": 3, "out_dir": str(run.root / "audit_direct_video"),
    }, timeout=15)
    assert result["sampled_count"] == 3, result["sampled_count"]
    assert 1.55 <= result["duration_sec"] <= 1.65, result["duration_sec"]
    assert result["segments"][0]["t0"] == 0 and result["segments"][-1]["t1"] == 1.6
    assert all(Path(frame["path"]).is_file() for frame in result["keyframes"])


def _block_rules_without_handlers(run: VerificationRun) -> None:
    import adaptive_eu_engine as engine

    with patch.dict(engine.CHECK_DISPATCH):
        engine.CHECK_DISPATCH.pop("check_pv01_timeline_coverage")
        bundle = engine.build_case_bundle("code_xr_uiux")
    assert bundle["admission_status"] == "BLOCKED", bundle["admission_status"]
    assert bundle["gates"]["violated_rule_id"] == "PV-01", bundle["gates"]["attribution"]
    assert "check_pv01_timeline_coverage" in bundle["gates"]["attribution"]


def _ignore_unlinked_stage_scripts(run: VerificationRun) -> None:
    import adaptive_eu_engine as engine

    stage = run.root / "cases" / "code_xr_uiux" / "app" / "index.html"
    original = stage.read_bytes()
    markup, removed = re.subn(rb'<script\b[^>]*\bsrc=["\'](?:\./)?app\.js["\'][^>]*>\s*</script>', b"", original)
    assert removed == 1, "the original stage should load app.js"
    try:
        stage.write_bytes(markup)
        result = engine.build_case_bundle("code_xr_uiux")
        assert result["admission_status"] == "BLOCKED", result["admission_status"]
        assert "eu_L3_sprint_hero" in result["readback"]["missing_trace_ids"]
        assert not any(item["passed"] for item in result["readback"]["interactions"])
    finally:
        stage.write_bytes(original)


def _keep_committed_state_after_write_failure(run: VerificationRun) -> None:
    import adaptive_eu_engine as engine

    case = "code_xr_uiux"
    before = engine.update_case_assumptions(case, "ALL", "reset")
    state_path = run.root / "cases" / case / "assumptions_state.json"
    original = state_path.read_bytes()
    write_text = Path.write_text
    replace = Path.replace

    def guarded_write(path, *args, **kwargs):
        if path == state_path:
            raise OSError("simulated state write error")
        return write_text(path, *args, **kwargs)

    def guarded_replace(path, target):
        if target == state_path:
            raise OSError("simulated state write error")
        return replace(path, target)

    with patch.object(Path, "write_text", guarded_write), patch.object(Path, "replace", guarded_replace):
        try:
            engine.update_case_assumptions(case, before[0]["assumption_id"], "confirm")
        except OSError as error:
            assert "simulated state write error" in str(error), error
        else:
            raise AssertionError("A failed state publication was reported as successful")

    assert engine.get_case_assumptions(case) == before, "failed writes must preserve in-memory state"
    assert state_path.read_bytes() == original, "failed writes must preserve persisted state"


def _persist_concurrent_confirmations(run: VerificationRun) -> None:
    import adaptive_eu_engine as engine

    case = "code_xr_uiux"
    before = engine.update_case_assumptions(case, "ALL", "reset")
    requested = [item["assumption_id"] for item in before[:2]]
    start = Barrier(2)

    def confirm(assumption_id):
        start.wait(timeout=5)
        engine.update_case_assumptions(case, assumption_id, "confirm")

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(confirm, requested))

    state = json.loads((run.root / "cases" / case / "assumptions_state.json").read_text(encoding="utf-8"))
    assert [state[aid]["status"] for aid in requested] == ["confirmed", "confirmed"], state
    engine.update_case_assumptions(case, "ALL", "reset")


def _rollback_assumptions_if_bundle_write_fails(run: VerificationRun) -> None:
    import adaptive_eu_engine as engine
    import ai_tools_mcp

    case_id = "code_xr_uiux"
    before = ai_tools_mcp.manage_assumptions(case_id, "reset", "ALL")
    case_dir = run.root / "cases" / case_id
    paths = [case_dir / "assumptions_state.json", case_dir / "inspection_bundle.json"]
    saved = [path.read_bytes() for path in paths]
    write_json = engine._write_json_atomically

    def fail_bundle_write(path, data):
        if path.name == "inspection_bundle.json":
            raise OSError("simulated bundle write error")
        write_json(path, data)

    with patch.object(engine, "_write_json_atomically", side_effect=fail_bundle_write):
        try:
            ai_tools_mcp.manage_assumptions(case_id, "confirm_all", "ALL")
        except OSError as error:
            assert "simulated bundle write error" in str(error), error
        else:
            raise AssertionError("A failed bundle write was reported as successful")
    assert [path.read_bytes() for path in paths] == saved
    assert engine.get_case_assumptions(case_id) == before["assumptions"]


def _case_summaries_track_state_and_category_changes(run: VerificationRun) -> None:
    case_id = "code_xr_poster"

    def summary():
        return next(item for item in run.get_json("/api/cases")["cases"] if item["case_id"] == case_id)

    case_url = f"/api/case/{case_id}"
    details = run.get_json(f"{case_url}/bundle")
    assert summary() == details["case_info"]
    mutation = run.post_json(f"{case_url}/confirm_assumption", {"action": "confirm_all"})
    assert mutation["admission_status"] == "RELEASE_READY"
    assert summary() == mutation["bundle"]["case_info"]
    run.post_json(f"{case_url}/confirm_assumption", {"action": "reset", "assumption_id": "ALL"})
    assert summary()["admission_status"] == "PROVISIONAL"

    category_path = run.root / "categories" / f"{details['case_info']['category_id']}.yaml"
    original = category_path.read_bytes()
    category = yaml.safe_load(original)
    category["name"] = "Local audit category"
    try:
        category_path.write_text(yaml.safe_dump(category, allow_unicode=True), encoding="utf-8")
        assert summary()["category_name"] == "Local audit category"
    finally:
        category_path.write_bytes(original)


def verify_regressions(run: VerificationRun) -> int:
    sys.path.insert(0, str(run.root / "backend"))
    checks = (
        _reject_non_object_json, _reject_invalid_case_mutation, _report_image_input_errors,
        _reject_unavailable_page, _round_trip_import_update, _static_assets_wait_for_case_publication,
        _keep_frame_timeline_when_sampling,
        _reject_invalid_video_inputs, _decode_direct_video,
        _block_rules_without_handlers, _ignore_unlinked_stage_scripts,
        _keep_committed_state_after_write_failure, _persist_concurrent_confirmations,
        _rollback_assumptions_if_bundle_write_fails, _case_summaries_track_state_and_category_changes,
    )
    failures = []
    for check in checks:
        try:
            check(run)
            print(f"[PASS] {check.__name__}")
        except Exception as error:
            message = f"{check.__name__}: {type(error).__name__}: {error}"
            failures.append(message)
            print(f"[FAIL] {message}")
    if failures:
        raise AssertionError("\n".join(failures))
    return len(checks)
