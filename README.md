# AIoT Lecture 13 – CWA Forecast Dashboard

Streamlit dashboard plus crawler for the Central Weather Administration (CWA) agricultural forecast dataset. It fetches one-week forecasts, stores them in SQLite, and visualizes each region7s daily max/min temperatures with line charts similar to the official site (https://www.cwa.gov.tw/V8/C/W/County/index.html).

## Project Structure

```
L13/
├── crawler.py        # Fetch dataset from CWA API and store per-region temps in SQLite
├── app.py            # Streamlit dashboard showing regional charts/tables
├── project.md        # Detailed plan/instructions followed for this build
├── requirements.txt  # Python dependencies
└── sqlitedata.db     # SQLite database (generated after running crawler)
```

## Setup

```bash
git clone https://github.com/chch1108/AIoT-Lecture-13.git
cd AIoT-Lecture-13/L13
python -m venv .venv && source .venv/bin/activate  # optional but recommended
pip install -r requirements.txt
```

## Refresh Data

Run the crawler whenever you need the latest forecast snapshot:

```bash
python crawler.py
```

This populates/updates `sqlitedata.db` with each region7s daily max/min temperatures.

## Launch Streamlit App

```bash
streamlit run app.py
```

Features:
- Sidebar selectors for region/date range.
- Summary metrics for the latest day in range.
- Plotly line chart showing max/min temperature trends.
- Data table plus last-updated timestamp.

## Deployment Notes

- Local deployment: run `streamlit run app.py --server.port 8501`.
- Streamlit Cloud: push this repo and configure the app entry point as `L13/app.py`.
- Manual data refresh: rerun `python crawler.py` on the host and restart the app if needed.

## Credits

- Data source: [Central Weather Administration – Agricultural Weather Forecast](https://www.cwa.gov.tw/V8/C/W/County/index.html)

