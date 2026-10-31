# Plan Power BI

## Gabarit commun

Chaque page utilise un canevas 1280 × 720, un en-tête, une navigation latérale, un rail de filtres, cinq cartes KPI et un bouton « Réinitialiser ». Aucune palette ni thème n’est imposé dans ce projet; le thème commun du portfolio sera choisi par Samuel.

**Convention temporelle unique :** chaque ligne représente un instantané client dont le dernier relevé est septembre 2005. Il n’y a pas de slicer calendrier, car la source n’est pas une série d’observations datées par client. Les historiques sont comparés avec `pay_6` (avril) à `pay_0` (septembre) et avec la matrice `pay_2` → `pay_0`. Ne pas créer d’axe temporel artificiel.

Les segments de sexe, d’âge et d’état matrimonial servent à l’analyse descriptive uniquement. Ils ne déclenchent pas une décision individuelle. La page modèle porte par défaut sur la partition test; les pages de portefeuille décrivent la cohorte complète.

## Vue d’ensemble

- **Objectif :** situer le niveau de défaut, l’exposition et l’utilisation du crédit.
- **Visuels :** cinq cartes — clients, taux de défaut, limite totale, exposition des défaillants, utilisation moyenne; barres du taux de défaut par bande de limite; barres de l’exposition des défaillants par bande de limite.
- **Axes et mesures :** bande de limite; nombre de clients, taux de défaut, limite totale, exposition des défaillants.
- **Segments :** bande de limite, niveau d’éducation; sexe disponible en analyse descriptive, avec avertissement.
- **Titre-message :** « La cohorte présente un défaut de [taux] et concentre [part] des limites chez les clients en défaut. » Les valeurs sont liées aux mesures, sans saisie manuelle.
- **Ordre de lecture :** cartes KPI, taux par limite, exposition par limite, filtres.

## Segments à risque

- **Objectif :** repérer les segments associés à une fréquence de défaut ou à une exposition élevée.
- **Visuels :** colonnes du taux de défaut par âge; barres par éducation et état matrimonial; nuage ou barres de taux par bande d’utilisation; tableau des effectifs et expositions.
- **Axes et mesures :** dimension de segment; taux de défaut, nombre de clients, exposition des défaillants, part d’exposition.
- **Segments :** âge, éducation, état matrimonial, utilisation, limite; sexe uniquement dans une vue descriptive distincte.
- **Titre-message :** « Les groupes [segment] affichent le taux observé le plus élevé; l’effectif et l’exposition accompagnent toujours le taux. »
- **Ordre de lecture :** taux et effectifs, exposition, puis filtres descriptifs.

## Comportement de paiement et retards

- **Objectif :** visualiser la persistance ou l’amélioration des retards dans l’historique.
- **Visuels :** matrice thermique du statut `pay_2` vers `pay_0`; colonnes du défaut par code `pay_0`; barres du défaut selon le nombre de mois en retard; tableau des effectifs.
- **Axes et mesures :** codes de statut et libellés de la dimension `dim_pay_status`; taux de défaut, nombre de clients et part de transition.
- **Segments :** statut récent, bande d’utilisation et bande de limite.
- **Titre-message :** « Les retards récents sont associés à un taux de défaut supérieur à la moyenne de cohorte. »
- **Ordre de lecture :** transition, défaut par statut récent, effectifs et filtres.

## Scoring et actions

- **Objectif :** restituer les performances du modèle hors échantillon et les pertes attendues sous hypothèses.
- **Visuels :** cartes de ROC-AUC, PR-AUC, KS, précision et rappel au seuil retenu; courbe de lift par décile; calibration prévu/observé; exposition et perte attendue par bande de risque; tableau des coefficients.
- **Axes et mesures :** décile, bande de risque et probabilité; taux de défaut, exposition facturée, PD moyenne, perte attendue.
- **Segments :** partition test obligatoire, bande de risque, retard récent, bande d’utilisation. Le sexe, le mariage et l’âge ne sont pas des variables de score ni des déclencheurs de politique.
- **Titre-message :** « Sur la partition test, la bande très élevée regroupe [part] des dossiers et [perte] de perte attendue sous LGD 45 % — hypothèse. »
- **Ordre de lecture :** performances test, lift/calibration, exposition et perte, recommandations.
