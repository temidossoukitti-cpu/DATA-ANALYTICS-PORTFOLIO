# Dashboards — Risque et performance d'un portefeuille

Les données de ce projet sont **simulées**. Les entreprises, prix et positions sont fictifs.

## Streamlit

Depuis le dossier du projet :

```bash
python3 -m pip install -r dashboard/requirements.txt
streamlit run dashboard/streamlit_app.py
```

## Power BI

Le dashboard principal est un **rapport Power BI** au format PBIP : voir [`powerbi/`](powerbi/) et son
[mode d’emploi](powerbi/README.md). L’ancienne version HTML a été retirée au profit de Power BI.

## Régénérer le rapport PDF

```bash
python3 dashboard/build_assets.py
```

Le script lit uniquement les CSV de `results/` et produit les données JSON du dashboard ainsi que le rapport PDF.
