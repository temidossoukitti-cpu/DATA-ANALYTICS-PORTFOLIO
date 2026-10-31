# Tests d’interaction Power BI

Ces contrôles sont manuels et restent en attente de la construction du PBIX par Samuel. Aucune interaction n’est déclarée validée.

| Test | Action | Résultat attendu | État |
|---|---|---|---|
| Filtre âge | Choisir une bande d’âge puis l’effacer. | Les visuels descriptifs changent; les totaux suivent le filtre; aucune conclusion de décision individuelle par âge. | [ ] |
| Filtre d’éducation | Choisir une catégorie d’éducation recodée. | L’étiquette « autre/inconnu » inclut les codes source recodés et les effectifs concordent avec les tables traitées. | [ ] |
| Filtre de limite | Choisir une bande de limite. | Les mesures et visuels par bande se mettent à jour sans perdre de clients. | [ ] |
| Filtre de statut | Choisir un statut `pay_0`. | Le taux par statut se met à jour et le libellé de code reste visible. | [ ] |
| Partition du modèle | Choisir `Test` dans la page Scoring et actions. | Les AUC, PR-AUC, KS, lift, calibration et résultats par bande restent limités aux observations test. | [ ] |
| Filtre de risque | Choisir une ou plusieurs bandes de risque. | Exposition et perte attendue changent conformément aux lignes de la partition test. | [ ] |
| Réinitialisation | Modifier plusieurs filtres puis cliquer « Réinitialiser ». | Tous les filtres reviennent aux valeurs par défaut propres à la page. | [ ] |
| Navigation | Passer d’une page à l’autre via la barre latérale. | La page attendue s’ouvre; le titre-message et les visuels correspondent au plan. | [ ] |
| Réouverture | Enregistrer, fermer puis rouvrir le PBIX dans Desktop. | Relations, mesures, pages, filtres et bouton de réinitialisation restent opérationnels. | [ ] |
