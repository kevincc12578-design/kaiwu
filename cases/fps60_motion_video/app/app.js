(function () {
  const viewport = document.getElementById('viewport');
  const tagBtns = Array.from(document.querySelectorAll('.fp-tag-btn'));
  const labCards = Array.from(document.querySelectorAll('.fp-lab-card'));

  const splitStage = document.getElementById('splitStage');
  const splitToggleBtn = document.getElementById('splitToggleBtn');
  const swipeDeck = document.getElementById('swipeDeck');
  const swipeNextBtn = document.getElementById('swipeNextBtn');
  const morphStage = document.getElementById('morphStage');
  const morphToggleBtn = document.getElementById('morphToggleBtn');
  const morphStateChip = document.getElementById('morphStateChip');

  const kSlider = document.getElementById('kSlider');
  const cSlider = document.getElementById('cSlider');
  const kVal = document.getElementById('kVal');
  const cVal = document.getElementById('cVal');
  const oscSummary = document.getElementById('oscSummary');
  const oscPath = document.getElementById('oscPath');

  const dialog = document.getElementById('tuningDialog');
  const openTuningBtn = document.getElementById('openTuningBtn');
  const closeTuningBtn = document.getElementById('closeTuningBtn');
  const presetBtns = Array.from(document.querySelectorAll('.fp-preset-btn'));

  let isSplit = false;
  let isMorphed = false;
  let k = 280;
  let c = 24;
  let lastTriggerEl = openTuningBtn;

  let stackCards = [
    { id: 1, tag: 'STEP 01 · ONBOARDING', title: 'Zero-latency Asset Sync', desc: 'Fluid momentum flick transfers card state cleanly across deck indices.', grad: 'linear-gradient(145deg, #2563eb, #1e3a8a)' },
    { id: 2, tag: 'STEP 02 · GESTURE STACK', title: 'Velocity-aware Detents', desc: 'Angular tilt follows horizontal displacement with spring snap-back.', grad: 'linear-gradient(145deg, #7c3aed, #312e81)' },
    { id: 3, tag: 'STEP 03 · HANDOFF LOOP', title: 'Continuous Deck Recycle', desc: 'Dismissed card smoothly rotates into back layer without DOM flash.', grad: 'linear-gradient(145deg, #0891b2, #164e63)' },
  ];

  function navigate(route) {
    const target = route || 'all';
    viewport.dataset.page = target;
    tagBtns.forEach((b) => b.classList.toggle('is-active', b.dataset.route === target));
    labCards.forEach((card) => {
      card.classList.toggle('is-dim', target !== 'all' && card.dataset.kind !== target);
    });
  }

  function toggleSplit(force) {
    isSplit = typeof force === 'boolean' ? force : !isSplit;
    splitStage.classList.toggle('is-split', isSplit);
    splitToggleBtn.textContent = isSplit ? 'Reset' : 'Split';
  }

  function toggleMorph(force) {
    isMorphed = typeof force === 'boolean' ? force : !isMorphed;
    morphStage.classList.toggle('is-morphed', isMorphed);
    morphToggleBtn.textContent = isMorphed ? 'Collapse' : 'Expand Morph';
    morphStateChip.textContent = isMorphed ? 'Expanded' : 'Compact';
  }

  function renderDeck() {
    swipeDeck.innerHTML = stackCards
      .map((card, idx) => {
        const yOff = idx * 10;
        const scale = 1 - idx * 0.05;
        const op = 1 - idx * 0.16;
        const z = stackCards.length - idx;
        return `
          <div class="deck-card" data-idx="${idx}" style="background:${card.grad};z-index:${z};opacity:${op};transform:translateY(${yOff}px) scale(${scale})">
            <span class="dc-tag">${card.tag}</span>
            <div>
              <h3>${card.title}</h3>
              <p>${card.desc}</p>
            </div>
          </div>
        `;
      })
      .join('');

    const topCard = swipeDeck.querySelector('.deck-card[data-idx="0"]');
    if (!topCard) return;
    let startX = 0;
    let dx = 0;
    let dragging = false;

    topCard.addEventListener('pointerdown', (e) => {
      dragging = true;
      startX = e.clientX;
      topCard.style.transition = 'none';
      topCard.setPointerCapture(e.pointerId);
    });
    topCard.addEventListener('pointermove', (e) => {
      if (!dragging) return;
      dx = e.clientX - startX;
      topCard.style.transform = `translate(${dx}px, ${Math.abs(dx) * 0.08}px) rotate(${dx * 0.06}deg)`;
    });
    const finishDrag = () => {
      if (!dragging) return;
      dragging = false;
      topCard.style.transition = '';
      if (Math.abs(dx) > 65) rotateDeck(dx >= 0 ? 1 : -1);
      else topCard.style.transform = 'translateY(0px) scale(1)';
      dx = 0;
    };
    topCard.addEventListener('pointerup', finishDrag);
    topCard.addEventListener('pointercancel', finishDrag);
  }

  function rotateDeck(dir = 1) {
    const topCard = swipeDeck.querySelector('.deck-card[data-idx="0"]');
    if (topCard) {
      topCard.style.transform = `translate(${dir * 260}px, -16px) rotate(${dir * 16}deg)`;
      topCard.style.opacity = '0';
    }
    setTimeout(() => {
      const first = stackCards.shift();
      stackCards.push(first);
      renderDeck();
    }, 180);
  }

  function solveSpringCurve(stiff, damp) {
    k = stiff;
    c = damp;
    kVal.textContent = String(k);
    cVal.textContent = String(c);
    kSlider.value = String(k);
    cSlider.value = String(c);
    oscSummary.textContent = `k=${k} · c=${c}`;

    const durMs = Math.round(Math.max(220, Math.min(720, 48000 / Math.sqrt(k * c))));
    document.documentElement.style.setProperty('--fp-dur-split', `${durMs}ms`);
    document.documentElement.style.setProperty('--fp-dur-morph', `${Math.round(durMs * 1.1)}ms`);

    let x = 0;
    let v = 0;
    const target = 1;
    const dt = 0.016;
    const pts = [];
    for (let i = 0; i <= 56; i++) {
      const a = k * (target - x) - c * v;
      v += a * dt;
      x += v * dt;
      const px = Math.round((i / 56) * 280);
      const py = Math.round(70 - x * 32);
      pts.push(`${i === 0 ? 'M' : 'L'}${px},${Math.max(4, Math.min(72, py))}`);
    }
    oscPath.setAttribute('d', pts.join(' '));
  }

  tagBtns.forEach((btn) => btn.addEventListener('click', () => navigate(btn.dataset.route)));
  splitToggleBtn.addEventListener('click', () => toggleSplit());
  swipeNextBtn.addEventListener('click', () => rotateDeck(1));
  morphToggleBtn.addEventListener('click', () => toggleMorph());

  kSlider.addEventListener('input', () => solveSpringCurve(Number(kSlider.value), c));
  cSlider.addEventListener('input', () => solveSpringCurve(k, Number(cSlider.value)));

  openTuningBtn.addEventListener('click', () => {
    lastTriggerEl = openTuningBtn;
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  });
  closeTuningBtn.addEventListener('click', () => dialog && dialog.close());
  presetBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      solveSpringCurve(Number(btn.dataset.k), Number(btn.dataset.c));
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
        navigate('all');
        toggleSplit(false);
        toggleMorph(false);
      } else if (msg.action === 'split_demo') {
        navigate('split');
        toggleSplit(true);
      } else if (msg.action === 'morph_demo') {
        navigate('morph');
        toggleMorph(true);
      }
    }
  });

  renderDeck();
  solveSpringCurve(280, 24);
})();
