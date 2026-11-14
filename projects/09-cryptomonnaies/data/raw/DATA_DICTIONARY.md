# Dictionnaire des données

Le fichier `binance_spot_daily_ohlc.csv` reprend les chandeliers Spot Binance pour les symboles `BTCUSDT` et `ETHUSDT`, à intervalle `1d`.

- `symbol` : paire négociée.
- `open_time`, `close_time` : début et fin UTC de la bougie.
- `open`, `high`, `low`, `close` : prix en USDT.
- `volume` : volume de l’actif de base.
- `quote_volume` : volume notionnel en USDT.
- `trades` : nombre de transactions agrégées.
- `taker_buy_base_volume`, `taker_buy_quote_volume` : volumes acheteurs taker.
- `ignore` : champ conservé tel que fourni par Binance.

Les colonnes `daily_return`, `log_return`, `wealth`, `running_max`, `drawdown` et `rolling_vol_30d` sont dérivées dans `results/daily_metrics.csv`.
