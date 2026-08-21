# AIR QUALITY LEVEL PREDICTOR

**Predict • Monitor • Protect** | Built by Team Synapse (Indian CPCB NAQI Standard)

---

## 🚀 Running the Python / Streamlit Application

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit Application
```bash
streamlit run app.py
```

The Streamlit app includes:
- **Circular Gauge Diagram**: AQI number and state string (`Good`, `Satisfactory`, `Moderate`, `Poor`, `Very Poor`, `Severe`)
- **Pollutant & Weather Bar Graphs**: PM2.5, PM10, NO2, SO2, CO, O3, Temperature, and Humidity
- **🔮 Future Air Quality Prediction**: 72-hour machine learning forecasting conditioned on meteorology
- **🗺️ All-Over India Station Map**: Interactive map across Indian cities and monitoring stations
- **🧮 Interactive AQI Calculator**: Custom user inputs for calculating official CPCB sub-indices and overall AQI

---

## ⚡ Running the React Web Application

```bash
npm install
npm run dev
```
Runs the Vite/React dashboard on `http://localhost:3000`.
