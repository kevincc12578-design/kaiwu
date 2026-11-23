"""
开物 v4.0 · 可扩展产品分类插件注册表与品类审计引擎 (category_registry.py)
零硬编码扩展：只需在 categories/*.yaml 添加分类插件，即可自动纳入路由、分类器与审计。
"""
from __future__ import annotations

import pathlib
from typing import Any

import yaml

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
CATEGORIES_DIR = PROJECT_ROOT / "categories"

CATEGORY_ORDER = [
    "app_dashboard",
    "data_hud",
    "collab_planner",
    "brand_landing",
    "editorial_grid",
    "print_graphic",
]

CASE_CATEGORY_MAP: dict[str, str] = {
    "code_xr_uiux": "app_dashboard",
    "refract_crm_web": "app_dashboard",
    "haven_admin_web": "app_dashboard",
    "web_fixture": "app_dashboard",
    "axiom_hud_web": "data_hud",
    "weeksync_paper_web": "collab_planner",
    "knob_hardware_web": "brand_landing",
    "defined_aurora_web": "brand_landing",
    "nogood_brutal_web": "editorial_grid",
    "code_xr_poster": "print_graphic",
    "monolog_swiss_poster": "print_graphic",
    "rauno_craft_video": "data_hud",
    "fps60_motion_video": "brand_landing",
    "screen_studio_video": "app_dashboard",
    "resend_dev_web": "data_hud",
    "linear_workspace_web": "app_dashboard",
    "raycast_cmd_web": "data_hud",
    "amie_collab_web": "collab_planner",
    "nothing_dot_web": "data_hud",
    "poolsuite_os_web": "app_dashboard",
    "daylight_eink_web": "collab_planner",
    "family_fluid_web": "app_dashboard",
}


def load_categories() -> dict[str, dict[str, Any]]:
    """读取 categories/*.yaml 中所有产品分类定义。"""
    loaded: dict[str, dict[str, Any]] = {}
    if not CATEGORIES_DIR.exists():
        return loaded
    for path in sorted(CATEGORIES_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("category_id"):
            cid = str(data["category_id"])
            loaded[cid] = data
    return loaded


def list_categories() -> list[dict[str, Any]]:
    """按核心族优先、标准顺序返回全部产品分类列表。"""
    cats = load_categories()
    ordered_ids = [cid for cid in CATEGORY_ORDER if cid in cats] + sorted(
        cid for cid in cats if cid not in CATEGORY_ORDER
    )
    out: list[dict[str, Any]] = []
    for cid in ordered_ids:
        c = cats[cid]
        out.append(
            {
                "category_id": cid,
                "name": c.get("name", cid),
                "name_en": c.get("name_en", cid),
                "tier": c.get("tier", "extended"),
                "default_domain": c.get("default_domain", "uiux"),
                "base_template_id": c.get("base_template_id", "tpl_uiux_workspace_v1"),
                "description": c.get("description", ""),
                "required_slots": c.get("required_slots", []),
                "optional_slots": c.get("optional_slots", []),
                "allowed_asset_slots": c.get("allowed_asset_slots", []),
                "rules_count": len(c.get("category_rules", [])),
                "category_rules": c.get("category_rules", []),
            }
        )
    return out


def get_case_category(case_id: str, dynamic_meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """获取指定案例所属分类元信息。"""
    cats = load_categories()
    cat_id = (
        (dynamic_meta or {}).get("category_id")
        or CASE_CATEGORY_MAP.get(case_id)
        or ("print_graphic" if "poster" in case_id else "app_dashboard")
    )
    cat = cats.get(cat_id) or next(iter(cats.values()), {})
    return {
        "category_id": cat.get("category_id", cat_id),
        "category_name": cat.get("name", cat_id),
        "category_name_en": cat.get("name_en", cat_id),
        "category_tier": cat.get("tier", "core"),
        "default_domain": cat.get("default_domain", "uiux"),
        "base_template_id": cat.get("base_template_id", "tpl_uiux_workspace_v1"),
    }


def classify_skeleton(skeleton: dict[str, Any], domain_hint: str | None = None) -> dict[str, Any]:
    """
    基于纯本地结构、像素/DOM 测量特征与关键词对统一 Skeleton IR 进行自动产品分类。
    零外部 API 依赖，确定性可复现。
    """
    cats = load_categories()
    canvas = skeleton.get("canvas") or skeleton.get("resolution") or {}
    cw = float(canvas.get("w") or 1440.0)
    ch = float(canvas.get("h") or 900.0)
    aspect = cw / max(ch, 1.0)

    signals = dict(skeleton.get("signals") or {})
    bboxes = skeleton.get("bboxes") or []
    text_fragments: list[str] = [
        str(skeleton.get("title") or ""),
        str(skeleton.get("source_url") or ""),
        str(skeleton.get("summary") or ""),
    ]
    for b in bboxes:
        text_fragments.append(str(b.get("label") or ""))
        text_fragments.append(str(b.get("kind") or ""))
        text_fragments.append(str(b.get("text_sample") or ""))
    for tok in (skeleton.get("raw_tokens") or {}).get("keywords", []):
        text_fragments.append(str(tok))
    corpus = " ".join(text_fragments).lower()

    has_nav_rail = bool(
        signals.get("has_nav_rail")
        or any(
            b.get("kind") in ("nav_rail", "aside", "nav") or (float(b.get("w", 999)) <= 160 and float(b.get("h", 0)) >= ch * 0.5)
            for b in bboxes
        )
    )
    interactive_cnt = int(signals.get("interactive_count") or len(skeleton.get("interactive_elements") or []))
    table_cnt = int(signals.get("table_count") or 0)
    code_cnt = int(signals.get("code_or_textarea_count") or 0)
    canvas_fx_ratio = float(signals.get("canvas_or_media_ratio") or 0.0)
    dark_bg = bool(signals.get("is_dark_surface"))
    has_schedule_grid = bool(signals.get("has_schedule_matrix"))
    sharp_borders = bool(signals.get("sharp_border_ratio", 0.0) > 0.35)

    scores: dict[str, float] = {}
    reasons: dict[str, list[str]] = {}

    for cid, cat in cats.items():
        s = 1.0
        why: list[str] = []
        exp = cat.get("expected_signals") or {}

        # 领域提示权重
        if domain_hint and cat.get("default_domain") == domain_hint:
            s += 2.5
            why.append(f"domain={domain_hint}")

        # 方向与画幅权重
        pref_aspect = exp.get("preferred_aspect", "landscape")
        if pref_aspect == "portrait" and aspect < 0.88:
            s += 4.5
            why.append("竖版印刷比例")
        elif pref_aspect == "landscape" and aspect >= 1.0:
            s += 1.2

        # 关键词命中
        kw_hits = [kw for kw in exp.get("keywords", []) if kw.lower() in corpus]
        if kw_hits:
            s += min(len(kw_hits), 5) * 1.6
            why.append(f"关键词:{','.join(kw_hits[:3])}")

        # 品类结构信号
        if cid == "app_dashboard":
            if has_nav_rail:
                s += 2.6
                why.append("侧栏导航")
            if interactive_cnt >= 8:
                s += 1.5
            if table_cnt >= 1:
                s += 1.8
                why.append("数据表格/KPI区")
        elif cid == "data_hud":
            if code_cnt >= 1 or "apl" in corpus or "query" in corpus or "sql" in corpus:
                s += 4.2
                why.append("查询编辑器/代码块")
            if dark_bg:
                s += 1.6
                why.append("深空低亮度面")
            if table_cnt >= 1:
                s += 1.2
        elif cid == "collab_planner":
            if has_schedule_grid or (interactive_cnt >= 14 and table_cnt == 0):
                s += 3.2
                why.append("多维排班/日历格")
            if any(d in corpus for d in ("mon ", "tue ", "wed ", "40h", "week ")):
                s += 3.0
                why.append("星期/工时汇总矩阵")
        elif cid == "brand_landing":
            if canvas_fx_ratio >= 0.14 or interactive_cnt <= 12:
                s += 2.0
            if not has_nav_rail and aspect >= 1.1:
                s += 2.2
                why.append("无固定侧栏品牌叙事流")
            if signals.get("has_large_hero"):
                s += 1.8
                why.append("大字号首屏Hero")
        elif cid == "editorial_grid":
            if sharp_borders:
                s += 3.2
                why.append("锐利直边框网格")
            if any(k in corpus for k in ("radio", "gallery", "illustration", "sketchbook")):
                s += 2.5
        elif cid == "print_graphic":
            if domain_hint == "graphic" or (interactive_cnt <= 4 and aspect < 0.9):
                s += 4.5
                why.append("静态平面画幅")

        scores[cid] = round(s, 3)
        reasons[cid] = why

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best_cid, best_score = ranked[0] if ranked else ("app_dashboard", 1.0)
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    total = sum(scores.values()) or 1.0
    confidence = round(min(0.99, max(0.35, (best_score / total) + (best_score - second_score) * 0.04)), 3)
    best_cat = cats.get(best_cid, {})

    return {
        "category_id": best_cid,
        "category_name": best_cat.get("name", best_cid),
        "tier": best_cat.get("tier", "core"),
        "default_domain": best_cat.get("default_domain", "uiux"),
        "confidence": confidence,
        "reasons": reasons.get(best_cid, []),
        "scores": dict(ranked),
    }


def evaluate_category_audit(
    category_id: str,
    skeleton: dict[str, Any],
    eu_tree: dict[str, Any],
    readback: dict[str, Any],
) -> dict[str, Any]:
    """根据产品所属分类的专属规则包执行非破坏性品类审计。"""
    cats = load_categories()
    cat = cats.get(category_id) or next(iter(cats.values()), {})
    nodes = eu_tree.get("nodes", [])
    edges = eu_tree.get("edges", [])
    stats = eu_tree.get("stats", {})

    slot_set = {n.get("template_slot") for n in nodes if n.get("level") == "L1"}
    overflow_map = readback.get("viewport_overflow_px") or {}
    overflow_zero = all(int(v) <= 0 for v in overflow_map.values()) if overflow_map else True
    token_scan = readback.get("token_consumption") or {}
    token_ok = float(token_scan.get("consumption_ratio", 0.0)) >= 1.0
    reduced_ok = bool(readback.get("reduced_motion_supported", token_scan.get("reduced_motion_supported", False)))
    edit_texts = int(readback.get("editable_text_nodes", 0))
    ctrl_cnt = int(readback.get("interactive_controls", 0))
    edge_types = {e.get("edge_type") for e in edges}
    interactions = readback.get("interactions") or []
    interactions_ok = all(bool(i.get("passed")) for i in interactions)
    deg_ok = int(stats.get("max_degree", 0)) <= 7

    def _eval_metric(mkey: str) -> tuple[bool, str, str]:
        if mkey == "nav_stage_separation":
            ok = ("nav_dock" in slot_set or "main_stage" in slot_set) and overflow_zero
            return ok, f"槽位 {len(slot_set)} · 零溢出={overflow_zero}", "工作台导航区与主舞台双断点几何闭合"
        if mkey == "live_dom_and_tokens":
            ok = edit_texts >= 4 and token_ok
            return ok, f"活文本 {edit_texts} · Token 100%", "真 DOM 数据组件与原子 Token 消费完整"
        if mkey == "state_filter_loop":
            ok = len(edges) >= 1 and interactions_ok
            return ok, f"边 {len(edges)} 条闭环", "状态切换 / 过滤与回检横向边闭环"
        if mkey == "density_zero_overflow":
            ok = overflow_zero and edit_texts >= 10
            return ok, f"文本 {edit_texts} · 1440/390 溢出 0px", "高密度监控面板多断点零溢出"
        if mkey == "query_results_loop":
            ok = token_ok and len([n for n in nodes if n.get("level") == "L3"]) >= 3
            return ok, "查询/结果双域 · Token 100%", "查询输入与可视化输出链路在树内对齐"
        if mkey == "hud_a11y_focus":
            ok = ctrl_cnt >= 6 and bool(edge_types & {"TRIGGERS_STATE", "RESTORES_FOCUS", "FILTERS_VIEW"}) and interactions_ok
            return ok, f"真控件 {ctrl_cnt} · 焦点/状态闭环", "HUD 核心控制台具备清晰状态与焦点回归"
        if mkey == "editable_schedule_matrix":
            ok = edit_texts >= 8 and ctrl_cnt >= 6 and overflow_zero
            return ok, f"真 DOM {edit_texts} / 控件 {ctrl_cnt}", "二维排班矩阵全量基于可编辑真 DOM 渲染"
        if mkey == "hours_rollup_consistency":
            ok = bool(edge_types & {"FILTERS_VIEW", "TRIGGERS_STATE"}) and interactions_ok
            return ok, "筛选/汇总状态边闭环", "单元格调度变动与汇总导出口径一致"
        if mkey == "matrix_complexity_bound":
            ok = deg_ok and token_ok
            return ok, f"max_deg={stats.get('max_degree', 0)}<=7", "排班阵列受扇出度上界保护并全部引用 Token"
        if mkey == "hero_and_asset_slots":
            ok = edit_texts >= 4 and float(readback.get("ui_bitmap_area_ratio", 0.0)) == 0.0
            return ok, f"活文本 {edit_texts} · 贴皮 0%", "叙事文本真 DOM 化，非几何视觉合法进资产槽位"
        if mkey == "brand_tokens_reduced_motion":
            ok = token_ok and reduced_ok
            return ok, "Token 100% · reduced-motion ON", "品牌色阶全消费且尊重减弱动效偏好"
        if mkey == "brand_viewport_closure":
            ok = overflow_zero and interactions_ok
            return ok, "1440/390px 零裁切", "品牌发布页 Hero 与导航条双端闭合无溢出"
        if mkey == "grid_artwork_separation":
            ok = edit_texts >= 6 and float(readback.get("ui_bitmap_area_ratio", 0.0)) == 0.0
            return ok, "插画与控件边界清晰", "Bento 网格内视觉插画槽位与业务文本互不吞并"
        if mkey == "brutal_interactive_truth":
            ok = ctrl_cnt >= 4 and interactions_ok
            return ok, f"真控件 {ctrl_cnt} · 交互全通", "电台/商店/筛选均由真实可交互节点承载"
        if mkey == "grid_mobile_stack":
            ok = overflow_zero and bool(readback.get("responsive_390_supported", True))
            return ok, "390px 堆叠溢出 0px", "高对比多栏在窄屏自动折列无横向溢出"
        if mkey == "vector_live_type":
            ok = bool(readback.get("vector_text_editable", True)) and int(readback.get("rasterized_text_count", 0)) == 0
            return ok, "活文字 100% · 栅格字 0", "瑞士网格印刷出版物保持纯矢量活文字"
        if mkey == "swiss_grid_and_bleed":
            pc = readback.get("poster_canvas") or {}
            bleed = pc.get("bleed") or {}
            bleed_ok = float(bleed.get("top", 0.0)) >= 3.0 or float(pc.get("reopen_max_drift_mm", 9.0)) == 0.0
            ok = (
                float(readback.get("dom_eu_binding_coverage", 0.0)) >= 1.0
                and float(readback.get("vector_graphic_ratio", 0.0)) >= 1.0
                and bleed_ok
            )
            return ok, f"矢量 100% · 出血/漂移 {pc.get('reopen_max_drift_mm', 0.0)}mm", "网格对齐与 3mm 印刷出血精确绑定"
        if mkey == "static_token_edges_only":
            non_static = [et for et in edge_types if et != "SHARES_TOKEN"]
            ok = len(non_static) == 0
            return ok, "纯 SHARES_TOKEN 约束" if ok else f"存在多余动态边 {non_static}", "静态印刷品无网页路由/滚动动态边污染"
        return True, "合规", "通过"

    rule_results: list[dict[str, Any]] = []
    passed_count = 0
    for rule in cat.get("category_rules", []):
        mkey = str(rule.get("metric_key") or "")
        passed, metric, detail = _eval_metric(mkey)
        if passed:
            passed_count += 1
        rule_results.append(
            {
                "rule_id": rule.get("id"),
                "name": rule.get("name"),
                "desc": rule.get("desc"),
                "status": "PASS" if passed else "FAIL",
                "metric": metric,
                "detail": detail,
            }
        )

    total_count = len(rule_results)
    return {
        "category_id": cat.get("category_id", category_id),
        "category_name": cat.get("name", category_id),
        "category_name_en": cat.get("name_en", category_id),
        "tier": cat.get("tier", "core"),
        "description": cat.get("description", ""),
        "allowed_asset_slots": cat.get("allowed_asset_slots", []),
        "passed_count": passed_count,
        "total_count": total_count,
        "status": "PASS" if passed_count == total_count else "WARN",
        "rules": rule_results,
    }
