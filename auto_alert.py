import os
import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText

def apply_terrain_correction(temp, altitude):
    return temp - (altitude / 100) * 0.65

def check_for_storms():
    # قراءة الملف
    df = pd.read_csv("Meta_data34.csv") 
    df.columns = df.columns.str.strip() # تنظيف المسافات المخفية
    
    alerts = []
    
    try:
        # توجيه الروبوت للبحث عن الأسماء المختصرة التي ذكرتها
        col_lat = 'Lat.' if 'Lat.' in df.columns else 'Lat'
        col_lon = 'Long.' if 'Long.' in df.columns else 'Long'
        col_alt = 'Altitude' if 'Altitude' in df.columns else 'alt'
        col_name = 'Station_Name' if 'Station_Name' in df.columns else 'Station'
        
        for _, row in df.iterrows():
            lat, lon = row[col_lat], row[col_lon]
            alt = row[col_alt]
            name = row[col_name]
            
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,cape&timezone=auto"
            
            response = requests.get(url).json()
            cape = response['hourly']['cape'][0]
            raw_temp = response['hourly']['temperature_2m'][0]
            corrected_temp = apply_terrain_correction(raw_temp, alt)
            
            if cape > 1000:
                alerts.append(f"📍 {name}: طاقة العاصفة={cape} J/kg، الحرارة المصححة={corrected_temp:.1f}°C")
                
    except KeyError as e:
        print(f"❌ حدث خطأ: الروبوت لم يجد العمود المسمى {e}")
        print("📋 الأعمدة الموجودة فعلياً في ملفك هي:", df.columns.tolist())
        return
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return

    if alerts:
        send_email("🚨 تحذير JM72: رصد ظروف غير مستقرة", "\n".join(alerts))
        print("✅ تم إرسال الإيميل بنجاح!")
    else:
        print("✅ تم الفحص: الوضع الجوي مستقر ولا توجد عواصف حالياً.")

def send_email(subject, body):
    sender = "jm72.weather@gmail.com"
    recipients = ["target@example.com"] # ضع إيميل الاستلام الحقيقي هنا
    password = os.environ.get('APP_PASSWORD')
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
    except Exception as e:
        print(f"❌ خطأ في إرسال الإيميل: {e}")

if __name__ == "__main__":
    check_for_storms()
