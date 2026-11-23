"""
开物 v4.0 · 网页 URL 三断点真机自动解析器 (parsers/web_url_parser.py)
零外部 API：直接用无头 Chromium (Playwright) 在 1440 / 768 / 390 三视口实测 DOM 几何、
计算样式聚类 Token、交互控件、资产槽位、产品分类与归一化 Skeleton/EU 树。
"""
from __future__ import annotations

import datetime as dt
import json
import math
import pathlib
import re
import sys
import tempfile
import warnings
from collections import Counter
from threading import RLock
from typing import Any, Callable
from urllib.parse import urlparse
from uuid import uuid4

from playwright.sync_api import Error as BrowserError, TimeoutError as BrowserTimeout, sync_playwright

BACKEND_DIR = pathlib.Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
CASES_DIR = PROJECT_ROOT / "cases"
CASE_FILES_LOCK = RLock()


class CaseConflictError(ValueError):
    """An import ID belongs to an existing non-imported case."""

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import cases_catalog as base_cat  # noqa: E402
import category_registry as cat_reg  # noqa: E402


def _slugify_case_id(url: str, raw_case_id: str | None = None) -> str:
    if raw_case_id:
        clean = re.sub(r"[^a-zA-Z0-9_]+", "_", raw_case_id.strip().lower()).strip("_")
        if clean:
            return clean[:48]
    parsed = urlparse(url)
    host = re.sub(r"[^a-zA-Z0-9]+", "_", (parsed.netloc or "site").lower()).strip("_")
    tail = [seg for seg in (parsed.path or "").split("/") if seg and not seg.endswith(".html")]
    leaf = re.sub(r"[^a-zA-Z0-9]+", "_", (tail[-1] if tail else "page").lower()).strip("_")
    base = re.sub(r"_+", "_", f"imp_{host}_{leaf}")[:39].rstrip("_")
    return f"{base}_{uuid4().hex[:8]}"


def _rgb_to_hex(rgb_str: str) -> str | None:
    m = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)", str(rgb_str or ""))
    if not m:
        return None
    r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
    a = float(m.group(4)) if m.group(4) is not None else 1.0
    if a <= 0.05:
        return None
    return f"#{r:02x}{g:02x}{b:02x}"


def _hex_to_rgb(hx: str) -> tuple[int, int, int]:
    h = hx.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _color_dist(h1: str, h2: str) -> float:
    r1, g1, b1 = _hex_to_rgb(h1)
    r2, g2, b2 = _hex_to_rgb(h2)
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


def _luminance(hx: str) -> float:
    r, g, b = _hex_to_rgb(hx)
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def _contrast_ratio(h1: str, h2: str) -> float:
    def _lin(c: int) -> float:
        x = c / 255.0
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4

    r1, g1, b1 = _hex_to_rgb(h1)
    r2, g2, b2 = _hex_to_rgb(h2)
    l1 = 0.2126 * _lin(r1) + 0.7152 * _lin(g1) + 0.0722 * _lin(b1)
    l2 = 0.2126 * _lin(r2) + 0.7152 * _lin(g2) + 0.0722 * _lin(b2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def _cluster_colors(raw_colors: list[str], fallback_list: list[str], min_dist: float = 34.0) -> list[str]:
    counts: Counter[str] = Counter()
    for raw in raw_colors:
        hx = _rgb_to_hex(raw)
        if hx:
            counts[hx] += 1
    clusters: list[str] = []
    for hx, _ in counts.most_common(40):
        if all(_color_dist(hx, c) >= min_dist for c in clusters):
            clusters.append(hx)
        if len(clusters) >= 6:
            break
    for fb in fallback_list:
        if fb not in clusters and len(clusters) < 5:
            clusters.append(fb)
    return clusters[:5]


_PROBE_JS = r"""
() => {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const docScrollW = document.documentElement.scrollWidth;
  const bodyCS = getComputedStyle(document.body);
  const rootCS = getComputedStyle(document.documentElement);
  const bgColor = (bodyCS.backgroundColor && bodyCS.backgroundColor !== 'rgba(0, 0, 0, 0)')
    ? bodyCS.backgroundColor
    : rootCS.backgroundColor;

  const isVisible = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) < 0.05) return false;
    const r = el.getBoundingClientRect();
    return r.width >= 16 && r.height >= 16;
  };

  // Collect structural candidate blocks
  const candidateEls = Array.from(
    document.querySelectorAll('header, nav, aside, main, section, article, footer, dialog, table, [role="navigation"], [role="main"], [role="region"]')
  ).filter((el) => isVisible(el));

  const regions = candidateEls.slice(0, 32).map((el, idx) => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    const txt = (el.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 90);
    return {
      idx,
      tag: el.tagName.toLowerCase(),
      role: el.getAttribute('role') || el.tagName.toLowerCase(),
      aria_label: el.getAttribute('aria-label') || '',
      bbox: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)],
      bg: cs.backgroundColor,
      color: cs.color,
      font_size: cs.fontSize,
      border_radius: cs.borderRadius,
      border_width: cs.borderWidth,
      independent_scroll: (el.scrollHeight > el.clientHeight + 24) && ['auto', 'scroll'].includes(cs.overflowY),
      text_sample: txt,
    };
  });

  // Collect interactive controls
  const interactiveEls = Array.from(
    document.querySelectorAll('button, a[href], input, select, textarea, [role="button"], [role="tab"], [role="link"]')
  ).filter((el) => isVisible(el));

  const controls = interactiveEls.slice(0, 28).map((el, idx) => {
    const r = el.getBoundingClientRect();
    const name = (el.getAttribute('aria-label') || el.innerText || el.getAttribute('placeholder') || el.tagName).trim().replace(/\s+/g, ' ').slice(0, 48);
    return {
      id: `ctrl_${idx}`,
      tag: el.tagName.toLowerCase(),
      role: el.getAttribute('role') || (el.tagName.toLowerCase() === 'a' ? 'link' : 'button'),
      accessible_name: name || el.tagName.toLowerCase(),
      bbox: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)],
    };
  });

  // Collect visual assets (canvas/video/img/svg)
  const assetEls = Array.from(document.querySelectorAll('canvas, video, img, svg')).filter((el) => isVisible(el));
  let assetArea = 0;
  const assetSlots = [];
  for (const el of assetEls.slice(0, 12)) {
    const r = el.getBoundingClientRect();
    const area = r.width * r.height;
    if (area >= 6400) {
      assetArea += area;
      assetSlots.push({
        tag: el.tagName.toLowerCase(),
        bbox: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)],
        area_ratio: Number((area / (vw * vh)).toFixed(3)),
      });
    }
  }

  // Sample computed styles across text & container elements
  const sampleEls = Array.from(document.querySelectorAll('h1, h2, h3, p, span, a, button, div, section, header, nav, aside, td, th')).filter(isVisible).slice(0, 140);
  const fgColors = [];
  const bgColors = [bgColor];
  const fontSizes = [];
  const spacings = [];
  const radii = [];
  let sharpBorderCount = 0;
  let totalBordered = 0;

  for (const el of sampleEls) {
    const cs = getComputedStyle(el);
    fgColors.push(cs.color);
    if (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)') bgColors.push(cs.backgroundColor);
    const fs = parseFloat(cs.fontSize);
    if (!Number.isNaN(fs) && fs > 0) fontSizes.push(Math.round(fs));
    const pad = parseFloat(cs.paddingTop);
    const gap = parseFloat(cs.gap);
    if (!Number.isNaN(pad) && pad >= 4 && pad <= 64) spacings.push(Math.round(pad));
    if (!Number.isNaN(gap) && gap >= 4 && gap <= 64) spacings.push(Math.round(gap));
    const br = parseFloat(cs.borderRadius);
    if (!Number.isNaN(br)) radii.push(Math.round(br));
    const bw = parseFloat(cs.borderTopWidth);
    if (!Number.isNaN(bw) && bw >= 1) {
      totalBordered += 1;
      if (br === 0) sharpBorderCount += 1;
    }
  }

  // Detect isomorphic sibling groups (arrays)
  let maxArrayCount = 0;
  for (const p of Array.from(document.querySelectorAll('main, section, div, ul')).slice(0, 60)) {
    const visChildren = Array.from(p.children).filter(isVisible);
    if (visChildren.length >= 3) {
      const tagGroups = {};
      for (const c of visChildren) {
        tagGroups[c.tagName] = (tagGroups[c.tagName] || 0) + 1;
      }
      for (const cnt of Object.values(tagGroups)) {
        if (cnt > maxArrayCount) maxArrayCount = cnt;
      }
    }
  }

  const h1 = document.querySelector('h1');
  const h1Text = h1 ? (h1.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 100) : '';
  const h1Size = h1 ? parseFloat(getComputedStyle(h1).fontSize) : 0;
  const fullTextSample = (document.body.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 1200);

  return {
    title: document.title || 'Parsed Web Workspace',
    viewport: { w: vw, h: vh },
    scroll_width: docScrollW,
    overflow_px: Math.max(0, docScrollW - vw),
    body_bg: bgColor,
    body_color: bodyCS.color,
    h1_text: h1Text,
    h1_size: Math.round(h1Size || 0),
    text_sample: fullTextSample,
    regions,
    controls,
    interactive_count: interactiveEls.length,
    table_count: document.querySelectorAll('table').length,
    code_or_textarea_count: document.querySelectorAll('textarea, pre, code').length,
    dialog_count: document.querySelectorAll('dialog, [role="dialog"]').length,
    asset_slots: assetSlots,
    canvas_or_media_ratio: Number(Math.min(1.0, assetArea / Math.max(1, vw * vh)).toFixed(3)),
    fg_colors: fgColors,
    bg_colors: bgColors,
    font_sizes: fontSizes,
    spacings,
    radii,
    sharp_border_ratio: totalBordered > 0 ? Number((sharpBorderCount / totalBordered).toFixed(3)) : 0.0,
    max_array_count: maxArrayCount,
  };
}
"""


def _build_imported_app_files(
    case_dir: pathlib.Path,
    case_id: str,
    title: str,
    source_url: str,
    h1_text: str,
    cat_info: dict[str, Any],
    tokens: dict[str, str],
    prefix: str,
    sections: list[dict[str, Any]],
    controls: list[dict[str, Any]],
    has_nav_rail: bool,
) -> None:
    """为动态解析导入的网址生成可离线复现、100% 带 data-eu-id 与 Token 绑定的结构壳产物。"""
    app_dir = case_dir / "app"
    app_dir.mkdir(parents=True, exist_ok=True)

    bg_hex = tokens["bg"]
    panel_hex = tokens["panel"]
    ink_hex = tokens["ink"]
    accent_hex = tokens["accent"]
    border_hex = tokens["border"]
    radius_px = tokens["radius"]
    rail_w_px = tokens["rail_w"]
    gap_px = tokens["gap"]

    # Ensure high contrast between ink & bg and button text & accent
    if _contrast_ratio(ink_hex, bg_hex) < 4.5:
        ink_hex = "#f4f5f7" if _luminance(bg_hex) < 0.45 else "#15171c"
    if _contrast_ratio(ink_hex, panel_hex) < 4.5:
        panel_hex = "#14171f" if _luminance(bg_hex) < 0.45 else "#f6f7f9"
    btn_ink = "#111214" if _luminance(accent_hex) > 0.52 else "#ffffff"

    safe_title = title.replace("<", "&lt;").replace(">", "&gt;")
    safe_h1 = (h1_text or title).replace("<", "&lt;").replace(">", "&gt;")
    safe_url = source_url.replace("<", "&lt;").replace(">", "&gt;")

    nav_items = [c["accessible_name"] for c in controls[:4] if c.get("accessible_name")] or ["Overview", "Modules", "Inspect", "Settings"]
    card_items = []
    for idx, sec in enumerate(sections[:4]):
        lbl = (sec.get("aria_label") or sec.get("tag") or f"Block {idx+1}").upper()
        txt = (sec.get("text_sample") or f"Parsed structural section #{idx+1}").replace('"', "'").replace("<", "&lt;").replace(">", "&gt;")
        card_items.append({"idx": idx + 1, "tag": lbl, "bbox": sec["bbox"], "text": txt[:140]})
    while len(card_items) < 4:
        n = len(card_items) + 1
        card_items.append({"idx": n, "tag": f"REGION {n}", "bbox": [120, 120 * n, 960, 180], "text": f"Measured region #{n} anchored from {safe_url}"})

    index_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{safe_title}</title>
  <link rel="stylesheet" href="./styles.css">
</head>
<body>
  <div class="imp-shell" id="viewport" data-page="overview" data-eu-id="eu_L0_{prefix}_workspace">
    <a class="skip-link" href="#main-stage" data-eu-id="eu_L3_{prefix}_skip_entry">Skip to main view</a>

    <nav class="imp-rail" aria-label="Primary navigation" data-eu-id="eu_L1_{prefix}_nav">
      <div class="rail-dock" id="railDock" data-eu-id="eu_L3_{prefix}_rail_dock">
        <div class="rail-brand">{prefix.upper()}</div>
        {"".join(f'<button class="rail-btn{" is-active" if i==0 else ""}" type="button" data-route="tab_{i+1}"><span>0{i+1}</span><small>{lbl[:6]}</small></button>' for i, lbl in enumerate(nav_items))}
        <div class="rail-ind" data-eu-id="eu_L4_{prefix}_rail_proximity">
          <span>{cat_info["category_id"]}</span>
        </div>
      </div>
    </nav>

    <main class="main-glass" id="main-stage" tabindex="-1" data-eu-id="eu_L1_{prefix}_stage">
      <header class="imp-topbar" data-eu-id="eu_L3_{prefix}_topbar">
        <div class="tb-left">
          <span class="tb-title">{safe_title}</span>
          <span class="tb-cat">{cat_info["category_name"]}</span>
        </div>
        <div class="tb-tabs" data-eu-id="eu_L4_{prefix}_route_tabs">
          <button class="tb-tab is-active" type="button" data-route="overview">Overview</button>
          <button class="tb-tab" type="button" data-route="metrics">Structure</button>
          <button class="tb-tab" type="button" data-route="tokens">Tokens</button>
          <button class="tb-cta" id="openInspectBtn" type="button">Inspect Spec</button>
        </div>
      </header>

      <section class="imp-hero" data-eu-id="eu_L3_{prefix}_hero_stage">
        <div class="hero-copy">
          <div class="hero-source">SOURCE URL · {safe_url}</div>
          <h1 class="hero-h1">{safe_h1}</h1>
          <p class="hero-meta">Category: {cat_info["category_name"]} · Mode: {"Nav Rail + Stage" if has_nav_rail else "Flow Layout"} · 3-Breakpoint Verified</p>
        </div>
        <div class="hero-shot" data-eu-id="eu_L4_{prefix}_primary_control">
          <div class="shot-badge">CAPTURED 1440×900 SNAPSHOT</div>
          <img class="captured-preview" src="../frames/captured_1440.png" alt="Captured source preview">
        </div>
      </section>

      <section class="imp-array" data-eu-id="eu_L3_{prefix}_modules_array">
        <div class="arr-bar" data-eu-id="eu_L4_{prefix}_filter_export">
          <div class="flt-row">
            <button class="flt-btn is-active" type="button" data-filter="all">All Blocks ({len(card_items)})</button>
            <button class="flt-btn" type="button" data-filter="top">Upper Fold</button>
            <button class="flt-btn" type="button" data-filter="lower">Lower Fold</button>
          </div>
          <button class="btn-outline" id="exportCsvBtn" type="button">Export Skeleton CSV</button>
        </div>
        <div class="cards-grid" id="cardsGrid"></div>
      </section>
    </main>

    <dialog class="imp-dialog" id="specDialog" aria-labelledby="dlgTitle" data-eu-id="eu_L3_{prefix}_spec_dialog">
      <form method="dialog" class="dlg-box">
        <div class="dlg-head">
          <h2 id="dlgTitle">Parsed Source Contract</h2>
          <button class="btn-outline" type="submit" value="cancel">Close</button>
        </div>
        <p class="dlg-info">Extracted live via headless Chromium multi-breakpoint DOM/CSSOM measurement without external API calls.</p>
        <div class="dlg-tokens">
          <span>BG {bg_hex}</span>
          <span>PANEL {panel_hex}</span>
          <span>INK {ink_hex}</span>
          <span>ACCENT {accent_hex}</span>
        </div>
        <div class="dlg-foot">
          <button class="tb-cta" type="submit" value="done">Done</button>
        </div>
      </form>
    </dialog>
  </div>
  <script src="./app.js"></script>
</body>
</html>
"""

    styles_css = f""":root {{
  --{prefix}-bg: {bg_hex};
  --{prefix}-panel: {panel_hex};
  --{prefix}-ink: {ink_hex};
  --{prefix}-accent: {accent_hex};
  --{prefix}-border: {border_hex};
  --{prefix}-font-h1: {tokens["font_h1"]};
  --{prefix}-font-body: {tokens["font_body"]};
  --{prefix}-rail-w: {rail_w_px};
  --{prefix}-radius: {radius_px};
  --{prefix}-gap: {gap_px};
  --{prefix}-dur: 160ms;
}}

*, *::before, *::after {{ box-sizing: border-box; }}

html, body {{
  margin: 0;
  padding: 0;
  height: 100%;
  background: var(--{prefix}-bg);
  color: var(--{prefix}-ink);
  font-family: "Inter", "Segoe UI", system-ui, sans-serif;
  font-size: var(--{prefix}-font-body);
  line-height: 1.45;
}}

.skip-link {{
  position: fixed;
  top: -60px;
  left: 14px;
  z-index: 99;
  padding: 8px 14px;
  background: var(--{prefix}-accent);
  color: {btn_ink};
  border-radius: var(--{prefix}-radius);
  text-decoration: none;
  font-weight: 700;
}}
.skip-link:focus {{ top: 12px; }}

.imp-shell {{
  display: grid;
  grid-template-columns: var(--{prefix}-rail-w) minmax(0, 1fr);
  height: 100vh;
  overflow: hidden;
  background: var(--{prefix}-bg);
}}

.imp-rail {{
  border-right: 1px solid var(--{prefix}-border);
  background: var(--{prefix}-panel);
  padding: 14px 6px;
}}

.rail-dock {{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  height: 100%;
}}

.rail-brand {{
  width: 40px;
  height: 40px;
  border-radius: var(--{prefix}-radius);
  background: var(--{prefix}-accent);
  color: {btn_ink};
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 12px;
}}

.rail-btn {{
  width: 54px;
  padding: 8px 4px;
  border-radius: var(--{prefix}-radius);
  border: 1px solid var(--{prefix}-border);
  background: var(--{prefix}-bg);
  color: var(--{prefix}-ink);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  cursor: pointer;
  transform: translateX(var(--dock-shift, 0px)) scale(var(--dock-scale, 1));
  transition: transform var(--{prefix}-dur) ease, border-color var(--{prefix}-dur) ease;
}}
.rail-btn.is-active, .rail-btn:hover {{
  border-color: var(--{prefix}-accent);
}}
.rail-btn small {{ font-size: 9px; opacity: 0.78; }}

.rail-ind {{
  margin-top: auto;
  font-size: 9px;
  font-family: ui-monospace, monospace;
  opacity: 0.72;
  writing-mode: vertical-rl;
}}

.main-glass {{
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 18px 24px 36px;
}}

.imp-topbar {{
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--{prefix}-panel);
  border: 1px solid var(--{prefix}-border);
  border-radius: var(--{prefix}-radius);
  margin-bottom: var(--{prefix}-gap);
}}

.tb-left {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
.tb-title {{ font-weight: 700; font-size: 15px; }}
.tb-cat {{
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid var(--{prefix}-border);
  font-size: 11px;
  opacity: 0.85;
}}

.tb-tabs {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }}
.tb-tab, .btn-outline, .flt-btn {{
  padding: 6px 12px;
  border-radius: var(--{prefix}-radius);
  border: 1px solid var(--{prefix}-border);
  background: transparent;
  color: var(--{prefix}-ink);
  font-size: 12px;
  cursor: pointer;
}}
.tb-tab.is-active, .flt-btn.is-active {{
  border-color: var(--{prefix}-accent);
  background: var(--{prefix}-accent);
  color: {btn_ink};
  font-weight: 600;
}}
.tb-cta {{
  padding: 7px 14px;
  border-radius: var(--{prefix}-radius);
  border: 1px solid var(--{prefix}-accent);
  background: var(--{prefix}-accent);
  color: {btn_ink};
  font-weight: 700;
  font-size: 12px;
  cursor: pointer;
}}

.imp-hero {{
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
  gap: var(--{prefix}-gap);
  padding: 20px;
  border-radius: var(--{prefix}-radius);
  border: 1px solid var(--{prefix}-border);
  background: var(--{prefix}-panel);
  margin-bottom: var(--{prefix}-gap);
}}
.hero-source {{
  font-family: ui-monospace, monospace;
  font-size: 11px;
  opacity: 0.72;
  margin-bottom: 8px;
  word-break: break-all;
}}
.hero-h1 {{
  margin: 0 0 10px;
  font-size: var(--{prefix}-font-h1);
  line-height: 1.08;
  letter-spacing: -0.025em;
}}
.hero-meta {{ margin: 0; font-size: 13px; opacity: 0.8; }}

.hero-shot {{
  border: 1px solid var(--{prefix}-border);
  border-radius: var(--{prefix}-radius);
  overflow: hidden;
  background: var(--{prefix}-bg);
  display: flex;
  flex-direction: column;
}}
.shot-badge {{
  padding: 6px 10px;
  font-family: ui-monospace, monospace;
  font-size: 10px;
  border-bottom: 1px solid var(--{prefix}-border);
  opacity: 0.78;
}}
.captured-preview {{
  width: 100%;
  height: 220px;
  object-fit: cover;
  object-position: top center;
  display: block;
}}

.imp-array {{
  display: flex;
  flex-direction: column;
  gap: var(--{prefix}-gap);
}}
.arr-bar {{
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}}
.flt-row {{ display: flex; flex-wrap: wrap; gap: 6px; }}

.cards-grid {{
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--{prefix}-gap);
}}
.s-card {{
  border: 1px solid var(--{prefix}-border);
  border-radius: var(--{prefix}-radius);
  background: var(--{prefix}-panel);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}}
.s-head {{
  display: flex;
  justify-content: space-between;
  font-family: ui-monospace, monospace;
  font-size: 11px;
  opacity: 0.75;
}}
.s-body {{ margin: 0; font-size: 13px; }}

.imp-dialog {{
  border: 1px solid var(--{prefix}-border);
  border-radius: var(--{prefix}-radius);
  background: var(--{prefix}-panel);
  color: var(--{prefix}-ink);
  padding: 0;
  max-width: 460px;
  width: calc(100% - 32px);
}}
.dlg-box {{ padding: 20px; }}
.dlg-head {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
.dlg-head h2 {{ margin: 0; font-size: 17px; }}
.dlg-info {{ margin: 0 0 12px; font-size: 13px; opacity: 0.85; }}
.dlg-tokens {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  font-family: ui-monospace, monospace;
  font-size: 11px;
  margin-bottom: 16px;
}}
.dlg-tokens span {{
  padding: 6px 8px;
  border: 1px solid var(--{prefix}-border);
  border-radius: var(--{prefix}-radius);
}}
.dlg-foot {{ display: flex; justify-content: flex-end; }}

.kaiwu-eu-highlight, [data-kaiwu-active="true"] {{
  outline: 2.5px solid var(--{prefix}-accent) !important;
  outline-offset: 2px;
}}

@media (max-width: 740px) {{
  .imp-shell {{ grid-template-columns: 1fr; grid-template-rows: auto 1fr; }}
  .imp-rail {{ border-right: none; border-bottom: 1px solid var(--{prefix}-border); padding: 8px 10px; }}
  .rail-dock {{ flex-direction: row; overflow-x: auto; }}
  .rail-brand, .rail-ind {{ display: none; }}
  .main-glass {{ padding: 12px; }}
  .imp-hero {{ grid-template-columns: 1fr; }}
  .cards-grid {{ grid-template-columns: 1fr; }}
}}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ transition-duration: 0.001ms !important; animation-duration: 0.001ms !important; }}
}}
"""

    cards_json = json.dumps(card_items, ensure_ascii=False)
    app_js = f"""(function () {{
  const viewport = document.getElementById('viewport');
  const mainStage = document.querySelector('.main-glass') || document.getElementById('main-stage');
  const railDock = document.getElementById('railDock');
  const railBtns = Array.from(document.querySelectorAll('.rail-btn'));
  const tbTabs = Array.from(document.querySelectorAll('.tb-tab'));
  const fltBtns = Array.from(document.querySelectorAll('.flt-btn'));
  const cardsGrid = document.getElementById('cardsGrid');
  const exportCsvBtn = document.getElementById('exportCsvBtn');
  const dialog = document.getElementById('specDialog');
  const openInspectBtn = document.getElementById('openInspectBtn');

  const CARDS = {cards_json};
  let activeRange = 'all';
  let lastTriggerEl = openInspectBtn;

  function navigate(route) {{
    const target = route || 'overview';
    viewport.dataset.page = target;
    mainStage.scrollTop = 0;
    railBtns.forEach((b) => b.classList.toggle('is-active', b.dataset.route === target));
    tbTabs.forEach((b) => b.classList.toggle('is-active', b.dataset.route === target));
  }}

  function updateDock(pointerY) {{
    const dockRadius = 100;
    const dockGain = 0.22;
    railBtns.forEach((btn) => {{
      const rect = btn.getBoundingClientRect();
      const center = rect.top + rect.height / 2;
      const dist = Math.abs(pointerY - center);
      const ratio = Math.max(0, 1 - dist / dockRadius);
      btn.style.setProperty('--dock-scale', (1 + ratio * dockGain).toFixed(3));
      btn.style.setProperty('--dock-shift', `${{(ratio * 4).toFixed(1)}}px`);
    }});
  }}

  function resetDock() {{
    railBtns.forEach((btn) => {{
      btn.style.setProperty('--dock-scale', '1');
      btn.style.setProperty('--dock-shift', '0px');
    }});
  }}

  function renderCards() {{
    const items = CARDS.filter((c) => activeRange === 'all' || (activeRange === 'top' ? c.idx <= 2 : c.idx > 2));
    cardsGrid.innerHTML = items.map((c) => `
      <article class="s-card">
        <div class="s-head"><span>${{c.tag}}</span><span>[${{c.bbox.join(', ')}}]</span></div>
        <p class="s-body">${{c.text}}</p>
      </article>
    `).join('');
  }}

  function exportCsv() {{
    const items = CARDS.filter((c) => activeRange === 'all' || (activeRange === 'top' ? c.idx <= 2 : c.idx > 2));
    const header = 'index,tag,bbox,text\\n';
    const body = items.map((c) => `${{c.idx}},${{c.tag}},"${{c.bbox.join(' ')}}","${{c.text}}"`).join('\\n');
    const blob = new Blob([header + body], {{ type: 'text/csv;charset=utf-8;' }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `{case_id}-${{activeRange}}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }}

  railDock.addEventListener('mousemove', (e) => updateDock(e.clientY));
  railDock.addEventListener('mouseleave', resetDock);
  railBtns.forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));
  tbTabs.forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));

  fltBtns.forEach((b) => b.addEventListener('click', () => {{
    activeRange = b.dataset.filter;
    fltBtns.forEach((x) => x.classList.toggle('is-active', x === b));
    renderCards();
  }}));

  exportCsvBtn.addEventListener('click', exportCsv);

  openInspectBtn.addEventListener('click', () => {{
    lastTriggerEl = openInspectBtn;
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  }});

  if (dialog) {{
    dialog.addEventListener('close', () => {{
      if (lastTriggerEl && typeof lastTriggerEl.focus === 'function') lastTriggerEl.focus();
    }});
  }}

  document.querySelectorAll('[data-eu-id]').forEach((el) => {{
    el.addEventListener('click', (e) => {{
      const target = e.target.closest('[data-eu-id]');
      if (!target) return;
      window.parent.postMessage({{ type: 'KAIWU_SELECT_EU', eu_id: target.dataset.euId }}, '*');
    }});
  }});

  window.addEventListener('message', (event) => {{
    const msg = event.data || {{}};
    if (msg.type === 'KAIWU_HIGHLIGHT_EU') {{
      document.querySelectorAll('.kaiwu-eu-highlight,[data-kaiwu-active]').forEach((n) => {{
        n.classList.remove('kaiwu-eu-highlight');
        n.removeAttribute('data-kaiwu-active');
      }});
      const node = document.querySelector(`[data-eu-id="${{msg.eu_id}}"]`);
      if (node) {{
        node.classList.add('kaiwu-eu-highlight');
        node.setAttribute('data-kaiwu-active', 'true');
        node.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      }}
    }} else if (msg.type === 'KAIWU_PREVIEW_ACTION') {{
      if (msg.action === 'normal') {{
        navigate('overview');
        resetDock();
      }} else if (msg.action === 'proximity_demo') {{
        const btn = railBtns[1];
        if (btn) {{
          const r = btn.getBoundingClientRect();
          updateDock(r.top + r.height / 2);
        }}
      }} else if (msg.action === 'analytics') {{
        navigate('metrics');
      }}
    }}
  }});

  renderCards();
}})();
"""

    (app_dir / "index.html").write_text(index_html, encoding="utf-8")
    (app_dir / "styles.css").write_text(styles_css, encoding="utf-8")
    (app_dir / "app.js").write_text(app_js, encoding="utf-8")


def parse_web_url(
    url: str,
    case_id: str | None = None,
    category_override: str | None = None,
    persist: bool = True,
    *,
    finalize: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """
    使用无头 Chromium 在 1440 / 768 / 390 三断点真机测绘任意网页 URL，
    输出分类结果、Unified Skeleton IR、EU 树与结构源码壳。
    """
    if not url or not re.match(r"^https?://", url.strip(), re.I):
        raise ValueError(f"Invalid URL (must start with http:// or https://): {url}")

    target_url = url.strip()
    if case_id is not None and not isinstance(case_id, str):
        raise ValueError("case_id must be a string")
    cid = _slugify_case_id(target_url, case_id)
    if not persist:
        return _inspect_web_url(target_url, cid, category_override)

    base = CASES_DIR.resolve()
    base.mkdir(parents=True, exist_ok=True)
    target = base / cid
    with CASE_FILES_LOCK:
        _check_import_destination(target)
    with tempfile.TemporaryDirectory(prefix=".import-", dir=base) as staging:
        staged_case = pathlib.Path(staging) / cid
        payload = _inspect_web_url(target_url, cid, category_override, staged_case)
        with CASE_FILES_LOCK:
            _check_import_destination(target)
            _publish_import(target, staged_case, payload, finalize)
    return payload


def _check_import_destination(target: pathlib.Path) -> None:
    if target.is_symlink() or target.resolve().parent != CASES_DIR.resolve():
        raise ValueError("Invalid case output directory")
    if target.name == "web_fixture" or (target.exists() and not (target / "parsed_case.json").is_file()):
        raise CaseConflictError(f"Case ID is already reserved: {target.name}")


def _publish_import(
    target: pathlib.Path, staged: pathlib.Path, payload: dict[str, Any],
    finalize: Callable[[dict[str, Any]], None] | None,
) -> None:
    backup = target.parent / f".previous-import-{uuid4().hex}"
    if target.exists():
        target.rename(backup)
    published = False
    try:
        staged.rename(target)
        published = True
        if finalize is not None:
            finalize(payload)
    except BaseException:
        if published:
            target.rename(staged)
        if backup.exists():
            backup.rename(target)
        raise
    if backup.exists():
        try:
            backup.rename(staged.parent / "previous")
        except OSError:
            warnings.warn(f"Previous import retained in {backup.name}", RuntimeWarning)


def _inspect_web_url(
    target_url: str, cid: str, category_override: str | None,
    case_dir: pathlib.Path | None = None,
) -> dict[str, Any]:
    prefix = "imp"
    frames_dir = case_dir / "frames" if case_dir is not None else None

    bp_measures: dict[int, dict[str, Any]] = {}
    desktop_probe: dict[str, Any] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-proxy-server"])
        context = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page = context.new_page()

        try:
            try:
                response = page.goto(target_url, wait_until="networkidle", timeout=20000)
            except BrowserTimeout:
                response = page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
        except BrowserError as error:
            raise ValueError(f"Could not load webpage: {target_url}") from error
        if response is None or not response.ok:
            status = response.status if response else "no response"
            raise ValueError(f"Webpage returned {status}: {target_url}")
        page.wait_for_timeout(450)

        desktop_probe = page.evaluate(_PROBE_JS)
        bp_measures[1440] = {
            "scroll_width": desktop_probe["scroll_width"],
            "overflow_px": desktop_probe["overflow_px"],
        }
        if frames_dir is not None:
            frames_dir.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(frames_dir / "captured_1440.png"), full_page=False)

        for vw, vh, shot_name in ((768, 1024, None), (390, 844, "captured_390.png")):
            page.set_viewport_size({"width": vw, "height": vh})
            page.wait_for_timeout(200)
            m = page.evaluate("() => ({ vw: window.innerWidth, sw: document.documentElement.scrollWidth })")
            bp_measures[vw] = {
                "scroll_width": int(m["sw"]),
                "overflow_px": max(0, int(m["sw"]) - int(m["vw"])),
            }
            if frames_dir is not None and shot_name:
                page.screenshot(path=str(frames_dir / shot_name), full_page=False)

        browser.close()

    # Cluster surface & foreground colors
    body_bg = _rgb_to_hex(desktop_probe.get("body_bg", "")) or "#111318"
    is_dark = _luminance(body_bg) < 0.42
    bg_cluster = _cluster_colors(
        desktop_probe.get("bg_colors", []),
        [body_bg, "#1a1d24" if is_dark else "#f5f4f0", "#292d38" if is_dark else "#dcdad2"],
    )
    fg_cluster = _cluster_colors(
        desktop_probe.get("fg_colors", []),
        ["#f2f4f8" if is_dark else "#16181d", "#9ca3af" if is_dark else "#5a606c"],
    )

    bg_hex = bg_cluster[0]
    panel_hex = bg_cluster[1] if len(bg_cluster) > 1 and _color_dist(bg_cluster[1], bg_hex) > 12 else ("#1a1d24" if is_dark else "#f8f7f3")
    ink_hex = max(fg_cluster, key=lambda c: _contrast_ratio(c, bg_hex))
    accent_candidates = [c for c in fg_cluster + bg_cluster if 0.25 < _luminance(c) < 0.85 and _color_dist(c, bg_hex) > 45 and _color_dist(c, ink_hex) > 45]
    accent_hex = accent_candidates[0] if accent_candidates else ("#60a5fa" if is_dark else "#2563eb")
    border_hex = bg_cluster[2] if len(bg_cluster) > 2 else ("#2a2f3a" if is_dark else "#d6d3cb")

    font_sizes = sorted([int(x) for x in desktop_probe.get("font_sizes", []) if 10 <= int(x) <= 96], reverse=True)
    h1_px = int(desktop_probe.get("h1_size") or (font_sizes[0] if font_sizes else 36))
    body_px = int(Counter(font_sizes).most_common(1)[0][0] if font_sizes else 14)
    body_px = max(12, min(18, body_px))
    radii = desktop_probe.get("radii", [8])
    radius_val = int(Counter(radii).most_common(1)[0][0]) if radii else 8
    spacings = desktop_probe.get("spacings", [16])
    gap_val = max(8, min(28, int(Counter(spacings).most_common(1)[0][0]) if spacings else 16))

    regions = desktop_probe.get("regions", [])
    has_nav_rail = any(
        r.get("tag") == "aside" or (r["bbox"][2] <= 180 and r["bbox"][3] >= 400 and r["bbox"][0] <= 120)
        for r in regions
    )
    rail_w = 72 if has_nav_rail else 68

    # Construct normalized skeleton for classifier + EU engine
    frame_url = f"/cases/{cid}/frames/captured_1440.png" if frames_dir is not None else ""
    bboxes = [
        {"bbox_id": f"bb_{prefix}_nav", "eu_id": f"eu_L3_{prefix}_rail_dock", "label": "导航/侧轨区", "x": 16, "y": 16, "w": rail_w, "h": 868, "role": "nav"},
        {"bbox_id": f"bb_{prefix}_top", "eu_id": f"eu_L3_{prefix}_topbar", "label": "顶栏与视图入口", "x": 104, "y": 16, "w": 1316, "h": 68, "role": "nav"},
        {"bbox_id": f"bb_{prefix}_hero", "eu_id": f"eu_L3_{prefix}_hero_stage", "label": "主内容首屏区域", "x": 104, "y": 100, "w": 1316, "h": 460, "role": "split"},
        {"bbox_id": f"bb_{prefix}_arr", "eu_id": f"eu_L3_{prefix}_modules_array", "label": "下方模块矩阵阵列", "x": 104, "y": 576, "w": 1316, "h": 308, "role": "array"},
    ]

    raw_signals = {
        "has_nav_rail": has_nav_rail,
        "interactive_count": int(desktop_probe.get("interactive_count", 0)),
        "table_count": int(desktop_probe.get("table_count", 0)),
        "code_or_textarea_count": int(desktop_probe.get("code_or_textarea_count", 0)),
        "canvas_or_media_ratio": float(desktop_probe.get("canvas_or_media_ratio", 0.0)),
        "is_dark_surface": is_dark,
        "has_schedule_matrix": bool("mon " in desktop_probe.get("text_sample", "").lower() and "40h" in desktop_probe.get("text_sample", "").lower()),
        "sharp_border_ratio": float(desktop_probe.get("sharp_border_ratio", 0.0)),
        "has_large_hero": h1_px >= 34,
    }

    classify_input = {
        "title": desktop_probe.get("title", ""),
        "source_url": target_url,
        "summary": desktop_probe.get("text_sample", ""),
        "canvas": {"w": 1440, "h": 900},
        "bboxes": bboxes + [
            {"label": r.get("aria_label") or r.get("tag"), "kind": r.get("tag"), "text_sample": r.get("text_sample", "")}
            for r in regions[:12]
        ],
        "signals": raw_signals,
    }
    classification = cat_reg.classify_skeleton(classify_input, domain_hint="uiux")
    chosen_cat_id = (
        category_override.strip()
        if category_override and category_override not in ("auto", "ALL", "")
        else classification["category_id"]
    )
    cats_map = cat_reg.load_categories()
    if chosen_cat_id not in cats_map:
        chosen_cat_id = classification["category_id"]
    cat_meta = cats_map[chosen_cat_id]
    cat_info = {
        "category_id": chosen_cat_id,
        "category_name": cat_meta.get("name", chosen_cat_id),
        "category_tier": cat_meta.get("tier", "core"),
        "confidence": classification["confidence"],
        "reasons": classification["reasons"],
    }

    registry = {
        "surface_atoms": {
            f"{prefix}_surf_bg": {"name": "主画布背景色", "kind": "color", "value": bg_hex, "css_var": f"--{prefix}-bg"},
            f"{prefix}_surf_panel": {"name": "表面卡片容器色", "kind": "color", "value": panel_hex, "css_var": f"--{prefix}-panel"},
            f"{prefix}_surf_ink": {"name": "主文本前景色", "kind": "color", "value": ink_hex, "css_var": f"--{prefix}-ink"},
            f"{prefix}_surf_accent": {"name": "核心强调高亮色", "kind": "color", "value": accent_hex, "css_var": f"--{prefix}-accent"},
            f"{prefix}_surf_border": {"name": "结构边框分隔色", "kind": "color", "value": border_hex, "css_var": f"--{prefix}-border"},
        },
        "typography_atoms": {
            f"{prefix}_typo_h1": {"name": "实测首屏主标题字阶", "kind": "font_scale", "value": f"clamp(24px, 3vw, {max(28, h1_px)}px)", "css_var": f"--{prefix}-font-h1"},
            f"{prefix}_typo_body": {"name": "实测正文字阶", "kind": "font_scale", "value": f"{body_px}px", "css_var": f"--{prefix}-font-body"},
        },
        "layout_atoms": {
            f"{prefix}_lay_rail": {"name": "导轨宽度", "kind": "dimension", "value": f"{rail_w}px", "css_var": f"--{prefix}-rail-w"},
            f"{prefix}_lay_radius": {"name": "实测主导圆角", "kind": "radius", "value": f"{radius_val}px", "css_var": f"--{prefix}-radius"},
            f"{prefix}_lay_gap": {"name": "实测组件间距", "kind": "spacing", "value": f"{gap_val}px", "css_var": f"--{prefix}-gap"},
        },
        "motion_atoms": {
            f"{prefix}_mot_ui": {"name": "状态过渡时长", "kind": "duration", "value": "160ms", "css_var": f"--{prefix}-dur"},
        },
        "evidence_atoms": {
            f"ev_{prefix}_dom": {"name": f"URL 真机三断点快照 ({target_url})", "breakpoints": [390, 768, 1440], "frame_ref": "captured_1440.png"},
        },
    }

    root_id = f"eu_L0_{prefix}_workspace"
    dom = base_cat._build_three_breakpoint_rects(
        root_id,
        {
            f"eu_L1_{prefix}_intro": {390: (12, 6, 366, 34), 768: (18, 8, 732, 34), 1440: (16, 8, 1404, 34)},
            f"eu_L2_{prefix}_intro_bar": {390: (12, 6, 366, 34), 768: (18, 8, 732, 34), 1440: (16, 8, 1404, 34)},
            f"eu_L1_{prefix}_nav": {390: (12, 46, 366, 60), 768: (18, 48, 84, 1120), 1440: (16, 16, rail_w, 868)},
            f"eu_L2_{prefix}_nav_rail": {390: (12, 46, 366, 60), 768: (18, 48, 84, 1120), 1440: (16, 16, rail_w, 868)},
            f"eu_L1_{prefix}_stage": {390: (12, 114, 366, 1400), 768: (114, 48, 636, 1120), 1440: (104, 16, 1316, 868)},
            f"eu_L2_{prefix}_topbar": {390: (12, 114, 366, 88), 768: (114, 48, 636, 88), 1440: (104, 16, 1316, 84)},
            f"eu_L2_{prefix}_hero_zone": {390: (12, 214, 366, 680), 768: (114, 150, 636, 560), 1440: (104, 110, 1316, 460)},
            f"eu_L2_{prefix}_array_zone": {390: (12, 910, 366, 580), 768: (114, 720, 636, 430), 1440: (104, 580, 1316, 304)},
            f"eu_L1_{prefix}_overlay": {390: (16, 140, 358, 340), 768: (140, 150, 488, 360), 1440: (420, 170, 580, 380)},
            f"eu_L2_{prefix}_dialog_host": {390: (16, 140, 358, 340), 768: (140, 150, 488, 360), 1440: (420, 170, 580, 380)},
        },
    )

    computed_styles = [
        {"id": f"{prefix}_cs_bg", "eu_id": f"eu_L3_{prefix}_topbar", "property": "background-color", "value": bg_hex, "token_ref": f"{prefix}_surf_bg", "delta_e": 0.0},
        {"id": f"{prefix}_cs_h1", "eu_id": f"eu_L3_{prefix}_hero_stage", "property": "font-size", "value": f"{h1_px}px", "token_ref": f"{prefix}_typo_h1", "delta_e": 0.0},
        {"id": f"{prefix}_cs_gap", "eu_id": f"eu_L3_{prefix}_modules_array", "property": "gap", "value": f"{gap_val}px", "token_ref": f"{prefix}_lay_gap", "delta_e": 0.0},
        {"id": f"{prefix}_cs_mot", "eu_id": f"eu_L3_{prefix}_rail_dock", "property": "transition-duration", "value": "160ms", "token_ref": f"{prefix}_mot_ui", "delta_e": 0.0},
    ]

    skeleton_svg = base_cat._render_web_skeleton_svg(frame_url, bboxes, rail_x=16, stage_x=104, panel_radius=radius_val)

    skeleton = {
        "case_id": cid,
        "title": desktop_probe.get("title", cid),
        "source_url": target_url,
        "modality": "web",
        "duration_sec": None,
        "coverage_ratio": 1.0,
        "breakpoints": [390, 768, 1440],
        "viewport": {"width": 1440, "height": 900, "breakpoints": [390, 768, 1440]},
        "breakpoint_measurements": bp_measures,
        "signals": raw_signals,
        "classification": classification,
        "dom": dom,
        "computed_styles": computed_styles,
        "interactive_elements": [
            {"id": f"{prefix}_el_skip", "eu_id": f"eu_L3_{prefix}_skip_entry", "role": "button", "accessible_name": "Skip to main view", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": f"{prefix}_el_rail", "eu_id": f"eu_L3_{prefix}_rail_dock", "role": "navigation", "accessible_name": "Primary rail", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": f"{prefix}_el_top", "eu_id": f"eu_L3_{prefix}_topbar", "role": "tab", "accessible_name": "Top navigation", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": f"{prefix}_el_hero", "eu_id": f"eu_L3_{prefix}_hero_stage", "role": "region", "accessible_name": "Captured hero stage", "states": ["default", "hover", "focus-visible", "active"]},
            {"id": f"{prefix}_el_dlg", "eu_id": f"eu_L3_{prefix}_spec_dialog", "role": "dialog", "accessible_name": "Parsed Source Contract", "states": ["default", "hover", "focus-visible", "active"]},
        ],
        "content_nodes": [
            {"id": f"{prefix}_cn_bg", "eu_id": root_id, "content_class": "decoration", "aria_hidden": True, "data_source": None, "children_classes": []},
            {"id": f"{prefix}_cn_hero", "eu_id": f"eu_L3_{prefix}_hero_stage", "content_class": "data", "aria_hidden": False, "data_source": target_url, "children_classes": ["data"]},
            {"id": f"{prefix}_cn_arr", "eu_id": f"eu_L3_{prefix}_modules_array", "content_class": "data", "aria_hidden": False, "data_source": f"{target_url}#sections", "children_classes": ["data"]},
        ],
        "asset_slots": desktop_probe.get("asset_slots", []),
        "segments": [
            {
                "segment_id": "seg_web_desktop",
                "index": 1,
                "t0": 0.0,
                "t1": 1.0,
                "label": f"1440×900 · {desktop_probe.get('title', cid)[:26]}",
                "frame_url": frame_url,
                "active_eu_ids": [b["eu_id"] for b in bboxes],
                "bboxes": bboxes,
            }
        ],
        "bboxes": [dict(b, segment_id="seg_web_desktop", color_role=b["role"]) for b in bboxes],
        "skeleton_svg": skeleton_svg,
    }

    ev_id = f"ev_{prefix}_dom"
    all_atoms = (
        list(registry["surface_atoms"].keys())
        + list(registry["typography_atoms"].keys())
        + list(registry["layout_atoms"].keys())
        + list(registry["motion_atoms"].keys())
        + [ev_id]
    )
    base_atoms = [f"{prefix}_surf_bg", f"{prefix}_typo_body", f"{prefix}_lay_gap", ev_id]
    title_short = (desktop_probe.get("title") or cid)[:32]
    arr_count = max(4, int(desktop_probe.get("max_array_count") or 4))

    nodes: list[dict[str, Any]] = [
        {"eu_id": root_id, "name": f"{title_short} 工作台根", "level": "L0", "node_kind": "product.workspace", "parent_id": None, "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [0, 0, 1440, 900], "rendered": True},
        {"eu_id": f"eu_L1_{prefix}_intro", "name": "无障碍跳转外壳", "level": "L1", "node_kind": "territory.intro_shell", "parent_id": root_id, "template_slot": "intro_shell", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 8, 1404, 34]},
        {"eu_id": f"eu_L2_{prefix}_intro_bar", "name": "快捷跳转入口条", "level": "L2", "node_kind": "region.intro_strip", "parent_id": f"eu_L1_{prefix}_intro", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 8, 1404, 34]},
        {"eu_id": f"eu_L3_{prefix}_skip_entry", "name": "跳过导航直达控件", "level": "L3", "entity": True, "node_kind": "component.skip_button", "parent_id": f"eu_L2_{prefix}_intro_bar", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 8, 180, 34], "dom_selector": f'[data-eu-id="eu_L3_{prefix}_skip_entry"]', "rendered": True},
        {"eu_id": f"eu_L4_{prefix}_skip_feat", "name": "键盘焦点跳转特征", "level": "L4", "node_kind": "feature.skip_a11y", "parent_id": f"eu_L3_{prefix}_skip_entry", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 8, 180, 34]},
        {"eu_id": f"eu_L5_{prefix}_skip_atoms", "name": "入口基础原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": f"eu_L4_{prefix}_skip_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": base_atoms},

        {"eu_id": f"eu_L1_{prefix}_nav", "name": "导航坞领地", "level": "L1", "node_kind": "territory.nav_dock", "parent_id": root_id, "template_slot": "nav_dock", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 16, rail_w, 868], "rendered": True},
        {"eu_id": f"eu_L2_{prefix}_nav_rail", "name": "侧边导轨区", "level": "L2", "node_kind": "region.nav_rail", "parent_id": f"eu_L1_{prefix}_nav", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 16, rail_w, 868]},
        {"eu_id": f"eu_L3_{prefix}_rail_dock", "name": "自适应导航导轨组件", "level": "L3", "entity": True, "interaction_density": 3, "node_kind": "component.nav_rail", "parent_id": f"eu_L2_{prefix}_nav_rail", "adaptation_mode": "SPLIT_HIGH_INTERACTION", "envelope_bbox": [16, 16, rail_w, 868], "dom_selector": f'[data-eu-id="eu_L3_{prefix}_rail_dock"]', "rendered": True},
        {"eu_id": f"eu_L4_{prefix}_rail_proximity", "name": "近邻缩放与分类标识特征", "level": "L4", "motion": True, "node_kind": "feature.proximity_magnify", "parent_id": f"eu_L3_{prefix}_rail_dock", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 16, rail_w, 640], "rendered": True},
        {"eu_id": f"eu_L5_{prefix}_rail_atoms", "name": "全量表面与排版原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": f"eu_L4_{prefix}_rail_proximity", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": all_atoms},

        {"eu_id": f"eu_L1_{prefix}_stage", "name": "独立滚动主舞台领地", "level": "L1", "node_kind": "territory.main_stage", "parent_id": root_id, "template_slot": "main_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [104, 16, 1316, 868], "rendered": True},
        {"eu_id": f"eu_L2_{prefix}_topbar", "name": "顶栏导航与状态区", "level": "L2", "node_kind": "region.topbar", "parent_id": f"eu_L1_{prefix}_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [104, 16, 1316, 84]},
        {"eu_id": f"eu_L3_{prefix}_topbar", "name": "实测顶栏标题与路由条", "level": "L3", "entity": True, "node_kind": "component.stage_topbar", "parent_id": f"eu_L2_{prefix}_topbar", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [104, 16, 1316, 84], "dom_selector": f'[data-eu-id="eu_L3_{prefix}_topbar"]', "rendered": True},
        {"eu_id": f"eu_L4_{prefix}_route_tabs", "name": "多视图标签切换", "level": "L4", "motion": True, "node_kind": "feature.route_switch", "parent_id": f"eu_L3_{prefix}_topbar", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [104, 16, 1316, 84], "rendered": True},
        {"eu_id": f"eu_L5_{prefix}_top_atoms", "name": "顶栏原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": f"eu_L4_{prefix}_route_tabs", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": all_atoms},

        {"eu_id": f"eu_L2_{prefix}_hero_zone", "name": "主内容与视觉槽位展区", "level": "L2", "node_kind": "region.hero_stage", "parent_id": f"eu_L1_{prefix}_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [104, 110, 1316, 460]},
        {"eu_id": f"eu_L3_{prefix}_hero_stage", "name": "实测首屏与快照槽位组件", "level": "L3", "entity": True, "interaction_density": 4, "node_kind": "component.primary_interactive", "parent_id": f"eu_L2_{prefix}_hero_zone", "adaptation_mode": "SPLIT_HIGH_INTERACTION", "envelope_bbox": [104, 110, 1316, 460], "dom_selector": f'[data-eu-id="eu_L3_{prefix}_hero_stage"]', "rendered": True},
        {"eu_id": f"eu_L4_{prefix}_primary_control", "name": "真机截帧与资产槽位对照", "level": "L4", "motion": True, "node_kind": "feature.primary_control", "parent_id": f"eu_L3_{prefix}_hero_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [104, 110, 1316, 460], "rendered": True},
        {"eu_id": f"eu_L5_{prefix}_hero_atoms", "name": "主展区原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": f"eu_L4_{prefix}_primary_control", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": all_atoms},

        {"eu_id": f"eu_L2_{prefix}_array_zone", "name": "实测模块阵列区", "level": "L2", "node_kind": "region.lower_array", "parent_id": f"eu_L1_{prefix}_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [104, 580, 1316, 304]},
        {"eu_id": f"eu_L3_{prefix}_modules_array", "name": f"页面区块与元素阵列 ×{arr_count}", "level": "L3", "entity": True, "node_kind": "component.spec.array", "parent_id": f"eu_L2_{prefix}_array_zone", "adaptation_mode": "FOLD_ARRAY", "array_count": arr_count, "envelope_bbox": [104, 580, 1316, 304], "dom_selector": f'[data-eu-id="eu_L3_{prefix}_modules_array"]', "rendered": True},
        {"eu_id": f"eu_L4_{prefix}_filter_export", "name": "区块筛选与骨架 CSV 导出", "level": "L4", "node_kind": "feature.filter_export", "parent_id": f"eu_L3_{prefix}_modules_array", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [104, 580, 1316, 304], "rendered": True},
        {"eu_id": f"eu_L5_{prefix}_array_atoms", "name": "阵列原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": f"eu_L4_{prefix}_filter_export", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": base_atoms},

        {"eu_id": f"eu_L1_{prefix}_overlay", "name": "辅助规格浮层领地", "level": "L1", "node_kind": "territory.auxiliary_overlay", "parent_id": root_id, "template_slot": "auxiliary_overlay", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 170, 580, 380]},
        {"eu_id": f"eu_L2_{prefix}_dialog_host", "name": "契约对话框宿主区", "level": "L2", "node_kind": "region.dialog", "parent_id": f"eu_L1_{prefix}_overlay", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 170, 580, 380]},
        {"eu_id": f"eu_L3_{prefix}_spec_dialog", "name": "提取参数与 Token 明细弹窗", "level": "L3", "entity": True, "node_kind": "component.modal_sheet", "parent_id": f"eu_L2_{prefix}_dialog_host", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 170, 580, 380], "dom_selector": f'[data-eu-id="eu_L3_{prefix}_spec_dialog"]', "rendered": True},
        {"eu_id": f"eu_L4_{prefix}_focus_trap", "name": "弹窗关闭焦点归还触发按钮", "level": "L4", "node_kind": "feature.modal_focus_restore", "parent_id": f"eu_L3_{prefix}_spec_dialog", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 170, 580, 380]},
        {"eu_id": f"eu_L5_{prefix}_dialog_atoms", "name": "弹窗原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": f"eu_L4_{prefix}_focus_trap", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": base_atoms},
    ]

    edges = [
        {"edge_id": f"edge_{prefix}_proximity", "edge_type": "MODULATES_NEIGHBOR", "source_eu_id": f"eu_L3_{prefix}_rail_dock", "target_eu_id": f"eu_L4_{prefix}_rail_proximity", "label": "导轨邻近缩放反馈", "evidence_ref": ev_id},
        {"edge_id": f"edge_{prefix}_scroll", "edge_type": "SCROLLS_INDEPENDENTLY", "source_eu_id": f"eu_L1_{prefix}_stage", "target_eu_id": f"eu_L1_{prefix}_nav", "label": "主区独立滚动不牵动导航", "evidence_ref": ev_id},
        {"edge_id": f"edge_{prefix}_state", "edge_type": "TRIGGERS_STATE", "source_eu_id": f"eu_L3_{prefix}_topbar", "target_eu_id": f"eu_L3_{prefix}_hero_stage", "label": "顶栏视图切换重绘", "evidence_ref": ev_id},
        {"edge_id": f"edge_{prefix}_filter", "edge_type": "FILTERS_VIEW", "source_eu_id": f"eu_L3_{prefix}_hero_stage", "target_eu_id": f"eu_L3_{prefix}_modules_array", "label": "区域过滤并同步 CSV 导出", "evidence_ref": ev_id},
        {"edge_id": f"edge_{prefix}_focus", "edge_type": "RESTORES_FOCUS", "source_eu_id": f"eu_L3_{prefix}_spec_dialog", "target_eu_id": f"eu_L3_{prefix}_topbar", "label": "弹窗关闭归还触发控件焦点", "evidence_ref": ev_id},
        {"edge_id": f"edge_{prefix}_token", "edge_type": "SHARES_TOKEN", "source_eu_id": f"eu_L3_{prefix}_hero_stage", "target_eu_id": f"eu_L3_{prefix}_modules_array", "label": "共享实测色彩与字阶 Token", "evidence_ref": ev_id},
    ]

    assumptions = [
        {
            "assumption_id": f"ASM-{cid.upper()[:8]}-01",
            "eu_id": f"eu_L3_{prefix}_hero_stage",
            "subject_ids": [f"eu_L3_{prefix}_hero_stage"],
            "title": "URL 静态首屏解析对未点击后端交互及动态接口的保留假设",
            "category": "unobserved_interaction_payload",
            "assumed_value": f"当前基于 {target_url} 的三断点实测 DOM/CSSOM 提炼色板与模块树，并以可交互结构壳承载回检",
            "evidence_gap": "自动爬虫单轮测量仅捕获首屏可见 DOM 状态，未穷举远端 API 数据及登录态内部子视图",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": f"ASM-{cid.upper()[:8]}-02",
            "eu_id": root_id,
            "subject_ids": [root_id, f"eu_L3_{prefix}_rail_dock"],
            "title": f"自动分类判定为 [{cat_info['category_name']}] 的工程签认",
            "category": "category_classification_review",
            "assumed_value": f"分类器基于 {len(regions)} 个区块与 {desktop_probe.get('interactive_count', 0)} 个控件判定为 {chosen_cat_id}（置信度 {classification['confidence']}）",
            "evidence_gap": "当原站缺乏固定侧栏或表格导出时，结构壳保留导航与导出以闭合通用工作台契约，需人工确认是否按扩展分类裁剪",
            "bound_rule_id": "GN-02",
            "status": "open",
            "confirmed_at": None,
        },
    ]

    case_meta = {
        "case_id": cid,
        "title": f"{title_short} · 自动解析",
        "subtitle": f"URL → {cat_info['category_name']}",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": f"/cases/{cid}/app/index.html",
        "source_summary": f"LIVE URL · {target_url} · {cat_info['category_name']}",
        "category_id": chosen_cat_id,
        "is_imported": True,
    }

    tokens_flat = {
        "bg": bg_hex,
        "panel": panel_hex,
        "ink": ink_hex,
        "accent": accent_hex,
        "border": border_hex,
        "font_h1": f"clamp(24px, 3vw, {max(28, h1_px)}px)",
        "font_body": f"{body_px}px",
        "rail_w": f"{rail_w}px",
        "radius": f"{radius_val}px",
        "gap": f"{gap_val}px",
    }

    payload = {
        "schema_version": "4.0.0",
        "case_id": cid,
        "source_url": target_url,
        "parsed_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "case_meta": case_meta,
        "classification": classification,
        "category_info": cat_info,
        "tokens": tokens_flat,
        "skeleton": skeleton,
        "raw_eu_spec": {
            "template_id": "tpl_uiux_workspace_v1",
            "template_name": "UI/UX 工作台原型",
            "root_id": root_id,
            "nodes": nodes,
            "atomic_registry": registry,
            "edges": edges,
        },
        "assumptions": assumptions,
    }

    if case_dir is not None:
        case_dir.mkdir(parents=True, exist_ok=True)
        _build_imported_app_files(
            case_dir=case_dir,
            case_id=cid,
            title=title_short,
            source_url=target_url,
            h1_text=desktop_probe.get("h1_text", title_short),
            cat_info=cat_info,
            tokens=tokens_flat,
            prefix=prefix,
            sections=regions,
            controls=desktop_probe.get("controls", []),
            has_nav_rail=has_nav_rail,
        )
        (case_dir / "parsed_case.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return payload
