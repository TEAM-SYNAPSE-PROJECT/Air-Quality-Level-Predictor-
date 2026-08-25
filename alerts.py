"""Rule-based AQI alerts and warnings."""

def generate_alerts(city, aqi_result):
    p = city["pollutants"]
    w = city["weather"]
    aqi = aqi_result["aqi"]
    alerts = []

    if aqi >= 400:
        alerts.append(("CRITICAL", "Severe AQI emergency", f"AQI is {aqi}. Outdoor exposure should be minimized."))
    elif aqi >= 300:
        alerts.append(("CRITICAL", "Very poor air quality", f"AQI is {aqi}. Avoid strenuous outdoor activity."))
    elif aqi >= 200:
        alerts.append(("WARNING", "Poor air quality", f"AQI is {aqi}. Sensitive groups should reduce exposure."))

    if p["pm25"] >= 90:
        alerts.append(("WARNING", "PM2.5 spike", f"PM2.5 is {p['pm25']} µg/m³."))

    if p["pm10"] >= 180:
        alerts.append(("WARNING", "PM10 spike", f"PM10 is {p['pm10']} µg/m³."))

    if w["windSpeed"] < 8 and aqi > 100:
        alerts.append(("ADVISORY", "Low dispersion", f"Wind speed is {w['windSpeed']} km/h; pollutant accumulation is possible."))

    return alerts

def all_national_alerts(cities, calculate_fn):
    rows = []
    for city in cities:
        result = calculate_fn(city["pollutants"])
        for severity, title, message in generate_alerts(city, result):
            rows.append({
                "severity": severity,
                "city": city["name"],
                "aqi": result["aqi"],
                "title": title,
                "message": message,
            })
    order = {"CRITICAL": 0, "WARNING": 1, "ADVISORY": 2}
    return sorted(rows, key=lambda x: order[x["severity"]])
