"""
Fetch historical data (1990-2026) for:
- NASDAQ (^IXIC)           — Yahoo Finance
- S&P 500 (^GSPC)          — Yahoo Finance
- Gold (GC=F)              — Yahoo Finance
- CSI Dividend Index (中证红利 000922) — Eastmoney + Sina Finance
"""

import urllib.request
import urllib.parse
import json
import ssl
import time
import pandas as pd
from datetime import datetime

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

START_TS = int(datetime(1990, 1, 1).timestamp())
END_TS   = int(datetime(2026, 4, 23).timestamp())


# ── Yahoo Finance ──────────────────────────────────────────────────────────────
def fetch_yahoo(name: str, symbol: str) -> pd.Series:
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}"
        f"?interval=1mo&period1={START_TS}&period2={END_TS}"
        f"&events=history&includeAdjustedClose=true"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        data = json.loads(r.read())
    result = data["chart"]["result"][0]
    dates  = pd.to_datetime(result["timestamp"], unit="s").normalize()
    closes = result["indicators"]["adjclose"][0]["adjclose"]
    s = pd.Series(closes, index=dates, name=name).dropna()
    s.index = s.index.to_period("M").to_timestamp("M")   # month-end
    s = s[~s.index.duplicated(keep="last")]
    return s


# ── Eastmoney: CSI Dividend Index monthly (2008-present) ──────────────────────
def fetch_eastmoney_csi() -> pd.Series:
    url = (
        "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        "?secid=1.000922&fields1=f1,f2,f3,f4,f5"
        "&fields2=f51,f52,f53,f54,f55,f56"
        "&klt=101&fqt=0&beg=19900101&end=20261231&lmt=10000"
    )
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.eastmoney.com"}
    )
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        d = json.loads(r.read())
    rows = []
    for line in d["data"]["klines"]:
        parts = line.split(",")
        rows.append((pd.to_datetime(parts[0]), float(parts[2])))   # date, close
    df = pd.DataFrame(rows, columns=["Date", "Close"]).set_index("Date")
    # Resample to month-end close
    s = df["Close"].resample("ME").last().dropna()
    s.name = "CSI_Dividend"
    return s


# ── Sina Finance: CSI Dividend Index daily (2005-2008, fill early gap) ─────────
def fetch_sina_csi_early() -> pd.Series:
    url = (
        "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php"
        "/CN_MarketData.getKLineData"
        "?symbol=sh000922&scale=240&ma=no&datalen=5000"
    )
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}
    )
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        data = json.loads(r.read().decode("gbk", "ignore"))
    rows = [(pd.to_datetime(item["day"]), float(item["close"])) for item in data]
    df = pd.DataFrame(rows, columns=["Date", "Close"]).set_index("Date")
    s = df["Close"].resample("ME").last().dropna()
    s.name = "CSI_Dividend"
    return s


# ── Main ───────────────────────────────────────────────────────────────────────
all_series = {}

for name, symbol in [("NASDAQ", "^IXIC"), ("SP500", "^GSPC"), ("Gold", "GC=F")]:
    print(f"Fetching {name} ({symbol}) ...", end=" ", flush=True)
    try:
        s = fetch_yahoo(name, symbol)
        all_series[name] = s
        print(f"OK  {len(s)} rows  [{s.index[0].date()} → {s.index[-1].date()}]")
    except Exception as e:
        print(f"FAILED: {e}")
    time.sleep(0.8)

print("Fetching CSI Dividend Index (000922) from Eastmoney ...", end=" ", flush=True)
try:
    em = fetch_eastmoney_csi()
    print(f"OK  {len(em)} rows  [{em.index[0].date()} → {em.index[-1].date()}]")
except Exception as e:
    print(f"FAILED: {e}")
    em = pd.Series(name="CSI_Dividend", dtype=float)

print("Fetching CSI Dividend Index early data from Sina Finance ...", end=" ", flush=True)
try:
    sina = fetch_sina_csi_early()
    print(f"OK  {len(sina)} rows  [{sina.index[0].date()} → {sina.index[-1].date()}]")
except Exception as e:
    print(f"FAILED: {e}")
    sina = pd.Series(name="CSI_Dividend", dtype=float)

# Merge: Sina for dates before Eastmoney starts, Eastmoney for the rest
if not em.empty and not sina.empty:
    em_start = em.index[0]
    sina_early = sina[sina.index < em_start]
    csi = pd.concat([sina_early, em]).sort_index()
    csi = csi[~csi.index.duplicated(keep="last")]
elif not em.empty:
    csi = em
else:
    csi = sina
all_series["CSI_Dividend"] = csi

# ── Combine & save ─────────────────────────────────────────────────────────────
combined = pd.DataFrame(all_series).sort_index()
combined.index.name = "Date"

print("\n=== Preview (first 5 rows) ===")
print(combined.head().to_string())
print("\n=== Preview (last 5 rows) ===")
print(combined.tail().to_string())
print(f"\nShape: {combined.shape}")

# Coverage per column
print("\n=== Data Coverage ===")
for col in combined.columns:
    s = combined[col].dropna()
    print(f"  {col:15s}: {len(s):4d} months  [{s.index[0].date()} → {s.index[-1].date()}]")

out_path = "d:/Work/Quant/historical_data_1990_2026.csv"
combined.to_csv(out_path, float_format="%.4f")
print(f"\nSaved → {out_path}")

print("\n=== Summary Statistics ===")
print(combined.describe().to_string())
