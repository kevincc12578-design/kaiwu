"""Focused regressions for parsing, rule evaluation and case state."""
from __future__ import annotations

import json
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from unittest.mock import patch
from urllib.error import HTTPError

from PIL import Image

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
    assert (case_dir / "app/index.html").read_bytes() != original_app


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


def verify_regressions(run: VerificationRun) -> int:
    sys.path.insert(0, str(run.root / "backend"))
    checks = (
        _reject_non_object_json, _reject_invalid_case_mutation, _report_image_input_errors,
        _reject_unavailable_page, _round_trip_import_update, _keep_frame_timeline_when_sampling,
        _reject_invalid_video_inputs, _decode_direct_video,
        _block_rules_without_handlers, _keep_committed_state_after_write_failure,
        _persist_concurrent_confirmations,
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
