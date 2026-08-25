"""
Alert Banners & Early Warning Notification Panels.
"""
import streamlit as st
from typing import List, Dict, Any

def render_alert_banners(alerts: List[Dict[str, Any]]):
    """Renders high-visibility alert cards for active environmental triggers."""
    if not alerts:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; color: #34d399; font-size: 13px;">
            ✅ <strong>All Environmental Triggers Nominal:</strong> No immediate air quality emergency alerts active for this monitoring zone.
        </div>
        """, unsafe_allow_html=True)
        return
        
    severity_styles = {
        "CRITICAL": {"bg": "#151515", "border": "#EF4444", "text": "#EF4444"},
        "HIGH": {"bg": "#151515", "border": "#F97316", "text": "#F97316"},
        "MEDIUM": {"bg": "#151515", "border": "#C5A368", "text": "#C5A368"},
        "INFO": {"bg": "#151515", "border": "#2A2A2A", "text": "#D4B87C"}
    }
    
    for a in alerts:
        sev = a.get("severity", "MEDIUM")
        style = severity_styles.get(sev, severity_styles["MEDIUM"])
        icon = a.get("icon", "⚠️")
        title = a.get("title", "Environmental Alert")
        msg = a.get("message", "")
        action = a.get("action", "")
        
        st.markdown(f"""
        <div style="background: {style['bg']}; border: 1px solid {style['border']}; border-left: 3px solid {style['border']}; border-radius: 6px; padding: 14px 18px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #F5F5F5; font-size: 13px; font-family: 'Playfair Display', Georgia, serif;">
                    <span>{icon}</span>
                    <span>{title}</span>
                </div>
                <span style="font-size: 9px; border: 1px solid {style['border']}88; color: {style['text']}; padding: 2px 6px; border-radius: 3px; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700;">{sev}</span>
            </div>
            <div style="color: #A3A3A3; font-size: 12px; margin-top: 6px; line-height: 1.5;">
                {msg}
            </div>
            {f'<div style="color: #C5A368; font-size: 11px; margin-top: 6px;"><strong>Operational Protocol:</strong> {action}</div>' if action else ''}
        </div>
        """, unsafe_allow_html=True)
