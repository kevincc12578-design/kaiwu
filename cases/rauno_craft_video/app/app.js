(function () {
  const viewport = document.getElementById('viewport');
  const navBtns = Array.from(document.querySelectorAll('.rn-nav-btn'));
  const slowMoBtn = document.getElementById('slowMoBtn');
  const slowRateTag = document.getElementById('slowRateTag');
  const timescaleReadout = document.getElementById('timescaleReadout');
  const precisionTierReadout = document.getElementById('precisionTierReadout');

  const radialArena = document.getElementById('radialArena');
  const radialSectors = document.getElementById('radialSectors');
  const radialBeam = document.getElementById('radialBeam');
  const radialCoreBtn = document.getElementById('radialCoreBtn');
  const radialCoreLabel = document.getElementById('radialCoreLabel');
  const radialReadout = document.getElementById('radialReadout');
  const toggleRadialBtn = document.getElementById('toggleRadialBtn');

  const precisionTrack = document.getElementById('precisionTrack');
  const rulerTicks = document.getElementById('rulerTicks');
  const rulerThumb = document.getElementById('rulerThumb');
  const thumbPill = document.getElementById('thumbPill');
  const scrubberTime = document.getElementById('scrubberTime');
  const precisionDepthLbl = document.getElementById('precisionDepthLbl');
  const scrubSlider = document.getElementById('scrubSlider');
  const precBtns = Array.from(document.querySelectorAll('.prec-btn'));

  const flashGrid = document.getElementById('flashGrid');
  const flTabs = Array.from(document.querySelectorAll('.fl-tab'));
  const flashCards = Array.from(document.querySelectorAll('.rn-flash-card'));

  const dialog = document.getElementById('inspectorDialog');
  const openInspectorBtn = document.getElementById('openInspectorBtn');
  const closeDlgBtn = document.getElementById('closeDlgBtn');
  const toggleSlowFromDlg = document.getElementById('toggleSlowFromDlg');
  const dlgSlowVal = document.getElementById('dlgSlowVal');

  const SECTORS = ['Play', 'Bookmark', 'Inspect', 'Split', 'Mirror', 'Export', 'Freeze', 'Reset'];
  let slowMo = false;
  let radialOpen = true;
  let selectedSectorIdx = 0;
  let tier = 'medium';
  let scrubMinutes = 865;
  let lastTriggerEl = openInspectorBtn;

  function navigate(route) {
    const target = route || 'radial';
    viewport.dataset.page = target;
    navBtns.forEach((b) => {
      const on = b.dataset.route === target;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    if (target === 'radial') {
      setRadialOpen(true);
    } else if (target === 'precision') {
      setPrecisionTier('fine');
    }
  }

  function setSlowMotion(flag) {
    slowMo = Boolean(flag);
    const scale = slowMo ? 4 : 1;
    document.documentElement.style.setProperty('--rn-slow-scale', String(scale));
    viewport.dataset.slow = slowMo ? '0.25' : '1';
    slowMoBtn.setAttribute('aria-pressed', slowMo ? 'true' : 'false');
    slowRateTag.textContent = slowMo ? '0.25x' : '1.0x';
    const label = slowMo ? '0.25x (1120ms)' : '1.00x (280ms)';
    timescaleReadout.textContent = label;
    dlgSlowVal.textContent = label;
  }

  function buildRadialSectors() {
    const radius = 122;
    radialSectors.innerHTML = SECTORS.map((name, idx) => {
      const deg = idx * 45 - 90;
      const rad = (deg * Math.PI) / 180;
      const x = Math.round(Math.cos(rad) * radius);
      const y = Math.round(Math.sin(rad) * radius);
      const cls = idx === selectedSectorIdx ? 'rn-sector-node is-selected' : 'rn-sector-node';
      return `<button type="button" class="${cls}" data-idx="${idx}" style="--sx:${x}px;--sy:${y}px">${name}</button>`;
    }).join('');
    syncRadialSelection(selectedSectorIdx);
  }

  function syncRadialSelection(idx) {
    selectedSectorIdx = ((idx % SECTORS.length) + SECTORS.length) % SECTORS.length;
    const deg = selectedSectorIdx * 45 - 90;
    radialBeam.style.transform = `rotate(${deg}deg)`;
    radialCoreLabel.textContent = SECTORS[selectedSectorIdx];
    radialReadout.textContent = `Sector: ${SECTORS[selectedSectorIdx]} / ${selectedSectorIdx * 45}deg`;
    radialSectors.querySelectorAll('.rn-sector-node').forEach((node) => {
      const on = Number(node.dataset.idx) === selectedSectorIdx;
      node.classList.toggle('is-selected', on);
      node.style.setProperty('--ssc', on ? '1.12' : '1');
    });
  }

  function setRadialOpen(open) {
    radialOpen = Boolean(open);
    radialArena.classList.toggle('is-closed', !radialOpen);
    radialCoreBtn.setAttribute('aria-expanded', radialOpen ? 'true' : 'false');
    toggleRadialBtn.textContent = radialOpen ? 'Close Dial' : 'Open Dial';
  }

  function setPrecisionTier(nextTier) {
    tier = nextTier;
    precBtns.forEach((b) => b.classList.toggle('is-active', b.dataset.tier === tier));
    const step = tier === 'fine' ? 1 : tier === 'medium' ? 5 : 15;
    scrubSlider.step = String(step);
    precisionDepthLbl.textContent = tier === 'fine' ? 'High Precision (1m)' : tier === 'medium' ? 'Normal (5m)' : 'Coarse (15m)';
    precisionTierReadout.textContent = `${step} min / step`;
    renderScrubberTicks();
    updateScrubber(scrubMinutes);
  }

  function renderScrubberTicks() {
    const count = tier === 'fine' ? 49 : tier === 'medium' ? 33 : 17;
    const html = [];
    for (let i = 0; i < count; i++) {
      const major = i % 4 === 0;
      const baseH = major ? 62 : tier === 'fine' ? 42 : 28;
      html.push(`<div class="ruler-tick${major ? ' major' : ''}" data-tick="${i}" style="height:${baseH}px"></div>`);
    }
    rulerTicks.innerHTML = html.join('');
  }

  function updateScrubber(mins) {
    const step = tier === 'fine' ? 1 : tier === 'medium' ? 5 : 15;
    const snapped = Math.round(mins / step) * step;
    scrubMinutes = Math.max(780, Math.min(1020, snapped));
    scrubSlider.value = String(scrubMinutes);
    const pct = ((scrubMinutes - 780) / (1020 - 780)) * 100;
    const clampedPct = Math.max(6, Math.min(94, pct));
    rulerThumb.style.left = `${clampedPct}%`;
    const hh = String(Math.floor(scrubMinutes / 60)).padStart(2, '0');
    const mm = String(scrubMinutes % 60).padStart(2, '0');
    const timeStr = `${hh}:${mm}`;
    thumbPill.textContent = timeStr;
    scrubberTime.textContent = `${timeStr} · ${step}m snap`;

    const ticks = Array.from(rulerTicks.querySelectorAll('.ruler-tick'));
    const nearestIdx = Math.round((pct / 100) * Math.max(1, ticks.length - 1));
    ticks.forEach((tk, idx) => {
      const dist = Math.abs(idx - nearestIdx);
      const isMajor = tk.classList.contains('major');
      const base = isMajor ? 58 : 28;
      const boost = Math.max(0, 24 - dist * 7);
      tk.style.height = `${base + boost}px`;
      tk.classList.toggle('near', dist <= 1);
    });
  }

  navBtns.forEach((btn) => btn.addEventListener('click', () => navigate(btn.dataset.route)));
  slowMoBtn.addEventListener('click', () => setSlowMotion(!slowMo));

  radialSectors.addEventListener('click', (e) => {
    const btn = e.target.closest('.rn-sector-node');
    if (btn) syncRadialSelection(Number(btn.dataset.idx));
  });
  radialArena.addEventListener('pointermove', (e) => {
    if (!radialOpen) return;
    const rect = radialArena.getBoundingClientRect();
    const dx = e.clientX - (rect.left + rect.width / 2);
    const dy = e.clientY - (rect.top + rect.height / 2);
    if (Math.hypot(dx, dy) < 28) return;
    let angle = (Math.atan2(dy, dx) * 180) / Math.PI + 90;
    if (angle < 0) angle += 360;
    syncRadialSelection(Math.round(angle / 45) % SECTORS.length);
  });
  radialCoreBtn.addEventListener('click', () => setRadialOpen(!radialOpen));
  toggleRadialBtn.addEventListener('click', () => setRadialOpen(!radialOpen));

  precisionTrack.addEventListener('pointermove', (e) => {
    if (e.buttons !== 1) return;
    const rect = precisionTrack.getBoundingClientRect();
    const relX = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const relY = e.clientY - rect.top;
    if (relY > rect.height * 0.68) setPrecisionTier('fine');
    else if (relY > rect.height * 0.42) setPrecisionTier('medium');
    else setPrecisionTier('coarse');
    updateScrubber(Math.round(780 + relX * 240));
  });
  precBtns.forEach((btn) => btn.addEventListener('click', () => setPrecisionTier(btn.dataset.tier)));
  scrubSlider.addEventListener('input', () => updateScrubber(Number(scrubSlider.value)));

  flTabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const f = tab.dataset.fl;
      flTabs.forEach((t) => t.classList.toggle('is-active', t === tab));
      flashCards.forEach((card) => card.classList.toggle('is-hidden', f !== 'all' && card.dataset.group !== f));
    });
  });

  flashGrid.addEventListener('pointermove', (e) => {
    flashCards.forEach((card) => {
      const r = card.getBoundingClientRect();
      card.style.setProperty('--mx', `${e.clientX - r.left}px`);
      card.style.setProperty('--my', `${e.clientY - r.top}px`);
    });
  });

  openInspectorBtn.addEventListener('click', () => {
    lastTriggerEl = openInspectorBtn;
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  });
  closeDlgBtn.addEventListener('click', () => dialog && dialog.close());
  toggleSlowFromDlg.addEventListener('click', () => {
    setSlowMotion(!slowMo);
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
        setSlowMotion(false);
        navigate('radial');
      } else if (msg.action === 'radial_demo') {
        setRadialOpen(true);
        syncRadialSelection((selectedSectorIdx + 2) % SECTORS.length);
      } else if (msg.action === 'toggle_slowmo') {
        setSlowMotion(true);
        navigate('precision');
      }
    }
  });

  buildRadialSectors();
  setPrecisionTier('medium');
})();
