# Dictionnaire des données

## prices_weekly.csv (format large)
| Colonne | Type | Description |
|---|---|---|
| date | date (AAAA-MM-JJ) | Vendredi de clôture de la semaine |
| NVTK … UTLG | nombre | Prix de clôture hebdomadaire de chaque titre (devise de référence commune) |
| IDX | nombre | Niveau de l'indice de référence du marché |

## assets.csv
| Colonne | Description |
|---|---|
| ticker | Code du titre (fictif) |
| company | Nom de l'entreprise (fictive) |
| sector | Secteur d'activité |
| currency | Devise de cotation d'origine (informatif ; aucune conversion appliquée) |

## holdings.csv
| Colonne | Description |
|---|---|
| ticker | Code du titre |
| shares | Nombre de titres détenus |
| buy_date | Date d'achat |
| buy_price | Prix d'achat (clôture de la date d'achat) |

## Tables produites (data/cleaned et results)
- `prices_long.csv` : date, ticker, close, rendement (format long pour Power BI).
- `portfolio_returns.csv` : rendements hebdomadaires du portefeuille et de l'indice.
- `performance_base100.csv` : valeur du portefeuille et de l'indice en base 100.
