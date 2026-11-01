# Mesures DAX proposées

Créer une table `_Mesures` dans Power BI. Les valeurs de référence sont issues des CSV générés par le pipeline et doivent être vérifiées après import.

```DAX
Campagnes = COUNTROWS(fact_campaign)
Souscriptions = SUM(fact_campaign[outcome_key])
Taux de conversion = DIVIDE([Souscriptions], [Campagnes])
Contacts moyens = AVERAGE(fact_campaign[campaign])
Campagnes déjà contactées = SUM(fact_campaign[previously_contacted])
Taux de contact antérieur = DIVIDE([Campagnes déjà contactées], [Campagnes])
```

## Règles

Le taux de conversion est le nombre de lignes `outcome_key = 1` divisé par le nombre de lignes visibles. Les mesures ne doivent pas utiliser `duration` pour une logique de priorisation pré-contact. Les mesures de segmentation doivent conserver les catégories `unknown` et afficher le volume avec le taux afin d'éviter de surinterpréter un petit groupe.

## Références attendues

- `Campagnes` : 41 188.
- `Souscriptions` : 4 640.
- `Taux de conversion` : 11,27 %.
- Les résultats par segment proviennent des fichiers de `results/`, notamment `conversion_by_job.csv`, `conversion_by_month.csv` et `conversion_by_poutcome.csv`.
