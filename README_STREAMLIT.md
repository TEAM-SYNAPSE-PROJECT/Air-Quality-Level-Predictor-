# Air Quality Level Predictor — Final Live AI Streamlit Version

## Run

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## New capabilities

### 1. Free-form Air AI Assistant
The user can type ANY natural-language question into the Streamlit chat input. It is not limited to buttons.

Examples:
- Hi
- What is the current AQI?
- What is the temperature?
- Is the wind strong?
- Which pollutant is highest?
- Is it safe to exercise outside?
- Will it rain tomorrow?
- What is the weather forecast?
- Are there any alerts?
- Are there any pollution spikes?
- Which city has the highest AQI?
- What algorithm is used?
- Where does the live data come from?

A greeting such as "Hi" returns a greeting plus the current AQI, temperature, humidity, wind and major pollutants.

### 2. Suggested questions
Clicking a suggested question automatically sends it to the chatbot.

### 3. Non-repeating responses
The assistant keeps a per-session answer history and rotates answer variants instead of returning the exact same sentence repeatedly.

### 4. Live weather
`live_data.py` calls Open-Meteo's forecast service for:
- current temperature
- apparent temperature
- humidity
- wind speed/direction
- pressure
- rain/precipitation
- weather condition
- 7-day forecast
- rain probability
- sunrise/sunset

### 5. Live air-quality data
The app requests current PM2.5, PM10, CO, NO2, SO2 and O3 from the Open-Meteo air-quality service and calculates the project AQI from those concentrations.

### Important accuracy note
This is live API/model data, not a direct CPCB/APPCB station feed. If the API is unavailable, the app clearly labels the screen as DEMO FALLBACK DATA. Never present fallback values as real sensor measurements.

### AQI colours
- Good: green
- Satisfactory: yellow
- Moderately Polluted: orange
- Poor: red
- Very Poor: purple
- Severe: dark/black

### Main files

```text
app.py
live_data.py
chatbot_engine.py
chatbot_knowledge.py
data.py
data_loader.py
cpcb_aqi.py
ml_engine.py
anomaly_engine.py
alerts.py
requirements.txt
.env.example
```


## Performance / speed improvements

- Live city data are cached for 5 minutes, so changing Streamlit pages does not call the external APIs repeatedly.
- The AI chatbot uses only the selected city's current snapshot for normal questions.
- Multi-city API requests are performed lazily only when a city-comparison question is asked.
- The Live Air Map starts from the local city snapshot and has an explicit checkbox for a full live national refresh.
- HTTP connections are reused and the live API timeout is limited to 6 seconds.
- Chat messages render in the same Streamlit run instead of forcing an extra rerun.

If the network/API is slow, the dashboard still falls back to local project data rather than blocking every page transition.
