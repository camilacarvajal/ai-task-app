"""
5-day weather forecast via OpenWeatherMap API.
Optional: only used when OPENWEATHER_API_KEY is set in .env.
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import requests
import streamlit as st

logger = logging.getLogger(__name__)

# OpenWeatherMap 5-day forecast (3-hour steps); we aggregate by day
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"


@dataclass
class DayForecast:
    """One day's summary: date, low, high, and a representative condition."""

    date: str  # e.g. "Sat, Feb 15"
    low_c: float
    high_c: float
    condition: str
    icon: str  # OpenWeatherMap icon code, e.g. "01d"


def get_api_key() -> Optional[str]:
    raw = os.environ.get("OPENWEATHER_API_KEY", "").strip()
    return raw or None


def get_location() -> tuple[Optional[float], Optional[float]]:
    """Return (lat, lon) from WEATHER_LAT/WEATHER_LON or from WEATHER_CITY geocode."""
    lat_s = os.environ.get("WEATHER_LAT", "").strip()
    lon_s = os.environ.get("WEATHER_LON", "").strip()
    if lat_s and lon_s:
        try:
            return float(lat_s), float(lon_s)
        except ValueError:
            pass
    city = os.environ.get("WEATHER_CITY", "").strip()
    if not city:
        return None, None
    try:
        r = requests.get(
            GEO_URL,
            params={"q": city, "limit": 1, "appid": get_api_key()},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if data and isinstance(data, list) and len(data) > 0:
            return data[0].get("lat"), data[0].get("lon")
    except requests.RequestException as e:
        logger.debug("Geocoding request failed for city %r: %s", city, e)
    except (ValueError, KeyError, TypeError) as e:
        logger.debug("Geocoding response parse error for city %r: %s", city, e)
    return None, None


@st.cache_data(ttl=600)  # 10 min cache to avoid API call on every rerun (e.g. checkbox toggle)
def _cached_forecast(lat: float, lon: float, api_key: str) -> tuple[Optional[list[DayForecast]], Optional[str]]:
    """Fetch and parse forecast; cache keyed by (lat, lon, api_key)."""
    try:
        r = requests.get(
            FORECAST_URL,
            params={
                "lat": lat,
                "lon": lon,
                "appid": api_key,
                "units": "metric",
                "cnt": 40,  # 5 days * 8 steps per day
            },
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        return None, f"Weather API error: {e}"
    except Exception as e:
        return None, str(e)

    list_ = data.get("list") or []
    if not list_:
        return [], None

    # Group by date (local date from dt is ideal; API returns UTC, so we use dt for date key)
    by_date: dict[str, list[dict]] = {}
    for item in list_:
        ts = item.get("dt")
        if ts is None:
            continue
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        key = dt.strftime("%Y-%m-%d")
        if key not in by_date:
            by_date[key] = []
        by_date[key].append(item)

    result: list[DayForecast] = []
    for key in sorted(by_date.keys())[:5]:
        items = by_date[key]
        temps = []
        condition = "—"
        icon = "01d"
        for it in items:
            main = it.get("main") or {}
            t = main.get("temp")
            if t is not None:
                temps.append(float(t))
            weather_list = it.get("weather") or []
            if weather_list:
                condition = (weather_list[0].get("description") or "—").capitalize()
                icon = weather_list[0].get("icon") or "01d"
        low = min(temps) if temps else 0.0
        high = max(temps) if temps else 0.0
        date_dt = datetime.strptime(key, "%Y-%m-%d")
        result.append(
            DayForecast(
                date=date_dt.strftime("%a, %b %d"),
                low_c=round(low, 1),
                high_c=round(high, 1),
                condition=condition,
                icon=icon,
            )
        )

    return result, None


def fetch_5day_forecast() -> tuple[Optional[list[DayForecast]], Optional[str]]:
    """
    Fetch 5-day forecast for the configured location (cached 10 min).
    Returns (list of DayForecast, None) on success, or (None, error_message).
    """
    api_key = get_api_key()
    if not api_key:
        return None, None  # feature disabled

    lat, lon = get_location()
    if lat is None or lon is None:
        return None, "Set WEATHER_CITY or WEATHER_LAT and WEATHER_LON in .env"

    return _cached_forecast(lat, lon, api_key)
