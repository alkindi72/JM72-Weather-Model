import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import requests
import math

# ==========================================
# 1. JM72 ADVANCED DYNAMIC CONFIG
# ==========================================
st.set_page_config(page_title="JM72 AI Weather Model", layout="wide")
st_autorefresh(interval=15 * 60 * 1000, key="data_refresh")

# 

# ==========================================
# 2. STABLE REST-API DATA AGENT
# ==========================================
stations = {
    "Al Hajar Mountains": {"lat": 25.3, "lon": 56.1, "type": "Mountains"},
    "Fujairah Coast": {"lat": 25.12, "lon": 56.32, "type": "Mountains"},
    "Al Ain": {"lat": 24.19, "lon": 55.76, "type": "Inland"},
    "Al Dhafra": {"lat": 23.65, "lon": 53.70, "type": "Desert"},
    "Abu Dhabi": {"lat": 24.45, "lon": 54.37, "type": "Coast"}
}

@st.cache_data(ttl=3600)
def fetch_stable_live_data():
    try:
        lats = ",".join([str(s["lat"]) for s in stations.values()])
        lons = ",".join([str(s["lon"]) for s in stations.values()])
        # Added relative humidity to API request for strict filtering
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly=temperature_2m,cape,winddirection_10m,relative_humidity_700hPa&models=gfs_seamless&timezone=auto"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        return False, str(e)

# ==========================================
# 3. JM72 AI DYNAMICS ENGINE (STRICT FILTER)
# ==========================================
weather_data = []
fetch_success, live_data = fetch_stable_live_data()

if fetch_success and type(live_data) is list:
    for idx, (name, coords) in enumerate(stations.items()):
        station_data = live_data[idx]["hourly"]
        for i in range(len(station_data["time"])):
            dt = datetime.fromisoformat(station_data["time"][i])
            
            temp_c = station_data["temperature_2m"][i] or 35.0
            cape = station_data["cape"][i] or 0
            rh_700 = station_data["relative_humidity_700hPa"][i] or 0
            wind_dir = station_data["winddirection_10m"][i] or 0
            
            # --- THE STRICT CLIMATOLOGICAL FILTER ---
            # 1. Base Convection: Normalized CAPE
            storm_prob = (cape / 2000) * 100
            
            # 2. Geography Filter: Reduce noise in Desert/Coast
            if coords["type"] != "Mountains":
                storm_prob *= 0.4 # Penalize non-mountainous areas
            
            # 3. Atmospheric Filter: Humidity Requirement
            if rh_700 < 45: # Strict threshold for dry summer air
                storm_prob *= 0.2
            
            # 4. Forcing Mechanism: Kaus Flow
            if 90 <= wind_dir <= 180:
                storm_prob *= 1.5
                
            storm_prob = np.clip(storm_prob, 0, 100)
            
            weather_data.append({
                "Time": dt.strftime('%d %b - %H:%M'),
                "DateOnly": dt.strftime('%d %b'),
                "Station": name,
                "Latitude": coords["lat"],
                "Longitude": coords["lon"],
                "Storm Probability": round(storm_prob),
                "Temperature": round(temp_c, 1)
            })

# [Rendering logic remains same, just point to the new df_all]
# (Copying the rest of the visualization code from previous step)
