"""Clean the Superstore dataset without modifying the source file."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = PROJECT_ROOT / "data" / "raw" / "Sample - Superstore.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "superstore_clean.csv"
REPORT_PATH = PROJECT_ROOT / "reports" / "data_cleaning_report.md"

SOURCE_ENCODING = "latin-1"
DATE_COLUMNS = ("Order Date", "Ship Date")
POSTAL_CODE_COLUMN = "Postal Code"
DUPLICATE_FLAG_COLUMN = "Potential Duplicate"
EXPECTED_COLUMNS = {
    "Row ID",
    "Order Date",
    "Ship Date",
    "Postal Code",
}


@dataclass(frozen=True)
class CleaningMetrics:
    """Metrics recorded before and after cleaning."""

    rows_before: int
    rows_after: int
    columns_before: int
    columns_after: int
    missing_before: int
    missing_after: int
    exact_duplicates_before: int
    exact_duplicates_after: int
    potential_duplicate_rows: int
    potential_duplicate_groups: int
    trimmed_values: dict[str, int]
    short_postal_codes: int
    constant_columns: list[str]


def load_source(path: Path) -> pd.DataFrame:
    """Load the source CSV and validate the columns required for cleaning."""
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")

    source = pd.read_csv(path, encoding=SOURCE_ENCODING)
    missing_columns = EXPECTED_COLUMNS.difference(source.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Required columns are missing: {missing}")

    return source


def count_values_to_trim(data: pd.DataFrame) -> dict[str, int]:
    """Count leading or trailing spaces in every text column."""
    counts: dict[str, int] = {}
    text_columns = data.select_dtypes(include=["object", "string"]).columns

    for column in text_columns:
        values = data[column].astype("string")
        count = int((values.notna() & values.ne(values.str.strip())).sum())
        if count:
            counts[column] = count

    return counts


def clean_data(source: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Return a cleaned copy while preserving all source rows."""
    cleaned = source.copy(deep=True)
    trimmed_values = count_values_to_trim(cleaned)

    for column in DATE_COLUMNS:
        cleaned[column] = pd.to_datetime(
            cleaned[column],
            format="%m/%d/%Y",
            errors="raise",
        )

    cleaned[POSTAL_CODE_COLUMN] = cleaned[POSTAL_CODE_COLUMN].astype("string")

    text_columns = cleaned.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        cleaned[column] = cleaned[column].str.strip()

    comparison_columns = [
        column for column in cleaned.columns if column != "Row ID"
    ]
    cleaned[DUPLICATE_FLAG_COLUMN] = cleaned.duplicated(
        subset=comparison_columns,
        keep=False,
    )

    return cleaned, trimmed_values


def collect_metrics(
    source: pd.DataFrame,
    cleaned: pd.DataFrame,
    trimmed_values: dict[str, int],
) -> CleaningMetrics:
    """Collect quality metrics used in the cleaning report."""
    comparison_columns = [
        column
        for column in cleaned.columns
        if column not in {"Row ID", DUPLICATE_FLAG_COLUMN}
    ]
    duplicate_mask = cleaned[DUPLICATE_FLAG_COLUMN]
    duplicate_groups = cleaned.loc[
        duplicate_mask, comparison_columns
    ].drop_duplicates()

    postal_lengths = cleaned[POSTAL_CODE_COLUMN].str.len()
    constant_columns = [
        column
        for column in cleaned.columns
        if column != DUPLICATE_FLAG_COLUMN
        and cleaned[column].nunique(dropna=False) <= 1
    ]

    return CleaningMetrics(
        rows_before=len(source),
        rows_after=len(cleaned),
        columns_before=len(source.columns),
        columns_after=len(cleaned.columns),
        missing_before=int(source.isna().sum().sum()),
        missing_after=int(cleaned.isna().sum().sum()),
        exact_duplicates_before=int(source.duplicated().sum()),
        exact_duplicates_after=int(cleaned.duplicated().sum()),
        potential_duplicate_rows=int(duplicate_mask.sum()),
        potential_duplicate_groups=len(duplicate_groups),
        trimmed_values=trimmed_values,
        short_postal_codes=int(postal_lengths.lt(5).sum()),
        constant_columns=constant_columns,
    )


def markdown_table(rows: list[tuple[str, str, str]]) -> str:
    """Build a compact three-column Markdown table."""
    lines = [
        "| Colonne | Transformation | Raison |",
        "|:--|:--|:--|",
    ]
    lines.extend(f"| {column} | {action} | {reason} |" for column, action, reason in rows)
    return "\n".join(lines)


def build_report(
    source: pd.DataFrame,
    cleaned: pd.DataFrame,
    metrics: CleaningMetrics,
) -> str:
    """Create the professional Markdown cleaning report."""
    type_rows = "\n".join(
        f"| {column} | `{source[column].dtype}` | `{cleaned[column].dtype}` |"
        for column in source.columns
    )
    type_rows += (
        f"\n| {DUPLICATE_FLAG_COLUMN} | Non presente | "
        f"`{cleaned[DUPLICATE_FLAG_COLUMN].dtype}` |"
    )

    if metrics.trimmed_values:
        trim_details = "\n".join(
            f"- `{column}` : {count:,} valeur(s)"
            for column, count in metrics.trimmed_values.items()
        )
    else:
        trim_details = "- Aucun espace peripherique detecte."

    constant_columns = (
        ", ".join(f"`{column}`" for column in metrics.constant_columns)
        if metrics.constant_columns
        else "Aucune"
    )

    transformations = markdown_table(
        [
            (
                "`Order Date`, `Ship Date`",
                "Conversion de texte vers `datetime64[ns]`.",
                "Permettre des tris et calculs temporels fiables.",
            ),
            (
                "`Postal Code`",
                "Conversion du type numerique vers `string`.",
                "Traiter le code postal comme un identifiant, pas une mesure.",
            ),
            (
                "Toutes les colonnes texte",
                "Suppression des espaces en debut et fin de valeur.",
                "Uniformiser les libelles sans modifier leur contenu utile.",
            ),
            (
                f"`{DUPLICATE_FLAG_COLUMN}`",
                "Ajout d'un indicateur booleen, sans suppression de ligne.",
                "Signaler les lignes identiques lorsque `Row ID` est ignore.",
            ),
        ]
    )

    return f"""# Rapport de nettoyage des donnees

## 1. Perimetre

Cette etape produit une copie nettoyee du jeu de donnees. Le fichier source
`data/raw/Sample - Superstore.csv` n'est jamais modifie.

- Fichier produit : `data/processed/superstore_clean.csv`
- Encodage de lecture : `{SOURCE_ENCODING}`
- Format d'export des dates : `YYYY-MM-DD`
- Lignes avant nettoyage : **{metrics.rows_before:,}**
- Lignes apres nettoyage : **{metrics.rows_after:,}**
- Colonnes avant nettoyage : **{metrics.columns_before}**
- Colonnes apres nettoyage : **{metrics.columns_after}**

L'augmentation d'une colonne correspond uniquement a l'ajout de
`{DUPLICATE_FLAG_COLUMN}`. Aucune ligne n'a ete ajoutee ou supprimee.

## 2. Transformations effectuees

{transformations}

### Espaces supprimes

{trim_details}

## 3. Verification de la qualite

| Controle | Avant | Apres |
|:--|--:|--:|
| Valeurs manquantes | {metrics.missing_before:,} | {metrics.missing_after:,} |
| Doublons stricts | {metrics.exact_duplicates_before:,} | {metrics.exact_duplicates_after:,} |
| Lignes conservees | {metrics.rows_before:,} | {metrics.rows_after:,} |

- Lignes marquees comme doublons potentiels : **{metrics.potential_duplicate_rows:,}**
- Groupes de doublons potentiels : **{metrics.potential_duplicate_groups:,}**
- Aucun doublon potentiel n'a ete supprime.

## 4. Verification des types

| Colonne | Type avant | Type apres |
|:--|:--|:--|
{type_rows}

Les types ci-dessus correspondent au DataFrame en memoire. Un fichier CSV ne
stocke pas de schema de types ; lors d'un rechargement, les colonnes de dates
et le code postal doivent donc etre explicitement declares.

## 5. Colonnes modifiees

- `Order Date`
- `Ship Date`
- `Postal Code`
- `Product Name` ({metrics.trimmed_values.get("Product Name", 0):,} valeurs corrigees)
- `{DUPLICATE_FLAG_COLUMN}` (nouvelle colonne)

Les autres colonnes texte ont ete controlees et normalisees avec la meme
operation de suppression des espaces peripheriques, sans changement de valeur
detecte.

## 6. Anomalies restantes

- **{metrics.potential_duplicate_rows:,} lignes** restent marquees comme
  doublons potentiels. Une validation metier est requise avant toute suppression.
- **{metrics.short_postal_codes:,} codes postaux** comportent moins de cinq
  caracteres. Le fichier source les stockait deja sans zero initial ; aucun zero
  n'a ete reconstitue sans regle metier explicite.
- Colonne(s) constante(s) conservee(s) : {constant_columns}.
- `Row ID` est conserve pour assurer la tracabilite.
- Aucune valeur manquante et aucun doublon strict ne subsistent.

## 7. Conclusion

Le nettoyage a conserve les **{metrics.rows_after:,} lignes** du fichier source.
Les transformations sont limitees aux types, a la normalisation des espaces et
a l'ajout d'un indicateur de doublon potentiel. Aucune analyse metier n'a ete
realisee.
"""


def save_outputs(cleaned: pd.DataFrame, report: str) -> None:
    """Write the cleaned dataset and report to their target directories."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    cleaned.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8",
        date_format="%Y-%m-%d",
    )
    REPORT_PATH.write_text(report, encoding="utf-8")


def verify_export(expected: pd.DataFrame) -> None:
    """Reload the CSV with its schema and verify the persisted output."""
    exported = pd.read_csv(
        OUTPUT_PATH,
        dtype={POSTAL_CODE_COLUMN: "string"},
        parse_dates=list(DATE_COLUMNS),
    )

    if exported.shape != expected.shape:
        raise ValueError(
            f"Export shape mismatch: expected {expected.shape}, got {exported.shape}"
        )
    if exported.isna().sum().sum() != expected.isna().sum().sum():
        raise ValueError("Missing-value count changed during CSV export.")
    if exported[DUPLICATE_FLAG_COLUMN].sum() != expected[DUPLICATE_FLAG_COLUMN].sum():
        raise ValueError("Potential duplicate flags changed during CSV export.")


def main() -> None:
    """Run the complete cleaning pipeline."""
    source = load_source(SOURCE_PATH)
    cleaned, trimmed_values = clean_data(source)
    metrics = collect_metrics(source, cleaned, trimmed_values)
    report = build_report(source, cleaned, metrics)

    save_outputs(cleaned, report)
    verify_export(cleaned)

    print(f"Source rows: {metrics.rows_before:,}")
    print(f"Clean rows: {metrics.rows_after:,}")
    print(f"Potential duplicate rows: {metrics.potential_duplicate_rows:,}")
    print(f"Clean dataset: {OUTPUT_PATH}")
    print(f"Cleaning report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
