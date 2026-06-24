import os
import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText

def apply_terrain_correction(temp, altitude):
    return temp - (altitude / 100) * 0.65

def get_email_list(filename="email_list.txt"):
    # دالة ذكية لقراءة الإيميلات من الملف النصي
    try:
        with open(filename, "r") as file:
            # تقرأ الأسطر، تزيل المسافات الفارغة، وتتجاهل الأسطر الخالية
            emails = [line.strip() for line in file if line.strip()]
        return emails
    except FileNotFoundError:
        print(f"⚠️ تحذير: ملف {filename} غير موجود.")
        return []

def check_for_storms():
    df = pd.read_csv("Meta_data34.csv") 
    df.columns = df.columns.str.strip() 
    
    alerts = []
    
    try:
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
            
            if cape > 300:
                alerts.append(f"📍 {name}: طاقة العاصفة={cape} J/kg، الحرارة المصححة={corrected_temp:.1f}°C")
                
    except KeyError as e:
        print(f"❌ حدث خطأ: الروبوت لم يجد العمود المسمى {e}")
        return
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return

    if alerts:
        # هنا يقوم الروبوت بسحب قائمة الإيميلات من الملف
        recipients = get_email_list("email_list.txt")
        
        if recipients:
            send_email("🚨 تحذير JM72: رصد ظروف غير مستقرة", "\n".join(alerts), recipients)
            print(f"✅ تم إرسال الإيميل بنجاح إلى {len(recipients)} مستلم/مستلمين!")
        else:
            print("❌ لم يتم الإرسال: ملف email_list.txt فارغ أو غير موجود.")
    else:
        print("✅ تم الفحص: الوضع الجوي مستقر ولا توجد عواصف حالياً.")

def send_email(subject, body, recipients):
    sender = "jm72.weather@gmail.com" # ضع إيميلك المرسل هنا
    password = os.environ.get('APP_PASSWORD')
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    # دمج قائمة الإيميلات ليتم إرسالها دفعة واحدة
    msg['To'] = ", ".join(recipients)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
    except Exception as e:
        print(f"❌ خطأ في إرسال الإيميل: {e}")

if __name__ == "__main__":
    check_for_storms()
