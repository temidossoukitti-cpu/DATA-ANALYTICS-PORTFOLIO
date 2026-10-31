"""Run the initial quality and structure checks on the source dataset."""

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = PROJECT_ROOT / "data" / "raw" / "Sample - Superstore.csv"


if not SOURCE_PATH.exists():
    raise FileNotFoundError(f"Source file not found: {SOURCE_PATH}")

df = pd.read_csv(SOURCE_PATH, encoding="latin-1")

print("=== SHAPE ===")
print(df.shape)

print("\n=== COLONNES + TYPES ===")
print(df.dtypes)

print("\n=== VALEURS MANQUANTES ===")
print(df.isnull().sum())

print("\n=== DOUBLONS ===")
print("Lignes dupliquees (toutes colonnes):", df.duplicated().sum())
print("Row ID dupliques:", df['Row ID'].duplicated().sum())

print("\n=== STATISTIQUES NUMERIQUES ===")
print(df[['Sales','Quantity','Discount','Profit']].describe())

print("\n=== VARIABLES CATEGORIQUES ===")
for col in ['Ship Mode','Segment','Country','Region','Category','Sub-Category']:
    print(f"\n{col} --- {df[col].nunique()} valeurs uniques:")
    print(df[col].value_counts().to_string())

print("\n=== TYPE COLONNES DATES ===")
print("Order Date dtype:", df['Order Date'].dtype)
print("Exemples:", df['Order Date'].head(3).tolist())

df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%m/%d/%Y')

print("\n=== PLAGE DE DATES ===")
print("Min:", df['Order Date'].min().date())
print("Max:", df['Order Date'].max().date())
print("Annees:", sorted(df['Order Date'].dt.year.unique().tolist()))

print("\n=== ANOMALIES NUMERIQUES ===")
print("Profit < 0:", (df['Profit'] < 0).sum())
print("Discount > 0.5:", (df['Discount'] > 0.5).sum())
print("Discount >= 0.8:", (df['Discount'] >= 0.8).sum())
print("Sales <= 0:", (df['Sales'] <= 0).sum())
print("Quantity <= 0:", (df['Quantity'] <= 0).sum())

print("\n=== COHERENCE DATES ===")
print("Ship avant Order:", (df['Ship Date'] < df['Order Date']).sum())

print("\n=== COLONNE COUNTRY ===")
print("Valeurs uniques:", df['Country'].unique().tolist())

print("\n=== POSTAL CODE ===")
print("Dtype:", df['Postal Code'].dtype)
print("Manquants:", df['Postal Code'].isnull().sum())
print("Exemple codes:", df['Postal Code'].head(5).tolist())

print("\n=== CARDINALITES ===")
print("Clients uniques:", df['Customer ID'].nunique())
print("Produits uniques:", df['Product ID'].nunique())
print("Commandes uniques:", df['Order ID'].nunique())
print("Villes uniques:", df['City'].nunique())
print("Etats uniques:", df['State'].nunique())

print("\n=== PROFIT PAR CATEGORIE ===")
print(df.groupby('Category')[['Sales','Profit']].sum().round(2).to_string())

print("\n=== DISCOUNT MOYEN PAR CATEGORIE ===")
print(df.groupby('Category')['Discount'].mean().round(3).to_string())
