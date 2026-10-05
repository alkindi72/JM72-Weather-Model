"""
71wm AI Weather Model — UAE specialized real-time weather intelligence.
Cleaned & hardened version.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import requests
import base64
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from typing import Any, Dict, List, Optional, Tuple

# ==========================================
# 1. PLATFORM SETTINGS
# ==========================================
st.set_page_config(
    page_title="71wm AI Weather Model",
    page_icon="🌩️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 2. CSS
# ==========================================
st.markdown(
    """
<style>
    html, body, [data-testid="stAppViewContainer"], .stApp, #root {
        background-color: #F8FAFC !important;
    }
    .block-container {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
        padding: 2rem !important;
        margin: 1rem auto !important;
        border: 1px solid #E2E8F0 !important;
        max-width: 95% !important;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }
    .stApp p, .stApp span, .stApp label, div[data-testid="stTickBar"],
    h1, h2, h3, h4, h5, h6 {
        color: #082F49 !important;
        font-weight: 900 !important;
        font-size: 15px !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        border-bottom: 2px solid #CBD5E1 !important;
    }
    div[data-testid="stTabs"] button {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px 8px 0 0 !important;
        margin-right: 5px !important;
        padding: 10px 20px !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        background-color: #082F49 !important;
        border-color: #082F49 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] p {
        color: #FFFFFF !important;
    }
    .ai-broadcaster {
        background: linear-gradient(90deg, #F0F9FF, #E0F2FE);
        border-left: 5px solid #0284C7;
        padding: 15px 20px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        color: #0369A1;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.1);
    }
    div[data-testid="stSlider"] {
        background-color: #F1F5F9 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        margin-bottom: 25px !important;
        border: 1px solid #E2E8F0 !important;
    }
    div[data-testid="stTickBar"] {
        color: #475569 !important;
        font-weight: bold !important;
    }
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #0284C7 !important;
        border: 2px solid #FFF !important;
    }
    .table-responsive {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #ffffff;
        min-width: 850px;
    }
    .custom-table th {
        background-color: #082F49;
        color: #ffffff !important;
        padding: 14px;
        text-align: center;
        border-bottom: 3px solid #D4AF37;
        white-space: nowrap;
    }
    .custom-table td {
        padding: 14px;
        border-bottom: 1px solid #F1F5F9;
        border-right: 1px solid #F1F5F9;
        color: #082F49 !important;
        font-weight: 800;
        text-align: center;
        white-space: nowrap;
    }
    .log-box {
        background-color: #1E293B;
        color: #10B981;
        padding: 15px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 13px;
        height: 150px;
        overflow-y: auto;
        margin-bottom: 15px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 3. LOGO
# ==========================================
SVG_LOGO = """
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
b64_svg = base64.b64encode(SVG_LOGO.encode("utf-8")).decode("utf-8")
st.markdown(
    f'<div style="width:100%;display:flex;justify-content:center;margin-bottom:15px;">'
    f'<img src="data:image/svg+xml;base64,{b64_svg}" style="max-width:450px;width:100%;height:auto;" alt="71wm Logo" />'
    f"</div>",
    unsafe_allow_html=True,
)

# ==========================================
# 4. SESSION STATE
# ==========================================
st_autorefresh(interval=15 * 60 * 1000, key="data_refresh")

DEFAULTS = {
    "admin_password": "Jumah71",
    "admin_logged_in": False,
    "email_enabled": False,
    "email_sender": "",
    "email_receiver": "",
    "email_password": "",
    "email_sent_track": {},
    "alert_logs": [],
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


def send_secure_alert_email(subject: str, html_body: str) -> Tuple[bool, str]:
    """Send HTML alert email via Gmail SMTP."""
    if not st.session_state["email_enabled"]:
        return False, "النظام معطل يدوياً"
    sender = st.session_state.get("email_sender", "").strip()
    password = st.session_state.get("email_password", "").strip()
    receiver_raw = st.session_state.get("email_receiver", "").strip()
    if not sender or not password or not receiver_raw:
        return False, "بيانات المرسل أو المستلم ناقصة"

    receivers = [e.strip() for e in receiver_raw.split(",") if e.strip()]
    if not receivers:
        return False, "تنسيق الإيميلات غير صحيح"

    try:
        msg = MIMEText(html_body, "html", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = sender
        msg["To"] = ", ".join(receivers)

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receivers, msg.as_string())
        return True, f"تم بنجاح لـ {len(receivers)} مستلم(ين)"
    except Exception as exc:
        return False, f"خطأ الخادم: {exc}"


# ==========================================
# 5. STATIONS & TIMELINE
# ==========================================
DAYS_EN = {
    "Monday": "Mon",
    "Tuesday": "Tue",
    "Wednesday": "Wed",
    "Thursday": "Thu",
    "Friday": "Fri",
    "Saturday": "Sat",
    "Sunday": "Sun",
}

STATIONS: Dict[str, Dict[str, Any]] = {
    "Abu Dhabi": {"lat": 24.4760, "lon": 54.3290, "type": "Coast"},
    "ADNOC HQ": {"lat": 24.4621, "lon": 54.3241, "type": "Coast"},
    "Burj Khalifah": {"lat": 25.2017, "lon": 55.2766, "type": "Coast"},
    "Sharjah University": {"lat": 25.2869, "lon": 55.4622, "type": "Coast"},
    "Ajman": {"lat": 25.4236, "lon": 55.4447, "type": "Coast"},
    "Umm Al Quwain": {"lat": 25.5301, "lon": 55.6548, "type": "Coast"},
    "Ras Al khaimah": {"lat": 25.7716, "lon": 55.9392, "type": "Coast"},
    "Fujairah Port": {"lat": 25.1699, "lon": 56.3595, "type": "Coast"},
    "Kalba": {"lat": 25.0430, "lon": 56.3640, "type": "Coast"},
    "Khor Fakkan Port": {"lat": 25.3578, "lon": 56.3618, "type": "Coast"},
    "AlRuwais": {"lat": 24.0915, "lon": 52.6242, "type": "Coast"},
    "Sir Bani Yas": {"lat": 24.3188, "lon": 52.5990, "type": "Coast"},
    "Dalma": {"lat": 24.4906, "lon": 52.2914, "type": "Coast"},
    "Sir Bu Nair": {"lat": 25.2201, "lon": 54.2341, "type": "Coast"},
    "Abu Al Abyad": {"lat": 24.1841, "lon": 53.8626, "type": "Coast"},
    "Jabal Jais": {"lat": 25.9508, "lon": 56.1674, "type": "Mountains"},
    "Jabal Al Rahba": {"lat": 25.9264, "lon": 56.1192, "type": "Mountains"},
    "Hatta": {"lat": 24.8121, "lon": 56.1396, "type": "Mountains"},
    "Al Tawiyen": {"lat": 25.5527, "lon": 56.0715, "type": "Mountains"},
    "Al Heben": {"lat": 25.1251, "lon": 56.1578, "type": "Mountains"},
    "AlQor": {"lat": 24.9065, "lon": 56.1529, "type": "Mountains"},
    "Al Aamerah": {"lat": 24.2356, "lon": 55.5396, "type": "Inland"},
    "Al Wathbah": {"lat": 24.1789, "lon": 54.7033, "type": "Inland"},
    "Al Dhaid": {"lat": 25.2371, "lon": 55.8179, "type": "Inland"},
    "Al Malaiha": {"lat": 25.1322, "lon": 55.8891, "type": "Inland"},
    "Madinat Zayed": {"lat": 23.6836, "lon": 53.6995, "type": "Desert"},
    "Mukhariz": {"lat": 22.9095, "lon": 52.8882, "type": "Desert"},
    "Owtaid": {"lat": 23.3955, "lon": 53.1119, "type": "Desert"},
    "Zayed Int'l Airport": {"lat": 24.4330, "lon": 54.6511, "type": "Inland"},
    "Dubai Int'l Airport": {"lat": 25.2528, "lon": 55.3644, "type": "Inland"},
    "Sharjah Int'l Airport": {"lat": 25.3286, "lon": 55.5172, "type": "Inland"},
    "Ras Al Khaimah Int'l Airport": {"lat": 25.6135, "lon": 55.9388, "type": "Inland"},
    "Fujairah Int'l Airport": {"lat": 25.1122, "lon": 56.3240, "type": "Inland"},
    "Al Ain Int'l Airport": {"lat": 24.2617, "lon": 55.6092, "type": "Inland"},
    "Al Bateen Executive Airport": {"lat": 24.4283, "lon": 54.4581, "type": "Coast"},
    "Al Maktoum Int'l Airport": {"lat": 24.8961, "lon": 55.1614, "type": "Inland"},
}

SECTOR_MAP = {
    "المنطقة الشرقية": [
        "Fujairah Port", "Fujairah Int'l Airport", "Hatta", "Al Tawiyen",
        "Al Heben", "AlQor", "Kalba", "Khor Fakkan Port",
    ],
    "المنطقة الوسطى": ["Al Dhaid", "Al Malaiha"],
    "أبوظبي ومنطقة الظفرة": [
        "Abu Dhabi", "ADNOC HQ", "Abu Al Abyad", "AlRuwais", "Sir Bani Yas",
        "Dalma", "Sir Bu Nair", "Al Wathbah", "Madinat Zayed", "Mukhariz",
        "Owtaid", "Zayed Int'l Airport", "Al Bateen Executive Airport",
    ],
    "منطقة العين": ["Al Ain Int'l Airport", "Al Aamerah"],
    "دبي والإمارات الشمالية": [
        "Burj Khalifah", "Sharjah University", "Ajman", "Umm Al Quwain",
        "Ras Al khaimah", "Jabal Jais", "Jabal Al Rahba", "Dubai Int'l Airport",
        "Sharjah Int'l Airport", "Ras Al Khaimah Int'l Airport", "Al Maktoum Int'l Airport",
    ],
}


def get_sector_for_station(station_name: str) -> str:
    for sector, stations in SECTOR_MAP.items():
        if station_name in stations:
            return sector
    return "مناطق متفرقة"


def _safe_num(value: Any, default: float = 0.0) -> float:
    """Convert API value to float, treating None/NaN as default."""
    if value is None:
        return default
    try:
        v = float(value)
        if np.isnan(v):
            return default
        return v
    except (TypeError, ValueError):
        return default


def _safe_max(series: pd.Series, default: float = 0.0) -> float:
    if series is None or series.empty:
        return default
    val = series.max()
    if pd.isna(val):
        return default
    return float(val)


def _safe_min(series: pd.Series, default: float = 0.0) -> float:
    if series is None or series.empty:
        return default
    val = series.min()
    if pd.isna(val):
        return default
    return float(val)


# Timeline (UAE = UTC+4)
uae_time = datetime.utcnow() + timedelta(hours=4)
base_date = uae_time.replace(minute=0, second=0, microsecond=0)
timeline = [base_date + timedelta(hours=i * 3) for i in range(8 * 5)]  # 5 days × 8 slots
timeline_str = [
    f"{DAYS_EN[dt.strftime('%A')]} {dt.strftime('%d')} - {dt.strftime('%H:%M')}"
    for dt in timeline
]
unique_dates_display: List[str] = []
for dt in timeline:
    d_str = f"{DAYS_EN[dt.strftime('%A')]} {dt.strftime('%d')}"
    if d_str not in unique_dates_display:
        unique_dates_display.append(d_str)


# ==========================================
# 6. DATA FETCH
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stable_live_data(stations_dict: Dict[str, Dict]) -> Tuple[bool, Any]:
    """Fetch multi-location forecast from Open-Meteo. Returns (success, data_or_error)."""
    try:
        lats = ",".join(str(s["lat"]) for s in stations_dict.values())
        lons = ",".join(str(s["lon"]) for s in stations_dict.values())
        params = {
            "latitude": lats,
            "longitude": lons,
            "current": "precipitation,weather_code",
            "hourly": (
                "temperature_2m,apparent_temperature,relative_humidity_2m,cape,"
                "winddirection_10m,windspeed_10m,windgusts_10m,"
                "relative_humidity_850hPa,relative_humidity_700hPa,relative_humidity_500hPa,"
                "temperature_850hPa,temperature_500hPa,cloudcover_low"
            ),
            "models": "gfs_seamless",
            "timezone": "auto",
        }
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        # Multi-location → list; single-location → dict
        if isinstance(data, dict) and data.get("error"):
            return False, data.get("reason", "Unknown API error")
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list) or len(data) == 0:
            return False, "Unexpected API response format"
        return True, data
    except requests.exceptions.Timeout:
        return False, "Timeout connecting to Open-Meteo"
    except requests.exceptions.RequestException as exc:
        return False, str(exc)
    except Exception as exc:
        return False, str(exc)


with st.spinner("🤖 71wm AI Engine: Compiling live metrics..."):
    fetch_success, live_data = fetch_stable_live_data(STATIONS)

if not fetch_success:
    st.error(f"⚠️ فشل جلب البيانات الحية: {live_data}")
    st.info("سيتم عرض بيانات افتراضية حتى يتوفر الاتصال.")


# ==========================================
# 7. AI DYNAMICS ENGINE
# ==========================================
weather_rows: List[Dict[str, Any]] = []

if fetch_success and isinstance(live_data, list):
    station_items = list(STATIONS.items())
    n = min(len(live_data), len(station_items))

    for idx in range(n):
        name, coords = station_items[idx]
        zone_mapped = "Inland" if coords["type"] in ("Inland", "Desert") else coords["type"]

        try:
            station_payload = live_data[idx]
            hourly = station_payload.get("hourly") or {}
            times_raw = hourly.get("time") or []
            if not times_raw:
                continue

            api_times = [
                datetime.fromisoformat(t).replace(tzinfo=None) for t in times_raw
            ]

            for dt_str, dt in zip(timeline_str, timeline):
                # defaults
                temp_c = 35.0
                app_temp = 35.0
                surface_rh = 50.0
                cloud_low = 0.0
                wind_dir = 0.0
                wind_spd = 0.0
                storm_prob = 0.0
                fog_prob = 0.0
                alkous_prob = 0.0
                drizzle_prob = 0.0

                try:
                    deltas = [abs((api_t - dt).total_seconds()) for api_t in api_times]
                    closest_idx = int(np.argmin(deltas))

                    temp_c = _safe_num(hourly.get("temperature_2m", [None])[closest_idx], 35.0)
                    app_list = hourly.get("apparent_temperature") or [temp_c] * len(api_times)
                    app_temp = _safe_num(app_list[closest_idx], temp_c)
                    surface_rh = _safe_num(
                        (hourly.get("relative_humidity_2m") or [50])[closest_idx], 50.0
                    )
                    cloud_low = _safe_num(
                        (hourly.get("cloudcover_low") or [0])[closest_idx], 0.0
                    )
                    wind_dir = _safe_num(
                        (hourly.get("winddirection_10m") or [0])[closest_idx], 0.0
                    )
                    wind_spd = _safe_num(
                        (hourly.get("windspeed_10m") or [0])[closest_idx], 0.0
                    )
                    cape_val = _safe_num(
                        (hourly.get("cape") or [0])[closest_idx], 0.0
                    )
                    rh_850 = _safe_num(
                        (hourly.get("relative_humidity_850hPa") or [50])[closest_idx], 50.0
                    )
                    rh_700 = _safe_num(
                        (hourly.get("relative_humidity_700hPa") or [50])[closest_idx], 50.0
                    )
                    rh_500 = _safe_num(
                        (hourly.get("relative_humidity_500hPa") or [50])[closest_idx], 50.0
                    )
                    t_850 = _safe_num(
                        (hourly.get("temperature_850hPa") or [20])[closest_idx], 20.0
                    )
                    t_500 = _safe_num(
                        (hourly.get("temperature_500hPa") or [-10])[closest_idx], -10.0
                    )

                    # --- Storm AI ---
                    prob = (cape_val / 2000.0) * 100.0
                    moisture_index = (rh_850 * 0.4) + (rh_700 * 0.4) + (rh_500 * 0.2)
                    lapse_rate = t_850 - t_500
                    if lapse_rate > 26:
                        prob *= 1.3
                    elif lapse_rate < 20:
                        prob *= 0.5
                    if moisture_index < 40:
                        prob *= 0.1
                    elif moisture_index > 70:
                        prob *= 1.2
                    if coords["type"] == "Mountains" and temp_c > 38:
                        prob *= 1.3
                    if dt.hour < 12 or dt.hour > 19:
                        prob *= 0.1  # night suppression
                    storm_prob = float(np.clip(prob, 0, 100))

                    # --- Fog AI ---
                    if (dt.hour < 8 or dt.hour > 22) and surface_rh > 80 and wind_spd < 15:
                        fog_prob = float(
                            np.clip(
                                ((surface_rh - 80) * 4) + ((15 - wind_spd) * 3), 0, 100
                            )
                        )

                    # --- Al-Kous AI ---
                    if coords["lon"] >= 55.8 and 45 <= wind_dir <= 160 and surface_rh >= 65:
                        alkous_base = ((surface_rh - 65) * 2) + (cloud_low * 0.5)
                        if temp_c >= 35:
                            alkous_base *= 1.2
                        alkous_prob = float(np.clip(alkous_base, 0, 100))

                    # --- Drizzle AI ---
                    if (
                        coords["lon"] >= 55.8
                        and 3 <= dt.hour <= 9
                        and 45 <= wind_dir <= 160
                        and surface_rh >= 85
                        and cloud_low >= 75
                    ):
                        drizzle_prob = float(
                            np.clip(
                                ((surface_rh - 85) * 4)
                                + ((cloud_low - 75) * 2)
                                + (wind_spd * 0.8),
                                0,
                                100,
                            )
                        )

                except Exception:
                    pass  # keep defaults

                weather_rows.append(
                    {
                        "Time": dt_str,
                        "DateOnly": f"{DAYS_EN[dt.strftime('%A')]} {dt.strftime('%d')}",
                        "Station": name,
                        "Zone": zone_mapped,
                        "Latitude": coords["lat"],
                        "Longitude": coords["lon"],
                        "Storm Probability": round(storm_prob),
                        "Fog Probability": round(fog_prob),
                        "AlKous Prob": round(alkous_prob),
                        "Drizzle Prob": round(drizzle_prob),
                        "Temperature": round(temp_c, 1),
                        "Apparent Temp": round(app_temp, 1),
                        "Humidity": round(surface_rh),
                    }
                )
        except Exception:
            continue

df_all = pd.DataFrame(weather_rows)

# Ensure expected columns even if empty
EXPECTED_COLS = [
    "Time", "DateOnly", "Station", "Zone", "Latitude", "Longitude",
    "Storm Probability", "Fog Probability", "AlKous Prob", "Drizzle Prob",
    "Temperature", "Apparent Temp", "Humidity",
]
for col in EXPECTED_COLS:
    if col not in df_all.columns:
        df_all[col] = 0 if col not in ("Time", "DateOnly", "Station", "Zone") else ""


# ==========================================
# 8. ALERTS
# ==========================================
def get_html_email_template(
    title: str,
    text: str,
    regions: str,
    start_dt: datetime,
    end_dt: datetime,
    header_color: str,
) -> str:
    start_str = start_dt.strftime("%d/%m/%Y - %H:%M")
    end_str = end_dt.strftime("%d/%m/%Y - %H:%M")
    return f"""
    <div dir="rtl" style="font-family:Arial,sans-serif;border:1px solid #E2E8F0;max-width:600px;margin:0 auto;border-radius:8px;overflow:hidden;background:#FFF;">
        <div style="background-color:{header_color};padding:15px;text-align:center;border-bottom:2px solid rgba(0,0,0,0.1);">
            <h2 style="margin:0;color:#000;font-size:22px;">{title}</h2>
        </div>
        <div style="padding:20px;">
            <p style="font-size:18px;font-weight:bold;color:#1E293B;line-height:1.6;text-align:center;">{text}</p>
            <div style="background:#F8FAFC;border-radius:6px;padding:15px;margin-top:20px;border:1px solid #E2E8F0;">
                <p style="margin:0 0 10px 0;font-size:16px;color:#082F49;"><b>المناطق المتأثرة:</b> {regions}</p>
                <hr style="border:0;border-top:1px solid #CBD5E1;margin:10px 0;">
                <div style="display:flex;justify-content:space-between;">
                    <p style="margin:0;font-size:16px;color:#334155;"><b>بداية التحذير:</b><br>{start_str}</p>
                    <p style="margin:0;font-size:16px;color:#334155;"><b>نهاية التحذير:</b><br>{end_str}</p>
                </div>
            </div>
        </div>
    </div>
    """


current_time_df = (
    df_all[df_all["Time"] == timeline_str[0]] if not df_all.empty else pd.DataFrame()
)
max_storm_now = _safe_max(current_time_df["Storm Probability"] if not current_time_df.empty else pd.Series(dtype=float))
max_drizzle_now = _safe_max(current_time_df["Drizzle Prob"] if not current_time_df.empty else pd.Series(dtype=float))
max_fog_now = _safe_max(current_time_df["Fog Probability"] if not current_time_df.empty else pd.Series(dtype=float))
current_time_stamp = datetime.now().strftime("%H:%M:%S")
now_dt = datetime.now()

if st.session_state["email_enabled"] and not current_time_df.empty:
    today_key = unique_dates_display[0] if unique_dates_display else "today"
    if today_key not in st.session_state["email_sent_track"]:
        st.session_state["email_sent_track"][today_key] = {
            "storm": False,
            "drizzle": False,
            "fog": False,
        }
    track = st.session_state["email_sent_track"][today_key]

    # Storm ≥ 65%
    if max_storm_now >= 65 and not track["storm"]:
        affected = current_time_df[current_time_df["Storm Probability"] >= 65]["Station"].tolist()
        regions_str = "، ".join(sorted(set(get_sector_for_station(s) for s in affected)))
        html_body = get_html_email_template(
            "⛈️ أمطار رعدية ، ☁️ سحب ركامية",
            "فرصة تكون سحب ركامية يصاحبها أمطار ورياح نشطة إلى قوية السرعة مع السحب مثيرة للغبار.",
            regions_str,
            now_dt,
            now_dt + timedelta(hours=5),
            "#FDE047",
        )
        success, msg_info = send_secure_alert_email("71 weather model: Storm Warning", html_body)
        if success:
            track["storm"] = True
            st.session_state["alert_logs"].insert(0, f"[{current_time_stamp}] ✅ نجاح (عاصفة): {msg_info}")

    # Drizzle ≥ 60%
    if max_drizzle_now >= 60 and not track["drizzle"]:
        affected = current_time_df[current_time_df["Drizzle Prob"] >= 60]["Station"].tolist()
        regions_str = "، ".join(sorted(set(get_sector_for_station(s) for s in affected)))
        html_body = get_html_email_template(
            "🌧️ رذاذ وسحب الكوس ، ☁️ سحب منخفضة",
            "فرصة تكون سحب الكوس المنخفضة وتدفقها نحو السواحل والجبال الشرقية، قد يصاحبها تساقط الرذاذ المستمر وانخفاض في مدى الرؤية الأفقية.",
            regions_str,
            now_dt,
            now_dt.replace(hour=10, minute=0, second=0, microsecond=0),
            "#E0F2FE",
        )
        success, msg_info = send_secure_alert_email("71 weather model: Al Kouse warning", html_body)
        if success:
            track["drizzle"] = True
            st.session_state["alert_logs"].insert(0, f"[{current_time_stamp}] ✅ نجاح (رذاذ): {msg_info}")

    # Fog ≥ 50%
    if max_fog_now >= 50 and not track["fog"]:
        affected = current_time_df[current_time_df["Fog Probability"] >= 50]["Station"].tolist()
        regions_str = "، ".join(sorted(set(get_sector_for_station(s) for s in affected)))
        end_fog = (
            now_dt.replace(hour=9, minute=30, second=0, microsecond=0)
            if now_dt.hour < 9
            else now_dt + timedelta(hours=4)
        )
        html_body = get_html_email_template(
            "🌫️ ضباب ، 📉 تدني الرؤية الأفقية",
            "فرصة تشكل ضباب أو ضباب خفيف وانخفاض مدى الرؤية الأفقية على بعض المناطق الداخلية والساحلية.",
            regions_str,
            now_dt,
            end_fog,
            "#E2E8F0",
        )
        success, msg_info = send_secure_alert_email("71 weather model: Fog & low Visibility", html_body)
        if success:
            track["fog"] = True
            st.session_state["alert_logs"].insert(0, f"[{current_time_stamp}] ✅ نجاح (ضباب): {msg_info}")


# ==========================================
# 9. AI BRIEFING
# ==========================================
ai_briefing = "🤖 **71wm AI Broadcaster:** "
if not current_time_df.empty:
    max_alkous = _safe_max(current_time_df["AlKous Prob"])
    if max_fog_now >= 50:
        ai_briefing += "🌫️ **🚨 Dense Fog Warning:** High risk of radiation fog affecting visibility. "
    elif max_drizzle_now >= 60:
        ai_briefing += f"🌧️ **🚨 Al-Kous Drizzle Warning:** High risk ({int(max_drizzle_now)}%) of morning drizzle forming over the eastern ridges. "
    elif max_storm_now >= 65:
        ai_briefing += f"🌩️ Convective activity shows a {int(max_storm_now)}% risk of isolated storms. "
    elif max_alkous > 50:
        ai_briefing += f"⚠️ High probability ({int(max_alkous)}%) of dense Al-Kous low clouds. "
    else:
        ai_briefing += "Atmospheric columns remain thermodynamically stable with no localized anomalies detected."
else:
    ai_briefing += "Waiting for live data feed..."

st.markdown(f'<div class="ai-broadcaster">{ai_briefing}</div>', unsafe_allow_html=True)


# ==========================================
# 10. HELPER: density map
# ==========================================
def make_density_map(
    df: pd.DataFrame,
    z_col: str,
    center_lat: float = 24.4,
    center_lon: float = 54.6,
    zoom: float = 5.5,
    colorscale: Optional[List] = None,
    opacity: float = 0.75,
    title: str = "",
):
    if df.empty or z_col not in df.columns:
        fig = px.scatter_mapbox(
            lat=[center_lat],
            lon=[center_lon],
            zoom=zoom,
            height=400,
        )
        fig.update_layout(
            mapbox_style="open-street-map",
            margin=dict(r=0, t=40 if title else 0, l=0, b=0),
            title=title or None,
        )
        return fig

    colorscale = colorscale or [
        "rgba(0,0,0,0)",
        "#A3E635",
        "#FDE047",
        "#EF4444",
        "#7E22CE",
    ]
    fig = px.density_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        z=z_col,
        radius=45,
        center=dict(lat=center_lat, lon=center_lon),
        zoom=zoom,
        mapbox_style="open-street-map",
        opacity=opacity,
        color_continuous_scale=colorscale,
        range_color=[0, 100],
        title=title or None,
    )
    fig.update_layout(margin=dict(r=0, t=40 if title else 0, l=0, b=0))
    return fig


# ==========================================
# 11. TABS
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "🌩️ Storms & Fog",
        "🔥 Heat & Anomalies",
        "☁️ Al-Kous & Drizzle",
        "📋 Model Matrix",
        "🤖 71wm AI Assistant",
        "⚙️ Control Room",
    ]
)

# ----- Tab 1: Storms & Fog -----
with tab1:
    st.markdown(
        '<h4 style="color:#082F49;font-weight:900;margin-bottom:15px;">📋 5-Day Storm & Fog Forecast (National)</h4>',
        unsafe_allow_html=True,
    )
    cols_t1 = st.columns(5)
    for i, date in enumerate(unique_dates_display[:5]):
        day_df = df_all[df_all["DateOnly"] == date] if not df_all.empty else pd.DataFrame()
        m_s = int(_safe_max(day_df["Storm Probability"] if not day_df.empty else pd.Series(dtype=float)))
        m_f = int(_safe_max(day_df["Fog Probability"] if not day_df.empty else pd.Series(dtype=float)))
        bg = "#FEF2F2" if max(m_s, m_f) >= 60 else ("#FFFBEB" if max(m_s, m_f) >= 30 else "#F0FDF4")
        cols_t1[i].markdown(
            f"<div style='background-color:{bg};border:1px solid #CBD5E1;border-radius:8px;padding:15px;text-align:center;'>"
            f"<div style='color:#082F49;font-size:15px;font-weight:900;margin-bottom:12px;'>📅 {date}</div>"
            f"<div style='font-size:16px;font-weight:900;color:#EF4444;margin-bottom:8px;'>⛈️ Storm: {m_s}%</div>"
            f"<div style='font-size:16px;font-weight:900;color:#64748B;'>🌫️ Fog: {m_f}%</div></div>",
            unsafe_allow_html=True,
        )

    selected_time_t1 = st.select_slider(
        "Forecast Timeline",
        options=timeline_str,
        key="t1_slider",
        label_visibility="collapsed",
    )
    df_time_t1 = (
        df_all[df_all["Time"] == selected_time_t1].copy()
        if not df_all.empty
        else pd.DataFrame()
    )
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            make_density_map(
                df_time_t1,
                "Storm Probability",
                colorscale=["rgba(0,0,0,0)", "#A3E635", "#FDE047", "#EF4444", "#7E22CE"],
            ),
            use_container_width=True,
        )
    with c2:
        st.plotly_chart(
            make_density_map(
                df_time_t1,
                "Fog Probability",
                colorscale=["rgba(0,0,0,0)", "#E2E8F0", "#94A3B8", "#475569"],
                opacity=0.8,
            ),
            use_container_width=True,
        )

    st.markdown(
        '<hr><h3 style="color:#082F49;font-weight:900;">🛰️ Live Telemetry: Satellite Cloud Imagery</h3>',
        unsafe_allow_html=True,
    )
    components.html(
        """
        <div style="position:relative;width:100%;height:500px;border-radius:12px;overflow:hidden;
                    box-shadow:0 4px 15px rgba(0,0,0,0.1);background:#F8FAFC;">
            <iframe width="100%" height="520"
                src="https://embed.windy.com/embed.html?type=map&location=coordinates&overlay=satellite&lat=24.6&lon=54.8&zoom=6"
                frameborder="0" style="position:absolute;top:0;left:0;"></iframe>
            <div style="position:absolute;bottom:0;right:0;width:180px;height:35px;
                        background:rgba(8,47,73,0.95);display:flex;align-items:center;justify-content:center;
                        border-top-left-radius:10px;border:1px solid #D4AF37;">
                <span style="color:#D4AF37;font-family:sans-serif;font-size:14px;font-weight:900;">🛰️ 71wm SATELLITE LIVE</span>
            </div>
        </div>
        """,
        height=520,
    )

# ----- Tab 2: Heat -----
with tab2:
    st.markdown(
        '<h4 style="color:#082F49;font-weight:900;margin-bottom:15px;">📋 5-Day Thermal Range (Min-Max By Zone)</h4>',
        unsafe_allow_html=True,
    )
    cols_t2 = st.columns(5)
    for i, date in enumerate(unique_dates_display[:5]):
        day_df = df_all[df_all["DateOnly"] == date] if not df_all.empty else pd.DataFrame()

        def zone_range(zone: str):
            zdf = day_df[day_df["Zone"] == zone] if not day_df.empty else pd.DataFrame()
            mx = round(_safe_max(zdf["Temperature"] if not zdf.empty else pd.Series(dtype=float), 0), 1)
            mn = round(_safe_min(zdf["Temperature"] if not zdf.empty else pd.Series(dtype=float), 0), 1)
            return mn, mx

        c_mn, c_mx = zone_range("Coast")
        m_mn, m_mx = zone_range("Mountains")
        i_mn, i_mx = zone_range("Inland")

        cols_t2[i].markdown(
            f"<div style='background-color:#F0FDF4;border:1px solid #CBD5E1;border-radius:8px;padding:15px;'>"
            f"<div style='color:#082F49;font-size:15px;font-weight:900;margin-bottom:12px;text-align:center;'>📅 {date}</div>"
            f"<div style='display:flex;justify-content:space-between;font-size:14px;'><span>🌊 Coast:</span><b>⬇ {c_mn}° - ⬆ {c_mx}°</b></div>"
            f"<div style='display:flex;justify-content:space-between;font-size:14px;'><span>⛰️ Mount:</span><b>⬇ {m_mn}° - ⬆ {m_mx}°</b></div>"
            f"<div style='display:flex;justify-content:space-between;font-size:14px;'><span>🏜️ Inland:</span><b>⬇ {i_mn}° - ⬆ {i_mx}°</b></div>"
            f"</div>",
            unsafe_allow_html=True,
        )

# ----- Tab 3: Al-Kous & Drizzle -----
with tab3:
    st.markdown(
        '<h4 style="color:#082F49;font-weight:900;margin-bottom:15px;">☁️ Al-Kous Stratus & Orographic Drizzle Radar Tracker</h4>',
        unsafe_allow_html=True,
    )
    cols_t3 = st.columns(5)
    for i, date in enumerate(unique_dates_display[:5]):
        day_df = df_all[df_all["DateOnly"] == date] if not df_all.empty else pd.DataFrame()
        mx_k = int(_safe_max(day_df["AlKous Prob"] if not day_df.empty else pd.Series(dtype=float)))
        mx_dr = int(_safe_max(day_df["Drizzle Prob"] if not day_df.empty else pd.Series(dtype=float)))
        bg = "#FEF2F2" if mx_dr > 40 else "#F8FAFC"
        cols_t3[i].markdown(
            f"<div style='background-color:{bg};border:1px solid #CBD5E1;border-radius:8px;padding:15px;text-align:center;'>"
            f"<div style='color:#082F49;font-size:14px;font-weight:900;'>📅 {date}</div>"
            f"<div style='color:#1E293B;font-weight:bold;margin-top:5px;'>☁️ الكوس: {mx_k}%</div>"
            f"<div style='color:#0284C7;font-weight:900;'>🌧️ الرذاذ: {mx_dr}%</div></div>",
            unsafe_allow_html=True,
        )

    selected_time_t3 = st.select_slider(
        "Forecast Timeline",
        options=timeline_str,
        key="t3_slider",
        label_visibility="collapsed",
    )
    df_time_t3 = (
        df_all[df_all["Time"] == selected_time_t3].copy()
        if not df_all.empty
        else pd.DataFrame()
    )
    east_stations = (
        df_time_t3[df_time_t3["Longitude"] >= 55.8].copy()
        if not df_time_t3.empty
        else pd.DataFrame()
    )
    st.plotly_chart(
        make_density_map(
            east_stations,
            "Drizzle Prob",
            center_lat=25.2,
            center_lon=56.2,
            zoom=7.5,
            colorscale=["rgba(0,0,0,0)", "#BAE6FD", "#38BDF8", "#0284C7", "#0369A1"],
            opacity=0.85,
            title="AI Orographic Drizzle Condensation Index (%)",
        ),
        use_container_width=True,
        key="kous_drizzle_map",
    )

# ----- Tab 4: Matrix -----
with tab4:
    selected_time_t4 = st.select_slider(
        "Forecast Timeline",
        options=timeline_str,
        key="t4_slider",
        label_visibility="collapsed",
    )
    df_time_t4 = (
        df_all[df_all["Time"] == selected_time_t4].copy()
        if not df_all.empty
        else pd.DataFrame()
    )
    st.markdown(
        "<h3 style='color:#082F49;font-weight:900;'>📊 Full 36-Station Atmospheric Matrix</h3>",
        unsafe_allow_html=True,
    )
    if df_time_t4.empty:
        st.warning("لا توجد بيانات متاحة لهذا الوقت حالياً.")
    else:
        display_df = df_time_t4.sort_values(by="Temperature", ascending=False)
        html_table = (
            "<div class='table-responsive'><table class='custom-table'>"
            "<tr><th>Station</th><th>Actual Temp</th><th>Feels Like</th><th>RH (%)</th>"
            "<th>Al-Kous (%)</th><th>Morning Drizzle (%)</th><th>Convective Storm (%)</th></tr>"
        )
        for _, row in display_df.iterrows():
            s_color = "#EF4444" if row["Storm Probability"] >= 75 else "#082F49"
            dr_color = "#0284C7" if row["Drizzle Prob"] >= 40 else "#082F49"
            html_table += (
                f"<tr><td>{row['Station']}</td>"
                f"<td>{row['Temperature']}°C</td>"
                f"<td>{row['Apparent Temp']}°C</td>"
                f"<td>{row['Humidity']}%</td>"
                f"<td>{row['AlKous Prob']}%</td>"
                f"<td style='color:{dr_color};font-weight:bold;'>{row['Drizzle Prob']}%</td>"
                f"<td style='color:{s_color};'>{row['Storm Probability']}%</td></tr>"
            )
        st.markdown(html_table + "</table></div>", unsafe_allow_html=True)

# ----- Tab 5: AI Assistant -----
with tab5:
    st.markdown(
        '<h4 style="color:#082F49;font-weight:900;">🤖 71wm AI Data Assistant</h4>',
        unsafe_allow_html=True,
    )
    prompt = st.chat_input("Ask about parameters... (drizzle / رذاذ / storm / fog / كوس)")
    if prompt:
        st.chat_message("user").write(prompt)
        p_l = prompt.lower()
        curr = (
            df_all[df_all["Time"] == timeline_str[0]]
            if not df_all.empty
            else pd.DataFrame()
        )
        if curr.empty:
            res = "البيانات الحية غير متوفرة حالياً. حاول مرة أخرى بعد قليل."
        elif "drizzle" in p_l or "رذاذ" in p_l:
            dr_stations = curr[curr["Drizzle Prob"] > 30]
            res = (
                f"🌧️ Drizzle mapped at: {', '.join(dr_stations['Station'].tolist())}."
                if not dr_stations.empty
                else "No microclimatic drizzle mapped."
            )
        elif "storm" in p_l or "عاصفة" in p_l or "رعد" in p_l:
            st_stations = curr[curr["Storm Probability"] > 40]
            res = (
                f"🌩️ Elevated storm probability at: {', '.join(st_stations['Station'].tolist())}."
                if not st_stations.empty
                else "No significant convective risk currently."
            )
        elif "fog" in p_l or "ضباب" in p_l:
            fg_stations = curr[curr["Fog Probability"] > 30]
            res = (
                f"🌫️ Fog risk at: {', '.join(fg_stations['Station'].tolist())}."
                if not fg_stations.empty
                else "No significant fog risk currently."
            )
        elif "كوس" in p_l or "kous" in p_l or "alkous" in p_l:
            k_stations = curr[curr["AlKous Prob"] > 40]
            res = (
                f"☁️ Al-Kous probability elevated at: {', '.join(k_stations['Station'].tolist())}."
                if not k_stations.empty
                else "Al-Kous activity is low."
            )
        else:
            res = "I am ready. Ask me about drizzle, storm, fog, or Al-Kous for the current time slot."
        st.chat_message("assistant").write(res)

# ----- Tab 6: Control Room -----
with tab6:
    st.markdown("### ⚙️ 71wm Secure Control Room")
    if not st.session_state["admin_logged_in"]:
        st.warning("🔒 هذه الغرفة مقفلة أمنياً ومخصصة لمدير النظام فقط.")
        admin_pwd = st.text_input("الرمز السري الحالي (PIN):", type="password", key="login_pin_input")
        if st.button("🔓 فتح الغرفة"):
            if admin_pwd == st.session_state["admin_password"]:
                st.session_state["admin_logged_in"] = True
                st.rerun()
            else:
                st.error("❌ الرمز السري غير صحيح، تم رفض الوصول.")
    else:
        st.success("✅ تم فتح القفل. أهلاً بك في غرفة التحكم الآمنة.")
        if st.button("🔒 قفل الغرفة (تسجيل الخروج)"):
            st.session_state["admin_logged_in"] = False
            st.rerun()

        st.markdown("---")
        st.markdown("#### 🔑 تغيير الرمز السري للمشرف")
        new_pwd_input = st.text_input("أدخل الرمز السري الجديد:", type="password", key="change_pin_field")
        if st.button("💾 حفظ الرمز السري الجديد"):
            if new_pwd_input.strip():
                st.session_state["admin_password"] = new_pwd_input.strip()
                st.success("✅ تأكيد: تم تغيير الرمز السري بنجاح!")
            else:
                st.error("❌ خطأ: لا يمكن إدخال رمز سري فارغ.")

        st.markdown("---")
        st.markdown("#### 📧 إعدادات خادم التنبيهات والبريد الإلكتروني")
        st.session_state["email_enabled"] = st.checkbox(
            "تفعيل نظام الإرسال التلقائي (Email Alerts Active)",
            value=st.session_state["email_enabled"],
        )
        st.session_state["email_sender"] = st.text_input(
            "بريد المرسل (Gmail)",
            value=st.session_state["email_sender"],
            key="email_sender_input",
        )
        st.session_state["email_password"] = st.text_input(
            "كلمة مرور التطبيقات السرية (16 حرفاً من جوجل)",
            type="password",
            value=st.session_state["email_password"],
            key="email_password_input",
        )

        st.info("💡 **تلميح:** أضف الإيميل ثم اضغط الزر. يمكنك أيضاً التعديل اليدوي في القائمة أدناه.")

        new_email = st.text_input("إضافة بريد مستلم جديد:", key="new_email_input")
        if st.button("➕ إضافة للقائمة"):
            if new_email and "@" in new_email:
                current_list = [
                    e.strip()
                    for e in st.session_state["email_receiver"].split(",")
                    if e.strip()
                ]
                if new_email.strip() not in current_list:
                    current_list.append(new_email.strip())
                    st.session_state["email_receiver"] = ", ".join(current_list)
                    st.success(f"تم إضافة {new_email} للقائمة.")
                else:
                    st.warning("هذا البريد موجود مسبقاً في القائمة.")
            else:
                st.error("يرجى إدخال بريد إلكتروني صحيح.")

        # Use a unique key and sync back to session state
        edited_receivers = st.text_area(
            "قائمة المستلمين الحالية (يمكنك التعديل اليدوي أو الحذف من هنا):",
            value=st.session_state["email_receiver"],
            key="email_receiver_editor",
        )
        if edited_receivers != st.session_state["email_receiver"]:
            st.session_state["email_receiver"] = edited_receivers

        if st.button("🔄 تصفير الذاكرة وإجبار الإرسال الآن"):
            st.session_state["email_sent_track"] = {}
            st.success("تم التصفير! سيقوم النظام الآن بإعادة تقييم الطقس ومحاولة الإرسال فوراً...")
            st.rerun()

        st.markdown("---")
        st.markdown("#### 📡 سجل عمليات الإرسال الحي (Live Delivery Log)")
        logs_html = "<div class='log-box'>"
        if not st.session_state["alert_logs"]:
            logs_html += ">> النظام في وضع الاستعداد. لم يتم رصد أي عمليات إرسال..."
        else:
            for log in st.session_state["alert_logs"][:50]:
                logs_html += f">> {log}<br>"
        logs_html += "</div>"
        st.markdown(logs_html, unsafe_allow_html=True)
