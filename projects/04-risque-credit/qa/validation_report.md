# Rapport de validation — Projet 04

Généré par `scripts/06_report.py`; les compteurs ci-dessous sont recalculés depuis les données, le plan Power BI et les fichiers produits. Le rapport ne revendique aucune validation manuelle dans Power BI Desktop.

## Compteurs générés

| Élément | Valeur | Source |
|---|---:|---|
| Clients traités | 30 000 | `data/processed/fact_clients.csv` |
| Colonnes source | 25 | Schéma XLS UCI et `DATA_DICTIONARY.md` |
| Tables CSV Power BI | 8 | `data/processed/` |
| Tables du schéma en étoile | 7 | Fact et dimensions |
| Mesures DAX documentées | 14 | `model/DAX_MEASURES.md` |
| Pages Power BI planifiées | 4 | `powerbi/PAGE_PLAN.md` |
| Indicateurs de portefeuille | 9 | `results/metrics_summary.csv` |
| Recommandations quantifiées | 4 | `results/recommendations.csv` |
| Graphiques PNG | 8 | `visuals/` |

## Indicateurs clés

Taux de défaut : **22,12 %**; limite totale : **NT$ 5 024 529 680**; exposition des défaillants : **NT$ 863 407 680**; ROC-AUC test : **0,7536**; PR-AUC test : **0,5016**; perte attendue test à LGD 45 % : **NT$ 43 390 137**.

## Contrôles automatisés

| Contrôle | Attendu | Constaté | Statut |
|---|---|---|---|
| Source UCI | Fichier brut inchangé, SHA-256 conforme | 30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933; 5 539 328 octets | PASS |
| Structure source | 30 000 lignes et 25 colonnes | 30 000 lignes fact_clients; 25 colonnes brutes | PASS |
| Qualité et conservation | Aucun échec; aucune ligne supprimée | 16/16 PASS; 30 000 lignes après nettoyage | PASS |
| Licence et attribution | CC BY 4.0 et citation Yeh (2009) dans SOURCE et README | CC BY 4.0 | PASS |
| Modèle Power BI | 7 tables en étoile + 1 scorecard; fact 30 000 lignes | 8 CSV traités; 8 tables SQLite; 30 000 lignes fact | PASS |
| Modèle prédictif | Split stratifié 70/30, graine 42, seuil documenté; variables sensibles exclues | 21 000/9 000; random_state=42; seuil 0,25; ROC-AUC 0,7536 | PASS |
| Parité SQL / Python | Au moins 5 indicateurs, écarts dans la tolérance | 34 comparaisons; 34 PASS | PASS |
| Mesures DAX | Chaque mesure commentée, valeur attendue issue des résultats | 14 mesures générées; valeurs issues des CSV results | PASS |
| Pages Power BI | Le README correspond au PAGE_PLAN | 4 pages; README cohérent | PASS |
| README et navigation | Badge PORTFOLIO, moins de 120 lignes, liens/images locaux résolus | 119 lignes; 0 lien(s) rompu(s) | PASS |
| Conformité du texte | Aucun marqueur de tâche restant, chemin absolu ou lien professionnel | Détection tâche=False; chemin absolu=False; LinkedIn URL=False | PASS |
| Poids du projet | Projet <25 Mo et aucun fichier >50 Mo | 17.74 Mo; 0 fichier(s) >50 Mo | PASS |
| Graphiques | De 6 à 8 PNG Matplotlib | 8 PNG | PASS |
| Recommandations | De 4 à 6 pistes chiffrées, issues des résultats | 4 recommandations générées | PASS |
| Caches et PBIX | Aucun cache; aucun PBIX/PBIP/PBIR/TMDL généré | aucun cache | PASS |
| Contrôles Power BI manuels | Checklist laissée non cochée et interactions en attente | 20 cases non cochées; 0 cochée(s) | PASS |

**Statut global automatisé : PASS.** **Statut manuel Power BI : à faire.** Les cases de `qa/CHECKLIST.md` et `qa/INTERACTION_TESTS.md` restent décochées tant que Samuel n’a pas construit et testé le PBIX.

## Parité SQL / Python

La base `data/processed/credit_risk.db` est reconstruite par `scripts/05_sql.py` depuis les CSV. Le fichier `results/sql_parity.csv` contient **34 comparaisons**; toutes doivent être PASS à la tolérance indiquée.

## Hypothèses conservées

Codes `pay_*` -2 et 0 traités comme hypothèses documentées; utilisation plafonnée entre 0 et 150 %; ratio de paiement défini seulement si `bill_amt1 > 0`; bandes de score fixes; seuil de classification issu de `model_metrics.csv`; perte attendue fondée sur la facture positive et une LGD supposée à 45 %, avec sensibilité 30/45/60 %.
