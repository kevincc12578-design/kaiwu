(function () {
  const viewport = document.getElementById('viewport');
  const navBtns = Array.from(document.querySelectorAll('.ng-nav-btn'));
  const ngHeroTitle = document.getElementById('ngHeroTitle');
  const ngHeroBio = document.getElementById('ngHeroBio');
  const ngRadioBtn = document.getElementById('ngRadioBtn');
  const ngToggleStream = document.getElementById('ngToggleStream');
  const ngRadioState = document.getElementById('ngRadioState');
  const ngCartBtn = document.getElementById('ngCartBtn');
  const ngQuickAddBtn = document.getElementById('ngQuickAddBtn');
  const logTabs = Array.from(document.querySelectorAll('.log-tab'));
  const ngLogsList = document.getElementById('ngLogsList');
  const dialog = document.getElementById('ngDialog');
  const dlgCartCount = document.getElementById('dlgCartCount');
  const dlgCartEur = document.getElementById('dlgCartEur');
  const ngAddBookDlg = document.getElementById('ngAddBookDlg');
  const ngClearCartBtn = document.getElementById('ngClearCartBtn');
  const ngToast = document.getElementById('ngToast');

  const LOGS = [
    { cat: 'Node', key: 'PROJECT', val: 'Rado Go Gen2' },
    { cat: 'Node', key: 'NOGOODNODE', val: 'ONLINE · BLOCK 870142' },
    { cat: 'Shop', key: 'MONOGRAPH', val: 'VOL. 1 · 184/400 LEFT' },
    { cat: 'Audio', key: 'STREAM', val: 'SYNTHWAVE ARCHIVE 04' },
  ];

  const ROUTE_COPY = {
    work: ['Illustration inspired by retro tech and fuelled by open web counterculture.', "I'm Thomas, aka NoGood, an illustrator based in Amsterdam. Working under the pseudonym since 2021 to experiment with sharp grid systems and counterculture art."],
    sketchbook: ['Raw ink studies, visor wireframes & acid halftone plates.', 'Unfiltered daily experiments exploring cyberpunk helmets, brutalist poster grids and monospaced glyph collisions.'],
    shop: ['Limited Monograph & Risograph Print Artifacts.', 'Self-published hardcover editions and tactile numbered prints ships straight from Amsterdam with BTC or SEPA.'],
    about: ['Independent studio opposing homogenous SaaS polish.', 'Building loud editorial surfaces with 0px corners, solid inks and unapologetic typography since 2021.'],
    now: ['Currently shipping Monograph Vol. 1 & radio mixtapes.', 'Available for bold editorial covers, album artwork and kinetic web commissions.'],
  };

  let state = { route: 'work', radioOn: false, cartCount: 0, cartEur: 0, activeRange: 'All' };
  let lastTriggerEl = ngCartBtn;

  function showToast(msg) {
    ngToast.textContent = msg;
    ngToast.classList.add('show');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => ngToast.classList.remove('show'), 1800);
  }

  function syncUi() {
    ngRadioBtn.classList.toggle('playing', state.radioOn);
    ngRadioBtn.textContent = state.radioOn ? '||| ON AIR' : '||| NOGOOD RADIO';
    ngRadioState.textContent = state.radioOn ? 'CHANNEL: SYNTHWAVE STREAMING' : 'CHANNEL: STANDBY';
    ngToggleStream.textContent = state.radioOn ? 'STOP STREAM' : 'PLAY STREAM';
    ngCartBtn.textContent = `CART €${state.cartEur.toFixed(2)}`;
    dlgCartCount.textContent = String(state.cartCount);
    dlgCartEur.textContent = `€${state.cartEur.toFixed(2)}`;
  }

  function renderLogs() {
    const items = LOGS.filter((l) => state.activeRange === 'All' || l.cat === state.activeRange);
    ngLogsList.innerHTML = items.map((l) => `<div class="ng-log-row"><span>${l.key}</span><b>${l.val}</b></div>`).join('');
  }

  function navigate(route) {
    const target = route || 'work';
    state.route = target;
    viewport.dataset.page = target;
    navBtns.forEach((b) => b.classList.toggle('is-active', b.dataset.route === target));
    const pair = ROUTE_COPY[target] || ROUTE_COPY.work;
    ngHeroTitle.textContent = pair[0];
    ngHeroBio.textContent = pair[1];
  }

  function toggleRadio() {
    state.radioOn = !state.radioOn;
    syncUi();
    showToast(state.radioOn ? 'NOGOOD RADIO LIVE' : 'RADIO STANDBY');
  }

  function addMonograph() {
    state.cartCount += 1;
    state.cartEur += 70;
    syncUi();
    showToast('Added The NoGood Book (€70)');
  }

  navBtns.forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));
  ngRadioBtn.addEventListener('click', toggleRadio);
  ngToggleStream.addEventListener('click', toggleRadio);
  ngQuickAddBtn.addEventListener('click', addMonograph);

  ngCartBtn.addEventListener('click', () => {
    lastTriggerEl = ngCartBtn;
    syncUi();
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  });

  ngAddBookDlg.addEventListener('click', () => {
    addMonograph();
    dialog.close();
  });

  ngClearCartBtn.addEventListener('click', () => {
    state.cartCount = 0;
    state.cartEur = 0;
    syncUi();
    dialog.close();
    showToast('Cart cleared');
  });

  if (dialog) {
    dialog.addEventListener('close', () => {
      if (lastTriggerEl && typeof lastTriggerEl.focus === 'function') lastTriggerEl.focus();
    });
  }

  logTabs.forEach((t) => {
    t.addEventListener('click', () => {
      state.activeRange = t.dataset.filter;
      logTabs.forEach((x) => x.classList.toggle('is-active', x === t));
      renderLogs();
    });
  });

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
        navigate('work');
      } else if (msg.action === 'toggle_radio') {
        toggleRadio();
      } else if (msg.action === 'analytics' || msg.action === 'shop') {
        navigate('shop');
      }
    }
  });

  syncUi();
  renderLogs();
})();
