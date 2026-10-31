# Rapport de validation automatique — projet 05

**Statut automatisé : PASS.** Généré par `scripts/06_report.py` depuis les sorties du pipeline. Les tests Desktop sont séparés et restent à faire par Samuel.

| Contrôle | Attendu | Constaté | Statut |
|---|---|---|---|
| Fichiers requis | Tous présents | 0 absent(s) | PASS |
| Échantillon et fraudes | 284,807 source; 492 fraudes conservées | 25,492 échantillon; 492 fraudes | PASS |
| Poids populationnels | Reconstruction à moins de 0,01 transaction | écart 0.0000000001 | PASS |
| Contrôles qualité | Aucun FAIL; informations de doublons documentées | 0 FAIL; 16 règles | PASS |
| Split et fuite de doublons | Test 30 % ± 0,5 %; aucun groupe partagé | test 30.0016%; groupes partagés 0; échecs 0 | PASS |
| Parité SQL/Python | Au moins 5, tous PASS | 84/84 PASS; 0 FAIL | PASS |
| Tables Power BI | 8 CSV traités | 8/8 présents | PASS |
| Mesures DAX | Définitions numérotées et valeurs générées | 15 mesures | PASS |
| Pages planifiées | 4 pages | 4 pages | PASS |
| Graphiques | Au moins 6 PNG Matplotlib | 7 PNG | PASS |
| README projet | Au plus 120 lignes; badge PORTFOLIO | 93 lignes; badge présent | PASS |
| Liens relatifs/images | Tous résolus | 0 cassé(s) | PASS |
| Taille du projet | <25 Mo hors Parquet complet local | 11.91 Mo; maximum 7.41 Mo | PASS |
| Parquet complet ignoré | Exclu de Git et du décompte versionné | ignore actif | PASS |
| Caches Python | Aucun | 0 artefact(s) | PASS |
| Conformité texte | Aucun chemin absolu, TODO, LinkedIn ou emoji | 0 chemin(s), 0 TODO, 0 LinkedIn, 0 emoji | PASS |
| Dépendances | Versions directes épinglées avec == | 6 dépendances | PASS |
| Formats interdits | Aucun HTML/Excel/PBIX/PBIP/PBIR/TMDL | 0 fichier(s) | PASS |
| Checklist Desktop | Tous les tests manuels restent non cochés | 13 cases; toutes non cochées=True | PASS |

**Source :** OpenML 43627; SHA-256 `91650a62cb263b7fd76610a8f2fa55c4e861033b56dd51ed22d707838c95e0cf`; 73,231,038 octets; le fichier complet local est ignoré par Git.
**Référence modèle :** seuil 0.191 choisi sur prédictions hors pli du train; test 30.00%; PR-AUC pondérée 0.6595; précision 67.9710%; rappel 81.7568%.
**Coûts :** hypothèses de base sévérité=1.0, friction=10.0 unités; le modèle et la référence P99 ne représentent pas des pertes comptables constatées.
**Manuel :** le dashboard Power BI, les mesures saisies dans Desktop, les scénarios d’interaction et les exports PDF/PNG ne sont pas exécutés dans cette livraison.
