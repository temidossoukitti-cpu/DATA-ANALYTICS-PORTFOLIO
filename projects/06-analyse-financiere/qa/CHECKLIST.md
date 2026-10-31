# Checklist de validation manuelle Power BI

## Contrôles automatisés

L’état des scripts, des résultats et des comparaisons SQL/Python est produit dans [`validation_report.md`](validation_report.md). Ces vérifications automatisées ne valident pas le rendu dans Power BI Desktop.

## À réaliser par Samuel dans Power BI Desktop

Toutes les cases ci-dessous restent décochées tant que l’action n’a pas été faite sur le fichier PBIX réel.

- [ ] Créer ou actualiser les sept tables en suivant `powerbi/POWER_QUERY.md`.
- [ ] Confirmer les sept noms de tables et les types numériques; vérifier que `fiscal_year_key`, `metric_key` et `ratio_key` ne sont jamais interprétés comme des montants.
- [ ] Créer et contrôler les relations 1:* décrites dans `model/DATA_MODEL.md`.
- [ ] Créer la table `_Mesures`, ajouter les mesures de `model/DAX_MEASURES.md`, leur dossier d’affichage et leurs formats.
- [ ] Vérifier chaque valeur attendue des mesures contre `qa/validation_report.md` avec le segment sur l’exercice 2025.
- [ ] Construire exactement les quatre pages décrites dans `powerbi/PAGE_PLAN.md` au gabarit 1280×720, sans choisir de thème avant la décision commune du portfolio.
- [ ] Confirmer que le segment temporel est annuel et que le tri de `dim_fiscal_year[label_fr]` utilise `sort_order`.
- [ ] Vérifier les cinq cartes KPI, les titres-messages, la navigation et le bouton « Réinitialiser » sur chaque page.
- [ ] Tester tous les scénarios de `qa/INTERACTION_TESTS.md` et y noter le résultat observé.
- [ ] Examiner les montants : conserver la formulation en dollars américains et ne pas ajouter de symbole aux ratios.
- [ ] Vérifier les avertissements de portée : sept exercices, absence de segmentation par activité et de ventilation géographique.
- [ ] Exporter et relire le PDF et les quatre aperçus PNG suivant `powerbi/EXPORT_PREVIEWS.md`; enregistrer la version de Desktop.
- [ ] Après validation, remplacer `À construire par Samuel` par un état factuel et commit les exports si Samuel souhaite les versionner.
