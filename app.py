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
# 1. PLATFORM SETTINGS & STRICT CSS FIXES
# ==========================================
st.set_page_config(page_title="JM72 AI Weather Model", layout="wide")
st_autorefresh(interval=15 * 60 * 1000, key="data_refresh")

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC !important; }
    .stApp p, .stApp span, .stApp label, div[data-testid="stTickBar"] { color: #082F49 !important; font-weight: 900 !important; font-size: 16px !important; }
    
    button[data-baseweb="tab"] { background-color: #FFFFFF !important; border: 2px solid #E2E8F0 !important; border-radius: 8px 8px 0 0 !important; margin-right: 5px !important; padding: 10px 20px !important; }
    button[data-baseweb="tab"] p { font-size: 18px !important; color: #475569 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { background-color: #082F49 !important; border-color: #082F49 !important; }
    button[data-baseweb="tab"][aria-selected="true"] p { color: #FFFFFF !important; }

    .alert-banner { background-color: #FEF2F2; color: #991B1B !important; padding: 18px; border-left: 6px solid #EF4444; border-radius: 8px; font-size: 16px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); line-height: 1.6; }
    .sys-success { background-color: #F0FDF4; color: #065F46 !important; padding: 15px; border-left: 6px solid #10B981; border-radius: 8px; font-weight: bold; font-size: 16px; margin-bottom: 20px; }
    .sys-warning { background-color: #FEF9C3; color: #854D0E !important; padding: 15px; border-left: 6px solid #EAB308; border-radius: 8px; font-weight: bold; font-size: 16px; margin-bottom: 20px; }
    
    .custom-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .custom-table th { background-color: #082F49; color: #ffffff; font-weight: bold; padding: 12px; text-align: center; }
    .custom-table td { padding: 12px; border: 1px solid #e2e8f0; color: #1e293b; font-weight: bold; text-align: center; }
</style>
""", unsafe_allow_html=True)

# IDENTITY LOGO & BANNER WITH ENFORCED WHITE TEXT VISIBILITY
jm72_logo_svg = """<svg width="130" height="65" viewBox="0 0 130 65" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="desertGold" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#FDE047" /><stop offset="50%" stop-color="#D4AF37" /><stop offset="100%" stop-color="#9A3412" /></linearGradient><linearGradient id="seaSky" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#38BDF8" /><stop offset="100%" stop-color="#0369A1" /></linearGradient><linearGradient id="bgDark" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="#0F172A" /><stop offset="100%" stop-color="#082F49" /></linearGradient></defs><rect width="130" height="65" rx="12" fill="url(#bgDark)" stroke="url(#desertGold)" stroke-width="2"/><path d="M0,65 Q35,40 65,65 T130,55 L130,65 L0,65 Z" fill="url(#seaSky)" opacity="0.5"/><path d="M0,65 Q25,48 55,65 T130,58 L130,65 L0,65 Z" fill="url(#desertGold)" opacity="0.8"/><text x="65" y="44" font-family="'Segoe UI', Tahoma, sans-serif" font-weight="900" font-size="32" text-anchor="middle" letter-spacing="2"><tspan fill="#FFFFFF">J</tspan><tspan fill="url(#seaSky)">M</tspan><tspan fill="url(#desertGold)">72</tspan></text></svg>"""

st.markdown(f'''
<div style="background-color: #082F49; padding: 25px; border-radius: 12px; text-align: center; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 25px; border-bottom: 3px solid #D4AF37;">
    {jm72_logo_svg}
    <h1 style="margin: 0 0 0 25px !important; color: #FFFFFF !important; font-weight: 900 !important; font-size: 34px !important; letter-spacing: 1px; font-family: 'Segoe UI', sans-serif;">JM72 AI Weather Model</h1>
</div>
''', unsafe_allow_html=True)

# ==========================================
# 2. REST-API LIVE DATA AGENT & UAE TIMEZONE
# ==========================================
stations = {
    "Al Hajar Mountains": {"lat": 25.3, "lon": 56.1, "type": "Mountains"},
    "Fujairah Coast": {"lat": 25.12, "lon": 56.32, "type": "Mountains"},
    "Al Ain": {"lat": 24.19, "lon": 55.76, "type": "Inland"},
    "Al Dhafra": {"lat": 23.65, "lon": 53.70, "type": "Desert"},
    "Abu Dhabi": {"lat": 24.45, "lon": 54.37, "type": "Coast"}
}

# Synced to UAE Local Time (UTC+4)
uae_time = datetime.utcnow() + timedelta(hours=4)
base_date = uae_time.replace(minute=0, second=0, microsecond=0)
timeline = [base_date + timedelta(hours=i*3) for i in range(8 * 5)]
timeline_str = [dt.strftime('%d %b - %H:%M') for dt in timeline]

@st.cache_data(ttl=3600)
def fetch_stable_live_data():
    try:
        lats = ",".join([str(s["lat"]) for s in stations.values()])
        lons = ",".join([str(s["lon"]) for s in stations.values()])
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly=temperature_2m,cape,winddirection_10m,relative_humidity_700hPa&models=gfs_seamless&timezone=auto"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        return False, str(e)

with st.spinner("🤖 Ingesting and analyzing live atmospheric data runs..."):
    fetch_success, live_data = fetch_stable_live_data()

# ==========================================
# 3. JM72 AI DYNAMICS ENGINE (STRICT FILTERS)
# ==========================================
weather_data = []

if fetch_success and type(live_data) is list:
    st.markdown('<div class="sys-success">🟢 LIVE OPERATIONS ACTIVE: Model dynamically executing orographic convergence & climatological physics grid.</div>', unsafe_allow_html=True)
    
    for idx, (name, coords) in enumerate(stations.items()):
        station_data = live_data[idx]["hourly"]
        api_times = [datetime.fromisoformat(t).replace(tzinfo=None) for t in station_data["time"]]
        
        for dt_str, dt in zip(timeline_str, timeline):
            try:
                time_diffs = [abs((api_t - dt).total_seconds()) for api_t in api_times]
                closest_idx = time_diffs.index(min(time_diffs))
                
                temp_c = station_data["temperature_2m"][closest_idx] or 35.0
                cape_val = station_data["cape"][closest_idx] or 0
                rh_700 = station_data["relative_humidity_700hPa"][closest_idx] or 0
                wind_dir = station_data["winddirection_10m"][closest_idx] or 0
                
                # Strict Filtering Matrix
                prob = (cape_val / 2000) * 100
                if rh_700 < 45: 
                    prob *= 0.05
                elif rh_700 < 55:
                    prob *= 0.3
                    
                if coords["type"] == "Mountains":
                    if 90 <= wind_dir <= 180:
                        prob *= 1.4
                    if temp_c > 38:
                        prob *= 1.2
                else:
                    prob *= 0.15
                
                storm_prob = np.clip(prob, 0, 100)
                
            except Exception:
                temp_c = 36.0
                storm_prob = 0.0

            weather_data.append({
                "Time": dt_str,
                "DateOnly": dt.strftime('%d %b'),
                "Station": name,
                "Latitude": coords["lat"],
                "Longitude": coords["lon"],
                "Storm Probability": round(storm_prob),
                "Temperature": round(temp_c, 1)
            })
else:
    st.markdown(f'<div class="sys-warning">⚠️ MET-ENGINE WARNING: Operating on Local Simulated Expert Physics Node.</div>', unsafe_allow_html=True)
    np.random.seed(42)
    for dt_str, dt in zip(timeline_str, timeline):
        hour = dt.hour
        is_afternoon = 12 <= hour <= 18
        for name, coords in stations.items():
            base_storm = 75 if (is_afternoon and coords["type"] == "Mountains") else 0
            temp = 42 + np.random.uniform(-3, 4)
            weather_data.append({
                "Time": dt_str,
                "DateOnly": dt.strftime('%d %b'),
                "Station": name,
                "Latitude": coords["lat"],
                "Longitude": coords["lon"],
                "Storm Probability": round(np.clip(base_storm + np.random.uniform(-5, 10), 0, 100)) if base_storm > 0 else 0,
                "Temperature": round(temp, 1)
            })

df_all = pd.DataFrame(weather_data)

# ==========================================
# 4. GLOBAL CONTROLS & BRIEFINGS (BILINGUAL NOTICES)
# ==========================================
st.markdown('<h4 style="color:#082F49; font-weight:900; margin-bottom:15px;">📋 5-Day Fast Briefing Matrix</h4>', unsafe_allow_html=True)
unique_dates = df_all["DateOnly"].unique()[:5]
cols = st.columns(len(unique_dates))
for i, date in enumerate(unique_dates):
    daily_max = df_all[df_all["DateOnly"] == date]["Storm Probability"].max()
    with cols[i]:
        # Alerts/Briefings show Bilingual statuses based on threshold
        if daily_max >= 75:
            st.error(f"🔴 **{date}**\n\n**Severe Convective Risk**\nخطر روايح شديد\n\n### {daily_max}%")
        elif daily_max >= 40:
            st.warning(f"🟡 **{date}**\n\n**Localized Convection**\nتكونات محلية محتملة\n\n### {daily_max}%")
        else:
            st.success(f"🟢 **{date}**\n\n**Atmosphere Stable**\nالاستقرار سيد الموقف\n\n### {daily_max}%")

st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
st.markdown('<h4 style="color:#082F49; font-weight:900;">⏱️ Interactive Operational Forecast Timeline (UAE Local Time):</h4>', unsafe_allow_html=True)
selected_time = st.select_slider("Select Time Check", options=timeline_str, label_visibility="collapsed")
df_time = df_all[df_all["Time"] == selected_time].copy()
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. THREE-TAB PROFESSIONAL INTERFACE
# ==========================================
tab1, tab2, tab3 = st.tabs(["🌩️ Orographic Thunderstorms (Radar)", "🔥 Heat Dome Tracker", "📋 Live Data & Model Matrix"])

with tab1:
    # Critical Convective Alert Check (Bilingual)
    max_storm = df_time["Storm Probability"].max()
    if max_storm >= 75:
        target = df_time.loc[df_time["Storm Probability"].idxmax(), "Station"]
        st.markdown(f'''
        <div class="alert-banner">
            <strong>🚨 RED ALERT:</strong> Severe Convective Storm Risk ({max_storm}%) detected over {target} at the selected hour!<br>
            <strong>🚨 إنذار أحمر:</strong> رصد احتمالية عاصفة رعدية شديدة (روايح) بنسبة ({max_storm}%) فوق منطقة {target} في الوقت المحدد!
        </div>
        ''', unsafe_allow_html=True)
    
    df_plot_storm = df_time[df_time["Storm Probability"] > 0].copy()
    if df_plot_storm.empty:
        st.info("✅ Stable Sky Conditions: No convective storm development expected for this specific hour.")
    else:
        fig1 = px.scatter_mapbox(df_plot_storm, lat="Latitude", lon="Longitude", color="Storm Probability", size="Storm Probability",
                                mapbox_style="open-street-map", zoom=6, color_continuous_scale=["#FEF08A", "#F59E0B", "#EF4444", "#7F1D1D"], range_color=[0, 100])
        fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig1, use_container_width=True)
        
    st.markdown
