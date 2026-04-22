"""
Generate a dated research report and register it in _manifest.json.
Usage: python generate_report.py
"""
import base64, datetime, json, subprocess, sys

REPORTS_DIR = "d:/Work/Quant/reports"
MANIFEST    = f"{REPORTS_DIR}/_manifest.json"

def img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

today     = datetime.date.today()
today_str = today.strftime("%Y-%m-%d")
today_fmt = today.strftime("%B %d, %Y")

img1 = img_b64("d:/Work/Quant/historical_subplots.png")
img2 = img_b64("d:/Work/Quant/historical_pct_overlap.png")
img3 = img_b64("d:/Work/Quant/permanent_portfolio_rebal.png")

REPORT_META = {
    "date":     today_str,
    "slug":     "permanent-portfolio",
    "title":    "Permanent Portfolio: A Cross-Asset Allocation Study",
    "subtitle": "NASDAQ · S&P 500 · Gold · CSI Dividend Index (A-Shares)",
    "abstract": (
        "We examine equal-weighted permanent portfolio performance (25% each) across four major "
        "global assets over 21.2 years. Annual rebalancing delivers CAGR 11.93% with Sharpe 0.75, "
        "outperforming buy-and-hold and higher-frequency strategies. Maximum drawdown is capped at "
        "−40.4%, versus −70.2% for the most volatile single constituent."
    ),
    "tags":     ["Asset Allocation", "Backtesting", "Rebalancing"],
    "filename": f"{today_str}-permanent-portfolio.html",
    "metrics":  {"CAGR": "11.93%", "Sharpe": "0.75", "Period": "2005-2026"},
}

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{REPORT_META['title']} | Quant Research</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  :root{{--gs-navy:#00205B;--gs-blue:#003087;--gs-gold:#B5A46E;--gs-light:#F4F6FA;--gs-border:#D6DCE8;--gs-text:#1A1A2E;--gs-muted:#5A6478;--gs-green:#007A5E;--gs-red:#C0392B;}}
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{font-family:'Inter','Helvetica Neue',Arial,sans-serif;background:#FFFFFF;color:var(--gs-text);font-size:13px;line-height:1.6;}}
  nav{{background:var(--gs-navy);padding:0 48px;display:flex;align-items:center;justify-content:space-between;height:52px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,0.3);}}
  .nav-logo{{font-size:14px;font-weight:700;color:#FFF;letter-spacing:3px;text-decoration:none;}}
  .nav-logo span{{color:#B5A46E;}}
  .nav-back{{font-size:11.5px;color:#A8B8D0;text-decoration:none;transition:color .2s;}}
  .nav-back:hover{{color:#FFF;}}
  .header{{background:var(--gs-navy);}}
  .header-top{{display:flex;align-items:center;justify-content:space-between;padding:18px 48px;border-bottom:2px solid var(--gs-gold);}}
  .logo{{font-size:22px;font-weight:700;color:#FFF;letter-spacing:3px;text-transform:uppercase;}}
  .logo span{{color:var(--gs-gold);}}
  .header-meta{{text-align:right;color:#A8B8D0;font-size:11px;line-height:1.7;}}
  .header-meta strong{{color:#FFF;font-size:12px;}}
  .header-band{{background:var(--gs-blue);padding:22px 48px 20px;}}
  .report-type{{font-size:10px;font-weight:600;color:var(--gs-gold);letter-spacing:2.5px;text-transform:uppercase;margin-bottom:6px;}}
  .report-title{{font-size:26px;font-weight:700;color:#FFF;line-height:1.25;margin-bottom:8px;}}
  .report-subtitle{{font-size:13px;color:#A8B8D0;}}
  .body-wrap{{max-width:1100px;margin:0 auto;padding:40px 48px 60px;}}
  .exec-box{{background:var(--gs-light);border-left:4px solid var(--gs-navy);padding:20px 24px;margin-bottom:36px;border-radius:0 4px 4px 0;}}
  .exec-box .label{{font-size:9px;font-weight:700;color:var(--gs-navy);letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;}}
  .exec-box p{{font-size:13px;line-height:1.75;}}
  .findings-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:40px;}}
  .finding-card{{border:1px solid var(--gs-border);border-top:3px solid var(--gs-navy);padding:16px 18px;border-radius:0 0 4px 4px;}}
  .finding-card .metric{{font-size:28px;font-weight:700;color:var(--gs-navy);line-height:1;margin-bottom:4px;}}
  .finding-card .metric.green{{color:var(--gs-green);}}
  .finding-card .metric.gold{{color:#8B7340;}}
  .finding-card .desc{{font-size:11px;color:var(--gs-muted);font-weight:500;line-height:1.4;}}
  .section{{margin-bottom:40px;}}
  .section-header{{display:flex;align-items:center;gap:12px;margin-bottom:18px;padding-bottom:8px;border-bottom:1px solid var(--gs-border);}}
  .section-num{{background:var(--gs-navy);color:#FFF;font-size:10px;font-weight:700;width:22px;height:22px;display:flex;align-items:center;justify-content:center;border-radius:2px;flex-shrink:0;}}
  .section-title{{font-size:15px;font-weight:700;color:var(--gs-navy);}}
  .chart-wrap{{border:1px solid var(--gs-border);border-radius:4px;overflow:hidden;margin-bottom:10px;}}
  .chart-wrap img{{width:100%;display:block;}}
  .chart-caption{{font-size:10.5px;color:var(--gs-muted);margin-bottom:28px;font-style:italic;padding-left:2px;}}
  table{{width:100%;border-collapse:collapse;margin-bottom:10px;font-size:12.5px;}}
  thead tr{{background:var(--gs-navy);color:#FFF;}}
  thead th{{padding:10px 14px;text-align:left;font-weight:600;font-size:11px;letter-spacing:0.5px;text-transform:uppercase;}}
  thead th.num{{text-align:right;}}
  tbody tr:nth-child(even){{background:var(--gs-light);}}
  tbody tr:hover{{background:#E8EDF5;}}
  tbody td{{padding:9px 14px;border-bottom:1px solid var(--gs-border);}}
  tbody td.num{{text-align:right;font-variant-numeric:tabular-nums;}}
  .highlight-row{{background:#EBF0F9!important;font-weight:600;}}
  .highlight-row td{{color:var(--gs-navy);}}
  .up{{color:var(--gs-green);font-weight:600;}}
  .down{{color:var(--gs-red);font-weight:600;}}
  .gold{{color:#8B7340;font-weight:600;}}
  .insight-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:28px;}}
  .insight{{border:1px solid var(--gs-border);padding:16px 18px;border-radius:4px;}}
  .insight .i-label{{font-size:9.5px;font-weight:700;color:var(--gs-gold);letter-spacing:1.8px;text-transform:uppercase;margin-bottom:7px;}}
  .insight p{{font-size:12.5px;line-height:1.65;}}
  .insight strong{{color:var(--gs-navy);}}
  .timeline{{border-left:2px solid var(--gs-border);padding-left:20px;margin-bottom:28px;}}
  .tl-item{{position:relative;margin-bottom:14px;padding-left:4px;}}
  .tl-item::before{{content:'';position:absolute;left:-25px;top:5px;width:8px;height:8px;border-radius:50%;background:var(--gs-navy);border:2px solid #FFF;box-shadow:0 0 0 1px var(--gs-navy);}}
  .tl-year{{font-size:10px;font-weight:700;color:var(--gs-muted);margin-bottom:2px;}}
  .tl-text{{font-size:12.5px;}}
  .badge{{display:inline-block;padding:2px 9px;border-radius:2px;font-size:10px;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;}}
  .badge-buy{{background:#D4EDDA;color:#155724;}}
  .badge-neutral{{background:#FFF3CD;color:#856404;}}
  .badge-overweight{{background:#CCE5FF;color:#004085;}}
  footer{{background:var(--gs-navy);padding:24px 48px;margin-top:60px;}}
  footer p{{font-size:10px;color:#7A91B0;line-height:1.7;}}
  .footer-brand{{font-size:11px;font-weight:700;color:var(--gs-gold);letter-spacing:2px;margin-bottom:10px;}}
  hr.foot{{border:none;border-top:1px solid rgba(255,255,255,0.15);margin-bottom:16px;}}
</style>
</head>
<body>
<nav>
  <a href="../index.html" class="nav-logo">Quant<span>Research</span></a>
  <a href="../index.html" class="nav-back">← Back to Research</a>
</nav>
<div class="header">
  <div class="header-top">
    <div class="logo">Quant<span>Research</span></div>
    <div class="header-meta"><strong>GLOBAL MULTI-ASSET STRATEGY</strong><br>{today_fmt}<br>Quantitative Investment Research</div>
  </div>
  <div class="header-band">
    <div class="report-type">Quantitative Strategy &nbsp;|&nbsp; Asset Allocation &nbsp;|&nbsp; Backtesting</div>
    <div class="report-title">Permanent Portfolio: A Cross-Asset Allocation Study<br>Across Four Major Global Markets (2005–2026)</div>
    <div class="report-subtitle">NASDAQ · S&amp;P 500 · Gold · CSI Dividend Index (A-Shares) &nbsp;—&nbsp; Rebalancing Frequency Analysis &amp; Risk-Adjusted Return Attribution</div>
  </div>
</div>
<div class="body-wrap">
  <div class="exec-box">
    <div class="label">Executive Summary</div>
    <p>This report examines an equal-weighted permanent portfolio (25% each) across NASDAQ, S&amp;P 500, Gold, and CSI Dividend Index over January 2005 to April 2026 (21.2 years). <strong>Annual rebalancing delivers the highest risk-adjusted returns</strong> (CAGR 11.93%, Sharpe 0.75), outperforming both passive buy-and-hold and higher-frequency strategies. Maximum drawdown limited to −40.4% versus −70.2% for the highest-volatility constituent. All figures are price-return only; dividends and transaction costs excluded.</p>
  </div>
  <div class="findings-grid">
    <div class="finding-card"><div class="metric green">11.93%</div><div class="desc">Best Strategy CAGR<br>(Annual Rebalancing)</div></div>
    <div class="finding-card"><div class="metric" style="color:#003087;">10.96×</div><div class="desc">Total Return Multiple<br>over 21.2 Years</div></div>
    <div class="finding-card"><div class="metric gold">0.75</div><div class="desc">Sharpe Ratio<br>(Annual &amp; Quarterly)</div></div>
    <div class="finding-card"><div class="metric" style="color:#C0392B;">−40.4%</div><div class="desc">Max Drawdown<br>(Annual Rebal)</div></div>
  </div>
  <div class="section">
    <div class="section-header"><div class="section-num">1</div><div class="section-title">Historical Asset Performance (1990–2026)</div></div>
    <div class="chart-wrap"><img src="data:image/png;base64,{img1}" alt="Historical Prices"></div>
    <div class="chart-caption">Exhibit 1. Monthly closing prices. NASDAQ and S&amp;P 500 from Jan 1990; Gold (GC=F) from Aug 2000; CSI Dividend (000922.SS) from Jan 2005. Source: Yahoo Finance, Eastmoney, Sina Finance.</div>
    <div class="insight-grid">
      <div class="insight"><div class="i-label">US Equities</div><p>NASDAQ delivered the highest nominal price appreciation. Two major drawdowns exceeding <strong>−45%</strong>: dot-com bust (2000–2002) and GFC (2008–2009), before an extended bull market amplified by AI-driven re-rating from 2023.</p></div>
      <div class="insight"><div class="i-label">Gold &amp; A-Shares</div><p>Gold appreciated <strong>+1,032%</strong> over the common period. CSI Dividend reflected China's A-share volatility with extreme boom-bust cycles in 2007–2008 and 2014–2015, but showed strong resilience in recent years.</p></div>
    </div>
  </div>
  <div class="section">
    <div class="section-header"><div class="section-num">2</div><div class="section-title">Cumulative Return Comparison — Common Window (2005–2026)</div></div>
    <div class="chart-wrap"><img src="data:image/png;base64,{img2}" alt="Cumulative Returns"></div>
    <div class="chart-caption">Exhibit 2. Cumulative % return from January 2005 baseline. NASDAQ and Gold significantly outperformed; S&amp;P 500 and CSI Dividend showed comparable total returns.</div>
    <table>
      <thead><tr><th>Asset</th><th class="num">CAGR</th><th class="num">Total Return</th><th class="num">Ann. Vol</th><th class="num">Max DD</th><th class="num">Sharpe</th><th>Rating</th></tr></thead>
      <tbody>
        <tr><td><strong>NASDAQ Composite</strong></td><td class="num up">+12.30%</td><td class="num up">+1,076%</td><td class="num">18.80%</td><td class="num down">−48.4%</td><td class="num">0.66</td><td><span class="badge badge-overweight">Overweight</span></td></tr>
        <tr><td><strong>Gold (GC=F)</strong></td><td class="num up">+12.10%</td><td class="num up">+1,032%</td><td class="num">17.45%</td><td class="num down">−42.0%</td><td class="num">0.69</td><td><span class="badge badge-overweight">Overweight</span></td></tr>
        <tr><td><strong>S&amp;P 500</strong></td><td class="num up">+8.78%</td><td class="num up">+498%</td><td class="num">15.07%</td><td class="num down">−46.7%</td><td class="num">0.54</td><td><span class="badge badge-neutral">Neutral</span></td></tr>
        <tr><td><strong>CSI Dividend (A-shares)</strong></td><td class="num up">+8.80%</td><td class="num up">+500%</td><td class="num">32.97%</td><td class="num down">−70.2%</td><td class="num">0.37</td><td><span class="badge badge-neutral">Neutral</span></td></tr>
      </tbody>
    </table>
    <div class="chart-caption">Table 1. Individual asset metrics, 2005-01 to 2026-04. Sharpe at 3% risk-free rate.</div>
  </div>
  <div class="section">
    <div class="section-header"><div class="section-num">3</div><div class="section-title">Permanent Portfolio — Rebalancing Frequency Analysis</div></div>
    <div class="chart-wrap"><img src="data:image/png;base64,{img3}" alt="Rebalancing Strategy"></div>
    <div class="chart-caption">Exhibit 3. Top: growth of $1. Middle: drawdown. Bottom: rolling 36-month annualized return.</div>
    <table>
      <thead><tr><th>Strategy</th><th class="num">CAGR</th><th class="num">Total</th><th class="num">Ann. Vol</th><th class="num">Max DD</th><th class="num">Sharpe</th><th class="num">Calmar</th></tr></thead>
      <tbody>
        <tr><td>Buy &amp; Hold</td><td class="num">+10.76%</td><td class="num">8.77×</td><td class="num">17.56%</td><td class="num down">−49.7%</td><td class="num">0.60</td><td class="num">0.22</td></tr>
        <tr class="highlight-row"><td><strong>Annual Rebalancing ★ Best</strong></td><td class="num up">+11.93%</td><td class="num up">10.96×</td><td class="num">15.42%</td><td class="num">−40.4%</td><td class="num gold">0.75</td><td class="num gold">0.30</td></tr>
        <tr><td>Quarterly Rebalancing</td><td class="num">+11.71%</td><td class="num">10.51×</td><td class="num">14.88%</td><td class="num">−41.3%</td><td class="num">0.75</td><td class="num">0.28</td></tr>
        <tr><td>Monthly Rebalancing</td><td class="num">+11.69%</td><td class="num">10.48×</td><td class="num">14.83%</td><td class="num">−41.1%</td><td class="num">0.75</td><td class="num">0.28</td></tr>
      </tbody>
    </table>
    <div class="chart-caption">Table 2. 2005-01 to 2026-04, 21.2 years. Risk-free rate 3.0% p.a. Transaction costs not modeled.</div>
  </div>
  <div class="section">
    <div class="section-header"><div class="section-num">4</div><div class="section-title">Key Observations &amp; Investment Implications</div></div>
    <div class="insight-grid">
      <div class="insight"><div class="i-label">Rebalancing Bonus</div><p>Annual rebalancing generates <strong>+117bps CAGR premium</strong> over buy-and-hold while reducing volatility by 214bps and max drawdown by 933bps — systematic mean-reversion capture.</p></div>
      <div class="insight"><div class="i-label">Frequency Paradox</div><p><strong>Higher frequency reduces returns.</strong> Quarterly and monthly trail annual by 22–24bps CAGR. Over-rebalancing prematurely cuts winners before momentum trends exhaust.</p></div>
      <div class="insight"><div class="i-label">Diversification Benefit</div><p>Portfolio max DD of <strong>−40.4%</strong> beats all individual constituents except Gold (−42%), dramatically below CSI Dividend alone (−70.2%).</p></div>
      <div class="insight"><div class="i-label">Volatility Reduction</div><p>Portfolio vol of <strong>15.4%</strong> sits below NASDAQ (18.8%), Gold (17.5%), and CSI Dividend (33.0%), driven by Gold's low equity correlation during stress.</p></div>
    </div>
    <div class="section-header" style="margin-top:8px;"><div class="section-num" style="background:#5A6478;">↗</div><div class="section-title" style="color:var(--gs-muted);font-size:13px;">Major Market Events</div></div>
    <div class="timeline">
      <div class="tl-item"><div class="tl-year">2007–2009</div><div class="tl-text">Global Financial Crisis — S&amp;P 500 −56.8% peak-to-trough; Gold +25% in 2009 partially offset equity losses.</div></div>
      <div class="tl-item"><div class="tl-year">2014–2015</div><div class="tl-text">China A-share bubble and crash — CSI Dividend +150% then −60%, extreme local-market risk partially absorbed by diversification.</div></div>
      <div class="tl-item"><div class="tl-year">2020</div><div class="tl-text">COVID-19 — rapid −34% equity drawdown; Gold new ATH above $2,000/oz. Portfolio drawdown capped near −25%.</div></div>
      <div class="tl-item"><div class="tl-year">2022</div><div class="tl-text">Synchronised equity-bond selloff on global rate hike cycle — diversification benefits compressed as correlations spiked.</div></div>
      <div class="tl-item"><div class="tl-year">2023–2026</div><div class="tl-text">AI re-rating lifted NASDAQ +80% from 2023 trough; Gold above $3,000 on central bank demand and geopolitical risk premium.</div></div>
    </div>
  </div>
  <div class="section">
    <div class="section-header"><div class="section-num">5</div><div class="section-title">Conclusion</div></div>
    <div class="exec-box" style="border-left-color:var(--gs-gold);">
      <div class="label" style="color:#8B7340;">Investment Conclusion</div>
      <p>Equal-weighted permanent portfolio delivered <strong>11.93% CAGR</strong> over 21.2 years — $1.00 → <strong>$10.96</strong> — Sharpe 0.75 outperforming all single-asset benchmarks. Optimal cadence is <strong>annual rebalancing</strong>. Real-world implementation should account for transaction costs, tax treatment, and currency hedging for USD-denominated assets.</p>
    </div>
  </div>
</div>
<footer>
  <div class="footer-brand">QUANT RESEARCH</div>
  <hr class="foot">
  <p><strong style="color:#A8B8D0;">IMPORTANT DISCLOSURES</strong><br>
  Educational purposes only. Not investment advice. Past performance not indicative of future results. Price-return only; dividends and costs excluded. Data: Yahoo Finance, Eastmoney, Sina Finance. Generated: {today_fmt}.</p>
</footer>
</body>
</html>"""

out_path = f"{REPORTS_DIR}/{REPORT_META['filename']}"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Report saved: {out_path}")

with open(MANIFEST, encoding="utf-8") as f:
    manifest = json.load(f)
manifest = [r for r in manifest if not (r["slug"] == REPORT_META["slug"] and r["date"] == REPORT_META["date"])]
manifest.append(REPORT_META)
manifest.sort(key=lambda r: r["date"], reverse=True)
with open(MANIFEST, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print(f"Manifest updated: {len(manifest)} report(s)")

result = subprocess.run([sys.executable, "d:/Work/Quant/scripts/build_index.py"],
                        capture_output=True, text=True)
print(result.stdout.strip())
if result.returncode != 0:
    print("build_index error:", result.stderr)
