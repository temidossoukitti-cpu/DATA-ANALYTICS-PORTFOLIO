# Source des données

## Origine

Jeu **Default of Credit Card Clients**, fourni par l’UCI Machine Learning Repository. Les observations concernent 30 000 clients de cartes de crédit à Taïwan et des comportements de paiement d’avril à septembre 2005. La cible porte sur le défaut du mois suivant.

- Fiche officielle : https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
- DOI : https://doi.org/10.24432/C55S3H
- Fichier brut conservé sans modification : `default_of_credit_card_clients.xls`
- URL officielle de téléchargement utilisée : https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls
- Date d’accès : 2026-10-31
- Taille du fichier brut : 5 539 328 octets
- SHA-256 : `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933`

## Licence et attribution

La fiche UCI indique : “This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license. This allows for the sharing and adaptation of the datasets for any purpose, provided that the appropriate credit is given.” Le fichier brut peut donc être redistribué avec l’attribution appropriée.

Citation à conserver : Yeh, I. (2009). *Default of Credit Card Clients* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C55S3H.

Le fichier XLS a une première ligne de métadonnées X1–X23, puis une ligne d’en-tête métier. Le script lit la feuille avec `header=1`; le fichier original n’est jamais réécrit.

## Limites de provenance

Les données sont historiques et se rapportent à un établissement taïwanais en 2005. La représentativité pour d’autres pays, périodes ou politiques de crédit n’est pas établie. Les codes de remboursement `-2` et `0` ne sont pas définis par la description UCI consultée; leur interprétation dans ce projet est explicitement traitée comme une hypothèse documentée dans `DATA_DICTIONARY.md`.
