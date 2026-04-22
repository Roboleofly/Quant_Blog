import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec

df = pd.read_csv("d:/Work/Quant/historical_data_1990_2026.csv", index_col="Date", parse_dates=True)

def normalize(s):
    s = s.dropna()
    return s / s.iloc[0] * 100

SERIES = [
    ("NASDAQ",       "#00d4ff", "NASDAQ Composite"),
    ("SP500",        "#ff9500", "S&P 500"),
    ("Gold",         "#ffd700", "Gold (USD/oz)"),
    ("CSI_Dividend", "#ff4d6d", "CSI Dividend (A-shares)"),
]

# ── Fig 1: 4 individual subplots ──────────────────────────────────────────────
fig = plt.figure(figsize=(16, 12))
fig.patch.set_facecolor("#0d1117")
gs = GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)
axes = [fig.add_subplot(gs[i // 2, i % 2]) for i in range(4)]

for ax, (col, color, label) in zip(axes, SERIES):
    s = df[col].dropna()
    ax.set_facecolor("#161b22")
    ax.plot(s.index, s.values, color=color, linewidth=1.4, alpha=0.95)
    ax.fill_between(s.index, s.values, alpha=0.12, color=color)
    ax.annotate(f"{s.iloc[0]:,.0f}", xy=(s.index[0], s.iloc[0]),
                xytext=(6, 6), textcoords="offset points",
                fontsize=7.5, color=color, alpha=0.85)
    ax.annotate(f"{s.iloc[-1]:,.0f}", xy=(s.index[-1], s.iloc[-1]),
                xytext=(-55, 6), textcoords="offset points",
                fontsize=7.5, color=color, alpha=0.85)
    ax.set_title(label, color="white", fontsize=11, fontweight="bold", pad=8)
    ax.tick_params(colors="#8b949e", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.grid(axis="y", color="#21262d", linewidth=0.7)
    ax.set_xlim(s.index[0], s.index[-1])

fig.suptitle("Global Asset Historical Prices  1990–2026", color="white",
             fontsize=14, fontweight="bold", y=1.01)
fig.savefig("d:/Work/Quant/historical_subplots.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())

# ── Fig 2: normalized from each series' own start ─────────────────────────────
fig2, ax2 = plt.subplots(figsize=(16, 6))
fig2.patch.set_facecolor("#0d1117")
ax2.set_facecolor("#161b22")

for col, color, label in SERIES:
    ns = normalize(df[col])
    ax2.plot(ns.index, ns.values, color=color, linewidth=1.6, label=label, alpha=0.9)

ax2.set_title("Normalized Comparison — each series rebased to 100 at its own start", color="white",
              fontsize=13, fontweight="bold", pad=10)
ax2.tick_params(colors="#8b949e", labelsize=9)
for spine in ax2.spines.values():
    spine.set_edgecolor("#30363d")
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax2.grid(color="#21262d", linewidth=0.7)
ax2.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="white",
           fontsize=10, loc="upper left")
ax2.set_xlim(pd.Timestamp("1990-01-01"), pd.Timestamp("2026-06-01"))

fig2.savefig("d:/Work/Quant/historical_normalized.png", dpi=150, bbox_inches="tight",
             facecolor=fig2.get_facecolor())

# ── Fig 3: % change in common overlap (all 4 have data) ───────────────────────
# Find common window where all 4 series are non-null
common = df.dropna()
common_start = common.index[0]
common_end   = common.index[-1]

# % change relative to common_start
pct = (common / common.iloc[0] - 1) * 100

fig3, ax3 = plt.subplots(figsize=(16, 7))
fig3.patch.set_facecolor("#0d1117")
ax3.set_facecolor("#161b22")

for col, color, label in SERIES:
    ax3.plot(pct.index, pct[col].values, color=color, linewidth=1.8, label=label, alpha=0.92)
    # Annotate final % gain
    final = pct[col].iloc[-1]
    ax3.annotate(f"+{final:.0f}%" if final >= 0 else f"{final:.0f}%",
                 xy=(pct.index[-1], final),
                 xytext=(6, 0), textcoords="offset points",
                 fontsize=9, color=color, fontweight="bold", va="center")

ax3.axhline(0, color="#8b949e", linewidth=0.8, linestyle="--", alpha=0.5)

start_str = common_start.strftime("%Y-%m")
end_str   = common_end.strftime("%Y-%m")
ax3.set_title(f"Cumulative % Return from Common Start  ({start_str} → {end_str})",
              color="white", fontsize=13, fontweight="bold", pad=10)
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:+,.0f}%"))
ax3.tick_params(colors="#8b949e", labelsize=9)
for spine in ax3.spines.values():
    spine.set_edgecolor("#30363d")
ax3.grid(color="#21262d", linewidth=0.7)
ax3.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="white",
           fontsize=11, loc="upper left")
ax3.set_xlim(common_start, common_end + pd.DateOffset(months=6))

fig3.savefig("d:/Work/Quant/historical_pct_overlap.png", dpi=150, bbox_inches="tight",
             facecolor=fig3.get_facecolor())

print(f"Common overlap: {start_str} → {end_str}  ({len(common)} months)")
print("Final cumulative returns from overlap start:")
for col, _, label in SERIES:
    print(f"  {label:30s}: {pct[col].iloc[-1]:+.1f}%")
print("\nSaved: historical_subplots.png  historical_normalized.png  historical_pct_overlap.png")
plt.show()
