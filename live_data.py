"""
LIVE WEATHER + AIR QUALITY DATA
Uses Open-Meteo's public forecast and air-quality APIs.

Important:
- Weather/pollutant values are fetched live from the API when the internet is available.
- Open-Meteo data are forecast/model data, not a direct CPCB sensor feed.
- The app falls back to the project's demo data if the API is unavailable.
"""

from datetime import datetime
import requests
import pandas as pd

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    80: ("Rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}

def weather_description(code):
    return WEATHER_CODES.get(int(code), ("Unknown", "🌍"))

_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": "AirQualityLevelPredictor/1.0"})

def _get_json(url, params):
    r = _SESSION.get(url, params=params, timeout=6)
    r.raise_for_status()
    return r.json()

def get_live_weather(city, forecast_days=7):
    params = {
        "latitude": city["lat"],
        "longitude": city["lng"],
        "current": ",".join([
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "precipitation", "rain", "weather_code", "wind_speed_10m",
            "wind_direction_10m", "surface_pressure", "visibility",
        ]),
        "hourly": ",".join([
            "temperature_2m", "relative_humidity_2m",
            "precipitation_probability", "precipitation",
            "weather_code", "wind_speed_10m", "wind_direction_10m",
        ]),
        "daily": ",".join([
            "weather_code", "temperature_2m_max", "temperature_2m_min",
            "precipitation_probability_max", "precipitation_sum",
            "sunrise", "sunset",
        ]),
        "forecast_days": forecast_days,
        "timezone": "Asia/Kolkata",
    }
    return _get_json(WEATHER_URL, params)

def get_live_air(city):
    params = {
        "latitude": city["lat"],
        "longitude": city["lng"],
        "current": ",".join([
            "pm10", "pm2_5", "carbon_monoxide",
            "nitrogen_dioxide", "sulphur_dioxide", "ozone",
        ]),
        "hourly": ",".join([
            "pm10", "pm2_5", "carbon_monoxide",
            "nitrogen_dioxide", "sulphur_dioxide", "ozone",
        ]),
        "forecast_days": 2,
        "timezone": "Asia/Kolkata",
    }
    return _get_json(AIR_URL, params)

def fetch_live_bundle(city):
    """
    Returns:
      {
        "ok": bool,
        "weather": {...},
        "air": {...},
        "source": "...",
        "fetched_at": "...",
        "error": optional string
      }
    """
    try:
        weather = get_live_weather(city)
        air = get_live_air(city)
        wc = weather["current"].get("weather_code", 0)
        desc, icon = weather_description(wc)
        return {
            "ok": True,
            "weather": weather,
            "air": air,
            "source": "Open-Meteo live weather + air-quality services",
            "fetched_at": datetime.now().astimezone().strftime("%d %b %Y, %H:%M:%S %Z"),
            "description": desc,
            "weather_icon": icon,
        }
    except Exception as exc:
        return {
            "ok": False,
            "weather": None,
            "air": None,
            "source": "Demo fallback",
            "fetched_at": datetime.now().astimezone().strftime("%d %b %Y, %H:%M:%S %Z"),
            "error": str(exc),
            "description": "Live service unavailable",
            "weather_icon": "⚠️",
        }

def extract_current(bundle):
    if not bundle["ok"]:
        return None
    w = bundle["weather"]["current"]
    a = bundle["air"]["current"]
    return {
        "temperature": w.get("temperature_2m"),
        "humidity": w.get("relative_humidity_2m"),
        "apparent_temperature": w.get("apparent_temperature"),
        "wind_speed": w.get("wind_speed_10m"),
        "wind_direction": w.get("wind_direction_10m"),
        "precipitation": w.get("precipitation"),
        "rain": w.get("rain"),
        "pressure": w.get("surface_pressure"),
        "visibility": w.get("visibility"),
        "weather_code": w.get("weather_code"),
        "pm25": a.get("pm2_5"),
        "pm10": a.get("pm10"),
        "co": a.get("carbon_monoxide"),
        "no2": a.get("nitrogen_dioxide"),
        "so2": a.get("sulphur_dioxide"),
        "o3": a.get("ozone"),
    }

def forecast_dataframe(bundle):
    if not bundle["ok"]:
        return pd.DataFrame()
    d = bundle["weather"]["daily"]
    out = pd.DataFrame({
        "date": pd.to_datetime(d["time"]),
        "weather_code": d["weather_code"],
        "max_temp": d["temperature_2m_max"],
        "min_temp": d["temperature_2m_min"],
        "rain_probability": d["precipitation_probability_max"],
        "rain_mm": d["precipitation_sum"],
        "sunrise": d["sunrise"],
        "sunset": d["sunset"],
    })
    out[["description","icon"]] = out["weather_code"].apply(
        lambda x: pd.Series(weather_description(x))
    )
    return out

def hourly_weather_dataframe(bundle):
    if not bundle["ok"]:
        return pd.DataFrame()
    h = bundle["weather"]["hourly"]
    return pd.DataFrame({
        "datetime": pd.to_datetime(h["time"]),
        "temperature": h["temperature_2m"],
        "humidity": h["relative_humidity_2m"],
        "rain_probability": h["precipitation_probability"],
        "precipitation": h["precipitation"],
        "weather_code": h["weather_code"],
        "wind_speed": h["wind_speed_10m"],
    })

def live_pollutants_as_project_keys(bundle):
    current = extract_current(bundle)
    if current is None:
        return None
    return {
        "pm25": current["pm25"],
        "pm10": current["pm10"],
        "no2": current["no2"],
        "so2": current["so2"],
        "co": (current["co"] or 0) / 1000.0,  # Open-Meteo CO is µg/m³; CPCB CO is mg/m³.
        "o3": current["o3"],
    }
