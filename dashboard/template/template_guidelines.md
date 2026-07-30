# Template Power BI - Executive Analytics

## 1. Objectif et fichiers

Ce template constitue une base visuelle générique pour des dashboards
exécutifs Retail, HR, Finance, Marketing, Supply Chain, Healthcare et Sales.
Il privilégie la lecture rapide, la comparaison et l'identification des écarts.

| Fichier | Usage |
|:--|:--|
| `powerbi_theme.json` | Thème à importer dans Power BI Desktop |
| `dashboard_background.png` | Fond de page recommandé, 1440 x 900 px |
| `dashboard_background.svg` | Source vectorielle éditable du fond |

Le fond contient les cadres et titres de zones. Les visuels Power BI doivent
avoir un arrière-plan transparent, une bordure désactivée et un titre natif
désactivé.

## 2. Format et grille

- Taille de page : **personnalisée, 1440 x 900 px**.
- Dimension imposée : `1440 x 900`, soit un ratio mathématique `16:10`.
  La composition est optimisée pour rester entièrement lisible sur un écran
  `16:9`, y compris avec les contrôles Power BI visibles.
- Marge extérieure : `24 px`.
- Gouttière principale : `24 px`.
- Gouttière entre colonnes : `24 px`.
- Grille d'espacement : multiples de `4 px`, avec `8 px` comme unité standard.
- Rayon : `4-5 px`.
- Ombre : faible, noire/bleue à `7 %`, décalage vertical `2 px`, flou `3 px`.
- Aucun dégradé, motif décoratif ou effet 3D.

## 3. Palette de couleurs

### Couleurs structurelles

| Rôle | Couleur | Usage |
|:--|:--|:--|
| En-tête | `#243D4D` | Bandeau supérieur |
| Accent principal | `#176B78` | Série principale, sélection, repère |
| Texte principal | `#172B3A` | Valeurs KPI, titres, données |
| Texte secondaire | `#536572` | Axes, labels, métadonnées |
| Fond de page | `#F3F5F7` | Canvas |
| Surface | `#FFFFFF` | Panneaux et cartes |
| Surface secondaire | `#F7F8F9` | Alternance de lignes, champs |
| Séparateur | `#DDE3E7` | Grilles et séparations |

### Couleurs analytiques

| Rôle | Couleur | Usage |
|:--|:--|:--|
| Série 1 | `#176B78` | Mesure prioritaire |
| Série 2 | `#4F6B78` | Comparatif ou N-1 |
| Positif | `#2F7D62` | Objectif atteint, variation positive |
| Attention | `#A6783D` | Seuil intermédiaire |
| Négatif | `#B45454` | Sous-performance, alerte |
| Série complémentaire | `#6B6585` | Segmentation secondaire |
| Série complémentaire | `#4D7699` | Segmentation secondaire |

Règles :

- Utiliser une couleur dominante et au maximum trois couleurs de séries par
  graphique.
- Réserver vert, ambre et rouge aux statuts, jamais à la décoration.
- Ne pas utiliser uniquement la couleur pour transmettre une information :
  ajouter un signe, une étiquette ou une référence à l'objectif.
- Pour les catégories nombreuses, limiter l'affichage aux catégories majeures
  et regrouper le reste sous `Autres`.

## 4. Typographie

Police principale : **Segoe UI**, native dans Power BI et l'écosystème
Microsoft. Police de secours : Arial.

| Élément | Taille | Graisse |
|:--|--:|:--|
| Titre du dashboard | `24 px` | Semibold |
| Valeur KPI | `28 px` | Semibold |
| Titre de panneau | `12 px` | Semibold |
| En-tête de tableau | `10 px` | Semibold |
| Label / axe | `9-10 px` | Regular |
| Métadonnée / source | `9-10 px` | Regular |

- Casse phrase pour les titres, capitales uniquement pour les micro-labels.
- Une ligne maximum par titre de panneau.
- Aucun texte inférieur à `9 px`.
- Letter spacing : `0`.
- Nombres alignés à droite dans les tableaux.

## 5. Espacement

- Padding interne des panneaux : `20 px`.
- Distance titre / séparateur : `12 px`.
- Zone réservée au titre d'un panneau : `44 px`.
- Espacement label / valeur KPI : `8 px`.
- Espacement vertical entre slicers : `24 px`.
- Hauteur standard d'un slicer déroulant : `34 px`.
- Padding des lignes de tableau : `6 px`.
- Ne jamais réduire une gouttière pour faire tenir un visuel. Réduire plutôt le
  nombre d'éléments affichés.

## 6. KPI Cards

- Six cartes maximum sur une ligne.
- Taille du cadre : `212 x 104 px`.
- Valeur : `28 px`, Semibold, texte principal.
- Label : `10 px`, Semibold, texte secondaire.
- Accent vertical gauche : `4 px`.
- Comparatif sous la valeur : variation, période de référence et symbole
  directionnel. Taille `9-10 px`.
- Afficher unités et devise explicitement dans le sous-label ou le format.
- Une carte = une mesure principale. Ne pas ajouter de mini-graphique si cela
  réduit la lisibilité.
- Rouge uniquement pour une vraie exception métier. Une baisse de coût peut
  être positive selon le contexte.

Positions des visuels de valeur, à poser sous les labels du fond :

| KPI | Cadre du fond `x,y,w,h` | Zone valeur recommandée `x,y,w,h` |
|:--|:--|:--|
| KPI 01 | `24,92,212,104` | `40,126,180,58` |
| KPI 02 | `260,92,212,104` | `276,126,180,58` |
| KPI 03 | `496,92,212,104` | `512,126,180,58` |
| KPI 04 | `732,92,212,104` | `748,126,180,58` |
| KPI 05 | `968,92,212,104` | `984,126,180,58` |
| KPI 06 | `1204,92,212,104` | `1220,126,180,58` |

## 7. Graphiques

- Désactiver le titre natif et le fond du visuel.
- Garder les axes visibles seulement lorsqu'ils aident la comparaison.
- Utiliser des lignes de grille horizontales `#E7EBEE`, fines et discrètes.
- Courbe principale : `3 px`, sans marqueur sauf faible nombre de points.
- Barres : tri décroissant, orientation horizontale pour les libellés longs.
- Histogrammes : largeur de catégorie stable, espacement interne modéré.
- Donut : uniquement pour `2-5` catégories ; préférer une barre au-delà.
- Légende : en haut ou à droite, jamais flottante au centre des données.
- Data labels : activer seulement si le nombre de marques reste lisible.
- Afficher une ligne zéro pour les valeurs positives et négatives.
- Ajouter objectif, budget ou N-1 comme référence lorsque disponible.
- Tooltips : valeur, variation, période, dimension et contexte de filtre.
- Ne pas dépasser `7` couleurs visibles sur une page.

## 8. Slicers

- Style recommandé : **Dropdown**.
- Hauteur : `34 px`, bordure `#CFD8DE`, fond `#F7F8F9`.
- Label externe : `10 px`, Semibold.
- Recherche activée pour les listes textuelles longues.
- `Select all` activé pour les sélections multiples.
- Conserver le même ordre sur toutes les pages : période, géographie,
  organisation, produit/service, statut.
- Prévoir un bouton global de réinitialisation des filtres dans Power BI si le
  rapport comporte plusieurs slicers.
- Le rail du template accueille trois slicers. Pour en ajouter, utiliser un
  panneau de filtres escamotable ou une seconde page, pas une compression.

## 9. Tableaux et matrices

- En-tête `#243D4D`, texte blanc, `10 px` Semibold.
- Corps blanc avec alternance `#F7F8F9`.
- Séparateurs horizontaux uniquement.
- Libellés à gauche, nombres à droite, dates alignées de manière cohérente.
- Formats courts et homogènes : `1.2 M`, `245 k`, `12.4 %`.
- Totaux en fond `#E9EEF1`, Semibold.
- Mise en forme conditionnelle sobre : barre de données ou couleur de police,
  jamais les deux simultanément sur une même colonne.
- Pour un Top 10, afficher le rang, le libellé, la valeur, la variation et une
  mesure de contexte.

## 10. Icônes recommandées

Utiliser les icônes natives Power BI ou Microsoft Fluent UI en style
**outline**, taille `16-20 px`, épaisseur cohérente.

| Action / concept | Icône |
|:--|:--|
| Réinitialiser | Arrow counterclockwise |
| Filtrer | Filter |
| Développer | Chevron down / up |
| Information | Info |
| Exporter | Arrow download |
| Navigation | Home, arrow left, arrow right |
| Date | Calendar |
| Objectif | Target |
| Alerte | Warning |

Le dossier `icons/` n'est pas créé car le template n'embarque aucune icône
propriétaire. Cette approche évite les doublons et conserve la compatibilité
avec les bibliothèques natives.

## 11. Alignement

- Activer `View > Gridlines` et `Snap to grid` dans Power BI Desktop.
- Aligner les bords des visuels sur les coordonnées documentées.
- Utiliser `Align` et `Distribute horizontally/vertically`.
- Conserver une ligne de base commune pour les valeurs KPI.
- Ne pas centrer arbitrairement les graphiques : leurs zones de tracé doivent
  commencer sur la même verticale que les titres de panneau.
- Les titres sont alignés à gauche ; les métadonnées contextuelles à droite.
- Les marges internes gauche et droite d'un panneau sont toujours `20 px`.

## 12. Mise en page et wireframe

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ Dashboard Title                                            Reporting Period │
├───────────┬───────────┬───────────┬───────────┬───────────┬────────────────┤
│ KPI 01    │ KPI 02    │ KPI 03    │ KPI 04    │ KPI 05    │ KPI 06         │
├──────────────┬─────────────────────────────────────────────────────────────┤
│ Filters      │ Main Trend Chart                                            │
├──────────────┴────────────────────────┬────────────────────────────────────┤
│ Chart 01                              │ Chart 02                           │
├───────────────────────────────────────┼────────────────────────────────────┤
│ Chart 03                              │ Table / Top 10                     │
└───────────────────────────────────────┴────────────────────────────────────┘
```

Coordonnées des zones de contenu, hors bandeau de titre du panneau :

| Zone | Cadre du fond `x,y,w,h` | Zone visuel `x,y,w,h` |
|:--|:--|:--|
| Filters | `24,220,260,250` | `44,274,220,194` |
| Main Trend | `308,220,1108,250` | `328,274,1068,176` |
| Chart 01 | `24,494,686,178` | `44,548,646,104` |
| Chart 02 | `734,494,682,178` | `754,548,642,104` |
| Chart 03 | `24,696,686,180` | `44,750,646,106` |
| Table / Top 10 | `734,696,682,180` | `754,750,642,106` |

## 13. Réutilisation par domaine

| Domaine | KPI possibles | Visuels adaptés |
|:--|:--|:--|
| Retail | CA, marge, panier, commandes | tendance, catégorie, magasin, Top produits |
| HR | effectif, turnover, absentéisme | tendance, département, ancienneté, Top causes |
| Finance | revenu, EBITDA, cash, budget | réel vs budget, variance, P&L, centres de coût |
| Marketing | leads, CAC, ROAS, conversion | funnel, canal, campagne, Top audiences |
| Supply Chain | OTIF, stock, délai, coût | tendance, fournisseur, route, références |
| Healthcare | patients, attente, occupation | tendance, service, diagnostic, capacité |
| Sales | pipeline, win rate, quota, cycle | tendance, étape, région, Top comptes |

## 14. Mise en oeuvre dans Power BI

1. Régler la page sur `1440 x 900`.
2. Importer `powerbi_theme.json`.
3. Définir `dashboard_background.png` comme image de fond, ajustement `Fit`,
   transparence `0 %`.
4. Poser les visuels selon les coordonnées ci-dessus.
5. Désactiver fond, bordure, ombre, titre et en-tête visuel de chaque visuel.
6. Renommer les textes génériques dans `dashboard_background.svg`, puis
   régénérer le PNG si les titres doivent être figés dans le fond.
7. Vérifier à 100 % de zoom puis en mode lecture sur un écran 16:9.
8. Contrôler contraste, troncature, interactions, ordre de tabulation et
   cohérence des formats numériques avant publication.
