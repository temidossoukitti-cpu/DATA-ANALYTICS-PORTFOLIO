# Consignes communes : Portfolio Data Analytics (v2)

Elles s'appliquent au dépôt `temidossoukitti-cpu/DATA-ANALYTICS-PORTFOLIO` et sont copiées dans `docs/CONSIGNES_PROJETS.md`. La v2 intègre les corrections issues de l'audit du dépôt modèle (section 11).

Auteur : Samuel DOSSOU-KITTI · temidossoukitti@gmail.com. Langue du dépôt : **français**. Aucun badge ni lien LinkedIn. Le badge PORTFOLIO reste en place.

## 0. Périmètre et phases
- **Projets neufs (04 et suivants)** : toutes les règles s'appliquent.
- **Projet 01** : protégé, on n'y touche pas (sauf migration demandée par écrit).
- **Projets 02 et 03** : mis aux normes dans une phase dédiée (« Phase C »), pas avant.
- Les livrables existants du projet 03 (dashboard HTML/JS, classeur Excel) sont **conservés** en statut « hérité » ; l'interdiction de la section 2 ne vise que les projets neufs.
- Ordre de travail : Phase B (projet 04) → Phase C (02 et 03) → projets 05 à 15, un par un.

## 1. Objectif
15 projets, **finance d'abord**, lisibles en 90 secondes par un recruteur, crédibles pour un client. Chaque projet : question de gestion, données documentées, méthode reproductible, résultats chiffrés, recommandations, limites.

## 2. Stack imposée (identique partout)
| Besoin | Outil | Règle |
|---|---|---|
| Analyse | Python 3.11+ : pandas, numpy, scipy | Seule base de calcul |
| Modélisation | scikit-learn | Seulement si nécessaire ; `random_state=42` |
| Graphiques d'analyse | matplotlib | Ni seaborn ni plotly |
| SQL | SQLite (SQL standard) | Base reconstruite par script ; requêtes dans `sql/` |
| Dashboard | Power BI + DAX | **Construit par Samuel.** Tu prépares tout ce qui le rend rapide |
| Documentation | Markdown | Français |
| Versionnage | Git | Une branche par projet, une pull request |

Interdits pour les projets neufs, sauf demande écrite : dashboards HTML/JS, Streamlit, Excel généré, fichiers d'instructions pour assistants IA, fichiers PBIP/PBIR/TMDL écrits à la main (Samuel les exportera depuis Power BI Desktop).

## 3. Structure d'un projet
```text
projects/NN-nom-du-projet/
├── README.md              # le seul README du projet
├── requirements.txt       # versions épinglées (==)
├── data/
│   ├── raw/               # brut intact + SOURCE.md + DATA_DICTIONARY.md
│   └── processed/         # nettoyé, tables Power BI (étoile), base .db
├── sql/                   # schema.sql + requêtes numérotées
├── scripts/               # 01_clean.py, 02_analyze.py, ..., run_all.py
├── notebooks/             # exploration (jamais seule source de calcul)
├── results/               # CSV produits par les scripts
├── visuals/               # PNG d'analyse (matplotlib)
├── model/                 # DATA_MODEL.md, DAX_MEASURES.md
├── powerbi/               # PAGE_PLAN.md, POWER_QUERY.md, EXPORT_PREVIEWS.md
├── qa/                    # validation_report.md (auto), CHECKLIST.md (manuel), INTERACTION_TESTS.md
└── preview/               # exports du dashboard (Samuel, plus tard)
```
Pas de dossiers « v2 », pas de README imbriqués hors `data/raw/SOURCE.md` et `DATA_DICTIONARY.md`.

## 4. Méthode (8 étapes dans l'ordre)
1. Question de gestion (1 à 2 phrases). 2. Données publiques, licence vérifiée, brut intact. 3. Contrôle qualité et nettoyage tracé (compteurs avant/après dans `results/quality_check.csv`). 4. Exploration. 5. Indicateurs définis en une ligne et comparés à une référence. 6. Modélisation seulement si pertinent, validée sur un jeu de test. 7. 3 à 5 recommandations chiffrées. 8. Limites explicites.

## 5. Règles de qualité
- **Aucun chiffre sans source** : tout nombre du README sort d'un fichier de `results/` ou de `qa/validation_report.md`.
- **Hypothèses nommées** et signalées (taux de perte, seuils, regroupements).
- **Reproductible** : `python scripts/run_all.py` depuis un clone propre régénère `data/processed/`, `results/`, `visuals/`, `qa/validation_report.md`.
- **Parité SQL / Python** : au moins 5 indicateurs calculés des deux façons, résultat identique à l'arrondi près.
- **Équité** : aucune variable protégée dans un modèle de décision ; description seulement, avec mise en garde.
- **Licence** citée dans `SOURCE.md` et le README (attribution).
- **Sobriété** : < 25 Mo par projet hors PBIX, aucun fichier > 50 Mo, pas de caches.

## 6. README d'un projet (≤ 120 lignes)
Titre `NN · Nom` + badge PORTFOLIO + lien « ← Retour à l'index » → mention « Données publiques » avec source → Question de gestion → **Résumé en 60 secondes** (4 puces chiffrées) → Données + contrôle qualité → Méthode → Résultats clés → Recommandations → Limites → Aperçu des graphiques → **Statut qualité** (« Automatisé : PASS · Manuel Power BI : à faire », issu de `qa/`) → Dashboard (« Plan dans `powerbi/PAGE_PLAN.md` ; dashboard à venir ») → Reproduire → Contenu du dossier.

## 7. Livrables « Power BI prêt »
- `data/processed/` : table de faits + dimensions (étoile), CSV UTF-8, types stables, clés explicites.
- `model/DATA_MODEL.md` : tables, clés, relations, cardinalités.
- `model/DAX_MEASURES.md` : mesures dans une table `_Mesures`, dossiers d'affichage par thème, noms français sans unité, chaque mesure avec commentaire et **valeur attendue** issue de `results/`.
- `powerbi/PAGE_PLAN.md` : 3 à 4 pages ; gabarit commun 1280×720 : en-tête, navigation latérale, rail de filtres, 5 cartes KPI, visuels, bouton « Réinitialiser ». Pour chaque page : objectif, visuels précis (type, axes, mesures), segments, titres-messages, ordre de lecture. **Une seule convention de filtre de dates par projet.** Le nombre de pages du README est celui du plan.
- `powerbi/POWER_QUERY.md` : requêtes M avec un **paramètre `DataFolder`** (aucun chemin absolu).
- `powerbi/EXPORT_PREVIEWS.md` : Fichier → Exporter → PDF, PNG par page, nommage `preview/NN-nom-page.png`, version de Power BI Desktop notée.
- Aucun thème ni couleur : un **thème unique pour les 15 projets** sera choisi par Samuel avant le premier dashboard.

## 8. Workflow Git
1. Branche `projet-NN-nom`, jamais de commit direct sur `main`. Commits clairs en français.
2. Même PR : mettre à jour le `README.md` racine (index par domaine avec **un chiffre clé** par projet, tableau d'état, parcours) et `docs/ROADMAP.md`.
3. Ne jamais toucher à `gh-pages` ni à `projects/project-1-budget-vs-actual/`.
4. Racine autorisée : `README.md`, `LICENSE`, `.gitignore`, `.gitattributes`, `docs/`, `projects/`, `assets/` (images du README racine seulement).
5. Fusion autorisée **uniquement si tous les contrôles de la section 9 sont verts**.

## 9. Contrôles avant fusion
Depuis un clone propre : `pip install -r requirements.txt` puis `python scripts/run_all.py` réussit · liens relatifs et images des README résolus · aucun `TODO`, aucun chemin absolu (`C:\`, `/home/`), aucun lien LinkedIn · badge PORTFOLIO présent · aucun fichier > 50 Mo · parité SQL/Python vérifiée · chiffres du README = `results/` et `qa/validation_report.md` · nombre de pages README = PAGE_PLAN · racine conforme.

## 10. Rapport final (max 25 lignes)
Tableau « Contrôle | Attendu | Constaté | OK/KO », liens des PR, écarts corrigés, hypothèses retenues, actions manuelles pour Samuel.

## 11. Journal des corrections (issu de l'audit du dépôt modèle)
| # | Règle | Origine |
|---|---|---|
| C1 | **Source unique de vérité** : tous les compteurs (lignes, tables, mesures, pages) sont générés par script dans `qa/validation_report.md` ; le README les cite, ne les saisit jamais à la main ; un seul README par projet. | Modèle : 129 / 85 / 74 mesures selon les documents, 3 pages annoncées pour 4 réelles |
| C2 | **Zéro chemin absolu** : scripts en `pathlib` relatif, Power Query avec paramètre `DataFolder`. | Modèle : chemins Windows absolus |
| C3 | **QA en deux colonnes** : automatisé (PASS généré) et manuel Power BI (à cocher par Samuel). Jamais « validé » à côté d'une case non cochée. | Modèle : checklists non cochées avec claims de validation |
| C4 | **Aucune affirmation non vérifiée** : écrire « non vérifié » ou retirer. | Modèle : 73 conteneurs revendiqués, non confirmés |
| C5 | **Licences et citations complètes** ; brut inclus seulement si la licence autorise la redistribution, sinon lien + étapes + SHA-256. | Modèle : licences absentes ou incomplètes |
| C6 | **Gabarit dashboard commun** et une seule convention de filtre de dates, documentée. | Modèle : conventions de slicer contradictoires |
| C7 | **Thème unique** pour tous les projets, validé par Samuel. | Modèle : un thème différent par projet |
| C8 | **DAX** : table `_Mesures`, dossiers d'affichage, commentaires, valeur attendue, nombre généré. | Modèle : comptes incohérents |
| C9 | **Exports d'aperçu** documentés (procédure, version de Desktop). | Modèle : commande non documentée |
| C10 | **Index racine** avec un chiffre clé par projet et statut exact. | Modèle : pas de chiffres sur les cartes |
| C11 | **Poids** < 25 Mo hors PBIX ; PBIP exporté par Samuel, pas écrit à la main. | Modèle : 150 à 265 fichiers par projet |
| C12 | **Python reproductible** : versions épinglées, graine 42, `run_all.py` depuis clone propre. | Notre dépôt : scripts absents |
| C13 | **Un indicateur = une définition = une fonction** ; si deux méthodes existent, une seule est utilisée ou l'écart est expliqué. | Notre projet 02 : rendement composé 13,0 % contre somme pondérée dans l'optimisation |
| C14 | **Racine du dépôt** conforme à la liste de la section 8. | Notre dépôt : dossier `assets/` non prévu |
