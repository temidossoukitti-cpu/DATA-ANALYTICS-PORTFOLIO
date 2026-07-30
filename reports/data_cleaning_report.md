# Rapport de nettoyage des donnees

## 1. Perimetre

Cette etape produit une copie nettoyee du jeu de donnees. Le fichier source
`data/raw/Sample - Superstore.csv` n'est jamais modifie.

- Fichier produit : `data/processed/superstore_clean.csv`
- Encodage de lecture : `latin-1`
- Format d'export des dates : `YYYY-MM-DD`
- Lignes avant nettoyage : **9,994**
- Lignes apres nettoyage : **9,994**
- Colonnes avant nettoyage : **21**
- Colonnes apres nettoyage : **22**

L'augmentation d'une colonne correspond uniquement a l'ajout de
`Potential Duplicate`. Aucune ligne n'a ete ajoutee ou supprimee.

## 2. Transformations effectuees

| Colonne | Transformation | Raison |
|:--|:--|:--|
| `Order Date`, `Ship Date` | Conversion de texte vers `datetime64[ns]`. | Permettre des tris et calculs temporels fiables. |
| `Postal Code` | Conversion du type numerique vers `string`. | Traiter le code postal comme un identifiant, pas une mesure. |
| Toutes les colonnes texte | Suppression des espaces en debut et fin de valeur. | Uniformiser les libelles sans modifier leur contenu utile. |
| `Potential Duplicate` | Ajout d'un indicateur booleen, sans suppression de ligne. | Signaler les lignes identiques lorsque `Row ID` est ignore. |

### Espaces supprimes

- `Product Name` : 16 valeur(s)

## 3. Verification de la qualite

| Controle | Avant | Apres |
|:--|--:|--:|
| Valeurs manquantes | 0 | 0 |
| Doublons stricts | 0 | 0 |
| Lignes conservees | 9,994 | 9,994 |

- Lignes marquees comme doublons potentiels : **2**
- Groupes de doublons potentiels : **1**
- Aucun doublon potentiel n'a ete supprime.

## 4. Verification des types

| Colonne | Type avant | Type apres |
|:--|:--|:--|
| Row ID | `int64` | `int64` |
| Order ID | `object` | `object` |
| Order Date | `object` | `datetime64[ns]` |
| Ship Date | `object` | `datetime64[ns]` |
| Ship Mode | `object` | `object` |
| Customer ID | `object` | `object` |
| Customer Name | `object` | `object` |
| Segment | `object` | `object` |
| Country | `object` | `object` |
| City | `object` | `object` |
| State | `object` | `object` |
| Postal Code | `int64` | `string` |
| Region | `object` | `object` |
| Product ID | `object` | `object` |
| Category | `object` | `object` |
| Sub-Category | `object` | `object` |
| Product Name | `object` | `object` |
| Sales | `float64` | `float64` |
| Quantity | `int64` | `int64` |
| Discount | `float64` | `float64` |
| Profit | `float64` | `float64` |
| Potential Duplicate | Non presente | `bool` |

Les types ci-dessus correspondent au DataFrame en memoire. Un fichier CSV ne
stocke pas de schema de types ; lors d'un rechargement, les colonnes de dates
et le code postal doivent donc etre explicitement declares.

## 5. Colonnes modifiees

- `Order Date`
- `Ship Date`
- `Postal Code`
- `Product Name` (16 valeurs corrigees)
- `Potential Duplicate` (nouvelle colonne)

Les autres colonnes texte ont ete controlees et normalisees avec la meme
operation de suppression des espaces peripheriques, sans changement de valeur
detecte.

## 6. Anomalies restantes

- **2 lignes** restent marquees comme
  doublons potentiels. Une validation metier est requise avant toute suppression.
- **449 codes postaux** comportent moins de cinq
  caracteres. Le fichier source les stockait deja sans zero initial ; aucun zero
  n'a ete reconstitue sans regle metier explicite.
- Colonne(s) constante(s) conservee(s) : `Country`.
- `Row ID` est conserve pour assurer la tracabilite.
- Aucune valeur manquante et aucun doublon strict ne subsistent.

## 7. Conclusion

Le nettoyage a conserve les **9,994 lignes** du fichier source.
Les transformations sont limitees aux types, a la normalisation des espaces et
a l'ajout d'un indicateur de doublon potentiel. Aucune analyse metier n'a ete
realisee.
