(() => {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const viewport = $('#viewport');
  const railDock = $('#railDock');
  const mainStage = $('.main-glass') || $('#mainStage');
  const body = document.body;
  const dialog = $('#psDialog');
  const dockRadius = 96;
  const dockGain = 0.24;
  let lastTrigger = null;

  const CHANNELS = [
    { id: 'ch-malibu', cat: 'Synthwave', title: "Malibu Sunset '94", bpm: '112 BPM', listeners: '5,420' },
    { id: 'ch-yacht', cat: 'Yacht', title: 'Sausalito Yacht Club', bpm: '104 BPM', listeners: '4,180' },
    { id: 'ch-tokyo', cat: 'Lo-Fi', title: 'Shibuya VHS Loops', bpm: '88 BPM', listeners: '2,940' },
    { id: 'ch-hangover', cat: 'Synthwave', title: 'Poolside Hangover', bpm: '118 BPM', listeners: '2,280' },
  ];

  const state = {
    theme: 'peach',
    frontWin: 'fm',
    playing: true,
    trackIdx: 0,
    activeFilter: 'all',
    scrollByRoute: {},
  };

  function updateDock(pointerY) {
    const btns = Array.from(railDock.querySelectorAll('.ps-desk-ico'));
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
      b.style.setProperty('--dock-shift', `${(ease * 5).toFixed(1)}px`);
    });
  }

  function renderEq() {
    const heights = state.playing ? [24, 42, 58, 36, 64, 52, 32, 68, 54, 40, 60, 44, 30, 56, 38, 26] : [10, 14, 12, 16, 12, 10, 14, 12, 10, 14, 12, 10, 12, 10, 12, 10];
    const bars = heights.map((h, i) => {
      const x = 10 + i * 21;
      const y = 76 - h;
      const col = i % 2 === 0 ? '#3b6ef6' : '#ffb7a5';
      return `<rect x="${x}" y="${y}" width="14" height="${h}" fill="${col}" stroke="#1c1917" stroke-width="1.5"/>`;
    }).join('');
    $('#psEqSvg').innerHTML = `<svg viewBox="0 0 354 84" aria-label="Cassette Audio Spectrum"><line x1="6" y1="76" x2="348" y2="76" stroke="#1c1917" stroke-width="2"/>${bars}</svg>`;
  }

  function renderCharts() {
    const linePts = [
      [14, 72], [68, 58], [122, 62], [176, 40], [230, 32], [284, 24], [338, 16],
    ];
    const poly = linePts.map(([x, y]) => `${x},${y}`).join(' ');
    $('#psLineChartSvg').innerHTML = `
      <svg viewBox="0 0 356 96" aria-label="Listener Pixel Trend Chart">
        <rect x="4" y="4" width="348" height="78" fill="#fbf7f0" stroke="#1c1917" stroke-width="1.5"/>
        <line x1="4" y1="30" x2="352" y2="30" stroke="#1c1917" stroke-opacity="0.16" stroke-dasharray="3 3"/>
        <line x1="4" y1="56" x2="352" y2="56" stroke="#1c1917" stroke-opacity="0.16" stroke-dasharray="3 3"/>
        <polyline points="${poly}" fill="none" stroke="#3b6ef6" stroke-width="2.5"/>
        ${linePts.map(([x, y]) => `<rect x="${x - 3.5}" y="${y - 3.5}" width="7" height="7" fill="#ffb7a5" stroke="#1c1917" stroke-width="1.5"/>`).join('')}
        <text x="14" y="93" fill="#5c5349" font-size="9">08H</text>
        <text x="176" y="93" text-anchor="middle" fill="#5c5349" font-size="9">12H</text>
        <text x="338" y="93" text-anchor="end" fill="#5c5349" font-size="9">NOW</text>
      </svg>
    `;

    const r = 34;
    const c = 2 * Math.PI * r;
    $('#psDonutSvg').innerHTML = `
      <svg viewBox="0 0 92 92" aria-label="Genre Split Donut" style="transform:rotate(-90deg);">
        <circle cx="46" cy="46" r="${r}" fill="none" stroke="#1c1917" stroke-width="16"/>
        <circle cx="46" cy="46" r="${r}" fill="none" stroke="#ffb7a5" stroke-width="13" stroke-dasharray="${(c * 0.46).toFixed(1)} ${c.toFixed(1)}"/>
        <circle cx="46" cy="46" r="${r}" fill="none" stroke="#3b6ef6" stroke-width="13" stroke-dasharray="${(c * 0.34).toFixed(1)} ${c.toFixed(1)}" stroke-dashoffset="${(-c * 0.46).toFixed(1)}"/>
        <circle cx="46" cy="46" r="${r}" fill="none" stroke="#5c5349" stroke-width="13" stroke-dasharray="${(c * 0.20).toFixed(1)} ${c.toFixed(1)}" stroke-dashoffset="${(-c * 0.80).toFixed(1)}"/>
      </svg>
    `;

    const sysMetrics = [['AUDIO DSP', 78, '#3b6ef6'], ['TAPE DECK', 92, '#ffb7a5'], ['MODEM 56K', 64, '#3b6ef6'], ['VRAM BUS', 84, '#1c1917']];
    $('#psBarsSvg').innerHTML = `
      <svg viewBox="0 0 340 120" aria-label="System 9 Resource Bars">
        ${sysMetrics.map(([lbl, pct, col], idx) => {
          const y = 8 + idx * 28;
          return `
            <text x="2" y="${y + 13}" fill="#1c1917" font-size="10" font-weight="700">${lbl}</text>
            <rect x="86" y="${y + 2}" width="208" height="14" fill="#f4ece1" stroke="#1c1917" stroke-width="1.5"/>
            <rect x="86" y="${y + 2}" width="${Math.round((pct / 100) * 208)}" height="14" fill="${col}" stroke="#1c1917" stroke-width="1.5"/>
            <text x="336" y="${y + 13}" text-anchor="end" fill="#1c1917" font-size="10" font-weight="700">${pct}%</text>
          `;
        }).join('')}
      </svg>
    `;

    const cells = [2,3,2,1,3,2,3, 3,2,3,3,2,1,2, 2,3,3,2,3,3,2];
    $('#psHeatCells').innerHTML = cells.map((v, i) => `<div class="ps-heat-cell" data-v="${v}">${i + 1}</div>`).join('');
  }

  function renderTrack() {
    const ch = CHANNELS[state.trackIdx % CHANNELS.length];
    $('#psTrackTitle').textContent = ch.title;
    $('#psTrackSub').textContent = `CH-0${(state.trackIdx % CHANNELS.length) + 1} · ${ch.bpm} · ${ch.cat.toUpperCase()}`;
    $('#psPlayBtn').textContent = state.playing ? 'Pause' : 'Play';
    renderEq();
  }

  function renderChannels() {
    const activeRange = state.activeFilter;
    const rows = CHANNELS.filter((c) => activeRange === 'all' || c.cat === activeRange);
    const activeCh = CHANNELS[state.trackIdx % CHANNELS.length];
    $('#psChannelGrid').innerHTML = rows.map((c) => `
      <button type="button" class="ps-ch-card ${activeCh.id === c.id ? 'is-tuned' : ''}" data-chid="${c.id}">
        <div class="ps-ch-top"><span>${esc(c.cat)}</span><strong>${esc(c.bpm)}</strong></div>
        <strong>${esc(c.title)}</strong>
        <span style="font-size:11px;">${esc(c.listeners)} listeners</span>
      </button>
    `).join('');
    $('#psChannelGrid').querySelectorAll('[data-chid]').forEach((b) => b.addEventListener('click', () => {
      const idx = CHANNELS.findIndex((c) => c.id === b.dataset.chid);
      if (idx >= 0) { state.trackIdx = idx; renderTrack(); renderChannels(); }
    }));
  }

  function focusWin(winKey) {
    state.frontWin = winKey;
    document.querySelectorAll('.ps-win[data-win]').forEach((w) => w.classList.toggle('is-front', w.dataset.win === winKey));
  }

  function navigate(theme) {
    state.scrollByRoute[state.theme] = mainStage.scrollTop;
    state.theme = theme === 'mint' || theme === 'platinum' ? theme : 'peach';
    viewport.dataset.page = state.theme;
    body.setAttribute('data-theme', state.theme);
    document.querySelectorAll('.ps-tab[data-route]').forEach((t) => t.classList.toggle('is-active', t.dataset.route === state.theme));
    mainStage.scrollTop = state.scrollByRoute[state.theme] || 0;
  }

  function exportCsv() {
    const activeRange = state.activeFilter;
    const rows = CHANNELS.filter((c) => activeRange === 'all' || c.cat === activeRange);
    const lines = ['theme,category,channel,bpm,listeners'];
    rows.forEach((c) => lines.push(`${state.theme},${c.cat},"${c.title}",${c.bpm},"${c.listeners}"`));
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `poolsuite-queue-${state.theme}-${activeRange}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  railDock.addEventListener('pointermove', (e) => updateDock(e.clientY));
  railDock.addEventListener('pointerleave', () => updateDock(null));
  document.querySelectorAll('.ps-tab[data-route]').forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));
  document.querySelectorAll('.ps-win[data-win]').forEach((w) => w.addEventListener('click', () => focusWin(w.dataset.win)));
  document.querySelectorAll('[data-focus-win]').forEach((b) => b.addEventListener('click', () => focusWin(b.dataset.focusWin)));

  $('#psPlayBtn').addEventListener('click', () => { state.playing = !state.playing; renderTrack(); });
  $('#psPrevBtn').addEventListener('click', () => { state.trackIdx = (state.trackIdx + CHANNELS.length - 1) % CHANNELS.length; renderTrack(); renderChannels(); });
  $('#psNextBtn').addEventListener('click', () => { state.trackIdx = (state.trackIdx + 1) % CHANNELS.length; renderTrack(); renderChannels(); });

  document.querySelectorAll('.ps-flt[data-flt]').forEach((b) => b.addEventListener('click', () => {
    state.activeFilter = b.dataset.flt;
    document.querySelectorAll('.ps-flt[data-flt]').forEach((x) => x.classList.toggle('is-active', x === b));
    renderChannels();
  }));
  $('#exportCsvBtn').addEventListener('click', exportCsv);

  $('#openSysBtn').addEventListener('click', (e) => { lastTrigger = e.currentTarget; dialog.showModal(); });
  $('#closeSysBtn').addEventListener('click', () => dialog.close());
  $('#psCycleSkinBtn').addEventListener('click', () => {
    const order = ['peach', 'mint', 'platinum'];
    navigate(order[(order.indexOf(state.theme) + 1) % order.length]);
  });
  dialog.addEventListener('close', () => { if (lastTrigger && typeof lastTrigger.focus === 'function') lastTrigger.focus(); });

  window.addEventListener('message', (ev) => {
    const msg = ev.data || {};
    if (msg.type === 'KAIWU_HIGHLIGHT_EU') {
      document.querySelectorAll('[data-kaiwu-active]').forEach((n) => n.removeAttribute('data-kaiwu-active'));
      if (msg.eu_id === 'eu_L3_ps_system_dialog') {
        if (!dialog.open) { lastTrigger = $('#openSysBtn'); dialog.showModal(); }
        dialog.setAttribute('data-kaiwu-active', 'true');
        return;
      }
      if (dialog.open) dialog.close();
      if (msg.eu_id === 'eu_L3_ps_rail_dock' || msg.eu_id === 'eu_L4_ps_rail_proximity' || msg.action === 'proximity_demo') {
        const btn = railDock.querySelector('.ps-desk-ico');
        if (btn) updateDock(btn.getBoundingClientRect().top + 14);
      } else {
        updateDock(null);
      }
      const target = document.querySelector(`[data-eu-id="${msg.eu_id}"]`) || (msg.fallback_eu_id && document.querySelector(`[data-eu-id="${msg.fallback_eu_id}"]`));
      if (target) { target.setAttribute('data-kaiwu-active', 'true'); target.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
    } else if (msg.type === 'KAIWU_PREVIEW_ACTION') {
      if (dialog.open) dialog.close();
      if (msg.action === 'proximity_demo') {
        const btn = railDock.querySelector('.ps-desk-ico');
        if (btn) updateDock(btn.getBoundingClientRect().top + 14);
      } else {
        updateDock(null);
        navigate(msg.action === 'mint' ? 'mint' : 'peach');
      }
    }
  });

  document.addEventListener('click', (ev) => {
    if (window.parent === window) return;
    const hit = ev.target.closest('[data-eu-id]');
    if (hit) window.parent.postMessage({ type: 'KAIWU_SELECT_EU', eu_id: hit.getAttribute('data-eu-id'), case_id: 'poolsuite_os_web' }, '*');
  }, true);

  renderTrack();
  renderCharts();
  renderChannels();
})();
