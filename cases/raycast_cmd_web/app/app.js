(function () {
  const viewport = document.getElementById('viewport');
  const starCanvas = document.getElementById('starCanvas');
  const navTabs = Array.from(document.querySelectorAll('.ry-tab'));
  const paletteInput = document.getElementById('paletteInput');
  const matchCounter = document.getElementById('matchCounter');
  const clipList = document.getElementById('clipList');
  const clipPreview = document.getElementById('clipPreview');
  const focusCmdBtn = document.getElementById('focusCmdBtn');

  const kbdRows = document.getElementById('kbdRows');
  const pressedHotkeyLabel = document.getElementById('pressedHotkeyLabel');
  const lightDemoBtn = document.getElementById('lightDemoBtn');

  const extFlts = Array.from(document.querySelectorAll('.ext-flt'));
  const extGrid = document.getElementById('extGrid');
  const exportCsvBtn = document.getElementById('exportCsvBtn');

  const dialog = document.getElementById('hotkeyDialog');
  const openHotkeyBtn = document.getElementById('openHotkeyBtn');
  const closeHotkeyBtn = document.getElementById('closeHotkeyBtn');
  const chordBtns = Array.from(document.querySelectorAll('.ry-chord-btn'));

  const CLIPS = [
    { id: 'c1', title: '#FF6363 · Flame Accent Token', type: 'COLOR', swatch: '#ff6363', code: '--ry-flame: #ff6363; /* Raycast glow */', meta: 'Copied 12s ago · Design Tokens' },
    { id: 'c2', title: 'springCurve(320, 28)', type: 'CODE', swatch: '#3b82f6', code: 'cubic-bezier(0.22, 1, 0.36, 1)', meta: 'Copied 2m ago · Motion Spec' },
    { id: 'c3', title: '#121318 · Glass HUD Surface', type: 'COLOR', swatch: '#121318', code: 'background: rgba(18, 19, 24, 0.92);', meta: 'Copied 9m ago · Stylesheet' },
    { id: 'c4', title: 'git rebase -i HEAD~4', type: 'SHELL', swatch: '#10b981', code: 'git rebase -i HEAD~4 --autosquash', meta: 'Copied 24m ago · Terminal' },
  ];

  const KEY_GRID = [
    ['Esc', '1', '2', '3', 'K', 'Del'],
    ['Tab', 'Q', 'W', 'E', 'R', 'V'],
    ['Shift', 'Cmd', 'Opt', 'Space', '↑', '↓'],
  ];

  const EXTENSIONS = [
    { name: 'Clipboard History', cat: 'Productivity', chord: 'Cmd + Shift + V', cmd: 'Search recent copies' },
    { name: 'GitHub PR Triage', cat: 'Engineering', chord: 'Cmd + G + P', cmd: 'Review open pull requests' },
    { name: 'Color Picker Studio', cat: 'Design', chord: 'Cmd + Shift + C', cmd: 'Pick & copy HEX / OKLCH' },
    { name: 'Quick AI Rewrite', cat: 'Writing', chord: 'Opt + Space', cmd: 'Refine selected paragraph' },
  ];

  let selectedIdx = 0;
  let litKeys = new Set(['Cmd', 'Shift', 'V']);
  let activeRange = 'all';
  let lastTriggerEl = openHotkeyBtn;

  function navigate(route) {
    const target = route || 'clipboard';
    viewport.dataset.page = target;
    navTabs.forEach((b) => b.classList.toggle('is-active', b.dataset.route === target));
    if (target === 'keyboard') applyChord(['Cmd', 'K']);
  }

  function renderPalette() {
    const q = (paletteInput.value || '').trim().toLowerCase();
    const filtered = CLIPS.filter((c) => !q || `${c.title} ${c.type} ${c.code}`.toLowerCase().includes(q));
    matchCounter.textContent = `${filtered.length} items`;
    if (selectedIdx >= filtered.length) selectedIdx = 0;

    clipList.innerHTML = filtered
      .map((c, idx) => `
        <button type="button" class="clip-item ${idx === selectedIdx ? 'is-selected' : ''}" data-idx="${idx}" role="option" aria-selected="${idx === selectedIdx}">
          <span class="clip-title">${c.title}</span>
          <span class="clip-type">${c.type}</span>
        </button>
      `)
      .join('');

    const cur = filtered[selectedIdx];
    if (cur) {
      clipPreview.innerHTML = `
        <div class="preview-swatch" style="background:${cur.swatch}"></div>
        <pre class="preview-code">${cur.code}</pre>
        <div style="font-size:11.5px;color:#90929c">${cur.meta}</div>
      `;
    } else {
      clipPreview.innerHTML = '<div style="color:#90929c;font-size:12px">No clipboard match</div>';
    }
  }

  function renderKeyboard() {
    kbdRows.innerHTML = KEY_GRID.map((row) => `
      <div class="kbd-row">
        ${row.map((k) => `<button type="button" class="keycap ${litKeys.has(k) ? 'is-lit' : ''}" data-k="${k}">${k}</button>`).join('')}
      </div>
    `).join('');
    pressedHotkeyLabel.textContent = `Active Chord: ${Array.from(litKeys).join(' + ') || 'None'}`;
  }

  function applyChord(keys) {
    litKeys = new Set(keys);
    renderKeyboard();
  }

  function renderExtensions() {
    const rows = EXTENSIONS.filter((x) => activeRange === 'all' || x.cat === activeRange);
    extGrid.innerHTML = rows
      .map((x) => `
        <article class="ext-card">
          <span class="ext-cat">${x.cat}</span>
          <strong>${x.name}</strong>
          <div style="font-size:12px;color:#90929c">${x.cmd}</div>
          <code>${x.chord}</code>
        </article>
      `)
      .join('');
  }

  function exportCsv() {
    const rows = EXTENSIONS.filter((x) => activeRange === 'all' || x.cat === activeRange);
    const lines = ['name,category,hotkey,command'].concat(rows.map((r) => `${r.name},${r.cat},${r.chord},${r.cmd}`));
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `raycast-shortcuts-${activeRange}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function initStars() {
    if (!starCanvas || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const ctx = starCanvas.getContext('2d');
    if (!ctx) return;
    const stars = Array.from({ length: 48 }, (_, i) => ({
      x: (i * 197) % 1440,
      y: (i * 89) % 900,
      r: (i % 3) + 0.8,
      a: 0.25 + (i % 5) * 0.12,
    }));
    const render = () => {
      const w = (starCanvas.width = window.innerWidth);
      const h = (starCanvas.height = window.innerHeight);
      ctx.clearRect(0, 0, w, h);
      for (const s of stars) {
        s.y -= 0.18;
        if (s.y < 0) s.y = h;
        ctx.fillStyle = `rgba(255, 99, 99, ${s.a * 0.45})`;
        ctx.beginPath();
        ctx.arc(s.x % w, s.y % h, s.r, 0, Math.PI * 2);
        ctx.fill();
      }
      requestAnimationFrame(render);
    };
    render();
  }

  navTabs.forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));
  paletteInput.addEventListener('input', () => {
    selectedIdx = 0;
    renderPalette();
  });
  clipList.addEventListener('click', (e) => {
    const item = e.target.closest('.clip-item');
    if (!item) return;
    selectedIdx = Number(item.dataset.idx);
    renderPalette();
  });
  focusCmdBtn.addEventListener('click', () => {
    applyChord(['Cmd', 'K']);
    paletteInput.focus();
  });

  kbdRows.addEventListener('click', (e) => {
    const cap = e.target.closest('.keycap');
    if (!cap) return;
    const k = cap.dataset.k;
    if (litKeys.has(k)) litKeys.delete(k);
    else litKeys.add(k);
    renderKeyboard();
  });
  lightDemoBtn.addEventListener('click', () => applyChord(['Opt', 'Space']));

  extFlts.forEach((b) => {
    b.addEventListener('click', () => {
      activeRange = b.dataset.flt;
      extFlts.forEach((x) => x.classList.toggle('is-active', x === b));
      renderExtensions();
    });
  });
  exportCsvBtn.addEventListener('click', exportCsv);

  openHotkeyBtn.addEventListener('click', () => {
    lastTriggerEl = openHotkeyBtn;
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  });
  closeHotkeyBtn.addEventListener('click', () => dialog && dialog.close());
  chordBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      applyChord(btn.dataset.keys.split(','));
      dialog.close();
    });
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
        paletteInput.value = '';
        navigate('clipboard');
        renderPalette();
      } else if (msg.action === 'palette_demo') {
        paletteInput.value = 'Color';
        selectedIdx = 0;
        renderPalette();
      } else if (msg.action === 'keyboard_demo') {
        navigate('keyboard');
        applyChord(['Cmd', 'Shift', 'V', 'K']);
      }
    }
  });

  renderPalette();
  renderKeyboard();
  renderExtensions();
  initStars();
})();
