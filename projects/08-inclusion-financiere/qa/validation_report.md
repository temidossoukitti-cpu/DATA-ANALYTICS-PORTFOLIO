# Validation qualité — projet 08

Le fichier source Global Findex 2025 a été chargé avec **8 577 lignes** et **438 colonnes**. Les années présentes dans le fichier sont 2011, 2014, 2017, 2021, 2022 et 2024. L’analyse comparative conserve les cinq années publiées dans la page officielle de téléchargement : 2011, 2014, 2017, 2021 et 2024.

La vue nationale contient **756 lignes** pour les années retenues et **153 pays** en 2024. Le contrôle d’unicité pays-année sur `group=all`, `group2=all` est PASS avec zéro doublon. Le taux de compte est disponible pour les 153 pays de la vue 2024.

Les résultats sont générés par `scripts/01_analyze.py`. Les données de présentation sont générées par `dashboard/build_web_data.py`. Les quatre pages du dashboard ont été ouvertes dans Chromium, avec navigation entre les vues et vérification de l’absence d’erreur JavaScript.
