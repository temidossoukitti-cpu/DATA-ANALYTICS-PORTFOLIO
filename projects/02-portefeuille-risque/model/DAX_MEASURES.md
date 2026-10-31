# Modèle de données et mesures DAX (Power BI)

> Mesures écrites pour Power BI Desktop, **à valider dans ton rapport** (vérifie chaque résultat contre `results/metrics_portfolio_vs_index.csv`).

## Tables à importer
| Table | Fichier | Rôle |
|---|---|---|
| Prix | data/cleaned/prices_long.csv | date, ticker, close, rendement |
| Actifs | data/raw/assets.csv | ticker, secteur |
| Positions | results/weights.csv | ticker, valeur_marche, poids, secteur |
| Rendements | results/portfolio_returns.csv | date, portefeuille, IDX |
| Performance | results/performance_base100.csv | date, portefeuille, IDX (base 100) |

Relations : Prix[ticker] → Actifs[ticker] (plusieurs à un) ; Positions[ticker] → Actifs[ticker].

## Paramètre
```dax
Taux sans risque = 0.035
Periodes par an = 52
```

## Mesures sur la table Rendements
```dax
Rendement annualisé =
VAR n = COUNTROWS ( Rendements )
VAR cumul = PRODUCTX ( Rendements, 1 + Rendements[portefeuille] )
RETURN POWER ( cumul, [Periodes par an] / n ) - 1

Volatilité annualisée =
STDEV.S ( Rendements[portefeuille] ) * SQRT ( [Periodes par an] )

Ratio de Sharpe =
DIVIDE ( [Rendement annualisé] - [Taux sans risque], [Volatilité annualisée] )

VaR 95 % hebdo =
-PERCENTILEX.INC ( Rendements, Rendements[portefeuille], 0.05 )

Bêta vs IDX =
VAR mp = AVERAGE ( Rendements[portefeuille] )
VAR mi = AVERAGE ( Rendements[IDX] )
VAR cov =
    SUMX ( Rendements, ( Rendements[portefeuille] - mp ) * ( Rendements[IDX] - mi ) )
        / ( COUNTROWS ( Rendements ) - 1 )
RETURN DIVIDE ( cov, VAR.S ( Rendements[IDX] ) )
```

## Drawdown (sur la table Performance)
```dax
Sommet historique =
CALCULATE (
    MAX ( Performance[portefeuille] ),
    FILTER ( ALL ( Performance[date] ), Performance[date] <= MAX ( Performance[date] ) )
)

Drawdown = DIVIDE ( MAX ( Performance[portefeuille] ), [Sommet historique] ) - 1

Drawdown maximum = MINX ( VALUES ( Performance[date] ), [Drawdown] )
```

## Répartition
```dax
Poids = SUM ( Positions[poids] )
Poids par secteur = CALCULATE ( [Poids], ALLEXCEPT ( Positions, Positions[sector] ) )
```
