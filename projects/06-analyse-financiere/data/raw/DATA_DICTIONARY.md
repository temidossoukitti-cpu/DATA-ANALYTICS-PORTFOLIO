# Dictionnaire des données

Le fichier `mastercard_companyfacts.json` contient les faits XBRL déposés auprès de la SEC pour Mastercard Incorporated. Les champs ci-dessous sont ceux retenus par l’extraction, avec leur balise d’origine et leur usage dans le projet.

| Champ | Balise SEC | Définition et usage |
|---|---|---|
| `revenue` | `Revenues` | Produits consolidés de l’exercice. Base des marges et de la croissance. |
| `operating_income` | `OperatingIncomeLoss` | Résultat d’exploitation. Numérateur de la marge opérationnelle et de la couverture des intérêts. |
| `net_income` | `ProfitLoss` | Résultat net attribuable. Base de la marge nette, du ROA et du ROE. |
| `eps_diluted` | `EarningsPerShareDiluted` | Bénéfice par action dilué. Comparé au résultat net divisé par les actions diluées. |
| `total_assets` | `Assets` | Total de l’actif au 31 décembre. Dénominateur du ROA et du taux d’endettement. |
| `total_liabilities` | `Liabilities` | Total du passif. Numérateur du ratio d’endettement. |
| `equity` | `StockholdersEquity` | Capitaux propres. Dénominateur du ROE et du levier. |
| `current_assets` | `AssetsCurrent` | Actif courant. Numérateur du ratio de liquidité courante. |
| `current_liabilities` | `LiabilitiesCurrent` | Passif courant. Dénominateur de la liquidité courante et du ratio de trésorerie. |
| `cash` | `CashAndCashEquivalentsAtCarryingValue` | Trésorerie et équivalents. Numérateur du ratio de trésorerie. |
| `cfo` | `NetCashProvidedByUsedInOperatingActivities` | Flux de trésorerie d’exploitation. Base du flux disponible. |
| `capex` | `PaymentsToAcquirePropertyPlantAndEquipment` | Décaissements d’investissement corporel. Soustraits du flux d’exploitation. |
| `interest_expense` | `InterestExpenseNonoperating` puis `InterestExpense` | Charge d’intérêts. Dénominateur de la couverture des intérêts. |
| `income_tax` | `IncomeTaxExpenseBenefit` | Charge d’impôt. Sert au taux d’imposition effectif. |
| `diluted_shares` | `WeightedAverageNumberOfDilutedSharesOutstanding` | Nombre moyen pondéré d’actions diluées, en millions. Contrôle du BPA. |

## Champs dérivés

| Champ | Définition |
|---|---|
| `fiscal_year` | Année civile de clôture, du 1er janvier au 31 décembre. |
| `metric_key` | Identifiant technique de l’indicateur dans le modèle en étoile. |
| `ratio_key` | Identifiant technique d’un ratio calculé. |
| `fcf` | Flux de trésorerie disponible : `cfo - capex`. |
| `fcf_margin` | Flux disponible rapporté aux produits. |
| `revenue_growth` | Variation annuelle des produits par rapport à l’exercice précédent. |

Les valeurs exprimées en dollars sont conservées en unités, sans arrondi intermédiaire. Le formatage français n’intervient qu’à l’affichage.
