# Mesures DAX

Créer une table dédiée `_Mesures` dans Power BI Desktop et y placer ces définitions. Les noms sont en français et sans unité intégrée; choisir ensuite les formats de devise, de pourcentage ou de nombre dans Desktop. Chaque expression est commentée et classée dans un dossier d’affichage.

### M01 · Produits
```DAX
// Produits de l'exercice sélectionné; le dernier exercice disponible par défaut.
Produits =
VAR Annee = MAX(dim_fiscal_year[fiscal_year_key])
RETURN
CALCULATE(
    SUM(fact_financials[value]),
    dim_metric[metric_key] = "revenue",
    dim_fiscal_year[fiscal_year_key] = Annee
)
```
Dossier d’affichage : `01 Compte de résultat`.

### M02 · Résultat d'exploitation
```DAX
// Résultat d'exploitation de l'exercice sélectionné.
Résultat d'exploitation =
VAR Annee = MAX(dim_fiscal_year[fiscal_year_key])
RETURN
CALCULATE(
    SUM(fact_financials[value]),
    dim_metric[metric_key] = "operating_income",
    dim_fiscal_year[fiscal_year_key] = Annee
)
```
Dossier d’affichage : `01 Compte de résultat`.

### M03 · Résultat net
```DAX
// Résultat net attribuable de l'exercice sélectionné.
Résultat net =
VAR Annee = MAX(dim_fiscal_year[fiscal_year_key])
RETURN
CALCULATE(
    SUM(fact_financials[value]),
    dim_metric[metric_key] = "net_income",
    dim_fiscal_year[fiscal_year_key] = Annee
)
```
Dossier d’affichage : `01 Compte de résultat`.

### M04 · Marge opérationnelle
```DAX
// Résultat d'exploitation divisé par les produits.
Marge opérationnelle = DIVIDE([Résultat d'exploitation], [Produits])
```
Dossier d’affichage : `02 Rentabilité`.

### M05 · Marge nette
```DAX
// Résultat net divisé par les produits.
Marge nette = DIVIDE([Résultat net], [Produits])
```
Dossier d’affichage : `02 Rentabilité`.

### M06 · ROE
```DAX
// Résultat net rapporté aux capitaux propres de l'exercice sélectionné.
ROE =
VAR Annee = MAX(dim_fiscal_year[fiscal_year_key])
VAR Capitaux = CALCULATE(
    SUM(fact_financials[value]),
    dim_metric[metric_key] = "equity",
    dim_fiscal_year[fiscal_year_key] = Annee
)
RETURN DIVIDE([Résultat net], Capitaux)
```
Dossier d’affichage : `02 Rentabilité`.

### M07 · ROA
```DAX
// Résultat net rapporté au total de l'actif de l'exercice sélectionné.
ROA =
VAR Annee = MAX(dim_fiscal_year[fiscal_year_key])
VAR Actif = CALCULATE(
    SUM(fact_financials[value]),
    dim_metric[metric_key] = "total_assets",
    dim_fiscal_year[fiscal_year_key] = Annee
)
RETURN DIVIDE([Résultat net], Actif)
```
Dossier d’affichage : `02 Rentabilité`.

### M08 · Flux de trésorerie disponible
```DAX
// Flux d'exploitation moins les investissements corporels.
Flux de trésorerie disponible =
VAR Annee = MAX(dim_fiscal_year[fiscal_year_key])
VAR Exploitation = CALCULATE(
    SUM(fact_financials[value]),
    dim_metric[metric_key] = "cfo",
    dim_fiscal_year[fiscal_year_key] = Annee
)
VAR Investissements = CALCULATE(
    SUM(fact_financials[value]),
    dim_metric[metric_key] = "capex",
    dim_fiscal_year[fiscal_year_key] = Annee
)
RETURN Exploitation - Investissements
```
Dossier d’affichage : `03 Trésorerie`.

### M09 · Marge de flux disponible
```DAX
// Flux disponible divisé par les produits.
Marge de flux disponible = DIVIDE([Flux de trésorerie disponible], [Produits])
```
Dossier d’affichage : `03 Trésorerie`.

### M10 · Croissance des produits
```DAX
// Variation annuelle des produits issue de fact_ratios.
Croissance des produits =
VAR Annee = MAX(dim_fiscal_year[fiscal_year_key])
RETURN
CALCULATE(
    SUM(fact_ratios[value]),
    dim_ratio[ratio_key] = "revenue_growth",
    dim_fiscal_year[fiscal_year_key] = Annee
)
```
Dossier d’affichage : `04 Croissance`.

### M11 · Ratio de liquidité courante
```DAX
// Actif courant divisé par le passif courant.
Ratio de liquidité courante =
VAR Annee = MAX(dim_fiscal_year[fiscal_year_key])
RETURN
CALCULATE(
    SUM(fact_ratios[value]),
    dim_ratio[ratio_key] = "current_ratio",
    dim_fiscal_year[fiscal_year_key] = Annee
)
```
Dossier d’affichage : `05 Structure et liquidité`.

### M12 · Taux d'endettement
```DAX
// Passif total divisé par le total de l'actif.
Taux d'endettement =
VAR Annee = MAX(dim_fiscal_year[fiscal_year_key])
RETURN
CALCULATE(
    SUM(fact_ratios[value]),
    dim_ratio[ratio_key] = "debt_ratio",
    dim_fiscal_year[fiscal_year_key] = Annee
)
```
Dossier d’affichage : `05 Structure et liquidité`.

### M13 · Couverture des intérêts
```DAX
// Résultat d'exploitation divisé par la charge d'intérêts.
Couverture des intérêts =
VAR Annee = MAX(dim_fiscal_year[fiscal_year_key])
RETURN
CALCULATE(
    SUM(fact_ratios[value]),
    dim_ratio[ratio_key] = "interest_coverage",
    dim_fiscal_year[fiscal_year_key] = Annee
)
```
Dossier d’affichage : `05 Structure et liquidité`.

### M14 · BPA dilué
```DAX
// Bénéfice par action dilué déclaré pour l'exercice sélectionné.
BPA dilué =
VAR Annee = MAX(dim_fiscal_year[fiscal_year_key])
RETURN
CALCULATE(
    SUM(fact_financials[value]),
    dim_metric[metric_key] = "eps_diluted",
    dim_fiscal_year[fiscal_year_key] = Annee
)
```
Dossier d’affichage : `06 Synthèse`.

### M15 · Taux d'imposition effectif
```DAX
// Charge d'impôt rapportée au résultat avant impôt.
Taux d'imposition effectif =
VAR Annee = MAX(dim_fiscal_year[fiscal_year_key])
RETURN
CALCULATE(
    SUM(fact_ratios[value]),
    dim_ratio[ratio_key] = "effective_tax_rate",
    dim_fiscal_year[fiscal_year_key] = Annee
)
```
Dossier d’affichage : `06 Synthèse`.

<!-- AUTO:DAX_EXPECTED_BEGIN -->
| ID | Mesure | Valeur attendue depuis les sorties générées |
|---|---|---|
| M01 | Produits | 32 791 000 000 USD |
| M02 | Résultat d'exploitation | 18 897 000 000 USD |
| M03 | Résultat net | 14 968 000 000 USD |
| M04 | Marge opérationnelle | 57,63 % |
| M05 | Marge nette | 45,65 % |
| M06 | ROE | 193,46 % |
| M07 | ROA | 27,64 % |
| M08 | Flux de trésorerie disponible | 17 159 000 000 USD |
| M09 | Marge de flux disponible | 52,33 % |
| M10 | Croissance des produits | 16,42 % |
| M11 | Ratio de liquidité courante | 1,03 |
| M12 | Taux d'endettement | 85,70 % |
| M13 | Couverture des intérêts | 26,17x |
| M14 | BPA dilué | 16,52 USD par action |
| M15 | Taux d'imposition effectif | 19,43 % |
<!-- AUTO:DAX_EXPECTED_END -->
