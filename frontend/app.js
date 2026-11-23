/* 开物 v3.4 · 宣纸·瑞士极简检验台（Stage-First 非对称架构 · 原生 ES6 零依赖） */
"use strict";

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const LAYER_SHORT = { parsing: "解析", general: "总规则", generation: "生成" };
const LAYER_FULL = { parsing: "解析层", general: "总规则层", generation: "生成层" };
const MODE_CLASS = { SPLIT_HIGH_INTERACTION: "split", FOLD_ARRAY: "fold", ATOMIC_MOUNT: "atom" };
const SEG_COLORS = ["var(--kw-l1)", "var(--kw-l2)", "var(--kw-l5)", "var(--kw-l3)", "var(--kw-l4)", "var(--kw-info)"];
const EU_COLORS = {
  L0: "var(--kw-l0)",
  L1: "var(--kw-l1)",
  L2: "var(--kw-l2)",
  L3: "var(--kw-l3)",
  L4: "var(--kw-l4)",
  L5: "var(--kw-l5)",
};

const S = {
  cases: [],
  categories: [],
  caseId: null,
  caseSeq: 0,
  bundle: null,
  nodes: new Map(),
  atoms: new Map(),
  rootId: null,
  gates: null,
  admission: null,
  readback: null,
  sandbox: null,
  reviewSeq: 0,
  selected: null,
  explainSeq: 0,
  open: new Set(),
  depth: 5,
  query: "",
  segIdx: 0,
  layers: { skeleton: true, bbox: true, timeline: true },
  vp: "desktop",
  action: "normal",
  toggles: { grid: true, bleed: true },
  scope: "active",
  rulesLib: null,
  ledgerFallback: null,
  frameLoaded: false,
  pendingHighlight: null,
  proxTimer: 0,
  stageFocused: false,
  compareMode: false,
  selfEuSpec: null,
  xrayWire: false,
};

/* ---------------- 网络 ---------------- */
async function api(path, opts) {
  const res = await fetch(path, opts);
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { throw new Error(`${path} 返回非 JSON`); }
  if (!res.ok || (data && data.status && data.status !== "OK")) {
    throw new Error((data && (data.message || data.error)) || `${path} ${res.status}`);
  }
  return data;
}
const post = (path, body) => api(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

let toastTimer = 0;
function toast(msg, err = false) {
  const el = $("#toast");
  el.textContent = msg;
  el.className = "toast" + (err ? " err" : "");
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (el.hidden = true), err ? 4200 : 2200);
}

/* ---------------- 工具 ---------------- */
const fmtT = (t) => {
  const n = Number(t);
  if (!Number.isFinite(n)) return "0.00";
  let s = n.toFixed(3).replace(/0+$/, "");
  if (/\.\d$/.test(s)) s += "0";
  if (s.endsWith(".")) s += "00";
  return s;
};
const pct = (r) => `${Math.round(Number(r) * 1000) / 10}%`.replace(/\.0%$/, "%");
const cleanSegLabel = (s) => String((s && s.label) || "").replace(/^\s*[\d.]+\s*[-–~—]\s*[\d.]+s?\s*[·•:：\-]?\s*/i, "").trim() || String((s && s.label) || "");
const nodeOf = (id) => S.nodes.get(id);
const lvNum = (n) => (n ? (typeof n.level_num === "number" ? n.level_num : Number(String(n.level).replace(/\D/g, ""))) : 0);
const lvTag = (level) => { const l = String(level ?? "0").replace(/\D/g, "") || "0"; return `<span class="lv" data-l="${l}">L${l}</span>`; };

/* 去噪：仅对高信号自适应节点（分裂 / 折叠 / 原子）显示徽标，不再刷屏“模板锚定” */
function badgeTextOf(n) {
  const m = n.adaptation_mode;
  if (m === "SPLIT_HIGH_INTERACTION") return "⚡ 分裂";
  if (m === "FOLD_ARRAY") return `×${n.array_count || (n.children_ids || []).length || ""} 阵列`.replace("× 阵列", "阵列");
  if (m === "ATOMIC_MOUNT") return "L5";
  return "";
}

function fallbackDomEu(id) {
  for (let cur = id, g = 0; cur && g < 8; cur = (nodeOf(cur) || {}).parent_id, g++) {
    const n = nodeOf(cur);
    if (n && lvNum(n) >= 1 && lvNum(n) <= 3) return cur;
  }
  return S.rootId || id;
}

function syncSelectLabel(sel) {
  if (!sel) return;
  const wrap = sel.closest(".select-wrap");
  const out = wrap && wrap.querySelector(".sel-val");
  if (!out) return;
  const opt = sel.options[sel.selectedIndex] || sel.querySelector("option");
  const txt = (opt && opt.textContent) || "";
  out.textContent = txt;
  wrap.title = txt;
}

/* ---------------- 载入与分类分组 ---------------- */
function renderCaseSelector(selectedId) {
  const sel = $("#caseSelect");
  const cats = S.categories || [];
  const catOrder = cats.map((c) => c.category_id);
  const catName = new Map(cats.map((c) => [c.category_id, `${c.tier === "core" ? "核心" : "扩展"} · ${c.name}`]));

  const imported = S.cases.filter((c) => c.is_imported);
  const builtIn = S.cases.filter((c) => !c.is_imported);

  const groupsHtml = [];
  for (const cid of catOrder) {
    const items = builtIn.filter((c) => c.category_id === cid);
    if (!items.length) continue;
    groupsHtml.push(
      `<optgroup label="${esc(catName.get(cid) || cid)}">${items
        .map((c) => `<option value="${esc(c.case_id)}">${esc(c.title)}${c.subtitle ? " [" + esc(c.subtitle) + "]" : ""}</option>`)
        .join("")}</optgroup>`
    );
  }
  const ungrouped = builtIn.filter((c) => !catOrder.includes(c.category_id));
  if (ungrouped.length) {
    groupsHtml.push(
      `<optgroup label="其他案例">${ungrouped.map((c) => `<option value="${esc(c.case_id)}">${esc(c.title)}</option>`).join("")}</optgroup>`
    );
  }
  if (imported.length) {
    groupsHtml.push(
      `<optgroup label="动态解析导入">${imported
        .map((c) => `<option value="${esc(c.case_id)}">${esc(c.title)} [${esc(c.category_name || c.category_id || "Web")}]</option>`)
        .join("")}</optgroup>`
    );
  }

  sel.innerHTML = groupsHtml.length
    ? groupsHtml.join("")
    : S.cases.map((c) => `<option value="${esc(c.case_id)}">${esc(c.title)}</option>`).join("");
  if (selectedId) sel.value = selectedId;
  syncSelectLabel(sel);

  const impCatSel = $("#impCatSelect");
  if (impCatSel && cats.length) {
    impCatSel.innerHTML =
      '<option value="auto">自动特征识别分类</option>' +
      cats.map((c) => `<option value="${esc(c.category_id)}">${esc(c.tier === "core" ? "核心" : "扩展")} · ${esc(c.name)}</option>`).join("");
    syncSelectLabel(impCatSel);
  }
}

function setLayoutMode({ compare = false, focused = false } = {}) {
  const panes = $("#panes");
  S.compareMode = Boolean(compare);
  S.stageFocused = Boolean(focused && !compare);
  panes.classList.toggle("compare-mode", S.compareMode);
  panes.classList.toggle("stage-focused", S.stageFocused);

  const cmpBtn = $("#compareModeBtn");
  if (cmpBtn) {
    cmpBtn.classList.toggle("on", S.compareMode);
    cmpBtn.setAttribute("aria-pressed", String(S.compareMode));
    cmpBtn.textContent = S.compareMode ? "底坞视图" : "并排对照";
  }
  const focBtn = $("#stageFocusBtn");
  if (focBtn) {
    focBtn.classList.toggle("on", S.stageFocused);
    focBtn.setAttribute("aria-pressed", String(S.stageFocused));
    focBtn.textContent = S.stageFocused ? "展开测绘" : "全高舞台";
  }
  setTimeout(() => { fitSkel(); fitStage(); }, 40);
}

async function boot() {
  bindStatic();
  bindResizers();
  bindGateProximity();
  try {
    const data = await api("/api/cases");
    S.cases = data.cases || [];
    S.categories = data.categories || [];
    const want = new URLSearchParams(location.search).get("case");
    const picked = S.cases.find((c) => c.case_id === want) || S.cases.find((c) => c.case_id === data.default_case_id) || S.cases[0];
    if (!picked) throw new Error("未找到案例");
    renderCaseSelector(picked.case_id);
    await loadCase(picked.case_id);
  } catch (e) {
    console.error(e);
    toast(e.message, true);
    setStatus("BLOCKED", "服务未响应");
  }
}

async function loadCase(id, suppliedBundle) {
  const mySeq = ++S.caseSeq;
  let b;
  try {
    b = suppliedBundle ?? await api(`/api/case/${encodeURIComponent(id)}/bundle`);
    if (b.case_id !== id) throw new Error("案例响应与选择不一致");
  } catch (error) {
    if (mySeq !== S.caseSeq) return;
    if (S.caseId) {
      $("#caseSelect").value = S.caseId;
      syncSelectLabel($("#caseSelect"));
    }
    throw error;
  }
  if (mySeq !== S.caseSeq) return;
  S.caseId = id;
  S.sandbox = null;
  S.selected = null;
  S.pendingHighlight = null;
  S.segIdx = 0;
  S.query = "";
  S.explainSeq++;
  $("#caseSelect").value = id;
  syncSelectLabel($("#caseSelect"));
  $("#treeSearch").value = "";
  $("#explain").hidden = true;
  $("#explain").innerHTML = "";
  history.replaceState(null, "", `?case=${encodeURIComponent(id)}`);
  applyBundle(b, { fresh: true });
}

function applyBundle(b, { fresh = false } = {}) {
  if (b.case_id && S.caseId && b.case_id !== S.caseId) return;
  S.bundle = b;
  if (b.case_id) { S.caseId = b.case_id; $("#caseSelect").value = b.case_id; syncSelectLabel($("#caseSelect")); }
  const tree = b.eu_tree || {};
  S.nodes = new Map((tree.nodes || []).map((n) => [n.eu_id, n]));
  S.atoms = new Map();
  for (const [category, entries] of Object.entries(tree.atomic_registry || {})) {
    if (entries && typeof entries === "object") {
      for (const [atomId, atom] of Object.entries(entries)) {
        S.atoms.set(atomId, { atom_id: atomId, category, ...(atom || {}) });
      }
    }
  }
  S.rootId = tree.root_id || ((tree.nodes || []).find((n) => !n.parent_id) || {}).eu_id;
  S.gates = b.gates;
  S.admission = b.admission_status;
  S.readback = b.readback;
  S.cases = S.cases.map((c) => (c.case_id === b.case_id ? { ...c, admission_status: b.admission_status, open_assumptions_count: b.open_assumptions_count } : c));
  if (fresh) {
    const sk = b.skeleton || {};
    const vp = sk.viewport || { width: 1440, height: 900 };
    const isPortraitPoster = (b.case_info || {}).domain === "graphic" || vp.height > vp.width;
    setLayoutMode({ compare: isPortraitPoster, focused: false });
    initOpen();
    renderStageActions();
    renderPresets();
    loadFrame();
  }
  renderHeader();
  renderLeft(fresh);
  renderTreeTools();
  renderTree();
  renderGates();
  renderLedger();
  renderReadback();
  if (fresh) {
    const edgeIds = new Set((tree.edges || []).flatMap((e) => [e.source_eu_id, e.target_eu_id]));
    const isHeroStage = (n) => !/nav|rail|dock|opening|analytics|dialog|modal/i.test(n.eu_id);
    const first =
      firstOf((n) => lvNum(n) === 3 && isHeroStage(n) && edgeIds.has(n.eu_id)) ||
      firstOf((n) => lvNum(n) === 3 && isHeroStage(n)) ||
      firstOf((n) => lvNum(n) === 3) ||
      nodeOf(S.rootId);
    if (first) selectEu(first.eu_id, { from: "init", scroll: false, post: true });
  } else if (S.selected) {
    markSelected();
    refreshExplain();
  }
}

function firstOf(pred) {
  for (const n of S.nodes.values()) if (pred(n)) return n;
  return null;
}
function initOpen() {
  S.open = new Set();
  S.nodes.forEach((n) => { if (lvNum(n) < S.depth && (n.children_ids || []).length) S.open.add(n.eu_id); });
}

/* ---------------- 顶栏与门禁邻近调制 (MODULATES_NEIGHBOR) ---------------- */
function bindGateProximity() {
  const chain = $("#gateChain");
  if (!chain) return;
  const reset = () => $$(".gate-node", chain).forEach((el) => el.style.setProperty("--gate-scale", "1"));
  chain.addEventListener("pointermove", (e) => {
    const nodes = $$(".gate-node", chain);
    if (nodes.length < 2) return;
    nodes.forEach((el) => {
      const r = el.getBoundingClientRect();
      const cx = r.left + r.width / 2;
      const d = Math.abs(e.clientX - cx);
      let sc = 1.0;
      if (d < r.width * 0.6) sc = 1.055;
      else if (d < r.width * 1.75) sc = 1.022;
      el.style.setProperty("--gate-scale", sc.toFixed(3));
    });
  });
  chain.addEventListener("pointerleave", reset);
}

function curGates() { return S.gates || {}; }
function setStatus(state, text) {
  const p = $("#statusPill");
  p.dataset.state = state;
  p.textContent = text;
}
function openCount() {
  const a = (S.bundle && S.bundle.assumptions) || [];
  return a.filter((x) => x.status === "open").length;
}

function renderHeader() {
  const g = curGates();
  const layers = g.layers || [];
  const failLayer = g.blocked_layer;
  $("#gateChain").innerHTML = layers
    .map((l, i) => {
      const fail = l.status !== "PASS" || l.layer === failLayer;
      const cls = fail ? "fail" : "pass";
      const tail = fail ? " BLOCKED" : "";
      return `${i ? '<span class="gate-arrow" aria-hidden="true">→</span>' : ""}<button type="button" class="gate-node ${cls}" data-layer="${esc(l.layer)}" title="${esc(l.layer_label || LAYER_FULL[l.layer] || l.layer)}"><span class="gl">${esc(LAYER_SHORT[l.layer] || l.layer_label)}</span><b>${esc(l.prefix)}</b><span class="gc num">${l.passed}/${l.total}${tail}</span></button>`;
    })
    .join("");
  const adm = S.admission;
  const open = openCount();
  if (adm === "BLOCKED" || g.verdict === "BLOCKED") setStatus("BLOCKED", `BLOCKED · ${g.violated_rule_id || "GATE"}`);
  else if (adm === "RELEASE_READY") setStatus("RELEASE_READY", "RELEASE_READY");
  else setStatus("PROVISIONAL", `PROVISIONAL · 待确认假设 ${open}`);

  renderBanner();
  $("#resetBtn").disabled = !S.sandbox;
  $("#injectBtn").disabled = !$("#presetSelect").value;
  const activeCnt = g.active_count ?? 12;
  const totalLib = g.total_library_rules ?? 24;
  const passedCnt = g.passed_count ?? activeCnt;
  $("#scopeActive").textContent = `当前激活 (${activeCnt})`;
  $("#scopeAll").textContent = `全库矩阵 (${totalLib})`;
  $("#tabGates").innerHTML = `三层规则 <span class="cnt num ${g.verdict === "BLOCKED" ? "bad" : "ok"}">${passedCnt}/${totalLib}</span>`;
  $("#tabLedger").innerHTML = `假设与台账 <span class="cnt num ${open ? "" : "ok"}">${open ? open : "0"}</span>`;
}

function renderBanner() {
  const el = $("#banner");
  const r = S.sandbox && S.sandbox.result;
  if (!r || r.verdict !== "BLOCKED") { el.hidden = true; el.innerHTML = ""; return; }
  const nodes = (r.violated_node_ids || []).filter((id) => nodeOf(id)).slice(0, 4);
  const co = (r.co_failed_rule_ids || []).filter((x) => x !== r.violated_rule_id);
  el.innerHTML = `<span class="b-rule">${esc(r.violated_rule_id)}</span>${co.map((id) => `<span class="b-co">+${esc(id)}</span>`).join("")}<span class="b-layer">${esc(LAYER_FULL[r.blocked_layer] || r.blocked_layer)}阻断${r.violated_rule_name ? " · " + esc(r.violated_rule_name) : ""}</span><span class="b-text" title="${esc(r.attribution || "")}">${esc(r.attribution || "")}</span><span class="b-nodes">${nodes.map((id) => `<button type="button" class="b-node" data-eu="${esc(id)}">${esc(id)}</button>`).join("")}</span><button class="b-close" id="bannerReset" type="button">复位</button>`;
  el.hidden = false;
}

function applicablePresets() {
  return ((S.bundle && S.bundle.counterfactual_presets) || []).filter(
    (p) => !p.applicable_cases || !p.applicable_cases.length || p.applicable_cases.includes(S.caseId)
  );
}

function renderPresets() {
  const sel = $("#presetSelect");
  const list = applicablePresets();
  sel.innerHTML =
    `<option value="">反事实沙盒 (${list.length})</option>` +
    list
      .map((p) => {
        const text = String(p.label || "").includes(p.target_rule_id) ? p.label : `${p.target_rule_id} · ${p.label}`;
        return `<option value="${esc(p.preset)}">${esc(text)}</option>`;
      })
      .join("");
  sel.value = "";
  syncSelectLabel(sel);
}

async function injectPreset(preset) {
  if (!preset || preset === "reset") return clearSandbox();
  const reqCase = S.caseId, reqSeq = S.caseSeq;
  const reviewSeq = ++S.reviewSeq;
  try {
    const r = await post(`/api/case/${encodeURIComponent(reqCase)}/test_rule_gate`, { preset });
    if (S.caseId !== reqCase || S.caseSeq !== reqSeq || S.reviewSeq !== reviewSeq) return;
    $("#presetSelect").value = preset;
    syncSelectLabel($("#presetSelect"));
    S.sandbox = { preset, result: r };
    S.gates = r.gates;
    S.admission = r.admission_status;
    if (r.readback) S.readback = r.readback;
    renderHeader(); renderGates(); renderReadback(); renderTree(); renderLedger();
    if (r.verdict === "BLOCKED") {
      toast(`${r.violated_rule_id} · ${LAYER_FULL[r.blocked_layer] || r.blocked_layer}精准阻断`);
      const first = (r.violated_node_ids || []).find((id) => nodeOf(id));
      if (first) selectEu(first, { from: "banner", scroll: true });
    } else toast("沙盒求值通过");
  } catch (e) {
    if (S.caseSeq === reqSeq && S.reviewSeq === reviewSeq) toast(e.message, true);
  }
}

async function clearSandbox() {
  const reqCase = S.caseId, reqSeq = S.caseSeq;
  const reviewSeq = ++S.reviewSeq;
  try {
    const b = await api(`/api/case/${encodeURIComponent(reqCase)}/bundle`);
    if (S.caseId !== reqCase || S.caseSeq !== reqSeq || S.reviewSeq !== reviewSeq) return;
    S.sandbox = null;
    $("#presetSelect").value = "";
    syncSelectLabel($("#presetSelect"));
    applyBundle(b);
    toast("门禁已复位");
  } catch (e) {
    if (S.caseSeq === reqSeq && S.reviewSeq === reviewSeq) toast(e.message, true);
  }
}

/* ---------------- 底部水平骨架测绘坞 (#paneLeft) ---------------- */
function segments() { return (S.bundle && S.bundle.skeleton && S.bundle.skeleton.segments) || []; }
function curSeg() { return segments()[S.segIdx]; }
function allBoxes() {
  const sk = (S.bundle && S.bundle.skeleton) || {};
  const segs = segments();
  if (segs.length && segs[S.segIdx] && (segs[S.segIdx].bboxes || []).length) return segs[S.segIdx].bboxes;
  return sk.bboxes || [];
}

function renderLeft(fresh) {
  const sk = S.bundle.skeleton || {};
  const segs = segments();
  const isVideo = sk.modality === "video";
  $("#paneLeft").dataset.modality = sk.modality || "image";
  const vp = sk.viewport || { width: 1440, height: 900 };
  $("#modalChip").textContent = isVideo
    ? `VIDEO · ${fmtT(sk.duration_sec)}s · ${segs.length} 段 ${pct(sk.coverage_ratio ?? 1)}`
    : `${String(sk.modality || "IMAGE").toUpperCase()} · ${imageFormatLabel(vp)}`;
  $("#togTimeline").hidden = !isVideo && segs.length <= 1;
  if (fresh) {
    $("#skelSvg").innerHTML = sk.skeleton_svg || "";
  }
  const svg = $("#skelSvg svg");
  let vw = vp.width || 1440, vh = vp.height || 900;
  if (svg) {
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "100%");
    const vb = (svg.getAttribute("viewBox") || "").trim().split(/[\s,]+/).map(Number);
    if (vb.length === 4 && vb[2] > 0 && vb[3] > 0) { vw = vb[2]; vh = vb[3]; }
  }
  $("#skelFrame").style.aspectRatio = `${vw}/${vh}`;
  $("#skelFrame").dataset.vw = vw; $("#skelFrame").dataset.vh = vh;
  renderTimeline();
  renderSegView();
  fitSkel();
}

function imageFormatLabel(vp) {
  if (vp && vp.format) return `${vp.format} 版式`;
  const ci = S.bundle.case_info || {};
  const c = S.cases.find((x) => x.case_id === S.caseId) || {};
  const hint = [ci.paper_format, ci.format, ci.layout, c.source_summary].find((x) => typeof x === "string" && x);
  if (hint && /A\d/i.test(hint)) return hint.match(/A\d[^·,，；;]*/i)[0].trim() + (/版式/.test(hint) ? "" : " 版式");
  return `${vp.width}×${vp.height}`;
}

function renderTimeline() {
  const sk = S.bundle.skeleton || {};
  const segs = segments();
  const show = (sk.modality === "video" || segs.length > 1) && segs.length > 0 && S.layers.timeline;
  const el = $("#timeline");
  el.classList.toggle("off", !show);
  if (!segs.length || (sk.modality !== "video" && segs.length <= 1)) { el.innerHTML = ""; return; }
  el.innerHTML = segs
    .map((s, i) => {
      const shortLbl = cleanSegLabel(s);
      return `<button type="button" class="tl-seg ${i === S.segIdx ? "on" : ""} ${/放大|proximity/i.test(s.label) ? "hot" : ""}" data-i="${i}" style="--seg-c:${SEG_COLORS[i % SEG_COLORS.length]}" title="${fmtT(s.t0)}-${fmtT(s.t1)}s · ${esc(shortLbl)}"><span class="tl-t">${fmtT(s.t0)}-${fmtT(s.t1)}s</span><span class="tl-n">${esc(shortLbl)}</span><span class="tl-bar"></span></button>`;
    })
    .join("");
}

function renderSegView() {
  const sk = S.bundle.skeleton || {};
  const ci = S.bundle.case_info || {};
  const seg = curSeg();
  const svgBox = $("#skelSvg");
  const bgInSvg = $("#skeleton-bg-frame", svgBox);
  const base = $("#skelBase");
  const imgUrl = (seg && seg.frame_url) || (sk.source_image && sk.source_image.url) || sk.frame_url || sk.source_url || ci.source_url || "";
  if (bgInSvg) {
    base.innerHTML = ""; base.dataset.src = "";
    if (imgUrl) bgInSvg.setAttribute("href", imgUrl);
  } else if (imgUrl) {
    if (base.dataset.src !== imgUrl) {
      base.dataset.src = imgUrl;
      base.innerHTML = `<img alt="" src="${esc(imgUrl)}" draggable="false">`;
      $("img", base).addEventListener("error", () => { base.innerHTML = ""; base.dataset.src = ""; });
    }
  } else { base.innerHTML = ""; base.dataset.src = ""; }

  const layered = $$("[data-layer]", svgBox);
  svgBox.classList.toggle("off", !layered.length && !bgInSvg ? !S.layers.skeleton : false);
  $$("[data-segment-id]", svgBox).forEach((e) => {
    const inTl = Boolean(e.closest('[data-layer="timeline"]'));
    const match = !seg || e.getAttribute("data-segment-id") === seg.segment_id;
    if (inTl) {
      e.style.display = "";
      e.setAttribute("opacity", match ? "1" : "0.48");
    } else if (e.classList.contains("sk-segment-group")) {
      e.style.display = match ? "" : "none";
      if (match) e.setAttribute("opacity", "1");
    } else if (!e.closest(".sk-segment-group")) {
      e.style.display = match ? "" : "none";
    }
  });
  layered.forEach((e) => {
    const k = e.getAttribute("data-layer");
    if (k in S.layers) e.style.display = S.layers[k] ? "" : "none";
  });
  renderHit();
  renderSegEus();
}

function renderHit() {
  const sk = S.bundle.skeleton || {};
  const vp = sk.viewport || { width: 1440, height: 900 };
  const hit = $("#skelHit");
  const hasNativeSvgBoxes = Boolean($("#skelSvg .sk-box[data-eu-id]"));
  if (hasNativeSvgBoxes) {
    hit.innerHTML = "";
    markSelected();
    return;
  }
  const boxes = allBoxes();
  hit.classList.toggle("show-bbox", Boolean(S.layers.bbox));
  hit.classList.toggle("nobox", !S.layers.bbox && !S.layers.skeleton);
  hit.innerHTML = boxes
    .map((b, i) => {
      const n = nodeOf(b.eu_id);
      const col = EU_COLORS[(n && n.level) || "L3"];
      return `<div class="skel-box" data-eu="${esc(b.eu_id)}" data-i="${i}" style="--bc:${col};left:${(b.x / vp.width) * 100}%;top:${(b.y / vp.height) * 100}%;width:${(b.w / vp.width) * 100}%;height:${(b.h / vp.height) * 100}%"><span class="lbl">${esc(b.label || (n && n.name) || b.eu_id)}</span></div>`;
    })
    .join("");
  markSelected();
}

function renderSegEus() {
  const seg = curSeg();
  const rawIds = seg && (seg.active_eu_ids || []).length ? seg.active_eu_ids : allBoxes().map((b) => b.eu_id);
  const uniq = [...new Set(rawIds)].filter((id) => nodeOf(id));
  $("#segEus").innerHTML = uniq
    .slice(0, 60)
    .map((id) => { const n = nodeOf(id); return `<button type="button" class="eu-chip" data-eu="${esc(id)}" title="${esc(id)}">${lvTag(n.level)}<span class="nm">${esc(n.name)}</span></button>`; })
    .join("");
  markSelected();
}

function markSelected() {
  const sel = S.selected;
  let anchorId = null;
  if (sel) {
    const visibleSvgIds = $$("#skelSvg [data-eu-id]")
      .filter((e) => !e.closest('[data-layer="timeline"]') && (!e.closest(".sk-segment-group") || e.closest(".sk-segment-group").style.display !== "none"))
      .map((e) => e.getAttribute("data-eu-id"));
    const have = new Set([...allBoxes().map((b) => b.eu_id), ...visibleSvgIds]);
    for (let id = sel, g = 0; id && g < 8; id = (nodeOf(id) || {}).parent_id, g++) {
      if (have.has(id)) { anchorId = id; break; }
    }
  }
  $$("#skelHit .skel-box").forEach((e) => e.classList.toggle("sel", e.dataset.eu === anchorId));
  $$("#skelSvg .sk-box[data-eu-id], #skelSvg rect[data-eu-id]").forEach((e) => {
    const on = Boolean(anchorId && e.getAttribute("data-eu-id") === anchorId);
    e.classList.toggle("kw-sel", on);
    if (on) e.setAttribute("data-active", "true");
    else e.removeAttribute("data-active");
  });
  $$("#segEus .eu-chip").forEach((e) => e.classList.toggle("sel", e.dataset.eu === sel));
  const tag = $("#skelTag");
  if (sel && nodeOf(sel)) {
    const n = nodeOf(sel);
    tag.hidden = false;
    tag.textContent = `${n.level} · ${n.name}`;
  } else tag.hidden = true;
}

function fitSkel() {
  const stage = $("#skelStage"); const fr = $("#skelFrame");
  if (!stage || !fr.dataset.vw) return;
  const cs = getComputedStyle(stage);
  const w = stage.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  const h = stage.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
  const ar = fr.dataset.vw / fr.dataset.vh;
  if (!ar || w <= 0 || h <= 0) return;
  let fw = w, fh = w / ar;
  if (fh > h) { fh = h; fw = h * ar; }
  fr.style.width = `${Math.max(0, fw)}px`;
  fr.style.height = `${Math.max(0, fh)}px`;
}

function gotoSegmentFor(euId) {
  const segs = segments();
  if (!segs.length) return;
  const cur = segs[S.segIdx];
  const has = (s, id) => (s.active_eu_ids || []).includes(id) || (s.bboxes || []).some((b) => b.eu_id === id);
  for (let id = euId, g = 0; id && g < 8; id = (nodeOf(id) || {}).parent_id, g++) {
    if (cur && has(cur, id)) return;
    const n = nodeOf(id);
    const idx = segs.findIndex((s) => has(s, id) || (n && (n.segment_ids || []).includes(s.segment_id)));
    if (idx >= 0) { S.segIdx = idx; renderTimeline(); renderSegView(); return; }
  }
}

/* ---------------- 左侧检视器：EU 树 ---------------- */
function renderTreeTools() {
  const t = S.bundle.eu_tree || {};
  $("#tplChip").textContent = t.template_id || "—";
  $("#tplChip").title = t.template_name || "";
  const ca = S.bundle.category_audit || {};
  const ci = S.bundle.case_info || {};
  const catEl = $("#catChip");
  if (catEl) {
    const cname = ca.category_name || ci.category_name || "通用";
    const cntStr = ca.total_count ? ` · ${ca.passed_count}/${ca.total_count}` : "";
    catEl.textContent = `${cname}${cntStr}`;
    catEl.title = ca.description || cname;
  }
  $$("#depthSeg button").forEach((b) => b.classList.toggle("on", Number(b.dataset.depth) === S.depth));
}

function matches(n, q) {
  const hay = `${n.name} ${n.eu_id} ${n.node_kind || ""} ${badgeTextOf(n)} ${n.template_slot || ""}`.toLowerCase();
  return hay.includes(q);
}

function renderTree() {
  const ul = $("#tree");
  const q = S.query.trim().toLowerCase();
  let visible = null;
  if (q) {
    visible = new Set();
    S.nodes.forEach((n) => {
      if (matches(n, q)) for (let id = n.eu_id, g = 0; id && g < 10; id = (nodeOf(id) || {}).parent_id, g++) visible.add(id);
    });
  }
  const bad = new Set((S.sandbox && S.sandbox.result && S.sandbox.result.violated_node_ids) || []);
  const frag = [];
  const walk = (id, d) => {
    const n = nodeOf(id);
    if (!n || (visible && !visible.has(id))) return;
    const kids = (n.children_ids || []).filter((k) => nodeOf(k));
    const open = q ? true : S.open.has(id);
    const bt = badgeTextOf(n);
    const badge = bt ? `<span class="gb ${MODE_CLASS[n.adaptation_mode] || "plain"}">${esc(bt)}</span>` : "";
    frag.push(`<li class="tn ${open && kids.length ? "open" : ""}" role="treeitem" data-id="${esc(id)}"><div class="tn-row ${S.selected === id ? "sel" : ""} ${bad.has(id) ? "bad" : ""} ${q && matches(n, q) ? "hi" : ""}" style="--d:${d}" data-lvl="${lvNum(n)}" data-eu="${esc(id)}"><span class="tn-twist ${kids.length ? "" : "leaf"}" data-tw="${esc(id)}"></span>${lvTag(n.level)}<span class="tn-name" title="${esc(id)} · ${esc(n.node_kind || "")}">${esc(n.name)}</span>${badge}${kids.length ? `<span class="tn-ct num">${kids.length}</span>` : ""}</div>`);
    if (kids.length && open) { frag.push('<ul class="tn-kids" role="group">'); kids.forEach((k) => walk(k, d + 1)); frag.push("</ul>"); }
    frag.push("</li>");
  };
  if (S.rootId) walk(S.rootId, 0);
  ul.innerHTML = frag.join("") || '<li class="tree-empty">无匹配 EU</li>';
}

function openAncestors(id) {
  for (let p = (nodeOf(id) || {}).parent_id, g = 0; p && g < 10; p = (nodeOf(p) || {}).parent_id, g++) S.open.add(p);
}

async function selectEu(id, { from = "tree", scroll = false, post: doPost = true } = {}) {
  if (!id || !nodeOf(id)) return;
  S.selected = id;
  if (S.query && !matches(nodeOf(id), S.query.trim().toLowerCase())) {
    S.query = "";
    $("#treeSearch").value = "";
  }
  openAncestors(id);
  if (from !== "skeleton") gotoSegmentFor(id);
  renderTree();
  markSelected();
  if (scroll) {
    const row = $(`#tree .tn-row[data-eu="${CSS.escape(id)}"]`);
    if (row) row.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }
  if (doPost && from !== "stage") postHighlight(id);
  else if (from === "init") S.pendingHighlight = id;
  refreshExplain();
}

function buildLocalExplain(id) {
  const n = nodeOf(id);
  if (!n || !S.bundle) return null;
  const ancestors = [];
  for (let p = n.parent_id, g = 0; p && g < 10; p = (nodeOf(p) || {}).parent_id, g++) {
    const pn = nodeOf(p);
    if (pn) ancestors.unshift({ eu_id: pn.eu_id, name: pn.name, level: pn.level, adaptation_badge: badgeTextOf(pn) });
  }
  const l4 = [], l5 = [];
  const walkSub = (cid) => {
    const cn = nodeOf(cid);
    if (!cn) return;
    if (lvNum(cn) === 4) l4.push({ eu_id: cn.eu_id, name: cn.name });
    if (lvNum(cn) === 5) {
      const refs = cn.atom_refs || [];
      if (refs.length) {
        refs.forEach((aid) => {
          const at = S.atoms.get(aid) || { atom_id: aid, name: cn.name };
          l5.push({ eu_id: cn.eu_id, atom_id: aid, category: at.category, name: at.name || cn.name, value: at.value });
        });
      } else l5.push({ eu_id: cn.eu_id, atom_id: cn.eu_id, name: cn.name });
    }
    (cn.children_ids || []).forEach(walkSub);
  };
  (n.children_ids || []).forEach(walkSub);
  const edges = ((S.bundle.eu_tree && S.bundle.eu_tree.edges) || [])
    .filter((e) => e.source_eu_id === id || e.target_eu_id === id)
    .map((e) => {
      const out = e.source_eu_id === id;
      const peer = out ? e.target_eu_id : e.source_eu_id;
      return { edge_id: e.edge_id, edge_type: e.edge_type, direction: out ? "outgoing" : "incoming", peer_eu_id: peer, peer_name: (nodeOf(peer) || {}).name || peer, label: e.label };
    });
  return {
    case_id: S.caseId,
    eu_id: id,
    node: n,
    ancestors,
    descendants: { l4_features: l4, l5_atoms: l5.slice(0, 6), children: (n.children_ids || []).map((k) => nodeOf(k)).filter(Boolean) },
    edges,
  };
}

async function refreshExplain() {
  const id = S.selected;
  const reqCase = S.caseId, reqCaseSeq = S.caseSeq;
  if (!id || !reqCase) return;
  const local = buildLocalExplain(id);
  if (local) renderExplain(local);
  const seq = ++S.explainSeq;
  try {
    const r = await api(`/api/case/${encodeURIComponent(reqCase)}/explain/${encodeURIComponent(id)}`);
    if (seq !== S.explainSeq || S.caseId !== reqCase || S.caseSeq !== reqCaseSeq) return;
    if (r.case_id && r.case_id !== S.caseId) return;
    renderExplain(r);
  } catch (e) {
    console.warn(e);
  }
}

function crumb(id, name, level, badge, cur = false, extra = "") {
  const hasEu = id && nodeOf(id);
  return `<button type="button" class="crumb ${cur ? "cur" : ""}" ${hasEu ? `data-eu="${esc(id)}"` : ""} title="${esc(id || "")}${badge ? " · " + esc(badge) : ""} ${esc(extra)}">${lvTag(level)}<span class="nm">${esc(name)}</span>${extra ? `<span class="av">${esc(extra)}</span>` : ""}</button>`;
}

function renderExplain(r) {
  const n = r.node || nodeOf(r.eu_id) || {};
  const up = (r.ancestors || []).map((a) => crumb(a.eu_id, a.name, a.level, a.adaptation_badge)).join('<span class="ex-sep">/</span>');
  const cur = crumb(n.eu_id || r.eu_id, n.name || r.eu_id, n.level || "L0", n.adaptation_badge, true);
  const d = r.descendants || {};
  const l4 = (d.l4_features || []).map((f) => (typeof f === "string" ? { eu_id: f, name: (nodeOf(f) || {}).name || f } : f));
  const l4h = l4.map((f) => crumb(f.eu_id, f.name || f.eu_id, "L4")).join("");
  const l5 = d.l5_atoms || [];
  const l5h = l5
    .map((a) => {
      const val = a.value !== undefined && a.value !== null && typeof a.value !== "object" ? String(a.value) : a.category || "";
      return crumb(a.eu_id, a.name || a.atom_id, "L5", a.category, false, val);
    })
    .join("");
  const childFallback = !l4h && !l5h
    ? (d.children || []).map((c) => (typeof c === "string" ? nodeOf(c) : c)).filter(Boolean).map((c) => crumb(c.eu_id, c.name, c.level)).join("")
    : "";
  const ed = (r.edges || [])
    .map((e) => `<button type="button" class="crumb edge" data-eu="${esc(e.peer_eu_id)}" title="${esc(e.label || e.edge_id || "")}"><span class="et">${e.direction === "incoming" ? "←" : "→"} ${esc(e.edge_type)}</span><span class="nm">${esc(e.peer_name || e.peer_eu_id)}</span></button>`)
    .join("");
  const rows = [
    `<div class="ex-row"><span class="ex-k">向上</span><div class="ex-items">${up ? up + '<span class="ex-sep">/</span>' : ""}${cur}</div></div>`,
  ];
  if (l4h || l5h || childFallback) rows.push(`<div class="ex-row"><span class="ex-k">向下</span><div class="ex-items">${l4h}${l5h}${childFallback}</div></div>`);
  if (ed) rows.push(`<div class="ex-row"><span class="ex-k">横向边</span><div class="ex-items">${ed}</div></div>`);
  const el = $("#explain");
  el.innerHTML = rows.join("");
  el.hidden = false;
}

/* ---------------- 左侧检视器：两行瑞士三层规则表 ---------------- */
function renderGates() {
  const body = $("#gatesBody");
  const g = curGates();
  $$("#gateScope button").forEach((b) => b.classList.toggle("on", b.dataset.scope === S.scope));
  if (S.scope === "all") return renderLibrary(body, g);
  const presetByRule = new Map(applicablePresets().map((p) => [p.target_rule_id, p.preset]));
  const layersHtml = (g.layers || [])
    .map((l) => {
      const fail = l.status !== "PASS";
      const rules = (l.rules || []).map((r) => ruleRow(r, "", presetByRule.get(r.rule_id))).join("");
      return `<div class="layer-card ${fail ? "fail" : ""}"><div class="layer-hd">${esc(LAYER_FULL[l.layer] || l.layer_label)}<span class="chip">${esc(l.prefix)} · ${esc(l.route_key || l.layer)}</span><span class="lc num">${l.passed}/${l.total}${fail ? " BLOCKED" : ""}</span></div>${rules}</div>`;
    })
    .join("");
  const ca = S.bundle && S.bundle.category_audit;
  const catHtml = ca && Array.isArray(ca.rules) && ca.rules.length
    ? `<div class="layer-card cat-audit-card"><div class="layer-hd">品类规则 · ${esc(ca.category_name)}<span class="chip">${esc(ca.tier === "core" ? "核心族" : "扩展族")}</span><span class="lc num">${ca.passed_count}/${ca.total_count}</span></div>${ca.rules
        .map((r) => ruleRow({ ...r, rule_id: r.rule_id, name: r.name, status: r.status, metric: r.metric, detail: r.detail }))
        .join("")}</div>`
    : "";
  body.innerHTML = layersHtml + catHtml;
}

function ruleRow(r, state = "", preset = "") {
  const rid = r.rule_id || r.id || "";
  const fail = r.status === "FAIL";
  const nodes = (r.violated_node_ids || []).filter((id) => nodeOf(id));
  const tryBtn = preset && !fail ? `<button type="button" class="r-try" data-preset="${esc(preset)}" title="沙盒注入 ${esc(rid)}">演练</button>` : "<span></span>";
  const det = fail && r.detail ? `<div class="r-det">${esc(r.detail)}</div>` : "";
  return `<div class="rule ${fail ? "fail" : ""} ${state} ${nodes.length ? "clk" : ""}" ${nodes.length ? `data-eu="${esc(nodes[0])}"` : ""}><span class="dot"></span><span class="rid">${esc(rid)}</span><span class="rt" title="${esc(r.detail || r.name)}">${esc(r.name || r.title || rid)}</span>${tryBtn}<span class="rm num" title="${esc(r.detail || "")}">${esc(r.metric ?? (fail ? "FAIL" : "PASS"))}</span>${det}</div>`;
}

async function renderLibrary(body, g) {
  if (!S.rulesLib) {
    body.innerHTML = '<div class="empty">载入中…</div>';
    try { S.rulesLib = await api("/api/rules"); } catch (e) { body.innerHTML = `<div class="empty">${esc(e.message)}</div>`; return; }
    if (S.scope !== "all") return;
  }
  const active = new Map();
  (g.layers || []).forEach((l) => (l.rules || []).forEach((r) => active.set(r.rule_id || r.id, r)));
  const presetByRule = new Map(applicablePresets().map((p) => [p.target_rule_id, p.preset]));
  const mods = S.rulesLib.modules || [];
  body.innerHTML = mods
    .map((m) => {
      const rules = m.rules || [];
      const on = rules.filter((r) => active.has(r.rule_id || r.id)).length;
      const title = m.title || m.name || m.module_id || "";
      const key = [m.rule_prefix || m.prefix, m.route_value || m.modality || m.domain || m.scope].filter(Boolean).join(" · ");
      return `<div class="layer-card"><div class="layer-hd">${esc(title)}<span class="chip">${esc(key || m.route_key || "")}</span><span class="lc num" style="color:${on ? "var(--kw-ok)" : "var(--kw-ink-3)"}">${on ? "激活 " + on + "/" + rules.length : "未激活 0/" + rules.length}</span></div>${rules
        .map((r) => {
          const id = r.rule_id || r.id;
          const a = active.get(id);
          return a
            ? ruleRow({ ...r, ...a, rule_id: id, name: r.name || a.name }, "", presetByRule.get(id))
            : `<div class="rule off"><span class="dot"></span><span class="rid">${esc(id)}</span><span class="rt" title="${esc(r.name || "")}">${esc(r.name || id)}</span><span></span><span class="rm">未激活</span></div>`;
        })
        .join("")}</div>`;
    })
    .join("");
}

/* ---------------- 左侧检视器：假设与台账 ---------------- */
async function renderLedger() {
  const list = (S.bundle && S.bundle.assumptions) || [];
  const open = list.filter((a) => a.status === "open").length;
  $("#asmCount").textContent = `${list.length - open}/${list.length} 已签认`;
  $("#confirmAllBtn").disabled = !open;
  $("#asmList").innerHTML = list
    .map((a) => {
      const done = a.status === "confirmed";
      const n = nodeOf(a.eu_id);
      return `<li class="asm ${done ? "confirmed" : ""}" data-a="${esc(a.assumption_id)}"><div class="asm-top"><span class="asm-id">${esc(a.assumption_id)}</span><span class="asm-st">${done ? "CONFIRMED" : "OPEN"}</span><span class="asm-act">${done ? `<button type="button" class="btn btn-ghost btn-sm" data-act="reset">重置</button>` : `<button type="button" class="btn btn-primary btn-sm" data-act="confirm">确认</button>`}</span></div><div class="asm-txt">${esc(a.title)}</div><div class="asm-meta">${a.bound_rule_id ? `<span class="chip">${esc(a.bound_rule_id)}</span>` : ""}${a.category ? `<span class="chip">${esc(a.category)}</span>` : ""}${n ? `<button type="button" class="eu-chip" data-eu="${esc(a.eu_id)}">${lvTag(n.level)}<span class="nm">${esc(n.name)}</span></button>` : ""}</div>${a.assumed_value ? `<div class="asm-sub">${esc(a.assumed_value)}</div>` : ""}${a.evidence_gap ? `<div class="asm-sub muted">${esc(a.evidence_gap)}</div>` : ""}</li>`;
    })
    .join("") || '<li class="empty">无待确认假设</li>';

  let led = S.bundle && S.bundle.error_ledger;
  let entries = Array.isArray(led) ? led : (led && led.entries) || [];
  if (!entries.length) {
    if (!S.ledgerFallback) {
      try { const d = await api("/api/error_ledger"); S.ledgerFallback = d.entries || []; } catch { S.ledgerFallback = []; }
    }
    entries = S.ledgerFallback;
  }
  const rid = S.sandbox && S.sandbox.result && S.sandbox.result.violated_rule_id;
  $("#resList").innerHTML = entries
    .map((e) => {
      const id = e.res_id || e.entry_id || e.id || "RES-KW";
      const title = e.title || e.symptom || "";
      const body = [e.root_cause, e.fix].filter(Boolean).join(" → ") || e.symptom || e.detail || "";
      const rule = e.rule_id || e.bound_rule_id || "";
      return `<li class="res ${rid && rule === rid ? "cur" : ""}"><span class="rk">${esc(id)}</span><div class="rb"><b>${esc(title)}</b>${body ? `<span>${esc(body)}</span>` : ""}</div>${rule ? `<span class="chip">${esc(rule)}</span>` : ""}</li>`;
    })
    .join("") || '<li class="empty">无台账记录</li>';
}

async function confirmAssumption(action, assumption_id) {
  const reqCase = S.caseId, reqSeq = S.caseSeq;
  const reviewSeq = ++S.reviewSeq;
  try {
    const body = { action, assumption_id: assumption_id || "all" };
    const r = await post(`/api/case/${encodeURIComponent(reqCase)}/confirm_assumption`, body);
    if (S.caseId !== reqCase || S.caseSeq !== reqSeq || S.reviewSeq !== reviewSeq) return;
    S.sandbox = null;
    $("#presetSelect").value = "";
    syncSelectLabel($("#presetSelect"));
    if (r.bundle) applyBundle(r.bundle); else await loadCase(reqCase);
    const n = r.open_assumptions_count ?? openCount();
    let notice = action === "reset" ? `已重置 · 待确认假设 ${n}` : `已确认 · 待确认假设 ${n}`;
    if (r.admission_status === "BLOCKED") notice += " · BLOCKED";
    else if (r.admission_status === "RELEASE_READY") notice = "全部签认 · RELEASE_READY";
    toast(notice);
  } catch (e) {
    if (S.caseSeq === reqSeq && S.reviewSeq === reviewSeq) toast(e.message, true);
  }
}

/* ---------------- 右上方超大主舞台 (#paneRight) ---------------- */
function renderReadback() {
  const r = S.readback || {};
  const c = $("#readbackChip");
  c.textContent = r.summary_pill || (r.dom_eu_binding_coverage !== undefined ? `DOM 溯源 ${pct(r.dom_eu_binding_coverage)}` : "—");
  c.classList.toggle("bad", r.status === "FAIL");
}

function renderStageActions() {
  const isGraphic = (S.bundle.case_info || {}).domain === "graphic";
  const el = $("#actSeg");
  S.action = "normal";
  if (!isGraphic) {
    const stageLabels = {
      refract_crm_web: [["normal", "正常"], ["proximity_demo", "邻近放大"], ["analytics", "Pipeline"]],
      haven_admin_web: [["normal", "正常"], ["proximity_demo", "导轨邻近"], ["analytics", "Sales"]],
      knob_hardware_web: [["normal", "正常"], ["spin_dials", "双编码器"], ["keysets", "Keysets"]],
      nogood_brutal_web: [["normal", "正常"], ["toggle_radio", "RADIO"], ["shop", "Shop"]],
      axiom_hud_web: [["normal", "正常"], ["run_apl", "APL 查询"], ["dashboards", "Dashboards"]],
      weeksync_paper_web: [["normal", "正常"], ["proximity_demo", "虚线导轨"], ["analytics", "Weeks"]],
      defined_aurora_web: [["normal", "正常"], ["open_manifesto", "品牌宣言"], ["portfolio", "Portfolio"]],
      rauno_craft_video: [["normal", "正常"], ["radial_demo", "径向菜单"], ["toggle_slowmo", "0.25× 慢放"]],
      fps60_motion_video: [["normal", "正常"], ["split_demo", "卡片分裂"], ["morph_demo", "元素变形"]],
      screen_studio_video: [["normal", "正常"], ["proximity_demo", "导轨邻近"], ["auto_zoom", "2.0× 运镜"]],
      resend_dev_web: [["normal", "正常"], ["send_test", "测试请求"], ["webhooks", "Webhooks"]],
      linear_workspace_web: [["normal", "正常"], ["proximity_demo", "侧栏邻近"], ["toggle_diff", "Code Diff"]],
      raycast_cmd_web: [["normal", "正常"], ["palette_demo", "命令面板"], ["keyboard_demo", "快捷键矩阵"]],
      amie_collab_web: [["normal", "正常"], ["proximity_demo", "日程导轨"], ["ask_amie", "Ask Amie"]],
    };
    const labels = stageLabels[S.caseId] || [["normal", "正常"], ["proximity_demo", "邻近放大"], ["analytics", "Analytics"]];
    el.innerHTML = labels
      .map(([k, t]) => `<button type="button" data-act="${k}" class="${k === "normal" ? "on" : ""}">${t}</button>`)
      .join("");
  } else {
    S.toggles = { grid: true, bleed: true };
    el.innerHTML = [["toggle_grid", "12 列网格"], ["toggle_bleed", "出血框"]]
      .map(([k, t]) => `<button type="button" data-act="${k}" class="on">${t}</button>`).join("");
  }
}

function frame() { return $("#stageFrame"); }
function loadFrame() {
  const url = S.bundle.stage_url;
  S.frameLoaded = false;
  const f = frame();
  if (f.getAttribute("src") !== url) f.setAttribute("src", url);
  else if (f.contentWindow) f.contentWindow.location.reload();
  fitStage();
}
function sendFrame(msg) {
  const f = frame();
  if (f && f.contentWindow) f.contentWindow.postMessage(msg, location.origin);
}
function postHighlight(id) {
  S.pendingHighlight = id;
  sendFrame({ type: "KAIWU_HIGHLIGHT_EU", eu_id: id, fallback_eu_id: fallbackDomEu(id), action: "highlight" });
}

function fitStage() {
  const st = $("#stage"); const fit = $("#stageFit"); const f = frame();
  if (!st || !S.bundle) return;
  const cs = getComputedStyle(st);
  const W = st.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  const H = st.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
  if (W <= 0 || H <= 0) return;
  const sk = S.bundle.skeleton || {};
  const vp = sk.viewport || { width: 1440, height: 900 };
  let vw, vh, sc;
  if (S.vp === "mobile") {
    vw = 390; vh = 844; sc = Math.min(1, W / vw, H / vh);
  } else if (sk.modality === "video") {
    vw = vp.width || 1440; vh = vp.height || 900; sc = Math.min(W / vw, H / vh);
  } else if (vp.height > vp.width) {
    vw = 820; vh = 1210; sc = Math.min(W / vw, H / vh);
  } else {
    vw = vp.width || 1280; vh = vp.height || 900; sc = Math.min(W / vw, H / vh);
  }
  fit.style.width = `${vw * sc}px`; fit.style.height = `${vh * sc}px`;
  f.style.width = `${vw}px`; f.style.height = `${vh}px`; f.style.transform = `scale(${sc})`;
  const meta = $("#stageMeta");
  if (meta) meta.textContent = `${vw}×${vh} · ${Math.round(sc * 100)}%`;
}

function runStageAction(act) {
  clearTimeout(S.proxTimer);
  if (act === "toggle_grid") S.toggles.grid = !S.toggles.grid;
  else if (act === "toggle_bleed") S.toggles.bleed = !S.toggles.bleed;
  else S.action = act;
  $$("#actSeg button").forEach((b) => {
    const k = b.dataset.act;
    b.classList.toggle("on", k === "toggle_grid" ? S.toggles.grid : k === "toggle_bleed" ? S.toggles.bleed : k === S.action);
  });
  if (act === "proximity_demo") {
    sendFrame({ type: "KAIWU_PREVIEW_ACTION", action: "proximity_demo" });
    S.proxTimer = setTimeout(() => sendFrame({ type: "KAIWU_PREVIEW_ACTION", action: "proximity_demo" }), 560);
    const proxNode =
      firstOf((n) => lvNum(n) === 3 && /proximity|dock/i.test(n.eu_id)) ||
      firstOf((n) => /proximity/i.test(n.eu_id) || n.adaptation_mode === "SPLIT_HIGH_INTERACTION");
    if (proxNode) selectEu(proxNode.eu_id, { from: "stage", scroll: true, post: false });
  } else if (act === "analytics") {
    sendFrame({ type: "KAIWU_PREVIEW_ACTION", action: "analytics" });
    const anaNode =
      firstOf((n) => lvNum(n) === 3 && /analytics/i.test(n.eu_id)) ||
      firstOf((n) => lvNum(n) === 3 && /hot_deals|sales_bars|specs_array|system_log|results_array|summary_cards|portfolio_grid|modules_array/i.test(n.eu_id));
    if (anaNode) selectEu(anaNode.eu_id, { from: "stage", scroll: true, post: false });
  } else if (act === "normal") {
    sendFrame({ type: "KAIWU_PREVIEW_ACTION", action: "normal" });
    const heroNode = firstOf((n) => lvNum(n) === 3 && !/dock|opening|analytics|dialog|modal/i.test(n.eu_id));
    if (heroNode) selectEu(heroNode.eu_id, { from: "stage", scroll: true, post: false });
  } else {
    sendFrame({ type: "KAIWU_PREVIEW_ACTION", action: act });
  }
}

/* ---------------- 双向拖拽分割柄（左侧语义栏宽度 + 底部测绘坞高度） ---------------- */
function bindResizers() {
  const rootStyle = document.documentElement.style;

  const rv = $("#resizerV");
  if (rv) {
    rv.addEventListener("dblclick", () => { rootStyle.setProperty("--kw-inspector-w", "392px"); fitSkel(); fitStage(); });
    rv.addEventListener("pointerdown", (e) => {
      if (window.innerWidth <= 1120) return;
      e.preventDefault();
      rv.setPointerCapture(e.pointerId);
      rv.classList.add("dragging");
      const startX = e.clientX;
      const startW = $("#paneMid").getBoundingClientRect().width;
      const onMove = (ev) => {
        const nw = Math.max(320, Math.min(540, startW + (ev.clientX - startX)));
        rootStyle.setProperty("--kw-inspector-w", `${Math.round(nw)}px`);
        fitSkel(); fitStage();
      };
      const onUp = () => {
        rv.classList.remove("dragging");
        rv.removeEventListener("pointermove", onMove);
        rv.removeEventListener("pointerup", onUp);
        rv.removeEventListener("pointercancel", onUp);
      };
      rv.addEventListener("pointermove", onMove);
      rv.addEventListener("pointerup", onUp);
      rv.addEventListener("pointercancel", onUp);
    });
  }

  const rh = $("#resizerH");
  if (rh) {
    rh.addEventListener("dblclick", () => { rootStyle.setProperty("--kw-dock-h", "224px"); fitSkel(); fitStage(); });
    rh.addEventListener("pointerdown", (e) => {
      if (window.innerWidth <= 1120 || S.stageFocused || S.compareMode) return;
      e.preventDefault();
      rh.setPointerCapture(e.pointerId);
      rh.classList.add("dragging");
      const startY = e.clientY;
      const startH = $("#paneLeft").getBoundingClientRect().height;
      const onMove = (ev) => {
        const nh = Math.max(168, Math.min(400, startH - (ev.clientY - startY)));
        rootStyle.setProperty("--kw-dock-h", `${Math.round(nh)}px`);
        fitSkel(); fitStage();
      };
      const onUp = () => {
        rh.classList.remove("dragging");
        rh.removeEventListener("pointermove", onMove);
        rh.removeEventListener("pointerup", onUp);
        rh.removeEventListener("pointercancel", onUp);
      };
      rh.addEventListener("pointermove", onMove);
      rh.addEventListener("pointerup", onUp);
      rh.addEventListener("pointercancel", onUp);
    });
  }

  $("#compareModeBtn")?.addEventListener("click", () => {
    setLayoutMode({ compare: !S.compareMode, focused: false });
  });
  $("#stageFocusBtn")?.addEventListener("click", () => {
    setLayoutMode({ compare: false, focused: !S.stageFocused });
  });
}

/* ---------------- 开物工作台自举 EU 透视抽屉 ---------------- */
async function openSelfXray() {
  const dlg = $("#selfXrayDialog");
  if (!dlg) return;
  if (!S.selfEuSpec) {
    try {
      const res = await fetch("kaiwu_self_eu.json");
      S.selfEuSpec = await res.json();
    } catch {
      S.selfEuSpec = null;
    }
  }
  const spec = S.selfEuSpec;
  const domIds = new Set($$("[data-eu-id]").filter((el) => !el.closest("#skelSvg")).map((el) => el.getAttribute("data-eu-id")));
  const expected = spec ? (spec.nodes || []).filter((n) => n.rendered).map((n) => n.eu_id) : [];
  const covered = expected.filter((id) => domIds.has(id)).length;
  const covPct = expected.length ? Math.round((covered / expected.length) * 100) : 100;
  const reg = (spec && spec.atomic_registry) || {};
  const atomCount = ["surface_atoms", "typography_atoms", "layout_atoms", "motion_atoms", "evidence_atoms"]
    .reduce((acc, k) => acc + Object.keys(reg[k] || {}).length, 0);
  const edges = (spec && spec.edges) || [];

  $("#xrayStats").innerHTML = [
    ["L0~L5 节点", spec ? `${spec.nodes.length}` : "—"],
    ["DOM 溯源", `${covered}/${expected.length} (${covPct}%)`],
    ["单源 L5 原子", `${atomCount}`],
    ["横向交互边", `${edges.length} 条`],
  ].map(([k, v]) => `<div class="xray-stat"><small>${esc(k)}</small><strong>${esc(v)}</strong></div>`).join("");

  $("#xrayEdges").innerHTML = edges
    .map((e) => `<div class="xray-item"><code>${esc(e.edge_type)}</code><span>${esc(e.label)}</span></div>`)
    .join("") || '<div class="empty">未载入自举规范</div>';

  $("#toggleXrayWireBtn").textContent = S.xrayWire ? "关闭 EU 线框透视" : "开启 EU 线框透视";
  $("#toggleXrayWireBtn").classList.toggle("on", S.xrayWire);
  if (typeof dlg.showModal === "function") dlg.showModal();
}

/* ---------------- 事件 ---------------- */
function bindStatic() {
  $("#caseSelect").addEventListener("change", (e) => {
    syncSelectLabel(e.target);
    loadCase(e.target.value).catch((x) => toast(x.message, true));
  });
  $("#impCatSelect")?.addEventListener("change", (e) => syncSelectLabel(e.target));

  const impBtn = $("#importBtn");
  const impDlg = $("#importDialog");
  const impCloseBtn = $("#impCloseBtn");
  const impForm = $("#importForm");
  if (impBtn && impDlg) {
    impBtn.addEventListener("click", () => {
      $("#impStatus").textContent = "";
      if (typeof impDlg.showModal === "function") impDlg.showModal();
    });
    impCloseBtn?.addEventListener("click", () => impDlg.close());
    impDlg.addEventListener("close", () => impBtn.focus());
    impForm?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const urlVal = ($("#impUrlInput").value || "").trim();
      const cidVal = ($("#impCaseInput").value || "").trim();
      const catVal = $("#impCatSelect").value || "auto";
      if (!urlVal) return;
      const submitBtn = $("#impSubmitBtn");
      submitBtn.disabled = true;
      $("#impStatus").textContent = "三断点真机测绘中…";
      try {
        const res = await api("/api/parse/url", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: urlVal, case_id: cidVal || null, category: catVal }),
        });
        const listData = await api("/api/cases");
        S.cases = listData.cases || [];
        S.categories = listData.categories || S.categories;
        renderCaseSelector(res.case_id);
        impDlg.close();
        await loadCase(res.case_id, res.bundle);
        toast(`解析完成：${res.category_info?.category_name || res.case_id}`);
      } catch (err) {
        $("#impStatus").textContent = err.message || "解析失败";
        toast(err.message || "解析失败", true);
      } finally {
        submitBtn.disabled = false;
      }
    });
  }

  const xrayBtn = $("#selfXrayBtn");
  const xrayDlg = $("#selfXrayDialog");
  if (xrayBtn && xrayDlg) {
    xrayBtn.addEventListener("click", openSelfXray);
    $("#xrayCloseBtn")?.addEventListener("click", () => xrayDlg.close());
    xrayDlg.addEventListener("close", () => xrayBtn.focus());
    $("#toggleXrayWireBtn")?.addEventListener("click", () => {
      S.xrayWire = !S.xrayWire;
      document.body.classList.toggle("kw-xray", S.xrayWire);
      xrayBtn.classList.toggle("on", S.xrayWire);
      $("#toggleXrayWireBtn").textContent = S.xrayWire ? "关闭 EU 线框透视" : "开启 EU 线框透视";
      $("#toggleXrayWireBtn").classList.toggle("on", S.xrayWire);
    });
  }

  $("#mobilePaneNav")?.addEventListener("click", (e) => {
    const b = e.target.closest("[data-mpane]");
    if (!b) return;
    const key = b.dataset.mpane;
    $$("#mobilePaneNav .tab").forEach((x) => x.classList.toggle("on", x === b));
    $("#paneLeft").classList.toggle("m-active", key === "left");
    $("#paneMid").classList.toggle("m-active", key === "mid");
    $("#paneRight").classList.toggle("m-active", key === "right");
    setTimeout(() => { fitSkel(); fitStage(); }, 30);
  });

  $("#presetSelect").addEventListener("change", (e) => {
    syncSelectLabel(e.target);
    const v = e.target.value;
    $("#injectBtn").disabled = !v;
    if (v) injectPreset(v);
    else clearSandbox();
  });
  $("#injectBtn").addEventListener("click", () => injectPreset($("#presetSelect").value));
  $("#resetBtn").addEventListener("click", () => clearSandbox());
  $("#banner").addEventListener("click", (e) => {
    const n = e.target.closest("[data-eu]"); if (n) selectEu(n.dataset.eu, { scroll: true });
    if (e.target.closest("#bannerReset")) clearSandbox();
  });

  $("#midTabs").addEventListener("click", (e) => {
    const t = e.target.closest(".tab"); if (!t) return;
    $$("#midTabs .tab").forEach((x) => x.classList.toggle("on", x === t));
    $$(".tabpane").forEach((p) => p.classList.toggle("on", p.id === `tab-${t.dataset.tab}`));
  });

  $("#layerToggles").addEventListener("click", (e) => {
    const b = e.target.closest(".tog"); if (!b) return;
    const k = b.dataset.layer;
    S.layers[k] = !S.layers[k];
    b.classList.toggle("on", S.layers[k]);
    if (k === "timeline") renderTimeline();
    renderSegView(); fitSkel();
  });
  $("#timeline").addEventListener("click", (e) => {
    const b = e.target.closest(".tl-seg"); if (!b) return;
    S.segIdx = Number(b.dataset.i);
    renderTimeline(); renderSegView();
  });
  $("#skelFrame").addEventListener("click", (e) => {
    const segEl = e.target.closest('.sk-seg[data-segment-id]');
    if (segEl) {
      const idx = segments().findIndex((s) => s.segment_id === segEl.getAttribute("data-segment-id"));
      if (idx >= 0) { S.segIdx = idx; renderTimeline(); renderSegView(); }
      const anchor = segEl.getAttribute("data-eu-id");
      if (anchor && nodeOf(anchor)) selectEu(anchor, { from: "skeleton", scroll: true });
      return;
    }
    const x = e.clientX, y = e.clientY;
    const candidates = [
      ...$$("#skelSvg .sk-box[data-eu-id], #skelSvg rect[data-eu-id]").filter((el) => !el.closest('[data-layer="timeline"]')),
      ...$$("#skelHit .skel-box"),
    ].filter((el) => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
    });
    if (candidates.length) {
      candidates.sort((a, b) => {
        const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        return ra.width * ra.height - rb.width * rb.height;
      });
      const eu = candidates[0].getAttribute("data-eu-id") || candidates[0].dataset.eu;
      if (eu) return selectEu(eu, { from: "skeleton", scroll: true });
    }
    const svgEl = e.target.closest("[data-eu-id]");
    if (svgEl) selectEu(svgEl.getAttribute("data-eu-id"), { from: "skeleton", scroll: true });
  });
  $("#segEus").addEventListener("click", (e) => { const b = e.target.closest("[data-eu]"); if (b) selectEu(b.dataset.eu, { from: "chip", scroll: true }); });

  $("#depthSeg").addEventListener("click", (e) => {
    const b = e.target.closest("button"); if (!b) return;
    S.depth = Number(b.dataset.depth);
    S.open = new Set();
    S.nodes.forEach((n) => { if ((n.children_ids || []).length && lvNum(n) < S.depth) S.open.add(n.eu_id); });
    if (S.selected) openAncestors(S.selected);
    renderTreeTools(); renderTree();
  });
  let st = 0;
  $("#treeSearch").addEventListener("input", (e) => { clearTimeout(st); st = setTimeout(() => { S.query = e.target.value; renderTree(); }, 100); });
  $("#tree").addEventListener("click", (e) => {
    const tw = e.target.closest(".tn-twist");
    if (tw && !tw.classList.contains("leaf")) { const id = tw.dataset.tw; S.open.has(id) ? S.open.delete(id) : S.open.add(id); renderTree(); return; }
    const row = e.target.closest(".tn-row"); if (row) selectEu(row.dataset.eu, { from: "tree" });
  });
  $("#tree").addEventListener("dblclick", (e) => {
    const row = e.target.closest(".tn-row"); if (!row) return;
    const id = row.dataset.eu; S.open.has(id) ? S.open.delete(id) : S.open.add(id); renderTree();
  });
  $("#explain").addEventListener("click", (e) => { const b = e.target.closest("[data-eu]"); if (b && b.dataset.eu) selectEu(b.dataset.eu, { from: "explain", scroll: true }); });

  $("#gateScope").addEventListener("click", (e) => { const b = e.target.closest("button"); if (!b) return; S.scope = b.dataset.scope; renderGates(); });
  $("#gatesBody").addEventListener("click", (e) => {
    const tryBtn = e.target.closest(".r-try[data-preset]");
    if (tryBtn) return injectPreset(tryBtn.dataset.preset);
    const r = e.target.closest(".rule[data-eu]");
    if (r) selectEu(r.dataset.eu, { scroll: true });
  });
  $("#gateChain").addEventListener("click", (e) => {
    const n = e.target.closest(".gate-node"); if (!n) return;
    $$("#midTabs .tab").forEach((x) => x.classList.toggle("on", x.dataset.tab === "gates"));
    $$(".tabpane").forEach((p) => p.classList.toggle("on", p.id === "tab-gates"));
    S.scope = "active"; renderGates();
    const card = $$("#gatesBody .layer-card")[$$("#gateChain .gate-node").indexOf(n)];
    if (card) card.scrollIntoView({ block: "start", behavior: "smooth" });
  });

  $("#confirmAllBtn").addEventListener("click", () => confirmAssumption("confirm_all"));
  $("#asmList").addEventListener("click", (e) => {
    const eu = e.target.closest(".eu-chip[data-eu]"); if (eu) return selectEu(eu.dataset.eu, { scroll: true });
    const b = e.target.closest("[data-act]"); if (!b) return;
    confirmAssumption(b.dataset.act, b.closest(".asm").dataset.a);
  });

  $("#vpSeg").addEventListener("click", (e) => {
    const b = e.target.closest("button"); if (!b) return;
    S.vp = b.dataset.vp;
    $$("#vpSeg button").forEach((x) => x.classList.toggle("on", x === b));
    fitStage();
    setTimeout(() => S.selected && postHighlight(S.selected), 360);
  });
  $("#actSeg").addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) runStageAction(b.dataset.act); });

  frame().addEventListener("load", () => {
    S.frameLoaded = true;
    fitStage();
    const id = S.pendingHighlight || S.selected;
    const caseSeq = S.caseSeq;
    if (id) setTimeout(() => {
      if (caseSeq === S.caseSeq && id === S.selected) postHighlight(id);
    }, 220);
  });
  window.addEventListener("message", (e) => {
    if (e.source !== frame().contentWindow || e.origin !== location.origin) return;
    const d = e.data;
    if (!d || typeof d !== "object") return;
    if (d.type === "KAIWU_SELECT_EU" && d.eu_id) {
      if (d.case_id && d.case_id !== S.caseId) return;
      if (nodeOf(d.eu_id)) selectEu(d.eu_id, { from: "stage", scroll: true });
    }
  });
  const ro = new ResizeObserver(() => { fitSkel(); fitStage(); });
  ro.observe($("#skelStage")); ro.observe($("#stage"));
  window.addEventListener("resize", () => { fitSkel(); fitStage(); });
}

document.addEventListener("DOMContentLoaded", boot);
