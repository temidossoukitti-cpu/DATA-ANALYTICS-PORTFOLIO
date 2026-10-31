# 02 · Risque et performance d'un portefeuille d'actions

> **Données simulées.** Les entreprises, les prix et les positions de ce projet sont fictifs, générés pour reproduire un marché réaliste (dont une phase de correction). Voir `scripts/fetch_real_data.py` pour la version avec de vraies cotations.

## Question de gestion
Le portefeuille compense-t-il le risque qu'il prend par rapport à son indice de référence, où le risque est-il concentré, et comment rééquilibrer les positions ?

## Résumé en 60 secondes
- Sur 2 ans (104 semaines), le portefeuille rapporte **13,0 % par an** contre **11,4 %** pour l'indice, mais avec plus de risque : volatilité **19,9 %** contre 17,1 %.
- Le **ratio de Sharpe** est quasiment identique (0,48 contre 0,46) : le rendement supplémentaire ne rémunère que le risque supplémentaire.
- **Le risque est concentré** : une seule banque (AFBK) pèse 28,5 % de la valeur et **34,9 % du risque** ; le secteur Finance représente 34,8 % du portefeuille.
- Pire phase : **-35,7 %** de perte maximale (drawdown), contre -30,4 % pour l'indice.

## Données
| Fichier | Contenu |
|---|---|
| `data/raw/prices_weekly.csv` | 104 clôtures hebdomadaires (01/11/2024 – 23/10/2026) pour 10 actions et l'indice IDX |
| `data/raw/assets.csv` | Entreprise, secteur et devise d'origine de chaque titre |
| `data/raw/holdings.csv` | Positions : nombre de titres, date et prix d'achat |

Contrôle qualité (`results/quality_check.csv`) : 104 lignes, 0 doublon, 0 valeur manquante, 0 prix nul. Dictionnaire complet : `data/raw/DATA_DICTIONARY.md`.

## Méthode
1. Contrôle qualité et nettoyage des prix.
2. Rendements hebdomadaires, poids calculés sur la valeur de marché à la dernière date.
3. Indicateurs : rendement annualisé, volatilité, Sharpe (taux sans risque 3,5 %), drawdown maximum, bêta et alpha contre l'indice, VaR historique à 95 %.
4. Corrélations et **contribution de chaque titre au risque total**.
5. Optimisation (variance minimale et Sharpe maximal, poids limités à 35 % par titre) pour comparer avec la répartition actuelle.

## Résultats clés
| Indicateur | Portefeuille | Indice IDX |
|---|---:|---:|
| Rendement annualisé | 13,0 % | 11,4 % |
| Volatilité annualisée | 19,9 % | 17,1 % |
| Ratio de Sharpe | 0,48 | 0,46 |
| Drawdown maximum | -35,7 % | -30,4 % |
| Bêta vs IDX | 1,03 | 1,00 |
| Alpha annualisé | +1,4 % | n/a |
| VaR 95 % (1 semaine) | 3,2 % | 3,0 % |
| Pire semaine | -11,6 % | -9,3 % |

**Contribution au risque (principaux titres)**

| Titre | Poids | Part du risque |
|---|---:|---:|
| AFBK (Finance) | 28,5 % | 34,9 % |
| CLDX (Technologie) | 14,1 % | 21,2 % |
| ENRG (Énergie) | 9,1 % | 7,4 % |

AFBK et CLDX représentent 42,6 % de la valeur mais **56,1 % du risque**.

## Recommandations
1. **Plafonner chaque position à 20 %** : ramener AFBK de 28,5 % à 20 % réduit directement la part du risque la plus élevée.
2. **Surveiller CLDX** : bêta de 1,46 et perte maximale de -52 % sur la période ; la conserver comme moteur de croissance, mais avec un poids limité.
3. **Ajouter des titres défensifs** : UTLG et TLCM ont les bêtas les plus faibles (0,54 et 0,57) et les volatilités les plus basses ; ils amortissent les corrections, au prix d'un rendement plus faible sur la période.
4. **Fixer des seuils d'alerte** : revue du portefeuille si la perte hebdomadaire dépasse la VaR (3,2 %) ou si le drawdown dépasse -20 %.
5. **Diversifier au-delà de la Finance** (34,8 % du portefeuille) pour réduire le risque sectoriel.

## Limites
- Données simulées : les conclusions illustrent la méthode, pas un marché réel.
- Poids constants sur toute la période, sans frais de transaction ni taux de change (les prix sont supposés exprimés dans une même devise).
- Optimisation calculée sur le passé (in-sample) : elle sert de repère, pas de prévision, et le résultat « Sharpe maximal » est très probablement surévalué.
- Période courte (2 ans) et fréquence hebdomadaire.

## Reproduire l'analyse
```bash
pip install -r requirements.txt
python scripts/analysis.py
```
Les résultats sont écrits dans `results/` et `data/cleaned/`.

## Dashboard
*À venir : dashboard Power BI (aperçus dans `preview/`). Les mesures DAX sont déjà documentées dans `model/DAX_MEASURES.md`.*
