const DATA_URL = "../../data/processed/superstore_clean.csv";
const C = { navy: "#111842", blue: "#536bd5", blue2: "#8b99e8", green: "#1d9b75", red: "#e64f5d", grid: "#ededf1", axis: "#d9d9e0", text: "#777989", ink: "#202136", Furniture: "#111842", "Office Supplies": "#6678d9", Technology: "#a7b0ec" };
const state = { rows: [], filtered: [], filters: { year: "", region: "", segment: "", category: "", shipMode: "" } };
const $ = (s) => document.querySelector(s);
const fmtMoney = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const fmtMoney2 = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "USD", maximumFractionDigits: 2 });
const fmtInt = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
const fmtPct = new Intl.NumberFormat("fr-FR", { style: "percent", maximumFractionDigits: 1 });
const monthShort = new Intl.DateTimeFormat("fr-FR", { month: "short" });
function parseCsv(text) {
  const rows = []; let row = []; let field = ""; let quoted = false;
  for (let i = 0; i < text.length; i++) { const c = text[i]; if (quoted) { if (c === '"' && text[i + 1] === '"') { field += '"'; i++; } else if (c === '"') quoted = false; else field += c; } else if (c === '"') quoted = true; else if (c === ",") { row.push(field); field = ""; } else if (c === "\n") { row.push(field.replace(/\r$/, "")); rows.push(row); row = []; field = ""; } else field += c; }
  if (field || row.length) { row.push(field.replace(/\r$/, "")); rows.push(row); }
  const headers = rows.shift(); return rows.filter((r) => r.length === headers.length).map((r) => Object.fromEntries(headers.map((h, i) => [h, r[i]])));
}
function normalize(r) { const d = new Date(`${r["Order Date"]}T00:00:00`); return { date: d, year: String(d.getFullYear()), monthKey: `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}`, orderId: r["Order ID"], customerId: r["Customer ID"], region: r.Region, segment: r.Segment, category: r.Category, shipMode: r["Ship Mode"], sales: Number(r.Sales), profit: Number(r.Profit), discount: Number(r.Discount) }; }
function sum(rows, key) { return rows.reduce((a, r) => a + r[key], 0); }
function group(rows, key) { const m = new Map(); for (const r of rows) { const k = r[key]; if (!m.has(k)) m.set(k, { key:k, sales:0, profit:0, count:0 }); const x=m.get(k); x.sales += r.sales; x.profit += r.profit; x.count++; } return [...m.values()]; }
function groupedMonth(rows) { const map = new Map(); for (const r of rows) { if (!map.has(r.monthKey)) map.set(r.monthKey,{ key:r.monthKey,date:new Date(`${r.monthKey}-01T00:00:00`),sales:0,profit:0 }); const x=map.get(r.monthKey); x.sales+=r.sales; x.profit+=r.profit; } return [...map.values()].sort((a,b)=>a.key.localeCompare(b.key)); }
function esc(s) { return String(s).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;"); }
function svgEl(tag,attrs={},text="") { const e=document.createElementNS("http://www.w3.org/2000/svg",tag); for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v); if(text)e.textContent=text; return e; }
function svgFor(container) { container.innerHTML=""; const w=Math.max(160,container.clientWidth),h=Math.max(90,container.clientHeight); const svg=svgEl("svg",{viewBox:`0 0 ${w} ${h}`,preserveAspectRatio:"none","aria-hidden":"true"}); container.append(svg); return {svg,w,h}; }
function tooltip(event,title,items) { const t=$("#tooltip"); t.innerHTML=`<strong>${esc(title)}</strong>`+items.map(([a,b])=>`<span>${esc(a)}<b>${esc(b)}</b></span>`).join(""); t.hidden=false; const r=t.getBoundingClientRect(); let x=event.clientX+12,y=event.clientY+12; if(x+r.width>innerWidth-8)x=event.clientX-r.width-12;if(y+r.height>innerHeight-8)y=event.clientY-r.height-12;t.style.left=`${Math.max(8,x)}px`;t.style.top=`${Math.max(8,y)}px`; }
function hideTip(){ $("#tooltip").hidden=true; }
function selectFilter(field,value){ const ids={year:"filter-year",region:"filter-region",segment:"filter-segment",category:"filter-category",shipMode:"filter-ship-mode"}; state.filters[field]=value; $("#"+ids[field]).value=value; update(); }
function setupFilters(){ const conf=[["year","year"],["region","region"],["segment","segment"],["category","category"],["shipMode","shipMode"]]; for(const [id,field] of conf){ const sel=$("#filter-"+(field==="shipMode"?"ship-mode":field)); const vals=[...new Set(state.rows.map(r=>r[field]))].sort((a,b)=>field==="year"?Number(a)-Number(b):a.localeCompare(b)); for(const v of vals){const o=document.createElement("option");o.value=v;o.textContent=v;sel.append(o);} sel.addEventListener("change",()=>{state.filters[field]=sel.value;update();}); } }
function filteredRows(){return state.rows.filter(r=>Object.entries(state.filters).every(([k,v])=>!v||String(r[k])===v));}
function renderSpark(container,values,color){container.innerHTML="";if(!values.length)return;const w=Math.max(100,container.clientWidth),h=36,p=3;const min=Math.min(...values),max=Math.max(...values),range=max-min||1;const pts=values.map((v,i)=>[p+i/(Math.max(1,values.length-1))*(w-p*2),h-p-(v-min)/range*(h-p*2)]);const d=pts.map((q,i)=>`${i?"L":"M"}${q[0]} ${q[1]}`).join(" ");const svg=svgEl("svg",{viewBox:`0 0 ${w} ${h}`,preserveAspectRatio:"none"});svg.append(svgEl("path",{d,fill:"none",stroke:color,"stroke-width":2,"stroke-linecap":"round","stroke-linejoin":"round"}));const last=pts.at(-1);svg.append(svgEl("circle",{cx:last[0],cy:last[1],r:2.7,fill:color}));container.append(svg);}
function changeText(node,now,previous,label){ node.className=""; if(!previous){node.textContent=`${label} · comparaison indisponible`;return;}const c=(now-previous)/Math.abs(previous);node.classList.add(c>=0?"positive":"negative");node.textContent=`${c>=0?"▲":"▼"} ${fmtPct.format(Math.abs(c))} vs ${label}`; }
function updateKpis(rows){ const sales=sum(rows,"sales"),profit=sum(rows,"profit"),margin=sales?profit/sales:0; const sparkMonths=groupedMonth(rows); $("#kpi-sales").textContent=fmtMoney.format(sales);$("#kpi-profit").textContent=fmtMoney.format(profit);$("#kpi-margin").textContent=fmtPct.format(margin); renderSpark($("#spark-sales"),sparkMonths.map(x=>x.sales),C.navy);renderSpark($("#spark-profit"),sparkMonths.map(x=>x.profit),C.blue);renderSpark($("#spark-margin"),sparkMonths.map(x=>x.sales?x.profit/x.sales:0),"#7a79c9");
  const years=[...new Set(rows.map(r=>Number(r.year)))].sort((a,b)=>a-b); const current=state.filters.year?Number(state.filters.year):Math.max(...years); const comp=state.rows.filter(r=>Object.entries(state.filters).every(([k,v])=>k==="year"||!v||String(r[k])===v)); const currRows=comp.filter(r=>Number(r.year)===current),prevRows=comp.filter(r=>Number(r.year)===current-1); changeText($("#kpi-sales-change"),sum(currRows,"sales"),sum(prevRows,"sales"),current-1);changeText($("#kpi-profit-change"),sum(currRows,"profit"),sum(prevRows,"profit"),current-1);const ms=$("#kpi-margin-status");ms.className=margin>=0?"positive":"negative";ms.textContent=`${fmtInt.format(new Set(rows.map(r=>r.orderId)).size)} commandes · ${fmtInt.format(new Set(rows.map(r=>r.customerId)).size)} clients`;
}
function renderDonut(rows){const data=group(rows,"category").sort((a,b)=>b.sales-a.sales);const {svg,w,h}=svgFor($("#category-sales"));if(!data.length)return;const cx=Math.min(65,w*.27),cy=h*.51,r=Math.min(43,h*.42),ri=r*.66,total=data.reduce((a,x)=>a+x.sales,0)||1;let angle=0;function polar(a,rad){const t=(a-90)*Math.PI/180;return[cx+rad*Math.cos(t),cy+rad*Math.sin(t)];}data.forEach(item=>{const sweep=item.sales/total*360,a=polar(angle+sweep,r),b=polar(angle, r),c=polar(angle,ri),d=polar(angle+sweep,ri),large=sweep>180?1:0;const path=`M ${a[0]} ${a[1]} A ${r} ${r} 0 ${large} 0 ${b[0]} ${b[1]} L ${c[0]} ${c[1]} A ${ri} ${ri} 0 ${large} 1 ${d[0]} ${d[1]} Z`;const el=svgEl("path",{d:path,fill:C[item.key]||C.blue,stroke:"#fff","stroke-width":2,class:"interactive"});el.addEventListener("mousemove",e=>tooltip(e,item.key,[["Ventes",fmtMoney2.format(item.sales)],["Part du CA",fmtPct.format(item.sales/total)],["Profit",fmtMoney2.format(item.profit)]]));el.addEventListener("mouseleave",hideTip);el.addEventListener("click",()=>selectFilter("category",item.key));svg.append(el);angle+=sweep;});svg.append(svgEl("text",{x:cx,y:cy-1,"text-anchor":"middle",fill:C.ink,"font-size":13,"font-weight":700},"100%"),svgEl("text",{x:cx,y:cy+12,"text-anchor":"middle","font-size":7},"du CA"));const lx=Math.max(cx+r+15,w*.53),space=Math.min(24,(h-20)/Math.max(1,data.length));data.forEach((item,i)=>{const y=cy-(data.length-1)*space/2+i*space;svg.append(svgEl("rect",{x:lx,y:y-6,width:7,height:7,rx:1,fill:C[item.key]||C.blue}),svgEl("text",{x:lx+12,y,fill:C.ink,"font-size":8},item.key),svgEl("text",{x:w-2,y,"text-anchor":"end","font-size":8,"font-weight":650},fmtPct.format(item.sales/total)));});}
function renderAnnual(rows){const data=group(rows,"year").sort((a,b)=>Number(a.key)-Number(b.key));const {svg,w,h}=svgFor($("#annual-performance"));if(!data.length)return;const m={top:17,right:43,bottom:30,left:48},pw=w-m.left-m.right,ph=h-m.top-m.bottom;const maxS=Math.max(1,...data.map(x=>x.sales))*1.12,maxP=Math.max(1,...data.map(x=>Math.abs(x.profit)))*1.15;const yS=v=>m.top+ph-v/maxS*ph,yP=v=>m.top+ph-(v+maxP)/(2*maxP)*ph;for(let i=0;i<=4;i++){const val=maxS*i/4,yy=yS(val);svg.append(svgEl("line",{x1:m.left,y1:yy,x2:w-m.right,y2:yy,class:"grid-line"}),svgEl("text",{x:m.left-6,y:yy+3,"text-anchor":"end"},compact(val)));const pv=-maxP+(2*maxP*i/4);svg.append(svgEl("text",{x:w-m.right+6,y:yy+3,"text-anchor":"start"},compact(pv)));}const slot=pw/data.length,bw=Math.min(54,slot*.48);data.forEach((x,i)=>{const xx=m.left+i*slot+(slot-bw)/2,yy=yS(x.sales);const bar=svgEl("rect",{x:xx,y:yy,width:bw,height:m.top+ph-yy,rx:2,fill:C.navy,class:"interactive"});bar.addEventListener("mousemove",e=>tooltip(e,x.key,[["Ventes",fmtMoney2.format(x.sales)],["Profit",fmtMoney2.format(x.profit)],["Marge",fmtPct.format(x.profit/x.sales)]]));bar.addEventListener("mouseleave",hideTip);bar.addEventListener("click",()=>selectFilter("year",x.key));svg.append(bar,svgEl("text",{x:xx+bw/2,y:h-9,"text-anchor":"middle","font-size":9,"font-weight":650},x.key));});const pts=data.map((x,i)=>[m.left+i*slot+slot/2,yP(x.profit)]);const d=pts.map((p,i)=>`${i?"L":"M"}${p[0]} ${p[1]}`).join(" ");svg.append(svgEl("path",{d,fill:"none",stroke:C.blue,"stroke-width":2.4,"stroke-linecap":"round","stroke-linejoin":"round"}));pts.forEach((p,i)=>{const x=data[i],dot=svgEl("circle",{cx:p[0],cy:p[1],r:4,fill:C.blue,stroke:"#fff","stroke-width":1.5,class:"interactive"});dot.addEventListener("mousemove",e=>tooltip(e,x.key,[["Profit",fmtMoney2.format(x.profit)],["Ventes",fmtMoney2.format(x.sales)]]));dot.addEventListener("mouseleave",hideTip);svg.append(dot);});svg.append(svgEl("text",{x:m.left,y:9,"font-size":7},"VENTES · USD"),svgEl("text",{x:w-m.right+3,y:9,"font-size":7},"PROFIT · USD"));}
function compact(v){const a=Math.abs(v);if(a>=1e6)return `${(v/1e6).toFixed(1)}M`;if(a>=1e3)return `${(v/1e3).toFixed(0)}k`;return fmtInt.format(v);}
function renderMonthly(rows) {
  const data = groupedMonth(rows);
  const { svg, w, h } = svgFor($("#monthly-profit-chart"));
  if (!data.length) return;
  let running = 0;
  const steps = data.map((item) => {
    const start = running;
    running += item.profit;
    return { ...item, start, end: running };
  });
  const total = running;
  steps.push({ key: "total", date: null, profit: total, sales: sum(rows, "sales"), start: 0, end: total, isTotal: true });
  const values = steps.flatMap((item) => [item.start, item.end]);
  const min = Math.min(0, ...values);
  const max = Math.max(0, ...values);
  const range = max - min || 1;
  const m = { top: 18, right: 8, bottom: 31, left: 44 };
  const pw = w - m.left - m.right;
  const ph = h - m.top - m.bottom;
  const y = (value) => m.top + ((max - value) / range) * ph;
  for (let i = 0; i <= 4; i += 1) {
    const value = min + (range * i) / 4;
    const yy = y(value);
    svg.append(
      svgEl("line", { x1: m.left, y1: yy, x2: w - m.right, y2: yy, class: "grid-line" }),
      svgEl("text", { x: m.left - 5, y: yy + 3, "text-anchor": "end" }, compact(value)),
    );
  }
  const slot = pw / steps.length;
  const bw = Math.max(2, Math.min(12, slot * 0.62));
  steps.forEach((item, i) => {
    const xx = m.left + i * slot + (slot - bw) / 2;
    const y1 = y(item.start);
    const y2 = y(item.end);
    const color = item.isTotal ? C.navy : item.profit >= 0 ? C.blue : C.red;
    const bar = svgEl("rect", {
      x: xx, y: Math.min(y1, y2), width: bw, height: Math.max(1, Math.abs(y2 - y1)),
      rx: 1, fill: color, class: "interactive",
    });
    const title = item.isTotal ? "Profit net total" : `${monthShort.format(item.date)} ${item.date.getFullYear()}`;
    bar.addEventListener("mousemove", (event) => tooltip(event, title, [
      [item.isTotal ? "Profit total" : "Contribution du mois", fmtMoney2.format(item.profit)],
      ["Cumul après le mois", fmtMoney2.format(item.end)],
    ]));
    bar.addEventListener("mouseleave", hideTip);
    svg.append(bar);
    if (i < steps.length - 1 && i % 3 === 2) {
      const connectorY = y(item.end);
      svg.append(svgEl("line", {
        x1: xx + bw, y1: connectorY, x2: m.left + (i + 1) * slot + (slot - bw) / 2, y2: connectorY,
        stroke: "#b9bbc8", "stroke-width": 1, "stroke-dasharray": "2 2",
      }));
    }
    if ((i < data.length && (i % 3 === 0 || i === data.length - 1)) || item.isTotal) {
      const label = item.isTotal ? "Total" : `${monthShort.format(item.date)} ${String(item.date.getFullYear()).slice(-2)}`;
      svg.append(svgEl("text", { x: xx + bw / 2, y: h - 9, "text-anchor": "middle", "font-size": 7 }, label));
    }
  });
  $("#profit-total-note").textContent = `Profit cumulé : ${fmtMoney.format(total)}`;
}
function update(){state.filtered=filteredRows();const rows=state.filtered;updateKpis(rows);renderDonut(rows);renderAnnual(rows);renderMonthly(rows);$("#selection-count").textContent=`${fmtInt.format(rows.length)} lignes · ${fmtInt.format(new Set(rows.map(r=>r.orderId)).size)} commandes`;if(rows.length){const years=rows.map(r=>Number(r.year));$("#reporting-period").textContent=`USD · ${Math.min(...years)}—${Math.max(...years)}`;}else{$("#reporting-period").textContent="Aucune donnée";}}
function reset(){for(const k of Object.keys(state.filters))state.filters[k]="";document.querySelectorAll(".filter-bar select").forEach(s=>s.value="");update();}
async function init(){try{const res=await fetch(DATA_URL);if(!res.ok)throw new Error(`HTTP ${res.status}`);state.rows=parseCsv(await res.text()).map(normalize);setupFilters();$("#reset-filters").addEventListener("click",reset);update();$("#loading").hidden=true;document.querySelectorAll(".nav-link").forEach(a=>a.addEventListener("click",()=>{document.querySelectorAll(".nav-link").forEach(x=>x.classList.remove("is-active"));a.classList.add("is-active");}));}catch(err){console.error(err);$("#loading").querySelector("strong").textContent="Chargement impossible";$("#loading").querySelector("span").textContent="Vérifiez que le serveur web est lancé depuis le dossier du projet.";$(".spinner").remove();}}
window.addEventListener("resize",()=>{if(state.rows.length)update();});init();
