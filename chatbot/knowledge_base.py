"""
Environmental Knowledge Base.
Contains facts, Indian CPCB standards, medical guidelines,
and architecture explanations.
"""

POLLUTANT_KNOWLEDGE = {
    "pm25": {
        "title": "PM2.5 (Fine Particulate Matter <= 2.5 micrometers)",
        "explanation": "Microscopic airborne particles less than 2.5 microns in diameter (about 30 times finer than a human hair). Because of their microscopic size, they bypass nasal cilia and penetrate deep into lung alveoli and the bloodstream.",
        "sources": "Vehicular exhaust, coal-fired power plants, biomass burning, crop stubble combustion, construction, industrial emissions.",
        "health_impact": "Aggravates asthma, chronic bronchitis, reduced lung function, cardiovascular arrhythmia, and increased mortality on prolonged exposure.",
        "cpcb_standard": "60 µg/m³ (24-hour average), 40 µg/m³ (Annual average)"
    },
    "pm10": {
        "title": "PM10 (Coarse Particulate Matter <= 10 micrometers)",
        "explanation": "Inhalable coarse particles ranging from 2.5 to 10 micrometers.",
        "sources": "Road dust resuspension, construction debris, agricultural tilling, stone crushing, desert windblown dust.",
        "health_impact": "Irritates eyes, throat, and upper airways; triggers severe coughing and reduces athletic capacity.",
        "cpcb_standard": "100 µg/m³ (24-hour average), 60 µg/m³ (Annual average)"
    },
    "no2": {
        "title": "NO2 (Nitrogen Dioxide)",
        "explanation": "A pungent reddish-brown gas produced during high-temperature fuel combustion.",
        "sources": "Diesel vehicle exhausts, thermal power stations, heavy industrial furnaces.",
        "health_impact": "Inflames airways, increases vulnerability to respiratory infections, triggers asthma attacks.",
        "cpcb_standard": "80 µg/m³ (24-hour average), 40 µg/m³ (Annual average)"
    },
    "so2": {
        "title": "SO2 (Sulfur Dioxide)",
        "explanation": "A toxic gas formed by the burning of fossil fuels containing sulfur.",
        "sources": "Coal-fired thermal electricity generation, petroleum refineries, metal smelting.",
        "health_impact": "Bronchoconstriction, throat irritation, exacerbates cardiovascular and pulmonary diseases.",
        "cpcb_standard": "80 µg/m³ (24-hour average), 50 µg/m³ (Annual average)"
    },
    "co": {
        "title": "CO (Carbon Monoxide)",
        "explanation": "A colorless, odorless, highly toxic gas formed by incomplete carbon combustion.",
        "sources": "Poorly tuned gasoline engines, biomass chulhas, enclosed generator sets, waste burning.",
        "health_impact": "Binds to hemoglobin with 200x affinity compared to oxygen (forming carboxyhemoglobin), starving vital organs of oxygen.",
        "cpcb_standard": "2.0 mg/m³ (8-hour average), 4.0 mg/m³ (1-hour average)"
    },
    "o3": {
        "title": "O3 (Tropospheric / Ground-Level Ozone)",
        "explanation": "Secondary photochemical pollutant formed when NOx and VOCs react in the presence of intense solar ultraviolet radiation.",
        "sources": "Secondary atmospheric reactions downstream of traffic and solvent emissions on hot sunny afternoons.",
        "health_impact": "Severe airway inflammation, chest pain, wheezing, significant lung tissue scarring.",
        "cpcb_standard": "100 µg/m³ (8-hour average), 180 µg/m³ (1-hour average)"
    }
}

PROJECT_ARCHITECTURE_KNOWLEDGE = """
The **Air Quality Level Predictor** is a live India-wide environmental intelligence platform built with the following architecture:
1. **Dynamic Real-Time Ingestion**: Real-time datetime calculation for Asia/Kolkata (IST), live meteorological seasons (Winter, Summer, Monsoon, Post-Monsoon), GPS reverse geocoding, and Open-Meteo atmospheric telemetry.
2. **Indian CPCB NAQI Engine**: Strict mathematical implementation of Central Pollution Control Board piecewise linear sub-index interpolation for PM2.5, PM10, NO2, SO2, CO, and O3.
3. **Machine Learning Pipeline**:
   - **Chronological Time Split**: Strict past-train, recent-val, future-test partitioning preventing lookahead bias.
   - **Feature Engineering**: 60+ engineered indicators including cyclical diurnal time, ventilation indices, meteorological interaction ratios, autoregressive lags (t-1, t-2, t-3, t-6, t-12, t-24), and rolling aggregates (3h, 6h, 12h, 24h).
   - **Model Benchmarking**: Trains and compares Ridge Linear Regression, Random Forest Regressors, and XGBoost Gradient Boosting models using MAE, RMSE, and R².
   - **Anomaly Detection**: Uses Scikit-Learn Isolation Forest to detect atmospheric outlier spikes.
4. **Early Warning System**: Real-time evaluation across 7 distinct environmental trigger cases.
5. **Interactive Visualization**: Plotly telemetry indicators, India risk distribution maps, and dynamic mitigation recommendations.
"""
