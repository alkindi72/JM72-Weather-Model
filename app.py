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
    page_title="JM72 AI Weather Model", 
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
    .custom-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; background-color: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #E2E8F0;}
    .custom-table th { background-color: #082F49; color: #ffffff !important; padding: 14px; text-align: center; border-bottom: 3px solid #D4AF37;}
    .custom-table td { padding: 14px; border-bottom: 1px solid #F1F5F9; border-right: 1px solid #F1F5F9; color: #082F49 !important; font-weight: 800; text-align: center;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CENTERED LOGO
# ==========================================
svg_code = """
<svg width="600" height="240" viewBox="0 0 600 240" xmlns="http://www.w3.org/2000/svg">
    <path id="textArcPath" d="M 70,160 Q 300,0 530,160" fill="transparent" />
    <text font-family="'Arial Black', 'Segoe UI Black', sans-serif" font-weight="900" font-size="36" fill="#082F49">
        <textPath href="#textArcPath" startOffset="50%" text-anchor="middle">
            JM72 AI Weather Model
        </textPath>
    </text>
    <g transform="translate(230, 110)">
        <path d="M 10,70 L 40,25 L 70,55 L 100,15 L 130,70 Z" fill="#D4AF37" />
        <path d="M -5,70 Q 35,55 70,70 T 145,70 L 145,85 L -5,85 Z" fill="#0284C7" />
        <text x="70" y="55" font-family="'Arial Black', sans-serif" font-weight="900" font-size="24" fill="#082F49" text-anchor="middle" letter-spacing="1">JM72</text>
    </g>
</svg>
"""
b64_svg = base64.b64encode(svg_code.encode('utf-8')).decode('utf-8')
st.markdown(f'<div style="width: 100%; display: flex; justify-content: center; margin-top: 0px; margin-bottom: 15px;"><img src="data:image/svg+xml;base64,{b64_svg}" style="max-width: 450px; width: 100%; height: auto;" alt="JM72 Logo" /></div>', unsafe_allow_html=True)

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

SECTOR_MAP = {
    "Eastern Region": ["Fujairah Port", "Fujairah Int'l Airport", "Hatta", "Al Tawiyen", "Al Heben", "AlQor"],
    "Central Region": ["Al Dhaid", "Al Malaiha"],
    "Abu Dhabi & Al Dhafra": ["Abu Dhabi", "ADNOC HQ", "Abu Al Abyad", "AlRuwais", "Sir Bani Yas", "Dalma", "Sir Bu Nair", "Al Wathbah", "Madinat Zayed", "Mukhariz", "Owtaid", "Zayed Int'l Airport", "Al Bateen Executive Airport"],
    "Al Ain Region": ["Al Ain Int'l Airport", "Al Aamerah"],
    "Dubai & Northern Emirates": ["Burj Khalifah", "Sharjah University", "Ajman", "Umm Al Quwain", "Ras Al khaimah", "Jabal Jais", "Jabal Al Rahba", "Dubai Int'l Airport", "Sharjah Int'l Airport", "Ras Al Khaimah Int'l Airport", "Al Maktoum Int'l Airport"]
}

def get_clustered_sectors(station_list):
    sectors = set()
    for station in station_list:
        found = False
        for sector, stations in SECTOR_MAP.items():
            if station in stations:
                sectors.add(sector); found = True; break
        if not found: sectors.add(station)
    return list(sectors)

@st.cache_data(ttl=3600)
def fetch_stable_live_data(stations_dict):
    try:
        lats = ",".join([str(s["lat"]) for s in stations_dict.values()]); lons = ",".join([str(s["lon"]) for s in stations_dict.values()])
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&current=precipitation,weather_code&hourly=temperature_2m,relative_humidity_2m,cape,winddirection_10m,windspeed_10m,windgusts_10m,relative_humidity_700hPa&models=gfs_seamless&timezone=auto"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return True, response.json()
    except Exception as e: return False, str(e)

with st.spinner("🤖 JM72 AI Engine: Compiling live metrics & executing models..."):
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
# 6. AI DYNAMICS ENGINE (CORE PROCESSING)
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
                    surface_rh = station_data.get("relative_humidity_2m", [50]*len(api_times))[closest_idx] or 50
                    rh_700 = station_data["relative_humidity_700hPa"][closest_idx] or 0
                    wind_spd = station_data.get("windspeed_10m", [0]*len(api_times))[closest_idx] or 0
                    wind_gst = max(station_data.get("windgusts_10m", [0]*len(api_times))[closest_idx] or 0, wind_spd * 1.35)
                    cape_val = station_data["cape"][closest_idx] or 0
                    
                    # Storm Probability Logic
                    prob = (cape_val / 2000) * 100
                    if rh_700 < 45: prob *= 0.05
                    elif rh_700 < 55: prob *= 0.3
                    if coords["type"] == "Mountains" and temp_c > 38: prob *= 1.3
                    storm_prob = np.clip(prob, 0, 100)
                    
                    # FOG PREDICTOR LOGIC
                    fog_prob = 0
                    is_night_early_morning = dt.hour < 8 or dt.hour > 22
                    if is_night_early_morning and surface_rh > 80 and wind_spd < 15:
                        fog_prob = ((surface_rh - 80) * 4) + ((15 - wind_spd) * 3)
                    fog_prob = np.clip(fog_prob, 0, 100)
                    
                    # Dust Logic
                    dust_p = (wind_spd / 35) * 100 if coords["type"] == "Desert" else (wind_spd / 45) * 100
                    if wind_gst > 45: dust_p += 25
                    dust_p = np.clip(dust_p, 0, 100)

                except Exception: temp_c, storm_prob, fog_prob, wind_spd, wind_gst, dust_p = 36.0, 0.0, 0.0, 10.0, 15.0, 0.0

                weather_data.append({
                    "Time": dt_str, "DateOnly": f"{days_en[dt.strftime('%A')]} {dt.strftime('%d')}", 
                    "Station": name, "Zone": zone_mapped,
                    "Latitude": coords["lat"], "Longitude": coords["lon"],
                    "Storm Probability": round(storm_prob), "Fog Probability": round(fog_prob), 
                    "Temperature": round(temp_c, 1), "Humidity": round(surface_rh),
                    "Wind Speed": round(wind_spd, 1), "Gusts": round(wind_gst, 1),
                    "Dust Probability": round(dust_p), "dBZ": dbz, "Radar Verif": radar_verif
                })
        except Exception: pass

if not weather_data:
    st.error("⚠️ Connection to Weather API failed. Offline Mode Active.")
    # Fallback dummy data
    np.random.seed(42)
    for dt_str, dt in zip(timeline_str, timeline):
        is_afternoon = 12 <= dt.hour <= 18
        for name, coords in stations_matrix.items():
            zone_mapped = "Inland" if coords["type"] in ["Inland", "Desert"] else coords["type"]
            base_storm = 75 if (is_afternoon and coords["type"] == "Mountains") else 0
            temp = 42 + np.random.uniform(-3, 4)
            wind_spd = np.random.uniform(10, 45)
            s_prob = round(np.clip(base_storm + np.random.uniform(-5, 10), 0, 100)) if base_storm > 0 else 0
            weather_data.append({
                "Time": dt_str, "DateOnly": f"{days_en[dt.strftime('%A')]} {dt.strftime('%d')}", 
                "Station": name, "Zone": zone_mapped,
                "Latitude": coords["lat"], "Longitude": coords["lon"], "Storm Probability": s_prob, "Fog Probability": 0, "Temperature": round(temp, 1), 
                "Wind Speed": round(wind_spd, 1), "Wind Direction": round(np.random.uniform(0, 360)),
                "Gusts": round(wind_spd * 1.5, 1), "Dust Probability": round((wind_spd/50)*100),
                "Visibility": round(10.0 - (wind_spd/50)*9.0, 1), "Rainfall": round(np.random.uniform(10, 40), 1) if s_prob > 70 else 0.0,
                "dBZ": 0.0, "Radar Verif": "⏳ Offline Data"
            })

df_all = pd.DataFrame(weather_data)

# ==========================================
# AI GENERATIVE BRIEFING (Top Banner)
# ==========================================
current_time_df = df_all[df_all["Time"] == timeline_str[0]]
max_temp_val = current_time_df["Temperature"].max()
max_temp_loc = current_time_df.loc[current_time_df["Temperature"].idxmax()]["Station"]
max_storm_val = current_time_df["Storm Probability"].max()
max_fog_val = current_time_df["Fog Probability"].max()

ai_briefing = f"🤖 **JM72 AI Broadcaster:** Currently, the thermal peak is centered over {max_temp_loc} at {max_temp_val}°C. "
if max_storm_val > 40: ai_briefing += f"Convective activity shows a {max_storm_val}% risk of isolated storms. "
elif max_fog_val > 50: ai_briefing += f"High surface moisture indicates a {max_fog_val}% risk of radiation fog formation tonight. "
else: ai_briefing += "Atmospheric conditions remain generally stable across most geographic sectors."

st.markdown(f'<div class="ai-broadcaster">{ai_briefing}</div>', unsafe_allow_html=True)

# ==========================================
# 9. TABS & INTERFACE
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🌩️ Storms & Fog", "🔥 Heat & Anomalies", "🗺️ Dynamic Clusters", "📋 Model Matrix", "🤖 JM72 AI Assistant", "⚙️ Control Room"
])

esri_topo_layer = [{"below": 'traces', "sourcetype": "raster", "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"]}]

with tab1:
    st.markdown('<h4 style="color:#082F49; font-weight:900; margin-bottom:15px;">📋 5-Day Storm & Fog Forecast (By Zone)</h4>', unsafe_allow_html=True)
    
    # 3-ZONES 5-DAY STORM & FOG CARDS - FIXED WITH FLEXBOX
    cols_t1 = st.columns(len(unique_dates_display[:5]))
    for i, date in enumerate(unique_dates_display[:5]):
        day_df = df_all[df_all["DateOnly"] == date]
        
        coast_storm = int(day_df[day_df["Zone"] == "Coast"]["Storm Probability"].max())
        coast_fog = int(day_df[day_df["Zone"] == "Coast"]["Fog Probability"].max())
        mount_storm = int(day_df[day_df["Zone"] == "Mountains"]["Storm Probability"].max())
        mount_fog = int(day_df[day_df["Zone"] == "Mountains"]["Fog Probability"].max())
        inland_storm = int(day_df[day_df["Zone"] == "Inland"]["Storm Probability"].max())
        inland_fog = int(day_df[day_df["Zone"] == "Inland"]["Fog Probability"].max())
        
        max_overall = max(coast_storm, mount_storm, inland_storm, coast_fog, mount_fog, inland_fog)
        if max_overall >= 60: border, bg = "#FCA5A5", "#FEF2F2"
        elif max_overall >= 30: border, bg = "#FDE047", "#FFFBEB"
        else: border, bg = "#86EFAC", "#F0FDF4"
        
        card_html = f"""
        <div style="background-color:{bg}; border: 1px solid {border}; border-radius: 8px; padding: 15px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="color:#082F49; font-size:15px; font-weight:900; margin-bottom:12px; text-align:center; border-bottom: 1px solid {border}; padding-bottom: 8px;">📅 {date}</div>
            
            <div style="display: flex; justify-content: space-between; font-size:14px; color:#1E293B; margin-bottom:6px;">
                <span>🌊 Coast:</span>
                <span style="font-weight:900;"><span style="color:#EF4444;">⛈️ {coast_storm}%</span> &nbsp; <span style="color:#64748B;">🌫️ {coast_fog}%</span></span>
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size:14px; color:#1E293B; margin-bottom:6px;">
                <span>⛰️ Mount:</span>
                <span style="font-weight:900;"><span style="color:#EF4444;">⛈️ {mount_storm}%</span> &nbsp; <span style="color:#64748B;">🌫️ {mount_fog}%</span></span>
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size:14px; color:#1E293B;">
                <span>🏜️ Inland:</span>
                <span style="font-weight:900;"><span style="color:#EF4444;">⛈️ {inland_storm}%</span> &nbsp; <span style="color:#64748B;">🌫️ {inland_fog}%</span></span>
            </div>
        </div>
        """
        cols_t1[i].markdown(card_html, unsafe_allow_html=True)

    selected_time_t1 = st.select_slider("Forecast Timeline", options=timeline_str, key="t1_slider", label_visibility="collapsed")
    df_time_t1 = df_all[df_all["Time"] == selected_time_t1].copy()

    col_s, col_f = st.columns(2)
    with col_s:
        max_storm = df_time_t1["Storm Probability"].max()
        st.markdown(f"**Max Storm Risk:** {max_storm}%")
        fig1 = px.density_mapbox(df_time_t1, lat="Latitude", lon="Longitude", z="Storm Probability", radius=45, center=dict(lat=24.4, lon=54.6), zoom=5.5, mapbox_style="white-bg", opacity=0.75, color_continuous_scale=["rgba(0,0,0,0)", "#A3E635", "#FDE047", "#EF4444", "#7E22CE"], range_color=[0, 100], title="Convective Storm Probability")
        fig1.update_layout(mapbox_layers=esri_topo_layer, margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig1, use_container_width=True, key="storm_map_data")
        
    with col_f:
        max_fog = df_time_t1["Fog Probability"].max()
        st.markdown(f"**Max Radiation Fog Risk:** {max_fog}%")
        fig_fog = px.density_mapbox(df_time_t1, lat="Latitude", lon="Longitude", z="Fog Probability", radius=45, center=dict(lat=24.4, lon=54.6), zoom=5.5, mapbox_style="white-bg", opacity=0.8, color_continuous_scale=["rgba(0,0,0,0)", "#E2E8F0", "#94A3B8", "#475569"], range_color=[0, 100], title="AI Fog Formation Index")
        fig_fog.update_layout(mapbox_layers=esri_topo_layer, margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_fog, use_container_width=True, key="fog_map_data")

with tab2:
    st.markdown('<h4 style="color:#082F49; font-weight:900; margin-bottom:15px;">📋 5-Day Thermal Range (Min-Max By Zone)</h4>', unsafe_allow_html=True)
    
    # 3-ZONES 5-DAY MIN-MAX TEMPERATURE CARDS - FIXED WITH FLEXBOX
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
        
        card_html = f"""
        <div style="background-color:{bg}; border: 1px solid {border}; border-radius: 8px; padding: 15px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="color:#082F49; font-size:15px; font-weight:900; margin-bottom:12px; text-align:center; border-bottom: 1px solid {border}; padding-bottom: 8px;">📅 {date}</div>
            
            <div style="display: flex; justify-content: space-between; font-size:14px; color:#1E293B; margin-bottom:6px;">
                <span>🌊 Coast:</span>
                <span style="font-weight:900;">⬇ {coast_min}° - ⬆ {coast_max}°</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size:14px; color:#1E293B; margin-bottom:6px;">
                <span>⛰️ Mount:</span>
                <span style="font-weight:900;">⬇ {mount_min}° - ⬆ {mount_max}°</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size:14px; color:#1E293B;">
                <span>🏜️ Inland:</span>
                <span style="font-weight:900;">⬇ {inland_min}° - ⬆ {inland_max}°</span>
            </div>
        </div>
        """
        cols_t2[i].markdown(card_html, unsafe_allow_html=True)
        
    # ANOMALY DETECTION
    current_month_str = str(datetime.utcnow().month)
    if not almanac_df.empty:
        hist_max_raw = almanac_df['highest_temperature_value'].replace(['-', '', ' '], np.nan).astype(float).max()
        if not np.isnan(hist_max_raw) and max_temp_val > (hist_max_raw - 3.0):
            st.markdown(f'<div class="anomaly-alert">⚠️ AI Anomaly Detected: Current max temperature ({max_temp_val}°C) is approaching the historical national extreme ({hist_max_raw}°C).</div>', unsafe_allow_html=True)

    selected_time_t2 = st.select_slider("Forecast Timeline", options=timeline_str, key="t2_slider", label_visibility="collapsed")
    df_time_t2 = df_all[df_all["Time"] == selected_time_t2].copy()

    fig2 = px.density_mapbox(df_time_t2, lat="Latitude", lon="Longitude", z="Temperature", radius=50, center=dict(lat=24.4, lon=54.6), zoom=6, mapbox_style="white-bg", opacity=0.7, color_continuous_scale=["rgba(0,0,0,0)", "#FDE047", "#F97316", "#DC2626", "#450A0A"], range_color=[40, 60])
    fig2.update_layout(mapbox_layers=esri_topo_layer, margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig2, use_container_width=True, key="heat_map_data")

with tab3:
    st.markdown('<h4 style="color:#082F49; font-weight:900;">🗺️ AI Dynamic Clustering (Live Behavioral Groups)</h4>', unsafe_allow_html=True)
    st.info("💡 Instead of fixed maps, the ML Engine groups stations based on their *live* atmospheric behavior (Thermal, Convective, Stable).")
    
    selected_time_t3 = st.select_slider("Forecast Timeline", options=timeline_str, key="t3_slider", label_visibility="collapsed")
    df_time_t3 = df_all[df_all["Time"] == selected_time_t3].copy()
    
    conditions = [
        (df_time_t3['Storm Probability'] > 30),
        (df_time_t3['Fog Probability'] > 50),
        (df_time_t3['Temperature'] >= 48),
        (df_time_t3['Wind Speed'] > 35)
    ]
    choices = ['Convective/Storm', 'Fog/Low Vis', 'Extreme Heat', 'High Wind']
    df_time_t3['AI Cluster'] = np.select(conditions, choices, default='Stable/Clear')
    
    color_map = {'Convective/Storm': '#EF4444', 'Fog/Low Vis': '#94A3B8', 'Extreme Heat': '#F97316', 'High Wind': '#D97706', 'Stable/Clear': '#10B981'}
    
    fig3 = px.scatter_mapbox(df_time_t3, lat="Latitude", lon="Longitude", color="AI Cluster", size_max=15, zoom=6, center=dict(lat=24.4, lon=54.6), mapbox_style="white-bg", color_discrete_map=color_map, hover_name="Station", hover_data={"Temperature": True, "Storm Probability": True})
    fig3.update_traces(marker=dict(size=12, opacity=0.9))
    fig3.update_layout(mapbox_layers=esri_topo_layer, margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig3, use_container_width=True, key="cluster_map_data")

with tab4:
    selected_time_t4 = st.select_slider("Forecast Timeline", options=timeline_str, key="t4_slider", label_visibility="collapsed")
    df_time_t4 = df_all[df_all["Time"] == selected_time_t4].copy()
    
    st.markdown(f"<h3 style='color:#082F49; font-weight:900;'>📊 Full 34-Station Matrix at {selected_time_t4}</h3>", unsafe_allow_html=True)
    display_df = df_time_t4.sort_values(by="Temperature", ascending=False)
    html_table = "<table class='custom-table'><tr><th>Station</th><th>Temp (°C)</th><th>Wind (km/h)</th><th>Fog Prob (%)</th><th>Storm (%)</th><th>Radar (dBZ)</th></tr>"
    for _, row in display_df.iterrows():
        s_color = "#EF4444" if row['Storm Probability'] >= 75 else "#082F49"
        f_color = "#64748B" if row['Fog Probability'] >= 60 else "#082F49"
        dbz_color = "#7E22CE" if row['dBZ'] >= 45 else ("#10B981" if row['dBZ'] > 0 else "#64748B")
        html_table += f"<tr><td>{row['Station']}</td><td>{row['Temperature']}°C</td><td>{row['Wind Speed']} km/h</td><td style='color:{f_color}; font-weight:bold;'>{row['Fog Probability']}%</td><td style='color:{s_color};'>{row['Storm Probability']}%</td><td style='color:{dbz_color}; font-weight:900;'>{row['dBZ']}</td></tr>"
    html_table += "</table>"
    st.markdown(html_table, unsafe_allow_html=True)

with tab5:
    st.markdown('<h4 style="color:#082F49; font-weight:900;">🤖 JM72 AI Data Assistant (Interactive Chatbot)</h4>', unsafe_allow_html=True)
    st.write("Ask the AI to instantly analyze the massive weather matrix for you.")
    
    prompt = st.chat_input("Ask a question (e.g., 'What is the hottest station right now?')")
    if prompt:
        st.chat_message("user").write(prompt)
        p_lower = prompt.lower()
        response = ""
        current_data = df_all[df_all["Time"] == timeline_str[0]]
        
        if "hot" in p_lower or "أعلى حرارة" in p_lower:
            hot_st = current_data.loc[current_data["Temperature"].idxmax()]
            response = f"The hottest station right now is **{hot_st['Station']}** recording **{hot_st['Temperature']}°C**."
        elif "storm" in p_lower or "عاصفة" in p_lower or "rain" in p_lower:
            stormy = current_data[current_data["Storm Probability"] > 40]
            if not stormy.empty: response = f"Stations with storm risk > 40%: {', '.join(stormy['Station'].tolist())}."
            else: response = "Currently, there are no stations with a storm probability above 40%."
        elif "fog" in p_lower or "ضباب" in p_lower:
            foggy = current_data[current_data["Fog Probability"] > 50]
            if not foggy.empty: response = f"High fog risk detected at: {', '.join(foggy['Station'].tolist())}."
            else: response = "No significant fog risk detected at this hour."
        else:
            response = "I am the JM72 AI Assistant. I can currently answer questions about the 'hottest station', 'storm risks', and 'fog predictions'. Try asking one of those!"
            
        st.chat_message("assistant").write(response)
    else:
        st.chat_message("assistant").write("Hello Jumah! I am ready to analyze the 34-station data array. What would you like to know?")

with tab6:
    st.markdown("### 🚨 JM72 Alert Control Room")
    st.info("ℹ️ The automated email alert engine has been permanently physically severed from the codebase to ensure zero spam. Alerts will only trigger visually inside this dashboard.")
