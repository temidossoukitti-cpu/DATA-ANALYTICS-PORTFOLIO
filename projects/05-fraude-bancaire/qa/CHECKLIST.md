# Checklist de validation manuelle Power BI

## Contrôles automatisés

L’état des scripts, des résultats et des comparaisons SQL/Python est produit dans [`validation_report.md`](validation_report.md). Ces vérifications automatisées ne valident pas le rendu dans Power BI Desktop.

## À réaliser par Samuel dans Power BI Desktop

Toutes les cases ci-dessous restent décochées tant que l’action n’a pas été faite sur le fichier PBIX réel.

- [ ] Créer ou actualiser les huit tables en suivant `powerbi/POWER_QUERY.md`.
- [ ] Confirmer les huit noms de tables et les types numériques; vérifier qu’aucun identifiant technique n’est interprété comme montant.
- [ ] Créer et contrôler les relations 1:* et la relation `fact_transactions` 1→0..1 `fact_model_test` décrites dans `model/DATA_MODEL.md`.
- [ ] Créer la table `_Mesures`, ajouter les mesures de `model/DAX_MEASURES.md`, leur dossier d’affichage et leurs formats.
- [ ] Vérifier chaque valeur attendue des mesures contre `qa/validation_report.md`.
- [ ] Construire exactement les quatre pages décrites dans `powerbi/PAGE_PLAN.md` au gabarit 1280×720, sans choisir de thème avant la décision commune du portfolio.
- [ ] Confirmer que le segment temporel utilise les fenêtres relatives et qu’aucun slicer de date civile n’est ajouté.
- [ ] Vérifier les cinq cartes KPI, les titres-messages, la navigation et le bouton « Réinitialiser » sur chaque page.
- [ ] Tester tous les scénarios de `qa/INTERACTION_TESTS.md` et y noter le résultat observé.
- [ ] Examiner les montants : conserver la formulation « unités du dataset » et ne pas ajouter de symbole de devise.
- [ ] Vérifier les avertissements de portée : deux jours d’observations, PCA anonymisée et absence de type de transaction.
- [ ] Exporter et relire le PDF et les quatre aperçus PNG suivant `powerbi/EXPORT_PREVIEWS.md`; enregistrer la version de Desktop.
- [ ] Après validation, remplacer `À construire par Samuel` par un état factuel et commit les exports si Samuel souhaite les versionner.
