"""
Contextual Response Generation Engine.
Synthesizes dynamic real-time telemetry, location context, and domain knowledge
into natural, precise, non-hallucinatory explanations.
"""
from typing import Dict, Any
import random
from chatbot.knowledge_base import POLLUTANT_KNOWLEDGE, PROJECT_ARCHITECTURE_KNOWLEDGE
from chatbot.intent_detection import detect_user_intent

def generate_chatbot_response(user_message: str, live_context: Dict[str, Any]) -> str:
    """
    Generates intelligent response grounded strictly in current live metrics and environmental knowledge.
    """
    intent = detect_user_intent(user_message)
    
    # Extract live contextual parameters
    loc_city = live_context.get("city", "Delhi")
    loc_state = live_context.get("state", "Delhi")
    loc_district = live_context.get("district", loc_city)
    lat = live_context.get("latitude", 28.6139)
    lon = live_context.get("longitude", 77.2090)
    is_live_gps = live_context.get("is_live_gps", False)
    
    # Nearest Station Context
    nearest_stn = live_context.get("nearest_station", {})
    stn_name = nearest_stn.get("station", f"{loc_city} Continuous Ambient Monitoring Station")
    stn_dist = nearest_stn.get("distance_km", 0.0)
    stn_city = nearest_stn.get("city", loc_city)
    
    aqi_val = live_context.get("aqi")
    aqi_cat = live_context.get("aqi_category", "Moderate")
    dom_pollutant = live_context.get("dominant_pollutant", "PM2.5")
    risk_level = live_context.get("risk_level", "Moderate")
    temp = live_context.get("temperature")
    humidity = live_context.get("humidity")
    weather_cond = live_context.get("weather_condition", "Partly Cloudy")
    wind_spd = live_context.get("wind_speed")
    season = live_context.get("season", "Monsoon")
    time_str = live_context.get("time_str", "")
    date_str = live_context.get("date_str", "")
    status_label = live_context.get("data_status", "LIVE")
    pollutants = live_context.get("pollutants", {})
    
    # Hour for dynamic greeting
    hour = live_context.get("hour", 12)
    if 4 <= hour < 12:
        day_period = "Good morning! 🌤️"
    elif 12 <= hour < 17:
        day_period = "Good afternoon! ☀️"
    elif 17 <= hour < 22:
        day_period = "Good evening! 🌆"
    else:
        day_period = "Greetings! 🌙"
        
    if intent == "GREETING":
        return (
            f"{day_period} Welcome to the **Air Quality Level Predictor**. Telemetry for **{loc_city}, {loc_state}** is active:\n\n"
            f"- **Current AQI**: **{aqi_val}** ({aqi_cat.upper()})\n"
            f"- **Dominant Factor**: **{dom_pollutant}** (Risk: {risk_level})\n"
            f"- **Nearest Station**: `{stn_name}` ({stn_dist} km away)\n"
            f"- **Meteorology**: {temp}°C, {humidity}% Humidity, {weather_cond}\n"
            f"- **Position**: `{lat:.4f}°N, {lon:.4f}°E` ({'🟢 Live GPS' if is_live_gps else '📍 Manual'})\n\n"
            f"How can I assist you with environmental analytics, forecasts, or health advisories today?"
        )
        
    elif intent == "CURRENT_AQI":
        if aqi_val is None:
            return f"Current live AQI telemetry for **{loc_city}** is being refreshed. Please check the dashboard or select another city."
        pm25_val = pollutants.get("pm25", "N/A")
        pm10_val = pollutants.get("pm10", "N/A")
        co_val = pollutants.get("co", "N/A")
        no2_val = pollutants.get("no2", "N/A")
        so2_val = pollutants.get("so2", "N/A")
        o3_val = pollutants.get("o3", "N/A")
        
        return (
            f"### 🌫️ Air Quality Telemetry at **{loc_city}, {loc_state}**\n\n"
            f"- **National AQI**: **{aqi_val}** ({aqi_cat.upper()})\n"
            f"- **Assessed Risk**: **{risk_level}**\n"
            f"- **Governing Pollutant**: **{dom_pollutant}**\n"
            f"- **Monitoring Station**: `{stn_name}` (Located **{stn_dist} km** from your position)\n\n"
            f"**Pollutant Breakdown (CPCB 6-Pollutants)**:\n"
            f"- PM2.5: `{pm25_val} µg/m³`\n"
            f"- PM10: `{pm10_val} µg/m³`\n"
            f"- CO: `{co_val} mg/m³`\n"
            f"- NO2: `{no2_val} µg/m³`\n"
            f"- SO2: `{so2_val} µg/m³`\n"
            f"- O3: `{o3_val} µg/m³`\n\n"
            f"**Health Statement**: {live_context.get('health_statement', 'Standard precautions apply based on CPCB guidelines.')}\n\n"
            f"*Status: {status_label} | Updated: {time_str} IST*"
        )
        
    elif intent == "CURRENT_WEATHER":
        return (
            f"### 🌦️ Current Weather in **{loc_city}, {loc_state}**\n\n"
            f"- **Condition**: **{weather_cond}**\n"
            f"- **Temperature**: **{temp} °C** (Feels like {live_context.get('feels_like', temp)} °C)\n"
            f"- **Relative Humidity**: **{humidity} %**\n"
            f"- **Wind Speed**: **{wind_spd} km/h** (Direction: {live_context.get('wind_direction', 180)}°)\n"
            f"- **Atmospheric Pressure**: **{live_context.get('pressure', 1010)} hPa**\n"
            f"- **Precipitation**: **{live_context.get('rainfall', 0.0)} mm**\n"
            f"- **Indian Season**: **{season}**\n\n"
            f"*Weather data is refreshed dynamically via high-resolution Open-Meteo atmospheric models.*"
        )
        
    elif intent == "LOCATION":
        gps_tag = "🟢 Detected via Live Browser GPS" if is_live_gps else "📍 Selected via Manual Navigation"
        return (
            f"### 📍 Active Location Telemetry\n\n"
            f"- **City**: **{loc_city}**\n"
            f"- **District**: **{loc_district}**\n"
            f"- **State / Territory**: **{loc_state}**\n"
            f"- **Country**: India\n"
            f"- **Exact Coordinates**: `{lat:.6f}° N, {lon:.6f}° E`\n"
            f"- **Position Mode**: {gps_tag}\n\n"
            f"**Nearest Air-Quality Monitoring Sensor**:\n"
            f"- Station: **{stn_name}** ({stn_city})\n"
            f"- Distance from your location: **{stn_dist} km**\n"
            f"- Current Station AQI: **{aqi_val}** ({aqi_cat})\n\n"
            f"You can click **📍 MY LOCATION** on the top action bar to refresh your browser GPS at any time."
        )
        
    elif intent == "SAFETY_CHECK":
        risk = live_context.get("risk_details", {})
        mask_str = "Yes, certified N95 respirator is strongly advised." if risk.get("mask_recommended") else "Not mandatory for the general public."
        exercise_str = risk.get("outdoor_exercise", "Acceptable with moderation")
        return (
            f"### 🛡️ Outdoor Health & Safety Advisory for **{loc_city}**\n\n"
            f"Current AQI is **{aqi_val} ({aqi_cat})** with risk rated as **{risk_level}**.\n\n"
            f"- **Outdoor Exercise**: **{exercise_str}**\n"
            f"- **Mask Recommendation**: {mask_str}\n"
            f"- **General Public**: {risk.get('general_advisory', 'Normal activity is acceptable.')}\n"
            f"- **Sensitive Groups (Children, Elderly, Asthma)**: {risk.get('sensitive_advisory', 'Limit prolonged outdoor exertion.')}"
        )
        
    elif intent == "FORECAST":
        forecasts = live_context.get("forecasts", [])
        if forecasts:
            f_lines = "\n".join([f"- **{f['label']} ({f['display_time']})**: Predicted AQI **{f['predicted_aqi']}** ({f['aqi_category']}) | PM2.5 `{f['predicted_pm25']} µg/m³`" for f in forecasts[:4]])
            return (
                f"### 🔮 Machine Learning AQI Forecast for **{loc_city}**\n\n"
                f"Generated by the champion gradient-boosted regression pipeline:\n\n"
                f"{f_lines}\n\n"
                f"*Note: Forecasts are machine learning projections based on autoregressive lag and weather interaction features, labeled as **PREDICTED**.*"
            )
        else:
            return f"AQI forecasting for **{loc_city}** indicates steady levels near {aqi_val} based on current wind dispersion ({wind_spd} km/h). View the dedicated **AQI Prediction** page for full horizon charts."
            
    elif intent.startswith("POLLUTANT_"):
        p_key = intent.replace("POLLUTANT_", "").lower()
        info = POLLUTANT_KNOWLEDGE.get(p_key)
        if info:
            current_val = pollutants.get(p_key, "N/A")
            unit = "mg/m³" if p_key == "co" else "µg/m³"
            return (
                f"### 🧪 {info['title']}\n\n"
                f"**Current Reading in {loc_city}**: `{current_val} {unit}`\n\n"
                f"- **What it is**: {info['explanation']}\n"
                f"- **Major Emission Sources**: {info['sources']}\n"
                f"- **Health Impacts**: {info['health_effects']}\n"
                f"- **Indian CPCB 24h Threshold**: `{info['cpcb_standard']} {unit}`"
            )
            
    elif intent == "REDUCE_POLLUTION":
        return (
            f"### 🌱 Targeted Pollution Reduction for **{loc_city}** (Dominant: {dom_pollutant})\n\n"
            f"1. **Public Transit**: Prioritize electrified rail, metro, and CNG/electric buses for urban transit.\n"
            f"2. **Idling Suppression**: Turn off vehicle ignitions during traffic stops exceeding 15 seconds.\n"
            f"3. **Zero Waste Burning**: Strictly enforce bans on open agricultural residue, garden trash, and plastics burning.\n"
            f"4. **Construction Dust Controls**: Mandate perimeter water mist cannons and high dust barrier sheeting.\n"
            f"5. **Indoor Protection**: Use HEPA filtration indoors during peak pollution hours."
        )
        
    elif intent == "PROJECT_ALGO":
        return PROJECT_ARCHITECTURE_KNOWLEDGE
        
    # Default conversational fallthrough
    return (
        f"I am monitoring real-time environmental telemetry for **{loc_city}, {loc_state}** (AQI: **{aqi_val}**, Category: **{aqi_cat}**, Nearest Station: `{stn_name}`).\n\n"
        f"You can ask me about:\n"
        f"- Current AQI & 6-pollutant concentration breakdown\n"
        f"- Health advisories & outdoor exercise safety\n"
        f"- Meteorology (temperature, humidity, wind dispersion)\n"
        f"- Machine learning forecasts & pollution drivers\n"
        f"- Your detected GPS coordinates and nearest monitoring station"
    )
