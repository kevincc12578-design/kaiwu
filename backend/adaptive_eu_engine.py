"""
开物 v3.4 · 受控自适应语义内核与 Y 型三层正交门禁引擎 (adaptive_eu_engine.py)
核心职责：
  1. 读取 rules/*.yaml (6 模块 × 4 条 = 24 条硬规则) 与 templates/*.yaml (2 原型模板)
  2. 构建模板锚定 + 自适应分裂/折叠/裁剪 L0~L5 语义树与单源双索引 atomic_registry
  3. 动态按 modality + general + domain 激活 12 条正交规则并执行 100% 真实数据结构求值
  4. 驱动三态准入状态机 (BLOCKED / PROVISIONAL / RELEASE_READY) 与假设签认持久化
  5. 提供 /explain/{eu_id} 上下双向解释链与横向 Edge-as-EU 关系组装
  6. 提供全量 24 项反事实异常注入内存沙盒与首障精准归因
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import re
import tempfile
from contextlib import nullcontext
from pathlib import Path
from typing import Any, NamedTuple

import cases_catalog as catalog_mod
import category_registry as cat_reg
import generator_readback as readback_mod
import motion_catalog as motion_mod
import parsers as parsers_mod
import skeleton_extractors as skel_mod
import styles_catalog as styles_mod

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
RULES_DIR = PROJECT_ROOT / "rules"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
CASES_DIR = PROJECT_ROOT / "cases"
LEDGER_PATH = PROJECT_ROOT / "UI与交互EU错误排查台账.md"
VERSION_PATH = PROJECT_ROOT / "VERSION"

PRODUCT_NAME = "开物 · Kaiwu Adaptive-EU Design Workbench"
WORKBENCH_VERSION = (
    VERSION_PATH.read_text(encoding="utf-8").strip() if VERSION_PATH.exists() else "3.4.0"
)
SCHEMA_VERSION = "3.4.0"


# ==============================================================================
# 零外部强依赖 YAML 加载器（优先 PyYAML safe_load，内置标准库回退解析器）
# ==============================================================================
def _parse_scalar(val: str) -> Any:
    s = val.strip()
    if not s:
        return ""
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    if s in ("true", "True"):
        return True
    if s in ("false", "False"):
        return False
    if s in ("null", "None", "~"):
        return None
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part) for part in inner.split(",")]
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        return s


def _fallback_yaml_load(text: str) -> dict[str, Any]:
    """轻量块状 YAML 子集解析器（当环境无 PyYAML 时作为零依赖回退）。"""
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        # 去除行尾非引号内注释
        in_q = False
        cleaned_chars: list[str] = []
        for ch in raw:
            if ch == '"':
                in_q = not in_q
            if ch == "#" and not in_q:
                break
            cleaned_chars.append(ch)
        stripped = "".join(cleaned_chars).rstrip()
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped.lstrip(" ")))

    def parse_block(idx: int, base_indent: int) -> tuple[Any, int]:
        if idx >= len(lines):
            return {}, idx
        if lines[idx][1].startswith("- "):
            arr: list[Any] = []
            while idx < len(lines) and lines[idx][0] == base_indent and lines[idx][1].startswith("- "):
                item_str = lines[idx][1][2:].strip()
                idx += 1
                if not item_str:
                    sub, idx = parse_block(idx, lines[idx][0]) if idx < len(lines) and lines[idx][0] > base_indent else ({}, idx)
                    arr.append(sub)
                elif ":" in item_str and not item_str.startswith('"'):
                    k, v = item_str.split(":", 1)
                    obj: dict[str, Any] = {k.strip(): _parse_scalar(v) if v.strip() else None}
                    if not v.strip() and idx < len(lines) and lines[idx][0] > base_indent:
                        obj[k.strip()], idx = parse_block(idx, lines[idx][0])
                    while idx < len(lines) and lines[idx][0] > base_indent:
                        sub_indent, sub_line = lines[idx]
                        if ":" in sub_line:
                            sk, sv = sub_line.split(":", 1)
                            idx += 1
                            if sv.strip():
                                obj[sk.strip()] = _parse_scalar(sv)
                            elif idx < len(lines) and lines[idx][0] > sub_indent:
                                obj[sk.strip()], idx = parse_block(idx, lines[idx][0])
                            else:
                                obj[sk.strip()] = {}
                        else:
                            idx += 1
                    arr.append(obj)
                else:
                    arr.append(_parse_scalar(item_str))
            return arr, idx

        mapping: dict[str, Any] = {}
        while idx < len(lines) and lines[idx][0] == base_indent and not lines[idx][1].startswith("- "):
            line = lines[idx][1]
            idx += 1
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            key = k.strip().strip('"')
            if v.strip():
                mapping[key] = _parse_scalar(v)
            elif idx < len(lines) and lines[idx][0] > base_indent:
                mapping[key], idx = parse_block(idx, lines[idx][0])
            else:
                mapping[key] = None
        return mapping, idx

    parsed, _ = parse_block(0, lines[0][0] if lines else 0)
    return parsed if isinstance(parsed, dict) else {}


def load_yaml_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except Exception:
        return _fallback_yaml_load(text)


def load_all_rule_modules() -> list[dict[str, Any]]:
    modules: list[dict[str, Any]] = []
    for p in sorted(RULES_DIR.glob("*.yaml")):
        doc = load_yaml_file(p)
        if not doc:
            continue
        doc["_file"] = p.name
        doc["module_id"] = p.stem
        modules.append(doc)
    modules.sort(key=lambda m: (int(m.get("layer_order", 9)), str(m.get("rule_prefix", ""))))
    return modules


def load_all_templates() -> dict[str, dict[str, Any]]:
    templates: dict[str, dict[str, Any]] = {}
    for p in sorted(TEMPLATES_DIR.glob("*.yaml")):
        doc = load_yaml_file(p)
        tid = doc.get("template_id")
        if tid:
            templates[str(tid)] = doc
    return templates


def load_error_ledger() -> list[dict[str, Any]]:
    if not LEDGER_PATH.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("| RES-KW-"):
            continue
        cols = [c.strip() for c in s.strip("|").split("|")]
        if len(cols) < 9:
            continue
        res_id, title, layer, rule_id, preset, symptom, root_cause, fix, status = cols[:9]
        entries.append(
            {
                "res_id": res_id,
                "entry_id": res_id,
                "id": res_id,
                "title": title,
                "layer": layer,
                "rule_id": rule_id,
                "counterfactual_preset": preset,
                "symptom": symptom,
                "root_cause": root_cause,
                "fix": fix,
                "status": status,
            }
        )
    return entries


# ==============================================================================
# 受控自适应 L0~L5 语义树与单源双索引 atomic_registry 构建器
# ==============================================================================
BADGE_MAP: dict[str, str] = {
    "TEMPLATE_ANCHOR": "模板锚定",
    "SPLIT_HIGH_INTERACTION": "⚡分裂·高密交互",
    "FOLD_ARRAY": "📦折叠·阵列",
    "ATOMIC_MOUNT": "L5原子",
    "PRUNE_OPTIONAL_SLOT": "裁剪·可选域",
}


def _finalize_tree(
    template_id: str,
    template_name: str,
    root_id: str,
    raw_nodes: list[dict[str, Any]],
    atomic_registry: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
) -> dict[str, Any]:
    """统一补全 children_ids、level_num、自适应徽标与单源双索引 used_by，并统计树指标。"""
    by_id: dict[str, dict[str, Any]] = {}
    for n in raw_nodes:
        node = copy.deepcopy(n)
        lvl = str(node["level"])
        node["level_num"] = int(lvl[1:])
        node.setdefault("children_ids", [])
        node.setdefault("parent_id", None)
        node.setdefault("template_slot", None)
        node.setdefault("array_count", None)
        node.setdefault("atom_refs", [])
        node.setdefault("evidence_refs", [])
        node.setdefault("verified", True)
        node.setdefault("rendered", False)
        mode = node.get("adaptation_mode", "TEMPLATE_ANCHOR")
        if mode == "FOLD_ARRAY" and node.get("array_count"):
            node["adaptation_badge"] = f"📦折叠·×{node['array_count']}阵列"
        else:
            node["adaptation_badge"] = BADGE_MAP.get(mode, mode)
        by_id[node["eu_id"]] = node

    # 重建父->子列表
    for n in raw_nodes:
        pid = n.get("parent_id")
        if pid and pid in by_id:
            if n["eu_id"] not in by_id[pid]["children_ids"]:
                by_id[pid]["children_ids"].append(n["eu_id"])

    # 重建单源双索引 atomic_registry.used_by 并为节点自动汇总子树内的 evidence_refs
    reg = copy.deepcopy(atomic_registry)
    for sec_dict in reg.values():
        for atom in sec_dict.values():
            atom["used_by"] = []

    atom_lookup: dict[str, tuple[str, dict[str, Any]]] = {}
    for sec_name, sec_dict in reg.items():
        for aid, atom in sec_dict.items():
            atom_lookup[aid] = (sec_name, atom)

    for nid, node in by_id.items():
        if node["level"] == "L5":
            for ref in node.get("atom_refs", []):
                if ref in atom_lookup:
                    sec_name, atom = atom_lookup[ref]
                    if nid not in atom["used_by"]:
                        atom["used_by"].append(nid)
                    if sec_name == "evidence_atoms" and ref not in node["evidence_refs"]:
                        node["evidence_refs"].append(ref)

    # 自底向上传播子树 evidence_refs 和 atom_refs 摘要供 GN-03 verified 核验与前端展示
    def collect_evidence(uid: str) -> list[str]:
        cur = by_id[uid]
        evs = list(cur.get("evidence_refs", []))
        for cid in cur["children_ids"]:
            for e in collect_evidence(cid):
                if e not in evs:
                    evs.append(e)
        cur["evidence_refs"] = evs
        return evs

    if root_id in by_id:
        collect_evidence(root_id)

    ordered_nodes = [by_id[n["eu_id"]] for n in raw_nodes]
    max_deg = max((len(n["children_ids"]) for n in ordered_nodes), default=0)
    l3_entities = [n for n in ordered_nodes if n["level"] == "L3" and n.get("entity", True)]
    adapt_counts: dict[str, int] = {}
    for n in ordered_nodes:
        m = n["adaptation_mode"]
        adapt_counts[m] = adapt_counts.get(m, 0) + 1

    return {
        "template_id": template_id,
        "template_name": template_name,
        "root_id": root_id,
        "stats": {
            "total_nodes": len(ordered_nodes),
            "levels_present": sorted({n["level"] for n in ordered_nodes}),
            "max_child_degree": max_deg,
            "l3_entity_count": len(l3_entities),
            "l3_atom_coverage_ratio": 1.0,
            "edge_count": len(edges),
            "adaptation_counts": adapt_counts,
        },
        "nodes": ordered_nodes,
        "atomic_registry": reg,
        "edges": copy.deepcopy(edges),
    }


def build_eu_tree_code_xr_uiux() -> dict[str, Any]:
    """构建一号主基线案例 Code XR · Glass Workspace 的 L0~L5 自适应语义树。"""
    atomic_registry: dict[str, dict[str, Any]] = {
        "surface_atoms": {
            "surf_ink_walnut": {"name": "墨棕主字色", "kind": "color", "value": "#221611", "css_var": "--ink"},
            "surf_warm_paper": {"name": "暖象牙玻璃卡片色", "kind": "color", "value": "#fff6ef", "css_var": "--paper"},
            "surf_rose_glass": {"name": "豆沙折光侧栏基底", "kind": "color", "value": "#a46755", "css_var": "--rose"},
            "surf_studio_coral": {"name": "工作室珊瑚主强调色", "kind": "color", "value": "#e9644e", "css_var": "--coral"},
            "surf_deep_brick": {"name": "深砖红渐变尾色", "kind": "color", "value": "#b94130", "css_var": "--brick"},
            "surf_soft_green": {"name": "正向增量柔绿胶囊", "kind": "color", "value": "#cfe4cd", "css_var": "--green"},
        },
        "typography_atoms": {
            "typo_display_h1": {"name": "主舞台问候大标题字阶", "kind": "font_scale", "value": "clamp(31px,3.09vw,47px) / 780", "css_var": "--kw-font-display"},
            "typo_card_title": {"name": "模块卡片标题字阶", "kind": "font_scale", "value": "19px / 800", "css_var": "--kw-font-title"},
            "typo_body_ui": {"name": "界面正文与副标字阶", "kind": "font_scale", "value": "13.5px / 620", "css_var": "--kw-font-body"},
            "typo_caption_meta": {"name": "徽章与等宽辅助字阶", "kind": "font_scale", "value": "11px / 760", "css_var": "--kw-font-caption"},
        },
        "layout_atoms": {
            "lay_rail_expanded": {"name": "展开态侧栏宽度", "kind": "dimension", "value": "240px", "css_var": "--kw-rail-expanded"},
            "lay_rail_collapsed": {"name": "收起态交互坞宽度", "kind": "dimension", "value": "66px", "css_var": "--kw-rail-collapsed"},
            "lay_card_radius": {"name": "折光卡片圆角", "kind": "radius", "value": "27px", "css_var": "--radius"},
            "lay_grid_gap": {"name": "双栏与四指标栅格间距", "kind": "spacing", "value": "16px", "css_var": "--gap"},
        },
        "motion_atoms": {
            "mot_spring_curve": {"name": "阻尼弹簧缓动曲线", "kind": "easing", "value": "cubic-bezier(.18,.82,.24,1)", "css_var": "--curve"},
            "mot_rail_transition": {"name": "侧栏收展过渡时长", "kind": "duration", "value": "520ms", "css_var": "--kw-dur-rail"},
            "mot_dock_proximity": {"name": "邻近放大响应时长与增益", "kind": "proximity", "value": "135ms · peak 1.37x · r=108px", "css_var": "--kw-dur-dock"},
            "mot_iris_opening": {"name": "开场虹膜扩开时长", "kind": "duration", "value": "800ms", "css_var": "--kw-dur-iris"},
        },
        "evidence_atoms": {
            "ev_seg01_opening": {"name": "0.00–0.75s 品牌揭幕关键帧证据", "segment_id": "seg_01", "time_range": [0.00, 0.75], "frame": "seg_01_opening_0.10s.png"},
            "ev_seg02_aperture": {"name": "0.75–1.60s 亮区展开与数值稳定证据", "segment_id": "seg_02", "time_range": [0.75, 1.60], "frame": "seg_02_aperture_1.44s.png"},
            "ev_seg03_proximity": {"name": "1.60–2.23s 窄侧栏鼠标邻近放大证据", "segment_id": "seg_03", "time_range": [1.60, 2.23], "frame": "seg_03_proximity_1.83s.png"},
            "ev_seg04_dashboard": {"name": "2.23–3.80s 展开侧栏与首屏证据", "segment_id": "seg_04", "time_range": [2.23, 3.80], "frame": "seg_04_dashboard_2.78s.png"},
            "ev_seg05_scroll": {"name": "3.80–4.85s 主区独立下滚证据", "segment_id": "seg_05", "time_range": [3.80, 4.85], "frame": "seg_05_scroll_4.36s.png"},
            "ev_seg06_analytics": {"name": "4.85–5.689s Analytics 切页证据", "segment_id": "seg_06", "time_range": [4.85, 5.689], "frame": "seg_06_analytics_5.62s.png"},
        },
    }

    def l5(uid: str, parent: str, kind: str, name: str, refs: list[str]) -> dict[str, Any]:
        return {
            "eu_id": uid,
            "name": name,
            "level": "L5",
            "node_kind": f"atom.{kind}",
            "parent_id": parent,
            "adaptation_mode": "ATOMIC_MOUNT",
            "atom_refs": refs,
            "verified": True,
            "rendered": False,
        }

    nodes: list[dict[str, Any]] = [
        # L0 Root
        {
            "eu_id": "eu_L0_codexr_workspace",
            "name": "Code XR · Glass Workspace 全域工作台",
            "level": "L0",
            "node_kind": "product.workspace",
            "parent_id": None,
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [0, 0, 1440, 780],
            "frame_bbox": [0, 380, 1920, 1040],
            "time_range": [0.0, 5.689],
            "segment_ids": ["seg_01", "seg_02", "seg_03", "seg_04", "seg_05", "seg_06"],
            "dom_selector": '[data-eu-id="eu_L0_codexr_workspace"]',
            "rendered": True,
        },
        # ---------------- L1 Slot 1: intro_shell ----------------
        {
            "eu_id": "eu_L1_intro_shell",
            "name": "开场与环境基底领地",
            "level": "L1",
            "node_kind": "territory.intro_shell",
            "parent_id": "eu_L0_codexr_workspace",
            "template_slot": "intro_shell",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [0, 0, 1440, 780],
            "time_range": [0.0, 1.60],
            "segment_ids": ["seg_01", "seg_02"],
            "dom_selector": '[data-eu-id="eu_L3_opening_iris"]',
            "rendered": False,
        },
        {
            "eu_id": "eu_L2_brand_opening",
            "name": "品牌虹膜揭幕区",
            "level": "L2",
            "node_kind": "region.brand_reveal",
            "parent_id": "eu_L1_intro_shell",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [0, 0, 1440, 780],
            "time_range": [0.0, 0.75],
            "segment_ids": ["seg_01"],
        },
        {
            "eu_id": "eu_L3_opening_iris",
            "name": "Code XR 虹膜揭幕与跳过层",
            "level": "L3",
            "entity": True,
            "node_kind": "component.opening_iris",
            "parent_id": "eu_L2_brand_opening",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [0, 0, 1440, 780],
            "time_range": [0.0, 0.75],
            "segment_ids": ["seg_01"],
            "dom_selector": '[data-eu-id="eu_L3_opening_iris"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_iris_reveal",
            "name": "虹膜光圈扩开与可中断跳过特征",
            "level": "L4",
            "node_kind": "feature.iris_reveal",
            "motion": True,
            "parent_id": "eu_L3_opening_iris",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [520, 250, 400, 260],
            "dom_selector": '[data-eu-id="eu_L4_feat_iris_reveal"]',
            "rendered": True,
        },
        l5(
            "eu_L5_opening_atoms",
            "eu_L4_feat_iris_reveal",
            "bundle",
            "开场设计动效证据原子集",
            ["surf_ink_walnut", "typo_display_h1", "lay_card_radius", "mot_iris_opening", "ev_seg01_opening"],
        ),
        {
            "eu_id": "eu_L2_ambient_room",
            "name": "胡桃木室内景深背景区",
            "level": "L2",
            "node_kind": "region.loader",
            "parent_id": "eu_L1_intro_shell",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [0, 0, 1440, 780],
            "time_range": [0.75, 5.689],
            "segment_ids": ["seg_02", "seg_03", "seg_04", "seg_05", "seg_06"],
        },
        {
            "eu_id": "eu_L3_room_backdrop",
            "name": "暖棕木柜室内环境景深层",
            "level": "L3",
            "entity": True,
            "node_kind": "component.ambient_backdrop",
            "parent_id": "eu_L2_ambient_room",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [0, 0, 1440, 780],
            "time_range": [0.75, 5.689],
            "segment_ids": ["seg_02"],
            "dom_selector": '[data-eu-id="eu_L3_room_backdrop"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_ambient_blur",
            "name": "透射玻璃冷暖景深衬底特征",
            "level": "L4",
            "node_kind": "feature.ambient_backdrop",
            "motion": False,
            "parent_id": "eu_L3_room_backdrop",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [0, 0, 1440, 780],
        },
        l5(
            "eu_L5_room_atoms",
            "eu_L4_feat_ambient_blur",
            "bundle",
            "室内背景表面与证据原子集",
            ["surf_ink_walnut", "typo_caption_meta", "lay_grid_gap", "ev_seg02_aperture"],
        ),
        # ---------------- L1 Slot 2: nav_dock ----------------
        {
            "eu_id": "eu_L1_nav_dock",
            "name": "折光侧栏与导航坞领地",
            "level": "L1",
            "node_kind": "territory.nav_dock",
            "parent_id": "eu_L0_codexr_workspace",
            "template_slot": "nav_dock",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [60, 6, 250, 768],
            "frame_bbox": [80, 388, 333, 1024],
            "time_range": [0.75, 5.689],
            "segment_ids": ["seg_02", "seg_03", "seg_04", "seg_05", "seg_06"],
            "dom_selector": '[data-eu-id="eu_L1_nav_dock"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L2_brand_rail_head",
            "name": "侧栏品牌头与收展控制区",
            "level": "L2",
            "node_kind": "region.nav_header",
            "parent_id": "eu_L1_nav_dock",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [63, 8, 244, 72],
            "time_range": [2.23, 5.689],
            "segment_ids": ["seg_04"],
        },
        {
            "eu_id": "eu_L3_brand_header",
            "name": "Code XR 品牌锁排与折叠按钮",
            "level": "L3",
            "entity": True,
            "node_kind": "component.brand_header",
            "parent_id": "eu_L2_brand_rail_head",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [66, 12, 238, 60],
            "time_range": [2.23, 5.689],
            "segment_ids": ["seg_04"],
            "dom_selector": '[data-eu-id="eu_L3_brand_header"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_rail_collapse",
            "name": "240px↔66px 侧栏弹性收展特征",
            "level": "L4",
            "node_kind": "feature.rail_collapse",
            "motion": True,
            "parent_id": "eu_L3_brand_header",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [272, 20, 31, 31],
            "dom_selector": '[data-eu-id="eu_L4_feat_rail_collapse"]',
            "rendered": True,
        },
        l5(
            "eu_L5_brand_rail_atoms",
            "eu_L4_feat_rail_collapse",
            "bundle",
            "侧栏收展布局动效原子集",
            ["surf_rose_glass", "typo_body_ui", "lay_rail_expanded", "mot_rail_transition", "ev_seg04_dashboard"],
        ),
        {
            "eu_id": "eu_L2_collapsed_rail",
            "name": "收起态窄栏高密微交互区",
            "level": "L2",
            "node_kind": "region.command_entry",
            "parent_id": "eu_L1_nav_dock",
            "adaptation_mode": "SPLIT_HIGH_INTERACTION",
            "interaction_density": 4,
            "envelope_bbox": [63, 8, 150, 764],
            "time_range": [1.60, 2.23],
            "segment_ids": ["seg_03"],
        },
        {
            "eu_id": "eu_L3_rail_proximity_dock",
            "name": "收起侧栏 · 鼠标邻近放大交互坞",
            "level": "L3",
            "entity": True,
            "node_kind": "component.proximity_dock",
            "parent_id": "eu_L2_collapsed_rail",
            "adaptation_mode": "SPLIT_HIGH_INTERACTION",
            "interaction_density": 4,
            "envelope_bbox": [63, 8, 148, 760],
            "time_range": [1.60, 2.23],
            "segment_ids": ["seg_03"],
            "dom_selector": '[data-eu-id="eu_L3_rail_proximity_dock"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_proximity_magnify",
            "name": "feature.proximity_magnify · 距离场 1.37x 连续缩放",
            "level": "L4",
            "node_kind": "feature.proximity_magnify",
            "motion": True,
            "parent_id": "eu_L3_rail_proximity_dock",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [66, 70, 142, 260],
            "dom_selector": '[data-eu-id="eu_L4_feat_proximity_magnify"]',
            "rendered": True,
        },
        l5(
            "eu_L5_prox_motion_atoms",
            "eu_L4_feat_proximity_magnify",
            "motion",
            "邻近放大距离场与帧证据原子",
            ["mot_dock_proximity", "mot_spring_curve", "lay_rail_collapsed", "ev_seg03_proximity"],
        ),
        {
            "eu_id": "eu_L4_dock_search_orb",
            "name": "搜索光球子项 (34→46.6px)",
            "level": "L4",
            "node_kind": "feature.dock_search_orb",
            "motion": True,
            "parent_id": "eu_L3_rail_proximity_dock",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [70, 74, 52, 52],
            "dom_selector": '[data-eu-id="eu_L4_dock_search_orb"]',
            "rendered": True,
        },
        l5(
            "eu_L5_dock_orb_atoms",
            "eu_L4_dock_search_orb",
            "surface",
            "搜索光球表面与布局原子",
            ["surf_rose_glass", "lay_rail_collapsed", "mot_dock_proximity", "ev_seg03_proximity"],
        ),
        {
            "eu_id": "eu_L4_dock_active_pill",
            "name": "当前页白色圆底主项 (40→54.8px)",
            "level": "L4",
            "node_kind": "feature.dock_active_backplate",
            "motion": True,
            "parent_id": "eu_L3_rail_proximity_dock",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [68, 144, 58, 58],
            "dom_selector": '[data-eu-id="eu_L4_dock_active_pill"]',
            "rendered": True,
        },
        l5(
            "eu_L5_dock_active_atoms",
            "eu_L4_dock_active_pill",
            "surface",
            "当前页白色圆底表面与字阶原子",
            ["surf_warm_paper", "surf_ink_walnut", "typo_body_ui", "ev_seg03_proximity"],
        ),
        {
            "eu_id": "eu_L4_dock_neighbor_field",
            "name": "相邻导航图标梯度让位与浮签",
            "level": "L4",
            "node_kind": "feature.dock_neighbor_gradient",
            "motion": True,
            "parent_id": "eu_L3_rail_proximity_dock",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [68, 204, 140, 96],
            "dom_selector": '[data-eu-id="eu_L4_dock_neighbor_field"]',
            "rendered": True,
        },
        l5(
            "eu_L5_dock_neighbor_atoms",
            "eu_L4_dock_neighbor_field",
            "typography",
            "邻项浮签排版与动效原子",
            ["typo_caption_meta", "mot_dock_proximity", "ev_seg03_proximity"],
        ),
        {
            "eu_id": "eu_L2_expanded_nav_groups",
            "name": "展开态分组路由与账户底栏区",
            "level": "L2",
            "node_kind": "region.nav_rail",
            "parent_id": "eu_L1_nav_dock",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [63, 134, 240, 636],
            "time_range": [2.23, 5.689],
            "segment_ids": ["seg_04", "seg_05", "seg_06"],
        },
        {
            "eu_id": "eu_L3_nav_route_list",
            "name": "分组导航路由项阵列",
            "level": "L3",
            "entity": True,
            "node_kind": "component.nav_item.array",
            "parent_id": "eu_L2_expanded_nav_groups",
            "adaptation_mode": "FOLD_ARRAY",
            "array_count": 8,
            "envelope_bbox": [68, 138, 230, 468],
            "time_range": [2.23, 5.689],
            "segment_ids": ["seg_04", "seg_06"],
            "dom_selector": '[data-eu-id="eu_L3_nav_route_list"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_route_array",
            "name": "三组八项路由导航同构阵列 ×8",
            "level": "L4",
            "node_kind": "feature.isomorphic_route_array",
            "motion": False,
            "parent_id": "eu_L3_nav_route_list",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [68, 138, 230, 468],
        },
        l5(
            "eu_L5_nav_routes_atoms",
            "eu_L4_feat_route_array",
            "bundle",
            "路由导航阵列原子集",
            ["surf_warm_paper", "typo_body_ui", "lay_rail_expanded", "ev_seg04_dashboard"],
        ),
        {
            "eu_id": "eu_L3_sidebar_footer",
            "name": "通知热标与工作室账户底栏",
            "level": "L3",
            "entity": True,
            "node_kind": "component.account_footer",
            "parent_id": "eu_L2_expanded_nav_groups",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [68, 616, 230, 146],
            "time_range": [2.23, 5.689],
            "segment_ids": ["seg_04"],
            "dom_selector": '[data-eu-id="eu_L3_sidebar_footer"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_account_status",
            "name": "未读计数热标与账户资料触发器",
            "level": "L4",
            "node_kind": "feature.account_badge",
            "motion": False,
            "parent_id": "eu_L3_sidebar_footer",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [68, 616, 230, 146],
        },
        l5(
            "eu_L5_sidebar_footer_atoms",
            "eu_L4_feat_account_status",
            "bundle",
            "侧栏底部账户原子集",
            ["surf_studio_coral", "typo_caption_meta", "lay_rail_expanded", "ev_seg04_dashboard"],
        ),
        # ---------------- L1 Slot 3: main_stage ----------------
        {
            "eu_id": "eu_L1_main_stage",
            "name": "独立滚动折光主舞台领地",
            "level": "L1",
            "node_kind": "territory.main_stage",
            "parent_id": "eu_L0_codexr_workspace",
            "template_slot": "main_stage",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [320, 6, 1066, 768],
            "frame_bbox": [427, 388, 1420, 1024],
            "time_range": [0.75, 5.689],
            "segment_ids": ["seg_02", "seg_04", "seg_05", "seg_06"],
            "dom_selector": '[data-eu-id="eu_L1_main_stage"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L2_dashboard_upper",
            "name": "Dashboard 首屏英雄与议程区",
            "level": "L2",
            "node_kind": "region.hero",
            "parent_id": "eu_L1_main_stage",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [348, 28, 1004, 472],
            "time_range": [0.75, 3.80],
            "segment_ids": ["seg_02", "seg_04"],
        },
        {
            "eu_id": "eu_L3_page_heading",
            "name": "主舞台问候标题与顶栏操作组",
            "level": "L3",
            "entity": True,
            "node_kind": "component.page_heading",
            "parent_id": "eu_L2_dashboard_upper",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [352, 32, 992, 86],
            "time_range": [2.23, 3.80],
            "segment_ids": ["seg_04"],
            "dom_selector": '[data-eu-id="eu_L3_page_heading"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_heading_bar",
            "name": "自适应大字阶问候语与双胶囊动作按钮",
            "level": "L4",
            "node_kind": "feature.heading_actions",
            "motion": False,
            "parent_id": "eu_L3_page_heading",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [352, 32, 992, 86],
        },
        l5(
            "eu_L5_heading_atoms",
            "eu_L4_feat_heading_bar",
            "bundle",
            "顶栏标题排版表面原子集",
            ["surf_ink_walnut", "typo_display_h1", "typo_body_ui", "lay_grid_gap", "ev_seg04_dashboard"],
        ),
        {
            "eu_id": "eu_L3_sprint_hero",
            "name": "Sprint 24 珊瑚红英雄卡",
            "level": "L3",
            "entity": True,
            "node_kind": "component.sprint_hero",
            "parent_id": "eu_L2_dashboard_upper",
            "adaptation_mode": "SPLIT_HIGH_INTERACTION",
            "interaction_density": 3,
            "envelope_bbox": [352, 132, 658, 362],
            "time_range": [0.75, 3.80],
            "segment_ids": ["seg_02", "seg_04"],
            "dom_selector": '[data-eu-id="eu_L3_sprint_hero"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_sprint_copy",
            "name": "斜衬线强调文案与三栏冲刺数字卷轴",
            "level": "L4",
            "node_kind": "feature.sprint_telemetry",
            "motion": True,
            "parent_id": "eu_L3_sprint_hero",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [376, 154, 410, 316],
            "dom_selector": '[data-eu-id="eu_L4_feat_sprint_copy"]',
            "rendered": True,
        },
        l5(
            "eu_L5_sprint_copy_atoms",
            "eu_L4_feat_sprint_copy",
            "bundle",
            "冲刺英雄卡表面字阶动效原子集",
            ["surf_studio_coral", "surf_deep_brick", "typo_display_h1", "lay_card_radius", "mot_spring_curve", "ev_seg02_aperture"],
        ),
        {
            "eu_id": "eu_L4_feat_orbit_ring",
            "name": "68% 矢量环形轨道与进度圆点",
            "level": "L4",
            "node_kind": "feature.orbit_progress_arc",
            "motion": True,
            "parent_id": "eu_L3_sprint_hero",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [760, 186, 200, 200],
            "dom_selector": '[data-eu-id="eu_L4_feat_orbit_ring"]',
            "rendered": True,
        },
        l5(
            "eu_L5_orbit_ring_atoms",
            "eu_L4_feat_orbit_ring",
            "motion",
            "68% 进度环弧线动效原子",
            ["surf_warm_paper", "mot_spring_curve", "ev_seg04_dashboard"],
        ),
        {
            "eu_id": "eu_L3_orbit_avatars_fold",
            "name": "环绕进度环工作室成员头像阵列",
            "level": "L3",
            "entity": True,
            "node_kind": "component.orbit_avatar.array",
            "parent_id": "eu_L2_dashboard_upper",
            "adaptation_mode": "FOLD_ARRAY",
            "array_count": 6,
            "envelope_bbox": [740, 178, 256, 256],
            "time_range": [2.23, 3.80],
            "segment_ids": ["seg_04"],
            "dom_selector": '[data-eu-id="eu_L3_orbit_avatars_fold"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_avatar_orbit_array",
            "name": "极坐标环绕成员头像按钮阵列 ×6",
            "level": "L4",
            "node_kind": "feature.avatar_orbit_array",
            "motion": True,
            "parent_id": "eu_L3_orbit_avatars_fold",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [740, 178, 256, 256],
        },
        l5(
            "eu_L5_orbit_avatars_atoms",
            "eu_L4_feat_avatar_orbit_array",
            "bundle",
            "环绕头像阵列原子集",
            ["surf_warm_paper", "typo_caption_meta", "lay_card_radius", "mot_spring_curve", "ev_seg04_dashboard"],
        ),
        {
            "eu_id": "eu_L3_studio_calendar",
            "name": "November 9 周历与日程卡片",
            "level": "L3",
            "entity": True,
            "node_kind": "component.studio_calendar",
            "parent_id": "eu_L2_dashboard_upper",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [1022, 132, 322, 362],
            "time_range": [2.23, 3.80],
            "segment_ids": ["seg_04"],
            "dom_selector": '[data-eu-id="eu_L3_studio_calendar"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_week_picker",
            "name": "七日切换胶囊条与日程弹窗触发器",
            "level": "L4",
            "node_kind": "feature.week_day_selector",
            "motion": False,
            "parent_id": "eu_L3_studio_calendar",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [1038, 212, 290, 64],
            "dom_selector": '[data-eu-id="eu_L4_feat_week_picker"]',
            "rendered": True,
        },
        l5(
            "eu_L5_calendar_atoms",
            "eu_L4_feat_week_picker",
            "bundle",
            "周历卡片玻璃表面与排版原子集",
            ["surf_warm_paper", "surf_studio_coral", "typo_card_title", "lay_card_radius", "ev_seg04_dashboard"],
        ),
        {
            "eu_id": "eu_L2_kpi_metrics_band",
            "name": "经营四维指标横幅区",
            "level": "L2",
            "node_kind": "region.metric_strip",
            "parent_id": "eu_L1_main_stage",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [348, 504, 1004, 224],
            "time_range": [0.75, 3.80],
            "segment_ids": ["seg_02", "seg_04"],
        },
        {
            "eu_id": "eu_L3_metrics_grid_fold",
            "name": "经营四指标卡片阵列",
            "level": "L3",
            "entity": True,
            "node_kind": "component.metric_card.array",
            "parent_id": "eu_L2_kpi_metrics_band",
            "adaptation_mode": "FOLD_ARRAY",
            "array_count": 4,
            "envelope_bbox": [352, 508, 992, 216],
            "time_range": [0.75, 3.80],
            "segment_ids": ["seg_02", "seg_04"],
            "dom_selector": '[data-eu-id="eu_L3_metrics_grid_fold"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_metric_cards_array",
            "name": "指标数字卷轴与微折线同构阵列 ×4",
            "level": "L4",
            "node_kind": "feature.metric_card_array",
            "motion": True,
            "parent_id": "eu_L3_metrics_grid_fold",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [352, 508, 992, 216],
        },
        l5(
            "eu_L5_metrics_atoms",
            "eu_L4_feat_metric_cards_array",
            "bundle",
            "经营指标阵列设计动效原子集",
            ["surf_warm_paper", "surf_soft_green", "typo_card_title", "lay_grid_gap", "mot_spring_curve", "ev_seg04_dashboard"],
        ),
        {
            "eu_id": "eu_L2_dashboard_lower",
            "name": "Dashboard 下滚快捷动作与收益图表区",
            "level": "L2",
            "node_kind": "region.chart",
            "parent_id": "eu_L1_main_stage",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [348, 190, 1004, 562],
            "time_range": [3.80, 4.85],
            "segment_ids": ["seg_05"],
        },
        {
            "eu_id": "eu_L3_quick_actions_fold",
            "name": "工作室快捷动作阵列",
            "level": "L3",
            "entity": True,
            "node_kind": "component.quick_action.array",
            "parent_id": "eu_L2_dashboard_lower",
            "adaptation_mode": "FOLD_ARRAY",
            "array_count": 6,
            "envelope_bbox": [352, 196, 992, 136],
            "time_range": [3.80, 4.85],
            "segment_ids": ["seg_05"],
            "dom_selector": '[data-eu-id="eu_L3_quick_actions_fold"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_quick_array",
            "name": "三列两行快捷动作胶囊阵列 ×6",
            "level": "L4",
            "node_kind": "feature.quick_action_array",
            "motion": True,
            "parent_id": "eu_L3_quick_actions_fold",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [352, 196, 992, 136],
        },
        l5(
            "eu_L5_quick_atoms",
            "eu_L4_feat_quick_array",
            "bundle",
            "快捷动作阵列玻璃与渐显原子集",
            ["surf_warm_paper", "typo_body_ui", "lay_grid_gap", "mot_spring_curve", "ev_seg05_scroll"],
        ),
        {
            "eu_id": "eu_L3_revenue_chart_card",
            "name": "Revenue 月度利润/成本双柱图卡",
            "level": "L3",
            "entity": True,
            "node_kind": "component.revenue_chart",
            "parent_id": "eu_L2_dashboard_lower",
            "adaptation_mode": "SPLIT_HIGH_INTERACTION",
            "interaction_density": 3,
            "envelope_bbox": [352, 346, 658, 398],
            "time_range": [3.80, 5.689],
            "segment_ids": ["seg_05", "seg_06"],
            "dom_selector": '[data-eu-id="eu_L3_revenue_chart_card"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_range_segments",
            "name": "3/6/12 月区间分段过滤器",
            "level": "L4",
            "node_kind": "feature.range_filter_segments",
            "motion": False,
            "parent_id": "eu_L3_revenue_chart_card",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [690, 362, 196, 42],
            "dom_selector": '[data-eu-id="eu_L4_feat_range_segments"]',
            "rendered": True,
        },
        l5(
            "eu_L5_range_seg_atoms",
            "eu_L4_feat_range_segments",
            "bundle",
            "区间分段器排版与表面原子",
            ["surf_ink_walnut", "typo_caption_meta", "lay_card_radius", "ev_seg05_scroll"],
        ),
        {
            "eu_id": "eu_L4_feat_dual_bars",
            "name": "自适应刻度利润/成本双柱绘图区",
            "level": "L4",
            "node_kind": "feature.dual_bar_plot",
            "motion": True,
            "parent_id": "eu_L3_revenue_chart_card",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [374, 462, 614, 260],
            "dom_selector": '[data-eu-id="eu_L4_feat_dual_bars"]',
            "rendered": True,
        },
        l5(
            "eu_L5_dual_bars_atoms",
            "eu_L4_feat_dual_bars",
            "bundle",
            "双柱图珊瑚/墨棕表面与生长动效原子",
            ["surf_studio_coral", "surf_ink_walnut", "lay_grid_gap", "mot_spring_curve", "ev_seg05_scroll"],
        ),
        {
            "eu_id": "eu_L3_channel_donut_card",
            "name": "$236.8K 四渠道环形分布卡",
            "level": "L3",
            "entity": True,
            "node_kind": "component.channel_donut",
            "parent_id": "eu_L2_dashboard_lower",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [1022, 346, 322, 398],
            "time_range": [3.80, 4.85],
            "segment_ids": ["seg_05"],
            "dom_selector": '[data-eu-id="eu_L3_channel_donut_card"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_conic_donut",
            "name": "四色圆锥渐变环与总额中心读数",
            "level": "L4",
            "node_kind": "feature.conic_donut_wheel",
            "motion": False,
            "parent_id": "eu_L3_channel_donut_card",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [1092, 434, 180, 180],
            "dom_selector": '[data-eu-id="eu_L4_feat_conic_donut"]',
            "rendered": True,
        },
        l5(
            "eu_L5_channel_atoms",
            "eu_L4_feat_conic_donut",
            "bundle",
            "渠道分布环表面排版原子集",
            ["surf_studio_coral", "typo_card_title", "lay_card_radius", "ev_seg05_scroll"],
        ),
        {
            "eu_id": "eu_L2_analytics_stage",
            "name": "Analytics 经营分析路由视图区",
            "level": "L2",
            "node_kind": "region.view",
            "parent_id": "eu_L1_main_stage",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [348, 28, 1004, 724],
            "time_range": [4.85, 5.689],
            "segment_ids": ["seg_06"],
        },
        {
            "eu_id": "eu_L3_analytics_header_csv",
            "name": "Analytics 顶栏与 CSV 报表下载器",
            "level": "L3",
            "entity": True,
            "node_kind": "component.analytics_header",
            "parent_id": "eu_L2_analytics_stage",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [352, 32, 992, 86],
            "time_range": [4.85, 5.689],
            "segment_ids": ["seg_06"],
            "dom_selector": '[data-eu-id="eu_L3_analytics_header_csv"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_csv_export",
            "name": "按当前月份区间导出 CSV 报表特征",
            "level": "L4",
            "node_kind": "feature.csv_report_export",
            "motion": False,
            "parent_id": "eu_L3_analytics_header_csv",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [1172, 48, 170, 46],
            "dom_selector": '[data-eu-id="eu_L4_feat_csv_export"]',
            "rendered": True,
        },
        l5(
            "eu_L5_analytics_head_atoms",
            "eu_L4_feat_csv_export",
            "bundle",
            "Analytics 页头与下载按钮原子集",
            ["surf_ink_walnut", "typo_display_h1", "lay_grid_gap", "ev_seg06_analytics"],
        ),
        {
            "eu_id": "eu_L3_analytics_wide_stage",
            "name": "Analytics 全宽收益图与稳态基线区",
            "level": "L3",
            "entity": True,
            "node_kind": "component.analytics_wide_revenue",
            "parent_id": "eu_L2_analytics_stage",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [352, 346, 992, 398],
            "time_range": [4.85, 5.689],
            "segment_ids": ["seg_06"],
            "dom_selector": '[data-eu-id="eu_L3_analytics_wide_stage"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_wide_revenue",
            "name": "单列全宽收益容器与片尾瞬态数字隔离",
            "level": "L4",
            "node_kind": "feature.wide_revenue_stage",
            "motion": True,
            "parent_id": "eu_L3_analytics_wide_stage",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [352, 346, 992, 398],
        },
        l5(
            "eu_L5_analytics_wide_atoms",
            "eu_L4_feat_wide_revenue",
            "bundle",
            "Analytics 全宽舞台设计动效证据原子集",
            ["surf_warm_paper", "typo_card_title", "lay_card_radius", "mot_spring_curve", "ev_seg06_analytics"],
        ),
        # ---------------- L1 Slot 4: auxiliary_overlay ----------------
        {
            "eu_id": "eu_L1_auxiliary_overlay",
            "name": "模态抽屉与窄屏导航辅助领地",
            "level": "L1",
            "node_kind": "territory.auxiliary_overlay",
            "parent_id": "eu_L0_codexr_workspace",
            "template_slot": "auxiliary_overlay",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [0, 0, 1440, 780],
            "time_range": [2.23, 5.689],
            "segment_ids": ["seg_04"],
            "dom_selector": '[data-eu-id="eu_L3_dialog_sheet"]',
            "rendered": False,
        },
        {
            "eu_id": "eu_L2_modal_dialog_sheet",
            "name": "原生 Dialog 模态弹窗与命令面板区",
            "level": "L2",
            "node_kind": "region.dialog",
            "parent_id": "eu_L1_auxiliary_overlay",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [465, 110, 510, 520],
            "time_range": [2.23, 5.689],
            "segment_ids": ["seg_04"],
        },
        {
            "eu_id": "eu_L3_dialog_sheet",
            "name": "工作室详情/表单模态抽屉",
            "level": "L3",
            "entity": True,
            "node_kind": "component.modal_sheet",
            "parent_id": "eu_L2_modal_dialog_sheet",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [465, 110, 510, 520],
            "time_range": [2.23, 5.689],
            "segment_ids": ["seg_04"],
            "dom_selector": '[data-eu-id="eu_L3_dialog_sheet"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_modal_focus_trap",
            "name": "模态背景模糊与关闭后焦点归还特征",
            "level": "L4",
            "node_kind": "feature.focus_restoration",
            "motion": True,
            "parent_id": "eu_L3_dialog_sheet",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [465, 110, 510, 520],
        },
        l5(
            "eu_L5_dialog_atoms",
            "eu_L4_feat_modal_focus_trap",
            "bundle",
            "模态弹窗表面排版动效原子集",
            ["surf_warm_paper", "typo_card_title", "lay_card_radius", "mot_spring_curve", "ev_seg04_dashboard"],
        ),
        {
            "eu_id": "eu_L2_mobile_responsive_bar",
            "name": "390px 窄屏顶栏与侧滑抽屉区",
            "level": "L2",
            "node_kind": "region.drawer",
            "parent_id": "eu_L1_auxiliary_overlay",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [0, 0, 390, 56],
            "time_range": [2.23, 5.689],
            "segment_ids": ["seg_04"],
        },
        {
            "eu_id": "eu_L3_mobile_top_bar",
            "name": "窄屏粘性导航顶栏",
            "level": "L3",
            "entity": True,
            "node_kind": "component.mobile_bar",
            "parent_id": "eu_L2_mobile_responsive_bar",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [0, 0, 390, 56],
            "time_range": [2.23, 5.689],
            "segment_ids": ["seg_04"],
            "dom_selector": '[data-eu-id="eu_L3_mobile_top_bar"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_feat_responsive_390",
            "name": "<=740px 抽屉导航与零裁切双列重排特征",
            "level": "L4",
            "node_kind": "feature.responsive_reflow_390",
            "motion": False,
            "parent_id": "eu_L3_mobile_top_bar",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [0, 0, 390, 56],
        },
        l5(
            "eu_L5_mobile_atoms",
            "eu_L4_feat_responsive_390",
            "bundle",
            "窄屏顶栏弹性布局原子集",
            ["surf_warm_paper", "typo_caption_meta", "lay_grid_gap", "ev_seg04_dashboard"],
        ),
    ]

    edges: list[dict[str, Any]] = [
        {
            "edge_id": "edge_01_rail_modulates_neighbor",
            "edge_type": "MODULATES_NEIGHBOR",
            "source_eu_id": "eu_L4_feat_proximity_magnify",
            "target_eu_id": "eu_L4_dock_neighbor_field",
            "label": "指针距离场驱动主项 1.37x 放大与邻项梯度让位，离开自动复位",
            "source": "observed",
            "evidence_ref": "ev_seg03_proximity",
            "evidence": {"t0": 1.60, "t1": 2.23, "frame_bbox": [84, 390, 180, 1018]},
        },
        {
            "edge_id": "edge_02_main_scrolls_independently",
            "edge_type": "SCROLLS_INDEPENDENTLY",
            "source_eu_id": "eu_L1_main_stage",
            "target_eu_id": "eu_L1_nav_dock",
            "label": "主舞台纵向独立下滚时左侧玻璃导航栏保持原位静止",
            "source": "observed",
            "evidence_ref": "ev_seg05_scroll",
            "evidence": {"t0": 3.80, "t1": 4.85, "frame_bbox": [427, 388, 1420, 1024]},
        },
        {
            "edge_id": "edge_03_nav_triggers_analytics",
            "edge_type": "TRIGGERS_STATE",
            "source_eu_id": "eu_L3_nav_route_list",
            "target_eu_id": "eu_L3_analytics_wide_stage",
            "label": "侧栏导航切换触发 Dashboard ↔ Analytics 视图状态跃迁并保存滚动位",
            "source": "observed",
            "evidence_ref": "ev_seg06_analytics",
            "evidence": {"t0": 4.85, "t1": 5.689, "frame_bbox": [84, 390, 1800, 1020]},
        },
        {
            "edge_id": "edge_04_range_filters_csv",
            "edge_type": "FILTERS_VIEW",
            "source_eu_id": "eu_L4_feat_range_segments",
            "target_eu_id": "eu_L3_analytics_header_csv",
            "label": "3/6/12 月区间胶囊同步过滤收益柱图数据集与 CSV 报表导出口径",
            "source": "inferred_realized",
            "evidence_ref": "ev_seg05_scroll",
            "evidence": {"t0": 3.80, "t1": 5.689, "frame_bbox": [469, 390, 1320, 990]},
        },
        {
            "edge_id": "edge_05_dialog_restores_focus",
            "edge_type": "RESTORES_FOCUS",
            "source_eu_id": "eu_L3_dialog_sheet",
            "target_eu_id": "eu_L3_studio_calendar",
            "label": "模态日程/命令抽屉关闭后将键盘焦点精准归还触发按钮",
            "source": "inferred_realized",
            "evidence_ref": "ev_seg04_dashboard",
            "evidence": {"t0": 2.23, "t1": 3.80, "frame_bbox": [1360, 550, 430, 480]},
        },
        {
            "edge_id": "edge_06_kpi_shares_token",
            "edge_type": "SHARES_TOKEN",
            "source_eu_id": "eu_L3_metrics_grid_fold",
            "target_eu_id": "eu_L3_analytics_wide_stage",
            "label": "Dashboard 与 Analytics 共享墨棕/暖象牙/珊瑚玻璃设计 Token 与稳态基线",
            "source": "observed",
            "evidence_ref": "ev_seg06_analytics",
            "evidence": {"t0": 2.23, "t1": 5.689, "frame_bbox": [469, 390, 1320, 990]},
        },
    ]

    return _finalize_tree(
        template_id="tpl_uiux_workspace_v1",
        template_name="UI/UX 工作台原型",
        root_id="eu_L0_codexr_workspace",
        raw_nodes=nodes,
        atomic_registry=atomic_registry,
        edges=edges,
    )


def build_eu_tree_code_xr_poster() -> dict[str, Any]:
    """构建二号同源跨领域案例 Code XR · 品牌视觉展板 (ISO A3 · Graphic) 的 L0~L5 自适应语义树。"""
    atomic_registry: dict[str, dict[str, Any]] = {
        "surface_atoms": {
            "ps_surf_paper": {"name": "A3 暖象牙特种纸色", "kind": "color", "value": "#fff6ef", "css_var": "--poster-paper"},
            "ps_surf_ink": {"name": "墨棕主印刷色", "kind": "color", "value": "#221611", "css_var": "--poster-ink"},
            "ps_surf_muted": {"name": "暖棕次级印刷色", "kind": "color", "value": "#5b3e32", "css_var": "--poster-muted"},
            "ps_surf_coral": {"name": "工作室珊瑚主视觉色", "kind": "color", "value": "#e9644e", "css_var": "--poster-coral"},
            "ps_surf_brick": {"name": "深砖红强调色", "kind": "color", "value": "#b94130", "css_var": "--poster-brick"},
            "ps_surf_rose": {"name": "豆沙折光标准色", "kind": "color", "value": "#a46755", "css_var": "--poster-rose"},
            "ps_surf_green": {"name": "柔绿网格信息底色", "kind": "color", "value": "#cfe4cd", "css_var": "--poster-green"},
        },
        "typography_atoms": {
            "ps_typo_display": {"name": "展板主标题字阶", "kind": "font_scale", "size_px": 52, "value": "52px / 800", "css_var": "--poster-font-display"},
            "ps_typo_headline": {"name": "展板副标题与指标字阶", "kind": "font_scale", "size_px": 26, "value": "26px / 800", "css_var": "--poster-font-headline"},
            "ps_typo_body": {"name": "展板导语正文字阶", "kind": "font_scale", "size_px": 14, "value": "14px / 600", "css_var": "--poster-font-body"},
            "ps_typo_caption": {"name": "印前规格注记字阶", "kind": "font_scale", "size_px": 11, "value": "11px / 700", "css_var": "--poster-font-caption"},
        },
        "layout_atoms": {
            "ps_lay_unit_16": {"name": "版块垂直节奏间距", "kind": "spacing", "value": 16, "css_var": "--poster-space-unit"},
            "ps_lay_gap_12": {"name": "栏间视觉间距", "kind": "spacing", "value": 12, "css_var": "--poster-grid-gap"},
            "ps_lay_safe_32": {"name": "安全边距映射单位", "kind": "spacing", "value": 32, "css_var": "--poster-safe-pad"},
        },
        "motion_atoms": {},
        "evidence_atoms": {
            "ps_ev_header": {"name": "A3 源展板页眉区采样锚点", "evidence_bbox": {"x": 12.0, "y": 14.0, "w": 273.0, "h": 28.0}},
            "ps_ev_hero": {"name": "A3 源展板主视觉区采样锚点", "evidence_bbox": {"x": 12.0, "y": 48.0, "w": 273.0, "h": 186.0}},
            "ps_ev_spec": {"name": "A3 源展板色卡与字阶区采样锚点", "evidence_bbox": {"x": 12.0, "y": 242.0, "w": 273.0, "h": 126.0}},
            "ps_ev_footer": {"name": "A3 源展板版权页脚采样锚点", "evidence_bbox": {"x": 12.0, "y": 376.0, "w": 273.0, "h": 32.0}},
        },
    }

    def l5(uid: str, parent: str, name: str, refs: list[str]) -> dict[str, Any]:
        return {
            "eu_id": uid,
            "name": name,
            "level": "L5",
            "node_kind": "atom.graphic_bundle",
            "parent_id": parent,
            "adaptation_mode": "ATOMIC_MOUNT",
            "atom_refs": refs,
            "verified": True,
            "rendered": False,
        }

    # 12 栏瑞士网格精确栏线：margin=12, col=229/12=19.083333, gutter=4
    c8_w = round(8 * (229.0 / 12.0) + 7 * 4.0, 4)   # 180.6667
    c9_x = round(12.0 + c8_w + 4.0, 4)              # 196.6667
    c9_12_w = round(285.0 - c9_x, 4)                # 88.3333
    c7_w = round(7 * (229.0 / 12.0) + 6 * 4.0, 4)   # 157.5833
    c8_x = round(12.0 + c7_w + 4.0, 4)              # 173.5833
    c8_12_w = round(285.0 - c8_x, 4)                # 111.4167
    c6_w = round(6 * (229.0 / 12.0) + 5 * 4.0, 4)   # 134.5
    c7_x = round(12.0 + c6_w + 4.0, 4)              # 150.5
    c7_12_w = round(285.0 - c7_x, 4)                # 134.5

    nodes: list[dict[str, Any]] = [
        {
            "eu_id": "eu_L0_codexr_poster",
            "name": "Code XR · 品牌视觉发布展板 (ISO A3)",
            "level": "L0",
            "node_kind": "product.poster",
            "parent_id": None,
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [0.0, 0.0, 297.0, 420.0],
            "role": "background_material",
            "dom_selector": '[data-eu-id="eu_L0_codexr_poster"]',
            "rendered": True,
        },
        # L1 Slot 1: header_brand
        {
            "eu_id": "eu_L1_poster_header",
            "name": "品牌页眉领地",
            "level": "L1",
            "node_kind": "territory.header_brand",
            "parent_id": "eu_L0_codexr_poster",
            "template_slot": "header_brand",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 14.0, 273.0, 28.0],
            "dom_selector": '[data-eu-id="eu_L1_poster_header"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L2_poster_logo_region",
            "name": "标志与品牌主名版块",
            "level": "L2",
            "source": "parsed",
            "node_kind": "region.logo_lockup",
            "parent_id": "eu_L1_poster_header",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 14.0, c8_w, 28.0],
            "evidence_bbox": {"x": 12.0, "y": 14.0, "w": c8_w, "h": 28.0},
        },
        {
            "eu_id": "eu_L3_poster_logo_lockup",
            "name": "Code XR 矢量标志与标题锁排",
            "level": "L3",
            "entity": True,
            "source": "parsed",
            "carries_text": True,
            "rendered_as": "dom_text",
            "node_kind": "component.logo_lockup",
            "parent_id": "eu_L2_poster_logo_region",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 14.0, c8_w, 28.0],
            "evidence_bbox": {"x": 12.0, "y": 14.0, "w": c8_w, "h": 28.0},
            "dom_selector": '[data-eu-id="eu_L3_poster_logo_lockup"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_poster_logo_align",
            "name": "Col 1–8 左对齐锁排特征",
            "level": "L4",
            "node_kind": "feature.grid_snap_lockup",
            "parent_id": "eu_L3_poster_logo_lockup",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 14.0, c8_w, 28.0],
        },
        l5("eu_L5_poster_logo_atoms", "eu_L4_poster_logo_align", "页眉标志原子集", ["ps_surf_ink", "ps_typo_caption", "ps_lay_gap_12", "ps_ev_header"]),
        {
            "eu_id": "eu_L2_poster_issue_region",
            "name": "版本期号信息版块",
            "level": "L2",
            "source": "parsed",
            "node_kind": "region.issue_meta",
            "parent_id": "eu_L1_poster_header",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [c9_x, 14.0, c9_12_w, 28.0],
            "evidence_bbox": {"x": c9_x, "y": 14.0, "w": c9_12_w, "h": 28.0},
        },
        {
            "eu_id": "eu_L3_poster_issue_meta",
            "name": "Edition R21 期号胶囊",
            "level": "L3",
            "entity": True,
            "source": "parsed",
            "carries_text": True,
            "rendered_as": "dom_text",
            "node_kind": "component.issue_capsule",
            "parent_id": "eu_L2_poster_issue_region",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [c9_x, 14.0, c9_12_w, 28.0],
            "evidence_bbox": {"x": c9_x, "y": 14.0, "w": c9_12_w, "h": 28.0},
            "dom_selector": '[data-eu-id="eu_L3_poster_issue_meta"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_poster_issue_tabular",
            "name": "Col 9–12 右对齐等宽期号特征",
            "level": "L4",
            "node_kind": "feature.tabular_meta",
            "parent_id": "eu_L3_poster_issue_meta",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [c9_x, 14.0, c9_12_w, 28.0],
        },
        l5("eu_L5_poster_issue_atoms", "eu_L4_poster_issue_tabular", "期号胶囊原子集", ["ps_surf_ink", "ps_surf_paper", "ps_typo_caption", "ps_lay_gap_12", "ps_ev_header"]),
        # L1 Slot 2: hero_key_visual
        {
            "eu_id": "eu_L1_poster_hero",
            "name": "主视觉与标题字阶领地",
            "level": "L1",
            "node_kind": "territory.hero_key_visual",
            "parent_id": "eu_L0_codexr_poster",
            "template_slot": "hero_key_visual",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 48.0, 273.0, 186.0],
            "dom_selector": '[data-eu-id="eu_L1_poster_hero"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L2_poster_headline_region",
            "name": "主标题四级字阶版块",
            "level": "L2",
            "source": "parsed",
            "node_kind": "region.headline",
            "parent_id": "eu_L1_poster_hero",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 48.0, c7_w, 186.0],
            "evidence_bbox": {"x": 12.0, "y": 48.0, "w": c7_w, "h": 186.0},
        },
        {
            "eu_id": "eu_L3_poster_headline",
            "name": "主标题、导语与关键数标组合",
            "level": "L3",
            "entity": True,
            "source": "parsed",
            "carries_text": True,
            "rendered_as": "dom_text",
            "node_kind": "component.hero_headline",
            "parent_id": "eu_L2_poster_headline_region",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 48.0, c7_w, 186.0],
            "evidence_bbox": {"x": 12.0, "y": 48.0, "w": c7_w, "h": 186.0},
            "dom_selector": '[data-eu-id="eu_L3_poster_headline"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_poster_type_hierarchy",
            "name": "52/26/14/11px 递减字阶与高对比特征",
            "level": "L4",
            "node_kind": "feature.type_hierarchy",
            "parent_id": "eu_L3_poster_headline",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 56.0, c7_w, 96.0],
            "dom_selector": '[data-eu-id="eu_L4_poster_type_hierarchy"]',
            "rendered": True,
        },
        l5("eu_L5_poster_headline_atoms", "eu_L4_poster_type_hierarchy", "主标题四级字阶原子集", ["ps_surf_ink", "ps_surf_brick", "ps_typo_display", "ps_typo_headline", "ps_typo_body", "ps_lay_unit_16", "ps_ev_hero"]),
        {
            "eu_id": "eu_L2_poster_graphic_region",
            "name": "纯矢量核心几何版块",
            "level": "L2",
            "source": "parsed",
            "node_kind": "region.key_graphic",
            "parent_id": "eu_L1_poster_hero",
            "adaptation_mode": "SPLIT_HIGH_INTERACTION",
            "interaction_density": 3,
            "envelope_bbox": [c8_x, 48.0, c8_12_w, 186.0],
            "evidence_bbox": {"x": c8_x, "y": 48.0, "w": c8_12_w, "h": 186.0},
        },
        {
            "eu_id": "eu_L3_poster_key_graphic",
            "name": "68% 折射圆环纯矢量几何构成",
            "level": "L3",
            "entity": True,
            "source": "parsed",
            "layer_role": "foreground_graphic",
            "rendered_as": "svg_shape",
            "node_kind": "component.vector_key_graphic",
            "parent_id": "eu_L2_poster_graphic_region",
            "adaptation_mode": "SPLIT_HIGH_INTERACTION",
            "interaction_density": 3,
            "envelope_bbox": [c8_x, 48.0, c8_12_w, 186.0],
            "evidence_bbox": {"x": c8_x, "y": 48.0, "w": c8_12_w, "h": 186.0},
            "dom_selector": '[data-eu-id="eu_L3_poster_key_graphic"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_poster_orbit_geometry",
            "name": "SVG 矢量圆弧与 6 极坐标节点图层",
            "level": "L4",
            "node_kind": "feature.vector_orbit_svg",
            "parent_id": "eu_L3_poster_key_graphic",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [c8_x + 8.0, 78.0, c8_12_w - 16.0, 120.0],
            "dom_selector": '[data-eu-id="eu_L4_poster_orbit_geometry"]',
            "rendered": True,
        },
        l5("eu_L5_poster_orbit_atoms", "eu_L4_poster_orbit_geometry", "矢量圆环构成原子集", ["ps_surf_coral", "ps_surf_brick", "ps_surf_paper", "ps_typo_headline", "ps_lay_unit_16", "ps_ev_hero"]),
        {
            "eu_id": "eu_L4_poster_glass_planes",
            "name": "折射半透明叠片与比例题注图层",
            "level": "L4",
            "node_kind": "feature.glass_plane_layer",
            "parent_id": "eu_L3_poster_key_graphic",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [c8_x + 6.0, 54.0, c8_12_w - 12.0, 20.0],
            "dom_selector": '[data-eu-id="eu_L4_poster_glass_planes"]',
            "rendered": True,
        },
        l5("eu_L5_poster_plane_atoms", "eu_L4_poster_glass_planes", "玻璃叠片原子集", ["ps_surf_paper", "ps_typo_caption", "ps_ev_hero"]),
        {
            "eu_id": "eu_L4_poster_bleed_crop",
            "name": "四边 3mm 出血与 12mm 安全框守恒特征",
            "level": "L4",
            "node_kind": "feature.bleed_safe_margin",
            "parent_id": "eu_L3_poster_key_graphic",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [c8_x, 48.0, c8_12_w, 186.0],
            "dom_selector": '[data-eu-id="eu_L4_poster_bleed_crop"]',
            "rendered": True,
        },
        l5("eu_L5_poster_bleed_atoms", "eu_L4_poster_bleed_crop", "出血与安全边距原子集", ["ps_lay_safe_32", "ps_ev_hero"]),
        # L1 Slot 3: spec_grid
        {
            "eu_id": "eu_L1_poster_spec_grid",
            "name": "设计规范与瑞士网格领地",
            "level": "L1",
            "node_kind": "territory.spec_grid",
            "parent_id": "eu_L0_codexr_poster",
            "template_slot": "spec_grid",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 242.0, 273.0, 126.0],
            "dom_selector": '[data-eu-id="eu_L1_poster_spec_grid"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L2_poster_palette_region",
            "name": "品牌标准色卡版块",
            "level": "L2",
            "source": "parsed",
            "node_kind": "region.palette",
            "parent_id": "eu_L1_poster_spec_grid",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 242.0, 273.0, 58.0],
            "evidence_bbox": {"x": 12.0, "y": 242.0, "w": 273.0, "h": 58.0},
        },
        {
            "eu_id": "eu_L3_poster_palette_fold",
            "name": "Code XR 标准色卡阵列",
            "level": "L3",
            "entity": True,
            "source": "parsed",
            "carries_text": True,
            "rendered_as": "dom_text",
            "node_kind": "component.color_swatch.array",
            "parent_id": "eu_L2_poster_palette_region",
            "adaptation_mode": "FOLD_ARRAY",
            "array_count": 4,
            "envelope_bbox": [12.0, 242.0, 273.0, 58.0],
            "evidence_bbox": {"x": 12.0, "y": 242.0, "w": 273.0, "h": 58.0},
            "dom_selector": '[data-eu-id="eu_L3_poster_palette_fold"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_poster_swatch_array",
            "name": "四基准色块与十六进制/对比度同构阵列 ×4",
            "level": "L4",
            "node_kind": "feature.color_swatch_array",
            "parent_id": "eu_L3_poster_palette_fold",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 242.0, 273.0, 58.0],
        },
        l5("eu_L5_poster_palette_atoms", "eu_L4_poster_swatch_array", "四色色卡阵列原子集", ["ps_surf_ink", "ps_surf_paper", "ps_surf_coral", "ps_surf_rose", "ps_typo_caption", "ps_lay_gap_12", "ps_ev_spec"]),
        {
            "eu_id": "eu_L2_poster_specimen_region",
            "name": "字体与数标标本版块",
            "level": "L2",
            "source": "parsed",
            "node_kind": "region.type_specimen",
            "parent_id": "eu_L1_poster_spec_grid",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 306.0, c8_w, 62.0],
            "evidence_bbox": {"x": 12.0, "y": 306.0, "w": c8_w, "h": 62.0},
        },
        {
            "eu_id": "eu_L3_poster_type_specimen",
            "name": "Manrope + Georgia 活文字标本卡",
            "level": "L3",
            "entity": True,
            "source": "parsed",
            "carries_text": True,
            "rendered_as": "dom_text",
            "node_kind": "component.type_specimen",
            "parent_id": "eu_L2_poster_specimen_region",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 306.0, c8_w, 62.0],
            "evidence_bbox": {"x": 12.0, "y": 306.0, "w": c8_w, "h": 62.0},
            "dom_selector": '[data-eu-id="eu_L3_poster_type_specimen"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_poster_live_text_spec",
            "name": "可选中可编辑活文字与等宽数字特征",
            "level": "L4",
            "node_kind": "feature.live_dom_typography",
            "parent_id": "eu_L3_poster_type_specimen",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 306.0, c8_w, 62.0],
        },
        l5("eu_L5_poster_specimen_atoms", "eu_L4_poster_live_text_spec", "字体标本原子集", ["ps_surf_muted", "ps_typo_headline", "ps_typo_body", "ps_lay_gap_12", "ps_ev_spec"]),
        {
            "eu_id": "eu_L2_poster_grid_region",
            "name": "瑞士网格规格版块",
            "level": "L2",
            "source": "parsed",
            "node_kind": "region.grid_overlay",
            "parent_id": "eu_L1_poster_spec_grid",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [c9_x, 306.0, c9_12_w, 62.0],
            "evidence_bbox": {"x": c9_x, "y": 306.0, "w": c9_12_w, "h": 62.0},
        },
        {
            "eu_id": "eu_L3_poster_grid_overlay",
            "name": "12 栏瑞士网格规格与叠层基准卡",
            "level": "L3",
            "entity": True,
            "source": "parsed",
            "carries_text": True,
            "rendered_as": "dom_text",
            "node_kind": "component.grid_spec_card",
            "parent_id": "eu_L2_poster_grid_region",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [c9_x, 306.0, c9_12_w, 62.0],
            "evidence_bbox": {"x": c9_x, "y": 306.0, "w": c9_12_w, "h": 62.0},
            "dom_selector": '[data-eu-id="eu_L3_poster_grid_overlay"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_poster_swiss_grid",
            "name": "12 栏 × 19.08mm + 4mm 槽宽闭合尺寸链特征",
            "level": "L4",
            "node_kind": "feature.swiss_12col_chain",
            "parent_id": "eu_L3_poster_grid_overlay",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [c9_x, 306.0, c9_12_w, 62.0],
        },
        l5("eu_L5_poster_grid_atoms", "eu_L4_poster_swiss_grid", "网格尺寸链原子集", ["ps_surf_green", "ps_surf_ink", "ps_typo_caption", "ps_lay_safe_32", "ps_ev_spec"]),
        # L1 Slot 4: footer_colophon
        {
            "eu_id": "eu_L1_poster_footer",
            "name": "版权与印前页脚领地",
            "level": "L1",
            "node_kind": "territory.footer_colophon",
            "parent_id": "eu_L0_codexr_poster",
            "template_slot": "footer_colophon",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 376.0, 273.0, 32.0],
            "dom_selector": '[data-eu-id="eu_L1_poster_footer"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L2_poster_credits_region",
            "name": "工作室署名版块",
            "level": "L2",
            "source": "parsed",
            "node_kind": "region.credits",
            "parent_id": "eu_L1_poster_footer",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 376.0, c6_w, 32.0],
            "evidence_bbox": {"x": 12.0, "y": 376.0, "w": c6_w, "h": 32.0},
        },
        {
            "eu_id": "eu_L3_poster_credits",
            "name": "Code XR Studio 创作署名栏",
            "level": "L3",
            "entity": True,
            "source": "parsed",
            "carries_text": True,
            "rendered_as": "dom_text",
            "node_kind": "component.studio_credits",
            "parent_id": "eu_L2_poster_credits_region",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 376.0, c6_w, 32.0],
            "evidence_bbox": {"x": 12.0, "y": 376.0, "w": c6_w, "h": 32.0},
            "dom_selector": '[data-eu-id="eu_L3_poster_credits"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_poster_credits_text",
            "name": "Col 1–6 左对齐页脚署名特征",
            "level": "L4",
            "node_kind": "feature.colophon_credits",
            "parent_id": "eu_L3_poster_credits",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [12.0, 376.0, c6_w, 32.0],
        },
        l5("eu_L5_poster_credits_atoms", "eu_L4_poster_credits_text", "署名栏原子集", ["ps_surf_muted", "ps_typo_caption", "ps_lay_gap_12", "ps_ev_footer"]),
        {
            "eu_id": "eu_L2_poster_imprint_region",
            "name": "出版与图层印记版块",
            "level": "L2",
            "source": "parsed",
            "node_kind": "region.imprint",
            "parent_id": "eu_L1_poster_footer",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [c7_x, 376.0, c7_12_w, 32.0],
            "evidence_bbox": {"x": c7_x, "y": 376.0, "w": c7_12_w, "h": 32.0},
        },
        {
            "eu_id": "eu_L3_poster_imprint",
            "name": "印前零栅格文字规格印记",
            "level": "L3",
            "entity": True,
            "source": "parsed",
            "carries_text": True,
            "rendered_as": "dom_text",
            "node_kind": "component.prepress_imprint",
            "parent_id": "eu_L2_poster_imprint_region",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [c7_x, 376.0, c7_12_w, 32.0],
            "evidence_bbox": {"x": c7_x, "y": 376.0, "w": c7_12_w, "h": 32.0},
            "dom_selector": '[data-eu-id="eu_L3_poster_imprint"]',
            "rendered": True,
        },
        {
            "eu_id": "eu_L4_poster_imprint_text",
            "name": "Col 7–12 右对齐出版印记特征",
            "level": "L4",
            "node_kind": "feature.colophon_imprint",
            "parent_id": "eu_L3_poster_imprint",
            "adaptation_mode": "TEMPLATE_ANCHOR",
            "envelope_bbox": [c7_x, 376.0, c7_12_w, 32.0],
        },
        l5("eu_L5_poster_imprint_atoms", "eu_L4_poster_imprint_text", "出版印记原子集", ["ps_surf_muted", "ps_typo_caption", "ps_lay_gap_12", "ps_ev_footer"]),
    ]

    edges: list[dict[str, Any]] = [
        {
            "edge_id": "edge_ps_01_hero_spec_token",
            "edge_type": "SHARES_TOKEN",
            "source_eu_id": "eu_L3_poster_key_graphic",
            "target_eu_id": "eu_L3_poster_palette_fold",
            "label": "主视觉几何构成与色卡网格共享 #221611 / #FFF6EF / #E9644E / #A46755 标准色 Token",
            "evidence_ref": "ps_ev_spec",
        },
        {
            "edge_id": "edge_ps_02_header_footer_token",
            "edge_type": "SHARES_TOKEN",
            "source_eu_id": "eu_L3_poster_logo_lockup",
            "target_eu_id": "eu_L3_poster_credits",
            "label": "品牌页眉与版权页脚共享 11px 注记字阶与 12mm 安全边距基准",
            "evidence_ref": "ps_ev_footer",
        },
    ]

    return _finalize_tree(
        template_id="tpl_graphic_poster_v1",
        template_name="平面海报 / 展板原型",
        root_id="eu_L0_codexr_poster",
        raw_nodes=nodes,
        atomic_registry=atomic_registry,
        edges=edges,
    )


def build_eu_tree_web_fixture() -> dict[str, Any]:
    """构建内置轻量 web 夹具的 L0~L5 自适应语义树（激活 PW-01..04 + GN-01..04 + GU-01..04）。"""
    reg: dict[str, dict[str, Any]] = {
        "surface_atoms": {
            "surf_ink_walnut": {"name": "墨棕字色", "kind": "color", "value": "#221611", "css_var": "--ink"},
            "surf_warm_paper": {"name": "暖象牙底色", "kind": "color", "value": "#fff6ef", "css_var": "--paper"},
        },
        "typography_atoms": {
            "typo_display_h1": {"name": "大标题字阶", "kind": "font_scale", "value": "36px", "css_var": "--kw-font-display"},
            "typo_card_title": {"name": "卡片字阶", "kind": "font_scale", "value": "19px", "css_var": "--kw-font-title"},
        },
        "layout_atoms": {
            "lay_card_radius": {"name": "卡片圆角", "kind": "radius", "value": "27px", "css_var": "--radius"},
            "lay_grid_gap": {"name": "栅格间距", "kind": "spacing", "value": "16px", "css_var": "--gap"},
        },
        "motion_atoms": {
            "mot_rail_transition": {"name": "侧栏过渡", "kind": "duration", "value": "520ms", "css_var": "--kw-dur-rail"},
        },
        "evidence_atoms": {
            "ev_web_dom": {"name": "三断点 DOM 测量快照", "breakpoints": [390, 768, 1440]},
        },
    }
    nodes: list[dict[str, Any]] = [
        {"eu_id": "eu_L0_web_workspace", "name": "Web 夹具工作台", "level": "L0", "node_kind": "product.workspace", "parent_id": None, "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [0, 0, 1440, 900], "rendered": True},
        {"eu_id": "eu_L1_web_intro", "name": "开场外壳", "level": "L1", "node_kind": "territory.intro_shell", "parent_id": "eu_L0_web_workspace", "template_slot": "intro_shell", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [24, 12, 1392, 48]},
        {"eu_id": "eu_L2_web_loader", "name": "加载顶条", "level": "L2", "node_kind": "region.loader", "parent_id": "eu_L1_web_intro", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [24, 12, 1392, 48]},
        {"eu_id": "eu_L3_web_skip_btn", "name": "跳过入口控件", "level": "L3", "entity": True, "node_kind": "component.skip_button", "parent_id": "eu_L2_web_loader", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [24, 12, 180, 44], "dom_selector": '[data-eu-id="eu_L3_web_skip_btn"]', "rendered": True},
        {"eu_id": "eu_L4_web_skip_feat", "name": "无障碍跳转特征", "level": "L4", "node_kind": "feature.skip_a11y", "parent_id": "eu_L3_web_skip_btn", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [24, 12, 180, 44]},
        {"eu_id": "eu_L5_web_skip_atoms", "name": "跳过控件原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_web_skip_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["surf_ink_walnut", "typo_card_title", "lay_grid_gap", "ev_web_dom"]},
        {"eu_id": "eu_L1_web_nav", "name": "导航坞", "level": "L1", "node_kind": "territory.nav_dock", "parent_id": "eu_L0_web_workspace", "template_slot": "nav_dock", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [24, 68, 240, 780]},
        {"eu_id": "eu_L2_web_rail", "name": "侧边导航栏", "level": "L2", "node_kind": "region.nav_rail", "parent_id": "eu_L1_web_nav", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [24, 68, 240, 780]},
        {"eu_id": "eu_L3_web_nav_list", "name": "导航路由组", "level": "L3", "entity": True, "node_kind": "component.nav_item.array", "parent_id": "eu_L2_web_rail", "adaptation_mode": "FOLD_ARRAY", "array_count": 4, "envelope_bbox": [24, 68, 240, 420], "dom_selector": '[data-eu-id="eu_L3_web_nav_list"]', "rendered": True},
        {"eu_id": "eu_L4_web_nav_feat", "name": "路由切换特征", "level": "L4", "node_kind": "feature.route_switch", "motion": True, "parent_id": "eu_L3_web_nav_list", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [24, 68, 240, 420]},
        {"eu_id": "eu_L5_web_nav_atoms", "name": "导航原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_web_nav_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["surf_warm_paper", "typo_display_h1", "lay_card_radius", "mot_rail_transition", "ev_web_dom"]},
        {"eu_id": "eu_L1_web_stage", "name": "主舞台", "level": "L1", "node_kind": "territory.main_stage", "parent_id": "eu_L0_web_workspace", "template_slot": "main_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [280, 68, 1136, 560]},
        {"eu_id": "eu_L2_web_metrics", "name": "指标区域", "level": "L2", "node_kind": "region.metric_strip", "parent_id": "eu_L1_web_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [280, 68, 1136, 240]},
        {"eu_id": "eu_L3_web_kpi_fold", "name": "KPI 阵列宿主", "level": "L3", "entity": True, "node_kind": "component.kpi.array", "parent_id": "eu_L2_web_metrics", "adaptation_mode": "FOLD_ARRAY", "array_count": 4, "envelope_bbox": [280, 68, 1136, 240], "dom_selector": '[data-eu-id="eu_L3_web_kpi_fold"]', "rendered": True},
        {"eu_id": "eu_L4_web_kpi_feat", "name": "KPI 四卡阵列特征", "level": "L4", "node_kind": "feature.kpi_array", "parent_id": "eu_L3_web_kpi_fold", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [280, 68, 1136, 240]},
        {"eu_id": "eu_L5_web_kpi_atoms", "name": "KPI 原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_web_kpi_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["surf_ink_walnut", "surf_warm_paper", "typo_card_title", "lay_card_radius", "ev_web_dom"]},
        {"eu_id": "eu_L1_web_overlay", "name": "辅助浮层", "level": "L1", "node_kind": "territory.auxiliary_overlay", "parent_id": "eu_L0_web_workspace", "template_slot": "auxiliary_overlay", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [24, 120, 480, 320]},
        {"eu_id": "eu_L2_web_dialog", "name": "模态对话框区", "level": "L2", "node_kind": "region.dialog", "parent_id": "eu_L1_web_overlay", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [24, 120, 480, 320]},
        {"eu_id": "eu_L3_web_modal", "name": "详情弹窗", "level": "L3", "entity": True, "node_kind": "component.modal", "parent_id": "eu_L2_web_dialog", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [24, 120, 480, 320], "dom_selector": '[data-eu-id="eu_L3_web_modal"]', "rendered": True},
        {"eu_id": "eu_L4_web_modal_feat", "name": "焦点归还特征", "level": "L4", "node_kind": "feature.focus_return", "parent_id": "eu_L3_web_modal", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [24, 120, 480, 320]},
        {"eu_id": "eu_L5_web_modal_atoms", "name": "弹窗原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_web_modal_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["surf_warm_paper", "typo_card_title", "lay_card_radius", "ev_web_dom"]},
    ]
    edges = [
        {"edge_id": "edge_web_scroll", "edge_type": "SCROLLS_INDEPENDENTLY", "source_eu_id": "eu_L1_web_stage", "target_eu_id": "eu_L1_web_nav", "label": "主舞台独立滚动", "evidence_ref": "ev_web_dom"},
        {"edge_id": "edge_web_state", "edge_type": "TRIGGERS_STATE", "source_eu_id": "eu_L3_web_nav_list", "target_eu_id": "eu_L3_web_kpi_fold", "label": "导航触发视图切换", "evidence_ref": "ev_web_dom"},
        {"edge_id": "edge_web_focus", "edge_type": "RESTORES_FOCUS", "source_eu_id": "eu_L3_web_modal", "target_eu_id": "eu_L3_web_skip_btn", "label": "弹窗关闭焦点归还", "evidence_ref": "ev_web_dom"},
        {"edge_id": "edge_web_token", "edge_type": "SHARES_TOKEN", "source_eu_id": "eu_L3_web_nav_list", "target_eu_id": "eu_L3_web_kpi_fold", "label": "共享表面与间距 Token", "evidence_ref": "ev_web_dom"},
    ]
    return _finalize_tree("tpl_uiux_workspace_v1", "UI/UX 工作台原型", "eu_L0_web_workspace", nodes, reg, edges)


# ==============================================================================
# 假设管理 (AssumptionRecord) 与持久化状态
# ==============================================================================
DEFAULT_ASSUMPTIONS: dict[str, list[dict[str, Any]]] = {
    "code_xr_uiux": [
        {
            "assumption_id": "ASM-XR-01",
            "eu_id": "eu_L3_analytics_wide_stage",
            "subject_ids": ["obs_analytics_tail_reels", "eu_L3_analytics_wide_stage"],
            "title": "片尾 5.62s Analytics 指标卷轴滚动未定值隔离",
            "category": "transient_motion_value",
            "assumed_value": "沿用 Dashboard 已核实稳态基线值（128 / 49 / $42,500 / 99.96%），不把片尾滚动瞬态帧冒充新定值",
            "evidence_gap": "原视频 5.62s 结束前 Analytics 四张指标卡数字仍在翻滚，未出现静止终帧",
            "bound_rule_id": "PV-03",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-XR-02",
            "eu_id": "eu_L3_analytics_header_csv",
            "subject_ids": ["eu_L3_analytics_header_csv", "eu_L4_feat_csv_export"],
            "title": "3 / 6 / 12 月利润成本明细与 CSV 导出口径",
            "category": "unobserved_interaction_payload",
            "assumed_value": "采用 12 个月确定性工作室样本序列跟随区间过滤，并实时生成同口径 CSV 文件下载",
            "evidence_gap": "原片仅展示区间胶囊与 Download report 按钮外观，未录制点击导出的文件内容",
            "bound_rule_id": "GN-03",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-XR-03",
            "eu_id": "eu_L3_room_backdrop",
            "subject_ids": ["eu_L3_room_backdrop"],
            "title": "透射玻璃底层胡桃木室内背景图替代声明",
            "category": "substitute_background_asset",
            "assumed_value": "使用同色温冷暖明暗分布的受控生成环境底图 assets/room.webp 衬托折光玻璃层",
            "evidence_gap": "原视频中玻璃面板与底层室内照片叠加耦合，无法从成片无损分离无界面纯背景图",
            "bound_rule_id": "PV-02",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-XR-04",
            "eu_id": "eu_L4_feat_proximity_magnify",
            "subject_ids": ["eu_L4_feat_proximity_magnify"],
            "title": "收起侧栏鼠标邻近放大精确感应半径与阻尼公式",
            "category": "motion_curve_parameter",
            "assumed_value": "锁定原帧实测峰值倍率 1.37x (40→54.8px)，采用感应半径 108px 与三次 Hermite 平滑曲线实现",
            "evidence_gap": "30fps 连续帧可测得主项与邻项像素尺寸梯度，但无法直接反推源站 JS 内部半径常数",
            "bound_rule_id": "PV-04",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "code_xr_poster": [
        {
            "assumption_id": "ASM-PS-01",
            "eu_id": "eu_L3_poster_palette_fold",
            "subject_ids": ["eu_L3_poster_palette_fold"],
            "title": "屏幕 sRGB 色值向 A3 印前特种纸油墨映射假设",
            "category": "print_color_profile",
            "assumed_value": "以 Code XR 数字基准 HEX (#221611 / #FFF6EF / #E9644E / #A46755) 作为在线展板标准色样",
            "evidence_gap": "源工程为屏幕 RGB 色彩空间，未附带实体纸张 ICC 专色打样文件",
            "bound_rule_id": "PI-03",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-PS-02",
            "eu_id": "eu_L4_poster_bleed_crop",
            "subject_ids": ["eu_L4_poster_bleed_crop"],
            "title": "ISO 216 A3 展板四边 3mm 出血与 12mm 安全框印前契约",
            "category": "prepress_bleed_spec",
            "assumed_value": "按国际单张海报通用印前标准设定 3mm 四边出血与 12mm 安全边距",
            "evidence_gap": "数字视觉源稿不含实体裁切刀版说明，按 tpl_graphic_poster_v1 标准契约锚定",
            "bound_rule_id": "GG-01",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "web_fixture": [],
    **catalog_mod.EXTRA_DEFAULT_ASSUMPTIONS,
    **styles_mod.STYLE_DEFAULT_ASSUMPTIONS,
    **motion_mod.MOTION_DEFAULT_ASSUMPTIONS,
}

_ASSUMPTION_MEMORY_STATE: dict[str, dict[str, dict[str, Any]]] = {}


def _write_bytes_atomically(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    stream = tempfile.NamedTemporaryFile(
        mode="wb", dir=path.parent, prefix=f".{path.stem}-",
        suffix=".tmp", delete=False,
    )
    temporary = Path(stream.name)
    try:
        with stream:
            stream.write(value)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _write_json_atomically(path: Path, value: Any) -> None:
    _write_bytes_atomically(path, json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8"))


def _state_file_for_case(case_id: str) -> Path:
    return CASES_DIR / case_id / "assumptions_state.json"


def get_case_assumptions(case_id: str) -> list[dict[str, Any]]:
    with parsers_mod.CASE_FILES_LOCK:
        default_list = DEFAULT_ASSUMPTIONS.get(case_id)
        if default_list is None:
            imported = parsers_mod.load_imported_case(case_id)
            default_list = (imported or {}).get("assumptions", [])
        if case_id == "web_fixture":
            state_map = _ASSUMPTION_MEMORY_STATE.get(case_id, {})
        else:
            try:
                state_map = json.loads(_state_file_for_case(case_id).read_text(encoding="utf-8"))
            except (FileNotFoundError, UnicodeError, json.JSONDecodeError):
                state_map = {}
    base = copy.deepcopy(default_list)
    if not isinstance(state_map, dict):
        state_map = {}
    for item in base:
        saved = state_map.get(item["assumption_id"])
        if isinstance(saved, dict):
            item["status"] = saved.get("status", item["status"])
            item["confirmed_at"] = saved.get("confirmed_at")
    return base


def update_case_assumptions(case_id: str, assumption_id: str, action: str) -> list[dict[str, Any]]:
    act = (action or "confirm").lower()
    if act not in {"confirm", "confirm_all", "reset"}:
        raise ValueError(f"Unknown assumption action: {action}")
    apply_to_all = (
        act == "confirm_all" or assumption_id in ("ALL", "all")
        or (act == "reset" and not assumption_id)
    )

    with parsers_mod.CASE_FILES_LOCK:
        _get_case_meta(case_id)
        current = get_case_assumptions(case_id)
        if not apply_to_all and not any(item["assumption_id"] == assumption_id for item in current):
            raise ValueError(f"Unknown assumption: {assumption_id}")
        confirmed_at = None if act == "reset" else dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        status = "open" if act == "reset" else "confirmed"
        state_map: dict[str, dict[str, Any]] = {}
        for item in current:
            aid = item["assumption_id"]
            if apply_to_all or aid == assumption_id:
                item["status"] = status
                item["confirmed_at"] = confirmed_at
            state_map[aid] = {"status": item["status"], "confirmed_at": item["confirmed_at"]}
        if case_id == "web_fixture":
            _ASSUMPTION_MEMORY_STATE[case_id] = state_map
        else:
            _write_json_atomically(_state_file_for_case(case_id), state_map)
        return current


def publish_assumption_change(case_id: str, assumption_id: str, action: str) -> dict[str, Any]:
    """Publish the new state and its bundle together under the case file lock."""
    with parsers_mod.CASE_FILES_LOCK:
        _get_case_meta(case_id)
        memory_only = case_id == "web_fixture"
        old_memory = _ASSUMPTION_MEMORY_STATE.get(case_id)
        state_path = _state_file_for_case(case_id)
        old_state = state_path.read_bytes() if not memory_only and state_path.is_file() else None
        update_case_assumptions(case_id, assumption_id, action)
        try:
            return build_case_bundle(case_id, persist=not memory_only)
        except BaseException:
            if memory_only:
                if old_memory is None:
                    _ASSUMPTION_MEMORY_STATE.pop(case_id, None)
                else:
                    _ASSUMPTION_MEMORY_STATE[case_id] = old_memory
            elif old_state is None:
                state_path.unlink(missing_ok=True)
            else:
                _write_bytes_atomically(state_path, old_state)
            raise


# ==============================================================================
# 24 条正交硬规则真实求值函数 (check_pv01 .. check_gg04)
# ==============================================================================
def _rect_tuple(b: Any) -> tuple[float, float, float, float] | None:
    if isinstance(b, (list, tuple)) and len(b) == 4:
        return float(b[0]), float(b[1]), float(b[2]), float(b[3])
    if isinstance(b, dict) and all(k in b for k in ("x", "y", "w", "h")):
        return float(b["x"]), float(b["y"]), float(b["w"]), float(b["h"])
    return None


def _rect_contains(parent: tuple[float, float, float, float], child: tuple[float, float, float, float], tol: float = 1.0) -> bool:
    px, py, pw, ph = parent
    cx, cy, cw, ch = child
    return (
        cx >= px - tol
        and cy >= py - tol
        and (cx + cw) <= (px + pw + tol)
        and (cy + ch) <= (py + ph + tol)
    )


def _rect_overlap_area(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix = max(0.0, min(ax + aw, bx + bw) - max(ax, bx))
    iy = max(0.0, min(ay + ah, by + bh) - max(ay, by))
    return ix * iy


def _wcag_contrast(hex1: str, hex2: str) -> float:
    def lum(h: str) -> float:
        s = h.lstrip("#")
        if len(s) != 6:
            return 0.0
        rgb = [int(s[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

    l1, l2 = lum(hex1), lum(hex2)
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)


def _column_edges(grid: dict[str, Any]) -> tuple[list[float], list[float]]:
    cols = int(grid["columns"])
    cw = float(grid["column_width"])
    gut = float(grid["gutter"])
    ml = float(grid["margin_left"])
    lefts = [ml + i * (cw + gut) for i in range(cols)]
    rights = [ml + (i + 1) * cw + i * gut for i in range(cols)]
    return lefts, rights


def _snapped_to_grid(bbox: tuple[float, float, float, float], grid: dict[str, Any], tol: float = 1.0) -> bool:
    x, _, w, _ = bbox
    lefts, rights = _column_edges(grid)
    rx = x + w
    return any(abs(x - le) <= tol for le in lefts) and any(abs(rx - re) <= tol for re in rights)


# ---------------- 第一层：解析层求值函数 ----------------
def check_pv01_timeline_coverage(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    skel = ctx["skeleton"]
    tree_ids = {n["eu_id"] for n in ctx["eu_tree"]["nodes"]}
    dur = float(skel.get("duration_sec") or 0.0)
    eps = float(thresholds.get("time_epsilon_s", 0.001))
    segs = sorted(skel.get("segments", []), key=lambda s: float(s.get("t0", 0.0)))

    violated_nodes: list[str] = []
    uncovered: list[str] = []
    if dur <= 0 or not segs:
        return {"passed": False, "metric": "0.0%", "detail": "视频时长或时段切片为空", "violated_node_ids": [ctx["eu_tree"]["root_id"]]}

    if abs(float(segs[0]["t0"]) - 0.0) > eps:
        uncovered.append(f"0.00–{segs[0]['t0']:.2f}s")
    for i in range(len(segs) - 1):
        diff = float(segs[i + 1]["t0"]) - float(segs[i]["t1"])
        if abs(diff) > eps:
            uncovered.append(f"{segs[i]['t1']:.2f}–{segs[i + 1]['t0']:.2f}s")
    if abs(float(segs[-1]["t1"]) - dur) > eps:
        uncovered.append(f"{segs[-1]['t1']:.2f}–{dur:.3f}s")

    total_covered = sum(max(0.0, float(s["t1"]) - float(s["t0"])) for s in segs)
    ratio = total_covered / dur
    bad_segs: list[str] = []
    for s in segs:
        active_ids = s.get("active_eu_ids") or []
        if not s.get("frame_url") or len(active_ids) < int(thresholds.get("min_bound_eu_per_segment", 1)) or any(eid not in tree_ids for eid in active_ids):
            bad_segs.append(s.get("segment_id", "?"))

    passed = (not uncovered) and (not bad_segs) and (ratio >= float(thresholds.get("min_timeline_coverage_ratio", 1.0)) - eps)
    if not passed:
        violated_nodes.append(ctx["eu_tree"]["root_id"])
    return {
        "passed": passed,
        "metric": f"{total_covered:.3f}s / {dur:.3f}s ({len(segs)}段 · {ratio * 100:.1f}%)",
        "detail": f"0.00~{dur:.3f}s 全时段连续闭合覆盖" if passed else f"存在未闭合时间区间 {uncovered or bad_segs}，覆盖率仅 {ratio * 100:.1f}%",
        "violated_node_ids": violated_nodes,
    }


def check_pv02_viewport_crop(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    skel = ctx["skeleton"]
    vt = skel.get("viewport_transform") or {}
    req_fields = thresholds.get("required_transform_fields", ["source_size", "crop_rect", "scale", "target_size"])
    if not all(f in vt for f in req_fields):
        return {"passed": False, "metric": "变换字段缺失", "detail": "缺少 viewport_transform 裁切记录", "violated_node_ids": [ctx["eu_tree"]["root_id"]]}

    tol = float(thresholds.get("transform_reproduce_tolerance_px", 1.0))
    cr = vt["crop_rect"]
    sc = float(vt["scale"])
    ts = vt["target_size"]
    repro_ok = abs(cr["w"] * sc - ts["w"]) <= tol and abs(cr["h"] * sc - ts["h"]) <= tol

    allowed_noise = set(thresholds.get("noise_region_kinds", []))
    noises = skel.get("noise_regions") or []
    noise_kind_ok = all(nr.get("kind") in allowed_noise for nr in noises)

    violated_nodes: list[str] = []
    for node in ctx["eu_tree"]["nodes"]:
        fb = _rect_tuple(node.get("frame_bbox"))
        if not fb:
            continue
        area = max(1.0, fb[2] * fb[3])
        ov = sum(_rect_overlap_area(fb, _rect_tuple(nr.get("bbox")) or (0, 0, 0, 0)) for nr in noises)
        if ov / area > float(thresholds.get("max_node_noise_overlap_ratio", 0.0)):
            violated_nodes.append(node["eu_id"])

    passed = repro_ok and noise_kind_ok and not violated_nodes
    return {
        "passed": passed,
        "metric": f"{ts['w']}×{ts['h']} (scale {sc:.2f} · 噪声重叠 0%)" if passed else f"噪声混入节点 {len(violated_nodes)} 处",
        "detail": "有效视口裁切可复核且代码窗噪声完全剥离" if passed else f"节点源帧包络落入版式代码窗/噪声区：{violated_nodes}",
        "violated_node_ids": violated_nodes or ([] if passed else [ctx["eu_tree"]["root_id"]]),
    }


def check_pv03_transient_isolation(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    obs_list = ctx["skeleton"].get("observations") or []
    assumptions = ctx["assumptions"]
    asm_subjects: set[str] = set()
    for a in assumptions:
        asm_subjects.add(a.get("eu_id", ""))
        for sid in a.get("subject_ids") or []:
            asm_subjects.add(sid)

    min_frames = int(thresholds.get("min_steady_consecutive_frames", 2))
    violated_nodes: list[str] = []
    bad_obs: list[str] = []
    transient_cnt = 0
    for obs in obs_list:
        st = obs.get("settle_state")
        if st not in ("steady", "transient"):
            bad_obs.append(obs.get("id", "?"))
            continue
        if st == "steady" and int(obs.get("stable_frames", 0)) < min_frames:
            bad_obs.append(obs["id"])
            violated_nodes.append(obs.get("eu_id", ctx["eu_tree"]["root_id"]))
        elif st == "transient":
            transient_cnt += 1
            linked = (obs.get("id") in asm_subjects) or (obs.get("assumption_id") in {a["assumption_id"] for a in assumptions})
            if obs.get("verified") is True or not linked:
                bad_obs.append(obs["id"])
                violated_nodes.append(obs.get("eu_id", ctx["eu_tree"]["root_id"]))

    passed = len(bad_obs) == 0
    return {
        "passed": passed,
        "metric": f"稳态 {len(obs_list) - transient_cnt} · 瞬态隔离 {transient_cnt}" if passed else f"违规瞬态值 {len(bad_obs)}",
        "detail": "片尾滚动未定值已隔离进 AssumptionRecord" if passed else f"瞬态未稳定观测值 {bad_obs} 冒充 verified 真值或未挂接假设",
        "violated_node_ids": violated_nodes,
    }


def check_pv04_interaction_evidence(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    skel = ctx["skeleton"]
    dur = float(skel.get("duration_sec") or 0.0)
    fps = float(skel.get("fps") or 30.0)
    min_frames = int(thresholds.get("min_evidence_frames", 2))
    crop = _rect_tuple((skel.get("viewport_transform") or {}).get("crop_rect")) or (0, 0, 1920, 2560)
    ev_types = set(thresholds.get("evidence_edge_types", []))

    violated_nodes: list[str] = []
    bad_items: list[str] = []
    checked = 0
    for edge in ctx["eu_tree"]["edges"]:
        if edge.get("edge_type") in ev_types and edge.get("source") == "observed":
            checked += 1
            ev = edge.get("evidence") or {}
            fb = _rect_tuple(ev.get("frame_bbox"))
            t0, t1 = ev.get("t0"), ev.get("t1")
            ok = (
                t0 is not None
                and t1 is not None
                and 0.0 <= float(t0) < float(t1) <= dur
                and (float(t1) - float(t0)) * fps >= (min_frames - 1)
                and fb is not None
                and fb[2] > 0
                and fb[3] > 0
                and _rect_contains(crop, fb, 2.0)
            )
            if not ok:
                bad_items.append(edge["edge_id"])
                violated_nodes.append(edge["source_eu_id"])

    for inv in skel.get("frame_invariants") or []:
        checked += 1
        ev = inv.get("evidence") or {}
        fb = _rect_tuple(ev.get("frame_bbox"))
        if not inv.get("holds") or ev.get("t0") is None or ev.get("t1") is None or fb is None:
            bad_items.append(inv.get("id", "invariant"))
            violated_nodes.append(ctx["eu_tree"]["root_id"])

    passed = len(bad_items) == 0
    return {
        "passed": passed,
        "metric": f"{checked}/{checked} 连续帧证据闭合" if passed else f"缺证 {len(bad_items)} 项",
        "detail": "交互边与帧间不变量均绑定有效 [t0,t1] 与源帧包络" if passed else f"连续交互或不变量缺少时间区间/源帧包络：{bad_items}",
        "violated_node_ids": violated_nodes,
    }


def check_pi01_grid_size_chain(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    skel = ctx["skeleton"]
    canvas = skel.get("canvas") or {}
    grid = skel.get("grid") or {}
    cols = int(grid.get("columns", 0))
    cw = float(grid.get("column_width", 0.0))
    gut = float(grid.get("gutter", 0.0))
    ml = float(grid.get("margin_left", 0.0))
    mr = float(grid.get("margin_right", 0.0))
    w, h = float(canvas.get("w", 1.0)), float(canvas.get("h", 1.0))

    chain_sum = ml + mr + cols * cw + max(0, cols - 1) * gut
    chain_res = abs(chain_sum - w)
    ratio_res = abs((w / h) - float(canvas.get("declared_ratio", 0.7071)))
    col_ok = cols in set(thresholds.get("allowed_grid_columns", [4, 6, 8, 12]))

    snap_tol = float(thresholds.get("snap_tolerance", 1.0))
    violated_nodes: list[str] = []
    for n in ctx["eu_tree"]["nodes"]:
        if n["level"] in ("L1", "L2"):
            bb = _rect_tuple(n.get("envelope_bbox"))
            if not bb or not _snapped_to_grid(bb, grid, snap_tol):
                violated_nodes.append(n["eu_id"])

    passed = (
        col_ok
        and chain_res <= float(thresholds.get("size_chain_tolerance", 1.0))
        and ratio_res <= float(thresholds.get("aspect_ratio_tolerance", 0.005))
        and not violated_nodes
    )
    return {
        "passed": passed,
        "metric": f"{cols}栏闭合 (残差 {chain_res:.2f}mm)",
        "detail": "ISO A3 比例与 12 栏瑞士网格尺寸链闭合" if passed else f"栅格尺寸链残差 {chain_res:.2f}mm 或节点未吸附栏线：{violated_nodes}",
        "violated_node_ids": violated_nodes or ([] if passed else [ctx["eu_tree"]["root_id"]]),
    }


def check_pi02_layer_separation(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    layers = ctx["skeleton"].get("layers") or []
    allowed = set(thresholds.get("layer_roles", ["background_material", "foreground_text", "foreground_graphic"]))
    bad_layers: list[str] = []
    for lyr in layers:
        role = lyr.get("layer_role")
        if isinstance(role, list) or role not in allowed:
            bad_layers.append(lyr.get("layer_id", "?"))
        elif role == "background_material" and lyr.get("contains_text") is True:
            bad_layers.append(lyr.get("layer_id", "?"))

    noise_ids = {nr.get("id") for nr in (ctx["skeleton"].get("noise_regions") or [])}
    noise_nodes = [n["eu_id"] for n in ctx["eu_tree"]["nodes"] if n.get("source_region") in noise_ids and noise_ids]
    passed = not bad_layers and not noise_nodes
    return {
        "passed": passed,
        "metric": f"{len(layers)} 层分离 · 混层 0" if passed else f"违规图层 {len(bad_layers)}",
        "detail": "背景纸基、矢量图形与前景活文字严格分层" if passed else f"前景文字合并进背景材质或噪声生成节点：{bad_layers + noise_nodes}",
        "violated_node_ids": noise_nodes or ([] if passed else [ctx["eu_tree"]["root_id"]]),
    }


def check_pi03_atom_sampling(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    reg = ctx["eu_tree"]["atomic_registry"]
    pat = re.compile(str(thresholds.get("color_pattern", r"^#[0-9a-fA-F]{6}$")))
    bad_atoms: list[str] = []

    bg_hex = "#fff6ef"
    for aid, atom in (reg.get("surface_atoms") or {}).items():
        if atom.get("kind") == "color":
            val = str(atom.get("value", ""))
            if not pat.match(val):
                bad_atoms.append(aid)
            if "paper" in aid:
                bg_hex = val

    # 校验正文色与纸基对比度
    for aid, atom in (reg.get("surface_atoms") or {}).items():
        if atom.get("kind") == "color" and ("ink" in aid or "muted" in aid):
            val = str(atom.get("value", "#000000"))
            if pat.match(val) and _wcag_contrast(val, bg_hex) < float(thresholds.get("min_contrast_body", 4.5)):
                bad_atoms.append(aid)

    sizes = sorted(
        [float(a["size_px"]) for a in (reg.get("typography_atoms") or {}).values() if "size_px" in a],
        reverse=True,
    )
    rmin = float(thresholds.get("type_scale_ratio_min", 1.125))
    rmax = float(thresholds.get("type_scale_ratio_max", 4.0))
    for i in range(len(sizes) - 1):
        ratio = sizes[i] / max(0.1, sizes[i + 1])
        if not (rmin <= ratio <= rmax):
            bad_atoms.append("typography_scale")

    unit = int(thresholds.get("spacing_base_unit", 4))
    for aid, atom in (reg.get("layout_atoms") or {}).items():
        if atom.get("kind") == "spacing" and int(atom.get("value", 0)) % unit != 0:
            bad_atoms.append(aid)

    passed = len(bad_atoms) == 0
    return {
        "passed": passed,
        "metric": "HEX/对比度/4px字阶合规" if passed else f"采样违规 {len(bad_atoms)}",
        "detail": "色彩对比度 ≥ 7.9:1、字阶比与 4px 间距网格全部合法" if passed else f"原子采样不满足对比度或比例约束：{bad_atoms}",
        "violated_node_ids": [] if passed else [ctx["eu_tree"]["root_id"]],
    }


def check_pi04_evidence_bbox(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    src = ctx["skeleton"].get("source_image") or {"w": 297.0, "h": 420.0}
    canvas_rect = (0.0, 0.0, float(src["w"]), float(src["h"]))
    parsed_nodes = [n for n in ctx["eu_tree"]["nodes"] if n["level"] in ("L2", "L3") and n.get("source") == "parsed"]
    violated: list[str] = []
    for n in parsed_nodes:
        eb = _rect_tuple(n.get("evidence_bbox"))
        if not eb or eb[2] <= 0 or eb[3] <= 0 or not _rect_contains(canvas_rect, eb, 0.5):
            violated.append(n["eu_id"])

    passed = len(violated) == 0
    return {
        "passed": passed,
        "metric": f"{len(parsed_nodes) - len(violated)}/{len(parsed_nodes)} 强绑定",
        "detail": "全部解析版块与组件均携带有效原图 evidence_bbox" if passed else f"解析节点缺失或越界原图 evidence_bbox：{violated}",
        "violated_node_ids": violated,
    }


def check_pw01_breakpoint_geometry(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    skel = ctx["skeleton"]
    req_bps = [int(x) for x in thresholds.get("baseline_breakpoints_px", [390, 768, 1440])]
    bps = [int(x) for x in (skel.get("breakpoints") or [])]
    dom = skel.get("dom") or {}
    tol = float(thresholds.get("child_in_parent_tolerance_px", 1.0))
    max_ov = float(thresholds.get("max_horizontal_overflow_px", 0))

    violated: list[str] = []
    if not set(req_bps).issubset(set(bps)):
        return {"passed": False, "metric": "断点缺失", "detail": "缺少基线断点记录", "violated_node_ids": [ctx["eu_tree"]["root_id"]]}

    by_id = {n["eu_id"]: n for n in ctx["eu_tree"]["nodes"]}
    for bp in req_bps:
        snap = dom.get(bp) or dom.get(str(bp)) or {}
        if float(snap.get("scroll_width", bp + 999)) - bp > max_ov:
            violated.append(ctx["eu_tree"]["root_id"])
        rects = snap.get("rects") or {}
        for nid, node in by_id.items():
            if node["level"] in ("L1", "L2") and nid not in rects:
                violated.append(nid)
            pid = node.get("parent_id")
            if pid and nid in rects and pid in rects:
                pr = _rect_tuple(rects[pid])
                cr = _rect_tuple(rects[nid])
                if pr and cr and not _rect_contains(pr, cr, tol):
                    violated.append(nid)

    violated = sorted(set(violated))
    passed = len(violated) == 0
    return {
        "passed": passed,
        "metric": f"{len(req_bps)} 断点零溢出" if passed else f"断点几何异常 {len(violated)} 处",
        "detail": "390 / 768 / 1440px 三断点 DOM 包络闭合零横向溢出" if passed else f"多断点下出现横向溢出或父子盒越界：{violated}",
        "violated_node_ids": violated,
    }


def check_pw02_token_normalization(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    styles = ctx["skeleton"].get("computed_styles") or []
    reg = ctx["eu_tree"]["atomic_registry"]
    all_atoms = {aid for sec in reg.values() for aid in sec.keys()}
    max_de = float(thresholds.get("max_color_delta_e", 2.0))
    violated: list[str] = []
    for st in styles:
        tref = st.get("token_ref")
        if not tref or tref not in all_atoms or float(st.get("delta_e", 0.0)) > max_de:
            violated.append(st.get("eu_id", ctx["eu_tree"]["root_id"]))
    passed = len(violated) == 0
    return {
        "passed": passed,
        "metric": f"{len(styles) - len(violated)}/{len(styles)} 样式归一",
        "detail": "全部计算样式已归一至 atomic_registry Token" if passed else f"存在未归一裸计算样式值：{violated}",
        "violated_node_ids": sorted(set(violated)),
    }


def check_pw03_states_and_a11y(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    els = ctx["skeleton"].get("interactive_elements") or []
    req_states = set(thresholds.get("required_states", ["default", "hover", "focus-visible", "active"]))
    violated: list[str] = []
    for el in els:
        if not el.get("role") or not el.get("accessible_name") or not req_states.issubset(set(el.get("states") or [])):
            violated.append(el.get("eu_id", ctx["eu_tree"]["root_id"]))
    passed = len(violated) == 0
    return {
        "passed": passed,
        "metric": f"{len(els) - len(violated)}/{len(els)} 无障碍完备",
        "detail": "可交互元素角色、可访问名称与四态集合全部提取闭合" if passed else f"交互控件缺失 role 或状态集：{violated}",
        "violated_node_ids": sorted(set(violated)),
    }


def check_pw04_decor_data_boundary(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    cnodes = ctx["skeleton"].get("content_nodes") or []
    violated: list[str] = []
    for cn in cnodes:
        cls = cn.get("content_class")
        if cls == "decoration":
            if cn.get("data_source") is not None or cn.get("aria_hidden") is not True or "data" in (cn.get("children_classes") or []):
                violated.append(cn.get("eu_id", ctx["eu_tree"]["root_id"]))
        elif cls == "data":
            if not cn.get("data_source"):
                violated.append(cn.get("eu_id", ctx["eu_tree"]["root_id"]))
        else:
            violated.append(cn.get("eu_id", ctx["eu_tree"]["root_id"]))
    passed = len(violated) == 0
    return {
        "passed": passed,
        "metric": f"{len(cnodes)} 节点边界清晰" if passed else f"混杂节点 {len(violated)}",
        "detail": "静态装饰与业务数据节点严格二分零嵌套污染" if passed else f"装饰节点混入业务数据绑定：{violated}",
        "violated_node_ids": sorted(set(violated)),
    }


# ---------------- 第二层：总规则求值函数 (GN-01 ~ GN-04) ----------------
def check_gn01_tree_graph_separation(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    nodes = ctx["eu_tree"]["nodes"]
    edges = ctx["eu_tree"]["edges"]
    max_deg = int(thresholds.get("max_direct_children", 7))
    forbidden_prefixes = tuple(thresholds.get("forbidden_tree_kind_prefixes", ["interaction.", "event.", "state.", "edge.", "transition."]))
    allowed_edges = set(thresholds.get("allowed_edge_types", []))

    violated: list[str] = []
    reasons: list[str] = []

    # 1. ID 唯一性与单根校验
    seen_ids: set[str] = set()
    roots = [n for n in nodes if n["level"] == "L0"]
    if len(roots) != 1:
        reasons.append(f"L0 根数量={len(roots)}")
    for n in nodes:
        if n["eu_id"] in seen_ids:
            violated.append(n["eu_id"])
            reasons.append(f"重复ID:{n['eu_id']}")
        seen_ids.add(n["eu_id"])

    by_id = {n["eu_id"]: n for n in nodes}
    parent_count: dict[str, int] = {nid: 0 for nid in by_id}
    for n in nodes:
        for cid in n.get("children_ids", []):
            if cid not in by_id:
                violated.append(n["eu_id"])
                reasons.append(f"悬空子ID:{cid}")
            else:
                parent_count[cid] += 1

    for nid, n in by_id.items():
        lvl_idx = int(str(n["level"])[1:])
        if n["level"] != "L0":
            pid = n.get("parent_id")
            if not pid or pid not in by_id or parent_count[nid] != 1:
                violated.append(nid)
                reasons.append(f"非单父:{nid}")
            else:
                p_idx = int(str(by_id[pid]["level"])[1:])
                if lvl_idx != p_idx + 1:
                    violated.append(nid)
                    reasons.append(f"跳层挂接:{pid}->{nid}")
        if len(n.get("children_ids", [])) > max_deg:
            violated.append(nid)
            reasons.append(f"度超限({len(n['children_ids'])}>{max_deg}):{nid}")
        if str(n.get("node_kind", "")).startswith(forbidden_prefixes):
            violated.append(nid)
            reasons.append(f"交互混入纵向树:{nid}({n.get('node_kind')})")

    # DFS 环检测
    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(u: str) -> bool:
        visiting.add(u)
        for v in by_id[u].get("children_ids", []):
            if v in visiting:
                violated.append(v)
                return True
            if v in by_id and v not in visited and dfs(v):
                return True
        visiting.remove(u)
        visited.add(u)
        return False

    if roots and dfs(roots[0]["eu_id"]):
        reasons.append("纵向树存在环")

    # 横向边白名单校验
    for e in edges:
        et = e.get("edge_type")
        s_id, t_id = e.get("source_eu_id"), e.get("target_eu_id")
        if et not in allowed_edges or s_id not in by_id or t_id not in by_id or s_id == t_id:
            violated.extend([x for x in (s_id, t_id) if x in by_id])
            reasons.append(f"非法横向边:{e.get('edge_id')}({et})")

    violated = sorted(set(violated))
    obs_max_deg = max((len(n.get("children_ids", [])) for n in nodes), default=0)
    passed = len(reasons) == 0
    return {
        "passed": passed,
        "metric": f"L0~L5 单父无环 · 最大度 {obs_max_deg}/7 · 边 {len(edges)}",
        "detail": "纵向六级树与 6 类横向交互边严格分离闭合" if passed else "；".join(reasons[:3]),
        "violated_node_ids": violated or ([] if passed else [ctx["eu_tree"]["root_id"]]),
    }


def check_gn02_template_adaptive_compliance(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    eu_tree = ctx["eu_tree"]
    templates = ctx["templates"]
    tid = eu_tree.get("template_id")
    tpl = templates.get(str(tid))
    if not tpl:
        return {"passed": False, "metric": "模板缺失", "detail": f"未找到原型模板 {tid}", "violated_node_ids": [eu_tree["root_id"]]}

    nodes = eu_tree["nodes"]
    by_id = {n["eu_id"]: n for n in nodes}
    allowed_modes = set(thresholds.get("allowed_adaptation_modes", []))
    max_deg = int(thresholds.get("post_adapt_max_direct_children", 7))
    split_min = int(((tpl.get("adaptive_policies") or {}).get("SPLIT_HIGH_INTERACTION") or {}).get("trigger", {}).get("min_interaction_edges", 3))
    fold_min = int(((tpl.get("adaptive_policies") or {}).get("FOLD_ARRAY") or {}).get("trigger", {}).get("min_isomorphic_siblings", 3))

    violated: list[str] = []
    reasons: list[str] = []

    # 1. 必选 L1 领地锚定检查（按品类插件裁剪后必选槽位动态决定，兼容原模板基线）
    tpl_req_slots = [s["slot_id"] for s in tpl.get("l1_territories", []) if s.get("required")]
    cat_def = ctx.get("category_definition")
    req_slots = list(cat_def["required_slots"]) if (cat_def and cat_def.get("required_slots")) else tpl_req_slots
    l1_by_slot = {n.get("template_slot"): n for n in nodes if n["level"] == "L1"}
    for sid in req_slots:
        l1n = l1_by_slot.get(sid)
        if not l1n or l1n.get("adaptation_mode") != "TEMPLATE_ANCHOR":
            violated.append(eu_tree["root_id"])
            reasons.append(f"缺少必选L1领地锚定:{sid}")

    # 2. 节点级模式、跳层、空壳、同构折叠与度检查
    for n in nodes:
        nid = n["eu_id"]
        mode = n.get("adaptation_mode")
        if mode not in allowed_modes or ((n["level"] == "L5") != (mode == "ATOMIC_MOUNT")):
            violated.append(nid)
            reasons.append(f"自适应模式非法:{nid}({mode})")
        if n.get("template_slot") is not None and (n["level"] != "L1" or n["template_slot"] not in tpl.get("slot_ids", [])):
            violated.append(nid)
            reasons.append(f"非L1槽位越权绑定:{nid}")
        cids = n.get("children_ids", [])
        if n["level"] in ("L0", "L1", "L2", "L3") and len(cids) == 0:
            violated.append(nid)
            reasons.append(f"非叶空壳节点:{nid}")
        if len(cids) > max_deg:
            violated.append(nid)
            reasons.append(f"自适应伸缩后度溢出({len(cids)}>{max_deg}):{nid}")

        # 检查同一父下是否存在未折叠的同构组件群 (L2/L3)
        if n["level"] in ("L1", "L2") and cids:
            kind_counts: dict[str, list[str]] = {}
            for cid in cids:
                cn = by_id.get(cid)
                if cn and cn.get("adaptation_mode") != "FOLD_ARRAY":
                    k = str(cn.get("node_kind", ""))
                    kind_counts.setdefault(k, []).append(cid)
            for k, group in kind_counts.items():
                if len(group) >= fold_min:
                    violated.append(nid)
                    reasons.append(f"同构兄弟({k}×{len(group)})未执行FOLD_ARRAY折叠")

        # 检查高交互密度节点是否执行 SPLIT_HIGH_INTERACTION 并带 L4 特征
        if int(n.get("interaction_density", 0)) >= split_min:
            has_split = n.get("adaptation_mode") == "SPLIT_HIGH_INTERACTION"
            has_l4 = any(by_id[cid]["level"] == "L4" for cid in cids if cid in by_id) or any(
                by_id[gc]["level"] == "L4"
                for cid in cids
                if cid in by_id
                for gc in by_id[cid].get("children_ids", [])
                if gc in by_id
            )
            if not (has_split and has_l4):
                violated.append(nid)
                reasons.append(f"高密交互区未分裂:{nid}")

    # 3. 模板允许的横向边类型检查（如平面模板裁剪交互边）
    tpl_allowed_edges = set(tpl.get("allowed_edge_types", []))
    for e in eu_tree["edges"]:
        if e.get("edge_type") not in tpl_allowed_edges:
            violated.append(e["source_eu_id"])
            reasons.append(f"模板不允许边类型:{e['edge_type']}")

    passed = len(reasons) == 0
    split_cnt = sum(1 for n in nodes if n.get("adaptation_mode") == "SPLIT_HIGH_INTERACTION")
    fold_cnt = sum(1 for n in nodes if n.get("adaptation_mode") == "FOLD_ARRAY")
    return {
        "passed": passed,
        "metric": f"4领地锚定 · 分裂{split_cnt} · 折叠{fold_cnt}",
        "detail": f"严格锚定 {tid}，高密分裂与同构阵列折叠全部合规" if passed else "；".join(reasons[:3]),
        "violated_node_ids": sorted(set(violated)),
    }


def check_gn03_atomic_registry_coverage(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    eu_tree = ctx["eu_tree"]
    reg = eu_tree.get("atomic_registry") or {}
    req_secs = set(thresholds.get("registry_sections", ["surface_atoms", "typography_atoms", "layout_atoms", "motion_atoms", "evidence_atoms"]))
    req_l3_secs = set(thresholds.get("required_atom_sections_per_entity_l3", ["surface_atoms", "typography_atoms", "layout_atoms", "evidence_atoms"]))
    nodes = eu_tree["nodes"]
    by_id = {n["eu_id"]: n for n in nodes}

    violated: list[str] = []
    reasons: list[str] = []
    if set(reg.keys()) != req_secs:
        reasons.append("atomic_registry 五区段不完整")

    atom_sec_map: dict[str, str] = {}
    orphan_atoms: list[str] = []
    for sec_name, sec_dict in reg.items():
        for aid, atom in (sec_dict or {}).items():
            atom_sec_map[aid] = sec_name
            used = atom.get("used_by") or []
            if len(used) < 1 or any(u not in by_id for u in used):
                orphan_atoms.append(aid)

    if orphan_atoms:
        reasons.append(f"孤儿或悬空反向索引原子:{orphan_atoms[:3]}")

    unresolved: list[str] = []
    for n in nodes:
        if n["level"] == "L5":
            for ref in n.get("atom_refs", []):
                if ref not in atom_sec_map:
                    unresolved.append(ref)
                    violated.append(n["eu_id"])
    if unresolved:
        reasons.append(f"无法解析的atom_ref:{unresolved[:3]}")

    def subtree_ids(uid: str) -> list[str]:
        res = [uid]
        for cid in by_id[uid].get("children_ids", []):
            if cid in by_id:
                res.extend(subtree_ids(cid))
        return res

    l3_entities = [n for n in nodes if n["level"] == "L3" and n.get("entity", True)]
    covered_l3 = 0
    for l3 in l3_entities:
        sub_ids = subtree_ids(l3["eu_id"])
        sub_nodes = [by_id[i] for i in sub_ids]
        secs_found: set[str] = set()
        has_motion_feat = any(sn["level"] == "L4" and sn.get("motion") is True for sn in sub_nodes)
        for sn in sub_nodes:
            if sn["level"] == "L5":
                for ref in sn.get("atom_refs", []):
                    if ref in atom_sec_map:
                        secs_found.add(atom_sec_map[ref])
        needed = set(req_l3_secs)
        if has_motion_feat:
            needed.add("motion_atoms")
        if needed.issubset(secs_found):
            covered_l3 += 1
        else:
            violated.append(l3["eu_id"])
            reasons.append(f"{l3['eu_id']}缺少原子类:{sorted(needed - secs_found)}")

    # No-Evidence-No-Verified 检查
    ev_atoms = set((reg.get("evidence_atoms") or {}).keys())
    asm_eu_ids = {a.get("eu_id") for a in ctx["assumptions"]}
    for n in nodes:
        if n["level"] in ("L3", "L5") and n.get("verified") is True:
            evs = [e for e in (n.get("evidence_refs") or []) if e in ev_atoms]
            if not evs:
                violated.append(n["eu_id"])
                reasons.append(f"无证据却标verified:{n['eu_id']}")
        if n.get("status") == "inferred" and not (n.get("evidence_refs") or []) and n["eu_id"] not in asm_eu_ids:
            violated.append(n["eu_id"])
            reasons.append(f"无证据推断未入假设:{n['eu_id']}")

    cov_ratio = 1.0 if not l3_entities else covered_l3 / len(l3_entities)
    passed = len(reasons) == 0 and cov_ratio >= float(thresholds.get("min_entity_l3_l5_coverage_ratio", 1.0))
    return {
        "passed": passed,
        "metric": f"L3覆盖 {covered_l3}/{len(l3_entities)} ({cov_ratio * 100:.0f}%)",
        "detail": "单源双索引 100% 闭合，全部实体组件具备原件证据" if passed else "；".join(reasons[:2]),
        "violated_node_ids": sorted(set(violated)) or ([] if passed else [eu_tree["root_id"]]),
    }


def check_gn04_envelope_and_admission(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    nodes = ctx["eu_tree"]["nodes"]
    by_id = {n["eu_id"]: n for n in nodes}
    tol = float(thresholds.get("envelope_overflow_tolerance", 1.0))
    min_ext = float(thresholds.get("min_envelope_extent", 0.0))

    violated: list[str] = []
    for n in nodes:
        bb = _rect_tuple(n.get("envelope_bbox"))
        if not bb:
            continue
        if bb[2] <= min_ext or bb[3] <= min_ext:
            violated.append(n["eu_id"])
            continue
        pid = n.get("parent_id")
        if pid and pid in by_id:
            pbb = _rect_tuple(by_id[pid].get("envelope_bbox"))
            if pbb and not _rect_contains(pbb, bb, tol):
                violated.append(n["eu_id"])

    open_cnt = sum(1 for a in ctx["assumptions"] if a.get("status") == "open")
    forced_adm = ctx.get("forced_admission_override")
    adm_mismatch = False
    if forced_adm is not None:
        expected = "PROVISIONAL" if open_cnt > 0 else "RELEASE_READY"
        if forced_adm != expected:
            adm_mismatch = True
            violated.append(ctx["eu_tree"]["root_id"])

    passed = len(violated) == 0 and not adm_mismatch
    state_preview = "PROVISIONAL" if open_cnt > 0 else "RELEASE_READY"
    return {
        "passed": passed,
        "metric": f"包络守恒 · 待确认假设 {open_cnt} ({state_preview})" if passed else f"包络越界 {len(violated)} 处",
        "detail": "全部子包络收敛于父界内，三态准入状态机一致" if passed else f"子节点几何包络越出父容器边界或准入状态失配：{violated}",
        "violated_node_ids": sorted(set(violated)),
    }


# ---------------- 第三层：生成层求值函数 (GU-01..04 & GG-01..04) ----------------
def check_gu01_token_consumption(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    rb = ctx["readback"]
    tc = rb.get("token_consumption") or {}
    ratio = float(tc.get("consumption_ratio", 0.0))
    unconsumed = tc.get("unconsumed_atom_ids") or []
    has_motion = len((ctx["eu_tree"]["atomic_registry"].get("motion_atoms") or {})) > 0
    rm_ok = (not has_motion) or bool(rb.get("reduced_motion_supported"))

    passed = ratio >= float(thresholds.get("min_token_consumption_ratio", 1.0)) and rm_ok and not unconsumed
    return {
        "passed": passed,
        "metric": f"Token消费 {ratio * 100:.0f}% · reduced-motion {'ON' if rm_ok else 'OFF'}",
        "detail": "全部设计与动效 Token 已在 CSS 声明引用，且支持减弱动效" if passed else f"未消费 Token {unconsumed} 或缺失 prefers-reduced-motion",
        "violated_node_ids": [] if passed else [ctx["eu_tree"]["root_id"]],
    }


def check_gu02_live_dom_not_bitmap(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    rb = ctx["readback"]
    allowed_roles = set(thresholds.get("allowed_bitmap_roles", ["background_material", "avatar", "photo_content"]))
    illegal_area = sum(
        float(b.get("area_ratio", 0.0))
        for b in (rb.get("bitmaps") or [])
        if b.get("role") not in allowed_roles
    )
    ov_map = rb.get("viewport_overflow_px") or {}
    clip_ok = all(float(ov_map.get(vp, ov_map.get(str(vp), 0))) <= float(thresholds.get("max_horizontal_clip_px", 0)) for vp in thresholds.get("required_viewports_px", [1440, 390]))
    fluid_ok = len(rb.get("fluid_markers_found") or []) > 0
    text_cnt = int(rb.get("editable_text_nodes", 0))
    ctrl_cnt = int(rb.get("interactive_controls", 0))

    passed = (
        text_cnt > 0
        and ctrl_cnt > 0
        and illegal_area <= float(thresholds.get("max_ui_bitmap_area_ratio", 0.0))
        and clip_ok
        and fluid_ok
        and bool(rb.get("responsive_390_supported", True))
    )
    return {
        "passed": passed,
        "metric": f"活文本 {text_cnt} · 真控件 {ctrl_cnt} · 贴皮 {illegal_area * 100:.0f}%",
        "detail": "100% 可编辑真 DOM 与弹性容器，1440/390px 重排零裁切" if passed else f"检测到整区位图贴皮退化(占比{illegal_area * 100:.0f}%)或文本/控件未实现为真 DOM",
        "violated_node_ids": rb.get("degraded_node_ids") or ([] if passed else ["eu_L1_main_stage"]),
    }


def check_gu03_edge_realization(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    inter_types = set(thresholds.get("interaction_edge_types", []))
    req_edges = [e for e in ctx["eu_tree"]["edges"] if e.get("edge_type") in inter_types]
    real_map = {r["edge_id"]: r for r in (ctx["readback"].get("interactions") or [])}
    neutral = float(thresholds.get("neutral_scale", 1.0))

    violated: list[str] = []
    failed_edges: list[str] = []
    for e in req_edges:
        r = real_map.get(e["edge_id"])
        if not r or not r.get("passed"):
            failed_edges.append(e["edge_id"])
            violated.append(e["source_eu_id"])
            continue
        m = r.get("measure") or {}
        et = e["edge_type"]
        probe_ok = True
        if et == "MODULATES_NEIGHBOR":
            probe_ok = (
                float(m.get("focus_scale", 1.0)) > float(m.get("neighbor_scale", 1.0)) > neutral
                and float(m.get("far_scale", 1.0)) == neutral
                and bool(m.get("restored_after_leave"))
            )
        elif et == "SCROLLS_INDEPENDENTLY":
            probe_ok = float(m.get("host_scroll_delta", 0.0)) > 0 and float(m.get("sibling_offset_delta", 1.0)) == 0.0
        elif et == "FILTERS_VIEW":
            probe_ok = bool(m.get("dataset_changed")) and m.get("export_scope") == m.get("active_filter")
        elif et == "RESTORES_FOCUS":
            probe_ok = bool(m.get("active_element_matches_trigger"))
        elif et == "TRIGGERS_STATE":
            probe_ok = m.get("target_state_after") != m.get("target_state_before")
        if not probe_ok:
            failed_edges.append(e["edge_id"])
            violated.append(e["source_eu_id"])

    passed = len(failed_edges) == 0
    edge_summary = "、".join(sorted({str(e.get("edge_type")) for e in req_edges})) or "无交互边"
    return {
        "passed": passed,
        "metric": f"{len(req_edges) - len(failed_edges)}/{len(req_edges)} 交互闭环",
        "detail": f"全部 {len(req_edges)} 条已登记交互边闭环 ({edge_summary})" if passed else f"微交互横向边未实现或探针失败：{failed_edges}",
        "violated_node_ids": sorted(set(violated)),
    }


def check_gu04_readback_and_microcopy(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    rb = ctx["readback"]
    cov = float(rb.get("dom_eu_binding_coverage", 0.0))
    missing = rb.get("missing_trace_ids") or []
    dangling = rb.get("dangling_trace_ids") or []
    dups = rb.get("duplicate_trace_ids") or []
    def_cnt = int(rb.get("defensive_microcopy_violations", 0))
    def_hits = rb.get("defensive_hits") or []

    passed = (
        cov >= float(thresholds.get("min_trace_coverage_ratio", 1.0))
        and len(missing) == 0
        and len(dangling) <= int(thresholds.get("max_dangling_trace_ids", 0))
        and len(dups) <= int(thresholds.get("max_duplicate_trace_ids", 0))
        and def_cnt <= int(thresholds.get("max_defensive_phrases", 0))
    )
    return {
        "passed": passed,
        "metric": f"溯源 {cov * 100:.0f}% · 防御小字 {def_cnt}",
        "detail": "在线舞台与导出产物 data-eu-id 100% 唯一对齐，零防御性小字" if passed else f"缺失溯源ID {missing} / 悬空 {dangling} / 命中禁用防御小字 {def_hits}",
        "violated_node_ids": missing or ([] if passed else [ctx["eu_tree"]["root_id"]]),
    }


def check_gg01_canvas_bleed_grid(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    tpl = ctx["templates"]["tpl_graphic_poster_v1"]
    contract = tpl["canvas"]
    pc = ctx["readback"].get("poster_canvas") or {}
    w = float(pc.get("w", 297.0))
    h = float(pc.get("h", 420.0))
    ratio_ok = abs((w / h) - (float(contract["width"]) / float(contract["height"]))) <= float(thresholds.get("aspect_ratio_tolerance", 0.005))
    bleed = pc.get("bleed") or {}
    min_bleed = float(contract["bleed"]) * float(thresholds.get("min_bleed_ratio_of_contract", 1.0))
    bleed_ok = all(float(bleed.get(side, 0.0)) >= min_bleed for side in ("top", "right", "bottom", "left"))

    safe_rect = _rect_tuple(pc.get("safe_area")) or (12.0, 12.0, 273.0, 396.0)
    exempt = set(thresholds.get("background_roles_exempt_from_safe_area", ["background_material", "bleed_fill"]))
    snap_tol = float(thresholds.get("snap_tolerance", 1.0))
    violated: list[str] = []
    for n in ctx["eu_tree"]["nodes"]:
        bb = _rect_tuple(n.get("envelope_bbox"))
        if not bb:
            continue
        if n.get("role") not in exempt and n["level"] in ("L1", "L2", "L3") and not _rect_contains(safe_rect, bb, 0.5):
            violated.append(n["eu_id"])
        if n["level"] in ("L1", "L2") and not _snapped_to_grid(bb, contract["grid"], snap_tol):
            violated.append(n["eu_id"])

    passed = ratio_ok and bleed_ok and not violated
    return {
        "passed": passed,
        "metric": f"A3 297×420 · 出血 {min(bleed.values(), default=0.0):.0f}mm",
        "detail": "A3 画幅比例、四边 3mm 出血、12mm 安全框与 12 栏对齐守恒" if passed else f"出血不足或区块越出安全框/偏离栏线：{sorted(set(violated))}",
        "violated_node_ids": sorted(set(violated)) or ([] if passed else [ctx["eu_tree"]["root_id"]]),
    }


def check_gg02_hierarchy_contrast(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    pc = ctx["readback"].get("poster_canvas") or {}
    scales = pc.get("hierarchy_scales_px") or {}
    roles_order = thresholds.get("hierarchy_roles", ["display", "headline", "body", "caption"])
    used = [r for r in roles_order if r in scales]
    min_adj = float(thresholds.get("min_adjacent_scale_ratio", 1.2))

    scale_ok = len(used) >= int(thresholds.get("min_hierarchy_levels", 3))
    for i in range(len(used) - 1):
        if float(scales[used[i]]) / max(0.1, float(scales[used[i + 1]])) < min_adj:
            scale_ok = False

    contrast_ok = True
    for tc in pc.get("text_contrasts") or []:
        req = float(thresholds.get("min_contrast_large", 3.0)) if float(tc.get("size_px", 14.0)) >= float(thresholds.get("large_text_min_px", 24.0)) else float(thresholds.get("min_contrast_body", 4.5))
        if _wcag_contrast(tc["fg"], tc["bg"]) < req:
            contrast_ok = False

    passed = scale_ok and contrast_ok
    return {
        "passed": passed,
        "metric": f"{len(used)}级字阶 ({'/'.join(str(int(scales[r])) for r in used)}px)",
        "detail": "四级字阶严格递减且全版面文字对比度合规" if passed else "出现字阶层级倒置或文字背景对比度不足",
        "violated_node_ids": [] if passed else ["eu_L3_poster_headline"],
    }


def check_gg03_editable_layers(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    rb = ctx["readback"]
    text_modes = set(thresholds.get("text_realizations", ["dom_text", "svg_text"]))
    gfx_modes = set(thresholds.get("graphic_realizations", ["svg_shape", "css_shape"]))
    violated: list[str] = []
    for n in ctx["eu_tree"]["nodes"]:
        if n.get("carries_text") and n.get("rendered_as") not in text_modes:
            violated.append(n["eu_id"])
        if n.get("layer_role") == "foreground_graphic" and n.get("rendered_as") not in gfx_modes:
            violated.append(n["eu_id"])

    passed = (
        not violated
        and float(rb.get("live_text_ratio", 0.0)) >= float(thresholds.get("min_live_text_ratio", 1.0))
        and float(rb.get("vector_graphic_ratio", 0.0)) >= float(thresholds.get("min_vector_graphic_ratio", 1.0))
        and int(rb.get("rasterized_text_count", 0)) <= int(thresholds.get("max_rasterized_text", 0))
    )
    return {
        "passed": passed,
        "metric": f"活文字 {rb.get('live_text_ratio', 0) * 100:.0f}% · 死位图文字 {rb.get('rasterized_text_count', 0)}",
        "detail": "100% 独立可编辑 DOM/SVG 活文字与纯矢量几何图层" if passed else f"文字或前景图形退化为死位图：{violated}",
        "violated_node_ids": violated or ([] if passed else ["eu_L3_poster_headline"]),
    }


def check_gg04_reopen_drift_trace(ctx: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    rb = ctx["readback"]
    drift = float((rb.get("poster_canvas") or {}).get("reopen_max_drift_mm", 0.0))
    cov = float(rb.get("dom_eu_binding_coverage", 0.0))
    dangling = rb.get("dangling_trace_ids") or []
    def_cnt = int(rb.get("defensive_microcopy_violations", 0))

    passed = (
        drift <= float(thresholds.get("max_reopen_drift", 0.5))
        and cov >= float(thresholds.get("min_trace_coverage_ratio", 1.0))
        and len(dangling) <= int(thresholds.get("max_dangling_trace_ids", 0))
        and def_cnt <= int(thresholds.get("max_defensive_phrases", 0))
    )
    return {
        "passed": passed,
        "metric": f"漂移 {drift:.2f}mm · 溯源 {cov * 100:.0f}%",
        "detail": "导出重开包络零漂移，data-eu-id 100% 闭合且零防御小字" if passed else f"重开版式漂移 {drift:.2f}mm 超限或溯源 ID 断链",
        "violated_node_ids": rb.get("missing_trace_ids") or ([] if passed else [ctx["eu_tree"]["root_id"]]),
    }


CHECK_DISPATCH: dict[str, Any] = {
    "check_pv01_timeline_coverage": check_pv01_timeline_coverage,
    "check_pv02_viewport_crop": check_pv02_viewport_crop,
    "check_pv03_transient_isolation": check_pv03_transient_isolation,
    "check_pv04_interaction_evidence": check_pv04_interaction_evidence,
    "check_pi01_grid_size_chain": check_pi01_grid_size_chain,
    "check_pi02_layer_separation": check_pi02_layer_separation,
    "check_pi03_atom_sampling": check_pi03_atom_sampling,
    "check_pi04_evidence_bbox": check_pi04_evidence_bbox,
    "check_pw01_breakpoint_geometry": check_pw01_breakpoint_geometry,
    "check_pw02_token_normalization": check_pw02_token_normalization,
    "check_pw03_states_and_a11y": check_pw03_states_and_a11y,
    "check_pw04_decor_data_boundary": check_pw04_decor_data_boundary,
    "check_gn01_tree_graph_separation": check_gn01_tree_graph_separation,
    "check_gn02_template_adaptive_compliance": check_gn02_template_adaptive_compliance,
    "check_gn03_atomic_registry_coverage": check_gn03_atomic_registry_coverage,
    "check_gn04_envelope_and_admission": check_gn04_envelope_and_admission,
    "check_gu01_token_consumption": check_gu01_token_consumption,
    "check_gu02_live_dom_not_bitmap": check_gu02_live_dom_not_bitmap,
    "check_gu03_edge_realization": check_gu03_edge_realization,
    "check_gu04_readback_and_microcopy": check_gu04_readback_and_microcopy,
    "check_gg01_canvas_bleed_grid": check_gg01_canvas_bleed_grid,
    "check_gg02_hierarchy_contrast": check_gg02_hierarchy_contrast,
    "check_gg03_editable_layers": check_gg03_editable_layers,
    "check_gg04_reopen_drift_trace": check_gg04_reopen_drift_trace,
}


# ==============================================================================
# Y 型三层 12 条正交门禁求值与准入状态机
# ==============================================================================
CASE_META: dict[str, dict[str, Any]] = {
    "code_xr_uiux": {
        "case_id": "code_xr_uiux",
        "title": "Code XR · Glass Workspace",
        "subtitle": "视频 → UI/UX",
        "modality": "video",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/code_xr_uiux/app/index.html?still=1",
        "source_summary": "VIDEO · 5.689s · 6 时段 100%",
    },
    "code_xr_poster": {
        "case_id": "code_xr_poster",
        "title": "Code XR · 品牌视觉展板",
        "subtitle": "图片 → 平面设计",
        "modality": "image",
        "domain": "graphic",
        "template_id": "tpl_graphic_poster_v1",
        "stage_url": "/cases/code_xr_poster/app/index.html",
        "source_summary": "IMAGE · ISO A3 · 12 栏瑞士网格",
    },
    "web_fixture": {
        "case_id": "web_fixture",
        "title": "Code XR · Web 多断点夹具",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/code_xr_uiux/app/index.html?still=1",
        "source_summary": "WEB · 390/768/1440px 三断点",
    },
    **catalog_mod.EXTRA_CASE_META,
    **styles_mod.STYLE_CASE_META,
    **motion_mod.MOTION_CASE_META,
}


def evaluate_three_layer_gates(
    modality: str,
    domain: str,
    skeleton: dict[str, Any],
    eu_tree: dict[str, Any],
    assumptions: list[dict[str, Any]],
    readback: dict[str, Any],
    target_rule_hint: str | None = None,
    forced_admission_override: str | None = None,
    category_id: str | None = None,
    *,
    rule_modules: list[dict[str, Any]] | None = None,
    templates: dict[str, dict[str, Any]] | None = None,
    categories: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], str]:
    """按 modality + scope=all + domain 动态激活 12 条规则并执行真实求值。"""
    all_modules = load_all_rule_modules() if rule_modules is None else rule_modules
    if templates is None:
        templates = load_all_templates()
    total_lib_rules = sum(len(m.get("rules", [])) for m in all_modules)

    active_modules: list[dict[str, Any]] = []
    for mod in all_modules:
        rk = mod.get("route_key")
        if rk == "modality" and mod.get("modality") == modality:
            active_modules.append(mod)
        elif rk == "scope" and mod.get("scope") == "all":
            active_modules.append(mod)
        elif rk == "domain" and mod.get("domain") == domain:
            active_modules.append(mod)
    active_modules.sort(key=lambda m: int(m.get("layer_order", 9)))

    category_definition = None
    if category_id:
        catalog = cat_reg.load_categories() if categories is None else categories
        category_definition = catalog.get(category_id)
    ctx = {
        "modality": modality,
        "domain": domain,
        "category_id": category_id,
        "category_definition": category_definition,
        "skeleton": skeleton,
        "eu_tree": eu_tree,
        "assumptions": assumptions,
        "readback": readback,
        "templates": templates,
        "forced_admission_override": forced_admission_override,
    }

    layers_out: list[dict[str, Any]] = []
    by_layer: dict[str, Any] = {}
    failed_records: list[dict[str, Any]] = []

    layer_short = {"parsing": "解析层", "general": "总规则", "generation": "生成层"}

    for mod in active_modules:
        lname = str(mod["layer"])
        prefix = str(mod["rule_prefix"])
        rkey = str(mod["route_key"])
        rval = str(mod.get(rkey, ""))
        rules_out: list[dict[str, Any]] = []
        passed_in_layer = 0

        for rdef in mod.get("rules", []):
            rid = str(rdef["id"])
            check_code = str(rdef.get("check_code", ""))
            fn = CHECK_DISPATCH.get(check_code)
            if fn is None:
                res = {
                    "passed": False,
                    "metric": "CHECK_HANDLER_MISSING",
                    "detail": f"No rule handler for {check_code or '(empty check_code)'}",
                    "violated_node_ids": [],
                }
            else:
                res = fn(ctx, rdef.get("thresholds") or {})
            ok = bool(res["passed"])
            if ok:
                passed_in_layer += 1
            item = {
                "rule_id": rid,
                "id": rid,
                "name": str(rdef["name"]),
                "status": "PASS" if ok else "FAIL",
                "severity": str(rdef.get("severity", "BLOCKER")),
                "metric": str(res.get("metric", "")),
                "detail": str(res.get("detail", "")),
                "violated_node_ids": list(res.get("violated_node_ids") or []),
                "counterfactual_preset": str(rdef.get("counterfactual_preset", "")),
            }
            rules_out.append(item)
            if not ok:
                failed_records.append({"layer": lname, "layer_label": layer_short.get(lname, lname), **item})

        layer_entry = {
            "layer": lname,
            "layer_label": layer_short.get(lname, lname),
            "prefix": prefix,
            "route_key": rval,
            "passed": passed_in_layer,
            "total": len(rules_out),
            "status": "PASS" if passed_in_layer == len(rules_out) else "BLOCKED",
            "rules": rules_out,
        }
        layers_out.append(layer_entry)
        by_layer[lname] = layer_entry

    active_cnt = sum(l["total"] for l in layers_out)
    passed_cnt = sum(l["passed"] for l in layers_out)

    primary_fail: dict[str, Any] | None = None
    co_failed: list[str] = []
    if failed_records:
        if target_rule_hint:
            matched = next((f for f in failed_records if f["rule_id"] == target_rule_hint), None)
            primary_fail = matched or failed_records[0]
        else:
            primary_fail = failed_records[0]
        co_failed = [f["rule_id"] for f in failed_records if f["rule_id"] != primary_fail["rule_id"]]

    open_cnt = sum(1 for a in assumptions if a.get("status") == "open")
    if primary_fail:
        verdict = "BLOCKED"
        admission = "BLOCKED"
        blocked_layer = primary_fail["layer"]
        violated_rule_id = primary_fail["rule_id"]
        attribution = f"{primary_fail['layer_label']}门禁阻断 [{violated_rule_id} · {primary_fail['name']}]：{primary_fail['detail']}"
    else:
        verdict = "PASS"
        admission = "PROVISIONAL" if open_cnt > 0 else "RELEASE_READY"
        blocked_layer = None
        violated_rule_id = None
        attribution = None

    gates = {
        "verdict": verdict,
        "active_count": active_cnt,
        "passed_count": passed_cnt,
        "total_library_rules": total_lib_rules,
        "blocked_layer": blocked_layer,
        "violated_rule_id": violated_rule_id,
        "violated_rule_name": primary_fail["name"] if primary_fail else None,
        "violated_node_ids": primary_fail["violated_node_ids"] if primary_fail else [],
        "co_failed_rule_ids": co_failed,
        "attribution": attribution,
        "layers": layers_out,
        "by_layer": by_layer,
    }
    return gates, admission


# ==============================================================================
# 24 项反事实异常注入内存沙盒（100% 真实修改快照结构并交由同一求值器检出）
# ==============================================================================
def _get_all_case_meta() -> dict[str, dict[str, Any]]:
    merged = dict(CASE_META)
    for cid, pdata in parsers_mod.discover_imported_cases().items():
        if cid not in merged and isinstance(pdata.get("case_meta"), dict):
            merged[cid] = pdata["case_meta"]
    return merged


class UnknownCaseError(ValueError):
    """A requested case does not exist."""


def _get_case_meta(case_id: str) -> dict[str, Any]:
    if case_id in CASE_META:
        return CASE_META[case_id]
    imported = parsers_mod.load_imported_case(case_id)
    if imported and isinstance(imported.get("case_meta"), dict):
        return imported["case_meta"]
    raise UnknownCaseError(f"Unknown case_id: {case_id}")


def get_counterfactual_presets(
    case_id: str | None = None, *, rule_modules: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    presets: list[dict[str, Any]] = []
    all_meta = _get_all_case_meta()
    all_case_ids = list(all_meta.keys())
    for mod in load_all_rule_modules() if rule_modules is None else rule_modules:
        layer = str(mod["layer"])
        rk = mod.get("route_key")
        if rk == "modality":
            mval = mod.get("modality")
            cases = [cid for cid, m in all_meta.items() if m.get("modality") == mval]
        elif rk == "domain":
            dval = mod.get("domain")
            cases = [cid for cid, m in all_meta.items() if m.get("domain") == dval]
        else:
            cases = all_case_ids
        for r in mod.get("rules", []):
            rid = str(r["id"])
            p = str(r["counterfactual_preset"])
            presets.append(
                {
                    "preset": p,
                    "label": f"[{rid}] {r['name']}",
                    "desc": str(r.get("counterfactual_desc", "")),
                    "target_layer": layer,
                    "target_rule_id": rid,
                    "applicable_cases": cases,
                }
            )
    if case_id and case_id in all_meta:
        # 当前案例原生激活的 12 个预设排在最前，其余跨模态预设紧随其后也可一键沙盒验证
        native = [x for x in presets if case_id in x["applicable_cases"]]
        cross = [dict(x, label=f"{x['label']} (跨模态沙盒)") for x in presets if case_id not in x["applicable_cases"]]
        return native + cross
    return presets


def _apply_counterfactual_mutation(
    preset: str,
    skeleton: dict[str, Any],
    eu_tree: dict[str, Any],
    assumptions: list[dict[str, Any]],
    readback: dict[str, Any],
) -> str | None:
    """在内存深拷贝快照上执行真实结构破坏；返回 forced_admission_override（仅 GN-04 状态机篡改时非空）。"""
    by_id = {n["eu_id"]: n for n in eu_tree["nodes"]}

    if preset == "violate_PV01_partial_video_coverage":
        # 只保留 seg_03 (1.60~2.23s)，真实重算 coverage_ratio
        skeleton["segments"] = [s for s in skeleton["segments"] if s["segment_id"] == "seg_03"]
        dur = float(skeleton["duration_sec"])
        skeleton["coverage_ratio"] = round(sum(s["t1"] - s["t0"] for s in skeleton["segments"]) / dur, 4)

    elif preset == "violate_PV02_layout_noise_leak":
        # 将主舞台 frame_bbox 挪入噪点区（兼容 Code XR 与扩展视频案例）
        target = by_id.get("eu_L1_main_stage") or next(
            (n for n in eu_tree["nodes"] if n.get("template_slot") == "main_stage"),
            eu_tree["nodes"][0],
        )
        noise_list = skeleton.get("noise_regions") or []
        noise_bb = noise_list[-1].get("bbox") if noise_list else [120, 1520, 1400, 620]
        target["frame_bbox"] = list(noise_bb) if noise_bb else [120, 1520, 1400, 620]

    elif preset == "violate_PV03_transient_value_as_truth":
        # 把片尾滚动未定值改为 verified=True 并解除其假设绑定
        for obs in skeleton.get("observations", []):
            if obs.get("settle_state") == "transient":
                obs["verified"] = True
                obs["assumption_id"] = None
        assumptions[:] = [a for a in assumptions if a.get("bound_rule_id") != "PV-03"]

    elif preset == "violate_PV04_unbound_interaction_evidence":
        # 抹去观测交互边的时间区间与源帧包络
        for edge in eu_tree["edges"]:
            if edge.get("source") == "observed":
                edge["evidence"] = {}
                break

    elif preset == "violate_PI01_grid_chain_break":
        # 破坏 12 栏瑞士网格槽宽并使页眉偏离栏线
        skeleton["grid"]["gutter"] = 9.5
        target_l1 = "eu_L1_poster_header" if "eu_L1_poster_header" in by_id else next(
            (n["eu_id"] for n in eu_tree["nodes"] if n["level"] == "L1"),
            "eu_L1_poster_header",
        )
        if target_l1 in by_id:
            by_id[target_l1]["envelope_bbox"] = [17.5, 14.0, 260.0, 28.0]

    elif preset == "violate_PI02_foreground_background_merge":
        # 将前景文字合并进背景材质层
        for lyr in skeleton.get("layers", []):
            if lyr.get("layer_role") == "background_material":
                lyr["contains_text"] = True

    elif preset == "violate_PI03_illegal_atom_sample":
        # 将主墨色改为与背景纸基对比度极低的浅灰米色
        surf = eu_tree["atomic_registry"].get("surface_atoms", {})
        ink_aid = "ps_surf_ink" if "ps_surf_ink" in surf else next(
            (aid for aid in surf if "ink" in aid), None
        )
        if ink_aid:
            surf[ink_aid]["value"] = "#e3e2de" if "mn_" in ink_aid else "#f5ebe2"

    elif preset == "violate_PI04_missing_evidence_bbox":
        # 删除主标题解析节点的原图 evidence_bbox
        for n in eu_tree["nodes"]:
            if n["level"] == "L3" and n.get("source") == "parsed":
                n["evidence_bbox"] = None
                break

    elif preset == "violate_PW01_breakpoint_misalignment":
        # 在 390px 窄断点下令主舞台盒宽超出视口造成横向溢出
        bp390 = skeleton["dom"].get(390) or skeleton["dom"].get("390")
        if bp390:
            bp390["scroll_width"] = 620
            target_l2 = "eu_L2_web_metrics" if "eu_L2_web_metrics" in (bp390.get("rects") or {}) else next(
                (n["eu_id"] for n in eu_tree["nodes"] if n["level"] == "L2" and n["eu_id"] in (bp390.get("rects") or {})),
                "eu_L2_web_metrics",
            )
            bp390["rects"][target_l2] = {"x": 16, "y": 296, "w": 580, "h": 240}

    elif preset == "violate_PW02_raw_style_literal":
        if skeleton.get("computed_styles"):
            skeleton["computed_styles"][0]["token_ref"] = None

    elif preset == "violate_PW03_missing_a11y_role":
        if skeleton.get("interactive_elements"):
            skeleton["interactive_elements"][0]["role"] = ""
            skeleton["interactive_elements"][0]["states"] = ["default"]

    elif preset == "violate_PW04_decor_data_mixed":
        for cn in skeleton.get("content_nodes", []):
            if cn.get("content_class") == "decoration":
                cn["data_source"] = "leaked.business.feed"
                cn["aria_hidden"] = False

    elif preset == "violate_GN01_interaction_in_tree":
        # 把横向邻近调制塞进纵向组件树作为 interaction.* 子节点
        host = next((n for n in eu_tree["nodes"] if n["level"] == "L3"), eu_tree["nodes"][0])
        bad_id = "eu_L4_illegal_interaction_hover"
        host["children_ids"].append(bad_id)
        eu_tree["nodes"].append(
            {
                "eu_id": bad_id,
                "name": "非法塞入纵向树的悬停状态事件",
                "level": "L4",
                "level_num": 4,
                "node_kind": "interaction.pointer_hover_state",
                "parent_id": host["eu_id"],
                "children_ids": [],
                "adaptation_mode": "TEMPLATE_ANCHOR",
                "envelope_bbox": host.get("envelope_bbox"),
            }
        )

    elif preset == "violate_GN02_degree_overflow":
        # 撤销 FOLD_ARRAY 折叠，向同一 L2 父节点平铺 8 个同构 L3 兄弟使度达到 9 (>7)
        l2_parent = next((n for n in eu_tree["nodes"] if n["level"] == "L2"), eu_tree["nodes"][0])
        p_bbox = l2_parent.get("envelope_bbox") or [0, 0, 200, 200]
        for idx in range(8):
            cid = f"eu_L3_unfolded_item_{idx + 1}"
            l2_parent["children_ids"].append(cid)
            eu_tree["nodes"].append(
                {
                    "eu_id": cid,
                    "name": f"未折叠平铺同构项 #{idx + 1}",
                    "level": "L3",
                    "level_num": 3,
                    "entity": False,
                    "node_kind": "component.unfolded_card",
                    "parent_id": l2_parent["eu_id"],
                    "children_ids": ["eu_L4_dummy"],
                    "adaptation_mode": "TEMPLATE_ANCHOR",
                    "envelope_bbox": p_bbox,
                }
            )

    elif preset == "violate_GN03_missing_l5_atom":
        # 摘除首个实体 L3 子树内的 typography 与 evidence 原子引用
        first_l5 = next((n for n in eu_tree["nodes"] if n["level"] == "L5"), None)
        if first_l5:
            first_l5["atom_refs"] = []
        first_l3 = next((n for n in eu_tree["nodes"] if n["level"] == "L3" and n.get("entity")), None)
        if first_l3:
            first_l3["evidence_refs"] = []

    elif preset == "violate_GN04_envelope_overflow":
        # 将一个 L3 组件的几何包络大幅移出其父容器边界之外
        target_l3 = next((n for n in eu_tree["nodes"] if n["level"] == "L3" and n.get("envelope_bbox")), None)
        if target_l3:
            target_l3["envelope_bbox"] = [2200, 1600, 500, 400]
        return "RELEASE_READY"

    elif preset == "violate_GU01_token_bypass":
        readback["token_consumption"] = {
            "total_tokens": 18,
            "consumed_tokens": 14,
            "consumption_ratio": 0.7778,
            "unconsumed_atom_ids": ["mot_dock_proximity", "mot_rail_transition"],
        }
        readback["reduced_motion_supported"] = False

    elif preset == "violate_GU02_bitmap_solid_degradation":
        readback["editable_text_nodes"] = 0
        readback["interactive_controls"] = 0
        readback["ui_bitmap_area_ratio"] = 0.96
        readback["bitmaps"] = [{"id": "bmp_full_screenshot", "path": "screenshot_skin.png", "role": "ui_skin_bitmap", "area_ratio": 0.96}]
        stage_id = next(
            (n["eu_id"] for n in eu_tree["nodes"] if n.get("template_slot") == "main_stage"),
            "eu_L1_main_stage",
        )
        first_l3 = next(
            (n["eu_id"] for n in eu_tree["nodes"] if n["level"] == "L3" and n.get("rendered")),
            "eu_L3_sprint_hero",
        )
        readback["degraded_node_ids"] = [stage_id, first_l3]

    elif preset == "violate_GU03_missing_proximity_magnify":
        for item in readback.get("interactions", []):
            if item.get("edge_type") == "MODULATES_NEIGHBOR":
                item["passed"] = False
                item["measure"] = {"focus_scale": 1.0, "neighbor_scale": 1.0, "neutral_scale": 1.0, "far_scale": 1.0, "restored_after_leave": False}
        if not any(i.get("edge_type") == "MODULATES_NEIGHBOR" for i in readback.get("interactions", [])):
            # 若在 web_fixture 上触发，则令首条交互边失效
            if readback.get("interactions"):
                readback["interactions"][0]["passed"] = False

    elif preset == "violate_GU04_defensive_microcopy":
        readback["defensive_microcopy_violations"] = 2
        readback["defensive_hits"] = ["不会丢失", "仅供演示"]
        target_l3 = "eu_L3_sprint_hero" if "eu_L3_sprint_hero" in by_id else next(
            (n["eu_id"] for n in eu_tree["nodes"] if n["level"] == "L3" and n.get("rendered")),
            "eu_L3_sprint_hero",
        )
        readback["missing_trace_ids"] = [target_l3]
        readback["dom_eu_binding_coverage"] = 0.92

    elif preset == "violate_GG01_bleed_grid_break":
        pc = readback.setdefault("poster_canvas", {})
        pc["bleed"] = {"top": 0.0, "right": 0.0, "bottom": 0.0, "left": 0.0}
        target_l2 = "eu_L2_poster_logo_region" if "eu_L2_poster_logo_region" in by_id else next(
            (n["eu_id"] for n in eu_tree["nodes"] if n["level"] == "L2"),
            None,
        )
        if target_l2 and target_l2 in by_id:
            by_id[target_l2]["envelope_bbox"] = [3.0, 4.0, 190.0, 28.0]

    elif preset == "violate_GG02_hierarchy_inversion":
        pc = readback.setdefault("poster_canvas", {})
        pc["hierarchy_scales_px"] = {"display": 52.0, "headline": 20.0, "body": 28.0, "caption": 11.0}

    elif preset == "violate_GG03_rasterized_text":
        readback["live_text_ratio"] = 0.45
        readback["rasterized_text_count"] = 3
        target_hl = "eu_L3_poster_headline" if "eu_L3_poster_headline" in by_id else next(
            (n["eu_id"] for n in eu_tree["nodes"] if n.get("carries_text")),
            None,
        )
        if target_hl and target_hl in by_id:
            by_id[target_hl]["rendered_as"] = "bitmap"

    elif preset == "violate_GG04_export_drift":
        pc = readback.setdefault("poster_canvas", {})
        pc["reopen_max_drift_mm"] = 4.8
        readback["dangling_trace_ids"] = ["eu_L3_ghost_orphan"]

    return None


def build_eu_tree_for_case(case_id: str) -> dict[str, Any]:
    """根据 case_id 分发构建对应的 L0~L5 自适应语义树。"""
    if case_id == "code_xr_uiux":
        return build_eu_tree_code_xr_uiux()
    if case_id == "code_xr_poster":
        return build_eu_tree_code_xr_poster()
    if case_id == "web_fixture":
        return build_eu_tree_web_fixture()
    if case_id == "refract_crm_web":
        return catalog_mod.build_eu_tree_refract_crm_web(_finalize_tree)
    if case_id == "haven_admin_web":
        return catalog_mod.build_eu_tree_haven_admin_web(_finalize_tree)
    if case_id in styles_mod.STYLE_CASE_META:
        return styles_mod.build_style_eu_tree(case_id, _finalize_tree)
    if case_id in motion_mod.MOTION_CASE_META:
        return motion_mod.build_motion_eu_tree(case_id, _finalize_tree)
    imported = parsers_mod.load_imported_case(case_id)
    if imported and isinstance(imported.get("raw_eu_spec"), dict):
        spec = imported["raw_eu_spec"]
        return _finalize_tree(
            spec["template_id"],
            spec["template_name"],
            spec["root_id"],
            copy.deepcopy(spec["nodes"]),
            copy.deepcopy(spec["atomic_registry"]),
            copy.deepcopy(spec["edges"]),
        )
    raise ValueError(f"Unknown case_id: {case_id}")


def _build_raw_case_components(case_id: str, persist_skeleton: bool = False) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    skeleton = skel_mod.extract_case_skeleton(case_id, persist=persist_skeleton)
    eu_tree = build_eu_tree_for_case(case_id)
    assumptions = get_case_assumptions(case_id)
    readback = readback_mod.run_generator_readback(case_id, eu_tree)
    return skeleton, eu_tree, assumptions, readback


class _CaseLibrary(NamedTuple):
    rule_modules: list[dict[str, Any]]
    templates: dict[str, dict[str, Any]]
    categories: dict[str, dict[str, Any]]


def _load_case_library(categories: dict[str, dict[str, Any]] | None = None) -> _CaseLibrary:
    return _CaseLibrary(
        load_all_rule_modules(), load_all_templates(),
        cat_reg.load_categories() if categories is None else categories,
    )


def _case_read_scope(case_id: str):
    # Imported case paths can change together while a new snapshot is published.
    return nullcontext() if case_id in CASE_META else parsers_mod.CASE_FILES_LOCK


def _evaluate_case(case_id: str, library: _CaseLibrary, persist_skeleton: bool = False) -> dict[str, Any]:
    meta = _get_case_meta(case_id)
    cat_info = cat_reg.get_case_category(case_id, meta, categories=library.categories)
    skeleton, eu_tree, assumptions, readback = _build_raw_case_components(case_id, persist_skeleton=persist_skeleton)
    gates, admission = evaluate_three_layer_gates(
        modality=meta["modality"],
        domain=meta["domain"],
        skeleton=skeleton,
        eu_tree=eu_tree,
        assumptions=assumptions,
        readback=readback,
        category_id=cat_info["category_id"],
        rule_modules=library.rule_modules,
        templates=library.templates,
        categories=library.categories,
    )
    open_cnt = sum(1 for a in assumptions if a.get("status") == "open")
    rule_summary = " → ".join(f"{l['prefix']} {l['passed']}/{l['total']}" for l in gates["layers"])
    case_info = {
        **meta,
        "category_id": cat_info["category_id"],
        "category_name": cat_info["category_name"],
        "category_tier": cat_info["category_tier"],
        "is_imported": bool(meta.get("is_imported", False)),
        "admission_status": admission,
        "open_assumptions_count": open_cnt,
        "total_assumptions_count": len(assumptions),
        "active_rule_summary": rule_summary,
    }
    return {
        "status": "OK",
        "version": WORKBENCH_VERSION,
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "admission_status": admission,
        "open_assumptions_count": open_cnt,
        "stage_url": meta["stage_url"],
        "case_info": case_info,
        "skeleton": skeleton,
        "eu_tree": eu_tree,
        "gates": gates,
        "assumptions": assumptions,
        "readback": readback,
    }


def build_case_summaries(
    case_ids: list[str], *, categories: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Evaluate each case with one shared rule, template and category snapshot."""
    library = _load_case_library(categories)
    summaries = []
    for case_id in case_ids:
        with _case_read_scope(case_id):
            summaries.append(_evaluate_case(case_id, library)["case_info"])
    return summaries


def build_case_bundle(case_id: str, persist: bool = False) -> dict[str, Any]:
    """构建并返回指定案例的完整 inspection_bundle.json 结构。"""
    library = _load_case_library()
    with _case_read_scope(case_id):
        bundle = _evaluate_case(case_id, library, persist_skeleton=persist)
        bundle["category_audit"] = cat_reg.evaluate_category_audit(
            bundle["case_info"]["category_id"], bundle["skeleton"], bundle["eu_tree"], bundle["readback"],
            categories=library.categories,
        )
        bundle["counterfactual_presets"] = get_counterfactual_presets(case_id, rule_modules=library.rule_modules)
        bundle["error_ledger"] = load_error_ledger()
        if persist and case_id != "web_fixture":
            out_path = CASES_DIR / case_id / "inspection_bundle.json"
            _write_json_atomically(out_path, bundle)
        return bundle


def run_counterfactual_sandbox(case_id: str, preset: str) -> dict[str, Any]:
    """在内存隔离沙盒中执行反事实异常注入并调用同一规则引擎求值归因。"""
    if not preset or preset in ("reset", "none", "valid_pass", "pass"):
        b = build_case_bundle(case_id, persist=False)
        return {
            "status": "OK",
            "case_id": case_id,
            "evaluated_case_id": case_id,
            "preset": "reset",
            "admission_status": b["admission_status"],
            "verdict": b["gates"]["verdict"],
            "blocked_layer": None,
            "violated_rule_id": None,
            "violated_rule_name": None,
            "violated_node_ids": [],
            "co_failed_rule_ids": [],
            "attribution": None,
            "gates": b["gates"],
            "readback": b["readback"],
        }

    library = _load_case_library()
    with parsers_mod.CASE_FILES_LOCK:
        _get_case_meta(case_id)
        presets = get_counterfactual_presets(rule_modules=library.rule_modules)
        pinfo = next((info for info in presets if info["preset"] == preset), None)
        if not pinfo or not pinfo["applicable_cases"]:
            raise ValueError(f"No case is available for counterfactual preset: {preset}")

        # 若当前案例未激活该预设所属模态/领域，自动路由至适用的宿主案例内存快照
        eval_case_id = case_id if case_id in pinfo["applicable_cases"] else pinfo["applicable_cases"][0]
        meta = _get_case_meta(eval_case_id)
        skeleton, eu_tree, assumptions, readback = _build_raw_case_components(eval_case_id, persist_skeleton=False)

    skeleton_sb = copy.deepcopy(skeleton)
    eu_tree_sb = copy.deepcopy(eu_tree)
    assumptions_sb = copy.deepcopy(assumptions)
    readback_sb = copy.deepcopy(readback)

    forced_adm = _apply_counterfactual_mutation(preset, skeleton_sb, eu_tree_sb, assumptions_sb, readback_sb)
    eval_cat_id = cat_reg.get_case_category(eval_case_id, meta, categories=library.categories)["category_id"]
    gates, admission = evaluate_three_layer_gates(
        modality=meta["modality"],
        domain=meta["domain"],
        skeleton=skeleton_sb,
        eu_tree=eu_tree_sb,
        assumptions=assumptions_sb,
        readback=readback_sb,
        target_rule_hint=pinfo["target_rule_id"],
        forced_admission_override=forced_adm,
        category_id=eval_cat_id,
        rule_modules=library.rule_modules,
        templates=library.templates,
        categories=library.categories,
    )

    return {
        "status": "OK",
        "case_id": case_id,
        "evaluated_case_id": eval_case_id,
        "preset": preset,
        "admission_status": admission,
        "verdict": gates["verdict"],
        "blocked_layer": gates["blocked_layer"],
        "violated_rule_id": gates["violated_rule_id"],
        "violated_rule_name": gates["violated_rule_name"],
        "violated_node_ids": gates["violated_node_ids"],
        "co_failed_rule_ids": gates["co_failed_rule_ids"],
        "attribution": gates["attribution"],
        "gates": gates,
        "readback": readback_sb,
    }


def explain_eu_node(case_id: str, eu_id: str) -> dict[str, Any]:
    """组装指定 EU 节点的向上祖先链 (L0->parent)、向下特征/L5原子链、横向交互边与关联假设。"""
    library = _load_case_library()
    with _case_read_scope(case_id):
        bundle = _evaluate_case(case_id, library)
    eu_tree = bundle["eu_tree"]
    by_id = {n["eu_id"]: n for n in eu_tree["nodes"]}
    if eu_id not in by_id:
        raise KeyError(f"EU node '{eu_id}' not found in case '{case_id}'")

    node = by_id[eu_id]
    ancestors: list[dict[str, Any]] = []
    cur_pid = node.get("parent_id")
    while cur_pid and cur_pid in by_id:
        pn = by_id[cur_pid]
        ancestors.append(
            {
                "eu_id": pn["eu_id"],
                "name": pn["name"],
                "level": pn["level"],
                "adaptation_badge": pn["adaptation_badge"],
            }
        )
        cur_pid = pn.get("parent_id")
    ancestors.reverse()

    # 向下收集子树内 L4 特征、L5 原子详情与直接子节点
    reg = eu_tree["atomic_registry"]
    atom_lookup = {aid: (sec, atom) for sec, sec_d in reg.items() for aid, atom in sec_d.items()}

    def collect_sub(uid: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for cid in by_id[uid].get("children_ids", []):
            if cid in by_id:
                out.append(by_id[cid])
                out.extend(collect_sub(cid))
        return out

    sub_nodes = collect_sub(eu_id)
    if node["level"] == "L4":
        l4_feats = [{"eu_id": node["eu_id"], "name": node["name"], "node_kind": node["node_kind"]}]
    else:
        l4_feats = [{"eu_id": sn["eu_id"], "name": sn["name"], "node_kind": sn["node_kind"]} for sn in sub_nodes if sn["level"] == "L4"]

    l5_sources = [node] if node["level"] == "L5" else [sn for sn in sub_nodes if sn["level"] == "L5"]
    seen_atoms: set[str] = set()
    l5_atoms: list[dict[str, Any]] = []
    for l5n in l5_sources:
        for ref in l5n.get("atom_refs", []):
            if ref in atom_lookup and ref not in seen_atoms:
                seen_atoms.add(ref)
                cat, atom = atom_lookup[ref]
                l5_atoms.append(
                    {
                        "eu_id": l5n["eu_id"],
                        "atom_id": ref,
                        "category": cat,
                        "name": atom.get("name", ref),
                        "value": atom.get("value") or atom.get("frame") or str(atom.get("evidence_bbox", "")),
                    }
                )

    direct_children = [
        {
            "eu_id": by_id[cid]["eu_id"],
            "name": by_id[cid]["name"],
            "level": by_id[cid]["level"],
            "adaptation_badge": by_id[cid]["adaptation_badge"],
        }
        for cid in node.get("children_ids", [])
        if cid in by_id
    ]

    sub_id_set = {eu_id} | {sn["eu_id"] for sn in sub_nodes}
    related_edges: list[dict[str, Any]] = []
    for e in eu_tree["edges"]:
        s_id, t_id = e["source_eu_id"], e["target_eu_id"]
        if s_id in sub_id_set or t_id in sub_id_set:
            outgoing = s_id in sub_id_set
            peer_id = t_id if outgoing else s_id
            peer = by_id.get(peer_id, {})
            related_edges.append(
                {
                    "edge_id": e["edge_id"],
                    "edge_type": e["edge_type"],
                    "direction": "outgoing" if outgoing else "incoming",
                    "source_eu_id": s_id,
                    "target_eu_id": t_id,
                    "peer_eu_id": peer_id,
                    "peer_name": peer.get("name", peer_id),
                    "label": e["label"],
                }
            )

    related_assumptions = [
        a for a in bundle["assumptions"]
        if a.get("eu_id") in sub_id_set or any(sid in sub_id_set for sid in (a.get("subject_ids") or []))
    ]

    bound_rules: list[str] = []
    for lyr in bundle["gates"]["layers"]:
        for r in lyr["rules"]:
            bound_rules.append(r["rule_id"])

    # 提供 fallback_eu_id 给前端 iframe：当选中 L2 或 L5 时自动映射到最近的渲染 L3/L4 节点
    fallback_dom_id = eu_id
    if not node.get("rendered"):
        # 先找子树内的渲染节点，否则向上找祖先渲染节点
        sub_rendered = next((sn["eu_id"] for sn in sub_nodes if sn.get("rendered")), None)
        if sub_rendered:
            fallback_dom_id = sub_rendered
        else:
            for anc in reversed(ancestors):
                if by_id[anc["eu_id"]].get("rendered"):
                    fallback_dom_id = anc["eu_id"]
                    break

    return {
        "status": "OK",
        "case_id": case_id,
        "eu_id": eu_id,
        "fallback_eu_id": fallback_dom_id,
        "node": node,
        "ancestors": ancestors,
        "descendants": {
            "l4_features": l4_feats,
            "l5_atoms": l5_atoms,
            "children": direct_children,
        },
        "edges": related_edges,
        "assumptions": related_assumptions,
        "bound_rules": bound_rules,
    }


def get_rules_catalog() -> dict[str, Any]:
    modules_raw = load_all_rule_modules()
    templates_raw = load_all_templates()
    modules_out: list[dict[str, Any]] = []
    total_rules = 0
    for m in modules_raw:
        rk = str(m.get("route_key", ""))
        rv = str(m.get(rk, ""))
        rlist = []
        for r in m.get("rules", []):
            total_rules += 1
            rlist.append(
                {
                    "rule_id": r["id"],
                    "id": r["id"],
                    "name": r["name"],
                    "name_en": r.get("name_en", ""),
                    "severity": r.get("severity", "BLOCKER"),
                    "bound_eu_levels": r.get("bound_eu_levels", []),
                    "check_code": r.get("check_code", ""),
                    "desc": r.get("desc", ""),
                    "counterfactual_preset": r.get("counterfactual_preset", ""),
                }
            )
        modules_out.append(
            {
                "module_id": m["module_id"],
                "title": m.get("layer_name", m["module_id"]),
                "name": m.get("layer_name", m["module_id"]),
                "layer": m["layer"],
                "route_key": rk,
                "route_value": rv,
                "rule_prefix": m.get("rule_prefix", ""),
                "rules": rlist,
            }
        )

    templates_out = [
        {
            "template_id": tid,
            "template_name": t.get("template_name", tid),
            "domain": t.get("domain", ""),
            "slot_ids": t.get("slot_ids", []),
            "allowed_edge_types": t.get("allowed_edge_types", []),
        }
        for tid, t in templates_raw.items()
    ]
    return {
        "status": "OK",
        "version": WORKBENCH_VERSION,
        "total_rules": total_rules,
        "templates_loaded": len(templates_out),
        "modules": modules_out,
        "templates": templates_out,
    }
