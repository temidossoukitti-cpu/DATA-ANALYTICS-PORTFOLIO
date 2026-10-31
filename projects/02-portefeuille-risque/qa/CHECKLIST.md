# Checklist de validation : projet 01

## Données
- [ ] 104 lignes, du 2024-11-01 au 2026-10-23
- [ ] Aucun doublon, aucune valeur manquante, aucun prix nul (`results/quality_check.csv`)
- [ ] Mention « données simulées » visible dans le README

## Calculs
- [ ] `python scripts/analysis.py` s'exécute sans erreur depuis le dossier du projet
- [ ] Les poids de `results/weights.csv` totalisent 100 %
- [ ] Les contributions au risque totalisent 100 %
- [ ] Mesures DAX : rendement, volatilité, Sharpe, bêta, VaR et drawdown égaux aux résultats Python (écart < 0,1 point)

## Dashboard (quand il sera construit)
- [ ] Une question de gestion claire en haut de la page
- [ ] Filtres testés (période, secteur) et bouton de réinitialisation
- [ ] Chaque graphique a un titre qui énonce un message
- [ ] Aperçus PNG/PDF enregistrés dans `preview/`

## Publication
- [ ] README relu : résumé de 60 secondes, résultats, recommandations, limites
- [ ] Aucun fichier confidentiel ni identifiant dans le dépôt
