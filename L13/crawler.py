import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import requests

DB_PATH = "sqlitedata.db"
FALLBACK_JSON = Path(__file__).with_name("F-A0010-001.json")
FORECAST_TABLE = "forecasts"


def parse_forecasts(payload: dict) -> List[Tuple[str, str, Optional[float], Optional[float]]]:
    """Extract (location, date, max_temp, min_temp) tuples from API payload."""

    def to_float(value: Optional[str]) -> Optional[float]:
        if value in (None, ""):
            return None
        try:
            return float(value)
        except ValueError:
            return None

    try:
        locations = (
            payload["cwaopendata"]["resources"]["resource"]["data"]["agrWeatherForecasts"][
                "weatherForecasts"
            ]["location"]
        )
    except (KeyError, TypeError):
        return []

    records: List[Tuple[str, str, Optional[float], Optional[float]]] = []
    for location in locations:
        location_name = location.get("locationName")
        if not location_name:
            continue
        weather_elements = location.get("weatherElements", {})
        max_daily = weather_elements.get("MaxT", {}).get("daily", [])
        min_daily = weather_elements.get("MinT", {}).get("daily", [])
        max_map = {entry.get("dataDate"): to_float(entry.get("temperature")) for entry in max_daily}
        min_map = {entry.get("dataDate"): to_float(entry.get("temperature")) for entry in min_daily}
        for data_date in sorted({*max_map.keys(), *min_map.keys()}):
            if not data_date:
                continue
            records.append((location_name, data_date, max_map.get(data_date), min_map.get(data_date)))
    return records


def save_to_db(records: List[Tuple[str, str, Optional[float], Optional[float]]]) -> None:
    if not records:
        print("沒有可儲存的天氣資料。")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {FORECAST_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                data_date TEXT NOT NULL,
                max_temp REAL,
                min_temp REAL,
                fetched_at TEXT NOT NULL,
                UNIQUE(location, data_date)
            )
            """
        )
        timestamp = datetime.utcnow().isoformat(timespec="seconds")
        conn.executemany(
            f"""
            INSERT OR REPLACE INTO {FORECAST_TABLE} (location, data_date, max_temp, min_temp, fetched_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [(loc, date, max_t, min_t, timestamp) for loc, date, max_t, min_t in records],
        )
        conn.commit()
    finally:
        conn.close()

def fetch_data() -> dict:
    url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001"
    params = {
        "Authorization": "CWA-DAC039F0-FBE6-42ED-AC20-E9ED75C0D5F9",
        "downloadType": "WEB",
        "format": "JSON"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        print("成功透過 API 取得資料。")
        return response.json()
    except requests.exceptions.RequestException as e:
        print("API 連線失敗，將改用本地備援檔案:", e)
        if not FALLBACK_JSON.exists():
            raise FileNotFoundError("找不到備援 JSON 檔案")
        with FALLBACK_JSON.open("r", encoding="utf-8") as f:
            return json.load(f)


if __name__ == "__main__":
    data = fetch_data()
    forecast_rows = parse_forecasts(data)
    save_to_db(forecast_rows)
    print(f"成功寫入 {len(forecast_rows)} 筆天氣資料！")
