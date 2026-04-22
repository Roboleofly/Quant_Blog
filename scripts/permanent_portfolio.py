"""
Permanent Portfolio: equal 1/4 allocation
Rebalancing variants: Buy & Hold / Annual / Quarterly / Monthly
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv("d:/Work/Quant/historical_data_1990_2026.csv",
                 index_col="Date", parse_dates=True)

COLS   = ["NASDAQ", "SP500", "Gold", "CSI_Dividend"]
LABELS = ["NASDAQ", "S&P 500", "Gold", "CSI Dividend"]
COLORS = ["#00d4ff", "#ff9500", "#ffd700", "#ff4d6d"]

prices  = df[COLS].dropna()
n_years = (prices.index[-1] - prices.index[0]).days / 365.25
print(f"Period: {prices.index[0].date()} → {prices.index[-1].date()}  ({n_years:.1f} yrs)")

# ── Generic rebalancer ────────────────────────────────────────────────────────
def simulate(prices, freq):
    """
    freq: 'BH' = buy-and-hold, 'A' = annual, 'Q' = quarterly, 'M' = monthly
    Returns Series of portfolio value indexed like prices.
    """
    shares = {c: 0.25 / prices[c].iloc[0] for c in COLS}
    vals   = {}
    last_rebal_period = None

    for date, row in prices.iterrows():
        # Determine rebalance trigger
        if freq == "A":
            period = date.year
        elif freq == "Q":
            period = (date.year, date.quarter)
        elif freq == "M":
            period = (date.year, date.month)
        else:
            period = None

        if freq != "BH" and period != last_rebal_period and last_rebal_period is not None:
            port_val = sum(shares[c] * row[c] for c in COLS)
            shares   = {c: 0.25 * port_val / row[c] for c in COLS}

        last_rebal_period = period
        vals[date] = sum(shares[c] * row[c] for c in COLS)

    return pd.Series(vals)

# ── Risk metrics ──────────────────────────────────────────────────────────────
def metrics(vals, rf=0.03):
    r       = vals.pct_change().dropna()
    n_yrs   = (vals.index[-1] - vals.index[0]).days / 365.25
    total   = vals.iloc[-1] / vals.iloc[0]
    cagr    = total ** (1 / n_yrs) - 1
    vol     = r.std() * np.sqrt(12)
    mdd     = ((vals - vals.cummax()) / vals.cummax()).min()
    sharpe  = (r.mean() * 12 - rf) / vol
    calmar  = cagr / abs(mdd)
    return dict(cagr=cagr, total=total, vol=vol, mdd=mdd, sharpe=sharpe, calmar=calmar)

STRATEGIES = [
    ("Buy & Hold",          "BH", "#8b949e"),
    ("Annual Rebal",        "A",  "#b5ff4d"),
    ("Quarterly Rebal",     "Q",  "#ff9500"),
    ("Monthly Rebal",       "M",  "#00d4ff"),
]

results = {}
for name, freq, color in STRATEGIES:
    vals = simulate(prices, freq)
    results[name] = {"vals": vals, "color": color, **metrics(vals)}

# ── Print table ───────────────────────────────────────────────────────────────
print("\n" + "="*72)
print("  PERMANENT PORTFOLIO — Rebalancing Frequency Comparison")
print("="*72)
print(f"  {'Strategy':<20}  {'CAGR':>8}  {'Total':>7}  {'Vol':>7}  {'MaxDD':>8}  {'Sharpe':>7}  {'Calmar':>7}")
print(f"  {'-'*20}  {'-'*8}  {'-'*7}  {'-'*7}  {'-'*8}  {'-'*7}  {'-'*7}")
for name, freq, _ in STRATEGIES:
    m = results[name]
    print(f"  {name:<20}  {m['cagr']:>8.2%}  {m['total']:>7.2f}x  {m['vol']:>7.2%}  "
          f"{m['mdd']:>8.2%}  {m['sharpe']:>7.2f}  {m['calmar']:>7.2f}")
print("="*72)

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(16, 16),
                         gridspec_kw={"height_ratios": [3, 1.4, 1.4]})
fig.patch.set_facecolor("#0d1117")

# ── Panel 1: cumulative growth ────────────────────────────────────────────────
ax = axes[0]
ax.set_facecolor("#161b22")

for c, label, color in zip(COLS, LABELS, COLORS):
    norm = prices[c] / prices[c].iloc[0]
    ax.plot(norm.index, norm.values, color=color, linewidth=0.9,
            alpha=0.3, linestyle="--")

for name, freq, color in STRATEGIES:
    v = results[name]["vals"]
    m = results[name]
    ax.plot(v.index, v / v.iloc[0],
            color=color, linewidth=2.0, alpha=0.92,
            label=f"{name}  CAGR {m['cagr']:.2%}  Sharpe {m['sharpe']:.2f}")

ax.set_title(
    f"Permanent Portfolio 1/4 Each — Growth of $1  "
    f"({prices.index[0].strftime('%Y-%m')} → {prices.index[-1].strftime('%Y-%m')})",
    color="white", fontsize=13, fontweight="bold", pad=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}x"))
ax.tick_params(colors="#8b949e", labelsize=9)
for spine in ax.spines.values():
    spine.set_edgecolor("#30363d")
ax.grid(color="#21262d", linewidth=0.7)
ax.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="white",
          fontsize=10, loc="upper left")
ax.set_xlim(prices.index[0], prices.index[-1] + pd.DateOffset(months=6))

# ── Panel 2: drawdown ─────────────────────────────────────────────────────────
ax2 = axes[1]
ax2.set_facecolor("#161b22")

for name, freq, color in STRATEGIES:
    v  = results[name]["vals"]
    dd = (v - v.cummax()) / v.cummax() * 100
    ax2.fill_between(dd.index, dd.values, 0, color=color, alpha=0.18)
    ax2.plot(dd.index, dd.values, color=color, linewidth=1.3, alpha=0.85,
             label=f"{name}  MaxDD {results[name]['mdd']:.1%}")

ax2.set_title("Drawdown (%)", color="white", fontsize=11, fontweight="bold", pad=6)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
ax2.tick_params(colors="#8b949e", labelsize=9)
for spine in ax2.spines.values():
    spine.set_edgecolor("#30363d")
ax2.grid(color="#21262d", linewidth=0.7)
ax2.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="white",
           fontsize=9, loc="lower left", ncol=2)
ax2.set_xlim(prices.index[0], prices.index[-1])

# ── Panel 3: rolling 3-year CAGR ─────────────────────────────────────────────
ax3 = axes[2]
ax3.set_facecolor("#161b22")
WINDOW = 36  # months

for name, freq, color in STRATEGIES:
    v = results[name]["vals"]
    roll_cagr = (v / v.shift(WINDOW)) ** (12 / WINDOW) - 1
    ax3.plot(roll_cagr.index, roll_cagr * 100, color=color,
             linewidth=1.3, alpha=0.85, label=name)

ax3.axhline(0, color="#8b949e", linewidth=0.8, linestyle="--", alpha=0.5)
ax3.set_title("Rolling 3-Year Annualized Return (%)", color="white",
              fontsize=11, fontweight="bold", pad=6)
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
ax3.tick_params(colors="#8b949e", labelsize=9)
for spine in ax3.spines.values():
    spine.set_edgecolor("#30363d")
ax3.grid(color="#21262d", linewidth=0.7)
ax3.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="white",
           fontsize=9, loc="lower left", ncol=2)
ax3.set_xlim(prices.index[0], prices.index[-1])

plt.tight_layout(h_pad=0.5)
fig.savefig("d:/Work/Quant/permanent_portfolio_rebal.png", dpi=150,
            bbox_inches="tight", facecolor=fig.get_facecolor())
print("\nSaved: permanent_portfolio_rebal.png")
plt.show()
