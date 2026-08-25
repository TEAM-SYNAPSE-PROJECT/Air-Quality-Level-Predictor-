"""
Environmental Report Generation Service.
Generates comprehensive PDF & CSV audit documents separating observed vs predicted data.
"""
from typing import Dict, Any, Optional
import io
import pandas as pd
from datetime import datetime
from fpdf import FPDF

class EnvironmentalPDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(11, 15, 25)
        self.cell(0, 10, "AIR QUALITY LEVEL PREDICTOR - INTELLIGENCE REPORT", border=0, align="C")
        self.ln(8)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(107, 114, 128)
        self.cell(0, 5, "National Air Quality & Environmental Command Center (India)", border=0, align="C")
        self.ln(8)
        self.set_draw_color(6, 182, 212)
        self.set_line_width(0.5)
        self.line(10, 26, 200, 26)
        self.ln(6)
        
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(156, 163, 175)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | Automated CPCB NAQI Report | Generated dynamically", align="C")

def generate_pdf_report(report_data: Dict[str, Any]) -> bytes:
    """Generates structured PDF audit report."""
    pdf = EnvironmentalPDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # 1. Location & Meta
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, "1. AUDIT METADATA & TELEMETRY PROVENANCE", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    
    loc = report_data.get("location", {})
    dt_str = report_data.get("timestamp_str", datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"))
    season = report_data.get("season", "N/A")
    data_status = report_data.get("data_status", "LIVE / RECENT")
    
    pdf.cell(95, 5, f"Location: {loc.get('city', 'Delhi')}, {loc.get('state', 'Delhi')}", ln=False)
    pdf.cell(95, 5, f"Coordinates: {loc.get('latitude', '28.61')} N, {loc.get('longitude', '77.20')} E", ln=True)
    pdf.cell(95, 5, f"Generated At: {dt_str}", ln=False)
    pdf.cell(95, 5, f"Current Season: {season}", ln=True)
    pdf.cell(95, 5, f"Data Provenance: {data_status}", ln=False)
    pdf.cell(95, 5, f"Standard: Indian CPCB NAQI Breakpoint Guidelines", ln=True)
    pdf.ln(4)
    
    # 2. Observed Air Quality Index
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, "2. OBSERVED REAL-TIME AIR QUALITY METRICS (ACTUAL)", ln=True)
    
    aqi = report_data.get("aqi", 0)
    cat = report_data.get("category", "N/A")
    dom = report_data.get("dominant_pollutant", "PM2.5")
    risk = report_data.get("risk_level", "N/A")
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, f"Calculated NAQI: {aqi} | Category: {cat.upper()} | Primary Driver: {dom} | Risk: {risk}", ln=True)
    pdf.ln(2)
    
    # Pollutant Table
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(32, 6, "Pollutant", border=1, fill=True)
    pdf.cell(32, 6, "Concentration", border=1, fill=True)
    pdf.cell(32, 6, "Standard Unit", border=1, fill=True)
    pdf.cell(32, 6, "CPCB Sub-Index", border=1, fill=True)
    pdf.cell(62, 6, "Safe Benchmark", border=1, fill=True)
    pdf.ln()
    
    pollutants = report_data.get("pollutants", {})
    sub_indices = report_data.get("sub_indices", {})
    
    benchmarks = {
        "pm25": ("Fine Particulate (PM2.5)", "µg/m³", "60 µg/m³ (24h Standard)"),
        "pm10": ("Coarse Dust (PM10)", "µg/m³", "100 µg/m³ (24h Standard)"),
        "no2": ("Nitrogen Dioxide (NO2)", "µg/m³", "80 µg/m³ (24h Standard)"),
        "so2": ("Sulfur Dioxide (SO2)", "µg/m³", "80 µg/m³ (24h Standard)"),
        "co": ("Carbon Monoxide (CO)", "mg/m³", "2.0 mg/m³ (8h Standard)"),
        "o3": ("Ozone (O3)", "µg/m³", "100 µg/m³ (8h Standard)")
    }
    
    pdf.set_font("Helvetica", "", 8)
    for p_key, (p_name, unit, bench) in benchmarks.items():
        val = pollutants.get(p_key, "N/A")
        si = sub_indices.get(p_key, "N/A")
        pdf.cell(32, 5, p_name, border=1)
        pdf.cell(32, 5, f"{val}", border=1)
        pdf.cell(32, 5, unit, border=1)
        pdf.cell(32, 5, f"{si}", border=1)
        pdf.cell(62, 5, bench, border=1)
        pdf.ln()
        
    pdf.ln(4)
    
    # 3. Weather Conditions
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, "3. METEOROLOGICAL DISPERSION CONTEXT", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    
    weather = report_data.get("weather", {})
    pdf.cell(95, 5, f"Temperature: {weather.get('temperature', 'N/A')} °C (Feels: {weather.get('feels_like', 'N/A')} °C)", ln=False)
    pdf.cell(95, 5, f"Relative Humidity: {weather.get('humidity', 'N/A')} %", ln=True)
    pdf.cell(95, 5, f"Wind Speed: {weather.get('wind_speed', 'N/A')} km/h", ln=False)
    pdf.cell(95, 5, f"Surface Pressure: {weather.get('pressure', 'N/A')} hPa", ln=True)
    pdf.cell(95, 5, f"Atmospheric Condition: {weather.get('weather_condition', 'N/A')}", ln=True)
    pdf.ln(4)
    
    # 4. Predictions & Forecasts (Explicitly labeled)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, "4. MACHINE LEARNING AQI FORECAST (PREDICTED - NOT OBSERVED)", ln=True)
    
    forecasts = report_data.get("forecasts", [])
    if forecasts:
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(241, 245, 249)
        pdf.cell(35, 6, "Horizon", border=1, fill=True)
        pdf.cell(45, 6, "Forecast Target Time", border=1, fill=True)
        pdf.cell(35, 6, "Predicted PM2.5", border=1, fill=True)
        pdf.cell(35, 6, "Predicted AQI", border=1, fill=True)
        pdf.cell(40, 6, "Expected Risk", border=1, fill=True)
        pdf.ln()
        
        pdf.set_font("Helvetica", "", 8)
        for f in forecasts[:6]:
            pdf.cell(35, 5, f.get("label", ""), border=1)
            pdf.cell(45, 5, f.get("display_time", ""), border=1)
            pdf.cell(35, 5, f"{f.get('predicted_pm25', 'N/A')} µg/m³", border=1)
            pdf.cell(35, 5, f"{f.get('predicted_aqi', 'N/A')} ({f.get('aqi_category', '')})", border=1)
            pdf.cell(40, 5, f.get("risk_level", "N/A"), border=1)
            pdf.ln()
    else:
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 5, "Multi-step ahead forecast currently being initialized.", ln=True)
        
    pdf.ln(4)
    
    # 5. Early Warnings & Recommendations
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, "5. ACTIVE WARNINGS & TARGETED REDUCTION ACTIONS", ln=True)
    
    warnings = report_data.get("warnings", [])
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(71, 85, 105)
    
    if warnings:
        for w in warnings:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 5, f"* [{w.get('severity', 'INFO')}] {w.get('title', '')}", ln=True)
            pdf.set_font("Helvetica", "", 8)
            pdf.multi_cell(0, 4, f"  Action: {w.get('action', '')}")
            pdf.ln(1)
    else:
        pdf.cell(0, 5, "No critical environmental triggers currently active.", ln=True)
        
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "Recommended Individual & Community Mitigations:", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(0, 4, "- Prioritize electric or CNG public transit; avoid vehicle idling in congested intersections.\n- Strictly avoid open biomass, leaf, or solid municipal waste burning.\n- Utilize certified N95 respirators if AQI > 200 during morning or evening peak inversion hours.\n- Maintain indoor air filtration in residential and work spaces.")
    
    return bytes(pdf.output())

def generate_csv_report(report_data: Dict[str, Any]) -> str:
    """Generates clean CSV text data."""
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
        "weather_condition": report_data.get("weather", {}).get("weather_condition", "")
    }
    df = pd.DataFrame([flat_record])
    return df.to_csv(index=False)
