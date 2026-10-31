# Source des données

## Jeu de données et accès

Le projet utilise l’API publique **SEC EDGAR companyfacts** pour l’entité **Mastercard Incorporated**, identifiant central (CIK) **1141391**. Le fichier JSON téléchargé correspond à l’URL `https://data.sec.gov/api/xbrl/companyfacts/CIK0001141391.json` et pèse **4 182 087 octets**; son SHA-256 est `eec2f64179fe268380a6f9f4b5e3da53a9c1c5adb988aa31cc40c8372c0d8899`. Ces valeurs portent sur le fichier brut conservé dans `data/raw/mastercard_companyfacts.json` [1].

L’extraction retient les dépôts **10-K** annuels de formulaire et de période **FY**, avec une clôture au **31 décembre**. La période analysée couvre les exercices **2019 à 2025**, soit sept exercices. Les montants sont exprimés en **dollars américains** (USD), les actions en **millions** et le bénéfice par action en **USD par action**.

## Licence et redistribution

Les dépôts déposés auprès de la SEC sont des documents publics. L’API companyfacts expose les faits XBRL déjà déposés; aucune licence commerciale n’est requise pour les consulter. Le fichier brut est conservé tel quel afin de permettre la vérification des valeurs extraites. Les résultats du projet ne constituent ni une recommandation d’investissement ni une opinion sur la valeur de l’entreprise.

## Extraction et contrôle

Le script `scripts/01_clean.py` lit le JSON brut, sélectionne pour chaque indicateur la dernière valeur déposée pour chaque exercice clos au 31 décembre et construit une table de faits annuelle. Les contrôles portent sur l’identité de l’entité, la présence des quinze indicateurs sur les sept exercices, l’unicité de la clé (exercice, indicateur), la positivité des produits, de l’actif et des capitaux propres, la cohérence du bilan et le rapprochement du bénéfice par action avec le résultat net divisé par les actions diluées.

Deux écarts sont documentés :

- **Identité du bilan :** l’écart maximal entre l’actif total et la somme du passif et des capitaux propres atteint **126 millions USD**, soit moins de 0,5 % du total de l’actif. Il est traité comme information et non comme erreur, l’extraction ne détaillant pas les intérêts minoritaires.
- **Bénéfice par action :** l’écart maximal entre le BPA déclaré et le rapport résultat net / actions diluées est de **0,0643 %**, sous la tolérance de 1 %.

## Limites connues

La source ne fournit **aucune segmentation par activité**, aucune ventilation géographique, aucun détail des rachats d’actions et aucune ligne d’intérêts minoritaires. Les analyses portent donc sur les états financiers consolidés annuels, sans décomposition du chiffre d’affaires. Les exercices 2019 à 2025 constituent une fenêtre courte : les tendances observées ne préjugent pas des exercices futurs.

## Références

[1]: https://data.sec.gov/api/xbrl/companyfacts/CIK0001141391.json "SEC EDGAR companyfacts, Mastercard Incorporated (CIK 1141391)"
