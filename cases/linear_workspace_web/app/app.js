(function () {
  const viewport = document.getElementById('viewport');
  const mainStage = document.querySelector('.main-glass');
  const railDock = document.getElementById('railDock');
  const railBtns = Array.from(document.querySelectorAll('.rail-btn'));
  const lnTabs = Array.from(document.querySelectorAll('.ln-tab'));

  const issueList = document.getElementById('issueList');
  const issueCountBadge = document.getElementById('issueCountBadge');
  const fltBtns = Array.from(document.querySelectorAll('.ln-flt'));
  const diffPanel = document.getElementById('diffPanel');
  const diffThemeSelect = document.getElementById('diffThemeSelect');
  const diffModeBtn = document.getElementById('diffModeBtn');
  const pulseSpeedBtn = document.getElementById('pulseSpeedBtn');
  const agentBtn = document.getElementById('agentBtn');
  const exportCsvBtn = document.getElementById('exportCsvBtn');

  const dialog = document.getElementById('issueDialog');
  const openIssueBtn = document.getElementById('openIssueBtn');
  const closeIssueBtn = document.getElementById('closeIssueBtn');
  const createIssueConfirm = document.getElementById('createIssueConfirm');
  const newIssueInput = document.getElementById('newIssueInput');

  let issues = [
    { id: 'KAI-412', title: 'Spring proximity scale curve calibration', state: 'progress' },
    { id: 'KAI-413', title: 'Zero-overflow mobile breakpoint grid pass', state: 'progress' },
    { id: 'KAI-414', title: 'Isometric wire pulse GPU shader fallback', state: 'done' },
    { id: 'KAI-415', title: 'Restore keyboard trigger focus on dialog close', state: 'done' },
  ];

  let activeRange = 'all';
  let scrollByRoute = { issues: 0, isometric: 0, diff: 0, cycles: 0 };
  let fastPulse = false;
  let agentOn = true;
  let lastTriggerEl = openIssueBtn;

  function navigate(route) {
    const prev = viewport.dataset.page || 'issues';
    if (mainStage) scrollByRoute[prev] = mainStage.scrollTop;
    const target = route || 'issues';
    viewport.dataset.page = target;
    railBtns.forEach((b) => b.classList.toggle('is-active', b.dataset.route === target));
    lnTabs.forEach((t) => t.classList.toggle('is-active', t.dataset.route === target));
    if (mainStage) mainStage.scrollTop = scrollByRoute[target] || 0;
  }

  function updateDock(pointerY) {
    const dockRadius = 110;
    const dockGain = 0.28;
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

  function renderIssues() {
    const visible = issues.filter((it) => activeRange === 'all' || it.state === activeRange);
    issueCountBadge.textContent = `${issues.length} Issues`;
    issueList.innerHTML = visible
      .map((it) => `
        <button type="button" class="issue-row" data-id="${it.id}">
          <span class="issue-id">${it.id}</span>
          <span class="issue-title">${it.title}</span>
          <span class="issue-state ${it.state}">${it.state === 'done' ? 'Done' : 'In Progress'}</span>
        </button>
      `)
      .join('');
  }

  function exportCsv() {
    const rows = issues.filter((it) => activeRange === 'all' || it.state === activeRange);
    const lines = ['issue_id,title,state'].concat(rows.map((r) => `${r.id},"${r.title}",${r.state}`));
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `linear-cycle42-${activeRange}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  railDock.addEventListener('pointermove', (e) => updateDock(e.clientY));
  railDock.addEventListener('pointerleave', resetDock);
  railBtns.forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));
  lnTabs.forEach((t) => t.addEventListener('click', () => navigate(t.dataset.route)));

  issueList.addEventListener('click', (e) => {
    const row = e.target.closest('.issue-row');
    if (!row) return;
    const item = issues.find((i) => i.id === row.dataset.id);
    if (item) {
      item.state = item.state === 'done' ? 'progress' : 'done';
      renderIssues();
    }
  });

  fltBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      activeRange = btn.dataset.flt;
      fltBtns.forEach((b) => b.classList.toggle('is-active', b === btn));
      renderIssues();
    });
  });

  diffThemeSelect.addEventListener('change', () => {
    diffPanel.classList.remove('theme-obsidian', 'theme-nord', 'theme-mono');
    diffPanel.classList.add(`theme-${diffThemeSelect.value}`);
  });
  diffModeBtn.addEventListener('click', () => {
    const uni = diffPanel.classList.toggle('is-unified');
    diffModeBtn.textContent = uni ? 'Unified View' : 'Split View';
  });
  pulseSpeedBtn.addEventListener('click', () => {
    fastPulse = !fastPulse;
    document.documentElement.style.setProperty('--ln-dur-dash', fastPulse ? '900ms' : '2400ms');
    pulseSpeedBtn.textContent = fastPulse ? 'Pulse 2.5x' : 'Pulse 1x';
  });
  agentBtn.addEventListener('click', () => {
    agentOn = !agentOn;
    agentBtn.textContent = agentOn ? 'Linear Agent: On' : 'Linear Agent: Off';
  });
  exportCsvBtn.addEventListener('click', exportCsv);

  openIssueBtn.addEventListener('click', () => {
    lastTriggerEl = openIssueBtn;
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  });
  closeIssueBtn.addEventListener('click', () => dialog && dialog.close());
  createIssueConfirm.addEventListener('click', () => {
    const val = (newIssueInput.value || '').trim() || 'KAI-419: Untitled issue';
    issues.unshift({ id: `KAI-${416 + issues.length}`, title: val, state: 'progress' });
    renderIssues();
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
        navigate('issues');
        resetDock();
      } else if (msg.action === 'proximity_demo') {
        const btn = railBtns[1] || railBtns[0];
        if (btn) updateDock(btn.getBoundingClientRect().top + 18);
      } else if (msg.action === 'toggle_diff') {
        navigate('diff');
        diffThemeSelect.value = 'nord';
        diffThemeSelect.dispatchEvent(new Event('change'));
      }
    }
  });

  renderIssues();
})();
