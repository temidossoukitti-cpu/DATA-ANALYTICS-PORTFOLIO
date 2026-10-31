# Data Analytics Portfolio · Finance & Gestion du risque

**Des tableaux de bord et des analyses conçus pour aider à décider : finance et risque d'abord, puis commerce, économie, santé, IA et cybersécurité.**

[![Portfolio](https://img.shields.io/badge/PORTFOLIO-C7F436?style=for-the-badge)](https://temidossoukitti-cpu.github.io/DATA-ANALYTICS-PORTFOLIO/)

Chaque projet de ce dépôt est présenté comme un **produit d'analyse vérifiable** : une question de gestion, des données documentées, une méthode reproductible, des résultats chiffrés, des recommandations et des limites assumées. Les données sont publiques ou clairement signalées comme simulées.

---

## Projets phares

| Projet | En une phrase |
|---|---|
| [01 · Civic Signal Budget Control Tower](projects/project-1-budget-vs-actual/) | Où le budget dérape-t-il par rapport au réalisé, à partir de données publiques ? |
| [02 · Risque d'un portefeuille d'actions](projects/02-portefeuille-risque/README.md) | Où le risque se concentre-t-il, et comment rééquilibrer ? |

---

## Index des projets

### Finance

| # | Projet | Décision soutenue | Outils | Livrables | Statut |
|---|---|---|---|---|---|
| 01 | [Budget contre réalisé · Civic Signal Budget Control Tower](projects/project-1-budget-vs-actual/) | Repérer et corriger les écarts entre budget et réalisé | SQL · DAX · Web | Données · Contrôles qualité · SQL · DAX · Rapports · [Dashboard web](https://temidossoukitti-cpu.github.io/DATA-ANALYTICS-PORTFOLIO/) | Publié |
| 02 | [Risque et performance d'un portefeuille](projects/02-portefeuille-risque/README.md) | Rééquilibrer pour réduire la concentration du risque | Python · DAX | Données · Code · Résultats · DAX · QA | Analyse terminée, dashboard en cours |

### Commerce et ventes

| # | Projet | Décision soutenue | Outils | Livrables | Statut |
|---|---|---|---|---|---|
| 03 | [Analyse des ventes d'un distributeur](projects/03-ventes-retail/README.md) | Améliorer la rentabilité : remises, produits déficitaires, régions | Python · Excel · Web · Power BI | Données · Scripts · Rapports · Classeur Excel · 8 graphiques | Publié |

<!-- Pour ajouter un projet : copie une ligne du tableau du bon domaine, change le numéro, le nom, le lien et le statut. -->

### Économie · Santé · IA · Cybersécurité

*Les projets de diversification seront ajoutés après le lot Finance.*

<details>
<summary><b>Projets à venir</b></summary>

- Risque de crédit d'un portefeuille de prêts
- Analyse financière d'une entreprise : ratios, marges, liquidité
- Détection de fraude sur des transactions bancaires
- Performance marketing d'une banque
- P&L et seuil de rentabilité d'une PME

</details>

---

## Parcours conseillé pour un recruteur

1. **Résumé de 60 secondes** : ouvrir le README d'un projet et lire la question de gestion et les chiffres clés.
2. **Aperçu du dashboard** : consulter le dashboard en ligne ou les images du projet.
3. **Reproduire** : lancer le script d'analyse du projet.
4. **Vérifier** : lire les mesures DAX, les contrôles qualité et les limites.

---

## Structure d'un projet

```text
projects/<numero-nom-du-projet>/
├── README.md        # question, résumé, résultats, recommandations, limites
├── data/            # données brutes et nettoyées + dictionnaire
├── scripts/         # code reproductible
├── notebooks/       # exploration commentée
├── results/         # tableaux produits par l'analyse
├── model/           # modèle de données et mesures DAX
├── qa/              # checklist de validation
└── preview/         # aperçus du dashboard (PNG / PDF)
```

Chaque projet garde sa propre organisation interne : les chemins du README d'un projet partent toujours de son dossier.

---

## État de livraison

| Projet | Données | Contrôles qualité | SQL | DAX | Rapport | Dashboard |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| 01 · Budget contre réalisé | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ web |
| 02 · Portefeuille | ✅ | ✅ | – | ✅ | ⏳ | ⏳ |
| 03 · Ventes | ✅ | ✅ | – | ✅ | ✅ | ✅ web |

✅ livré · ⏳ en cours · – sans objet

---

## Standard de qualité

- Une **question de gestion** avant tout graphique.
- Des données **documentées** (source, période, dictionnaire) et un nettoyage tracé.
- Une analyse **reproductible** : un script régénère les résultats.
- Des indicateurs **définis en une ligne** et comparés à une référence.
- 3 à 5 **recommandations** chiffrées, classées par impact.
- Des **limites** explicites.
- Aucune donnée confidentielle.

Détails : [`docs/STANDARD_QUALITE.md`](docs/STANDARD_QUALITE.md) · Prochains projets : [`docs/ROADMAP.md`](docs/ROADMAP.md)

---

## Compétences et outils

| Domaine | Outils |
|---|---|
| Analyse et modélisation | Python (pandas, NumPy, SciPy) · SQL |
| Visualisation | Power BI · DAX · Matplotlib · HTML/CSS/JavaScript |
| Finance | Budget et réalisé · risque et performance · rentabilité |
| Méthode | Git · documentation · contrôle qualité |

---

## Auteur

**Samuel DOSSOU-KITTI** · Data Analyst, finance et gestion du risque

[![Portfolio](https://img.shields.io/badge/PORTFOLIO-C7F436?style=flat-square)](https://temidossoukitti-cpu.github.io/DATA-ANALYTICS-PORTFOLIO/)
[![Email](https://img.shields.io/badge/EMAIL-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:temidossoukitti@gmail.com)
