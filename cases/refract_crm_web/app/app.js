(() => {
  'use strict';

  const $ = (s, root = document) => root.querySelector(s);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const shell = $('#workspace');
  const sidebar = $('#sidebar');
  const viewport = $('#main-panel');
  const dialog = $('#rfDialog');
  const toastEl = $('#rfToast');

  const NAV_GROUPS = [
    ['WORKSPACE', [
      ['overview', 'Overview', 'grid'],
      ['inbox', 'Inbox', 'mail', 3],
      ['calendar', 'Calendar', 'cal'],
      ['tasks', 'Tasks', 'check', 7],
    ]],
    ['SALES', [
      ['pipeline', 'Pipeline', 'pipe'],
      ['leads', 'Leads', 'filter', 6],
      ['contacts', 'Contacts', 'users'],
      ['quotes', 'Quotes', 'doc'],
    ]],
    ['INSIGHTS', [
      ['reports', 'Reports', 'chart'],
    ]],
  ];

  const ICONS = {
    grid: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    mail: '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/>',
    cal: '<rect x="3" y="4" width="18" height="17" rx="2.5"/><path d="M8 2v4M16 2v4M3 10h18"/>',
    check: '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    pipe: '<path d="M4 5h4v14H4zM10 5h4v10h-4zM16 5h4v7h-4z"/>',
    filter: '<path d="M3 5h18l-7 8v6l-4-2v-4z"/>',
    users: '<circle cx="9" cy="8" r="3.5"/><path d="M2 20a7 7 0 0 1 14 0"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14a5 5 0 0 1 6 6"/>',
    doc: '<path d="M6 3h9l5 5v13H6z"/><path d="M15 3v5h5"/>',
    chart: '<path d="M4 19V5M4 19h16M8 15l4-5 3 3 5-7"/>',
    phone: '<path d="M22 16.9v3a2 2 0 0 1-2.2 2A19.8 19.8 0 0 1 3.1 5.2 2 2 0 0 1 5.1 3h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L9 11a16 16 0 0 0 4 4l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7a2 2 0 0 1 1.7 2Z" fill="currentColor" stroke="none"/>',
    prev: '<path d="m11 17-5-5 5-5M18 17l-5-5 5-5"/>',
    next: '<path d="m13 17 5-5-5-5M6 17l5-5-5-5"/>',
    search: '<circle cx="10" cy="10" r="6.5"/><path d="m15 15 5 5"/>',
    left: '<path d="m15 6-6 6 6 6"/>',
    right: '<path d="m9 6 6 6-6 6"/>',
    download: '<path d="M12 3v12m-4-4 4 4 4-4M4 18v2h16v-2"/>',
  };
  const svgIcon = (k, size = 17) => `<svg aria-hidden="true" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${ICONS[k] || ICONS.grid}</svg>`;

  const REVENUE_SERIES = {
    '7D': { total: '$482K', delta: '+4.6%', target: '$460K', labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], rev: [58, 64, 62, 74, 81, 69, 74], tgt: [55, 59, 61, 65, 70, 68, 72] },
    '30D': { total: '$1.42M', delta: '+3.1%', target: '$1.37M', labels: ['W1', 'W2', 'W3', 'W4'], rev: [310, 345, 368, 397], tgt: [305, 330, 355, 380] },
    '12M': { total: '$3.62M', delta: '+1.8%', target: '$3.55M', labels: ['Dec', 'Feb', 'Apr', 'Jun', 'Aug', 'Oct', 'Nov'], rev: [250, 224, 275, 292, 335, 358, 412], tgt: [254, 240, 268, 286, 322, 348, 392] },
  };

  const CONTACTS = [
    { initials: 'SB', name: 'Sofia Brandt', title: 'COO · Brightwater Co', quote: 'Pricing for all 38 stores', deal: 'Store analytics rollout · $86.0k', phone: '+1 (555) 874-2000' },
    { initials: 'MK', name: 'Marcus Klein', title: 'VP Ops · Nordik Retail', quote: 'Annual renewal & SLA upgrade', deal: 'Enterprise license · $142.0k', phone: '+1 (555) 391-8840' },
    { initials: 'AL', name: 'Aria Lin', title: 'Head of IT · Crestline', quote: 'Security audit sign-off call', deal: 'Multi-region seat pack · $64.5k', phone: '+1 (555) 602-1190' },
  ];

  const DEALS = [
    { name: 'Brightwater Co · 38 Stores', stage: 'Proposal', amount: '$86,000', prob: '78%' },
    { name: 'Nordik Retail · Enterprise', stage: 'Negotiation', amount: '$142,000', prob: '84%' },
    { name: 'Crestline Group · Core', stage: 'Qualified', amount: '$64,500', prob: '55%' },
  ];

  const state = {
    route: 'overview',
    collapsed: false,
    activeRange: '12M',
    contactIdx: 0,
    callsDone: 0,
    inCall: false,
    tasks: [
      { id: 't1', label: 'Send updated quote to Brightwater COO', done: true },
      { id: 't2', label: 'Review Q4 pipeline velocity outliers', done: false },
      { id: 't3', label: 'Follow up with Marcus on SLA clauses', done: false },
      { id: 't4', label: 'Export 12M closed-won CSV for finance', done: false },
      { id: 't5', label: 'Prepare Friday executive forecast', done: false },
      { id: 't6', label: 'Confirm Crestline onboarding schedule', done: false },
    ],
    scrollByRoute: {},
    lastFocus: null,
  };

  let dockPointer = null;
  const dockRadius = 112;
  const dockGain = 0.35;

  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toast._t);
    toast._t = setTimeout(() => toastEl.classList.remove('show'), 2100);
  }

  function updateDock() {
    const items = Array.from(sidebar.querySelectorAll('.nav-row'));
    const tip = $('#rfDockTip');
    if (!state.collapsed || !dockPointer) {
      items.forEach((el) => {
        el.style.setProperty('--dock-scale', '1');
        el.style.setProperty('--dock-shift', '0px');
      });
      if (tip) tip.classList.remove('show');
      return;
    }
    let hotItem = null;
    let maxScale = 1;
    items.forEach((el) => {
      const r = el.getBoundingClientRect();
      const cy = r.top + r.height / 2;
      const dist = Math.abs(dockPointer.y - cy);
      if (dist >= dockRadius) {
        el.style.setProperty('--dock-scale', '1');
        el.style.setProperty('--dock-shift', '0px');
      } else {
        const t = 1 - dist / dockRadius;
        const smooth = t * t * (3 - 2 * t);
        const scale = 1 + dockGain * smooth;
        const shift = (cy - dockPointer.y) * 0.08 * smooth;
        el.style.setProperty('--dock-scale', scale.toFixed(3));
        el.style.setProperty('--dock-shift', `${shift.toFixed(2)}px`);
        if (scale > maxScale) { maxScale = scale; hotItem = { el, r }; }
      }
    });
    if (tip && hotItem) {
      tip.textContent = hotItem.el.dataset.label || '';
      tip.style.left = `${hotItem.r.right + 12}px`;
      tip.style.top = `${hotItem.r.top + hotItem.r.height / 2 - 14}px`;
      tip.classList.add('show');
    }
  }

  function renderSidebar() {
    sidebar.innerHTML = `
      <button type="button" class="rail-toggle" id="rfToggleRail" aria-label="Toggle sidebar">${svgIcon(state.collapsed ? 'right' : 'left', 14)}</button>
      <div class="nav" data-eu-id="eu_L3_rf_sidebar_dock">
        <div class="brand-row">
          <div class="brand-prism" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><polygon points="12,3 21,19 3,19" stroke="#ff6b3d" stroke-width="2" fill="rgba(255,107,61,0.28)"/></svg>
          </div>
          <span class="brand-name">Refract</span>
          <span class="brand-pill">CRM</span>
        </div>
        <div class="nav-groups" data-eu-id="eu_L4_rf_nav_groups">
          <div class="nav-dock-field" data-eu-id="eu_L4_rf_dock_proximity">
            ${NAV_GROUPS.map(([sec, rows]) => `
              <div>
                <p class="nav-sec-title">${sec}</p>
                <div class="nav-list">
                  ${rows.map(([id, label, ico, badge]) => `
                    <button type="button" class="nav-row" data-route="${id}" data-label="${label}" aria-current="${state.route === id ? 'page' : 'false'}">
                      <span class="nav-ico">${svgIcon(ico, 17)}</span>
                      <span class="nav-lbl">${label}</span>
                      ${badge ? `<span class="nav-badge ${badge === 3 || badge === 7 ? 'hot' : ''}">${badge}</span>` : ''}
                    </button>
                  `).join('')}
                </div>
              </div>
            `).join('')}
          </div>
        </div>
        <div class="sidebar-foot">
          <div class="quota-card" data-eu-id="eu_L3_rf_quota_profile">
            <div class="quota-head"><span>Q4 quota</span><span>92%</span></div>
            <div class="quota-track"><div class="quota-fill"></div></div>
            <p class="quota-sub">$386k of $420k · $33.6k to go</p>
          </div>
          <button type="button" class="profile-row" id="rfProfileBtn">
            <span class="avatar-pill">LM</span>
            <span class="profile-meta"><strong>Leah Moreno</strong><small>Head of Sales</small></span>
          </button>
        </div>
      </div>
      <div id="rfDockTip" class="dock-tooltip"></div>
    `;

    $('#rfToggleRail').addEventListener('click', () => {
      state.collapsed = !state.collapsed;
      shell.classList.toggle('collapsed', state.collapsed);
      renderSidebar();
      if (state.collapsed) updateDock();
    });

    const field = $('.nav-dock-field', sidebar);
    field.addEventListener('pointermove', (e) => {
      if (!state.collapsed) return;
      dockPointer = { x: e.clientX, y: e.clientY };
      updateDock();
    });
    field.addEventListener('pointerleave', () => {
      dockPointer = null;
      updateDock();
    });

    sidebar.querySelectorAll('.nav-row').forEach((btn) => {
      btn.addEventListener('click', () => navigate(btn.dataset.route));
    });
  }

  function buildSpark(points, stroke) {
    const max = Math.max(...points), min = Math.min(...points), span = Math.max(1, max - min);
    const d = points.map((v, i) => {
      const x = (i / (points.length - 1)) * 72 + 2;
      const y = 28 - ((v - min) / span) * 22;
      return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(' ');
    return `<svg class="spark-svg" viewBox="0 0 76 32" aria-hidden="true"><path d="${d}" fill="none" stroke="${stroke}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  }

  function buildAreaSvg(data) {
    const W = 600, H = 190, padL = 38, padR = 14, padT = 16, padB = 26;
    const all = [...data.rev, ...data.tgt];
    const max = Math.max(...all) * 1.12;
    const min = Math.min(...all) * 0.85;
    const span = Math.max(1, max - min);
    const pts = (arr) => arr.map((v, i) => {
      const x = padL + (i / Math.max(1, arr.length - 1)) * (W - padL - padR);
      const y = padT + (1 - (v - min) / span) * (H - padT - padB);
      return [x, y];
    });
    const revPts = pts(data.rev);
    const tgtPts = pts(data.tgt);
    const toPath = (p) => p.map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
    const areaPath = `${toPath(revPts)} L${revPts[revPts.length - 1][0].toFixed(1)},${H - padB} L${revPts[0][0].toFixed(1)},${H - padB} Z`;
    return `
      <svg class="area-svg" viewBox="0 0 ${W} ${H}" aria-label="Revenue trend">
        <defs>
          <linearGradient id="rfAreaFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#ff6b3d" stop-opacity="0.46"/>
            <stop offset="100%" stop-color="#ff6b3d" stop-opacity="0.02"/>
          </linearGradient>
        </defs>
        ${[0, 0.33, 0.66, 1].map((r) => {
          const y = padT + r * (H - padT - padB);
          return `<line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" stroke="rgba(255,255,255,0.12)" stroke-dasharray="3 4"/>`;
        }).join('')}
        <path d="${areaPath}" fill="url(#rfAreaFill)"/>
        <path d="${toPath(tgtPts)}" fill="none" stroke="rgba(255,255,255,0.52)" stroke-width="1.6" stroke-dasharray="4 4"/>
        <path d="${toPath(revPts)}" fill="none" stroke="#ff6b3d" stroke-width="2.6" stroke-linecap="round"/>
        ${revPts.map(([x, y], idx) => `
          <circle cx="${x}" cy="${y}" r="3.5" fill="#ff6b3d" stroke="#fff" stroke-width="1.2"/>
          <text x="${x}" y="${H - 6}" text-anchor="middle" fill="rgba(247,243,239,0.65)" font-size="11">${esc(data.labels[idx])}</text>
        `).join('')}
      </svg>
    `;
  }

  function exportCsv() {
    const s = REVENUE_SERIES[state.activeRange];
    const rows = ['Period,Revenue,Target', ...s.labels.map((l, i) => `${l},${s.rev[i]},${s.tgt[i]}`)];
    const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `refract-revenue-${state.activeRange.toLowerCase()}.csv`;
    a.click();
    toast(`Exported ${a.download}`);
  }

  function openDialog(mode, triggerEl) {
    state.lastFocus = triggerEl || document.activeElement;
    if (mode === 'cmd') {
      dialog.innerHTML = `
        <div class="dlg-head"><h2 id="rf-dialog-title">Command & Quick Jump</h2><button type="button" class="btn-ghost" id="rfDlgClose">Esc</button></div>
        <div class="dlg-body">
          <input id="rfCmdInput" type="search" placeholder="Jump to Overview, Pipeline, 12M Revenue or Call Desk…">
          <div class="cmd-list">
            <button type="button" data-cmd="overview"><span>Go to Overview Dashboard</span><small>⌘1</small></button>
            <button type="button" data-cmd="pipeline"><span>Open Pipeline Kanban</span><small>⌘2</small></button>
            <button type="button" data-cmd="range12"><span>Switch Revenue to 12M</span><small>Filter</small></button>
            <button type="button" data-cmd="csv"><span>Download Active Revenue CSV</span><small>Export</small></button>
          </div>
        </div>
      `;
      dialog.showModal();
      $('#rfCmdInput', dialog).focus();
      dialog.querySelectorAll('[data-cmd]').forEach((b) => b.addEventListener('click', () => {
        const c = b.dataset.cmd;
        dialog.close();
        if (c === 'overview' || c === 'pipeline') navigate(c);
        else if (c === 'range12') { state.activeRange = '12M'; renderMain(); }
        else if (c === 'csv') exportCsv();
      }));
    } else {
      dialog.innerHTML = `
        <div class="dlg-head"><h2 id="rf-dialog-title">Create New Deal</h2><button type="button" class="btn-ghost" id="rfDlgClose">Close</button></div>
        <form class="dlg-body" id="rfDealForm">
          <label>Account & Opportunity<input name="deal" required placeholder="e.g. Harbor Logistics · 24 Hubs"></label>
          <label>Amount (USD)<input name="amount" required placeholder="$92,000"></label>
          <button type="submit" class="btn-coral">Add to Hot Deals</button>
        </form>
      `;
      dialog.showModal();
      const form = $('#rfDealForm', dialog);
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const fd = new FormData(form);
        DEALS.unshift({ name: String(fd.get('deal')), stage: 'Qualified', amount: String(fd.get('amount')), prob: '65%' });
        dialog.close();
        renderMain();
        toast('New deal added to CRM pipeline');
      });
    }
    $('#rfDlgClose', dialog).addEventListener('click', () => dialog.close());
  }

  dialog.addEventListener('close', () => {
    if (state.lastFocus && typeof state.lastFocus.focus === 'function') state.lastFocus.focus();
  });

  function renderMain() {
    viewport.dataset.page = state.route;
    const revData = REVENUE_SERIES[state.activeRange];
    const contact = CONTACTS[state.contactIdx];
    const doneCnt = state.tasks.filter((t) => t.done).length;
    const donePct = Math.round((doneCnt / state.tasks.length) * 100);

    if (state.route === 'pipeline') {
      const stages = ['Qualified', 'Proposal', 'Negotiation'];
      viewport.innerHTML = `
        <header class="liquid-glass rf-topbar" data-eu-id="eu_L3_rf_header_search">
          <div class="rf-greet"><h1>Sales Pipeline</h1><p>Active opportunity stages · ${DEALS.length} open deals</p></div>
          <div class="rf-top-tools">
            <button type="button" class="cmd-btn" id="rfCmdTrigger" data-eu-id="eu_L4_rf_cmd_trigger"><span>${svgIcon('search', 14)} Search or jump to…</span><kbd>⌘K</kbd></button>
            <button type="button" class="btn-ghost" id="rfBackOverview">Back to Overview</button>
            <button type="button" class="btn-coral" id="rfNewDealBtn">+ New deal</button>
          </div>
        </header>
        <section class="pipeline-board" data-eu-id="eu_L3_rf_hot_deals">
          ${stages.map((st) => `
            <div class="liquid-glass pipe-col">
              <h3><span>${st}</span><span class="delta-pill">${DEALS.filter((d) => d.stage === st).length}</span></h3>
              ${DEALS.filter((d) => d.stage === st).map((d) => `
                <article class="pipe-deal"><strong>${esc(d.name)}</strong><span>${esc(d.amount)} · Win prob ${esc(d.prob)}</span></article>
              `).join('')}
            </div>
          `).join('')}
        </section>
      `;
      $('#rfBackOverview').addEventListener('click', () => navigate('overview'));
    } else {
      viewport.innerHTML = `
        <header class="liquid-glass rf-topbar" data-eu-id="eu_L3_rf_header_search">
          <div class="rf-greet">
            <h1>Good morning, Leah</h1>
            <p>Monday, November 23 · Refract Liquid-Glass CRM</p>
          </div>
          <div class="rf-top-tools">
            <button type="button" class="cmd-btn" id="rfCmdTrigger" data-eu-id="eu_L4_rf_cmd_trigger"><span>${svgIcon('search', 14)} Search or jump to…</span><kbd>⌘K</kbd></button>
            <button type="button" class="btn-coral" id="rfNewDealBtn">+ New deal</button>
          </div>
        </header>

        <section class="rf-kpis" data-eu-id="eu_L3_rf_kpi_array" aria-label="Primary KPIs">
          <article class="liquid-glass kpi-card">
            <div class="kpi-head"><span>Won this month</span><span class="delta-pill">+12.2%</span></div>
            <div class="kpi-body"><strong class="kpi-val">$229k</strong>${buildSpark([18, 21, 19, 25, 29, 27, 34], '#ff6b3d')}</div>
          </article>
          <article class="liquid-glass kpi-card">
            <div class="kpi-head"><span>Open pipeline</span><span class="delta-pill">+8.2%</span></div>
            <div class="kpi-body"><strong class="kpi-val">$846k</strong>${buildSpark([42, 46, 44, 51, 56, 58, 63], '#38bdf8')}</div>
          </article>
          <article class="liquid-glass kpi-card">
            <div class="kpi-head"><span>Win rate</span><span class="delta-pill">+3.3%</span></div>
            <div class="win-ring-wrap">
              <svg class="win-ring" viewBox="0 0 68 68">
                <circle cx="34" cy="34" r="26" fill="none" stroke="rgba(255,255,255,0.14)" stroke-width="7"/>
                <circle cx="34" cy="34" r="26" fill="none" stroke="#ff6b3d" stroke-width="7" stroke-dasharray="${(36 / 100) * 163.36} 163.36" stroke-linecap="round" transform="rotate(-90 34 34)"/>
                <text x="34" y="39" text-anchor="middle">36%</text>
              </svg>
              <p class="win-note"><strong>4</strong> deals won this quarter, <strong>18</strong> still open.</p>
            </div>
          </article>
          <article class="liquid-glass kpi-card">
            <div class="kpi-head"><span>Leads this week</span><span class="delta-pill">+27.3%</span></div>
            <div class="kpi-body"><strong class="kpi-val">14</strong>${buildSpark([4, 9, 6, 11, 8, 12, 14], '#c4b5fd')}</div>
          </article>
        </section>

        <section class="rf-mid-grid">
          <article class="liquid-glass rev-card" data-eu-id="eu_L3_rf_revenue_chart">
            <div class="card-head">
              <div><h2>Revenue</h2><p>Closed-won against target</p></div>
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;" data-eu-id="eu_L4_rf_rev_filter">
                <div class="seg-pills" role="group" aria-label="Revenue range">
                  ${['7D', '30D', '12M'].map((r) => `<button type="button" data-range="${r}" aria-pressed="${state.activeRange === r}">${r}</button>`).join('')}
                </div>
                <button type="button" class="btn-ghost" id="rfCsvBtn">${svgIcon('download', 14)} CSV</button>
              </div>
            </div>
            <div class="rev-figure">
              <strong>${revData.total}</strong>
              <span class="delta-pill">${revData.delta}</span>
              <span>vs target ${revData.target}</span>
            </div>
            <div class="area-chart-box">${buildAreaSvg(revData)}</div>
          </article>

          <article class="liquid-glass dialer-card" data-eu-id="eu_L3_rf_call_desk">
            <div class="contact-top">
              <div class="contact-avatar">${esc(contact.initials)}</div>
              <div>
                <h2>${esc(contact.name)}</h2>
                <p style="font-size:12px;color:var(--rf-muted);">${esc(contact.title)}</p>
              </div>
            </div>
            <p class="contact-quote">${esc(contact.quote)}</p>
            <div class="deal-pill"><i></i><span>${esc(contact.deal)}</span></div>
            <p style="font-size:11px;letter-spacing:0.06em;color:var(--rf-muted);">UP NEXT · 11:00 · ${state.contactIdx + 1} OF ${CONTACTS.length}</p>
            <div class="dialer-ctrl" data-eu-id="eu_L4_rf_dialer_ctrl">
              <div class="dialer-meta">
                <span>${state.callsDone} of 5 done</span>
                <span>${esc(contact.phone)}</span>
              </div>
              <div class="dialer-btns">
                <button type="button" class="round-btn" id="rfPrevContact" aria-label="Previous contact">${svgIcon('prev', 16)}</button>
                <button type="button" class="call-main-btn ${state.inCall ? 'calling' : ''}" id="rfCallBtn" aria-label="Toggle call">${svgIcon('phone', 20)}</button>
                <button type="button" class="round-btn" id="rfNextContact" aria-label="Next contact">${svgIcon('next', 16)}</button>
              </div>
            </div>
          </article>
        </section>

        <section class="rf-bottom-grid">
          <article class="liquid-glass bottom-card" data-eu-id="eu_L3_rf_hot_deals">
            <div class="card-head">
              <div><h2>Hot deals</h2><p>Most likely to close soon</p></div>
              <button type="button" class="btn-ghost" id="rfJumpPipeline" data-eu-id="eu_L4_rf_pipeline_route">Pipeline &rsaquo;</button>
            </div>
            ${DEALS.slice(0, 3).map((d) => `
              <div class="deal-item">
                <div><strong>${esc(d.name)}</strong><p style="font-size:11.5px;color:var(--rf-muted);">${esc(d.stage)} · ${esc(d.prob)}</p></div>
                <strong>${esc(d.amount)}</strong>
              </div>
            `).join('')}
          </article>

          <article class="liquid-glass bottom-card" data-eu-id="eu_L3_rf_today_tasks">
            <div class="card-head">
              <div><h2>Today</h2><p>${doneCnt} of ${state.tasks.length} done</p></div>
              <svg width="36" height="36" viewBox="0 0 36 36" aria-hidden="true">
                <circle cx="18" cy="18" r="14" fill="none" stroke="rgba(255,255,255,0.14)" stroke-width="4"/>
                <circle cx="18" cy="18" r="14" fill="none" stroke="#ff6b3d" stroke-width="4" stroke-dasharray="${(donePct / 100) * 87.96} 87.96" stroke-linecap="round" transform="rotate(-90 18 18)"/>
              </svg>
            </div>
            ${state.tasks.slice(0, 3).map((t) => `
              <div class="task-item ${t.done ? 'done' : ''}">
                <label><input type="checkbox" data-task="${t.id}" ${t.done ? 'checked' : ''}><span>${esc(t.label)}</span></label>
              </div>
            `).join('')}
          </article>
        </section>
      `;

      viewport.querySelectorAll('[data-range]').forEach((b) => b.addEventListener('click', () => {
        state.activeRange = b.dataset.range;
        renderMain();
      }));
      $('#rfCsvBtn').addEventListener('click', exportCsv);
      $('#rfPrevContact').addEventListener('click', () => { state.contactIdx = (state.contactIdx + CONTACTS.length - 1) % CONTACTS.length; renderMain(); });
      $('#rfNextContact').addEventListener('click', () => { state.contactIdx = (state.contactIdx + 1) % CONTACTS.length; renderMain(); });
      $('#rfCallBtn').addEventListener('click', () => {
        state.inCall = !state.inCall;
        if (!state.inCall) state.callsDone = Math.min(5, state.callsDone + 1);
        renderMain();
        toast(state.inCall ? `Dialing ${contact.name}…` : 'Call logged');
      });
      $('#rfJumpPipeline').addEventListener('click', () => navigate('pipeline'));
      viewport.querySelectorAll('[data-task]').forEach((chk) => chk.addEventListener('change', () => {
        const item = state.tasks.find((x) => x.id === chk.dataset.task);
        if (item) item.done = chk.checked;
        renderMain();
      }));
    }

    $('#rfCmdTrigger').addEventListener('click', (e) => openDialog('cmd', e.currentTarget));
    $('#rfNewDealBtn').addEventListener('click', (e) => openDialog('deal', e.currentTarget));
  }

  function navigate(route) {
    state.scrollByRoute[state.route] = viewport.scrollTop;
    state.route = route;
    renderSidebar();
    renderMain();
    viewport.scrollTop = state.scrollByRoute[route] || 0;
  }

  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openDialog('cmd', $('#rfCmdTrigger'));
    }
  });

  function clearHighlight() {
    document.querySelectorAll('[data-kaiwu-active]').forEach((el) => el.removeAttribute('data-kaiwu-active'));
  }

  function highlightEu(rawId, fallbackId, action) {
    clearHighlight();
    if (!rawId) return;
    if (rawId === 'eu_L3_rf_cmd_dialog' || rawId === 'eu_L4_rf_focus_trap') {
      if (!dialog.open) openDialog('cmd', $('#rfCmdTrigger'));
      dialog.setAttribute('data-kaiwu-active', 'true');
      return;
    }
    if (dialog.open) dialog.close();
    if (rawId === 'eu_L3_rf_sidebar_dock' || rawId === 'eu_L4_rf_dock_proximity' || action === 'proximity_demo') {
      if (!state.collapsed) {
        state.collapsed = true;
        shell.classList.add('collapsed');
        renderSidebar();
      }
      requestAnimationFrame(() => {
        const firstRow = $('.nav-row[data-route="overview"]', sidebar);
        if (firstRow) {
          const r = firstRow.getBoundingClientRect();
          dockPointer = { x: (r.left + r.right) / 2, y: (r.top + r.bottom) / 2 };
          updateDock();
        }
      });
    } else if (state.collapsed && rawId !== 'eu_L0_rf_workspace') {
      state.collapsed = false;
      shell.classList.remove('collapsed');
      renderSidebar();
    }
    const target = $(`[data-eu-id="${rawId}"]`) || (fallbackId && $(`[data-eu-id="${fallbackId}"]`)) || shell;
    if (viewport.contains(target) && rawId !== 'eu_L1_rf_stage') {
      target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    target.setAttribute('data-kaiwu-active', 'true');
  }

  window.addEventListener('message', (ev) => {
    const msg = ev.data;
    if (!msg || typeof msg !== 'object') return;
    if (msg.type === 'KAIWU_HIGHLIGHT_EU') {
      highlightEu(msg.eu_id, msg.fallback_eu_id, msg.action);
    } else if (msg.type === 'KAIWU_PREVIEW_ACTION') {
      if (dialog.open) dialog.close();
      if (msg.action === 'proximity_demo') {
        state.collapsed = true;
        shell.classList.add('collapsed');
        navigate('overview');
        requestAnimationFrame(() => {
          const row = $('.nav-row[data-route="overview"]', sidebar);
          if (row) {
            const r = row.getBoundingClientRect();
            dockPointer = { x: (r.left + r.right) / 2, y: (r.top + r.bottom) / 2 };
            updateDock();
          }
        });
      } else if (msg.action === 'analytics') {
        state.collapsed = false;
        shell.classList.remove('collapsed');
        navigate('pipeline');
      } else {
        state.collapsed = false;
        shell.classList.remove('collapsed');
        navigate('overview');
      }
    }
  });

  document.addEventListener('click', (ev) => {
    if (window.parent === window) return;
    const hit = ev.target.closest('[data-eu-id]');
    if (!hit) return;
    window.parent.postMessage({ type: 'KAIWU_SELECT_EU', eu_id: hit.getAttribute('data-eu-id'), case_id: 'refract_crm_web' }, '*');
  }, true);

  renderSidebar();
  renderMain();
})();
