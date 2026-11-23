(function () {
  const viewport = document.getElementById('viewport');
  const mainStage = document.querySelector('.main-glass');
  const railDock = document.getElementById('railDock');
  const railBtns = Array.from(document.querySelectorAll('.rail-btn'));
  const modeTabs = Array.from(document.querySelectorAll('.mode-tab'));

  const zoomFrame = document.getElementById('zoomFrame');
  const zoomReadout = document.getElementById('zoomReadout');
  const smoothCursor = document.getElementById('smoothCursor');
  const hotspots = Array.from(document.querySelectorAll('.hotspot'));
  const zKeys = Array.from(document.querySelectorAll('.z-key'));
  const playZoomBtn = document.getElementById('playZoomBtn');
  const resetZoomBtn = document.getElementById('resetZoomBtn');
  const pipCam = document.getElementById('pipCam');

  const audBtns = Array.from(document.querySelectorAll('.aud-btn'));
  const trackFlts = Array.from(document.querySelectorAll('.track-flt'));
  const tracks = Array.from(document.querySelectorAll('.ss-track'));
  const audioWave = document.getElementById('audioWave');
  const exportCsvBtn = document.getElementById('exportCsvBtn');

  const dialog = document.getElementById('exportDialog');
  const openExportBtn = document.getElementById('openExportBtn');
  const closeExportBtn = document.getElementById('closeExportBtn');
  const confirmExportCsv = document.getElementById('confirmExportCsv');
  const dlgAudMode = document.getElementById('dlgAudMode');

  let activeRange = 'all';
  let audioMode = 'standard';
  let scrollByRoute = { recording: 0, editing: 0, cursor: 0, sharing: 0 };
  let lastTriggerEl = openExportBtn;

  function navigate(route) {
    const prev = viewport.dataset.page || 'editing';
    if (mainStage) scrollByRoute[prev] = mainStage.scrollTop;
    const target = route || 'editing';
    viewport.dataset.page = target;
    railBtns.forEach((b) => b.classList.toggle('is-active', b.dataset.route === target));
    modeTabs.forEach((t) => t.classList.toggle('is-active', t.dataset.route === target));
    if (mainStage) mainStage.scrollTop = scrollByRoute[target] || 0;
  }

  function updateDock(pointerY) {
    const dockRadius = 110;
    const dockGain = 0.35;
    railBtns.forEach((btn) => {
      const rect = btn.getBoundingClientRect();
      const center = rect.top + rect.height / 2;
      const dist = Math.abs(pointerY - center);
      const ratio = Math.max(0, 1 - dist / dockRadius);
      const scale = 1 + ratio * dockGain;
      const shift = ratio * 5;
      btn.style.setProperty('--dock-scale', scale.toFixed(3));
      btn.style.setProperty('--dock-shift', `${shift.toFixed(1)}px`);
    });
  }

  function resetDock() {
    railBtns.forEach((btn) => {
      btn.style.setProperty('--dock-scale', '1');
      btn.style.setProperty('--dock-shift', '0px');
    });
  }

  function applyZoom(zx, zy, scale, label) {
    zoomFrame.style.setProperty('--zx', `${zx}%`);
    zoomFrame.style.setProperty('--zy', `${zy}%`);
    zoomFrame.style.setProperty('--zscale', String(scale));
    smoothCursor.style.setProperty('--cx', `${zx}%`);
    smoothCursor.style.setProperty('--cy', `${zy}%`);
    zoomReadout.textContent = scale > 1.05 ? `${scale.toFixed(2)}x · ${label}` : '1.00x Center';
    hotspots.forEach((h) => h.classList.toggle('is-target', Number(h.dataset.zx) === zx && scale > 1.05));
  }

  function renderWaveform() {
    const factor = audioMode === 'podcast' ? 1.18 : audioMode === 'noise' ? 0.65 : 0.92;
    const bars = [];
    for (let i = 0; i < 40; i++) {
      const base = 24 + ((i * 19) % 62);
      const h = Math.max(16, Math.min(96, Math.round(base * factor)));
      bars.push(`<span class="wave-bar" style="height:${h}%"></span>`);
    }
    audioWave.innerHTML = bars.join('');
  }

  function filterTracks(flt) {
    activeRange = flt || 'all';
    trackFlts.forEach((b) => b.classList.toggle('is-active', b.dataset.flt === activeRange));
    tracks.forEach((tr) => tr.classList.toggle('is-hidden', activeRange !== 'all' && tr.dataset.t !== activeRange));
  }

  function exportCsv() {
    const rows = [
      'track,start_sec,end_sec,detail,audio_mode',
      `video,0.00,5.20,FullScreen Capture,${audioMode}`,
      `zoom,1.25,2.40,2.0x Billing Metrics,${audioMode}`,
      `zoom,2.60,3.85,2.0x Webhook Inspector,${audioMode}`,
      `zoom,3.95,5.10,2.0x Deployment Trigger,${audioMode}`,
      `audio,0.00,5.20,48kHz Waveform,${audioMode}`,
    ].filter((r, i) => i === 0 || activeRange === 'all' || r.startsWith(activeRange));
    const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `screen-studio-${activeRange}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  railDock.addEventListener('pointermove', (e) => updateDock(e.clientY));
  railDock.addEventListener('pointerleave', resetDock);
  railBtns.forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));
  modeTabs.forEach((t) => t.addEventListener('click', () => navigate(t.dataset.route)));

  hotspots.forEach((btn) => {
    btn.addEventListener('click', () => {
      applyZoom(Number(btn.dataset.zx), Number(btn.dataset.zy), 1.48, btn.dataset.label);
    });
  });
  zKeys.forEach((btn) => {
    btn.addEventListener('click', () => {
      applyZoom(Number(btn.dataset.zx), Number(btn.dataset.zy), 1.55, btn.dataset.label);
    });
  });
  playZoomBtn.addEventListener('click', () => applyZoom(52, 56, 1.55, 'Auto-Zoom 2.0x'));
  resetZoomBtn.addEventListener('click', () => applyZoom(50, 50, 1.0, 'Center'));
  pipCam.addEventListener('click', () => pipCam.classList.toggle('is-left'));

  audBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      audioMode = btn.dataset.aud;
      audBtns.forEach((b) => b.classList.toggle('is-active', b === btn));
      dlgAudMode.textContent = btn.textContent;
      renderWaveform();
    });
  });

  trackFlts.forEach((btn) => btn.addEventListener('click', () => filterTracks(btn.dataset.flt)));
  exportCsvBtn.addEventListener('click', exportCsv);

  openExportBtn.addEventListener('click', () => {
    lastTriggerEl = openExportBtn;
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  });
  closeExportBtn.addEventListener('click', () => dialog && dialog.close());
  confirmExportCsv.addEventListener('click', () => {
    exportCsv();
    dialog.close();
  });
  if (dialog) {
    dialog.addEventListener('close', () => {
      if (lastTriggerEl && typeof lastTriggerEl.focus === 'function') lastTriggerEl.focus();
    });
  }

  document.querySelectorAll('[data-eu-id]').forEach((el) => {
    el.addEventListener('click', (e) => {
      const target = e.target.closest('[data-eu-id]');
      if (!target) return;
      window.parent.postMessage({ type: 'KAIWU_SELECT_EU', eu_id: target.dataset.euId }, '*');
    });
  });

  window.addEventListener('message', (event) => {
    const msg = event.data || {};
    if (msg.type === 'KAIWU_HIGHLIGHT_EU') {
      document.querySelectorAll('.kaiwu-eu-highlight,[data-kaiwu-active]').forEach((n) => {
        n.classList.remove('kaiwu-eu-highlight');
        n.removeAttribute('data-kaiwu-active');
      });
      const node =
        document.querySelector(`[data-eu-id="${msg.eu_id}"]`) ||
        (msg.fallback_eu_id ? document.querySelector(`[data-eu-id="${msg.fallback_eu_id}"]`) : null);
      if (node) {
        node.classList.add('kaiwu-eu-highlight');
        node.setAttribute('data-kaiwu-active', 'true');
        node.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    } else if (msg.type === 'KAIWU_PREVIEW_ACTION') {
      if (msg.action === 'normal') {
        navigate('editing');
        applyZoom(50, 50, 1.0, 'Center');
        resetDock();
      } else if (msg.action === 'proximity_demo') {
        const firstBtn = railBtns[1] || railBtns[0];
        if (firstBtn) updateDock(firstBtn.getBoundingClientRect().top + 18);
      } else if (msg.action === 'auto_zoom') {
        applyZoom(52, 56, 1.55, 'Auto-Zoom 2.0x');
      }
    }
  });

  renderWaveform();
})();
