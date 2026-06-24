import os
import re
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def get_email_list(filename="email_list.txt"):
    valid_emails = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                # فلتر ذكي يستخرج الإيميل الإنجليزي فقط ويتجاهل أي مسافات أو حروف عربية
                found = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', line)
                valid_emails.extend(found)
        return valid_emails
    except FileNotFoundError:
        return []

def send_alert():
    try:
        df = pd.read_csv("Meta_data34.csv") 
        df.columns = df.columns.str.strip() 
        
        col_name = 'Station_Name' if 'Station_Name' in df.columns else 'Station'
        col_lat = 'Lat.' if 'Lat.' in df.columns else 'Lat'
        col_lon = 'Long.' if 'Long.' in df.columns else 'Long'
        
        locations_list = []
        for _, row in df.iterrows():
            name = row.get(col_name, 'غير محدد')
            lat = row.get(col_lat, 'غير محدد')
            lon = row.get(col_lon, 'غير محدد')
            locations_list.append(f"📍 {name}  (خط الطول: {lon} | خط العرض: {lat})")
        
        locations_text = "\n".join(locations_list)
        
    except Exception as e:
        print(f"❌ حدث خطأ في قراءة ملف البيانات: {e}")
        locations_text = "📍 الأماكن المحددة في النظام"

    probability = 100
    
    en_alert = f"🚨 RED ALERT: Severe Convective Storm Risk ({probability}%) detected over the following areas:"
    ar_alert = f"🚨 إنذار أحمر: خطر عواصف ركامية شديدة بنسبة ({probability}%) مرصودة فوق المناطق التالية:"
    
    full_alert = f"{en_alert}\n\n{ar_alert}\n\n{locations_text}\n\n{'-'*50}"

    recipients = get_email_list("email_list.txt")
    if not recipients:
        print("❌ لم يتم الإرسال: تأكد من وجود إيميلات صحيحة داخل ملف email_list.txt")
        return

    # الاعتماد الكلي على الخزنة السرية (لن تكتب إيميلك هنا أبداً بعد الآن)
    sender = os.environ.get('SENDER_EMAIL')
    password = os.environ.get('APP_PASSWORD')
    
    if not sender or not password:
        print("❌ خطأ: يرجى التأكد من إضافة SENDER_EMAIL و APP_PASSWORD في GitHub Secrets.")
        return
        
    # تنظيف الإيميل المخفي من أي مسافات زائدة لضمان عدم حدوث خطأ
    sender = sender.strip()
    
    # إعداد الرسالة بترميز utf-8 لدعم اللغة العربية
    msg = MIMEText(full_alert, 'plain', 'utf-8')
    msg['Subject'] = Header("🚨 JM72 RED ALERT - إنذار جوي عالي الأهمية", 'utf-8')
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print(f"✅ تم إرسال الإنذار بنجاح لـ {len(recipients)} مستلم!")
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")

if __name__ == "__main__":
    send_alert()
