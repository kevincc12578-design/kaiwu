(() => {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const viewport = $('#viewport');
  const railDock = $('#railDock');
  const mainStage = $('.main-glass') || $('#mainStage');
  const dialog = $('#fmDialog');
  const morphSheet = $('#fmMorphSheet');
  const dockRadius = 96;
  const dockGain = 0.28;

  const RANGE_DATA = {
    '1D': { val: '$148,920.40', delta: '+1.42% (1D)', pts: [144, 145, 144.8, 146.2, 147.1, 148.0, 148.9], labels: ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00', 'Now'] },
    '1W': { val: '$148,920.40', delta: '+3.95% (1W)', pts: [141, 142.5, 144, 143.2, 146, 147.4, 148.9], labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
    '1M': { val: '$148,920.40', delta: '+6.84% (1M)', pts: [134, 137, 136, 141, 144, 146, 148.9], labels: ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'Now'] },
    '1Y': { val: '$148,920.40', delta: '+38.2% (1Y)', pts: [104, 112, 118, 126, 132, 141, 148.9], labels: ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov', 'Dec'] },
  };

  const TXS = [
    { id: 'tx-1', cat: 'Send', title: 'vitalik.eth', amount: '-1.20 ETH', time: '2m ago' },
    { id: 'tx-2', cat: 'Swap', title: 'USDC → ETH', amount: '+0.85 ETH', time: '18m ago' },
    { id: 'tx-3', cat: 'Yield', title: 'Base Staking Pool', amount: '+48.40 USDC', time: '1h ago' },
    { id: 'tx-4', cat: 'Send', title: 'studio.ens', amount: '-250.00 USDC', time: '3h ago' },
  ];

  const state = {
    range: '1M',
    trayMode: 'send',
    activeFilter: 'all',
    txs: [...TXS],
    scrollByRoute: {},
    lastTrigger: null,
  };

  function updateDock(pointerY) {
    const btns = Array.from(railDock.querySelectorAll('.rail-btn[data-tray]'));
    if (pointerY === null) {
      btns.forEach((b) => {
        b.style.setProperty('--dock-scale', '1');
        b.style.setProperty('--dock-shift', '0px');
      });
      return;
    }
    btns.forEach((b) => {
      const r = b.getBoundingClientRect();
      const d = Math.abs(pointerY - (r.top + r.bottom) / 2);
      const t = Math.max(0, 1 - d / dockRadius);
      const ease = t * t * (3 - 2 * t);
      b.style.setProperty('--dock-scale', (1 + ease * dockGain).toFixed(3));
      b.style.setProperty('--dock-shift', `${(ease * 6).toFixed(1)}px`);
    });
  }

  function renderCharts() {
    const d = RANGE_DATA[state.range];
    $('#fmBalValue').textContent = d.val;
    $('#fmBalDelta').textContent = d.delta;

    const W = 540;
    const H = 152;
    const min = Math.min(...d.pts) - 2;
    const max = Math.max(...d.pts) + 2;
    const coords = d.pts.map((v, i) => [16 + (i / (d.pts.length - 1)) * (W - 32), H - 26 - ((v - min) / (max - min)) * (H - 42)]);
    let pathD = `M${coords[0][0].toFixed(1)},${coords[0][1].toFixed(1)}`;
    for (let i = 0; i < coords.length - 1; i += 1) {
      const [x1, y1] = coords[i];
      const [x2, y2] = coords[i + 1];
      const cx = (x1 + x2) / 2;
      pathD += ` C${cx.toFixed(1)},${y1.toFixed(1)} ${cx.toFixed(1)},${y2.toFixed(1)} ${x2.toFixed(1)},${y2.toFixed(1)}`;
    }
    const areaD = `${pathD} L${coords[coords.length - 1][0].toFixed(1)},${H - 24} L${coords[0][0].toFixed(1)},${H - 24} Z`;
    const last = coords[coords.length - 1];
    $('#fmAreaSvg').innerHTML = `
      <svg viewBox="0 0 ${W} ${H}" aria-label="Portfolio Valuation Curve">
        <defs><linearGradient id="fmAreaG" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0ea5e9" stop-opacity="0.28"/><stop offset="100%" stop-color="#0ea5e9" stop-opacity="0.01"/></linearGradient></defs>
        <line x1="12" y1="34" x2="${W - 12}" y2="34" stroke="#e5e7eb" stroke-dasharray="4 4"/>
        <line x1="12" y1="78" x2="${W - 12}" y2="78" stroke="#e5e7eb" stroke-dasharray="4 4"/>
        <path d="${areaD}" fill="url(#fmAreaG)"/>
        <path d="${pathD}" fill="none" stroke="#0ea5e9" stroke-width="3" stroke-linecap="round"/>
        <circle cx="${last[0].toFixed(1)}" cy="${last[1].toFixed(1)}" r="5" fill="#fff" stroke="#0ea5e9" stroke-width="2.5"/>
        ${d.labels.map((lb, i) => `<text x="${(16 + (i / (d.labels.length - 1)) * (W - 32)).toFixed(1)}" y="${H - 6}" text-anchor="middle" fill="#6b7280" font-size="10">${esc(lb)}</text>`).join('')}
      </svg>
    `;

    const r = 36;
    const c = 2 * Math.PI * r;
    $('#fmDonutSvg').innerHTML = `
      <svg viewBox="0 0 98 98" aria-label="Asset Allocation Ring" style="transform:rotate(-90deg);">
        <circle cx="49" cy="49" r="${r}" fill="none" stroke="#f2f4f7" stroke-width="12"/>
        <circle cx="49" cy="49" r="${r}" fill="none" stroke="#0ea5e9" stroke-width="12" stroke-dasharray="${(c * 0.50).toFixed(1)} ${c.toFixed(1)}" stroke-linecap="round"/>
        <circle cx="49" cy="49" r="${r}" fill="none" stroke="#10b981" stroke-width="12" stroke-dasharray="${(c * 0.26).toFixed(1)} ${c.toFixed(1)}" stroke-dashoffset="${(-c * 0.52).toFixed(1)}" stroke-linecap="round"/>
        <circle cx="49" cy="49" r="${r}" fill="none" stroke="#8b5cf6" stroke-width="12" stroke-dasharray="${(c * 0.18).toFixed(1)} ${c.toFixed(1)}" stroke-dashoffset="${(-c * 0.80).toFixed(1)}" stroke-linecap="round"/>
      </svg>
    `;

    const gasPts = [[10, 72], [54, 62], [98, 66], [142, 46], [186, 52], [230, 34], [270, 28]];
    const gasPoly = gasPts.map(([x, y]) => `${x},${y}`).join(' ');
    $('#fmGasSvg').innerHTML = `
      <svg viewBox="0 0 280 96" aria-label="Base L2 Live Gas Fee Chart">
        <polyline points="${gasPoly}" fill="none" stroke="#10b981" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
        ${gasPts.map(([x, y], idx) => `<circle cx="${x}" cy="${y}" r="${idx === gasPts.length - 1 ? 4 : 2.5}" fill="#10b981"/>`).join('')}
        <text x="10" y="90" fill="#6b7280" font-size="9.5">-30m</text>
        <text x="142" y="90" text-anchor="middle" fill="#6b7280" font-size="9.5">-15m</text>
        <text x="270" y="90" text-anchor="end" fill="#6b7280" font-size="9.5">Live 0.08</text>
      </svg>
    `;
  }

  function renderTray() {
    const m = state.trayMode;
    $('#fmTrayBadge').textContent = m.toUpperCase();
    morphSheet.setAttribute('data-mode', m);
    document.querySelectorAll('.fm-tray-pill[data-tray], .rail-btn[data-tray]').forEach((b) => {
      b.classList.toggle('is-active', b.dataset.tray === m);
    });
    const host = $('#fmTrayDynamic');
    if (m === 'send') {
      host.innerHTML = `
        <span class="fm-mono">INSTANT TRANSFER · ZERO SLIPPAGE</span>
        <input id="fmSendAddr" class="fm-input-box" type="text" value="alice.eth">
        <input id="fmSendAmt" class="fm-input-box" type="text" value="0.45 ETH ($1,404)">
        <button type="button" id="fmTraySubmitBtn" class="fm-btn fm-btn-sky">Slide to Send</button>
      `;
    } else if (m === 'swap') {
      host.innerHTML = `
        <span class="fm-mono">FLUID SWAP ROUTE · BASE POOL</span>
        <input class="fm-input-box" type="text" value="Pay: 2,500 USDC" readonly>
        <input class="fm-input-box" type="text" value="Receive: 0.801 ETH (Best Rate)" readonly>
        <div class="fm-mono" style="color:#0284c7;">Price Impact: &lt;0.01% · Gas $0.02</div>
        <button type="button" id="fmTraySubmitBtn" class="fm-btn fm-btn-sky">Confirm Fluid Swap</button>
      `;
    } else if (m === 'speed') {
      host.innerHTML = `
        <span class="fm-mono" style="color:#e11d48;">PENDING TX · #0x8f2...c1</span>
        <strong style="font-size:15px;">Accelerate to Instant Block</strong>
        <span class="fm-mono">Priority Fee: 0.08 &rarr; 0.24 Gwei</span>
        <button type="button" id="fmTraySubmitBtn" class="fm-btn fm-btn-sky" style="background:#f43f5e;">Speed Up Transaction</button>
      `;
    } else {
      host.innerHTML = `
        <span class="fm-mono" style="color:#059669;">USDC NATIVE YIELD · 4.85% APY</span>
        <input class="fm-input-box" type="text" value="Stake: 5,000 USDC" readonly>
        <div class="fm-mono">Est. Yearly Return: +$242.50 USDC</div>
        <button type="button" id="fmTraySubmitBtn" class="fm-btn fm-btn-sky" style="background:#10b981;">Activate Auto-Yield</button>
      `;
    }
    $('#fmTraySubmitBtn')?.addEventListener('click', () => {
      const mapCat = { send: 'Send', swap: 'Swap', speed: 'Send', yield: 'Yield' };
      state.txs.unshift({
        id: `tx-${Date.now()}`,
        cat: mapCat[state.trayMode],
        title: state.trayMode === 'send' ? ($('#fmSendAddr')?.value || 'alice.eth') : `${state.trayMode.toUpperCase()} Action`,
        amount: state.trayMode === 'yield' ? '+4.85% APY' : 'Confirmed',
        time: 'Just now',
      });
      renderTxs();
      const btn = $('#fmTraySubmitBtn');
      if (btn) btn.textContent = '✓ Anchored in Ledger';
    });
  }

  function renderTxs() {
    const activeRange = state.activeFilter;
    const rows = state.txs.filter((t) => activeRange === 'all' || t.cat === activeRange);
    $('#fmTxGrid').innerHTML = rows.slice(0, 4).map((t) => `
      <article class="fm-tx-card">
        <div class="fm-tx-top"><span>${esc(t.cat)}</span><span>${esc(t.time)}</span></div>
        <strong style="font-size:14px;">${esc(t.title)}</strong>
        <span class="fm-mono" style="color:#0ea5e9;font-weight:700;">${esc(t.amount)}</span>
      </article>
    `).join('');
  }

  function navigate(range) {
    state.scrollByRoute[state.range] = mainStage.scrollTop;
    state.range = RANGE_DATA[range] ? range : '1M';
    viewport.dataset.page = state.range;
    document.querySelectorAll('.fm-tab[data-route]').forEach((t) => t.classList.toggle('is-active', t.dataset.route === state.range));
    renderCharts();
    mainStage.scrollTop = state.scrollByRoute[state.range] || 0;
  }

  function exportCsv() {
    const activeRange = state.activeFilter;
    const rows = state.txs.filter((t) => activeRange === 'all' || t.cat === activeRange);
    const lines = ['range,category,entity,amount,time'];
    rows.forEach((t) => lines.push(`${state.range},${t.cat},"${t.title}","${t.amount}",${t.time}`));
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `family-receipts-${state.range}-${activeRange}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  railDock.addEventListener('pointermove', (e) => updateDock(e.clientY));
  railDock.addEventListener('pointerleave', () => updateDock(null));
  document.querySelectorAll('.fm-tab[data-route]').forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));
  document.querySelectorAll('[data-tray]').forEach((b) => b.addEventListener('click', () => {
    state.trayMode = b.dataset.tray;
    renderTray();
  }));
  document.querySelectorAll('.fm-flt[data-flt]').forEach((b) => b.addEventListener('click', () => {
    state.activeFilter = b.dataset.flt;
    document.querySelectorAll('.fm-flt[data-flt]').forEach((x) => x.classList.toggle('is-active', x === b));
    renderTxs();
  }));
  $('#exportCsvBtn').addEventListener('click', exportCsv);

  $('#openVaultBtn').addEventListener('click', (e) => { state.lastTrigger = e.currentTarget; dialog.showModal(); });
  $('#closeVaultBtn').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => { if (state.lastTrigger && typeof state.lastTrigger.focus === 'function') state.lastTrigger.focus(); });

  window.addEventListener('message', (ev) => {
    const msg = ev.data || {};
    if (msg.type === 'KAIWU_HIGHLIGHT_EU') {
      document.querySelectorAll('[data-kaiwu-active]').forEach((n) => n.removeAttribute('data-kaiwu-active'));
      if (msg.eu_id === 'eu_L3_fm_vault_dialog') {
        if (!dialog.open) { state.lastTrigger = $('#openVaultBtn'); dialog.showModal(); }
        dialog.setAttribute('data-kaiwu-active', 'true');
        return;
      }
      if (dialog.open) dialog.close();
      if (msg.eu_id === 'eu_L3_fm_rail_dock' || msg.eu_id === 'eu_L4_fm_rail_proximity' || msg.action === 'proximity_demo') {
        const btn = railDock.querySelector('.rail-btn');
        if (btn) updateDock(btn.getBoundingClientRect().top + 14);
      } else {
        updateDock(null);
      }
      const target = document.querySelector(`[data-eu-id="${msg.eu_id}"]`) || (msg.fallback_eu_id && document.querySelector(`[data-eu-id="${msg.fallback_eu_id}"]`));
      if (target) { target.setAttribute('data-kaiwu-active', 'true'); target.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
    } else if (msg.type === 'KAIWU_PREVIEW_ACTION') {
      if (dialog.open) dialog.close();
      if (msg.action === 'proximity_demo') {
        const btn = railDock.querySelector('.rail-btn');
        if (btn) updateDock(btn.getBoundingClientRect().top + 14);
      } else {
        updateDock(null);
        navigate('1M');
      }
    }
  });

  document.addEventListener('click', (ev) => {
    if (window.parent === window) return;
    const hit = ev.target.closest('[data-eu-id]');
    if (hit) window.parent.postMessage({ type: 'KAIWU_SELECT_EU', eu_id: hit.getAttribute('data-eu-id'), case_id: 'family_fluid_web' }, '*');
  }, true);

  renderCharts();
  renderTray();
  renderTxs();
})();
