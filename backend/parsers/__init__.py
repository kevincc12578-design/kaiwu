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
from parsers.web_url_parser import CASE_FILES_LOCK, CaseConflictError, parse_web_url

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CASES_DIR = PROJECT_ROOT / "cases"


def discover_imported_cases() -> dict[str, dict[str, Any]]:
    """发现并加载通过解析管线落地在 cases/<id>/parsed_case.json 的动态案例。"""
    found: dict[str, dict[str, Any]] = {}
    with CASE_FILES_LOCK:
        for p in sorted(CASES_DIR.glob("*/parsed_case.json")):
            if p.parent.name.startswith("."):
                continue
            try:
                data = load_imported_case(p.parent.name)
            except (OSError, ValueError):
                continue
            if data and data.get("case_id", p.parent.name) == p.parent.name:
                found[p.parent.name] = data
    return found


def _import_file(case_id: str) -> pathlib.Path | None:
    base = CASES_DIR.resolve()
    if not case_id or case_id.startswith(".") or pathlib.Path(case_id).name != case_id:
        return None
    folder = base / case_id
    path = folder / "parsed_case.json"
    if folder.is_symlink() or folder.resolve().parent != base or path.is_symlink():
        return None
    return path


def load_imported_case(case_id: str) -> dict[str, Any] | None:
    with CASE_FILES_LOCK:
        path = _import_file(case_id)
        if path is None or not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Invalid case data: {case_id}")
        return data


def delete_imported_case(case_id: str) -> bool:
    with CASE_FILES_LOCK:
        path = _import_file(case_id)
        if path is None or not path.is_file():
            return False
        shutil.rmtree(path.parent)
        return True


__all__ = [
    "parse_web_url",
    "parse_local_image",
    "parse_local_video",
    "discover_imported_cases",
    "load_imported_case",
    "delete_imported_case",
]
