(function () {
  const viewport = document.getElementById('viewport');
  const mainStage = document.querySelector('.main-glass') || document.getElementById('main-stage');
  const railDock = document.getElementById('railDock');
  const railBtns = Array.from(document.querySelectorAll('.rail-btn'));
  const segBtns = Array.from(document.querySelectorAll('.seg-btn'));
  const plannerGrid = document.getElementById('plannerGrid');
  const scheduleRows = document.getElementById('scheduleRows');
  const railTotalHours = document.getElementById('railTotalHours');
  const sumCommittedVal = document.getElementById('sumCommittedVal');
  const sumBufferVal = document.getElementById('sumBufferVal');
  const sumBlocksVal = document.getElementById('sumBlocksVal');
  const pfBtns = Array.from(document.querySelectorAll('.pf-btn'));
  const exportCsvBtn = document.getElementById('exportCsvBtn');
  const dialog = document.getElementById('taskDialog');
  const openNewTaskBtn = document.getElementById('openNewTaskBtn');
  const confirmAddTaskBtn = document.getElementById('confirmAddTaskBtn');

  const MEMBERS = [
    { id: 'mia', name: 'Mia Chen', role: 'Design Lead · 40h' },
    { id: 'leo', name: 'Leo Novak', role: 'Systems Eng · 40h' },
    { id: 'sofia', name: 'Sofia Reyes', role: 'Product Dir · 40h' }
  ];

  const DAY_NAMES = ['Mon 23', 'Tue 24', 'Wed 25', 'Thu 26', 'Fri 27'];

  let tasks = [
    { id: 1, member: 'mia', day: 0, project: 'Brand', label: 'Type scale pass', hours: 8 },
    { id: 2, member: 'mia', day: 1, project: 'Design', label: 'Paper cards', hours: 8 },
    { id: 3, member: 'mia', day: 2, project: 'Brand', label: 'Press export', hours: 8 },
    { id: 4, member: 'mia', day: 4, project: 'Design', label: 'Critique sync', hours: 8 },
    { id: 5, member: 'leo', day: 0, project: 'Core', label: 'Calendar engine', hours: 8 },
    { id: 6, member: 'leo', day: 1, project: 'Core', label: 'Sync cursor API', hours: 8 },
    { id: 7, member: 'leo', day: 2, project: 'Core', label: 'Hour rollup', hours: 8 },
    { id: 8, member: 'leo', day: 3, project: 'Core', label: 'CSV serializer', hours: 8 },
    { id: 9, member: 'sofia', day: 0, project: 'Brand', label: 'Editorial brief', hours: 8 },
    { id: 10, member: 'sofia', day: 2, project: 'Design', label: 'Studio review', hours: 8 },
    { id: 11, member: 'sofia', day: 3, project: 'Core', label: 'Release notes', hours: 12 }
  ];

  let nextTaskId = 12;
  let activeRange = 'all';
  let lastTriggerEl = openNewTaskBtn;

  function navigate(route) {
    const target = route || 'weeks';
    viewport.dataset.page = target;
    mainStage.scrollTop = 0;

    railBtns.forEach((btn) => btn.classList.toggle('is-active', btn.dataset.route === target));
    segBtns.forEach((btn) => btn.classList.toggle('is-active', btn.dataset.route === target));
    plannerGrid.classList.toggle('is-day-focus', target === 'days');
  }

  function updateDock(pointerY) {
    const dockRadius = 110;
    const dockGain = 0.2;
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

  function renderSchedule() {
    const visibleTasks = tasks.filter((t) => activeRange === 'all' || t.project === activeRange);

    scheduleRows.innerHTML = MEMBERS.map((member) => {
      const memberAllTasks = tasks.filter((t) => t.member === member.id);
      const memberHours = memberAllTasks.reduce((sum, t) => sum + t.hours, 0);
      const pct = Math.min(100, Math.round((memberHours / 40) * 100));
      const overClass = memberHours > 40 ? ' is-over' : '';
      const statusText = memberHours > 40 ? `${memberHours - 40}h over` : `${40 - memberHours}h open`;

      const cellsHtml = DAY_NAMES.map((_, dayIdx) => {
        const dayChips = visibleTasks
          .filter((t) => t.member === member.id && t.day === dayIdx)
          .map((t) => `
            <div class="task-chip proj-${t.project}">
              <div class="chip-info">
                <span class="chip-title">${t.label}</span>
                <span class="chip-meta">${t.project} · ${t.hours}h</span>
              </div>
              <button class="chip-del" type="button" data-del-id="${t.id}" aria-label="Remove ${t.label}">×</button>
            </div>
          `)
          .join('');
        return `
          <div class="day-cell">
            ${dayChips}
            <button class="cell-add-btn" type="button" data-add-member="${member.id}" data-add-day="${dayIdx}">+ 4h</button>
          </div>
        `;
      }).join('');

      return `
        <div class="member-row" data-member="${member.id}">
          <div class="member-cell">
            <span class="m-name">${member.name}</span>
            <span class="m-role">${member.role}</span>
          </div>
          ${cellsHtml}
          <div class="total-cell">
            <span class="load-text">${memberHours}h of 40h</span>
            <div class="load-bar-track"><div class="load-bar-fill${overClass}" style="width:${pct}%"></div></div>
            <span class="load-note">${statusText}</span>
          </div>
        </div>
      `;
    }).join('');

    const totalCommitted = visibleTasks.reduce((sum, t) => sum + t.hours, 0);
    const totalCapacity = MEMBERS.length * 40;
    const bufferHours = Math.max(0, totalCapacity - totalCommitted);
    railTotalHours.textContent = `${totalCommitted}h`;
    sumCommittedVal.textContent = `${totalCommitted}h / ${totalCapacity}h`;
    sumBufferVal.textContent = `${bufferHours}h available`;
    sumBlocksVal.textContent = `${visibleTasks.length} scheduled`;
  }

  function exportCsv() {
    const visible = tasks.filter((t) => activeRange === 'all' || t.project === activeRange);
    const header = 'id,member,day,project,task,hours\n';
    const body = visible
      .map((t) => `${t.id},${t.member},${DAY_NAMES[t.day]},${t.project},"${t.label}",${t.hours}`)
      .join('\n');
    const blob = new Blob([header + body], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `weeksync-${activeRange.toLowerCase()}-w48.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  scheduleRows.addEventListener('click', (e) => {
    const delBtn = e.target.closest('[data-del-id]');
    if (delBtn) {
      const id = Number(delBtn.dataset.delId);
      tasks = tasks.filter((t) => t.id !== id);
      renderSchedule();
      return;
    }
    const addBtn = e.target.closest('[data-add-member]');
    if (addBtn) {
      const proj = activeRange === 'all' ? 'Brand' : activeRange;
      tasks.push({
        id: nextTaskId++,
        member: addBtn.dataset.addMember,
        day: Number(addBtn.dataset.addDay),
        project: proj,
        label: 'Focus sprint',
        hours: 4
      });
      renderSchedule();
    }
  });

  railDock.addEventListener('mousemove', (e) => updateDock(e.clientY));
  railDock.addEventListener('mouseleave', resetDock);

  railBtns.forEach((btn) => btn.addEventListener('click', () => navigate(btn.dataset.route)));
  segBtns.forEach((btn) => btn.addEventListener('click', () => navigate(btn.dataset.route)));

  pfBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      activeRange = btn.dataset.filter;
      pfBtns.forEach((b) => b.classList.toggle('is-active', b === btn));
      renderSchedule();
    });
  });

  exportCsvBtn.addEventListener('click', exportCsv);

  openNewTaskBtn.addEventListener('click', () => {
    lastTriggerEl = openNewTaskBtn;
    if (dialog && typeof dialog.showModal === 'function') {
      dialog.showModal();
    }
  });

  confirmAddTaskBtn.addEventListener('click', () => {
    const member = document.getElementById('dlgMember').value;
    const day = Number(document.getElementById('dlgDay').value);
    const project = document.getElementById('dlgProject').value;
    const label = document.getElementById('dlgLabel').value.trim() || 'Studio task';
    const hours = Math.max(1, Math.min(12, Number(document.getElementById('dlgHours').value) || 4));
    tasks.push({ id: nextTaskId++, member, day, project, label, hours });
    dialog.close();
    renderSchedule();
  });

  if (dialog) {
    dialog.addEventListener('close', () => {
      if (lastTriggerEl && typeof lastTriggerEl.focus === 'function') {
        lastTriggerEl.focus();
      }
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
      document.querySelectorAll('.kaiwu-eu-highlight').forEach((n) => n.classList.remove('kaiwu-eu-highlight'));
      const node = document.querySelector(`[data-eu-id="${msg.eu_id}"]`);
      if (node) {
        node.classList.add('kaiwu-eu-highlight');
        node.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    } else if (msg.type === 'KAIWU_PREVIEW_ACTION') {
      if (msg.action === 'normal') {
        navigate('weeks');
        resetDock();
      } else if (msg.action === 'proximity_demo') {
        const secondBtn = railBtns[1];
        if (secondBtn) {
          const rect = secondBtn.getBoundingClientRect();
          updateDock(rect.top + rect.height / 2);
        }
      } else if (msg.action === 'analytics') {
        navigate(viewport.dataset.page === 'days' ? 'weeks' : 'days');
      }
    }
  });

  renderSchedule();
})();
