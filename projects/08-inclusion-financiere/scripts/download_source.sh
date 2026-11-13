#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW="$ROOT/data/raw"
mkdir -p "$RAW"
curl -fL --retry 2 -o "$RAW/GlobalFindexDatabase2025.csv" \
  'https://thedocs.worldbank.org/en/doc/be6615202d1f08a25855c8ac2d615122-0050012025/related/GlobalFindexDatabase2025.csv'
curl -fL --retry 2 -o "$RAW/GlobalFindex2025-glossary.xlsx" \
  'https://thedocs.worldbank.org/en/doc/be6615202d1f08a25855c8ac2d615122-0050012025/related/GlobalFindex2025-glossary.xlsx'
echo "Sources téléchargées dans $RAW"
