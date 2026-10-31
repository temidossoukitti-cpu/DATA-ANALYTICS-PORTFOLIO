# Dictionnaire des données

Le fichier OpenML 43627 contient 31 colonnes numériques. Les résultats du projet portent sur les transactions des deux jours décrits par la source; aucune devise, date civile, typologie de commerce ou identité de client n’est fournie [1].

| Champ | Origine | Définition et usage |
|---|---|---|
| `Time` | Source | Secondes écoulées depuis la première transaction du fichier. Utilisé uniquement pour une analyse descriptive par fenêtres relatives de six heures; exclu du modèle prédictif. |
| `V1`–`V28` | Source | Composantes principales PCA anonymisées. Leurs sens métier ne sont pas divulgués; utilisées comme variables numériques du modèle, jamais renommées en facteurs métier. |
| `Amount` | Source | Montant de transaction, sans unité ou devise précisée. Utilisé pour les bandes descriptives, le modèle et les hypothèses de coûts explicitement signalées. |
| `Class` | Source | Cible binaire : 1 = fraude, 0 = légitime. |
| `transaction_id` | Dérivée | Position de ligne d’origine, numérotée à partir de 0. Ce n’est pas un identifiant de transaction fourni par OpenML. |
| `sampling_weight` | Dérivée | Poids d’estimation de population : 1 pour chaque fraude conservée; 11.3726 pour chaque transaction légitime tirée dans l’échantillon. Ne pas utiliser comme prédicteur. |
| `amount_band_key` | Dérivée | Clé de bande de montant : ≤10, (10, 50], (50, 200], >200 unités du dataset. Les seuils sont des regroupements descriptifs. |
| `time_window_key` | Dérivée | Clé d’une fenêtre de six heures depuis la transaction initiale, parmi huit fenêtres couvrant l’intervalle observé. Ce ne sont pas des heures civiles. |
| `outcome_key` | Dérivée | Clé de la dimension de résultat, identique au code `Class` (0 ou 1). |
| `duplicate_group` | Dérivée de calcul | Empreinte déterministe des attributs source hors cible, utilisée pour garder les lignes identiques dans la même partition train/test; jamais présentée comme identifiant métier. |
| `model_probability` | Dérivée | Probabilité estimée par la régression logistique sur la partition test uniquement. |
| `model_prediction` | Dérivée | Indicateur 0/1 produit au seuil de coût choisi sur les prédictions hors échantillon d’entraînement. |
| `baseline_amount_flag` | Dérivée | Règle simple de contrôle : 1 si le montant atteint ou dépasse le 99e percentile pondéré des transactions légitimes du train. |

Les noms `V1` à `V28` sont conservés tels quels. Il serait injustifié de les décrire comme type de commerce, géographie, canal ou comportement client.

## Référence

[1]: https://www.openml.org/api/v1/json/data/43627 "OpenML dataset 43627 API et description"
