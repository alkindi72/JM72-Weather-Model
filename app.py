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
    
    .log-box { background-color: #1E293B; color: #10B981; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 13px; height: 150px; overflow-y: auto; margin-bottom: 15px;}
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

if "admin_password" not in st.session_state: st.session_state["admin_password"] = "Jumah71"
if "admin_logged_in" not in st.session_state: st.session_state["admin_logged_in"] = False
if "email_enabled" not in st.session_state: st.session_state["email_enabled"] = False
if "email_sender" not in st.session_state: st.session_state["email_sender"] = ""
if "email_receiver" not in st.session_state: st.session_state["email_receiver"] = ""
if "email_password" not in st.session_state: st.session_state["email_password"] = ""
if "email_sent_track" not in st.session_state: st.session_state["email_sent_track"] = {}
if "alert_logs" not in st.session_state: st.session_state["alert_logs"] = []

def send_secure_alert_email(subject, html_body):
    if not st.session_state["email_enabled"]: 
        return False, "النظام معطل يدوياً"
    if not st.session_state["email_sender"] or not st.session_state["email_password"] or not st.session_state["email_receiver"]: 
        return False, "بيانات المرسل أو المستلم ناقصة"
    try:
        receivers_list = [email.strip() for email in st.session_state["email_receiver"].split(",") if email.strip()]
        if not receivers_list: return False, "تنسيق الإيميلات غير صحيح"

        msg = MIMEText(html_body, 'html', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = st.session_state["email_sender"]
        msg['To'] = ", ".join(receivers_list)
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(st.session_state["email_sender"], st.session_state["email_password"])
        server.sendmail(st.session_state["email_sender"], receivers_list, msg.as_string())
        server.quit()
        return True, f"تم بنجاح لـ {len(receivers_list)} مستلم(ين)"
    except Exception as e:
        return False, f"خطأ الخادم: {str(e)}"

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
    "المنطقة الشرقية": ["Fujairah Port", "Fujairah Int'l Airport", "Hatta", "Al Tawiyen", "Al Heben", "AlQor", "Kalba", "Khor Fakkan Port"],
    "المنطقة الوسطى": ["Al Dhaid", "Al Malaiha"],
    "أبوظبي ومنطقة الظفرة": ["Abu Dhabi", "ADNOC HQ", "Abu Al Abyad", "AlRuwais", "Sir Bani Yas", "Dalma", "Sir Bu Nair", "Al Wathbah", "Madinat Zayed", "Mukhariz", "Owtaid", "Zayed Int'l Airport", "Al Bateen Executive Airport"],
    "منطقة العين": ["Al Ain Int'l Airport", "Al Aamerah"],
    "دبي والإمارات الشمالية": ["Burj Khalifah", "Sharjah University", "Ajman", "Umm Al Quwain", "Ras Al khaimah", "Jabal Jais", "Jabal Al Rahba", "Dubai Int'l Airport", "Sharjah Int'l Airport", "Ras Al Khaimah Int'l Airport", "Al Maktoum Int'l Airport"]
}

def get_sector_for_station(station_name):
    for sector, stations in SECTOR_MAP.items():
        if station_name in stations: return sector
    return "مناطق متفرقة"

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
                    if dt.hour < 12 or dt.hour > 19: prob *= 0.1 # فلتر الإخماد الليلي للعواصف
                    storm_prob = np.clip(prob, 0, 100)
                    
                    # Fog AI
                    fog_prob = 0
                    if (dt.hour < 8 or dt.hour > 22) and surface_rh > 80 and wind_spd < 15:
                        fog_prob = np.clip(((surface_rh - 80) * 4) + ((15 - wind_spd) * 3), 0, 100)
                    
                    # Al-Kous AI
                    alkous_prob = 0
                    if coords["lon"] >= 55.8 and 45 <= wind_dir <= 160 and surface_rh >= 65:
                        alkous_base = ((surface_rh - 65) * 2) + (cloud_low * 0.5)
                        if temp_c >= 35: alkous_base *= 1.2
                        alkous_prob = np.clip(alkous_base, 0, 100)
                    
                    # Drizzle AI
                    drizzle_prob = 0
                    if coords["lon"] >= 55.8 and (3 <= dt.hour <= 9) and 45 <= wind_dir <= 160 and surface_rh >= 85 and cloud_low >= 75:
                        drizzle_prob = np.clip(((surface_rh - 85) * 4) + ((cloud_low - 75) * 2) + (wind_spd * 0.8), 0, 100)

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
# 7. CRITICAL ANTI-SPAM ALERTS LOGIC (HTML EMAILS)
# ==========================================
current_time_df = df_all[df_all["Time"] == timeline_str[0]]
max_storm_now = current_time_df["Storm Probability"].max()
max_drizzle_now = current_time_df["Drizzle Prob"].max()
max_fog_now = current_time_df["Fog Probability"].max()
current_time_stamp = datetime.now().strftime("%H:%M:%S")
now_dt = datetime.now()

def get_html_email_template(title, text, regions, start_dt, end_dt, header_color, text_color):
    start_str = start_dt.strftime("%d/%m/%Y - %H:%M")
    end_str = end_dt.strftime("%d/%m/%Y - %H:%M")
    return f"""
    <div dir="rtl" style="font-family: Arial, sans-serif; border: 1px solid #E2E8F0; max-width: 600px; margin: 0 auto; border-radius: 8px; overflow: hidden; background-color: #FFFFFF;">
        <div style="background-color: {header_color}; padding: 15px; text-align: center; border-bottom: 2px solid rgba(0,0,0,0.1);">
            <h2 style="margin: 0; color: #000; font-size: 22px;">{title}</h2>
        </div>
        <div style="padding: 20px;">
            <p style="font-size: 18px; font-weight: bold; color: #1E293B; line-height: 1.6; text-align: center;">{text}</p>
            <div style="background-color: #F8FAFC; border-radius: 6px; padding: 15px; margin-top: 20px; border: 1px solid #E2E8F0;">
                <p style="margin: 0 0 10px 0; font-size: 16px; color: #082F49;"><b>المناطق المتأثرة:</b> {regions}</p>
                <hr style="border: 0; border-top: 1px solid #CBD5E1; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <p style="margin: 0 0 10px 0; font-size: 16px; color: #334155;"><b>بداية التحذير:</b><br>{start_str}</p>
                    <p style="margin: 0; font-size: 16px; color: #334155;"><b>نهاية التحذير:</b><br>{end_str}</p>
                </div>
            </div>
        </div>
    </div>
    """

if st.session_state["email_enabled"]:
    today_key = unique_dates_display[0]
    if today_key not in st.session_state["email_sent_track"]:
        st.session_state["email_sent_track"][today_key] = {"storm": False, "drizzle": False, "fog": False}
        
    # 1. Storm Warning (65%)
    if max_storm_now >= 65 and not st.session_state["email_sent_track"][today_key]["storm"]:
        affected_stations = current_time_df[current_time_df["Storm Probability"] >= 65]["Station"].tolist()
        affected_regions = list(set([get_sector_for_station(st) for st in affected_stations]))
        regions_str = "، ".join(affected_regions)
        
        sub = "71 weather model: Storm Warning"
        html_body = get_html_email_template(
            "⛈️ أمطار رعدية ، ☁️ سحب ركامية",
            "فرصة تكون سحب ركامية يصاحبها أمطار ورياح نشطة إلى قوية السرعة مع السحب مثيرة للغبار.",
            regions_str, now_dt, now_dt + timedelta(hours=5), "#FDE047", "#1E293B"
        )
        success, msg_info = send_secure_alert_email(sub, html_body)
        if success:
            st.session_state["email_sent_track"][today_key]["storm"] = True
            st.session_state["alert_logs"].insert(0, f"[{current_time_stamp}] ✅ نجاح (عاصفة): {msg_info}")
            
    # 2. Drizzle Warning (60%)
    if max_drizzle_now >= 60 and not st.session_state["email_sent_track"][today_key]["drizzle"]:
        affected_stations = current_time_df[current_time_df["Drizzle Prob"] >= 60]["Station"].tolist()
        affected_regions = list(set([get_sector_for_station(st) for st in affected_stations]))
        regions_str = "، ".join(affected_regions)
        
        sub = "71 weather model: Al Kouse warning"
        html_body = get_html_email_template(
            "🌧️ رذاذ وسحب الكوس ، ☁️ سحب منخفضة",
            "فرصة تكون سحب الكوس المنخفضة وتدفقها نحو السواحل والجبال الشرقية، قد يصاحبها تساقط الرذاذ المستمر وانخفاض في مدى الرؤية الأفقية.",
            regions_str, now_dt, now_dt.replace(hour=10, minute=0), "#E0F2FE", "#0369A1"
        )
        success, msg_info = send_secure_alert_email(sub
