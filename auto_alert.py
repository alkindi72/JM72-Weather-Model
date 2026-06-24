import os
import requests
import smtplib
from email.mime.text import MIMEText

# إضافة الارتفاع (Elevation) لكل محطة بالأمتار
stations = {
    "Jabal Jais": {"lat": 25.95, "lon": 56.16, "alt": 1800},
    "Hatta": {"lat": 24.81, "lon": 56.13, "alt": 400},
    "Al Dhaid": {"lat": 25.23, "lon": 55.81, "alt": 50},
    "Al Ain": {"lat": 24.26, "lon": 55.60, "alt": 300}
}

def apply_terrain_correction(temp, altitude):
    # معدل التناقص الأديباتي (Lapse Rate): تنخفض الحرارة تقريباً 0.65 درجة لكل 100 متر
    correction = (altitude / 100) * 0.65
    return temp - correction

def check_for_storms():
    latitudes = ",".join([str(s['lat']) for s in stations.values()])
    longitudes = ",".join([str(s['lon']) for s in stations.values()])
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitudes}&longitude={longitudes}&hourly=temperature_2m,cape&timezone=auto"
    
    response = requests.get(url).json()
    alerts = []

    for i, (name, data) in enumerate(stations.items()):
        raw_temp = response[i]['hourly']['temperature_2m'][0]
        cape = response[i]['hourly']['cape'][0]
        
        # تطبيق التصحيح التضاريسي
        corrected_temp = apply_terrain_correction(raw_temp, data['alt'])
        
        # منطق التحذير: دمج CAPE مع انخفاض الحرارة التضاريسي
        if cape > 1000:
            intensity = "عالية جداً" if cape > 2000 else "متوسطة"
            alerts.append(f"📍 المحطة: {name}\n   الشدة: {intensity} (CAPE: {cape})\n   الحرارة المصححة: {corrected_temp:.1f}°C\n")

    if alerts:
        message = "🚨 تحذير JM72: ظروف جوية غير مستقرة مرصودة:\n\n" + "\n".join(alerts)
        send_email("🚨 تحذير عواصف رعدية", message)

def send_email(subject, body):
    sender = "jm72.weather@gmail.com" 
    recipients = ["target@example.com"] 
    password = os.environ.get('APP_PASSWORD')
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())

if __name__ == "__main__":
    check_for_storms()
