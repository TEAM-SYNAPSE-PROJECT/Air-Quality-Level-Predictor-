"""
Page 2: India-Wide Air Quality Intelligence & State Benchmarking.
"""
import streamlit as st
from components.page_theme import prepare_page
import pandas as pd
import plotly.express as px
from services.air_quality_service import get_india_wide_monitoring_status
from components.navbar import render_command_header
from components.cards import render_metric_card

st.set_page_config(page_title="India Air Quality | Air Quality Predictor", page_icon="🇮🇳", layout="wide")

prepare_page()


# Fetch Dynamic India Monitoring Status
status_summary = get_india_wide_monitoring_status()
df_india = status_summary["dataset_df"]

render_command_header(city="All India", state="National Overview", status="DYNAMIC DATASET")

# Top Mandatory India Monitoring Metrics Bar
st.markdown("### 🇮🇳 NATIONAL AIR QUALITY TELEMETRY SUMMARY")
st.caption("Real-time aggregated indicators calculated dynamically across all registered Indian ambient monitoring stations.")

m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    render_metric_card(
        "Total Cities Monitored",
        f"{status_summary['total_monitored']}",
        "Active continuous CAAQM & open sensors",
        "National Network",
        "#38bdf8"
    )

with m_col2:
    render_metric_card(
        "Cities Currently At Risk",
        f"{status_summary['cities_at_risk']}",
        "AQI > 200 (Poor, Very Poor, Severe)",
        "Action Required",
        "#ef4444"
    )

with m_col3:
    render_metric_card(
        "Cities with Good/Satisfactory Air",
        f"{status_summary['cities_good_satisfactory']}",
        "AQI <= 100 (Safe for outdoor activities)",
        "Clean Air",
        "#10b981"
    )

with m_col4:
    render_metric_card(
        "Cities Requiring Attention",
        f"{status_summary['cities_requiring_attention']}",
        "AQI 101-200 (Moderate breathing risk)",
        "Watchlist",
        "#f59e0b"
    )

st.markdown("---")

# City Search & State Filter
search_col, state_filter_col, sort_col = st.columns([2, 1.5, 1.5])

with search_col:
    search_query = st.text_input("🔍 Search Indian City, State, or Station", placeholder="e.g. Delhi, Mumbai, Bengaluru, Lucknow, Patna...")

with state_filter_col:
    all_states = ["All States"] + sorted(list(df_india["state"].dropna().unique()))
    selected_state_filter = st.selectbox("Filter by State", all_states)

with sort_col:
    sort_by = st.selectbox("Sort Table By", ["AQI (Highest First)", "AQI (Lowest First)", "PM2.5 (Highest First)", "City Name (A-Z)"])

# Filter DataFrame
filtered_df = df_india.copy()
if selected_state_filter != "All States":
    filtered_df = filtered_df[filtered_df["state"] == selected_state_filter]
if search_query:
    q = search_query.lower()
    filtered_df = filtered_df[
        filtered_df["city"].str.lower().str.contains(q, na=False) |
        filtered_df["state"].str.lower().str.contains(q, na=False) |
        filtered_df["station"].str.lower().str.contains(q, na=False)
    ]

# Sort
if sort_by == "AQI (Highest First)":
    filtered_df = filtered_df.sort_values(by="aqi", ascending=False)
elif sort_by == "AQI (Lowest First)":
    filtered_df = filtered_df.sort_values(by="aqi", ascending=True)
elif sort_by == "PM2.5 (Highest First)":
    filtered_df = filtered_df.sort_values(by="pm25", ascending=False)
elif sort_by == "City Name (A-Z)":
    filtered_df = filtered_df.sort_values(by="city", ascending=True)

# Charts Section: State Averages & Category Distribution
col_chart1, col_chart2 = st.columns([1.3, 1])

with col_chart1:
    st.markdown("#### 📊 Average AQI by Indian State")
    state_avg = df_india.groupby("state")["aqi"].mean().reset_index().sort_values(by="aqi", ascending=False).head(15)
    fig_state = px.bar(
        state_avg,
        x="state",
        y="aqi",
        color="aqi",
        color_continuous_scale="Reds",
        labels={"state": "State", "aqi": "Average AQI"},
        title="Top 15 Most Polluted States (Average AQI)"
    )
    fig_state.update_layout(
        paper_bgcolor="rgba(11, 15, 25, 0.7)",
        plot_bgcolor="rgba(17, 24, 39, 0.7)",
        font={"color": "#cbd5e1"},
        margin=dict(l=30, r=20, t=40, b=80),
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_state, use_container_width=True)

with col_chart2:
    st.markdown("#### 🥧 National AQI Category Distribution")
    cat_counts = df_india["aqi_category"].value_counts().reset_index()
    cat_counts.columns = ["Category", "Count"]
    
    cat_color_map = {
        "Good": "#10b981",
        "Satisfactory": "#84cc16",
        "Moderate": "#f59e0b",
        "Poor": "#f97316",
        "Very Poor": "#ef4444",
        "Severe": "#991b1b"
    }
    
    fig_cat = px.pie(
        cat_counts,
        names="Category",
        values="Count",
        color="Category",
        color_discrete_map=cat_color_map,
        hole=0.45
    )
    fig_cat.update_layout(
        paper_bgcolor="rgba(11, 15, 25, 0.7)",
        font={"color": "#cbd5e1"},
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# Data Table Display
st.markdown("### 📋 India-Wide Continuous Monitoring Stations")
st.caption(f"Displaying {len(filtered_df)} of {len(df_india)} monitoring locations.")

display_cols = ["city", "state", "aqi", "aqi_category", "dominant_pollutant", "pm25", "pm10", "temperature", "humidity", "risk_level", "timestamp"]
col_rename = {
    "city": "City",
    "state": "State",
    "aqi": "NAQI",
    "aqi_category": "AQI Level",
    "dominant_pollutant": "Dominant Pollutant",
    "pm25": "PM2.5 (µg/m³)",
    "pm10": "PM10 (µg/m³)",
    "temperature": "Temp (°C)",
    "humidity": "Humidity (%)",
    "risk_level": "Assessed Risk",
    "timestamp": "Last Telemetry Sync"
}

st.dataframe(
    filtered_df[display_cols].rename(columns=col_rename),
    use_container_width=True,
    hide_index=True
)
