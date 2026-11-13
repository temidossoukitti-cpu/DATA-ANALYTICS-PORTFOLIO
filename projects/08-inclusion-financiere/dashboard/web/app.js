const D = window.DASHBOARD_DATA;
const charts = {};
const $ = id => document.getElementById(id);
const short = value => String(value || 'Non précisé')
  .replace(' (excluding high income)','')
  .replace('High income','Revenu élevé')
  .replace('Upper middle income','Revenu intermédiaire supérieur')
  .replace('Lower middle income','Revenu intermédiaire inférieur')
  .replace('Low income','Faible revenu')
  .replace('World','Monde')
  .replace('North America','Amérique du Nord')
  .replace('Sub-Saharan Africa','Afrique subsaharienne')
  .replace('East Asia & Pacific','Asie de l’Est et Pacifique')
  .replace('Latin America & Caribbean','Amérique latine et Caraïbes')
  .replace('Middle East & North Africa','Moyen-Orient et Afrique du Nord')
  .replace('Europe & Central Asia','Europe et Asie centrale')
  .replace('South Asia','Asie du Sud');
const COUNTRY_LABELS = {'Algeria':'Algérie','United Arab Emirates':'Émirats arabes unis','West Bank and Gaza':'Cisjordanie et Gaza','Tunisia':'Tunisie','Nigeria':'Nigéria','Iraq':'Irak','Azerbaijan':'Azerbaïdjan','Viet Nam':'Vietnam','Lao PDR':'Laos','Mozambique':'Mozambique','El Salvador':'El Salvador','Panama':'Panama','Cameroon':'Cameroun','Romania':'Roumanie','Albania':'Albanie','Togo':'Togo','Pakistan':'Pakistan'};
const countryLabel = name => COUNTRY_LABELS[name] || name || 'Pays non précisé';
const pct = value => value === null || value === undefined || Number.isNaN(Number(value)) ? '—' : `${(Number(value) * 100).toLocaleString('fr-FR',{maximumFractionDigits:1})} %`;
const points = value => value === null || value === undefined || Number.isNaN(Number(value)) ? '—' : `${(Math.abs(Number(value)) * 100).toLocaleString('fr-FR',{minimumFractionDigits:1,maximumFractionDigits:1})} pts`;
const number = value => Number(value || 0).toLocaleString('fr-FR',{maximumFractionDigits:0});
const valueOf = (row,key) => row?.[key] === null || row?.[key] === undefined || row?.[key] === '' ? null : Number(row[key]);

function makeChart(id,type,labels,datasets,options={}) {
  const node = $(id);
  if (!node) return;
  if (charts[id]) charts[id].destroy();
  const horizontal = options.indexAxis === 'y';
  charts[id] = new Chart(node,{type,data:{labels,datasets},options:{
    responsive:true,maintainAspectRatio:false,
    plugins:{legend:{position:'bottom',labels:{font:{size:10},usePointStyle:true,boxWidth:8}},tooltip:{callbacks:{label:ctx=>`${ctx.dataset.label}: ${Number(ctx.parsed[horizontal?'x':'y']).toLocaleString('fr-FR',{maximumFractionDigits:1})}${options.pointAxis?' pts':options.percentAxis?' %':''}`}}},
    scales:{
      y:{beginAtZero:true,ticks:{font:{size:9},callback:v=>options.pointAxis&&!horizontal?`${v} pts`:options.percentAxis?`${Math.round(v*100)} %`:v},grid:{color:'#edf1f5'}},
      x:{beginAtZero:horizontal,ticks:{font:{size:9},maxRotation:35,callback:v=>horizontal&&options.pointAxis?`${v} pts`:options.percentAxis?`${Math.round(v*100)} %`:v},grid:{color:horizontal?'#edf1f5':'transparent'}}
    },
    ...options
  }});
}
function cards(target,items) {
  const node = $(target);
  if (!node) return;
  const colors=['#db2777','#7c3aed','#0f766e','#06b6d4','#2563eb'];
  node.innerHTML=items.map((item,index)=>`<article class="kpi" style="--accent:${colors[index%colors.length]}"><label>${item[0]}</label><strong>${item[1]}</strong><small>${item[2]||''}</small></article>`).join('');
}
function makeTable(id,headers,rows) {
  const node=$(id); if(!node)return;
  node.innerHTML='<thead><tr>'+headers.map(h=>`<th>${h}</th>`).join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(x=>`<td>${x ?? '—'}</td>`).join('')+'</tr>').join('')+'</tbody>';
}
function gapRows(rows,key,kind,limit=10) {
  return rows.filter(row=>valueOf(row,key)!==null).map(row=>{
    const signed=valueOf(row,key);
    const direction=kind==='gender'?(signed>=0?'Hommes > femmes':'Femmes > hommes'):(signed>=0?'Riches > pauvres':'Pauvres > riches');
    return {name:countryLabel(row.countrynewwb||row.codewb),region:row.regionwb24_hi||'Non précisée',signed,abs:Math.abs(signed),direction};
  }).sort((a,b)=>b.abs-a.abs).slice(0,limit);
}
function regionalAverages(rows,key) {
  const grouped=new Map();
  for(const row of rows){
    const value=valueOf(row,key), region=row.regionwb24_hi;
    if(value===null||!region)continue;
    if(!grouped.has(region))grouped.set(region,[]);
    grouped.get(region).push(Math.abs(value)*100);
  }
  return [...grouped.entries()].map(([region,values])=>({region,average:values.reduce((a,b)=>a+b,0)/values.length,countries:values.length}));
}
function renderGaps() {
  const genderKey='account_t_d_men_minus_women';
  const incomeKey='account_t_d_richest_minus_poorest';
  const gender=gapRows(D.genderGaps||[],genderKey,'gender',10);
  const income=gapRows(D.incomeGaps||[],incomeKey,'income',10);
  const allGender=gapRows(D.genderGaps||[],genderKey,'gender',10000);
  const allIncome=gapRows(D.incomeGaps||[],incomeKey,'income',10000);
  const genderCodes=new Set((D.genderGaps||[]).filter(r=>valueOf(r,genderKey)!==null).map(r=>r.codewb));
  const incomeCodes=new Set((D.incomeGaps||[]).filter(r=>valueOf(r,incomeKey)!==null).map(r=>r.codewb));
  const both=[...genderCodes].filter(code=>incomeCodes.has(code)).length;
  const topGender=allGender[0], topIncome=allIncome[0];
  cards('gapKpis',[
    ['Plus grand écart femmes–hommes',topGender?points(topGender.signed):'—',topGender?`${topGender.name} · ${topGender.direction}`:'Aucune estimation comparable'],
    ['Plus grand écart riches–pauvres',topIncome?points(topIncome.signed):'—',topIncome?`${topIncome.name} · ${topIncome.direction}`:'Aucune estimation comparable'],
    ['Pays comparables sur les deux écarts',number(both),'Estimations pays disponibles en 2024']
  ]);
  const genderOpts={indexAxis:'y',pointAxis:true,plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>`${points(gender[ctx.dataIndex].signed)} · ${gender[ctx.dataIndex].direction}`}}},scales:{x:{beginAtZero:true,ticks:{font:{size:9},callback:v=>`${v} pts`},grid:{color:'#edf1f5'}},y:{ticks:{font:{size:9}},grid:{display:false}}}};
  const incomeOpts={...genderOpts,plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>`${points(income[ctx.dataIndex].signed)} · ${income[ctx.dataIndex].direction}`}}}};
  makeChart('genderChart','bar',gender.map(x=>`${x.name} · ${x.direction}`),[{label:'Écart absolu',data:gender.map(x=>x.abs*100),backgroundColor:'#db2777',borderRadius:4}],genderOpts);
  makeChart('incomeGapChart','bar',income.map(x=>`${x.name} · ${x.direction}`),[{label:'Écart absolu',data:income.map(x=>x.abs*100),backgroundColor:'#7c3aed',borderRadius:4}],incomeOpts);
  const rg=regionalAverages(D.genderGaps||[],genderKey), ri=regionalAverages(D.incomeGaps||[],incomeKey);
  const regions=[...new Set([...rg,...ri].map(x=>x.region))];
  const byRegion=(arr,region)=>arr.find(x=>x.region===region)?.average??null;
  makeChart('regionalGapChart','bar',regions.map(short),[
    {label:'Femmes–hommes',data:regions.map(r=>byRegion(rg,r)),backgroundColor:'#db2777',borderRadius:3},
    {label:'Riches–pauvres',data:regions.map(r=>byRegion(ri,r)),backgroundColor:'#7c3aed',borderRadius:3}
  ],{pointAxis:true,scales:{y:{beginAtZero:true,ticks:{font:{size:9},callback:v=>`${v} pts`},grid:{color:'#edf1f5'}},x:{ticks:{font:{size:9},maxRotation:35},grid:{display:false}}},plugins:{legend:{position:'bottom',labels:{font:{size:10}}},tooltip:{callbacks:{label:ctx=>`${ctx.dataset.label}: ${Number(ctx.parsed.y).toLocaleString('fr-FR',{maximumFractionDigits:1})} pts`}}}});
}
function renderContext() {
  const summary=D.summaryMap||{};
  cards('kpis',[
    ['Compte ou mobile money',pct(summary.account_rate_2024),'moyenne pondérée 2024'],
    ['Compte bancaire',pct(summary.bank_account_rate_2024),'moyenne pondérée 2024'],
    ['Mobile money',pct(summary.mobile_money_rate_2024),'moyenne pondérée 2024'],
    ['Épargne',pct(summary.saving_rate_2024),'au cours des 12 derniers mois'],
    ['Emprunt',pct(summary.borrowing_rate_2024),'au cours des 12 derniers mois']
  ]);
  const regions=D.regional||[];
  makeChart('regionChart','bar',regions.map(x=>short(x.regionwb24_hi)),[
    {label:'Détention d’un compte',data:regions.map(x=>x.account_t_d),backgroundColor:'#0f766e'},
    {label:'Compte bancaire',data:regions.map(x=>x.fiaccount_t_d),backgroundColor:'#06b6d4'}
  ],{percentAxis:true});
  const channels=[['Compte',summary.account_rate_2024],['Banque',summary.bank_account_rate_2024],['Mobile money',summary.mobile_money_rate_2024],['Épargne',summary.saving_rate_2024],['Emprunt',summary.borrowing_rate_2024]];
  makeChart('channelChart','bar',channels.map(x=>x[0]),[{label:'Taux',data:channels.map(x=>x[1]),backgroundColor:['#0f766e','#06b6d4','#2563eb','#7c3aed','#f59e0b']}],{percentAxis:true});
  const ranking=(D.ranking||[]).filter(x=>valueOf(x,'account_t_d')!==null).sort((a,b)=>b.account_t_d-a.account_t_d);
  const top=ranking.slice(0,12).reverse();
  makeChart('topChart','bar',top.map(x=>countryLabel(x.countrynewwb)),[{label:'Détention d’un compte',data:top.map(x=>x.account_t_d),backgroundColor:'#0f766e'}],{percentAxis:true});
  const focus=D.focus||[];
  makeChart('focusChart','bar',focus.map(x=>countryLabel(x.countrynewwb)),[{label:'Compte',data:focus.map(x=>x.account_t_d),backgroundColor:'#2563eb'},{label:'Mobile money',data:focus.map(x=>x.mobileaccount_t_d),backgroundColor:'#06b6d4'}],{percentAxis:true});
  makeTable('countryTable',['Pays','Région','Compte','Banque','Mobile money','Épargne'],ranking.slice(0,40).map(x=>[countryLabel(x.countrynewwb),short(x.regionwb24_hi),pct(x.account_t_d),pct(x.fiaccount_t_d),pct(x.mobileaccount_t_d),pct(x.save_any_t_d)]));
  const trend=D.trend||[];
  makeChart('trendChart','line',trend.map(x=>x.year),[
    {label:'Compte total',data:trend.map(x=>x.account_t_d),borderColor:'#0f766e',backgroundColor:'#0f766e22',fill:true,tension:.25},
    {label:'Compte bancaire',data:trend.map(x=>x.fiaccount_t_d),borderColor:'#06b6d4',tension:.25},
    {label:'Mobile money',data:trend.map(x=>x.mobileaccount_t_d),borderColor:'#2563eb',tension:.25},
    {label:'Épargne',data:trend.map(x=>x.save_any_t_d),borderColor:'#7c3aed',tension:.25}
  ],{percentAxis:true});
  const latest=trend.at(-1)||{};
  makeChart('connectivityChart','bar',['Téléphone mobile','Internet'],[{label:'2024',data:[latest.con1,latest.internet],backgroundColor:['#f59e0b','#2563eb']}],{percentAxis:true});
}
function nav() {
  document.querySelectorAll('.nav').forEach(button=>button.addEventListener('click',()=>{
    document.querySelectorAll('.nav').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('.page').forEach(x=>x.classList.remove('active'));
    button.classList.add('active');
    $(button.dataset.page).classList.add('active');
  }));
  $('reset').addEventListener('click',()=>document.querySelector('.nav[data-page="gaps"]').click());
}
renderGaps();
renderContext();
nav();
