(function () {
  const viewport = document.getElementById('viewport');
  const mainStage = document.querySelector('.main-glass');
  const railDock = document.getElementById('railDock');
  const railBtns = Array.from(document.querySelectorAll('.rail-btn'));
  const amTabs = Array.from(document.querySelectorAll('.am-tab'));
  const railHoursLabel = document.getElementById('railHoursLabel');

  const transcriptLines = Array.from(document.querySelectorAll('.tr-line'));
  const cycleLineBtn = document.getElementById('cycleLineBtn');
  const askCapsule = document.getElementById('askCapsule');
  const toggleAskBtn = document.getElementById('toggleAskBtn');
  const askTriggerTopBtn = document.getElementById('askTriggerTopBtn');
  const askReplyText = document.getElementById('askReplyText');
  const askPromptBtns = Array.from(document.querySelectorAll('.ask-prompt-btn'));

  const amFlts = Array.from(document.querySelectorAll('.am-flt'));
  const scheduleGrid = document.getElementById('scheduleGrid');
  const exportCsvBtn = document.getElementById('exportCsvBtn');

  const dialog = document.getElementById('eventDialog');
  const openEventBtn = document.getElementById('openEventBtn');
  const closeEventBtn = document.getElementById('closeEventBtn');
  const confirmAddBlock = document.getElementById('confirmAddBlock');
  const newBlockTitle = document.getElementById('newBlockTitle');
  const newBlockDay = document.getElementById('newBlockDay');

  let blocks = [
    { day: 'Mon 24', cat: 'Deep Work', title: 'Spring Physics Audit', hours: 8 },
    { day: 'Tue 25', cat: 'Sync', title: '47s AI Summary Sync', hours: 4 },
    { day: 'Wed 26', cat: 'Focus', title: 'Radial Scrubber Polish', hours: 8 },
    { day: 'Thu 27', cat: 'Deep Work', title: 'Ask Amie Capsule UX', hours: 6 },
  ];

  let activeRange = 'all';
  let highlightIdx = 0;
  let scrollByRoute = { notes: 0, week: 0, onboard: 0, faq: 0 };
  let lastTriggerEl = openEventBtn;

  function navigate(route) {
    const prev = viewport.dataset.page || 'notes';
    if (mainStage) scrollByRoute[prev] = mainStage.scrollTop;
    const target = route || 'notes';
    viewport.dataset.page = target;
    railBtns.forEach((b) => b.classList.toggle('is-active', b.dataset.route === target));
    amTabs.forEach((t) => t.classList.toggle('is-active', t.dataset.route === target));
    if (mainStage) mainStage.scrollTop = scrollByRoute[target] || 0;
  }

  function updateDock(pointerY) {
    const dockRadius = 110;
    const dockGain = 0.25;
    railBtns.forEach((btn) => {
      const rect = btn.getBoundingClientRect();
      const center = rect.top + rect.height / 2;
      const dist = Math.abs(pointerY - center);
      const ratio = Math.max(0, 1 - dist / dockRadius);
      const scale = 1 + ratio * dockGain;
      const shift = ratio * 4;
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

  function renderBlocks() {
    const visible = blocks.filter((b) => activeRange === 'all' || b.cat === activeRange);
    const totalHours = blocks.reduce((acc, b) => acc + b.hours, 0);
    railHoursLabel.textContent = `${totalHours}h`;
    scheduleGrid.innerHTML = visible
      .map((b) => `
        <article class="sched-card">
          <span class="sched-tag">${b.day} · ${b.cat}</span>
          <strong>${b.title}</strong>
          <span>${b.hours}h committed</span>
        </article>
      `)
      .join('');
  }

  function setAskExpanded(force) {
    const open = typeof force === 'boolean' ? force : !askCapsule.classList.contains('is-expanded');
    askCapsule.classList.toggle('is-expanded', open);
    toggleAskBtn.textContent = open ? 'Collapse' : 'Expand';
  }

  function exportCsv() {
    const rows = blocks.filter((b) => activeRange === 'all' || b.cat === activeRange);
    const lines = ['day,category,title,hours'].concat(rows.map((r) => `${r.day},${r.cat},"${r.title}",${r.hours}`));
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `amie-week47-${activeRange}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  railDock.addEventListener('pointermove', (e) => updateDock(e.clientY));
  railDock.addEventListener('pointerleave', resetDock);
  railBtns.forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));
  amTabs.forEach((t) => t.addEventListener('click', () => navigate(t.dataset.route)));

  transcriptLines.forEach((line, idx) => {
    line.addEventListener('click', () => {
      highlightIdx = idx;
      transcriptLines.forEach((l, i) => l.classList.toggle('is-highlighted', i === highlightIdx));
      blocks.push({
        day: 'Fri 28',
        cat: line.dataset.cat || 'Focus',
        title: line.dataset.task || 'Action Item',
        hours: Number(line.dataset.hrs || 2),
      });
      renderBlocks();
    });
  });

  cycleLineBtn.addEventListener('click', () => {
    highlightIdx = (highlightIdx + 1) % transcriptLines.length;
    transcriptLines.forEach((l, i) => l.classList.toggle('is-highlighted', i === highlightIdx));
  });

  toggleAskBtn.addEventListener('click', () => setAskExpanded());
  askTriggerTopBtn.addEventListener('click', () => setAskExpanded(true));
  askPromptBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      askReplyText.textContent = `Amie scheduled: "${btn.dataset.prompt}" into Week 47.`;
    });
  });

  amFlts.forEach((btn) => {
    btn.addEventListener('click', () => {
      activeRange = btn.dataset.flt;
      amFlts.forEach((b) => b.classList.toggle('is-active', b === btn));
      renderBlocks();
    });
  });

  exportCsvBtn.addEventListener('click', exportCsv);

  openEventBtn.addEventListener('click', () => {
    lastTriggerEl = openEventBtn;
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  });
  closeEventBtn.addEventListener('click', () => dialog && dialog.close());
  confirmAddBlock.addEventListener('click', () => {
    const title = (newBlockTitle.value || '').trim() || 'Team sync block';
    blocks.push({ day: `${newBlockDay.value} 28`, cat: 'Focus', title, hours: 3 });
    renderBlocks();
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
        navigate('notes');
        setAskExpanded(false);
        resetDock();
      } else if (msg.action === 'proximity_demo') {
        const btn = railBtns[1] || railBtns[0];
        if (btn) updateDock(btn.getBoundingClientRect().top + 18);
      } else if (msg.action === 'ask_amie') {
        setAskExpanded(true);
        askReplyText.textContent = 'Amie extracted 3 focus tasks into Week 47.';
      }
    }
  });

  renderBlocks();
})();
