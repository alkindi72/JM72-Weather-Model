import os
import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText

def apply_terrain_correction(temp, altitude):
    return temp - (altitude / 100) * 0.65

def get_email_list(filename="email_list.txt"):
    try:
        with open(filename, "r") as file:
            emails = [line.strip() for line in file if line.strip()]
        return emails
    except FileNotFoundError:
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
                probability = min(100, int((cape / 1500) * 100))
                
                en_alert = f"🚨 RED ALERT: Severe Convective Storm Risk ({probability}%) detected over {name}!"
                ar_alert = f"🚨 إنذار أحمر: خطر عواصف ركامية شديدة بنسبة ({probability}%) مرصودة فوق منطقة {name}!"
                weather_info = f"📍 المنطقة المعرضة للحدث: {name} | درجة الحرارة: {corrected_temp:.1f}°C"
                
                full_alert = f"{en_alert}\n{ar_alert}\n{weather_info}\n{'-'*50}"
                alerts.append(full_alert)
                
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الفحص: {e}")
        return

    if alerts:
        recipients = get_email_list("email_list.txt")
        if recipients:
            final_message = "تحذير من نظام JM72 للأرصاد الجوية:\n\n" + "\n\n".join(alerts)
            send_email("🚨 JM72 RED ALERT - إنذار جوي عالي الأهمية", final_message, recipients)
            print(f"✅ تم إرسال الإنذار الأحمر بنجاح!")
    else:
        print("✅ تم الفحص: لا توجد سحب ركامية خطرة حالياً.")

def send_email(subject, body, recipients):
    sender = "jm72.weather@gmail.com" # ضع إيميلك المرسل هنا
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
