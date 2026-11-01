# Power Query

Le dashboard doit importer les tables préparées dans `data/processed/`. Pour conserver un modèle transférable, créer un paramètre texte `DataFolder` qui pointe vers le dossier `data/processed` du projet, puis utiliser ce paramètre pour chaque fichier CSV. Aucun chemin absolu ne doit être enregistré dans le rapport.

Exemple de fonction d'import :

```powerquery
(fileName as text) as table =>
let
    Source = Csv.Document(
        File.Contents(DataFolder & "/" & fileName),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    Headers
```

Après import, typer les clés en entier, les indicateurs en nombre décimal et `outcome_key` en entier. Charger d'abord les dimensions, puis `fact_campaign`, et créer les relations décrites dans `model/DATA_MODEL.md`.
