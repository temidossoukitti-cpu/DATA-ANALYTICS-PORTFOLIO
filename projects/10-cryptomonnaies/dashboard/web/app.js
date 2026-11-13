const state = { data: null, year: '2024', currency: 'USD', view: 'overview', asset: 'BTCUSDT', metric: 'return', chart: 'wealth' };
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const fmtPct = (v, digits = 1) => `${(Number(v) * 100).toFixed(digits)}%`;
const fmtPrice = (v) => `${new Intl.NumberFormat('en-US', { maximumFractionDigits: Number(v) > 10000 ? 0 : 2 }).format(Number(v) * (state.currency === 'EUR' ? .92 : 1))} ${state.currency}`;
const fmtDate = (s) => String(s).slice(0, 10);
const val = (row, asset, metric) => Number(row[`${asset.toLowerCase()}_${metric}`]);
const selectedSeries = () => state.data.series.filter(row => state.year === 'all' || fmtDate(row.date).startsWith(state.year));
const selectedMonthly = () => state.data.monthly.filter(row => state.year === 'all' || String(row.month).startsWith(state.year));
const colorFor = (asset) => asset === 'BTCUSDT' ? '#9d55ff' : '#f0bd66';

function lineSvg(svg, series, keys, normalize = false) {
  const width = 800, height = 250, pad = { x: 10, y: 16, b: 18 };
  const all = keys.flatMap(key => series.map(row => Number(row[key])).filter(Number.isFinite));
  if (!all.length) { svg.innerHTML = ''; return; }
  const start = Object.fromEntries(keys.map(key => [key, Number(series[0][key])]));
  const plotted = keys.flatMap(key => series.map(row => normalize ? Number(row[key]) / start[key] * 100 : Number(row[key])).filter(Number.isFinite));
  const min = Math.min(...plotted), max = Math.max(...plotted), span = max - min || 1;
  const x = (i) => pad.x + i * ((width - pad.x * 2) / Math.max(series.length - 1, 1));
  const y = (v) => height - pad.b - ((v - min) / span) * (height - pad.y - pad.b);
  const grid = [0, .33, .66, 1].map(t => `<line x1="${pad.x}" x2="${width - pad.x}" y1="${height - pad.b - t * (height - pad.y - pad.b)}" y2="${height - pad.b - t * (height - pad.y - pad.b)}" stroke="#332d55" stroke-width="1" stroke-dasharray="2 5"/>`).join('');
  const lines = keys.map((key, index) => {
    const asset = key.includes('eth') ? 'ETHUSDT' : 'BTCUSDT';
    const points = series.map((row, i) => `${x(i)},${y(normalize ? Number(row[key]) / start[key] * 100 : Number(row[key]))}`).join(' ');
    const fill = `${points} ${width - pad.x},${height - pad.b} ${pad.x},${height - pad.b}`;
    return `<polygon points="${fill}" fill="url(#g${index})" opacity=".18"/><polyline points="${points}" fill="none" stroke="${colorFor(asset)}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>`;
  }).join('');
  const defs = `<defs><linearGradient id="g0" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#a453ff"/><stop offset="1" stop-color="#a453ff" stop-opacity="0"/></linearGradient><linearGradient id="g1" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#f0bd66"/><stop offset="1" stop-color="#f0bd66" stop-opacity="0"/></linearGradient></defs>`;
  const last = series[series.length - 1];
  const dots = keys.map((key) => { const asset = key.includes('eth') ? 'ETHUSDT' : 'BTCUSDT'; const v = normalize ? Number(last[key]) / start[key] * 100 : Number(last[key]); return `<circle cx="${x(series.length - 1)}" cy="${y(v)}" r="4" fill="${colorFor(asset)}" stroke="#19162e" stroke-width="3"/>`; }).join('');
  svg.innerHTML = `${defs}${grid}${lines}${dots}`;
}

function updateOverview() {
  const rows = selectedSeries();
  const final = rows[rows.length - 1] || state.data.series[state.data.series.length - 1];
  const first = rows[0] || state.data.series[0];
  const wealth = (val(final, 'BTCUSDT', 'wealth') + val(final, 'ETHUSDT', 'wealth')) / 2;
  const startWealth = (val(first, 'BTCUSDT', 'wealth') + val(first, 'ETHUSDT', 'wealth')) / 2;
  const heroValue = state.chart === 'wealth' ? wealth : (val(final, 'BTCUSDT', 'close') + val(final, 'ETHUSDT', 'close')) / 2;
  $('#hero-number').textContent = state.chart === 'wealth' ? heroValue.toFixed(1) : fmtPrice(heroValue);
  $('#hero-delta').textContent = state.chart === 'wealth' ? `↑ ${fmtPct(heroValue / startWealth - 1)}` : `↑ ${fmtPct(heroValue / ((val(first, 'BTCUSDT', 'close') + val(first, 'ETHUSDT', 'close')) / 2) - 1)}`;
  $('#btc-price').textContent = fmtPrice(val(final, 'BTCUSDT', 'close'));
  $('#eth-price').textContent = fmtPrice(val(final, 'ETHUSDT', 'close'));
  const btc = state.data.summary.find(x => x.symbol === 'BTCUSDT');
  const eth = state.data.summary.find(x => x.symbol === 'ETHUSDT');
  $('#btc-return').textContent = fmtPct(btc.total_return);
  $('#eth-return').textContent = fmtPct(eth.total_return);
  $('#btc-dd').textContent = fmtPct(btc.max_drawdown);
  $('#eth-dd').textContent = fmtPct(eth.max_drawdown);
  $('#corr-value').textContent = Number(state.data.correlation).toFixed(2);
  $('#btc-bar').style.width = `${Math.min(100, Math.max(12, btc.cagr * 180))}%`;
  $('#eth-bar').style.width = `${Math.min(100, Math.max(12, eth.cagr * 220))}%`;
  lineSvg($('#wealth-chart'), rows, ['btcusdt_wealth', 'ethusdt_wealth'], state.chart === 'close');
  drawMonthly();
}

function drawMonthly() {
  const rows = selectedMonthly();
  const months = [...new Set(rows.map(x => String(x.month)))].slice(-12);
  const metric = state.metric === 'return' ? 'monthly_return' : 'monthly_volatility';
  const max = Math.max(...rows.map(x => Math.abs(Number(x[metric]))), .001);
  $('#monthly-bars').innerHTML = months.map(month => {
    const b = rows.find(x => String(x.month) === month && x.symbol === 'BTCUSDT');
    const e = rows.find(x => String(x.month) === month && x.symbol === 'ETHUSDT');
    const blocks = [b, e].filter(Boolean).map((row, i) => { const n = Number(row[metric]); const h = Math.max(4, Math.round(Math.abs(n) / max * 54)); return `<div class="month-col ${i ? 'eth' : ''}"><div class="bar ${n < 0 ? 'neg' : ''}" style="--h:${h}px" title="${row.symbol} ${month}: ${fmtPct(n)}"></div></div>`; }).join('');
    return `<div class="month-group" title="${month}">${blocks}<span>${month.slice(5)}</span></div>`;
  }).join('');
}

function updateMomentum() {
  const rows = selectedMonthly().filter(x => x.symbol === state.asset);
  const metric = 'monthly_return';
  const last = rows[rows.length - 1];
  $('#momentum-number').textContent = last ? fmtPct(last[metric]) : '—';
  $('#momentum-delta').textContent = last && Number(last[metric]) >= 0 ? '↑ positive month' : '↓ negative month';
  const svgRows = rows.map(x => ({ date: x.month, value: Number(x[metric]) }));
  const svg = $('#momentum-chart'), width = 800, height = 250, pad = { x: 10, y: 16, b: 18 }, values = svgRows.map(x => x.value), max = Math.max(...values.map(Math.abs), .01), x = i => pad.x + i * ((width - pad.x * 2) / Math.max(svgRows.length - 1, 1)), y = v => height / 2 - (v / max) * (height / 2 - 24);
  const zero = height / 2, points = svgRows.map((r, i) => `${x(i)},${y(r.value)}`).join(' '), fill = `${points} ${width - pad.x},${zero} ${pad.x},${zero}`;
  svg.innerHTML = `<defs><linearGradient id="momentumFill" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#a453ff" stop-opacity=".46"/><stop offset="1" stop-color="#a453ff" stop-opacity="0"/></linearGradient></defs><line x1="${pad.x}" x2="${width - pad.x}" y1="${zero}" y2="${zero}" stroke="#665b8e" stroke-dasharray="3 5"/><polygon points="${fill}" fill="url(#momentumFill)"/><polyline points="${points}" fill="none" stroke="${colorFor(state.asset)}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>`;
  const sorted = [...rows].sort((a, b) => Number(b[metric]) - Number(a[metric]));
  $('#leaderboard-list').innerHTML = sorted.length ? `<div class="leader up"><span>Best month</span><b>${fmtPct(sorted[0][metric])}</b><small>${sorted[0].month} · ${state.asset.replace('USDT','')}</small></div><div class="leader down"><span>Worst month</span><b>${fmtPct(sorted[sorted.length - 1][metric])}</b><small>${sorted[sorted.length - 1].month} · ${state.asset.replace('USDT','')}</small></div><div class="leader"><span>Average month</span><b>${fmtPct(rows.reduce((a, x) => a + Number(x[metric]), 0) / rows.length)}</b><small>${rows.length} observations in selected range</small></div>` : '<div class="leader"><span>No data for this filter</span></div>';
  const latest = [...rows].reverse().slice(0, 8);
  $('#momentum-count').textContent = `${rows.length} rows`;
  $('#monthly-table').innerHTML = latest.map(row => `<tr><td>${row.month}</td><td><b style="color:${colorFor(row.symbol)}">${row.symbol.replace('USDT','')}</b></td><td class="${Number(row.monthly_return) >= 0 ? 'positive' : 'negative'}">${fmtPct(row.monthly_return)}</td><td>${fmtPct(row.monthly_volatility)}</td><td>${fmtPrice(row.close)}</td></tr>`).join('');
}

function updatePersona() {
  const btc = state.data.summary.find(x => x.symbol === 'BTCUSDT');
  const eth = state.data.summary.find(x => x.symbol === 'ETHUSDT');
  const last = state.data.series[state.data.series.length - 1];
  const combined = (val(last, 'BTCUSDT', 'wealth') + val(last, 'ETHUSDT', 'wealth')) / 2;
  $('#persona-score').textContent = combined.toFixed(1);
  $('#persona-delta').textContent = `↑ ${fmtPct(combined / 100 - 1)}`;
  lineSvg($('#persona-chart'), state.data.series.slice(-120), ['btcusdt_wealth', 'ethusdt_wealth'], false);
  $('#risk-bands').innerHTML = [btc, eth].map((row, i) => `<div class="risk-band"><span>${row.symbol.replace('USDT','')}</span><div class="risk-track ${i ? 'gold' : ''}"><i style="width:${Math.min(100, row.annualized_volatility * 100)}%"></i></div><b>${fmtPct(row.annualized_volatility)}</b></div>`).join('');
  $('#signal-bars').innerHTML = [btc, eth].map((row, i) => `<div class="signal-row"><span>${row.symbol.replace('USDT','')}</span><div class="signal-bar ${i ? 'eth' : ''}" style="width:${Math.min(100, Math.max(18, row.positive_days_pct * 100))}%"></div><b>${fmtPct(row.positive_days_pct)}</b></div>`).join('');
  $('#score-table').innerHTML = `<div class="score-row header"><span>Asset</span><span>CAGR</span><span>Vol.</span><span>Drawdown</span></div>${[btc, eth].map(row => `<div class="score-row"><b>${row.symbol.replace('USDT','')}</b><b class="green">${fmtPct(row.cagr)}</b><span>${fmtPct(row.annualized_volatility)}</span><span class="pink">${fmtPct(row.max_drawdown)}</span></div>`).join('')}`;
  const avgVol = (btc.annualized_volatility + eth.annualized_volatility) / 2;
  $('#recommendations').innerHTML = `<div class="reco"><span class="reco-icon">↗</span><div><b>Keep the cycle in context</b><p>Historical CAGR is high, but both assets experienced deep drawdowns.</p></div></div><div class="reco"><span class="reco-icon">≈</span><div><b>Watch dispersion</b><p>ETH annualized volatility is ${fmtPct(eth.annualized_volatility / btc.annualized_volatility - 1)} above BTC in this sample.</p></div></div><div class="reco"><span class="reco-icon">◌</span><div><b>Signal confidence</b><p>Positive daily closes represent roughly ${fmtPct((btc.positive_days_pct + eth.positive_days_pct) / 2)} of observations.</p></div></div>`;
}

function setView(view) {
  state.view = view;
  $$('.view').forEach(el => el.classList.toggle('active', el.id === `view-${view}`));
  $$('.nav-item,.mobile-nav button').forEach(el => el.classList.toggle('active', el.dataset.view === view));
  const titles = { overview: ['Performance overview', 'Une lecture claire des cycles BTC et ETH, sur les données Spot quotidiennes.'], momentum: ['Momentum', 'Les régimes mensuels qui structurent les accélérations et les ralentissements.'], persona: ['Market persona', 'Un résumé comportemental construit à partir des observations du marché.'], about: ['Project info', 'Méthode, source et limites du projet 10.'] };
  $('#page-title').textContent = titles[view][0]; $('#page-subtitle').textContent = titles[view][1];
  if (view === 'overview') updateOverview(); if (view === 'momentum') updateMomentum(); if (view === 'persona') updatePersona();
}

function bindEvents() {
  $$('[data-view]').forEach(el => el.addEventListener('click', (event) => { event.preventDefault(); setView(el.dataset.view); }));
  $$('#year-filter button').forEach(btn => btn.addEventListener('click', () => { state.year = btn.dataset.year; $$('#year-filter button').forEach(x => x.classList.toggle('selected', x === btn)); updateOverview(); updateMomentum(); }));
  $$('#currency-filter button').forEach(btn => btn.addEventListener('click', () => { state.currency = btn.dataset.currency; $$('#currency-filter button').forEach(x => x.classList.toggle('selected', x === btn)); updateOverview(); updateMomentum(); }));
  $$('[data-chart]').forEach(btn => btn.addEventListener('click', () => { state.chart = btn.dataset.chart; $$('[data-chart]').forEach(x => x.classList.toggle('active', x === btn)); updateOverview(); }));
  $$('[data-metric]').forEach(btn => btn.addEventListener('click', () => { state.metric = btn.dataset.metric; $$('[data-metric]').forEach(x => x.classList.toggle('active', x === btn)); drawMonthly(); }));
  $$('[data-asset]').forEach(btn => btn.addEventListener('click', () => { state.asset = btn.dataset.asset; $$('[data-asset]').forEach(x => x.classList.toggle('active', x === btn)); updateMomentum(); }));
  $('#portfolio-link').addEventListener('click', (event) => { event.preventDefault(); setView('about'); });
}

fetch('../../results/dashboard_data.json').then(response => response.json()).then(data => {
  state.data = data;
  $('#updated').textContent = `through ${data.last_updated}`;
  $('#footer-date').textContent = data.last_updated;
  bindEvents(); updateOverview(); updateMomentum(); updatePersona();
}).catch(error => { console.error(error); $('#updated').textContent = 'data unavailable'; });
