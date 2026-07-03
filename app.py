import streamlit as st
import pandas as pd
import numpy as np
import joblib
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
import math
from datetime import datetime

# ====================================
# إعداد الصفحة
# ====================================
st.set_page_config(
    page_title="JM72 | UAE Mountain Storm Warning",
    page_icon="⛈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; }

    .hero-banner {
        background: linear-gradient(135deg, #0d1b2a, #1b2838, #0d1b2a);
        border: 1px solid #e74c3c;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        margin-bottom: 20px;
    }

    .kpi-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border-left: 4px solid #e74c3c;
        margin-bottom: 10px;
    }

    .risk-extreme {
        background: linear-gradient(135deg, #2d0a0a, #4a0e0e);
        border: 2px solid #e74c3c;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        animation: pulse 1.5s infinite;
    }
    .risk-high {
        background: linear-gradient(135deg, #2d1a0a, #4a2e0e);
        border: 2px solid #e67e22;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
    }
    .risk-moderate {
        background: linear-gradient(135deg, #2d2a0a, #4a440e);
        border: 2px solid #f1c40f;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
    }
    .risk-low {
        background: linear-gradient(135deg, #0a1a2d, #0e2a4a);
        border: 2px solid #3498db;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
    }
    .risk-minimal {
        background: linear-gradient(135deg, #0a2d1a, #0e4a2e);
        border: 2px solid #2ecc71;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
    }

    .section-header {
        background: linear-gradient(90deg, #e74c3c, #c0392b);
        border-radius: 8px;
        padding: 10px 20px;
        color: white;
        font-weight: bold;
        margin-bottom: 15px;
    }

    .station-card {
        background: #1a1a2e;
        border: 1px solid #e74c3c;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(231,76,60,0.7); }
        70% { box-shadow: 0 0 0 10px rgba(231,76,60,0); }
        100% { box-shadow: 0 0 0 0 rgba(231,76,60,0); }
    }

    div[data-testid="stMetricValue"] {
        color: #e74c3c !important;
        font-size: 1.8rem !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #bdc3c7 !important;
    }

    .stDataFrame { background-color: #1a1a2e; }
    .stSelectbox label { color: white !important; }
    .stSlider label { color: white !important; }
    .stNumberInput label { color: white !important; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b2a, #1a1a2e);
        border-right: 1px solid #e74c3c;
    }
</style>
""", unsafe_allow_html=True)

# ====================================
# تحميل البيانات والنموذج
# ====================================
@st.cache_resource
def load_model():
    return joblib.load("models/thunderstorm_xgb.pkl")

@st.cache_data
def load_data():
    df   = pd.read_csv("data/features_engineered_v2.csv")
    meta = pd.read_csv("data/Meta_data34.csv")
    meta.columns = meta.columns.str.strip()
    return df, meta

try:
    model = load_model()
    df_climate, df_meta = load_data()
    model_loaded = True
except Exception as e:
    model_loaded = False
    st.sidebar.error(f"⚠️ خطأ: {e}")

# ====================================
# Sidebar
# ====================================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:15px;'>
        <div style='font-size:50px'>⛈️</div>
        <h2 style='color:#e74c3c; margin:5px 0'>JM72</h2>
        <p style='color:#bdc3c7; font-size:12px'>نظام الإنذار المبكر للعواصف الجبلية</p>
        <hr style='border-color:#e74c3c'>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "📋 التنقل:",
        ["🏠 الرئيسية",
         "🔮 التنبؤ الفوري",
         "📊 التحليل الشهري",
         "🌊 تحليل ENSO",
         "🗺️ خريطة المحطات",
         "📈 إحصائيات المشروع"]
    )

    st.markdown("""
    <hr style='border-color:#333'>
    <div style='color:#bdc3c7; font-size:13px'>
        <b style='color:#e74c3c'>🏔️ المحطات الجبلية (Zone 8):</b><br><br>
        ⛰️ جبل جيس - 1,934م<br>
        ⛰️ جبل مبرح<br>
        ⛰️ جبل ينس<br>
        ⛰️ جبل الرحبة<br>
        ⛰️ جبل الحبن<br>
        ⛰️ جبل حفيت - 1,249م<br>
    </div>
    <hr style='border-color:#333'>
    <div style='color:#666; font-size:11px; text-align:center'>
        📡 البيانات: 2003-2025<br>
        🤖 XGBoost | دقة 83.8%
    </div>
    """, unsafe_allow_html=True)

# ====================================
# 🏠 الرئيسية
# ====================================
if page == "🏠 الرئيسية":

    st.markdown("""
    <div class='hero-banner'>
        <h1 style='color:#e74c3c; font-size:2.5rem; margin:0'>⛈️ JM72</h1>
        <h3 style='color:white; margin:10px 0'>نظام الإنذار المبكر للعواصف الجبلية</h3>
        <p style='color:#bdc3c7'>تحليل وتنبؤ العواصف الرعدية في جبال الحجر - الإمارات العربية المتحدة</p>
        <p style='color:#e74c3c; font-size:13px'>📡 يغطي 146 محطة رصد جوي | الفترة 2003-2025</p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("📡 المحطات", "146", "إجمالي")
    with c2: st.metric("🏔️ جبلية", "6", "Zone 8")
    with c3: st.metric("🤖 الدقة", "83.8%", "XGBoost")
    with c4: st.metric("⛈️ عواصف", "51 يوم", "≥30mm")
    with c5: st.metric("🌧️ أعلى هطول", "287.6mm", "مارس 2016")

    st.markdown("---")

    if model_loaded:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 توزيع مستوى الخطر")
            risk_counts = df_climate["mtn_thunderstorm_risk"].value_counts()
            risk_order  = ["EXTREME","HIGH","MODERATE","LOW","MINIMAL"]
            colors      = ["#e74c3c","#e67e22","#f1c40f","#3498db","#2ecc71"]

            fig = go.Figure(go.Pie(
                labels=[r for r in risk_order if r in risk_counts.index],
                values=[risk_counts.get(r,0) for r in risk_order if r in risk_counts.index],
                marker_colors=colors,
                hole=0.45,
                textinfo="label+percent",
                textfont_size=12
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=380,
                legend=dict(font=dict(color="white"))
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 🌧️ الأمطار الشهرية في جبال الحجر")
            monthly = df_climate.groupby("month_num")["highest_rainfall"].mean()
            months  = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
                       "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]
            vals    = [monthly.get(m, 0) for m in range(1, 13)]

            fig = go.Figure(go.Bar(
                x=months, y=vals,
                marker_color=["#e74c3c" if v > 40 else "#3498db" for v in vals],
                text=[f"{v:.1f}" for v in vals],
                textposition="outside",
                textfont=dict(color="white", size=10)
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white", height=380,
                yaxis=dict(title="متوسط الأمطار (mm)", gridcolor="#333"),
                xaxis=dict(gridcolor="#333")
            )
            st.plotly_chart(fig, use_container_width=True)

        # الصف الثاني
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("### 🌡️ نطاق الحرارة الشهري")
            monthly_h = df_climate.groupby("month_num")["highest_temp"].mean()
            monthly_l = df_climate.groupby("month_num")["lowest_temp"].mean()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=months,
                y=[monthly_h.get(m,0) for m in range(1,13)],
                name="أعلى حرارة",
                line=dict(color="#e74c3c", width=3),
                fill="tonexty", fillcolor="rgba(231,76,60,0.1)"
            ))
            fig.add_trace(go.Scatter(
                x=months,
                y=[monthly_l.get(m,0) for m in range(1,13)],
                name="أدنى حرارة",
                line=dict(color="#3498db", width=3)
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white", height=320,
                legend=dict(font=dict(color="white")),
                yaxis=dict(gridcolor="#333"),
                xaxis=dict(gridcolor="#333")
            )
            st.plotly_chart(fig, use_container_width=True)

        with col4:
            st.markdown("### 💨 سرعة الرياح الشهرية")
            monthly_w = df_climate.groupby("month_num")["max_wind"].mean()
            wvals     = [monthly_w.get(m,0) for m in range(1,13)]

            fig = go.Figure(go.Bar(
                x=months, y=wvals,
                marker_color=["#e74c3c" if w>80 else "#95a5a6" for w in wvals],
                text=[f"{w:.0f}" for w in wvals],
                textposition="outside",
                textfont=dict(color="white", size=10)
            ))
            fig.add_hline(y=80, line_dash="dash",
                          line_color="yellow",
                          annotation_text="⚠️ حد الخطر 80",
                          annotation_font_color="yellow")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white", height=320,
                yaxis=dict(title="km/h", gridcolor="#333"),
                xaxis=dict(gridcolor="#333")
            )
            st.plotly_chart(fig, use_container_width=True)

# ====================================
# 🔮 التنبؤ الفوري
# ====================================
elif page == "🔮 التنبؤ الفوري":

    st.markdown("""
    <div class='hero-banner'>
        <h2 style='color:#e74c3c'>🔮 التنبؤ الفوري بمستوى الخطر</h2>
        <p style='color:#bdc3c7'>أدخل البيانات الجوية للحصول على تقييم فوري لمستوى خطر العاصفة</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 📥 بيانات الإدخال")

        months_ar = {
            "يناير":1,"فبراير":2,"مارس":3,"أبريل":4,
            "مايو":5,"يونيو":6,"يوليو":7,"أغسطس":8,
            "سبتمبر":9,"أكتوبر":10,"نوفمبر":11,"ديسمبر":12
        }

        sel_month  = st.selectbox("📅 الشهر:", list(months_ar.keys()))
        month_num  = months_ar[sel_month]
        day        = st.slider("📆 اليوم:", 1, 31, 15)
        temp_high  = st.number_input("🌡️ أعلى حرارة (°C):",
                                      min_value=10.0, max_value=55.0,
                                      value=35.0, step=0.5)
        temp_low   = st.number_input("🌡️ أدنى حرارة (°C):",
                                      min_value=-5.0, max_value=40.0,
                                      value=15.0, step=0.5)
        rainfall   = st.number_input("🌧️ الأمطار (mm):",
                                      min_value=0.0, max_value=300.0,
                                      value=25.0, step=1.0)
        wind       = st.number_input("💨 سرعة الرياح (km/h):",
                                      min_value=0, max_value=200,
                                      value=60, step=5)
        enso       = st.selectbox("🌊 حالة ENSO:", [
                                      "Neutral","El_Nino","Strong_ElNino",
                                      "La_Nina","Strong_LaNina","Weak_ElNino"])

        predict_btn = st.button("🔮 احسب مستوى الخطر", use_container_width=True,
                                 type="primary")

    with col2:
        if predict_btn:
            temp_range  = temp_high - temp_low
            risk_score  = 0
            warnings_list = []

            # الموسم
            if month_num in [3,4]:      risk_score += 3
            elif month_num in [11,12,1,2]: risk_score += 2
            elif month_num in [7,8]:    risk_score += 2
            else:                        risk_score += 1

            # الحرارة
            if temp_range > 30:
                risk_score += 3
                warnings_list.append(("🌡️", f"فرق حرارة كبير جداً: {temp_range:.1f}°C", "#e74c3c"))
            elif temp_range > 25:
                risk_score += 2
                warnings_list.append(("🌡️", f"فرق حرارة ملحوظ: {temp_range:.1f}°C", "#e67e22"))

            # الأمطار
            if rainfall >= 100:
                risk_score += 5
                warnings_list.append(("🌊", f"أمطار استثنائية: {rainfall}mm ⚠️ خطر فيضانات!", "#e74c3c"))
            elif rainfall >= 50:
                risk_score += 4
                warnings_list.append(("🌧️", f"أمطار غزيرة جداً: {rainfall}mm", "#e67e22"))
            elif rainfall >= 30:
                risk_score += 3
                warnings_list.append(("🌧️", f"أمطار غزيرة: {rainfall}mm", "#f1c40f"))
            elif rainfall >= 15:
                risk_score += 2
                warnings_list.append(("🌦️", f"أمطار متوسطة: {rainfall}mm", "#3498db"))

            # الرياح
            if wind >= 120:
                risk_score += 5
                warnings_list.append(("🌪️", f"رياح عاصفة شديدة: {wind} km/h", "#e74c3c"))
            elif wind >= 100:
                risk_score += 4
                warnings_list.append(("💨", f"رياح عاصفة: {wind} km/h", "#e67e22"))
            elif wind >= 80:
                risk_score += 3
                warnings_list.append(("💨", f"رياح قوية: {wind} km/h", "#f1c40f"))
            elif wind >= 60:
                risk_score += 2
                warnings_list.append(("💨", f"رياح نشطة: {wind} km/h", "#3498db"))

            # ENSO
            enso_mult = {
                "Strong_ElNino":1.4,"El_Nino":1.3,"Weak_ElNino":1.1,
                "Neutral":1.0,"La_Nina":1.1,"Strong_LaNina":1.2
            }.get(enso, 1.0)
            final_score = risk_score * enso_mult

            # تحديد المستوى
            if final_score >= 15:
                level  = "🔴 EXTREME"
                color  = "#e74c3c"
                css    = "risk-extreme"
                action = "⛔ إغلاق فوري لجبال الحجر!"
                desc   = "خطر شديد جداً - لا تقترب من المناطق الجبلية"
            elif final_score >= 10:
                level  = "🟠 HIGH"
                color  = "#e67e22"
                css    = "risk-high"
                action = "⚠️ تحذير عاجل - تجنب المناطق الجبلية"
                desc   = "خطر عالٍ - يُنصح بعدم الذهاب للجبال"
            elif final_score >= 7:
                level  = "🟡 MODERATE"
                color  = "#f1c40f"
                css    = "risk-moderate"
                action = "📢 توخي الحذر في جبال الحجر"
                desc   = "خطر متوسط - كن حذراً ومتابعاً للأحوال"
            elif final_score >= 4:
                level  = "🔵 LOW"
                color  = "#3498db"
                css    = "risk-low"
                action = "ℹ️ متابعة الأحوال الجوية"
                desc   = "خطر منخفض - الأوضاع شبه طبيعية"
            else:
                level  = "🟢 MINIMAL"
                color  = "#2ecc71"
                css    = "risk-minimal"
                action = "✅ الأحوال مستقرة"
                desc   = "خطر ضئيل جداً - أوضاع مستقرة"

            # بطاقة النتيجة
            st.markdown(f"""
            <div class='{css}'>
                <h1 style='color:{color}; margin:0; font-size:2rem'>{level}</h1>
                <h2 style='color:white; margin:10px 0'>درجة الخطر: {final_score:.1f} / 25</h2>
                <h3 style='color:{color}; margin:5px 0'>{action}</h3>
                <p style='color:#bdc3c7; margin:0'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=final_score,
                title={"text": "مؤشر الخطر الكلي", "font": {"color":"white","size":16}},
                delta={"reference": 7, "valueformat": ".1f"},
                gauge={
                    "axis": {"range":[0,25], "tickcolor":"white",
                             "tickfont":{"color":"white"}},
                    "bar":  {"color": color, "thickness": 0.3},
                    "bgcolor": "rgba(0,0,0,0)",
                    "bordercolor": "#333",
                    "steps": [
                        {"range":[0,4],   "color":"rgba(46,204,113,0.3)"},
                        {"range":[4,7],   "color":"rgba(52,152,219,0.3)"},
                        {"range":[7,10],  "color":"rgba(241,196,15,0.3)"},
                        {"range":[10,15], "color":"rgba(230,126,34,0.3)"},
                        {"range":[15,25], "color":"rgba(231,76,60,0.3)"},
                    ],
                    "threshold": {
                        "line":{"color":"white","width":4},
                        "thickness":0.8,
                        "value": final_score
                    }
                },
                number={"font":{"color":"white","size":36}}
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white", height=280
            )
            st.plotly_chart(fig, use_container_width=True)

            # التحذيرات
            if warnings_list:
                st.markdown("### ⚠️ التحذيرات التفصيلية:")
                for icon, msg, clr in warnings_list:
                    st.markdown(f"""
                    <div style='background:rgba(0,0,0,0.3); border-left:3px solid {clr};
                                padding:10px 15px; margin:5px 0; border-radius:5px; color:white'>
                        {icon} {msg}
                    </div>
                    """, unsafe_allow_html=True)

            # المناطق المتأثرة
            if model_loaded:
                st.markdown("### 🏔️ المحطات الجبلية المتأثرة:")
                zone8 = df_meta[df_meta["Zone"] == 8][
                    ["Full_Name_eng","Full_Name_ar","Emirate","Lat.","Long."]
                ].reset_index(drop=True)
                st.dataframe(zone8, use_container_width=True)
        else:
            st.markdown("""
            <div style='text-align:center; padding:60px; color:#555;
                        border:2px dashed #333; border-radius:15px; margin-top:20px'>
                <div style='font-size:60px'>🔮</div>
                <h3 style='color:#888'>أدخل البيانات واضغط "احسب مستوى الخطر"</h3>
                <p style='color:#555'>سيظهر هنا تقييم تفصيلي لمستوى خطر العاصفة</p>
            </div>
            """, unsafe_allow_html=True)

# ====================================
# 📊 التحليل الشهري
# ====================================
elif page == "📊 التحليل الشهري":

    st.markdown("""
    <div class='hero-banner'>
        <h2 style='color:#e74c3c'>📊 التحليل المناخي الشهري</h2>
        <p style='color:#bdc3c7'>تحليل شامل للبيانات المناخية على مدار العام</p>
    </div>
    """, unsafe_allow_html=True)

    months = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
              "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]

    col1, col2 = st.columns(2)

    with col1:
        monthly_h = df_climate.groupby("month_num")["highest_temp"].mean()
        monthly_l = df_climate.groupby("month_num")["lowest_temp"].mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months, y=[monthly_h.get(m,0) for m in range(1,13)],
            name="أعلى حرارة",
            line=dict(color="#e74c3c", width=3),
            fill="tonexty", fillcolor="rgba(231,76,60,0.15)"
        ))
        fig.add_trace(go.Scatter(
            x=months, y=[monthly_l.get(m,0) for m in range(1,13)],
            name="أدنى حرارة",
            line=dict(color="#3498db", width=3)
        ))
        fig.update_layout(
            title=dict(text="🌡️ درجات الحرارة الشهرية", font=dict(color="white")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white", height=350,
            legend=dict(font=dict(color="white")),
            yaxis=dict(title="°C", gridcolor="#333"),
            xaxis=dict(gridcolor="#333")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        monthly_r = df_climate.groupby("month_num")["highest_rainfall"].mean()
        rvals     = [monthly_r.get(m,0) for m in range(1,13)]

        fig = go.Figure(go.Bar(
            x=months, y=rvals,
            marker=dict(
                color=rvals,
                colorscale="RdYlBu_r",
                showscale=True,
                colorbar=dict(title="mm", tickfont=dict(color="white"),
                              titlefont=dict(color="white"))
            ),
            text=[f"{v:.1f}" for v in rvals],
            textposition="outside",
            textfont=dict(color="white")
        ))
        fig.update_layout(
            title=dict(text="🌧️ متوسط الأمطار الشهري", font=dict(color="white")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white", height=350,
            yaxis=dict(title="mm", gridcolor="#333"),
            xaxis=dict(gridcolor="#333")
        )
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        monthly_w = df_climate.groupby("month_num")["max_wind"].mean()
        wvals     = [monthly_w.get(m,0) for m in range(1,13)]

        fig = go.Figure(go.Bar(
            x=months, y=wvals,
            marker_color=["#e74c3c" if w>80 else "#95a5a6" for w in wvals],
            text=[f"{w:.0f}" for w in wvals],
            textposition="outside",
            textfont=dict(color="white")
        ))
        fig.add_hline(y=80, line_dash="dash", line_color="yellow",
                      annotation_text="⚠️ حد الخطر",
                      annotation_font_color="yellow")
        fig.update_layout(
            title=dict(text="💨 الرياح الشهرية", font=dict(color="white")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white", height=350,
            yaxis=dict(title="km/h", gridcolor="#333"),
            xaxis=dict(gridcolor="#333")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        if "hajar_rain" in df_climate.columns:
            storm_monthly = df_climate.groupby("month_num")["hajar_rain"].sum()
            svals = [storm_monthly.get(m,0) for m in range(1,13)]
        else:
            svals = [0]*12

        fig = go.Figure(go.Bar(
            x=months, y=svals,
            marker_color=["#e74c3c" if v>3 else "#e67e22" if v>1 else "#f1c40f" for v in svals],
            text=[str(int(v)) for v in svals],
            textposition="outside",
            textfont=dict(color="white")
        ))
        fig.update_layout(
            title=dict(text="⛈️ أيام العواصف الجبلية", font=dict(color="white")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white", height=350,
            yaxis=dict(title="عدد الأيام", gridcolor="#333"),
            xaxis=dict(gridcolor="#333")
        )
        st.plotly_chart(fig, use_container_width=True)

    # جدول شهري
    st.markdown("### 📋 الجدول الشهري الكامل")
    try:
        monthly_table = df_climate.groupby("month").agg(
            أعلى_حرارة=("highest_temp","max"),
            أدنى_حرارة=("lowest_temp","min"),
            متوسط_أمطار=("highest_rainfall","mean"),
            أعلى_أمطار=("highest_rainfall","max"),
            أيام_عواصف=("hajar_rain","sum")
        ).round(1)
        st.dataframe(monthly_table, use_container_width=True)
    except:
        st.info("لا تتوفر بيانات كافية للجدول")

# ====================================
# 🌊 تحليل ENSO
# ====================================
elif page == "🌊 تحليل ENSO":

    st.markdown("""
    <div class='hero-banner'>
        <h2 style='color:#e74c3c'>🌊 تحليل ظاهرة النينيو (ENSO)</h2>
        <p style='color:#bdc3c7'>تأثير ظاهرة النينيو ولانينا على المناخ في الإمارات</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        enso_data = df_climate.groupby("enso_year_rainfall").agg(
            متوسط_أمطار=("highest_rainfall","mean"),
            أعلى_أمطار=("highest_rainfall","max"),
            متوسط_حرارة=("highest_temp","mean"),
            متوسط_رياح=("max_wind","mean"),
            عدد_الأيام=("highest_rainfall","count")
        ).round(1).reset_index()

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(enso_data,
                         x="enso_year_rainfall", y="متوسط_أمطار",
                         color="متوسط_أمطار",
                         color_continuous_scale="RdYlBu_r",
                         title="🌧️ تأثير ENSO على متوسط الأمطار",
                         text="متوسط_أمطار")
            fig.update_traces(texttemplate="%{text:.1f}", textposition="outside",
                              textfont_color="white")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)",
                              font_color="white", height=380,
                              title_font_color="white",
                              yaxis=dict(gridcolor="#333"),
                              xaxis=dict(gridcolor="#333"))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(enso_data,
                         x="enso_year_rainfall", y="أعلى_أمطار",
                         color="أعلى_أمطار",
                         color_continuous_scale="Reds",
                         title="🌊 تأثير ENSO على أعلى هطول مطري",
                         text="أعلى_أمطار")
            fig.update_traces(texttemplate="%{text:.1f}", textposition="outside",
                              textfont_color="white")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)",
                              font_color="white", height=380,
                              title_font_color="white",
                              yaxis=dict(gridcolor="#333"),
                              xaxis=dict(gridcolor="#333"))
            st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            fig = px.bar(enso_data,
                         x="enso_year_rainfall", y="متوسط_حرارة",
                         color="متوسط_حرارة",
                         color_continuous_scale="Hot",
                         title="🌡️ تأثير ENSO على متوسط الحرارة")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)",
                              font_color="white", height=350,
                              yaxis=dict(gridcolor="#333"),
                              xaxis=dict(gridcolor="#333"))
            st.plotly_chart(fig, use_container_width=True)

        with col4:
            fig = px.bar(enso_data,
                         x="enso_year_rainfall", y="متوسط_رياح",
                         color="متوسط_رياح",
                         color_continuous_scale="Blues",
                         title="💨 تأثير ENSO على متوسط الرياح")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)",
                              font_color="white", height=350,
                              yaxis=dict(gridcolor="#333"),
                              xaxis=dict(gridcolor="#333"))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📋 جدول تأثير ENSO الكامل")
        st.dataframe(enso_data, use_container_width=True)

    except Exception as e:
        st.error(f"خطأ في تحليل ENSO: {e}")

# ====================================
# 🗺️ خريطة المحطات
# ====================================
elif page == "🗺️ خريطة المحطات":

    st.markdown("""
    <div class='hero-banner'>
        <h2 style='color:#e74c3c'>🗺️ خريطة محطات الرصد الجوي</h2>
        <p style='color:#bdc3c7'>توزيع 146 محطة رصد جوي في الإمارات العربية المتحدة</p>
    </div>
    """, unsafe_allow_html=True)

    # إحصائيات المناطق
    if model_loaded:
        zone_counts = df_meta["Zone"].value_counts().sort_index()
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("🔴 Zone 8 (جبلية)", str(zone_counts.get(8,0)))
        with c2: st.metric("🟠 Zone 9 (ساحل شرقي)", str(zone_counts.get(9,0)))
        with c3: st.metric("🔵 Zone 1-5 (داخلية)", str(sum(zone_counts.get(i,0) for i in range(1,6))))
        with c4: st.metric("🟢 Zone 6-7 (ساحلية)", str(sum(zone_counts.get(i,0) for i in [6,7])))

    st.markdown("---")

    m = folium.Map(location=[24.0, 54.5], zoom_start=7,
                   tiles="CartoDB dark_matter")

    zone_colors = {
        8:"red", 9:"orange", 7:"blue", 6:"green",
        1:"lightblue", 2:"purple", 3:"cadetblue",
        4:"pink", 5:"lightgray"
    }
    zone_names = {
        8:"🏔️ جبلية", 9:"🌊 ساحل شرقي",
        7:"🌿 داخلية شمالية", 6:"🏙️ ساحلية",
        1:"🏜️ العين", 2:"🏛️ أبوظبي",
        3:"🛢️ الظفرة الساحلية", 4:"🌵 الظفرة الجنوبية",
        5:"🏗️ الظفرة الداخلية"
    }

    for _, row in df_meta.iterrows():
        if pd.notna(row["Lat."]) and pd.notna(row["Long."]):
            try:
                zone   = int(row["Zone"]) if pd.notna(row["Zone"]) else 0
                color  = zone_colors.get(zone, "gray")
                radius = 14 if zone == 8 else 8
                name_e = str(row["Full_Name_eng"]).strip()
                name_a = str(row["Full_Name_ar"]).strip()

                folium.CircleMarker(
                    location=[float(row["Lat."]), float(row["Long."])],
                    radius=radius,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.8,
                    popup=folium.Popup(
                        f"<b>{name_e}</b><br>{name_a}<br>Zone: {zone}<br>{zone_names.get(zone,'')}",
                        max_width=200
                    ),
                    tooltip=f"{'⭐ ' if zone==8 else ''}{name_e}"
                ).add_to(m)
            except:
                continue

    st_folium(m, width=None, height=550, returned_objects=[])

    # جدول المحطات الجبلية
    st.markdown("### 🏔️ تفاصيل المحطات الجبلية (Zone 8)")
    if model_loaded:
        zone8 = df_meta[df_meta["Zone"] == 8][
            ["Full_Name_eng","Full_Name_ar","Emirate","Lat.","Long.","Start_Date","End_Date"]
        ].reset_index(drop=True)
        st.dataframe(zone8, use_container_width=True)

# ====================================
# 📈 إحصائيات المشروع
# ====================================
elif page == "📈 إحصائيات المشروع":

    st.markdown("""
    <div class='hero-banner'>
        <h2 style='color:#e74c3c'>📈 إحصائيات المشروع</h2>
        <p style='color:#bdc3c7'>ملخص شامل لمشروع JM72 للإنذار المبكر بالعواصف الجبلية</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🤖 النموذج")
        st.metric("الخوارزمية",  "XGBoost")
        st.metric("الدقة الكلية","83.8%")
        st.metric("عدد المميزات","20")
        st.metric("عدد الفئات", "5")
        st.metric("طريقة التقييم","Cross-Validation")

    with col2:
        st.markdown("### 📊 البيانات")
        st.metric("إجمالي الأيام",   "366")
        st.metric("الفترة الزمنية",  "2003-2025")
        st.metric("إجمالي المحطات", "146")
        st.metric("المحطات الجبلية","6")
        st.metric("عدد الإمارات",    "7")

    with col3:
        st.markdown("### ⛈️ أرقام قياسية")
        st.metric("أعلى هطول",        "287.6mm")
        st.metric("أعلى رياح",         "141 km/h")
        st.metric("أبرد يوم - جبل جيس","-2°C")
        st.metric("أحر يوم",            "51.5°C")
        st.metric("أشد موسم",           "Strong El Niño")

    st.markdown("---")

    # مستويات الخطر
    st.markdown("### 🎯 تعريف مستويات الخطر")
    risk_def = pd.DataFrame({
        "المستوى":  ["🟢 MINIMAL","🔵 LOW","🟡 MODERATE","🟠 HIGH","🔴 EXTREME"],
        "الدرجة":   ["0-4","4-7","7-10","10-15","15+"],
        "الوصف":    [
            "أحوال مستقرة - لا توجد مخاوف",
            "بعض النشاط الجوي - متابعة مستمرة",
            "نشاط جوي ملحوظ - حذر مطلوب",
            "عواصف محتملة - تجنب الجبال",
            "عواصف شديدة - إغلاق فوري"
        ],
        "الإجراء":  [
            "✅ لا إجراء مطلوب",
            "ℹ️ متابعة الأحوال",
            "📢 تحذير للمواطنين",
            "⚠️ تحذير عاجل",
            "⛔ إغلاق فوري"
        ]
    })
    st.dataframe(risk_def, use_container_width=True, hide_index=True)

    # Feature Importance
    if model_loaded:
        st.markdown("### 🎯 أهمية المميزات في النموذج (Top 10)")
        feature_names = [
            "month_sin","month_cos","day_sin","day_cos",
            "highest_temp","lowest_temp","temp_range",
            "highest_rainfall","rainfall_occurrences",
            "max_wind","hajar_rain","hajar_wind",
            "mtn_thunderstorm_idx","rain_risk_index",
            "wind_risk","heat_stress_index","jais_cold",
            "enso_year_max_temp","enso_year_rainfall",
            "rainfall_in_hajar"
        ]
        try:
            imp = pd.DataFrame({
                "المميزة": feature_names[:len(model.feature_importances_)],
                "الأهمية": model.feature_importances_
            }).sort_values("الأهمية", ascending=True).tail(10)

            fig = px.bar(imp, x="الأهمية", y="المميزة",
                         orientation="h",
                         color="الأهمية",
                         color_continuous_scale="Reds",
                         title="أهم 10 مميزات في النموذج",
                         text="الأهمية")
            fig.update_traces(texttemplate="%{text:.3f}", textposition="outside",
                              textfont_color="white")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white", height=420,
                title_font_color="white",
                yaxis=dict(gridcolor="#333"),
                xaxis=dict(gridcolor="#333")
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info(f"تعذر عرض Feature Importance: {e}")

    # معلومات التقنية
    st.markdown("### 🛠️ التقنيات المستخدمة")
    tech_cols = st.columns(4)
    techs = [
        ("🐍","Python 3.11"),
        ("🤖","XGBoost"),
        ("🌐","Streamlit"),
        ("📊","Plotly"),
        ("🗺️","Folium"),
        ("🐼","Pandas"),
        ("🔢","NumPy"),
        ("💾","Joblib")
    ]
    for i, (icon, name) in enumerate(techs):
        with tech_cols[i % 4]:
            st.markdown(f"""
            <div style='background:#1a1a2e; border:1px solid #333;
                        border-radius:8px; padding:10px; text-align:center;
                        margin:5px 0; color:white'>
                <div style='font-size:24px'>{icon}</div>
                <div style='font-size:12px; color:#bdc3c7'>{name}</div>
            </div>
            """, unsafe_allow_html=True)
