# Dashboard web — Risque de défaut des cartes de crédit

Dashboard interactif sans Power BI : HTML, CSS et JavaScript, sans backend.

- **Version hébergée :** https://temidossoukitti-cpu.github.io/DATA-ANALYTICS-PORTFOLIO/projects/04-risque-credit/dashboard/web/
- **Filtres :** limite de crédit, tranche d'âge, éducation, état matrimonial, niveau de risque, statut de paiement récent. Tous les indicateurs et graphiques se recalculent.
- **Indicateurs :** clients, défaillants, taux de défaut, exposition des défaillants (limite de crédit), utilisation moyenne, comparés au portefeuille complet.

## Ouvrir en local

```bash
python3 -m http.server 8000
```

Puis ouvrir http://localhost:8000/dashboard/web/ (depuis le dossier du projet). Le fichier `index.html` fonctionne aussi ouvert directement.

## Régénérer les données du dashboard

```bash
python3 scripts/run_all.py            # si les CSV traités n'existent pas encore
python3 dashboard/build_web_data.py   # agrège data/processed/fact_clients.csv en dashboard/web/data.js
```

Source : UCI Default of Credit Card Clients (Yeh, 2009), licence CC BY 4.0.
