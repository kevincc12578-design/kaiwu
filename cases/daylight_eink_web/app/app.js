(() => {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const viewport = $('#viewport');
  const railDock = $('#railDock');
  const mainStage = $('.main-glass') || $('#mainStage');
  const dialog = $('#dlDialog');
  const dockRadius = 96;
  const dockGain = 0.28;

  const NOTES = [
    { id: 'n-1', cat: 'Reading', title: 'Ambient Backlight Discipline', meta: 'Ch. 04 · 38 min', state: 'Clipped' },
    { id: 'n-2', cat: 'Notes', title: 'Chunked Focus Intervals', meta: 'Deep Note · 25 min', state: 'Verified' },
    { id: 'n-3', cat: 'Tasks', title: 'Audit Blue-Light Cutoff', meta: 'Sol:OS · 45 min', state: 'Queued' },
    { id: 'n-4', cat: 'Reading', title: 'Zero-Flicker Frame Pacing', meta: 'Ch. 06 · 32 min', state: 'Clipped' },
  ];

  const state = {
    route: 'read',
    amberPct: 32,
    pageNum: 42,
    timerRunning: false,
    secondsLeft: 1500,
    activeFilter: 'all',
    notes: [...NOTES],
    scrollByRoute: {},
    lastTrigger: null,
  };
  let timerHandle = 0;

  function updateDock(pointerY) {
    const btns = Array.from(railDock.querySelectorAll('.rail-btn[data-route]'));
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

  function applyAmber(pct) {
    state.amberPct = Math.max(0, Math.min(100, Number(pct) || 0));
    $('#amberPctLabel').textContent = `${state.amberPct}%`;
    document.documentElement.style.setProperty(
      '--dl-surface',
      `color-mix(in srgb, var(--dl-paper) ${100 - state.amberPct}%, var(--dl-amber) ${state.amberPct}%)`
    );
  }

  function renderInkCharts() {
    const mins = [45, 62, 54, 78, 66, 58, 47];
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const max = 85;
    const bars = mins.map((m, i) => {
      const x = 18 + i * 52;
      const h = Math.round((m / max) * 76);
      const y = 96 - h;
      const fill = i === 3 ? '#1a1714' : '#e5bc75';
      return `
        <rect x="${x}" y="${y}" width="26" height="${h}" rx="3" fill="${fill}" stroke="#1a1714" stroke-width="1.5"/>
        <text x="${x + 13}" y="${y - 4}" text-anchor="middle" fill="#1a1714" font-size="9.5" font-family="monospace">${m}m</text>
        <text x="${x + 13}" y="112" text-anchor="middle" fill="#5e574c" font-size="10" font-family="monospace">${days[i]}</text>
      `;
    }).join('');
    $('#dlBarChartSvg').innerHTML = `
      <svg viewBox="0 0 390 120" aria-label="Daily Reading Minutes Chart">
        <line x1="12" y1="96" x2="378" y2="96" stroke="#1a1714" stroke-width="1.5"/>
        ${bars}
      </svg>
    `;

    const r = 38;
    const c = 2 * Math.PI * r;
    $('#dlRingSvg').innerHTML = `
      <svg viewBox="0 0 112 112" aria-label="Deep Focus Ratio Ring">
        <circle cx="56" cy="56" r="${r}" fill="none" stroke="#c5bcab" stroke-width="10"/>
        <circle cx="56" cy="56" r="${r}" fill="none" stroke="#1a1714" stroke-width="10" stroke-dasharray="${(c * 0.88).toFixed(1)} ${c.toFixed(1)}" transform="rotate(-90 56 56)"/>
        <text x="56" y="60" text-anchor="middle" fill="#1a1714" font-size="16" font-weight="700" font-family="monospace">88%</text>
      </svg>
    `;

    const cells = [2,3,3,2,3,1,0, 3,3,2,3,3,2,1, 2,3,3,3,2,1,0, 3,3,3,3,2,2,1];
    $('#dlHeatGrid').innerHTML = cells.map((d, i) => `<div class="dl-heat-cell" data-d="${d}">${i + 1}</div>`).join('');
  }

  function renderNotes() {
    const activeRange = state.activeFilter;
    const rows = state.notes.filter((n) => activeRange === 'all' || n.cat === activeRange);
    $('#dlNotesGrid').innerHTML = rows.slice(0, 4).map((n) => `
      <article class="dl-note-card">
        <div class="dl-note-top"><span>${esc(n.cat.toUpperCase())}</span><strong>${esc(n.state)}</strong></div>
        <strong style="font-size:13.5px;">${esc(n.title)}</strong>
        <span class="dl-mono">${esc(n.meta)}</span>
      </article>
    `).join('');
  }

  function navigate(route) {
    state.scrollByRoute[state.route] = mainStage.scrollTop;
    state.route = route || 'read';
    viewport.dataset.page = state.route;
    document.querySelectorAll('.rail-btn[data-route], .dl-tab[data-route]').forEach((b) => {
      b.classList.toggle('is-active', b.dataset.route === state.route);
    });
    mainStage.scrollTop = state.scrollByRoute[state.route] || 0;
  }

  function exportCsv() {
    const activeRange = state.activeFilter;
    const rows = state.notes.filter((n) => activeRange === 'all' || n.cat === activeRange);
    const lines = ['amber_pct,category,title,meta,status'];
    rows.forEach((n) => lines.push(`${state.amberPct}%,${n.cat},"${n.title}","${n.meta}",${n.state}`));
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `daylight-paper-${activeRange}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  railDock.addEventListener('pointermove', (e) => updateDock(e.clientY));
  railDock.addEventListener('pointerleave', () => updateDock(null));
  document.querySelectorAll('.rail-btn[data-route], .dl-tab[data-route]').forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));

  $('#amberRange').addEventListener('input', (e) => applyAmber(e.target.value));
  $('#refreshInkBtn').addEventListener('click', () => {
    document.body.classList.add('is-flashing');
    setTimeout(() => document.body.classList.remove('is-flashing'), 140);
  });

  $('#dlExcerpts').querySelectorAll('.dl-excerpt').forEach((b) => b.addEventListener('click', () => {
    $('#dlExcerpts').querySelectorAll('.dl-excerpt').forEach((x) => x.classList.remove('is-picked'));
    b.classList.add('is-picked');
    state.notes.unshift({ id: `n-${Date.now()}`, cat: b.dataset.cat, title: b.dataset.title, meta: `P.${state.pageNum} · ${b.dataset.min} min`, state: 'Clipped' });
    renderNotes();
  }));

  $('#dlPageNextBtn').addEventListener('click', () => {
    state.pageNum = state.pageNum >= 186 ? 1 : state.pageNum + 1;
    $('#dlPageNum').textContent = `P. ${state.pageNum} / 186`;
  });

  $('#dlTimerBtn').addEventListener('click', () => {
    state.timerRunning = !state.timerRunning;
    $('#dlTimerBtn').textContent = state.timerRunning ? 'Pause Sprint' : 'Start Sprint';
    clearInterval(timerHandle);
    if (state.timerRunning) {
      timerHandle = setInterval(() => {
        state.secondsLeft = Math.max(0, state.secondsLeft - 1);
        const m = String(Math.floor(state.secondsLeft / 60)).padStart(2, '0');
        const s = String(state.secondsLeft % 60).padStart(2, '0');
        $('#dlTimerDisplay').textContent = `${m}:${s}`;
      }, 1000);
    }
  });

  document.querySelectorAll('.dl-flt[data-flt]').forEach((b) => b.addEventListener('click', () => {
    state.activeFilter = b.dataset.flt;
    document.querySelectorAll('.dl-flt[data-flt]').forEach((x) => x.classList.toggle('is-active', x === b));
    renderNotes();
  }));
  $('#exportCsvBtn').addEventListener('click', exportCsv);

  $('#openNoteBtn').addEventListener('click', (e) => { state.lastTrigger = e.currentTarget; dialog.showModal(); });
  $('#closeNoteBtn').addEventListener('click', () => dialog.close());
  $('#dlNoteForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const title = ($('#dlNoteTitleInp').value || '').trim();
    const cat = $('#dlNoteCatSel').value;
    if (title) {
      state.notes.unshift({ id: `n-${Date.now()}`, cat, title, meta: `P.${state.pageNum} · Manual`, state: 'Verified' });
      renderNotes();
    }
    dialog.close();
  });
  dialog.addEventListener('close', () => { if (state.lastTrigger && typeof state.lastTrigger.focus === 'function') state.lastTrigger.focus(); });

  window.addEventListener('message', (ev) => {
    const msg = ev.data || {};
    if (msg.type === 'KAIWU_HIGHLIGHT_EU') {
      document.querySelectorAll('[data-kaiwu-active]').forEach((n) => n.removeAttribute('data-kaiwu-active'));
      if (msg.eu_id === 'eu_L3_dl_note_dialog') {
        if (!dialog.open) { state.lastTrigger = $('#openNoteBtn'); dialog.showModal(); }
        dialog.setAttribute('data-kaiwu-active', 'true');
        return;
      }
      if (dialog.open) dialog.close();
      if (msg.eu_id === 'eu_L3_dl_rail_dock' || msg.eu_id === 'eu_L4_dl_rail_proximity' || msg.action === 'proximity_demo') {
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
        navigate('read');
      }
    }
  });

  document.addEventListener('click', (ev) => {
    if (window.parent === window) return;
    const hit = ev.target.closest('[data-eu-id]');
    if (hit) window.parent.postMessage({ type: 'KAIWU_SELECT_EU', eu_id: hit.getAttribute('data-eu-id'), case_id: 'daylight_eink_web' }, '*');
  }, true);

  applyAmber(32);
  renderInkCharts();
  renderNotes();
})();
