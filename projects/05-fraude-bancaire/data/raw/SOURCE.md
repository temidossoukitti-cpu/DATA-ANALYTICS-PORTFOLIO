# Source des données

## Jeu de données et accès

Le projet utilise la version 1 du jeu OpenML **credit-card-fraud-detection**, ID **43627**. L’API OpenML indique le champ de licence `Database: Open Database, Contents: Database Contents` [1]. Le téléchargement Parquet officiel testé ne demande ni compte, ni clé API [2]. La fiche indique 284 807 transactions de septembre 2013 provenant de titulaires européens de cartes, observées sur deux jours; 492 sont étiquetées fraude [1].

Attribution à conserver : **OpenML, dataset 43627, “credit-card-fraud-detection”, version 1**, avec la source et les notices de licence indiquées dans ce fichier. La description publiée par OpenML précise que les attributs `V1` à `V28` sont des composantes principales anonymisées; elle ne fournit pas les variables d’origine ni davantage de contexte métier [1].

## Licence et redistribution

Le champ de licence OpenML distingue une base sous **Open Database License (ODbL) 1.0** et son contenu sous **Database Contents License (DbCL) 1.0** [1]. Le résumé ODbL autorise la copie, la distribution, l’utilisation, la création d’œuvres et l’adaptation, sous conditions d’attribution, de partage à l’identique pour une base adaptée rendue publique, et de maintien des notices [3]. La DbCL accorde les droits sur le contenu sous réserve du respect de l’ODbL [4].

Le Parquet complet dépasse 50 Mo et n’est pas commité. Le dépôt redistribue un échantillon déterministe de cette base, avec l’attribution et les notices ODbL/DbCL; l’échantillon et toute base adaptée publique doivent respecter les conditions de partage à l’identique applicables. La base de résultats du projet n’est pas une autorisation de retirer les notices ou les obligations de licence.

## Fichier complet et échantillon commité

Le Parquet OpenML téléchargé localement pèse **73 231 038 octets**. Son SHA-256 est `91650a62cb263b7fd76610a8f2fa55c4e861033b56dd51ed22d707838c95e0cf`. Ces valeurs portent sur le fichier complet utilisé pour créer l’échantillon; elles ne sont pas recalculées à partir du fichier échantillonné.

Le script `scripts/00_make_sample.py` conserve **toutes les lignes fraude** (Class=1), tire **25 000 lignes légitimes** (Class=0) sans remise avec `random_state=42`, puis stocke les poids d’inclusion. Chaque ligne fraude porte le poids 1; chaque ligne légitime échantillonnée porte le poids `284315 / 25000 = 11.3726`. Les résultats de population calculés une fois sur le fichier complet sont consignés dans `results/population_kpis.csv`. Le pipeline reproductible utilise ensuite uniquement `data/processed/transactions_sample.parquet`.

Pour recréer l’échantillon, télécharger le Parquet complet à partir de l’URL officielle [2] vers `data/raw/openml_43627_full.parquet`, vérifier la taille et l’empreinte ci-dessus, puis exécuter depuis la racine du projet :

```bash
python -m pip install -r requirements.txt
python scripts/00_make_sample.py --input data/raw/openml_43627_full.parquet
```

Le fichier complet local est ignoré par Git. Ne pas le commiter.

## Limites connues

Le jeu ne fournit aucun champ de type de transaction, d’identifiant de compte, de date calendaire ou de devise. `Time` est le nombre de secondes écoulées depuis la première transaction du fichier; les fenêtres temporelles du projet sont donc relatives, pas des heures civiles. `Amount` est exprimé en unités non précisées par la source et aucun symbole monétaire ne doit lui être attribué.

Le fichier complet contient 1 081 lignes répétées à l’identique (dont 19 occurrences fraude au-delà de la première). Elles sont conservées, car le fichier source ne permet pas de déterminer si ces lignes sont des répétitions de données ou des transactions distinctes ayant des attributs identiques. Les groupes de lignes identiques sont maintenus dans une seule partition du split train/test pour réduire le risque de fuite. Les résultats décrivent le jeu fourni et ne démontrent pas la représentativité de la fraude réelle hors de cette fenêtre de deux jours.

## Références

[1]: https://www.openml.org/api/v1/json/data/43627 "OpenML dataset 43627 API et description"
[2]: https://data.openml.org/datasets/0004/43627/dataset_43627.pq "Parquet officiel OpenML du dataset 43627"
[3]: https://opendatacommons.org/licenses/odbl/summary/ "Résumé officiel de l’Open Database License 1.0"
[4]: https://opendatacommons.org/licenses/dbcl/1-0/ "Database Contents License 1.0"
