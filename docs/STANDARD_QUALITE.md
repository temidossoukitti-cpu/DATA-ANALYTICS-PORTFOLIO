# Standard de qualité

Chaque projet de ce dépôt respecte les règles suivantes.

1. **Question de gestion d'abord** : le README formule la décision à prendre avant tout graphique.
2. **Données documentées** : source, période, volume, dictionnaire des colonnes. Les données simulées sont clairement signalées.
3. **Nettoyage tracé** : contrôle qualité chiffré (doublons, valeurs manquantes, cohérence) enregistré dans `results/`.
4. **Méthode reproductible** : un script qui régénère tous les résultats à partir de `data/raw/`.
5. **Résultats chiffrés** : indicateurs définis en une ligne, comparés à une référence.
6. **Recommandations actionnables** : 3 à 5, classées par impact.
7. **Limites explicites** : ce que l'analyse ne prouve pas.
8. **Validation** : checklist `qa/` complétée avant publication.
9. **Aucune donnée confidentielle**.
