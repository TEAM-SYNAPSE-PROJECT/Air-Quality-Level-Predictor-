"""
Environmental Report Generation Service.
Generates comprehensive PDF & CSV audit documents separating observed vs predicted data.

The PDF writer uses Helvetica for maximum deployment compatibility. Because Helvetica
is not a full Unicode font, all dynamic text is normalized to Windows-1252/Latin-1
safe characters before being sent to FPDF. This prevents FPDFUnicodeEncodingException
when values such as season emojis are present.
"""
from typing import Dict, Any
from datetime import datetime

import pandas as pd
from fpdf import FPDF


def _pdf_text(value: Any) -> str:
    """Return text that is safe for FPDF built-in Helvetica fonts."""
    if value is None:
        return ""

    text = str(value)

    replacements = {
        "❄️": "Winter",
        "❄": "Winter",
        "☀️": "Summer",
        "☀": "Summer",
        "🌧️": "Monsoon",
        "🌧": "Monsoon",
        "🍂": "Post-Monsoon",
        "µ": "u",
        "μ": "u",
        "°": " deg",
        "³": "3",
        "²": "2",
        "₃": "3",
        "₂": "2",
        "≥": ">=",
        "≤": "<=",
        "→": "->",
        "←": "<-",
        "–": "-",
        "—": "-",
        "•": "-",
        "₹": "INR",
        "×": "x",
        "…": "...",
        "✓": "OK",
        "✗": "X",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Helvetica is a built-in Latin-1 font in FPDF.
    # Any remaining unsupported Unicode character is safely replaced.
    return text.encode("latin-1", errors="replace").decode("latin-1")


class EnvironmentalPDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(11, 15, 25)
        self.cell(
            0,
            10,
            _pdf_text("AIR QUALITY LEVEL PREDICTOR - INTELLIGENCE REPORT"),
            border=0,
            align="C",
        )
        self.ln(8)

        self.set_font("Helvetica", "I", 9)
        self.set_text_color(107, 114, 128)
        self.cell(
            0,
            5,
            _pdf_text("National Air Quality & Environmental Command Center (India)"),
            border=0,
            align="C",
        )
        self.ln(8)

        self.set_draw_color(6, 182, 212)
        self.set_line_width(0.5)
        self.line(10, 26, 200, 26)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(156, 163, 175)
        self.cell(
            0,
            10,
            _pdf_text(
                f"Page {self.page_no()}/{{nb}} | Automated CPCB NAQI Report | Generated dynamically"
            ),
            align="C",
        )


def generate_pdf_report(report_data: Dict[str, Any]) -> bytes:
    """Generate a structured PDF audit report without Unicode font crashes."""
    pdf = EnvironmentalPDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()

    # 1. Location & Meta
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, _pdf_text("1. AUDIT METADATA & TELEMETRY PROVENANCE"), ln=True)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)

    loc = report_data.get("location", {})
    dt_str = report_data.get(
        "timestamp_str", datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    )
    season = report_data.get("season", "N/A")
    data_status = report_data.get("data_status", "LIVE / RECENT")

    pdf.cell(
        95,
        5,
        _pdf_text(f"Location: {loc.get('city', 'Delhi')}, {loc.get('state', 'Delhi')}"),
        ln=False,
    )
    pdf.cell(
        95,
        5,
        _pdf_text(
            f"Coordinates: {loc.get('latitude', '28.61')} N, "
            f"{loc.get('longitude', '77.20')} E"
        ),
        ln=True,
    )
    pdf.cell(95, 5, _pdf_text(f"Generated At: {dt_str}"), ln=False)
    pdf.cell(95, 5, _pdf_text(f"Current Season: {season}"), ln=True)
    pdf.cell(95, 5, _pdf_text(f"Data Provenance: {data_status}"), ln=False)
    pdf.cell(
        95,
        5,
        _pdf_text("Standard: Indian CPCB NAQI Breakpoint Guidelines"),
        ln=True,
    )
    pdf.ln(4)

    # 2. Observed Air Quality Index
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(
        0,
        6,
        _pdf_text("2. OBSERVED REAL-TIME AIR QUALITY METRICS (ACTUAL)"),
        ln=True,
    )

    aqi = report_data.get("aqi", 0)
    cat = report_data.get("category", "N/A")
    dom = report_data.get("dominant_pollutant", "PM2.5")
    risk = report_data.get("risk_level", "N/A")

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(
        0,
        6,
        _pdf_text(
            f"Calculated NAQI: {aqi} | Category: {str(cat).upper()} | "
            f"Primary Driver: {dom} | Risk: {risk}"
        ),
        ln=True,
    )
    pdf.ln(2)

    # Pollutant Table
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(241, 245, 249)

    for width, text in [
        (32, "Pollutant"),
        (32, "Concentration"),
        (32, "Standard Unit"),
        (32, "CPCB Sub-Index"),
        (62, "Safe Benchmark"),
    ]:
        pdf.cell(width, 6, _pdf_text(text), border=1, fill=True)
    pdf.ln()

    pollutants = report_data.get("pollutants", {})
    sub_indices = report_data.get("sub_indices", {})

    benchmarks = {
        "pm25": ("Fine Particulate (PM2.5)", "ug/m3", "60 ug/m3 (24h Standard)"),
        "pm10": ("Coarse Dust (PM10)", "ug/m3", "100 ug/m3 (24h Standard)"),
        "no2": ("Nitrogen Dioxide (NO2)", "ug/m3", "80 ug/m3 (24h Standard)"),
        "so2": ("Sulfur Dioxide (SO2)", "ug/m3", "80 ug/m3 (24h Standard)"),
        "co": ("Carbon Monoxide (CO)", "mg/m3", "2.0 mg/m3 (8h Standard)"),
        "o3": ("Ozone (O3)", "ug/m3", "100 ug/m3 (8h Standard)"),
    }

    pdf.set_font("Helvetica", "", 8)
    for p_key, (p_name, unit, bench) in benchmarks.items():
        val = pollutants.get(p_key, "N/A")
        si = sub_indices.get(p_key, "N/A")
        pdf.cell(32, 5, _pdf_text(p_name), border=1)
        pdf.cell(32, 5, _pdf_text(val), border=1)
        pdf.cell(32, 5, _pdf_text(unit), border=1)
        pdf.cell(32, 5, _pdf_text(si), border=1)
        pdf.cell(62, 5, _pdf_text(bench), border=1)
        pdf.ln()

    pdf.ln(4)

    # 3. Weather Conditions
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(
        0,
        6,
        _pdf_text("3. METEOROLOGICAL DISPERSION CONTEXT"),
        ln=True,
    )
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)

    weather = report_data.get("weather", {})
    pdf.cell(
        95,
        5,
        _pdf_text(
            f"Temperature: {weather.get('temperature', 'N/A')} deg C "
            f"(Feels: {weather.get('feels_like', 'N/A')} deg C)"
        ),
        ln=False,
    )
    pdf.cell(
        95,
        5,
        _pdf_text(f"Relative Humidity: {weather.get('humidity', 'N/A')} %"),
        ln=True,
    )
    pdf.cell(
        95,
        5,
        _pdf_text(f"Wind Speed: {weather.get('wind_speed', 'N/A')} km/h"),
        ln=False,
    )
    pdf.cell(
        95,
        5,
        _pdf_text(f"Surface Pressure: {weather.get('pressure', 'N/A')} hPa"),
        ln=True,
    )
    pdf.cell(
        95,
        5,
        _pdf_text(
            f"Atmospheric Condition: {weather.get('weather_condition', 'N/A')}"
        ),
        ln=True,
    )
    pdf.ln(4)

    # 4. Predictions & Forecasts
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(
        0,
        6,
        _pdf_text("4. MACHINE LEARNING AQI FORECAST (PREDICTED - NOT OBSERVED)"),
        ln=True,
    )

    forecasts = report_data.get("forecasts", [])

    if forecasts:
        pdf.set_font("Helvetica", "B", 8)

        for width, text in [
            (35, "Horizon"),
            (45, "Forecast Target Time"),
            (35, "Predicted PM2.5"),
            (35, "Predicted AQI"),
            (40, "Expected Risk"),
        ]:
            pdf.cell(width, 6, _pdf_text(text), border=1, fill=True)
        pdf.ln()

        pdf.set_font("Helvetica", "", 8)

        for f in forecasts[:6]:
            pdf.cell(35, 5, _pdf_text(f.get("label", "")), border=1)
            pdf.cell(45, 5, _pdf_text(f.get("display_time", "")), border=1)
            pdf.cell(
                35,
                5,
                _pdf_text(f"{f.get('predicted_pm25', 'N/A')} ug/m3"),
                border=1,
            )
            pdf.cell(
                35,
                5,
                _pdf_text(
                    f"{f.get('predicted_aqi', 'N/A')} ({f.get('aqi_category', '')})"
                ),
                border=1,
            )
            pdf.cell(40, 5, _pdf_text(f.get("risk_level", "N/A")), border=1)
            pdf.ln()
    else:
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(
            0,
            5,
            _pdf_text("Multi-step ahead forecast currently being initialized."),
            ln=True,
        )

    pdf.ln(4)

    # 5. Early Warnings & Recommendations
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(
        0,
        6,
        _pdf_text("5. ACTIVE WARNINGS & TARGETED REDUCTION ACTIONS"),
        ln=True,
    )

    warnings = report_data.get("warnings", [])

    if warnings:
        for w in warnings:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(
                0,
                5,
                _pdf_text(
                    f"* [{w.get('severity', 'INFO')}] {w.get('title', '')}"
                ),
                ln=True,
            )
            pdf.set_font("Helvetica", "", 8)
            pdf.multi_cell(
                0,
                4,
                _pdf_text(f"  Action: {w.get('action', '')}"),
            )
            pdf.ln(1)
    else:
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(
            0,
            5,
            _pdf_text("No critical environmental triggers currently active."),
            ln=True,
        )

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(
        0,
        5,
        _pdf_text("Recommended Individual & Community Mitigations:"),
        ln=True,
    )
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(
        0,
        4,
        _pdf_text(
            "- Prioritize electric or CNG public transit; avoid vehicle idling "
            "in congested intersections.\n"
            "- Strictly avoid open biomass, leaf, or solid municipal waste burning.\n"
            "- Utilize certified N95 respirators if AQI > 200 during morning or "
            "evening peak inversion hours.\n"
            "- Maintain indoor air filtration in residential and work spaces."
        ),
    )

    return bytes(pdf.output())


def generate_csv_report(report_data: Dict[str, Any]) -> str:
    """Generate clean CSV text data."""
    flat_record = {
        "timestamp": report_data.get("timestamp_str", ""),
        "city": report_data.get("location", {}).get("city", ""),
        "state": report_data.get("location", {}).get("state", ""),
        "latitude": report_data.get("location", {}).get("latitude", ""),
        "longitude": report_data.get("location", {}).get("longitude", ""),
        "season": report_data.get("season", ""),
        "data_status": report_data.get("data_status", ""),
        "aqi": report_data.get("aqi", ""),
        "aqi_category": report_data.get("category", ""),
        "dominant_pollutant": report_data.get("dominant_pollutant", ""),
        "risk_level": report_data.get("risk_level", ""),
        "pm25_ug_m3": report_data.get("pollutants", {}).get("pm25", ""),
        "pm10_ug_m3": report_data.get("pollutants", {}).get("pm10", ""),
        "no2_ug_m3": report_data.get("pollutants", {}).get("no2", ""),
        "so2_ug_m3": report_data.get("pollutants", {}).get("so2", ""),
        "co_mg_m3": report_data.get("pollutants", {}).get("co", ""),
        "o3_ug_m3": report_data.get("pollutants", {}).get("o3", ""),
        "temperature_c": report_data.get("weather", {}).get("temperature", ""),
        "humidity_pct": report_data.get("weather", {}).get("humidity", ""),
        "wind_speed_kmh": report_data.get("weather", {}).get("wind_speed", ""),
        "weather_condition": report_data.get("weather", {}).get(
            "weather_condition", ""
        ),
    }

    return pd.DataFrame([flat_record]).to_csv(index=False)
