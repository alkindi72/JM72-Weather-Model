import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText

def get_email_list(filename="email_list.txt"):
    try:
        with open(filename, "r") as file:
            emails = [line.strip() for line in file if line.strip()]
        return emails
    except FileNotFoundError:
        return []

def send_alert():
    try:
        df = pd.read_csv("Meta_data34.csv") 
        df.columns = df.columns.str.strip() 
        
        col_name = 'Station_Name' if 'Station_Name' in df.columns else 'Station'
        col_lat = 'Lat.' if 'Lat.' in df.columns else 'Lat'
        col_lon = 'Long.' if 'Long.' in df.columns else 'Long'
        
        # تجميع قائمة بجميع المناطق الموجودة في الملف مع إحداثياتها
        locations_list = []
        for _, row in df.iterrows():
            name = row.get(col_name, 'غير محدد')
            lat = row.get(col_lat, 'غير محدد')
            lon = row.get(col_lon, 'غير محدد')
            locations_list.append(f"📍 {name}  (خط الطول: {lon} | خط العرض: {lat})")
        
        # تحويل القائمة إلى نص متسلسل
        locations_text = "\n".join(locations_list)
        
    except Exception as e:
        print(f"❌ حدث خطأ في قراءة ملف البيانات: {e}")
        locations_text = "📍 الأماكن المحددة في النظام"

    # نسبة التوقع
    probability = 100
    
    # صياغة التحذير باللغتين ليدعم منطقة أو عدة مناطق
    en_alert = f"🚨 RED ALERT: Severe Convective Storm Risk ({probability}%) detected over the following areas:"
    ar_alert = f"🚨 إنذار أحمر: خطر عواصف ركامية شديدة بنسبة ({probability}%) مرصودة فوق المناطق التالية:"
    
    # دمج الرسالة بالكامل
    full_alert = f"{en_alert}\n\n{ar_alert}\n\n{locations_text}\n\n{'-'*50}"

    # جلب الإيميلات
    recipients = get_email_list("email_list.txt")
    if not recipients:
        print("❌ لم يتم الإرسال: تأكد من وجود إيميلات داخل ملف email_list.txt")
        return

    # ⚠️ استبدل هذا السطر بإيميلك الحقيقي
    sender = "اكتب_إيميلك_الحقيقي_هنا@gmail.com" 
    password = os.environ.get('APP_PASSWORD')
    
    msg = MIMEText(full_alert)
    msg['Subject'] = "🚨 JM72 RED ALERT - إنذار جوي عالي الأهمية"
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    
    # الإرسال
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
        print(f"✅ تم إرسال الإنذار بنجاح لـ {len(recipients)} مستلم، متضمناً قائمة الأماكن!")
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")

if __name__ == "__main__":
    send_alert()
