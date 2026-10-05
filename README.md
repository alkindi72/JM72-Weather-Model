# 71wm AI Weather Model

منصة Streamlit لمتابعة الطقس في دولة الإمارات: عواصف، ضباب، سحب الكوس، الرذاذ، ومؤشر النينيو/النينيا.

## التشغيل المحلي

```powershell
cd JM72-Weather-Model-main
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

على macOS / Linux استبدل سطر التفعيل بـ `source .venv/bin/activate`.

## ماذا تعرض المنصة

| التبويب | المحتوى |
|---|---|
| Storms & Fog | احتمال العواصف والضباب لخمسة أيام وخرائط |
| Heat & Anomalies | المدى الحراري حسب الساحل والجبل والداخل |
| Al-Kous & Drizzle | سحب الكوس والرذاذ على الساحل الشرقي |
| Model Matrix | جدول المحطات للوقت المحدد |
| Niño / Niña | مؤشر ONI من NOAA وأثره المحتمل على الخليج |
| Control Room | تفعيل البريد وتغيير الرمز |

البيانات الساعية من [Open-Meteo](https://open-meteo.com/) (نموذج GFS). مؤشر النينيو من [NOAA CPC ONI](https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt).

المنطق الحالي قواعد مناخية (CAPE، الرطوبة، معدل التناقص، الرياح) وليس نموذجاً مدرَّباً. علاقة النينيو بأمطار الإمارات إحصائية وليست حتمية.

## التنبيهات

`auto_alert.py` يفحص 15 محطة للإمارات، ويرسل بريداً فقط إذا تجاوزت إحدى العتبات خلال 18 ساعة:

- عاصفة ≥ 65٪
- رذاذ الكوس ≥ 60٪
- ضباب ≥ 50٪

كل نوع يُرسل مرة واحدة في اليوم (توقيت الإمارات) عبر ملف `alert_state.json`.

### GitHub Actions

1. في المستودع: Settings → Secrets → Actions
2. أضف:
   - `SENDER_EMAIL` بريد Gmail المُرسِل
   - `APP_PASSWORD` كلمة مرور التطبيقات من Google (16 حرفاً، ليست كلمة الحساب)
3. ضع المستلمين في `email_list.txt`، بريد واحد في كل سطر.
4. انسخ `auto_alert.yml` إلى `.github/workflows/auto_alert.yml`.
5. يمكن تشغيله يدوياً من تبويب Actions، أو ينتظر الجدولة كل 3 ساعات.

التشغيل اليدوي المحلي:

```powershell
$env:SENDER_EMAIL="you@gmail.com"
$env:APP_PASSWORD="xxxx xxxx xxxx xxxx"
python auto_alert.py
```

## غرفة التحكم

الرمز الافتراضي داخل الجلسة هو `Jumah71`. غيّره من التبويب بعد الدخول. الرمز يبقى لجلسة المتصفح فقط ولا يُحفظ في الملف.

## الملفات

- `app.py` — التطبيق
- `auto_alert.py` — التنبيه المجدول
- `email_list.txt` — المستلمون
- `requirements.txt` — اعتماديات الواجهة
- `.github/workflows/auto_alert.yml` — الجدولة
