"""
71wm scheduled weather alert.

Reads live Open-Meteo data for UAE stations, applies the same storm / fog /
drizzle rules used by the Streamlit app, and emails recipients only when a
threshold is crossed. A local state file stops the same alert type from being
sent more than once per UAE day (pair it with actions/cache in GitHub Actions).
"""

from __future__ import annotations

import json
import os
import re
import smtplib
from datetime import datetime, timedelta
from email.header import Header
from email.mime.text import MIMEText
from pathlib import Path

import requests

STATE_PATH = Path(os.environ.get("ALERT_STATE_PATH", "alert_state.json"))
EMAIL_LIST = Path(os.environ.get("EMAIL_LIST_PATH", "email_list.txt"))

STATIONS = [
    {"name": "أبوظبي", "en": "Abu Dhabi", "lat": 24.4760, "lon": 54.3290, "type": "Coast", "sector": "أبوظبي والظفرة"},
    {"name": "الرويس", "en": "Al Ruwais", "lat": 24.0915, "lon": 52.6242, "type": "Coast", "sector": "أبوظبي والظفرة"},
    {"name": "مدينة زايد", "en": "Madinat Zayed", "lat": 23.6836, "lon": 53.6995, "type": "Desert", "sector": "أبوظبي والظفرة"},
    {"name": "العين", "en": "Al Ain", "lat": 24.2617, "lon": 55.6092, "type": "Inland", "sector": "العين"},
    {"name": "دبي", "en": "Dubai", "lat": 25.2528, "lon": 55.3644, "type": "Inland", "sector": "دبي والشمال"},
    {"name": "الشارقة", "en": "Sharjah", "lat": 25.3286, "lon": 55.5172, "type": "Inland", "sector": "دبي والشمال"},
    {"name": "عجمان", "en": "Ajman", "lat": 25.4236, "lon": 55.4447, "type": "Coast", "sector": "دبي والشمال"},
    {"name": "أم القيوين", "en": "Umm Al Quwain", "lat": 25.5301, "lon": 55.6548, "type": "Coast", "sector": "دبي والشمال"},
    {"name": "رأس الخيمة", "en": "Ras Al Khaimah", "lat": 25.7716, "lon": 55.9392, "type": "Coast", "sector": "دبي والشمال"},
    {"name": "جبل جيس", "en": "Jabal Jais", "lat": 25.9508, "lon": 56.1674, "type": "Mountains", "sector": "المنطقة الشرقية"},
    {"name": "حتا", "en": "Hatta", "lat": 24.8121, "lon": 56.1396, "type": "Mountains", "sector": "المنطقة الشرقية"},
    {"name": "الفجيرة", "en": "Fujairah", "lat": 25.1122, "lon": 56.3240, "type": "Inland", "sector": "المنطقة الشرقية"},
    {"name": "خورفكان", "en": "Khor Fakkan", "lat": 25.3578, "lon": 56.3618, "type": "Coast", "sector": "المنطقة الشرقية"},
    {"name": "كلباء", "en": "Kalba", "lat": 25.0430, "lon": 56.3640, "type": "Coast", "sector": "المنطقة الشرقية"},
    {"name": "الذيد", "en": "Al Dhaid", "lat": 25.2371, "lon": 55.8179, "type": "Inland", "sector": "المنطقة الوسطى"},
]

THRESHOLDS = {"storm": 65, "drizzle": 60, "fog": 50}


def uae_now() -> datetime:
    return datetime.utcnow() + timedelta(hours=4)


def load_emails() -> list[str]:
    if not EMAIL_LIST.exists():
        return []
    found = []
    for line in EMAIL_LIST.read_text(encoding="utf-8").splitlines():
        found.extend(re.findall(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9-.]+", line))
    # preserve order, drop duplicates
    seen = set()
    unique = []
    for email in found:
        key = email.lower()
        if key not in seen:
            seen.add(key)
            unique.append(email)
    return unique


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def num(value, default=0.0) -> float:
    try:
        if value is None:
            return default
        v = float(value)
        if v != v:  # NaN
            return default
        return v
    except (TypeError, ValueError):
        return default


def fetch_forecast() -> list[dict]:
    params = {
        "latitude": ",".join(str(s["lat"]) for s in STATIONS),
        "longitude": ",".join(str(s["lon"]) for s in STATIONS),
        "hourly": (
            "temperature_2m,relative_humidity_2m,cape,winddirection_10m,"
            "windspeed_10m,relative_humidity_850hPa,relative_humidity_700hPa,"
            "relative_humidity_500hPa,temperature_850hPa,temperature_500hPa,cloudcover_low"
        ),
        "forecast_days": 2,
        "timezone": "Asia/Dubai",
    }
    response = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict):
        if data.get("error"):
            raise RuntimeError(data.get("reason", "Open-Meteo error"))
        data = [data]
    return data


def score_station(station: dict, payload: dict, now: datetime) -> dict:
    hourly = payload.get("hourly") or {}
    times = hourly.get("time") or []
    best = {"storm": 0.0, "fog": 0.0, "drizzle": 0.0, "when": ""}
    horizon = now + timedelta(hours=18)

    for i, stamp in enumerate(times):
        try:
            dt = datetime.fromisoformat(stamp)
        except ValueError:
            continue
        if dt < now or dt > horizon:
            continue
        temp = num((hourly.get("temperature_2m") or [None])[i], 35)
        rh = num((hourly.get("relative_humidity_2m") or [None])[i], 50)
        cloud = num((hourly.get("cloudcover_low") or [None])[i], 0)
        wind_dir = num((hourly.get("winddirection_10m") or [None])[i], 0)
        wind = num((hourly.get("windspeed_10m") or [None])[i], 0)
        cape = num((hourly.get("cape") or [None])[i], 0)
        rh850 = num((hourly.get("relative_humidity_850hPa") or [None])[i], 50)
        rh700 = num((hourly.get("relative_humidity_700hPa") or [None])[i], 50)
        rh500 = num((hourly.get("relative_humidity_500hPa") or [None])[i], 50)
        t850 = num((hourly.get("temperature_850hPa") or [None])[i], 20)
        t500 = num((hourly.get("temperature_500hPa") or [None])[i], -10)

        prob = (cape / 2000.0) * 100.0
        moisture = rh850 * 0.4 + rh700 * 0.4 + rh500 * 0.2
        lapse = t850 - t500
        if lapse > 26:
            prob *= 1.3
        elif lapse < 20:
            prob *= 0.5
        if moisture < 40:
            prob *= 0.1
        elif moisture > 70:
            prob *= 1.2
        if station["type"] == "Mountains" and temp > 38:
            prob *= 1.3
        if dt.hour < 12 or dt.hour > 19:
            prob *= 0.1
        storm = max(0.0, min(100.0, prob))

        fog = 0.0
        if (dt.hour < 8 or dt.hour > 22) and rh > 80 and wind < 15:
            fog = max(0.0, min(100.0, (rh - 80) * 4 + (15 - wind) * 3))

        drizzle = 0.0
        if (
            station["lon"] >= 55.8
            and 3 <= dt.hour <= 9
            and 45 <= wind_dir <= 160
            and rh >= 85
            and cloud >= 75
        ):
            drizzle = max(0.0, min(100.0, (rh - 85) * 4 + (cloud - 75) * 2 + wind * 0.8))

        if storm > best["storm"]:
            best["storm"] = storm
            best["when"] = stamp
        best["fog"] = max(best["fog"], fog)
        best["drizzle"] = max(best["drizzle"], drizzle)
    best["station"] = station
    return best


def html_alert(title: str, body: str, regions: str, color: str) -> str:
    now = uae_now().strftime("%d/%m/%Y %H:%M")
    return f"""
    <div dir="rtl" style="font-family:Arial,sans-serif;max-width:600px;margin:auto;border:1px solid #E2E8F0;border-radius:8px;overflow:hidden">
      <div style="background:{color};padding:14px;text-align:center">
        <h2 style="margin:0;color:#111">{title}</h2>
      </div>
      <div style="padding:18px;color:#1E293B">
        <p style="font-size:16px;line-height:1.7">{body}</p>
        <p><b>المناطق:</b> {regions or "غير محددة"}</p>
        <p style="color:#64748B;font-size:13px">وقت الرصد (الإمارات): {now} — 71wm AI Weather Model</p>
      </div>
    </div>
    """


def send_email(subject: str, html: str, recipients: list[str]) -> None:
    sender = os.environ.get("SENDER_EMAIL", "").strip()
    password = os.environ.get("APP_PASSWORD", "").strip()
    if not sender or not password:
        raise RuntimeError("SENDER_EMAIL or APP_PASSWORD is missing")
    msg = MIMEText(html, "html", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
        server.login(sender, password)
        server.send_message(msg)


def main() -> int:
    recipients = load_emails()
    if not recipients:
        print("No recipients in email_list.txt")
        return 0

    now = uae_now()
    day_key = now.strftime("%Y-%m-%d")
    state = load_state()
    sent_today = set(state.get(day_key, []))

    try:
        payloads = fetch_forecast()
    except Exception as exc:
        print(f"Forecast fetch failed: {exc}")
        return 1

    scored = []
    for station, payload in zip(STATIONS, payloads):
        scored.append(score_station(station, payload, now))

    alerts = {
        "storm": ("71wm: Storm warning", "⛈️ أمطار رعدية محتملة", "فرصة سحب ركامية وأمطار ورياح نشطة خلال 18 ساعة القادمة.", "#FDE047", THRESHOLDS["storm"]),
        "drizzle": ("71wm: Al-Kous drizzle", "🌧️ رذاذ وسحب الكوس", "فرصة سحب منخفضة ورذاذ على السواحل والجبال الشرقية.", "#BAE6FD", THRESHOLDS["drizzle"]),
        "fog": ("71wm: Fog warning", "🌫️ ضباب وتدني رؤية", "فرصة ضباب أو تدني مدى الرؤية خلال الساعات القادمة.", "#E2E8F0", THRESHOLDS["fog"]),
    }

    sent_any = False
    for kind, (subject, title, body, color, threshold) in alerts.items():
        if kind in sent_today:
            print(f"Skip {kind}: already sent today")
            continue
        hits = [row for row in scored if row[kind] >= threshold]
        if not hits:
            print(f"No {kind} alert (max {max(row[kind] for row in scored):.0f}%)")
            continue
        regions = "، ".join(sorted({row["station"]["sector"] for row in hits}))
        names = "، ".join(row["station"]["name"] for row in hits[:8])
        html = html_alert(title, f"{body}<br><b>المحطات:</b> {names}", regions, color)
        try:
            send_email(subject, html, recipients)
        except Exception as exc:
            print(f"Send failed for {kind}: {exc}")
            return 1
        sent_today.add(kind)
        sent_any = True
        print(f"Sent {kind} to {len(recipients)} recipients")

    state[day_key] = sorted(sent_today)
    # keep only the last 14 days
    state = {k: v for k, v in state.items() if k >= (now - timedelta(days=14)).strftime("%Y-%m-%d")}
    save_state(state)
    if not sent_any:
        print("No new alerts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
