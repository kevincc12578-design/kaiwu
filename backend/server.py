"""
开物 v3.4 · Kaiwu Adaptive-EU Design Workbench 后端服务 (server.py, 默认端口 4340)
静态挂载：
  - /       -> frontend/ (折光三窗格联动检验台)
  - /cases/ -> cases/    (Code XR 在线可交互网页、A3 视觉展板、关键帧与叠图资产)
REST JSON API：
  - GET  /api/health
  - GET  /api/cases
  - GET  /api/rules
  - GET  /api/case/{case_id}/bundle
  - GET  /api/case/{case_id}/explain/{eu_id}
  - POST /api/case/{case_id}/test_rule_gate
  - POST /api/case/{case_id}/confirm_assumption
  - GET  /api/error_ledger
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
CASES_DIR = PROJECT_ROOT / "cases"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import adaptive_eu_engine as engine  # noqa: E402
import ai_tools_mcp as ai_tools  # noqa: E402
import category_registry as cat_reg  # noqa: E402
import parsers as parsers_mod  # noqa: E402

mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/json", ".json")

SERVER_PORT: int = 4340


def api_health() -> dict[str, Any]:
    cat = engine.get_rules_catalog()
    cats = cat_reg.list_categories()
    return {
        "status": "OK",
        "product": engine.PRODUCT_NAME,
        "version": engine.WORKBENCH_VERSION,
        "port": SERVER_PORT,
        "rules_loaded": cat["total_rules"],
        "templates_loaded": cat["templates_loaded"],
        "categories_loaded": len(cats),
        "local_parsers": ["web_url", "image_som", "video_diff"],
    }


ALL_PUBLISHED_CASES = [
    "code_xr_uiux",
    "code_xr_poster",
    "refract_crm_web",
    "haven_admin_web",
    "knob_hardware_web",
    "nogood_brutal_web",
    "axiom_hud_web",
    "monolog_swiss_poster",
    "weeksync_paper_web",
    "defined_aurora_web",
    "rauno_craft_video",
    "fps60_motion_video",
    "screen_studio_video",
    "resend_dev_web",
    "linear_workspace_web",
    "raycast_cmd_web",
    "amie_collab_web",
    "nothing_dot_web",
    "poolsuite_os_web",
    "daylight_eink_web",
    "family_fluid_web",
]


def api_cases(include_fixtures: bool = False) -> dict[str, Any]:
    cids = list(ALL_PUBLISHED_CASES)
    for imp_cid in parsers_mod.discover_imported_cases().keys():
        if imp_cid not in cids:
            cids.append(imp_cid)
    if include_fixtures:
        cids.append("web_fixture")
    items = [engine.build_case_bundle(cid, persist=False)["case_info"] for cid in cids]
    return {
        "status": "OK",
        "product": engine.PRODUCT_NAME,
        "version": engine.WORKBENCH_VERSION,
        "default_case_id": "code_xr_uiux",
        "categories": cat_reg.list_categories(),
        "cases": items,
    }


def api_categories() -> dict[str, Any]:
    cats = cat_reg.list_categories()
    return {
        "status": "OK",
        "version": engine.WORKBENCH_VERSION,
        "count": len(cats),
        "categories": cats,
    }


def api_rules() -> dict[str, Any]:
    cat = engine.get_rules_catalog()
    cat["mcp_tools"] = ai_tools.get_mcp_tools_schema()
    return cat


def api_error_ledger() -> dict[str, Any]:
    entries = engine.load_error_ledger()
    return {
        "status": "OK",
        "version": engine.WORKBENCH_VERSION,
        "count": len(entries),
        "entries": entries,
    }


class KaiwuHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stdout.write(f"[Kaiwu-v3.4] {self.address_string()} - {fmt % args}\n")
        sys.stdout.flush()

    def _send_json(self, payload: dict[str, Any], status_code: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _send_static(self, base_dir: Path, rel_path: str) -> None:
        clean_rel = rel_path.lstrip("/\\")
        target = (base_dir / clean_rel).resolve()
        base_resolved = base_dir.resolve()
        if not str(target).startswith(str(base_resolved)):
            self._send_json({"status": "ERROR", "message": "Forbidden path"}, 403)
            return
        if target.is_dir():
            target = target / "index.html"
        if not target.exists() or not target.is_file():
            self._send_json({"status": "ERROR", "message": f"Not found: {rel_path}"}, 404)
            return

        ctype, _ = mimetypes.guess_type(str(target))
        if not ctype:
            ctype = "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "application/json", "image/svg+xml"):
            ctype = f"{ctype}; charset=utf-8"

        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        if not raw.strip():
            return {}
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        qs = parse_qs(parsed.query)

        try:
            if path == "/api/health":
                self._send_json(api_health())
                return
            if path == "/api/cases":
                inc = qs.get("include_fixtures", ["0"])[0] == "1"
                self._send_json(api_cases(include_fixtures=inc))
                return
            if path == "/api/categories":
                self._send_json(api_categories())
                return
            if path == "/api/rules":
                self._send_json(api_rules())
                return
            if path == "/api/error_ledger":
                self._send_json(api_error_ledger())
                return

            if path.startswith("/api/case/"):
                parts = [p for p in path.split("/") if p]
                # parts: ['api', 'case', case_id, ...]
                if len(parts) == 4 and parts[3] == "bundle":
                    cid = parts[2]
                    self._send_json(engine.build_case_bundle(cid, persist=False))
                    return
                if len(parts) >= 5 and parts[3] == "explain":
                    cid = parts[2]
                    eu_id = "/".join(parts[4:])
                    self._send_json(engine.explain_eu_node(cid, eu_id))
                    return

            if path.startswith("/api/"):
                self._send_json({"status": "ERROR", "message": f"Unknown API endpoint: {path}"}, 404)
                return

            if path == "/cases" or path.startswith("/cases/"):
                rel = path[len("/cases") :]
                self._send_static(CASES_DIR, rel)
                return

            # 默认静态托管 frontend/
            rel_front = "index.html" if path in ("", "/") else path
            self._send_static(FRONTEND_DIR, rel_front)

        except KeyError as ke:
            self._send_json({"status": "ERROR", "message": str(ke)}, 404)
        except ValueError as ve:
            self._send_json({"status": "ERROR", "message": str(ve)}, 400)
        except Exception as exc:
            traceback.print_exc()
            self._send_json({"status": "ERROR", "message": str(exc)}, 500)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        try:
            body = self._read_json_body()
            if path == "/api/parse/url":
                url = str(body.get("url") or "").strip()
                cid = body.get("case_id")
                cat_ov = body.get("category")
                parsed = parsers_mod.parse_web_url(url=url, case_id=cid, category_override=cat_ov, persist=True)
                bundle = engine.build_case_bundle(parsed["case_id"], persist=True)
                self._send_json(
                    {
                        "status": "OK",
                        "case_id": parsed["case_id"],
                        "classification": parsed["classification"],
                        "category_info": parsed["category_info"],
                        "bundle": bundle,
                    }
                )
                return

            if path == "/api/parse/image":
                img_path = str(body.get("image_path") or "").strip()
                cid = body.get("case_id")
                cat_ov = body.get("category")
                out_dir = body.get("out_dir")
                res = parsers_mod.parse_local_image(image_path=img_path, case_id=cid, category_override=cat_ov, output_dir=out_dir)
                self._send_json(res)
                return

            if path == "/api/parse/video":
                src_path = str(body.get("source_path") or "").strip()
                cid = body.get("case_id")
                max_samples = int(body.get("max_samples") or 12)
                out_dir = body.get("out_dir")
                res = parsers_mod.parse_local_video(source_path=src_path, case_id=cid, max_samples=max_samples, output_dir=out_dir)
                self._send_json(res)
                return

            if path.startswith("/api/case/"):
                parts = [p for p in path.split("/") if p]
                if len(parts) == 4 and parts[3] == "test_rule_gate":
                    cid = parts[2]
                    preset = str(body.get("preset") or "reset")
                    self._send_json(engine.run_counterfactual_sandbox(cid, preset))
                    return

                if len(parts) == 4 and parts[3] == "confirm_assumption":
                    cid = parts[2]
                    action = str(body.get("action") or "confirm")
                    asm_id = str(body.get("assumption_id") or ("ALL" if action in ("confirm_all", "reset") else ""))
                    if action == "confirm_all":
                        asm_id = "ALL"
                    res = ai_tools.manage_assumptions(cid, action=action, assumption_id=asm_id)
                    self._send_json(
                        {
                            "status": "OK",
                            "case_id": cid,
                            "action": action,
                            "assumption_id": asm_id,
                            "admission_status": res["admission_status"],
                            "open_assumptions_count": res["open_assumptions_count"],
                            "assumptions": res["assumptions"],
                            "bundle": res["bundle"],
                        }
                    )
                    return

            self._send_json({"status": "ERROR", "message": f"Unknown POST endpoint: {path}"}, 404)
        except ValueError as ve:
            self._send_json({"status": "ERROR", "message": str(ve)}, 400)
        except Exception as exc:
            traceback.print_exc()
            self._send_json({"status": "ERROR", "message": str(exc)}, 500)


def run_server(host: str = "127.0.0.1", port: int = 4340) -> None:
    global SERVER_PORT
    SERVER_PORT = port
    # 启动时预构建并刷新各落地案例的持久化 inspection_bundle.json 与骨架文件
    for cid in ALL_PUBLISHED_CASES:
        engine.build_case_bundle(cid, persist=True)

    httpd = ThreadingHTTPServer((host, port), KaiwuHTTPRequestHandler)
    print(f"[Kaiwu-v3.4] Server listening at http://{host}:{port}/ (version {engine.WORKBENCH_VERSION})")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="开物 v3.4 Web 服务")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址 (默认 127.0.0.1)")
    parser.add_argument("--port", type=int, default=4340, help="监听端口 (默认 4340)")
    ns = parser.parse_args()
    run_server(host=ns.host, port=ns.port)


if __name__ == "__main__":
    main()
