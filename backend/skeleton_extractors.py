"""
开物 v3.4 · 三模态确定性骨架提取与 4 色高对比 SVG 叠图生成器 (skeleton_extractors.py)
支持模态：
  1. video  -> Code XR · Glass Workspace (5.689s 连续 6 时段 100% 闭合覆盖)
  2. image  -> Code XR · 品牌视觉发布展板 (ISO 216 A3 · 297x420mm · 12 栏瑞士网格)
  3. web    -> 内置多断点 DOM 夹具 (390 / 768 / 1440 三断点几何与无障碍闭合)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cases_catalog as catalog_mod
import motion_catalog as motion_mod
import styles_catalog as styles_mod

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
CASES_DIR = PROJECT_ROOT / "cases"

# 4 色高对比语义色板（导航青 / 舞台珊瑚 / 阵列翠绿 / 高密分裂亮紫）
ROLE_COLORS: dict[str, tuple[str, str]] = {
    "nav": ("#0ea5e9", "rgba(14,165,233,0.13)"),
    "stage": ("#f97316", "rgba(249,115,22,0.12)"),
    "array": ("#10b981", "rgba(16,185,129,0.13)"),
    "split": ("#8b5cf6", "rgba(139,92,246,0.15)"),
}


def _escape_xml(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_video_skeleton_code_xr() -> dict[str, Any]:
    """构建 Code XR 5.689s 全时段连续切分确定性视频骨架 IR 与 4 色叠图 SVG。"""
    duration_sec = 5.689
    segments: list[dict[str, Any]] = [
        {
            "segment_id": "seg_01",
            "index": 1,
            "t0": 0.00,
            "t1": 0.75,
            "label": "0.00–0.75s · 品牌虹膜揭幕",
            "frame_url": "/cases/code_xr_uiux/frames/seg_01_opening_0.10s.png",
            "active_eu_ids": [
                "eu_L1_intro_shell",
                "eu_L3_opening_iris",
                "eu_L4_feat_iris_reveal",
            ],
            "bboxes": [
                {
                    "bbox_id": "bb_seg01_opening",
                    "eu_id": "eu_L3_opening_iris",
                    "label": "虹膜揭幕画幅",
                    "x": 0,
                    "y": 0,
                    "w": 1440,
                    "h": 780,
                    "role": "stage",
                },
                {
                    "bbox_id": "bb_seg01_brand",
                    "eu_id": "eu_L4_feat_iris_reveal",
                    "label": "CODE XR 标记与进度线",
                    "x": 560,
                    "y": 270,
                    "w": 320,
                    "h": 210,
                    "role": "split",
                },
            ],
        },
        {
            "segment_id": "seg_02",
            "index": 2,
            "t0": 0.75,
            "t1": 1.60,
            "label": "0.75–1.60s · 亮区展开与数值稳定",
            "frame_url": "/cases/code_xr_uiux/frames/seg_02_aperture_1.44s.png",
            "active_eu_ids": [
                "eu_L3_room_backdrop",
                "eu_L3_sprint_hero",
                "eu_L3_metrics_grid_fold",
            ],
            "bboxes": [
                {
                    "bbox_id": "bb_seg02_room",
                    "eu_id": "eu_L3_room_backdrop",
                    "label": "胡桃木室内环境底图",
                    "x": 0,
                    "y": 0,
                    "w": 1440,
                    "h": 780,
                    "role": "stage",
                },
                {
                    "bbox_id": "bb_seg02_sprint",
                    "eu_id": "eu_L3_sprint_hero",
                    "label": "Sprint 24 英雄区揭开",
                    "x": 168,
                    "y": 134,
                    "w": 776,
                    "h": 356,
                    "role": "split",
                },
                {
                    "bbox_id": "bb_seg02_metrics",
                    "eu_id": "eu_L3_metrics_grid_fold",
                    "label": "四维指标数字卷轴稳定",
                    "x": 168,
                    "y": 506,
                    "w": 1178,
                    "h": 212,
                    "role": "array",
                },
            ],
        },
        {
            "segment_id": "seg_03",
            "index": 3,
            "t0": 1.60,
            "t1": 2.23,
            "label": "1.60–2.23s · 窄侧栏鼠标邻近放大",
            "frame_url": "/cases/code_xr_uiux/frames/seg_03_proximity_1.83s.png",
            "active_eu_ids": [
                "eu_L3_rail_proximity_dock",
                "eu_L4_feat_proximity_magnify",
                "eu_L4_dock_search_orb",
                "eu_L4_dock_active_pill",
                "eu_L4_dock_neighbor_field",
            ],
            "bboxes": [
                {
                    "bbox_id": "bb_seg03_rail",
                    "eu_id": "eu_L3_rail_proximity_dock",
                    "label": "66px 收起态交互坞",
                    "x": 63,
                    "y": 8,
                    "w": 68,
                    "h": 764,
                    "role": "nav",
                },
                {
                    "bbox_id": "bb_seg03_orb",
                    "eu_id": "eu_L4_dock_search_orb",
                    "label": "搜索光球 (34→46.6px)",
                    "x": 74,
                    "y": 76,
                    "w": 46,
                    "h": 46,
                    "role": "split",
                },
                {
                    "bbox_id": "bb_seg03_active",
                    "eu_id": "eu_L4_dock_active_pill",
                    "label": "主项白底 1.37x (40→54.8px)",
                    "x": 69,
                    "y": 146,
                    "w": 56,
                    "h": 56,
                    "role": "split",
                },
                {
                    "bbox_id": "bb_seg03_neighbor",
                    "eu_id": "eu_L4_dock_neighbor_field",
                    "label": "邻项梯度缩放与浮签",
                    "x": 69,
                    "y": 204,
                    "w": 135,
                    "h": 92,
                    "role": "split",
                },
            ],
        },
        {
            "segment_id": "seg_04",
            "index": 4,
            "t0": 2.23,
            "t1": 3.80,
            "label": "2.23–3.80s · 展开侧栏与 Dashboard 首屏",
            "frame_url": "/cases/code_xr_uiux/frames/seg_04_dashboard_2.78s.png",
            "active_eu_ids": [
                "eu_L1_nav_dock",
                "eu_L3_brand_header",
                "eu_L3_nav_route_list",
                "eu_L3_sidebar_footer",
                "eu_L3_page_heading",
                "eu_L3_sprint_hero",
                "eu_L3_orbit_avatars_fold",
                "eu_L3_studio_calendar",
                "eu_L3_metrics_grid_fold",
            ],
            "bboxes": [
                {
                    "bbox_id": "bb_seg04_sidebar",
                    "eu_id": "eu_L1_nav_dock",
                    "label": "240px 展开折光侧栏",
                    "x": 63,
                    "y": 8,
                    "w": 240,
                    "h": 764,
                    "role": "nav",
                },
                {
                    "bbox_id": "bb_seg04_routes",
                    "eu_id": "eu_L3_nav_route_list",
                    "label": "分组路由阵列 ×8",
                    "x": 74,
                    "y": 140,
                    "w": 218,
                    "h": 456,
                    "role": "array",
                },
                {
                    "bbox_id": "bb_seg04_heading",
                    "eu_id": "eu_L3_page_heading",
                    "label": "Dashboard 问候顶栏",
                    "x": 352,
                    "y": 34,
                    "w": 990,
                    "h": 82,
                    "role": "stage",
                },
                {
                    "bbox_id": "bb_seg04_hero",
                    "eu_id": "eu_L3_sprint_hero",
                    "label": "Sprint 24 珊瑚红英雄卡",
                    "x": 352,
                    "y": 134,
                    "w": 656,
                    "h": 358,
                    "role": "split",
                },
                {
                    "bbox_id": "bb_seg04_orbit",
                    "eu_id": "eu_L3_orbit_avatars_fold",
                    "label": "68% 进度环 + 6 头像阵列",
                    "x": 742,
                    "y": 182,
                    "w": 252,
                    "h": 252,
                    "role": "array",
                },
                {
                    "bbox_id": "bb_seg04_calendar",
                    "eu_id": "eu_L3_studio_calendar",
                    "label": "November 9 周历卡片",
                    "x": 1024,
                    "y": 134,
                    "w": 318,
                    "h": 358,
                    "role": "stage",
                },
                {
                    "bbox_id": "bb_seg04_metrics",
                    "eu_id": "eu_L3_metrics_grid_fold",
                    "label": "经营四指标阵列 ×4",
                    "x": 352,
                    "y": 508,
                    "w": 990,
                    "h": 214,
                    "role": "array",
                },
            ],
        },
        {
            "segment_id": "seg_05",
            "index": 5,
            "t0": 3.80,
            "t1": 4.85,
            "label": "3.80–4.85s · 主区独立下滚",
            "frame_url": "/cases/code_xr_uiux/frames/seg_05_scroll_4.36s.png",
            "active_eu_ids": [
                "eu_L1_main_stage",
                "eu_L3_quick_actions_fold",
                "eu_L3_revenue_chart_card",
                "eu_L4_feat_range_segments",
                "eu_L3_channel_donut_card",
            ],
            "bboxes": [
                {
                    "bbox_id": "bb_seg05_sidebar_inv",
                    "eu_id": "eu_L1_nav_dock",
                    "label": "侧栏静止不变量 (Δy=0)",
                    "x": 63,
                    "y": 8,
                    "w": 240,
                    "h": 764,
                    "role": "nav",
                },
                {
                    "bbox_id": "bb_seg05_quick",
                    "eu_id": "eu_L3_quick_actions_fold",
                    "label": "快捷动作阵列 ×6",
                    "x": 352,
                    "y": 196,
                    "w": 990,
                    "h": 136,
                    "role": "array",
                },
                {
                    "bbox_id": "bb_seg05_rev",
                    "eu_id": "eu_L3_revenue_chart_card",
                    "label": "月度利润/成本双柱图",
                    "x": 352,
                    "y": 348,
                    "w": 656,
                    "h": 396,
                    "role": "split",
                },
                {
                    "bbox_id": "bb_seg05_channels",
                    "eu_id": "eu_L3_channel_donut_card",
                    "label": "$236.8K 渠道环形分布",
                    "x": 1024,
                    "y": 348,
                    "w": 318,
                    "h": 396,
                    "role": "stage",
                },
            ],
        },
        {
            "segment_id": "seg_06",
            "index": 6,
            "t0": 4.85,
            "t1": 5.689,
            "label": "4.85–5.689s · Analytics 切页与瞬态隔离",
            "frame_url": "/cases/code_xr_uiux/frames/seg_06_analytics_5.62s.png",
            "active_eu_ids": [
                "eu_L3_analytics_header_csv",
                "eu_L3_analytics_wide_stage",
                "eu_L4_feat_csv_export",
            ],
            "bboxes": [
                {
                    "bbox_id": "bb_seg06_head",
                    "eu_id": "eu_L3_analytics_header_csv",
                    "label": "Analytics 顶栏与 CSV 导出",
                    "x": 352,
                    "y": 34,
                    "w": 990,
                    "h": 82,
                    "role": "stage",
                },
                {
                    "bbox_id": "bb_seg06_wide",
                    "eu_id": "eu_L3_analytics_wide_stage",
                    "label": "全宽 Revenue 与瞬态隔离区",
                    "x": 352,
                    "y": 348,
                    "w": 990,
                    "h": 396,
                    "role": "split",
                },
            ],
        },
    ]

    all_bboxes: list[dict[str, Any]] = []
    for seg in segments:
        for b in seg["bboxes"]:
            item = dict(b)
            item["segment_id"] = seg["segment_id"]
            item["color_role"] = b["role"]
            all_bboxes.append(item)

    covered = sum(round(s["t1"] - s["t0"], 6) for s in segments)
    coverage_ratio = round(covered / duration_sec, 6)

    svg_str = render_video_skeleton_svg(segments, duration_sec)

    skeleton: dict[str, Any] = {
        "case_id": "code_xr_uiux",
        "modality": "video",
        "fps": 30.0,
        "duration_sec": duration_sec,
        "coverage_ratio": coverage_ratio,
        "viewport": {
            "width": 1440,
            "height": 780,
            "raw_video_size": [1920, 2560],
            "crop_bbox": [0, 380, 1920, 1040],
            "scale": 0.75,
        },
        "viewport_transform": {
            "source_size": {"w": 1920, "h": 2560},
            "crop_rect": {"x": 0, "y": 380, "w": 1920, "h": 1040},
            "scale": 0.75,
            "target_size": {"w": 1440, "h": 780},
        },
        "noise_regions": [
            {
                "id": "noise_top_letterbox",
                "kind": "letterbox",
                "bbox": [0, 0, 1920, 380],
                "desc": "竖版视频顶部留黑区",
            },
            {
                "id": "noise_bottom_code_window",
                "kind": "code_window",
                "bbox": [0, 1420, 1920, 1140],
                "desc": "竖版视频下半部代码展示窗（非网页组件）",
            },
        ],
        "observations": [
            {
                "id": "obs_sprint_progress_68",
                "eu_id": "eu_L3_sprint_hero",
                "label": "Sprint 24 进度环百分比",
                "value": "68%",
                "settle_state": "steady",
                "stable_frames": 62,
                "verified": True,
            },
            {
                "id": "obs_kpi_people_128",
                "eu_id": "eu_L3_metrics_grid_fold",
                "label": "Active people 指标",
                "value": "128",
                "settle_state": "steady",
                "stable_frames": 48,
                "verified": True,
            },
            {
                "id": "obs_kpi_deals_49",
                "eu_id": "eu_L3_metrics_grid_fold",
                "label": "Open deals 指标",
                "value": "49",
                "settle_state": "steady",
                "stable_frames": 48,
                "verified": True,
            },
            {
                "id": "obs_kpi_revenue_42500",
                "eu_id": "eu_L3_metrics_grid_fold",
                "label": "Revenue this month 指标",
                "value": "$42,500",
                "settle_state": "steady",
                "stable_frames": 48,
                "verified": True,
            },
            {
                "id": "obs_kpi_uptime_9996",
                "eu_id": "eu_L3_metrics_grid_fold",
                "label": "System uptime 指标",
                "value": "99.96%",
                "settle_state": "steady",
                "stable_frames": 48,
                "verified": True,
            },
            {
                "id": "obs_rail_proximity_peak",
                "eu_id": "eu_L4_feat_proximity_magnify",
                "label": "窄栏主项峰值放大倍率",
                "value": "1.37x",
                "settle_state": "steady",
                "stable_frames": 4,
                "verified": True,
            },
            {
                "id": "obs_analytics_tail_reels",
                "eu_id": "eu_L3_analytics_wide_stage",
                "label": "5.62s Analytics 指标卷轴滚动瞬态值",
                "value": "rolling_unsettled",
                "settle_state": "transient",
                "stable_frames": 0,
                "verified": False,
                "assumption_id": "ASM-XR-01",
            },
        ],
        "frame_invariants": [
            {
                "id": "inv_rail_stationary_on_scroll",
                "desc": "主舞台纵向滚动时左侧玻璃导航栏位移恒为 0",
                "holds": True,
                "evidence": {
                    "t0": 3.80,
                    "t1": 4.85,
                    "frame_bbox": [84, 390, 320, 1018],
                },
            },
            {
                "id": "inv_dock_hitbox_stable",
                "desc": "收起侧栏邻近放大仅缩放绘制层，命中盒与当前路由保持不变",
                "holds": True,
                "evidence": {
                    "t0": 1.60,
                    "t1": 2.23,
                    "frame_bbox": [84, 390, 96, 1018],
                },
            },
        ],
        "segments": segments,
        "bboxes": all_bboxes,
        "skeleton_svg": svg_str,
    }
    return skeleton


def render_video_skeleton_svg(segments: list[dict[str, Any]], duration_sec: float) -> str:
    """渲染 1440x780 的 4 色高对比可交互视频骨架叠图 SVG。"""
    parts: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 836" width="100%" height="100%" data-modality="video">',
        "  <defs>",
        '    <style>',
        '      .sk-box { cursor: pointer; transition: stroke-width 0.16s, fill-opacity 0.16s; }',
        '      .sk-box:hover, .sk-box[data-active="true"] { stroke-width: 4px !important; fill-opacity: 0.28 !important; }',
        '      .sk-tag { font-family: Manrope, "Segoe UI", sans-serif; font-size: 13px; font-weight: 700; pointer-events: none; }',
        '      .sk-seg { cursor: pointer; }',
        '    </style>',
        "  </defs>",
        '  <rect x="0" y="0" width="1440" height="836" rx="14" fill="#181210"/>',
        '  <image id="skeleton-bg-frame" href="/cases/code_xr_uiux/frames/seg_04_dashboard_2.78s.png" x="0" y="0" width="1440" height="780" preserveAspectRatio="xMidYMid slice" opacity="0.88"/>',
        '  <g data-layer="skeleton" opacity="0.55">',
        '    <rect x="55" y="6" width="1330" height="768" rx="28" fill="none" stroke="#fff6ef" stroke-width="1.5" stroke-dasharray="6 4"/>',
        '    <line x1="320" y1="6" x2="320" y2="774" stroke="#0ea5e9" stroke-width="1.5" stroke-dasharray="5 5"/>',
        "  </g>",
        '  <g data-layer="bbox">',
    ]

    for seg in segments:
        seg_id = seg["segment_id"]
        # 默认首屏展示 seg_04 + seg_03 的关键框；所有时段框均带 data-segment-id 供前端按时段筛选
        default_opacity = "1" if seg_id in ("seg_04", "seg_03") else "0.22"
        parts.append(f'    <g class="sk-segment-group" data-segment-id="{seg_id}" opacity="{default_opacity}">')
        for b in seg["bboxes"]:
            stroke, fill = ROLE_COLORS.get(b["role"], ("#0ea5e9", "rgba(14,165,233,0.12)"))
            x, y, w, h = b["x"], b["y"], b["w"], b["h"]
            eu_id = b["eu_id"]
            label = _escape_xml(f'{b["label"]}')
            tag_w = min(w, max(124, len(b["label"]) * 12 + 18))
            tag_y = max(4, y + 4)
            parts.append(
                f'      <g class="sk-node" data-eu-id="{eu_id}" data-segment-id="{seg_id}" data-bbox-id="{b["bbox_id"]}">'
                f'<rect class="sk-box" data-eu-id="{eu_id}" data-segment-id="{seg_id}" x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="2.4"/>'
                f'<rect x="{x + 4}" y="{tag_y}" width="{tag_w}" height="22" rx="6" fill="{stroke}" fill-opacity="0.92"/>'
                f'<text class="sk-tag" x="{x + 11}" y="{tag_y + 15}" fill="#ffffff">{label}</text>'
                f"</g>"
            )
        parts.append("    </g>")
    parts.append("  </g>")

    # 底部 6 段连续时间轴闭合条 (y=786..830)
    parts.append('  <g data-layer="timeline" transform="translate(16, 788)">')
    bar_w = 1408.0
    seg_palette = ["#8b5cf6", "#f97316", "#0ea5e9", "#10b981", "#f59e0b", "#ec4899"]
    for idx, seg in enumerate(segments):
        x0 = round((seg["t0"] / duration_sec) * bar_w, 2)
        w0 = round(((seg["t1"] - seg["t0"]) / duration_sec) * bar_w, 2)
        col = seg_palette[idx % len(seg_palette)]
        short_lbl = _escape_xml(f'S{idx + 1} {seg["t0"]:.2f}-{seg["t1"]:.2f}s')
        eu_anchor = seg["active_eu_ids"][0]
        parts.append(
            f'    <g class="sk-seg" data-segment-id="{seg["segment_id"]}" data-eu-id="{eu_anchor}">'
            f'<rect x="{x0}" y="0" width="{max(4.0, w0 - 2)}" height="36" rx="7" fill="{col}" fill-opacity="0.86" stroke="#fff6ef" stroke-width="1"/>'
            f'<text class="sk-tag" x="{x0 + 8}" y="23" fill="#ffffff" style="font-size:12px">{short_lbl}</text>'
            f"</g>"
        )
    parts.append("  </g>")
    parts.append("</svg>")
    return "\n".join(parts)


def build_image_skeleton_poster() -> dict[str, Any]:
    """构建 Code XR 平面视觉发布展板 (ISO A3 · 297x420mm · 12 栏瑞士网格) 确定性图片骨架 IR 与叠图 SVG。"""
    col_w = 229.0 / 12.0  # 19.083333mm: 12 + 12 + 12*col_w + 11*4 == 297.0mm
    bboxes: list[dict[str, Any]] = [
        {
            "bbox_id": "bb_poster_header",
            "eu_id": "eu_L1_poster_header",
            "label": "品牌页眉 (Col 1–12)",
            "x": 12.0,
            "y": 14.0,
            "w": 273.0,
            "h": 28.0,
            "role": "nav",
        },
        {
            "bbox_id": "bb_poster_logo",
            "eu_id": "eu_L3_poster_logo_lockup",
            "label": "标志与主名锁排 (Col 1–8)",
            "x": 12.0,
            "y": 14.0,
            "w": 180.67,
            "h": 28.0,
            "role": "nav",
        },
        {
            "bbox_id": "bb_poster_issue",
            "eu_id": "eu_L3_poster_issue_meta",
            "label": "期号规格胶囊 (Col 9–12)",
            "x": 196.67,
            "y": 14.0,
            "w": 88.33,
            "h": 28.0,
            "role": "stage",
        },
        {
            "bbox_id": "bb_poster_headline",
            "eu_id": "eu_L3_poster_headline",
            "label": "主标题四级字阶区 (Col 1–7)",
            "x": 12.0,
            "y": 48.0,
            "w": 157.58,
            "h": 186.0,
            "role": "stage",
        },
        {
            "bbox_id": "bb_poster_graphic",
            "eu_id": "eu_L3_poster_key_graphic",
            "label": "68% 纯矢量几何主图 (Col 8–12)",
            "x": 173.58,
            "y": 48.0,
            "w": 111.42,
            "h": 186.0,
            "role": "split",
        },
        {
            "bbox_id": "bb_poster_palette",
            "eu_id": "eu_L3_poster_palette_fold",
            "label": "品牌色卡阵列 ×4 (Col 1–12)",
            "x": 12.0,
            "y": 242.0,
            "w": 273.0,
            "h": 58.0,
            "role": "array",
        },
        {
            "bbox_id": "bb_poster_specimen",
            "eu_id": "eu_L3_poster_type_specimen",
            "label": "Manrope 字阶标本 (Col 1–8)",
            "x": 12.0,
            "y": 306.0,
            "w": 180.67,
            "h": 62.0,
            "role": "stage",
        },
        {
            "bbox_id": "bb_poster_grid_spec",
            "eu_id": "eu_L3_poster_grid_overlay",
            "label": "12 栏网格参数卡 (Col 9–12)",
            "x": 196.67,
            "y": 306.0,
            "w": 88.33,
            "h": 62.0,
            "role": "array",
        },
        {
            "bbox_id": "bb_poster_footer",
            "eu_id": "eu_L1_poster_footer",
            "label": "版权与印前页脚 (Col 1–12)",
            "x": 12.0,
            "y": 376.0,
            "w": 273.0,
            "h": 32.0,
            "role": "nav",
        },
    ]

    segments = [
        {
            "segment_id": "seg_poster_full",
            "index": 1,
            "t0": 0.0,
            "t1": 1.0,
            "label": "ISO A3 全画幅 · 12 栏瑞士网格与 3mm 出血",
            "frame_url": "/cases/code_xr_poster/frames/poster_source_a3.svg",
            "active_eu_ids": [b["eu_id"] for b in bboxes],
            "bboxes": bboxes,
        }
    ]

    svg_parts: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 -6 309 432" width="100%" height="100%" data-modality="image">',
        "  <defs><style>",
        "    .sk-box { cursor: pointer; transition: stroke-width 0.16s, fill-opacity 0.16s; }",
        '    .sk-box:hover, .sk-box[data-active="true"] { stroke-width: 1.8px !important; fill-opacity: 0.26 !important; }',
        '    .sk-lbl { font-family: Manrope, "Segoe UI", sans-serif; font-size: 4.3px; font-weight: 800; pointer-events: none; }',
        "  </style></defs>",
        '  <rect x="-3" y="-3" width="303" height="426" fill="#231712" stroke="#f97316" stroke-width="0.6" stroke-dasharray="2.5 1.5"/>',
        '  <image id="skeleton-bg-frame" href="/cases/code_xr_poster/frames/poster_source_a3.svg" x="0" y="0" width="297" height="420"/>',
        '  <g data-layer="skeleton">',
        '    <rect x="-3" y="-3" width="303" height="426" fill="none" stroke="#ef4444" stroke-width="0.5" stroke-dasharray="2 2"/>',
        '    <rect x="12" y="12" width="273" height="396" fill="none" stroke="#10b981" stroke-width="0.6" stroke-dasharray="3 2"/>',
    ]
    for c in range(12):
        cx = round(12.0 + c * (col_w + 4.0), 3)
        svg_parts.append(
            f'    <rect x="{cx}" y="12" width="{col_w:.3f}" height="396" fill="#0ea5e9" fill-opacity="0.06" stroke="#0ea5e9" stroke-opacity="0.28" stroke-width="0.25"/>'
        )
    svg_parts.append("  </g>")
    svg_parts.append('  <g data-layer="bbox">')
    for b in bboxes:
        stroke, fill = ROLE_COLORS.get(b["role"], ("#0ea5e9", "rgba(14,165,233,0.12)"))
        x, y, w, h = b["x"], b["y"], b["w"], b["h"]
        eu_id = b["eu_id"]
        lbl = _escape_xml(b["label"])
        tag_w = min(w, max(44.0, len(b["label"]) * 2.9 + 6.0))
        svg_parts.append(
            f'    <g class="sk-node" data-eu-id="{eu_id}" data-segment-id="seg_poster_full">'
            f'<rect class="sk-box" data-eu-id="{eu_id}" data-segment-id="seg_poster_full" x="{x}" y="{y}" width="{w}" height="{h}" rx="2.5" fill="{fill}" stroke="{stroke}" stroke-width="0.9"/>'
            f'<rect x="{x + 1}" y="{y + 1}" width="{tag_w:.1f}" height="7.2" rx="1.6" fill="{stroke}" fill-opacity="0.92"/>'
            f'<text class="sk-lbl" x="{x + 3}" y="{y + 6.1}" fill="#ffffff">{lbl}</text>'
            f"</g>"
        )
    svg_parts.append("  </g>")
    svg_parts.append('  <g data-layer="timeline"><text x="12" y="416" class="sk-lbl" fill="#0ea5e9">ISO 216 A3 · 297×420mm · BLEED 3mm · 12-COL SWISS GRID</text></g>')
    svg_parts.append("</svg>")

    return {
        "case_id": "code_xr_poster",
        "modality": "image",
        "duration_sec": None,
        "coverage_ratio": 1.0,
        "viewport": {
            "width": 297.0,
            "height": 420.0,
            "unit": "mm",
            "format": "ISO 216 A3",
            "bleed_mm": 3.0,
            "safe_margin_mm": 12.0,
            "grid_columns": 12,
        },
        "canvas": {
            "w": 297.0,
            "h": 420.0,
            "declared_ratio": 0.7071,
            "bleed": 3.0,
            "safe_margin": 12.0,
        },
        "grid": {
            "columns": 12,
            "column_width": col_w,
            "gutter": 4.0,
            "margin_left": 12.0,
            "margin_right": 12.0,
        },
        "source_image": {
            "w": 297.0,
            "h": 420.0,
            "url": "/cases/code_xr_poster/frames/poster_source_a3.svg",
        },
        "layers": [
            {
                "layer_id": "lyr_paper_bg",
                "layer_role": "background_material",
                "contains_text": False,
                "desc": "暖象牙纸基与柔和径向氛围渐变",
            },
            {
                "layer_id": "lyr_orbit_vector",
                "layer_role": "foreground_graphic",
                "contains_text": False,
                "desc": "68% 纯 SVG 几何圆环与色卡色块",
            },
            {
                "layer_id": "lyr_swiss_typography",
                "layer_role": "foreground_text",
                "contains_text": True,
                "desc": "四级字阶活 DOM / SVG 排版层",
            },
        ],
        "noise_regions": [],
        "segments": segments,
        "bboxes": [dict(b, segment_id="seg_poster_full", color_role=b["role"]) for b in bboxes],
        "skeleton_svg": "\n".join(svg_parts),
    }


def build_web_fixture_skeleton() -> dict[str, Any]:
    """构建内置轻量 web 模态多断点 DOM 夹具（供 PW-01 ~ PW-04 规则验证与反事实沙盒演练）。"""
    breakpoints = [390, 768, 1440]
    dom_by_bp: dict[int, dict[str, Any]] = {}
    for bp in breakpoints:
        pad = 16 if bp == 390 else 24
        inner_w = bp - pad * 2
        rail_w = inner_w if bp == 390 else (180 if bp == 768 else 240)
        stage_x = pad if bp == 390 else pad + rail_w + 16
        stage_w = inner_w if bp == 390 else inner_w - rail_w - 16
        dom_by_bp[bp] = {
            "viewport_w": bp,
            "scroll_width": bp,
            "rects": {
                "eu_L0_web_workspace": {"x": 0, "y": 0, "w": bp, "h": 900},
                "eu_L1_web_intro": {"x": pad, "y": 12, "w": inner_w, "h": 48},
                "eu_L2_web_loader": {"x": pad, "y": 12, "w": inner_w, "h": 48},
                "eu_L1_web_nav": {"x": pad, "y": 68, "w": rail_w, "h": 220 if bp == 390 else 780},
                "eu_L2_web_rail": {"x": pad, "y": 68, "w": rail_w, "h": 220 if bp == 390 else 780},
                "eu_L1_web_stage": {"x": stage_x, "y": 296 if bp == 390 else 68, "w": stage_w, "h": 560},
                "eu_L2_web_metrics": {"x": stage_x, "y": 296 if bp == 390 else 68, "w": stage_w, "h": 240},
                "eu_L1_web_overlay": {"x": pad, "y": 120, "w": min(480, inner_w), "h": 320},
                "eu_L2_web_dialog": {"x": pad, "y": 120, "w": min(480, inner_w), "h": 320},
            },
        }

    return {
        "case_id": "web_fixture",
        "modality": "web",
        "duration_sec": None,
        "coverage_ratio": 1.0,
        "breakpoints": breakpoints,
        "viewport": {"width": 1440, "height": 900, "breakpoints": breakpoints},
        "dom": dom_by_bp,
        "computed_styles": [
            {"id": "cs_ink", "eu_id": "eu_L3_web_kpi_fold", "property": "color", "value": "#221611", "token_ref": "surf_ink_walnut", "delta_e": 0.0},
            {"id": "cs_bg", "eu_id": "eu_L3_web_kpi_fold", "property": "background-color", "value": "#fff6ef", "token_ref": "surf_warm_paper", "delta_e": 0.0},
            {"id": "cs_fs", "eu_id": "eu_L3_web_kpi_fold", "property": "font-size", "value": "19px", "token_ref": "typo_card_title", "delta_e": 0.0},
            {"id": "cs_fw", "eu_id": "eu_L3_web_kpi_fold", "property": "font-weight", "value": "800", "token_ref": "typo_display_h1", "delta_e": 0.0},
            {"id": "cs_rad", "eu_id": "eu_L3_web_kpi_fold", "property": "border-radius", "value": "27px", "token_ref": "lay_card_radius", "delta_e": 0.0},
            {"id": "cs_gap", "eu_id": "eu_L3_web_kpi_fold", "property": "gap", "value": "16px", "token_ref": "lay_grid_gap", "delta_e": 0.0},
            {"id": "cs_pad", "eu_id": "eu_L3_web_nav_list", "property": "padding", "value": "16px", "token_ref": "lay_grid_gap", "delta_e": 0.0},
            {"id": "cs_shd", "eu_id": "eu_L3_web_kpi_fold", "property": "box-shadow", "value": "0 11px 27px #45291b1c", "token_ref": "surf_warm_paper", "delta_e": 0.0},
            {"id": "cs_dur", "eu_id": "eu_L3_web_nav_list", "property": "transition-duration", "value": "520ms", "token_ref": "mot_rail_transition", "delta_e": 0.0},
        ],
        "interactive_elements": [
            {
                "id": "el_nav_dash",
                "eu_id": "eu_L3_web_nav_list",
                "role": "link",
                "accessible_name": "Dashboard",
                "states": ["default", "hover", "focus-visible", "active"],
            },
            {
                "id": "el_skip_intro",
                "eu_id": "eu_L3_web_skip_btn",
                "role": "button",
                "accessible_name": "Skip intro",
                "states": ["default", "hover", "focus-visible", "active"],
            },
            {
                "id": "el_dialog_close",
                "eu_id": "eu_L3_web_modal",
                "role": "button",
                "accessible_name": "Close dialog",
                "states": ["default", "hover", "focus-visible", "active"],
            },
        ],
        "content_nodes": [
            {
                "id": "cn_ambient_orb",
                "eu_id": "eu_L3_web_skip_btn",
                "content_class": "decoration",
                "aria_hidden": True,
                "data_source": None,
                "children_classes": [],
            },
            {
                "id": "cn_kpi_cards",
                "eu_id": "eu_L3_web_kpi_fold",
                "content_class": "data",
                "aria_hidden": False,
                "data_source": "workspace.metrics",
                "children_classes": ["data"],
            },
        ],
        "segments": [
            {
                "segment_id": "seg_web_bps",
                "index": 1,
                "t0": 0.0,
                "t1": 1.0,
                "label": "390 / 768 / 1440px 三断点 DOM 几何快照",
                "frame_url": "",
                "active_eu_ids": ["eu_L1_web_nav", "eu_L1_web_stage", "eu_L3_web_kpi_fold"],
                "bboxes": [],
            }
        ],
        "bboxes": [],
        "skeleton_svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 400"><rect width="1440" height="400" fill="#181210"/><rect data-eu-id="eu_L1_web_nav" data-layer="bbox" x="24" y="24" width="240" height="352" rx="14" fill="rgba(14,165,233,0.16)" stroke="#0ea5e9" stroke-width="2"/><rect data-eu-id="eu_L1_web_stage" data-layer="bbox" x="280" y="24" width="1136" height="352" rx="14" fill="rgba(16,185,129,0.14)" stroke="#10b981" stroke-width="2"/></svg>',
    }


def extract_case_skeleton(case_id: str, persist: bool = True) -> dict[str, Any]:
    """按 case_id 提取确定性骨架，并在 persist=True 时写入 cases/<case_id>/skeleton_ir.json 与 skeleton_overlay.svg。"""
    if case_id == "code_xr_uiux":
        skel = build_video_skeleton_code_xr()
    elif case_id == "code_xr_poster":
        skel = build_image_skeleton_poster()
    elif case_id == "web_fixture":
        skel = build_web_fixture_skeleton()
    elif case_id == "refract_crm_web":
        skel = catalog_mod.build_web_skeleton_refract()
    elif case_id == "haven_admin_web":
        skel = catalog_mod.build_web_skeleton_haven()
    elif case_id in styles_mod.STYLE_CASE_META:
        skel = styles_mod.extract_style_skeleton(case_id)
    elif case_id in motion_mod.MOTION_CASE_META:
        skel = motion_mod.extract_motion_skeleton(case_id)
    else:
        parsed_file = CASES_DIR / case_id / "parsed_case.json"
        if not parsed_file.exists():
            raise ValueError(f"Unknown case_id for skeleton extraction: {case_id}")
        skel = json.loads(parsed_file.read_text(encoding="utf-8"))["skeleton"]

    if persist and case_id != "web_fixture":
        out_dir = CASES_DIR / case_id
        out_dir.mkdir(parents=True, exist_ok=True)
        ir_copy = {k: v for k, v in skel.items() if k != "skeleton_svg"}
        (out_dir / "skeleton_ir.json").write_text(
            json.dumps(ir_copy, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_dir / "skeleton_overlay.svg").write_text(
            skel["skeleton_svg"], encoding="utf-8"
        )
    return skel
