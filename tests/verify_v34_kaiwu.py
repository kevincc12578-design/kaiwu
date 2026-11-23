# -*- coding: utf-8 -*-
"""
开物 v3.4 · Kaiwu Adaptive-EU Design Workbench 独立全栈与浏览器自动化验收套件
文件所有权：@verifier
运行方式：python tests/verify_v34_kaiwu.py [--artifacts-dir <dir>] [--skip-e2e] [--screenshot-dir <dir>]

验收覆盖 5 大维度：
1. 三层 Y 型正交规则与原型模板规范核验（6 YAML × 4 = 24 条规则、零单项目硬编码、Y 型 3 路由各激活 12 条）
2. 模板引导自适应语义与 Code XR 全段结案核验（L0~L5 完整、度 <= 7、6 类横向边白名单、分裂/折叠/锚定、100% L5 覆盖、5.689s 全覆盖、三态状态机跃迁与复位）
3. 反事实异常注入真拦截核验（全部 24 项预设真实沙盒拦截、精准当层 BLOCKED 与首障归因）
4. REST API 契约与独立源码回检核验（/api/health, /cases, /rules, /bundle, /explain, /error_ledger, readback 100%）
5. 真实服务与无头 Chromium (1440×900) 端到端交互核验 + 4 张核心实测截图留存

输出成果：
- 本次输出目录中的 v34_verification_report.json
- 4 张 1440×900 实测截图
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
import urllib.parse
from typing import Any

import yaml

from verification_env import VerificationRun, isolated_workbench

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "3.4.0"

RULE_FILES_SPEC = {
    "general_rules.yaml": {"layer": "general", "route_key": "scope", "route_val": "all", "prefix": "GN"},
    "parsing_video.yaml": {"layer": "parsing", "route_key": "modality", "route_val": "video", "prefix": "PV"},
    "parsing_image.yaml": {"layer": "parsing", "route_key": "modality", "route_val": "image", "prefix": "PI"},
    "parsing_web.yaml": {"layer": "parsing", "route_key": "modality", "route_val": "web", "prefix": "PW"},
    "generation_uiux.yaml": {"layer": "generation", "route_key": "domain", "route_val": "uiux", "prefix": "GU"},
    "generation_graphic.yaml": {"layer": "generation", "route_key": "domain", "route_val": "graphic", "prefix": "GG"},
}

ALLOWED_EDGE_TYPES = {
    "TRIGGERS_STATE",
    "RESTORES_FOCUS",
    "FILTERS_VIEW",
    "MODULATES_NEIGHBOR",
    "SCROLLS_INDEPENDENTLY",
    "SHARES_TOKEN",
}

FORBIDDEN_TREE_PREFIXES = ("interaction.", "event.", "state.", "edge.", "transition.")

FORBIDDEN_SINGLE_PROJECT_TOKENS = [
    "Code XR",
    "code_xr",
    "5.689",
    "1.37",
    "1920",
    "2560",
    "room.webp",
    "Analytics",
]

FORBIDDEN_DEFENSIVE_MICROCOPY = [
    "不会丢失",
    "不会丢",
    "仍可用",
    "仍然可用",
    "仅供演示",
    "仅供参考",
    "仅作示意",
    "请放心",
    "无需担心",
    "温馨提示",
    "本页面仅",
    "以下内容仅",
]


class VerificationContext:
    def __init__(self, run: VerificationRun, screenshot_dir: pathlib.Path):
        self.run = run
        self.results: dict[str, list[dict[str, Any]]] = {}
        self.errors: list[str] = []
        self.metrics: dict[str, Any] = {}
        self.screenshots: list[dict[str, str]] = []
        self.screenshot_dir = screenshot_dir

    def record_pass(self, category: str, test_id: str, detail: str = "") -> None:
        self.results.setdefault(category, []).append({"id": test_id, "status": "PASS", "detail": detail})
        print(f"  [PASS] [{category}] {test_id}: {detail}")

    def record_fail(self, category: str, test_id: str, reason: str) -> None:
        self.results.setdefault(category, []).append({"id": test_id, "status": "FAIL", "reason": reason})
        self.errors.append(f"[{category}] {test_id}: {reason}")
        print(f"  [FAIL] [{category}] {test_id}: {reason}")


# ==============================================================================
# 维度 1：三层 Y 型正交规则与原型模板规范核验
# ==============================================================================
def test_1_rules_and_templates(ctx: VerificationContext) -> None:
    print("\n" + "=" * 80)
    print("【维度 1】三层 Y 型正交规则与原型模板规范核验")
    print("=" * 80)
    cat = "rules_and_templates"

    # 1.1 文档与 VERSION 检查
    ver_path = ctx.run.root / "VERSION"
    if ver_path.exists() and ver_path.read_text(encoding="utf-8").strip() == EXPECTED_VERSION:
        ctx.record_pass(cat, "version_340", f"VERSION 精确为 {EXPECTED_VERSION}")
    else:
        ctx.record_fail(cat, "version_340", f"VERSION 缺失或不等于 {EXPECTED_VERSION}")

    for doc_rel in ("README.md", "CHANGELOG.md", "UI与交互EU错误排查台账.md", "docs/ARCHITECTURE_v3.4.md"):
        p = ctx.run.root / doc_rel
        if p.exists() and p.stat().st_size > 200:
            ctx.record_pass(cat, f"doc_{p.stem}", f"{doc_rel} 存在且非空 ({p.stat().st_size} bytes)")
        else:
            ctx.record_fail(cat, f"doc_{p.stem}", f"文档缺失或过小: {doc_rel}")

    # 1.2 6 个 YAML 文件 × 4 条 = 24 条规则检查 + 零单项目硬编码检查
    all_presets: list[str] = []
    all_rule_ids: list[str] = []
    for fname, spec in RULE_FILES_SPEC.items():
        ypath = ctx.run.root / "rules" / fname
        try:
            assert ypath.exists(), f"Missing {ypath}"
            raw_text = ypath.read_text(encoding="utf-8")
            data = yaml.safe_load(raw_text)
            assert data.get("version") == EXPECTED_VERSION
            assert data.get("layer") == spec["layer"]
            assert data.get("route_key") == spec["route_key"]
            assert data.get(spec["route_key"]) == spec["route_val"]
            assert data.get("rule_prefix") == spec["prefix"]
            rules = data.get("rules", [])
            assert isinstance(rules, list) and len(rules) == 4, f"Expected 4 rules, got {len(rules)}"

            expected_ids = [f"{spec['prefix']}-0{i}" for i in range(1, 5)]
            got_ids = [r.get("id") for r in rules]
            assert got_ids == expected_ids, f"Rule IDs mismatch: {got_ids} != {expected_ids}"

            for r in rules:
                for field in (
                    "id",
                    "name",
                    "severity",
                    "bound_eu_levels",
                    "check_code",
                    "thresholds",
                    "invariants",
                    "failure_boundary",
                    "counterfactual_preset",
                ):
                    assert field in r and r[field], f"Missing {field} in {r.get('id')}"
                assert r["severity"] == "BLOCKER"
                all_rule_ids.append(r["id"])
                all_presets.append(r["counterfactual_preset"])

            # 零单项目硬编码数字/名称校验（在规则定义主体序列化文本中检测）
            serialized_rules = json.dumps(rules, ensure_ascii=False)
            hits = [tok for tok in FORBIDDEN_SINGLE_PROJECT_TOKENS if tok in serialized_rules]
            assert not hits, f"Single-project hardcoded tokens found in {fname}: {hits}"

            ctx.record_pass(
                cat,
                f"rule_yaml_{fname}",
                f"{fname} 含 {got_ids} 共 4 条 BLOCKER 规则，字段齐全，零单项目硬编码",
            )
        except Exception as e:
            ctx.record_fail(cat, f"rule_yaml_{fname}", str(e))

    if len(all_rule_ids) == 24 and len(set(all_presets)) == 24:
        ctx.record_pass(cat, "total_24_unique_presets", "全库 24 条规则与 24 个反事实预设唯一且闭合")
    else:
        ctx.record_fail(
            cat,
            "total_24_unique_presets",
            f"规则数={len(all_rule_ids)}, 唯一预设数={len(set(all_presets))}",
        )

    # 1.3 2 个原型模板 YAML 校验
    for tpl_name, exp_id, exp_domain in (
        ("uiux_workspace_template.yaml", "tpl_uiux_workspace_v1", "uiux"),
        ("graphic_poster_template.yaml", "tpl_graphic_poster_v1", "graphic"),
    ):
        tpath = ctx.run.root / "templates" / tpl_name
        try:
            assert tpath.exists(), f"Missing {tpath}"
            tdata = yaml.safe_load(tpath.read_text(encoding="utf-8"))
            assert tdata.get("template_id") == exp_id
            assert tdata.get("domain") == exp_domain
            assert len(tdata.get("l1_territories", [])) == 4
            assert len(tdata.get("level_contract", [])) == 6
            assert "SPLIT_HIGH_INTERACTION" in tdata.get("adaptive_policies", {})
            assert "FOLD_ARRAY" in tdata.get("adaptive_policies", {})
            ctx.record_pass(cat, f"template_{exp_id}", f"{tpl_name} 结构完整，含 4 大 L1 领地与分裂/折叠策略")
        except Exception as e:
            ctx.record_fail(cat, f"template_{exp_id}", str(e))

    # 1.4 Y 型动态三路由激活矩阵核验（需要后端 API）
    expected_routes = {
        "code_xr_uiux": (["PV-01", "PV-02", "PV-03", "PV-04"], ["GN-01", "GN-02", "GN-03", "GN-04"], ["GU-01", "GU-02", "GU-03", "GU-04"]),
        "code_xr_poster": (["PI-01", "PI-02", "PI-03", "PI-04"], ["GN-01", "GN-02", "GN-03", "GN-04"], ["GG-01", "GG-02", "GG-03", "GG-04"]),
        "web_fixture": (["PW-01", "PW-02", "PW-03", "PW-04"], ["GN-01", "GN-02", "GN-03", "GN-04"], ["GU-01", "GU-02", "GU-03", "GU-04"]),
    }
    for cid, (exp_p, exp_g, exp_o) in expected_routes.items():
        try:
            b = ctx.run.get_json(f"/api/case/{cid}/bundle")
            gates = b["gates"]
            assert gates["active_count"] == 12, f"active_count={gates['active_count']}"
            assert gates["total_library_rules"] == 24
            by_l = gates["by_layer"]
            got_p = [r["rule_id"] for r in by_l["parsing"]["rules"]]
            got_g = [r["rule_id"] for r in by_l["general"]["rules"]]
            got_o = [r["rule_id"] for r in by_l["generation"]["rules"]]
            assert got_p == exp_p, f"parsing mismatch: {got_p} != {exp_p}"
            assert got_g == exp_g, f"general mismatch: {got_g} != {exp_g}"
            assert got_o == exp_o, f"generation mismatch: {got_o} != {exp_o}"
            assert gates["verdict"] == "PASS"
            ctx.record_pass(
                cat,
                f"y_route_{cid}",
                f"{cid} 精准激活 {got_p[0][:2]}(4)+GN(4)+{got_o[0][:2]}(4)=12 条且全部 PASS",
            )
        except Exception as e:
            ctx.record_fail(cat, f"y_route_{cid}", str(e))


# ==============================================================================
# 维度 2：模板引导自适应语义与 Code XR 全段结案核验
# ==============================================================================
def test_2_adaptive_eu_and_lifecycle(ctx: VerificationContext) -> None:
    print("\n" + "=" * 80)
    print("【维度 2】模板引导自适应语义与 Code XR 全段结案核验")
    print("=" * 80)
    cat = "adaptive_eu_and_lifecycle"

    for cid in ("code_xr_uiux", "code_xr_poster", "web_fixture"):
        try:
            b = ctx.run.get_json(f"/api/case/{cid}/bundle")
            tree = b["eu_tree"]
            nodes = tree["nodes"]
            by_id = {n["eu_id"]: n for n in nodes}
            edges = tree["edges"]
            reg = tree["atomic_registry"]

            # 2.1 六级完整无跳层、单父无环、度 <= 7、无交互混入纵向树
            roots = [n for n in nodes if n["level"] == "L0"]
            assert len(roots) == 1, f"L0 count != 1: {len(roots)}"
            root = roots[0]
            assert root.get("parent_id") is None

            visited: set[str] = set()

            def walk(uid: str, expected_lvl: int) -> None:
                assert uid not in visited, f"Cycle detected at {uid}"
                visited.add(uid)
                node = by_id[uid]
                assert node["level_num"] == expected_lvl, f"Level jump at {uid}: {node['level_num']} != {expected_lvl}"
                nk = node.get("node_kind", "")
                assert not nk.startswith(FORBIDDEN_TREE_PREFIXES), f"Interaction in tree: {uid} ({nk})"
                kids = node.get("children_ids", [])
                assert len(kids) <= 7, f"Degree overflow at {uid}: {len(kids)}"
                if expected_lvl <= 3:
                    assert len(kids) > 0, f"Empty shell node at {uid}"
                for kid in kids:
                    assert kid in by_id, f"Missing child {kid}"
                    assert by_id[kid]["parent_id"] == uid, f"Parent mismatch on {kid}"
                    walk(kid, expected_lvl + 1)

            walk(root["eu_id"], 0)
            assert len(visited) == len(nodes), f"Unreachable nodes: {len(nodes) - len(visited)}"
            levels_present = {n["level"] for n in nodes}
            assert levels_present == {"L0", "L1", "L2", "L3", "L4", "L5"}, f"Missing levels: {levels_present}"

            # 2.2 6 类横向边白名单校验
            for e in edges:
                assert e["edge_type"] in ALLOWED_EDGE_TYPES, f"Illegal edge_type: {e['edge_type']}"
                assert e["source_eu_id"] in by_id and e["target_eu_id"] in by_id
                assert e["source_eu_id"] != e["target_eu_id"]

            # 2.3 自适应操作模式校验 (TEMPLATE_ANCHOR / SPLIT_HIGH_INTERACTION / FOLD_ARRAY)
            modes = {n.get("adaptation_mode") for n in nodes}
            assert "TEMPLATE_ANCHOR" in modes, f"Missing TEMPLATE_ANCHOR in {cid}"
            if cid in ("code_xr_uiux", "code_xr_poster"):
                assert "SPLIT_HIGH_INTERACTION" in modes, f"Missing SPLIT_HIGH_INTERACTION in {cid}"
            assert "FOLD_ARRAY" in modes, f"Missing FOLD_ARRAY in {cid}"
            fold_hosts = [n for n in nodes if n.get("adaptation_mode") == "FOLD_ARRAY"]
            assert all((n.get("array_count") or 0) >= 3 for n in fold_hosts), "FOLD_ARRAY host array_count < 3"

            # 2.4 单源双索引 atomic_registry + 100% L5 覆盖
            expected_secs = {"surface_atoms", "typography_atoms", "layout_atoms", "motion_atoms", "evidence_atoms"}
            assert set(reg.keys()) == expected_secs
            atom_lookup = {aid: atom for sec in reg.values() for aid, atom in sec.items()}
            for n in nodes:
                if n["level"] == "L5":
                    refs = n.get("atom_refs", [])
                    assert len(refs) >= 1, f"L5 node {n['eu_id']} has no atom_refs"
                    for ref in refs:
                        assert ref in atom_lookup, f"Unresolved atom_ref {ref}"
            for aid, atom in atom_lookup.items():
                used = atom.get("used_by", [])
                assert len(used) >= 1 and all(u in by_id for u in used), f"Orphan or dangling atom {aid}: {used}"
            assert tree["stats"]["l3_atom_coverage_ratio"] == 1.0

            ctx.record_pass(
                cat,
                f"tree_and_atoms_{cid}",
                f"{cid} L0~L5 共 {len(nodes)} 节点, max_degree={tree['stats']['max_child_degree']}<=7, "
                f"{len(edges)} 条横向边合规, 含锚定/分裂/折叠, L5覆盖率=100%",
            )
            ctx.metrics[f"{cid}_stats"] = tree["stats"]
        except Exception as e:
            ctx.record_fail(cat, f"tree_and_atoms_{cid}", str(e))

    # 2.5 Code XR 5.689s 连续时段 100% 全覆盖校验
    try:
        b = ctx.run.get_json("/api/case/code_xr_uiux/bundle")
        sk = b["skeleton"]
        dur = float(sk["duration_sec"])
        segs = sorted(sk["segments"], key=lambda s: float(s["t0"]))
        assert abs(dur - 5.689) <= 0.001, f"duration_sec={dur}"
        assert abs(float(sk["coverage_ratio"]) - 1.0) <= 0.001, f"coverage_ratio={sk['coverage_ratio']}"
        assert len(segs) == 6, f"Expected 6 segments, got {len(segs)}"
        assert abs(float(segs[0]["t0"]) - 0.0) <= 0.001
        assert abs(float(segs[-1]["t1"]) - dur) <= 0.001
        for i in range(len(segs) - 1):
            assert abs(float(segs[i + 1]["t0"]) - float(segs[i]["t1"])) <= 0.001, f"Gap/overlap between seg {i} and {i+1}"
        for s in segs:
            assert len(s.get("active_eu_ids", [])) >= 1
            f_url = s["frame_url"].lstrip("/")
            assert (ctx.run.root / f_url).exists(), f"Missing frame file {f_url}"
        ctx.record_pass(
            cat,
            "codexr_full_timeline_5689s",
            f"Code XR 0.00~{dur:.3f}s 共 6 段无缝闭合覆盖 100%，6 张真帧文件全部落盘",
        )
    except Exception as e:
        ctx.record_fail(cat, "codexr_full_timeline_5689s", str(e))

    # 2.6 三态准入状态机实测：PROVISIONAL -> RELEASE_READY -> PROVISIONAL
    try:
        # 先确保处于初始 open 状态
        ctx.run.post_json("/api/case/code_xr_uiux/confirm_assumption", {"assumption_id": "ALL", "action": "reset"})
        b0 = ctx.run.get_json("/api/case/code_xr_uiux/bundle")
        assert b0["admission_status"] == "PROVISIONAL", f"Initial status={b0['admission_status']}"
        open_n = b0["open_assumptions_count"]
        assert open_n >= 3, f"Expected >= 3 open assumptions, got {open_n}"

        res_confirm = ctx.run.post_json(
            "/api/case/code_xr_uiux/confirm_assumption",
            {"assumption_id": "ALL", "action": "confirm_all"},
        )
        assert res_confirm["open_assumptions_count"] == 0
        assert res_confirm["admission_status"] == "RELEASE_READY"

        res_reset = ctx.run.post_json(
            "/api/case/code_xr_uiux/confirm_assumption",
            {"assumption_id": "ALL", "action": "reset"},
        )
        assert res_reset["open_assumptions_count"] == open_n
        assert res_reset["admission_status"] == "PROVISIONAL"

        ctx.record_pass(
            cat,
            "tri_state_admission_fsm",
            f"准入状态机闭环：初始 PROVISIONAL ({open_n} open) → confirm_all 跃迁 RELEASE_READY → reset 恢复 PROVISIONAL",
        )
    except Exception as e:
        ctx.record_fail(cat, "tri_state_admission_fsm", str(e))


# ==============================================================================
# 维度 3：反事实异常注入真拦截核验（全 24 项预设全覆盖）
# ==============================================================================
def test_3_counterfactual_rule_gates(ctx: VerificationContext) -> None:
    print("\n" + "=" * 80)
    print("【维度 3】反事实异常注入与三层门禁真拦截核验（全 24 项预设全覆盖）")
    print("=" * 80)
    cat = "counterfactual_gates"

    rules_cat = ctx.run.get_json("/api/rules")
    expected_presets: list[tuple[str, str, str, str]] = []
    for mod in rules_cat["modules"]:
        layer = mod["layer"]
        for r in mod["rules"]:
            rid = r["rule_id"]
            preset = r["counterfactual_preset"]
            case_target = "code_xr_poster" if rid.startswith(("PI-", "GG-")) else ("web_fixture" if rid.startswith("PW-") else "code_xr_uiux")
            expected_presets.append((preset, case_target, layer, rid))

    assert len(expected_presets) == 24, f"Expected 24 presets, got {len(expected_presets)}"

    for preset, cid, exp_layer, exp_rule in expected_presets:
        test_id = f"gate_{preset}"
        try:
            res = ctx.run.post_json(f"/api/case/{cid}/test_rule_gate", {"preset": preset})
            assert res.get("verdict") == "BLOCKED", f"verdict={res.get('verdict')}"
            assert res.get("admission_status") == "BLOCKED", f"admission={res.get('admission_status')}"
            assert res.get("blocked_layer") == exp_layer, f"blocked_layer={res.get('blocked_layer')} != {exp_layer}"
            assert res.get("violated_rule_id") == exp_rule, f"violated_rule_id={res.get('violated_rule_id')} != {exp_rule}"

            # 验证在对应层规则列表里该规则真实状态为 FAIL（非字符串假拼凑）
            layer_rules = res["gates"]["by_layer"][exp_layer]["rules"]
            target_entry = next((x for x in layer_rules if x["rule_id"] == exp_rule), None)
            assert target_entry and target_entry["status"] == "FAIL", f"Rule {exp_rule} status not FAIL in gates"
            assert res.get("attribution"), "Missing attribution"

            ctx.record_pass(
                cat,
                test_id,
                f"[{exp_layer}] {exp_rule} 真实 FAIL 并阻断 ({cid})",
            )
        except Exception as e:
            ctx.record_fail(cat, test_id, str(e))

    # 验证复位
    try:
        reset_res = ctx.run.post_json("/api/case/code_xr_uiux/test_rule_gate", {"preset": "reset"})
        assert reset_res.get("verdict") == "PASS"
        assert reset_res.get("admission_status") == "PROVISIONAL"
        ctx.record_pass(cat, "gate_reset_pass", "反事实沙盒复位后恢复 PASS / PROVISIONAL")
    except Exception as e:
        ctx.record_fail(cat, "gate_reset_pass", str(e))


# ==============================================================================
# 维度 4：REST API 契约与独立源码回检核验
# ==============================================================================
def test_4_api_and_readback(ctx: VerificationContext) -> None:
    print("\n" + "=" * 80)
    print("【维度 4】REST API 契约与独立源码回检核验")
    print("=" * 80)
    cat = "api_and_readback"

    try:
        h = ctx.run.get_json("/api/health")
        assert h["status"] == "OK" and h["version"] == EXPECTED_VERSION
        assert h["rules_loaded"] == 24 and h["templates_loaded"] == 2
        ctx.record_pass(cat, "api_health", f"/api/health 200 OK (v{h['version']}, rules={h['rules_loaded']})")
    except Exception as e:
        ctx.record_fail(cat, "api_health", str(e))

    try:
        cases = ctx.run.get_json("/api/cases")
        cids = [c["case_id"] for c in cases["cases"]]
        assert "code_xr_uiux" in cids and "code_xr_poster" in cids
        ctx.record_pass(cat, "api_cases", f"/api/cases 返回双案例: {cids}")
    except Exception as e:
        ctx.record_fail(cat, "api_cases", str(e))

    try:
        ledger = ctx.run.get_json("/api/error_ledger")
        entries = ledger["entries"]
        res_ids = [e["res_id"] for e in entries]
        assert len(entries) == 8 and res_ids[0] == "RES-KW-01" and res_ids[-1] == "RES-KW-08"
        ctx.record_pass(cat, "api_error_ledger", f"/api/error_ledger 返回完整 8 条台账 ({res_ids[0]}..{res_ids[-1]})")
    except Exception as e:
        ctx.record_fail(cat, "api_error_ledger", str(e))

    for cid, sample_eu in (("code_xr_uiux", "eu_L3_rail_proximity_dock"), ("code_xr_poster", "eu_L3_poster_key_graphic")):
        try:
            exp = ctx.run.get_json(f"/api/case/{cid}/explain/{urllib.parse.quote(sample_eu)}")
            assert exp["eu_id"] == sample_eu
            assert len(exp["ancestors"]) == 3  # L0, L1, L2
            assert len(exp["descendants"]["l5_atoms"]) >= 1
            assert len(exp["edges"]) >= 1
            ctx.record_pass(cat, f"api_explain_{cid}", f"/explain/{sample_eu} 返回完整向上链/L5原子/横向边")
        except Exception as e:
            ctx.record_fail(cat, f"api_explain_{cid}", str(e))

    # 独立源码回检核验
    try:
        b_ui = ctx.run.get_json("/api/case/code_xr_uiux/bundle")
        rb_ui = b_ui["readback"]
        assert rb_ui["status"] == "PASS"
        assert rb_ui["dom_eu_binding_coverage"] == 1.0
        assert rb_ui["reduced_motion_supported"] is True
        assert rb_ui["responsive_390_supported"] is True
        assert rb_ui["defensive_microcopy_violations"] == 0
        assert rb_ui["editable_text_nodes"] >= 10 and rb_ui["interactive_controls"] >= 5

        b_po = ctx.run.get_json("/api/case/code_xr_poster/bundle")
        rb_po = b_po["readback"]
        assert rb_po["status"] == "PASS"
        assert rb_po["dom_eu_binding_coverage"] == 1.0
        assert rb_po["vector_text_editable"] is True
        assert rb_po["defensive_microcopy_violations"] == 0

        ctx.record_pass(
            cat,
            "independent_readback",
            f"双案例源码回检均 PASS：UI/UX DOM覆盖={rb_ui['dom_eu_binding_coverage']*100:.0f}% (texts={rb_ui['editable_text_nodes']}), "
            f"Poster 活文字/矢量={rb_po['vector_text_editable']}, 防御小字=0",
        )
    except Exception as e:
        ctx.record_fail(cat, "independent_readback", str(e))


# ==============================================================================
# 维度 5：真实浏览器 (1440×900) 端到端交互实测 + Swarm 截图
# ==============================================================================
def test_5_playwright_browser_e2e(ctx: VerificationContext, skip_e2e: bool = False) -> None:
    print("\n" + "=" * 80)
    print("【维度 5】真实服务与无头 Chromium (1440×900) 端到端交互核验 + 截图")
    print("=" * 80)
    cat = "browser_e2e"

    if skip_e2e:
        print("  [SKIP] 已跳过 Playwright 端到端测试")
        return

    # 预先复位两个案例假设，保证进入浏览器的初始状态诚实为 PROVISIONAL
    ctx.run.post_json("/api/case/code_xr_uiux/confirm_assumption", {"assumption_id": "ALL", "action": "reset"})
    ctx.run.post_json("/api/case/code_xr_poster/confirm_assumption", {"assumption_id": "ALL", "action": "reset"})

    ctx.screenshot_dir.mkdir(parents=True, exist_ok=True)
    shot1 = ctx.screenshot_dir / "v34_01_workbench_codexr_linkage.png"
    shot2 = ctx.screenshot_dir / "v34_02_codexr_proximity_magnify.png"
    shot3 = ctx.screenshot_dir / "v34_03_counterfactual_blocked.png"
    shot4 = ctx.screenshot_dir / "v34_04_poster_release_ready.png"

    try:
        from playwright.sync_api import expect, sync_playwright

        page_errors: list[str] = []
        console_errors: list[str] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-proxy-server"])
            context = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
            page = context.new_page()
            page.on("pageerror", lambda err: page_errors.append(str(err)))
            page.on(
                "console",
                lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
            )

            # 5.1 加载主页并检查零断链、零防御小字、Y 型门禁显示
            page.goto(f"{ctx.run.base_url}/", wait_until="networkidle", timeout=20000)
            page.wait_for_selector("#tree .tn-row", timeout=10000)
            page.wait_for_selector("#stageFrame", timeout=10000)
            # 等待 iframe 内部渲染就绪
            stage_frame = page.frame_locator("#stageFrame")
            stage_frame.locator("#workspace .main-glass").wait_for(state="visible", timeout=10000)
            time.sleep(0.8)

            body_text = page.locator("body").inner_text()
            for bad_tok in ("undefined", "NaN", "null"):
                assert bad_tok not in body_text, f"Found '{bad_tok}' in workbench body text"
            for phrase in FORBIDDEN_DEFENSIVE_MICROCOPY:
                assert phrase not in body_text, f"Defensive microcopy violation in workbench: {phrase}"

            gate_text = page.locator("#gateChain").inner_text()
            assert "PV" in gate_text and "4/4" in gate_text and "GN" in gate_text and "GU" in gate_text, f"Gate chain text: {gate_text}"
            status_text = page.locator("#statusPill").inner_text()
            assert "PROVISIONAL" in status_text, f"Initial status pill: {status_text}"
            ctx.record_pass(cat, "workbench_boot_zero_errors", f"1440×900 载入正常，门禁={gate_text.replace(chr(10), ' ')}, 状态={status_text}")

            # 5.2 三屏联动：点击中窗格 L3 节点 -> 左窗格骨架高亮 + 解释链刷新 + 右窗格 Code XR 高亮 [data-eu-id]
            target_eu = "eu_L3_sprint_hero"
            page.locator(f'#tree .tn-row[data-eu="{target_eu}"]').click()
            time.sleep(0.6)
            explain_text = page.locator("#explain").inner_text()
            assert "向上" in explain_text and "向下" in explain_text, f"Explain panel missing chains: {explain_text}"
            skel_active = page.locator(f'#skelSvg [data-eu-id="{target_eu}"][data-active="true"], #skelHit .skel-box.sel[data-eu="{target_eu}"]').count()
            assert skel_active >= 1, f"Left skeleton pane did not highlight {target_eu}"
            iframe_active = stage_frame.locator(f'[data-eu-id="{target_eu}"][data-kaiwu-active="true"]').count()
            assert iframe_active >= 1, f"Right Code XR iframe did not highlight {target_eu}"

            page.screenshot(path=str(shot1), full_page=False)
            ctx.screenshots.append({"path": str(shot1), "caption": "开物v3.4三窗格检验台与Code XR全段联动"})
            ctx.record_pass(cat, "three_pane_linkage", f"三屏联动生效：点击 {target_eu} 后左骨架/中解释链/右DOM 同步高亮")

            source_readback = ctx.run.get_json("/api/case/code_xr_uiux/bundle")["readback"]
            assert target_eu in source_readback["stage_trace_ids"], "source readback omitted the observed EU"
            expect(stage_frame.locator(f'[data-eu-id="{target_eu}"]')).to_have_count(1)
            ctx.record_pass(cat, "stage_trace_readback", f"{target_eu} 的源码索引与舞台 DOM 一致")

            # 5.3 Code XR 右窗格内交互：收起左侧栏 + 真实鼠标悬停 Dock 邻近放大 + Analytics 切换
            # 点击中窗格邻近放大拆分节点 eu_L4_feat_proximity_magnify 或直接触发收起侧栏
            page.locator('#timeline .tl-seg[data-i="2"]').click()  # 1.60-2.23s 邻近放大段
            time.sleep(0.3)
            page.locator('#tree .tn-row[data-eu="eu_L4_feat_proximity_magnify"]').click()
            time.sleep(0.6)

            # 进一步在真实浏览器坐标上执行鼠标滑过收起后的侧栏 Dashboard 图标，验证实时计算的 --dock-scale
            dash_loc = stage_frame.locator('a[data-route="dashboard"]')
            analy_loc = stage_frame.locator('a[data-route="analytics"]')
            sett_loc = stage_frame.locator('a[data-route="settings"]')
            dash_box = dash_loc.bounding_box()
            assert dash_box is not None, "Collapsed dashboard dock item missing bounding box"
            page.mouse.move(dash_box["x"] + dash_box["width"] / 2, dash_box["y"] + dash_box["height"] / 2)
            time.sleep(0.35)

            scales = page.evaluate(
                """() => {
                    const fr = document.querySelector('#stageFrame');
                    const doc = fr.contentDocument;
                    const getScale = (sel) => {
                        const el = doc.querySelector(sel);
                        if (!el) return null;
                        const v = el.style.getPropertyValue('--dock-scale');
                        return v ? parseFloat(v) : 1.0;
                    };
                    return {
                        closed: doc.querySelector('#workspace').classList.contains('collapsed'),
                        focus: getScale('a[data-route="dashboard"]'),
                        neighbor: getScale('a[data-route="analytics"]'),
                        far: getScale('a[data-route="settings"]'),
                        labelVisible: !doc.querySelector('.dock-label').hidden,
                    };
                }"""
            )
            assert scales["closed"] is True, "Sidebar was not collapsed"
            assert scales["focus"] > scales["neighbor"] > 1.0, f"Proximity magnification hierarchy invalid: {scales}"
            assert scales["far"] == 1.0, f"Far item should stay 1.0, got {scales}"

            page.screenshot(path=str(shot2), full_page=False)
            ctx.screenshots.append({"path": str(shot2), "caption": "Code XR窄侧栏邻近放大与双向解释链"})

            # 切换 Analytics 并验证 3/6/12 月份切换按钮
            page.locator('#actSeg button[data-act="analytics"]').click()
            time.sleep(0.5)
            stage_frame.locator('.main-glass[data-page="analytics"]').wait_for(state="visible", timeout=5000)
            stage_frame.locator('[data-action="range"][data-index="12"]').click()
            time.sleep(0.3)
            range_active = stage_frame.locator('[data-action="range"][data-index="12"]').get_attribute("aria-pressed")
            assert range_active == "true", f"Analytics 12m range button aria-pressed={range_active}"

            ctx.record_pass(
                cat,
                "codexr_proximity_and_analytics",
                f"邻近放大实测生效 (focus={scales['focus']:.3f} > neighbor={scales['neighbor']:.3f} > 1.0, far={scales['far']:.1f})，Analytics 12月切换正常",
            )

            # 5.4 反事实异常注入当层阻断演练
            page.locator("#presetSelect").select_option("violate_GU03_missing_proximity_magnify")
            expect(page.locator("#statusPill")).to_contain_text("BLOCKED", timeout=15000)
            banner_vis = page.locator("#banner").is_visible()
            banner_txt = page.locator("#banner").inner_text()
            status_blocked = page.locator("#statusPill").inner_text()
            assert banner_vis and "GU-03" in banner_txt and "BLOCKED" in status_blocked, f"Blocked UI mismatch: {status_blocked} / {banner_txt}"

            page.screenshot(path=str(shot3), full_page=False)
            ctx.screenshots.append({"path": str(shot3), "caption": "反事实异常注入当层阻断演练"})

            page.locator("#resetBtn").click()
            expect(page.locator("#statusPill")).to_contain_text("PROVISIONAL", timeout=15000)
            ctx.record_pass(cat, "ui_counterfactual_blocked_reset", "浏览器端触发 GU-03 反事实 BLOCKED 横幅归因并成功复位")

            # 同一案例连续操作时，慢响应不能覆盖最后一次选择。
            slow = "violate_GU03_missing_proximity_magnify"
            recent = "violate_GU04_defensive_microcopy"
            endpoint = "**/api/case/code_xr_uiux/test_rule_gate"
            delayed = []

            def order_response(route):
                if route.request.post_data_json["preset"] == slow:
                    delayed.append(route)
                else:
                    route.continue_()

            page.route(endpoint, order_response)
            with page.expect_request(lambda req: req.url.endswith("/test_rule_gate") and req.post_data_json["preset"] == slow):
                page.evaluate("(preset) => { window.slowVerificationRequest = injectPreset(preset); }", slow)
            page.evaluate("(preset) => injectPreset(preset)", recent)
            expect(page.locator("#banner")).to_contain_text("GU-04")
            assert len(delayed) == 1
            delayed[0].continue_()
            page.evaluate("window.slowVerificationRequest")
            expect(page.locator("#presetSelect")).to_have_value(recent, timeout=1000)
            expect(page.locator("#banner")).to_contain_text("GU-04", timeout=1000)
            page.unroute(endpoint, order_response)
            ctx.record_pass(cat, "same_case_request_order", "乱序返回后保留最新反事实预设")

            write_endpoint = "**/api/case/code_xr_uiux/confirm_assumption"
            delayed_writes = []
            page.route(write_endpoint, lambda route: delayed_writes.append(route))
            with page.expect_request(lambda req: req.url.endswith("/confirm_assumption")):
                page.evaluate('() => { window.pendingSignoff = confirmAssumption("confirm_all", "ALL"); }')
            page.evaluate(
                """() => {
                    window.afterSignoff = clearSandbox();
                    return Promise.race([window.afterSignoff, new Promise(resolve => setTimeout(resolve, 600))]);
                }"""
            )
            assert len(delayed_writes) == 1
            delayed_writes[0].continue_()
            page.evaluate("Promise.all([window.pendingSignoff, window.afterSignoff])")
            expect(page.locator("#statusPill")).to_have_text("RELEASE_READY", timeout=5000)
            page.unroute(write_endpoint)
            page.evaluate('() => confirmAssumption("reset", "ALL")')
            ctx.record_pass(cat, "pending_signoff_reconciled", "复位沙盒读到已完成签认的正式案例")

            bundle_endpoint = "**/api/case/code_xr_poster/bundle"
            page.route(bundle_endpoint, lambda route: route.fulfill(json={"status": "ERROR", "message": "验证用加载失败"}))
            page.locator("#caseSelect").select_option("code_xr_poster")
            expect(page.locator("#caseSelect")).to_have_value("code_xr_uiux", timeout=5000)
            expect(page.locator("#modalChip")).to_contain_text("VIDEO")
            page.unroute(bundle_endpoint)
            ctx.record_pass(cat, "case_failure_keeps_last_bundle", "加载失败时选择器和舞台保留同一案例")

            # 5.5 切换 code_xr_poster 平面设计案例 + 网格预览 + 全假设签认 RELEASE_READY
            page.locator("#caseSelect").select_option("code_xr_poster")
            expect(page.locator("#modalChip")).to_contain_text("IMAGE", timeout=15000)
            poster_gate = page.locator("#gateChain").inner_text()
            assert "PI" in poster_gate and "GN" in poster_gate and "GG" in poster_gate, f"Poster gate chain mismatch: {poster_gate}"
            modal_txt = page.locator("#modalChip").inner_text()
            assert "IMAGE" in modal_txt, f"Poster modal chip mismatch: {modal_txt}"

            # 确认 iframe 平面展板渲染且验证 12 列网格开关（初始开启 -> 关闭 -> 再开启）
            stage_frame.locator(".poster-canvas").wait_for(state="visible", timeout=8000)
            grid_init = page.evaluate("() => document.querySelector('#stageFrame').contentDocument.querySelector('.poster-canvas').classList.contains('show-grid')")
            assert grid_init is True, "Poster 12-column grid should be on initially"
            page.locator('#actSeg button[data-act="toggle_grid"]').click()
            time.sleep(0.25)
            grid_off = page.evaluate("() => document.querySelector('#stageFrame').contentDocument.querySelector('.poster-canvas').classList.contains('show-grid')")
            assert grid_off is False, "Poster 12-column grid did not toggle off"
            page.locator('#actSeg button[data-act="toggle_grid"]').click()
            time.sleep(0.25)
            has_grid = page.evaluate("() => document.querySelector('#stageFrame').contentDocument.querySelector('.poster-canvas').classList.contains('show-grid')")
            assert has_grid is True, "Poster 12-column grid did not toggle back on"

            # 检查平面展板可见文本零防御性小字
            poster_text = stage_frame.locator("body").inner_text()
            for phrase in FORBIDDEN_DEFENSIVE_MICROCOPY:
                assert phrase not in poster_text, f"Defensive microcopy in poster: {phrase}"

            # 切换到假设与台账页签，点击全部签认放行 -> 跃迁为 RELEASE_READY
            page.locator('#midTabs .tab[data-tab="ledger"]').click()
            page.locator("#confirmAllBtn").click()
            expect(page.locator("#statusPill")).to_have_text("RELEASE_READY", timeout=15000)
            status_ready = page.locator("#statusPill").inner_text().strip()
            assert status_ready == "RELEASE_READY", f"Expected RELEASE_READY, got {status_ready}"

            page.screenshot(path=str(shot4), full_page=False)
            ctx.screenshots.append({"path": str(shot4), "caption": "平面设计案例路由与全假设签认放行"})
            ctx.record_pass(cat, "poster_routing_and_release_ready", "平面设计案例 PI→GN→GG 路由、12列网格开关与全部签认跃迁 RELEASE_READY 全通过")

            page.set_viewport_size({"width": 390, "height": 844})
            expect(page.locator("#mobilePaneNav")).to_be_visible()
            page.locator('#mobilePaneNav [data-mpane="mid"]').click()
            expect(page.locator("#paneMid")).to_be_visible()
            page.locator('#mobilePaneNav [data-mpane="right"]').click()
            expect(stage_frame.locator(".poster-canvas")).to_be_visible()
            ctx.record_pass(cat, "narrow_workbench", "390×844 下可切换语义树与舞台")

            browser.close()

        assert len(page_errors) == 0, f"pageerrors detected: {page_errors}"
        assert len(console_errors) == 0, f"console errors detected: {console_errors}"
        ctx.record_pass(cat, "zero_browser_console_errors", "全流程无任何 pageerror 或 console.error")

    except Exception as e:
        ctx.record_fail(cat, "playwright_e2e_run", f"{type(e).__name__}: {e}")
    finally:
        # 验收收尾：恢复两案例假设为初始 open (PROVISIONAL)
        try:
            ctx.run.post_json("/api/case/code_xr_uiux/confirm_assumption", {"assumption_id": "ALL", "action": "reset"})
            ctx.run.post_json("/api/case/code_xr_poster/confirm_assumption", {"assumption_id": "ALL", "action": "reset"})
        except Exception:
            pass


def generate_report(ctx: VerificationContext) -> dict[str, Any]:
    total = sum(len(items) for items in ctx.results.values())
    passed = sum(sum(1 for it in items if it["status"] == "PASS") for items in ctx.results.values())
    failed = total - passed
    rate = round((passed / total * 100.0) if total else 0.0, 2)
    verdict = "PASS" if failed == 0 and total > 0 else "FAIL"

    report = {
        "product": "开物 · Kaiwu Adaptive-EU Design Workbench",
        "version": EXPECTED_VERSION,
        "verification_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "overall_verdict": verdict,
        "summary": {
            "total_checks": total,
            "passed_checks": passed,
            "failed_checks": failed,
            "pass_rate_pct": rate,
        },
        "category_summaries": {
            cat: {
                "total": len(items),
                "passed": sum(1 for it in items if it["status"] == "PASS"),
                "failed": sum(1 for it in items if it["status"] == "FAIL"),
                "verdict": "PASS" if all(it["status"] == "PASS" for it in items) else "FAIL",
            }
            for cat, items in ctx.results.items()
        },
        "metrics": ctx.metrics,
        "screenshots": ctx.screenshots,
        "details": ctx.results,
        "errors": ctx.errors,
    }
    report_path = ctx.run.artifacts_dir / "v34_verification_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 80)
    print(f"【开物 v3.4 验收报告已生成】{report_path}")
    print(f"总检查项: {total} | 通过: {passed} | 失败: {failed} | 通过率: {rate:.2f}% | 结论: {verdict}")
    print("=" * 80)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Kaiwu v3.4 Full-Stack & Browser Verification Suite")
    parser.add_argument("--skip-e2e", action="store_true", help="跳过 Playwright 浏览器端到端实测")
    parser.add_argument("--artifacts-dir", type=pathlib.Path, help="验收输出所在目录")
    parser.add_argument("--screenshot-dir", type=pathlib.Path, help="实测截图保存目录")
    args = parser.parse_args()

    with isolated_workbench(REPO_ROOT, args.artifacts_dir) as run:
        ctx = VerificationContext(run, args.screenshot_dir or (run.artifacts_dir / "screenshots"))
        test_1_rules_and_templates(ctx)
        test_2_adaptive_eu_and_lifecycle(ctx)
        test_3_counterfactual_rule_gates(ctx)
        test_4_api_and_readback(ctx)
        test_5_playwright_browser_e2e(ctx, skip_e2e=args.skip_e2e)
        report = generate_report(ctx)

    if report["overall_verdict"] != "PASS":
        sys.exit(1)



if __name__ == "__main__":
    main()
