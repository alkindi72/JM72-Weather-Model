import os
import re
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import requests
import base64

# ==========================================
# 1. PLATFORM SETTINGS
# ==========================================
st.set_page_config(
    page_title="71wm AI Weather Model", 
    page_icon="🌩️", 
    layout="wide"
)

# ==========================================
# 2. CLEAN & BRIGHT CSS
# ==========================================
st.markdown("""
<style>
    /* Clean Bright UI Globally */
    html, body, [data-testid="stAppViewContainer"], .stApp, #root { background-color: #F8FAFC !important; }
    .block-container { background-color: #FFFFFF !important; border-radius: 12px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important; padding: 2rem !important; margin: 1rem auto !important; border: 1px solid #E2E8F0 !important; max-width: 95% !important;}
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; visibility: hidden !important;}
    .stApp p, .stApp span, .stApp label, div[data-testid="stTickBar"], h1, h2, h3, h4, h5, h6 { color: #082F49 !important; font-weight: 900 !important; font-size: 15px !important; }
    
    /* Tabs */
    div[data-testid="stTabs"] [data-baseweb="tab-list"] { border-bottom: 2px solid #CBD5E1 !important; }
    div[data-testid="stTabs"] button { background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-radius: 8px 8px 0 0 !important; margin-right: 5px !important; padding: 10px 20px !important; }
    div[data-testid="stTabs"] button[aria-selected="true"] { background-color: #082F49 !important; border-color: #082F49 !important; }
    div[data-testid="stTabs"] button[aria-selected="true"] p { color: #FFFFFF !important; }
    
    /* AI Components */
    .ai-broadcaster { background: linear-gradient(90deg, #F0F9FF, #E0F2FE); border-left: 5px solid #0284C7; padding: 15px 20px; border-radius: 8px; font-size: 16px; font-weight: bold; color: #0369A1; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(2, 132, 199, 0.1); }
    .anomaly-alert { background-color: #FFFBEB; border: 1px solid #FEF08A; padding: 10px 15px; border-radius: 6px; color: #92400E; font-weight: bold; margin-bottom: 10px; font-size: 14px;}
    
    /* Timeline & Tables */
    div[data-testid="stSlider"] { background-color: #F1F5F9 !important; padding: 20px !important; border-radius: 12px !important; margin-bottom: 25px !important; border: 1px solid #E2E8F0 !important; }
    div[data-testid="stTickBar"] { color: #475569 !important; font-weight: bold !important; }
    div[data-testid="stSlider"] div[role="slider"] { background-color: #0284C7 !important; border: 2px solid #FFF !important; }
    div[data-testid="stSlider"] div[role="slider"] > div { background-color: #0284C7 !important; color: #FFF !important; border-radius: 4px; padding: 2px 8px;}
    .alert-banner { background-color: #FEF2F2 !important; color: #991B1B !important; padding: 18px; border-left: 6px solid #EF4444; border-radius: 8px; margin-bottom: 20px; border: 1px solid #FEE2E2;}
    .sys-success { background-color: #F0FDF4 !important; color: #065F46 !important; padding: 15px; border-left: 6px solid #10B981; border-radius: 8px; margin-bottom: 20px; border: 1px solid #DCFCE7;}
    
    .table-responsive { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .custom-table { width: 100%; border-collapse: collapse; background-color: #ffffff; min-width: 800px; }
    .custom-table th { background-color: #082F49; color: #ffffff !important; padding: 14px; text-align: center; border-bottom: 3px solid #D4AF37; white-space: nowrap; font-size: 13px;}
    .custom-table td { padding: 14px; border-bottom: 1px solid #F1F5F9; border-right: 1px solid #F1F5F9; color: #082F49 !important; font-weight: 800; text-align: center; white-space: nowrap; font-size: 13px;}

    /* Mobile */
    @media (max-width: 768px) {
        .block-container { padding: 1rem !important; margin: 0.5rem auto !important; max-width: 100% !important; border-radius: 0px !important; border: none !important; }
        .stApp p, .stApp span, .stApp label, div[data-testid="stTickBar"], h1, h2, h3, h4, h5, h6 { font-size: 13px !important; }
        div[data-testid="stTabs"] button { padding: 8px 10px !important; font-size: 13px !important; flex-grow: 1; text-align: center; }
        .ai-broadcaster { font-size: 14px; padding: 12px 15px; }
        div[data-testid="stSlider"] { padding: 15px 10px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CENTERED LOGO
# ==========================================
svg_code = """
<svg width="600" height="220" viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(240, 10)">
        <polygon points="60,0 112,30 112,90 60,120 8,90 8,30" fill="none" stroke="#E2E8F0" stroke-width="3"/>
        <polygon points="60,10 103,35 103,85 60,110 17,85 17,35" fill="#F8FAFC" stroke="#082F49" stroke-width="1.5"/>
        <circle cx="60" cy="60" r="25" fill="#FDE047" opacity="0.4" />
        <path d="M 30,35 L 70,35 L 55,65 L 65,65 L 40,95 L 45,70 L 35,70 Z" fill="#D4AF37" />
        <path d="M 75,35 L 90,35 L 90,95 L 75,95 Z" fill="#0284C7" />
        <g transform="translate(31, 108)">
            <rect x="0" y="0" width="10" height="10" fill="#EF4444" rx="2" transform="rotate(45 5 5)"/>
            <rect x="16" y="0" width="10" height="10" fill="#10B981" rx="2" transform="rotate(45 5 5)"/>
            <rect x="32" y="0" width="10" height="10" fill="#CBD5E1" rx="2" transform="rotate(45 5 5)"/>
            <rect x="48" y="0" width="10" height="10" fill="#1E293B" rx="2" transform="rotate(45 5 5)"/>
        </g>
    </g>
    <text x="300" y="180" font-family="'Arial Black', system-ui, sans-serif" font-weight="900" font-size="34" fill="#082F49" text-anchor="middle" letter-spacing="1">71wm AI</text>
    <text x="300" y="205" font-family="system-ui, sans-serif" font-weight="800" font-size="14" fill="#64748B" text-anchor="middle" letter-spacing="6">WEATHER MODEL • U.A.E</text>
</svg>
"""
b64_svg = base64.b64encode(svg_code.encode('utf-8')).decode('utf-8')
st.markdown(f'<div style="width: 100%; display: flex; justify-content: center; margin-top: 0px; margin-bottom: 15px;"><img src="data:image/svg+xml;base64,{b64_svg}" style="max-width: 450px; width: 100%; height: auto;" alt="71wm Logo" /></div>', unsafe_allow_html=True)

# ==========================================
# 4. SESSION & TIMELINE SETUP
# ==========================================
st_autorefresh(interval=15 * 60 * 1000, key="data_refresh")
if "admin_logged_in" not in st.session_state: st.session_state["admin_logged_in"] = False

days_en = {"Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed", "Thursday": "Thu", "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"}
uae_time = datetime.utcnow() + timedelta(hours=4)
base_date = uae_time.replace(minute=0, second=0, microsecond=0)
timeline = [base_date + timedelta(hours=i*3) for i in range(8 * 5)]
timeline_str = [f"{days_en[dt.strftime('%A')]} {dt.strftime('%d')} - {dt.strftime('%H:%M')}" for dt in timeline]
unique_dates_display = []
for dt in timeline:
    d_str = f"{days_en[dt.strftime('%A')]} {dt.strftime('%d')}"
    if d_str not in unique_dates_display: unique_dates_display.append(d_str)

# ==========================================
# 5. DATA FETCHING & 3-ZONES MAPPING
# ==========================================
stations_matrix = {
    "Abu Dhabi": {"lat": 24.4760, "lon": 54.3290, "type": "Coast"}, "ADNOC HQ": {"lat": 24.4621, "lon": 54.3241, "type": "Coast"},
    "Burj Khalifah": {"lat": 25.2017, "lon": 55.2766, "type": "Coast"}, "Sharjah University": {"lat": 25.2869, "lon": 55.4622, "type": "Coast"},
    "Ajman": {"lat": 25.4236, "lon": 55.4447, "type": "Coast"}, "Umm Al Quwain": {"lat": 25.5301, "lon": 55.6548, "type": "Coast"},
    "Ras Al khaimah": {"lat": 25.7716, "lon": 55.9392, "type": "Coast"}, "Fujairah Port": {"lat": 25.1699, "lon": 56.3595, "type": "Coast"},
    "AlRuwais": {"lat": 24.0915, "lon": 52.6242, "type": "Coast"}, "Sir Bani Yas": {"lat": 24.3188, "lon": 52.5990, "type": "Coast"},
    "Dalma": {"lat": 24.4906, "lon": 52.2914, "type": "Coast"}, "Sir Bu Nair": {"lat": 25.2201, "lon": 54.2341, "type": "Coast"},
    "Abu Al Abyad": {"lat": 24.1841, "lon": 53.8626, "type": "Coast"}, "Jabal Jais": {"lat": 25.9508, "lon": 56.1674, "type": "Mountains"},
    "Jabal Al Rahba": {"lat": 25.9264, "lon": 56.1192, "type": "Mountains"}, "Hatta": {"lat": 24.8121, "lon": 56.1396, "type": "Mountains"},
    "Al Tawiyen": {"lat": 25.5527, "lon": 56.0715, "type": "Mountains"}, "Al Heben": {"lat": 25.1251, "lon": 56.1578, "type": "Mountains"},
    "AlQor": {"lat": 24.9065, "lon": 56.1529, "type": "Mountains"}, "Al Aamerah": {"lat": 24.2356, "lon": 55.5396, "type": "Inland"},
    "Al Wathbah": {"lat": 24.1789, "lon": 54.7033, "type": "Inland"}, "Al Dhaid": {"lat": 25.2371, "lon": 55.8179, "type": "Inland"},
    "Al Malaiha": {"lat": 25.1322, "lon": 55.8891, "type": "Inland"}, "Madinat Zayed": {"lat": 23.6836, "lon": 53.6995, "type": "Desert"},
    "Mukhariz": {"lat": 22.9095, "lon": 52.8882, "type": "Desert"}, "Owtaid": {"lat": 23.3955, "lon": 53.1119, "type": "Desert"},
    "Zayed Int'l Airport": {"lat": 24.4330, "lon": 54.6511, "type": "Inland"}, "Dubai Int'l Airport": {"lat": 25.2528, "lon": 55.3644, "type": "Inland"},
    "Sharjah Int'l Airport": {"lat": 25.3286, "lon": 55.5172, "type": "Inland"}, "Ras Al Khaimah Int'l Airport": {"lat": 25.6135, "lon": 55.9388, "type": "Inland"},
    "Fujairah Int'l Airport": {"lat": 25.1122, "lon": 56.3240, "type": "Inland"}, "Al Ain Int'l Airport": {"lat": 24.2617, "lon": 55.6092, "type": "Inland"},
    "Al Bateen Executive Airport": {"lat": 24.4283, "lon": 54.4581, "type": "Coast"}, "Al Maktoum Int'l Airport": {"lat": 24.8961, "lon": 55.1614, "type": "Inland"}
}

@st.cache_data(ttl=3600)
def fetch_stable_live_data(stations_dict):
    try:
        lats = ",".join([str(s["lat"]) for s in stations_dict.values()]); lons = ",".join([str(s["lon"]) for s in stations_dict.values()])
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&current=precipitation,weather_code&hourly=temperature_2m,apparent_temperature,relative_humidity_2m,cape,winddirection_10m,windspeed_10m,windgusts_10m,relative_humidity_850hPa,relative_humidity_700hPa,relative_humidity_500hPa,temperature_850hPa,temperature_500hPa,cloudcover_low&models=gfs_seamless&timezone=auto"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return True, response.json()
    except Exception as e: return False, str(e)

with st.spinner("🤖 71wm AI Engine: Compiling live metrics..."):
    fetch_success, live_data = fetch_stable_live_data(stations_matrix)

@st.cache_data
def load_national_almanac():
    try:
        df = pd.read_csv("climate_yearly_almanac_till_dec_20252.csv", encoding='utf-8-sig')
        if 'month_day' not in df.columns:
            for i in range(min(5, len(df))):
                if 'month_day' in df.iloc[i].astype(str).values:
                    df.columns = df.iloc[i]; df = df[i+1:].reset_index(drop=True); break
        return df, None
    except Exception as e: return pd.DataFrame(), str(e)

almanac_df, err_msg = load_national_almanac()

# ==========================================
# 6. AI DYNAMICS ENGINE
# ==========================================
weather_data = []

if fetch_success and type(live_data) is list:
    for idx, (name, coords) in enumerate(stations_matrix.items()):
        zone_mapped = "Inland" if coords["type"] in ["Inland", "Desert"] else coords["type"]
        try:
            current_precip = live_data[idx].get("current", {}).get("precipitation", 0.0)
            dbz = round(10 * np.log10(200 * (current_precip ** 1.6)), 1) if current_precip > 0.1 else 0.0
            radar_verif = "🚨 Extreme" if dbz >= 45 else ("✅ Active Storm" if dbz >= 25 else ("⚠️ Light Rain" if dbz > 0 else "⏳ Clear"))

            station_data = live_data[idx]["hourly"]
            api_times = [datetime.fromisoformat(t).replace(tzinfo=None) for t in station_data["time"]]
            for dt_str, dt in zip(timeline_str, timeline):
                try:
                    time_diffs = [abs((api_t - dt).total_seconds()) for api_t in api_times]
                    closest_idx = time_diffs.index(min(time_diffs))
                    
                    temp_c = station_data["temperature_2m"][closest_idx] or 35.0
                    app_temp = station_data.get("apparent_temperature", [temp_c]*len(api_times))[closest_idx] or temp_c
                    surface_rh = station_data.get("relative_humidity_2m", [50]*len(api_times))[closest_idx] or 50
                    cloud_low = station_data.get("cloudcover_low", [0]*len(api_times))[closest_idx] or 0
                    
                    wind_dir = station_data.get("winddirection_10m", [0]*len(api_times))[closest_idx] or 0
                    wind_spd = station_data.get("windspeed_10m", [0]*len(api_times))[closest_idx] or 0
                    wind_gst = max(station_data.get("windgusts_10m", [0]*len(api_times))[closest_idx] or 0, wind_spd * 1.35)
                    cape_val = station_data["cape"][closest_idx] or 0
                    
                    rh_850 = station_data.get("relative_humidity_850hPa", [50]*len(api_times))[closest_idx] or 50
                    rh_700 = station_data.get("relative_humidity_700hPa", [50]*len(api_times))[closest_idx] or 50
                    rh_500 = station_data.get("relative_humidity_500hPa", [50]*len(api_times))[closest_idx] or 50
                    t_850 = station_data.get("temperature_850hPa", [20]*len(api_times))[closest_idx] or 20
                    t_500 = station_data.get("temperature_500hPa", [-10]*len(api_times))[closest_idx] or -10
                    
                    # Storm AI
                    prob = (cape_val / 2000.0) * 100 
                    moisture_index = (rh_850 * 0.4) + (rh_700 * 0.4) + (rh_500 * 0.2)
                    lapse_rate = t_850 - t_500
                    if lapse_rate > 26: prob *= 1.3
                    elif lapse_rate < 20: prob *= 0.5
                    if moisture_index < 40: prob *= 0.1
                    elif moisture_index > 70: prob *= 1.2
                    if coords["type"] == "Mountains" and temp_c > 38: prob *= 1.3
                    storm_prob = np.clip(prob, 0, 100)
                    
                    # General Fog AI
                    fog_prob = 0
                    is_night_early_morning = dt.hour < 8 or dt.hour > 22
                    if is_night_early_morning and surface_rh > 80 and wind_spd < 15:
                        fog_prob = ((surface_rh - 80) * 4) + ((15 - wind_spd) * 3)
                    fog_prob = np.clip(fog_prob, 0, 100)
                    
                    # AL-KOUS CLOUD PREDICTOR
                    alkous_prob = 0
                    if coords["lon"] >= 55.8:
                        if 45 <= wind_dir <= 160 and surface_rh >= 65:
                            alkous_base = ((surface_rh - 65) * 2) + (cloud_low * 0.5)
                            if temp_c >= 35: alkous_base *= 1.2
                            alkous_prob = np.clip(alkous_base, 0, 100)
                    
                    dust_p = (wind_spd / 35) * 100 if coords["type"] == "Desert" else (wind_spd / 45) * 100
                    if wind_gst > 45: dust_p += 25
                    dust_p = np.clip(dust_p, 0, 100)

                except Exception: temp_c, app_temp, storm_prob, fog_prob, alkous_prob, wind_spd = 36.0, 36.0, 0.0, 0.0, 0.0, 10.0

                weather_data.append({
                    "Time": dt_str, "DateOnly": f"{days_en[dt.strftime('%A')]} {dt.strftime('%d')}", 
                    "Station": name, "Zone": zone_mapped,
                    "Latitude": coords["lat"], "Longitude": coords["lon"],
                    "Storm Probability": round(storm_prob), "Fog Probability": round(fog_prob), "AlKous Prob": round(alkous_prob),
                    "Temperature": round(temp_c, 1), "Apparent Temp": round(app_temp, 1), "Humidity": round(surface_rh),
                    "Wind Speed": round(wind_spd, 1), "dBZ": dbz, "Radar Verif": radar_verif
                })
        except Exception: pass

df_all = pd.DataFrame(weather_data)

# ==========================================
# AI GENERATIVE BRIEFING
# ==========================================
current_time_df = df_all[df_all["Time"] == timeline_str[0]]
max_temp_val = current_time_df["Temperature"].max()
max_temp_loc = current_time_df.loc[current_time_df["Temperature"].idxmax()]["Station"]
max_app_temp = current_time_df["Apparent Temp"].max()
max_storm_val = current_time_df["Storm Probability"].max()
max_alkous = current_time_df["AlKous Prob"].max()

ai_briefing = f"🤖 **71wm AI Broadcaster:** The thermal peak is at {max_temp_loc} ({max_temp_val}°C), feeling like {max_app_temp}°C. "
if max_alkous > 50: ai_briefing += f"⚠️ High probability ({max_alkous}%) of stifling 'Al-Kous' low clouds hugging the Eastern Coast and Hajar Mountains. "
elif max_storm_val > 40: ai_briefing += f"Convective activity shows a {max_storm_val}% risk of isolated storms. "
else: ai_briefing += "Atmospheric conditions remain generally stable across most geographic sectors."

st.markdown(f'<div class="ai-broadcaster">{ai_briefing}</div>', unsafe_allow_html=True)

# ==========================================
# 9. TABS & INTERFACE
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🌩️ Storms & Fog", "🔥 Heat & Anomalies", "☁️ Al-Kous Clouds", "📋 Model Matrix", "🤖 71wm AI Assistant", "⚙️ Control Room"
])

esri_topo_layer = [{"below": 'traces', "sourcetype": "raster", "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"]}]

with tab1:
    st.markdown('<h4 style="color:#082F49; font-weight:900; margin-bottom:15px;">📋 5-Day Storm & Fog Forecast (National)</h4>', unsafe_allow_html=True)
    
    cols_t1 = st.columns(len(unique_dates_display[:5]))
    for i, date in enumerate(unique_dates_display[:5]):
        day_df = df_all[df_all["DateOnly"] == date]
        daily_max_storm = int(day_df["Storm Probability"].max())
        daily_max_fog = int(day_df["Fog Probability"].max())
        
        max_overall = max(daily_max_storm, daily_max_fog)
        if max_overall >= 60: border, bg = "#FCA5A5", "#FEF2F2"
        elif max_overall >= 30: border, bg = "#FDE047", "#FFFBEB"
        else: border, bg = "#86EFAC", "#F0FDF4"
        
        card_html_flat = f"<div style='background-color:{bg}; border: 1px solid {border}; border-radius: 8px; padding: 15px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); text-align:center;'><div style='color:#082F49; font-size:15px; font-weight:900; margin-bottom:12px; border-bottom: 1px solid {border}; padding-bottom: 8px;'>📅 {date}</div><div style='font-size:16px; font-weight:900; color:#EF4444; margin-bottom:8px;'>⛈️ Storm: {daily_max_storm}%</div><div style='font-size:16px; font-weight:900; color:#64748B;'>🌫️ Fog: {daily_max_fog}%</div></div>"
        cols_t1[i].markdown(card_html_flat, unsafe_allow_html=True)

    selected_time_t1 = st.select_slider("Forecast Timeline", options=timeline_str, key="t1_slider", label_visibility="collapsed")
    df_time_t1 = df_all[df_all["Time"] == selected_time_t1].copy()

    col_s, col_f = st.columns(2)
    with col_s:
        fig1 = px.density_mapbox(df_time_t1, lat="Latitude", lon="Longitude", z="Storm Probability", radius=45, center=dict(lat=24.4, lon=54.6), zoom=5.5, mapbox_style="white-bg", opacity=0.75, color_continuous_scale=["rgba(0,0,0,0)", "#A3E635", "#FDE047", "#EF4444", "#7E22CE"], range_color=[0, 100], title="Convective Storm Probability")
        fig1.update_layout(mapbox_layers=esri_topo_layer, margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig1, use_container_width=True, key="storm_map_data")
        
    with col_f:
        fig_fog = px.density_mapbox(df_time_t1, lat="Latitude", lon="Longitude", z="Fog Probability", radius=45, center=dict(lat=24.4, lon=54.6), zoom=5.5, mapbox_style="white-bg", opacity=0.8, color_continuous_scale=["rgba(0,0,0,0)", "#E2E8F0", "#94A3B8", "#475569"], range_color=[0, 100], title="AI Fog Formation Index")
        fig_fog.update_layout(mapbox_layers=esri_topo_layer, margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_fog, use_container_width=True, key="fog_map_data")

    st.markdown('<hr><h3 style="color:#082F49; font-weight:900;">🛰️ Live Telemetry: Satellite Cloud Imagery</h3>', unsafe_allow_html=True)
    components.html("""<div style="position: relative; width: 100%; height: 500px; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); background-color: #F8FAFC;"><iframe width="100%" height="520" src="https://embed.windy.com/embed.html?type=map&location=coordinates&overlay=satellite&lat=24.6&lon=54.8&zoom=6" frameborder="0" style="position: absolute; top: 0; left: 0;"></iframe><div style="position: absolute; bottom: 0px; right: 0px; width: 180px; height: 35px; background: rgba(8, 47, 73, 0.95); display: flex; align-items: center; justify-content: center; border-top-left-radius: 10px; border: 1px solid #D4AF37;"><span style="color: #D4AF37; font-family: sans-serif; font-size: 14px; font-weight: 900;">🛰️ 71wm SATELLITE LIVE</span></div></div>""", height=520)

with tab2:
    st.markdown('<h4 style="color:#082F49; font-weight:900; margin-bottom:15px;">📋 5-Day Thermal Range (Min-Max By Zone)</h4>', unsafe_allow_html=True)
    
    cols_t2 = st.columns(len(unique_dates_display[:5]))
    for i, date in enumerate(unique_dates_display[:5]):
        day_df = df_all[df_all["DateOnly"] == date]
        coast_max = round(day_df[day_df["Zone"] == "Coast"]["Temperature"].max(), 1)
        coast_min = round(day_df[day_df["Zone"] == "Coast"]["Temperature"].min(), 1)
        mount_max = round(day_df[day_df["Zone"] == "Mountains"]["Temperature"].max(), 1)
        mount_min = round(day_df[day_df["Zone"] == "Mountains"]["Temperature"].min(), 1)
        inland_max = round(day_df[day_df["Zone"] == "Inland"]["Temperature"].max(), 1)
        inland_min = round(day_df[day_df["Zone"] == "Inland"]["Temperature"].min(), 1)
        
        max_overall = max(coast_max, mount_max, inland_max)
        if max_overall >= 48: border, bg = "#FCA5A5", "#FEF2F2"
        elif max_overall >= 40: border, bg = "#FDE047", "#FFFBEB"
        else: border, bg = "#86EFAC", "#F0FDF4"
        
        card_html = f"<div style='background-color:{bg}; border: 1px solid {border}; border-radius: 8px; padding: 15px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'><div style='color:#082F49; font-size:15px; font-weight:900; margin-bottom:12px; text-align:center; border-bottom: 1px solid {border}; padding-bottom: 8px;'>📅 {date}</div><div style='display: flex; justify-content: space-between; font-size:14px; color:#1E293B; margin-bottom:6px;'><span>🌊 Coast:</span><span style='font-weight:900;'>⬇ {coast_min}° - ⬆ {coast_max}°</span></div><div style='display: flex; justify-content: space-between; font-size:14px; color:#1E293B; margin-bottom:6px;'><span>⛰️ Mount:</span><span style='font-weight:900;'>⬇ {mount_min}° - ⬆ {mount_max}°</span></div><div style='display: flex; justify-content: space-between; font-size:14px; color:#1E293B;'><span>🏜️ Inland:</span><span style='font-weight:900;'>⬇ {inland_min}° - ⬆ {inland_max}°</span></div></div>"
        cols_t2[i].markdown(card_html, unsafe_allow_html=True)
        
    selected_time_t2 = st.select_slider("Forecast Timeline", options=timeline_str, key="t2_slider", label_visibility="collapsed")
    df_time_t2 = df_all[df_all["Time"] == selected_time_t2].copy()

    fig2 = px.density_mapbox(df_time_t2, lat="Latitude", lon="Longitude", z="Temperature", radius=50, center=dict(lat=24.4, lon=54.6), zoom=6, mapbox_style="white-bg", opacity=0.7, color_continuous_scale=["rgba(0,0,0,0)", "#FDE047", "#F97316", "#DC2626", "#450A0A"], range_color=[40, 60])
    fig2.update_layout(mapbox_layers=esri_topo_layer, margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig2, use_container_width=True, key="heat_map_data")

with tab3:
    st.markdown('<h4 style="color:#082F49; font-weight:900; margin-bottom:15px;">📋 5-Day Al-Kous Cloud Forecast (Eastern Coast & Mountains)</h4>', unsafe_allow_html=True)
    
    cols_t3 = st.columns(len(unique_dates_display[:5]))
    for i, date in enumerate(unique_dates_display[:5]):
        day_df = df_all[df_all["DateOnly"] == date]
        max_kous_day = int(day_df["AlKous Prob"].max())
        
        if max_kous_day >= 60: border, bg = "#CBD5E1", "#F1F5F9"
        elif max_kous_day >= 30: border, bg = "#E2E8F0", "#F8FAFC"
        else: border, bg = "#86EFAC", "#F0FDF4"
        
        card_html_kous = f"<div style='background-color:{bg}; border: 1px solid {border}; border-radius: 8px; padding: 15px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); text-align:center;'><div style='color:#082F49; font-size:15px; font-weight:900; margin-bottom:12px; border-bottom: 1px solid {border}; padding-bottom: 8px;'>📅 {date}</div><div style='font-size:18px; font-weight:900; color:#334155; margin-bottom:4px;'>☁️ الكوس: {max_kous_day}%</div></div>"
        cols_t3[i].markdown(card_html_kous, unsafe_allow_html=True)

    selected_time_t3 = st.select_slider("Forecast Timeline", options=timeline_str, key="t3_slider", label_visibility="collapsed")
    df_time_t3 = df_all[df_all["Time"] == selected_time_t3].copy()
    
    east_stations = df_time_t3[df_time_t3["Longitude"] >= 55.8].copy()
    
    # =========================================================================
    # 🛑 تم الإصلاح الجذري هنا: تحويل الخريطة إلى الخارطة الحرارية الانسيابية بالكامل
    # =========================================================================
    fig3 = px.density_mapbox(
        east_stations, 
        lat="Latitude", 
        lon="Longitude", 
        z="AlKous Prob", 
        radius=55, 
        center=dict(lat=25.1, lon=56.2), 
        zoom=7.5, 
        mapbox_style="white-bg", 
        opacity=0.85, 
        color_continuous_scale=["rgba(0,0,0,0)", "#E2E8F0", "#94A3B8", "#475569", "#1E293B"], 
        range_color=[0, 100], 
        title="Al-Kous Cloud Density Matrix"
    )
    fig3.update_layout(mapbox_layers=esri_topo_layer, margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig3, use_container_width=True, key="kous_heatmap_data")

with tab4:
    selected_time_t4 = st.select_slider("Forecast Timeline", options=timeline_str, key="t4_slider", label_visibility="collapsed")
    df_time_t4 = df_all[df_all["Time"] == selected_time_t4].copy()
    
    st.markdown(f"<h3 style='color:#082F49; font-weight:900;'>📊 Full 34-Station Matrix at {selected_time_t4}</h3>", unsafe_allow_html=True)
    display_df = df_time_t4.sort_values(by="Temperature", ascending=False)
    html_table = "<div class='table-responsive'><table class='custom-table'><tr><th>Station</th><th>Temp (°C)</th><th>Feels Like</th><th>RH (%)</th><th>Al-Kous (%)</th><th>Storm (%)</th></tr>"
    for _, row in display_df.iterrows():
        s_color = "#EF4444" if row['Storm Probability'] >= 75 else "#082F49"
        k_color = "#475569" if row['AlKous Prob'] >= 50 else "#082F49"
        app_color = "#DC2626" if row['Apparent Temp'] >= 45 else ("#F97316" if row['Apparent Temp'] >= 40 else "#082F49")
        kous_val = f"{row['AlKous Prob']}%" if row['AlKous Prob'] > 0 else "-"
        
        html_table += f"<tr><td>{row['Station']}</td><td>{row['Temperature']}°C</td><td style='color:{app_color}; font-weight:bold;'>{row['Apparent Temp']}°C</td><td>{row['Humidity']}%</td><td style='color:{k_color}; font-weight:bold;'>{kous_val}</td><td style='color:{s_color};'>{row['Storm Probability']}%</td></tr>"
    html_table += "</table></div>"
    st.markdown(html_table, unsafe_allow_html=True)

with tab5:
    st.markdown('<h4 style="color:#082F49; font-weight:900;">🤖 71wm AI Data Assistant (Interactive Chatbot)</h4>', unsafe_allow_html=True)
    
    prompt = st.chat_input("Ask a question...")
    if prompt:
        st.chat_message("user").write(prompt)
        p_lower = prompt.lower()
        response = ""
        current_data = df_all[df_all["Time"] == timeline_str[0]]
        
        if "hot" in p_lower or "أعلى حرارة" in p_lower:
            hot_st = current_data.loc[current_data["Temperature"].idxmax()]
            response = f"The hottest station right now is **{hot_st['Station']}** recording **{hot_st['Temperature']}°C**, feeling like **{hot_st['Apparent Temp']}°C**."
        elif "kous" in p_lower or "كوس" in p_lower:
            kous_st = current_data[current_data["AlKous Prob"] > 30]
            if not kous_st.empty: response = f"Al-Kous clouds are likely forming over: {', '.join(kous_st['Station'].tolist())}."
            else: response = "No significant Al-Kous activity detected at the moment on the Eastern Coast."
        elif "storm" in p_lower or "عاصفة" in p_lower or "rain" in p_lower:
            stormy = current_data[current_data["Storm Probability"] > 40]
            if not stormy.empty: response = f"Stations with storm risk > 40%: {', '.join(stormy['Station'].tolist())}."
            else: response = "Currently, there are no stations with a storm probability above 40%."
        else:
            response = "I am the 71wm AI Assistant. Try asking about the 'hottest station', 'storm risks', or 'al-kous clouds'."
            
        st.chat_message("assistant").write(response)
    else:
        st.chat_message("assistant").write("Hello! I am ready to analyze the 34-station data array. What would you like to know?")

with tab6:
    st.markdown("### 🚨 71wm Alert Control Room")
    st.info("ℹ️ The automated email alert engine has been permanently physically severed from the codebase to ensure zero spam. Alerts will only trigger visually inside this dashboard.")
