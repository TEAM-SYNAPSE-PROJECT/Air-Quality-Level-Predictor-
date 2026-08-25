"""
Geospatial Map Visualizers & India Air Quality Risk Mapping.
Renders interactive Folium and Plotly maps with color-coded monitoring stations,
live user GPS position markers, and proximity vectors to nearest air quality sensors.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium
from utils.helpers import get_aqi_category_info

AQI_HEX_COLORS = {
    "Good": "#10b981",
    "Satisfactory": "#34d399",
    "Moderate": "#c5a368",
    "Poor": "#eab308",
    "Very Poor": "#f97316",
    "Severe": "#ef4444"
}

def create_folium_air_quality_map(
    df_cities: pd.DataFrame,
    user_lat: float = 28.6139,
    user_lon: float = 77.2090,
    user_city: str = "Detected Location",
    user_state: str = "India",
    is_live_gps: bool = False,
    nearest_station: dict = None,
    station_aqi: int = None,
    station_aqi_cat: str = "Moderate",
    zoom_start: int = 7
) -> folium.Map:
    """
    Constructs an interactive Folium map centered on the user's detected location.
    Renders 'YOU ARE HERE' marker, the nearest air monitoring station, a proximity line,
    and all continuous ambient monitoring stations with color-coded AQI circles.
    """
    # Create Base Map with Dark CartoDB Tiles
    m = folium.Map(
        location=[user_lat, user_lon],
        zoom_start=zoom_start,
        tiles="CartoDB dark_matter",
        prefer_canvas=True
    )
    
    status_tag = "🟢 LIVE GPS POSITION" if is_live_gps else "📍 ACTIVE LOCATION"
    
    # 1. Add User Location Marker (📍 YOU ARE HERE)
    user_popup_html = f"""
    <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 12px; min-width: 200px; color: #0f172a; padding: 4px;">
        <div style="font-weight: 800; font-size: 14px; color: #10B981; margin-bottom: 2px;">📍 YOU ARE HERE</div>
        <div style="font-size: 13px; font-weight: 700; color: #1e293b;">{user_city}, {user_state}</div>
        <div style="font-size: 11px; color: #64748b; margin-top: 4px;">
            Latitude: <b>{user_lat:.6f}°N</b><br/>
            Longitude: <b>{user_lon:.6f}°E</b>
        </div>
        <div style="margin-top: 6px; font-size: 10px; background: #ecfdf5; color: #059669; padding: 2px 6px; border-radius: 4px; font-weight: 700; display: inline-block;">
            {status_tag}
        </div>
    </div>
    """
    
    folium.Marker(
        location=[user_lat, user_lon],
        popup=folium.Popup(user_popup_html, max_width=280),
        tooltip=f"📍 YOU ARE HERE ({user_city})",
        icon=folium.Icon(color="green" if is_live_gps else "blue", icon="user", prefix="fa")
    ).add_to(m)
    
    # Accuracy / presence radius circle
    folium.Circle(
        location=[user_lat, user_lon],
        radius=1200, # 1.2km radius
        color="#10B981" if is_live_gps else "#C5A368",
        fill=True,
        fill_color="#10B981" if is_live_gps else "#C5A368",
        fill_opacity=0.12,
        weight=1.5
    ).add_to(m)
    
    # 2. Add Nearest Monitoring Station & Connection Line if available
    if nearest_station:
        st_lat = nearest_station.get("lat")
        st_lon = nearest_station.get("lon")
        st_name = nearest_station.get("station", "Continuous Ambient Station")
        st_dist = nearest_station.get("distance_km", 0.0)
        
        if st_lat is not None and st_lon is not None:
            cat_info = get_aqi_category_info(station_aqi or 100)
            
            st_popup_html = f"""
            <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 12px; min-width: 220px; color: #0f172a; padding: 4px;">
                <div style="font-weight: 800; font-size: 13px; color: {cat_info['color']}; margin-bottom: 2px;">
                    🌫️ NEAREST MONITORING STATION
                </div>
                <div style="font-size: 12px; font-weight: 700; color: #1e293b;">{st_name}</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px;">
                    Distance from You: <b style="color: #0f172a;">{st_dist} km</b><br/>
                    Station Coordinates: {st_lat:.4f}°N, {st_lon:.4f}°E
                </div>
                <div style="margin-top: 6px; padding: 4px 8px; background: {cat_info['color']}22; border-radius: 4px;">
                    <span style="font-weight: 800; color: {cat_info['color']}; font-size: 14px;">AQI {station_aqi or '--'}</span>
                    <span style="font-size: 11px; color: {cat_info['color']}; font-weight: 700;"> • {station_aqi_cat.upper()}</span>
                </div>
            </div>
            """
            
            folium.Marker(
                location=[st_lat, st_lon],
                popup=folium.Popup(st_popup_html, max_width=300),
                tooltip=f"🌫️ Nearest Station: {st_name} ({st_dist} km)",
                icon=folium.Icon(color="red" if (station_aqi or 0) > 200 else "orange", icon="dashboard", prefix="fa")
            ).add_to(m)
            
            # Connect user GPS to station with dashed proximity line
            if st_dist > 0.05:
                folium.PolyLine(
                    locations=[[user_lat, user_lon], [st_lat, st_lon]],
                    color="#C5A368",
                    weight=2,
                    dash_array="6, 6",
                    opacity=0.8,
                    tooltip=f"Distance to Sensor: {st_dist} km"
                ).add_to(m)
                
    # 3. Add All Regional / National Monitoring Stations
    for _, row in df_cities.iterrows():
        lat = row.get("latitude")
        lon = row.get("longitude")
        if pd.isna(lat) or pd.isna(lon):
            continue
            
        city = row.get("city", "N/A")
        state = row.get("state", "N/A")
        aqi = int(row.get("aqi", 100))
        cat = row.get("aqi_category", "Moderate")
        dom = row.get("dominant_pollutant", "PM2.5")
        pm25 = row.get("pm25", "N/A")
        pm10 = row.get("pm10", "N/A")
        temp = row.get("temperature", "N/A")
        time_u = row.get("timestamp", "")
        
        cat_info = get_aqi_category_info(aqi)
        color = cat_info["color"]
        
        popup_html = f"""
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 12px; min-width: 190px; color: #0f172a; padding: 2px;">
            <div style="font-weight: 800; font-size: 14px; color: {color};">{city}, {state}</div>
            <div style="margin: 4px 0; font-size: 13px;"><b>AQI: {aqi}</b> ({cat.upper()})</div>
            <hr style="margin: 4px 0; border: 0.5px solid #cbd5e1;"/>
            <div>• Dominant Factor: <b>{dom}</b></div>
            <div>• PM2.5: <b>{pm25} µg/m³</b></div>
            <div>• PM10: <b>{pm10} µg/m³</b></div>
            <div>• Ambient Temp: <b>{temp} °C</b></div>
            <div style="font-size: 10px; color: #64748b; margin-top: 4px;">Data Timestamp: {time_u}</div>
        </div>
        """
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=6 + min(12, aqi / 40),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.75,
            weight=1.5,
            tooltip=f"{city}: AQI {aqi} ({cat})",
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)
        
    return m

def create_plotly_india_risk_map(df_cities: pd.DataFrame, selected_city: str = None) -> go.Figure:
    """
    Renders high-speed Plotly Scatter Mapbox visualization of India-wide air pollution stations.
    """
    df_map = df_cities.copy()
    
    fig = px.scatter_mapbox(
        df_map,
        lat="latitude",
        lon="longitude",
        color="aqi_category",
        color_discrete_map=AQI_HEX_COLORS,
        size="aqi",
        size_max=18,
        hover_name="city",
        hover_data={
            "state": True,
            "aqi": True,
            "aqi_category": True,
            "dominant_pollutant": True,
            "pm25": True,
            "temperature": True,
            "latitude": False,
            "longitude": False
        },
        zoom=4.2,
        center={"lat": 22.5937, "lon": 78.9629},
        mapbox_style="carto-darkmatter"
    )
    
    # Highlight selected city if provided
    if selected_city:
        sel_row = df_map[df_map["city"].str.lower() == selected_city.lower()]
        if not sel_row.empty:
            r = sel_row.iloc[0]
            fig.add_trace(go.Scattermapbox(
                lat=[r["latitude"]],
                lon=[r["longitude"]],
                mode="markers+text",
                marker=dict(size=24, color="#C5A368", opacity=0.9),
                text=[f"📍 {r['city']}"],
                textposition="top right",
                textfont=dict(family="Plus Jakarta Sans", size=12, color="#F5F5F5"),
                name="Selected City"
            ))
            
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=520,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.02,
            xanchor="center",
            x=0.5,
            bgcolor="#111111",
            bordercolor="#222222",
            borderwidth=1,
            font=dict(color="#F5F5F5", size=10, family="Plus Jakarta Sans")
        )
    )
    return fig
