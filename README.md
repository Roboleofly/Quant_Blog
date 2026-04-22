# Quant Research Blog

Systematic investment research — asset allocation, backtesting, and quantitative strategy studies.

**Live site:** https://roboleofly.github.io/Quant_Blog/

---

## What's in this repo

Only the deployed web pages are tracked here. Scripts and data stay local.

```
Quant_Blog/
├── index.html                          # Research portal homepage
└── reports/
    ├── _manifest.json                  # Report registry (date, title, abstract, tags)
    └── YYYY-MM-DD-report-name.html     # Self-contained report pages
```

## Adding a new report

All analysis and generation happens locally, then only the HTML output is pushed:

1. Run analysis scripts locally (`scripts/` — not in this repo)
2. Run `python scripts/generate_report.py` — writes to `reports/` and rebuilds `index.html`
3. Push the new files:

```bash
git add index.html reports/YYYY-MM-DD-*.html reports/_manifest.json
git commit -m "Add report: title"
git push
```

## Reports

| Date | Title |
|------|-------|
| 2026-04-22 | [Permanent Portfolio: Cross-Asset Allocation Study](reports/2026-04-22-permanent-portfolio.html) |
