# 07 · Performance marketing d'une banque

[![Portfolio](../../assets/portfolio-button.svg)](../../README.md) · [← Retour à l'index](../../README.md)

**Données publiques :** [UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing), sous licence CC BY 4.0.

## Question de gestion

Quels segments et contextes de campagne sont associés à une meilleure souscription d'un dépôt à terme, et comment prioriser les contacts sans transformer une corrélation en décision automatique ?

## Résumé en 60 secondes

- **41 188** observations de campagne et **4 640** souscriptions, soit **11,27 %** de conversion.
- Les observations dont la campagne précédente s'est soldée par un succès affichent **65,11 %** de conversion, contre **8,83 %** lorsque l'issue précédente est inexistante.
- Les groupes **66 ans et plus** et **17–25 ans** affichent respectivement **46,85 %** et **20,95 %** de conversion, avec des volumes très différents.
- Le modèle logistique atteint **ROC-AUC 0,7917**, **PR-AUC 0,4518** et **F1 0,4903** sur le test, avec un seuil choisi à **0,65**.

## Données et qualité

Le fichier `bank-additional-full.csv` provient du dépôt UCI et couvre les campagnes téléphoniques d'une banque portugaise de mai 2008 à novembre 2010. La source contient 20 variables explicatives et la cible `y`. Les modalités `unknown` sont conservées comme catégories explicites. Les 12 doublons exacts sont conservés pour l'analyse descriptive et regroupés lors de la séparation train/test.

Les contrôles de présence des colonnes, de cible, d'âge, de campagne, de durées, de dates relatives et d'indicateurs macroéconomiques sont PASS. Le rapport complet se trouve dans `qa/validation_report.md`; la provenance, la licence et l'empreinte du fichier sont dans `data/raw/SOURCE.md`.

## Méthode

Le pipeline Python nettoie la source, construit une table de faits et huit dimensions, produit les agrégats et les graphiques, puis entraîne une régression logistique avec séparation groupée stratifiée 70/30. Le seuil est sélectionné sur des prédictions hors pli afin de maximiser le F1. La variable `duration` est exclue du modèle car elle est connue après l'appel et provoquerait une fuite d'information dans une logique de priorisation pré-contact.

## Résultats clés et recommandations

Le résultat de campagne précédente est le signal descriptif le plus marqué. Il peut servir à construire une règle de suivi commercial, mais il ne prouve pas que le résultat passé cause la souscription. Le nombre de contacts est également associé à une baisse du taux observé : **13,04 %** après un contact contre **4,61 %** pour sept contacts ou plus. Ce résultat doit être interprété avec prudence, car les campagnes plus longues peuvent cibler des profils plus difficiles.

La recommandation est de commencer par une segmentation de suivi fondée sur l'issue précédente, de suivre le volume avec chaque taux de conversion et de tester les campagnes par groupe d'âge sans exclure automatiquement les autres catégories. Le modèle peut aider à classer des contacts pour une revue humaine ; il ne doit pas décider seul d'une offre ou d'un refus.

## Aperçu des graphiques

Les sorties sont dans `visuals/` : conversion par mois, métier, issue précédente, groupe d'âge, nombre de contacts, distribution des probabilités et courbe précision-rappel. Les fichiers CSV correspondants sont dans `results/`.

## Statut qualité

**Automatisé : PASS**, sous réserve de l'exécution de `python scripts/run_all.py`. **Manuel Power BI : à faire.** Les contrôles de relations, filtres, interactions, export PDF et cohérence visuelle sont listés dans `qa/CHECKLIST.md` et `qa/INTERACTION_TESTS.md`.

## Dashboard Power BI

Le dashboard à construire comporte trois pages : vue exécutive, segmentation et priorisation contrôlée. Le plan détaillé, les mesures DAX, l'import Power Query et la procédure d'export sont dans `powerbi/` et `model/`.

## Reproduire

Depuis ce dossier :

```bash
python -m pip install -r requirements.txt
python scripts/run_all.py
```

Le pipeline régénère les tables de `data/processed/`, les agrégats de `results/` et les graphiques de `visuals/`. Les requêtes SQLite de contrôle sont dans `sql/`.

## Contenu du dossier

`data/` contient la source, le dictionnaire et les tables préparées. `scripts/` contient le pipeline. `results/` et `visuals/` contiennent les sorties. `model/` et `powerbi/` préparent le dashboard. `qa/` sépare les contrôles automatisés des vérifications manuelles.
