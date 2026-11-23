(() => {
  'use strict';
  const $ = (s, root = document) => root.querySelector(s);
  const asset = (name) => window.__codeXrAssets?.[name] ?? name;
  const escape = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const usd = new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0});
  const path = {
    home:'<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z" fill="currentColor" stroke="none"/>',
    pie:'<path d="M11 2a10 10 0 1 0 11 11H11z" fill="currentColor" stroke="none"/><path d="M14 2v8h8a10 10 0 0 0-8-8" fill="currentColor" stroke="none"/>',
    users:'<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m20 0v-2a4 4 0 0 0-3-4m-4-11a4 4 0 0 1 0 8"/><circle cx="9" cy="8" r="4"/>',
    calendar:'<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M16 3v4M8 3v4M3 10h18m-14 4h2m3 0h2m3 0h1m-11 3h2m3 0h2"/>',
    video:'<rect x="2" y="5" width="14" height="14" rx="3"/><path d="m16 10 5-3v10l-5-3z" fill="currentColor" stroke="none"/>',
    message:'<path d="M21 11.5a8 8 0 0 1-8.5 8H4l1.8-4A8 8 0 0 1 4 11.5a8.5 8.5 0 1 1 17 0Z" fill="currentColor" stroke="none"/>',
    bolt:'<path d="M13 2 3 14h8l-1 8 11-13h-8z" fill="currentColor" stroke="none"/>',
    settings:'<path d="m10 2-1 3-3 1-3 1v4l2 2v2l-1 3 3 3 3-2 3 1 2 2 4-2v-3l2-2 1-3-2-3-3 1-2-2V3z"/><circle cx="12" cy="12" r="3"/>',
    bell:'<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9Zm-8 12a2 2 0 0 0 4 0"/>',
    clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    plus:'<path d="M12 5v14M5 12h14"/>',
    arrow:'<path d="M6 18 18 6m-9 0h9v9"/>',
    left:'<path d="m14 6-6 6 6 6"/>',
    right:'<path d="m10 6 6 6-6 6"/>',
    bag:'<rect x="4" y="7" width="16" height="13" rx="3"/><path d="M9 7V5h6v2M4 12h16"/>',
    coin:'<circle cx="12" cy="12" r="8"/><path d="M12 7v10m-2-7h3a1.5 1.5 0 0 1 0 3h-2a1.5 1.5 0 0 0 0 3h3"/>',
    server:'<rect x="5" y="4" width="14" height="6" rx="2"/><rect x="5" y="14" width="14" height="6" rx="2"/><path d="M8 7h2m-2 10h2"/>',
    pin:'<path d="M18 9c0 4-6 10-6 10S6 13 6 9a6 6 0 0 1 12 0Z"/><circle cx="12" cy="9" r="1.8"/>',
    clipboard:'<rect x="5" y="5" width="14" height="16" rx="3"/><path d="M9 5V3h6v2m-6 5h6m-6 5h6"/>',
    download:'<path d="M12 3v12m-5-5 5 5 5-5m-13 6v4h16v-4"/>',
    support:'<path d="M3 13v-1a9 9 0 0 1 18 0v4a4 4 0 0 1-4 4h-4M3 12h4v5H3zm14 0h4v5h-4z"/>',
    megaphone:'<path d="M4 9h4l10-5v14L8 14H4zM8 14l2 6h3l-2-5"/>',
    archive:'<rect x="4" y="5" width="16" height="4" rx="1"/><path d="M6 9v11h12V9m-8 4h4"/>',
    close:'<path d="m6 6 12 12M6 18 18 6"/>',
    menu:'<path d="M4 7h16M4 12h16M4 17h16"/>',
    play:'<path d="m9 5 11 7-11 7z" fill="currentColor" stroke="none"/>',
    search:'<circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/>'
  };
  const icon = (name, size=18) => `<svg aria-hidden="true" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${path[name] ?? path.bolt}</svg>`;
  const groups = [
    ['主导航', [['dashboard','总览','home'],['analytics','数据分析','pie'],['team','团队成员','users'],['schedule','日程安排','calendar']]],
    ['工作区', [['media','媒体与文件','video'],['inbox','收件箱','message','3'],['activity','动态日志','bolt']]],
    ['系统', [['settings','偏好设置','settings']]],
  ];
  const routes = Object.fromEntries(groups.flatMap(([, items]) => items.map(row => [row[0],row[1]])));
  const routeOf = () => Object.hasOwn(routes,location.hash.slice(1)) ? location.hash.slice(1) : 'dashboard';
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const narrow = matchMedia('(max-width: 740px)');
  const query = new URLSearchParams(location.search);
  const demo = query.get('demo') === '1';
  const still = query.get('still') === '1';
  const onWorkbench = query.get('surface') === 'kaiwu-code-xr' && window.parent !== window && location.origin !== 'null';
  const landing = onWorkbench ? query.get('landing') : null;
  const shell = $('#workspace'), sheet = $('#sheet'), opening = $('#opening');
  const storeKey = 'code-xr-glass-workspace-v1';
  const readState = () => { try { return JSON.parse(localStorage.getItem(storeKey)) || {}; } catch { return {}; } };
  const stored = readState();
  function save(key,value) {
    const next = {...stored,[key]:value};
    try { localStorage.setItem(storeKey,JSON.stringify(next)); }
    catch { toast('浏览器本地存储不可用，更改未保存。'); return false; }
    stored[key] = value;
    return true;
  }
  const roster = [
    ['林安雅','创意总监',31,14], ['朴俊赫','设计主管',70,11],
    ['陆知行','制片人',92,47], ['森田空','美术指导',74,86],
    ['陈美雅','动效设计师',35,90], ['顾明朗','研发工程师',13,53]
  ];
  const events = {
    9:[['09:30','管理层周同步会','极光会议室','核对近期上线计划、排查阻塞项并对齐后续推进方案。'],['12:45','创意突破头脑风暴','设计实验室','为下一期工作室冲刺准备一个核心创意与一份视觉参考。']],
    11:[['10:00','第 24 期冲刺同步','极光会议室','复盘第 24 期冲刺已交付成果。']],
    12:[['14:00','设计方案评审会','设计实验室','与核心团队共同走查最新视觉概念稿。']],
    13:[['11:00','上线发布核验会','极光会议室','共同逐项确认交付上线检查清单。']],
    14:[['10:30','工作室开放交流时段','设计实验室','用于项目短会与跨组快速沟通的预约时段。']],
  };
  const allMonths = [
    ['12月',22,13],['1月',26,15],['2月',24,13],['3月',29,18],['4月',31,17],['5月',27,14],
    ['6月',28.5,14.2],['7月',36,18],['8月',34.3,16.8],['9月',41,19],['10月',54.5,20.4],['11月',42.5,18.3]
  ];
  const channelData = [['官网直销',109.3,'#ea624e'],['客户推荐',58,'#6465b5'],['社媒获客',49.1,'#e8a454'],['合作伙伴',20.4,'#4d9b87']];
  const actions = [['requests','clipboard','审核创意请求','6 项待处理'],['pay','coin','团队薪资结算','薪资汇总'],['announce','megaphone','发布新公告','1 项已排期'],['support','support','处理支持工单','4 项未关闭'],['download','download','下载营收报表','近 6 个月'],['backup','archive','立即备份','导出工作区副本']];
  const messages = [['发布资产已就绪','林安雅','最终发布文件已上传至媒体与文件中心。'],['11 月用量分析报告','朴俊赫','前往数据分析页可对比近 3、6 或 12 个月经营表现。'],['第 24 期冲刺检查点','陆知行','今日有 7 项任务到期，请进入冲刺详情核对后续安排。']];
  const recent = [['09:10','交付检查清单已更新','林安雅'],['08:54','新增 2 项创意需求','森田空'],['昨天','11 月经营报表已归档','顾明朗']];
  const scrollByRoute = Object.create(null);
  let route = routeOf(), selectedDay = 9, range = 6, closed = false, mobileOpen = false;
  let caller, timers = [], openingCleanup, frame = 0, toastTimer, playingDemo = false, revealObserver;
  const metric = (v, lead='', suffix='', pad=0) => `<span class="metric-number" data-number="${v}" data-lead="${lead}" data-suffix="${suffix}" data-pad="${pad}">${lead}${Number(v).toLocaleString('en-US',{minimumIntegerDigits: Math.max(1,pad),maximumFractionDigits:2,minimumFractionDigits:v===99.96?2:0})}${suffix}</span>`;
  const btn = (text, design, action, glyph='', extra='') => `<button type="button" class="button ${design}" data-action="${action}" ${extra}>${glyph?icon(glyph,16):''}<span>${text}</span></button>`;
  const head = (title, sub, controls='', euId='') => `<header class="heading enter"${euId?` data-eu-id="${euId}"`:''}><div class="heading-copy"><h1 tabindex="-1">${title}</h1><p>${sub}</p></div><div class="heading-actions">${controls}</div></header>`;
  const avatar = (index, cls='') => `<img src="${asset(`assets/portrait-${index+1}.webp`)}" alt="" class="${cls}" width="44" height="44">`;
  const navRowEu = (id) => id === 'dashboard' ? ' data-eu-id="eu_L4_dock_active_pill"' : id === 'analytics' ? ' data-eu-id="eu_L4_dock_neighbor_field"' : '';

  shell.innerHTML = `<button type="button" class="mobile-shade" aria-label="关闭导航" tabindex="-1" data-action="mobile-close"></button>
    <aside class="sidebar" id="sidebar" data-eu-id="eu_L1_nav_dock"><nav aria-label="工作区导航" class="nav" data-eu-id="eu_L3_rail_proximity_dock">
      <div class="brand" data-eu-id="eu_L3_brand_header"><span class="brand-tile"><img src="${asset('assets/mark.svg')}" alt=""></span><span class="brand-copy"><strong>Code XR</strong><small>折光玻璃工作台</small></span></div>
      <button type="button" class="rail-toggle" data-eu-id="eu_L4_feat_rail_collapse" aria-label="收起侧栏" aria-expanded="true" aria-controls="workspace-links" data-action="collapse">${icon('left',16)}</button>
      <button type="button" class="ask" data-eu-id="eu_L4_dock_search_orb" aria-label="问一问或搜索" data-action="search"><span class="orb" aria-hidden="true"></span><span class="ask-copy">问一问或搜索<span class="caret">_</span></span><kbd>⌘K</kbd></button>
      <div class="nav-groups" id="workspace-links" data-eu-id="eu_L3_nav_route_list">${groups.map(([label,items])=>`<section class="nav-group" aria-label="${label}"><p aria-hidden="true">${label}</p>${items.map(([id,title,glyph,count])=>`<a class="nav-row" data-route="${id}"${navRowEu(id)} href="#${id}" aria-label="${title}"><span class="dock-backplate" aria-hidden="true"></span>${icon(glyph)}<span class="nav-label">${title}</span>${count?`<span class="nav-count">${count}</span>`:''}</a>`).join('')}</section>`).join('')}</div>
      <div class="nav-bottom" data-eu-id="eu_L3_sidebar_footer"><button type="button" class="nav-row" data-action="notifications" aria-label="消息通知">${icon('bell')}<span class="nav-label">消息通知</span><span class="nav-count hot" id="notice-count">2</span></button>
      <button type="button" class="profile" data-action="profile" aria-label="Code XR 账户" title="Code XR 账户">${avatar(5,'profile-pic')}<span class="profile-copy"><strong>Code XR</strong><small>hello@codexr.studio</small></span></button></div>
    </nav><span class="dock-label" data-eu-id="eu_L4_feat_proximity_magnify" aria-hidden="true" hidden></span></aside>
    <main class="main-glass" id="main-panel" data-eu-id="eu_L1_main_stage" tabindex="-1" aria-label="工作区内容"><div class="mobile-bar" data-eu-id="eu_L3_mobile_top_bar"><button type="button" class="mobile-toggle" data-action="mobile-open" aria-label="打开导航" aria-controls="sidebar" aria-expanded="false">${icon('menu',20)}</button><span class="mobile-brand">CODE XR</span><button type="button" class="mobile-toggle" data-action="search" aria-label="搜索工作区">${icon('search',19)}</button></div><div class="view" id="view"></div></main>`;
  const viewport = $('.main-glass'), view = $('#view'), sidebar = $('.sidebar'), toggle = $('.rail-toggle'), mobileButton = $('.mobile-bar [data-action="mobile-open"]');
  const dockItems = [...sidebar.querySelectorAll('.ask, .nav-row')];
  const dockLabel = $('.dock-label',sidebar), dockLinks = $('.nav-groups',sidebar);
  const dockRadius = 108, dockGain = .37;
  let dockPointer, dockFrame = 0, dockActive = new Set();

  const dockAvailable = () => closed && !narrow.matches && opening.hidden && !sheet.open;
  function clearDock() {
    for(const item of dockActive) {
      item.style.removeProperty('--dock-scale');
      item.style.removeProperty('--dock-shift');
    }
    dockActive.clear();
    dockLabel.hidden = true;
  }
  function resetDock() {
    cancelAnimationFrame(dockFrame);
    dockFrame = 0;
    dockPointer = null;
    clearDock();
  }
  function updateDock() {
    dockFrame = 0;
    if(!dockAvailable()) return clearDock();
    const rail = sidebar.getBoundingClientRect();
    const pointer = dockPointer;
    const inReach = pointer && pointer.x >= rail.left-32 && pointer.x <= rail.right+32
      && pointer.y >= rail.top && pointer.y <= rail.bottom;
    const focus = document.activeElement;
    const target = inReach ? document.elementFromPoint(pointer.x,pointer.y)?.closest('.ask,.nav-row')
      : focus?.matches(':focus-visible') ? focus : null;
    const labelItem = dockItems.includes(target) ? target : null;
    if((!inReach || motion.matches) && !labelItem) return clearDock();

    // Measure the stable hit boxes first; transform only their paint, never the links themselves.
    const scrollBox = dockLinks.getBoundingClientRect();
    const settings = [], active = new Set();
    let labelAt = 0;
    for(const item of dockItems) {
      const box = item.getBoundingClientRect(), cy = (box.top+box.bottom)/2;
      if(dockLinks.contains(item) && (cy < scrollBox.top || cy > scrollBox.bottom)) continue;
      const dx = inReach ? pointer.x-(box.left+box.right)/2 : 0;
      const dy = inReach ? cy-pointer.y : 0;
      const near = inReach && !motion.matches ? Math.max(0,1-Math.hypot(dx*1.8,dy)/dockRadius) : 0;
      const gain = near*near*(3-2*near);
      const shift = Math.max(-1,Math.min(1,dy/36))*gain*7;
      if(near > 0) {
        active.add(item);
        settings.push([item,1+dockGain*gain,shift]);
      }
      if(item===labelItem) labelAt = cy+shift-rail.top;
    }
    for(const item of dockActive) if(!active.has(item)) {
      item.style.removeProperty('--dock-scale');
      item.style.removeProperty('--dock-shift');
    }
    for(const [item,scale,shift] of settings) {
      item.style.setProperty('--dock-scale',scale.toFixed(4));
      item.style.setProperty('--dock-shift',`${shift.toFixed(2)}px`);
    }
    dockActive = active;
    dockLabel.hidden = !labelAt;
    if(labelAt) {
      dockLabel.style.top = `${labelAt}px`;
      const name = labelItem.getAttribute('aria-label');
      if(dockLabel.textContent!==name) dockLabel.textContent = name;
    }
  }
  function queueDock() {
    if(!dockFrame) dockFrame = requestAnimationFrame(updateDock);
  }

  function renderSprint() {
    return `<section class="sprint-card enter" data-eu-id="eu_L3_sprint_hero" aria-labelledby="sprint-title"><div class="sprint-copy" data-eu-id="eu_L4_feat_sprint_copy">
      <div class="sprint-badge"><i></i><span>第 24 期冲刺</span><span>4 位成员在线</span></div>
      <h2 id="sprint-title">团队本周状态<br><em>势如破竹</em></h2>
      <p>本期冲刺已交付 68%，另有 3 个发布版本蓄势待发。</p>
      <dl class="sprint-stats"><div><dt>${metric(12)}</dt><dd>进行中项目</dd></div><div><dt>${metric(7)}</dt><dd>今日到期</dd></div><div><dt>${metric(98,'','%')}</dt><dd>准时交付</dd></div></dl>
      <div class="sprint-actions"><button class="button light" type="button" data-action="sprint"><span>查看冲刺</span>${icon('arrow',15)}</button>${btn('添加成员','outline','invite','plus')}</div></div>
      <figure class="progress-wheel" data-eu-id="eu_L3_orbit_avatars_fold" aria-label="第 24 期冲刺：已交付 68%">
        <svg class="orbit" data-eu-id="eu_L4_feat_orbit_ring" viewBox="0 0 190 190" aria-hidden="true"><circle class="orbit-track" cx="95" cy="95" r="79"/><circle class="orbit-value" cx="95" cy="95" r="79" pathLength="100"/><circle class="orbit-point" cx="23.51" cy="128.64" r="4.5"/></svg>
        <figcaption><strong>${metric(68,'','%')}</strong><span>已交付</span></figcaption>
        ${roster.map(([name,role,x,y],i)=>`<button class="orbit-avatar" style="--x:${x}%;--y:${y}%;--delay:${i*60}ms" type="button" data-action="person" data-index="${i}" aria-label="${name}，${role}" title="${name}">${avatar(i)}</button>`).join('')}
      </figure></section>`;
  }
  function calendarBody() {
    const weekdays = ['星期一','星期二','星期三','星期四','星期五','星期六','星期日'];
    const shortDays = ['一','二','三','四','五','六','日'];
    const list = events[selectedDay] || [];
    return `<div class="calendar-head"><strong class="calendar-date">${String(selectedDay).padStart(2,'0')}</strong><div><h2>${weekdays[selectedDay-9]}</h2><p>2026年11月 <span>·</span> ${list.length} 项日程</p></div>
      <button class="icon-chip" type="button" data-action="${route==='schedule'?'today':'open-schedule'}" aria-label="${route==='schedule'?'回到今日':'打开完整日程'}">${icon('calendar',17)}</button></div>
      <div class="week" data-eu-id="eu_L4_feat_week_picker" aria-label="11月9日当周">${shortDays.map((d,i)=>`<button class="day" type="button" data-action="day" data-index="${i+9}" aria-label="11月${i+9}日" aria-pressed="${selectedDay===i+9}"><span>${d}</span><b>${i+9}</b><i class="${events[i+9]?'has-event':''}"></i></button>`).join('')}</div>
      <div class="event-list" aria-live="polite">${list.length ? list.map(([time,title,where],i)=>`<button class="event" type="button" data-action="event" data-index="${i}"><time>${time}</time><span class="event-rule"></span><span class="event-copy"><strong>${title}</strong><small>${icon('pin',12)}${where}</small></span>${i===0&&selectedDay===9?'<b class="next-label">即将开始</b>':''}</button>`).join('') : '<p class="empty-day">当日暂无日程安排。</p>'}</div>`;
  }
  const calendar = () => `<section class="glass-card calendar enter" data-eu-id="eu_L3_studio_calendar" aria-label="工作室日程">${calendarBody()}</section>`;
  const revenueNow = () => 42500 + (stored.deals || []).reduce((sum,d)=>sum+d.amount,0);
  const amountShort = (n) => `$${n.toFixed(1).replace(/\.0$/,'')}K`;
  const metricData = () => [
    ['people','users',128,'','','↑ 12%','活跃成员','当前 24 人在线','M3 33 12 27 20 29 32 21 39 22 50 13 62 14 76 5'],
    ['deals','bag',49+(stored.deals?.length||0),'','','↑ 8%','跟进中商机','管线总额 $4.8M','M3 34 10 29 17 32 27 24 38 25 48 16 58 17 73 8'],
    ['revenue','coin',revenueNow(),'$','','↓ 5%','本月营收','上月营收 $44.7K','M3 8 13 19 20 16 30 25 39 21 49 28 57 26 73 34'],
    ['uptime','server',99.96,'','%','↑ 0.4%','系统可用性','近 30 天 · 全绿运行','M3 34 12 24 22 28 34 13 44 11 52 19 61 8 73 8'],
  ];
  function metrics() {
    return `<div class="metrics" data-eu-id="eu_L3_metrics_grid_fold" aria-label="核心指标">${metricData().map(([id,symbol,value,pre,suf,change,title,foot,d],i)=>`<article class="glass-card metric metric-${id} enter" style="--stagger:${i}"><header><span class="icon-chip">${icon(symbol,17)}</span><span class="delta">${change}</span></header><p class="metric-value">${metric(value,pre,suf)}</p><div class="metric-label"><h2>${title}</h2><p>${foot}</p></div><svg class="spark" viewBox="0 0 78 40" aria-hidden="true"><path pathLength="1" d="${d}"/><circle cx="${d.split(' ').at(-2)}" cy="${d.split(' ').at(-1)}" r="2.8"/></svg></article>`).join('')}</div>`;
  }
  function series() {
    return allMonths.slice(-range).map(([month,profit,cost])=>[month,month==='11月'?revenueNow()/1000:profit,cost]);
  }
  function revenueChart() {
    const data = series(), profit = data.reduce((sum,row)=>sum+row[1],0);
    const max = Math.max(60, Math.ceil(Math.max(...data.map(row=>row[1]))/20)*20);
    return `<article class="glass-card revenue-card enter" data-eu-id="eu_L3_revenue_chart_card" aria-labelledby="revenue-title"><header class="chart-head"><div><h2 id="revenue-title">营收趋势</h2><p>近 ${range} 个月累计利润 ${amountShort(profit)}</p></div><div class="chart-actions"><div class="segments" data-eu-id="eu_L4_feat_range_segments" role="group" aria-label="统计周期">${[3,6,12].map(r=>`<button type="button" aria-pressed="${range===r}" data-action="range" data-index="${r}">近 ${r} 个月</button>`).join('')}</div>${btn('录入商机','dark','deal','plus')}</div></header>
      <div class="legend"><span><i></i>利润</span><span><i></i>成本</span></div>
      <div class="chart" data-eu-id="eu_L4_feat_dual_bars" aria-label="月度利润与成本"><div class="axis-y" aria-hidden="true">${[max,max*3/4,max/2,max/4,0].map(v=>`<span>${v}K</span>`).join('')}</div>
      <div class="plot" style="--groups:${data.length}">${data.map(([month,p,c],i)=>`<button type="button" class="bar-group" data-action="chart-detail" data-index="${i}" aria-label="${month}：利润 ${amountShort(p)}，成本 ${amountShort(c)}"><span class="bar-pair"><i style="--height:${p/max*100}%;--stagger:${i}"></i><i style="--height:${c/max*100}%;--stagger:${i}"></i></span><span class="month">${month}</span><span class="chart-tooltip" aria-hidden="true">${month} · ${amountShort(p)}</span></button>`).join('')}</div></div></article>`;
  }
  function channels() {
    return `<article class="glass-card channels enter" data-eu-id="eu_L3_channel_donut_card"><header><h2>各渠道营收分布</h2><p>近 6 个月 · 峰值一目了然</p></header><div class="channel-wheel" data-eu-id="eu_L4_feat_conic_donut" aria-label="总营收 236,800 美元"><div><strong>$236.8K</strong><span>总营收</span></div></div><ul>${channelData.map(([name,value,color])=>`<li><i style="--color:${color}"></i><span>${name}</span><b>${amountShort(value)}</b></li>`).join('')}</ul></article>`;
  }
  const quick = () => `<section class="quick" data-eu-id="eu_L3_quick_actions_fold" aria-label="快捷操作">${actions.map(([id,glyph,name,desc])=>`<button type="button" class="quick-action glass-card enter" data-action="${id}"><span class="icon-chip">${icon(glyph,16)}</span><span><strong>${name}</strong><small>${id==='download'?`近 ${range} 个月`:desc}</small></span></button>`).join('')}</section>`;
  function dashboard() {
    return head('下午好，Code XR','2026年11月9日 星期一 <span>·</span> 7 项待办需要关注',btn('动态日志','soft','activity','clock')+btn('邀请成员','dark','invite','plus'),'eu_L3_page_heading') +
      `<div class="hero-grid">${renderSprint()}${calendar()}</div>${metrics()}${quick()}<section class="revenue-grid">${revenueChart()}${channels()}</section>`;
  }
  function analytics() {
    return head('数据分析','追踪营收、成本与工作室整体表现。',btn('下载报表','dark','download','download','data-eu-id="eu_L4_feat_csv_export"'),'eu_L3_analytics_header_csv')+metrics()+`<section class="revenue-grid full" data-eu-id="eu_L3_analytics_wide_stage">${revenueChart()}</section>`;
  }
  const sectionRow = (name,desc,glyph,extra='') => `<article class="list-row"><span class="icon-chip">${icon(glyph,17)}</span><div><strong>${name}</strong><p>${desc}</p></div>${extra}</article>`;
  function moduleView(id) {
    if(id==='team') return head('团队成员','共同创造这些作品的核心成员。',btn('邀请成员','dark','invite','plus')) + `<section class="glass-card module-card"><h2>工作室成员</h2><div class="team-grid">${roster.map(([n,r],i)=>`<button class="person-card" data-action="person" data-index="${i}">${avatar(i)}<strong>${n}</strong><span>${r}</span></button>`).join('')}</div><h2>待发送邀请</h2>${(stored.invites || []).length?(stored.invites).map(e=>sectionRow(escape(e),'邀请草稿','users')).join(''):'<p>暂无待发送的邀请草稿。</p>'}</section>`;
    if(id==='schedule') return head('日程安排','工作室活动 · 11月9日当周')+`<div class="schedule-layout">${calendar()}<section class="glass-card module-card"><h2>本周安排</h2>${Object.entries(events).flatMap(([day,list])=>list.map(([time,title,where])=>sectionRow(title,`11月${day}日 · ${time} · ${where}`,'calendar'))).join('')}</section></div>`;
    if(id==='media') return head('媒体与文件','工作室视觉参考与交付资产。')+`<section class="glass-card module-card"><h2>工作区文件</h2>${sectionRow('营收统计报表','CSV · 当前所选周期','clipboard',btn('下载','soft','download','download'))}${sectionRow('工作区数据快照','JSON · 本地工作区备份','archive',btn('导出','soft','backup','download'))}</section>`;
    if(id==='inbox') return head('收件箱','来自工作室内部的最新消息。')+`<section class="glass-card module-card"><h2>近期消息</h2>${messages.map(([name,from],i)=>sectionRow(name,from,'message',`<button class="button soft" data-action="message" data-index="${i}">查看</button>`)).join('')}</section>`;
    if(id==='activity') return head('动态日志','工作室近期更新记录。')+`<section class="glass-card module-card"><h2>变更流水</h2>${recent.map(([time,title,who])=>sectionRow(title,`${time} · ${who}`,'clock')).join('')}${(stored.deals||[]).map(d=>sectionRow(escape(d.name),`${usd.format(d.amount)} · 已录入商机`,'coin')).join('')}</section>`;
    return head('偏好设置','折光玻璃工作台配置项。')+`<section class="glass-card module-card"><h2>工作区控制台</h2>${sectionRow('入场动画','重播 Code XR 品牌虹膜揭幕。','play',btn('重播','soft','replay','play'))}${sectionRow('全段参考序列','连续演示揭幕、总览滚动与数据分析切页。','play',btn('播放序列','soft','demo','play'))}${sectionRow('工作区副本','导出已保存的草稿与商机数据。','archive',btn('导出','soft','backup','download'))}</section>`;
  }

  function setCollapsed(value) {
    resetDock();
    closed = value;
    shell.classList.toggle('collapsed',closed);
    toggle.setAttribute('aria-expanded',String(!closed));
    toggle.setAttribute('aria-label',closed?'展开侧栏':'收起侧栏');
    toggle.innerHTML=icon(closed?'right':'left',16);
  }
  function drawer(open, focusBack=false) {
    mobileOpen = open && narrow.matches;
    shell.classList.toggle('drawer-open',mobileOpen);
    mobileButton.setAttribute('aria-expanded',String(mobileOpen));
    sidebar.inert = narrow.matches && !mobileOpen;
    viewport.inert = mobileOpen;
    if(mobileOpen) $('.nav-row[aria-current="page"]').focus();
    if(focusBack && narrow.matches) mobileButton.focus();
  }
  function render(animated=true) {
    document.title = `${route==='dashboard'?'Code XR':routes[route]+' · Code XR'} · 折光玻璃工作台`;
    viewport.dataset.page = route;
    view.innerHTML = route==='dashboard'?dashboard():route==='analytics'?analytics():moduleView(route);
    shell.querySelectorAll('[data-route]').forEach(el=>el.dataset.route===route?el.setAttribute('aria-current','page'):el.removeAttribute('aria-current'));
    $('#notice-count').hidden = !!stored.readNotices;
    revealObserver?.disconnect();
    if(route==='dashboard' && 'IntersectionObserver' in window) {
      const quickActions = $('.quick',view);
      quickActions.classList.add('waiting-reveal');
      revealObserver = new IntersectionObserver(entries=>{
        for(const entry of entries) if(entry.isIntersecting && entry.intersectionRatio>.20){
          entry.target.classList.remove('waiting-reveal');
          revealObserver.unobserve(entry.target);
        }
      },{root:viewport,threshold:[.21]});
      revealObserver.observe(quickActions);
    }
    if(animated && !motion.matches) animateView();
    else { cancelAnimationFrame(frame); view.classList.remove('animated'); }
  }
  function navigate(to,{push=true,focus=true}={}) {
    if(!Object.hasOwn(routes,to)) return;
    if(to!==route) {
      scrollByRoute[route] = viewport.scrollTop;
      route=to;
      if(push) history.pushState(null,'',`#${route}`);
      render();
      viewport.scrollTop = scrollByRoute[route] || 0;
      if(onWorkbench && (route==='dashboard'||route==='analytics')) {
        window.parent.postMessage({type:'code-xr:navigation/1',route},location.origin);
      }
    }
    if(mobileOpen) drawer(false);
    if(focus) $('h1',view).focus({preventScroll:true});
  }
  function animateView(hold=0) {
    cancelAnimationFrame(frame);
    view.classList.remove('animated');
    view.style.setProperty('--enter-wait',hold?'420ms':'0ms');
    void view.offsetWidth;
    view.classList.add('animated');
    const numbers = [...view.querySelectorAll('[data-number]')].map((el,i)=>{
      const last=el.textContent;
      const visual=document.createElement('span');visual.className='reels';visual.setAttribute('aria-hidden','true');
      const accessible=document.createElement('span');accessible.className='sr-only';accessible.textContent=last;
      let pos=0;
      const reels=[];
      for(const char of last) {
        if(!/\d/.test(char)){visual.append(char);continue;}
        const slot=document.createElement('span');slot.className='reel-slot';
        const wheel=document.createElement('span');wheel.className='reel-wheel';
        const turns=(pos%2===0?10:0)+Number(char);
        for(let n=0;n<=turns;n++){const numeral=document.createElement('span');numeral.textContent=String(n%10);wheel.append(numeral);}
        slot.append(wheel);visual.append(slot);
        reels.push({wheel,turns,delay:100+(i%4)*55+pos*27});pos++;
      }
      el.replaceChildren(accessible,visual);
      return {el,last,reels};
    });
    const arc = $('.orbit-value'), dot = $('.orbit-point');
    let start;
    const amount = (v,t) => v * (1-Math.pow(1-t,3));
    const tick = (now) => {
      start ??= now;
      const passed = now-start-hold;
      for(const {el,last,reels} of numbers) if(passed>=1420) el.textContent=last;
      else for(const {wheel,turns,delay} of reels) {
        const t = Math.max(0,Math.min(1,(passed-delay)/980));
        wheel.style.transform=`translate3d(0,${-amount(turns,t)*1.08}em,0)`;
      }
      if(arc && dot) {
        const progress = amount(68,Math.max(0,Math.min(1,(passed-180)/1180)));
        const angle = progress/100 * 2*Math.PI - Math.PI/2;
        arc.style.strokeDasharray=`${progress} 100`;
        dot.setAttribute('cx',String(95+79*Math.cos(angle)));
        dot.setAttribute('cy',String(95+79*Math.sin(angle)));
      }
      if(passed<1420) frame=requestAnimationFrame(tick);
    };
    frame=requestAnimationFrame(tick);
  }
  function toast(message) {
    const status = $('#status');
    status.textContent=message;
    status.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer=setTimeout(()=>status.classList.remove('show'),2800);
  }
  function dialog(title, body, kind='') {
    resetDock();
    if(!sheet.open) caller = document.activeElement;
    sheet.className=`sheet ${kind}`;
    sheet.innerHTML=`<header class="sheet-head"><h2 id="sheet-title">${title}</h2><button type="button" data-action="close" class="icon-button" aria-label="关闭">${icon('close')}</button></header><div class="sheet-body">${body}</div>`;
    if(!sheet.open) sheet.showModal();
    const initial = $('input',sheet) ?? $('.icon-button',sheet);
    initial.focus();
  }
  function download(name,contents,type) {
    const url=URL.createObjectURL(new Blob([contents],{type}));
    const link=Object.assign(document.createElement('a'),{href:url,download:name});
    document.body.append(link);link.click();link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),10000);
  }
  const commandItems = [...Object.entries(routes).map(([id,label])=>[label,'go-'+id,'页面']),['下载营收报表','download','操作'],['邀请成员','invite','操作'],['查看冲刺','sprint','操作']];
  function searchResults(q='') {
    const list = commandItems.filter(([label])=>label.toLowerCase().includes(q.trim().toLowerCase()));
    $('#commands').innerHTML=list.length?list.map(([name,action,type])=>`<button type="button" data-action="${action}" aria-label="${name}"><span>${name}</span><small>${type}</small></button>`).join(''):'<p>未找到匹配的页面或操作。</p>';
  }
  function updateCalendar(index) {
    selectedDay=index;
    const cal=$('.calendar',view);
    cal.innerHTML=calendarBody();
    $(`[data-action="day"][data-index="${index}"]`,cal).focus({preventScroll:true});
  }
  function runAction(action,index) {
    if(action.startsWith('go-')) { if(sheet.open) sheet.close(); navigate(action.slice(3)); return; }
    switch(action) {
      case 'collapse': setCollapsed(!closed);break;
      case 'mobile-open': drawer(true);break;
      case 'mobile-close': drawer(false,true);break;
      case 'activity': navigate('activity');break;
      case 'open-schedule':navigate('schedule');break;
      case 'today':updateCalendar(9);break;
      case 'day':updateCalendar(index);break;
      case 'close':sheet.close();break;
      case 'search': dialog('工作区全局检索','<label class="sr-only" for="command-input">搜索页面或快捷操作</label><input id="command-input" type="search" placeholder="搜索页面或快捷操作…" autocomplete="off"><div id="commands" class="commands"></div>','command-sheet');searchResults();break;
      case 'range': {
        range=index;
        $('.revenue-card',view).outerHTML=revenueChart();
        $(`[data-action="range"][data-index="${range}"]`,view).focus({preventScroll:true});
        const quickText=$('.quick [data-action="download"] small',view);
        if(quickText) quickText.textContent=`近 ${range} 个月`;
        break;
      }
      case 'download': download(`code-xr-revenue-${range}m.csv`,'月份,利润(USD),成本(USD)\n'+series().map(([m,p,c])=>`${m},${Math.round(p*1000)},${Math.round(c*1000)}`).join('\n')+'\n','text/csv;charset=utf-8');toast('营收报表已开始下载。');break;
      case 'backup': download('code-xr-workspace.json',JSON.stringify({workspace:'Code XR',...stored},null,2),'application/json');toast('工作区备份副本已导出。');break;
      case 'event': {const [time,title,where,note]=events[selectedDay][index];dialog(title,`<p class="sheet-detail">${icon('calendar')} 11月${selectedDay}日 · ${time}</p><p class="sheet-detail">${icon('pin')} ${where}</p><p>${note}</p>`);break;}
      case 'sprint': dialog('第 24 期冲刺','<p>已交付 68% · 今日到期 7 项 · 准时交付率 98%</p><ul class="detail-list"><li><span>插画资产包</span><b>已就绪</b></li><li><span>工作台正式发布</span><b>已就绪</b></li><li><span>11 月工作室官网</span><b>已就绪</b></li></ul>');break;
      case 'person':{const [name,role]=roster[index];dialog(name,`<div class="person-detail">${avatar(index)}<div><strong>${role}</strong><p>Code XR 创意工作室</p></div></div>`);break;}
      case 'invite':dialog('邀请成员','<form data-form="invite"><label for="email">电子邮箱</label><input id="email" name="email" type="email" placeholder="name@example.com" maxlength="254" required><p>将成员邀请草稿保存至团队列表。</p><button class="button dark" type="submit">保存邀请草稿</button></form>');break;
      case 'deal':dialog('录入商机','<form data-form="deal"><label for="deal-name">商机名称</label><input id="deal-name" name="name" maxlength="90" required><label for="amount">金额（美元）</label><input id="amount" type="number" name="amount" min="1" max="10000000" step="1" required><button class="button dark" type="submit">确认录入</button></form>');break;
      case 'chart-detail':{const [m,p,c]=series()[index];dialog(`${m}营收明细`,`<p>利润：<b>${usd.format(p*1000)}</b> · 成本：<b>${usd.format(c*1000)}</b></p>`);break;}
      case 'notifications':dialog('消息通知',`<ul class="detail-list"><li><span>有两项上线版本等待复核</span><b>今日</b></li><li><span>管理层周同步会将于 09:30 开始</span><b>今日</b></li></ul>${stored.readNotices?'':btn('全部标为已读','dark','mark-read')}`);break;
      case 'mark-read':if(save('readNotices',true)){ $('#notice-count').hidden=true;sheet.close();toast('消息已全部标为已读。'); }break;
      case 'profile':dialog('Code XR','<p>折光玻璃工作台 · hello@codexr.studio</p>'+btn('播放序列','soft','demo','play')+btn('偏好设置','soft','go-settings','settings'));break;
      case 'replay':case 'demo':if(sheet.open)sheet.close();navigate('dashboard',{focus:false});viewport.scrollTop=0;startIntro(action==='demo');break;
      case 'message':{const [name,from,note]=messages[index];dialog(name,`<p><b>${from}</b></p><p>${note}</p>`);break;}
      case 'requests':dialog('创意请求列表','<ul class="detail-list"><li><span>设计创意需求</span><b>6 项待处理</b></li><li><span>待上线项目</span><b>3 个项目</b></li></ul>');break;
      case 'pay':dialog('团队薪资汇总','<p>生成薪资清单前请核对当前工作室成员名单。</p>'+btn('查看团队成员','soft','go-team','users'));break;
      case 'announce':dialog('工作室公告','<ul class="detail-list"><li><span>第 24 期冲刺发布简报</span><b>已排期</b></li></ul>');break;
      case 'support':dialog('客户支持队列','<p>当前有 4 项未关闭支持工单。</p>'+btn('打开收件箱','soft','go-inbox','message'));break;
    }
  }
  function cancelTimers() { timers.forEach(clearTimeout);timers=[];playingDemo=false; }
  function finishOpening() { opening.hidden=true; opening.classList.remove('playing'); shell.inert=false; sheet.inert=false; }
  function startIntro(runDemo) {
    cancelTimers();clearTimeout(openingCleanup);
    if(motion.matches) {setCollapsed(false);finishOpening();return;}
    setCollapsed(!narrow.matches);
    opening.hidden=false;
    shell.inert=true; sheet.inert=true;
    opening.classList.remove('playing');void opening.offsetWidth;opening.classList.add('playing');
    playingDemo=runDemo;
    render(false);
    animateView(520);
    openingCleanup=setTimeout(finishOpening,1120);
    timers.push(setTimeout(()=>setCollapsed(false),2350));
    if(runDemo) {
      timers.push(setTimeout(()=>viewport.scrollTo({top:512,behavior:'smooth'}),3500));
      timers.push(setTimeout(()=>{navigate('analytics',{focus:false});playingDemo=false;},4770));
    }
  }

  document.addEventListener('click',e=>{
    const nav=e.target.closest('a[data-route]');
    if(nav && !e.ctrlKey&&!e.metaKey&&!e.shiftKey&&!e.altKey) { e.preventDefault();cancelTimers();navigate(nav.dataset.route);return; }
    const button=e.target.closest('[data-action]');
    if(button){cancelTimers();runAction(button.dataset.action,Number(button.dataset.index));}
  });
  opening.addEventListener('click',e=>{if(e.target.closest('button')){cancelTimers();clearTimeout(openingCleanup);setCollapsed(false);finishOpening();render(false);$('h1',view).focus({preventScroll:true});}});
  sheet.addEventListener('close',()=>{if(caller?.isConnected && sheet.contains(document.activeElement))caller.focus();else if(caller?.isConnected && document.activeElement===document.body)caller.focus();});
  sheet.addEventListener('click',e=>{if(e.target===sheet) {const r=sheet.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)sheet.close();}});
  sheet.addEventListener('input',e=>{if(e.target.id==='command-input')searchResults(e.target.value);});
  sheet.addEventListener('submit',e=>{
    e.preventDefault(); const data=new FormData(e.target);
    if(e.target.dataset.form==='invite') {
      const email=String(data.get('email')).trim().toLowerCase();
      if((stored.invites||[]).includes(email)) {toast('该邮箱的邀请草稿已存在。'); return;}
      if(!save('invites',[...(stored.invites||[]),email]))return;
      sheet.close();if(route==='team') render(false);toast('邀请草稿已保存。');
    } else if(e.target.dataset.form==='deal') {
      const name=String(data.get('name')).trim(), amount=Number(data.get('amount'));
      if(!name||!Number.isInteger(amount)||amount<1||amount>10000000)return;
      if(!save('deals',[...(stored.deals||[]),{name,amount}]))return;
      const y=viewport.scrollTop;
      sheet.close();render(false);viewport.scrollTop=y;
      $('[data-action="deal"]',view)?.focus({preventScroll:true});toast('商机已录入工作区。');
    }
  });
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'&&!opening.hidden){cancelTimers();finishOpening();setCollapsed(false);render(false);return;}
    if(e.key==='Escape'&&mobileOpen&&!sheet.open){drawer(false,true);return;}
    if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'&&opening.hidden){e.preventDefault();cancelTimers();if(sheet.open)sheet.close();else runAction('search');}
    if(e.key==='Enter'&&e.target.id==='command-input'){e.preventDefault();$('#commands button')?.click();}
    if(playingDemo && !['Tab','Shift'].includes(e.key))cancelTimers();
  });
  document.addEventListener('pointermove',e=>{
    if(!dockAvailable()) return;
    if(e.pointerType!=='mouse') {
      if(dockPointer) resetDock();
      return;
    }
    dockPointer = {x:e.clientX,y:e.clientY};
    queueDock();
  },{passive:true});
  document.addEventListener('pointerout',e=>{if(e.relatedTarget===null && dockPointer) resetDock();});
  document.addEventListener('pointercancel',resetDock);
  document.addEventListener('focusin',e=>{
    if(!dockAvailable()) return;
    if(e.target.matches(':focus-visible')) dockPointer = null;
    queueDock();
  });
  document.addEventListener('focusout',()=>{if(dockAvailable() && !dockPointer) queueDock();});
  dockLinks.addEventListener('scroll',()=>{if(dockAvailable() && dockPointer) queueDock();},{passive:true});
  window.addEventListener('blur',resetDock);
  window.addEventListener('resize',()=>{if(dockAvailable() && dockPointer) queueDock();});
  viewport.addEventListener('wheel',e=>{if(e.isTrusted&&playingDemo)cancelTimers();},{passive:true});
  window.addEventListener('popstate',()=>navigate(routeOf(),{push:false,focus:false}));
  narrow.addEventListener('change',()=>{if(narrow.matches && closed) setCollapsed(false);drawer(false);});
  motion.addEventListener('change',()=>{
    resetDock();
    if(motion.matches && (!opening.hidden || playingDemo)){cancelTimers();finishOpening();setCollapsed(false);render(false);}
  });
  render(false);drawer(false);
  if(route==='dashboard' && landing==='lower') {
    const metricsRow=$('.metrics',view);
    viewport.scrollTop=metricsRow.getBoundingClientRect().top-viewport.getBoundingClientRect().top-12;
  } else if(route==='dashboard' && landing==='collapsed') setCollapsed(!narrow.matches);
  else if(route==='dashboard'&&!still&&!motion.matches)startIntro(demo);

  /* Kaiwu v3.4 Bidirectional EU Bridge */
  const euAlias = {
    eu_L1_intro_shell: 'eu_L3_opening_iris',
    eu_L2_ambient_room: 'eu_L3_room_backdrop',
    eu_L4_feat_ambient_blur: 'eu_L3_room_backdrop',
    eu_L2_brand_opening: 'eu_L3_opening_iris',
    eu_L2_brand_rail_head: 'eu_L3_brand_header',
    eu_L2_collapsed_rail: 'eu_L3_rail_proximity_dock',
    eu_L2_expanded_nav_groups: 'eu_L3_nav_route_list',
    eu_L4_feat_route_array: 'eu_L3_nav_route_list',
    eu_L4_feat_account_status: 'eu_L3_sidebar_footer',
    eu_L2_dashboard_upper: 'eu_L3_sprint_hero',
    eu_L4_feat_heading_bar: 'eu_L3_page_heading',
    eu_L4_feat_avatar_orbit_array: 'eu_L3_orbit_avatars_fold',
    eu_L2_kpi_metrics_band: 'eu_L3_metrics_grid_fold',
    eu_L4_feat_metric_cards_array: 'eu_L3_metrics_grid_fold',
    eu_L2_dashboard_lower: 'eu_L3_quick_actions_fold',
    eu_L4_feat_quick_array: 'eu_L3_quick_actions_fold',
    eu_L2_analytics_stage: 'eu_L3_analytics_wide_stage',
    eu_L4_feat_wide_revenue: 'eu_L3_analytics_wide_stage',
    eu_L1_auxiliary_overlay: 'eu_L3_dialog_sheet',
    eu_L2_modal_dialog_sheet: 'eu_L3_dialog_sheet',
    eu_L4_feat_modal_focus_trap: 'eu_L3_dialog_sheet',
    eu_L2_mobile_responsive_bar: 'eu_L3_mobile_top_bar',
    eu_L4_feat_responsive_390: 'eu_L3_mobile_top_bar'
  };
  const dockEuSet = new Set([
    'eu_L2_collapsed_rail','eu_L3_rail_proximity_dock','eu_L4_feat_proximity_magnify',
    'eu_L4_dock_search_orb','eu_L4_dock_active_pill','eu_L4_dock_neighbor_field'
  ]);
  const analyticsEuSet = new Set([
    'eu_L2_analytics_stage','eu_L3_analytics_header_csv','eu_L4_feat_csv_export',
    'eu_L3_analytics_wide_stage','eu_L4_feat_wide_revenue'
  ]);
  const lowerEuSet = new Set([
    'eu_L2_dashboard_lower','eu_L3_quick_actions_fold','eu_L4_feat_quick_array',
    'eu_L3_revenue_chart_card','eu_L4_feat_range_segments','eu_L4_feat_dual_bars',
    'eu_L3_channel_donut_card','eu_L4_feat_conic_donut'
  ]);
  const openingEuSet = new Set(['eu_L1_intro_shell','eu_L2_brand_opening','eu_L3_opening_iris','eu_L4_feat_iris_reveal']);

  function clearKaiwuHighlight() {
    document.querySelectorAll('[data-kaiwu-active]').forEach(el => el.removeAttribute('data-kaiwu-active'));
  }

  function highlightKaiwuEu(rawEuId, fallbackEuId, action) {
    clearKaiwuHighlight();
    if (!rawEuId) return;
    cancelTimers(); clearTimeout(openingCleanup);

    if (openingEuSet.has(rawEuId)) {
      if (sheet.open) sheet.close();
      opening.hidden = false;
      opening.classList.remove('playing');
      shell.inert = false;
      const target = $(`[data-eu-id="${rawEuId}"]`) || $('.opening-brand') || opening;
      target.setAttribute('data-kaiwu-active', 'true');
      return;
    }

    if (!opening.hidden) finishOpening();
    if (rawEuId === 'eu_L3_dialog_sheet' || rawEuId === 'eu_L2_modal_dialog_sheet' || rawEuId === 'eu_L4_feat_modal_focus_trap') {
      if (!sheet.open) runAction('sprint');
      sheet.setAttribute('data-kaiwu-active', 'true');
      return;
    }
    if (sheet.open) sheet.close();

    if (analyticsEuSet.has(rawEuId)) {
      if (route !== 'analytics') navigate('analytics', {push: false, focus: false});
      if (closed) setCollapsed(false);
    } else if (dockEuSet.has(rawEuId)) {
      if (route !== 'dashboard') navigate('dashboard', {push: false, focus: false});
      if (!closed && !narrow.matches) setCollapsed(true);
      if (rawEuId === 'eu_L4_feat_proximity_magnify' || action === 'proximity_demo') {
        requestAnimationFrame(() => {
          const dashRow = $('a[data-route="dashboard"]', sidebar);
          if (dashRow && dockAvailable()) {
            const box = dashRow.getBoundingClientRect();
            dockPointer = { x: (box.left + box.right) / 2, y: (box.top + box.bottom) / 2 };
            updateDock();
          }
        });
      }
    } else {
      if (route !== 'dashboard') navigate('dashboard', {push: false, focus: false});
      if (closed && !narrow.matches && rawEuId !== 'eu_L0_codexr_workspace') setCollapsed(false);
    }

    const resolvedId = euAlias[rawEuId] || fallbackEuId || rawEuId;
    let el = $(`[data-eu-id="${rawEuId}"]`) || $(`[data-eu-id="${resolvedId}"]`);
    if (rawEuId === 'eu_L4_feat_proximity_magnify') el = $('.nav', sidebar) || sidebar;
    if (!el && fallbackEuId) el = $(`[data-eu-id="${fallbackEuId}"]`);
    if (!el) el = shell;

    const quickSec = $('.quick', view);
    if (quickSec) quickSec.classList.remove('waiting-reveal');

    if (lowerEuSet.has(rawEuId) || lowerEuSet.has(resolvedId)) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else if (viewport.contains(el) && rawEuId !== 'eu_L1_main_stage') {
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    el.setAttribute('data-kaiwu-active', 'true');
  }

  function handlePreviewAction(action) {
    clearKaiwuHighlight();
    cancelTimers(); clearTimeout(openingCleanup);
    if (sheet.open) sheet.close();
    if (action === 'collapse_sidebar') {
      finishOpening();
      if (route !== 'dashboard') navigate('dashboard', {push: false, focus: false});
      setCollapsed(true);
    } else if (action === 'proximity_demo') {
      finishOpening();
      if (route !== 'dashboard') navigate('dashboard', {push: false, focus: false});
      setCollapsed(true);
      requestAnimationFrame(() => {
        const dashRow = $('a[data-route="dashboard"]', sidebar);
        if (dashRow && dockAvailable()) {
          const box = dashRow.getBoundingClientRect();
          dockPointer = { x: (box.left + box.right) / 2, y: (box.top + box.bottom) / 2 };
          updateDock();
        }
      });
    } else if (action === 'analytics') {
      finishOpening();
      setCollapsed(false);
      navigate('analytics', {push: false, focus: false});
    } else if (action === 'opening' || action === 'replay') {
      navigate('dashboard', {push: false, focus: false});
      viewport.scrollTop = 0;
      startIntro(false);
    } else {
      finishOpening();
      setCollapsed(false);
      navigate('dashboard', {push: false, focus: false});
      viewport.scrollTop = 0;
    }
  }

  window.addEventListener('message', (ev) => {
    const msg = ev.data;
    if (!msg || typeof msg !== 'object') return;
    if (msg.type === 'KAIWU_HIGHLIGHT_EU') {
      highlightKaiwuEu(msg.eu_id, msg.fallback_eu_id, msg.action);
    } else if (msg.type === 'KAIWU_PREVIEW_ACTION') {
      handlePreviewAction(msg.action);
    }
  });

  document.addEventListener('click', (ev) => {
    if (window.parent === window) return;
    const target = ev.target.closest('[data-eu-id]');
    if (!target) return;
    const euId = target.getAttribute('data-eu-id');
    if (euId) {
      window.parent.postMessage({ type: 'KAIWU_SELECT_EU', eu_id: euId, case_id: 'code_xr_uiux' }, '*');
    }
  }, true);
})();
