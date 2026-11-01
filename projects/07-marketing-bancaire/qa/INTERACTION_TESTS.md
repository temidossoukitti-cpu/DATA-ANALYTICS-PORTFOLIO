# Tests d’interaction Power BI

Les tests sont à exécuter après construction du rapport. Le résultat doit être noté avec la date et la version de Power BI Desktop.

| Test | Attendu |
|---|---|
| Aucun filtre | 41 188 campagnes, 4 640 souscriptions, conversion 11,27 % |
| Filtre mois = mars | Les cartes et les visuels se recalculent sur le mois sélectionné |
| Filtre issue précédente = succès | Le taux affiché correspond au segment `Succès` de `conversion_by_poutcome.csv` |
| Filtre métier = retraité | Les cartes et le graphique par métier restent cohérents |
| Réinitialisation | Retour aux KPI globaux et aux segments par défaut |
| Navigation entre pages | Les filtres persistants et les titres restent compréhensibles |
