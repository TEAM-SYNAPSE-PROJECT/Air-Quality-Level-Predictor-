"""Curated training knowledge for the Air AI Assistant.

This is an intent/FAQ knowledge base rather than model fine-tuning. It is deliberately
small, transparent and editable so students can show their instructor exactly what the
assistant knows. Runtime answers are generated from the current AQI/pollutant/weather/ML
context, so the chatbot does not blindly return stale canned values.
"""

KNOWLEDGE_BASE = [
    {
        "intent": "current_aqi",
        "title": "Current AQI",
        "patterns": [
            "what is the current aqi", "current air quality", "how is the air now",
            "tell me the aqi", "what is aqi right now", "air quality today",
            "is the air quality good", "current pollution level"
        ],
        "suggestions": ["What is the current AQI?", "Is the air quality safe today?"],
    },
    {
        "intent": "aqi_explain",
        "title": "AQI explanation",
        "patterns": [
            "what does aqi mean", "explain aqi", "how is aqi calculated",
            "how do you calculate aqi", "what is the meaning of aqi",
            "explain the air quality index"
        ],
        "suggestions": ["How is AQI calculated?", "Explain the AQI categories."],
    },
    {
        "intent": "category",
        "title": "AQI category",
        "patterns": [
            "what category is this", "what is the aqi level", "which level is my city",
            "is this good satisfactory poor", "tell me the pollution category"
        ],
        "suggestions": ["What AQI level is my city in?", "What does this AQI category mean?"],
    },
    {
        "intent": "dominant",
        "title": "Dominant pollutant",
        "patterns": [
            "which pollutant is highest", "what is the dominant pollutant",
            "which pollutant is dangerous", "what is causing the aqi",
            "main pollutant", "worst pollutant"
        ],
        "suggestions": ["Which pollutant is driving the AQI?", "Which pollutant is highest?"],
    },
    {
        "intent": "pollutants",
        "title": "Pollutant readings",
        "patterns": [
            "show pollutants", "what are the pollutant levels", "give me pm25 and pm10",
            "pollution readings", "tell me all pollutant values", "current pollutant values"
        ],
        "suggestions": ["Show me all current pollutant readings.", "What are the PM2.5 and PM10 levels?"],
    },
    {
        "intent": "health",
        "title": "Health guidance",
        "patterns": [
            "is it safe to go outside", "health effects", "health advice",
            "can i exercise outside", "should i wear a mask", "is outdoor activity safe",
            "what should people do", "health impact"
        ],
        "suggestions": ["Is it safe to exercise outside?", "What health precautions should I take?"],
    },
    {
        "intent": "pm25",
        "title": "PM2.5",
        "patterns": [
            "what is pm25", "pm2.5 level", "pm 2.5", "explain pm25", "is pm25 high"
        ],
        "suggestions": ["Is PM2.5 high right now?", "Why is PM2.5 important?"],
    },
    {
        "intent": "pm10",
        "title": "PM10",
        "patterns": [
            "what is pm10", "pm10 level", "is pm10 high", "explain pm10"
        ],
        "suggestions": ["Is PM10 high right now?", "What does PM10 mean?"],
    },
    {
        "intent": "season",
        "title": "Season and weather",
        "patterns": [
            "what season is it", "current season", "is it monsoon", "weather impact",
            "how does season affect air quality", "does weather affect aqi",
            "how does monsoon affect pollution"
        ],
        "suggestions": ["What season is it and how does it affect AQI?", "How does weather affect pollution?"],
    },
    {
        "intent": "forecast",
        "title": "AQI forecast",
        "patterns": [
            "what will aqi be tomorrow", "aqi forecast", "predict aqi",
            "future air quality", "next 24 hours", "will pollution increase",
            "forecast air quality"
        ],
        "suggestions": ["What is the 24-hour AQI forecast?", "Will the AQI increase?"],
    },
    {
        "intent": "model",
        "title": "ML model",
        "patterns": [
            "which algorithm do you use", "what model is used", "explain the ml model",
            "how does machine learning work here", "what is xgboost", "which algorithm"
        ],
        "suggestions": ["Which ML algorithm is used?", "How does the AQI prediction model work?"],
    },
    {
        "intent": "anomaly",
        "title": "Anomaly detection",
        "patterns": [
            "are there anomalies", "detect anomaly", "any pollution spike",
            "what is isolation forest", "show unusual pollution", "is there a spike"
        ],
        "suggestions": ["Are there any pollution anomalies?", "How does anomaly detection work?"],
    },
    {
        "intent": "alerts",
        "title": "Alerts",
        "patterns": [
            "any alerts", "show warnings", "is there an alert", "current warnings",
            "critical alert", "what alerts are active"
        ],
        "suggestions": ["Are there any active AQI alerts?", "What warnings are active?"],
    },
    {
        "intent": "compare",
        "title": "City comparison",
        "patterns": [
            "which city is worst", "compare cities", "worst aqi in india",
            "best air quality city", "which city has highest aqi", "compare indian cities"
        ],
        "suggestions": ["Which monitored city has the highest AQI?", "Which city has the lowest AQI?"],
    },
    {
        "intent": "data",
        "title": "Data source",
        "patterns": [
            "where does the data come from", "is this real data", "data source",
            "is this live", "where are readings from", "api used", "is it sensor data"
        ],
        "suggestions": ["Is this real-time sensor data?", "Where does the air-quality data come from?"],
    },
    {
        "intent": "help",
        "title": "Assistant help",
        "patterns": [
            "what can you do", "help me", "what can i ask", "commands", "features"
        ],
        "suggestions": ["What can you do?", "Give me suggested questions."],
    },
]
