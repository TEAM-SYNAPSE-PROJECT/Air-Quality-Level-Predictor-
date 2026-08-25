"""
Location Intelligence & Indian Geospatial Engine.
Manages city lookup, GPS coordinate matching, state catalogs, reverse geocoding,
and Haversine distance calculations to the nearest continuous monitoring stations.
"""
import json
import os
import math
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional

# In-memory cache for reverse geocoding to avoid repetitive HTTP calls
_REVERSE_GEOCODE_CACHE: Dict[str, Dict[str, Any]] = {}

def load_indian_cities() -> List[Dict[str, Any]]:
    """Loads all Indian monitoring locations with coordinates and metadata."""
    meta_path = "data/indian_cities_metadata.json"
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("cities", [])
        except Exception:
            pass
    return []

def get_states_and_cities() -> Dict[str, List[Dict[str, Any]]]:
    """Groups cities by Indian state / union territory."""
    cities = load_indian_cities()
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for c in cities:
        state = c.get("state", "India")
        if state not in grouped:
            grouped[state] = []
        grouped[state].append(c)
    return grouped

def calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes exact great-circle distance between two GPS coordinate pairs in kilometers using the Haversine formula.
    """
    R = 6371.0088  # Mean Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_compass_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
    """Calculates compass heading from origin (lat1, lon1) to destination (lat2, lon2)."""
    dlon = math.radians(lon2 - lon1)
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    y = math.sin(dlon) * math.cos(lat2_r)
    x = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dlon)
    initial_bearing = math.degrees(math.atan2(y, x))
    compass_bearing = (initial_bearing + 360) % 360
    
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int((compass_bearing + 11.25) / 22.5) % 16
    return directions[idx]

def reverse_geocode_coordinates(lat: float, lon: float) -> Dict[str, Any]:
    """
    Performs real-world reverse geocoding via OpenStreetMap Nominatim and BigDataCloud.
    Extracts City, District, State, Country, Postal Code, and Neighbourhood.
    Falls back gracefully to nearest Indian geographic center if offline.
    """
    cache_key = f"{round(lat, 4)}_{round(lon, 4)}"
    if cache_key in _REVERSE_GEOCODE_CACHE:
        return _REVERSE_GEOCODE_CACHE[cache_key]
        
    result = {
        "city": "",
        "district": "",
        "state": "",
        "country": "India",
        "postcode": "",
        "suburb": "",
        "formatted_address": "",
        "latitude": lat,
        "longitude": lon,
        "is_geocoded": False
    }
    
    # Try BigDataCloud Client API (fast & highly reliable for client coordinates)
    try:
        url_bdc = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en"
        req = urllib.request.Request(url_bdc, headers={"User-Agent": "AirQualityIntelligence/2.0"})
        with urllib.request.urlopen(req, timeout=3.5) as response:
            data = json.loads(response.read().decode("utf-8"))
            city = data.get("city") or data.get("locality") or ""
            state = data.get("principalSubdivision") or ""
            country = data.get("countryName") or "India"
            postcode = data.get("postcode") or ""
            
            if city or state:
                result["city"] = city
                result["state"] = state
                result["country"] = country
                result["postcode"] = postcode
                result["is_geocoded"] = True
    except Exception:
        pass
        
    # Try Nominatim if city or district is still missing
    if not result["city"] or not result["state"]:
        try:
            url_nom = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            req = urllib.request.Request(url_nom, headers={"User-Agent": "AirQualityIntelligenceApp/2.0 (contact: support@airquality.in)"})
            with urllib.request.urlopen(req, timeout=4.0) as response:
                data = json.loads(response.read().decode("utf-8"))
                addr = data.get("address", {})
                city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("municipality") or addr.get("county") or ""
                district = addr.get("state_district") or addr.get("county") or addr.get("district") or ""
                state = addr.get("state") or ""
                country = addr.get("country") or "India"
                suburb = addr.get("suburb") or addr.get("neighbourhood") or addr.get("residential") or ""
                postcode = addr.get("postcode") or ""
                
                result["city"] = city or result["city"]
                result["district"] = district or result["district"]
                result["state"] = state or result["state"]
                result["country"] = country or result["country"]
                result["suburb"] = suburb or result["suburb"]
                result["postcode"] = postcode or result["postcode"]
                result["formatted_address"] = data.get("display_name", "")
                result["is_geocoded"] = True
        except Exception:
            pass

    # If geocoding failed or returned empty values, find closest Indian station for intelligent defaults
    nearest_station = find_nearest_monitoring_station(lat, lon)
    if not result["city"]:
        result["city"] = nearest_station["city"]
    if not result["state"]:
        result["state"] = nearest_station["state"]
    if not result["district"]:
        result["district"] = nearest_station.get("district", result["city"])
        
    _REVERSE_GEOCODE_CACHE[cache_key] = result
    return result

def find_nearest_monitoring_station(lat: float, lon: float) -> Dict[str, Any]:
    """
    Computes precise Haversine distance to find the closest valid continuous Indian air quality monitoring station.
    Returns station metadata, coordinates, distance in km, and compass bearing.
    """
    cities = load_indian_cities()
    if not cities:
        return {
            "city": "Delhi",
            "state": "Delhi",
            "district": "Central Delhi",
            "station": "Anand Vihar, Delhi - DPCC",
            "lat": 28.6139,
            "lon": 77.2090,
            "distance_km": round(calculate_haversine_distance_km(lat, lon, 28.6139, 77.2090), 1),
            "bearing": calculate_compass_bearing(lat, lon, 28.6139, 77.2090)
        }
        
    closest_station = None
    min_dist = float("inf")
    
    for c in cities:
        st_lat = c.get("lat")
        st_lon = c.get("lon")
        if st_lat is not None and st_lon is not None:
            dist = calculate_haversine_distance_km(lat, lon, float(st_lat), float(st_lon))
            if dist < min_dist:
                min_dist = dist
                closest_station = c
                
    if closest_station is None:
        closest_station = cities[0]
        min_dist = calculate_haversine_distance_km(lat, lon, closest_station["lat"], closest_station["lon"])
        
    bearing = calculate_compass_bearing(lat, lon, closest_station["lat"], closest_station["lon"])
    
    return {
        "city": closest_station["city"],
        "state": closest_station["state"],
        "district": closest_station.get("district", closest_station["city"]),
        "station": closest_station.get("station", f"{closest_station['city']} Continuous Ambient Station"),
        "lat": float(closest_station["lat"]),
        "lon": float(closest_station["lon"]),
        "distance_km": round(min_dist, 1),
        "bearing": bearing
    }

def get_city_details(city_name: str) -> Optional[Dict[str, Any]]:
    """Retrieves full coordinate and station metadata for a specific Indian city."""
    cities = load_indian_cities()
    for c in cities:
        if c.get("city", "").lower() == city_name.lower():
            return c
    return None
