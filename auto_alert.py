import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# إحداثيات المحطات التي نراقبها
stations = {
    "Jabal Jais": {"lat": 25.9508, "lon": 56.1674, "type": "Mountains"},
    "Hatta": {"lat": 24.8121, "lon": 56.1396, "type": "Mountains"},
    # أضف باقي المحطات هنا بنفس التنسيق
}

def get_live_weather():
    # هذا هو رابط الـ API الذي تستخدمه في التطبيق
    url = "https://api.open-meteo.com/v1/forecast?latitude=25.9508,24.8121&longitude=56.1674,56.1396&hourly=temperature_2m,cape&timezone=auto"
    return requests.get(url).json()

def check_and_dispatch():
    data = get_live_weather()
    # منطق الفحص (نفس المنطق الموجود في app.py)
    # نقوم بحساب Cape ودرجة الحرارة لكل محطة
    
    critical_alerts = []
    # (هنا نضع المعادلة الرياضية الخاصة بك لحساب العاصفة)
    
    if critical_alerts:
        msg = f"تحذير JM72: عواصف رعدية متوقعة في: {', '.join(critical_alerts)}"
        send_email(msg)

def send_email(body):
    password = os.environ.get('APP_PASSWORD')
    msg = MIMEText(body)
    msg['Subject'] = "🚨 JM72 Weather Alert"
    msg['From'] = "sender@gmail.com"
    msg['To'] = "receiver@gmail.com"
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login("sender@gmail.com", password)
        server.sendmail("sender@gmail.com", ["receiver@gmail.com"], msg.as_string())

if __name__ == "__main__":
    check_and_dispatch()
