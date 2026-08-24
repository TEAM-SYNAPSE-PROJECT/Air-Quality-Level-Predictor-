"""
AIR QUALITY LEVEL PREDICTOR — LIVE AI COMMAND CENTER
Python + Streamlit + ML + live weather/air-quality + interactive AI assistant.

Run:
    python -m pip install -r requirements.txt
    python -m streamlit run app.py
"""

from datetime import datetime
import time

import pandas as pd
import plotly.express as px
import streamlit as st

from data import CITIES, get_city
from data_loader import demo_dataframe, fill_missing_with_demo, load_csv
from cpcb_aqi import calculate_aqi
from ml_engine import train_aqi_model, forecast_aqi, isolation_forest_analysis
from alerts import generate_alerts, all_national_alerts
from anomaly_engine import pollutant_spikes
from live_data import (
    fetch_live_bundle, extract_current, forecast_dataframe,
    hourly_weather_dataframe, live_pollutants_as_project_keys
)
from chatbot_engine import answer_user

st.set_page_config(
    page_title="Air Quality Level Predictor",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root {
  --gold:#d6ad57; --green:#00d084; --red:#ff5b63; --blue:#49a6ff;
  --bg:#070707; --panel:#0d0d0e; --line:#252525; --text:#e8e8e8; --muted:#888;
}
.stApp { background:#050505; color:var(--text); }
.block-container { padding:1rem 1.4rem 3rem; max-width:1500px; }
section[data-testid="stSidebar"] { background:#090909; border-right:1px solid #252525; }
section[data-testid="stSidebar"] * { color:#ddd; }
.hero {
  background:linear-gradient(135deg,#0c0c0c,#11100c);
  border:1px solid #272727; border-radius:18px; padding:26px 30px; margin-bottom:16px;
}
.hero h1 { font-family:Georgia,serif; font-size:3rem; margin:0; letter-spacing:-1px; }
.eyebrow { color:var(--gold); letter-spacing:3px; font-size:.75rem; font-weight:700; }
.panel { background:#0b0b0b; border:1px solid #242424; border-radius:16px; padding:18px; }
.telemetry { background:#0d0d0d; border:1px solid #242424; border-radius:14px; padding:18px; min-height:120px; }
.telemetry .label { color:#777; font-size:.7rem; text-transform:uppercase; letter-spacing:1px; }
.telemetry .value { font-size:1.55rem; font-weight:800; margin-top:8px; }
.live-dot { color:#00d084; font-weight:800; }
.aqi-good { border-left:5px solid #00d084; }
.aqi-sat { border-left:5px solid #b9d83d; }
.aqi-mod { border-left:5px solid #ffd166; }
.aqi-poor { border-left:5px solid #ff9f43; }
.aqi-vpoor { border-left:5px solid #ff5b63; }
.aqi-severe { border-left:5px solid #a855f7; }
.chatbox { background:#0b0b0b; border:1px solid #292929; border-radius:16px; padding:18px; }
.source-live { color:#00d084; font-weight:700; }
.source-demo { color:#ffb347; font-weight:700; }
</style>
""", unsafe_allow_html=True)

def season_now(month):
    if month in [3,4,5]: return "Summer", "MARCH — MAY"
    if month in [6,7,8,9]: return "Monsoon", "JUNE — SEPTEMBER"
    if month in [10,11]: return "Post-Monsoon", "OCTOBER — NOVEMBER"
    return "Winter", "DECEMBER — FEBRUARY"

def aqi_class(cat):
    return {
        "Good":"aqi-good","Satisfactory":"aqi-sat","Moderately Polluted":"aqi-mod",
        "Poor":"aqi-poor","Very Poor":"aqi-vpoor","Severe":"aqi-severe"
    }.get(cat,"aqi-sat")

def fmt(v, unit="", decimals=1):
    if v is None:
        return "—"
    try:
        return f"{float(v):.{decimals}f}{unit}"
    except Exception:
        return str(v)

# Session state
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "used_answers" not in st.session_state:
    st.session_state.used_answers = set()
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0.0

with st.sidebar:
    st.markdown("## 🌬️ AIR QUALITY")
    st.markdown("### LEVEL PREDICTOR")
    st.caption("TEAM SYNAPSE • LIVE AI COMMAND CENTER")
    st.divider()
    selected_name = st.selectbox("Select city", [c["name"] for c in CITIES])
    uploaded = st.file_uploader("Upload your AQI CSV", type=["csv"])
    auto_refresh = st.checkbox("🔄 Auto-refresh live data", value=True)
    refresh = st.button("↻ Refresh now", use_container_width=True)
    page = st.radio(
        "AIR INTELLIGENCE",
        [
            "🏠 Air Command Center", "🗺️ Live Air Map", "🔮 AI Forecast",
            "📊 Pollution Analytics", "🔬 AI & ML Intelligence",
            "🔎 Anomaly & Spike Intelligence", "🚨 Alert Center",
            "🧮 AQI Calculator", "📍 Location Hub", "📄 Reports & Export",
            "🤖 Air AI Assistant", "ℹ️ About & Team"
        ],
    )
    st.divider()
    st.caption("SYSTEM STATUS")
    st.success("● Air Data: ONLINE" if st.session_state.last_refresh else "● Air Data: CONNECTING")
    st.info("● Weather: LIVE API + FALLBACK")
    st.info("● ML Engine: ONLINE")

city = get_city(selected_name)

# Fetch live bundle. Cache for 60 seconds so the chatbot and dashboard use the same snapshot.
@st.cache_data(ttl=300, show_spinner=False)
def get_bundle(city_name):
    return fetch_live_bundle(get_city(city_name))

@st.cache_data(ttl=300, show_spinner=False)
def get_national_snapshot():
    """Fetch city AQI values only when a national comparison is actually needed."""
    rows = []
    for c in CITIES:
        b = get_bundle(c["name"])
        lp = live_pollutants_as_project_keys(b)
        rr = calculate_aqi(lp if lp else c["pollutants"])
        rows.append({"city": c["name"], "aqi": rr["aqi"]})
    return rows

if refresh:
    get_bundle.clear()
    st.rerun()

bundle = get_bundle(selected_name)
current = extract_current(bundle)
live_pollutants = live_pollutants_as_project_keys(bundle)
forecast_weather = forecast_dataframe(bundle)
hourly_weather = hourly_weather_dataframe(bundle)

# Use live air values when available; otherwise demo city values.
if live_pollutants and all(v is not None for v in live_pollutants.values()):
    active_pollutants = live_pollutants
    source_label = "LIVE API DATA"
    source_class = "source-live"
else:
    active_pollutants = city["pollutants"]
    source_label = "DEMO FALLBACK DATA"
    source_class = "source-demo"

result = calculate_aqi(active_pollutants)
alerts = generate_alerts(city, result)
season, season_months = season_now(datetime.now().month)

# Use live weather for display, otherwise built-in project weather.
weather = current or {
    "temperature": city["weather"]["temperature"],
    "humidity": city["weather"]["humidity"],
    "wind_speed": city["weather"]["windSpeed"],
    "wind_direction": None,
    "weather_code": None,
}
weather_desc = bundle.get("description", "Live weather unavailable")
weather_icon = bundle.get("weather_icon", "🌍")

st.markdown(
    f"""
<div class="hero">
  <div class="eyebrow">● AIR QUALITY LEVEL PREDICTOR • AI COMMAND CENTER</div>
  <div style="color:#777;font-size:.72rem;margin:5px 0 18px;">BY TEAM SYNAPSE</div>
  <h1>{city['name']}, <span style="color:#999">{city['state']}</span></h1>
  <div style="color:#777;margin-top:6px;">{city['description']}</div>
  <div style="margin-top:14px;color:#888;">
    📍 Station: <b>{city['stationName']}</b>
    &nbsp; • &nbsp; Coordinates: {city['lat']:.4f}° N, {city['lng']:.4f}° E
  </div>
  <div style="margin-top:14px;"><span class="{source_class}">● {source_label}</span>
  &nbsp; • &nbsp; Last synchronized: {bundle['fetched_at']}</div>
</div>
""",
    unsafe_allow_html=True,
)

# Live telemetry
now = datetime.now().astimezone()
st.markdown("### <span class='live-dot'>●</span> LIVE TEMPORAL & METEOROLOGICAL TELEMETRY", unsafe_allow_html=True)
t1,t2,t3,t4 = st.columns(4)
cards = [
    (t1,"CURRENT TIME",now.strftime("%H:%M:%S"),"LIVE • "+now.strftime("%I:%M:%S %p")),
    (t2,"CURRENT DATE",now.strftime("%d %B %Y"),now.strftime("%A")),
    (t3,"TIMEZONE",now.tzname() or "IST","UTC+05:30 • India Standard Time"),
    (t4,"CURRENT SEASON",f"{season} {weather_icon}",season_months),
]
for col,label,value,sub in cards:
    col.markdown(
        f"<div class='telemetry'><div class='label'>{label}</div><div class='value'>{value}</div><div style='color:#777;font-size:.75rem;margin-top:6px'>{sub}</div></div>",
        unsafe_allow_html=True
    )

st.markdown(
    f"**{weather_icon} Weather now:** {weather_desc} • "
    f"Temperature **{fmt(weather.get('temperature'),'°C')}** • "
    f"Humidity **{fmt(weather.get('humidity'),'% ',0)}** • "
    f"Wind **{fmt(weather.get('wind_speed'),' km/h')}** • "
    f"Pressure **{fmt(weather.get('pressure'),' hPa')}**"
)

# AQI level legend with colors
st.markdown("### 🎨 AIR QUALITY LEVELS")
legend = st.columns(6)
levels = [
    ("Good","0–50","🟢"),("Satisfactory","51–100","🟡"),
    ("Moderately Polluted","101–200","🟠"),("Poor","201–300","🔴"),
    ("Very Poor","301–400","🟣"),("Severe","401–500","⚫")
]
for col,(name,rng,emoji) in zip(legend,levels):
    col.markdown(f"<div class='panel' style='text-align:center'><b>{emoji} {name}</b><br><span style='color:#888'>{rng}</span></div>", unsafe_allow_html=True)

if page == "🏠 Air Command Center":
    left,right = st.columns([2.1,1])
    with left:
        st.markdown(f"<div class='panel {aqi_class(result['category'])}'><div class='eyebrow'>CURRENT AIR QUALITY</div><div style='font-size:4rem;font-weight:900'>{result['aqi']}</div><div style='font-size:1.3rem;font-weight:800'>{result['category']}</div><div style='color:#aaa;margin-top:8px'>Dominant pollutant: <b>{result['dominant'].upper()}</b></div><div style='color:#aaa;margin-top:10px'>{result['health']}</div></div>", unsafe_allow_html=True)
    with right:
        st.markdown("#### 🌬️ Live pollutants")
        for key,label,unit in [("pm25","PM2.5","µg/m³"),("pm10","PM10","µg/m³"),("no2","NO₂","µg/m³"),("so2","SO₂","µg/m³"),("co","CO","mg/m³"),("o3","O₃","µg/m³")]:
            st.metric(label, fmt(active_pollutants.get(key),f" {unit}"))

    st.subheader("📈 AQI & pollutant intelligence")
    c1,c2 = st.columns(2)
    with c1:
        sub = pd.DataFrame(result["subindices"])
        fig = px.bar(sub, x="name", y="sub_index", color="category", text="sub_index", title="CPCB pollutant sub-indices")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        trend = city["trend24h"]
        fig = px.line(x=list(range(1,len(trend)+1)), y=trend, markers=True, labels={"x":"Recent hour","y":"AQI"}, title="AQI trend")
        st.plotly_chart(fig, use_container_width=True)

elif page == "🗺️ Live Air Map":
    st.subheader("🗺️ India AQI Monitoring Map")
    # Do not hit 21 external APIs merely because the user changed pages.
    # The map starts instantly from the project's city snapshot; a user can
    # request the live national refresh explicitly.
    use_live_map = st.checkbox("Fetch live AQI for all monitored cities", value=False)
    if use_live_map:
        map_df = pd.DataFrame([
            {"city": r["city"], "AQI": r["aqi"]}
            for r in get_national_snapshot()
        ])
        city_meta = pd.DataFrame([
            {"city": c["name"], "state": c["state"], "lat": c["lat"], "lon": c["lng"]}
            for c in CITIES
        ])
        map_df = city_meta.merge(map_df, on="city", how="left")
        map_df["level"] = map_df["AQI"].apply(lambda x: calculate_aqi({"pm25": x, "pm10": x})["category"] if pd.notna(x) else "Unknown")
    else:
        rows=[]
        for c in CITIES:
            rr=calculate_aqi(c["pollutants"])
            rows.append({"city":c["name"],"state":c["state"],"lat":c["lat"],"lon":c["lng"],"AQI":rr["aqi"],"level":rr["category"]})
        map_df=pd.DataFrame(rows)
    fig=px.scatter_map(map_df,lat="lat",lon="lon",size="AQI",color="AQI",hover_name="city",hover_data=["state","level"],zoom=4.2,height=620)
    fig.update_layout(map_style="open-street-map")
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(map_df.sort_values("AQI",ascending=False),use_container_width=True,hide_index=True)

elif page == "🔮 AI Forecast":
    st.subheader("🌦️ Live Weather Forecast")
    if len(forecast_weather):
        cols=st.columns(min(7,len(forecast_weather)))
        for col,(_,r) in zip(cols,forecast_weather.iterrows()):
            col.markdown(f"<div class='panel' style='text-align:center'><div style='font-size:1.7rem'>{r['icon']}</div><b>{r['date'].strftime('%a')}</b><br>{r['min_temp']:.0f}° / {r['max_temp']:.0f}°C<br><span style='color:#49a6ff'>🌧️ {r['rain_probability']:.0f}%</span><br><span style='color:#777'>{r['description']}</span></div>",unsafe_allow_html=True)
        fig=px.line(forecast_weather,x="date",y=["min_temp","max_temp"],markers=True,title="7-day temperature forecast")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(forecast_weather,use_container_width=True,hide_index=True)
    else:
        st.warning("Live weather forecast is unavailable; the app is using fallback data.")

    st.subheader("🤖 ML AQI forecast")
    try:
        df=fill_missing_with_demo(demo_dataframe(city,720),city)
        fc,metrics=forecast_aqi(df,24)
        st.caption(f"{metrics['algorithm']} • MAE {metrics['MAE']:.2f} • RMSE {metrics['RMSE']:.2f} • R² {metrics['R2']:.3f}")
        fig=px.line(fc,x="datetime",y="predicted_aqi",markers=True,title="24-hour predicted AQI")
        st.plotly_chart(fig,use_container_width=True)
    except Exception as exc:
        st.warning(f"ML forecast unavailable: {exc}")

elif page == "📊 Pollution Analytics":
    st.subheader("📊 Pollution Analytics & EDA")
    if uploaded:
        try: source_df=fill_missing_with_demo(load_csv(uploaded),city)
        except Exception as e: st.error(str(e)); source_df=demo_dataframe(city,720)
    else:
        source_df=demo_dataframe(city,720)
    st.dataframe(source_df.tail(100),use_container_width=True,hide_index=True)
    c1,c2=st.columns(2)
    with c1:
        fig=px.line(source_df.tail(200),x="datetime",y=["pm25","pm10","no2","so2","o3"],title="Pollutant time series")
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        corr=source_df[["humidity","no2","co","so2","pm25","pm10","o3","temperature"]].corr()
        fig=px.imshow(corr,text_auto=".2f",title="Correlation matrix")
        st.plotly_chart(fig,use_container_width=True)

elif page == "🔬 AI & ML Intelligence":
    st.subheader("🔬 AI & ML Intelligence")
    df=fill_missing_with_demo(demo_dataframe(city,720),city)
    try:
        model,metrics,engineered=train_aqi_model(df)
        a,b,c,d=st.columns(4)
        a.metric("Model",metrics["algorithm"]); b.metric("MAE",f"{metrics['MAE']:.2f}"); c.metric("RMSE",f"{metrics['RMSE']:.2f}"); d.metric("R²",f"{metrics['R2']:.3f}")
        if hasattr(model,"feature_importances_"):
            imp=pd.DataFrame({"feature":metrics["features"],"importance":model.feature_importances_}).sort_values("importance",ascending=False)
            st.plotly_chart(px.bar(imp.head(15),x="importance",y="feature",orientation="h",title="Feature importance"),use_container_width=True)
    except Exception as exc: st.error(str(exc))

elif page == "🔎 Anomaly & Spike Intelligence":
    st.subheader("🔎 Isolation Forest")
    df=fill_missing_with_demo(demo_dataframe(city,720),city)
    try:
        _,adf=isolation_forest_analysis(df)
        st.metric("Anomalies detected",int(adf["is_anomaly"].sum()))
        st.plotly_chart(px.scatter(adf.reset_index(),x="index",y="anomaly_score",color="is_anomaly",title="Anomaly score"),use_container_width=True)
        st.dataframe(pd.DataFrame(pollutant_spikes(city)),use_container_width=True,hide_index=True)
    except Exception as exc: st.error(str(exc))

elif page == "🚨 Alert Center":
    st.subheader("🚨 Alert Center")
    if not alerts: st.success("No active AQI alerts for this city.")
    for sev,title,msg in alerts:
        if sev=="CRITICAL": st.error(f"🚨 **{title}** — {msg}")
        elif sev=="WARNING": st.warning(f"⚠️ **{title}** — {msg}")
        else: st.info(f"ℹ️ **{title}** — {msg}")
    national=all_national_alerts(CITIES,lambda p:calculate_aqi(p))
    st.dataframe(pd.DataFrame(national),use_container_width=True,hide_index=True)

elif page == "🧮 AQI Calculator":
    st.subheader("🧮 CPCB AQI Calculator")
    vals={}
    cols=st.columns(4)
    for i,key in enumerate(["pm25","pm10","no2","so2","co","o3","nh3","pb"]):
        vals[key]=cols[i%4].number_input(key.upper(),min_value=0.0,value=float(active_pollutants.get(key,0) or 0),step=.1)
    r=calculate_aqi(vals)
    st.markdown(f"<div class='panel {aqi_class(r['category'])}'><h1>{r['aqi']}</h1><b>{r['category']}</b><br>Dominant: {r['dominant'].upper()}</div>",unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(r["subindices"]),use_container_width=True,hide_index=True)

elif page == "📍 Location Hub":
    st.subheader(f"📍 {city['name']}, {city['state']}")
    st.write(city["description"])
    st.map(pd.DataFrame({"lat":[city["lat"]],"lon":[city["lng"]]}),zoom=10)
    st.write(f"Station: **{city['stationName']}**")

elif page == "📄 Reports & Export":
    st.subheader("📄 Reports & Export")
    report=pd.DataFrame([{"City":city["name"],"State":city["state"],"AQI":result["aqi"],"AQI Level":result["category"],"Dominant":result["dominant"],**active_pollutants}])
    st.dataframe(report,use_container_width=True,hide_index=True)
    st.download_button("⬇️ Download AQI report",report.to_csv(index=False),"aqi_report.csv","text/csv")

elif page == "🤖 Air AI Assistant":
    st.subheader("🤖 Air AI Assistant")
    st.caption("Ask naturally — not just the suggested questions. Answers are grounded in the current dashboard data.")
    st.info("⚡ Fast mode: page changes use cached live data. Full multi-city live refresh happens only when you request it.")

    # Suggestion buttons
    suggestions=[
        "👋 Hi",
        "🌬️ What is the current AQI?",
        "🌡️ What is the temperature and wind speed?",
        "🧪 Which pollutants are high?",
        "🌦️ What is the weather forecast?",
        "❤️ Is it safe to exercise outside?",
        "🚨 Are there any alerts?",
        "🔎 Are there any pollution spikes?",
    ]
    st.markdown("**💡 Suggested questions**")
    cols=st.columns(4)
    for i,s in enumerate(suggestions):
        if cols[i%4].button(s,key=f"suggestion_{i}",use_container_width=True):
            st.session_state.pending_question=s[2:].strip()
            st.rerun()

    if "pending_question" in st.session_state:
        q=st.session_state.pop("pending_question")
        st.session_state.chat_messages.append(("user",q))
        # Most chatbot questions only need the selected city's current snapshot.
        # National data are fetched lazily only when the user asks for a city comparison.
        national = get_national_snapshot() if any(k in q.lower() for k in ["city", "cities", "highest", "lowest"]) else []
        ans,_=answer_user(q,city,current,active_pollutants,forecast_weather,season,national,st.session_state.used_answers)
        st.session_state.chat_messages.append(("assistant",ans))

    for role,msg in st.session_state.chat_messages:
        with st.chat_message(role):
            st.markdown(msg)

    q=st.chat_input("Ask Air AI anything about AQI, pollutants, weather, health, forecast, alerts...")
    if q:
        st.session_state.chat_messages.append(("user",q))
        # Most chatbot questions only need the selected city's current snapshot.
        # National data are fetched lazily only when the user asks for a city comparison.
        national = get_national_snapshot() if any(k in q.lower() for k in ["city", "cities", "highest", "lowest"]) else []
        ans,_=answer_user(q,city,current,active_pollutants,forecast_weather,season,national,st.session_state.used_answers)
        st.session_state.chat_messages.append(("assistant",ans))

    if st.button("🗑️ Clear chat"):
        st.session_state.chat_messages=[]
        st.session_state.used_answers=set()
        st.rerun()

elif page == "ℹ️ About & Team":
    st.subheader("ℹ️ About & Team")
    st.markdown("""
### Air Quality Level Predictor

A Python + Streamlit air-intelligence dashboard combining:

- **Live weather:** Open-Meteo forecast service
- **Live pollutant data:** Open-Meteo air-quality service
- **CPCB-style AQI calculation**
- **XGBoost / Random Forest** AQI prediction
- **Isolation Forest** anomaly detection
- **Interactive Air AI Assistant**
- **CSV upload and report export**
- **Automatic fallback data** when internet/API services are unavailable

### Accuracy and transparency

The dashboard labels live API data separately from demo fallback data. Weather and air-quality API values are model/service data and should not be described as direct CPCB station measurements unless a CPCB/APPCB feed is actually connected.
""")

# Auto refresh: Streamlit rerun after 60 seconds so the live clock/data stays fresh.
if auto_refresh:
    elapsed=time.time()-st.session_state.last_refresh
    if elapsed > 60:
        st.session_state.last_refresh=time.time()
        st.rerun()
