"""
开物 v4.0 · 录屏 / 帧序列纯本地稳态切片与跨帧 Diff 分析器 (parsers/video_frame_parser.py)
零 ffmpeg / 零 cv2 / 零外部 API：
- 目录输入直接读取帧序列；
- MP4/WebM 视频输入通过内置临时 HTTP 流 + 无头 Chromium <video>/<canvas> 离线均匀抽帧；
- 使用 NumPy 计算稳态关键帧、12×8 空间网格帧差热点与横/纵交互边候选推理，
  并调用 image_local_parser 生成首帧 Set-of-Mark 标号图供 Agent 组装视频 EU 树。
"""
from __future__ import annotations

import base64
import json
import pathlib
import sys
from typing import Any

import numpy as np
from PIL import Image

BACKEND_DIR = pathlib.Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from parsers import image_local_parser  # noqa: E402


def _extract_video_frames_via_browser(
    video_path: pathlib.Path, out_frames_dir: pathlib.Path, max_samples: int = 12,
) -> tuple[float, list[dict[str, Any]]]:
    """Decode only the selected file through Chromium's video and canvas APIs."""
    from playwright.sync_api import Error as BrowserError, sync_playwright

    with sync_playwright() as playwright:
        with playwright.chromium.launch(headless=True, args=["--no-proxy-server"]) as browser:
            page = browser.new_page()
            page.set_content('<input type="file" id="source"><video muted playsinline preload="auto"></video>')
            page.locator("#source").set_input_files(str(video_path.resolve()))
            try:
                result = page.evaluate(
                    """async (maxSamples) => {
                        const video = document.querySelector("video");
                        const source = URL.createObjectURL(document.querySelector("#source").files[0]);
                        const waitFor = (event, start) => new Promise((resolve, reject) => {
                            const finish = (error) => {
                                clearTimeout(timer);
                                video.removeEventListener(event, ready);
                                video.removeEventListener("error", failed);
                                if (error) reject(error);
                                else resolve();
                            };
                            const ready = () => finish();
                            const failed = () => finish(new Error("Video decode failed"));
                            const timer = setTimeout(() => finish(new Error("Video decode timed out")), 8000);
                            video.addEventListener(event, ready);
                            video.addEventListener("error", failed);
                            start();
                        });
                        try {
                            await waitFor("loadeddata", () => { video.src = source; });
                            const duration = video.duration;
                            if (!Number.isFinite(duration) || duration <= 0) {
                                throw new Error("Video has no finite duration");
                            }
                            const canvas = document.createElement("canvas");
                            canvas.width = video.videoWidth;
                            canvas.height = video.videoHeight;
                            const context = canvas.getContext("2d");
                            const last = duration - Math.min(duration / 2, 0.01);
                            const count = Math.min(maxSamples, Math.floor(last * 1000) + 1);
                            const frames = [];
                            for (let i = 0; i < count; i++) {
                                const time = last * i / Math.max(1, count - 1);
                                if (Math.abs(video.currentTime - time) >= 0.0005) {
                                    await waitFor("seeked", () => { video.currentTime = time; });
                                }
                                context.drawImage(video, 0, 0);
                                frames.push({t: Number(time.toFixed(3)), data: canvas.toDataURL("image/png")});
                            }
                            return {duration, frames};
                        } finally {
                            URL.revokeObjectURL(source);
                        }
                    }""",
                    max_samples,
                )
            except BrowserError as error:
                raise ValueError(f"Could not decode video: {video_path.name}") from error

    out_frames_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for index, frame in enumerate(result["frames"], 1):
        path = out_frames_dir / f"frame_{index:03d}.png"
        path.write_bytes(base64.b64decode(frame["data"].split(",", 1)[1]))
        frames.append({"path": path, "t": frame["t"]})
    return result["duration"], frames


def _load_frame_series(source_path: pathlib.Path, out_root: pathlib.Path, max_samples: int) -> tuple[float, list[dict[str, Any]]]:
    if source_path.is_dir():
        exts = {".png", ".jpg", ".jpeg", ".webp"}
        files = sorted([p for p in source_path.iterdir() if p.is_file() and p.suffix.lower() in exts])
        if not files:
            raise ValueError(f"No frame images found in directory: {source_path}")
        dur = round(len(files) * 0.9, 3)
        indices = np.linspace(0, len(files) - 1, min(len(files), max_samples), dtype=int)
        frames = [{"path": files[i], "t": round(i * 0.9, 3)} for i in indices.tolist()]
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
    if type(max_samples) is not int or max_samples < 1:
        raise ValueError("max_samples must be a positive integer")
    src = pathlib.Path(source_path)
    if not source_path or not src.exists():
        raise FileNotFoundError(f"Source path not found: {source_path}")

    if output_dir:
        out_root = pathlib.Path(output_dir)
    else:
        output_base = (PROJECT_ROOT / "cases" / "_video_diff_outputs").resolve()
        out_root = (output_base / (case_id or src.stem)).resolve()
        if out_root.parent != output_base:
            raise ValueError("The video case ID must identify a single output directory")

    duration_sec, frames = _load_frame_series(src, out_root, max_samples=max_samples)

    # Load resized arrays for fast comparison
    arrays: list[np.ndarray] = []
    orig_res = {"w": 1440, "h": 900}
    for i, item in enumerate(frames):
        try:
            with Image.open(item["path"]) as source:
                width, height = source.size
                if i == 0:
                    orig_res = {"w": width, "h": height}
                if width * orig_res["h"] != height * orig_res["w"]:
                    raise ValueError("Frame sequence images must have the same aspect ratio")
                target_size = (360, max(120, int(360 * orig_res["h"] / orig_res["w"])))
                small = source.convert("RGB").resize(target_size, Image.Resampling.BILINEAR)
        except (OSError, Image.DecompressionBombError) as error:
            raise ValueError(f"Could not decode frame: {item['path'].name}") from error
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
