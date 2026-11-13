const DATA_FILES = [
  'fact_clients', 'portfolio_kpis', 'risk_band_summary', 'default_by_segment',
  'default_rate_by_pay0', 'delinquency_transition', 'model_metrics',
  'decile_lift', 'calibration_bins', 'recommendations', 'expected_loss_sensitivity',
  'dim_age_band', 'dim_education', 'dim_limit_band', 'dim_marriage', 'dim_pay_status', 'dim_risk_band'
];

const validPages = ['overview', 'segments', 'payments', 'scoring'];
const state = { page: validPages.includes(location.hash.slice(1)) ? location.hash.slice(1) : 'overview', partition: 'all', risk: 'all', limit: 'all', pay: 'all' };
const data = {};
const els = {
  dashboard: document.querySelector('#dashboard'),
  title: document.querySelector('#pageTitle'),
  kicker: document.querySelector('#pageKicker'),
  description: document.querySelector('#pageDescription'),
  summary: document.querySelector('#filterSummary'),
  warning: document.querySelector('#filterWarning'),
  sidebar: document.querySelector('#sidebar'),
  toast: document.querySelector('#toast')
};

function parseCSV(text) {
  const rows = [];
  let row = [], cell = '', quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i], next = text[i + 1];
    if (c === '"' && quoted && next === '"') { cell += '"'; i++; continue; }
    if (c === '"') { quoted = !quoted; continue; }
    if (c === ',' && !quoted) { row.push(cell); cell = ''; continue; }
    if ((c === '\n' || c === '\r') && !quoted) {
      if (c === '\r' && next === '\n') i++;
      row.push(cell); cell = '';
      if (row.some(v => v !== '')) rows.push(row);
      row = []; continue;
    }
    cell += c;
  }
  if (cell.length || row.length) { row.push(cell); if (row.some(v => v !== '')) rows.push(row); }
  if (!rows.length) return [];
  const headers = rows[0].map(v => v.trim());
  return rows.slice(1).map(values => Object.fromEntries(headers.map((h, i) => [h, values[i] ?? ''])));
}

function coerceRows(rows) {
  return rows.map(row => Object.fromEntries(Object.entries(row).map(([k, v]) => {
    if (v === '') return [k, null];
    const n = Number(v);
    return [k, Number.isFinite(n) && /^-?\d+(\.\d+)?([eE][+-]?\d+)?$/.test(String(v).trim()) ? n : v];
  })));
}
async function loadData() {
  await Promise.all(DATA_FILES.map(async name => {
    const response = await fetch(`data/${name}.csv`);
    if (!response.ok) throw new Error(`Impossible de charger ${name}.csv`);
    data[name] = coerceRows(parseCSV(await response.text()));
  }));
  data.fact = data.fact_clients;
}
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
const sum = (rows, key) => rows.reduce((a, r) => a + (Number(r[key]) || 0), 0);
const average = (rows, key) => rows.length ? sum(rows, key) / rows.length : 0;
const rate = (rows, key = 'default_next_month') => rows.length ? sum(rows, key) / rows.length : 0;
const money = n => { n = Number(n) || 0; const abs = Math.abs(n); if (abs >= 1e9) return `NT$ ${(n/1e9).toFixed(2)} Md`; if (abs >= 1e6) return `NT$ ${(n/1e6).toFixed(1)} M`; if (abs >= 1e3) return `NT$ ${Math.round(n/1e3).toLocaleString('fr-FR')} k`; return `NT$ ${Math.round(n).toLocaleString('fr-FR')}`; };
const moneyShort = n => { n = Number(n) || 0; const abs = Math.abs(n); if (abs >= 1e9) return `${(n/1e9).toFixed(1)} Md`; if (abs >= 1e6) return `${(n/1e6).toFixed(1)} M`; if (abs >= 1e3) return `${Math.round(n/1e3)} k`; return Math.round(n).toLocaleString('fr-FR'); };
const pct = n => `${(Number(n || 0) * 100).toFixed(1).replace('.', ',')} %`;
const pct0 = n => `${Math.round(Number(n || 0) * 100)} %`;
const integer = n => Math.round(Number(n) || 0).toLocaleString('fr-FR');
const escLabel = s => esc(String(s).replace('Statut pay_0', '').trim());

const lookup = (name, key, value, label) => { const found = (data[name] || []).find(r => String(r[key]) === String(value)); return found?.[label] ?? value; };
const riskLabel = key => lookup('dim_risk_band', 'risk_band_key', key, 'risk_band_label');
const payLabel = code => lookup('dim_pay_status', 'pay_code', code, 'pay_status_label');
const pageMeta = {
  overview: ['SYNTHÈSE DU PORTEFEUILLE', 'Vue d’ensemble', 'La cohorte présente une lecture claire de l’exposition, de l’utilisation et du défaut à horizon un mois.'],
  segments: ['LECTURE DES PROFILS', 'Segments à risque', 'Les taux observés sont accompagnés des effectifs et de l’exposition pour éviter toute lecture isolée.'],
  payments: ['HISTORIQUE DE PAIEMENT', 'Paiements & retards', 'Les retards récents sont associés à un taux de défaut supérieur à la moyenne de cohorte.'],
  scoring: ['PERFORMANCE DU MODÈLE', 'Scoring & actions', 'Les métriques de score sont évaluées hors échantillon sur la partition Test.']
};

function filteredFacts() {
  return data.fact.filter(r =>
    (state.partition === 'all' || r.model_partition === state.partition) &&
    (state.risk === 'all' || String(r.risk_band_key) === state.risk) &&
    (state.limit === 'all' || r.limit_band === state.limit) &&
    (state.pay === 'all' || String(r.pay_0) === state.pay)
  );
}
function activeFilterText() {
  const bits = [];
  if (state.partition !== 'all') bits.push(state.partition === 'Test' ? 'Test' : 'Train');
  if (state.risk !== 'all') bits.push(riskLabel(state.risk));
  if (state.limit !== 'all') bits.push(state.limit);
  if (state.pay !== 'all') bits.push(`pay_0 ${state.pay}`);
  return bits.length ? bits.join(' · ') : 'Tous les clients';
}
function kpiCard(icon, label, value, foot, accent = '') { return `<article class="kpi-card ${accent}"><div class="kpi-icon">${icon}</div><span class="kpi-label">${label}</span><strong class="kpi-value">${value}</strong><span class="kpi-foot">${foot}</span></article>`; }
function panel(title, subtitle, body, tag = '') { return `<section class="panel"><div class="panel-head"><div><h3>${title}</h3><p>${subtitle}</p></div>${tag ? `<span class="panel-tag">${tag}</span>` : ''}</div>${body}</section>`; }
function empty(message = 'Aucune ligne ne correspond aux filtres actifs.') { return `<div class="empty-state">${message}</div>`; }

function chartFrame(content, height = 230) { return `<div class="chart-box" style="height:${height}px"><svg class="svg-chart" viewBox="0 0 720 ${height}" preserveAspectRatio="none" aria-label="Graphique de données">${content}</svg></div>`; }
function barChart(items, { color = '#6f55e8', format = integer, max = null, horizontal = false } = {}) {
  if (!items.length) return '';
  const W = 720, H = horizontal ? Math.max(190, items.length * 34 + 28) : 230, left = horizontal ? 130 : 36, right = 16, top = 12, bottom = horizontal ? 18 : 45;
  const maxValue = max ?? Math.max(...items.map(i => Number(i.value) || 0), 0.01);
  let shapes = '';
  if (horizontal) {
    const innerW = W - left - right, rowH = (H - top - bottom) / items.length;
    items.forEach((item, i) => { const y = top + i * rowH + 5, width = Math.max(2, (Number(item.value) / maxValue) * innerW); shapes += `<text x="${left-9}" y="${y+15}" class="axis-label" text-anchor="end">${esc(item.label)}</text><rect class="bar ${item.class || ''}" x="${left}" y="${y}" width="${width}" height="${Math.min(21,rowH-9)}" rx="4" fill="${item.color || color}"/><text x="${Math.min(W-right-2,left+width+7)}" y="${y+15}" class="axis-label">${esc(format(item.value))}</text>`; });
  } else {
    const innerW = W - left - right, innerH = H - top - bottom, barW = Math.min(72, innerW / items.length * .57), step = innerW / items.length;
    [0,.5,1].forEach(t => { const y = top + innerH * (1-t); shapes += `<line x1="${left}" x2="${W-right}" y1="${y}" y2="${y}" class="chart-grid"/><text x="${left-7}" y="${y+3}" text-anchor="end" class="axis-label">${esc(format(maxValue*t))}</text>`; });
    items.forEach((item, i) => { const value = Number(item.value)||0, h = (value/maxValue)*innerH, x = left + i*step + (step-barW)/2, y = top+innerH-h; shapes += `<rect class="bar ${item.class||''}" x="${x}" y="${y}" width="${barW}" height="${Math.max(h,1)}" rx="5" fill="${item.color||color}"/><text x="${x+barW/2}" y="${H-25}" text-anchor="middle" class="axis-label">${esc(item.label)}</text><text x="${x+barW/2}" y="${Math.max(10,y-6)}" text-anchor="middle" class="axis-label" fill="#3b4665">${esc(format(value))}</text>`; });
  }
  return chartFrame(shapes, H);
}
function lineChart(items, { valueKeys = ['value'], labels = [], colors = ['#6f55e8'], max = null, format = pct } = {}) {
  if (!items.length) return '';
  const W=720,H=230,left=38,right=15,top=15,bottom=42, innerW=W-left-right,innerH=H-top-bottom;
  const values = items.flatMap(i => valueKeys.map(k => Number(i[k])||0)); const maxValue = max ?? Math.max(...values, .01); let out='';
  [0,.5,1].forEach(t=>{ const y=top+innerH*(1-t); out+=`<line x1="${left}" x2="${W-right}" y1="${y}" y2="${y}" class="chart-grid"/><text x="${left-7}" y="${y+3}" text-anchor="end" class="axis-label">${esc(format(maxValue*t))}</text>`; });
  valueKeys.forEach((key, series) => { const pts=items.map((item,i)=>{const x=left+(items.length===1?innerW/2:i*innerW/(items.length-1)); const y=top+innerH-(Number(item[key])||0)/maxValue*innerH; return [x,y];}); out += `<polyline points="${pts.map(p=>p.join(',')).join(' ')}" fill="none" stroke="${colors[series]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`; pts.forEach(([x,y],i)=>{ out+=`<circle cx="${x}" cy="${y}" r="4" fill="#fff" stroke="${colors[series]}" stroke-width="2"/><text x="${x}" y="${H-23}" text-anchor="middle" class="axis-label">${esc(labels[i] ?? items[i].label ?? '')}</text>`; }); });
  return chartFrame(out,H);
}
function table(headers, rows) { return `<div class="table-wrap"><table class="data-table"><thead><tr>${headers.map(h=>`<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`; }
function rateBadge(value) { const cls = value >= .4 ? 'rate-high' : value >= .22 ? 'rate-mid' : 'rate-low'; return `<span class="rate-badge ${cls}">${pct(value)}</span>`; }
function aggregate(rows, key, labelFn = x => x) {
  const map = new Map();
  rows.forEach(r => { const keyValue = key(r), label = labelFn(keyValue); if (!map.has(String(keyValue))) map.set(String(keyValue), { key:keyValue, label, rows:[] }); map.get(String(keyValue)).rows.push(r); });
  return [...map.values()].map(g => ({ label:g.label, key:g.key, customers:g.rows.length, defaultRate:rate(g.rows), defaults:sum(g.rows,'default_next_month'), limit:sum(g.rows,'limit_bal'), exposure:sum(g.rows.filter(r=>Number(r.default_next_month)===1),'limit_bal'), utilization:average(g.rows,'utilization'), expectedLoss:g.rows.filter(r=>r.model_partition==='Test').reduce((a,r)=>a+(Number(r.predicted_pd)||0)*Math.max(0,Number(r.bill_amt1)||0)*0.45,0) }));
}
function pageOverview(rows) {
  if (!rows.length) return empty();
  const totalLimit=sum(rows,'limit_bal'), defaulterExposure=sum(rows.filter(r=>Number(r.default_next_month)===1),'limit_bal'), defaultRate=rate(rows), util=average(rows,'utilization');
  const testRows=rows.filter(r=>r.model_partition==='Test'), highShare=testRows.length?testRows.filter(r=>Number(r.risk_band_key)>=3).length/testRows.length:0;
  const expectedLoss=testRows.reduce((a,r)=>a+(Number(r.predicted_pd)||0)*Math.max(0,Number(r.bill_amt1)||0)*.45,0);
  const limits=aggregate(rows,r=>r.limit_band,x=>x).sort((a,b)=>String(a.key).localeCompare(String(b.key)));
  const risk=aggregate(rows,r=>r.risk_band_key,x=>riskLabel(x)).sort((a,b)=>Number(a.key)-Number(b.key));
  const age=aggregate(rows,r=>r.age_band,x=>x).sort((a,b)=>['<25','25-34','35-44','45-54','55+'].indexOf(a.label)-['<25','25-34','35-44','45-54','55+'].indexOf(b.label));
  const pay=aggregate(rows,r=>r.pay_0,x=>String(x)).sort((a,b)=>Number(a.key)-Number(b.key));
  const education=aggregate(rows,r=>r.education,x=>({1:'Études supérieures',2:'Université',3:'Lycée',4:'Autre'})[x]||`Code ${x}`).sort((a,b)=>b.defaultRate-a.defaultRate);
  const utilization=aggregate(rows,r=>r.utilization_band,x=>x).sort((a,b)=>['<30 %','30-<60 %','60-100 %','>100 %'].indexOf(a.label)-['<30 %','30-<60 %','60-100 %','>100 %'].indexOf(b.label));
  const kpis=`<div class="crm-kpis">${kpiCard('◉','Clients',integer(rows.length),'Cohorte filtrée')}${kpiCard('↯','Taux de défaut',pct(defaultRate),'Mois suivant','accent-red')}${kpiCard('▣','Limite totale',money(totalLimit),'Crédit autorisé','accent-cyan')}${kpiCard('◒','Exposition défaillants',money(defaulterExposure),`${pct(totalLimit?defaulterExposure/totalLimit:0)} des limites`,'accent-orange')}${kpiCard('◌','Utilisation moyenne',pct(util),'Facture / limite','accent-green')}${kpiCard('◎','Risque élevé Test',pct(highShare),'Bandes Élevé + Très élevé','accent-orange')}${kpiCard('◈','Perte attendue',money(expectedLoss),'LGD hypothétique 45 %','accent-red')}</div>`;
  const limitsChart=barChart(limits.map(x=>({label:x.label,value:x.defaultRate,class:x.defaultRate>.3?'red':''})),{format:pct,max:.35});
  const riskChart=barChart(risk.map(x=>({label:x.label,value:x.customers,class:Number(x.key)>=4?'red':Number(x.key)>=3?'orange':''})),{format:integer,color:'#416b8d',horizontal:true});
  const ageChart=barChart(age.map(x=>({label:x.label,value:x.defaultRate,class:x.defaultRate>.25?'red':''})),{format:pct,max:.35});
  const payChart=barChart(pay.slice(-8).map(x=>({label:String(x.key),value:x.defaultRate,class:x.defaultRate>.4?'red':x.defaultRate>.25?'orange':''})),{format:pct,max:.85});
  const educationChart=barChart(education.map(x=>({label:x.label.length>13?x.label.slice(0,12)+'…':x.label,value:x.defaultRate,class:x.defaultRate>.25?'red':''})),{format:pct,max:Math.max(.35,...education.map(x=>x.defaultRate)),horizontal:true});
  const utilizationChart=barChart(utilization.map(x=>({label:x.label,value:x.defaultRate,class:x.defaultRate>.3?'red':''})),{format:pct,max:.55});
  const exposureChart=barChart(risk.map(x=>({label:x.label,value:x.exposure,class:Number(x.key)>=4?'red':''})),{format:moneyShort,color:'#5d84a1',horizontal:true});
  const topAction=(data.recommendations||[])[0];
  const action=topAction?`<div class="crm-action"><span class="action-id">${esc(topAction.recommendation_id)}</span><strong>${esc(topAction.trigger)}</strong><p>${esc(topAction.action)}</p></div>`:empty('Recommandation indisponible.');
  const mini=(label,value,delta,accent='violet')=>`<div class="bank-mini ${accent}"><span>${label}</span><strong>${value}</strong><small>${delta}</small></div>`;
  const riskRows=risk.map(x=>`<div class="bank-risk-row"><span>${esc(x.label)}</span><b>${moneyShort(x.exposure)}</b><i><em style="width:${Math.max(8,Math.min(100,(x.exposure/Math.max(...risk.map(y=>y.exposure)))*100))}%"></em></i></div>`).join('');
  return `<div class="banking-dashboard"><div class="banking-topbar"><div class="banking-title"><span>◈ BANKING ANALYSIS</span><strong>Credit risk · Overview</strong></div><div class="banking-switches"><button>NT$</button><button class="selected">2005</button><button id="crmReset">↶ Reset</button></div></div><div class="banking-body"><aside class="banking-sidebar"><div class="bank-logo">CR</div><div class="bank-section">Navigation</div><button class="bank-nav active">◉ <span>Overview</span></button><button class="bank-nav">♙ <span>Segments</span></button><button class="bank-nav">⌕ <span>Momentum</span></button><div class="bank-section connect">Connect</div><button class="bank-nav muted">▣ <span>Portfolio</span></button><button class="bank-nav muted">▤ <span>Project info</span></button><div class="bank-signature">◈<span>RISK ANALYTICS</span></div></aside><main class="banking-main"><div class="banking-hero"><div class="bank-card bank-large-card"><div class="bank-card-head"><span>Total credit limit</span><b>↗ 0.82 % vs PY</b></div><strong>${money(totalLimit)}</strong><small>Δ · ${moneyShort(defaulterExposure)} exposed in default</small>${limitsChart}</div><div class="bank-large-stat"><span>Total portfolio risk</span><strong>${pct(defaultRate)}</strong><small>Default next month</small><div class="bank-ring"><i></i></div></div><div class="bank-large-stat green"><span>Expected loss</span><strong>${money(expectedLoss)}</strong><small>LGD assumption 45 %</small><div class="bank-ring"><i></i></div></div></div><div class="banking-middle"><div class="banking-mini-grid">${mini('Clients',integer(rows.length),'Full cohort','violet')}${mini('Default rate',pct(defaultRate),'Next month','red')}${mini('Avg utilization',pct(util),'Bill / limit','violet')}${mini('High-risk Test',pct(highShare),'Risk bands 3 + 4','red')}${mini('Defaulter exposure',money(defaulterExposure),'Of total limit','violet')}${mini('Test expected loss',money(expectedLoss),'LGD 45 %','green')}</div><div class="bank-card bank-chart-card"><div class="bank-card-head"><span>Risk band pipeline</span><b>Clients</b></div>${riskChart}</div><div class="bank-card bank-chart-card"><div class="bank-card-head"><span>Default status momentum</span><b>pay_0</b></div>${payChart}</div></div><aside class="banking-right"><div class="bank-map-card"><div class="bank-card-head"><span>Risk exposure</span><b>NT$</b></div><div class="bank-orbit"><span></span><i></i><em></em><small>RISK<br/>BANDS</small></div><div class="bank-risk-list">${riskRows}</div></div><div class="bank-card bank-bottom-card"><div class="bank-card-head"><span>Recorded clients</span><b>Test 30 %</b></div><strong>${integer(testRows.length)}</strong><small>↗ ${pct(highShare)} high risk · ${money(expectedLoss)} expected loss</small><div class="bank-segment-bars"><i style="width:${Math.round((risk[0]?.customers||0)/rows.length*100)}%"></i><i style="width:${Math.round((risk[1]?.customers||0)/rows.length*100)}%"></i><i style="width:${Math.round((risk[2]?.customers||0)/rows.length*100)}%"></i><i style="width:${Math.round((risk[3]?.customers||0)/rows.length*100)}%"></i></div></div></aside></main></div><div class="banking-footnote">Projet 4 · Cohorte historique taïwanaise · Données réelles · Les dimensions âge, éducation et mariage restent descriptives et ne sont pas des règles de décision.</div></div>`;
}
function pageSegments(rows) {
  if (!rows.length) return empty();
  const age = aggregate(rows,r=>r.age_band,x=>x).sort((a,b)=>['<25','25-34','35-44','45-54','55+'].indexOf(a.label)-['<25','25-34','35-44','45-54','55+'].indexOf(b.label));
  const eduLabels = {1:'Études supérieures',2:'Université',3:'Lycée',4:'Autre ou inconnu'};
  const education = aggregate(rows,r=>r.education,r=>eduLabels[r]||`Code ${r}`).sort((a,b)=>b.defaultRate-a.defaultRate);
  const utilization = aggregate(rows,r=>r.utilization_band,x=>x).sort((a,b)=>['<30 %','30-<60 %','60-100 %','>100 %'].indexOf(a.label)-['<30 %','30-<60 %','60-100 %','>100 %'].indexOf(b.label));
  const marriageLabels = {1:'Marié',2:'Célibataire',3:'Autre / inconnu'};
  const marriage = aggregate(rows,r=>r.marriage,r=>marriageLabels[r]||`Code ${r}`);
  const ageChart=barChart(age.map(x=>({label:x.label,value:x.defaultRate,class:x.defaultRate>.25?'red':''})),{format:pct,max:.35});
  const eduChart=barChart(education.map(x=>({label:x.label.length>16?x.label.slice(0,15)+'…':x.label,value:x.defaultRate,class:x.defaultRate>.25?'red':''})),{format:pct,max:Math.max(.35,...education.map(x=>x.defaultRate)),horizontal:true});
  const utilChart=barChart(utilization.map(x=>({label:x.label,value:x.defaultRate,class:x.defaultRate>.3?'red':''})),{format:pct,max:Math.max(.55,...utilization.map(x=>x.defaultRate))});
  const rowsTable = [...age,...utilization].sort((a,b)=>b.defaultRate-a.defaultRate).slice(0,7).map(x=>[`<strong>${esc(x.label)}</strong>`,integer(x.customers),rateBadge(x.defaultRate),money(x.exposure)]);
  return `<div class="grid two-col">${panel('Défaut par bande d’âge','Dimension descriptive · taux et effectif restent visibles',ageChart,'DESCRIPTIF')}${panel('Défaut par niveau d’éducation','Dimension descriptive · pas de règle automatique',eduChart,'DESCRIPTIF')}</div><div class="grid two-col">${panel('Défaut selon l’utilisation','Utilisation calculée sur la facture et la limite',utilChart,'UTILISATION')}${panel('Segments prioritaires à regarder','Taux, volume et exposition associés',table(['Segment','Clients','Taux','Exposition'],rowsTable),'LECTURE RAPIDE')}</div><div class="callout"><strong>Garde-fou métier.</strong> Sexe, âge et état matrimonial sont disponibles pour l’analyse descriptive et la revue d’équité uniquement. Ils sont exclus du score de risque; aucune décision individuelle ne doit être fondée sur eux.</div>`;
}
function paymentBucket(code) { const n=Number(code); return n>=3?'3+':String(n); }
function pagePayments(rows) {
  if (!rows.length) return empty();
  const pay = aggregate(rows,r=>r.pay_0,c=>payLabel(c)).sort((a,b)=>Number(a.key)-Number(b.key));
  const months = aggregate(rows,r=>r.n_delays_6m,x=>x).sort((a,b)=>Number(a.key)-Number(b.key));
  const transitions = new Map(); rows.forEach(r=>{ const from=paymentBucket(r.pay_2), to=paymentBucket(r.pay_0), key=`${from}|${to}`; if(!transitions.has(key)) transitions.set(key,{from,to,count:0,defaults:0}); const v=transitions.get(key); v.count++; v.defaults+=Number(r.default_next_month)||0; });
  const codes=['-2','-1','0','1','2','3+']; const matrix=[...new Set([...transitions.values()].flatMap(x=>[x.from,x.to]))].sort((a,b)=>Number(a)-Number(b));
  const matrixHtml=`<div class="heat-subtitle">Taux de défaut dans chaque transition · PAY_2 en ligne → PAY_0 en colonne</div><div class="heatmap" style="grid-template-columns:78px repeat(${matrix.length},1fr)"><div></div>${matrix.map(c=>`<div class="heat-head" style="text-align:center">${esc(c)}</div>`).join('')}${matrix.map(from=>`<div class="heat-side">${esc(from)}</div>${matrix.map(to=>{const v=transitions.get(`${from}|${to}`);const val=v?v.defaults/v.count:null;const alpha=val==null?0:Math.min(.92,.18+val*1.05);return `<div class="heat-cell ${val==null?'empty':''}" style="${val==null?'':'background:rgba(105,71,232,'+alpha+')'}">${val==null?'—':pct0(val)}</div>`}).join('')}`).join('')}</div>`;
  const payChart=barChart(pay.slice(-8).map(x=>({label:String(x.key),value:x.defaultRate,class:x.defaultRate>.4?'red':x.defaultRate>.25?'orange':''})),{format:pct,max:.85});
  const delayChart=barChart(months.slice(0,10).map(x=>({label:String(x.label),value:x.customers,class:x.defaultRate>.4?'red':''})),{format:integer,color:'#27b8d8'});
  const payRows=pay.slice().sort((a,b)=>b.defaultRate-a.defaultRate).slice(0,7).map(x=>[`<strong>${esc(String(x.key))}</strong><br><span style="font-size:8px;color:#9aa4b8">${esc(String(payLabel(x.key)).slice(0,24))}</span>`,integer(x.customers),rateBadge(x.defaultRate),pct(x.utilization)]);
  return `<div class="grid two-col">${panel('Transition PAY_2 → PAY_0','Lecture des changements de statut sur l’historique disponible',matrixHtml,'MATRICE')}${panel('Défaut par statut récent','Le statut pay_0 porte le signal le plus récent',payChart,'PAY_0')}</div><div class="grid two-col">${panel('Nombre de mois en retard','Nombre de mois avec un retard observé sur six relevés',delayChart,'6 RELEVÉS')}${panel('Statuts à surveiller','Effectif, taux et utilisation moyenne',table(['Statut','Clients','Taux','Utilisation'],payRows),'TRIAGE')}</div><div class="callout"><strong>À lire avec prudence.</strong> Les codes -2 (« aucun achat déclaré ») et 0 (« crédit renouvelable ») sont des hypothèses documentées par le projet, non des libellés source exhaustifs.</div>`;
}
function pageScoring(rows) {
  const metric = data.model_metrics[0] || {};
  const testRows = rows.filter(r=>r.model_partition==='Test');
  const base = data.fact.filter(r=>r.model_partition==='Test');
  const metrics = `<div class="metric-grid"><div class="metric-chip"><span>ROC-AUC</span><strong>${Number(metric.roc_auc||0).toFixed(3)}</strong><small>Partition test</small></div><div class="metric-chip"><span>PR-AUC</span><strong>${Number(metric.pr_auc_average_precision||0).toFixed(3)}</strong><small>Average precision</small></div><div class="metric-chip"><span>KS</span><strong>${Number(metric.ks_statistic||0).toFixed(3)}</strong><small>Discrimination</small></div><div class="metric-chip"><span>Précision</span><strong>${pct(metric.precision_at_threshold)}</strong><small>Seuil ${metric.decision_threshold}</small></div><div class="metric-chip"><span>Rappel</span><strong>${pct(metric.recall_at_threshold)}</strong><small>Seuil ${metric.decision_threshold}</small></div></div>`;
  const lift = data.decile_lift || []; const calibration=data.calibration_bins || [];
  const liftChart = lineChart(lift,{valueKeys:['default_rate'],labels:lift.map(x=>`D${x.decile}`),colors:['#e85e70'],max:.7,format:pct});
  const calibChart = lineChart(calibration.map(x=>({label:`B${x.calibration_bin}`,observed_default_rate:x.observed_default_rate,mean_predicted_pd:x.mean_predicted_pd})),{valueKeys:['observed_default_rate','mean_predicted_pd'],labels:calibration.map(x=>`B${x.calibration_bin}`),colors:['#6f55e8','#27b8d8'],max:.7,format:pct});
  const riskGroups = aggregate(testRows,r=>r.risk_band_key,x=>riskLabel(x)).sort((a,b)=>Number(a.key)-Number(b.key));
  const riskChart = barChart(riskGroups.map(x=>({label:x.label,value:x.expectedLoss, class:Number(x.key)>=4?'red':Number(x.key)>=3?'orange':''})),{format:moneyShort,color:'#f1a35a',horizontal:true});
  const actions=(data.recommendations||[]).map(r=>`<article class="action-card"><header><span class="action-id">${esc(r.recommendation_id)}</span><span class="action-trigger">${esc(r.trigger)}</span></header><p>${esc(r.action)}</p><div class="action-meta"><span>${integer(r.cohort_customers)} clients</span><span>${pct(r.observed_default_rate)} défaut observé</span><span>${money(r.exposure_ntd)} exposition</span></div></article>`).join('');
  const currentNote = state.partition !== 'all' || state.risk !== 'all' || state.limit !== 'all' || state.pay !== 'all' ? `<div class="filter-warning">Les métriques ROC-AUC, PR-AUC, KS, précision, rappel, lift et calibration restent les artefacts officiels de la partition Test complète (${integer(base.length)} clients). Les graphiques d’exposition ci-dessous suivent les filtres actifs (${integer(testRows.length)} clients Test dans la sélection).</div>` : '';
  return `${metrics}${currentNote}<div class="grid two-col">${panel('Lift par décile','Taux de défaut observé sur la partition test',`${liftChart}<div class="chart-legend"><span><i class="legend-dot" style="background:#e85e70"></i>Taux de défaut</span><span>Le décile 1 concentre le risque le plus élevé</span></div>`,'TEST')}${panel('Calibration prévu / observé','Écart entre PD moyenne et défaut observé',`${calibChart}<div class="chart-legend"><span><i class="legend-dot" style="background:#6f55e8"></i>Observé</span><span><i class="legend-dot" style="background:#27b8d8"></i>PD moyenne</span></div>`,'TEST')}</div><div class="grid two-col">${panel('Perte attendue par bande de risque','PD × facture positive × LGD hypothétique 45 %',riskChart,'LGD 45 %')}${panel('Recommandations de triage','Pistes opérationnelles à valider par une équipe de crédit',actions || empty('Recommandations indisponibles.'),'PRUDENCE')}</div><div class="callout"><strong>Limites du score.</strong> La cohorte est historique, taïwanaise et datée de 2005. Sexe, mariage et âge sont exclus du modèle. La perte attendue est une sensibilité illustrative sous LGD 45 % et ne constitue ni une prévision comptable ni une estimation réglementaire.</div>`;
}
function render() {
  const rows=filteredFacts(); const meta=pageMeta[state.page]; els.kicker.textContent=meta[0]; els.title.textContent=meta[1]; els.description.textContent=meta[2]; els.summary.textContent=`${activeFilterText()} · ${integer(rows.length)} lignes`;
  document.querySelector('.content-wrap').classList.toggle('model-overview', state.page==='overview');
  els.warning.hidden = true;
  els.dashboard.innerHTML = state.page==='overview'?pageOverview(rows):state.page==='segments'?pageSegments(rows):state.page==='payments'?pagePayments(rows):pageScoring(rows);
  document.querySelector('#crmReset')?.addEventListener('click',()=>{Object.assign(state,{partition:'all',risk:'all',limit:'all',pay:'all'}); updateSelects(); render(); toast('Filtres réinitialisés');});
  if (state.page==='scoring' && (state.partition==='Train')) { els.warning.hidden=false; els.warning.textContent='La vue de scoring est évaluée sur Test. Le filtre Train sert uniquement à comparer le portefeuille ; les métriques de modèle restent celles de la partition Test.'; }
  document.querySelectorAll('.nav-item').forEach(btn=>btn.classList.toggle('active',btn.dataset.page===state.page));
  document.querySelectorAll('.top-nav-item').forEach(btn=>btn.classList.toggle('active',btn.dataset.page===state.page));
}
function updateSelects() {
  const paySelect=document.querySelector('#payFilter');
  paySelect.innerHTML='<option value="all">Tous</option>'+(data.dim_pay_status||[]).map(r=>`<option value="${r.pay_code}">${r.pay_code} · ${esc(String(r.pay_status_label).slice(0,27))}</option>`).join('');
  document.querySelector('#partitionFilter').value=state.partition; document.querySelector('#riskFilter').value=state.risk; document.querySelector('#limitFilter').value=state.limit; paySelect.value=state.pay;
}
function toast(message) { els.toast.textContent=message; els.toast.classList.add('show'); setTimeout(()=>els.toast.classList.remove('show'),2200); }
function setup() {
  document.querySelectorAll('.nav-item').forEach(btn=>btn.addEventListener('click',()=>{state.page=btn.dataset.page; history.replaceState(null,'',`#${state.page}`); render(); els.sidebar.classList.remove('open');}));
  document.querySelectorAll('.top-nav-item').forEach(btn=>btn.addEventListener('click',()=>{state.page=btn.dataset.page; history.replaceState(null,'',`#${state.page}`); render();}));
  const bind=(id,key)=>document.querySelector(`#${id}`).addEventListener('change',e=>{state[key]=e.target.value; render();});
  bind('partitionFilter','partition'); bind('riskFilter','risk'); bind('limitFilter','limit'); bind('payFilter','pay');
  document.querySelector('#resetBtn').addEventListener('click',()=>{Object.assign(state,{partition:'all',risk:'all',limit:'all',pay:'all'}); updateSelects(); render(); toast('Filtres réinitialisés');});
  document.querySelector('#menuBtn').addEventListener('click',()=>els.sidebar.classList.toggle('open'));
  const dialog=document.querySelector('#infoDialog'); document.querySelector('#infoBtn').addEventListener('click',()=>dialog.showModal()); document.querySelector('#dialogClose').addEventListener('click',()=>dialog.close());
}
async function main() {
  try { await loadData(); updateSelects(); setup(); render(); }
  catch(error) { console.error(error); els.dashboard.innerHTML=empty(`Les données du projet n’ont pas pu être chargées. ${esc(error.message)}`); }
}
main();
