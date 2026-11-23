"""
开物 v3.4 · 6 大 AI-First 标准 MCP 工具集与 CLI 入口 (ai_tools_mcp.py)
工具清单：
  1. extract_skeleton          — 提取三模态确定性骨架与 4 色高对比 SVG 叠图
  2. build_adaptive_eu         — 构建原型模板锚定与复杂度自适应伸缩 L0~L5 语义树
  3. audit_three_layer_gates   — 执行 Y 型三层 12 条激活正交规则门禁求值
  4. simulate_counterfactual   — 在内存隔离沙盒中注入反事实异常并验证首障归因
  5. manage_assumptions        — 查询、确认、全量签认或重置显式 AssumptionRecord
  6. verify_and_publish_bundle — 执行独立回检、门禁求值并持久化 inspection_bundle.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import adaptive_eu_engine as engine  # noqa: E402
import category_registry as cat_reg  # noqa: E402
import parsers as parsers_mod  # noqa: E402
import skeleton_extractors as skel_mod  # noqa: E402


def extract_skeleton(case_id: str = "code_xr_uiux", persist: bool = True) -> dict[str, Any]:
    skel = skel_mod.extract_case_skeleton(case_id, persist=persist)
    return {
        "status": "OK",
        "tool": "extract_skeleton",
        "case_id": case_id,
        "modality": skel["modality"],
        "duration_sec": skel.get("duration_sec"),
        "coverage_ratio": skel.get("coverage_ratio"),
        "segment_count": len(skel.get("segments", [])),
        "bbox_count": len(skel.get("bboxes", [])),
    }


def build_adaptive_eu(case_id: str = "code_xr_uiux") -> dict[str, Any]:
    tree = engine.build_eu_tree_for_case(case_id)
    return {
        "status": "OK",
        "tool": "build_adaptive_eu",
        "case_id": case_id,
        "template_id": tree["template_id"],
        "root_id": tree["root_id"],
        "stats": tree["stats"],
    }


def audit_three_layer_gates(case_id: str = "code_xr_uiux") -> dict[str, Any]:
    bundle = engine.build_case_bundle(case_id, persist=False)
    return {
        "status": "OK",
        "tool": "audit_three_layer_gates",
        "case_id": case_id,
        "admission_status": bundle["admission_status"],
        "open_assumptions_count": bundle["open_assumptions_count"],
        "gates": bundle["gates"],
        "readback_summary": bundle["readback"]["summary_pill"],
    }


def simulate_counterfactual(case_id: str = "code_xr_uiux", preset: str = "violate_PV01_partial_video_coverage") -> dict[str, Any]:
    res = engine.run_counterfactual_sandbox(case_id, preset)
    res["tool"] = "simulate_counterfactual"
    return res


def manage_assumptions(case_id: str = "code_xr_uiux", action: str = "list", assumption_id: str = "ALL") -> dict[str, Any]:
    if action == "list":
        bundle = engine.build_case_bundle(case_id)
    else:
        bundle = engine.publish_assumption_change(case_id, assumption_id, action)
    return {
        "status": "OK",
        "tool": "manage_assumptions",
        "case_id": case_id,
        "action": action,
        "assumption_id": assumption_id,
        "admission_status": bundle["admission_status"],
        "open_assumptions_count": bundle["open_assumptions_count"],
        "assumptions": bundle["assumptions"],
        "bundle": bundle,
    }


def verify_and_publish_bundle(case_id: str = "code_xr_uiux") -> dict[str, Any]:
    bundle = engine.build_case_bundle(case_id, persist=True)
    return {
        "status": "OK",
        "tool": "verify_and_publish_bundle",
        "case_id": case_id,
        "version": bundle["version"],
        "admission_status": bundle["admission_status"],
        "open_assumptions_count": bundle["open_assumptions_count"],
        "active_rule_summary": bundle["case_info"]["active_rule_summary"],
        "readback_summary": bundle["readback"]["summary_pill"],
        "bundle_path": str((engine.CASES_DIR / case_id / "inspection_bundle.json").resolve())
        if case_id != "web_fixture"
        else None,
    }


def list_categories() -> dict[str, Any]:
    cats = cat_reg.list_categories()
    return {"status": "OK", "tool": "list_categories", "count": len(cats), "categories": cats}


def import_web_case(
    url: str, case_id: str | None = None, category: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    bundle: dict[str, Any] = {}

    def finalize(parsed: dict[str, Any]) -> None:
        bundle.update(engine.build_case_bundle(parsed["case_id"], persist=True))

    parsed = parsers_mod.parse_web_url(url=url, case_id=case_id, category_override=category, finalize=finalize)
    return parsed, bundle


def parse_url_live(url: str, case_id: str | None = None, category: str | None = None) -> dict[str, Any]:
    parsed, bundle = import_web_case(url, case_id, category)
    cid = parsed["case_id"]
    return {
        "status": "OK",
        "tool": "parse_url_live",
        "case_id": cid,
        "source_url": url,
        "classification": parsed["classification"],
        "category_info": parsed["category_info"],
        "admission_status": bundle["admission_status"],
        "active_rule_summary": bundle["case_info"]["active_rule_summary"],
        "category_audit": bundle["category_audit"],
        "bundle_path": str((engine.CASES_DIR / cid / "inspection_bundle.json").resolve()),
    }


def inspect_image_som(
    image: str,
    case_id: str | None = None,
    category: str | None = None,
    out_dir: str | None = None,
) -> dict[str, Any]:
    return parsers_mod.parse_local_image(
        image_path=image,
        case_id=case_id,
        category_override=category,
        output_dir=out_dir,
    )


def inspect_video_diff(
    source: str,
    case_id: str | None = None,
    max_samples: int = 12,
    out_dir: str | None = None,
) -> dict[str, Any]:
    return parsers_mod.parse_local_video(
        source_path=source,
        case_id=case_id,
        max_samples=max_samples,
        output_dir=out_dir,
    )


def get_mcp_tools_schema() -> list[dict[str, Any]]:
    return [
        {"name": "extract_skeleton", "description": "提取 video/image/web 模态确定性骨架与 4 色叠图 SVG", "required": ["case_id"]},
        {"name": "build_adaptive_eu", "description": "构建原型模板锚定与分裂/折叠自适应 L0~L5 语义树", "required": ["case_id"]},
        {"name": "audit_three_layer_gates", "description": "求值解析层(4)+总规则(4)+生成层(4)共 12 条正交门禁", "required": ["case_id"]},
        {"name": "simulate_counterfactual", "description": "在内存隔离沙盒注入反事实异常预设并返回首障归因", "required": ["case_id", "preset"]},
        {"name": "manage_assumptions", "description": "查询、单条确认、全部签认或重置显式假设记录", "required": ["case_id", "action"]},
        {"name": "verify_and_publish_bundle", "description": "独立回检产物源码并生成持久化 inspection_bundle.json", "required": ["case_id"]},
        {"name": "list_categories", "description": "列出全部可扩展产品分类插件（核心族与扩展族）及各自规则", "required": []},
        {"name": "parse_url_live", "description": "使用无头 Chromium 在 1440/768/390 三断点真机测绘 URL、自动分类并发布结构壳案例", "required": ["url"]},
        {"name": "inspect_image_som", "description": "对本地静图执行纯 CV 色板提取、区域分割与 Set-of-Mark 标号图生成（零外部 API）", "required": ["image"]},
        {"name": "inspect_video_diff", "description": "对本地录屏视频或帧目录执行稳态切片、跨帧热点差分与交互边候选推理（零 ffmpeg/API）", "required": ["source"]},
    ]


TOOL_DISPATCH = {
    "extract_skeleton": lambda a: extract_skeleton(a.get("case_id", "code_xr_uiux"), bool(a.get("persist", True))),
    "build_adaptive_eu": lambda a: build_adaptive_eu(a.get("case_id", "code_xr_uiux")),
    "audit_three_layer_gates": lambda a: audit_three_layer_gates(a.get("case_id", "code_xr_uiux")),
    "simulate_counterfactual": lambda a: simulate_counterfactual(a.get("case_id", "code_xr_uiux"), a.get("preset", "violate_PV01_partial_video_coverage")),
    "manage_assumptions": lambda a: manage_assumptions(a.get("case_id", "code_xr_uiux"), a.get("action", "list"), a.get("assumption_id", "ALL")),
    "verify_and_publish_bundle": lambda a: verify_and_publish_bundle(a.get("case_id", "code_xr_uiux")),
    "list_categories": lambda _a: list_categories(),
    "parse_url_live": lambda a: parse_url_live(a["url"], a.get("case_id"), a.get("category")),
    "inspect_image_som": lambda a: inspect_image_som(a["image"], a.get("case_id"), a.get("category"), a.get("out_dir")),
    "inspect_video_diff": lambda a: inspect_video_diff(a["source"], a.get("case_id"), int(a.get("max_samples", 12)), a.get("out_dir")),
}


def invoke_tool(tool_name: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
    if tool_name not in TOOL_DISPATCH:
        raise ValueError(f"Unsupported MCP tool: {tool_name}")
    return TOOL_DISPATCH[tool_name](args or {})


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="开物 v4.0 AI-First MCP 工具 CLI")
    parser.add_argument("tool", nargs="?", default="list", help="工具名称或 list")
    parser.add_argument("--case", default=None, help="案例 ID")
    parser.add_argument("--preset", default="violate_PV01_partial_video_coverage", help="反事实异常预设名")
    parser.add_argument("--action", default="list", help="假设动作 (list | confirm | confirm_all | reset)")
    parser.add_argument("--assumption-id", default="ALL", help="假设记录 ID")
    parser.add_argument("--url", default=None, help="待解析网页 URL")
    parser.add_argument("--image", default=None, help="待测绘静图路径")
    parser.add_argument("--source", default=None, help="待分析录屏视频或帧目录路径")
    parser.add_argument("--category", default="auto", help="产品分类覆盖 ID（默认 auto 自动分类）")
    parser.add_argument("--out-dir", default=None, help="输出目录")
    ns = parser.parse_args()

    if ns.tool in ("list", "--list-tools"):
        out = {"status": "OK", "tools": get_mcp_tools_schema()}
    elif ns.tool == "publish_all":
        cids = [cid for cid in engine.CASE_META.keys() if cid != "web_fixture"]
        out = {
            "status": "OK",
            "results": [verify_and_publish_bundle(cid) for cid in cids],
        }
    else:
        res = invoke_tool(
            ns.tool,
            {
                "case_id": ns.case or ("code_xr_uiux" if ns.tool not in ("parse_url_live", "inspect_image_som", "inspect_video_diff") else None),
                "preset": ns.preset,
                "action": ns.action,
                "assumption_id": ns.assumption_id,
                "url": ns.url,
                "image": ns.image,
                "source": ns.source,
                "category": ns.category,
                "out_dir": ns.out_dir,
            },
        )
        out = {k: v for k, v in res.items() if k != "bundle"}
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
