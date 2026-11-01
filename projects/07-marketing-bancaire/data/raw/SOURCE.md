# Source des données

## Source principale

- **Nom :** UCI Bank Marketing
- **Producteur :** Moro, Rita et Cortez
- **Dépôt officiel :** [UCI Machine Learning Repository — Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing)
- **DOI :** [10.24432/C5K306](https://doi.org/10.24432/C5K306)
- **Fichier utilisé :** `bank-additional-full.csv`
- **Période indiquée par UCI :** mai 2008 à novembre 2010
- **Taille utilisée :** 41 188 lignes et 21 colonnes
- **Licence :** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Empreinte SHA-256 :** générée dans `results/source_integrity.csv`

## Usage dans ce projet

Le fichier est conservé dans son format brut. L'analyse étudie le résultat de campagnes de marketing téléphonique d'une banque portugaise et la souscription d'un dépôt à terme (`y`). Les variables démographiques servent à décrire des segments, pas à justifier une décision automatisée sur une personne.

Le modèle logistique exclut `duration` car cette variable est connue après l'appel et créerait une fuite d'information si l'objectif est de prioriser les contacts avant leur résultat. Les doublons exacts sont conservés dans l'analyse descriptive et regroupés dans le découpage train/test afin d'éviter qu'une même observation dupliquée traverse les deux échantillons.

## Attribution

Moro, S., Rita, P., & Cortez, P. (2014). *Bank Marketing*. UCI Machine Learning Repository. https://doi.org/10.24432/C5K306
