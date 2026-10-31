# Power Query

## Paramètre requis

Créer un paramètre texte `DataFolder` dans **Gérer les paramètres**. Sa valeur est le dossier racine du projet sur l’ordinateur de Samuel et se termine par le séparateur de dossier reconnu par sa plateforme. Les requêtes ci-dessous composent des chemins relatifs; aucun chemin de disque ou de profil n’est codé dans le projet.

## Fonction de chargement CSV

```powerquery
(DataFolder as text, RelativeFileName as text) as table =>
let
    Source = Csv.Document(
        File.Contents(DataFolder & RelativeFileName),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
in
    Headers
```

Créer une requête `LoadCsv` à partir de cette fonction, puis les requêtes de tables :

```powerquery
FactClients = LoadCsv(DataFolder, "data/processed/fact_clients.csv"),
DimAgeBand = LoadCsv(DataFolder, "data/processed/dim_age_band.csv"),
DimEducation = LoadCsv(DataFolder, "data/processed/dim_education.csv"),
DimMarriage = LoadCsv(DataFolder, "data/processed/dim_marriage.csv"),
DimLimitBand = LoadCsv(DataFolder, "data/processed/dim_limit_band.csv"),
DimPayStatus = LoadCsv(DataFolder, "data/processed/dim_pay_status.csv"),
DimRiskBand = LoadCsv(DataFolder, "data/processed/dim_risk_band.csv"),
ModelScorecard = LoadCsv(DataFolder, "data/processed/model_scorecard.csv")
```

Les sept premières tables forment le schéma en étoile; `ModelScorecard` est une table auxiliaire déconnectée d’une ligne. Appliquer les types indiqués dans `model/DATA_MODEL.md`. Désactiver le chargement de la fonction `LoadCsv`; conserver le chargement des tables. Ne pas importer les autres sorties d’analyse comme tables métier.

## Relations à créer dans le modèle

`fact_clients` est la table centrale. Relier chacune des six dimensions à sa clé étrangère correspondante dans le fait, en cardinalité un-à-plusieurs et avec un filtrage simple de la dimension vers le fait. `model_scorecard` est sans relation. Créer séparément `_Mesures` et `Param_LGD` dans Power BI Desktop; les deux tables sont décrites dans `model/DAX_MEASURES.md`.
