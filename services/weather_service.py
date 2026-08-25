"""
Weather Intelligence Service.
Queries real-time meteorological metrics, hourly projections, and multi-day forecasts.
"""
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime
import pytz
from services.api_service import make_resilient_request

WMO_WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    80: "Slight Rain Showers",
    81: "Moderate Showers",
    82: "Violent Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Hail"
}

def get_live_weather(lat: float, lon: float, city_name: str = "Detected Location") -> Dict[str, Any]:
    """
    Fetches real-time weather and forecast from Open-Meteo meteorological endpoints.
    """
    cache_key = f"weather_{round(lat, 3)}_{round(lon, 3)}"
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,surface_pressure,wind_speed_10m,wind_direction_10m",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,wind_speed_10m,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "Asia/Kolkata",
        "forecast_days": 7
    }
    
    resp = make_resilient_request(url, params=params, cache_key=cache_key)
    now_ist = datetime.now(pytz.timezone("Asia/Kolkata"))
    
    if resp["status"] in ["LIVE", "CACHED", "RECENT"] and resp["data"]:
        data = resp["data"]
        curr = data.get("current", {})
        w_code = curr.get("weather_code", 0)
        weather_desc = WMO_WEATHER_CODES.get(w_code, "Partly Cloudy")
        
        # Parse hourly
        hourly_data = []
        if "hourly" in data:
            h_obj = data["hourly"]
            times = h_obj.get("time", [])[:24]
            temps = h_obj.get("temperature_2m", [])[:24]
            hums = h_obj.get("relative_humidity_2m", [])[:24]
            winds = h_obj.get("wind_speed_10m", [])[:24]
            probs = h_obj.get("precipitation_probability", [])[:24]
            codes = h_obj.get("weather_code", [])[:24]
            
            for i in range(len(times)):
                t_str = times[i]
                dt_h = datetime.fromisoformat(t_str)
                hourly_data.append({
                    "time": dt_h.strftime("%I:%M %p"),
                    "full_time": t_str,
                    "temperature": temps[i] if i < len(temps) else None,
                    "humidity": hums[i] if i < len(hums) else None,
                    "wind_speed": winds[i] if i < len(winds) else None,
                    "rain_probability": probs[i] if i < len(probs) else 0,
                    "condition": WMO_WEATHER_CODES.get(codes[i] if i < len(codes) else 0, "Clear")
                })
                
        # Parse daily
        daily_data = []
        if "daily" in data:
            d_obj = data["daily"]
            d_times = d_obj.get("time", [])[:7]
            t_maxs = d_obj.get("temperature_2m_max", [])[:7]
            t_mins = d_obj.get("temperature_2m_min", [])[:7]
            p_maxs = d_obj.get("precipitation_probability_max", [])[:7]
            d_codes = d_obj.get("weather_code", [])[:7]
            
            for i in range(len(d_times)):
                dt_d = datetime.fromisoformat(d_times[i])
                daily_data.append({
                    "day_name": dt_d.strftime("%a, %d %b"),
                    "max_temp": t_maxs[i] if i < len(t_maxs) else None,
                    "min_temp": t_mins[i] if i < len(t_mins) else None,
                    "rain_probability": p_maxs[i] if i < len(p_maxs) else 0,
                    "condition": WMO_WEATHER_CODES.get(d_codes[i] if i < len(d_codes) else 0, "Clear")
                })
                
        return {
            "city": city_name,
            "latitude": lat,
            "longitude": lon,
            "status": resp["status"],
            "last_updated": now_ist.strftime("%H:%M:%S IST"),
            "temperature": round(float(curr.get("temperature_2m", 29.0)), 1),
            "feels_like": round(float(curr.get("apparent_temperature", 31.0)), 1),
            "humidity": round(float(curr.get("relative_humidity_2m", 68.0)), 1),
            "wind_speed": round(float(curr.get("wind_speed_10m", 8.5)), 1),
            "wind_direction": int(curr.get("wind_direction_10m", 180)),
            "pressure": round(float(curr.get("surface_pressure", 1010.0)), 1),
            "rainfall": round(float(curr.get("precipitation", 0.0)), 1),
            "weather_condition": weather_desc,
            "hourly_forecast": hourly_data,
            "daily_forecast": daily_data,
            "source": f"Open-Meteo Realtime API ({resp['status']})"
        }
        
    # Local fallback if network query fails
    return {
        "city": city_name,
        "latitude": lat,
        "longitude": lon,
        "status": "LOCAL DATA",
        "last_updated": now_ist.strftime("%H:%M:%S IST"),
        "temperature": 30.5,
        "feels_like": 33.2,
        "humidity": 65.0,
        "wind_speed": 7.8,
        "wind_direction": 140,
        "pressure": 1011.0,
        "rainfall": 0.0,
        "weather_condition": "Partly Cloudy",
        "hourly_forecast": [],
        "daily_forecast": [],
        "source": "Local Climatological Baseline"
    }
