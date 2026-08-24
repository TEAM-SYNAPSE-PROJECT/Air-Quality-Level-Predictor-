"""
AIR AI ASSISTANT
Free-form user interaction with deterministic, data-grounded answers.

The assistant:
- accepts natural-language questions, not only buttons;
- detects greetings and responds conversationally;
- uses the currently selected city's live/demonstration data;
- uses answer variants so the same question does not receive the exact same text;
- avoids inventing sensor readings;
- can answer AQI, pollutants, weather, forecast, season, alerts, anomalies,
  ML model, location and data-source questions.
"""

import random
import re
from datetime import datetime

from cpcb_aqi import calculate_aqi
from anomaly_engine import pollutant_spikes
from alerts import generate_alerts

GREETINGS = {
    "hi", "hello", "hey", "hii", "hiii", "good morning",
    "good afternoon", "good evening", "namaste", "hai"
}

def _norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9? ]+", " ", text.lower())).strip()

def _has(text, *words):
    return any(w in text for w in words)

def _aqi_context(city, live_pollutants=None):
    pollutants = live_pollutants or city["pollutants"]
    return calculate_aqi(pollutants)

def _wind_direction(deg):
    if deg is None:
        return "unknown direction"
    dirs = ["N","NE","E","SE","S","SW","W","NW"]
    return dirs[int((float(deg)+22.5)//45) % 8]

def greeting_answer(city, current, result, season):
    p = city["pollutants"]
    wind = current.get("wind_speed") if current else city["weather"].get("windSpeed")
    temp = current.get("temperature") if current else city["weather"].get("temperature")
    humidity = current.get("humidity") if current else city["weather"].get("humidity")
    pm25 = p.get("pm25")
    pm10 = p.get("pm10")
    return (
        f"Hi! 👋 I'm your Air AI Assistant for **{city['name']}**. "
        f"Right now the dashboard reports an AQI of **{result['aqi']} ({result['category']})**. "
        f"Temperature is about **{temp:.1f}°C**, humidity **{humidity:.0f}%**, and wind "
        f"**{wind:.1f} km/h**. Key pollutants are PM2.5 **{pm25:.1f} µg/m³** and "
        f"PM10 **{pm10:.1f} µg/m³**. The current season is **{season}**. "
        f"Ask me anything about the AQI, pollutants, weather, forecast, health guidance, "
        f"alerts, anomalies or the ML model."
    )

def _answer_variants(topic, city, result, current, forecast_df, season, national_rows):
    p = city["pollutants"]
    current = current or {}
    temp = current.get("temperature", city["weather"].get("temperature"))
    humidity = current.get("humidity", city["weather"].get("humidity"))
    wind = current.get("wind_speed", city["weather"].get("windSpeed"))
    wind_dir = _wind_direction(current.get("wind_direction"))
    pm25 = p.get("pm25", 0)
    pm10 = p.get("pm10", 0)
    dominant = result["dominant"].upper()

    variants = {}

    variants["aqi"] = [
        f"The current AQI for **{city['name']}** is **{result['aqi']}**, classified as **{result['category']}**. The dominant pollutant is **{dominant}**.",
        f"For **{city['name']}**, the latest available dashboard AQI is **{result['aqi']} ({result['category']})**. **{dominant}** is currently driving the highest sub-index.",
        f"Current air-quality status: **AQI {result['aqi']} — {result['category']}**. The main contributor is **{dominant}**."
    ]
    variants["temperature"] = [
        f"The current temperature around **{city['name']}** is **{temp:.1f}°C**.",
        f"Right now, the weather data show about **{temp:.1f}°C** in **{city['name']}**.",
        f"Current temperature: **{temp:.1f}°C**. The exact value is refreshed from the live weather source when available."
    ]
    variants["wind"] = [
        f"Wind is currently around **{wind:.1f} km/h**, from approximately **{wind_dir}**.",
        f"The current wind speed is **{wind:.1f} km/h** ({wind_dir}). Wind affects how quickly pollutants disperse.",
        f"Current wind: **{wind:.1f} km/h** toward/from the reported **{wind_dir}** direction. Stronger ventilation generally helps dispersion."
    ]
    variants["pollutants"] = [
        f"Current key pollutants are PM2.5 **{pm25:.1f}**, PM10 **{pm10:.1f}**, NO₂ **{p.get('no2',0):.1f}**, SO₂ **{p.get('so2',0):.1f}**, CO **{p.get('co',0):.2f}**, and O₃ **{p.get('o3',0):.1f}**.",
        f"Pollutant snapshot for **{city['name']}**: PM2.5 {pm25:.1f} µg/m³, PM10 {pm10:.1f} µg/m³, NO₂ {p.get('no2',0):.1f} µg/m³, SO₂ {p.get('so2',0):.1f} µg/m³, CO {p.get('co',0):.2f} mg/m³ and O₃ {p.get('o3',0):.1f} µg/m³.",
    ]
    variants["pm25"] = [
        f"PM2.5 is **{pm25:.1f} µg/m³**. Fine particles can penetrate deep into the lungs; the AQI calculation shows how much this concentration contributes.",
        f"The current PM2.5 reading is **{pm25:.1f} µg/m³**. If it rises, sensitive people should consider reducing prolonged outdoor exposure.",
    ]
    variants["pm10"] = [
        f"PM10 is currently **{pm10:.1f} µg/m³**. These larger particles are commonly associated with dust, road activity and other coarse sources.",
        f"The latest PM10 value is **{pm10:.1f} µg/m³**; its CPCB sub-index is included in the AQI breakdown."
    ]
    variants["health"] = [
        f"The AQI is **{result['aqi']} ({result['category']})**. {result.get('health','Use the AQI category as the primary guide for outdoor activity.')}",
        f"Health guidance for the current **{result['category']}** level: {result.get('health','Reduce exposure if you are sensitive to air pollution.')}"
    ]
    variants["season"] = [
        f"It is **{season}** in India at this time of year. Season affects air quality through rainfall, humidity, wind and atmospheric mixing.",
        f"Current season: **{season}**. Weather conditions can change pollutant dispersion, especially when winds are weak or rain is absent."
    ]

    if forecast_df is not None and len(forecast_df):
        first = forecast_df.iloc[0]
        last = forecast_df.iloc[-1]
        variants["weather_forecast"] = [
            f"The weather forecast starts around **{first['date'].strftime('%d %b')}** at **{first['min_temp']:.0f}–{first['max_temp']:.0f}°C**, with up to **{first['rain_probability']:.0f}%** precipitation probability. Over the displayed period, the final day is about **{last['min_temp']:.0f}–{last['max_temp']:.0f}°C**.",
            f"For the upcoming forecast, expect temperatures between roughly **{first['min_temp']:.0f}°C and {first['max_temp']:.0f}°C** on the first day, with **{first['rain_probability']:.0f}%** rain probability. The dashboard shows the full multi-day forecast."
        ]

    alerts = generate_alerts(city, result)
    if alerts:
        variants["alerts"] = [
            "There are active air-quality alerts: " + "; ".join(a[1] for a in alerts) + ".",
            "Current warning status: " + " | ".join(f"{a[0]} — {a[1]}" for a in alerts) + "."
        ]
    else:
        variants["alerts"] = [
            "There are no active rule-based AQI alerts for this city at the moment.",
            "The current alert engine has not triggered a warning for this city's present AQI/pollutant values."
        ]

    spikes = pollutant_spikes(city)
    top = spikes[0] if spikes else None
    variants["anomaly"] = [
        f"The spike engine's highest current signal is **{top['pollutant']}**, with a z-score of **{top['z_score']:.2f}** ({top['severity']}). This is a screening signal, not proof of a sensor fault or pollution source.",
        f"Anomaly screening currently ranks **{top['pollutant']}** highest at **{top['z_score']:.2f} z-score**. The system uses this to flag unusual pollutant levels for investigation."
    ] if top else ["No anomaly result is available."]

    return variants

def detect_topic(text):
    t = _norm(text)
    if t in GREETINGS or any(t.startswith(g + " ") for g in GREETINGS):
        return "greeting"
    if _has(t, "forecast", "tomorrow", "next week", "next 7", "weather forecast", "rain tomorrow"):
        return "weather_forecast"
    if _has(t, "aqi", "air quality", "air level", "air pollution level", "status"):
        return "aqi"
    if _has(t, "temperature", "hot", "cold", "degree", "temp"):
        return "temperature"
    if _has(t, "wind", "wind speed", "wind direction"):
        return "wind"
    if _has(t, "pollutant", "pollutants", "pm2.5", "pm25", "pm 2.5", "pm10", "no2", "so2", "o3", "carbon monoxide"):
        if _has(t, "pm2.5", "pm25", "pm 2.5"):
            return "pm25"
        if _has(t, "pm10"):
            return "pm10"
        return "pollutants"
    if _has(t, "safe", "health", "exercise", "outside", "outdoor", "children", "elderly"):
        return "health"
    if _has(t, "season", "monsoon", "summer", "winter", "post monsoon"):
        return "season"
    if _has(t, "alert", "warning", "danger", "critical"):
        return "alerts"
    if _has(t, "anomaly", "spike", "unusual", "abnormal"):
        return "anomaly"
    if _has(t, "algorithm", "model", "xgboost", "machine learning", "ml", "isolation forest"):
        return "ml"
    if _has(t, "city", "cities", "highest", "lowest", "india"):
        return "cities"
    if _has(t, "data source", "source", "api", "real time", "realtime", "live data"):
        return "source"
    if _has(t, "hello", "help", "what can you do", "who are you"):
        return "greeting"
    return "unknown"

def answer_user(
    question,
    city,
    current=None,
    live_pollutants=None,
    forecast_df=None,
    season="Unknown",
    national_rows=None,
    used_answers=None,
):
    used_answers = used_answers if used_answers is not None else set()
    topic = detect_topic(question)
    result = _aqi_context(city, live_pollutants)

    if topic == "greeting":
        return greeting_answer(city, current, result, season), topic

    variants = _answer_variants(topic, city, result, current, forecast_df, season, national_rows or [])
    if topic == "ml":
        answers = [
            "The prediction pipeline uses **XGBoost Regressor** when XGBoost is available, with **Random Forest** as a fallback. It engineers time/lag features and predicts AQI from pollutant and weather signals.",
            "This project combines a supervised AQI prediction model with **Isolation Forest** for anomaly detection. XGBoost is the primary regressor and Random Forest is the fallback."
        ]
    elif topic == "cities":
        rows = national_rows or []
        if rows:
            highest = max(rows, key=lambda x: x["aqi"])
            lowest = min(rows, key=lambda x: x["aqi"])
            answers = [
                f"Among the monitored demo/live city records currently loaded, **{highest['city']}** has the highest AQI at **{highest['aqi']}**, while **{lowest['city']}** has the lowest at **{lowest['aqi']}**.",
                f"Current city comparison: highest AQI is **{highest['city']} ({highest['aqi']})**; lowest is **{lowest['city']} ({lowest['aqi']})**."
            ]
        else:
            answers = ["City comparison data is not available right now."]
    elif topic == "source":
        answers = [
            "When internet access is available, the app fetches live weather and air-quality data from **Open-Meteo** for the selected coordinates. If that service is unavailable, the app clearly switches to built-in demo data instead of pretending demo values are live.",
            "The dashboard distinguishes **LIVE API data** from **demo fallback data**. Weather and pollutant values come from the configured live source when reachable; otherwise the application labels the fallback."
        ]
    elif topic == "unknown":
        return (
            f"I can help with **{city['name']} AQI, pollutants, wind, temperature, weather forecast, "
            f"health guidance, alerts, anomalies, seasons, cities, data sources and the ML model**. "
            f"Try asking: “What is the current AQI?”, “Will it rain tomorrow?”, or “Is it safe to exercise outside?”",
            topic
        )
    else:
        answers = variants.get(topic, variants["aqi"])

    # Avoid exact repetition while variants remain.
    available = [(i, a) for i, a in enumerate(answers) if (topic, i) not in used_answers]
    if not available:
        # Reset only this topic after all variants have been seen.
        for i in range(len(answers)):
            used_answers.discard((topic, i))
        available = list(enumerate(answers))
    idx, selected = random.choice(available)
    used_answers.add((topic, idx))
    return selected, topic
