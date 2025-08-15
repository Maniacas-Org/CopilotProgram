# CopilotProgram

A small Flask demo that fetches gold futures (ticker `GC=F`) via Yahoo Finance, computes the MACD indicator, and renders an interactive Plotly chart in the browser.

Files added:

- `app.py` — Flask web application
- `templates/index.html` — Jinja2 template that embeds Plotly HTML
- `requirements.txt` — Python dependencies

Quick start (run these in the workspace root):

```bash
# create a venv (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser. Use the Period and Interval fields to change the data range (examples: `1y`, `6mo`, `3mo`, `1mo`) and interval (`1d`, `1wk`, `1h` where supported by yfinance).

Notes:

- Data source: Yahoo Finance via `yfinance` (ticker `GC=F`).
- Plot rendering: `plotly` embedded as an HTML div.
- This is a demo and not financial advice.
# CopilotProgram
Python
