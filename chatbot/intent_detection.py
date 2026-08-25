"""
Intent Detection & Query Classification.
Classifies user natural-language queries into discrete actionable operational intents.
"""
import re

INTENTS = {
    "GREETING": [r"\b(hi|hello|hey|greetings|good morning|good afternoon|good evening|namaste)\b"],
    "CURRENT_AQI": [r"\b(aqi|air quality|pollution level|how is the air|how dirty is the air|current air)\b"],
    "CURRENT_WEATHER": [r"\b(temperature|weather|humidity|wind|rain|temp|climate|is it hot|is it raining)\b"],
    "LOCATION": [r"\b(where am i|my location|current city|which city|coordinates|gps)\b"],
    "SAFETY_CHECK": [r"\b(safe outside|can i go out|can i run|should i wear a mask|is it safe for kids|outdoor exercise)\b"],
    "FORECAST": [r"\b(tomorrow|forecast|future|next hour|predicted|will it rain|prediction|trend)\b"],
    "POLLUTANT_PM25": [r"\b(pm2\.?5|fine particle|fine particulate)\b"],
    "POLLUTANT_PM10": [r"\b(pm10|coarse particle|dust)\b"],
    "POLLUTANT_NO2": [r"\b(no2|nitrogen dioxide)\b"],
    "POLLUTANT_SO2": [r"\b(so2|sulfur dioxide)\b"],
    "POLLUTANT_CO": [r"\b(carbon monoxide|\bco\b)\b"],
    "POLLUTANT_O3": [r"\b(ozone|o3)\b"],
    "REDUCE_POLLUTION": [r"\b(reduce pollution|improve air|stop pollution|how to reduce|mitigate|clean air)\b"],
    "PROJECT_ALGO": [r"\b(how does this work|algorithm|model|architecture|xgboost|random forest|machine learning|cpcb formula)\b"]
}

def detect_user_intent(user_message: str) -> str:
    """Classifies user natural language input into standard intent category."""
    msg = user_message.lower().strip()
    
    for intent, patterns in INTENTS.items():
        for pat in patterns:
            if re.search(pat, msg):
                return intent
                
    return "GENERAL"
