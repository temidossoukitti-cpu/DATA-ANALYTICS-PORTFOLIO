# Modèle de données

## Grain

Une ligne de `fact_campaign` représente une observation de campagne et un contact enregistré dans le fichier UCI. Il ne s'agit pas d'un client identifié de manière unique : la source ne fournit pas d'identifiant client.

## Tables

| Table | Clé | Contenu |
|---|---|---|
| `fact_campaign` | `campaign_id` | Mesures de campagne, cible, variables numériques et clés étrangères |
| `dim_outcome` | `outcome_key` | Souscrit / non souscrit |
| `dim_job` | `job_key` | Métier et ordre d'affichage |
| `dim_education` | `education_key` | Niveau d'études |
| `dim_marital` | `marital_key` | Situation matrimoniale |
| `dim_month` | `month_key` | Mois et ordre chronologique |
| `dim_contact` | `contact_key` | Canal de contact |
| `dim_poutcome` | `poutcome_key` | Résultat de la campagne précédente |
| `dim_age_band` | `age_band_key` | Groupe d'âge |
| `dim_campaign_band` | `campaign_band_key` | Nombre de contacts regroupé |

Chaque dimension se relie à `fact_campaign` par une relation 1-vers-plusieurs, avec le filtre dirigé de la dimension vers la table de faits. Les relations doivent être contrôlées dans Power BI après import.
