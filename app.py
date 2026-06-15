import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import requests

st.set_page_config(page_title="JM72 AI Weather Model", layout="wide")

# CSS Styling
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC !important; }
    .header { background-color: #082F49; color: white; padding: 20px; border-radius: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>JM72 AI Weather Model - Operational Mode</h1></div>', unsafe_allow_html=True)

# Data Fetching
stations = {
    "Al Hajar Mountains": {"lat": 25.3, "lon": 56.1, "type": "Mountains"},
    "Fujairah Coast": {"lat": 25.12, "lon": 56.32, "type": "Mountains"},
    "Al Ain": {"lat": 24.19, "lon": 55.76, "type": "Inland"},
    "Al Dhafra": {"lat": 23.65, "lon": 53.70, "type": "Desert"},
    "Abu Dhabi": {"lat": 24.45, "lon": 54.37, "type": "Coast"}
}

@st.cache_data(ttl=3600)
def get_data():
    lats = ",".join([str(s["lat"]) for s in stations.values()])
    lons = ",".join([str(s["lon"]) for s in stations.values()])
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly=temperature_2m,cape,winddirection_10m,relative_humidity_700hPa&models=gfs_seamless&timezone=auto"
    return requests.get(url).json()

try:
    data = get_data()
    weather_data = []
    for idx, (name, coords) in enumerate(stations.items()):
        hourly = data[idx]["hourly"]
        for i in range(len(hourly["time"])):
            # Strict Filters
            cape = hourly["cape"][i] or 0
            rh = hourly["relative_humidity_700hPa"][i] or 0
            wind = hourly["winddirection_10m"][i] or 0
            
            prob = (cape / 2000) * 100
            if coords["type"] != "Mountains": prob *= 0.4
            if rh < 45: prob *= 0.2
            if 90 <= wind <= 180: prob *= 1.5
            
            weather_data.append({
                "Station": name, "Time": hourly["time"][i],
                "Probability": round(min(prob, 100)),
                "Temp": hourly["temperature_2m"][i]
            })

    df = pd.DataFrame(weather_data)
    st.success("البيانات محدثة ومعالجة وفق المعايير المناخية الصارمة")
    st.dataframe(df[df["Probability"] > 0].sort_values("Probability", ascending=False).head(10))
    
except Exception as e:
    st.error(f"خطأ في تحميل البيانات: {e}")
