const fmtPct = (v) => `${(Number(v) * 100).toFixed(1)}%`;
const fmtUsd = (v) => new Intl.NumberFormat('en-US', {maximumFractionDigits: 2}).format(Number(v));
fetch('../../results/dashboard_data.json').then(r => r.json()).then(data => {
  document.querySelector('#updated').textContent = `jusqu’au ${data.last_updated}`;
  document.querySelector('#corr-value').textContent = Number(data.correlation).toFixed(2);
  const cards = document.querySelector('#cards');
  cards.innerHTML = data.summary.map(x => `<article class="card"><div class="card-top"><div class="asset">${x.symbol === 'BTCUSDT' ? '₿ Bitcoin' : 'Ξ Ethereum'}</div><div class="chip">${x.observations.toLocaleString('fr-FR')} jours</div></div><div class="metric">${fmtPct(x.cagr)}</div><div class="label">CAGR historique</div><div class="mini"><div><b>${fmtPct(x.annualized_volatility)}</b><span>Volatilité</span></div><div><b>${fmtPct(x.max_drawdown)}</b><span>Drawdown max.</span></div><div><b>${fmtUsd(x.end_close)} USDT</b><span>Dernière clôture</span></div></div></article>`).join('');
  const maxVol = Math.max(...data.summary.map(x => Number(x.annualized_volatility)));
  document.querySelector('#bars').innerHTML = data.summary.map(x => `<div class="bar-row"><strong>${x.symbol.replace('USDT','')}</strong><div class="bar-track"><div class="bar-fill ${x.symbol === 'BTCUSDT' ? 'green' : 'gold'}" style="width:${Math.max(8, Number(x.annualized_volatility) / maxVol * 100)}%"></div></div><span>${fmtPct(x.annualized_volatility)}</span></div>`).join('');
}).catch(() => { document.querySelector('#updated').textContent = 'résultats indisponibles'; });
