"""
Central API Infrastructure & Client Manager.
Enforces unified timeout, retry policies, response caching, error resilience,
and data provenance tracking (LIVE / CACHED / LOCAL DATA / DEMO).
"""
import os
import time
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Central Configuration
CONFIG = {
    "USE_LIVE_API": os.getenv("USE_LIVE_API", "true").lower() == "true",
    "CACHE_TTL_SECONDS": int(os.getenv("CACHE_TTL_SECONDS", "900")),
    "TIMEOUT_SECONDS": 5,
    "MAX_RETRIES": 2,
    "BACKOFF_FACTOR": 0.5,
    "USER_AGENT": "AirQualityIntelligencePlatform/1.0 (Environmental Research)"
}

# Simple In-Memory Timestamped Cache
_API_CACHE: Dict[str, Dict[str, Any]] = {}

def get_cached_response(cache_key: str) -> Optional[Any]:
    """Retrieves cached payload if within TTL."""
    if cache_key in _API_CACHE:
        entry = _API_CACHE[cache_key]
        if time.time() - entry["timestamp"] < CONFIG["CACHE_TTL_SECONDS"]:
            return entry["data"]
    return None

def set_cached_response(cache_key: str, data: Any):
    """Stores payload in in-memory cache with current epoch."""
    _API_CACHE[cache_key] = {
        "timestamp": time.time(),
        "data": data
    }

def make_resilient_request(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    cache_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes an HTTP GET with retry, timeout, caching, and fallback transparency.
    """
    if cache_key:
        cached = get_cached_response(cache_key)
        if cached is not None:
            return {"status": "CACHED", "data": cached, "error": None}
            
    if not CONFIG["USE_LIVE_API"]:
        return {"status": "LOCAL_DATA", "data": None, "error": "Live API disabled in configuration"}
        
    req_headers = {"User-Agent": CONFIG["USER_AGENT"]}
    if headers:
        req_headers.update(headers)
        
    retries = 0
    last_error = None
    
    while retries <= CONFIG["MAX_RETRIES"]:
        try:
            resp = requests.get(
                url,
                params=params,
                headers=req_headers,
                timeout=CONFIG["TIMEOUT_SECONDS"]
            )
            if resp.status_code == 200:
                data = resp.json()
                if cache_key:
                    set_cached_response(cache_key, data)
                return {"status": "LIVE", "data": data, "error": None}
            else:
                last_error = f"HTTP {resp.status_code}: {resp.text[:120]}"
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            
        retries += 1
        if retries <= CONFIG["MAX_RETRIES"]:
            time.sleep(CONFIG["BACKOFF_FACTOR"] * (2 ** (retries - 1)))
            
    # Check if stale cached data exists for graceful degradation
    if cache_key and cache_key in _API_CACHE:
        return {
            "status": "RECENT",
            "data": _API_CACHE[cache_key]["data"],
            "error": f"Live query failed ({last_error}); serving cached snapshot."
        }
        
    return {"status": "FALLBACK", "data": None, "error": last_error}
