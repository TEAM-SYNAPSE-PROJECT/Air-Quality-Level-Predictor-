"""
Page 6: Exploratory Data Analysis & Statistical Environmental Patterns.
"""
import streamlit as st
from components.page_theme import prepare_page
import pandas as pd
import plotly.express as px

from components.navbar import render_command_header
from components.charts import render_correlation_heatmap


st.set_page_config(
    page_title="EDA & Statistical Analysis | Air Quality Predictor",
    page_icon="📈",
    layout="wide",
)

prepare_page()


render_command_header(
    city="Statistical Analytics",
    state="Dataset Audit",
    status="DATA EXPLORER",
)

st.markdown("### 📈 EXPLORATORY DATA ANALYSIS (EDA)")
st.caption(
    "Statistical distributions, seasonal dispersion variances, "
    "diurnal patterns, and cross-pollutant correlations."
)


# ---------------------------------------------------------------------------
# Load and normalize the dataset
# ---------------------------------------------------------------------------
df = pd.read_csv("data/sample_air_quality.csv")

# The supplied sample CSV does not contain derived time fields such as
# season/hour/day_of_week. Create them here so every dataset version works.
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).copy()

    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_name()

    month = df["timestamp"].dt.month
    df["season"] = "Post-Monsoon"
    df.loc[month.isin([12, 1, 2]), "season"] = "Winter"
    df.loc[month.isin([3, 4, 5]), "season"] = "Summer"
    df.loc[month.isin([6, 7, 8, 9]), "season"] = "Monsoon"
else:
    if "hour" not in df.columns:
        df["hour"] = 0
    if "day_of_week" not in df.columns:
        df["day_of_week"] = "Unknown"
    if "season" not in df.columns:
        df["season"] = "Unknown"


# Convert numeric analysis columns safely.
numeric_candidates = [
    "pm25",
    "pm10",
    "no2",
    "so2",
    "co",
    "o3",
    "temperature",
    "humidity",
    "wind_speed",
    "pressure",
]

for col in numeric_candidates:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Pollutant Distributions",
        "🍂 Seasonal & Diurnal Cycles",
        "🌡️ Weather vs Pollution Interactions",
        "🔥 Correlation Matrix",
    ]
)


with tab1:
    st.markdown("#### Frequency Distribution of Atmospheric Particulates & Gases")

    available_pollutants = [
        c for c in ["pm25", "pm10", "no2", "so2", "co", "o3"] if c in df.columns
    ]

    if not available_pollutants:
        st.error("No pollutant columns were found in the dataset.")
    else:
        p_sel = st.selectbox(
            "Select Target Variable for Histogram & KDE",
            available_pollutants,
            index=0,
        )

        hist_df = df[[p_sel]].dropna()

        fig_hist = px.histogram(
            hist_df,
            x=p_sel,
            nbins=50,
            marginal="box",
            color_discrete_sequence=["#C5A368"],
            title=f"Empirical Probability Distribution of {p_sel.upper()}",
        )

        fig_hist.update_layout(
            paper_bgcolor="#0A0A0A",
            plot_bgcolor="#111111",
            font={"color": "#888888", "family": "Plus Jakarta Sans"},
            xaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
            yaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
            height=380,
        )

        st.plotly_chart(fig_hist, use_container_width=True)


with tab2:
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.markdown("#### 🍂 Seasonal Distribution (Boxplot)")

        if "season" not in df.columns or "pm25" not in df.columns:
            st.warning("Season or PM2.5 data is unavailable for this dataset.")
        else:
            season_df = df[["season", "pm25"]].dropna()

            # Pass the Series explicitly. This is robust against column-name
            # mismatches in different pandas/Plotly versions.
            fig_season = px.box(
                season_df,
                x=season_df["season"],
                y=season_df["pm25"],
                color=season_df["season"],
                title="PM2.5 Distribution Across Indian Seasons",
                color_discrete_sequence=[
                    "#C5A368",
                    "#D4B87C",
                    "#10B981",
                    "#EF4444",
                ],
                labels={
                    "x": "Season",
                    "y": "PM2.5 (ug/m3)",
                },
            )

            fig_season.update_layout(
                paper_bgcolor="#0A0A0A",
                plot_bgcolor="#111111",
                font={"color": "#888888", "family": "Plus Jakarta Sans"},
                xaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
                yaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
                height=360,
                showlegend=False,
            )

            st.plotly_chart(fig_season, use_container_width=True)

    with col_c2:
        st.markdown("#### ⏰ 24-Hour Diurnal Cycle")

        required = [
            c for c in ["hour", "pm25", "pm10", "no2"] if c in df.columns
        ]

        if len(required) < 4:
            st.warning(
                "Not enough pollutant/time columns are available for this chart."
            )
        else:
            hourly_avg = (
                df[required]
                .dropna()
                .groupby("hour")[["pm25", "pm10", "no2"]]
                .mean()
                .reset_index()
            )

            fig_diurnal = px.line(
                hourly_avg,
                x="hour",
                y=["pm25", "pm10", "no2"],
                title="Diurnal Pollutant Pattern",
                markers=True,
                color_discrete_sequence=[
                    "#C5A368",
                    "#D4B87C",
                    "#10B981",
                ],
            )

            fig_diurnal.update_layout(
                paper_bgcolor="#0A0A0A",
                plot_bgcolor="#111111",
                font={"color": "#888888", "family": "Plus Jakarta Sans"},
                xaxis=dict(
                    tickmode="linear",
                    tick0=0,
                    dtick=2,
                    gridcolor="#1A1A1A",
                    zerolinecolor="#2A2A2A",
                ),
                yaxis=dict(
                    gridcolor="#1A1A1A",
                    zerolinecolor="#2A2A2A",
                ),
                height=360,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=10, color="#888888"),
                ),
            )

            st.plotly_chart(fig_diurnal, use_container_width=True)


with tab3:
    col_w1, col_w2 = st.columns(2)

    with col_w1:
        st.markdown("#### Wind Speed vs PM2.5 (Ventilation Dispersion)")

        if not all(c in df.columns for c in ["wind_speed", "pm25"]):
            st.warning("Wind speed or PM2.5 data is unavailable.")
        else:
            valid = df[["wind_speed", "pm25"]].dropna()
            scatter_df = valid.sample(
                min(500, len(valid)),
                random_state=42,
            )

            # Deliberately no Plotly OLS trendline here, so the page does not
            # require the optional statsmodels package.
            fig_wind = px.scatter(
                scatter_df,
                x="wind_speed",
                y="pm25",
                title="Dispersion: High Wind Velocity Clears Particulates",
                labels={
                    "wind_speed": "Wind Speed (km/h)",
                    "pm25": "PM2.5 (ug/m3)",
                },
            )

            fig_wind.update_layout(
                paper_bgcolor="#0A0A0A",
                plot_bgcolor="#111111",
                font={"color": "#888888", "family": "Plus Jakarta Sans"},
                xaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
                yaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
                height=360,
            )

            st.plotly_chart(fig_wind, use_container_width=True)

    with col_w2:
        st.markdown("#### Temperature vs Ground Ozone (O3 Photochemistry)")

        if not all(c in df.columns for c in ["temperature", "o3"]):
            st.warning("Temperature or O3 data is unavailable.")
        else:
            valid = df[["temperature", "o3"]].dropna()
            scatter_df = valid.sample(
                min(500, len(valid)),
                random_state=42,
            )

            fig_temp = px.scatter(
                scatter_df,
                x="temperature",
                y="o3",
                title="Photochemistry: Temperature and Ozone Relationship",
                labels={
                    "temperature": "Temperature (deg C)",
                    "o3": "Ozone (ug/m3)",
                },
            )

            fig_temp.update_layout(
                paper_bgcolor="#0A0A0A",
                plot_bgcolor="#111111",
                font={"color": "#888888", "family": "Plus Jakarta Sans"},
                xaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
                yaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
                height=360,
            )

            st.plotly_chart(fig_temp, use_container_width=True)


with tab4:
    st.plotly_chart(
        render_correlation_heatmap(df),
        use_container_width=True,
    )
