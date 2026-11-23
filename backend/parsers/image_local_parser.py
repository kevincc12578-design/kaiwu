"""
开物 v4.0 · 静图纯本地 CV 测绘 + Set-of-Mark (SoM) 标号图生成器 (parsers/image_local_parser.py)
零外部 API / 零 cv2：仅使用 Pillow + NumPy 完成主色聚类、双层区域分割、对比度采样与标号图输出，
供调用 Agent 看图归组 L0~L5 EU 树与区分 ui_dom / asset_slot。
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
from collections import deque
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BACKEND_DIR = pathlib.Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import category_registry as cat_reg  # noqa: E402


def _rgb_tuple_to_hex(rgb: tuple[int, int, int] | np.ndarray) -> str:
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    return f"#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}{max(0, min(255, b)):02x}"


def _contrast(rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> float:
    def _lin(c: int) -> float:
        x = c / 255.0
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4

    l1 = 0.2126 * _lin(rgb1[0]) + 0.7152 * _lin(rgb1[1]) + 0.0722 * _lin(rgb1[2])
    l2 = 0.2126 * _lin(rgb2[0]) + 0.7152 * _lin(rgb2[1]) + 0.0722 * _lin(rgb2[2])
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)


def _kmeans_palette(arr: np.ndarray, k: int = 6, iters: int = 10) -> list[dict[str, Any]]:
    h, w, _ = arr.shape
    pixels = arr.reshape(-1, 3).astype(np.float32)
    if len(pixels) > 12000:
        step = max(1, len(pixels) // 12000)
        pixels = pixels[::step]

    rng = np.random.default_rng(42)
    idx = rng.choice(len(pixels), size=min(k, len(pixels)), replace=False)
    centers = pixels[idx].copy()

    labels = np.zeros(len(pixels), dtype=np.int32)
    for _ in range(iters):
        dists = np.linalg.norm(pixels[:, None, :] - centers[None, :, :], axis=2)
        labels = np.argmin(dists, axis=1)
        for j in range(len(centers)):
            pts = pixels[labels == j]
            if len(pts) > 0:
                centers[j] = pts.mean(axis=0)

    total = float(len(pixels))
    out: list[dict[str, Any]] = []
    for j in range(len(centers)):
        cnt = int((labels == j).sum())
        if cnt == 0:
            continue
        c_rgb = tuple(int(round(v)) for v in centers[j])
        out.append(
            {
                "hex": _rgb_tuple_to_hex(c_rgb),
                "rgb": list(c_rgb),
                "ratio": round(cnt / total, 3),
                "luminance": round((0.2126 * c_rgb[0] + 0.7152 * c_rgb[1] + 0.0722 * c_rgb[2]) / 255.0, 3),
            }
        )
    out.sort(key=lambda item: item["ratio"], reverse=True)
    return out


def _dilate_mask(mask: np.ndarray, radius_x: int = 2, radius_y: int = 2) -> np.ndarray:
    h, w = mask.shape
    out = mask.copy()
    for dy in range(-radius_y, radius_y + 1):
        for dx in range(-radius_x, radius_x + 1):
            if dx == 0 and dy == 0:
                continue
            src_y0 = max(0, -dy)
            src_y1 = min(h, h - dy)
            src_x0 = max(0, -dx)
            src_x1 = min(w, w - dx)
            dst_y0 = max(0, dy)
            dst_y1 = min(h, h + dy)
            dst_x0 = max(0, dx)
            dst_x1 = min(w, w + dx)
            out[dst_y0:dst_y1, dst_x0:dst_x1] |= mask[src_y0:src_y1, src_x0:src_x1]
    return out


def _extract_components(mask: np.ndarray, min_pixels: int = 45) -> list[tuple[int, int, int, int]]:
    h, w = mask.shape
    visited = np.zeros((h, w), dtype=bool)
    boxes: list[tuple[int, int, int, int]] = []
    ys, xs = np.where(mask)
    for sy, sx in zip(ys.tolist(), xs.tolist()):
        if visited[sy, sx]:
            continue
        q: deque[tuple[int, int]] = deque([(sy, sx)])
        visited[sy, sx] = True
        min_x = max_x = sx
        min_y = max_y = sy
        cnt = 0
        while q:
            cy, cx = q.popleft()
            cnt += 1
            if cx < min_x:
                min_x = cx
            if cx > max_x:
                max_x = cx
            if cy < min_y:
                min_y = cy
            if cy > max_y:
                max_y = cy
            for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                    visited[ny, nx] = True
                    q.append((ny, nx))
        if cnt >= min_pixels:
            boxes.append((min_x, min_y, max_x - min_x + 1, max_y - min_y + 1))
    return boxes


def _iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    ax1, ay1, aw, ah = a
    bx1, by1, bw, bh = b
    ax2, ay2 = ax1 + aw, ay1 + ah
    bx2, by2 = bx1 + bw, by1 + bh
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0
    inter = (ix2 - ix1) * (iy2 - iy1)
    union = aw * ah + bw * bh - inter
    return inter / max(1, union)


def parse_local_image(
    image_path: str,
    case_id: str | None = None,
    category_override: str | None = None,
    output_dir: str | None = None,
) -> dict[str, Any]:
    """
    对静图执行纯本地 Pillow + NumPy 视觉测绘，输出精确原子框列表、主色色板、
    Set-of-Mark 标号图 (som_annotated.png)、自动品类判定与 Agent 移交清单。
    """
    if category_override is not None and not isinstance(category_override, str):
        raise ValueError("category must be a string")
    src_path = pathlib.Path(image_path)
    if not src_path.is_file():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        with Image.open(src_path) as source:
            img = source.convert("RGB")
    except (OSError, Image.DecompressionBombError) as error:
        raise ValueError(f"Could not decode image: {src_path.name}") from error
    orig_w, orig_h = img.size

    # Palette extraction
    small_pal = img.resize((160, max(60, int(160 * orig_h / max(1, orig_w)))), Image.Resampling.BILINEAR)
    palette = _kmeans_palette(np.array(small_pal), k=6)
    dom_bg_rgb = tuple(int(v) for v in palette[0]["rgb"]) if palette else (20, 20, 20)

    # Border background median for cleaner foreground isolation
    full_np = np.array(img)
    border_pts = np.concatenate(
        [full_np[0, :, :], full_np[-1, :, :], full_np[:, 0, :], full_np[:, -1, :]],
        axis=0,
    )
    bg_median = np.median(border_pts, axis=0)
    bg_hex = _rgb_tuple_to_hex(bg_median)

    # Downscale to ~360px wide for fast deterministic gradient + color-diff segmentation
    work_w = 360
    work_h = max(120, int(work_w * orig_h / max(1, orig_w)))
    work_img = img.resize((work_w, work_h), Image.Resampling.BILINEAR)
    w_np = np.array(work_img, dtype=np.float32)

    gray = 0.299 * w_np[:, :, 0] + 0.587 * w_np[:, :, 1] + 0.114 * w_np[:, :, 2]
    gx = np.abs(np.diff(gray, axis=1, prepend=gray[:, :1]))
    gy = np.abs(np.diff(gray, axis=0, prepend=gray[:1, :]))
    grad = gx + gy

    bg_luma = (0.2126 * bg_median[0] + 0.7152 * bg_median[1] + 0.0722 * bg_median[2]) / 255.0
    grad_th = 16.0 if bg_luma < 0.25 else 24.0
    col_th = 18.0 if bg_luma < 0.25 else 28.0

    col_dist = np.linalg.norm(w_np - bg_median[None, None, :].astype(np.float32), axis=2)
    mask_raw = (grad > grad_th) | (col_dist > col_th)
    # Exclude browser scrollbar gutter on far-right edge (last ~6px in scaled space)
    mask_raw[:, max(1, work_w - 6) :] = False
    mask_dil = _dilate_mask(mask_raw, radius_x=3, radius_y=2)

    raw_comps = _extract_components(mask_dil, min_pixels=max(36, int(work_w * work_h * 0.0020)))
    scale_x = orig_w / float(work_w)
    scale_y = orig_h / float(work_h)

    # Convert back to full-res boxes, remove near-duplicates, full-canvas & ultra-thin edge strips
    cand_boxes: list[tuple[int, int, int, int]] = []
    for bx, by, bw, bh in raw_comps:
        area_ratio = (bw * bh) / float(work_w * work_h)
        if area_ratio > 0.85 or area_ratio < 0.0025:
            continue
        if bw <= 6 and bh >= work_h * 0.65:
            continue
        fx = max(0, int(round(bx * scale_x)))
        fy = max(0, int(round(by * scale_y)))
        fw = min(orig_w - fx, int(round(bw * scale_x)))
        fh = min(orig_h - fy, int(round(bh * scale_y)))
        if fw >= 20 and fh >= 14:
            cand_boxes.append((fx, fy, fw, fh))

    # Deduplicate overlapping boxes, prioritize informative blocks, cap at 24
    cand_boxes.sort(key=lambda b: (b[1] // 40, b[0]))
    filtered: list[tuple[int, int, int, int]] = []
    for box in cand_boxes:
        if all(_iou(box, kept) < 0.72 for kept in filtered):
            filtered.append(box)
        if len(filtered) >= 24:
            break

    # Annotate SoM image and compute per-box metrics
    annotated = img.copy()
    draw = ImageDraw.Draw(annotated)
    try:
        font = ImageFont.truetype("arial.ttf", max(13, int(orig_w * 0.011)))
    except Exception:
        font = ImageFont.load_default()

    raw_boxes_meta: list[dict[str, Any]] = []
    asset_area_sum = 0.0
    for idx, (x, y, w, h) in enumerate(filtered, start=1):
        crop = full_np[y : y + h, x : x + w]
        c_gray = 0.299 * crop[:, :, 0] + 0.587 * crop[:, :, 1] + 0.114 * crop[:, :, 2]
        c_grad = float(np.mean(np.abs(np.diff(c_gray, axis=1)))) if w > 2 else 0.0
        local_bg = tuple(int(v) for v in np.median(crop, axis=(0, 1)))
        luma = c_gray
        fg_pixel = crop[np.unravel_index(int(np.argmax(np.abs(luma - np.median(luma)))), luma.shape)]
        local_fg = (int(fg_pixel[0]), int(fg_pixel[1]), int(fg_pixel[2]))

        # Distinguish bimodal flat typography from continuous-tone photography / illustration
        c_max = np.max(crop, axis=2).astype(np.float32)
        c_min = np.min(crop, axis=2).astype(np.float32)
        sat_ratio = float(np.mean((c_max - c_min) > 26.0))
        mid_tone_ratio = float(np.mean((np.abs(luma - np.median(luma)) > 12.0) & (np.abs(luma - float(np.max(luma))) > 20.0)))

        area_frac = round((w * h) / float(orig_w * orig_h), 4)
        is_asset_candidate = area_frac >= 0.055 and h >= 110 and w >= 160 and (sat_ratio >= 0.22 or mid_tone_ratio >= 0.48)
        role_hint = "asset_slot_candidate" if is_asset_candidate else "ui_text_or_card"
        if is_asset_candidate:
            asset_area_sum += area_frac

        mark_id = f"#{idx}"
        raw_boxes_meta.append(
            {
                "mark_id": mark_id,
                "bbox": [x, y, w, h],
                "area_ratio": area_frac,
                "local_bg_hex": _rgb_tuple_to_hex(local_bg),
                "local_fg_hex": _rgb_tuple_to_hex(local_fg),
                "contrast_ratio": _contrast(local_fg, local_bg),
                "edge_energy": round(c_grad, 2),
                "color_sat_ratio": round(sat_ratio, 3),
                "role_hint": role_hint,
            }
        )

        box_color = (232, 100, 44) if is_asset_candidate else (14, 165, 233)
        draw.rectangle([x, y, x + w, y + h], outline=box_color, width=2)
        tag_w = max(28, len(mark_id) * 10 + 10)
        tag_h = 20
        # Place badge above box when room exists, else below bottom-left to avoid obscuring top glyphs
        if y >= tag_h + 2:
            ty = y - tag_h
        elif y + h + tag_h + 2 <= orig_h:
            ty = y + h
        else:
            ty = y
        draw.rectangle([x, ty, x + tag_w, ty + tag_h], fill=box_color)
        draw.text((x + 5, ty + 3), mark_id, fill=(255, 255, 255), font=font)

    out_root = pathlib.Path(output_dir) if output_dir else (PROJECT_ROOT / "cases" / "_som_outputs" / src_path.stem)
    out_root.mkdir(parents=True, exist_ok=True)
    som_path = out_root / "som_annotated.png"
    annotated.save(som_path)

    # Build classification input
    is_dark = (0.2126 * bg_median[0] + 0.7152 * bg_median[1] + 0.0722 * bg_median[2]) / 255.0 < 0.42
    domain_hint = "graphic" if orig_w < orig_h else "uiux"
    classify_input = {
        "title": case_id or src_path.stem,
        "source_url": str(src_path),
        "canvas": {"w": orig_w, "h": orig_h},
        "bboxes": [
            {
                "label": f"{b['mark_id']} {b['role_hint']}",
                "kind": "nav_rail" if (b["bbox"][2] <= orig_w * 0.12 and b["bbox"][3] >= orig_h * 0.45) else b["role_hint"],
                "x": b["bbox"][0],
                "y": b["bbox"][1],
                "w": b["bbox"][2],
                "h": b["bbox"][3],
            }
            for b in raw_boxes_meta
        ],
        "signals": {
            "interactive_count": len([b for b in raw_boxes_meta if b["role_hint"] == "ui_text_or_card"]),
            "canvas_or_media_ratio": round(min(1.0, asset_area_sum), 3),
            "is_dark_surface": is_dark,
            "has_large_hero": any(b["area_ratio"] >= 0.14 for b in raw_boxes_meta),
        },
    }
    classification = cat_reg.classify_skeleton(classify_input, domain_hint=domain_hint)
    if category_override and category_override not in ("auto", "ALL", ""):
        category = cat_reg.load_categories().get(category_override)
        if category:
            classification.update(
                category_id=category_override,
                category_name=category.get("name", category_override),
                tier=category.get("tier", "core"),
                default_domain=category.get("default_domain", "uiux"),
                confidence=1.0,
                reasons=["手动指定分类", *classification["reasons"]],
            )

    result = {
        "status": "OK",
        "tool": "inspect_image_som",
        "source_image": str(src_path.resolve()),
        "som_image_path": str(som_path.resolve()),
        "resolution": {"w": orig_w, "h": orig_h},
        "dominant_bg_hex": bg_hex,
        "palette": palette,
        "box_count": len(raw_boxes_meta),
        "raw_boxes": raw_boxes_meta,
        "classification": classification,
        "agent_handoff": {
            "instructions": "请调用方 Agent 直接读取 som_image_path 并对照 raw_boxes 中每个 [#i] 的像素框与色值，合并为 L0~L5 EU 树；标注为 asset_slot_candidate 的编号保留为视觉资产槽位，其余文字/卡片生成真 DOM。",
            "ui_dom_marks": [b["mark_id"] for b in raw_boxes_meta if b["role_hint"] == "ui_text_or_card"],
            "asset_slot_marks": [b["mark_id"] for b in raw_boxes_meta if b["role_hint"] == "asset_slot_candidate"],
        },
    }
    (out_root / "image_som_measurement.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
