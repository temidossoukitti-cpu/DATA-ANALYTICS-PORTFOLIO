from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).parents[1]
RAW = ROOT / "data" / "raw" / "binance_spot_daily_ohlc.csv"
RESULTS = ROOT / "results"
VISUALS = ROOT / "visuals"
RESULTS.mkdir(exist_ok=True)
VISUALS.mkdir(exist_ok=True)


def main() -> None:
    df = pd.read_csv(RAW, parse_dates=["open_time", "close_time"])
    df = df.sort_values(["symbol", "open_time"])
    df["daily_return"] = df.groupby("symbol")["close"].pct_change()
    df["log_return"] = np.log1p(df["daily_return"])
    df["wealth"] = df.groupby("symbol")["close"].transform(lambda s: s / s.iloc[0] * 100)
    df["running_max"] = df.groupby("symbol")["wealth"].cummax()
    df["drawdown"] = df["wealth"] / df["running_max"] - 1
    df["rolling_vol_30d"] = df.groupby("symbol")["daily_return"].transform(lambda s: s.rolling(30).std() * np.sqrt(365))
    df.to_csv(RESULTS / "daily_metrics.csv", index=False, date_format="%Y-%m-%dT%H:%M:%SZ")

    rows = []
    for symbol, g in df.groupby("symbol"):
        r = g["daily_return"].dropna()
        years = max((g["open_time"].max() - g["open_time"].min()).days / 365.25, 1 / 365.25)
        total_return = g["close"].iloc[-1] / g["close"].iloc[0] - 1
        cagr = (1 + total_return) ** (1 / years) - 1 if total_return > -1 else np.nan
        rows.append({
            "symbol": symbol, "start_date": g["open_time"].min().date(), "end_date": g["open_time"].max().date(),
            "observations": len(g), "start_close": g["close"].iloc[0], "end_close": g["close"].iloc[-1],
            "total_return": total_return, "cagr": cagr, "annualized_volatility": r.std() * np.sqrt(365),
            "best_day": r.max(), "worst_day": r.min(), "max_drawdown": g["drawdown"].min(),
            "positive_days_pct": (r > 0).mean(),
        })
    summary = pd.DataFrame(rows)
    summary.to_csv(RESULTS / "asset_summary.csv", index=False)

    wide = df.pivot(index="open_time", columns="symbol", values="daily_return").dropna()
    wide.corr().to_csv(RESULTS / "return_correlation.csv")
    monthly = df.assign(month=df["open_time"].dt.to_period("M")).groupby(["month", "symbol"], as_index=False).agg(
        close=("close", "last"), monthly_return=("close", lambda s: s.iloc[-1] / s.iloc[0] - 1),
        monthly_volatility=("daily_return", lambda s: s.std() * np.sqrt(365)),
    )
    monthly.to_csv(RESULTS / "monthly_metrics.csv", index=False)
    quality = pd.DataFrame([
        {"check": "rows", "value": len(df), "status": "PASS"},
        {"check": "symbols", "value": ", ".join(sorted(df.symbol.unique())), "status": "PASS"},
        {"check": "duplicate_symbol_date", "value": int(df.duplicated(["symbol", "open_time"]).sum()), "status": "PASS" if not df.duplicated(["symbol", "open_time"]).any() else "FAIL"},
        {"check": "missing_close", "value": int(df.close.isna().sum()), "status": "PASS" if not df.close.isna().any() else "FAIL"},
    ])
    quality.to_csv(RESULTS / "quality_check.csv", index=False)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12, 6))
    for symbol, g in df.groupby("symbol"):
        ax.plot(g.open_time, g.wealth, label=symbol, linewidth=1.6)
    ax.set_title("Croissance d’un investissement indicatif (base 100)")
    ax.set_ylabel("Valeur indicielle")
    ax.legend()
    fig.tight_layout(); fig.savefig(VISUALS / "wealth_index.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 6))
    for symbol, g in df.groupby("symbol"):
        ax.plot(g.open_time, g.drawdown * 100, label=symbol, linewidth=1.2)
    ax.set_title("Drawdown historique")
    ax.set_ylabel("Drawdown (%)")
    ax.legend()
    fig.tight_layout(); fig.savefig(VISUALS / "drawdown.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    summary.set_index("symbol")[["cagr", "annualized_volatility", "max_drawdown"]].mul(100).plot.bar(ax=ax, color=["#31c48d", "#f59e0b", "#ef4444"])
    ax.set_title("Rendement annualisé, volatilité et drawdown maximal")
    ax.set_ylabel("Pourcentage")
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout(); fig.savefig(VISUALS / "risk_return_summary.png", dpi=160); plt.close(fig)

    payload = {"summary": summary.replace({np.nan: None}).to_dict(orient="records"), "correlation": float(wide.corr().iloc[0, 1]), "last_updated": str(df.open_time.max().date())}
    (RESULTS / "dashboard_data.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
