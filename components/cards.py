"""
Telemetry Metric Cards & Informational Panels.
Renders dark glassmorphic cards with responsive layout styling.
"""
import streamlit as st
from typing import Dict, Any, List

def render_metric_card(title: str, value: str, subtitle: str = "", badge_text: str = "", badge_color: str = "#C5A368"):
    """Renders a single styled metric tile."""
    badge_html = f'<span style="background: {badge_color}18; color: {badge_color}; border: 1px solid {badge_color}44; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">{badge_text}</span>' if badge_text else ""
    
    card_html = f"""
    <div class="telemetry-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="telemetry-label">{title}</div>
            {badge_html}
        </div>
        <div class="telemetry-value">{value}</div>
        <div class="telemetry-sub">{subtitle}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_pollutant_breakdown_grid(pollutants: Dict[str, float], sub_indices: Dict[str, float]):
    """Renders the 6 standard CPCB pollutant tiles."""
    items = [
        ("PM2.5", pollutants.get("pm25", 0), "µg/m³", sub_indices.get("pm25", 0), "Fine Inhalable Particles", 60),
        ("PM10", pollutants.get("pm10", 0), "µg/m³", sub_indices.get("pm10", 0), "Coarse Road/Soil Dust", 100),
        ("NO2", pollutants.get("no2", 0), "µg/m³", sub_indices.get("no2", 0), "Combustion / Traffic Exhaust", 80),
        ("SO2", pollutants.get("so2", 0), "µg/m³", sub_indices.get("so2", 0), "Industrial / Coal Emissions", 80),
        ("CO", pollutants.get("co", 0), "mg/m³", sub_indices.get("co", 0), "Incomplete Carbon Burning", 2.0),
        ("O3", pollutants.get("o3", 0), "µg/m³", sub_indices.get("o3", 0), "Photochemical Ground Ozone", 100)
    ]
    
    cols = st.columns(6)
    for idx, (p_name, val, unit, sub_idx, desc, safe_std) in enumerate(items):
        with cols[idx]:
            is_above_std = (val > safe_std) if val is not None else False
            status_color = "#EF4444" if is_above_std else "#10B981"
            sub_status = f"Sub-Index: <strong>{round(sub_idx)}</strong>" if sub_idx else "No Index"
            
            st.markdown(f"""
            <div class="telemetry-card" style="padding: 14px 16px; text-align: center;">
                <div style="font-size: 11px; font-weight: 700; color: #C5A368; text-transform: uppercase; letter-spacing: 0.15em;">{p_name}</div>
                <div style="font-size: 20px; font-weight: 700; color: #FFFFFF; margin: 6px 0; font-family: 'JetBrains Mono', monospace;">
                    {val if val is not None else 'N/A'} <span style="font-size: 10px; color: #666666; font-weight: normal;">{unit}</span>
                </div>
                <div style="font-size: 11px; color: {status_color}; font-weight: 500;">
                    {sub_status}
                </div>
                <div style="font-size: 9px; color: #555555; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.08em;">
                    Std: {safe_std} {unit}
                </div>
            </div>
            """, unsafe_allow_html=True)
