# Version "données réelles" : à lancer sur ton PC (pip install yfinance pandas)
import yfinance as yf
tickers = ["AAPL","MSFT","JPM","V","JNJ","XOM","PG","CAT","T","NEE"]  # à adapter
df = yf.download(tickers + ["^GSPC"], start="2024-11-01", end="2026-10-24",
                 interval="1wk", auto_adjust=True)["Close"]
df.index.name = "date"
df.to_csv("prices_weekly_real.csv")
print(df.tail())
