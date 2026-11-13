# Rapport d’analyse — BTC/ETH OHLC

## Périmètre

Cette analyse compare les marchés spot BTC/USDT et ETH/USDT à partir des chandeliers quotidiens publics de Binance. Elle décrit la performance historique, la volatilité annualisée, les rendements journaliers, les jours positifs, le drawdown maximal et la corrélation des rendements.

Les prix sont exprimés en USDT par unité. Les rendements sont calculés à partir des cours de clôture quotidiens. La volatilité annualisée utilise l’écart-type des rendements journaliers multiplié par `sqrt(365)`, car le marché crypto fonctionne en continu.

## Interprétation

Les indicateurs décrivent le comportement historique de la paire et ne constituent pas une prévision ni une recommandation d’investissement. Le drawdown mesure la baisse depuis le plus haut historique de l’indice de richesse de chaque actif. Les résultats sont sensibles à la date de récupération et à la convention de clôture quotidienne de Binance.

## Reproduction

```bash
python projects/10-cryptomonnaies/scripts/fetch_data.py --start 2017-01-01
python projects/10-cryptomonnaies/scripts/analyze.py
```

## Fichiers de sortie

- `data/raw/binance_spot_daily_ohlc.csv` : snapshot source téléchargé.
- `results/daily_metrics.csv` : rendements, indice base 100, drawdown et volatilité glissante.
- `results/asset_summary.csv` : synthèse par actif.
- `results/monthly_metrics.csv` : métriques mensuelles.
- `results/return_correlation.csv` : corrélation des rendements journaliers communs.
- `visuals/wealth_index.png`, `visuals/drawdown.png`, `visuals/risk_return_summary.png` : graphiques.

## Source

Binance, **Binance Public Data** et documentation Spot REST API. La source et la date de récupération sont conservées dans `data/raw/SOURCE.md`.
