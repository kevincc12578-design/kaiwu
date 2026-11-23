# -*- coding: utf-8 -*-
"""
开物 v4.0 · 可扩展分类插件与零 API 三模态自动解析器专项端到端验收套件
运行：python -X utf8 tests/verify_parsers_and_categories.py
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import urllib.request
from typing import Any

from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(r"D:\gemini库\开物v3.3")
CASES_DIR = ROOT / "cases"
BASE_URL = "http://127.0.0.1:4340"
SHOT_DIR = pathlib.Path(r"C:\Users\admin\.gemini\antigravity\brain\5014452f-7e5a-4ccd-8b3e-ac833641376b\verify_shots_v4")
TMP_PARSE_OUT = pathlib.Path(r"C:\Users\admin\.gemini\antigravity\brain\5014452f-7e5a-4ccd-8b3e-ac833641376b\scratch\verify_parse_tmp")

FORBIDDEN_UI_TOKENS = ("undefined", "NaN", "null", "不会丢失", "仅供演示", "仅供参考", "仅作示意")


def _opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _get_json(path: str, timeout: float = 15.0) -> dict[str, Any]:
    req = urllib.request.Request(f"{BASE_URL}{path}")
    with _opener().open(req, timeout=timeout) as r:
        assert r.status == 200
        return json.loads(r.read().decode("utf-8"))


def _post_json(path: str, payload: dict[str, Any], timeout: float = 60.0) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with _opener().open(req, timeout=timeout) as r:
        assert r.status == 200
        return json.loads(r.read().decode("utf-8"))


def main() -> None:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    if TMP_PARSE_OUT.exists():
        shutil.rmtree(TMP_PARSE_OUT, ignore_errors=True)
    TMP_PARSE_OUT.mkdir(parents=True, exist_ok=True)

    created_case_ids = ["imp_test_weeksync", "imp_test_axiom", "imp_e2e_weeksync"]
    try:
        # Clean pre-existing leftovers if any
        for cid in created_case_ids:
            shutil.rmtree(CASES_DIR / cid, ignore_errors=True)

        # 1. Health & Categories API & CLI tool
        health = _get_json("/api/health")
        assert health["version"] == "3.4.0" and health["rules_loaded"] == 24 and health["templates_loaded"] == 2
        assert health["categories_loaded"] == 6, f"Expected 6 categories, got {health['categories_loaded']}"
        assert health["local_parsers"] == ["web_url", "image_som", "video_diff"]
        print("[PASS] 1. /api/health reports 6 categories & 3 zero-API local parsers")

        cats_res = _get_json("/api/categories")
        cats = cats_res["categories"]
        core_cnt = sum(1 for c in cats if c["tier"] == "core")
        ext_cnt = sum(1 for c in cats if c["tier"] == "extended")
        assert core_cnt == 3 and ext_cnt == 3, f"Expected 3 core + 3 extended, got {core_cnt}+{ext_cnt}"
        print(f"[PASS] 2. /api/categories returns 3 core + 3 extended plugins: {[c['category_id'] for c in cats]}")

        cli_out = subprocess.check_output(
            [sys.executable, "-X", "utf8", str(ROOT / "backend" / "ai_tools_mcp.py"), "list_categories"],
            cwd=str(ROOT),
            text=True,
            encoding="utf-8",
        )
        cli_json = json.loads(cli_out)
        assert cli_json["status"] == "OK" and cli_json["count"] == 6
        print("[PASS] 3. CLI ai_tools_mcp.py list_categories verified")

        # 2. Live URL parsing (WeekSync -> collab_planner, Axiom -> data_hud)
        res_ws = _post_json(
            "/api/parse/url",
            {
                "url": f"{BASE_URL}/cases/weeksync_paper_web/app/index.html",
                "case_id": "imp_test_weeksync",
                "category": "auto",
            },
        )
        assert res_ws["category_info"]["category_id"] == "collab_planner", (
            f"WeekSync classified as {res_ws['category_info']}"
        )
        b_ws = res_ws["bundle"]
        assert b_ws["gates"]["verdict"] == "PASS" and b_ws["admission_status"] == "PROVISIONAL"
        assert b_ws["category_audit"]["passed_count"] == b_ws["category_audit"]["total_count"]
        assert (CASES_DIR / "imp_test_weeksync" / "frames" / "captured_1440.png").exists()
        print(f"[PASS] 4. URL parser auto-classified WeekSync -> collab_planner (conf={res_ws['classification']['confidence']}) & gates PASS")

        res_ax = _post_json(
            "/api/parse/url",
            {
                "url": f"{BASE_URL}/cases/axiom_hud_web/app/index.html",
                "case_id": "imp_test_axiom",
                "category": "auto",
            },
        )
        assert res_ax["category_info"]["category_id"] == "data_hud", (
            f"Axiom classified as {res_ax['category_info']}"
        )
        assert res_ax["bundle"]["gates"]["verdict"] == "PASS"
        print(f"[PASS] 5. URL parser auto-classified Axiom -> data_hud (conf={res_ax['classification']['confidence']}) & gates PASS")

        # 3. Local Image SoM API (Pillow+NumPy zero-API)
        res_img = _post_json(
            "/api/parse/image",
            {
                "image_path": str(CASES_DIR / "monolog_swiss_poster" / "frames" / "ref_monolog_poster.png"),
                "out_dir": str(TMP_PARSE_OUT / "som_monolog"),
            },
        )
        assert res_img["status"] == "OK" and res_img["box_count"] >= 6
        assert pathlib.Path(res_img["som_image_path"]).exists()
        assert len(res_img["palette"]) >= 4 and "#7" in res_img["agent_handoff"]["asset_slot_marks"]
        print(f"[PASS] 6. Image SoM parser generated {res_img['box_count']} boxes + som_annotated.png + asset_slot_marks={res_img['agent_handoff']['asset_slot_marks']}")

        # 4. Local Video / Frame-Series Diff API (zero ffmpeg/cv2/API)
        res_vid = _post_json(
            "/api/parse/video",
            {
                "source_path": str(CASES_DIR / "code_xr_uiux" / "frames"),
                "case_id": "code_xr_frames_check",
                "out_dir": str(TMP_PARSE_OUT / "vid_codexr"),
            },
        )
        assert res_vid["status"] == "OK" and res_vid["keyframe_count"] >= 3
        assert len(res_vid["segments"]) == res_vid["keyframe_count"]
        assert "SCROLLS_INDEPENDENTLY" in res_vid["inferred_edge_types"]
        print(f"[PASS] 7. Video diff parser extracted {res_vid['keyframe_count']} keyframes & edges={res_vid['inferred_edge_types']}")

        # 5. Playwright Workbench UI E2E: Category optgroups + Category audit card + Import URL modal
        console_errs: list[str] = []
        page_errs: list[str] = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-proxy-server"])
            ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
            page = ctx.new_page()
            page.on("console", lambda m: console_errs.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: page_errs.append(str(e)))

            page.goto(f"{BASE_URL}/?case=axiom_hud_web", wait_until="networkidle")
            page.wait_for_selector("#caseSelect optgroup", state="attached", timeout=10000)
            og_count = page.locator("#caseSelect optgroup").count()
            assert og_count >= 6, f"Expected >=6 optgroups, got {og_count}"
            page.wait_for_function("() => (document.getElementById('catChip')?.innerText || '').includes('HUD')", timeout=8000)
            cat_text = page.locator("#catChip").inner_text()
            assert "HUD" in cat_text and "3/3" in cat_text, f"Unexpected #catChip text: {cat_text}"

            # Switch to Gates tab and inspect category audit card
            page.click("#tabGates")
            page.wait_for_selector(".cat-audit-card", timeout=5000)
            body_text = page.locator("body").inner_text()
            for bad in FORBIDDEN_UI_TOKENS:
                assert bad not in body_text, f"Forbidden token found in workbench: {bad}"
            page.screenshot(path=str(SHOT_DIR / "v4_workbench_cat_rules_1440x900.png"), full_page=False)

            # Test "+ 解析 URL" dialog end-to-end
            page.click("#importBtn")
            page.wait_for_selector("#importDialog[open]", timeout=5000)
            page.fill("#impUrlInput", f"{BASE_URL}/cases/weeksync_paper_web/app/index.html")
            page.fill("#impCaseInput", "imp_e2e_weeksync")
            page.click("#impSubmitBtn")
            page.wait_for_function("() => !document.getElementById('importDialog')?.hasAttribute('open')", timeout=30000)
            page.wait_for_function("() => document.getElementById('caseSelect').value === 'imp_e2e_weeksync'", timeout=10000)

            stage_frame = page.frame_locator("#stageFrame")
            stage_frame.locator('[data-eu-id="eu_L3_imp_hero_stage"]').wait_for(state="visible", timeout=10000)
            page.wait_for_timeout(500)
            page.click("#midTabs .tab[data-tab='tree']")
            page.wait_for_selector('#tree .tn-row[data-eu="eu_L3_imp_hero_stage"]', timeout=5000)
            page.click('#tree .tn-row[data-eu="eu_L3_imp_hero_stage"]')
            stage_frame.locator('[data-eu-id="eu_L3_imp_hero_stage"].kaiwu-eu-highlight').wait_for(state="visible", timeout=5000)

            page.screenshot(path=str(SHOT_DIR / "v4_workbench_imported_url_1440x900.png"), full_page=False)
            browser.close()

        assert not console_errs, f"Console errors: {console_errs}"
        assert not page_errs, f"Page errors: {page_errs}"
        print("[PASS] 8. Workbench Playwright E2E (optgroups + category audit + live URL import + 3-pane linkage) verified with 0 errors")
        print("\nALL V4.0 CATEGORY & ZERO-API PARSER TESTS PASSED.")
    finally:
        for cid in created_case_ids:
            shutil.rmtree(CASES_DIR / cid, ignore_errors=True)
        shutil.rmtree(TMP_PARSE_OUT, ignore_errors=True)


if __name__ == "__main__":
    main()
