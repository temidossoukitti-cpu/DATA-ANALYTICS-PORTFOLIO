# Guide complet Power BI Desktop - Retail Sales Dashboard

Ce document doit être suivi sur Windows, ligne par ligne, pour créer le fichier
Power BI `retail_sales_dashboard.pbix`.

## 1. Fichiers nécessaires

Avant de commencer, vérifier que le projet contient les fichiers suivants :

| Fichier | Utilisation |
|:--|:--|
| `data/processed/superstore_clean.csv` | Données du dashboard |
| `dashboard/power_query_sales.m` | Importation et typage automatique du CSV |
| `dashboard/measures.dax` | Table calendrier, colonnes et mesures |
| `dashboard/retail_executive_theme.json` | Thème Power BI |
| `dashboard/retail_dashboard_background.png` | Fond de page 1440 x 900 |
| `dashboard/dashboard_design.md` | Positions détaillées des visuels |

Le fichier `retail_dashboard_background.svg` sert uniquement à modifier le
design du fond. Il n'est pas nécessaire pour construire le rapport Power BI.

## 2. Préparer le chemin du projet

1. Copier le projet complet sur l'ordinateur Windows.
2. Ouvrir l'Explorateur de fichiers.
3. Aller dans :

```text
Retail-Sales-Analysis\data\processed\
```

4. Faire `Maj + clic droit` sur `superstore_clean.csv`.
5. Choisir **Copier en tant que chemin d'accès**.
6. Conserver ce chemin. Il sera utilisé dans Power Query.

Exemple :

```text
C:\Users\Samuel\Documents\Retail-Sales-Analysis\data\processed\superstore_clean.csv
```

## 3. Créer le rapport Power BI

1. Ouvrir **Power BI Desktop**.
2. Sélectionner **Rapport vide**.
3. Cliquer sur **Fichier > Enregistrer sous**.
4. Aller dans le dossier :

```text
Retail-Sales-Analysis\dashboard\
```

5. Enregistrer le rapport sous :

```text
retail_sales_dashboard.pbix
```

## 4. Importer les données avec Power Query

Cette méthode utilise le fichier `power_query_sales.m` et automatise les types
des colonnes.

### 4.1 Ouvrir Power Query

1. Dans Power BI Desktop, ouvrir l'onglet **Accueil**.
2. Cliquer sur **Transformer les données**.
3. L'éditeur Power Query s'ouvre.

### 4.2 Créer le paramètre CsvPath

1. Dans Power Query, ouvrir **Accueil > Gérer les paramètres**.
2. Cliquer sur **Nouveau paramètre**.
3. Renseigner :

| Propriété | Valeur |
|:--|:--|
| Nom | `CsvPath` |
| Description | `Chemin du fichier Superstore nettoyé` |
| Type | Texte |
| Valeurs suggérées | Toute valeur |
| Valeur actuelle | Chemin complet du CSV |

Exemple de valeur actuelle :

```text
C:\Users\Samuel\Documents\Retail-Sales-Analysis\data\processed\superstore_clean.csv
```

Ne pas ajouter manuellement de guillemets autour du chemin dans le champ du
paramètre.

4. Cliquer sur **OK**.

### 4.3 Créer la requête Sales

1. Dans Power Query, cliquer sur **Accueil > Nouvelle source > Requête vide**.
2. Dans le volet de gauche, faire un clic droit sur la nouvelle requête.
3. Choisir **Renommer**.
4. Entrer exactement :

```text
Sales
```

5. Avec la requête `Sales` sélectionnée, cliquer sur **Accueil > Éditeur
   avancé**.
6. Supprimer tout le contenu de l'éditeur.
7. Ouvrir le fichier :

```text
dashboard\power_query_sales.m
```

8. Copier tout son contenu.
9. Coller le contenu dans l'éditeur avancé.
10. Cliquer sur **Terminé**.

La prévisualisation doit présenter les 22 colonnes du fichier Superstore.

### 4.4 Vérifier les types

Vérifier les icônes de type dans les en-têtes :

| Colonnes | Type attendu |
|:--|:--|
| `Order Date`, `Ship Date` | Date |
| `Sales`, `Discount`, `Profit` | Nombre décimal |
| `Quantity`, `Row ID` | Nombre entier |
| `Postal Code` | Texte |
| `Potential Duplicate` | Vrai/Faux |
| Autres colonnes | Texte |

Si la requête affiche une erreur de chemin :

1. Ouvrir **Gérer les paramètres**.
2. Modifier la valeur de `CsvPath`.
3. Vérifier que le chemin pointe bien vers `superstore_clean.csv`.

### 4.5 Charger les données

1. Cliquer sur **Accueil > Fermer et appliquer**.
2. Attendre la fin du chargement.
3. Dans le volet des données de Power BI, vérifier que la table `Sales`
   apparaît.

Ne pas importer une deuxième fois le CSV avec **Texte/CSV**. La requête
`Sales` réalise déjà cet import.

## 5. Créer la table calendrier

Le fichier `measures.dax` contient plusieurs formules différentes. Il ne faut
pas coller tout le fichier en une seule fois.

### 5.1 Créer la table Date

1. Dans Power BI, ouvrir l'onglet **Modélisation**.
2. Cliquer sur **Nouvelle table**.
3. Coller :

```dax
Date =
VAR MinOrderDate = MIN ( Sales[Order Date] )
VAR MaxOrderDate = MAX ( Sales[Order Date] )
RETURN
    CALENDAR (
        DATE ( YEAR ( MinOrderDate ), 1, 1 ),
        DATE ( YEAR ( MaxOrderDate ), 12, 31 )
    )
```

4. Valider avec `Entrée`.
5. Vérifier que la table `Date` apparaît dans le volet des données.

### 5.2 Créer les colonnes de la table Date

Sélectionner la table `Date`, puis utiliser **Outils de table > Nouvelle
colonne** pour chaque formule suivante.

Créer la colonne `Year` :

```dax
Year = YEAR ( Date[Date] )
```

Créer la colonne `Month Number` :

```dax
Month Number = MONTH ( Date[Date] )
```

Créer la colonne `Month` :

```dax
Month = FORMAT ( Date[Date], "MMM" )
```

Créer la colonne `Month Full` :

```dax
Month Full = FORMAT ( Date[Date], "MMMM" )
```

Créer la colonne `Month Start` :

```dax
Month Start = DATE ( YEAR ( Date[Date] ), MONTH ( Date[Date] ), 1 )
```

Créer la colonne `Year Month` :

```dax
Year Month = FORMAT ( Date[Date], "YYYY-MMM" )
```

Créer la colonne `Year Month Sort` :

```dax
Year Month Sort = YEAR ( Date[Date] ) * 100 + MONTH ( Date[Date] )
```

Créer la colonne `Quarter` :

```dax
Quarter = "Q" & FORMAT ( Date[Date], "Q" )
```

## 6. Configurer les tris de dates

### 6.1 Trier les mois

1. Sélectionner `Date[Month]`.
2. Ouvrir **Outils de colonne**.
3. Cliquer sur **Trier par colonne**.
4. Choisir `Month Number`.

### 6.2 Trier les années-mois

1. Sélectionner `Date[Year Month]`.
2. Ouvrir **Outils de colonne**.
3. Cliquer sur **Trier par colonne**.
4. Choisir `Year Month Sort`.

Cette étape évite que les mois soient classés par ordre alphabétique.

## 7. Créer la relation entre Date et Sales

1. Cliquer sur l'icône **Modèle** dans la barre verticale de gauche.
2. Repérer les tables `Date` et `Sales`.
3. Faire glisser `Date[Date]` sur `Sales[Order Date]`.
4. Configurer la relation :

| Option | Valeur |
|:--|:--|
| Table principale | `Date` |
| Colonne principale | `Date` |
| Table liée | `Sales` |
| Colonne liée | `Order Date` |
| Cardinalité | Un à plusieurs `(1:*)` |
| Direction du filtre croisé | Simple |
| Rendre cette relation active | Oui |

5. Cliquer sur **OK**.

## 8. Marquer la table Date

1. Sélectionner la table `Date`.
2. Ouvrir **Outils de table**.
3. Cliquer sur **Marquer comme table de dates**.
4. Choisir la colonne `Date[Date]`.
5. Valider.

## 9. Créer les mesures

Pour chaque mesure :

1. Sélectionner la table `Sales`.
2. Cliquer sur **Modélisation > Nouvelle mesure**.
3. Coller une seule formule.
4. Valider avec `Entrée`.

### 9.1 Mesures principales

```dax
Total Sales =
SUM ( Sales[Sales] )
```

```dax
Total Profit =
SUM ( Sales[Profit] )
```

```dax
Profit Margin =
DIVIDE ( [Total Profit], [Total Sales] )
```

```dax
Orders =
DISTINCTCOUNT ( Sales[Order ID] )
```

```dax
Customers =
DISTINCTCOUNT ( Sales[Customer ID] )
```

### 9.2 Mesures complémentaires

```dax
Average Discount =
AVERAGE ( Sales[Discount] )
```

```dax
Average Order Value =
DIVIDE ( [Total Sales], [Orders] )
```

```dax
Profit per Order =
DIVIDE ( [Total Profit], [Orders] )
```

```dax
Sales LY =
CALCULATE ( [Total Sales], DATEADD ( Date[Date], -1, YEAR ) )
```

```dax
Sales YoY =
DIVIDE ( [Total Sales] - [Sales LY], [Sales LY] )
```

```dax
Profit LY =
CALCULATE ( [Total Profit], DATEADD ( Date[Date], -1, YEAR ) )
```

```dax
Profit YoY =
DIVIDE ( [Total Profit] - [Profit LY], [Profit LY] )
```

```dax
Customer Sales Rank =
RANKX (
    ALLSELECTED ( Sales[Customer Name] ),
    [Total Sales],
    ,
    DESC,
    DENSE
)
```

```dax
Top 10 Customer Sales =
IF ( [Customer Sales Rank] <= 10, [Total Sales] )
```

```dax
Profit Status Color =
IF ( [Total Profit] < 0, "#D95D5D", "#2A9D6F" )
```

```dax
Margin Status Color =
SWITCH (
    TRUE (),
    [Profit Margin] < 0, "#D95D5D",
    [Profit Margin] < 0.10, "#E0A458",
    "#2A9D6F"
)
```

```dax
Selected Period =
VAR MinVisibleDate = MIN ( Date[Date] )
VAR MaxVisibleDate = MAX ( Date[Date] )
RETURN
    FORMAT ( MinVisibleDate, "MMM YYYY" )
        & " - "
        & FORMAT ( MaxVisibleDate, "MMM YYYY" )
```

## 10. Formater les mesures

Sélectionner chaque mesure dans le volet des données, puis utiliser les options
de format disponibles dans **Outils de mesure**.

| Mesure | Format |
|:--|:--|
| `Total Sales` | Devise USD, 0 ou 2 décimales |
| `Total Profit` | Devise USD, 0 ou 2 décimales |
| `Sales LY` | Devise USD |
| `Profit LY` | Devise USD |
| `Average Order Value` | Devise USD |
| `Profit per Order` | Devise USD |
| `Profit Margin` | Pourcentage, 1 décimale |
| `Average Discount` | Pourcentage, 1 décimale |
| `Sales YoY` | Pourcentage, 1 décimale |
| `Profit YoY` | Pourcentage, 1 décimale |
| `Orders` | Nombre entier |
| `Customers` | Nombre entier |
| `Customer Sales Rank` | Nombre entier |

## 11. Masquer les champs techniques

Dans le volet des données, faire un clic droit puis **Masquer dans la vue
Rapport** sur :

- `Sales[Row ID]` ;
- `Sales[Customer ID]` ;
- `Sales[Product ID]` ;
- `Sales[Potential Duplicate]` ;
- `Date[Month Number]` ;
- `Date[Year Month Sort]`.

Ne pas supprimer ces colonnes.

## 12. Importer le thème Power BI

1. Ouvrir l'onglet **Affichage**.
2. Cliquer sur la flèche du menu **Thèmes**.
3. Choisir **Rechercher des thèmes** ou **Parcourir les thèmes**.
4. Sélectionner :

```text
Retail-Sales-Analysis\dashboard\retail_executive_theme.json
```

5. Valider l'importation.

Le thème configure les couleurs, la typographie et une partie du format des
visuels.

## 13. Configurer la taille de la page

1. Revenir dans la vue **Rapport**.
2. Cliquer sur une zone vide de la page.
3. Ouvrir le volet **Mettre en forme la page**.
4. Ouvrir **Paramètres du canevas**.
5. Choisir le type **Personnalisé**.
6. Entrer :

| Paramètre | Valeur |
|:--|--:|
| Largeur | `1440` |
| Hauteur | `900` |

## 14. Ajouter le fond du dashboard

1. Rester dans **Mettre en forme la page**.
2. Ouvrir **Arrière-plan du canevas**.
3. Activer l'image d'arrière-plan.
4. Cliquer sur **Parcourir**.
5. Sélectionner :

```text
Retail-Sales-Analysis\dashboard\retail_dashboard_background.png
```

6. Régler :

| Option | Valeur |
|:--|:--|
| Ajustement de l'image | Ajuster / Fit |
| Transparence | `0 %` |

Les cadres et les titres des graphiques sont déjà présents dans cette image.

## 15. Créer les cinq segments de filtre

Ajouter cinq visuels **Segment** ou **Slicer**.

| Filtre | Champ | Position `x, y, largeur, hauteur` |
|:--|:--|:--|
| Année | `Date[Year]` | `26, 168, 168, 34` |
| Région | `Sales[Region]` | `26, 250, 168, 34` |
| Segment | `Sales[Segment]` | `26, 332, 168, 34` |
| Catégorie | `Sales[Category]` | `26, 414, 168, 34` |
| Mode de livraison | `Sales[Ship Mode]` | `26, 496, 168, 34` |

Pour chaque segment :

1. Sélectionner le visuel.
2. Ouvrir **Mettre en forme le visuel**.
3. Choisir le style **Liste déroulante**.
4. Activer la sélection multiple.
5. Activer l'option **Sélectionner tout**.
6. Désactiver le titre natif.
7. Désactiver l'arrière-plan.
8. Désactiver la bordure.
9. Utiliser du texte blanc.

## 16. Créer les cinq cartes KPI

Ajouter cinq visuels **Carte (nouvelle)**.

| Carte | Mesure | Position `x, y, largeur, hauteur` |
|:--|:--|:--|
| Chiffre d'affaires | `[Total Sales]` | `254, 126, 198, 66` |
| Profit total | `[Total Profit]` | `492, 126, 198, 66` |
| Marge | `[Profit Margin]` | `730, 126, 198, 66` |
| Commandes | `[Orders]` | `968, 126, 198, 66` |
| Clients | `[Customers]` | `1206, 126, 200, 66` |

Pour chaque carte :

1. Mettre uniquement la mesure indiquée.
2. Désactiver l'étiquette de catégorie.
3. Désactiver le titre natif.
4. Désactiver l'arrière-plan.
5. Désactiver la bordure.
6. Désactiver l'ombre.
7. Régler la valeur principale autour de `28 px`.

Pour `Total Sales` et `Total Profit`, utiliser les unités d'affichage
**Millions** si les valeurs prennent trop de place.

## 17. Créer la tendance des ventes

1. Ajouter un **Graphique en courbes**.
2. Position : `254, 270, 550, 182`.
3. Configurer :

| Zone | Champ |
|:--|:--|
| Axe X | `Date[Year Month]` |
| Axe Y | `[Total Sales]` |
| Infobulles | `[Total Sales]`, `[Sales LY]`, `[Sales YoY]`, `[Orders]` |

4. Trier `Year Month` dans l'ordre croissant.
5. Utiliser la couleur `#1F7A8C`.
6. Régler l'épaisseur de la ligne autour de `3 px`.
7. Désactiver les marqueurs.
8. Désactiver le titre, le fond et la bordure.

## 18. Créer la tendance du profit

1. Ajouter un **Graphique en courbes**.
2. Position : `844, 270, 562, 182`.
3. Configurer :

| Zone | Champ |
|:--|:--|
| Axe X | `Date[Year Month]` |
| Axe Y | `[Total Profit]` |
| Infobulles | `[Total Profit]`, `[Profit LY]`, `[Profit YoY]`, `[Profit Margin]` |

4. Utiliser la couleur `#2A9D6F`.
5. Dans le volet **Analytique**, ajouter une ligne constante à `0`.
6. Désactiver le titre, le fond et la bordure.

## 19. Créer les ventes par catégorie

1. Ajouter un **Graphique en anneau**.
2. Position : `254, 530, 345, 132`.
3. Configurer :

| Zone | Champ |
|:--|:--|
| Légende | `Sales[Category]` |
| Valeurs | `[Total Sales]` |
| Infobulles | `[Total Sales]`, `[Total Profit]`, `[Profit Margin]`, `[Orders]` |

4. Utiliser les couleurs :

| Catégorie | Couleur |
|:--|:--|
| Technology | `#1F7A8C` |
| Office Supplies | `#2A9D6F` |
| Furniture | `#E0A458` |

5. Afficher la catégorie et le pourcentage du total.
6. Désactiver le titre, le fond et la bordure.

## 20. Créer le profit par sous-catégorie

1. Ajouter un **Graphique à barres groupées** horizontal.
2. Position : `639, 530, 445, 132`.
3. Configurer :

| Zone | Champ |
|:--|:--|
| Axe Y | `Sales[Sub-Category]` |
| Axe X | `[Total Profit]` |
| Infobulles | `[Total Sales]`, `[Total Profit]`, `[Profit Margin]`, `[Average Discount]` |

4. Trier par `[Total Profit]` en ordre décroissant.
5. Activer les étiquettes de données.
6. Utiliser le vert pour les profits positifs.
7. Utiliser le rouge `#D95D5D` pour les profits négatifs.
8. Ajouter une ligne constante à `0`.
9. Désactiver le titre, le fond et la bordure.

## 21. Créer le profit par région

1. Ajouter un **Graphique à barres groupées** horizontal.
2. Position : `1124, 530, 282, 132`.
3. Configurer :

| Zone | Champ |
|:--|:--|
| Axe Y | `Sales[Region]` |
| Axe X | `[Total Profit]` |
| Infobulles | `[Total Sales]`, `[Total Profit]`, `[Profit Margin]`, `[Orders]` |

4. Trier par `[Total Profit]` en ordre décroissant.
5. Utiliser la couleur `#5B6C8F`.
6. Activer les étiquettes de données.
7. Désactiver le titre, le fond et la bordure.

## 22. Créer le Top 10 clients

1. Ajouter un **Graphique à barres groupées** horizontal.
2. Position : `254, 740, 550, 126`.
3. Configurer :

| Zone | Champ |
|:--|:--|
| Axe Y | `Sales[Customer Name]` |
| Axe X | `[Top 10 Customer Sales]` |
| Infobulles | `[Total Sales]`, `[Total Profit]`, `[Profit Margin]`, `[Orders]` |

4. Dans les filtres du visuel, ajouter `[Customer Sales Rank]`.
5. Configurer le filtre sur **inférieur ou égal à 10**.
6. Trier par `[Top 10 Customer Sales]` en ordre décroissant.
7. Utiliser la couleur `#1F7A8C`.
8. Activer les étiquettes de données.
9. Désactiver le titre, le fond et la bordure.

## 23. Créer le graphique remise contre profit

1. Ajouter un **Nuage de points**.
2. Position : `844, 740, 562, 126`.
3. Configurer :

| Zone | Champ |
|:--|:--|
| Axe X | `[Average Discount]` |
| Axe Y | `[Total Profit]` |
| Taille | `[Total Sales]` |
| Détails | `Sales[Sub-Category]` |
| Légende | `Sales[Category]` |
| Infobulles | `Sales[Sub-Category]`, `[Average Discount]`, `[Total Sales]`, `[Total Profit]`, `[Profit Margin]` |

4. Formater l'axe X en pourcentage.
5. Régler approximativement l'axe X de `0` à `0,70`.
6. Ajouter une ligne constante à `0` sur l'axe du profit.
7. Dans le volet **Analytique**, ajouter une ligne de tendance si elle est
   disponible.
8. Désactiver le titre, le fond et la bordure.

## 24. Configurer les interactions

### 24.1 Segments

Les cinq segments doivent filtrer :

- les cinq cartes KPI ;
- les deux graphiques de tendance ;
- les graphiques catégorie, sous-catégorie et région ;
- le Top 10 clients ;
- le nuage de points.

### 24.2 Graphiques

Pour configurer une interaction :

1. Sélectionner un graphique.
2. Ouvrir **Format > Modifier les interactions**.
3. Sur les autres visuels, choisir l'icône **Filtrer**.
4. Éviter l'option de simple surbrillance lorsque le KPI doit être recalculé.

Les graphiques doivent principalement utiliser l'interaction **Filtrer**.

## 25. Vérifier les valeurs globales

Supprimer temporairement toutes les sélections des segments.

Les résultats doivent être :

| KPI | Valeur attendue |
|:--|--:|
| Chiffre d'affaires | `2 297 200,86 $` |
| Profit total | `286 397,02 $` |
| Marge bénéficiaire | `12,5 %` |
| Commandes | `5 009` |
| Clients | `793` |

Si le nombre de commandes est supérieur à `5 009`, vérifier que la mesure
utilise bien `DISTINCTCOUNT` sur `Sales[Order ID]`.

Si le nombre de clients est supérieur à `793`, vérifier que la mesure utilise
bien `DISTINCTCOUNT` sur `Sales[Customer ID]`.

Si la marge est incorrecte, vérifier qu'elle est calculée avec :

```dax
Profit Margin =
DIVIDE ( [Total Profit], [Total Sales] )
```

## 26. Contrôle visuel final

Vérifier les points suivants :

- aucun visuel ne dépasse de son cadre ;
- les titres natifs sont désactivés ;
- les fonds des visuels sont transparents ;
- les valeurs négatives apparaissent en rouge ;
- l'axe des mois est chronologique ;
- le Top 10 change lorsque les segments sont utilisés ;
- toutes les cartes changent lorsque les filtres sont utilisés ;
- les montants sont affichés en USD ;
- les textes restent lisibles à 100 % de zoom.

## 27. Enregistrer le rapport

1. Cliquer sur **Fichier > Enregistrer**.
2. Vérifier que le fichier se trouve dans :

```text
Retail-Sales-Analysis\dashboard\retail_sales_dashboard.pbix
```

Le rapport Power BI est alors terminé.

## 28. Résumé de l'ordre à respecter

Cocher chaque étape :

- [ ] Copier le projet sur Windows.
- [ ] Créer et enregistrer le fichier `.pbix`.
- [ ] Créer le paramètre `CsvPath`.
- [ ] Créer la requête `Sales` avec `power_query_sales.m`.
- [ ] Charger les données.
- [ ] Créer la table `Date`.
- [ ] Créer les huit colonnes de date.
- [ ] Configurer les deux tris.
- [ ] Créer la relation `Date` vers `Sales`.
- [ ] Marquer `Date` comme table de dates.
- [ ] Créer toutes les mesures.
- [ ] Formater les mesures.
- [ ] Importer le thème JSON.
- [ ] Régler la page sur `1440 x 900`.
- [ ] Ajouter le fond PNG.
- [ ] Créer les cinq segments.
- [ ] Créer les cinq cartes KPI.
- [ ] Créer les sept graphiques.
- [ ] Configurer les interactions.
- [ ] Vérifier les cinq valeurs globales.
- [ ] Enregistrer `retail_sales_dashboard.pbix`.
