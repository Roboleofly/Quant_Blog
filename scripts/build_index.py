"""
Build index.html from reports/_manifest.json.
Run after adding a new report entry to the manifest.
"""
import json, datetime

MANIFEST = "d:/Work/Quant/reports/_manifest.json"
OUT      = "d:/Work/Quant/index.html"
TODAY    = datetime.date.today().strftime("%B %d, %Y")

with open(MANIFEST, encoding="utf-8") as f:
    reports = json.load(f)

reports_sorted = sorted(reports, key=lambda r: r["date"], reverse=True)

def tag_badge(tag):
    colors = {
        "Asset Allocation": "#CCE5FF:#004085",
        "Backtesting":      "#D4EDDA:#155724",
        "Rebalancing":      "#FFF3CD:#856404",
        "Factor Investing": "#F8D7DA:#721C24",
        "Macro":            "#E2D9F3:#432874",
    }
    bg, fg = colors.get(tag, "#E9ECEF:#495057").split(":")
    return f'<span style="background:{bg};color:{fg};padding:2px 8px;border-radius:2px;font-size:10px;font-weight:600;letter-spacing:0.5px;margin-right:4px;">{tag}</span>'

def report_card(r):
    tags_html = "".join(tag_badge(t) for t in r.get("tags", []))
    metrics   = r.get("metrics", {})
    m_html = ""
    if metrics:
        items = [f'<span style="margin-right:18px;"><span style="color:#8b949e;font-size:10px;text-transform:uppercase;letter-spacing:1px;">{k}</span><br><strong style="font-size:16px;color:#00205B;">{v}</strong></span>'
                 for k, v in metrics.items()]
        m_html = f'<div style="display:flex;margin:14px 0 4px;padding:12px 14px;background:#F4F6FA;border-radius:4px;">{"".join(items)}</div>'

    return f"""
    <a href="reports/{r['filename']}" style="text-decoration:none;color:inherit;">
      <div class="card" onmouseenter="this.style.boxShadow='0 4px 20px rgba(0,32,91,0.12)';this.style.transform='translateY(-2px)'"
                        onmouseleave="this.style.boxShadow='0 1px 4px rgba(0,0,0,0.06)';this.style.transform='translateY(0)'">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
          <div>{tags_html}</div>
          <span style="font-size:11px;color:#8b949e;white-space:nowrap;margin-left:10px;">{r['date']}</span>
        </div>
        <div style="font-size:17px;font-weight:700;color:#00205B;line-height:1.3;margin-bottom:5px;">{r['title']}</div>
        <div style="font-size:11.5px;color:#5A6478;margin-bottom:10px;">{r['subtitle']}</div>
        <div style="font-size:12.5px;color:#3A3A5C;line-height:1.65;">{r['abstract']}</div>
        {m_html}
        <div style="margin-top:14px;font-size:11.5px;font-weight:600;color:#1E5799;letter-spacing:0.3px;">
          Read Report →
        </div>
      </div>
    </a>"""

cards_html = "\n".join(report_card(r) for r in reports_sorted)
count = len(reports_sorted)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="Quantitative investment research — systematic strategies, backtests, and asset allocation studies.">
<title>Quant Research | Systematic Investment Studies</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{font-family:'Inter','Helvetica Neue',Arial,sans-serif;background:#FFFFFF;color:#1A1A2E;}}

  /* NAV */
  nav{{background:#00205B;padding:0 48px;display:flex;align-items:center;justify-content:space-between;height:56px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,0.3);}}
  .nav-logo{{font-size:15px;font-weight:700;color:#FFFFFF;letter-spacing:3px;text-transform:uppercase;}}
  .nav-logo span{{color:#B5A46E;}}
  .nav-links{{display:flex;gap:28px;}}
  .nav-links a{{color:#A8B8D0;font-size:12px;font-weight:500;text-decoration:none;letter-spacing:0.5px;transition:color .2s;}}
  .nav-links a:hover{{color:#FFFFFF;}}

  /* HERO */
  .hero{{background:linear-gradient(135deg,#00205B 0%,#003087 60%,#1E5799 100%);padding:64px 48px 52px;position:relative;overflow:hidden;}}
  .hero::after{{content:'';position:absolute;right:-80px;top:-80px;width:400px;height:400px;border-radius:50%;background:rgba(181,164,110,0.07);pointer-events:none;}}
  .hero-inner{{max-width:1100px;margin:0 auto;}}
  .hero-eyebrow{{font-size:10px;font-weight:700;color:#B5A46E;letter-spacing:3px;text-transform:uppercase;margin-bottom:14px;}}
  .hero-title{{font-size:38px;font-weight:700;color:#FFFFFF;line-height:1.2;margin-bottom:14px;}}
  .hero-sub{{font-size:15px;color:#A8B8D0;max-width:600px;line-height:1.65;}}
  .hero-stats{{display:flex;gap:40px;margin-top:36px;padding-top:28px;border-top:1px solid rgba(255,255,255,0.1);}}
  .hero-stat .num{{font-size:26px;font-weight:700;color:#FFFFFF;}}
  .hero-stat .lbl{{font-size:11px;color:#7A91B0;margin-top:2px;}}

  /* BODY */
  .body-wrap{{max-width:1100px;margin:0 auto;padding:48px 48px 80px;}}

  /* FILTER BAR */
  .filter-bar{{display:flex;align-items:center;justify-content:space-between;margin-bottom:28px;padding-bottom:16px;border-bottom:1px solid #D6DCE8;}}
  .filter-bar .count{{font-size:12px;color:#5A6478;}}
  .filter-bar .sort{{font-size:11.5px;color:#5A6478;}}

  /* CARDS */
  .cards-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(480px,1fr));gap:20px;}}
  .card{{border:1px solid #D6DCE8;border-top:3px solid #00205B;border-radius:0 0 6px 6px;padding:20px 22px;background:#FFFFFF;cursor:pointer;transition:transform .18s,box-shadow .18s;box-shadow:0 1px 4px rgba(0,0,0,0.06);}}

  /* SECTION DIVIDER */
  .section-title{{font-size:11px;font-weight:700;color:#5A6478;letter-spacing:2px;text-transform:uppercase;margin-bottom:18px;}}

  /* FOOTER */
  footer{{background:#00205B;padding:32px 48px;margin-top:60px;}}
  footer p{{font-size:10.5px;color:#7A91B0;line-height:1.7;max-width:900px;}}
  footer .brand{{font-size:12px;font-weight:700;color:#B5A46E;letter-spacing:2px;margin-bottom:12px;}}
  hr.foot{{border:none;border-top:1px solid rgba(255,255,255,0.1);margin-bottom:14px;}}
</style>
</head>
<body>

<nav>
  <div class="nav-logo">Quant<span>Research</span></div>
  <div class="nav-links">
    <a href="index.html">Research</a>
    <a href="https://github.com/roboleofly/Quant" target="_blank">GitHub</a>
  </div>
</nav>

<div class="hero">
  <div class="hero-inner">
    <div class="hero-eyebrow">Systematic Investment Research</div>
    <div class="hero-title">Quantitative Strategy &amp;<br>Asset Allocation Studies</div>
    <div class="hero-sub">
      Independent research covering multi-asset allocation, factor strategies,
      backtesting methodology, and systematic investment frameworks.
      All analyses are data-driven with reproducible code.
    </div>
    <div class="hero-stats">
      <div class="hero-stat"><div class="num">{count}</div><div class="lbl">Research Reports</div></div>
      <div class="hero-stat"><div class="num">4</div><div class="lbl">Asset Classes</div></div>
      <div class="hero-stat"><div class="num">21yr</div><div class="lbl">Backtest History</div></div>
    </div>
  </div>
</div>

<div class="body-wrap">
  <div class="filter-bar">
    <div class="section-title">Latest Research</div>
    <div class="sort">{count} report{"s" if count!=1 else ""} &nbsp;·&nbsp; Updated {TODAY}</div>
  </div>
  <div class="cards-grid">
    {cards_html}
  </div>
</div>

<footer>
  <div class="brand">QUANT RESEARCH</div>
  <hr class="foot">
  <p>
    This website presents independent quantitative research for educational purposes only.
    Nothing herein constitutes investment advice or a solicitation to buy or sell securities.
    Past performance is not indicative of future results. All analyses use publicly available data.
    &nbsp;·&nbsp; Generated {TODAY}
  </p>
</footer>

</body>
</html>"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"index.html written  ({count} reports)")
