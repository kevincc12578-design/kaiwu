(function () {
  const viewport = document.getElementById('viewport');
  const matrixBtns = Array.from(document.querySelectorAll('.matrix-btn'));
  const auroraStage = document.getElementById('auroraStage');
  const portfolioSection = document.getElementById('portfolioSection');
  const portfolioCards = document.getElementById('portfolioCards');
  const secBtns = Array.from(document.querySelectorAll('.sec-btn'));
  const dialog = document.getElementById('manifestoDialog');
  const openManifestoBtn = document.getElementById('openManifestoBtn');
  const openManifestoTopBtn = document.getElementById('openManifestoTopBtn');
  const jumpPortfolioBtn = document.getElementById('jumpPortfolioBtn');
  const canvas = document.getElementById('ferroCanvas');

  const PORTFOLIO = [
    { id: 'PF-01', name: 'Aether Compiler', sector: 'Infra', stage: 'Seed · $12M', desc: 'Zero-overhead kernel fusion and deterministic graph scheduling for frontier GPUs.' },
    { id: 'PF-02', name: 'Kinetix Actuate', sector: 'Robotics', stage: 'Series A · $34M', desc: 'Tactile proprioceptive policies compiled directly to sub-millisecond servo loops.' },
    { id: 'PF-03', name: 'Verity Proofs', sector: 'Foundation', stage: 'Pre-Seed · $5.5M', desc: 'Formal verification substrate for theorem-proving neurosymbolic code agents.' },
    { id: 'PF-04', name: 'Solenoid Lab', sector: 'Robotics', stage: 'Seed · $14M', desc: 'Bimanual dexterity foundation models trained on synthetic physics trajectories.' },
    { id: 'PF-05', name: 'Helios Mesh', sector: 'Infra', stage: 'Seed · $16M', desc: 'Photonic interconnect fabric minimizing all-reduce latency across pods.' },
    { id: 'PF-06', name: 'Tensor Loom', sector: 'Foundation', stage: 'Series A · $42M', desc: 'Discrete state-space architectures for long-horizon scientific reasoning.' },
    { id: 'PF-07', name: 'Graviton FAB', sector: 'Infra', stage: 'Pre-Seed · $6M', desc: 'Cryogenic SRAM characterization and automated lithography synthesis.' },
    { id: 'PF-08', name: 'Tectonic Bio', sector: 'Foundation', stage: 'Seed · $19M', desc: 'Programmable protein conformational dynamics powered by flow matching.' },
  ];

  let activeRange = 'all';
  let lastTriggerEl = openManifestoBtn;
  const pointer = { x: 0.62, y: 0.42 };

  function navigate(route) {
    const target = route || 'frontier';
    viewport.dataset.page = target;
    matrixBtns.forEach((b) => b.classList.toggle('is-active', b.dataset.route === target));
    if (target === 'portfolio') {
      portfolioSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else if (target === 'frontier') {
      auroraStage.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function renderPortfolio() {
    const items = PORTFOLIO.filter((p) => activeRange === 'all' || p.sector === activeRange);
    portfolioCards.innerHTML = items
      .map(
        (p) => `
      <article class="p-card">
        <div class="p-top"><span>${p.id}</span><span class="p-sector">${p.sector}</span></div>
        <h3 class="p-name">${p.name}</h3>
        <p class="p-desc">${p.desc}</p>
        <div class="p-stage">${p.stage}</div>
      </article>`
      )
      .join('');
  }

  function initFerrofluidCanvas() {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const palette = ['#0055ff', '#ff2a85', '#f5c438', '#10b981', '#ffffff'];
    const particles = Array.from({ length: 320 }, (_, i) => ({
      angle: (i / 320) * Math.PI * 2,
      radius: 36 + (i % 16) * 28,
      speed: 0.003 + (i % 6) * 0.0012,
      size: 1.2 + (i % 4) * 0.9,
      color: palette[i % palette.length],
      phase: i * 0.29,
    }));

    const reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function drawFrame(time) {
      const w = canvas.width;
      const h = canvas.height;
      ctx.fillStyle = 'rgba(0, 0, 0, 0.26)';
      ctx.fillRect(0, 0, w, h);

      const cx = w * pointer.x;
      const cy = h * pointer.y;

      const grad = ctx.createRadialGradient(cx, cy, 24, cx, cy, w * 0.62);
      grad.addColorStop(0, 'rgba(255, 42, 133, 0.55)');
      grad.addColorStop(0.32, 'rgba(0, 85, 255, 0.50)');
      grad.addColorStop(0.62, 'rgba(16, 185, 129, 0.24)');
      grad.addColorStop(0.84, 'rgba(245, 196, 56, 0.14)');
      grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, w, h);

      for (let i = 0; i < particles.length; i += 1) {
        const p = particles[i];
        const t = time * p.speed + p.phase;
        const wobble = Math.sin(t * 2.1 + p.angle * 3) * 44;
        const rx = cx + Math.cos(p.angle + t * 0.26) * (p.radius * 1.6 + wobble);
        const ry = cy + Math.sin(p.angle * 1.15 - t * 0.22) * (p.radius * 1.0 + wobble * 0.72);
        ctx.beginPath();
        ctx.arc(rx, ry, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.fill();
      }
    }

    if (reducedMotion) {
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      drawFrame(1400);
      return;
    }

    let rafId = 0;
    function tick(now) {
      drawFrame(now * 0.08);
      rafId = window.requestAnimationFrame(tick);
    }
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    rafId = window.requestAnimationFrame(tick);

    auroraStage.addEventListener('mousemove', (e) => {
      const rect = auroraStage.getBoundingClientRect();
      pointer.x = Math.max(0.22, Math.min(0.86, (e.clientX - rect.left) / rect.width));
      pointer.y = Math.max(0.18, Math.min(0.80, (e.clientY - rect.top) / rect.height));
    });

    window.addEventListener('beforeunload', () => window.cancelAnimationFrame(rafId));
  }

  function openManifestoFrom(el) {
    lastTriggerEl = el;
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  }

  matrixBtns.forEach((b) => b.addEventListener('click', () => navigate(b.dataset.route)));
  secBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      activeRange = btn.dataset.filter;
      secBtns.forEach((b) => b.classList.toggle('is-active', b === btn));
      renderPortfolio();
    });
  });

  openManifestoBtn.addEventListener('click', () => openManifestoFrom(openManifestoBtn));
  openManifestoTopBtn.addEventListener('click', () => openManifestoFrom(openManifestoTopBtn));
  jumpPortfolioBtn.addEventListener('click', () => navigate('portfolio'));

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
        navigate('frontier');
      } else if (msg.action === 'open_manifesto') {
        openManifestoFrom(openManifestoTopBtn);
      } else if (msg.action === 'analytics' || msg.action === 'portfolio') {
        navigate('portfolio');
      }
    }
  });

  renderPortfolio();
  initFerrofluidCanvas();
})();
