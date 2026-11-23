"""
开物 v3.4 · 扩展相似项目案例库 (cases_catalog.py)
收录经原型模板锚定与 Web->UI/UX (PW-01..04 -> GN-01..04 -> GU-01..04) 完整落地的两个相似项目：
  1. refract_crm_web : Refract — Liquid-Glass CRM Workspace (暖色室内景深 + WebGL/CSS光学色散液态玻璃 + 36%胜率环 + 拨号台)
  2. haven_admin_web : Haven — Glass Admin & CRM Workspace (灰暖空间整窗透射玻璃 + 64%刻度表盘 + 音频波形复盘)
"""
from __future__ import annotations

from typing import Any, Callable

ROLE_COLORS: dict[str, tuple[str, str]] = {
    "nav": ("#0ea5e9", "rgba(14,165,233,0.14)"),
    "stage": ("#f97316", "rgba(249,115,22,0.13)"),
    "array": ("#10b981", "rgba(16,185,129,0.14)"),
    "split": ("#8b5cf6", "rgba(139,92,246,0.16)"),
}

EXTRA_CASE_META: dict[str, dict[str, Any]] = {
    "refract_crm_web": {
        "case_id": "refract_crm_web",
        "title": "Refract · Liquid-Glass CRM",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/refract_crm_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 液态玻璃折射",
    },
    "haven_admin_web": {
        "case_id": "haven_admin_web",
        "title": "Haven · Glass Admin Workspace",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/haven_admin_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 空间表盘与波形",
    },
}

EXTRA_DEFAULT_ASSUMPTIONS: dict[str, list[dict[str, Any]]] = {
    "refract_crm_web": [
        {
            "assumption_id": "ASM-RF-01",
            "eu_id": "eu_L0_rf_workspace",
            "subject_ids": ["eu_L0_rf_workspace"],
            "title": "液态玻璃底层暖棕客厅光影氛围图离线替代",
            "category": "substitute_background_asset",
            "assumed_value": "采用离线合成多层暖琥珀光影景深底图替代原站远程实景摄影资源，保持折射边缘色温一致",
            "evidence_gap": "网页截图内玻璃卡片与实景沙发照片耦合叠加，无法从单张截图分离无遮挡摄影底图",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-RF-02",
            "eu_id": "eu_L3_rf_revenue_chart",
            "subject_ids": ["eu_L3_rf_revenue_chart", "eu_L4_rf_rev_filter"],
            "title": "7D / 30D / 12M Revenue 成交明细与 CSV 导出口径",
            "category": "unobserved_interaction_payload",
            "assumed_value": "按 $3.62M 年营收目标与 12 个月同比趋势生成同口径 CRM 成交单据并支持按激活区间导出 CSV",
            "evidence_gap": "参考页展示 7D/30D/12M 切换胶囊，未公开后端原始逐笔订单 CSV 列头",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "haven_admin_web": [
        {
            "assumption_id": "ASM-HV-01",
            "eu_id": "eu_L0_hv_workspace",
            "subject_ids": ["eu_L0_hv_workspace"],
            "title": "灰暖调起居室透射玻璃环境背景离线替代",
            "category": "substitute_background_asset",
            "assumed_value": "以离线渲染灰暖调建筑光影景深图衬托整窗毛玻璃轮廓与 1px 高光边框",
            "evidence_gap": "原网页视窗底层室内环境图片未打包进本地静态资产",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-HV-02",
            "eu_id": "eu_L3_hv_call_player",
            "subject_ids": ["eu_L3_hv_call_player", "eu_L4_hv_wave_playback"],
            "title": "Discovery Call 通话复盘音频波形时序采样口径",
            "category": "unobserved_interaction_payload",
            "assumed_value": "使用 52 柱确定性声波振幅序列模拟 02:12 / 03:32 通话片段播放与倍速推进",
            "evidence_gap": "参考网页展示静态音频波形与播放态，未附带真实 mp3 音轨文件",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
    ],
}


def _escape_xml(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _render_web_skeleton_svg(
    frame_url: str,
    bboxes: list[dict[str, Any]],
    rail_x: int,
    stage_x: int,
    panel_radius: int,
) -> str:
    """生成 1440x900 的 4 色高对比 Web 骨架叠图 SVG（兼容前端左窗格选框与高亮协议）。"""
    parts: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 900" width="100%" height="100%" data-modality="web">',
        "  <defs>",
        "    <style>",
        "      .sk-box { cursor: pointer; transition: stroke-width 0.16s, fill-opacity 0.16s; }",
        '      .sk-box:hover, .sk-box[data-active="true"] { stroke-width: 4px !important; fill-opacity: 0.28 !important; }',
        '      .sk-tag { font-family: Manrope, "Segoe UI", sans-serif; font-size: 13px; font-weight: 700; pointer-events: none; }',
        "    </style>",
        "  </defs>",
        '  <rect x="0" y="0" width="1440" height="900" rx="14" fill="#181210"/>',
        f'  <image id="skeleton-bg-frame" href="{_escape_xml(frame_url)}" x="0" y="0" width="1440" height="900" preserveAspectRatio="xMidYMid slice" opacity="0.90"/>',
        '  <g data-layer="skeleton" opacity="0.58">',
        f'    <rect x="{rail_x}" y="14" width="{1440 - rail_x - 20}" height="872" rx="{panel_radius}" fill="none" stroke="#fff6ef" stroke-width="1.5" stroke-dasharray="6 4"/>',
        f'    <line x1="{stage_x}" y1="14" x2="{stage_x}" y2="886" stroke="#0ea5e9" stroke-width="1.6" stroke-dasharray="5 5"/>',
        "  </g>",
        '  <g data-layer="bbox">',
        '    <g class="sk-segment-group" data-segment-id="seg_web_desktop" opacity="1">',
    ]
    for b in bboxes:
        stroke, fill = ROLE_COLORS.get(b["role"], ("#0ea5e9", "rgba(14,165,233,0.14)"))
        x, y, w, h = b["x"], b["y"], b["w"], b["h"]
        eu_id = b["eu_id"]
        label = _escape_xml(b["label"])
        tag_w = min(w, max(124, len(b["label"]) * 12 + 18))
        tag_y = max(4, y + 4)
        parts.append(
            f'      <g class="sk-node" data-eu-id="{eu_id}" data-segment-id="seg_web_desktop" data-bbox-id="{b["bbox_id"]}">'
            f'<rect class="sk-box" data-eu-id="{eu_id}" data-segment-id="seg_web_desktop" x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="2.4"/>'
            f'<rect x="{x + 4}" y="{tag_y}" width="{tag_w}" height="22" rx="6" fill="{stroke}" fill-opacity="0.92"/>'
            f'<text class="sk-tag" x="{x + 11}" y="{tag_y + 15}" fill="#ffffff">{label}</text>'
            "</g>"
        )
    parts.extend(["    </g>", "  </g>", "</svg>"])
    return "\n".join(parts)


def _build_three_breakpoint_rects(
    root_id: str,
    l1_l2_specs: dict[str, dict[str, tuple[int, int, int, int]]],
) -> dict[int, dict[str, Any]]:
    """根据三断点规格表构建严格满足子盒不越出父盒与零横向溢出的 DOM 几何快照。"""
    dom_by_bp: dict[int, dict[str, Any]] = {}
    for bp in (390, 768, 1440):
        rects: dict[str, dict[str, int]] = {
            root_id: {"x": 0, "y": 0, "w": bp, "h": 900 if bp == 1440 else (1200 if bp == 768 else 1680)}
        }
        for nid, by_bp in l1_l2_specs.items():
            x, y, w, h = by_bp[bp]
            rects[nid] = {"x": x, "y": y, "w": w, "h": h}
        dom_by_bp[bp] = {
            "viewport_w": bp,
            "scroll_width": bp,
            "rects": rects,
        }
    return dom_by_bp


# ==============================================================================
# 案例 A：Refract — Liquid-Glass CRM Workspace
# ==============================================================================
def build_web_skeleton_refract() -> dict[str, Any]:
    frame_url = "/cases/refract_crm_web/frames/ref_refract_desktop.png"
    bboxes: list[dict[str, Any]] = [
        {"bbox_id": "bb_rf_nav", "eu_id": "eu_L3_rf_sidebar_dock", "label": "液态折射侧栏 · Refract CRM", "x": 20, "y": 14, "w": 290, "h": 740, "role": "nav"},
        {"bbox_id": "bb_rf_quota", "eu_id": "eu_L3_rf_quota_profile", "label": "Q4 配额进度 92% · 个人卡", "x": 20, "y": 758, "w": 290, "h": 128, "role": "nav"},
        {"bbox_id": "bb_rf_header", "eu_id": "eu_L3_rf_header_search", "label": "Leah 问候 · ⌘K 命令检索 · +New deal", "x": 330, "y": 14, "w": 1090, "h": 84, "role": "stage"},
        {"bbox_id": "bb_rf_kpi", "eu_id": "eu_L3_rf_kpi_array", "label": "CRM 四维 KPI + 36% Win rate 阵列 ×4", "x": 330, "y": 108, "w": 1090, "h": 200, "role": "array"},
        {"bbox_id": "bb_rf_rev", "eu_id": "eu_L3_rf_revenue_chart", "label": "Revenue $3.62M 面积对比 (7D/30D/12M)", "x": 330, "y": 322, "w": 686, "h": 444, "role": "split"},
        {"bbox_id": "bb_rf_dialer", "eu_id": "eu_L3_rf_call_desk", "label": "Sofia Brandt 联系卡 & 交互拨号台", "x": 1032, "y": 322, "w": 388, "h": 444, "role": "split"},
        {"bbox_id": "bb_rf_deals", "eu_id": "eu_L3_rf_hot_deals", "label": "Hot deals · Pipeline 跳转", "x": 330, "y": 778, "w": 594, "h": 108, "role": "stage"},
        {"bbox_id": "bb_rf_today", "eu_id": "eu_L3_rf_today_tasks", "label": "Today 环形待办 (1 of 6 done)", "x": 940, "y": 778, "w": 480, "h": 108, "role": "array"},
    ]
    dom = _build_three_breakpoint_rects(
        "eu_L0_rf_workspace",
        {
            "eu_L1_rf_intro": {390: (12, 6, 366, 34), 768: (18, 8, 732, 34), 1440: (20, 8, 1400, 34)},
            "eu_L2_rf_intro_bar": {390: (12, 6, 366, 34), 768: (18, 8, 732, 34), 1440: (20, 8, 1400, 34)},
            "eu_L1_rf_nav": {390: (12, 46, 366, 62), 768: (18, 48, 200, 1120), 1440: (20, 14, 290, 872)},
            "eu_L2_rf_nav_rail": {390: (12, 46, 366, 62), 768: (18, 48, 200, 1120), 1440: (20, 14, 290, 872)},
            "eu_L1_rf_stage": {390: (12, 116, 366, 1540), 768: (234, 48, 516, 1120), 1440: (330, 14, 1090, 872)},
            "eu_L2_rf_topbar": {390: (12, 116, 366, 120), 768: (234, 48, 516, 86), 1440: (330, 14, 1090, 84)},
            "eu_L2_rf_kpi_strip": {390: (12, 244, 366, 420), 768: (234, 144, 516, 260), 1440: (330, 108, 1090, 200)},
            "eu_L2_rf_center_grid": {390: (12, 676, 366, 680), 768: (234, 416, 516, 540), 1440: (330, 322, 1090, 444)},
            "eu_L2_rf_bottom_strip": {390: (12, 1368, 366, 260), 768: (234, 968, 516, 190), 1440: (330, 778, 1090, 108)},
            "eu_L1_rf_overlay": {390: (16, 140, 358, 360), 768: (140, 150, 488, 380), 1440: (420, 160, 580, 420)},
            "eu_L2_rf_dialog_host": {390: (16, 140, 358, 360), 768: (140, 150, 488, 380), 1440: (420, 160, 580, 420)},
        },
    )
    svg = _render_web_skeleton_svg(frame_url, bboxes, rail_x=20, stage_x=330, panel_radius=24)
    return {
        "case_id": "refract_crm_web",
        "modality": "web",
        "duration_sec": None,
        "coverage_ratio": 1.0,
        "breakpoints": [390, 768, 1440],
        "viewport": {"width": 1440, "height": 900, "breakpoints": [390, 768, 1440]},
        "dom": dom,
        "computed_styles": [
            {"id": "rf_cs_ink", "eu_id": "eu_L3_rf_header_search", "property": "color", "value": "#f7f3ef", "token_ref": "rf_surf_ink", "delta_e": 0.0},
            {"id": "rf_cs_glass", "eu_id": "eu_L3_rf_sidebar_dock", "property": "background-color", "value": "rgba(38,31,27,0.68)", "token_ref": "rf_surf_glass_panel", "delta_e": 0.0},
            {"id": "rf_cs_card", "eu_id": "eu_L3_rf_kpi_array", "property": "background-color", "value": "rgba(44,36,32,0.58)", "token_ref": "rf_surf_glass_card", "delta_e": 0.0},
            {"id": "rf_cs_coral", "eu_id": "eu_L3_rf_kpi_array", "property": "color", "value": "#ff6b3d", "token_ref": "rf_surf_coral", "delta_e": 0.0},
            {"id": "rf_cs_em", "eu_id": "eu_L3_rf_kpi_array", "property": "color", "value": "#34d399", "token_ref": "rf_surf_emerald", "delta_e": 0.0},
            {"id": "rf_cs_h1", "eu_id": "eu_L3_rf_header_search", "property": "font-size", "value": "34px", "token_ref": "rf_typo_h1", "delta_e": 0.0},
            {"id": "rf_cs_met", "eu_id": "eu_L3_rf_revenue_chart", "property": "font-size", "value": "38px", "token_ref": "rf_typo_metric", "delta_e": 0.0},
            {"id": "rf_cs_rad", "eu_id": "eu_L3_rf_kpi_array", "property": "border-radius", "value": "24px", "token_ref": "rf_lay_radius", "delta_e": 0.0},
            {"id": "rf_cs_gap", "eu_id": "eu_L3_rf_revenue_chart", "property": "gap", "value": "16px", "token_ref": "rf_lay_gap", "delta_e": 0.0},
            {"id": "rf_cs_dur", "eu_id": "eu_L3_rf_sidebar_dock", "property": "transition-duration", "value": "420ms", "token_ref": "rf_mot_dock", "delta_e": 0.0},
        ],
        "interactive_elements": [
            {"id": "rf_el_skip", "eu_id": "eu_L3_rf_skip_entry", "role": "button", "accessible_name": "Skip intro", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": "rf_el_nav", "eu_id": "eu_L3_rf_sidebar_dock", "role": "link", "accessible_name": "Overview / Pipeline navigation", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": "rf_el_cmd", "eu_id": "eu_L3_rf_header_search", "role": "button", "accessible_name": "Search or jump to", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": "rf_el_range", "eu_id": "eu_L3_rf_revenue_chart", "role": "button", "accessible_name": "Revenue range filter and export", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": "rf_el_dial", "eu_id": "eu_L3_rf_call_desk", "role": "button", "accessible_name": "Call desk dialer", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": "rf_el_dialog", "eu_id": "eu_L3_rf_cmd_dialog", "role": "dialog", "accessible_name": "Command palette and new deal dialog", "states": ["default", "hover", "focus-visible", "active"]},
        ],
        "content_nodes": [
            {"id": "rf_cn_backdrop", "eu_id": "eu_L0_rf_workspace", "content_class": "decoration", "aria_hidden": True, "data_source": None, "children_classes": []},
            {"id": "rf_cn_kpi", "eu_id": "eu_L3_rf_kpi_array", "content_class": "data", "aria_hidden": False, "data_source": "refract.crm.kpis", "children_classes": ["data"]},
            {"id": "rf_cn_rev", "eu_id": "eu_L3_rf_revenue_chart", "content_class": "data", "aria_hidden": False, "data_source": "refract.crm.revenue_series", "children_classes": ["data"]},
            {"id": "rf_cn_calls", "eu_id": "eu_L3_rf_call_desk", "content_class": "data", "aria_hidden": False, "data_source": "refract.crm.call_queue", "children_classes": ["data"]},
        ],
        "segments": [
            {
                "segment_id": "seg_web_desktop",
                "index": 1,
                "t0": 0.0,
                "t1": 1.0,
                "label": "1440×900 液态折射 CRM 全盘骨架",
                "frame_url": frame_url,
                "active_eu_ids": [b["eu_id"] for b in bboxes],
                "bboxes": bboxes,
            }
        ],
        "bboxes": [dict(b, segment_id="seg_web_desktop", color_role=b["role"]) for b in bboxes],
        "skeleton_svg": svg,
    }


def build_eu_tree_refract_crm_web(finalize_fn: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    reg: dict[str, dict[str, Any]] = {
        "surface_atoms": {
            "rf_surf_ink": {"name": "高对比暖白主字色", "kind": "color", "value": "#f7f3ef", "css_var": "--rf-ink"},
            "rf_surf_glass_panel": {"name": "深炭液态折射玻璃面板", "kind": "color", "value": "rgba(38,31,27,0.68)", "css_var": "--rf-glass-panel"},
            "rf_surf_glass_card": {"name": "色散光晕子玻璃卡片", "kind": "color", "value": "rgba(44,36,32,0.58)", "css_var": "--rf-glass-card"},
            "rf_surf_coral": {"name": "暖珊瑚橙主强调色", "kind": "color", "value": "#ff6b3d", "css_var": "--rf-coral"},
            "rf_surf_emerald": {"name": "同比上升翠绿徽标", "kind": "color", "value": "#34d399", "css_var": "--rf-emerald"},
        },
        "typography_atoms": {
            "rf_typo_h1": {"name": "问候主标题字阶", "kind": "font_scale", "value": "clamp(26px, 2.4vw, 34px)", "css_var": "--rf-font-h1"},
            "rf_typo_metric": {"name": "核心指标对齐数字字阶", "kind": "font_scale", "value": "clamp(28px, 2.6vw, 38px)", "css_var": "--rf-font-metric"},
            "rf_typo_body": {"name": "正文与导航字阶", "kind": "font_scale", "value": "13.5px", "css_var": "--rf-font-body"},
            "rf_typo_caption": {"name": "徽章与辅助标签字阶", "kind": "font_scale", "value": "11px", "css_var": "--rf-font-caption"},
        },
        "layout_atoms": {
            "rf_lay_rail_w": {"name": "左侧液态栏宽", "kind": "dimension", "value": "246px", "css_var": "--rf-rail-w"},
            "rf_lay_radius": {"name": "液态卡片圆角", "kind": "radius", "value": "24px", "css_var": "--rf-radius"},
            "rf_lay_gap": {"name": "Bento 玻璃网格间距", "kind": "spacing", "value": "16px", "css_var": "--rf-gap"},
        },
        "motion_atoms": {
            "rf_mot_dock": {"name": "侧栏收展与邻近弹性曲线", "kind": "duration", "value": "420ms", "css_var": "--rf-dur-dock"},
            "rf_mot_smooth": {"name": "图表筛选与卡片折射微动效", "kind": "duration", "value": "240ms", "css_var": "--rf-dur-ui"},
        },
        "evidence_atoms": {
            "ev_rf_dom": {"name": "Refract 三断点 DOM 几何与色散观测快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_refract_desktop.png"},
        },
    }

    nodes: list[dict[str, Any]] = [
        {"eu_id": "eu_L0_rf_workspace", "name": "Refract 液态玻璃 CRM 工作台", "level": "L0", "node_kind": "product.workspace", "parent_id": None, "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [0, 0, 1440, 900], "rendered": True},

        {"eu_id": "eu_L1_rf_intro", "name": "开场与无障碍外壳", "level": "L1", "node_kind": "territory.intro_shell", "parent_id": "eu_L0_rf_workspace", "template_slot": "intro_shell", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [20, 8, 1400, 34]},
        {"eu_id": "eu_L2_rf_intro_bar", "name": "顶层跳转入口区", "level": "L2", "node_kind": "region.intro_strip", "parent_id": "eu_L1_rf_intro", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [20, 8, 1400, 34]},
        {"eu_id": "eu_L3_rf_skip_entry", "name": "直达主区快捷入口", "level": "L3", "entity": True, "node_kind": "component.skip_button", "parent_id": "eu_L2_rf_intro_bar", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [20, 8, 180, 32], "dom_selector": '[data-eu-id="eu_L3_rf_skip_entry"]', "rendered": True},
        {"eu_id": "eu_L4_rf_skip_feat", "name": "键盘焦点直达特征", "level": "L4", "node_kind": "feature.skip_a11y", "parent_id": "eu_L3_rf_skip_entry", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [20, 8, 180, 32]},
        {"eu_id": "eu_L5_rf_skip_atoms", "name": "入口原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_rf_skip_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["rf_surf_ink", "rf_typo_caption", "rf_lay_radius", "ev_rf_dom"]},

        {"eu_id": "eu_L1_rf_nav", "name": "液态折射导航坞", "level": "L1", "node_kind": "territory.nav_dock", "parent_id": "eu_L0_rf_workspace", "template_slot": "nav_dock", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [20, 14, 290, 872], "rendered": True},
        {"eu_id": "eu_L2_rf_nav_rail", "name": "CRM 分组侧边栏容器", "level": "L2", "node_kind": "region.nav_rail", "parent_id": "eu_L1_rf_nav", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [20, 14, 290, 872]},
        {"eu_id": "eu_L3_rf_sidebar_dock", "name": "分组导航与邻近放大坞", "level": "L3", "entity": True, "interaction_density": 3, "node_kind": "component.proximity_rail", "parent_id": "eu_L2_rf_nav_rail", "adaptation_mode": "SPLIT_HIGH_INTERACTION", "envelope_bbox": [20, 14, 290, 740], "dom_selector": '[data-eu-id="eu_L3_rf_sidebar_dock"]', "rendered": True},
        {"eu_id": "eu_L4_rf_dock_proximity", "name": "收起态指针邻近缩放特征", "level": "L4", "motion": True, "node_kind": "feature.proximity_magnify", "parent_id": "eu_L3_rf_sidebar_dock", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [20, 14, 290, 520], "rendered": True},
        {"eu_id": "eu_L5_rf_dock_atoms", "name": "折射侧栏原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_rf_dock_proximity", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["rf_surf_glass_panel", "rf_surf_coral", "rf_typo_body", "rf_lay_rail_w", "rf_mot_dock", "ev_rf_dom"]},
        {"eu_id": "eu_L4_rf_nav_groups", "name": "Workspace/Sales/Insights 路由列表", "level": "L4", "node_kind": "feature.grouped_routes", "parent_id": "eu_L3_rf_sidebar_dock", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [20, 120, 290, 620], "rendered": True},
        {"eu_id": "eu_L5_rf_nav_atoms", "name": "分组路由原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_rf_nav_groups", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["rf_surf_glass_panel", "rf_typo_body", "rf_lay_gap", "ev_rf_dom"]},
        {"eu_id": "eu_L3_rf_quota_profile", "name": "Q4 配额进度 92% 与个人档案卡", "level": "L3", "entity": True, "node_kind": "component.quota_profile", "parent_id": "eu_L2_rf_nav_rail", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [20, 756, 290, 128], "dom_selector": '[data-eu-id="eu_L3_rf_quota_profile"]', "rendered": True},
        {"eu_id": "eu_L4_rf_quota_feat", "name": "季度配额条与账户信息", "level": "L4", "node_kind": "feature.quota_progress", "parent_id": "eu_L3_rf_quota_profile", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [20, 756, 290, 128]},
        {"eu_id": "eu_L5_rf_quota_atoms", "name": "配额卡片原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_rf_quota_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["rf_surf_coral", "rf_typo_caption", "rf_lay_radius", "ev_rf_dom"]},

        {"eu_id": "eu_L1_rf_stage", "name": "Refract 主舞台", "level": "L1", "node_kind": "territory.main_stage", "parent_id": "eu_L0_rf_workspace", "template_slot": "main_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [330, 14, 1090, 872], "rendered": True},
        {"eu_id": "eu_L2_rf_topbar", "name": "主舞台问候与全局检索顶栏", "level": "L2", "node_kind": "region.topbar", "parent_id": "eu_L1_rf_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [330, 14, 1090, 84]},
        {"eu_id": "eu_L3_rf_header_search", "name": "Leah 问候 · ⌘K 搜索与 +New deal", "level": "L3", "entity": True, "node_kind": "component.stage_header", "parent_id": "eu_L2_rf_topbar", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [330, 14, 1090, 84], "dom_selector": '[data-eu-id="eu_L3_rf_header_search"]', "rendered": True},
        {"eu_id": "eu_L4_rf_cmd_trigger", "name": "⌘K 全局跳转触发特征", "level": "L4", "node_kind": "feature.command_trigger", "parent_id": "eu_L3_rf_header_search", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [670, 22, 370, 54], "rendered": True},
        {"eu_id": "eu_L5_rf_header_atoms", "name": "顶栏原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_rf_cmd_trigger", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["rf_surf_ink", "rf_surf_coral", "rf_typo_h1", "rf_lay_radius", "ev_rf_dom"]},

        {"eu_id": "eu_L2_rf_kpi_strip", "name": "顶部 CRM KPI 指标带", "level": "L2", "node_kind": "region.kpi_strip", "parent_id": "eu_L1_rf_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [330, 108, 1090, 200]},
        {"eu_id": "eu_L3_rf_kpi_array", "name": "四维 KPI 与 36% 胜率环阵列宿主", "level": "L3", "entity": True, "node_kind": "component.kpi.array", "parent_id": "eu_L2_rf_kpi_strip", "adaptation_mode": "FOLD_ARRAY", "array_count": 4, "envelope_bbox": [330, 108, 1090, 200], "dom_selector": '[data-eu-id="eu_L3_rf_kpi_array"]', "rendered": True},
        {"eu_id": "eu_L4_rf_kpi_cards", "name": "Sparkline 折线与胜率环形度量特征", "level": "L4", "node_kind": "feature.kpi_spark_ring", "parent_id": "eu_L3_rf_kpi_array", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [330, 108, 1090, 200]},
        {"eu_id": "eu_L5_rf_kpi_atoms", "name": "KPI 阵列原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_rf_kpi_cards", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["rf_surf_glass_card", "rf_surf_emerald", "rf_typo_metric", "rf_lay_radius", "ev_rf_dom"]},

        {"eu_id": "eu_L2_rf_center_grid", "name": "营收趋势与拨号工作区", "level": "L2", "node_kind": "region.center_grid", "parent_id": "eu_L1_rf_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [330, 322, 1090, 444]},
        {"eu_id": "eu_L3_rf_revenue_chart", "name": "Revenue $3.62M 面积对比图表", "level": "L3", "entity": True, "interaction_density": 3, "node_kind": "component.revenue_area", "parent_id": "eu_L2_rf_center_grid", "adaptation_mode": "SPLIT_HIGH_INTERACTION", "envelope_bbox": [330, 322, 686, 444], "dom_selector": '[data-eu-id="eu_L3_rf_revenue_chart"]', "rendered": True},
        {"eu_id": "eu_L4_rf_rev_filter", "name": "7D/30D/12M 时间过滤与同口径 CSV 导出", "level": "L4", "motion": True, "node_kind": "feature.range_csv_filter", "parent_id": "eu_L3_rf_revenue_chart", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [780, 336, 220, 48], "rendered": True},
        {"eu_id": "eu_L5_rf_rev_atoms", "name": "营收图表原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_rf_rev_filter", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["rf_surf_coral", "rf_typo_metric", "rf_lay_gap", "rf_mot_smooth", "ev_rf_dom"]},

        {"eu_id": "eu_L3_rf_call_desk", "name": "Sofia Brandt 联系卡与拨号台", "level": "L3", "entity": True, "interaction_density": 3, "node_kind": "component.call_desk", "parent_id": "eu_L2_rf_center_grid", "adaptation_mode": "SPLIT_HIGH_INTERACTION", "envelope_bbox": [1032, 322, 388, 444], "dom_selector": '[data-eu-id="eu_L3_rf_call_desk"]', "rendered": True},
        {"eu_id": "eu_L4_rf_dialer_ctrl", "name": "队列切换与实时拨号控制特征", "level": "L4", "motion": True, "node_kind": "feature.dialer_queue", "parent_id": "eu_L3_rf_call_desk", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [1032, 540, 388, 226], "rendered": True},
        {"eu_id": "eu_L5_rf_dialer_atoms", "name": "拨号台原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_rf_dialer_ctrl", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["rf_surf_glass_card", "rf_typo_body", "rf_lay_radius", "rf_mot_smooth", "ev_rf_dom"]},

        {"eu_id": "eu_L2_rf_bottom_strip", "name": "底部高优商机与今日任务带", "level": "L2", "node_kind": "region.bottom_strip", "parent_id": "eu_L1_rf_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [330, 778, 1090, 108]},
        {"eu_id": "eu_L3_rf_hot_deals", "name": "Hot deals 商机列表与 Pipeline 入口", "level": "L3", "entity": True, "node_kind": "component.hot_deals", "parent_id": "eu_L2_rf_bottom_strip", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [330, 778, 594, 108], "dom_selector": '[data-eu-id="eu_L3_rf_hot_deals"]', "rendered": True},
        {"eu_id": "eu_L4_rf_pipeline_route", "name": "Pipeline 看板跳转触发特征", "level": "L4", "node_kind": "feature.pipeline_jump", "parent_id": "eu_L3_rf_hot_deals", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [790, 792, 118, 40], "rendered": True},
        {"eu_id": "eu_L5_rf_deals_atoms", "name": "商机列表原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_rf_pipeline_route", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["rf_surf_glass_card", "rf_typo_body", "rf_lay_gap", "ev_rf_dom"]},

        {"eu_id": "eu_L3_rf_today_tasks", "name": "Today 环形待办进度卡", "level": "L3", "entity": True, "node_kind": "component.today_checklist", "parent_id": "eu_L2_rf_bottom_strip", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [940, 778, 480, 108], "dom_selector": '[data-eu-id="eu_L3_rf_today_tasks"]', "rendered": True},
        {"eu_id": "eu_L4_rf_today_ring", "name": "任务勾选联动进度环特征", "level": "L4", "node_kind": "feature.checklist_ring", "parent_id": "eu_L3_rf_today_tasks", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [940, 778, 480, 108]},
        {"eu_id": "eu_L5_rf_today_atoms", "name": "待办进度原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_rf_today_ring", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["rf_surf_coral", "rf_typo_caption", "rf_lay_radius", "ev_rf_dom"]},

        {"eu_id": "eu_L1_rf_overlay", "name": "辅助命令与新建弹窗浮层", "level": "L1", "node_kind": "territory.auxiliary_overlay", "parent_id": "eu_L0_rf_workspace", "template_slot": "auxiliary_overlay", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 160, 580, 420]},
        {"eu_id": "eu_L2_rf_dialog_host", "name": "⌘K 与新建商机模态窗区", "level": "L2", "node_kind": "region.dialog", "parent_id": "eu_L1_rf_overlay", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 160, 580, 420]},
        {"eu_id": "eu_L3_rf_cmd_dialog", "name": "命令检索与商机表单弹窗", "level": "L3", "entity": True, "node_kind": "component.modal_sheet", "parent_id": "eu_L2_rf_dialog_host", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 160, 580, 420], "dom_selector": '[data-eu-id="eu_L3_rf_cmd_dialog"]', "rendered": True},
        {"eu_id": "eu_L4_rf_focus_trap", "name": "模态焦点陷阱与关闭归还特征", "level": "L4", "node_kind": "feature.modal_focus_restore", "parent_id": "eu_L3_rf_cmd_dialog", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 160, 580, 420]},
        {"eu_id": "eu_L5_rf_dialog_atoms", "name": "浮层弹窗原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_rf_focus_trap", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["rf_surf_glass_panel", "rf_typo_body", "rf_lay_radius", "ev_rf_dom"]},
    ]

    edges: list[dict[str, Any]] = [
        {"edge_id": "edge_rf_proximity", "edge_type": "MODULATES_NEIGHBOR", "source_eu_id": "eu_L3_rf_sidebar_dock", "target_eu_id": "eu_L4_rf_nav_groups", "label": "收起侧栏指针邻近放大 (1.34x > 1.18x > 1.0)", "evidence_ref": "ev_rf_dom"},
        {"edge_id": "edge_rf_scroll", "edge_type": "SCROLLS_INDEPENDENTLY", "source_eu_id": "eu_L1_rf_stage", "target_eu_id": "eu_L1_rf_nav", "label": "主舞台独立滚动，左侧液态栏静止不随滚", "evidence_ref": "ev_rf_dom"},
        {"edge_id": "edge_rf_route", "edge_type": "TRIGGERS_STATE", "source_eu_id": "eu_L3_rf_sidebar_dock", "target_eu_id": "eu_L3_rf_hot_deals", "label": "侧栏与 Pipeline 按钮触发看板视图切换", "evidence_ref": "ev_rf_dom"},
        {"edge_id": "edge_rf_filter", "edge_type": "FILTERS_VIEW", "source_eu_id": "eu_L3_rf_revenue_chart", "target_eu_id": "eu_L4_rf_rev_filter", "label": "7D/30D/12M 切换重绘面积图并对齐 CSV 导出", "evidence_ref": "ev_rf_dom"},
        {"edge_id": "edge_rf_focus", "edge_type": "RESTORES_FOCUS", "source_eu_id": "eu_L3_rf_cmd_dialog", "target_eu_id": "eu_L4_rf_cmd_trigger", "label": "⌘K / New deal 弹窗关闭归还触发控件焦点", "evidence_ref": "ev_rf_dom"},
        {"edge_id": "edge_rf_token", "edge_type": "SHARES_TOKEN", "source_eu_id": "eu_L3_rf_kpi_array", "target_eu_id": "eu_L3_rf_call_desk", "label": "共享珊瑚强调色与色散玻璃圆角 Token", "evidence_ref": "ev_rf_dom"},
    ]
    return finalize_fn("tpl_uiux_workspace_v1", "UI/UX 工作台原型", "eu_L0_rf_workspace", nodes, reg, edges)


# ==============================================================================
# 案例 B：Haven — Glass Admin & CRM Workspace
# ==============================================================================
def build_web_skeleton_haven() -> dict[str, Any]:
    frame_url = "/cases/haven_admin_web/frames/ref_haven_desktop.png"
    bboxes: list[dict[str, Any]] = [
        {"bbox_id": "bb_hv_rail", "eu_id": "eu_L3_hv_rail_dock", "label": "极简垂直图标导轨 (Icon Rail)", "x": 48, "y": 60, "w": 108, "h": 804, "role": "nav"},
        {"bbox_id": "bb_hv_tabs", "eu_id": "eu_L3_hv_nav_tabs", "label": "Overview / Sales / Marketing / Support 切页", "x": 170, "y": 60, "w": 1222, "h": 68, "role": "nav"},
        {"bbox_id": "bb_hv_team", "eu_id": "eu_L3_hv_team_card", "label": "Team 在线头像群", "x": 170, "y": 136, "w": 314, "h": 160, "role": "stage"},
        {"bbox_id": "bb_hv_dial", "eu_id": "eu_L3_hv_target_dial", "label": "Quarterly Target 64% 刻度表盘 (-/+/Forecast)", "x": 170, "y": 310, "w": 314, "h": 554, "role": "split"},
        {"bbox_id": "bb_hv_rev", "eu_id": "eu_L3_hv_revenue_area", "label": "Revenue $23.4k / $28k 渐变曲线", "x": 498, "y": 136, "w": 474, "h": 240, "role": "stage"},
        {"bbox_id": "bb_hv_leads", "eu_id": "eu_L3_hv_new_leads", "label": "New Leads 1,270 柱图", "x": 498, "y": 390, "w": 230, "h": 212, "role": "stage"},
        {"bbox_id": "bb_hv_app", "eu_id": "eu_L3_hv_approvals", "label": "Approvals $4,800 待审批流", "x": 742, "y": 390, "w": 230, "h": 212, "role": "stage"},
        {"bbox_id": "bb_hv_sales", "eu_id": "eu_L3_hv_sales_bars", "label": "Sales (k$) 周/月/年柱状图", "x": 498, "y": 616, "w": 474, "h": 248, "role": "stage"},
        {"bbox_id": "bb_hv_kpis", "eu_id": "eu_L3_hv_live_kpis_fold", "label": "实时开关四维 KPI 卡阵列 ×4", "x": 986, "y": 136, "w": 406, "h": 466, "role": "array"},
        {"bbox_id": "bb_hv_call", "eu_id": "eu_L3_hv_call_player", "label": "Discovery Call 音频波形播放器", "x": 986, "y": 616, "w": 406, "h": 248, "role": "split"},
    ]
    dom = _build_three_breakpoint_rects(
        "eu_L0_hv_workspace",
        {
            "eu_L1_hv_intro": {390: (12, 6, 366, 34), 768: (24, 16, 720, 34), 1440: (48, 22, 1344, 34)},
            "eu_L2_hv_intro_shell": {390: (12, 6, 366, 34), 768: (24, 16, 720, 34), 1440: (48, 22, 1344, 34)},
            "eu_L1_hv_nav": {390: (12, 46, 366, 62), 768: (24, 58, 92, 1100), 1440: (48, 60, 108, 804)},
            "eu_L2_hv_icon_rail": {390: (12, 46, 366, 62), 768: (24, 58, 92, 1100), 1440: (48, 60, 108, 804)},
            "eu_L1_hv_stage": {390: (12, 116, 366, 1520), 768: (128, 58, 616, 1100), 1440: (170, 60, 1222, 804)},
            "eu_L2_hv_topbar": {390: (12, 116, 366, 80), 768: (128, 58, 616, 64), 1440: (170, 60, 1222, 68)},
            "eu_L2_hv_left_col": {390: (12, 206, 366, 520), 768: (128, 132, 296, 660), 1440: (170, 136, 314, 728)},
            "eu_L2_hv_center_col": {390: (12, 738, 366, 480), 768: (436, 132, 308, 660), 1440: (498, 136, 474, 728)},
            "eu_L2_hv_right_col": {390: (12, 1230, 366, 400), 768: (128, 804, 616, 340), 1440: (986, 136, 406, 728)},
            "eu_L1_hv_overlay": {390: (16, 150, 358, 340), 768: (140, 160, 488, 360), 1440: (440, 180, 560, 380)},
            "eu_L2_hv_dialog_host": {390: (16, 150, 358, 340), 768: (140, 160, 488, 360), 1440: (440, 180, 560, 380)},
        },
    )
    svg = _render_web_skeleton_svg(frame_url, bboxes, rail_x=48, stage_x=170, panel_radius=30)
    return {
        "case_id": "haven_admin_web",
        "modality": "web",
        "duration_sec": None,
        "coverage_ratio": 1.0,
        "breakpoints": [390, 768, 1440],
        "viewport": {"width": 1440, "height": 900, "breakpoints": [390, 768, 1440]},
        "dom": dom,
        "computed_styles": [
            {"id": "hv_cs_ink", "eu_id": "eu_L3_hv_nav_tabs", "property": "color", "value": "#f4f6fa", "token_ref": "hv_surf_ink", "delta_e": 0.0},
            {"id": "hv_cs_win", "eu_id": "eu_L3_hv_rail_dock", "property": "background-color", "value": "rgba(78,76,74,0.44)", "token_ref": "hv_surf_glass_window", "delta_e": 0.0},
            {"id": "hv_cs_card", "eu_id": "eu_L3_hv_team_card", "property": "background-color", "value": "rgba(92,90,88,0.42)", "token_ref": "hv_surf_glass_card", "delta_e": 0.0},
            {"id": "hv_cs_blue", "eu_id": "eu_L3_hv_target_dial", "property": "color", "value": "#3b82f6", "token_ref": "hv_surf_blue", "delta_e": 0.0},
            {"id": "hv_cs_mint", "eu_id": "eu_L3_hv_live_kpis_fold", "property": "color", "value": "#4ade80", "token_ref": "hv_surf_mint", "delta_e": 0.0},
            {"id": "hv_cs_met", "eu_id": "eu_L3_hv_target_dial", "property": "font-size", "value": "36px", "token_ref": "hv_typo_metric", "delta_e": 0.0},
            {"id": "hv_cs_tit", "eu_id": "eu_L3_hv_team_card", "property": "font-size", "value": "16px", "token_ref": "hv_typo_title", "delta_e": 0.0},
            {"id": "hv_cs_rad", "eu_id": "eu_L3_hv_target_dial", "property": "border-radius", "value": "22px", "token_ref": "hv_lay_radius", "delta_e": 0.0},
            {"id": "hv_cs_gap", "eu_id": "eu_L3_hv_sales_bars", "property": "gap", "value": "14px", "token_ref": "hv_lay_gap", "delta_e": 0.0},
            {"id": "hv_cs_dur", "eu_id": "eu_L3_hv_rail_dock", "property": "transition-duration", "value": "320ms", "token_ref": "hv_mot_rail", "delta_e": 0.0},
        ],
        "interactive_elements": [
            {"id": "hv_el_skip", "eu_id": "eu_L3_hv_skip_entry", "role": "button", "accessible_name": "Skip intro", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": "hv_el_rail", "eu_id": "eu_L3_hv_rail_dock", "role": "link", "accessible_name": "Vertical icon rail", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": "hv_el_tabs", "eu_id": "eu_L3_hv_nav_tabs", "role": "tab", "accessible_name": "Overview Sales Marketing Support tabs", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": "hv_el_dial", "eu_id": "eu_L3_hv_target_dial", "role": "button", "accessible_name": "Quarterly target adjuster", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": "hv_el_app", "eu_id": "eu_L3_hv_approvals", "role": "button", "accessible_name": "Approve pending discount", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": "hv_el_play", "eu_id": "eu_L3_hv_call_player", "role": "button", "accessible_name": "Play discovery call audio", "states": ["default", "hover", "focus-visible", "active"]},
        ],
        "content_nodes": [
            {"id": "hv_cn_backdrop", "eu_id": "eu_L0_hv_workspace", "content_class": "decoration", "aria_hidden": True, "data_source": None, "children_classes": []},
            {"id": "hv_cn_target", "eu_id": "eu_L3_hv_target_dial", "content_class": "data", "aria_hidden": False, "data_source": "haven.okr.quarterly_target", "children_classes": ["data"]},
            {"id": "hv_cn_kpis", "eu_id": "eu_L3_hv_live_kpis_fold", "content_class": "data", "aria_hidden": False, "data_source": "haven.telemetry.live_kpis", "children_classes": ["data"]},
            {"id": "hv_cn_call", "eu_id": "eu_L3_hv_call_player", "content_class": "data", "aria_hidden": False, "data_source": "haven.calls.waveform_track", "children_classes": ["data"]},
        ],
        "segments": [
            {
                "segment_id": "seg_web_desktop",
                "index": 1,
                "t0": 0.0,
                "t1": 1.0,
                "label": "1440×900 空间透射玻璃工作台骨架",
                "frame_url": frame_url,
                "active_eu_ids": [b["eu_id"] for b in bboxes],
                "bboxes": bboxes,
            }
        ],
        "bboxes": [dict(b, segment_id="seg_web_desktop", color_role=b["role"]) for b in bboxes],
        "skeleton_svg": svg,
    }


def build_eu_tree_haven_admin_web(finalize_fn: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    reg: dict[str, dict[str, Any]] = {
        "surface_atoms": {
            "hv_surf_ink": {"name": "冰白高对比主字色", "kind": "color", "value": "#f4f6fa", "css_var": "--hv-ink"},
            "hv_surf_glass_window": {"name": "整窗灰暖高透毛玻璃", "kind": "color", "value": "rgba(78,76,74,0.44)", "css_var": "--hv-glass-window"},
            "hv_surf_glass_card": {"name": "内层透射 Bento 玻璃卡", "kind": "color", "value": "rgba(92,90,88,0.42)", "css_var": "--hv-glass-card"},
            "hv_surf_blue": {"name": "电光蓝核心强调色", "kind": "color", "value": "#3b82f6", "css_var": "--hv-blue"},
            "hv_surf_mint": {"name": "薄荷绿涨势徽标", "kind": "color", "value": "#4ade80", "css_var": "--hv-mint"},
        },
        "typography_atoms": {
            "hv_typo_metric": {"name": "表盘与主指标字阶", "kind": "font_scale", "value": "clamp(26px, 2.5vw, 36px)", "css_var": "--hv-font-metric"},
            "hv_typo_title": {"name": "卡片标题字阶", "kind": "font_scale", "value": "16px", "css_var": "--hv-font-title"},
            "hv_typo_body": {"name": "导航与正文标签字阶", "kind": "font_scale", "value": "13.5px", "css_var": "--hv-font-body"},
            "hv_typo_caption": {"name": "徽章与刻度标签字阶", "kind": "font_scale", "value": "11px", "css_var": "--hv-font-caption"},
        },
        "layout_atoms": {
            "hv_lay_rail_w": {"name": "垂直图标导轨宽度", "kind": "dimension", "value": "68px", "css_var": "--hv-rail-w"},
            "hv_lay_radius": {"name": "毛玻璃卡片圆角", "kind": "radius", "value": "22px", "css_var": "--hv-radius"},
            "hv_lay_gap": {"name": "三栏网格间距", "kind": "spacing", "value": "14px", "css_var": "--hv-gap"},
        },
        "motion_atoms": {
            "hv_mot_rail": {"name": "导轨邻近缩放弹簧时间", "kind": "duration", "value": "320ms", "css_var": "--hv-dur-rail"},
            "hv_mot_tab": {"name": "Tab 切换与审批微动效", "kind": "duration", "value": "220ms", "css_var": "--hv-dur-tab"},
            "hv_mot_dial": {"name": "表盘弧线与波形推进动效", "kind": "duration", "value": "360ms", "css_var": "--hv-dur-dial"},
        },
        "evidence_atoms": {
            "ev_hv_dom": {"name": "Haven 三断点 DOM 几何与空间视窗观测快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_haven_desktop.png"},
        },
    }

    nodes: list[dict[str, Any]] = [
        {"eu_id": "eu_L0_hv_workspace", "name": "Haven 透射空间玻璃工作台", "level": "L0", "node_kind": "product.workspace", "parent_id": None, "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [0, 0, 1440, 900], "rendered": True},

        {"eu_id": "eu_L1_hv_intro", "name": "空间视窗开场外壳", "level": "L1", "node_kind": "territory.intro_shell", "parent_id": "eu_L0_hv_workspace", "template_slot": "intro_shell", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [48, 22, 1344, 34]},
        {"eu_id": "eu_L2_hv_intro_shell", "name": "顶部快捷跳转条", "level": "L2", "node_kind": "region.intro_strip", "parent_id": "eu_L1_hv_intro", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [48, 22, 1344, 34]},
        {"eu_id": "eu_L3_hv_skip_entry", "name": "无障碍跳转主内容入口", "level": "L3", "entity": True, "node_kind": "component.skip_button", "parent_id": "eu_L2_hv_intro_shell", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [48, 22, 180, 34], "dom_selector": '[data-eu-id="eu_L3_hv_skip_entry"]', "rendered": True},
        {"eu_id": "eu_L4_hv_skip_feat", "name": "焦点跳跃特征", "level": "L4", "node_kind": "feature.skip_a11y", "parent_id": "eu_L3_hv_skip_entry", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [48, 22, 180, 34]},
        {"eu_id": "eu_L5_hv_skip_atoms", "name": "跳过入口原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_hv_skip_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["hv_surf_ink", "hv_typo_caption", "hv_lay_radius", "ev_hv_dom"]},

        {"eu_id": "eu_L1_hv_nav", "name": "空间垂直导轨坞", "level": "L1", "node_kind": "territory.nav_dock", "parent_id": "eu_L0_hv_workspace", "template_slot": "nav_dock", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [48, 60, 108, 804], "rendered": True},
        {"eu_id": "eu_L2_hv_icon_rail", "name": "图标轨道容器", "level": "L2", "node_kind": "region.nav_rail", "parent_id": "eu_L1_hv_nav", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [48, 60, 108, 804]},
        {"eu_id": "eu_L3_hv_rail_dock", "name": "垂直图标导轨与 Tooltip 坞", "level": "L3", "entity": True, "interaction_density": 3, "node_kind": "component.icon_rail_dock", "parent_id": "eu_L2_hv_icon_rail", "adaptation_mode": "SPLIT_HIGH_INTERACTION", "envelope_bbox": [48, 60, 108, 804], "dom_selector": '[data-eu-id="eu_L3_hv_rail_dock"]', "rendered": True},
        {"eu_id": "eu_L4_hv_rail_proximity", "name": "导轨邻近放大与气泡标签特征", "level": "L4", "motion": True, "node_kind": "feature.proximity_magnify", "parent_id": "eu_L3_hv_rail_dock", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [48, 60, 108, 620], "rendered": True},
        {"eu_id": "eu_L5_hv_rail_atoms", "name": "图标导轨原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_hv_rail_proximity", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["hv_surf_glass_window", "hv_surf_blue", "hv_typo_caption", "hv_lay_rail_w", "hv_mot_rail", "ev_hv_dom"]},

        {"eu_id": "eu_L1_hv_stage", "name": "Haven 三栏 Bento 主舞台", "level": "L1", "node_kind": "territory.main_stage", "parent_id": "eu_L0_hv_workspace", "template_slot": "main_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [170, 60, 1222, 804], "rendered": True},
        {"eu_id": "eu_L2_hv_topbar", "name": "业务域切页与快捷工具顶栏", "level": "L2", "node_kind": "region.topbar", "parent_id": "eu_L1_hv_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [170, 60, 1222, 68]},
        {"eu_id": "eu_L3_hv_nav_tabs", "name": "Overview/Sales/Marketing/Support 切页栏", "level": "L3", "entity": True, "node_kind": "component.domain_tabs", "parent_id": "eu_L2_hv_topbar", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [170, 60, 1222, 68], "dom_selector": '[data-eu-id="eu_L3_hv_nav_tabs"]', "rendered": True},
        {"eu_id": "eu_L4_hv_tab_switch", "name": "四域联动刷新与 CSV 导出特征", "level": "L4", "motion": True, "node_kind": "feature.domain_filter_export", "parent_id": "eu_L3_hv_nav_tabs", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [170, 60, 640, 68], "rendered": True},
        {"eu_id": "eu_L5_hv_tab_atoms", "name": "顶栏切页原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_hv_tab_switch", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["hv_surf_ink", "hv_surf_blue", "hv_typo_body", "hv_lay_gap", "hv_mot_tab", "ev_hv_dom"]},

        {"eu_id": "eu_L2_hv_left_col", "name": "左栏：团队与季度目标表盘", "level": "L2", "node_kind": "region.left_col", "parent_id": "eu_L1_hv_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [170, 136, 314, 728]},
        {"eu_id": "eu_L3_hv_team_card", "name": "Team 在线头像群与职位浮签", "level": "L3", "entity": True, "node_kind": "component.team_roster", "parent_id": "eu_L2_hv_left_col", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [170, 136, 314, 160], "dom_selector": '[data-eu-id="eu_L3_hv_team_card"]', "rendered": True},
        {"eu_id": "eu_L4_hv_team_avatars", "name": "头像悬停职位提示特征", "level": "L4", "node_kind": "feature.avatar_tooltip", "parent_id": "eu_L3_hv_team_card", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [170, 136, 314, 160]},
        {"eu_id": "eu_L5_hv_team_atoms", "name": "团队卡原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_hv_team_avatars", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["hv_surf_glass_card", "hv_typo_title", "hv_lay_radius", "ev_hv_dom"]},

        {"eu_id": "eu_L3_hv_target_dial", "name": "Quarterly Target 64% 刻度表盘", "level": "L3", "entity": True, "interaction_density": 4, "node_kind": "component.radial_target_dial", "parent_id": "eu_L2_hv_left_col", "adaptation_mode": "SPLIT_HIGH_INTERACTION", "envelope_bbox": [170, 310, 314, 554], "dom_selector": '[data-eu-id="eu_L3_hv_target_dial"]', "rendered": True},
        {"eu_id": "eu_L4_hv_dial_controls", "name": "-/+ 调节 · 预测开关 · 4维圆钮特征", "level": "L4", "motion": True, "node_kind": "feature.dial_controls", "parent_id": "eu_L3_hv_target_dial", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [170, 340, 314, 520], "rendered": True},
        {"eu_id": "eu_L5_hv_dial_atoms", "name": "目标表盘原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_hv_dial_controls", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["hv_surf_blue", "hv_typo_metric", "hv_lay_radius", "hv_mot_dial", "ev_hv_dom"]},

        {"eu_id": "eu_L2_hv_center_col", "name": "中栏：营收、线索、审批与周销柱图", "level": "L2", "node_kind": "region.center_col", "parent_id": "eu_L1_hv_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [498, 136, 474, 728]},
        {"eu_id": "eu_L3_hv_revenue_area", "name": "Revenue $23.4k/$28k 平滑曲线", "level": "L3", "entity": True, "node_kind": "component.revenue_spline", "parent_id": "eu_L2_hv_center_col", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [498, 136, 474, 240], "dom_selector": '[data-eu-id="eu_L3_hv_revenue_area"]', "rendered": True},
        {"eu_id": "eu_L4_hv_rev_range", "name": "Today/Week/Month 曲线切换特征", "level": "L4", "node_kind": "feature.period_toggle", "parent_id": "eu_L3_hv_revenue_area", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [740, 146, 220, 44], "rendered": True},
        {"eu_id": "eu_L5_hv_rev_atoms", "name": "营收曲线原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_hv_rev_range", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["hv_surf_glass_card", "hv_typo_metric", "hv_lay_gap", "ev_hv_dom"]},

        {"eu_id": "eu_L3_hv_new_leads", "name": "New Leads 1,270 +18.2% 柱图", "level": "L3", "entity": True, "node_kind": "component.leads_bars", "parent_id": "eu_L2_hv_center_col", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [498, 390, 230, 212], "dom_selector": '[data-eu-id="eu_L3_hv_new_leads"]', "rendered": True},
        {"eu_id": "eu_L4_hv_leads_bars", "name": "近期新增线索柱状对比特征", "level": "L4", "node_kind": "feature.leads_histogram", "parent_id": "eu_L3_hv_new_leads", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [498, 390, 230, 212]},
        {"eu_id": "eu_L5_hv_leads_atoms", "name": "线索卡原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_hv_leads_bars", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["hv_surf_blue", "hv_typo_metric", "hv_lay_radius", "ev_hv_dom"]},

        {"eu_id": "eu_L3_hv_approvals", "name": "Approvals $4,800 待审批流", "level": "L3", "entity": True, "node_kind": "component.approval_queue", "parent_id": "eu_L2_hv_center_col", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [742, 390, 230, 212], "dom_selector": '[data-eu-id="eu_L3_hv_approvals"]', "rendered": True},
        {"eu_id": "eu_L4_hv_approve_action", "name": "一键批准/驳回队列推进特征", "level": "L4", "motion": True, "node_kind": "feature.approval_action", "parent_id": "eu_L3_hv_approvals", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [742, 480, 230, 110], "rendered": True},
        {"eu_id": "eu_L5_hv_app_atoms", "name": "审批流原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_hv_approve_action", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["hv_surf_glass_card", "hv_typo_body", "hv_lay_radius", "hv_mot_tab", "ev_hv_dom"]},

        {"eu_id": "eu_L3_hv_sales_bars", "name": "Sales (k$) 周/月/年柱状图", "level": "L3", "entity": True, "node_kind": "component.sales_bars", "parent_id": "eu_L2_hv_center_col", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [498, 616, 474, 248], "dom_selector": '[data-eu-id="eu_L3_hv_sales_bars"]', "rendered": True},
        {"eu_id": "eu_L4_hv_sales_filter", "name": "柱图高亮与 Week/Month/Year 切换", "level": "L4", "node_kind": "feature.sales_granularity", "parent_id": "eu_L3_hv_sales_bars", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [740, 626, 220, 40], "rendered": True},
        {"eu_id": "eu_L5_hv_sales_atoms", "name": "周销柱图原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_hv_sales_filter", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["hv_surf_blue", "hv_typo_caption", "hv_lay_gap", "ev_hv_dom"]},

        {"eu_id": "eu_L2_hv_right_col", "name": "右栏：实时 KPI 矩阵与通话播放器", "level": "L2", "node_kind": "region.right_col", "parent_id": "eu_L1_hv_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [986, 136, 406, 728]},
        {"eu_id": "eu_L3_hv_live_kpis_fold", "name": "实时开关 KPI 四卡阵列宿主", "level": "L3", "entity": True, "node_kind": "component.live_kpi.array", "parent_id": "eu_L2_hv_right_col", "adaptation_mode": "FOLD_ARRAY", "array_count": 4, "envelope_bbox": [986, 136, 406, 466], "dom_selector": '[data-eu-id="eu_L3_hv_live_kpis_fold"]', "rendered": True},
        {"eu_id": "eu_L4_hv_kpi_toggles", "name": "LIVE 实时开关与折线脉动特征", "level": "L4", "motion": True, "node_kind": "feature.live_kpi_switches", "parent_id": "eu_L3_hv_live_kpis_fold", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [986, 136, 406, 466]},
        {"eu_id": "eu_L5_hv_kpis_atoms", "name": "实时 KPI 原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_hv_kpi_toggles", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["hv_surf_glass_card", "hv_surf_blue", "hv_surf_mint", "hv_typo_metric", "hv_lay_radius", "hv_mot_tab", "ev_hv_dom"]},

        {"eu_id": "eu_L3_hv_call_player", "name": "Discovery Call 音频波形播放器", "level": "L3", "entity": True, "interaction_density": 3, "node_kind": "component.audio_waveform_player", "parent_id": "eu_L2_hv_right_col", "adaptation_mode": "SPLIT_HIGH_INTERACTION", "envelope_bbox": [986, 616, 406, 248], "dom_selector": '[data-eu-id="eu_L3_hv_call_player"]', "rendered": True},
        {"eu_id": "eu_L4_hv_wave_playback", "name": "播放暂停推进与 1x/1.5x/2x 倍速特征", "level": "L4", "motion": True, "node_kind": "feature.waveform_playback", "parent_id": "eu_L3_hv_call_player", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [986, 660, 406, 200], "rendered": True},
        {"eu_id": "eu_L5_hv_player_atoms", "name": "波形播放器原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_hv_wave_playback", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["hv_surf_blue", "hv_typo_body", "hv_lay_radius", "hv_mot_dial", "ev_hv_dom"]},

        {"eu_id": "eu_L1_hv_overlay", "name": "辅助快捷新建浮层", "level": "L1", "node_kind": "territory.auxiliary_overlay", "parent_id": "eu_L0_hv_workspace", "template_slot": "auxiliary_overlay", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [440, 180, 560, 380]},
        {"eu_id": "eu_L2_hv_dialog_host", "name": "快捷创建模态框容器", "level": "L2", "node_kind": "region.dialog", "parent_id": "eu_L1_hv_overlay", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [440, 180, 560, 380]},
        {"eu_id": "eu_L3_hv_quick_dialog", "name": "新建条目与工作区设置弹窗", "level": "L3", "entity": True, "node_kind": "component.modal_sheet", "parent_id": "eu_L2_hv_dialog_host", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [440, 180, 560, 380], "dom_selector": '[data-eu-id="eu_L3_hv_quick_dialog"]', "rendered": True},
        {"eu_id": "eu_L4_hv_focus_trap", "name": "关闭弹窗焦点归还特征", "level": "L4", "node_kind": "feature.modal_focus_restore", "parent_id": "eu_L3_hv_quick_dialog", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [440, 180, 560, 380]},
        {"eu_id": "eu_L5_hv_dialog_atoms", "name": "弹窗原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_hv_focus_trap", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["hv_surf_glass_window", "hv_typo_body", "hv_lay_radius", "ev_hv_dom"]},
    ]

    edges: list[dict[str, Any]] = [
        {"edge_id": "edge_hv_proximity", "edge_type": "MODULATES_NEIGHBOR", "source_eu_id": "eu_L3_hv_rail_dock", "target_eu_id": "eu_L4_hv_rail_proximity", "label": "垂直图标导轨邻近放大 (1.35x > 1.19x > 1.0)", "evidence_ref": "ev_hv_dom"},
        {"edge_id": "edge_hv_scroll", "edge_type": "SCROLLS_INDEPENDENTLY", "source_eu_id": "eu_L1_hv_stage", "target_eu_id": "eu_L1_hv_nav", "label": "Bento 主舞台独立滚动，左侧导轨静止", "evidence_ref": "ev_hv_dom"},
        {"edge_id": "edge_hv_tabs", "edge_type": "TRIGGERS_STATE", "source_eu_id": "eu_L3_hv_nav_tabs", "target_eu_id": "eu_L3_hv_target_dial", "label": "Overview/Sales/Marketing/Support 切页联动整盘", "evidence_ref": "ev_hv_dom"},
        {"edge_id": "edge_hv_filter", "edge_type": "FILTERS_VIEW", "source_eu_id": "eu_L3_hv_nav_tabs", "target_eu_id": "eu_L3_hv_sales_bars", "label": "业务域筛选切换报表粒度并导出同口径 CSV", "evidence_ref": "ev_hv_dom"},
        {"edge_id": "edge_hv_focus", "edge_type": "RESTORES_FOCUS", "source_eu_id": "eu_L3_hv_quick_dialog", "target_eu_id": "eu_L3_hv_nav_tabs", "label": "快捷新建弹窗关闭归还焦点至触发控件", "evidence_ref": "ev_hv_dom"},
        {"edge_id": "edge_hv_token", "edge_type": "SHARES_TOKEN", "source_eu_id": "eu_L3_hv_target_dial", "target_eu_id": "eu_L3_hv_call_player", "label": "共享电光蓝高亮弧与整窗透射玻璃 Token", "evidence_ref": "ev_hv_dom"},
    ]
    return finalize_fn("tpl_uiux_workspace_v1", "UI/UX 工作台原型", "eu_L0_hv_workspace", nodes, reg, edges)
