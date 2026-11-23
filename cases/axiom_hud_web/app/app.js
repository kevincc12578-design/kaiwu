(function () {
  const viewport = document.getElementById('viewport');
  const navLinks = Array.from(document.querySelectorAll('.ax-link'));
  const hudTabs = Array.from(document.querySelectorAll('.hud-tab'));
  const modeBtns = Array.from(document.querySelectorAll('.mode-btn'));
  const builderControls = document.getElementById('builderControls');
  const aplInput = document.getElementById('aplInput');
  const timeSelect = document.getElementById('timeWindowSelect');
  const runAplBtn = document.getElementById('runAplBtn');
  const jumpHudBtn = document.getElementById('jumpHudBtn');
  const runLatencyLabel = document.getElementById('runLatencyLabel');
  const chartTitle = document.getElementById('chartTitle');
  const barGrid = document.getElementById('barGrid');
  const eventsTbody = document.getElementById('eventsTbody');
  const fltBtns = Array.from(document.querySelectorAll('.flt-btn'));
  const exportCsvBtn = document.getElementById('exportCsvBtn');
  const dialog = document.getElementById('queryDialog');
  const startFreeBtn = document.getElementById('startFreeBtn');
  const heroStartBtn = document.getElementById('heroStartBtn');
  const openDialogTopBtn = document.getElementById('openDialogTopBtn');
  const confirmRunFromDialog = document.getElementById('confirmRunFromDialog');

  let activeRange = 'all';
  let activeWindow = '30m';
  let runTick = 0;
  let lastTriggerEl = startFreeBtn;

  const LOG_ROWS = [
    { ts: '11:24:18.104', service: 'payment-service', reason: 'insufficient_funds', status: 402, dur: 18.4, trace: 'tr_94bc11a0' },
    { ts: '11:24:17.882', service: 'edge-proxy', reason: 'upstream_timeout', status: 504, dur: 41.2, trace: 'tr_94bc117b' },
    { ts: '11:24:17.410', service: 'payment-service', reason: 'card_declined', status: 402, dur: 15.9, trace: 'tr_94bc1152' },
    { ts: '11:24:16.955', service: 'auth-core', reason: 'token_expired', status: 401, dur: 9.8, trace: 'tr_94bc112e' },
    { ts: '11:24:16.320', service: 'payment-service', reason: 'risk_threshold', status: 403, dur: 22.7, trace: 'tr_94bc10ff' },
    { ts: '11:24:15.790', service: 'edge-proxy', reason: 'ok_dispatched', status: 200, dur: 8.1, trace: 'tr_94bc10a3' },
  ];

  const SERIES_BY_WIN = {
    '15m': [42, 56, 51, 68, 75, 71, 86, 92, 65, 74, 88, 94, 80, 69, 85, 89],
    '30m': [38, 46, 60, 54, 72, 86, 93, 74, 62, 71, 84, 90, 66, 75, 81, 88],
    '6h': [29, 36, 48, 62, 57, 76, 85, 96, 80, 64, 59, 73, 81, 87, 78, 91],
    '24h': [49, 41, 39, 47, 60, 68, 75, 84, 94, 86, 78, 70, 64, 75, 83, 89],
  };

  function navigate(route) {
    const target = route || 'query';
    viewport.dataset.page = target;
    navLinks.forEach((l) => l.classList.toggle('is-active', l.dataset.route === target));
    hudTabs.forEach((t) => t.classList.toggle('is-active', t.dataset.route === target));

    if (target === 'dashboards') {
      chartTitle.textContent = 'DASHBOARD OVERVIEW · P95 LATENCY & DECLINE REASONS';
      aplInput.value = "['payment-service']\n| summarize hits = count(), p95 = percentile(duration_ms, 95) by ['decline.reason']\n| sort by p95 desc";
    } else if (target === 'stream') {
      chartTitle.textContent = 'LIVE TAIL STREAM · REAL-TIME EVENT PIPE';
    } else {
      chartTitle.textContent = `EVENT DISTRIBUTION (${activeWindow.toUpperCase()} BUCKETS)`;
    }
    renderSeriesAndRows();
  }

  function renderSeriesAndRows() {
    const base = SERIES_BY_WIN[activeWindow] || SERIES_BY_WIN['30m'];
    barGrid.innerHTML = base
      .map((val, idx) => {
        const adj = Math.max(14, Math.min(99, val + ((runTick * 7 + idx * 3) % 13) - 6));
        const dimCls = idx % 5 === 3 ? ' is-dim' : '';
        return `<div class="bar-col" title="Bucket #${idx + 1}: ${adj}%"><div class="bar-fill${dimCls}" style="height:${adj}%"></div></div>`;
      })
      .join('');

    const filtered = LOG_ROWS.filter((row) => activeRange === 'all' || row.service === activeRange);
    eventsTbody.innerHTML = filtered
      .map((row) => {
        const cls = row.status >= 400 ? 'status-warn' : 'status-ok';
        return `<tr><td>${row.ts}</td><td>${row.service}</td><td>${row.reason}</td><td class="${cls}">${row.status}</td><td>${(row.dur + (runTick % 4) * 0.4).toFixed(1)} ms</td><td>${row.trace}</td></tr>`;
      })
      .join('');
  }

  function runAplQuery() {
    runTick += 1;
    const ms = 14 + ((runTick * 5) % 11);
    const scanned = (4.82 + runTick * 0.14).toFixed(2);
    runLatencyLabel.textContent = `Last execution: ${ms} ms · ${scanned}M events scanned`;
    renderSeriesAndRows();
  }

  function exportCsv() {
    const filtered = LOG_ROWS.filter((row) => activeRange === 'all' || row.service === activeRange);
    const header = '_time,service,decline_reason,status,duration_ms,trace_id\n';
    const body = filtered.map((r) => `${r.ts},${r.service},${r.reason},${r.status},${r.dur},${r.trace}`).join('\n');
    const blob = new Blob([header + body], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `axiom-${activeRange}-${activeWindow}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  navLinks.forEach((l) => l.addEventListener('click', () => navigate(l.dataset.route)));
  hudTabs.forEach((t) => t.addEventListener('click', () => navigate(t.dataset.route)));

  modeBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const mode = btn.dataset.mode;
      modeBtns.forEach((b) => b.classList.toggle('is-active', b === btn));
      builderControls.classList.toggle('is-hidden', mode !== 'builder');
    });
  });

  timeSelect.addEventListener('change', () => {
    activeWindow = timeSelect.value;
    chartTitle.textContent = `EVENT DISTRIBUTION (${activeWindow.toUpperCase()} BUCKETS)`;
    runAplQuery();
  });

  runAplBtn.addEventListener('click', runAplQuery);
  jumpHudBtn.addEventListener('click', () => {
    runAplQuery();
    aplInput.focus();
  });

  fltBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      activeRange = btn.dataset.filter;
      fltBtns.forEach((b) => b.classList.toggle('is-active', b === btn));
      renderSeriesAndRows();
    });
  });

  exportCsvBtn.addEventListener('click', exportCsv);

  function openDialogFrom(el) {
    lastTriggerEl = el;
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  }

  startFreeBtn.addEventListener('click', () => openDialogFrom(startFreeBtn));
  heroStartBtn.addEventListener('click', () => openDialogFrom(heroStartBtn));
  openDialogTopBtn.addEventListener('click', () => openDialogFrom(openDialogTopBtn));
  confirmRunFromDialog.addEventListener('click', () => {
    dialog.close();
    runAplQuery();
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
      const node = document.querySelector(`[data-eu-id="${msg.eu_id}"]`);
      if (node) {
        node.classList.add('kaiwu-eu-highlight');
        node.setAttribute('data-kaiwu-active', 'true');
        node.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    } else if (msg.type === 'KAIWU_PREVIEW_ACTION') {
      if (msg.action === 'normal') {
        navigate('query');
      } else if (msg.action === 'run_apl') {
        runAplQuery();
      } else if (msg.action === 'analytics' || msg.action === 'dashboards') {
        navigate('dashboards');
      }
    }
  });

  renderSeriesAndRows();
})();
