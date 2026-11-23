(() => {
  'use strict';

  const $ = (s, root = document) => root.querySelector(s);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const shell = $('#workspace');
  const railEl = $('#rail');
  const viewport = $('#main-panel');
  const dialog = $('#hvDialog');
  const toastEl = $('#hvToast');

  const RAIL_ITEMS = [
    ['overview', 'Home', 'home'],
    ['search', 'Search', 'search'],
    ['orders', 'Orders', 'bag'],
    ['products', 'Products', 'box'],
    ['customers', 'Customers', 'users'],
    ['apps', 'Modules', 'grid'],
    ['messages', 'Messages', 'msg'],
    ['calendar', 'Calendar', 'cal'],
    ['analytics', 'Analytics', 'chart'],
  ];

  const ICONS = {
    home: '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/>',
    search: '<circle cx="10.5" cy="10.5" r="6"/><path d="m15.5 15.5 4.5 4.5"/>',
    bag: '<rect x="4" y="7" width="16" height="13" rx="2.5"/><path d="M9 7V5a3 3 0 0 1 6 0v2"/>',
    box: '<path d="m12 3 8 4.5v9L12 21l-8-4.5v-9z"/><path d="M12 12v9m0-9 8-4.5M12 12 4 7.5"/>',
    users: '<circle cx="9" cy="8" r="3.5"/><path d="M2 20a7 7 0 0 1 14 0"/><circle cx="17" cy="9" r="2.5"/>',
    grid: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    msg: '<path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5H4l1.8-4A8.5 8.5 0 1 1 21 11.5Z"/>',
    cal: '<rect x="3" y="4" width="18" height="17" rx="2.5"/><path d="M8 2v4M16 2v4M3 10h18"/>',
    chart: '<path d="M4 19V5M4 19h16M8 15V9m5 6V6m5 9v-4"/>',
    gear: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-1.8-.3 1.6 1.6 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0 .3-1.8 1.6 1.6 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.8.3h.1a1.6 1.6 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.8v.1a1.6 1.6 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1Z"/>',
    power: '<path d="M12 2v10M18.4 6.6a9 9 0 1 1-12.8 0"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    play: '<path d="m8 5 11 7-11 7z" fill="currentColor" stroke="none"/>',
    pause: '<rect x="6" y="5" width="4" height="14" fill="currentColor" stroke="none"/><rect x="14" y="5" width="4" height="14" fill="currentColor" stroke="none"/>',
    download: '<path d="M12 3v12m-4-4 4 4 4-4M4 18v2h16v-2"/>',
    bolt: '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    trendUp: '<path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/>',
    layers: '<path d="m12 2 9 5-9 5-9-5 9-5z"/><path d="m3 12 9 5 9-5"/><path d="m3 17 9 5 9-5"/>',
    cpu: '<rect x="7" y="7" width="10" height="10" rx="2"/><path d="M9 3v4M15 3v4M9 17v4M15 17v4M3 9h4M3 15h4M17 9h4M17 15h4"/>',
    mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    phone: '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.8a2 2 0 0 1-.4 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7A2 2 0 0 1 22 16.9z"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    check: '<path d="m5 12 5 5L20 7"/>',
    sparkles: '<path d="m12 3 1.8 4.2L18 9l-4.2 1.8L12 15l-1.8-4.2L6 9l4.2-1.8z"/><path d="M19 16v4M17 18h4"/>',
    filter: '<path d="M3 5h18l-7 8v6l-4 2v-8z"/>',
    tag: '<path d="M12 2H4v8l9.5 9.5a2 2 0 0 0 2.8 0l5.2-5.2a2 2 0 0 0 0-2.8z"/><circle cx="7.5" cy="7.5" r="1.2"/>',
    creditCard: '<rect x="2" y="5" width="20" height="14" rx="2.5"/><path d="M2 10h20M6 15h4"/>',
    truck: '<rect x="2" y="5" width="13" height="11" rx="1.5"/><path d="M15 9h4l3 3v4h-7z"/><circle cx="6.5" cy="18" r="2"/><circle cx="18.5" cy="18" r="2"/>',
    activity: '<path d="M2 12h4l3-7 5 14 3-7h5"/>',
    webhook: '<circle cx="12" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="18" r="3"/><path d="M10.5 8.5 7.5 15.5M13.5 8.5l3 7"/>',
    database: '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    bell: '<path d="M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10 21a2 2 0 0 0 4 0"/>',
    sliders: '<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="9" cy="6" r="2"/><circle cx="15" cy="12" r="2"/><circle cx="10" cy="18" r="2"/>',
    compass: '<circle cx="12" cy="12" r="9"/><polygon points="16 8 14 14 8 16 10 10 16 8"/>',
    send: '<path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>',
    calendarPlus: '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M8 2v4M16 2v4M3 10h18M12 13v5M9.5 15.5h5"/>',
    mic: '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v4M8 22h8"/>',
  };
  const svgIcon = (k, s = 17) => `<svg aria-hidden="true" width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${ICONS[k] || ICONS.home}</svg>`;
  const iconOrb = (k, tone = 'blue', size = '') => `<span class="hv-icon-orb ${tone} ${size}">${svgIcon(k, size === 'sm' ? 14 : 17)}</span>`;

  function smoothPath(pts) {
    if (!pts.length) return '';
    if (pts.length === 1) return `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
    let d = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
    for (let i = 0; i < pts.length - 1; i += 1) {
      const p0 = pts[i - 1] || pts[i];
      const p1 = pts[i];
      const p2 = pts[i + 1];
      const p3 = pts[i + 2] || p2;
      const c1x = p1[0] + (p2[0] - p0[0]) / 6;
      const c1y = p1[1] + (p2[1] - p0[1]) / 6;
      const c2x = p2[0] - (p3[0] - p1[0]) / 6;
      const c2y = p2[1] - (p3[1] - p1[1]) / 6;
      d += ` C${c1x.toFixed(1)},${c1y.toFixed(1)} ${c2x.toFixed(1)},${c2y.toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
    }
    return d;
  }

  function sparklineSvg(values, uid, color = '#60a5fa') {
    const min = Math.min(...values);
    const max = Math.max(...values);
    const span = Math.max(1, max - min);
    const pts = values.map((v, i) => [4 + (i / Math.max(1, values.length - 1)) * 76, 25 - ((v - min) / span) * 19]);
    const lineD = smoothPath(pts);
    const areaD = `${lineD} L80,29 L4,29 Z`;
    const last = pts[pts.length - 1];
    return `
      <div class="hv-spark-wrap">
        <svg class="hv-chart-svg" viewBox="0 0 84 30" aria-hidden="true">
          <defs><linearGradient id="sp-${uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${color}" stop-opacity="0.38"/><stop offset="100%" stop-color="${color}" stop-opacity="0.02"/></linearGradient></defs>
          <path d="${areaD}" fill="url(#sp-${uid})"/>
          <path d="${lineD}" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round"/>
          <circle cx="${last[0].toFixed(1)}" cy="${last[1].toFixed(1)}" r="2.8" fill="#fff" stroke="${color}" stroke-width="1.5"/>
        </svg>
      </div>
    `;
  }

  function miniBarsHtml(values, tone = '') {
    const max = Math.max(...values, 1);
    return `
      <div class="hv-mini-bars" aria-hidden="true">
        ${values.map((v) => `<span class="hv-mini-bar ${tone}" style="height:${Math.max(8, Math.round((v / max) * 28))}px"></span>`).join('')}
      </div>
    `;
  }

  function ringMiniHtml(pct, color = '#4ade80') {
    const r = 20;
    const c = 2 * Math.PI * r;
    const dash = ((pct / 100) * c).toFixed(1);
    return `
      <div class="hv-ring-mini">
        <svg class="hv-chart-svg" viewBox="0 0 52 52" aria-hidden="true">
          <circle cx="26" cy="26" r="${r}" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="5"/>
          <circle cx="26" cy="26" r="${r}" fill="none" stroke="${color}" stroke-width="5" stroke-dasharray="${dash} ${c.toFixed(1)}" stroke-linecap="round"/>
        </svg>
        <span>${pct}%</span>
      </div>
    `;
  }

  function areaLineChartSvg({ uid, labels, primary, secondary = null, primaryColor = '#60a5fa', secondaryColor = '#4ade80', width = 400, height = 132 }) {
    const W = width;
    const top = 12;
    const bot = height - 22;
    const spanY = bot - top;
    const allVals = secondary ? [...primary, ...secondary] : [...primary];
    const rawMin = Math.min(...allVals);
    const rawMax = Math.max(...allVals);
    const pad = Math.max(1, (rawMax - rawMin) * 0.22);
    const min = rawMin - pad;
    const max = rawMax + pad * 0.45;
    const span = Math.max(1, max - min);
    const toPts = (arr) => arr.map((v, i) => [12 + (i / Math.max(1, arr.length - 1)) * (W - 24), bot - ((v - min) / span) * spanY]);
    const pPts = toPts(primary);
    const pLine = smoothPath(pPts);
    const pArea = `${pLine} L${pPts[pPts.length - 1][0].toFixed(1)},${bot} L${pPts[0][0].toFixed(1)},${bot} Z`;
    const pLast = pPts[pPts.length - 1];
    const sPts = secondary ? toPts(secondary) : null;
    const sLine = sPts ? smoothPath(sPts) : '';
    const grids = [0.25, 0.55, 0.85].map((r) => (top + spanY * r).toFixed(1));
    return `
      <svg class="hv-chart-svg" viewBox="0 0 ${W} ${height}" aria-hidden="true">
        <defs>
          <linearGradient id="area-${uid}" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="${primaryColor}" stop-opacity="0.34"/>
            <stop offset="100%" stop-color="${primaryColor}" stop-opacity="0.02"/>
          </linearGradient>
        </defs>
        ${grids.map((y) => `<line x1="8" y1="${y}" x2="${W - 8}" y2="${y}" stroke="rgba(255,255,255,0.10)" stroke-dasharray="3 3"/>`).join('')}
        <path d="${pArea}" fill="url(#area-${uid})"/>
        ${sLine ? `<path d="${sLine}" fill="none" stroke="${secondaryColor}" stroke-width="2" stroke-dasharray="5 4" stroke-linecap="round"/>` : ''}
        <path d="${pLine}" fill="none" stroke="${primaryColor}" stroke-width="2.5" stroke-linecap="round"/>
        ${pPts.map(([x, y], idx) => `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${idx === pPts.length - 1 ? 4.2 : 2.3}" fill="${idx === pPts.length - 1 ? '#fff' : primaryColor}" stroke="${primaryColor}" stroke-width="${idx === pPts.length - 1 ? 2 : 0}"/>`).join('')}
        <circle cx="${pLast[0].toFixed(1)}" cy="${pLast[1].toFixed(1)}" r="8" fill="${primaryColor}" fill-opacity="0.24"/>
        ${labels.map((lb, i) => {
          const lx = 12 + (i / Math.max(1, labels.length - 1)) * (W - 24);
          return `<text x="${lx.toFixed(1)}" y="${height - 5}" text-anchor="middle" fill="rgba(255,255,255,0.68)" font-size="10.5">${esc(lb)}</text>`;
        }).join('')}
      </svg>
    `;
  }

  function groupedBarChartSvg({ uid, labels, seriesA, seriesB = null, colorA = '#60a5fa', colorB = '#4ade80', width = 380, height = 122, highlightIdx = -1, unit = '' }) {
    const W = width;
    const top = 16;
    const bot = height - 22;
    const spanY = bot - top;
    const allVals = seriesB ? [...seriesA, ...seriesB] : [...seriesA];
    const maxVal = Math.max(...allVals, 1) * 1.12;
    const n = labels.length;
    const slotW = (W - 20) / Math.max(1, n);
    const grids = [0.25, 0.55, 0.85].map((r) => (top + spanY * r).toFixed(1));
    return `
      <svg class="hv-chart-svg" viewBox="0 0 ${W} ${height}" aria-hidden="true">
        <defs>
          <linearGradient id="barA-${uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#93c5fd"/><stop offset="100%" stop-color="${colorA}" stop-opacity="0.65"/></linearGradient>
          <linearGradient id="barB-${uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#86efac"/><stop offset="100%" stop-color="${colorB}" stop-opacity="0.65"/></linearGradient>
        </defs>
        ${grids.map((y) => `<line x1="8" y1="${y}" x2="${W - 8}" y2="${y}" stroke="rgba(255,255,255,0.09)" stroke-dasharray="3 3"/>`).join('')}
        ${labels.map((lb, i) => {
          const cx = 10 + i * slotW + slotW / 2;
          const vA = seriesA[i] || 0;
          const hA = Math.max(6, (vA / maxVal) * spanY);
          const yA = bot - hA;
          if (seriesB) {
            const vB = seriesB[i] || 0;
            const hB = Math.max(6, (vB / maxVal) * spanY);
            const yB = bot - hB;
            const bw = Math.min(20, slotW * 0.28);
            return `
              <rect x="${(cx - bw - 2).toFixed(1)}" y="${yA.toFixed(1)}" width="${bw.toFixed(1)}" height="${hA.toFixed(1)}" rx="4" fill="url(#barA-${uid})"/>
              <rect x="${(cx + 2).toFixed(1)}" y="${yB.toFixed(1)}" width="${bw.toFixed(1)}" height="${hB.toFixed(1)}" rx="4" fill="url(#barB-${uid})"/>
              <text x="${cx.toFixed(1)}" y="${height - 5}" text-anchor="middle" fill="rgba(255,255,255,0.68)" font-size="10.5">${esc(lb)}</text>
            `;
          }
          const bw = Math.min(28, slotW * 0.50);
          const isHi = i === highlightIdx;
          return `
            <rect x="${(cx - bw / 2).toFixed(1)}" y="${yA.toFixed(1)}" width="${bw.toFixed(1)}" height="${hA.toFixed(1)}" rx="5" fill="${isHi ? `url(#barA-${uid})` : 'rgba(255,255,255,0.22)'}"/>
            <text x="${cx.toFixed(1)}" y="${(yA - 4).toFixed(1)}" text-anchor="middle" fill="rgba(255,255,255,0.82)" font-size="9.5" font-weight="600">${vA}${unit}</text>
            <text x="${cx.toFixed(1)}" y="${height - 5}" text-anchor="middle" fill="rgba(255,255,255,0.68)" font-size="10.5">${esc(lb)}</text>
          `;
        }).join('')}
      </svg>
    `;
  }

  function donutRingSvg({ segments, size = 118, stroke = 13, centerVal = '', centerSub = '' }) {
    const r = (size - stroke) / 2;
    const c = 2 * Math.PI * r;
    const total = Math.max(1, segments.reduce((s, g) => s + g.pct, 0));
    let offset = 0;
    const arcs = segments.map((g) => {
      const len = (g.pct / total) * c;
      const draw = Math.max(2, len - 2.6);
      const html = `<circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="${g.color}" stroke-width="${stroke}" stroke-dasharray="${draw.toFixed(1)} ${c.toFixed(1)}" stroke-dashoffset="${(-offset).toFixed(1)}" stroke-linecap="round"/>`;
      offset += len;
      return html;
    }).join('');
    return `
      <div class="hv-donut-wrap">
        <div style="position:relative;width:${size}px;height:${size}px;flex-shrink:0;">
          <svg class="hv-chart-svg" viewBox="0 0 ${size} ${size}" style="transform:rotate(-90deg);" aria-hidden="true">
            <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="${stroke}"/>
            ${arcs}
          </svg>
          <div style="position:absolute;inset:0;display:grid;place-content:center;text-align:center;pointer-events:none;">
            <strong style="font-size:17px;font-weight:800;line-height:1.1;">${esc(centerVal)}</strong>
            <span style="font-size:10px;color:var(--hv-muted);">${esc(centerSub)}</span>
          </div>
        </div>
        <div class="hv-legend-list">
          ${segments.map((g) => `
            <div class="hv-legend-row">
              <span class="hv-legend-label"><i class="hv-dot" style="background:${g.color}"></i>${esc(g.label)}</span>
              <strong>${esc(g.val || `${g.pct}%`)}</strong>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  function radarChartSvg({ uid, axes, color = '#60a5fa', size = 152 }) {
    const cx = size / 2;
    const cy = size / 2;
    const maxR = size * 0.34;
    const n = axes.length;
    const ptAt = (idx, ratio) => {
      const ang = -Math.PI / 2 + (idx * 2 * Math.PI) / n;
      return [cx + Math.cos(ang) * maxR * ratio, cy + Math.sin(ang) * maxR * ratio];
    };
    const rings = [0.35, 0.68, 1].map((r) => {
      const d = axes.map((_, i) => ptAt(i, r).map((v) => v.toFixed(1)).join(',')).join(' ');
      return `<polygon points="${d}" fill="none" stroke="rgba(255,255,255,0.14)" stroke-width="1"/>`;
    }).join('');
    const spokes = axes.map((_, i) => {
      const [x, y] = ptAt(i, 1);
      return `<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="rgba(255,255,255,0.11)" stroke-width="1"/>`;
    }).join('');
    const dataPts = axes.map((a, i) => ptAt(i, Math.max(0.12, Math.min(1, a.score / 100))));
    const poly = dataPts.map((p) => p.map((v) => v.toFixed(1)).join(',')).join(' ');
    const labelsHtml = axes.map((a, i) => {
      const [x, y] = ptAt(i, 1.3);
      const anchor = x < cx - 8 ? 'end' : (x > cx + 8 ? 'start' : 'middle');
      return `<text x="${x.toFixed(1)}" y="${(y + 3).toFixed(1)}" text-anchor="${anchor}" fill="rgba(255,255,255,0.75)" font-size="9.5" font-weight="600">${esc(a.label)}</text>`;
    }).join('');
    return `
      <div class="hv-radar-wrap">
        <svg class="hv-chart-svg" viewBox="-26 -6 ${size + 52} ${size + 12}" style="max-width:240px;" aria-hidden="true">
          <defs><linearGradient id="rad-${uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="${color}" stop-opacity="0.42"/><stop offset="100%" stop-color="#4ade80" stop-opacity="0.20"/></linearGradient></defs>
          ${rings}
          ${spokes}
          <polygon points="${poly}" fill="url(#rad-${uid})" stroke="${color}" stroke-width="2" stroke-linejoin="round"/>
          ${dataPts.map(([x, y]) => `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3" fill="#fff" stroke="${color}" stroke-width="1.5"/>`).join('')}
          ${labelsHtml}
        </svg>
      </div>
    `;
  }

  function funnelChartHtml(stages) {
    return `
      <div class="hv-funnel-list">
        ${stages.map(([st, pct, vol, col]) => `
          <div class="hv-funnel-item">
            <div class="hv-funnel-head">
              <span style="color:var(--hv-muted);">${esc(st)}</span>
              <strong>${esc(vol)}</strong>
            </div>
            <div class="hv-funnel-track">
              <div class="hv-funnel-fill" style="width:${pct}%;background:${col || 'linear-gradient(90deg,#60a5fa,var(--hv-blue))'}"></div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  function heatmapGridHtml(cells) {
    return `
      <div class="hv-cohort-grid">
        ${cells.map((c) => `<div class="hv-heat-cell" data-level="${c.level}" title="${esc(c.tip || '')}">${esc(c.label)}</div>`).join('')}
      </div>
    `;
  }

  const DOMAIN_PRESETS = {
    Overview: { targetBase: 64, achieved: '$412k', goal: '$640k', rev: '$23.4k', revGoal: '$28k', revDelta: '+12.4%', leads: '1,270', leadsDelta: '+18.2%', customers: '2,837', pipe: '$1.24M', activeUsers: '311', tickets: '18', sales: [31, 34, 28.5, 30, 24, 27, 19] },
    Sales: { targetBase: 76, achieved: '$486k', goal: '$640k', rev: '$31.8k', revGoal: '$35k', revDelta: '+16.9%', leads: '1,540', leadsDelta: '+22.4%', customers: '3,012', pipe: '$1.58M', activeUsers: '348', tickets: '14', sales: [34, 36, 39, 32, 29, 31, 25] },
    Marketing: { targetBase: 58, achieved: '$371k', goal: '$640k', rev: '$19.2k', revGoal: '$24k', revDelta: '+9.5%', leads: '2,180', leadsDelta: '+29.1%', customers: '2,690', pipe: '$980k', activeUsers: '412', tickets: '21', sales: [22, 25, 29, 27, 26, 24, 18] },
    Support: { targetBase: 82, achieved: '$524k', goal: '$640k', rev: '$18.6k', revGoal: '$20k', revDelta: '+7.2%', leads: '940', leadsDelta: '+11.0%', customers: '2,945', pipe: '$1.10M', activeUsers: '289', tickets: '9', sales: [20, 22, 24, 21, 19, 17, 15] },
  };

  const APPROVAL_QUEUE = [
    { client: 'Lumen Labs · 15% off annual plan', amount: '$4,800', tag: 'DISCOUNT' },
    { client: 'Northwind Co · Multi-seat add-on', amount: '$7,200', tag: 'RENEWAL' },
    { client: 'Kestrel AI · Custom SLA waiver', amount: '$3,450', tag: 'TERMS' },
  ];

  const WAVE_HEIGHTS = [16, 28, 22, 34, 42, 30, 20, 38, 46, 32, 26, 40, 48, 35, 22, 36, 44, 38, 28, 34, 46, 40, 24, 30, 38, 42, 28, 20, 32, 36, 26, 18, 28, 34, 22, 16, 24, 30, 20, 14, 22, 18, 12, 16, 20, 14, 10, 14];

  const ORDERS_DATA = [
    { id: 'ORD-9428', account: 'Northwind Co.', plan: 'Enterprise 120 Seats', amount: '$14,400', numeric: 14400, status: 'Paid', date: '2026-11-23', owner: 'Sarah Chen', notes: 'Annual wire cleared via Stripe Treasury' },
    { id: 'ORD-9427', account: 'Lumen Labs', plan: 'Growth 45 Seats', amount: '$5,400', numeric: 5400, status: 'Processing', date: '2026-11-22', owner: 'Alma Reed', notes: 'Waiting countersign on 15% annual discount' },
    { id: 'ORD-9426', account: 'Kestrel AI', plan: 'Spatial Audio Add-on', amount: '$3,450', numeric: 3450, status: 'Paid', date: '2026-11-21', owner: 'Jules Park', notes: 'Auto-provisioned 48kHz call transcription' },
    { id: 'ORD-9425', account: 'Halcyon Systems', plan: 'Core Workspace 25', amount: '$2,250', numeric: 2250, status: 'Processing', date: '2026-11-20', owner: 'Milo Bell', notes: 'Invoice INV-4410 sent to AP contact' },
    { id: 'ORD-9424', account: 'Vesper Retail', plan: 'Pilot Bundle', amount: '$980', numeric: 980, status: 'Refunded', date: '2026-11-18', owner: 'Sarah Chen', notes: 'Downgraded before billing cycle lock' },
  ];

  const PRODUCTS_DATA = [
    { id: 'prd-ent', name: 'Haven Enterprise Grid', category: 'Plans', price: '$120 / seat', mrr: '$168.4k', seats: 88, active: true, desc: 'Full spatial glass workspace with custom SLA and audit export.' },
    { id: 'prd-grow', name: 'Haven Growth Team', category: 'Plans', price: '$65 / seat', mrr: '$94.2k', seats: 74, active: true, desc: 'Multi-domain CRM presets, approval queue & calendar sync.' },
    { id: 'prd-wave', name: 'Discovery Waveform AI', category: 'Add-ons', price: '$290 / mo', mrr: '$41.8k', seats: 62, active: true, desc: 'Real-time call sentiment tracking and variable-speed playback.' },
    { id: 'prd-sso', name: 'Zero-Trust SSO Guard', category: 'Add-ons', price: '$450 / mo', mrr: '$29.6k', seats: 54, active: true, desc: 'SAML 2.0, SCIM provisioning & session hardware binding.' },
    { id: 'prd-onboard', name: 'White-Glove Migration', category: 'Services', price: '$2,800 flat', mrr: '$18.0k', seats: 40, active: false, desc: 'Dedicated solutions engineer for legacy telemetry import.' },
    { id: 'prd-api', name: 'High-Frequency Webhook', category: 'Services', price: '$190 / mo', mrr: '$24.5k', seats: 81, active: true, desc: 'Sub-50ms event streaming for external revenue warehouses.' },
  ];

  const CUSTOMERS_DATA = [
    {
      id: 'cus-nw', name: 'Northwind Co.', initials: 'NW', color: '#1d4ed8', tier: 'Enterprise', arr: '$172,800', health: 94, badge: 'Healthy', contact: 'Elena Vance (VP Ops) · elena@northwind.co',
      notes: [{ ts: 'Nov 23 · 10:15', text: 'Discovery call rated positive sentiment at 26:48 mark.' }, { ts: 'Nov 19 · 16:40', text: 'Expanded 40 additional seats in APAC region.' }],
    },
    {
      id: 'cus-lm', name: 'Lumen Labs', initials: 'LM', color: '#0f766e', tier: 'Growth', arr: '$64,800', health: 86, badge: 'Growth', contact: 'Marcus Holt (Head of RevOps) · mholt@lumenlabs.io',
      notes: [{ ts: 'Nov 22 · 14:20', text: '15% annual discount queued in Approvals.' }],
    },
    {
      id: 'cus-ks', name: 'Kestrel AI', initials: 'KS', color: '#6d28d9', tier: 'Enterprise', arr: '$118,500', health: 91, badge: 'Healthy', contact: 'Priya Nair (CTO) · priya@kestrel.ai',
      notes: [{ ts: 'Nov 21 · 09:30', text: 'Enabled Discovery Waveform AI across 3 sales pods.' }],
    },
    {
      id: 'cus-hc', name: 'Halcyon Systems', initials: 'HC', color: '#b45309', tier: 'At Risk', arr: '$38,400', health: 58, badge: 'Risk', contact: 'Devon Cruz (IT Lead) · dcruz@halcyon.net',
      notes: [{ ts: 'Nov 20 · 17:05', text: 'Ticket spike on SSO sync; Alma scheduled check-in.' }],
    },
  ];

  const MODULES_DATA = [
    { id: 'mod-stripe', name: 'Stripe Billing', category: 'Billing', status: true, latency: '24ms sync', desc: 'Invoices, MRR recognition & instant payout reconciliation.' },
    { id: 'mod-slack', name: 'Slack Alerts', category: 'Comms', status: true, latency: 'Real-time', desc: 'Routes high-value approvals and SLA escalation pings.' },
    { id: 'mod-linear', name: 'Linear Issues', category: 'Dev', status: true, latency: 'Webhook v2', desc: 'Bi-directional escalation linking support tickets to engineering.' },
    { id: 'mod-resend', name: 'Resend SMTP', category: 'Comms', status: true, latency: '19ms API', desc: 'Transactional invoice receipts & weekly digest delivery.' },
    { id: 'mod-hubspot', name: 'HubSpot Sync', category: 'CRM', status: false, latency: 'Paused', desc: 'Stage mirror for outbound marketing attribution cohorts.' },
    { id: 'mod-notion', name: 'Notion Runbooks', category: 'CRM', status: true, latency: '5m poll', desc: 'Embeds Discovery Call notes directly into account wikis.' },
  ];

  const MESSAGES_THREADS = [
    {
      id: 'thr-nw', sender: 'Elena Vance · Northwind', role: 'VP Operations', unread: true, time: '2m ago',
      items: [
        { from: 'them', text: 'Sarah, the Q4 forecast numbers in Haven match our board sheet.', ts: '11:36' },
        { from: 'self', text: 'Awesome — I just attached the Discovery Call audio clips as well.', ts: '11:39' },
      ],
    },
    {
      id: 'thr-lm', sender: 'Marcus Holt · Lumen Labs', role: 'RevOps Lead', unread: true, time: '18m ago',
      items: [
        { from: 'them', text: 'Did the 15% annual discount approval clear on your side?', ts: '11:18' },
      ],
    },
    {
      id: 'thr-hc', sender: 'Devon Cruz · Halcyon', role: 'IT Lead', unread: true, time: '1h ago',
      items: [
        { from: 'them', text: 'Can we move SSO sync review to Thursday morning?', ts: '10:25' },
      ],
    },
  ];

  const CALENDAR_EVENTS = [
    { id: 'ev-1', day: 'Mon', time: '09:30', title: 'Executive Pipeline Sync', type: 'reviews', owner: 'Sarah Chen' },
    { id: 'ev-2', day: 'Mon', time: '14:00', title: 'Northwind Discovery Follow-up', type: 'calls', owner: 'Alma Reed' },
    { id: 'ev-3', day: 'Tue', time: '11:00', title: 'Lumen Labs Renewal Review', type: 'reviews', owner: 'Jules Park' },
    { id: 'ev-4', day: 'Wed', time: '15:30', title: 'Kestrel Waveform Live Demo', type: 'demos', owner: 'Milo Bell' },
    { id: 'ev-5', day: 'Thu', time: '10:00', title: 'Halcyon SSO Triage Call', type: 'calls', owner: 'Alma Reed' },
    { id: 'ev-6', day: 'Fri', time: '13:30', title: 'Q4 Revenue Closeout Check', type: 'reviews', owner: 'Sarah Chen' },
  ];

  const ANALYTICS_SERIES = {
    Week: { rev: '$164.2k', nrr: '118.4%', cac: '4.2 mo', winRate: '38.6%', points: 'M0,84 L70,74 L140,68 L210,54 L280,46 L350,30 L420,18', retain: 'M0,62 L70,60 L140,54 L210,49 L280,42 L350,36 L420,28', funnel: [['Visitors', 100, '24,800'], ['Signups', 64, '15,870'], ['Qualified', 41, '10,160'], ['Proposal', 24, '5,950'], ['Won Deals', 14, '3,472']] },
    Month: { rev: '$648.0k', nrr: '121.8%', cac: '3.9 mo', winRate: '41.2%', points: 'M0,92 L70,80 L140,64 L210,58 L280,38 L350,24 L420,12', retain: 'M0,70 L70,64 L140,52 L210,44 L280,34 L350,28 L420,20', funnel: [['Visitors', 100, '98,400'], ['Signups', 68, '66,910'], ['Qualified', 46, '45,260'], ['Proposal', 29, '28,530'], ['Won Deals', 17, '16,728']] },
    Quarter: { rev: '$1.94M', nrr: '124.6%', cac: '3.6 mo', winRate: '43.5%', points: 'M0,96 L70,82 L140,70 L210,48 L280,32 L350,20 L420,8', retain: 'M0,74 L70,66 L140,56 L210,46 L280,32 L350,22 L420,14', funnel: [['Visitors', 100, '294k'], ['Signups', 71, '208k'], ['Qualified', 49, '144k'], ['Proposal', 31, '91.1k'], ['Won Deals', 19, '55.8k']] },
  };

  const state = {
    activeRoute: 'overview',
    activeDomain: 'Overview',
    targetPct: 64,
    showForecast: true,
    activeMetric: 'Revenue',
    revPeriod: 'Today',
    salesPeriod: 'Week',
    approvalIdx: 0,
    kpiSwitches: { customers: true, pipeline: true, live: true, tickets: true },
    playing: false,
    playPos: 26,
    speed: 1,
    lastFocus: null,
    scrollByRoute: {},
    searchQuery: '',
    searchFilter: 'all',
    orderFilter: 'all',
    selectedOrderId: 'ORD-9428',
    orders: ORDERS_DATA,
    productFilter: 'all',
    products: PRODUCTS_DATA,
    customerFilter: 'all',
    selectedCustomerId: 'cus-nw',
    customers: CUSTOMERS_DATA,
    moduleFilter: 'all',
    modules: MODULES_DATA,
    threads: MESSAGES_THREADS,
    activeThreadId: 'thr-nw',
    calFilter: 'all',
    events: CALENDAR_EVENTS,
    analyticsGrain: 'Week',
    autoInvoice: true,
    autoRenewGuard: true,
    rateLimitGuard: true,
    autoRetryWebhook: true,
    focusShield: false,
    msgVoicePlaying: false,
    msgPlayPos: 14,
  };

  let dockPointer = null;
  const dockRadius = 104;
  const dockGain = 0.35;
  let playTimer = 0;

  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toast._t);
    toast._t = setTimeout(() => toastEl.classList.remove('show'), 2100);
  }

  function updateDock() {
    const btns = Array.from(railEl.querySelectorAll('.rail-btn[data-rail]'));
    const tip = $('#hvRailTip');
    if (!dockPointer) {
      btns.forEach((b) => {
        b.style.setProperty('--dock-scale', '1');
        b.style.setProperty('--dock-shift', '0px');
      });
      if (tip) tip.classList.remove('show');
      return;
    }
    let hot = null, best = 1;
    btns.forEach((b) => {
      const r = b.getBoundingClientRect();
      const cy = r.top + r.height / 2;
      const dist = Math.abs(dockPointer.y - cy);
      if (dist >= dockRadius) {
        b.style.setProperty('--dock-scale', '1');
        b.style.setProperty('--dock-shift', '0px');
      } else {
        const t = 1 - dist / dockRadius;
        const s = t * t * (3 - 2 * t);
        const scale = 1 + dockGain * s;
        const shift = (cy - dockPointer.y) * 0.08 * s;
        b.style.setProperty('--dock-scale', scale.toFixed(3));
        b.style.setProperty('--dock-shift', `${shift.toFixed(2)}px`);
        if (scale > best) { best = scale; hot = { b, r }; }
      }
    });
    if (tip && hot) {
      tip.textContent = hot.b.dataset.label || '';
      tip.style.left = `${hot.r.right + 12}px`;
      tip.style.top = `${hot.r.top + hot.r.height / 2 - 14}px`;
      tip.classList.add('show');
    }
  }

  function renderRail() {
    const unreadCnt = state.threads.filter((t) => t.unread).length;
    railEl.innerHTML = `
      <div class="hv-rail-inner" data-eu-id="eu_L3_hv_rail_dock">
        <div class="hv-rail-items" data-eu-id="eu_L4_hv_rail_proximity">
          ${RAIL_ITEMS.map(([id, lbl, ico]) => {
            const badge = id === 'messages' && unreadCnt > 0 ? unreadCnt : 0;
            return `
              <button type="button" class="rail-btn" data-rail="${id}" data-label="${lbl}" aria-label="${lbl}" aria-current="${state.activeRoute === id ? 'page' : 'false'}">
                ${svgIcon(ico, 17)}
                ${badge ? `<span class="rail-badge">${badge}</span>` : ''}
              </button>
            `;
          }).join('')}
        </div>
        <div class="hv-rail-items">
          <button type="button" class="rail-btn" id="hvGearBtn" aria-label="Settings">${svgIcon('gear', 17)}</button>
          <button type="button" class="rail-btn" id="hvPowerBtn" aria-label="Reset session">${svgIcon('power', 17)}</button>
        </div>
      </div>
      <div id="hvRailTip" class="rail-tip"></div>
    `;
    const itemsBox = $('.hv-rail-items', railEl);
    itemsBox.addEventListener('pointermove', (e) => {
      dockPointer = { x: e.clientX, y: e.clientY };
      updateDock();
    });
    itemsBox.addEventListener('pointerleave', () => {
      dockPointer = null;
      updateDock();
    });
    railEl.querySelectorAll('[data-rail]').forEach((b) => b.addEventListener('click', () => navigateRoute(b.dataset.rail)));
    $('#hvGearBtn').addEventListener('click', (e) => openQuickDialog(e.currentTarget, 'quick'));
    $('#hvPowerBtn').addEventListener('click', () => { state.activeRoute = 'overview'; navigate('Overview'); toast('Workspace reset'); });
  }

  function exportCsv() {
    let rows = [];
    let fname = `haven-${state.activeDomain.toLowerCase()}-${state.salesPeriod.toLowerCase()}.csv`;
    if (state.activeRoute === 'orders') {
      const activeRange = state.orderFilter;
      const list = state.orders.filter((o) => activeRange === 'all' || o.status === activeRange);
      rows = ['Order_ID,Account,Plan,Amount,Status,Date', ...list.map((o) => `${o.id},"${o.account}","${o.plan}","${o.amount}",${o.status},${o.date}`)];
      fname = `haven-orders-${activeRange.toLowerCase()}.csv`;
    } else if (state.activeRoute === 'analytics') {
      const a = ANALYTICS_SERIES[state.analyticsGrain];
      rows = ['Stage,Share_Pct,Volume', ...a.funnel.map(([st, pct, vol]) => `${st},${pct},"${vol}"`)];
      fname = `haven-analytics-${state.analyticsGrain.toLowerCase()}.csv`;
    } else {
      const d = DOMAIN_PRESETS[state.activeDomain];
      const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      rows = ['Domain,Day,Sales_K,Target_Pct', ...days.map((day, i) => `${state.activeDomain},${day},${d.sales[i]},${state.targetPct}`)];
    }
    const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = fname;
    a.click();
    toast(`Exported ${fname}`);
  }

  function openQuickDialog(triggerEl, mode = 'quick') {
    state.lastFocus = triggerEl || document.activeElement;
    if (mode === 'order') {
      dialog.innerHTML = `
        <div class="hv-dlg-head"><h2 id="hv-dlg-title">Create New Order</h2><button type="button" class="pill-btn" id="hvDlgClose">Close</button></div>
        <form class="hv-dlg-body" id="hvDlgForm">
          <label>Account Name<input name="account" required value="Aether Robotics"></label>
          <label>Plan Package<input name="plan" required value="Enterprise 30 Seats"></label>
          <label>Amount (USD)<input name="amount" type="number" min="100" required value="3600"></label>
          <button type="submit" class="pill-btn" style="background:var(--hv-blue);justify-self:start;">Create Order</button>
        </form>
      `;
      dialog.showModal();
      $('#hvDlgClose', dialog).addEventListener('click', () => dialog.close());
      $('#hvDlgForm', dialog).addEventListener('submit', (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const amt = Number(fd.get('amount')) || 3600;
        const nextId = `ORD-${9429 + state.orders.length}`;
        state.orders.unshift({
          id: nextId,
          account: String(fd.get('account') || 'New Account'),
          plan: String(fd.get('plan') || 'Growth Plan'),
          amount: `$${amt.toLocaleString()}`,
          numeric: amt,
          status: 'Processing',
          date: '2026-11-23',
          owner: 'Sarah Chen',
          notes: 'Created from Orders workbench',
        });
        state.selectedOrderId = nextId;
        dialog.close();
        renderMain();
        toast(`Order ${nextId} added`);
      });
      return;
    }

    if (mode === 'event') {
      dialog.innerHTML = `
        <div class="hv-dlg-head"><h2 id="hv-dlg-title">Add Calendar Block</h2><button type="button" class="pill-btn" id="hvDlgClose">Close</button></div>
        <form class="hv-dlg-body" id="hvDlgForm">
          <label>Session Title<input name="title" required value="Q4 Architecture Walkthrough"></label>
          <label>Weekday
            <select name="day">
              <option value="Mon">Monday</option><option value="Tue">Tuesday</option><option value="Wed">Wednesday</option><option value="Thu">Thursday</option><option value="Fri">Friday</option>
            </select>
          </label>
          <label>Time<input name="time" required value="16:00"></label>
          <button type="submit" class="pill-btn" style="background:var(--hv-blue);justify-self:start;">Schedule Block</button>
        </form>
      `;
      dialog.showModal();
      $('#hvDlgClose', dialog).addEventListener('click', () => dialog.close());
      $('#hvDlgForm', dialog).addEventListener('submit', (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        state.events.push({
          id: `ev-${Date.now()}`,
          day: String(fd.get('day') || 'Wed'),
          time: String(fd.get('time') || '16:00'),
          title: String(fd.get('title') || 'Sync Session'),
          type: 'calls',
          owner: 'Sarah Chen',
        });
        dialog.close();
        renderMain();
        toast('Calendar block scheduled');
      });
      return;
    }

    dialog.innerHTML = `
      <div class="hv-dlg-head"><h2 id="hv-dlg-title">Add Quick Metric Note</h2><button type="button" class="pill-btn" id="hvDlgClose">Close</button></div>
      <form class="hv-dlg-body" id="hvDlgForm">
        <label>Domain Scope<input name="scope" value="${esc(state.activeDomain)}" readonly></label>
        <label>Goal Override (%)<input name="pct" type="number" min="5" max="100" value="${state.targetPct}"></label>
        <button type="submit" class="pill-btn" style="background:var(--hv-blue);justify-self:start;">Apply Target</button>
      </form>
    `;
    dialog.showModal();
    $('#hvDlgClose', dialog).addEventListener('click', () => dialog.close());
    $('#hvDlgForm', dialog).addEventListener('submit', (e) => {
      e.preventDefault();
      const val = Number(new FormData(e.target).get('pct'));
      if (Number.isFinite(val)) state.targetPct = Math.max(5, Math.min(100, val));
      dialog.close();
      renderMain();
    });
  }

  dialog.addEventListener('close', () => {
    if (state.lastFocus && typeof state.lastFocus.focus === 'function') state.lastFocus.focus();
  });

  function renderSubHeader(title, subtitle, extraControlsHtml = '') {
    return `
      <header class="hv-topbar">
        <div class="sub-page-head">
          <div>
            <h1>${esc(title)}</h1>
            <p class="tile-sub">${esc(subtitle)}</p>
          </div>
        </div>
        <div class="hv-top-actions">
          ${extraControlsHtml}
          <button type="button" class="pill-btn" id="hvBackHomeBtn">Home Overview</button>
          <div class="user-avatar" title="Sarah Chen · Head of Ops">SC</div>
        </div>
      </header>
    `;
  }

  function renderOverviewHtml() {
    const d = DOMAIN_PRESETS[state.activeDomain];
    const appItem = APPROVAL_QUEUE[state.approvalIdx % APPROVAL_QUEUE.length];
    const pendingCount = Math.max(0, APPROVAL_QUEUE.length - state.approvalIdx);
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const salesMax = Math.max(...d.sales, 40);
    const circ = 2 * Math.PI * 76;
    const dialDash = ((state.targetPct / 100) * circ).toFixed(1);
    const forecastPct = Math.min(100, state.targetPct + 18);
    const forecastDash = ((forecastPct / 100) * circ).toFixed(1);
    const team = [
      ['AR', 'Alma Reed · Lead', '#b45309'],
      ['JP', 'Jules Park · Ops', '#0f766e'],
      ['SC', 'Sarah Chen · Sales', '#1d4ed8'],
      ['MB', 'Milo Bell · Eng', '#6d28d9'],
    ];
    const secCur = Math.round((state.playPos / WAVE_HEIGHTS.length) * 212);
    const mm = String(Math.floor(secCur / 60)).padStart(2, '0');
    const ss = String(secCur % 60).padStart(2, '0');

    return `
      <header class="hv-topbar" data-eu-id="eu_L3_hv_nav_tabs">
        <div class="hv-tabs" role="tablist" data-eu-id="eu_L4_hv_tab_switch">
          ${Object.keys(DOMAIN_PRESETS).map((dom) => `
            <button type="button" class="hv-tab" role="tab" data-domain="${dom}" aria-selected="${state.activeDomain === dom}">${dom}</button>
          `).join('')}
        </div>
        <div class="hv-top-actions">
          <button type="button" class="pill-btn" id="hvCsvBtn">${svgIcon('download', 13)} CSV</button>
          <button type="button" class="circle-btn" id="hvAddBtn" aria-label="Quick target edit">${svgIcon('plus', 15)}</button>
          <div class="user-avatar" title="Sarah Chen · Head of Ops">SC</div>
        </div>
      </header>

      <div class="bento-grid">
        <div class="col-stack">
          <section class="glass-tile" data-eu-id="eu_L3_hv_team_card">
            <div class="tile-head">
              <div><h2>Team</h2><p class="tile-sub"><i class="dot-mint"></i> 4 online now</p></div>
              <button type="button" class="circle-btn solid" id="hvTeamAdd" aria-label="Team action">${svgIcon('plus', 14)}</button>
            </div>
            <div class="avatar-row">
              ${team.map(([ini, tip, bg]) => `<div class="tm-avatar" style="background:${bg}">${ini}<span class="tm-tip">${esc(tip)}</span></div>`).join('')}
              <div class="tm-avatar" style="background:rgba(255,255,255,0.16)">+3</div>
            </div>
          </section>

          <section class="glass-tile dial-tile" data-eu-id="eu_L3_hv_target_dial">
            <div class="tile-head">
              <div><h2>Quarterly Target</h2><p class="tile-sub">Q4 2026 · ${esc(state.activeDomain)}</p></div>
              <button type="button" class="hv-switch" id="hvForecastSwitch" role="switch" aria-checked="${state.showForecast}" aria-label="Toggle forecast"><i></i></button>
            </div>
            <div class="dial-wrap" data-eu-id="eu_L4_hv_dial_controls">
              <svg class="dial-svg" viewBox="0 0 196 196">
                <circle cx="98" cy="98" r="76" fill="none" stroke="rgba(255,255,255,0.14)" stroke-width="11"/>
                ${state.showForecast ? `<circle class="dial-arc" cx="98" cy="98" r="76" fill="none" stroke="rgba(96,165,250,0.34)" stroke-width="11" stroke-dasharray="${forecastDash} ${circ.toFixed(1)}" stroke-linecap="round" transform="rotate(-90 98 98)"/>` : ''}
                <circle class="dial-arc" cx="98" cy="98" r="76" fill="none" stroke="#3b82f6" stroke-width="11" stroke-dasharray="${dialDash} ${circ.toFixed(1)}" stroke-linecap="round" transform="rotate(-90 98 98)"/>
              </svg>
              <div class="dial-center">
                <strong>${state.targetPct}%</strong>
                <span>Achieved</span>
                ${state.showForecast ? `<small>${forecastPct}% forecast</small>` : ''}
              </div>
            </div>
            <div class="dial-stepper">
              <button type="button" class="step-btn" id="hvDialDec" aria-label="Decrease target">&minus;</button>
              <span>${esc(d.achieved)} of ${esc(d.goal)}</span>
              <button type="button" class="step-btn" id="hvDialInc" aria-label="Increase target">+</button>
            </div>
            <div>
              <p class="tile-sub" style="margin-bottom:8px;">Metric (${esc(state.activeMetric)})</p>
              <div class="metric-orbs">
                ${[['Revenue', '$'], ['Deals', 'D'], ['Calls', 'C'], ['Meetings', 'M']].map(([m, sym]) => `
                  <button type="button" class="orb-btn" data-metric="${m}" aria-pressed="${state.activeMetric === m}"><span>${sym}</span>${m}</button>
                `).join('')}
              </div>
            </div>
          </section>
        </div>

        <div class="col-stack">
          <section class="glass-tile" data-eu-id="eu_L3_hv_revenue_area">
            <div class="tile-head">
              <div><p class="tile-sub">Revenue</p><div class="big-metric">${esc(d.rev)} <small>/ ${esc(d.revGoal)}</small></div><span class="delta-mint">${esc(d.revDelta)} vs yesterday</span></div>
              <div class="seg-group" data-eu-id="eu_L4_hv_rev_range">
                ${['Today', 'Week', 'Month'].map((p) => `<button type="button" data-revp="${p}" aria-pressed="${state.revPeriod === p}">${p}</button>`).join('')}
              </div>
            </div>
            <svg viewBox="0 0 420 92" style="width:100%;height:92px;margin-top:8px;" aria-hidden="true">
              <defs><linearGradient id="hvSpline" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#ffffff" stop-opacity="0.32"/><stop offset="100%" stop-color="#ffffff" stop-opacity="0.02"/></linearGradient></defs>
              <path d="M0,78 C80,74 160,52 240,34 C310,19 365,24 420,42 L420,90 L0,90 Z" fill="url(#hvSpline)"/>
              <path d="M0,78 C80,74 160,52 240,34 C310,19 365,24 420,42" fill="none" stroke="rgba(255,255,255,0.88)" stroke-width="2.2"/>
            </svg>
          </section>

          <div class="mid-split">
            <section class="glass-tile" data-eu-id="eu_L3_hv_new_leads">
              <p class="tile-sub">This week</p>
              <h2 style="margin-top:2px;">New Leads</h2>
              <div class="big-metric" style="font-size:26px;margin-top:20px;">${esc(d.leads)} <span class="mini-tag">${esc(d.leadsDelta)}</span></div>
              <div style="display:flex;align-items:flex-end;gap:5px;height:44px;margin-top:12px;">
                ${[28, 38, 46, 56, 72, 92].map((h, i) => `<div style="flex:1;height:${h}%;border-radius:4px;background:${i === 5 ? 'var(--hv-blue)' : 'rgba(255,255,255,0.22)'}"></div>`).join('')}
              </div>
            </section>

            <section class="glass-tile" style="display:flex;flex-direction:column;" data-eu-id="eu_L3_hv_approvals">
              <p class="tile-sub">${pendingCount} pending</p>
              <h2 style="margin-top:2px;">Approvals</h2>
              <span class="app-tag" style="margin-top:10px;align-self:start;">${esc(appItem.tag)}</span>
              <div class="big-metric" style="font-size:24px;margin-top:8px;">${esc(appItem.amount)}</div>
              <p class="tile-sub" style="margin-top:4px;">${esc(appItem.client)}</p>
              <div class="app-actions" data-eu-id="eu_L4_hv_approve_action">
                <button type="button" class="btn-approve" id="hvApproveBtn">Approve</button>
                <button type="button" class="btn-reject" id="hvRejectBtn" aria-label="Skip approval">&times;</button>
              </div>
            </section>
          </div>

          <section class="glass-tile" style="flex:1 1 auto;" data-eu-id="eu_L3_hv_sales_bars">
            <div class="tile-head">
              <h2>Sales (k$)</h2>
              <div class="seg-group" data-eu-id="eu_L4_hv_sales_filter">
                ${['Week', 'Month', 'Year'].map((p) => `<button type="button" data-salep="${p}" aria-pressed="${state.salesPeriod === p}">${p}</button>`).join('')}
              </div>
            </div>
            <div class="bars-row">
              ${d.sales.map((val, idx) => `
                <div class="bar-col">
                  <div class="bar-fill ${idx === 2 ? 'active' : ''}" style="height:${Math.round((val / salesMax) * 70)}px" title="${days[idx]}: ${val}k"></div>
                  <span>${days[idx]}</span>
                </div>
              `).join('')}
            </div>
          </section>
        </div>

        <div class="col-stack">
          <section class="right-kpis" data-eu-id="eu_L3_hv_live_kpis_fold">
            <article class="glass-tile kpi-mini">
              <div class="kpi-mini-top"><span>Customers</span><button type="button" class="hv-switch" data-kpisw="customers" role="switch" aria-checked="${state.kpiSwitches.customers}"><i></i></button></div>
              <div class="kpi-mini-val"><strong>${esc(d.customers)}</strong><span class="mini-tag">+4.2%</span></div>
            </article>
            <article class="glass-tile kpi-mini">
              <div class="kpi-mini-top"><span>Pipeline</span><button type="button" class="hv-switch" data-kpisw="pipeline" role="switch" aria-checked="${state.kpiSwitches.pipeline}"><i></i></button></div>
              <div class="pipe-bars">
                <div><span>Lead</span><i style="width:68%"></i></div>
                <div><span>Qual</span><i style="width:52%"></i></div>
                <div><span>Won</span><i style="width:36%"></i></div>
              </div>
              <div class="kpi-mini-val"><strong>${esc(d.pipe)}</strong><span class="mini-tag">+9.6%</span></div>
            </article>
            <article class="glass-tile kpi-mini">
              <div class="kpi-mini-top"><span class="live-badge">LIVE</span><button type="button" class="hv-switch" data-kpisw="live" role="switch" aria-checked="${state.kpiSwitches.live}"><i></i></button></div>
              <div class="kpi-mini-val"><strong>${esc(d.activeUsers)}</strong><span class="mini-tag">+2.8%</span></div>
              <p class="tile-sub">Active Users</p>
            </article>
            <article class="glass-tile kpi-mini">
              <div class="kpi-mini-top"><span>Open Tickets</span><button type="button" class="hv-switch" data-kpisw="tickets" role="switch" aria-checked="${state.kpiSwitches.tickets}"><i></i></button></div>
              <div class="kpi-mini-val"><strong>${esc(d.tickets)}</strong><span class="delta-rose">-6.4%</span></div>
            </article>
          </section>

          <section class="glass-tile player-card" data-eu-id="eu_L3_hv_call_player">
            <div class="tile-head">
              <div><h2>Discovery Call &middot; Northwind Co.</h2><p class="tile-sub">Sarah Chen, Head of Ops</p></div>
              <button type="button" class="pill-btn" id="hvSpeedBtn">${state.speed}x</button>
            </div>
            <div data-eu-id="eu_L4_hv_wave_playback">
              <div class="waveform" id="hvWave">
                ${WAVE_HEIGHTS.map((h, i) => `<span class="wave-bar ${i <= state.playPos ? 'played' : ''}" data-widx="${i}" style="height:${h}px"></span>`).join('')}
              </div>
              <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--hv-muted);margin-top:8px;font-variant-numeric:tabular-nums;">
                <span>${mm}:${ss}</span>
                <span style="color:var(--hv-mint);">Positive sentiment</span>
                <span>03:32</span>
              </div>
              <div class="player-ctrls" style="margin-top:8px;">
                <button type="button" class="step-btn" id="hvBack10" aria-label="Rewind">&laquo;</button>
                <button type="button" class="play-circle" id="hvPlayBtn" aria-label="Play or pause">${svgIcon(state.playing ? 'pause' : 'play', 16)}</button>
                <button type="button" class="step-btn" id="hvFwd10" aria-label="Forward">&raquo;</button>
              </div>
            </div>
          </section>
        </div>
      </div>
    `;
  }

  function renderKpiIconCard({ icon, tone, label, val, sub, chartHtml }) {
    return `
      <article class="glass-tile hv-kpi-icon-card">
        <div class="hv-kpi-left">
          ${iconOrb(icon, tone)}
          <div class="hv-kpi-meta">
            <span class="tile-sub">${esc(label)}</span>
            <div class="hv-kpi-val">${esc(val)}</div>
            <span class="hv-kpi-sub">${esc(sub)}</span>
          </div>
        </div>
        ${chartHtml}
      </article>
    `;
  }

  function renderSearchHtml() {
    const q = state.searchQuery.trim().toLowerCase();
    const corpus = [
      ...state.orders.map((o) => ({ kind: 'order', icon: 'bag', tone: 'blue', route: 'orders', id: o.id, title: `${o.id} · ${o.account}`, meta: `${o.plan} · ${o.amount} · ${o.status}` })),
      ...state.customers.map((c) => ({ kind: 'customer', icon: 'users', tone: 'mint', route: 'customers', id: c.id, title: c.name, meta: `${c.tier} · ARR ${c.arr} · Health ${c.health}%` })),
      ...state.products.map((p) => ({ kind: 'product', icon: 'box', tone: 'violet', route: 'products', id: p.id, title: p.name, meta: `${p.category} · ${p.price} · MRR ${p.mrr}` })),
      ...state.threads.map((t) => ({ kind: 'message', icon: 'msg', tone: 'amber', route: 'messages', id: t.id, title: t.sender, meta: `${t.role} · ${t.time}` })),
    ];
    const hits = corpus.filter((item) => {
      if (state.searchFilter !== 'all' && item.kind !== state.searchFilter) return false;
      if (!q) return true;
      return `${item.title} ${item.meta} ${item.id}`.toLowerCase().includes(q);
    });
    const ordCnt = state.orders.length;
    const cusCnt = state.customers.length;
    const prdCnt = state.products.length;
    const msgCnt = state.threads.length;
    const totCnt = Math.max(1, ordCnt + cusCnt + prdCnt + msgCnt);

    return `
      <div class="hv-page-fill">
        ${renderSubHeader('Global Search & Telemetry Index', 'Cross-module glass index with latency telemetry and entity distribution')}
        <section class="hv-grid-4">
          ${renderKpiIconCard({ icon: 'database', tone: 'blue', label: 'Indexed Entities', val: `${corpus.length * 74}`, sub: '+6.8% synced', chartHtml: sparklineSvg([118, 126, 129, 134, 141, 146, 152], 'srch-1', '#60a5fa') })}
          ${renderKpiIconCard({ icon: 'bolt', tone: 'mint', label: 'Query P50 Latency', val: '18ms', sub: '-4ms faster', chartHtml: miniBarsHtml([28, 25, 24, 21, 19, 18], 'mint') })}
          ${renderKpiIconCard({ icon: 'sparkles', tone: 'violet', label: 'Vector Cache Hit', val: '96.4%', sub: 'L1 Glass Cache', chartHtml: sparklineSvg([91, 92, 93, 94, 95, 96, 96.4], 'srch-2', '#a78bfa') })}
          ${renderKpiIconCard({ icon: 'cpu', tone: 'amber', label: 'Active Shards', val: '4 / 4', sub: '0.02% error rate', chartHtml: miniBarsHtml([62, 74, 80, 76, 88, 92], 'amber') })}
        </section>

        <div class="hv-bento-3">
          <div class="hv-col-fill">
            <section class="glass-tile">
              <div class="tile-head" style="margin-bottom:10px;">
                <div class="hv-head-title">${iconOrb('search', 'blue', 'sm')}<h2>Query Console</h2></div>
                <span class="mini-tag">Instant</span>
              </div>
              <div class="hv-search-box">
                ${svgIcon('search', 16)}
                <input id="hvGlobalSearchInput" type="search" value="${esc(state.searchQuery)}" placeholder="Northwind, ORD-9428, Enterprise...">
              </div>
              <div class="seg-group" style="margin-top:10px;">
                ${[['all', 'All'], ['order', 'Orders'], ['customer', 'Accounts'], ['product', 'SKUs'], ['message', 'Inbox']].map(([k, l]) => `<button type="button" data-sflt="${k}" aria-pressed="${state.searchFilter === k}">${l}</button>`).join('')}
              </div>
              <div class="hv-top-actions" style="margin-top:10px;">
                ${['Northwind', 'Lumen', 'SSO', 'Enterprise'].map((tag) => `<button type="button" class="pill-btn" data-sq="${tag}">${svgIcon('tag', 11)} ${tag}</button>`).join('')}
              </div>
            </section>

            <section class="glass-tile hv-tile-grow">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('trendUp', 'mint', 'sm')}<h2>7D Search Volume</h2></div>
                <span class="delta-mint">+24.1% wk</span>
              </div>
              ${areaLineChartSvg({ uid: 'srch-vol', labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], primary: [410, 480, 520, 495, 610, 645, 720], secondary: [320, 360, 410, 405, 480, 510, 580], height: 144 })}
              <div class="hv-chart-foot"><span>Solid: Queries · Dashed: Cache Hits</span><strong>Peak 720 req/hr</strong></div>
            </section>
          </div>

          <div class="hv-col-fill">
            <section class="glass-tile hv-tile-grow">
              <div class="tile-head" style="margin-bottom:8px;">
                <div class="hv-head-title">${iconOrb('layers', 'violet', 'sm')}<h2>Matched Records (${hits.length})</h2></div>
                <span class="tile-sub">Click row to navigate</span>
              </div>
              <div class="hv-list-stack" style="max-height:280px;overflow-y:auto;">
                ${hits.slice(0, 4).map((h) => `
                  <button type="button" class="hv-list-row" data-jump-route="${h.route}" data-jump-id="${esc(h.id)}">
                    <div style="display:flex;align-items:center;gap:10px;min-width:0;flex:1;">
                      ${iconOrb(h.icon, h.tone, 'sm')}
                      <div class="hv-row-main">
                        <strong>${esc(h.title)}</strong>
                        <span>${esc(h.meta)}</span>
                      </div>
                    </div>
                    <span class="hv-status-pill">${esc(h.kind.toUpperCase())} &rarr;</span>
                  </button>
                `).join('') || '<p class="tile-sub">No matching entities found.</p>'}
              </div>
            </section>

            <section class="glass-tile">
              <div class="tile-head" style="margin-bottom:6px;">
                <div class="hv-head-title">${iconOrb('activity', 'blue', 'sm')}<h2>Shard Latency (P50 vs P95)</h2></div>
                <span class="tile-sub">ms</span>
              </div>
              ${groupedBarChartSvg({ uid: 'srch-lat', labels: ['Orders', 'Accounts', 'SKUs', 'Inbox', 'Events'], seriesA: [16, 14, 12, 19, 15], seriesB: [34, 29, 25, 41, 31], height: 118 })}
            </section>
          </div>

          <div class="hv-col-fill">
            <section class="glass-tile">
              <div class="tile-head" style="margin-bottom:8px;">
                <div class="hv-head-title">${iconOrb('compass', 'blue', 'sm')}<h2>Index Distribution</h2></div>
                <span class="tile-sub">${totCnt} roots</span>
              </div>
              ${donutRingSvg({
                centerVal: `${hits.length}`,
                centerSub: 'Matched',
                segments: [
                  { label: 'Orders', pct: Math.round((ordCnt / totCnt) * 100), val: `${ordCnt} rows`, color: '#60a5fa' },
                  { label: 'Accounts', pct: Math.round((cusCnt / totCnt) * 100), val: `${cusCnt} rows`, color: '#4ade80' },
                  { label: 'Products', pct: Math.round((prdCnt / totCnt) * 100), val: `${prdCnt} SKUs`, color: '#a78bfa' },
                  { label: 'Threads', pct: Math.round((msgCnt / totCnt) * 100), val: `${msgCnt} live`, color: '#fbbf24' },
                ],
              })}
            </section>

            <section class="glass-tile hv-tile-grow">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('filter', 'mint', 'sm')}<h2>Top Search Signals</h2></div>
                <span class="tile-sub">7d hits</span>
              </div>
              ${funnelChartHtml([
                ['Northwind Co.', 92, '1,840', 'linear-gradient(90deg,#60a5fa,#3b82f6)'],
                ['Annual Renewal', 74, '1,320', 'linear-gradient(90deg,#4ade80,#10b981)'],
                ['SSO Guard', 58, '940', 'linear-gradient(90deg,#a78bfa,#7c3aed)'],
                ['Wire Settlement', 41, '610', 'linear-gradient(90deg,#fbbf24,#d97706)'],
              ])}
              <div class="hv-quick-grid" style="margin-top:10px;">
                <button type="button" class="hv-quick-btn" data-jump-route="orders" data-jump-id="ORD-9428">${iconOrb('bag', 'blue', 'sm')}<div><strong>Orders Queue</strong><span>${ordCnt} active</span></div></button>
                <button type="button" class="hv-quick-btn" data-jump-route="analytics" data-jump-id="ana">${iconOrb('chart', 'mint', 'sm')}<div><strong>Telemetry</strong><span>NRR & Funnel</span></div></button>
              </div>
            </section>
          </div>
        </div>
      </div>
    `;
  }

  function renderOrdersHtml() {
    const activeRange = state.orderFilter;
    const filtered = state.orders.filter((o) => activeRange === 'all' || o.status === activeRange);
    const sel = filtered.find((o) => o.id === state.selectedOrderId) || filtered[0] || state.orders[0];
    const totalAmt = state.orders.reduce((s, o) => s + o.numeric, 0);
    const paidCnt = state.orders.filter((o) => o.status === 'Paid').length;
    const procCnt = state.orders.filter((o) => o.status === 'Processing').length;
    const refCnt = state.orders.filter((o) => o.status === 'Refunded').length;
    const totOrd = Math.max(1, state.orders.length);
    const stepStage = sel ? (sel.status === 'Paid' ? 4 : (sel.status === 'Processing' ? 2 : 1)) : 2;
    const slaCells = [
      { label: 'D1', level: 4 }, { label: 'D2', level: 3 }, { label: 'D3', level: 4 }, { label: 'D4', level: 2 }, { label: 'D5', level: 4 }, { label: 'D6', level: 3 }, { label: 'D7', level: 4 },
      { label: 'D8', level: 3 }, { label: 'D9', level: 4 }, { label: 'D10', level: 4 }, { label: 'D11', level: 1 }, { label: 'D12', level: 3 }, { label: 'D13', level: 4 }, { label: 'D14', level: 3 },
      { label: 'D15', level: 4 }, { label: 'D16', level: 4 }, { label: 'D17', level: 2 }, { label: 'D18', level: 3 }, { label: 'D19', level: 4 }, { label: 'D20', level: 4 }, { label: 'D21', level: 4 },
    ];

    return `
      <div class="hv-page-fill">
        ${renderSubHeader('Orders & Billing Fulfillment', 'Settlement velocity, multi-stage fulfillment & invoice automation', `
          <button type="button" class="pill-btn" id="hvCsvBtn">${svgIcon('download', 13)} Orders CSV</button>
          <button type="button" class="pill-btn" id="hvNewOrderBtn" style="background:var(--hv-blue);">${svgIcon('plus', 13)} New Order</button>
        `)}
        <section class="hv-grid-4">
          ${renderKpiIconCard({ icon: 'creditCard', tone: 'blue', label: 'Gross Volume', val: `$${(totalAmt / 1000).toFixed(1)}k`, sub: '+14.2% vs last wk', chartHtml: sparklineSvg([18, 21, 19, 24, 25, 26, 29], 'ord-1', '#60a5fa') })}
          ${renderKpiIconCard({ icon: 'check', tone: 'mint', label: 'Settled Orders', val: `${paidCnt} / ${totOrd}`, sub: 'Wire & Stripe', chartHtml: miniBarsHtml([45, 58, 62, 74, 82, 95], 'mint') })}
          ${renderKpiIconCard({ icon: 'clock', tone: 'amber', label: 'In Processing', val: `${procCnt}`, sub: 'Awaiting signoff', chartHtml: sparklineSvg([4, 3, 5, 3, 2, 3, procCnt || 1], 'ord-2', '#fbbf24') })}
          ${renderKpiIconCard({ icon: 'trendUp', tone: 'violet', label: 'Average Ticket', val: `$${Math.round(totalAmt / totOrd).toLocaleString()}`, sub: 'Enterprise lift', chartHtml: miniBarsHtml([38, 44, 52, 60, 68, 86], 'violet') })}
        </section>

        <div class="hv-bento-3">
          <div class="hv-col-fill">
            <section class="glass-tile hv-tile-grow">
              <div class="tile-head" style="margin-bottom:8px;">
                <div class="hv-head-title">${iconOrb('bag', 'blue', 'sm')}<h2>Order Stream</h2></div>
                <div class="seg-group">
                  ${['all', 'Paid', 'Processing', 'Refunded'].map((st) => `<button type="button" data-oflt="${st}" aria-pressed="${state.orderFilter === st}">${st === 'all' ? 'All' : st}</button>`).join('')}
                </div>
              </div>
              <div class="hv-list-stack" style="max-height:280px;overflow-y:auto;">
                ${filtered.map((o) => `
                  <button type="button" class="hv-list-row" data-oid="${esc(o.id)}" aria-selected="${sel && sel.id === o.id}">
                    <div style="display:flex;align-items:center;gap:9px;min-width:0;flex:1;">
                      ${iconOrb(o.status === 'Paid' ? 'check' : 'creditCard', o.status === 'Paid' ? 'mint' : (o.status === 'Refunded' ? 'amber' : 'blue'), 'sm')}
                      <div class="hv-row-main">
                        <strong>${esc(o.id)} · ${esc(o.account)}</strong>
                        <span>${esc(o.plan)} · ${esc(o.date)}</span>
                      </div>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                      <strong>${esc(o.amount)}</strong>
                      <span class="hv-status-pill ${o.status.toLowerCase()}">${esc(o.status)}</span>
                    </div>
                  </button>
                `).join('')}
              </div>
            </section>

            <section class="glass-tile">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('trendUp', 'mint', 'sm')}<h2>Weekly Settlement Velocity</h2></div>
                <span class="delta-mint">+19.4%</span>
              </div>
              ${areaLineChartSvg({ uid: 'ord-gmv', labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], primary: [14, 19, 17, 24, 28, 25, 34], primaryColor: '#4ade80', height: 122 })}
            </section>
          </div>

          <div class="hv-col-fill">
            ${sel ? `
              <section class="glass-tile">
                <div class="tile-head">
                  <div><p class="tile-sub">${esc(sel.date)} · Owner ${esc(sel.owner)}</p><h2>${esc(sel.id)} · ${esc(sel.account)}</h2></div>
                  <span class="hv-status-pill ${sel.status.toLowerCase()}">${esc(sel.status)}</span>
                </div>
                <div class="big-metric" style="margin-top:8px;">${esc(sel.amount)} <small>${esc(sel.plan)}</small></div>
                <p class="tile-sub" style="margin-top:4px;">${esc(sel.notes)}</p>
                <div class="hv-step-bar">
                  ${[['Created', 'tag', 1], ['Verified', 'shield', 2], ['Provision', 'truck', 3], ['Settled', 'check', 4]].map(([lbl, ic, idx]) => `
                    <div class="hv-step-node ${stepStage > idx ? 'is-done' : (stepStage === idx ? 'is-active' : '')}">
                      <div class="hv-step-top"><span>${lbl}</span>${svgIcon(ic, 12)}</div>
                      <span class="tile-sub">${stepStage >= idx ? 'Done' : 'Queue'}</span>
                    </div>
                  `).join('')}
                </div>
                <div class="hv-switch-row" style="margin-top:10px;">
                  <div class="hv-switch-info">${iconOrb('bolt', 'blue', 'sm')}<div><strong style="font-size:12px;">Auto-Invoice Settlement</strong><span class="tile-sub" style="display:block;">Treasury wire webhook reconciliation</span></div></div>
                  <button type="button" class="hv-switch" id="hvAutoInvoiceSwitch" role="switch" aria-checked="${state.autoInvoice}" aria-label="Auto-Invoice Settlement"><i></i></button>
                </div>
                <div class="app-actions">
                  <button type="button" class="btn-approve" id="hvMarkPaidBtn" data-oid="${esc(sel.id)}">Mark Paid</button>
                  <button type="button" class="pill-btn" id="hvRefundOrderBtn" data-oid="${esc(sel.id)}">Refund</button>
                </div>
              </section>
            ` : ''}

            <section class="glass-tile hv-tile-grow">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('chart', 'violet', 'sm')}<h2>Revenue by Plan Tier (k$)</h2></div>
                <span class="tile-sub">This vs Last Month</span>
              </div>
              ${groupedBarChartSvg({ uid: 'ord-tier', labels: ['Ent', 'Growth', 'Add-on', 'Core'], seriesA: [14.4, 8.6, 5.9, 3.2], seriesB: [11.2, 6.8, 4.1, 2.9], colorA: '#60a5fa', colorB: '#a78bfa', height: 128 })}
            </section>
          </div>

          <div class="hv-col-fill">
            <section class="glass-tile">
              <div class="tile-head" style="margin-bottom:8px;">
                <div class="hv-head-title">${iconOrb('sliders', 'blue', 'sm')}<h2>Status Mix</h2></div>
                <span class="tile-sub">${totOrd} total</span>
              </div>
              ${donutRingSvg({
                centerVal: `$${(totalAmt / 1000).toFixed(1)}k`,
                centerSub: 'Total GMV',
                segments: [
                  { label: 'Paid', pct: Math.max(15, Math.round((paidCnt / totOrd) * 100)), val: `${paidCnt} orders`, color: '#4ade80' },
                  { label: 'Processing', pct: Math.max(12, Math.round((procCnt / totOrd) * 100)), val: `${procCnt} queue`, color: '#60a5fa' },
                  { label: 'Refunded', pct: Math.max(8, Math.round((refCnt / totOrd) * 100)), val: `${refCnt} ref`, color: '#fbbf24' },
                ],
              })}
            </section>

            <section class="glass-tile">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('cal', 'mint', 'sm')}<h2>21-Day Clearing SLA</h2></div>
                <span class="mini-tag">98.4%</span>
              </div>
              ${heatmapGridHtml(slaCells)}
            </section>

            <section class="glass-tile hv-tile-grow">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('globe', 'amber', 'sm')}<h2>Payment Rail Share</h2></div>
                <span class="tile-sub">Stripe + ACH</span>
              </div>
              <div class="hv-channel-stack">
                <div class="hv-channel-seg" style="width:58%;background:#60a5fa;"></div>
                <div class="hv-channel-seg" style="width:27%;background:#4ade80;"></div>
                <div class="hv-channel-seg" style="width:15%;background:#a78bfa;"></div>
              </div>
              <div class="hv-chart-foot"><span>Wire 58%</span><span>Stripe 27%</span><span>ACH 15%</span></div>
              <div class="hv-note-item"><span>Treasury Auto-Clear · 14h avg</span><strong>$14.4k</strong></div>
            </section>
          </div>
        </div>
      </div>
    `;
  }

  function renderProductsHtml() {
    const filtered = state.products.filter((p) => state.productFilter === 'all' || p.category === state.productFilter);
    const activeCount = state.products.filter((p) => p.active).length;
    const avgSeat = Math.round(state.products.reduce((s, p) => s + p.seats, 0) / Math.max(1, state.products.length));

    return `
      <div class="hv-page-fill">
        ${renderSubHeader('Product Catalog & SKU Telemetry', `${activeCount} of ${state.products.length} commercial SKUs enabled in spatial storefront`, `
          <div class="seg-group">
            ${['all', 'Plans', 'Add-ons', 'Services'].map((c) => `<button type="button" data-pflt="${c}" aria-pressed="${state.productFilter === c}">${c === 'all' ? 'All SKUs' : c}</button>`).join('')}
          </div>
        `)}
        <section class="hv-grid-4">
          ${renderKpiIconCard({ icon: 'box', tone: 'blue', label: 'Live Storefront SKUs', val: `${activeCount} / ${state.products.length}`, sub: 'Commercial catalog', chartHtml: miniBarsHtml([60, 72, 78, 84, 90, 96], 'blue') })}
          ${renderKpiIconCard({ icon: 'trendUp', tone: 'mint', label: 'Recurring Catalog MRR', val: '$376.5k', sub: '+16.8% QoQ', chartHtml: sparklineSvg([245, 272, 290, 318, 344, 360, 376.5], 'prd-1', '#4ade80') })}
          ${renderKpiIconCard({ icon: 'users', tone: 'violet', label: 'Seat Utilization', val: `${avgSeat}%`, sub: 'Licensed capacity', chartHtml: miniBarsHtml([54, 62, 68, 70, 74, avgSeat], 'violet') })}
          ${renderKpiIconCard({ icon: 'bolt', tone: 'amber', label: 'Expansion Attach', val: '+19.4%', sub: 'Waveform AI attach', chartHtml: sparklineSvg([11, 13, 14, 16, 17, 18.5, 19.4], 'prd-2', '#fbbf24') })}
        </section>

        <div class="hv-bento-2-1">
          <div class="hv-col-fill">
            <section class="hv-grid-3">
              ${filtered.map((p) => `
                <article class="glass-tile" style="display:flex;flex-direction:column;gap:8px;padding:13px 15px;">
                  <div class="tile-head">
                    <div class="hv-head-title">${iconOrb(p.category === 'Plans' ? 'layers' : (p.category === 'Add-ons' ? 'sparkles' : 'webhook'), p.active ? 'blue' : 'amber', 'sm')}<span class="app-tag">${esc(p.category.toUpperCase())}</span></div>
                    <button type="button" class="hv-switch" data-ptog="${esc(p.id)}" role="switch" aria-checked="${p.active}" aria-label="Toggle ${esc(p.name)}"><i></i></button>
                  </div>
                  <h2 style="font-size:14px;">${esc(p.name)}</h2>
                  <div class="big-metric" style="font-size:20px;margin-top:0;">${esc(p.price)} <small>· ${esc(p.mrr)}</small></div>
                  <p class="tile-sub" style="line-height:1.35;">${esc(p.desc)}</p>
                  <div style="margin-top:auto;">
                    <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--hv-muted);margin-bottom:4px;"><span>Seats</span><strong>${p.seats}%</strong></div>
                    <div class="hv-progress-track"><div class="hv-progress-fill" style="width:${p.seats}%"></div></div>
                  </div>
                </article>
              `).join('')}
            </section>

            <section class="glass-tile hv-tile-grow">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('chart', 'blue', 'sm')}<h2>6-Month SKU MRR Growth (Core Plans vs Add-ons)</h2></div>
                <span class="delta-mint">+21.8% half-yr</span>
              </div>
              ${groupedBarChartSvg({ uid: 'prd-mrr', labels: ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'], seriesA: [192, 208, 224, 238, 249, 263], seriesB: [48, 56, 67, 79, 91, 114], width: 680, height: 156 })}
            </section>
          </div>

          <div class="hv-col-fill">
            <section class="glass-tile">
              <div class="tile-head" style="margin-bottom:8px;">
                <div class="hv-head-title">${iconOrb('compass', 'violet', 'sm')}<h2>MRR Mix by Tier</h2></div>
                <span class="tile-sub">$376.5k</span>
              </div>
              ${donutRingSvg({
                centerVal: '$376k',
                centerSub: 'Total MRR',
                segments: [
                  { label: 'Core Plans', pct: 69, val: '$262.6k', color: '#60a5fa' },
                  { label: 'AI Add-ons', pct: 19, val: '$71.4k', color: '#4ade80' },
                  { label: 'Services', pct: 12, val: '$42.5k', color: '#a78bfa' },
                ],
              })}
            </section>

            <section class="glass-tile">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('shield', 'mint', 'sm')}<h2>Product Fit 6D Radar</h2></div>
                <span class="mini-tag">Score 88</span>
              </div>
              ${radarChartSvg({
                uid: 'prd-rad',
                color: '#60a5fa',
                axes: [
                  { label: 'Adoption', score: 91 },
                  { label: 'Margin', score: 86 },
                  { label: 'NRR', score: 94 },
                  { label: 'Uptime', score: 98 },
                  { label: 'Attach', score: 78 },
                  { label: 'Velocity', score: 84 },
                ],
              })}
            </section>

            <section class="glass-tile hv-tile-grow">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('filter', 'amber', 'sm')}<h2>Tier Expansion Funnel</h2></div>
                <span class="tile-sub">Pilot &rarr; Ent</span>
              </div>
              ${funnelChartHtml([
                ['Core Seats', 100, '3,240', 'linear-gradient(90deg,#60a5fa,#3b82f6)'],
                ['Growth Upgrade', 68, '2,203', 'linear-gradient(90deg,#4ade80,#10b981)'],
                ['Waveform AI Add-on', 44, '1,425', 'linear-gradient(90deg,#a78bfa,#7c3aed)'],
                ['Enterprise Grid', 29, '940', 'linear-gradient(90deg,#fbbf24,#f59e0b)'],
              ])}
            </section>
          </div>
        </div>
      </div>
    `;
  }

  function renderCustomersHtml() {
    const filtered = state.customers.filter((c) => state.customerFilter === 'all' || c.tier === state.customerFilter);
    const sel = filtered.find((c) => c.id === state.selectedCustomerId) || filtered[0] || state.customers[0];
    const avgHealth = Math.round(state.customers.reduce((s, c) => s + c.health, 0) / Math.max(1, state.customers.length));
    const hBase = sel ? sel.health : 82;
    const cusCells = [
      { label: 'W1', level: 3 }, { label: 'W1', level: 4 }, { label: 'W1', level: 3 }, { label: 'W1', level: 4 }, { label: 'W1', level: 4 }, { label: 'W1', level: 2 }, { label: 'W1', level: 1 },
      { label: 'W2', level: 4 }, { label: 'W2', level: 4 }, { label: 'W2', level: 3 }, { label: 'W2', level: 4 }, { label: 'W2', level: 3 }, { label: 'W2', level: 2 }, { label: 'W2', level: 2 },
      { label: 'W3', level: 3 }, { label: 'W3', level: 4 }, { label: 'W3', level: 4 }, { label: 'W3', level: 4 }, { label: 'W3', level: 4 }, { label: 'W3', level: 3 }, { label: 'W3', level: 2 },
      { label: 'W4', level: 4 }, { label: 'W4', level: 4 }, { label: 'W4', level: 4 }, { label: 'W4', level: 3 }, { label: 'W4', level: 4 }, { label: 'W4', level: 3 }, { label: 'W4', level: 4 },
    ];

    return `
      <div class="hv-page-fill">
        ${renderSubHeader('Customer Accounts & Health Telemetry', 'ARR cohort expansion, account 6D radar & executive check-in log', `
          <div class="seg-group">
            ${['all', 'Enterprise', 'Growth', 'At Risk'].map((t) => `<button type="button" data-cflt="${t}" aria-pressed="${state.customerFilter === t}">${t === 'all' ? 'All Tiers' : t}</button>`).join('')}
          </div>
        `)}
        <section class="hv-grid-4">
          ${renderKpiIconCard({ icon: 'users', tone: 'blue', label: 'Managed Portfolio ARR', val: '$394.5k', sub: '+18.1% YoY', chartHtml: sparklineSvg([290, 310, 326, 344, 362, 379, 394.5], 'cus-1', '#60a5fa') })}
          ${renderKpiIconCard({ icon: 'activity', tone: 'mint', label: 'Avg Health Index', val: `${avgHealth}%`, sub: 'Composite SLA', chartHtml: miniBarsHtml([74, 78, 80, 79, 84, avgHealth], 'mint') })}
          ${renderKpiIconCard({ icon: 'shield', tone: 'violet', label: 'Zero-Churn Streak', val: '94 days', sub: 'Enterprise SLA', chartHtml: sparklineSvg([82, 85, 88, 90, 92, 93, 94], 'cus-2', '#a78bfa') })}
          ${renderKpiIconCard({ icon: 'bell', tone: 'amber', label: 'Risk Watchlist', val: `${state.customers.filter((c) => c.tier === 'At Risk').length} acct`, sub: 'Follow-up active', chartHtml: miniBarsHtml([40, 32, 28, 22, 18, 16], 'amber') })}
        </section>

        <div class="hv-bento-3">
          <div class="hv-col-fill">
            <section class="glass-tile hv-tile-grow">
              <div class="tile-head" style="margin-bottom:8px;">
                <div class="hv-head-title">${iconOrb('users', 'blue', 'sm')}<h2>Active Accounts (${filtered.length})</h2></div>
                <span class="tile-sub">Health Ring</span>
              </div>
              <div class="hv-list-stack">
                ${filtered.map((c) => `
                  <button type="button" class="hv-list-row" data-cid="${esc(c.id)}" aria-selected="${sel && sel.id === c.id}">
                    <div style="display:flex;align-items:center;gap:10px;min-width:0;flex:1;">
                      <div class="tm-avatar" style="margin-left:0;background:${c.color}">${esc(c.initials)}</div>
                      <div class="hv-row-main"><strong>${esc(c.name)}</strong><span>${esc(c.tier)} · ARR ${esc(c.arr)}</span></div>
                    </div>
                    ${ringMiniHtml(c.health, c.health >= 85 ? '#4ade80' : (c.health >= 70 ? '#60a5fa' : '#fbbf24'))}
                  </button>
                `).join('')}
              </div>
            </section>

            <section class="glass-tile">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('trendUp', 'mint', 'sm')}<h2>Net ARR Expansion</h2></div>
                <span class="delta-mint">121% NRR</span>
              </div>
              ${areaLineChartSvg({ uid: 'cus-arr', labels: ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'], primary: [310, 328, 342, 358, 376, 394.5], secondary: [295, 305, 315, 322, 330, 338], primaryColor: '#60a5fa', secondaryColor: '#4ade80', height: 122 })}
            </section>
          </div>

          <div class="hv-col-fill">
            ${sel ? `
              <section class="glass-tile">
                <div class="tile-head">
                  <div><span class="hv-status-pill ${sel.badge.toLowerCase()}">${esc(sel.tier)} · Health ${sel.health}%</span><h2 style="margin-top:6px;">${esc(sel.name)}</h2><p class="tile-sub">${esc(sel.contact)}</p></div>
                  <div class="big-metric" style="font-size:20px;">${esc(sel.arr)}</div>
                </div>
                ${radarChartSvg({
                  uid: `cus-rad-${sel.id}`,
                  color: sel.health >= 85 ? '#4ade80' : '#fbbf24',
                  axes: [
                    { label: 'Adoption', score: Math.min(99, hBase + 4) },
                    { label: 'NPS', score: Math.max(48, hBase - 6) },
                    { label: 'SLA', score: Math.min(98, hBase + 7) },
                    { label: 'Seats', score: Math.min(96, hBase + 2) },
                    { label: 'Billing', score: Math.min(99, hBase + 5) },
                    { label: 'Sponsor', score: Math.max(52, hBase - 3) },
                  ],
                })}
                <div class="hv-switch-row">
                  <div class="hv-switch-info">${iconOrb('shield', 'mint', 'sm')}<div><strong style="font-size:12px;">Auto-Renewal Guardrail</strong><span class="tile-sub" style="display:block;">Alert 30d before usage drop</span></div></div>
                  <button type="button" class="hv-switch" id="hvRenewGuardSwitch" role="switch" aria-checked="${state.autoRenewGuard}" aria-label="Auto-Renewal Guardrail"><i></i></button>
                </div>
              </section>

              <section class="glass-tile hv-tile-grow">
                <div class="tile-head" style="margin-bottom:8px;">
                  <div class="hv-head-title">${iconOrb('mail', 'violet', 'sm')}<h2>Executive Touchpoints</h2></div>
                  <span class="tile-sub">${sel.notes.length} logs</span>
                </div>
                <div class="hv-list-stack" style="max-height:130px;overflow-y:auto;">
                  ${sel.notes.map((n) => `<div class="hv-note-item"><span>${esc(n.text)}</span><span style="color:var(--hv-muted);white-space:nowrap;">${esc(n.ts)}</span></div>`).join('')}
                </div>
                <form id="hvCustNoteForm" class="hv-chat-compose" style="margin-top:8px;" data-cid="${esc(sel.id)}">
                  <input id="hvCustNoteInput" type="text" required placeholder="Add follow-up check-in note...">
                  <button type="submit" class="pill-btn" style="background:var(--hv-blue);">Log Note</button>
                </form>
              </section>
            ` : ''}
          </div>

          <div class="hv-col-fill">
            <section class="glass-tile">
              <div class="tile-head" style="margin-bottom:8px;">
                <div class="hv-head-title">${iconOrb('layers', 'blue', 'sm')}<h2>ARR Tier Split</h2></div>
                <span class="tile-sub">4 Cohorts</span>
              </div>
              ${donutRingSvg({
                centerVal: '$395k',
                centerSub: 'Total ARR',
                segments: [
                  { label: 'Enterprise', pct: 74, val: '$291.3k', color: '#60a5fa' },
                  { label: 'Growth', pct: 16, val: '$64.8k', color: '#4ade80' },
                  { label: 'At Risk', pct: 10, val: '$38.4k', color: '#fbbf24' },
                ],
              })}
            </section>

            <section class="glass-tile">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('cal', 'mint', 'sm')}<h2>28-Day Account Activity</h2></div>
                <span class="mini-tag">Daily Pulse</span>
              </div>
              ${heatmapGridHtml(cusCells)}
            </section>

            <section class="glass-tile hv-tile-grow">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('bolt', 'amber', 'sm')}<h2>Renewal Window Stack</h2></div>
                <span class="tile-sub">Q4 Coverage</span>
              </div>
              <div class="hv-channel-stack">
                <div class="hv-channel-seg" style="width:66%;background:#4ade80;"></div>
                <div class="hv-channel-seg" style="width:24%;background:#60a5fa;"></div>
                <div class="hv-channel-seg" style="width:10%;background:#fbbf24;"></div>
              </div>
              <div class="hv-chart-foot"><span>Signed 66%</span><span>Review 24%</span><span>Save 10%</span></div>
              <div class="hv-note-item"><span>Next Renewal: Northwind + Kestrel</span><strong>$291k</strong></div>
            </section>
          </div>
        </div>
      </div>
    `;
  }

  function renderModulesHtml() {
    const filtered = state.modules.filter((m) => state.moduleFilter === 'all' || m.category === state.moduleFilter);
    const connCnt = state.modules.filter((m) => m.status).length;
    const pausedCnt = state.modules.length - connCnt;

    return `
      <div class="hv-page-fill">
        ${renderSubHeader('Connected Workspace Modules', `${connCnt} of ${state.modules.length} external telemetry bridges connected`, `
          <div class="seg-group">
            ${['all', 'Billing', 'Comms', 'CRM', 'Dev'].map((c) => `<button type="button" data-mflt="${c}" aria-pressed="${state.moduleFilter === c}">${c === 'all' ? 'All' : c}</button>`).join('')}
          </div>
        `)}
        <section class="hv-grid-4">
          ${renderKpiIconCard({ icon: 'webhook', tone: 'blue', label: 'Connected Bridges', val: `${connCnt} / ${state.modules.length}`, sub: 'Bi-directional', chartHtml: miniBarsHtml([48, 60, 72, 84, 88, 92], 'blue') })}
          ${renderKpiIconCard({ icon: 'activity', tone: 'mint', label: 'Webhook Throughput', val: '1.84M', sub: '24h events', chartHtml: sparklineSvg([1.1, 1.3, 1.45, 1.52, 1.68, 1.79, 1.84], 'app-1', '#4ade80') })}
          ${renderKpiIconCard({ icon: 'bolt', tone: 'amber', label: 'Median Bridge Ping', val: '21ms', sub: 'Sub-50ms SLA', chartHtml: miniBarsHtml([28, 25, 24, 23, 22, 21], 'amber') })}
          ${renderKpiIconCard({ icon: 'shield', tone: 'violet', label: 'Delivery SLA', val: '99.98%', sub: 'Zero dead-letters', chartHtml: sparklineSvg([99.4, 99.6, 99.7, 99.8, 99.9, 99.95, 99.98], 'app-2', '#a78bfa') })}
        </section>

        <div class="hv-bento-2-1">
          <div class="hv-col-fill">
            <section class="hv-grid-3">
              ${filtered.map((m) => `
                <article class="glass-tile" style="display:flex;flex-direction:column;gap:8px;padding:13px 15px;">
                  <div class="tile-head">
                    <div class="hv-head-title">${iconOrb(m.category === 'Billing' ? 'creditCard' : (m.category === 'Comms' ? 'bell' : (m.category === 'Dev' ? 'cpu' : 'globe')), m.status ? 'mint' : 'amber', 'sm')}<span class="app-tag">${esc(m.category)}</span></div>
                    <button type="button" class="hv-switch" data-mtog="${esc(m.id)}" role="switch" aria-checked="${m.status}" aria-label="Toggle ${esc(m.name)}"><i></i></button>
                  </div>
                  <h2 style="font-size:14px;">${esc(m.name)}</h2>
                  <p class="tile-sub" style="line-height:1.35;">${esc(m.desc)}</p>
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-top:auto;padding-top:4px;">
                    <span class="hv-status-pill ${m.status ? 'connected' : ''}">${m.status ? 'Connected' : 'Paused'}</span>
                    <span class="tile-sub">${esc(m.latency)}</span>
                  </div>
                </article>
              `).join('')}
            </section>

            <section class="glass-tile hv-tile-grow">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('trendUp', 'mint', 'sm')}<h2>API Event Stream Throughput & Delivery Rate (k/hr)</h2></div>
                <span class="delta-mint">Peak 312k/hr</span>
              </div>
              ${areaLineChartSvg({ uid: 'app-stream', labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', 'Now'], primary: [145, 130, 198, 265, 288, 274, 312], secondary: [142, 128, 194, 260, 284, 270, 309], width: 680, height: 152 })}
            </section>
          </div>

          <div class="hv-col-fill">
            <section class="glass-tile">
              <div class="tile-head" style="margin-bottom:4px;">
                <div class="hv-head-title">${iconOrb('chart', 'blue', 'sm')}<h2>Bridge P95 Latency (ms)</h2></div>
                <span class="tile-sub">Lower better</span>
              </div>
              ${groupedBarChartSvg({ uid: 'app-lat', labels: ['Strp', 'Slck', 'Lnr', 'Rsnd', 'Hub', 'Ntn'], seriesA: [24, 16, 29, 19, 44, 31], highlightIdx: 4, unit: 'ms', height: 126 })}
            </section>

            <section class="glass-tile">
              <div class="tile-head" style="margin-bottom:8px;">
                <div class="hv-head-title">${iconOrb('sliders', 'violet', 'sm')}<h2>Bridge Health Mix</h2></div>
                <span class="tile-sub">${state.modules.length} plugins</span>
              </div>
              ${donutRingSvg({
                centerVal: `${Math.round((connCnt / Math.max(1, state.modules.length)) * 100)}%`,
                centerSub: 'Online',
                segments: [
                  { label: 'Connected', pct: Math.max(20, Math.round((connCnt / state.modules.length) * 100)), val: `${connCnt} live`, color: '#4ade80' },
                  { label: 'Paused', pct: Math.max(10, Math.round((pausedCnt / state.modules.length) * 100)), val: `${pausedCnt} idle`, color: '#fbbf24' },
                ],
              })}
            </section>

            <section class="glass-tile hv-tile-grow">
              <div class="tile-head" style="margin-bottom:6px;">
                <div class="hv-head-title">${iconOrb('shield', 'blue', 'sm')}<h2>Edge Guardrails</h2></div>
                <span class="mini-tag">Active</span>
              </div>
              <div class="hv-switch-row">
                <div class="hv-switch-info">${iconOrb('bolt', 'blue', 'sm')}<div><strong style="font-size:12px;">Burst Rate Limiter</strong><span class="tile-sub" style="display:block;">Cap 5k req/s per tenant</span></div></div>
                <button type="button" class="hv-switch" id="hvRateGuardSwitch" role="switch" aria-checked="${state.rateLimitGuard}" aria-label="Burst Rate Limiter"><i></i></button>
              </div>
              <div class="hv-switch-row">
                <div class="hv-switch-info">${iconOrb('webhook', 'mint', 'sm')}<div><strong style="font-size:12px;">Auto-Retry Dead-Letters</strong><span class="tile-sub" style="display:block;">Exponential backoff 3x</span></div></div>
                <button type="button" class="hv-switch" id="hvRetrySwitch" role="switch" aria-checked="${state.autoRetryWebhook}" aria-label="Auto-Retry Dead-Letters"><i></i></button>
              </div>
            </section>
          </div>
        </div>
      </div>
    `;
  }

  function renderMessagesHtml() {
    const cur = state.threads.find((t) => t.id === state.activeThreadId) || state.threads[0];
    const unreadLeft = state.threads.filter((t) => t.unread).length;
    const msgWave = [14, 22, 18, 30, 34, 24, 16, 28, 32, 22, 18, 29, 34, 26, 17, 24, 30, 20, 15, 22, 18, 12];

    return `
      <div class="hv-page-fill">
        ${renderSubHeader('Messages & Call Review Inbox', `${unreadLeft} unread executive threads · Real-time audio snippet & response telemetry`)}
        <section class="hv-grid-4">
          ${renderKpiIconCard({ icon: 'msg', tone: 'blue', label: 'Active Threads', val: `${state.threads.length}`, sub: `${unreadLeft} unread alerts`, chartHtml: miniBarsHtml([4, 6, 5, 8, 7, 9], 'blue') })}
          ${renderKpiIconCard({ icon: 'clock', tone: 'mint', label: 'Median First Reply', val: '11 min', sub: 'SLA Target < 20m', chartHtml: sparklineSvg([19, 17, 15, 14, 13, 12, 11], 'msg-1', '#4ade80') })}
          ${renderKpiIconCard({ icon: 'sparkles', tone: 'violet', label: 'Positive Sentiment', val: '84%', sub: 'Call & thread NLP', chartHtml: sparklineSvg([74, 76, 78, 80, 81, 83, 84], 'msg-2', '#a78bfa') })}
          ${renderKpiIconCard({ icon: 'mic', tone: 'amber', label: 'Call Audio Clips', val: '12 clips', sub: '48kHz spatial stream', chartHtml: miniBarsHtml([16, 24, 32, 22, 28, 36], 'amber') })}
        </section>

        <div class="hv-bento-3">
          <div class="hv-col-fill">
            <section class="glass-tile hv-tile-grow">
              <div class="tile-head" style="margin-bottom:8px;">
                <div class="hv-head-title">${iconOrb('mail', 'blue', 'sm')}<h2>Conversations</h2></div>
                <span class="tile-sub">${state.threads.length} open</span>
              </div>
              <div class="hv-list-stack">
                ${state.threads.map((t) => `
                  <button type="button" class="hv-list-row" data-tid="${esc(t.id)}" aria-selected="${cur && cur.id === t.id}">
                    <div style="display:flex;align-items:center;gap:9px;min-width:0;flex:1;">
                      ${iconOrb(t.unread ? 'bell' : 'msg', t.unread ? 'blue' : 'mint', 'sm')}
                      <div class="hv-row-main">
                        <strong>${esc(t.sender)}</strong>
                        <span>${esc(t.role)} · ${esc(t.time)}</span>
                      </div>
                    </div>
                    ${t.unread ? '<span class="hv-status-pill processing">NEW</span>' : '<span class="tile-sub">Read</span>'}
                  </button>
                `).join('')}
              </div>
            </section>

            <section class="glass-tile">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('chart', 'mint', 'sm')}<h2>Inbound vs Resolved</h2></div>
                <span class="tile-sub">Mon–Fri</span>
              </div>
              ${groupedBarChartSvg({ uid: 'msg-vol', labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], seriesA: [28, 34, 31, 42, 37], seriesB: [25, 32, 29, 40, 36], height: 122 })}
            </section>
          </div>

          <div class="hv-col-fill">
            ${cur ? `
              <section class="glass-tile hv-tile-grow hv-chat-shell">
                <div class="tile-head">
                  <div class="hv-head-title">${iconOrb('users', 'violet', 'sm')}<div><h2>${esc(cur.sender)}</h2><p class="tile-sub">${esc(cur.role)}</p></div></div>
                  <button type="button" class="pill-btn" id="hvJumpCallAudioBtn">${svgIcon('play', 12)} Discovery Audio</button>
                </div>
                <div class="hv-chat-feed" id="hvChatFeed" style="flex:1 1 auto;max-height:280px;">
                  ${cur.items.map((msg) => `<div class="hv-bubble ${msg.from === 'self' ? 'self' : ''}">${esc(msg.text)}<small>${esc(msg.ts)}</small></div>`).join('')}
                </div>
                <div class="hv-top-actions">
                  ${['Approved 15% term', 'Sending Q4 deck now', 'Rescheduled Thu 10:00'].map((qr) => `<button type="button" class="pill-btn" data-qreply="${esc(qr)}">${esc(qr)}</button>`).join('')}
                </div>
                <form id="hvMsgForm" class="hv-chat-compose">
                  <input id="hvMsgInput" type="text" required placeholder="Reply to ${esc(cur.sender)}...">
                  <button type="submit" class="pill-btn" style="background:var(--hv-blue);">${svgIcon('send', 12)} Send</button>
                </form>
              </section>
            ` : ''}
          </div>

          <div class="hv-col-fill">
            <section class="glass-tile">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('phone', 'blue', 'sm')}<h2>Snippet Waveform</h2></div>
                <button type="button" class="pill-btn" id="hvMsgVoicePlay">${svgIcon(state.msgVoicePlaying ? 'pause' : 'play', 11)} ${state.msgVoicePlaying ? 'Pause' : 'Listen'}</button>
              </div>
              <div class="waveform" style="height:36px;margin-top:8px;">
                ${msgWave.map((h, i) => `<span class="wave-bar ${i <= state.msgPlayPos ? 'played' : ''}" data-mwidx="${i}" style="height:${h}px"></span>`).join('')}
              </div>
              <div class="hv-chart-foot"><span>26:48 positive peak</span><strong>01:42 / 03:32</strong></div>
            </section>

            <section class="glass-tile">
              <div class="tile-head" style="margin-bottom:6px;">
                <div class="hv-head-title">${iconOrb('sparkles', 'mint', 'sm')}<h2>Sentiment Distribution</h2></div>
                <span class="mini-tag">NLP v3</span>
              </div>
              ${donutRingSvg({
                centerVal: '84%',
                centerSub: 'Positive',
                segments: [
                  { label: 'Positive', pct: 68, val: '68%', color: '#4ade80' },
                  { label: 'Neutral', pct: 24, val: '24%', color: '#60a5fa' },
                  { label: 'Escalate', pct: 8, val: '8%', color: '#fbbf24' },
                ],
              })}
            </section>

            <section class="glass-tile hv-tile-grow">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('trendUp', 'amber', 'sm')}<h2>Response SLA Trend (min)</h2></div>
                <span class="delta-mint">-38% faster</span>
              </div>
              ${areaLineChartSvg({ uid: 'msg-sla', labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], primary: [18, 16, 15, 13, 12, 11], primaryColor: '#a78bfa', height: 112 })}
            </section>
          </div>
        </div>
      </div>
    `;
  }

  function renderCalendarHtml() {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
    const filtered = state.events.filter((e) => state.calFilter === 'all' || e.type === state.calFilter);
    const calMeet = days.map((d) => filtered.filter((ev) => ev.day === d).length * 2 + 1);
    const calFocus = days.map((d) => Math.max(2, 8 - filtered.filter((ev) => ev.day === d).length * 2));
    const calCells = [
      { label: 'M1', level: 4 }, { label: 'T1', level: 3 }, { label: 'W1', level: 2 }, { label: 'T1', level: 4 }, { label: 'F1', level: 2 }, { label: 'S1', level: 0 }, { label: 'S1', level: 0 },
      { label: 'M2', level: 3 }, { label: 'T2', level: 4 }, { label: 'W2', level: 3 }, { label: 'T2', level: 2 }, { label: 'F2', level: 3 }, { label: 'S2', level: 1 }, { label: 'S2', level: 0 },
      { label: 'M3', level: 4 }, { label: 'T3', level: 3 }, { label: 'W3', level: 4 }, { label: 'T3', level: 3 }, { label: 'F3', level: 2 }, { label: 'S3', level: 0 }, { label: 'S3', level: 1 },
      { label: 'M4', level: 3 }, { label: 'T4', level: 2 }, { label: 'W4', level: 4 }, { label: 'T4', level: 4 }, { label: 'F4', level: 3 }, { label: 'S4', level: 0 }, { label: 'S4', level: 0 },
    ];
    const cntCalls = state.events.filter((e) => e.type === 'calls').length;
    const cntRev = state.events.filter((e) => e.type === 'reviews').length;
    const cntDemo = state.events.filter((e) => e.type === 'demos').length;
    const totEv = Math.max(1, state.events.length);

    return `
      <div class="hv-page-fill">
        ${renderSubHeader('Team Calendar & Capacity Load', 'Weekly customer calls, renewal reviews & deep-work load balance', `
          <div class="seg-group">
            ${[['all', 'All'], ['calls', 'Calls'], ['reviews', 'Reviews'], ['demos', 'Demos']].map(([k, l]) => `<button type="button" data-calflt="${k}" aria-pressed="${state.calFilter === k}">${l}</button>`).join('')}
          </div>
          <button type="button" class="pill-btn" id="hvNewEventBtn" style="background:var(--hv-blue);">${svgIcon('calendarPlus', 13)} New Block</button>
        `)}
        <section class="hv-grid-4">
          ${renderKpiIconCard({ icon: 'cal', tone: 'blue', label: 'Scheduled Blocks', val: `${filtered.length} blocks`, sub: 'This workweek', chartHtml: miniBarsHtml(calMeet, 'blue') })}
          ${renderKpiIconCard({ icon: 'shield', tone: 'mint', label: 'Focus Time Ratio', val: state.focusShield ? '68%' : '59%', sub: state.focusShield ? 'Shield enabled' : 'Standard cap', chartHtml: sparklineSvg([52, 55, 57, 58, 60, 62, state.focusShield ? 68 : 59], 'cal-1', '#4ade80') })}
          ${renderKpiIconCard({ icon: 'phone', tone: 'violet', label: 'Discovery & Triage', val: `${cntCalls} calls`, sub: 'High sentiment', chartHtml: miniBarsHtml([12, 18, 22, 19, 25, 28], 'violet') })}
          ${renderKpiIconCard({ icon: 'clock', tone: 'amber', label: 'On-Time Start Rate', val: '98.2%', sub: '+1.4% vs Oct', chartHtml: sparklineSvg([94, 95, 96, 96.5, 97, 97.8, 98.2], 'cal-2', '#fbbf24') })}
        </section>

        <div class="hv-bento-2-1">
          <div class="hv-col-fill">
            <section class="glass-tile">
              <div class="hv-cal-grid">
                ${days.map((day) => {
                  const list = filtered.filter((ev) => ev.day === day);
                  return `
                    <div class="hv-cal-col">
                      <h3>${esc(day)} · Nov</h3>
                      ${list.map((ev) => `
                        <div class="hv-cal-event ${esc(ev.type)}">
                          <span>${esc(ev.time)} · ${esc(ev.owner)}</span>
                          <strong>${esc(ev.title)}</strong>
                        </div>
                      `).join('') || '<span class="tile-sub">Open slot</span>'}
                    </div>
                  `;
                }).join('')}
              </div>
            </section>

            <section class="glass-tile hv-tile-grow">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('chart', 'blue', 'sm')}<h2>Meeting Hours vs Deep-Work Focus (hrs/day)</h2></div>
                <span class="tile-sub">Blue: Meetings · Mint: Focus</span>
              </div>
              ${groupedBarChartSvg({ uid: 'cal-load', labels: days, seriesA: calMeet, seriesB: calFocus, colorA: '#60a5fa', colorB: '#4ade80', width: 680, height: 156 })}
            </section>
          </div>

          <div class="hv-col-fill">
            <section class="glass-tile">
              <div class="tile-head" style="margin-bottom:8px;">
                <div class="hv-head-title">${iconOrb('compass', 'mint', 'sm')}<h2>Allocation Mix</h2></div>
                <span class="tile-sub">${state.events.length} events</span>
              </div>
              ${donutRingSvg({
                centerVal: `${state.events.length}`,
                centerSub: 'Sessions',
                segments: [
                  { label: 'Reviews', pct: Math.max(15, Math.round((cntRev / totEv) * 100)), val: `${cntRev} blks`, color: '#4ade80' },
                  { label: 'Calls', pct: Math.max(15, Math.round((cntCalls / totEv) * 100)), val: `${cntCalls} blks`, color: '#60a5fa' },
                  { label: 'Demos', pct: Math.max(12, Math.round((cntDemo / totEv) * 100)), val: `${cntDemo} blks`, color: '#fbbf24' },
                ],
              })}
            </section>

            <section class="glass-tile">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('layers', 'violet', 'sm')}<h2>Team Capacity Heat Matrix</h2></div>
                <span class="mini-tag">4 Weeks</span>
              </div>
              ${heatmapGridHtml(calCells)}
            </section>

            <section class="glass-tile hv-tile-grow">
              <div class="tile-head">
                <div class="hv-head-title">${iconOrb('shield', 'blue', 'sm')}<h2>Focus Guardrail</h2></div>
                <span class="tile-sub">${state.focusShield ? 'Locked 2h AM' : 'Flexible'}</span>
              </div>
              <div class="hv-switch-row" style="margin-top:4px;">
                <div class="hv-switch-info">${iconOrb('clock', 'mint', 'sm')}<div><strong style="font-size:12px;">Deep-Work Morning Shield</strong><span class="tile-sub" style="display:block;">Auto-hold 08:30–10:30 Wed/Fri</span></div></div>
                <button type="button" class="hv-switch" id="hvFocusShieldSwitch" role="switch" aria-checked="${state.focusShield}" aria-label="Deep-Work Morning Shield"><i></i></button>
              </div>
              <div class="hv-note-item"><span>Protected Focus Quota</span><strong>${state.focusShield ? '14 hrs/wk' : '9 hrs/wk'}</strong></div>
            </section>
          </div>
        </div>
      </div>
    `;
  }

  function renderAnalyticsHtml() {
    const a = ANALYTICS_SERIES[state.analyticsGrain];
    const grainSets = {
      Week: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        revArr: [18, 22, 21, 25, 29, 27, 34],
        retArr: [14, 16, 17, 19, 21, 22, 25],
        regA: [64, 48, 36, 18],
        regB: [42, 34, 24, 12],
        radar: [88, 84, 91, 82, 86, 89],
      },
      Month: {
        labels: ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7'],
        revArr: [120, 145, 162, 178, 196, 214, 238],
        retArr: [96, 112, 128, 138, 152, 168, 184],
        regA: [248, 182, 134, 68],
        regB: [176, 129, 98, 49],
        radar: [92, 87, 94, 85, 90, 91],
      },
      Quarter: {
        labels: ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov', 'Dec'],
        revArr: [310, 395, 365, 480, 540, 625, 720],
        retArr: [260, 310, 330, 395, 455, 510, 595],
        regA: [780, 560, 410, 210],
        regB: [540, 395, 298, 154],
        radar: [95, 90, 96, 88, 93, 94],
      },
    }[state.analyticsGrain];

    const cohortCells = [
      { label: '99%', level: 4 }, { label: '96%', level: 4 }, { label: '93%', level: 3 }, { label: '91%', level: 3 }, { label: '89%', level: 3 }, { label: '88%', level: 3 }, { label: '87%', level: 3 },
      { label: '98%', level: 4 }, { label: '94%', level: 4 }, { label: '90%', level: 3 }, { label: '88%', level: 3 }, { label: '86%', level: 2 }, { label: '85%', level: 2 }, { label: '—', level: 0 },
      { label: '97%', level: 4 }, { label: '93%', level: 3 }, { label: '91%', level: 3 }, { label: '89%', level: 3 }, { label: '87%', level: 2 }, { label: '—', level: 0 }, { label: '—', level: 0 },
      { label: '99%', level: 4 }, { label: '96%', level: 4 }, { label: '94%', level: 4 }, { label: '92%', level: 3 }, { label: '—', level: 0 }, { label: '—', level: 0 }, { label: '—', level: 0 },
    ];

    return `
      <div class="hv-page-fill">
        ${renderSubHeader('Deep Revenue & Retention Analytics', 'Cohort retention heat matrix, regional pipeline & attribution telemetry', `
          <div class="seg-group">
            ${['Week', 'Month', 'Quarter'].map((g) => `<button type="button" data-agrain="${g}" aria-pressed="${state.analyticsGrain === g}">${g}</button>`).join('')}
          </div>
          <button type="button" class="pill-btn" id="hvCsvBtn">${svgIcon('download', 13)} Analytics CSV</button>
        `)}
        <section class="hv-grid-4">
          ${renderKpiIconCard({ icon: 'trendUp', tone: 'blue', label: 'Recognized Revenue', val: a.rev, sub: `+18.4% ${state.analyticsGrain}`, chartHtml: sparklineSvg(grainSets.revArr, 'ana-1', '#60a5fa') })}
          ${renderKpiIconCard({ icon: 'shield', tone: 'mint', label: 'Net Dollar Retention', val: a.nrr, sub: 'Cohort NRR', chartHtml: miniBarsHtml([76, 82, 86, 90, 94, 98], 'mint') })}
          ${renderKpiIconCard({ icon: 'clock', tone: 'amber', label: 'CAC Payback', val: a.cac, sub: 'Target < 5.0 mo', chartHtml: sparklineSvg([5.2, 4.9, 4.7, 4.4, 4.2, 4.0, 3.8], 'ana-2', '#fbbf24') })}
          ${renderKpiIconCard({ icon: 'sparkles', tone: 'violet', label: 'Qualified Win Rate', val: a.winRate, sub: '+3.1% lift', chartHtml: miniBarsHtml([54, 62, 68, 72, 78, 86], 'violet') })}
        </section>

        <div class="hv-bento-2-eq">
          <section class="glass-tile">
            <div class="tile-head">
              <div class="hv-head-title">${iconOrb('activity', 'blue', 'sm')}<h2>Revenue vs. Net Retention Trajectory</h2></div>
              <span class="mini-tag">${esc(state.analyticsGrain)}</span>
            </div>
            ${areaLineChartSvg({ uid: 'ana-main', labels: grainSets.labels, primary: grainSets.revArr, secondary: grainSets.retArr, width: 560, height: 150 })}
          </section>

          <section class="glass-tile">
            <div class="tile-head">
              <div class="hv-head-title">${iconOrb('globe', 'mint', 'sm')}<h2>Regional Pipeline vs Closed (k$)</h2></div>
              <span class="tile-sub">Blue: Pipe · Mint: Won</span>
            </div>
            ${groupedBarChartSvg({ uid: 'ana-reg', labels: ['NA', 'EMEA', 'APAC', 'LATAM'], seriesA: grainSets.regA, seriesB: grainSets.regB, width: 560, height: 150 })}
          </section>
        </div>

        <div class="hv-bento-3">
          <section class="glass-tile">
            <div class="tile-head" style="margin-bottom:8px;">
              <div class="hv-head-title">${iconOrb('compass', 'blue', 'sm')}<h2>Attribution Mix</h2></div>
              <span class="tile-sub">4 Channels</span>
            </div>
            ${donutRingSvg({
              centerVal: a.winRate,
              centerSub: 'Win Rate',
              segments: [
                { label: 'Product-Led', pct: 42, val: '42%', color: '#60a5fa' },
                { label: 'Outbound', pct: 28, val: '28%', color: '#4ade80' },
                { label: 'Organic', pct: 19, val: '19%', color: '#a78bfa' },
                { label: 'Partners', pct: 11, val: '11%', color: '#fbbf24' },
              ],
            })}
          </section>

          <section class="glass-tile">
            <div class="tile-head">
              <div class="hv-head-title">${iconOrb('filter', 'mint', 'sm')}<h2>Conversion & Retention Cohort</h2></div>
              <span class="mini-tag">6W Matrix</span>
            </div>
            ${funnelChartHtml(a.funnel.slice(0, 3).map(([st, pct, vol], idx) => [st, pct, vol, idx === 0 ? 'linear-gradient(90deg,#60a5fa,#3b82f6)' : (idx === 1 ? 'linear-gradient(90deg,#4ade80,#10b981)' : 'linear-gradient(90deg,#a78bfa,#7c3aed)')]))}
            ${heatmapGridHtml(cohortCells.slice(0, 14))}
          </section>

          <section class="glass-tile">
            <div class="tile-head">
              <div class="hv-head-title">${iconOrb('chart', 'violet', 'sm')}<h2>Growth Engine 6D Radar</h2></div>
              <span class="mini-tag">${esc(state.analyticsGrain)}</span>
            </div>
            ${radarChartSvg({
              uid: 'ana-rad',
              color: '#a78bfa',
              axes: [
                { label: 'NRR', score: grainSets.radar[0] },
                { label: 'Win', score: grainSets.radar[1] },
                { label: 'Magic No', score: grainSets.radar[2] },
                { label: 'Payback', score: grainSets.radar[3] },
                { label: 'Pipe', score: grainSets.radar[4] },
                { label: 'Velocity', score: grainSets.radar[5] },
              ],
            })}
          </section>
        </div>
      </div>
    `;
  }

  function bindOverviewEvents() {
    viewport.querySelectorAll('[data-domain]').forEach((b) => b.addEventListener('click', () => navigate(b.dataset.domain)));
    $('#hvCsvBtn')?.addEventListener('click', exportCsv);
    $('#hvAddBtn')?.addEventListener('click', (e) => openQuickDialog(e.currentTarget, 'quick'));
    $('#hvTeamAdd')?.addEventListener('click', (e) => openQuickDialog(e.currentTarget, 'quick'));
    $('#hvForecastSwitch')?.addEventListener('click', () => { state.showForecast = !state.showForecast; renderMain(); });
    $('#hvDialDec')?.addEventListener('click', () => { state.targetPct = Math.max(10, state.targetPct - 4); renderMain(); });
    $('#hvDialInc')?.addEventListener('click', () => { state.targetPct = Math.min(100, state.targetPct + 4); renderMain(); });
    viewport.querySelectorAll('[data-metric]').forEach((b) => b.addEventListener('click', () => { state.activeMetric = b.dataset.metric; renderMain(); }));
    viewport.querySelectorAll('[data-revp]').forEach((b) => b.addEventListener('click', () => { state.revPeriod = b.dataset.revp; renderMain(); }));
    viewport.querySelectorAll('[data-salep]').forEach((b) => b.addEventListener('click', () => { state.salesPeriod = b.dataset.salep; renderMain(); }));
    $('#hvApproveBtn')?.addEventListener('click', () => { state.approvalIdx += 1; renderMain(); toast('Approval signed'); });
    $('#hvRejectBtn')?.addEventListener('click', () => { state.approvalIdx += 1; renderMain(); toast('Moved to next item'); });
    viewport.querySelectorAll('[data-kpisw]').forEach((b) => b.addEventListener('click', () => {
      const k = b.dataset.kpisw;
      state.kpiSwitches[k] = !state.kpiSwitches[k];
      renderMain();
    }));
    $('#hvSpeedBtn')?.addEventListener('click', () => {
      state.speed = state.speed === 1 ? 1.5 : (state.speed === 1.5 ? 2 : 1);
      renderMain();
    });
    $('#hvBack10')?.addEventListener('click', () => { state.playPos = Math.max(0, state.playPos - 5); renderMain(); });
    $('#hvFwd10')?.addEventListener('click', () => { state.playPos = Math.min(WAVE_HEIGHTS.length - 1, state.playPos + 5); renderMain(); });
    $('#hvPlayBtn')?.addEventListener('click', () => {
      state.playing = !state.playing;
      clearInterval(playTimer);
      if (state.playing) {
        playTimer = setInterval(() => {
          state.playPos = (state.playPos + 1) % WAVE_HEIGHTS.length;
          renderMain();
        }, Math.round(450 / state.speed));
      }
      renderMain();
    });
    viewport.querySelectorAll('[data-widx]').forEach((bar) => bar.addEventListener('click', () => {
      state.playPos = Number(bar.dataset.widx);
      renderMain();
    }));
  }

  function bindSubpageEvents() {
    $('#hvBackHomeBtn')?.addEventListener('click', () => navigateRoute('overview'));
    $('#hvCsvBtn')?.addEventListener('click', exportCsv);

    if (state.activeRoute === 'search') {
      const inp = $('#hvGlobalSearchInput');
      if (inp) {
        inp.addEventListener('input', () => {
          state.searchQuery = inp.value;
          const pos = inp.selectionStart;
          renderMain();
          const freshInp = $('#hvGlobalSearchInput');
          if (freshInp) { freshInp.focus(); if (pos !== null) freshInp.setSelectionRange(pos, pos); }
        });
      }
      viewport.querySelectorAll('[data-sflt]').forEach((b) => b.addEventListener('click', () => { state.searchFilter = b.dataset.sflt; renderMain(); }));
      viewport.querySelectorAll('[data-sq]').forEach((b) => b.addEventListener('click', () => { state.searchQuery = b.dataset.sq; renderMain(); }));
      viewport.querySelectorAll('[data-jump-route]').forEach((b) => b.addEventListener('click', () => {
        const rt = b.dataset.jumpRoute;
        const jid = b.dataset.jumpId;
        if (rt === 'orders') state.selectedOrderId = jid;
        else if (rt === 'customers') state.selectedCustomerId = jid;
        else if (rt === 'messages') state.activeThreadId = jid;
        navigateRoute(rt);
      }));
    } else if (state.activeRoute === 'orders') {
      viewport.querySelectorAll('[data-oflt]').forEach((b) => b.addEventListener('click', () => { state.orderFilter = b.dataset.oflt; renderMain(); }));
      viewport.querySelectorAll('.hv-list-row[data-oid]').forEach((b) => b.addEventListener('click', () => { state.selectedOrderId = b.dataset.oid; renderMain(); }));
      $('#hvNewOrderBtn')?.addEventListener('click', (e) => openQuickDialog(e.currentTarget, 'order'));
      $('#hvAutoInvoiceSwitch')?.addEventListener('click', () => { state.autoInvoice = !state.autoInvoice; renderMain(); toast(`Auto-invoice ${state.autoInvoice ? 'enabled' : 'paused'}`); });
      $('#hvMarkPaidBtn')?.addEventListener('click', (e) => {
        const ord = state.orders.find((o) => o.id === e.currentTarget.dataset.oid);
        if (ord) { ord.status = 'Paid'; renderMain(); toast(`${ord.id} marked Paid`); }
      });
      $('#hvRefundOrderBtn')?.addEventListener('click', (e) => {
        const ord = state.orders.find((o) => o.id === e.currentTarget.dataset.oid);
        if (ord) { ord.status = 'Refunded'; renderMain(); toast(`${ord.id} refunded`); }
      });
    } else if (state.activeRoute === 'products') {
      viewport.querySelectorAll('[data-pflt]').forEach((b) => b.addEventListener('click', () => { state.productFilter = b.dataset.pflt; renderMain(); }));
      viewport.querySelectorAll('[data-ptog]').forEach((b) => b.addEventListener('click', () => {
        const prd = state.products.find((p) => p.id === b.dataset.ptog);
        if (prd) { prd.active = !prd.active; renderMain(); toast(`${prd.name} ${prd.active ? 'enabled' : 'disabled'}`); }
      }));
    } else if (state.activeRoute === 'customers') {
      viewport.querySelectorAll('[data-cflt]').forEach((b) => b.addEventListener('click', () => { state.customerFilter = b.dataset.cflt; renderMain(); }));
      viewport.querySelectorAll('.hv-list-row[data-cid]').forEach((b) => b.addEventListener('click', () => { state.selectedCustomerId = b.dataset.cid; renderMain(); }));
      $('#hvRenewGuardSwitch')?.addEventListener('click', () => { state.autoRenewGuard = !state.autoRenewGuard; renderMain(); toast(`Renewal guardrail ${state.autoRenewGuard ? 'armed' : 'paused'}`); });
      $('#hvCustNoteForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        const cid = e.currentTarget.dataset.cid;
        const txt = ($('#hvCustNoteInput')?.value || '').trim();
        const cus = state.customers.find((c) => c.id === cid);
        if (cus && txt) {
          cus.notes.unshift({ ts: 'Just now', text: txt });
          renderMain();
          toast('Follow-up note saved');
        }
      });
    } else if (state.activeRoute === 'apps') {
      viewport.querySelectorAll('[data-mflt]').forEach((b) => b.addEventListener('click', () => { state.moduleFilter = b.dataset.mflt; renderMain(); }));
      viewport.querySelectorAll('[data-mtog]').forEach((b) => b.addEventListener('click', () => {
        const mod = state.modules.find((m) => m.id === b.dataset.mtog);
        if (mod) { mod.status = !mod.status; renderMain(); toast(`${mod.name} ${mod.status ? 'connected' : 'paused'}`); }
      }));
      $('#hvRateGuardSwitch')?.addEventListener('click', () => { state.rateLimitGuard = !state.rateLimitGuard; renderMain(); toast(`Burst limiter ${state.rateLimitGuard ? 'enabled' : 'disabled'}`); });
      $('#hvRetrySwitch')?.addEventListener('click', () => { state.autoRetryWebhook = !state.autoRetryWebhook; renderMain(); toast(`Webhook retry ${state.autoRetryWebhook ? 'enabled' : 'disabled'}`); });
    } else if (state.activeRoute === 'messages') {
      viewport.querySelectorAll('.hv-list-row[data-tid]').forEach((b) => b.addEventListener('click', () => {
        state.activeThreadId = b.dataset.tid;
        const thr = state.threads.find((t) => t.id === b.dataset.tid);
        if (thr) thr.unread = false;
        renderRail();
        renderMain();
      }));
      viewport.querySelectorAll('[data-qreply]').forEach((b) => b.addEventListener('click', () => {
        const inp = $('#hvMsgInput');
        if (inp) { inp.value = b.dataset.qreply; inp.focus(); }
      }));
      $('#hvMsgVoicePlay')?.addEventListener('click', () => {
        state.msgVoicePlaying = !state.msgVoicePlaying;
        state.msgPlayPos = (state.msgPlayPos + 2) % 22;
        renderMain();
      });
      viewport.querySelectorAll('[data-mwidx]').forEach((bar) => bar.addEventListener('click', () => {
        state.msgPlayPos = Number(bar.dataset.mwidx);
        renderMain();
      }));
      $('#hvJumpCallAudioBtn')?.addEventListener('click', () => { state.playing = true; navigateRoute('overview'); toast('Playing Discovery Call snippet'); });
      $('#hvMsgForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        const txt = ($('#hvMsgInput')?.value || '').trim();
        const thr = state.threads.find((t) => t.id === state.activeThreadId);
        if (thr && txt) {
          thr.items.push({ from: 'self', text: txt, ts: 'Now' });
          thr.unread = false;
          renderRail();
          renderMain();
          toast('Message sent');
        }
      });
    } else if (state.activeRoute === 'calendar') {
      viewport.querySelectorAll('[data-calflt]').forEach((b) => b.addEventListener('click', () => { state.calFilter = b.dataset.calflt; renderMain(); }));
      $('#hvNewEventBtn')?.addEventListener('click', (e) => openQuickDialog(e.currentTarget, 'event'));
      $('#hvFocusShieldSwitch')?.addEventListener('click', () => { state.focusShield = !state.focusShield; renderMain(); toast(`Focus shield ${state.focusShield ? 'locked' : 'unlocked'}`); });
    } else if (state.activeRoute === 'analytics') {
      viewport.querySelectorAll('[data-agrain]').forEach((b) => b.addEventListener('click', () => { state.analyticsGrain = b.dataset.agrain; renderMain(); }));
    }
  }

  function renderMain() {
    viewport.dataset.page = state.activeRoute === 'overview' ? state.activeDomain.toLowerCase() : state.activeRoute;
    if (state.activeRoute === 'overview') {
      viewport.innerHTML = renderOverviewHtml();
      bindOverviewEvents();
      return;
    }
    const views = {
      search: renderSearchHtml,
      orders: renderOrdersHtml,
      products: renderProductsHtml,
      customers: renderCustomersHtml,
      apps: renderModulesHtml,
      messages: renderMessagesHtml,
      calendar: renderCalendarHtml,
      analytics: renderAnalyticsHtml,
    };
    const fn = views[state.activeRoute] || renderOverviewHtml;
    viewport.innerHTML = fn();
    bindSubpageEvents();
  }

  function navigateRoute(route) {
    const prevKey = `${state.activeRoute}:${state.activeDomain}`;
    state.scrollByRoute[prevKey] = viewport.scrollTop;
    state.activeRoute = route || 'overview';
    if (state.activeRoute === 'messages') {
      const cur = state.threads.find((t) => t.id === state.activeThreadId);
      if (cur) cur.unread = false;
    }
    renderRail();
    renderMain();
    viewport.scrollTop = state.scrollByRoute[`${state.activeRoute}:${state.activeDomain}`] || 0;
  }

  function navigate(domain) {
    state.scrollByRoute[`${state.activeRoute}:${state.activeDomain}`] = viewport.scrollTop;
    state.activeRoute = 'overview';
    state.activeDomain = domain || 'Overview';
    renderRail();
    renderMain();
    viewport.scrollTop = state.scrollByRoute[`overview:${state.activeDomain}`] || 0;
  }

  function clearHighlight() {
    document.querySelectorAll('[data-kaiwu-active]').forEach((el) => el.removeAttribute('data-kaiwu-active'));
  }

  function highlightEu(rawId, fallbackId, action) {
    clearHighlight();
    if (!rawId) return;
    if (rawId === 'eu_L3_hv_quick_dialog' || rawId === 'eu_L4_hv_focus_trap') {
      if (!dialog.open) openQuickDialog($('#hvAddBtn') || $('.rail-btn', railEl), 'quick');
      dialog.setAttribute('data-kaiwu-active', 'true');
      return;
    }
    if (dialog.open) dialog.close();
    if (rawId === 'eu_L3_hv_rail_dock' || rawId === 'eu_L4_hv_rail_proximity' || action === 'proximity_demo') {
      requestAnimationFrame(() => {
        const homeBtn = $('.rail-btn[data-rail="overview"]', railEl);
        if (homeBtn) {
          const r = homeBtn.getBoundingClientRect();
          dockPointer = { x: (r.left + r.right) / 2, y: (r.top + r.bottom) / 2 };
          updateDock();
        }
      });
    } else {
      dockPointer = null;
      updateDock();
    }
    let target = $(`[data-eu-id="${rawId}"]`);
    if (!target && state.activeRoute !== 'overview') {
      state.activeRoute = 'overview';
      renderRail();
      renderMain();
      target = $(`[data-eu-id="${rawId}"]`);
    }
    target = target || (fallbackId && $(`[data-eu-id="${fallbackId}"]`)) || shell;
    if (viewport.contains(target) && rawId !== 'eu_L1_hv_stage') {
      target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    target.setAttribute('data-kaiwu-active', 'true');
  }

  window.addEventListener('message', (ev) => {
    const msg = ev.data;
    if (!msg || typeof msg !== 'object') return;
    if (msg.type === 'KAIWU_HIGHLIGHT_EU') {
      highlightEu(msg.eu_id, msg.fallback_eu_id, msg.action);
    } else if (msg.type === 'KAIWU_PREVIEW_ACTION') {
      if (dialog.open) dialog.close();
      if (msg.action === 'proximity_demo') {
        requestAnimationFrame(() => {
          const homeBtn = $('.rail-btn[data-rail="overview"]', railEl);
          if (homeBtn) {
            const r = homeBtn.getBoundingClientRect();
            dockPointer = { x: (r.left + r.right) / 2, y: (r.top + r.bottom) / 2 };
            updateDock();
          }
        });
      } else if (msg.action === 'analytics') {
        dockPointer = null;
        navigateRoute('analytics');
      } else {
        dockPointer = null;
        navigate('Overview');
      }
    }
  });

  document.addEventListener('click', (ev) => {
    if (window.parent === window) return;
    const hit = ev.target.closest('[data-eu-id]');
    if (!hit) return;
    window.parent.postMessage({ type: 'KAIWU_SELECT_EU', eu_id: hit.getAttribute('data-eu-id'), case_id: 'haven_admin_web' }, '*');
  }, true);

  renderRail();
  renderMain();
})();
