# Power Query — chargement des tables

Créer dans Power BI Desktop un paramètre texte nommé `DataFolder`. Sa valeur est le dossier `data/processed` de cette copie du dépôt; ne pas inscrire de chemin de poste dans le code M. Le dossier doit être configuré sans séparateur final. Les tables sont des CSV générés par le pipeline.

Créer une requête fonction `LoadCsv` :

```powerquery
(fileName as text) as table =>
let
    Source = Csv.Document(
        File.Contents(DataFolder & "/" & fileName),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
in
    Promoted
```

Créer les sept requêtes ci-dessous; les types sont explicites pour éviter les conversions automatiques ambiguës.

```powerquery
// dim_fiscal_year
let
    Source = LoadCsv("dim_fiscal_year.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"fiscal_year", Int64.Type}, {"period_end", type text}, {"label_fr", type text}, {"sort_order", Int64.Type}}),
    Renamed = Table.RenameColumns(Typed, {{"fiscal_year", "fiscal_year_key"}})
in Renamed
```

```powerquery
// dim_metric
let
    Source = LoadCsv("dim_metric.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"metric_key", type text}, {"label_fr", type text}, {"statement", type text}, {"unit", type text}, {"definition", type text}, {"sort_order", Int64.Type}})
in Typed
```

```powerquery
// dim_ratio
let
    Source = LoadCsv("dim_ratio.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"ratio_key", type text}, {"label_fr", type text}, {"category", type text}, {"unit", type text}, {"definition", type text}, {"formula", type text}, {"sort_order", Int64.Type}})
in Typed
```

```powerquery
// fact_financials
let
    Source = LoadCsv("fact_financials.csv"),
    Selected = Table.SelectColumns(Source, {"fiscal_year_key", "metric_key", "value"}),
    Typed = Table.TransformColumnTypes(Selected, {{"fiscal_year_key", Int64.Type}, {"metric_key", type text}, {"value", type number}})
in Typed
```

```powerquery
// fact_ratios
let
    Source = LoadCsv("fact_ratios.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"fiscal_year_key", Int64.Type}, {"ratio_key", type text}, {"value", type number}})
in Typed
```

```powerquery
// financial_scorecard
let
    Source = LoadCsv("financial_scorecard.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"entity", type text}, {"latest_year", Int64.Type}, {"revenue", type number}, {"operating_income", type number}, {"net_income", type number}, {"operating_margin", type number}, {"net_margin", type number}, {"roe", type number}, {"roa", type number}, {"current_ratio", type number}, {"debt_ratio", type number}, {"fcf", type number}, {"fcf_margin", type number}, {"eps_diluted", type number}, {"revenue_cagr", type number}, {"net_income_cagr", type number}, {"period_start", Int64.Type}, {"period_end", Int64.Type}})
in Typed
```

```powerquery
// financial_alerts
let
    Source = LoadCsv("financial_alerts.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"alert_key", type text}, {"label_fr", type text}, {"unit", type text}, {"threshold", type number}, {"observed", type number}, {"status", type text}, {"definition", type text}})
in Typed
```

Après chargement, créer dans Power BI les relations indiquées dans `model/DATA_MODEL.md`, trier `dim_fiscal_year[label_fr]` par `sort_order` et désactiver le filtre bidirectionnel. La source étant annuelle, aucun calendrier quotidien n’est à créer.
