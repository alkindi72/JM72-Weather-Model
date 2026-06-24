import os
import requests
import smtplib
from email.mime.text import MIMEText

# قائمة المحطات (يمكنك إضافة أي إحداثيات أخرى)
stations = {
    "Jabal Jais": {"lat": 25.95, "lon": 56.16},
    "Hatta": {"lat": 24.81, "lon": 56.13},
    "Al Dhaid": {"lat": 25.23, "lon": 55.81},
    "Al Ain": {"lat": 24.26, "lon": 55.60}
}

def check_for_storms():
    # 1. سحب البيانات من Open-Meteo
    # نطلب cape و temperature_2m
    latitudes = ",".join([str(s['lat']) for s in stations.values()])
    longitudes = ",".join([str(s['lon']) for s in stations.values()])
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitudes}&longitude={longitudes}&hourly=temperature_2m,cape&timezone=auto"
    
    response = requests.get(url).json()
    alerts = []

    # 2. فحص كل محطة
    for i, (name, coords) in enumerate(stations.items()):
        cape = response[i]['hourly']['cape'][0] # القيمة الحالية
        
        # شرط التكون الرعدي: CAPE > 1000 مؤشر جيد، > 2000 قوي جداً
        if cape > 1000:
            intensity = "عالية جداً" if cape > 2000 else "متوسطة"
            alerts.append(f"📍 المحطة: {name}\n   الشدة: {intensity} (CAPE: {cape} J/kg)\n   الإحداثيات: {coords['lat']}, {coords['lon']}\n")

    # 3. إرسال الإيميل إذا وجدنا أي خطر
    if alerts:
        message = "🚨 تحذير JM72: رصد ظروف جوية غير مستقرة\n\n" + "\n".join(alerts)
        send_email("🚨 تحذير عواصف رعدية", message)

def send_email(subject, body):
    sender = "jm72.weather@gmail.com" # ضع إيميلك
    recipients = ["target@example.com"] # الإيميلات المستهدفة
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
