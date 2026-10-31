# Export des aperçus Power BI

Le dashboard n’a pas encore été construit. Cette procédure est réservée à Samuel après création et validation du PBIX dans Power BI Desktop.

1. Noter la version exacte de Power BI Desktop utilisée : **à renseigner lors de l’export; non vérifiée à ce stade**.
2. Ouvrir le PBIX final, vérifier les relations et terminer les contrôles manuels de `qa/CHECKLIST.md`.
3. Dans Power BI Desktop, choisir **Fichier → Exporter → Exporter au format PDF** et enregistrer la sortie de contrôle hors du dépôt.
4. Pour chaque page, exporter une image PNG à l’aide de la fonction d’export disponible dans la version de Desktop utilisée; si l’export direct PNG n’est pas proposé, utiliser la capture/export de page documentée par Samuel, sans reconstruire l’interface en HTML.
5. Enregistrer les aperçus validés dans `preview/` avec ces noms :
   - `preview/04-risque-credit-vue-ensemble.png`
   - `preview/04-risque-credit-segments-a-risque.png`
   - `preview/04-risque-credit-paiements-retards.png`
   - `preview/04-risque-credit-scoring-actions.png`
6. Contrôler lisibilité, filtres réinitialisés, titres, unité NT$ et version de Desktop avant ajout au dépôt.

Aucun PDF, PNG ni PBIX n’est inclus avant l’intervention de Samuel.
