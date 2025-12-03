from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

DB_PATH = Path(__file__).with_name("sqlitedata.db")
FORECAST_TABLE = "forecasts"
EXPECTED_COLUMNS = ["location", "data_date", "max_temp", "min_temp", "fetched_at"]


@st.cache_data(show_spinner=False)
def load_data(db_path: Path = DB_PATH) -> pd.DataFrame:
    """Read forecast data from SQLite and return a prepared DataFrame."""
    if not db_path.exists():
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            f"""
            SELECT location, data_date, max_temp, min_temp, fetched_at
            FROM {FORECAST_TABLE}
            ORDER BY location, data_date
            """,
            conn,
        )

    if df.empty:
        return df

    df["data_date"] = pd.to_datetime(df["data_date"])
    df["fetched_at"] = pd.to_datetime(df["fetched_at"])
    df["max_temp"] = pd.to_numeric(df["max_temp"], errors="coerce")
    df["min_temp"] = pd.to_numeric(df["min_temp"], errors="coerce")
    return df


def build_filters(df: pd.DataFrame) -> Tuple[str, pd.Timestamp, pd.Timestamp]:
    """Render selector widgets and return chosen region + date range."""
    regions = sorted(df["location"].dropna().unique())
    default_region = "北部地區" if "北部地區" in regions else regions[0]
    default_index = regions.index(default_region)
    selected_region = st.sidebar.selectbox("選擇地區", regions, index=default_index)

    min_date = df["data_date"].min().date()
    max_date = df["data_date"].max().date()
    date_range = st.sidebar.date_input(
        "日期範圍",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    return selected_region, start_dt, end_dt


def render_metrics(region_df: pd.DataFrame) -> None:
    latest_row = region_df.sort_values("data_date").iloc[-1]

    def fmt_temp(value) -> str:
        return f"{value:.1f} ℃" if pd.notna(value) else "—"

    col1, col2, col3 = st.columns(3)
    col1.metric("最新最高溫", fmt_temp(latest_row["max_temp"]))
    col2.metric("最新最低溫", fmt_temp(latest_row["min_temp"]))
    col3.metric("預報日期", latest_row["data_date"].date().isoformat())


def render_chart(region_df: pd.DataFrame) -> None:
    chart_df = (
        region_df[["data_date", "max_temp", "min_temp"]]
        .melt(id_vars="data_date", value_vars=["max_temp", "min_temp"], var_name="type", value_name="temperature")
        .dropna(subset=["temperature"])
    )
    if chart_df.empty:
        st.info("選定範圍內沒有完整的最高/最低溫資料。")
        return

    chart_df["label"] = chart_df["type"].map({"max_temp": "最高溫", "min_temp": "最低溫"})
    fig = px.line(
        chart_df,
        x="data_date",
        y="temperature",
        color="label",
        markers=True,
        title="最高 / 最低溫走勢",
        labels={"data_date": "日期", "temperature": "溫度 (℃)", "label": "類型"},
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig, use_container_width=True)


def render_table(region_df: pd.DataFrame) -> None:
    table_df = region_df[["data_date", "max_temp", "min_temp"]].copy()
    table_df["data_date"] = table_df["data_date"].dt.date
    table_df.rename(columns={"data_date": "日期", "max_temp": "最高溫 (℃)", "min_temp": "最低溫 (℃)"}, inplace=True)
    st.dataframe(table_df, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="農業氣象預報面板", layout="wide")
    st.title("農業氣象預報儀表板")
    st.caption("資料來源：中央氣象署農業氣象服務 (https://www.cwa.gov.tw/V8/C/W/County/index.html)")

    df = load_data()
    if df.empty:
        st.warning("資料庫目前沒有天氣資料，請先執行 `python crawler.py` 更新資料庫。")
        return

    selected_region, start_dt, end_dt = build_filters(df)
    region_df = df[
        (df["location"] == selected_region) & (df["data_date"] >= start_dt) & (df["data_date"] <= end_dt)
    ]

    st.subheader(f"{selected_region} 預報")
    if region_df.empty:
        st.info("這個篩選條件下沒有資料，請調整日期範圍。")
        return

    render_metrics(region_df)
    render_chart(region_df)
    render_table(region_df)

    last_fetch = region_df["fetched_at"].max()
    st.caption(f"資料更新時間 (UTC)：{last_fetch.strftime('%Y-%m-%d %H:%M:%S')}")
    st.info("若需要最新資料，請回到終端機執行 `python crawler.py` 後重新整理本頁。")


if __name__ == "__main__":
    main()
