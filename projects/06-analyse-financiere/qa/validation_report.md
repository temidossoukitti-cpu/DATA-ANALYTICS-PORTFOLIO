# Rapport de validation automatique — projet 06

**Statut automatisé : PASS.** Généré par `scripts/05_report.py` depuis les sorties du pipeline. Les tests Desktop sont séparés et restent à faire par Samuel.

| Contrôle | Attendu | Constaté | Statut |
|---|---|---|---|
| Fichiers requis | Tous présents | 0 absent(s) | PASS |
| Empreinte de la source | SHA-256 et taille conformes | conforme | PASS |
| Contrôles qualité | Aucun FAIL | 0 FAIL; 13 règles | PASS |
| Complétude | 105 valeurs comptables; 130 ratios | 105 valeurs; 130 ratios | PASS |
| Parité SQL/Python | Au moins 5 requêtes, tous PASS | 5 requêtes; 109/109 PASS; 0 FAIL | PASS |
| Tables Power BI | 7 CSV traités | 7/7 présents | PASS |
| Mesures DAX | Définitions numérotées et valeurs générées | 15 mesures | PASS |
| Pages planifiées | 4 pages | 4 pages | PASS |
| Graphiques | Au moins 6 PNG Matplotlib | 8 PNG | PASS |
| README projet | Au plus 120 lignes; badge PORTFOLIO | 94 lignes; badge présent | PASS |
| Liens relatifs/images | Tous résolus | 0 cassé(s) | PASS |
| Taille du projet | <25 Mo; aucun fichier >50 Mo | 4.92 Mo; maximum 4.18 Mo | PASS |
| Caches Python | Aucun | 0 artefact(s) | PASS |
| Conformité texte | Aucun chemin absolu, TODO, LinkedIn ou emoji | 0 chemin(s), 0 TODO, 0 LinkedIn, 0 emoji | PASS |
| Dépendances | Versions directes épinglées avec == | 3 dépendances | PASS |
| Formats interdits | Aucun HTML/Excel/PBIX/PBIP/PBIR/TMDL | 0 fichier(s) | PASS |
| Checklist Desktop | Tous les tests manuels restent non cochés | 13 cases; toutes non cochées=True | PASS |

**Source :** SEC EDGAR companyfacts, CIK 1141391; SHA-256 `eec2f64179fe268380a6f9f4b5e3da53a9c1c5adb988aa31cc40c8372c0d8899`; 4,182,087 octets; exercices 2019–2025.
**Dernier exercice :** produits 32 791 000 000 USD; résultat net 14 968 000 000 USD; marge opérationnelle 57,629 %; ROE 193,460 %; liquidité 1,035; flux disponible 17 159 000 000 USD.
**Ratios :** 19 ratios calculés, dont la croissance des produits à 11,699 % en moyenne annuelle sur la période; aucune valeur n’est extrapolée hors des sept exercices.
**Manuel :** le dashboard Power BI, les mesures saisies dans Desktop, les scénarios d’interaction et les exports PDF/PNG ne sont pas exécutés dans cette livraison.
