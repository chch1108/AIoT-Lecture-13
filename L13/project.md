# Project Plan – CWA Forecast Streamlit App

## 1. Goal
- Build a simple web UI (deploy with Streamlit) that visualizes the Central Weather Administration weekly forecast, similar to https://www.cwa.gov.tw/V8/C/W/County/index.html.
- Show each region’s daily max/min temperatures with a line chart plus supporting text/table.

## 2. Prerequisites
1. Python 3.10+ environment.
2. `requests`, `streamlit`, `pandas`, and `plotly` (or `altair`) available:  
   `pip install requests streamlit pandas plotly`.
3. Local SQLite database `sqlitedata.db` populated by `crawler.py`.

## 3. Data Refresh
1. Run `python crawler.py` to fetch the latest dataset and populate `sqlitedata.db`.
2. Confirm rows exist with `sqlite3 sqlitedata.db "SELECT COUNT(*) FROM forecasts;"`.

## 4. Streamlit App Requirements
1. Read forecast data from `sqlitedata.db` into a DataFrame.
2. Provide UI controls:
   - Region selector (dropdown or sidebar) listing distinct `location`.
   - Optional date range filter (from min/max available dates).
3. Display:
   - Summary metrics for selected region (latest max/min, date range).
   - Line chart (max/min temperature vs. date) similar to CWA reference.
   - Data table of the filtered rows.
4. Handle missing data gracefully (show message if database empty).
5. Include last fetched timestamp (from `fetched_at` column).

## 5. Implementation Steps
1. Create `app.py` with helper functions:
   - `load_data(db_path: str) -> pd.DataFrame`
   - `get_regions(df)` and `get_date_range(df)`
2. Build Streamlit layout following Section 4.
3. Use Plotly Express `px.line` (or Streamlit `st.line_chart`) to plot two lines (max/min).
4. Add instructions/buttons for refreshing data (just explain to rerun crawler manually).

## 6. Run Instructions
1. Ensure SQLite has data (Section 3).
2. Launch app: `streamlit run app.py`.
3. Deploy by running the same command on the target host or pushing to Streamlit Cloud.

## 7. Future Enhancements (optional)
- Display weather description text per region/day.
- Cache API fetch directly inside Streamlit with a refresh button.
- Add bilingual UI (Chinese/English) to match CWA site.

