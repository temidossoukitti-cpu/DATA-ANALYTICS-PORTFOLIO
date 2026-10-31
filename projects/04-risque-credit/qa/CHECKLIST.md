# Checklist manuelle Power BI

**À réaliser et cocher par Samuel après création du PBIX.** Toutes les cases sont laissées décochées. L’état automatisé est consigné séparément dans `validation_report.md`.

## Parité SQL / Python — contrôle automatisé

`scripts/05_sql.py` reconstruit `data/processed/credit_risk.db` depuis les CSV et exécute les cinq requêtes de `sql/`. La dernière exécution a comparé **34 résultats**, tous au statut PASS; le détail et les écarts mesurés figurent dans [`results/sql_parity.csv`](../results/sql_parity.csv) et `validation_report.md`. Ce contrôle automatisé ne remplace pas les validations Power BI Desktop ci-dessous.

- [ ] Charger les huit CSV (sept tables en étoile et la scorecard) depuis le paramètre `DataFolder` et vérifier les types dans Power BI Desktop.
- [ ] Créer et vérifier les six relations de dimension vers `fact_clients` décrites dans `model/DATA_MODEL.md`.
- [ ] Vérifier que la table `_Mesures` et ses dossiers d’affichage sont présents.
- [ ] Construire les quatre pages selon `powerbi/PAGE_PLAN.md`, sans inventer de palette propre à ce projet.
- [ ] Vérifier les cinq cartes KPI de la page Vue d’ensemble contre les valeurs attendues de `model/DAX_MEASURES.md`.
- [ ] Confirmer que les segments sexe, âge et état matrimonial sont utilisés à des fins descriptives, jamais comme règle de décision individuelle.
- [ ] Vérifier que les pages de scoring et de bandes de risque sont filtrées sur la partition test pour leurs mesures de performance.
- [ ] Tester le bouton « Réinitialiser » sur chaque page et s’assurer qu’il restaure les filtres par défaut.
- [ ] Vérifier la navigation latérale, les titres-message et l’affichage des montants en NT$.
- [ ] Terminer les scénarios de `qa/INTERACTION_TESTS.md`, rouvrir le fichier dans Desktop et vérifier les interactions après réouverture.
- [ ] Exporter les aperçus selon `powerbi/EXPORT_PREVIEWS.md` et noter la version de Power BI Desktop.
