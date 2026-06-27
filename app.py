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
import smtplib
from email.mime.text import MIMEText
from email.header import Header

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
    html, body, [data-testid="stAppViewContainer"], .stApp, #root { background-color: #F8FAFC !important; }
    .block-container { background-color: #FFFFFF !important; border-radius: 12px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important; padding: 2rem !important; margin: 1rem auto !important; border: 1px solid #E2E8F0 !important; max-width: 95% !important;}
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; visibility: hidden !important;}
    .stApp p, .stApp span, .stApp label, div[data-testid="stTickBar"], h1, h2, h3, h4, h5, h6 { color: #082F49 !important; font-weight: 900 !important; font-size: 15px !important; }
    
    div[data-testid="stTabs"] [data-baseweb="tab-list"] { border-bottom: 2px solid #CBD5E1 !important; }
    div[data-testid="stTabs"] button { background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-radius: 8px 8px 0 0 !important; margin-right: 5px !important; padding: 10px 20px !important; }
    div[data-testid="stTabs"] button[aria-selected="true"] { background-color: #082F49 !important; border-color: #082F49 !important; }
    div[data-testid="stTabs"] button[aria-selected="true"] p { color: #FFFFFF !important; }
    
    .ai-broadcaster { background: linear-gradient(90deg, #F0F9FF, #E0F2FE); border-left: 5px solid #0284C7; padding: 15px 20px; border-radius: 8px; font-size: 16px; font-weight: bold; color: #0369A1; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(2, 132, 199, 0.1); }
    
    div[data-testid="stSlider"] { background-color: #F1F5F9 !important; padding: 20px !important; border-radius: 12px !important; margin-bottom: 25px !important; border: 1px solid #E2E8F0 !important; }
    div[data-testid="stTickBar"] { color: #475569 !important; font-weight: bold !important; }
    div[data-testid="stSlider"] div[role="slider"] { background-color: #0284C7 !important; border: 2px solid #FFF !important; }
    
    .table-responsive { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .custom-table { width: 100%; border-collapse: collapse; background-color: #ffffff; min-width: 850px; }
    .custom-table th { background-color: #082F49; color: #ffffff !important; padding: 14px; text-align: center; border-bottom: 3px solid #D4AF37; white-space: nowrap;}
    .custom-table td { padding: 14px; border-bottom: 1px solid #F1F5F9; border-right: 1px solid #F1F5F9; color: #082F49 !important; font-weight: 800; text-align: center; white-space: nowrap;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CENTERED LOGO (71wm)
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
# 4. INITIALIZE LIVE STATES
# ==========================================
st_autorefresh(interval=15 * 60 * 1000, key="data_refresh")

if "admin_password" not in st.session_state: st.session_state["admin_password"] = "Jumah71"  # الرمز الافتراضي الأولي
if "admin_logged_in" not in st.session_state: st.session_state["admin_logged_in"] = False
if "email_enabled" not in st.session_state: st.session_state["email_enabled"] = False
if "email_sender" not in st.session_state: st.session_state["email_sender"] = ""
if "email_receiver" not in st.session_state: st.session_state["email_receiver"] = ""
if "email_password" not in st.session_state: st.session_state["email_password"] = ""
if "email_sent_track" not in st.session_state: st.session_state["email_sent_track"] = {}

def send_secure_alert_email(subject, body_text):
    if not st.session_state["email_enabled"]: return False
    if not st.session_state["email_sender"] or not st.session_state["email_password"]: return False
    
    try:
        msg = MIMEText(body_text, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = st.session_state["email_sender"]
        msg['To'] = st.session_state["email_receiver"]
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(st.session_state["email_sender"], st.session_state["email_password"])
        server.sendmail(st.session_state["email_sender"], [st.session_state["email_receiver"]], msg.as_string())
        server.quit()
        return True
    except Exception:
        return False

# ==========================================
# 5. TIMELINE & STATIONS MATRIX
# ==========================================
days_en = {"Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed", "Thursday": "Thu", "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"}
uae_time = datetime.utcnow() + timedelta(hours=4)
base_date = uae_time.replace(minute=0, second=0, microsecond=0)
timeline = [base_date + timedelta(hours=i*3) for i in range(8 * 5)]
timeline_str = [f"{days_en[dt.strftime('%A')]} {dt.strftime('%d')} - {dt.strftime('%H:%M')}" for dt in timeline]
unique_dates_display = []
for dt in timeline:
    d_str = f"{days_en[dt.strftime('%A')]} {dt.strftime('%d')}"
    if d_str not in unique_dates_display: unique_dates_display.append(d_str)

stations_matrix = {
    "Abu Dhabi": {"lat": 24.4760, "lon": 54.3290, "type": "Coast"}, "ADNOC HQ": {"lat": 24.4621, "lon": 54.3241, "type": "Coast"},
    "Burj Khalifah": {"lat": 25.2017, "lon": 55.2766, "type": "Coast"}, "Sharjah University": {"lat": 25.2869, "lon": 55.4622, "type": "Coast"},
    "Ajman": {"lat": 25.4236, "lon": 55.4447, "type": "Coast"}, "Umm Al Quwain": {"lat": 25.5301, "lon": 55.6548, "type": "Coast"},
    "Ras Al khaimah": {"lat": 25.7716, "lon": 55.9392, "type": "Coast"}, "Fujairah Port": {"lat": 25.1699, "lon": 56.3595, "type": "Coast"},
    "Kalba": {"lat": 25.0430, "lon": 56.3640, "type": "Coast"}, "Khor Fakkan Port": {"lat": 25.3578, "lon": 56.3618, "type": "Coast"},
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
    "Eastern Region": ["Fujairah Port", "Fujairah Int'l Airport", "Hatta", "Al Tawiyen", "Al Heben", "AlQor", "Kalba", "Khor Fakkan Port"]
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

with st.spinner("🤖 71wm AI Engine: Compiling live metrics & computing Orographic Drizzle index..."):
    fetch_success, live_data = fetch_stable_live_data(stations_matrix)

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
                    closest_idx = [abs((api_t - dt).total_seconds()) for api_t in api_times].index(min([abs((api_t - dt).total_seconds()) for api_t in api_times]))
                    
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
                    if dt.hour < 12 or dt.hour > 19: prob *= 0.1
                    storm_prob = np.clip(prob, 0, 100)
                    
                    # Fog AI
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
                    
                    # AL-KOUS OROGRAPHIC DRIZZLE ENGINE
                    drizzle_prob = 0
                    if coords["lon"] >= 55.8:
                        is_drizzle_window = 3 <= dt.hour <= 9 
                        if is_drizzle_window and 45 <= wind_dir <= 160 and surface_rh >= 85 and cloud_low >= 75:
                            drizzle_calc = ((surface_rh - 85) * 4) + ((cloud_low - 75) * 2) + (wind_spd * 0.8)
                            drizzle_prob = np.clip(drizzle_calc, 0, 100)

                except Exception: temp_c, app_temp, storm_prob, fog_prob, alkous_prob, drizzle_prob = 36.0, 36.0, 0.0, 0.0, 0.0, 0.0

                weather_data.append({
                    "Time": dt_str, "DateOnly": f"{days_en[dt.strftime('%A')]} {dt.strftime('%d')}", 
                    "Station": name, "Zone": zone_mapped, "Latitude": coords["lat"], "Longitude": coords["lon"],
                    "Storm Probability": round(storm_prob), "Fog Probability": round(fog_prob), 
                    "AlKous Prob": round(alkous_prob), "Drizzle Prob": round(drizzle_prob),
                    "Temperature": round(temp_c, 1), "Apparent Temp": round(app_temp, 1), "Humidity": round(surface_rh),
                })
        except Exception: pass

df_all = pd.DataFrame(weather_data)

# ==========================================
# 7. CRITICAL ANTI-SPAM ALERTS LOGIC
# ==========================================
current_time_df = df_all[df_all["Time"] == timeline_str[0]]
max_storm_now = current_time_df["Storm Probability"].max()
max_drizzle_now = current_time_df["Drizzle Prob"].max()

if st.session_state["email_enabled"]:
    today_key = unique_dates_display[0]
    if today_key not in st.session_state["email_sent_track"]:
        st.session_state["email_sent_track"][today_key] = {"storm": False, "drizzle": False}
        
    if max_storm_now >= 75 and not st.session_state["email_sent_track"][today_key]["storm"]:
        sub = "🚨 71wm AI Model: Severe Convective Storm Warning Detected"
        body = f"Alert Triggered on {today_key}.\nSevere convective storm risk reached {max_storm_now}% over mountain terrains."
        if send_secure_alert_email(sub, body): st.session_state["email_sent_track"][today_key]["storm"] = True
            
    if max_drizzle_now >= 60 and not st.session_state["email_sent_track"][today_key]["drizzle"]:
        sub = "🌧️ 71wm AI Model: Orographic Al-Kous Drizzle Warning"
        body = f"Alert Triggered on {today_key}.\nMechanical orographic saturation caused drizzle index to reach {max_drizzle_now}% over the Eastern Ridges."
        if send_secure_alert_email(sub, body): st.session_state["email_sent_track"][today_key]["drizzle"] = True

# ==========================================
# 8. AI GENERATIVE BRIEFING
# ==========================================
ai_briefing = f"🤖 **71wm AI Broadcaster:** "
if max_drizzle_now > 40: ai_briefing += f"🌧️ **🚨 Al-Kous Orographic Drizzle Warning:** High risk ({max_drizzle_now}%) of morning drizzle forming over the eastern maritime ridges. "
elif current_time_df["AlKous Prob"].max() > 50: ai_briefing += f"⚠️ High probability ({current_time_df['AlKous Prob'].max()}%) of dense Al-Kous low-level stratus capping the Eastern Coastline. "
else: ai_briefing += "Atmospheric columns remain thermodynamically stable with no localized anomalies detected."

st.markdown(f'<div class="ai-broadcaster">{ai_briefing}</div>', unsafe_allow_html=True)

# ==========================================
# 9. TABS INTERFACE
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🌩️ Storms & Fog", "🔥 Heat & Anomalies", "☁️ Al-Kous & Drizzle", "📋 Model Matrix", "🤖 71wm AI Assistant", "⚙️ Control Room"
])

# (محتويات التبويبات من 1 إلى 5 تبقى ثابتة ومكتملة تماماً كما هي)
with tab1:
    st.markdown('<h4 style="color:#082F49; font-weight:900; margin-bottom:15px;">📋 5-Day Storm & Fog Forecast (National)</h4>', unsafe_allow_html=True)
    cols_t1 = st.columns(5)
    for i, date in enumerate(unique_dates_display[:5]):
        day_df = df_all[df_all["DateOnly"] == date]
        m_s, m_f = int(day_df["Storm Probability"].max()), int(day_df["Fog Probability"].max())
        bg = "#FEF2F2" if max(m_s, m_f) >= 60 else ("#FFFBEB" if max(m_s, m_f) >= 30 else "#F0FDF4")
        cols_t1[i].markdown(f"<div style='background-color:{bg}; border: 1px solid #CBD5E1; border-radius: 8px; padding: 15px; text-align:center;'><div style='color:#082F49; font-size:15px; font-weight:900; margin-bottom:12px;'>📅 {date}</div><div style='font-size:16px; font-weight:900; color:#EF4444; margin-bottom:8px;'>⛈️ Storm: {m_s}%</div><div style='font-size:16px; font-weight:900; color:#64748B;'>🌫️ Fog: {m_f}%</div></div>", unsafe_allow_html=True)
    selected_time_t1 = st.select_slider("Forecast Timeline", options=timeline_str, key="t1_slider", label_visibility="collapsed")
    df_time_t1 = df_all[df_all["Time"] == selected_time_t1].copy()
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.density_mapbox(df_time_t1, lat="Latitude", lon="Longitude", z="Storm Probability", radius=45, center=dict(lat=24.4, lon=54.6), zoom=5.5, mapbox_style="white-bg", opacity=0.75, color_continuous_scale=["rgba(0,0,0,0)", "#A3E635", "#FDE047", "#EF4444", "#7E22CE"], range_color=[0, 100]).update_layout(mapbox_layers=[{"below": 'traces', "sourcetype": "raster", "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"]}], margin={"r":0,"t":0,"l":0,"b":0}), use_container_width=True)
    c2.plotly_chart(px.density_mapbox(df_time_t1, lat="Latitude", lon="Longitude", z="Fog Probability", radius=45, center=dict(lat=24.4, lon=54.6), zoom=5.5, mapbox_style="white-bg", opacity=0.8, color_continuous_scale=["rgba(0,0,0,0)", "#E2E8F0", "#94A3B8", "#475569"], range_color=[0, 100]).update_layout(mapbox_layers=[{"below": 'traces', "sourcetype": "raster", "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"]}], margin={"r":0,"t":0,"l":0,"b":0}), use_container_width=True)
    st.markdown('<hr><h3 style="color:#082F49; font-weight:900;">🛰️ Live Telemetry: Satellite Cloud Imagery</h3>', unsafe_allow_html=True)
    components.html("""<div style="position: relative; width: 100%; height: 500px; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); background-color: #F8FAFC;"><iframe width="100%" height="520" src="https://embed.windy.com/embed.html?type=map&location=coordinates&overlay=satellite&lat=24.6&lon=54.8&zoom=6" frameborder="0" style="position: absolute; top: 0; left: 0;"></iframe><div style="position: absolute; bottom: 0px; right: 0px; width: 180px; height: 35px; background: rgba(8, 47, 73, 0.95); display: flex; align-items: center; justify-content: center; border-top-left-radius: 10px; border: 1px solid #D4AF37;"><span style="color: #D4AF37; font-family: sans-serif; font-size: 14px; font-weight: 900;">🛰️ 71wm SATELLITE LIVE</span></div></div>""", height=520)

with tab2:
    st.markdown('<h4 style="color:#082F49; font-weight:900; margin-bottom:15px;">📋 5-Day Thermal Range (Min-Max By Zone)</h4>', unsafe_allow_html=True)
    cols_t2 = st.columns(5)
    for i, date in enumerate(unique_dates_display[:5]):
        day_df = df_all[df_all["DateOnly"] == date]
        c_mx, c_mn = round(day_df[day_df["Zone"] == "Coast"]["Temperature"].max(), 1), round(day_df[day_df["Zone"] == "Coast"]["Temperature"].min(), 1)
        m_mx, m_mn = round(day_df[day_df["Zone"] == "Mountains"]["Temperature"].max(), 1), round(day_df[day_df["Zone"] == "Mountains"]["Temperature"].min(), 1)
        i_mx, i_mn = round(day_df[day_df["Zone"] == "Inland"]["Temperature"].max(), 1), round(day_df[day_df["Zone"] == "Inland"]["Temperature"].min(), 1)
        cols_t2[i].markdown(f"<div style='background-color:#F0FDF4; border: 1px solid #CBD5E1; border-radius: 8px; padding: 15px;'><div style='color:#082F49; font-size:15px; font-weight:900; margin-bottom:12px; text-align:center;'>📅 {date}</div><div style='display: flex; justify-content: space-between; font-size:14px;'><span>🌊 Coast:</span><b>⬇ {c_mn}° - ⬆ {c_mx}°</b></div><div style='display: flex; justify-content: space-between; font-size:14px;'><span>⛰️ Mount:</span><b>⬇ {m_mn}° - ⬆ {m_mx}°</b></div><div style='display: flex; justify-content: space-between; font-size:14px;'><span>🏜️ Inland:</span><b>⬇ {i_mn}° - ⬆ {i_mx}°</b></div></div>", unsafe_allow_html=True)

with tab3:
    st.markdown('<h4 style="color:#082F49; font-weight:900; margin-bottom:15px;">☁️ Al-Kous Stratus & Orographic Drizzle Radar Tracker</h4>', unsafe_allow_html=True)
    cols_t3 = st.columns(5)
    for i, date in enumerate(unique_dates_display[:5]):
        day_df = df_all[df_all["DateOnly"] == date]
        mx_k, mx_dr = int(day_df["AlKous Prob"].max()), int(day_df["Drizzle Prob"].max())
        bg = "#FEF2F2" if mx_dr > 40 else "#F8FAFC"
        cols_t3[i].markdown(f"<div style='background-color:{bg}; border: 1px solid #CBD5E1; border-radius: 8px; padding: 15px; text-align:center;'><div style='color:#082F49; font-size:14px; font-weight:900;'>📅 {date}</div><div style='color:#1E293B; font-weight:bold; margin-top:5px;'>☁️ الكوس: {mx_k}%</div><div style='color:#0284C7; font-weight:900;'>🌧️ الرذاذ: {mx_dr}%</div></div>", unsafe_allow_html=True)
    selected_time_t3 = st.select_slider("Forecast Timeline", options=timeline_str, key="t3_slider", label_visibility="collapsed")
    df_time_t3 = df_all[df_all["Time"] == selected_time_t3].copy()
    east_stations = df_time_t3[df_time_t3["Longitude"] >= 55.8].copy()
    fig3 = px.density_mapbox(east_stations, lat="Latitude", lon="Longitude", z="Drizzle Prob", radius=45, center=dict(lat=25.2, lon=56.2), zoom=7.5, mapbox_style="white-bg", opacity=0.85, color_continuous_scale=["rgba(0,0,0,0)", "#BAE6FD", "#38BDF8", "#0284C7", "#0369A1"], range_color=[0, 100], title="AI Orographic Drizzle Condensation Index (%)")
    fig3.update_layout(mapbox_layers=[{"below": 'traces', "sourcetype": "raster", "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"]}], margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig3, use_container_width=True, key="kous_drizzle_map")

with tab4:
    selected_time_t4 = st.select_slider("Forecast Timeline", options=timeline_str, key="t4_slider", label_visibility="collapsed")
    df_time_t4 = df_all[df_all["Time"] == selected_time_t4].copy()
    st.markdown(f"<h3 style='color:#082F49; font-weight:900;'>📊 Full 36-Station Atmospheric Matrix</h3>", unsafe_allow_html=True)
    display_df = df_time_t4.sort_values(by="Temperature", ascending=False)
    html_table = "<div class='table-responsive'><table class='custom-table'><tr><th>Station</th><th>Actual Temp</th><th>Feels Like</th><th>RH (%)</th><th>Al-Kous (%)</th><th>Morning Drizzle (%)</th><th>Convective Storm (%)</th></tr>"
    for _, row in display_df.iterrows():
        s_color = "#EF4444" if row['Storm Probability'] >= 75 else "#082F49"
        dr_color = "#0284C7" if row['Drizzle Prob'] >= 40 else "#082F49"
        html_table += f"<tr><td>{row['Station']}</td><td>{row['Temperature']}°C</td><td>{row['Apparent Temp']}°C</td><td>{row['Humidity']}%</td><td>{row['AlKous Prob']}%</td><td style='color:{dr_color}; font-weight:bold;'>{row['Drizzle Prob']}%</td><td style='color:{s_color};'>{row['Storm Probability']}%</td></tr>"
    st.markdown(html_table + "</table></div>", unsafe_allow_html=True)

with tab5:
    st.markdown('<h4 style="color:#082F49; font-weight:900;">🤖 71wm AI Data Assistant</h4>', unsafe_allow_html=True)
    prompt = st.chat_input("Ask about parameters...")
    if prompt:
        st.chat_message("user").write(prompt)
        p_l = prompt.lower()
        curr = df_all[df_all["Time"] == timeline_str[0]]
        if "drizzle" in p_l or "رذاذ" in p_l:
            dr_stations = curr[curr["Drizzle Prob"] > 30]
            res = f"🌧️ Drizzle mapped at: {', '.join(dr_stations['Station'].tolist())}." if not dr_stations.empty else "No microclimatic drizzle mapped."
        else: res = "I am ready. Ask me to extract parameters from the 36 channels."
        st.chat_message("assistant").write(res)

# ==========================================
# 🛑 TABS 6: SECURE CONTROL ROOM (WITH PASSWORD MANAGEMENT)
# ==========================================
with tab6:
    st.markdown("### ⚙️ 71wm Secure Control Room")
    
    # بوابه جدار الحماية - التحقق من القفل
    if not st.session_state["admin_logged_in"]:
        st.warning("🔒 هذه الغرفة مقفلة أمنياً ومخصصة لمدير النظام فقط.")
        st.write("الرجاء إدخال الرمز السري للوصول إلى إعدادات النظام:")
        
        # الكود يقارن الآن بالرمز المخزن ديناميكياً في الـ session_state
        admin_pwd = st.text_input("الرمز السري الحالي (PIN):", type="password", key="login_pin_input")
        
        if st.button("🔓 فتح الغرفة"):
            if admin_pwd == st.session_state["admin_password"]:
                st.session_state["admin_logged_in"] = True
                st.rerun()
            else:
                st.error("❌ الرمز السري غير صحيح، تم رفض الوصول.")
                
    else:
        st.success("✅ تم فتح القفل. أهلاً بك في غرفة التحكم الآمنة.")
        
        col_logout, col_empty = st.columns([2, 8])
        with col_logout:
            if st.button("🔒 قفل الغرفة (تسجيل الخروج)"):
                st.session_state["admin_logged_in"] = False
                st.rerun()
            
        st.markdown("---")
        
        # ----------------------------------------------------
        # 🔑 الميزة الجديدة: قسم تغيير الرمز السري من الواجهة
        # ----------------------------------------------------
        st.markdown("#### 🔑 تغيير الرمز السري للمشرف")
        st.write("يمكنك تحديث رمز الدخول الخاص بالمنصة من هنا مباشرة دون الحاجة لتغيير الكود:")
        
        new_pwd_input = st.text_input("أدخل الرمز السري الجديد:", type="password", key="change_pin_field")
        
        if st.button("💾 حفظ الرمز السري الجديد"):
            if new_pwd_input.strip() != "":
                # تحديث الرمز في ذاكرة السيرفر الحية فوراً
                st.session_state["admin_password"] = new_pwd_input.strip()
                st.success("✅ تأكيد: تم تغيير الرمز السري بنجاح! سيتم اعتماده في المرة القادمة التي تقفل فيها الغرفة.")
            else:
                st.error("❌ خطأ: لا يمكن إدخال رمز سري فارغ.")
                
        st.markdown("---")
        st.markdown("#### 📧 إعدادات خادم التنبيهات والبريد الإلكتروني")
        st.session_state["email_enabled"] = st.checkbox("تفعيل نظام الإرسال التلقائي للإنذارات الطارئة (Email Alerts Active)", value=st.session_state["email_enabled"])
        st.session_state["email_sender"] = st.text_input("بريد المرسل (Gmail)", value=st.session_state["email_sender"])
        st.session_state["email_password"] = st.text_input("كلمة مرور التطبيقات السرية (16 حرفاً من جوجل)", type="password", value=st.session_state["email_password"])
        st.session_state["email_receiver"] = st.text_input("بريد المستلم الرئيسي للإشعارات", value=st.session_state["email_receiver"])
        
        if st.button("🔄 تصفير ذاكرة الإرسال لإعادة التجربة فوراً"):
            st.session_state["email_sent_track"] = {}
            st.success("تم تصفير الذاكرة! إذا كانت هناك حالة إنذار قائمة ومفتاح الإرسال مفعل، سيصلك إيميل فوراً.")
