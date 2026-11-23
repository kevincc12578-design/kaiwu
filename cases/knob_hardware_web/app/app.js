(function () {
  const viewport = document.getElementById('viewport');
  const navBtns = Array.from(document.querySelectorAll('.kb-nav-btn'));
  const kbHeroTitle = document.getElementById('kbHeroTitle');
  const kbHeroLead = document.getElementById('kbHeroLead');
  const kbKeyMatrix = document.getElementById('kbKeyMatrix');
  const kbLcd = document.getElementById('kbLcd');
  const kbDial1 = document.getElementById('kbDial1');
  const kbDial2 = document.getElementById('kbDial2');
  const specTabs = Array.from(document.querySelectorAll('.spec-tab'));
  const kbSpecsGrid = document.getElementById('kbSpecsGrid');
  const kbOrderBtn = document.getElementById('kbOrderBtn');
  const kbUpdatesForm = document.getElementById('kbUpdatesForm');
  const kbUpdatesBtn = document.getElementById('kbUpdatesBtn');
  const kbEmailInput = document.getElementById('kbEmailInput');
  const dialog = document.getElementById('kbDialog');
  const kbDlgTitle = document.getElementById('kbDlgTitle');
  const kbConfirmOrderBtn = document.getElementById('kbConfirmOrderBtn');
  const kbToast = document.getElementById('kbToast');

  const KEYS = [
    ['ESC', 'is-rust'], ['1', ''], ['2', ''], ['3', ''], ['4', ''], ['5', ''], ['6', ''], ['DEL', ''],
    ['TAB', 'is-rust'], ['Q', ''], ['W', ''], ['E', ''], ['R', ''], ['T', ''], ['Y', ''], ['BACK', ''],
    ['FN', 'is-rust'], ['A', ''], ['S', ''], ['D', ''], ['F', ''], ['G', ''], ['SHIFT', 'is-wide'],
  ];

  const SPECS_DATA = [
    { group: 'All', tag: 'CHASSIS', title: 'CNC Anodized Aluminum', body: 'Unibody low-profile frame milled from solid 6063 billet for zero deck flex.' },
    { group: 'Switches', tag: 'LIGHTSWITCH', title: 'Linear 38g Hot-Swap', body: 'Short-travel optical tactile actuation with 1.4mm pre-travel and factory lube.' },
    { group: 'Controls', tag: 'ENCODERS', title: 'Dual Knurled Encoders', body: 'Stepped magnetic detents mapped directly to display brightness and BPM scrub.' },
    { group: 'Keycaps', tag: 'PBT CAPS', title: 'Sculpted Warm Grey & Rust', body: 'Matte concave keycaps with high-contrast legends and rust modifier cluster.' },
  ];

  const COPY_BY_ROUTE = {
    keyboard: ['The low-profile mechanical keyboard of your dreams.', 'The k.no.b.1 is a low-profile mechanical keyboard with uniquely designed keycaps, two programmable knobs, and a feature-filled full-color screen.'],
    numpad: ['Precision wireless numpad with programmable macro wheel.', 'A matching anodized wireless numeric block built to sit cleanly alongside k.no.b.1 on tight studio desks.'],
    keysets: ['Sculpted warm grey & rust low-profile PBT keysets.', 'Replaceable double-shot low-profile legends tailored for rapid finger travel without glare.'],
    lightswitch: ['38g linear optical tactile mechanical lightswitches.', 'Tuned spring weight and dust-proof stem geometry for quiet nocturnal desktop sessions.'],
  };

  let state = { route: 'keyboard', activeRange: 'All', knob1Angle: 35, knob2Angle: 120, brightness: 78, bpm: 124, lastKey: 'READY' };
  let lastTriggerEl = kbOrderBtn;

  function showToast(msg) {
    kbToast.textContent = msg;
    kbToast.classList.add('show');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => kbToast.classList.remove('show'), 1800);
  }

  function renderLcd() {
    kbLcd.innerHTML = `
      <div class="lcd-row"><span>MODE: ${state.route.toUpperCase()}</span><span>KEY: ${state.lastKey}</span></div>
      <div class="lcd-row"><span>LUX ${state.brightness}%</span><span>${state.bpm} BPM</span></div>
    `;
    kbDial1.style.transform = `rotate(${state.knob1Angle}deg)`;
    kbDial2.style.transform = `rotate(${state.knob2Angle}deg)`;
  }

  function renderSpecs() {
    const items = SPECS_DATA.filter((s) => state.activeRange === 'All' || s.group === state.activeRange);
    kbSpecsGrid.innerHTML = items
      .map(
        (s) => `
      <article class="spec-card">
        <span class="spec-tag">${s.tag}</span>
        <h3>${s.title}</h3>
        <p>${s.body}</p>
      </article>`
      )
      .join('');
  }

  function navigate(route) {
    const target = route || 'keyboard';
    state.route = target;
    viewport.dataset.page = target;
    navBtns.forEach((b) => b.classList.toggle('is-active', b.dataset.route === target));
    const pair = COPY_BY_ROUTE[target] || COPY_BY_ROUTE.keyboard;
    kbHeroTitle.textContent = pair[0];
    kbHeroLead.textContent = pair[1];
    renderLcd();
  }

  kbKeyMatrix.innerHTML = KEYS.map(([label, cls]) => `<button type="button" class="kb-key ${cls}" data-k="${label}">${label}</button>`).join('');

  kbKeyMatrix.addEventListener('click', (e) => {
    const btn = e.target.closest('.kb-key');
    if (!btn) return;
    state.lastKey = btn.dataset.k;
    btn.classList.add('is-pressed');
    setTimeout(() => btn.classList.remove('is-pressed'), 120);
    renderLcd();
  });

  function stepDial1(delta) {
    state.knob1Angle = (state.knob1Angle + delta * 30 + 360) % 360;
    state.brightness = Math.max(10, Math.min(100, state.brightness + delta * 6));
    renderLcd();
  }

  function stepDial2(delta) {
    state.knob2Angle = (state.knob2Angle + delta * 30 + 360) % 360;
    state.bpm = Math.max(60, Math.min(180, state.bpm + delta * 4));
    renderLcd();
  }

  kbDial1.addEventListener('click', () => stepDial1(1));
  kbDial2.addEventListener('click', () => stepDial2(1));
  kbDial1.addEventListener('wheel', (e) => { e.preventDefault(); stepDial1(e.deltaY < 0 ? 1 : -1); }, { passive: false });
  kbDial2.addEventListener('wheel', (e) => { e.preventDefault(); stepDial2(e.deltaY < 0 ? 1 : -1); }, { passive: false });

  navBtns.forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));

  specTabs.forEach((t) => {
    t.addEventListener('click', () => {
      state.activeRange = t.dataset.filter;
      specTabs.forEach((x) => x.classList.toggle('is-active', x === t));
      renderSpecs();
    });
  });

  kbOrderBtn.addEventListener('click', () => {
    lastTriggerEl = kbOrderBtn;
    kbDlgTitle.textContent = 'Pre-Order k.no.b.1 ($439 USD)';
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  });

  kbUpdatesForm.addEventListener('submit', (e) => {
    e.preventDefault();
    lastTriggerEl = kbUpdatesBtn;
    kbDlgTitle.textContent = 'Firmware & Restock Dispatch';
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
    if (kbEmailInput.value) showToast(`Queued alerts for ${kbEmailInput.value}`);
  });

  kbConfirmOrderBtn.addEventListener('click', () => {
    dialog.close();
    showToast('k.no.b.1 hardware unit reserved');
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
        navigate('keyboard');
      } else if (msg.action === 'spin_dials') {
        stepDial1(1);
        stepDial2(1);
      } else if (msg.action === 'analytics' || msg.action === 'keysets') {
        navigate('keysets');
      }
    }
  });

  renderLcd();
  renderSpecs();
})();
