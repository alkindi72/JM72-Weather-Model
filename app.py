"""71wm AI Weather Model — UAE command deck."""

import base64
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="71wm AI Weather Model", page_icon="🌩️", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
  html, body, [data-testid="stAppViewContainer"], .stApp {
    background:
      radial-gradient(900px 420px at 10% -10%, rgba(56,189,248,.16), transparent 55%),
      radial-gradient(700px 380px at 100% 0%, rgba(212,175,55,.12), transparent 50%),
      #07111f !important;
    color: #e7eef8;
  }
  [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
  .block-container { padding: 1.1rem 1.4rem 2rem; max-width: 1380px; }
  h1, h2, h3, h4, p, span, label, li, div { color: #e7eef8; }
  html, body, [data-testid="stAppViewContainer"], .stApp, .stMarkdown, p, span, label {
    font-size: 18px !important;
  }
  h1 { font-size: 40px !important; }
  h2, h3, h4 { font-size: 26px !important; }
  .sub, .muted, .pill { font-size: 16px !important; }
  div[data-testid="stMetric"] label, div[data-testid="stMetric"] div { font-size: 18px !important; }
  .hero {
    border: 1px solid rgba(148,163,184,.22);
    background: linear-gradient(135deg, rgba(15,23,42,.92), rgba(8,47,73,.78));
    border-radius: 22px; padding: 18px 22px; margin-bottom: 14px;
    box-shadow: 0 18px 50px rgba(0,0,0,.28);
  }
  .stApp, .stMarkdown p, label, [data-testid="stCaptionContainer"] { font-size: 18px !important; }
  div[data-testid="stTabs"] button p { font-size: 18px !important; }
  .kicker { letter-spacing: .22em; color: #d4af37 !important; font-size: 14px !important; font-weight: 800; }
  .hero h1 { margin: 4px 0 2px; font-size: 40px !important; font-weight: 900; color: white !important; }
  .sub { color: #cbd5e1 !important; font-size: 18px !important; }
  .pill {
    display: inline-block; margin: 8px 8px 0 0; padding: 8px 12px; border-radius: 999px;
    background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.1); font-size: 16px !important;
  }
  .card {
    background: rgba(15,23,42,.72); border: 1px solid rgba(148,163,184,.18);
    border-radius: 16px; padding: 14px 16px; min-height: 108px;
  }
  .card b { display: block; font-size: 34px !important; margin-top: 4px; }
  .muted { color: #cbd5e1 !important; font-size: 16px !important; }
  div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 6px; overflow-x: auto; flex-wrap: nowrap;
  }
  div[data-testid="stTabs"] button { min-width: max-content; }
  @media (max-width: 800px) {
    .block-container { padding: .6rem .4rem 1.4rem !important; }
    .hero h1 { font-size: 28px !important; }
    .card b { font-size: 26px !important; }
  }
  div[data-testid="stMetric"] {
    background: rgba(15,23,42,.72); border: 1px solid rgba(148,163,184,.18); border-radius: 16px; padding: 8px 12px;
  }
  [data-baseweb="select"] > div, [data-baseweb="popover"] li {
    background: #0f172a !important; color: #f8fafc !important; font-size: 18px !important;
  }
  [data-baseweb="select"] span, [data-baseweb="popover"] { color: #f8fafc !important; }
  input, textarea { color: #f8fafc !important; background: #0f172a !important; }
</style>
""",
    unsafe_allow_html=True,
)

DAYS_EN = {"Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed", "Thursday": "Thu", "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"}
ELEVATION = {
    "Jabal Jais": 1934, "Jabal Al Rahba": 1543, "Hatta": 330, "Al Tawiyen": 450,
    "Al Heben": 700, "AlQor": 520, "Fujairah Port": 5, "Khor Fakkan Port": 8,
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
    "الساحل الشرقي": ["Fujairah Port", "Fujairah Int'l Airport", "Al Tawiyen", "Al Heben", "AlQor", "Kalba", "Khor Fakkan Port"],
    "الجبال الشرقية": ["Hatta", "Jabal Jais", "Jabal Al Rahba"],
    "المنطقة الوسطى": ["Al Dhaid", "Al Malaiha"],
    "العين": ["Al Ain Int'l Airport", "Al Aamerah"],
    "دبي": ["Burj Khalifah", "Dubai Int'l Airport", "Al Maktoum Int'l Airport"],
    "الشارقة وعجمان وأم القيوين": ["Sharjah University", "Sharjah Int'l Airport", "Ajman", "Umm Al Quwain"],
    "رأس الخيمة": ["Ras Al khaimah", "Ras Al Khaimah Int'l Airport"],
    "أبوظبي": ["Abu Dhabi", "ADNOC HQ", "Al Wathbah", "Zayed Int'l Airport", "Al Bateen Executive Airport", "Sir Bu Nair"],
    "الظفرة": ["Abu Al Abyad", "AlRuwais", "Sir Bani Yas", "Dalma", "Madinat Zayed", "Mukhariz", "Owtaid"],
}
SEASON_ORDER = ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"]


def tr(ar: str, en: str) -> str:
    return ar if st.session_state.get("lang", "ar") == "ar" else en


SECTOR_EN = {
    "الساحل الشرقي": "East coast",
    "الجبال الشرقية": "Eastern mountains",
    "المنطقة الوسطى": "Central region",
    "العين": "Al Ain",
    "دبي": "Dubai",
    "الشارقة وعجمان وأم القيوين": "Sharjah, Ajman and Umm Al Quwain",
    "رأس الخيمة": "Ras Al Khaimah",
    "أبوظبي": "Abu Dhabi",
    "الظفرة": "Al Dhafra",
    "متفرقة": "Other",
}
def sector_of(name: str) -> str:
    for sector, names in SECTOR_MAP.items():
        if name in names:
            return sector
    return "متفرقة"


def safe_num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return default
        v = float(value)
        return default if np.isnan(v) else v
    except (TypeError, ValueError):
        return default


def safe_max(series: pd.Series, default: float = 0.0) -> float:
    if series is None or len(series) == 0:
        return default
    val = series.max()
    return default if pd.isna(val) else float(val)


def heat_band(apparent: float) -> str:
    if apparent >= 45:
        return tr("إجهاد شديد", "Extreme stress")
    if apparent >= 40:
        return tr("إجهاد مرتفع", "High stress")
    if apparent >= 35:
        return tr("حار", "Hot")
    return tr("معتدل", "Moderate")


def ops_note(row: pd.Series) -> str:
    notes = []
    if row["Storm Probability"] >= 65:
        notes.append(tr("طيران: راقب خلايا رعدية", "Aviation: watch storms"))
    if row["Fog Probability"] >= 50:
        notes.append(tr("طرق: تدني رؤية", "Roads: low visibility"))
    if row["Shamal Index"] >= 60:
        notes.append(tr("غبار محتمل", "Dust possible"))
    if row["Drizzle Prob"] >= 60:
        notes.append(tr("شرق: رذاذ جبلي", "East: orographic drizzle"))
    if row["Apparent Temp"] >= 42:
        notes.append(tr("عمل خارجي: حدّ من التعرض", "Outdoor work: limit exposure"))
    return " · ".join(notes) if notes else tr("لا قيد تشغيلي بارز", "No major operational limit")


def gfs_cycle(now_utc: datetime) -> str:
    """Latest GFS cycle whose fields are normally available (about 3.5 h after 00/06/12/18 UTC)."""
    ready = now_utc - timedelta(hours=3, minutes=30)
    hour = (ready.hour // 6) * 6
    return ready.strftime("%Y-%m-%d") + f" {hour:02d}Z"


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def fetch_live(stations: Dict[str, Dict], cycle: str) -> Tuple[bool, Any]:
    try:
        params = {
            "latitude": ",".join(str(s["lat"]) for s in stations.values()),
            "longitude": ",".join(str(s["lon"]) for s in stations.values()),
            "current": "precipitation,weather_code",
            "hourly": "temperature_2m,apparent_temperature,relative_humidity_2m,cape,winddirection_10m,windspeed_10m,windgusts_10m,relative_humidity_850hPa,relative_humidity_700hPa,relative_humidity_500hPa,temperature_850hPa,temperature_500hPa,cloudcover_low",
            "models": "gfs_seamless",
            "timezone": "auto",
        }
        response = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and data.get("error"):
            return False, data.get("reason", "API error")
        if isinstance(data, dict):
            data = [data]
        return (True, data) if data else (False, "Empty response")
    except Exception as exc:
        return False, str(exc)


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def fetch_oni() -> Tuple[bool, Any]:
    try:
        text = requests.get("https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt", timeout=25).text
        rows = []
        for line in text.splitlines():
            parts = line.split()
            if len(parts) < 4 or parts[0] not in SEASON_ORDER:
                continue
            rows.append({"season": parts[0], "year": int(parts[1]), "sst": float(parts[2]), "anom": float(parts[3])})
        df = pd.DataFrame(rows)
        df["label"] = df["season"] + " " + df["year"].astype(str)
        df["order"] = df["year"] * 12 + df["season"].map({s: i for i, s in enumerate(SEASON_ORDER)})
        return True, df.sort_values("order").reset_index(drop=True)
    except Exception as exc:
        return False, str(exc)


st_autorefresh(interval=15 * 60 * 1000, key="data_refresh")
uae_now = datetime.utcnow() + timedelta(hours=4)
cycle = gfs_cycle(datetime.utcnow())
bulletin_day = (uae_now - timedelta(hours=5)).strftime("%Y-%m-%d")
base = uae_now.replace(minute=0, second=0, microsecond=0)
timeline = [base + timedelta(hours=i * 3) for i in range(40)]
timeline_str = [f"{DAYS_EN[dt.strftime('%A')]} {dt.strftime('%d')} - {dt.strftime('%H:%M')}" for dt in timeline]
dates = []
for dt in timeline:
    label = f"{DAYS_EN[dt.strftime('%A')]} {dt.strftime('%d')}"
    if label not in dates:
        dates.append(label)

with st.spinner("يجمع 71wm القراءات حسب آخر دورة نموذج..."):
    ok, live = fetch_live(STATIONS, cycle)

rows: List[Dict[str, Any]] = []
if ok and isinstance(live, list):
    for idx, (name, coords) in enumerate(list(STATIONS.items())[: len(live)]):
        hourly = (live[idx] or {}).get("hourly") or {}
        times = hourly.get("time") or []
        if not times:
            continue
        api_times = [datetime.fromisoformat(t).replace(tzinfo=None) for t in times]
        zone = "Inland" if coords["type"] in ("Inland", "Desert") else coords["type"]
        for dt_str, dt in zip(timeline_str, timeline):
            temp = app = 35.0
            rh = 50.0
            cloud = wind_dir = wind = gust = storm = fog = alkous = drizzle = shamal = 0.0
            try:
                i = int(np.argmin([abs((t - dt).total_seconds()) for t in api_times]))
                temp = safe_num((hourly.get("temperature_2m") or [None])[i], 35)
                app = safe_num((hourly.get("apparent_temperature") or [temp])[i], temp)
                rh = safe_num((hourly.get("relative_humidity_2m") or [50])[i], 50)
                cloud = safe_num((hourly.get("cloudcover_low") or [0])[i], 0)
                wind_dir = safe_num((hourly.get("winddirection_10m") or [0])[i], 0)
                wind = safe_num((hourly.get("windspeed_10m") or [0])[i], 0)
                gust = safe_num((hourly.get("windgusts_10m") or [wind])[i], wind)
                cape = safe_num((hourly.get("cape") or [0])[i], 0)
                rh850 = safe_num((hourly.get("relative_humidity_850hPa") or [50])[i], 50)
                rh700 = safe_num((hourly.get("relative_humidity_700hPa") or [50])[i], 50)
                rh500 = safe_num((hourly.get("relative_humidity_500hPa") or [50])[i], 50)
                t850 = safe_num((hourly.get("temperature_850hPa") or [20])[i], 20)
                t500 = safe_num((hourly.get("temperature_500hPa") or [-10])[i], -10)
                prob = cape / 20.0
                moisture = rh850 * 0.4 + rh700 * 0.4 + rh500 * 0.2
                lapse = t850 - t500
                prob *= 1.3 if lapse > 26 else (0.5 if lapse < 20 else 1)
                prob *= 0.1 if moisture < 40 else (1.2 if moisture > 70 else 1)
                if coords["type"] == "Mountains" and temp > 38:
                    prob *= 1.3
                if dt.hour < 12 or dt.hour > 19:
                    prob *= 0.1
                storm = float(np.clip(prob, 0, 100))
                if (dt.hour < 8 or dt.hour > 22) and rh > 80 and wind < 15:
                    fog = float(np.clip((rh - 80) * 4 + (15 - wind) * 3, 0, 100))
                if coords["lon"] >= 55.8 and 45 <= wind_dir <= 160 and rh >= 65:
                    base_k = (rh - 65) * 2 + cloud * 0.5
                    alkous = float(np.clip(base_k * (1.2 if temp >= 35 else 1), 0, 100))
                elev = ELEVATION.get(name, 0)
                if elev >= 800 and 45 <= wind_dir <= 160 and rh >= 60:
                    alkous = max(alkous, 40)
                    drizzle = max(drizzle, 15)
                if coords["lon"] >= 55.8 and 3 <= dt.hour <= 9 and 45 <= wind_dir <= 160 and rh >= 85 and cloud >= 75:
                    drizzle = float(np.clip((rh - 85) * 4 + (cloud - 75) * 2 + wind * 0.8, 0, 100))
                nw = wind_dir >= 300 or wind_dir <= 30
                shamal = float(np.clip((wind - 18) * 3.2 + (12 if nw else 0) + (8 if coords["type"] in ("Desert", "Coast") else 0), 0, 100)) if wind >= 20 and nw else 0.0
            except Exception:
                pass
            rows.append({
                "Time": dt_str, "DateOnly": f"{DAYS_EN[dt.strftime('%A')]} {dt.strftime('%d')}",
                "Station": name, "Sector": sector_of(name), "Zone": zone,
                "Latitude": coords["lat"], "Longitude": coords["lon"],
                "Storm Probability": round(storm), "Fog Probability": round(fog),
                "AlKous Prob": round(alkous), "Drizzle Prob": round(drizzle),
                "Shamal Index": round(shamal), "Temperature": round(temp, 1),
                "Apparent Temp": round(app, 1), "Humidity": round(rh),
                "Wind": round(wind, 1), "Gust": round(gust, 1), "Wind Dir": round(wind_dir),
            })

df = pd.DataFrame(rows)
now_df = df[df["Time"] == timeline_str[0]] if not df.empty else pd.DataFrame()
risk = 0 if now_df.empty else int(np.clip(max(safe_max(now_df["Storm Probability"]), safe_max(now_df["Fog Probability"]), safe_max(now_df["Shamal Index"]) * 0.7, safe_max(now_df["Drizzle Prob"]) * 0.8), 0, 100))
status_ar = "حرج" if risk >= 70 else ("مراقب" if risk >= 40 else "مستقر")
status_en = "Critical" if risk >= 70 else ("Watch" if risk >= 40 else "Stable")
choice = st.radio("Language", ["العربية", "English"], horizontal=True, key="lang_choice", label_visibility="collapsed")
st.session_state.lang = "ar" if choice == "العربية" else "en"
lang = st.session_state.lang
status = status_ar if lang == "ar" else status_en
risk_color = "#DC2626" if risk >= 70 else ("#D97706" if risk >= 40 else "#166534")
side = "rtl" if lang == "ar" else "ltr"
align = "right" if lang == "ar" else "left"
st.markdown(
    f"""
<style>
  html, body, [data-testid="stAppViewContainer"], .stApp, .block-container,
  [data-testid="stVerticalBlock"], .stMarkdown, section, [data-testid="stTabs"],
  [data-testid="stDataFrame"], label, p {{
    direction: {side} !important;
    text-align: {align} !important;
  }}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="hero">
  <div style="display:flex;align-items:center;gap:14px;">
    <svg width="78" height="92" viewBox="0 0 78 92" aria-label="71WM">
      <polygon points="39,3 73,22 73,70 39,89 5,70 5,22" fill="#082F49" stroke="#D4AF37" stroke-width="2.4"/>
      <circle cx="52" cy="28" r="5" fill="#D4AF37"/>
      <path d="M18 36c6-5 10-5 16 0 5-4 9-4 14 0" fill="#fff"/>
      <path d="M14 46c10-6 16-2 24 2 8 4 14 2 26-4v8c-12 6-18 8-26 4-8-4-14-8-24-2z" fill="#2BB3C7"/>
      <path d="M14 58c10-8 22-8 50 2v10H14z" fill="#D4AF37"/>
      <text x="39" y="80" text-anchor="middle" font-size="11" font-family="Arial" font-weight="700" fill="#D4AF37">71WM</text>
    </svg>
    <div>
      <div class="kicker">71WM · UAE WEATHER INTELLIGENCE</div>
      <h1>{tr("لوحة القيادة الجوية", "Weather command deck")}</h1>
    </div>
  </div>
  <div class="sub">{tr(f"قراءة موحّدة للعواصف، الضباب، الكوس، الشمال، والإجهاد الحراري على {len(STATIONS)} محطة.", f"Storms, fog, Al-Kous, shamal and heat stress across {len(STATIONS)} stations.")}</div>
  <span class="pill">{tr("توقيت الإمارات", "UAE time")} {uae_now.strftime('%H:%M')}</span>
  <span class="pill" style="background:{risk_color};color:#fff;">{tr("المخاطر الوطنية", "National risk")} {risk}% · {status}</span>
  <span class="pill">{tr("دورة النموذج", "Model cycle")} {cycle}</span>
  <span class="pill">{tr("نشرة الخمسة أيام", "Five-day bulletin")} {bulletin_day} · 05:00</span>
</div>
""",
    unsafe_allow_html=True,
)
if not ok:
    st.error(tr(f"تعذر جلب Open-Meteo: {live}", f"Open-Meteo fetch failed: {live}"))

c1, c2, c3, c4, c5 = st.columns(5)
cards = [
    (tr("عواصف", "Storms"), safe_max(now_df["Storm Probability"]) if not now_df.empty else 0, "%"),
    (tr("ضباب", "Fog"), safe_max(now_df["Fog Probability"]) if not now_df.empty else 0, "%"),
    (tr("كوس / رذاذ", "Al-Kous / drizzle"), max(safe_max(now_df["AlKous Prob"]) if not now_df.empty else 0, safe_max(now_df["Drizzle Prob"]) if not now_df.empty else 0), "%"),
    (tr("غبار الشمال", "Shamal dust"), safe_max(now_df["Shamal Index"]) if not now_df.empty else 0, "%"),
    (tr("أقصى إحساس", "Peak feels-like"), safe_max(now_df["Apparent Temp"]) if not now_df.empty else 0, "°C"),
]
for col, (title, value, unit) in zip((c1, c2, c3, c4, c5), cards):
    col.markdown(f"<div class='card'><div class='muted'>{title}</div><b>{value:.0f} {unit}</b></div>", unsafe_allow_html=True)

def hazard_window(frame: pd.DataFrame, column: str, threshold: float, sector: str):
    part = frame[frame["Sector"] == sector] if not frame.empty else frame
    if part.empty or column not in part:
        return None
    active_times = []
    for slot in timeline_str:
        slot_df = part[part["Time"] == slot]
        if not slot_df.empty and safe_max(slot_df[column]) >= threshold:
            active_times.append(slot)
    if not active_times:
        return None
    now_index = 0
    start_index = timeline_str.index(active_times[0])
    if start_index > now_index + 1:
        return None
    run = [active_times[0]]
    previous = timeline_str.index(active_times[0])
    for slot in active_times[1:]:
        current = timeline_str.index(slot)
        if current == previous + 1:
            run.append(slot)
            previous = current
        else:
            break
    peak_slot = max(run, key=lambda slot: safe_max(part[part["Time"] == slot][column]))
    peak_df = part[part["Time"] == peak_slot].sort_values(column, ascending=False)
    stations = peak_df[peak_df[column] >= threshold]["Station"].head(4).tolist()
    if not stations:
        return None
    joiner = "، " if st.session_state.get("lang") != "en" else ", "
    return run[0], run[-1], int(safe_max(peak_df[column])), joiner.join(stations)


alerts = []
if not df.empty:
    checks = [
        ("Fog Probability", 50, "ضباب وتدني رؤية", "fog and low visibility"),
        ("Storm Probability", 65, "عواصف وأمطار رعدية", "storms and thundery rain"),
        ("Shamal Index", 60, "غبار الشمال", "shamal dust"),
        ("Drizzle Prob", 60, "رذاذ الكوس", "Al-Kous drizzle"),
    ]
    for column, threshold, ar, en in checks:
        for sector in SECTOR_MAP:
            found = hazard_window(df, column, threshold, sector)
            if not found:
                continue
            start, end, level, stations = found
            place = SECTOR_EN.get(sector, sector) if lang == "en" else sector
            alerts.append(tr(
                f"الخطر الحالي: {ar} بنسبة {level}% على {place}، في {stations}. البداية {start} والنهاية المتوقعة {end}.",
                f"Current hazard: {en} at {level}% over {place}, at {stations}. Starts {start} and is expected to end {end}.",
            ))
if alerts and risk >= 40:
    st.markdown(
        "<div style='background:#7F1D1D;border:1px solid #FCA5A5;border-radius:14px;padding:14px 16px;margin:10px 0 16px;'>"
        + "".join(f"<p style='color:#FEE2E2;margin:6px 0;font-size:18px;'>{line}</p>" for line in alerts)
        + "</div>",
        unsafe_allow_html=True,
    )
else:
    st.info(tr("لا خطر وطني قائم حالياً.", "No national hazard is active now."))

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    tr("القيادة", "Command"),
    tr("المخاطر", "Hazards"),
    tr("الحرارة والشمال", "Heat & shamal"),
    tr("المحطات", "Stations"),
    tr("خمسة أيام", "5-day outlook"),
    tr("النينيو", "ENSO"),
    tr("النماذج والغبار", "Models & dust"),
    tr("في مثل هذا اليوم", "On this day"),
])


def density(frame: pd.DataFrame, z: str, lat=24.4, lon=54.6, zoom=5.5, title=""):
    if frame.empty:
        fig = go.Figure()
        fig.update_layout(title=title or "لا بيانات", height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=16))
        return fig
    fig = px.density_mapbox(
        frame, lat="Latitude", lon="Longitude", z=z, radius=42,
        center=dict(lat=lat, lon=lon), zoom=zoom,
        mapbox_style="open-street-map", range_color=[0, 100], opacity=0.72, title=title,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=46, b=0), height=480,
        paper_bgcolor="rgba(0,0,0,0)", font=dict(size=16, color="#e7eef8"),
        title_font_size=20,
    )
    return fig


with tab1:
    if not df.empty:
        peak = df.groupby("Time")[["Storm Probability", "Fog Probability", "Shamal Index", "Drizzle Prob", "AlKous Prob"]].max().reset_index()
        fig = go.Figure()
        names = {
            "Storm Probability": tr("عواصف", "Storms"),
            "Fog Probability": tr("ضباب", "Fog"),
            "Shamal Index": tr("شمال وغبار", "Shamal dust"),
            "Drizzle Prob": tr("رذاذ", "Drizzle"),
            "AlKous Prob": tr("سحب الكوس", "Al-Kous cloud"),
        }
        colors = {
            "Storm Probability": "#f87171",
            "Fog Probability": "#93c5fd",
            "Shamal Index": "#fbbf24",
            "Drizzle Prob": "#38bdf8",
            "AlKous Prob": "#c4b5fd",
        }
        for col in names:
            fig.add_trace(go.Scatter(x=peak["Time"], y=peak[col], name=names[col], line=dict(color=colors[col], width=3)))
        fig.update_layout(
            title=tr("ذروة كل خطر خلال 5 أيام", "Peak hazard over 5 days"),
            height=520,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(size=14, color="#e7eef8"),
            legend=dict(orientation="h", y=-0.35, x=0, font=dict(size=13)),
            margin=dict(l=8, r=8, t=50, b=120),
            xaxis=dict(tickangle=-40, nticks=6, title=""),
            yaxis=dict(title=tr("الاحتمال %", "Probability %"), range=[0, 100]),
        )
        fig.update_xaxes(automargin=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown(tr(
        "**معنى الخطوط:** الأحمر عواصف، الأزرق ضباب، الذهبي شمال وغبار، السماوي رذاذ، البنفسجي سحب الكوس.",
        "**Lines:** red storms, blue fog, gold shamal dust, cyan drizzle, purple Al-Kous cloud.",
    ))
    st.markdown(tr("#### أثر تشغيلي الآن", "#### Operational impact now"))
    if now_df.empty:
        st.warning(tr("لا توجد قراءة حالية.", "No current reading."))
    else:
        hot = now_df.assign(score=now_df[["Storm Probability", "Fog Probability", "Shamal Index", "Drizzle Prob"]].max(axis=1)).sort_values("score", ascending=False).head(6)
        for _, row in hot.iterrows():
            sector = row["Sector"] if lang == "ar" else SECTOR_EN.get(row["Sector"], row["Sector"])
            st.markdown(f"**{row['Station']}** · {sector}  \n{ops_note(row)}")
    st.markdown(tr("#### ملخص القطاعات", "#### Sector summary"))
    if not now_df.empty:
        sector = now_df.groupby("Sector")[["Storm Probability", "Fog Probability", "Shamal Index", "Apparent Temp"]].max().round(0)
        sector = sector.rename(columns={"Storm Probability": tr("عواصف %", "Storms %"), "Fog Probability": tr("ضباب %", "Fog %"), "Shamal Index": tr("شمال %", "Shamal %"), "Apparent Temp": tr("الإحساس °C", "Feels-like °C")})
        st.dataframe(sector, use_container_width=True)

with tab2:
    picked = st.select_slider(tr("الوقت", "Time"), options=timeline_str, key="risk_time")
    frame = df[df["Time"] == picked] if not df.empty else pd.DataFrame()
    a, b = st.columns(2)
    a.plotly_chart(density(frame, "Storm Probability", title=tr("احتمال العواصف %", "Storm probability %")), use_container_width=True)
    b.plotly_chart(density(frame, "Fog Probability", title=tr("احتمال الضباب %", "Fog probability %")), use_container_width=True)
    c, d = st.columns(2)
    east = frame[frame["Longitude"] >= 55.8] if not frame.empty else frame
    c.plotly_chart(density(east, "AlKous Prob", 25.2, 56.2, 7.2, tr("سحب الكوس %", "Al-Kous cloud %")), use_container_width=True)
    d.plotly_chart(density(east, "Drizzle Prob", 25.2, 56.2, 7.2, tr("رذاذ الكوس %", "Al-Kous drizzle %")), use_container_width=True)
    st.info(tr(
        "سحب الكوس: سحب منخفضة تأتي من بحر عمان مع رياح شرقية إلى جنوبية شرقية ورطوبة عالية، وغالباً تلامس جبال الفجيرة ورأس الخيمة. قد يصاحبها رذاذ صباحاً.",
        "Al-Kous: low cloud from the Gulf of Oman with easterly to southeasterly wind and high humidity, often against the Fujairah and Ras Al Khaimah mountains. Morning drizzle may follow.",
    ))
    components.html('<iframe src="https://embed.windy.com/embed.html?type=map&location=coordinates&overlay=satellite&lat=24.6&lon=54.8&zoom=6" width="100%" height="430" frameborder="0"></iframe>', height=450)

with tab3:
    picked = st.select_slider(tr("الوقت", "Time"), options=timeline_str, key="heat_time")
    frame = df[df["Time"] == picked] if not df.empty else pd.DataFrame()
    a, b = st.columns(2)
    a.plotly_chart(density(frame, "Shamal Index", title=tr("غبار الشمال %", "Shamal dust %")), use_container_width=True)
    if not frame.empty:
        heat = frame.sort_values("Apparent Temp", ascending=False)[["Station", "Sector", "Temperature", "Apparent Temp", "Humidity", "Wind"]].head(8).copy()
        wind_unit = "كم/س" if lang == "ar" else "km/h"
        heat["temp"] = heat["Temperature"].map(lambda v: f"{v:.1f} °C")
        heat["feel"] = heat["Apparent Temp"].map(lambda v: f"{v:.1f} °C")
        heat["rh"] = heat["Humidity"].map(lambda v: f"{v:.0f}%")
        heat["wind"] = heat["Wind"].map(lambda v: f"{v:.0f} {wind_unit}")
        heat["band"] = heat["Apparent Temp"].map(heat_band)
        heat["sector"] = heat["Sector"].map(lambda s: s if lang == "ar" else SECTOR_EN.get(s, s))
        b.dataframe(heat[["Station", "sector", "temp", "feel", "rh", "wind", "band"]].rename(columns={
            "Station": tr("المحطة", "Station"), "sector": tr("القطاع", "Sector"),
            "temp": tr("الحرارة", "Temperature"), "feel": tr("الإحساس", "Feels-like"),
            "rh": tr("الرطوبة", "Humidity"), "wind": tr("الرياح", "Wind"), "band": tr("الإجهاد", "Stress"),
        }), use_container_width=True, hide_index=True)
        st.caption(tr(
            "الشمال رياح شمالية غربية. فوق 20 كم/س قد تثير الغبار. الإجهاد: 35 حار، 40 مرتفع، 45 شديد.",
            "Shamal is a northwesterly wind. Above 20 km/h it may raise dust. Heat stress: 35 hot, 40 high, 45 extreme.",
        ))

AIRPORTS = {
    "OMAA": "مطار زايد الدولي",
    "OMDB": "مطار دبي",
    "OMDW": "مطار آل مكتوم",
    "OMAL": "مطار العين",
    "OMSJ": "مطار الشارقة",
    "OMRK": "مطار رأس الخيمة",
    "OMFJ": "مطار الفجيرة",
    "OMAD": "مطار البطين",
}


@st.cache_data(ttl=600, show_spinner=False)
def fetch_metar() -> Tuple[bool, Any]:
    try:
        response = requests.get(
            "https://aviationweather.gov/api/data/metar",
            params={"ids": ",".join(AIRPORTS), "format": "json"},
            timeout=25,
        )
        response.raise_for_status()
        return True, response.json()
    except Exception as exc:
        return False, str(exc)


with tab4:
    st.markdown(tr("#### الرصد الفعلي للمطارات", "#### Live airport observations"))
    st.caption(tr(
        "قراءات METAR الفعلية من مطارات الدولة عبر شبكة أرصاد الطيران، وتتجدد كل عشر دقائق. المركز الوطني لا يتيح واجهة مفتوحة لبقية المحطات الأرضية.",
        "Live METAR from UAE airports via the aviation weather network, refreshed every ten minutes. NCM does not publish an open feed for the other surface stations.",
    ))
    metar_ok, metars = fetch_metar()
    if not metar_ok:
        st.warning(tr(f"تعذر جلب الرصد: {metars}", f"Observations unavailable: {metars}"))
    elif metars:
        def phenomenon(raw: str) -> str:
            text = raw.upper()
            hits = []
            if any(code in text.split() for code in ("FG", "BCFG", "PRFG", "FZFG", "MIFG")):
                hits.append(tr("ضباب", "Fog"))
            if any(code in text for code in ("TSRA", "TS", "VCTS", "+TS", "CB")):
                hits.append(tr("عاصفة أو سحب ركامية CB", "Storm or CB"))
            if any(code in text.split() for code in ("RA", "SHRA", "DZ", "+RA", "SHRA")):
                hits.append(tr("مطر", "Rain"))
            if any(code in text.split() for code in ("DU", "SA", "BLDU", "BLSA", "SS", "DS", "DRDU", "DRSA")):
                hits.append(tr("غبار", "Dust"))
            return "، ".join(hits) if lang == "ar" else ", ".join(hits)

        rows_obs = []
        for item in metars:
            code = item.get("icaoId", "")
            raw = item.get("rawOb", "")
            event = phenomenon(raw)
            rows_obs.append({
                tr("المطار", "Airport"): f"{AIRPORTS.get(code, code)} ({code})",
                tr("الحالة", "Status"): event or tr("مستقر", "Quiet"),
                tr("الحرارة", "Temperature"): f"{item.get('temp', '—')} °C",
                tr("الندى", "Dew point"): f"{item.get('dewp', '—')} °C",
                tr("الرياح", "Wind"): f"{item.get('wdir', 'VRB')}° / {item.get('wspd', '—')} kt",
                tr("الرؤية", "Visibility"): item.get("visib", "—"),
                tr("التقرير", "Report"): raw,
            })
        frame_obs = pd.DataFrame(rows_obs)
        status_col = tr("الحالة", "Status")
        quiet = tr("مستقر", "Quiet")

        def paint(row):
            if row[status_col] != quiet:
                return ["background-color: #7F1D1D; color: #FEE2E2"] * len(row)
            return [""] * len(row)

        st.dataframe(frame_obs.style.apply(paint, axis=1), use_container_width=True, hide_index=True)
    st.markdown("---")
    if df.empty:
        st.warning(tr("لا توجد محطات للعرض.", "No stations to show."))
    else:
        names = sorted(df["Station"].unique())
        s1, s2 = st.columns(2)
        one = s1.selectbox(tr("المحطة", "Station"), names, index=0)
        two = s2.selectbox(tr("قارن مع", "Compare with"), [tr("بدون", "None")] + names, index=0)
        series = df[df["Station"] == one]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=series["Time"], y=series["Temperature"], name=f"{one} °C", line=dict(color="#38bdf8")))
        fig.add_trace(go.Scatter(x=series["Time"], y=series["Apparent Temp"], name=tr("الإحساس °C", "Feels-like °C"), line=dict(color="#f59e0b", dash="dot")))
        if two not in ("بدون", "None"):
            other = df[df["Station"] == two]
            fig.add_trace(go.Scatter(x=other["Time"], y=other["Temperature"], name=f"{two} °C", line=dict(color="#d4af37")))
        fig.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", title=tr("مقارنة الحرارة °C", "Temperature comparison °C"))
        st.plotly_chart(fig, use_container_width=True)
        slot = st.select_slider(tr("جدول الوقت", "Table time"), options=timeline_str, key="table_time")
        table = df[df["Time"] == slot].sort_values("Apparent Temp", ascending=False).copy()
        unit = "كم/س" if lang == "ar" else "km/h"
        show = pd.DataFrame({
            tr("المحطة", "Station"): table["Station"],
            tr("القطاع", "Sector"): table["Sector"].map(lambda s: s if lang == "ar" else SECTOR_EN.get(s, s)),
            tr("الحرارة", "Temperature"): table["Temperature"].map(lambda v: f"{v:.1f} °C"),
            tr("الإحساس", "Feels-like"): table["Apparent Temp"].map(lambda v: f"{v:.1f} °C"),
            tr("الرطوبة", "Humidity"): table["Humidity"].map(lambda v: f"{v:.0f}%"),
            tr("الرياح", "Wind"): table["Wind"].map(lambda v: f"{v:.0f} {unit}"),
            tr("الهبات", "Gusts"): table["Gust"].map(lambda v: f"{v:.0f} {unit}"),
            tr("عواصف", "Storms"): table["Storm Probability"].map(lambda v: f"{v:.0f}%"),
            tr("ضباب", "Fog"): table["Fog Probability"].map(lambda v: f"{v:.0f}%"),
            tr("سحب الكوس", "Al-Kous"): table["AlKous Prob"].map(lambda v: f"{v:.0f}%"),
            tr("رذاذ", "Drizzle"): table["Drizzle Prob"].map(lambda v: f"{v:.0f}%"),
            tr("الشمال", "Shamal"): table["Shamal Index"].map(lambda v: f"{v:.0f}%"),
        })
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.download_button(tr("تنزيل هذه اللقطة CSV", "Download this snapshot CSV"), show.to_csv(index=False).encode("utf-8-sig"), "71wm_snapshot.csv", "text/csv")

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_marine() -> Tuple[bool, Any]:
    points = {
        "gulf_coast": (24.55, 54.40),
        "gulf_offshore": (25.40, 53.00),
        "oman_coast": (25.15, 56.42),
        "oman_offshore": (25.30, 57.20),
    }
    try:
        params = {
            "latitude": ",".join(str(v[0]) for v in points.values()),
            "longitude": ",".join(str(v[1]) for v in points.values()),
            "hourly": "wave_height,wave_period,sea_surface_temperature",
            "timezone": "Asia/Dubai",
            "forecast_days": 5,
        }
        response = requests.get("https://marine-api.open-meteo.com/v1/marine", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            data = [data]
        return True, dict(zip(points.keys(), data))
    except Exception as exc:
        return False, str(exc)


def sea_words(height: float) -> str:
    if height < 0.5:
        return tr("هادئ", "calm")
    if height < 1.25:
        return tr("خفيف الموج", "slight")
    if height < 2.5:
        return tr("معتدل الموج", "moderate")
    if height < 4:
        return tr("مضطرب", "rough")
    return tr("هائج", "very rough")


def feet_phrase(meters: float) -> str:
    feet = max(1, round(meters * 3.28084)) if meters >= 0.2 else 1
    if lang == "ar":
        return "قدم" if feet == 1 else ("قدمين" if feet == 2 else f"{feet} أقدام")
    return "1 foot" if feet == 1 else f"{feet} feet"


def wind_words(direction: float, speed: float) -> str:
    names_ar = ["شمالية", "شمالية شرقية", "شرقية", "جنوبية شرقية", "جنوبية", "جنوبية غربية", "غربية", "شمالية غربية"]
    names_en = ["northerly", "northeasterly", "easterly", "southeasterly", "southerly", "southwesterly", "westerly", "northwesterly"]
    idx = int(((direction + 22.5) % 360) / 45)
    name = names_ar[idx] if lang == "ar" else names_en[idx]
    if speed < 15:
        force = tr("خفيفة", "light")
    elif speed < 30:
        force = tr("خفيفة إلى معتدلة", "light to moderate")
    elif speed < 40:
        force = tr("نشطة", "fresh")
    else:
        force = tr("قوية", "strong")
    return name, force


with tab5:
    st.markdown(tr(
        f"#### نشرة خمسة أيام — أُصدرت 05:00 بتوقيت الإمارات بعد مراجعة دورة {cycle}",
        f"#### Five-day bulletin — issued 05:00 UAE after review of cycle {cycle}",
    ))
    st.caption(tr(
        "تُقفل النشرة اليومية عند 05:00 بعد نافذة التحليل 04:00. الخرائط الحية تتحدث مع دورات GFS 00 و06 و12 و18 بالتوقيت العالمي بعد جاهزية الحقول.",
        "The daily bulletin locks at 05:00 UAE after the 04:00 analysis window. Live charts refresh on the GFS 00, 06, 12 and 18 UTC cycles once fields are available.",
    ))
    marine_ok, marine = fetch_marine()
    if not marine_ok:
        st.warning(tr(f"تعذر جلب حالة البحر: {marine}", f"Sea state unavailable: {marine}"))
    for date in dates[:5]:
        day = df[df["DateOnly"] == date] if not df.empty else pd.DataFrame()
        if day.empty:
            continue
        noon = day[day["Time"].str.contains("13:00|16:00")]
        sample = noon if not noon.empty else day
        direction = safe_max(sample["Wind Dir"]) if "Wind Dir" in sample else 320
        speed = safe_max(day["Wind"])
        wname, wforce = wind_words(direction, speed)
        cloud = safe_max(day["AlKous Prob"])
        sky = tr("غائم", "cloudy") if cloud >= 60 else (tr("صحو إلى غائم جزئياً", "fair to partly cloudy") if cloud >= 25 else tr("صحو بوجه عام", "generally fair"))
        tmax, tmin = safe_max(day["Temperature"]), day["Temperature"].min()
        extras = []
        if safe_max(day["Fog Probability"]) >= 45:
            where = day.loc[day["Fog Probability"].idxmax(), "Sector"]
            where = SECTOR_EN.get(where, where) if lang == "en" else where
            extras.append(tr(f"مع فرصة ضباب على {where} فجراً", f"with a chance of fog over {where} at dawn"))
        if safe_max(day["Storm Probability"]) >= 40 or safe_max(day["Drizzle Prob"]) >= 45:
            where = day.loc[day[["Storm Probability", "Drizzle Prob"]].max(axis=1).idxmax(), "Sector"]
            where = SECTOR_EN.get(where, where) if lang == "en" else where
            extras.append(tr(f"وفرصة أمطار على {where}", f"and a chance of rain over {where}"))
        if safe_max(day["Shamal Index"]) >= 45:
            where = day.loc[day["Shamal Index"].idxmax(), "Sector"]
            where = SECTOR_EN.get(where, where) if lang == "en" else where
            extras.append(tr(f"مع غبار مثار على {where}", f"with raised dust over {where}"))
        extra = ("، " if lang == "ar" else ", ").join(extras)

        def wave_pair(key):
            if not marine_ok:
                return 0.3, 0.6
            hourly = marine[key].get("hourly") or {}
            times = hourly.get("time") or []
            heights = hourly.get("wave_height") or []
            day_no = date.split()[-1]
            vals = [safe_num(h, 0.3) for t, h in zip(times, heights) if f"-{day_no}T" in t or t[8:10] == day_no]
            if not vals:
                return 0.3, 0.6
            return min(vals), max(vals)

        gc0, gc1 = wave_pair("gulf_coast")
        go0, go1 = wave_pair("gulf_offshore")
        oc0, oc1 = wave_pair("oman_coast")
        oo0, oo1 = wave_pair("oman_offshore")
        afternoon = tr("يضطرب بعد الظهر", "becoming rougher in the afternoon") if go1 > gc1 + 0.4 else tr("يبقى على حاله", "staying similar")
        text = tr(
            f"الطقس {sky} بوجه عام{('، ' + extra) if extra else ''}، والحرارة بين {tmin:.0f} و{tmax:.0f} درجة. الرياح {wname} على البحر، {wforce}، وقد تنشط بعد الظهر. البحر في الخليج العربي {sea_words(gc1)} و{afternoon}، وارتفاع الموج قرب الساحل من {feet_phrase(gc0)} إلى {feet_phrase(gc1)} وفي العمق يصل إلى {feet_phrase(go1)}. أما بحر عمان فيكون {sea_words(oc1)} بوجه عام، وارتفاع الموج قرب الساحل {feet_phrase(oc1)} وفي العمق من {feet_phrase(oo0)} إلى {feet_phrase(oo1)}.",
            f"Weather will be {sky} overall{(', ' + extra) if extra else ''}, with temperatures from {tmin:.0f} to {tmax:.0f} °C. Wind over the sea will be {wname} and {wforce}, freshening in the afternoon. The Arabian Gulf will be {sea_words(gc1)} and {afternoon}; waves near the coast {feet_phrase(gc0)} to {feet_phrase(gc1)}, and up to {feet_phrase(go1)} offshore. The Gulf of Oman will be {sea_words(oc1)} overall, with waves near the coast {feet_phrase(oc1)} and {feet_phrase(oo0)} to {feet_phrase(oo1)} offshore.",
        )
        st.markdown(f"<div class='card'><div class='kicker'>{date}</div><p>{text}</p></div>", unsafe_allow_html=True)
    st.caption(tr(
        "النشرة وصفية من بيانات الرياح والموج. ارتفاع الموج بالقدم قرب ميناء أبوظبي وميناء الفجيرة وفي العمق.",
        "The bulletin is written from wind and wave data. Wave height is in feet near Abu Dhabi and Fujairah ports and offshore.",
    ))

with tab6:
    ok_oni, oni = fetch_oni()
    if not ok_oni:
        st.error(tr(f"تعذر مؤشر ONI: {oni}", f"ONI fetch failed: {oni}"))
    else:
        latest = oni.iloc[-1]
        anom = float(latest["anom"])
        phase = tr("نينيو", "El Niño") if anom >= 0.5 else (tr("نينيا", "La Niña") if anom <= -0.5 else tr("محايد", "Neutral"))
        m1, m2, m3 = st.columns(3)
        m1.metric(tr("آخر موسم", "Latest season"), f"{latest['season']} {int(latest['year'])}")
        m2.metric("ONI", f"{anom:+.2f} °C")
        m3.metric(tr("الحالة", "Phase"), phase)
        recent = oni.tail(36)
        fig = go.Figure()
        fig.add_hrect(y0=0.5, y1=3, fillcolor="#7f1d1d", opacity=0.25, line_width=0)
        fig.add_hrect(y0=-3, y1=-0.5, fillcolor="#1e3a8a", opacity=0.25, line_width=0)
        fig.add_trace(go.Scatter(x=recent["label"], y=recent["anom"], mode="lines+markers", line=dict(color="#d4af37", width=3)))
        fig.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", title=tr("مؤشر النينيو 3.4 °C", "Niño 3.4 index °C"))
        st.plotly_chart(fig, use_container_width=True)
        if anom >= 0.5:
            st.info(tr("النينيو يميل إحصائياً إلى شتاء أرطب نسبياً على أجزاء من شبه الجزيرة. ليس ضماناً لموسم ماطر في الإمارات.", "El Niño statistically leans toward a relatively wetter winter on parts of the peninsula. It does not guarantee a wet UAE season."))
        elif anom <= -0.5:
            st.info(tr("النينيا تميل إحصائياً إلى شتاء أجف. الحالات القوية المنفردة تبقى ممكنة.", "La Niña statistically leans toward a drier winter. Strong individual events remain possible."))
        else:
            st.info(tr("الوضع المحايد يعني أن طقس الإمارات يتحدد أكثر بالمنخفضات المحلية ودورة الخليج.", "Neutral means UAE weather is driven more by local lows and the Gulf cycle."))
        st.dataframe(oni.tail(8)[["label", "sst", "anom"]].iloc[::-1].rename(columns={"label": tr("الموسم", "Season"), "sst": tr("الحرارة °C", "SST °C"), "anom": tr("الشذوذ °C", "Anomaly °C")}), use_container_width=True, hide_index=True)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_model_rain(model: str) -> Tuple[bool, Any]:
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": "25.12,25.95,24.45",
                "longitude": "56.33,56.17,54.38",
                "hourly": "precipitation,cloudcover_low,windspeed_10m",
                "models": model,
                "forecast_days": 3,
                "timezone": "Asia/Dubai",
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return True, data if isinstance(data, list) else [data]
    except Exception as exc:
        return False, str(exc)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_dust() -> Tuple[bool, Any]:
    points = {"الساحل الشرقي": (25.12, 56.33), "جبل جيس": (25.95, 56.17), "أبوظبي": (24.45, 54.38), "العين": (24.26, 55.61)}
    try:
        response = requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                "latitude": ",".join(str(v[0]) for v in points.values()),
                "longitude": ",".join(str(v[1]) for v in points.values()),
                "hourly": "pm10,dust",
                "forecast_days": 3,
                "timezone": "Asia/Dubai",
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return True, dict(zip(points, data if isinstance(data, list) else [data]))
    except Exception as exc:
        return False, str(exc)


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def fetch_on_this_day(month: int, day: int) -> Tuple[bool, Any]:
    spots = {
        "أبوظبي": (24.45, 54.38), "دبي": (25.25, 55.33), "الشارقة": (25.35, 55.39),
        "رأس الخيمة": (25.79, 55.94), "الفجيرة": (25.12, 56.33), "العين": (24.26, 55.61),
        "الظفرة": (23.68, 53.70), "جبل جيس": (25.95, 56.17), "الذيد": (25.29, 55.88),
    }
    names = list(spots)
    try:
        response = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": ",".join(str(v[0]) for v in spots.values()),
                "longitude": ",".join(str(v[1]) for v in spots.values()),
                "start_date": "2010-01-01",
                "end_date": "2025-12-31",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
                "timezone": "Asia/Dubai",
            },
            timeout=50,
        )
        if response.status_code == 429:
            return False, "تجاوز حد الطلبات. أعد فتح التبويب بعد دقيقة."
        response.raise_for_status()
        payload = response.json()
        blocks = payload if isinstance(payload, list) else [payload]
        rows = []
        for name, block in zip(names, blocks):
            daily = block.get("daily") or {}
            for date, tmax, tmin, rain, wind in zip(daily.get("time", []), daily.get("temperature_2m_max", []), daily.get("temperature_2m_min", []), daily.get("precipitation_sum", []), daily.get("wind_speed_10m_max", [])):
                if date[5:10] == f"{month:02d}-{day:02d}" and tmax is not None:
                    rows.append({"place": name, "date": date, "tmax": tmax, "tmin": tmin, "rain": rain or 0, "wind": wind or 0})
        return True, pd.DataFrame(rows)
    except Exception as exc:
        return False, "تعذر الأرشيف مؤقتاً. أعد المحاولة بعد دقيقة."


with tab7:
    st.markdown(tr("#### مقارنة GFS وECMWF وغبار CAMS", "#### GFS, ECMWF and CAMS dust"))
    st.caption(tr(
        "الجبال فوق 800 م، مثل جبل جيس، ترفع فرصة الكوس والرذاذ عندما تكون الرياح شرقية رطبة. الغبار من نموذج CAMS وليس من سرعة الرياح فقط.",
        "Peaks above 800 m, such as Jebel Jais, raise Al-Kous and drizzle chances in moist easterly flow. Dust comes from CAMS, not wind speed alone.",
    ))
    g_ok, gfs = fetch_model_rain("gfs_seamless")
    e_ok, ecmwf = fetch_model_rain("ecmwf_ifs")
    labels = [tr("الفجيرة", "Fujairah"), tr("جبل جيس", "Jebel Jais"), tr("أبوظبي", "Abu Dhabi")]
    if g_ok and e_ok:
        rows = []
        for i, label in enumerate(labels):
            g_rain = max(gfs[i].get("hourly", {}).get("precipitation") or [0])
            e_rain = max(ecmwf[i].get("hourly", {}).get("precipitation") or [0])
            rows.append({tr("الموقع", "Place"): label, "GFS mm": round(g_rain, 1), "ECMWF mm": round(e_rain, 1)})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.info(tr("إذا اقترب الرقمان فالثقة أعلى. إذا افترقا فالحالة غير محسومة.", "Close numbers mean higher confidence. A wide gap means the event is uncertain."))
    else:
        st.warning(tr("تعذر جلب أحد النموذجين.", "One of the models could not be fetched."))
    d_ok, dust = fetch_dust()
    if d_ok:
        dust_rows = []
        for place, payload in dust.items():
            values = [v for v in (payload.get("hourly") or {}).get("dust") or [] if v is not None]
            pm = [v for v in (payload.get("hourly") or {}).get("pm10") or [] if v is not None]
            dust_rows.append({tr("الموقع", "Place"): place, tr("أعلى غبار", "Peak dust"): round(max(values or [0]), 1), "PM10": round(max(pm or [0]), 1)})
        st.dataframe(pd.DataFrame(dust_rows), use_container_width=True, hide_index=True)
    else:
        st.warning(tr(f"تعذر جلب الغبار: {dust}", f"Dust unavailable: {dust}"))

with tab8:
    st.markdown(tr("#### في مثل هذا اليوم", "#### On this day"))
    ok_day, history = fetch_on_this_day(uae_now.month, uae_now.day)
    if not ok_day:
        st.warning(tr(f"تعذر الأرشيف: {history}", f"Archive unavailable: {history}"))
    elif history.empty:
        st.info(tr("لا سجل لهذا التاريخ.", "No record for this date."))
    else:
        wet = history.loc[history["rain"].idxmax()]
        hot = history.loc[history["tmax"].idxmax()]
        cold = history.loc[history["tmin"].idxmin()]
        windy = history.loc[history["wind"].idxmax()]
        lines = [
            tr(f"أعلى كمية أمطار: {wet['rain']:.1f} مم، سُجّلت في {wet['place']} بتاريخ {wet['date']}.", f"Highest rainfall: {wet['rain']:.1f} mm at {wet['place']} on {wet['date']}."),
            tr(f"أعلى درجة حرارة: {hot['tmax']:.1f} °C، سُجّلت في {hot['place']} بتاريخ {hot['date']}.", f"Highest temperature: {hot['tmax']:.1f} °C at {hot['place']} on {hot['date']}."),
            tr(f"أقل درجة حرارة: {cold['tmin']:.1f} °C، سُجّلت في {cold['place']} بتاريخ {cold['date']}.", f"Lowest temperature: {cold['tmin']:.1f} °C at {cold['place']} on {cold['date']}."),
            tr(f"أعلى سرعة رياح: {windy['wind']:.0f} كم/س، سُجّلت في {windy['place']} بتاريخ {windy['date']}.", f"Highest wind: {windy['wind']:.0f} km/h at {windy['place']} on {windy['date']}."),
        ]
        align = "right" if lang == "ar" else "left"
        side = "rtl" if lang == "ar" else "ltr"
        items = "".join(f"<li style='margin:8px 0;'>{line}</li>" for line in lines)
        st.markdown(
            f"<div dir='{side}' style='direction:{side};text-align:{align};background:#0f172a;border-radius:14px;padding:14px 18px;'><b>{tr('في مثل هذا اليوم على الدولة', 'On this day nationwide')}</b><ul style='direction:{side};text-align:{align};padding-inline-start:1.2rem;'>{items}</ul></div>",
            unsafe_allow_html=True,
        )
        if wet["rain"] >= 20:
            st.info(tr(f"الظاهرة الأبرز: يوم ماطر استثنائي في {wet['place']}.", f"Notable event: an exceptional wet day at {wet['place']}."))
        st.caption(tr("السجل من أرشيف إعادة التحليل منذ 2000 لعدد من مواقع الدولة، ويذكر أعلى قيمة ومكانها. ليس سجل المركز الوطني الرسمي.", "The record uses the reanalysis archive since 2000 at several UAE sites and names the place of each extreme. It is not the official NCM record."))
