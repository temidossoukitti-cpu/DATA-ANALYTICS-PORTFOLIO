"""Download daily Binance Spot klines for BTCUSDT and ETHUSDT.

Source: https://api.binance.com/api/v3/klines
The script is intentionally public-data only and does not require credentials.
"""
from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

API = "https://api.binance.com/api/v3/klines"
COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "trades", "taker_buy_base_volume", "taker_buy_quote_volume", "ignore",
]
NUMERIC = ["open", "high", "low", "close", "volume", "quote_volume", "trades",
           "taker_buy_base_volume", "taker_buy_quote_volume"]


def fetch_symbol(symbol: str, start: str, end: str | None) -> pd.DataFrame:
    start_ms = int(pd.Timestamp(start, tz="UTC").timestamp() * 1000)
    end_ms = int(pd.Timestamp(end, tz="UTC").timestamp() * 1000) if end else None
    rows: list[list] = []
    cursor = start_ms
    session = requests.Session()
    while True:
        params = {"symbol": symbol, "interval": "1d", "limit": 1000, "startTime": cursor}
        if end_ms is not None:
            params["endTime"] = end_ms
        response = session.get(API, params=params, timeout=30)
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        rows.extend(batch)
        last_open = int(batch[-1][0])
        if len(batch) < 1000 or (end_ms is not None and last_open >= end_ms):
            break
        cursor = last_open + 86_400_000
        time.sleep(0.15)
    df = pd.DataFrame(rows, columns=COLUMNS)
    if df.empty:
        raise RuntimeError(f"No data returned for {symbol}")
    df["symbol"] = symbol
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.drop_duplicates(["symbol", "open_time"]).sort_values("open_time")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2017-01-01")
    parser.add_argument("--end", default=None, help="UTC date/time; defaults to now")
    args = parser.parse_args()
    out = Path(__file__).parents[1] / "data" / "raw"
    out.mkdir(parents=True, exist_ok=True)
    end = args.end or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    frames = [fetch_symbol(symbol, args.start, end) for symbol in ("BTCUSDT", "ETHUSDT")]
    data = pd.concat(frames, ignore_index=True)
    data.to_csv(out / "binance_spot_daily_ohlc.csv", index=False, date_format="%Y-%m-%dT%H:%M:%SZ")
    metadata = out / "SOURCE.md"
    metadata.write_text(
        f"# Source\n\n- Provider: Binance Spot public REST API\n- Endpoint: `{API}`\n- Symbols: BTCUSDT, ETHUSDT\n- Interval: 1d\n- Requested window: {args.start} to {end}\n- Retrieved at: {datetime.now(timezone.utc).isoformat()}\n- Kline fields: open time, OHLC, volume, close time, quote volume, trades and taker-buy volumes.\n",
        encoding="utf-8",
    )
    print(f"saved {len(data):,} rows to {out / 'binance_spot_daily_ohlc.csv'}")


if __name__ == "__main__":
    main()
