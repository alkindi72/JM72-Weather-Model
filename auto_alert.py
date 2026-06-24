import os
import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText

def apply_terrain_correction(temp, altitude):
    # التصحيح التضاريسي: -0.65 درجة لكل 100 متر
    return temp - (altitude / 100) * 0.65

def check_for_storms():
    # 1. قراءة بيانات المحطات من ملفك الخاص
    # تأكد أن الملف مرفوع في المجلد الرئيسي على GitHub
    df = pd.read_excel("Meta_data34.xlsx") 
    
    # افتراض لأسماء الأعمدة (يرجى تعديلها إذا كانت مختلفة في ملفك)
    # نستخدم: 'Station_Name', 'Latitude', 'Longitude', 'Altitude'
    
    alerts = []
    
    for _, row in df.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        alt = row['Altitude']
        name = row['Station_Name']
        
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,cape&timezone=auto"
        
        try:
            response = requests.get(url).json()
            cape = response['hourly']['cape'][0]
            raw_temp = response['hourly']['temperature_2m'][0]
            corrected_temp = apply_terrain_correction(raw_temp, alt)
            
            # معايير التحذير: CAPE > 1000
            if cape > 1000:
                alerts.append(f"📍 {name}: طاقة العاصفة={cape} J/kg، الحرارة المصححة={corrected_temp:.1f}°C")
        except Exception as e:
            continue

    if alerts:
        send_email("🚨 تحذير JM72: رصد ظروف غير مستقرة", "\n".join(alerts))

def send_email(subject, body):
    sender = "jm72.weather@gmail.com"
    recipients = ["target@example.com"] # ضع إيميلاتك هنا
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
