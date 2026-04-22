# Quant Research Blog

Systematic investment research — asset allocation, backtesting, and quantitative strategy studies.

**Live site:** https://roboleofly.github.io/Quant_Blog/

## Adding a new report

1. Run the analysis scripts in `scripts/`
2. Update `scripts/generate_report.py` with the new report content and metadata
3. Run `python scripts/generate_report.py` — this saves to `reports/` and rebuilds `index.html`
4. Commit and push

## Structure

```
├── index.html              # Auto-generated research index
├── reports/
│   ├── _manifest.json      # Report registry
│   └── YYYY-MM-DD-*.html   # Individual reports (self-contained)
├── scripts/
│   ├── fetch_historical_data.py
│   ├── plot_historical_data.py
│   ├── permanent_portfolio.py
│   ├── generate_report.py  # Generate + register a report
│   └── build_index.py      # Rebuild index.html from manifest
└── data/
    └── historical_data_1990_2026.csv
```
