"""
开物 v4.0 · 本地三模态自动解析引擎 (backend/parsers/__init__.py)
"""
from __future__ import annotations

import json
import pathlib
import shutil
from typing import Any

from parsers.image_local_parser import parse_local_image
from parsers.video_frame_parser import parse_local_video
from parsers.web_url_parser import parse_web_url

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CASES_DIR = PROJECT_ROOT / "cases"


def discover_imported_cases() -> dict[str, dict[str, Any]]:
    """发现并加载通过解析管线落地在 cases/<id>/parsed_case.json 的动态案例。"""
    found: dict[str, dict[str, Any]] = {}
    if not CASES_DIR.exists():
        return found
    for p in sorted(CASES_DIR.glob("*/parsed_case.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            cid = str(data.get("case_id") or p.parent.name)
            found[cid] = data
        except Exception:
            continue
    return found


def load_imported_case(case_id: str) -> dict[str, Any] | None:
    p = CASES_DIR / case_id / "parsed_case.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def delete_imported_case(case_id: str) -> bool:
    p = CASES_DIR / case_id / "parsed_case.json"
    if not p.exists():
        return False
    shutil.rmtree(CASES_DIR / case_id, ignore_errors=True)
    return True


__all__ = [
    "parse_web_url",
    "parse_local_image",
    "parse_local_video",
    "discover_imported_cases",
    "load_imported_case",
    "delete_imported_case",
]
