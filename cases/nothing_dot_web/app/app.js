(() => {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const viewport = $('#viewport');
  const dialog = $('#ndDialog');
  let lastTrigger = null;

  const DIGITS_3X5 = {
    '1': [0,1,0, 1,1,0, 0,1,0, 0,1,0, 1,1,1],
    '2': [1,1,1, 0,0,1, 1,1,1, 1,0,0, 1,1,1],
    '4': [1,0,1, 1,0,1, 1,1,1, 0,0,1, 0,0,1],
    '0': [1,1,1, 1,0,1, 1,0,1, 1,0,1, 1,1,1],
    '7': [1,1,1, 0,0,1, 0,1,0, 0,1,0, 0,1,0],
    '8': [1,1,1, 1,0,1, 1,1,1, 1,0,1, 1,1,1],
    '9': [1,1,1, 1,0,1, 1,1,1, 0,0,1, 1,1,1],
    ':': [0, 1, 0, 1, 0],
  };

  const MODE_DATA = {
    glyph: {
      clock: '14:07',
      freq: '48.0 KHZ',
      cpuLabel: 'LOAD 38% · 41°C',
      wave: [22, 34, 28, 45, 58, 42, 36, 62, 74, 52, 46, 38],
      spec: [28, 44, 68, 52, 84, 72, 48, 64, 92, 76, 54, 42, 66, 82, 48, 32],
      steps: '8,420',
      stepPct: 84,
    },
    studio: {
      clock: '20:48',
      freq: '96.0 KHZ',
      cpuLabel: 'LOAD 64% · 49°C',
      wave: [40, 56, 48, 72, 68, 84, 78, 91, 82, 74, 88, 76],
      spec: [52, 78, 90, 82, 96, 88, 72, 86, 94, 84, 76, 68, 82, 92, 74, 58],
      steps: '9,180',
      stepPct: 92,
    },
    quiet: {
      clock: '07:20',
      freq: '24.0 KHZ',
      cpuLabel: 'LOAD 14% · 34°C',
      wave: [12, 16, 14, 20, 18, 22, 16, 18, 24, 16, 14, 12],
      spec: [14, 22, 30, 24, 36, 28, 20, 26, 32, 24, 18, 16, 22, 28, 18, 12],
      steps: '4,210',
      stepPct: 42,
    },
  };

  const WIDGETS = [
    { id: 'w-core', cat: 'SYSTEM', title: 'CORE.SCHED', metric: '38% NPU', status: 'ARMED', detail: '120Hz Scheduler Lock' },
    { id: 'w-dac', cat: 'AUDIO', title: 'DAC.48K', metric: '-6.0 dB', status: 'ARMED', detail: 'Nothing Ear Lossless' },
    { id: 'w-sync', cat: 'SYSTEM', title: 'GLYPH.BUS', metric: '4 ZONES', status: 'STANDBY', detail: 'Camera Ring Telemetry' },
    { id: 'w-temp', cat: 'SENSOR', title: 'THERM.CH0', metric: '41.2°C', status: 'ARMED', detail: 'Vapor Chamber Nominal' },
  ];

  const state = {
    mode: 'glyph',
    zones: [true, true, true, false],
    specBoost: 0,
    activeFilter: 'all',
    armedIds: new Set(['w-core', 'w-dac', 'w-temp']),
  };

  function renderDotClock(txt) {
    const tokens = txt.split('');
    let dots = '';
    let xOff = 8;
    tokens.forEach((ch) => {
      const mat = DIGITS_3X5[ch] || DIGITS_3X5['0'];
      const cols = ch === ':' ? 1 : 3;
      for (let r = 0; r < 5; r += 1) {
        for (let c = 0; c < cols; c += 1) {
          const on = mat[r * cols + c] === 1;
          const fill = on ? (ch === ':' ? '#d71921' : '#ffffff') : '#1e1e20';
          dots += `<circle cx="${xOff + c * 14}" cy="${12 + r * 14}" r="4.8" fill="${fill}"/>`;
        }
      }
      xOff += cols * 14 + 14;
    });
    $('#ndClockMatrix').innerHTML = `<svg class="nd-dot-svg" viewBox="0 0 ${xOff + 4} 84" aria-label="Dot Matrix Clock">${dots}</svg>`;
  }

  function renderGlyphRing() {
    const activeCount = state.zones.filter(Boolean).length;
    let segs = '';
    for (let i = 0; i < 4; i += 1) {
      const a0 = i * 90 + 10;
      const a1 = (i + 1) * 90 - 10;
      const r = 44;
      const x0 = 60 + r * Math.cos((a0 - 90) * Math.PI / 180);
      const y0 = 60 + r * Math.sin((a0 - 90) * Math.PI / 180);
      const x1 = 60 + r * Math.cos((a1 - 90) * Math.PI / 180);
      const y1 = 60 + r * Math.sin((a1 - 90) * Math.PI / 180);
      const col = state.zones[i] ? (i === 1 ? '#d71921' : '#ffffff') : '#2a2a2e';
      segs += `<path d="M${x0.toFixed(1)},${y0.toFixed(1)} A${r},${r} 0 0,1 ${x1.toFixed(1)},${y1.toFixed(1)}" fill="none" stroke="${col}" stroke-width="6" stroke-linecap="round"/>`;
    }
    $('#ndGlyphRingSvg').innerHTML = `
      <svg class="nd-dot-svg" viewBox="0 0 120 120" aria-label="Glyph Ring Diagram">
        <circle cx="60" cy="60" r="28" fill="none" stroke="#262626" stroke-dasharray="3 4" stroke-width="2"/>
        ${segs}
        <text x="60" y="57" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="700">${activeCount}/4</text>
        <text x="60" y="72" text-anchor="middle" fill="#8a8a8f" font-size="9">ZONES</text>
      </svg>
    `;
  }

  function renderWaveChart() {
    const arr = MODE_DATA[state.mode].wave;
    const W = 400;
    const H = 122;
    let bgDots = '';
    for (let x = 16; x <= W - 16; x += 24) {
      for (let y = 16; y <= H - 22; y += 18) {
        bgDots += `<circle cx="${x}" cy="${y}" r="1.3" fill="#262626"/>`;
      }
    }
    const pts = arr.map((v, i) => [16 + (i / (arr.length - 1)) * (W - 32), H - 24 - (v / 100) * (H - 40)]);
    const poly = pts.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
    const peakIdx = arr.indexOf(Math.max(...arr));
    const labels = ['T-11', 'T-9', 'T-7', 'T-5', 'T-3', 'NOW'].map((t, i) => {
      const lx = 16 + (i / 5) * (W - 32);
      return `<text x="${lx.toFixed(1)}" y="${H - 4}" text-anchor="middle" fill="#8a8a8f" font-size="9.5">${t}</text>`;
    }).join('');
    $('#ndWaveChartSvg').innerHTML = `
      <svg class="nd-dot-svg" viewBox="0 0 ${W} ${H}" aria-label="CPU Telemetry Waveform">
        ${bgDots}
        <polyline points="${poly}" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linejoin="round"/>
        ${pts.map(([x, y], i) => `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${i === peakIdx ? 4.5 : 2.8}" fill="${i === peakIdx ? '#d71921' : '#ffffff'}"/>`).join('')}
        ${labels}
      </svg>
    `;
  }

  function renderSpecChart() {
    const base = MODE_DATA[state.mode].spec;
    const W = 400;
    const H = 124;
    let dots = '';
    base.forEach((raw, col) => {
      const val = Math.min(98, (raw + state.specBoost * ((col % 3) * 6)) % 100);
      const count = Math.max(2, Math.round((val / 100) * 8));
      const cx = 14 + col * 24.5;
      for (let r = 0; r < 8; r += 1) {
        const y = H - 24 - r * 11;
        const on = r < count;
        const fill = !on ? '#1c1c1e' : (r >= 6 ? '#d71921' : '#ffffff');
        dots += `<circle cx="${cx.toFixed(1)}" cy="${y}" r="3.8" fill="${fill}"/>`;
      }
    });
    $('#ndSpecChartSvg').innerHTML = `
      <svg class="nd-dot-svg" viewBox="0 0 ${W} ${H}" aria-label="Audio Dot Spectrum Chart">
        ${dots}
        <text x="14" y="${H - 4}" fill="#8a8a8f" font-size="9.5">60HZ</text>
        <text x="195" y="${H - 4}" text-anchor="middle" fill="#8a8a8f" font-size="9.5">1.2KHZ</text>
        <text x="386" y="${H - 4}" text-anchor="end" fill="#8a8a8f" font-size="9.5">16KHZ</text>
      </svg>
    `;
  }

  function renderStepRing() {
    const d = MODE_DATA[state.mode];
    $('#ndStepCount').textContent = d.steps;
    let dots = '';
    const n = 24;
    const lit = Math.round((d.stepPct / 100) * n);
    for (let i = 0; i < n; i += 1) {
      const ang = -Math.PI / 2 + (i * 2 * Math.PI) / n;
      const x = 56 + 42 * Math.cos(ang);
      const y = 56 + 42 * Math.sin(ang);
      const on = i < lit;
      const fill = !on ? '#262626' : (i >= lit - 3 ? '#d71921' : '#ffffff');
      dots += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.4" fill="${fill}"/>`;
    }
    $('#ndStepRingSvg').innerHTML = `
      <svg class="nd-dot-svg" viewBox="0 0 112 112" aria-label="Step Goal Dot Ring">
        ${dots}
        <text x="56" y="60" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="700">${d.stepPct}%</text>
      </svg>
    `;
  }

  function renderHeatMatrix() {
    const lvls = state.mode === 'studio'
      ? [2,3,4,3,2,3,1, 3,4,4,2,3,4,2, 2,3,4,3,3,2,1, 3,4,3,4,3,2,2]
      : (state.mode === 'quiet'
        ? [0,1,1,0,1,0,0, 1,1,2,1,0,1,0, 0,1,1,2,1,0,0, 1,2,1,1,1,0,0]
        : [1,2,3,2,1,2,1, 2,3,4,2,3,2,1, 1,3,3,4,2,2,1, 2,3,2,3,4,2,1]);
    $('#ndHeatMatrix').innerHTML = lvls.map((l, i) => `<div class="nd-heat-cell" data-lvl="${l}">N${String(i + 1).padStart(2, '0')}</div>`).join('');
  }

  function renderWidgets() {
    const activeRange = state.activeFilter;
    const rows = WIDGETS.filter((w) => activeRange === 'all' || w.cat === activeRange);
    $('#ndWidgetsGrid').innerHTML = rows.map((w) => {
      const armed = state.armedIds.has(w.id);
      return `
        <button type="button" class="nd-widget-card ${armed ? 'is-armed' : ''}" data-wid="${w.id}">
          <div class="nd-widget-top"><span>[${esc(w.cat)}]</span><span>${armed ? 'ARMED' : 'IDLE'}</span></div>
          <strong>${esc(w.title)} · ${esc(w.metric)}</strong>
          <span class="nd-mono-sub">${esc(w.detail)}</span>
        </button>
      `;
    }).join('');
    $('#ndWidgetsGrid').querySelectorAll('[data-wid]').forEach((b) => b.addEventListener('click', () => {
      const id = b.dataset.wid;
      if (state.armedIds.has(id)) state.armedIds.delete(id);
      else state.armedIds.add(id);
      renderWidgets();
    }));
  }

  function renderAll() {
    const d = MODE_DATA[state.mode];
    $('#ndModeTag').textContent = state.mode.toUpperCase();
    $('#ndFreqLabel').textContent = d.freq;
    $('#ndCpuLabel').textContent = d.cpuLabel;
    renderDotClock(d.clock);
    renderGlyphRing();
    renderWaveChart();
    renderSpecChart();
    renderStepRing();
    renderHeatMatrix();
    renderWidgets();
  }

  function navigate(mode) {
    state.mode = MODE_DATA[mode] ? mode : 'glyph';
    viewport.dataset.page = state.mode;
    document.querySelectorAll('.nd-tab[data-route]').forEach((t) => t.classList.toggle('is-active', t.dataset.route === state.mode));
    renderAll();
  }

  function exportCsv() {
    const activeRange = state.activeFilter;
    const rows = WIDGETS.filter((w) => activeRange === 'all' || w.cat === activeRange);
    const lines = ['mode,category,widget,metric,status'];
    rows.forEach((w) => lines.push(`${state.mode},${w.cat},${w.title},"${w.metric}",${state.armedIds.has(w.id) ? 'ARMED' : 'IDLE'}`));
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `nothing-telemetry-${state.mode}-${activeRange}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  document.querySelectorAll('.nd-tab[data-route]').forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));
  document.querySelectorAll('.nd-zone-btn').forEach((b) => b.addEventListener('click', () => {
    const idx = Number(b.dataset.zone);
    state.zones[idx] = !state.zones[idx];
    b.classList.toggle('is-on', state.zones[idx]);
    b.querySelector('strong').textContent = state.zones[idx] ? 'ON' : 'OFF';
    renderGlyphRing();
  }));
  $('#pulseRingBtn').addEventListener('click', () => {
    state.zones = state.zones.map((_, i) => i === 1 || !state.zones[i]);
    document.querySelectorAll('.nd-zone-btn').forEach((b, i) => {
      b.classList.toggle('is-on', state.zones[i]);
      b.querySelector('strong').textContent = state.zones[i] ? 'ON' : 'OFF';
    });
    renderGlyphRing();
  });
  $('#shiftSpecBtn').addEventListener('click', () => { state.specBoost = (state.specBoost + 1) % 4; renderSpecChart(); });
  document.querySelectorAll('.nd-flt[data-flt]').forEach((b) => b.addEventListener('click', () => {
    state.activeFilter = b.dataset.flt;
    document.querySelectorAll('.nd-flt[data-flt]').forEach((x) => x.classList.toggle('is-active', x === b));
    renderWidgets();
  }));
  $('#exportCsvBtn').addEventListener('click', exportCsv);

  $('#openDiagBtn').addEventListener('click', (e) => { lastTrigger = e.currentTarget; dialog.showModal(); });
  $('#closeDiagBtn').addEventListener('click', () => dialog.close());
  $('#armAllBtn').addEventListener('click', () => {
    state.zones = [true, true, true, true];
    document.querySelectorAll('.nd-zone-btn').forEach((b) => { b.classList.add('is-on'); b.querySelector('strong').textContent = 'ON'; });
    renderGlyphRing();
    dialog.close();
  });
  $('#muteAllBtn').addEventListener('click', () => {
    state.zones = [false, false, false, false];
    document.querySelectorAll('.nd-zone-btn').forEach((b) => { b.classList.remove('is-on'); b.querySelector('strong').textContent = 'OFF'; });
    renderGlyphRing();
    dialog.close();
  });
  dialog.addEventListener('close', () => { if (lastTrigger && typeof lastTrigger.focus === 'function') lastTrigger.focus(); });

  window.addEventListener('message', (ev) => {
    const msg = ev.data || {};
    if (msg.type === 'KAIWU_HIGHLIGHT_EU') {
      document.querySelectorAll('[data-kaiwu-active]').forEach((n) => n.removeAttribute('data-kaiwu-active'));
      if (msg.eu_id === 'eu_L3_nd_diag_dialog') {
        if (!dialog.open) { lastTrigger = $('#openDiagBtn'); dialog.showModal(); }
        dialog.setAttribute('data-kaiwu-active', 'true');
        return;
      }
      if (dialog.open) dialog.close();
      const target = document.querySelector(`[data-eu-id="${msg.eu_id}"]`) || (msg.fallback_eu_id && document.querySelector(`[data-eu-id="${msg.fallback_eu_id}"]`));
      if (target) { target.setAttribute('data-kaiwu-active', 'true'); target.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
    } else if (msg.type === 'KAIWU_PREVIEW_ACTION') {
      if (dialog.open) dialog.close();
      if (msg.action === 'studio') navigate('studio');
      else navigate('glyph');
    }
  });

  document.addEventListener('click', (ev) => {
    if (window.parent === window) return;
    const hit = ev.target.closest('[data-eu-id]');
    if (hit) window.parent.postMessage({ type: 'KAIWU_SELECT_EU', eu_id: hit.getAttribute('data-eu-id'), case_id: 'nothing_dot_web' }, '*');
  }, true);

  renderAll();
})();
