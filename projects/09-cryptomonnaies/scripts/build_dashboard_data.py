from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parents[1]
RESULTS = ROOT / "results"


def main() -> None:
    summary = pd.read_csv(RESULTS / "asset_summary.csv").where(lambda x: x.notna(), None)
    daily = pd.read_csv(RESULTS / "daily_metrics.csv", parse_dates=["open_time"])
    daily = daily.sort_values(["open_time", "symbol"])
    wide = daily.pivot_table(index="open_time", columns="symbol", values=["wealth", "close", "drawdown", "rolling_vol_30d"])
    wide = wide.dropna(subset=[("wealth", "BTCUSDT"), ("wealth", "ETHUSDT")]).reset_index()
    wide = wide.iloc[::7].copy()
    wide.columns = ["date" if (isinstance(c, str) and c == "open_time") or (isinstance(c, tuple) and c[0] == "open_time") else f"{c[1].lower()}_{c[0]}" for c in wide.columns]
    monthly = pd.read_csv(RESULTS / "monthly_metrics.csv")
    monthly["month"] = monthly["month"].astype(str)
    payload = {
        "summary": summary.to_dict(orient="records"),
        "correlation": float(pd.read_csv(RESULTS / "return_correlation.csv", index_col=0).iloc[0, 1]),
        "last_updated": str(daily["open_time"].max().date()),
        "series": wide.to_dict(orient="records"),
        "monthly": monthly.where(lambda x: x.notna(), None).to_dict(orient="records"),
    }
    def clean(value):
        if isinstance(value, dict):
            return {k: clean(v) for k, v in value.items()}
        if isinstance(value, list):
            return [clean(v) for v in value]
        if pd.isna(value):
            return None
        return value

    (RESULTS / "dashboard_data.json").write_text(json.dumps(clean(payload), indent=2, allow_nan=False, default=str), encoding="utf-8")
    print(f"dashboard payload: {len(payload['series'])} series points, {len(payload['monthly'])} monthly rows")


if __name__ == "__main__":
    main()
