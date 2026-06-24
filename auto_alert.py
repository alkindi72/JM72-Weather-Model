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
                found = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', line)
                valid_emails.extend(found)
        return valid_emails
    except FileNotFoundError:
        return []

def send_alert():
    try:
        df = pd.read_csv("Meta_data34.csv") 
        df.columns = df.columns.str.strip() 
        
        locations_list = []
        for _, row in df.iterrows():
            # استخراج الأسماء بناءً على الأعمدة الدقيقة التي أرسلتها
            name_ar = str(row.get('Full_Name_ar', '')).strip()
            name_en = str(row.get('Full_Name_eng', '')).strip()
            
            # ترتيب عرض الاسم ليكون (عربي - إنجليزي) أو أحدهما إذا كان الآخر فارغاً
            if name_ar and name_en and name_ar != 'nan' and name_en != 'nan':
                display_name = f"{name_ar} ({name_en})"
            elif name_ar and name_ar != 'nan':
                display_name = name_ar
            elif name_en and name_en != 'nan':
                display_name = name_en
            else:
                continue # تجاهل السطر إذا كانت الأسماء فارغة تماماً
                
            locations_list.append(f"📍 {display_name}")
        
        locations_text = "\n".join(locations_list)
        
        # في حال كان الملف فارغاً أو لا توجد أسماء
        if not locations_text.strip():
            locations_text = "📍 لم يتم تحديد مناطق معينة في الملف"
            
    except Exception as e:
        print(f"❌ حدث خطأ في قراءة ملف البيانات: {e}")
        locations_text = "📍 حدث خطأ في قراءة أسماء المناطق"

    probability = 100
    
    en_alert = f"🚨 RED ALERT: Severe Convective Storm Risk ({probability}%) detected over the following areas:"
    ar_alert = f"🚨 إنذار أحمر: خطر عواصف ركامية شديدة بنسبة ({probability}%) مرصودة فوق المناطق التالية:"
    
    # دمج الرسالة
    full_alert = f"{en_alert}\n\n{ar_alert}\n\n{locations_text}\n\n{'-'*50}"

    recipients = get_email_list("email_list.txt")
    if not recipients:
        print("❌ لم يتم الإرسال: تأكد من وجود إيميلات صحيحة داخل ملف email_list.txt")
        return

    sender = os.environ.get('SENDER_EMAIL')
    password = os.environ.get('APP_PASSWORD')
    
    if not sender or not password:
        print("❌ خطأ: يرجى التأكد من إضافة SENDER_EMAIL و APP_PASSWORD في GitHub Secrets.")
        return
        
    sender = sender.strip()
    
    msg = MIMEText(full_alert, 'plain', 'utf-8')
    msg['Subject'] = Header("🚨 JM72 RED ALERT - إنذار جوي عالي الأهمية", 'utf-8')
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print(f"✅ تم إرسال الإنذار بنجاح مع أسماء المناطق لـ {len(recipients)} مستلم!")
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")

if __name__ == "__main__":
    send_alert()
