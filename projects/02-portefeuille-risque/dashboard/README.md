# Dashboards — Risque et performance d'un portefeuille

Les données de ce projet sont **simulées**. Les entreprises, prix et positions sont fictifs.

## Streamlit

Depuis le dossier du projet :

```bash
python3 -m pip install -r dashboard/requirements.txt
streamlit run dashboard/streamlit_app.py
```

## Version HTML

Depuis le dossier du projet, lancer un serveur statique :

```bash
python3 -m http.server 8000
```

Puis ouvrir [http://localhost:8000/dashboard/web/](http://localhost:8000/dashboard/web/).
La version HTML ne nécessite aucun backend et charge les fichiers JSON générés dans `dashboard/web/data/`.

## Régénérer les données web et le PDF

```bash
python3 dashboard/build_assets.py
```

Le script lit uniquement les CSV de `results/` et produit les données JSON du dashboard ainsi que le rapport PDF.
