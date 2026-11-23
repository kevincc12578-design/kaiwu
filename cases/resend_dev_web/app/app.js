(function () {
  const viewport = document.getElementById('viewport');
  const beamCanvas = document.getElementById('beamCanvas');
  const navTabs = Array.from(document.querySelectorAll('.rs-tab'));
  const sdkBtns = Array.from(document.querySelectorAll('.sdk-btn'));
  const sdkSlider = document.getElementById('sdkSlider');
  const sdkCode = document.getElementById('sdkCode');

  const sendNowBtn = document.getElementById('sendNowBtn');
  const heroSendBtn = document.getElementById('heroSendBtn');
  const logStream = document.getElementById('logStream');
  const statusBadge = document.getElementById('statusBadge');

  const whBtns = Array.from(document.querySelectorAll('.wh-btn'));
  const webhookList = document.getElementById('webhookList');
  const exportCsvBtn = document.getElementById('exportCsvBtn');
  const toggleEmailThemeBtn = document.getElementById('toggleEmailThemeBtn');
  const emailCanvas = document.getElementById('emailCanvas');

  const dialog = document.getElementById('apiDialog');
  const openApiBtn = document.getElementById('openApiBtn');
  const closeApiBtn = document.getElementById('closeApiBtn');
  const triggerFromDlg = document.getElementById('triggerFromDlg');

  const SNIPPETS = {
    node: `import { Resend } from 'resend';\n\nconst resend = new Resend(process.env.RESEND_API_KEY);\n\nawait resend.emails.send({\n  from: 'Acme <onboarding@resend.dev>',\n  to: ['delivered@resend.dev'],\n  subject: 'Hello World',\n  react: <WelcomeEmail user="Ada" />,\n});`,
    python: `import resend\n\nresend.api_key = os.environ["RESEND_API_KEY"]\n\nresend.Emails.send({\n  "from": "Acme <onboarding@resend.dev>",\n  "to": ["delivered@resend.dev"],\n  "subject": "Hello World",\n  "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"\n})`,
    go: `client := resend.NewClient(apiKey)\nparams := &resend.SendEmailRequest{\n    From:    "Acme <onboarding@resend.dev>",\n    To:      []string{"delivered@resend.dev"},\n    Subject: "Hello World",\n    Html:    "<strong>Verify token active</strong>",\n}\nsent, _ := client.Emails.Send(params)`,
    rust: `let resend = Resend::default();\nlet email = CreateEmailBaseOptions::new(\n  "Acme <onboarding@resend.dev>",\n  ["delivered@resend.dev"],\n  "Hello World",\n).with_html("<strong>Ready</strong>");\nresend.emails.send(email).await?;`,
  };

  let logs = [
    { id: 'em_4a9f0c21', to: 'delivered@resend.dev', ms: 18, status: 200 },
    { id: 'em_4a9f0b88', to: 'team@acme.io', ms: 21, status: 200 },
  ];

  const WEBHOOKS = [
    { id: 'wh_901', event: 'email.delivered', recipient: 'ada@vercel.com', state: 'delivered', time: '11:42:18' },
    { id: 'wh_902', event: 'email.opened', recipient: 'dev@linear.app', state: 'opened', time: '11:41:52' },
    { id: 'wh_903', event: 'email.delivered', recipient: 'ops@raycast.com', state: 'delivered', time: '11:40:11' },
    { id: 'wh_904', event: 'email.bounced', recipient: 'old@legacy.org', state: 'bounced', time: '11:39:04' },
  ];

  let activeSdk = 'node';
  let activeRange = 'all';
  let seq = 100;
  let lastTriggerEl = openApiBtn;

  function navigate(route) {
    const target = route || 'testmode';
    viewport.dataset.page = target;
    navTabs.forEach((b) => b.classList.toggle('is-active', b.dataset.route === target));
    if (target === 'reactemail') emailCanvas.classList.add('is-light');
  }

  function selectSdk(sdk) {
    activeSdk = sdk || 'node';
    sdkBtns.forEach((btn) => {
      const on = btn.dataset.sdk === activeSdk;
      btn.classList.toggle('is-active', on);
      if (on && sdkSlider) {
        sdkSlider.style.width = `${btn.offsetWidth}px`;
        sdkSlider.style.transform = `translateX(${btn.offsetLeft - 3}px)`;
      }
    });
    sdkCode.textContent = SNIPPETS[activeSdk] || SNIPPETS.node;
  }

  function renderLogs() {
    logStream.innerHTML = logs
      .map((l) => `<div class="log-entry"><span>{ "id": "${l.id}", "to": "${l.to}" }</span><span class="ok">HTTP ${l.status} · ${l.ms}ms</span></div>`)
      .join('');
  }

  function sendTestEmail() {
    seq += 1;
    const ms = 14 + (seq % 9);
    const id = `em_4a9f${seq.toString(16)}`;
    logs.unshift({ id, to: `dev+${seq}@resend.dev`, ms, status: 200 });
    logs = logs.slice(0, 6);
    statusBadge.textContent = `HTTP 200 OK · ${ms}ms`;
    renderLogs();
  }

  function renderWebhooks() {
    const rows = WEBHOOKS.filter((w) => activeRange === 'all' || w.state === activeRange);
    webhookList.innerHTML = rows
      .map((w) => `<div class="wh-row"><span>${w.event} · ${w.recipient}</span><span class="wh-pill ${w.state}">${w.state} · ${w.time}</span></div>`)
      .join('');
  }

  function exportCsv() {
    const rows = WEBHOOKS.filter((w) => activeRange === 'all' || w.state === activeRange);
    const lines = ['id,event,recipient,state,time'].concat(rows.map((r) => `${r.id},${r.event},${r.recipient},${r.state},${r.time}`));
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `resend-webhooks-${activeRange}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function initBeamCanvas() {
    if (!beamCanvas || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const ctx = beamCanvas.getContext('2d');
    if (!ctx) return;
    let t = 0;
    const draw = () => {
      const w = (beamCanvas.width = window.innerWidth);
      const h = (beamCanvas.height = window.innerHeight);
      ctx.clearRect(0, 0, w, h);
      const grad = ctx.createRadialGradient(w * (0.5 + Math.sin(t) * 0.08), 80, 20, w * 0.5, 160, w * 0.65);
      grad.addColorStop(0, 'rgba(255, 255, 255, 0.075)');
      grad.addColorStop(0.45, 'rgba(16, 185, 129, 0.04)');
      grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, w, h);
      t += 0.014;
      requestAnimationFrame(draw);
    };
    draw();
  }

  navTabs.forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));
  sdkBtns.forEach((b) => b.addEventListener('click', () => selectSdk(b.dataset.sdk)));
  sendNowBtn.addEventListener('click', sendTestEmail);
  heroSendBtn.addEventListener('click', sendTestEmail);

  whBtns.forEach((b) => {
    b.addEventListener('click', () => {
      activeRange = b.dataset.flt;
      whBtns.forEach((x) => x.classList.toggle('is-active', x === b));
      renderWebhooks();
    });
  });

  exportCsvBtn.addEventListener('click', exportCsv);
  toggleEmailThemeBtn.addEventListener('click', () => emailCanvas.classList.toggle('is-light'));

  openApiBtn.addEventListener('click', () => {
    lastTriggerEl = openApiBtn;
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  });
  closeApiBtn.addEventListener('click', () => dialog && dialog.close());
  triggerFromDlg.addEventListener('click', () => {
    sendTestEmail();
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
      if (msg.action === 'normal') navigate('testmode');
      else if (msg.action === 'send_test') sendTestEmail();
      else if (msg.action === 'webhooks') navigate('webhooks');
    }
  });

  selectSdk('node');
  renderLogs();
  renderWebhooks();
  initBeamCanvas();
})();
