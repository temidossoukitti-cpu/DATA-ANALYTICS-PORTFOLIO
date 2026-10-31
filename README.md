<div align="center">

# DATA ANALYTICS PORTFOLIO

### Portfolio professionnel · Analyse de données, finance et gestion du risque

**Des analyses reproductibles et des tableaux de bord conçus pour éclairer les décisions.**

<p align="center">
  <a href="mailto:temidossoukitti@gmail.com"><img src="assets/contact-button.svg" width="180" height="48" alt="Me contacter"></a>
  &nbsp;&nbsp;
  <a href="https://temidossoukitti-cpu.github.io/DATA-ANALYTICS-PORTFOLIO/"><img src="assets/portfolio-button.svg" width="150" height="48" alt="Portfolio"></a>
</p>

</div>

---

## Présentation

Je conçois des analyses de données qui relient les indicateurs aux décisions opérationnelles. Mon travail couvre la préparation des données, l’analyse, la modélisation, la visualisation et la formulation de recommandations.

Ce portfolio met l’accent sur la **finance et la gestion du risque**, avec des projets complémentaires en analyse commerciale. Chaque étude documente sa question de gestion, ses données, sa méthode, ses résultats et ses limites.

## Projets par domaine

### Finance

| Référence | Projet | Décision soutenue et repère chiffré | Technologies | État |
|---|---|---|---|---|
| 01 | [Civic Signal · Budget contre réalisé](projects/project-1-budget-vs-actual/) | Ajuster l’analyse budgétaire; consommation observée : **74,32 %**. | SQL · DAX · Web | Publié |
| 02 | [Risque et performance d’un portefeuille](projects/02-portefeuille-risque/README.md) | Limiter les concentrations; AFBK représente **34,9 % du risque**. | Python · pandas · NumPy · SciPy · DAX | Analyse terminée |
| 04 | [Risque de défaut des cartes de crédit](projects/04-risque-credit/README.md) | Orienter le suivi du risque; défaut observé : **22,12 %**. | Python · pandas · scikit-learn · SQLite · DAX | Données, QA, SQL, DAX et rapport prêts; Power BI en attente |
| 05 | [Détection de fraude sur les transactions bancaires](projects/05-fraude-bancaire/README.md) | Prioriser la revue; fraude source : **0,173 %**. | Python · pandas · scikit-learn · SQLite · Power BI/DAX | Analyse terminée; dashboard à construire par Samuel |

### Commerce

| Référence | Projet | Décision soutenue et repère chiffré | Technologies | État |
|---|---|---|---|---|
| 03 | [Analyse des ventes d’un distributeur](projects/03-ventes-retail/README.md) | Prioriser produits et marchés; **2,30 M$ de ventes**. | Python · Excel · Power BI · Web | Publié |

### État des livrables — projet 04

| Données | Qualité | SQL et parité | DAX | Rapport QA | Dashboard Power BI |
|---|---|---|---|---|---|
| Reproductibles | PASS | 34/34 comparaisons PASS | 14 mesures documentées | PASS | À construire par Samuel |

### État des livrables — projet 05

<!-- AUTO:PROJECT05_STATUS_BEGIN -->
| Données | Qualité | SQL/Python | DAX | Rapport QA | Dashboard Power BI |
|---|---|---|---|---|---|
| Échantillon 25 492 lignes | PASS | 84/84 comparaisons | 15 mesures | PASS | À construire par Samuel |
<!-- AUTO:PROJECT05_STATUS_END -->

### Aperçu du projet ventes

L’analyse du jeu de données Sample Superstore couvre **9 994 lignes** et la période **2014–2017**. Elle met en évidence **2,30 M$ de ventes**, **286 397 $ de profit** et une marge globale de **12,5 %**. Le dossier comprend les scripts de nettoyage et d’analyse, les rapports, un classeur Excel et huit visualisations.

[Consulter l’étude complète](projects/03-ventes-retail/README.md) · [Ouvrir le tableau de bord en ligne](https://temidossoukitti-cpu.github.io/DATA-ANALYTICS-PORTFOLIO/)

## Méthode de travail

Les projets sont structurés pour être compréhensibles et vérifiables :

- Données et sources décrites, avec distinction claire entre données publiques et données simulées.
- Nettoyage reproductible et conservation des données originales.
- Indicateurs définis et reliés à une question de gestion.
- Résultats accompagnés de recommandations et de limites explicites.
- Code, documentation et livrables organisés dans un dossier par projet.

Consulter le [standard de qualité](docs/STANDARD_QUALITE.md) et la [feuille de route](docs/ROADMAP.md).

## Compétences et outils

| Domaine | Outils et pratiques |
|---|---|
| Analyse et traitement | Python, pandas, NumPy, SciPy, SQL |
| Visualisation et restitution | Power BI, DAX, Matplotlib, Excel, HTML, CSS, JavaScript |
| Finance et gestion | Budget et réalisé, rentabilité, risque et performance de portefeuille |
| Méthode | Git, documentation, contrôles qualité, analyses reproductibles |

## Structure du portfolio

```text
.
├── docs/                              # Standard qualité et feuille de route
└── projects/
    ├── project-1-budget-vs-actual/    # Suivi budgétaire
    ├── 02-portefeuille-risque/        # Analyse de risque et allocation
    ├── 03-ventes-retail/              # Analyse commerciale
    ├── 04-risque-credit/              # Défaut des cartes de crédit
    └── 05-fraude-bancaire/            # Détection de fraude
```

Chaque dossier de projet contient sa propre présentation et ses livrables. Les instructions de reproduction sont indiquées dans le README correspondant.

## Contact

**Samuel Dossou-Kitti**  
Analyste de données · Finance et gestion du risque  
[temidossoukitti@gmail.com](mailto:temidossoukitti@gmail.com) · [Site portfolio](https://temidossoukitti-cpu.github.io/DATA-ANALYTICS-PORTFOLIO/)
