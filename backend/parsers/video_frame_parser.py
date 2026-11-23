"""
开物 v4.0 · 录屏 / 帧序列纯本地稳态切片与跨帧 Diff 分析器 (parsers/video_frame_parser.py)
零 ffmpeg / 零 cv2 / 零外部 API：
- 目录输入直接读取帧序列；
- MP4/WebM 视频输入通过内置临时 HTTP 流 + 无头 Chromium <video>/<canvas> 离线均匀抽帧；
- 使用 NumPy 计算稳态关键帧、12×8 空间网格帧差热点与横/纵交互边候选推理，
  并调用 image_local_parser 生成首帧 Set-of-Mark 标号图供 Agent 组装视频 EU 树。
"""
from __future__ import annotations

import functools
import http.server
import json
import pathlib
import socketserver
import sys
import threading
from typing import Any

import numpy as np
from PIL import Image

BACKEND_DIR = pathlib.Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from parsers import image_local_parser  # noqa: E402


def _extract_video_frames_via_browser(video_path: pathlib.Path, out_frames_dir: pathlib.Path, max_samples: int = 12) -> tuple[float, list[dict[str, Any]]]:
    """无需 ffmpeg：借由本地一次性 HTTP 静态服务 + Playwright <video>+<canvas> 离线抽帧。"""
    from playwright.sync_api import sync_playwright

    out_frames_dir.mkdir(parents=True, exist_ok=True)
    serve_dir = str(video_path.parent)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=serve_dir)

    class _QuietTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    with _QuietTCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            video_url = f"http://127.0.0.1:{port}/{video_path.name}"
            html = f"""<!doctype html><html><body>
            <video id="v" src="{video_url}" crossorigin="anonymous" muted playsinline preload="auto"></video>
            <script>
              window.__sampleFrames = async (maxSamples) => {{
                const v = document.getElementById('v');
                await new Promise((res, rej) => {{
                  if (v.readyState >= 1) return res();
                  v.onloadedmetadata = res;
                  v.onerror = () => rej('video load error');
                }});
                const dur = v.duration || 1.0;
                const w = v.videoWidth || 1280;
                const h = v.videoHeight || 720;
                const c = document.createElement('canvas');
                c.width = w; c.height = h;
                const ctx = c.getContext('2d');
                const frames = [];
                const n = Math.max(2, maxSamples);
                for (let i = 0; i < n; i++) {{
                  const ts = Math.min(dur - 0.01, (dur * i) / Math.max(1, n - 1));
                  v.currentTime = Math.max(0, ts);
                  await new Promise((res) => {{ v.onseeked = res; }});
                  ctx.drawImage(v, 0, 0, w, h);
                  frames.push({{ t: Number(ts.toFixed(3)), data_url: c.toDataURL('image/png') }});
                }}
                return {{ duration: Number(dur.toFixed(3)), w, h, frames }};
              }};
            </script></body></html>"""

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=["--no-proxy-server"])
                page = browser.new_page()
                page.set_content(html)
                res = page.evaluate(f"window.__sampleFrames({int(max_samples)})")
                browser.close()
        finally:
            httpd.shutdown()

    import base64

    saved: list[dict[str, Any]] = []
    for idx, f in enumerate(res["frames"], start=1):
        b64 = f["data_url"].split(",", 1)[1]
        fp = out_frames_dir / f"frame_{idx:03d}.png"
        fp.write_bytes(base64.b64decode(b64))
        saved.append({"path": fp, "t": float(f["t"])})
    return float(res["duration"]), saved


def _load_frame_series(source_path: pathlib.Path, out_root: pathlib.Path, max_samples: int) -> tuple[float, list[dict[str, Any]]]:
    if source_path.is_dir():
        exts = {".png", ".jpg", ".jpeg", ".webp"}
        files = sorted([p for p in source_path.iterdir() if p.is_file() and p.suffix.lower() in exts])
        if not files:
            raise ValueError(f"No frame images found in directory: {source_path}")
        if len(files) > max_samples:
            idxs = np.linspace(0, len(files) - 1, max_samples, dtype=int)
            files = [files[int(i)] for i in idxs]
        dur = round(float(len(files)) * 0.9, 3)
        frames = [{"path": fp, "t": round((i / max(1, len(files) - 1)) * dur, 3) if len(files) > 1 else 0.0} for i, fp in enumerate(files)]
        return dur, frames

    if source_path.is_file() and source_path.suffix.lower() in {".mp4", ".webm", ".mov"}:
        return _extract_video_frames_via_browser(source_path, out_root / "sampled_frames", max_samples=max_samples)

    raise ValueError(f"Unsupported video/frame source: {source_path}")


def _grid_diff(img_a: np.ndarray, img_b: np.ndarray, cols: int = 12, rows: int = 8) -> dict[str, Any]:
    h, w, _ = img_a.shape
    diff = np.mean(np.abs(img_a.astype(np.float32) - img_b.astype(np.float32)), axis=2) / 255.0
    mad = float(np.mean(diff))
    cw = max(1, w // cols)
    rh = max(1, h // rows)
    changed_cells: list[dict[str, Any]] = []
    static_cols = set(range(cols))

    for r in range(rows):
        for c in range(cols):
            patch = diff[r * rh : (r + 1) * rh, c * cw : (c + 1) * cw]
            score = float(np.mean(patch)) if patch.size else 0.0
            if score >= 0.045:
                changed_cells.append({"col": c, "row": r, "score": round(score, 3)})
                static_cols.discard(c)

    if changed_cells:
        min_c = min(x["col"] for x in changed_cells)
        max_c = max(x["col"] for x in changed_cells)
        min_r = min(x["row"] for x in changed_cells)
        max_r = max(x["row"] for x in changed_cells)
        changed_norm_bbox = [
            round(min_c / cols, 3),
            round(min_r / rows, 3),
            round((max_c - min_c + 1) / cols, 3),
            round((max_r - min_r + 1) / rows, 3),
        ]
    else:
        changed_norm_bbox = [0.0, 0.0, 0.0, 0.0]

    # Heuristic edge inference from spatial diff pattern
    edge_hints: list[str] = []
    left_static = (0 in static_cols) and len(changed_cells) >= 10
    if left_static:
        edge_hints.append("SCROLLS_INDEPENDENTLY")
    if len(changed_cells) >= 18:
        edge_hints.append("TRIGGERS_STATE")
    elif 2 <= len(changed_cells) <= 10:
        edge_hints.append("MODULATES_NEIGHBOR")
    if not edge_hints and mad >= 0.02:
        edge_hints.append("TRIGGERS_STATE")

    return {
        "mad": round(mad, 4),
        "changed_cell_count": len(changed_cells),
        "changed_norm_bbox": changed_norm_bbox,
        "left_rail_static": left_static,
        "edge_hints": edge_hints,
    }


def parse_local_video(
    source_path: str,
    case_id: str | None = None,
    max_samples: int = 12,
    output_dir: str | None = None,
) -> dict[str, Any]:
    """
    纯本地提取录屏/帧序列稳态分段、跨帧空间差异热点、交互边推理建议，
    并生成首张关键帧的 Set-of-Mark 标号图。
    """
    src = pathlib.Path(source_path)
    if not src.exists():
        raise FileNotFoundError(f"Source path not found: {source_path}")

    out_root = pathlib.Path(output_dir) if output_dir else (PROJECT_ROOT / "cases" / "_video_diff_outputs" / (case_id or src.stem))
    out_root.mkdir(parents=True, exist_ok=True)

    duration_sec, frames = _load_frame_series(src, out_root, max_samples=max_samples)

    # Load resized arrays for fast comparison
    arrays: list[np.ndarray] = []
    orig_res = {"w": 1440, "h": 900}
    for i, item in enumerate(frames):
        im = Image.open(item["path"]).convert("RGB")
        if i == 0:
            orig_res = {"w": im.size[0], "h": im.size[1]}
        small = im.resize((360, max(120, int(360 * im.size[1] / max(1, im.size[0])))), Image.Resampling.BILINEAR)
        arrays.append(np.array(small))

    # Segment contiguous steady keyframes
    keyframes: list[dict[str, Any]] = [{"frame_index": 0, "t": frames[0]["t"], "path": str(frames[0]["path"].resolve())}]
    transitions: list[dict[str, Any]] = []
    candidate_edges: set[str] = set()

    last_kf_idx = 0
    for idx in range(1, len(frames)):
        diff_info = _grid_diff(arrays[last_kf_idx], arrays[idx])
        if diff_info["mad"] >= 0.015 or idx == len(frames) - 1:
            transitions.append(
                {
                    "from_frame": last_kf_idx,
                    "to_frame": idx,
                    "t0": frames[last_kf_idx]["t"],
                    "t1": frames[idx]["t"],
                    **diff_info,
                }
            )
            for h in diff_info["edge_hints"]:
                candidate_edges.add(h)
            if diff_info["mad"] >= 0.015:
                keyframes.append({"frame_index": idx, "t": frames[idx]["t"], "path": str(frames[idx]["path"].resolve())})
                last_kf_idx = idx

    # Build contiguous timeline segments covering [0, duration_sec]
    segments: list[dict[str, Any]] = []
    for i, kf in enumerate(keyframes):
        t0 = 0.0 if i == 0 else kf["t"]
        t1 = duration_sec if i == len(keyframes) - 1 else keyframes[i + 1]["t"]
        if t1 <= t0:
            t1 = round(t0 + max(0.3, duration_sec / max(1, len(keyframes))), 3)
        segments.append(
            {
                "segment_id": f"seg_vid_{i+1:02d}",
                "index": i + 1,
                "t0": round(t0, 3),
                "t1": round(t1, 3),
                "keyframe_path": kf["path"],
            }
        )

    # Run SoM parser on first keyframe so Agent also gets numbered regions & category
    first_som = image_local_parser.parse_local_image(
        image_path=str(frames[0]["path"]),
        case_id=case_id or src.stem,
        output_dir=str(out_root),
    )

    result = {
        "status": "OK",
        "tool": "inspect_video_diff",
        "source_path": str(src.resolve()),
        "duration_sec": duration_sec,
        "resolution": orig_res,
        "sampled_count": len(frames),
        "keyframe_count": len(keyframes),
        "keyframes": keyframes,
        "segments": segments,
        "transitions": transitions,
        "inferred_edge_types": sorted(candidate_edges) or ["TRIGGERS_STATE"],
        "first_frame_som": {
            "som_image_path": first_som["som_image_path"],
            "box_count": first_som["box_count"],
            "classification": first_som["classification"],
            "palette": first_som["palette"],
        },
        "summary_path": str((out_root / "video_diff_summary.json").resolve()),
    }
    (out_root / "video_diff_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
