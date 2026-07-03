import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import requests

st.set_page_config(
    page_title="71wm AI Weather Model",
    page_icon="🌩️",
    layout="wide"
)

try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="color: #082F49; font-size: 48px;">71wm AI</h1>
    <p style="color: #0284C7; font-size: 18px;">Weather Model - UAE</p>
    <hr style="border: 2px solid #0284C7;">
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #0284C7, #082F49); border-radius: 12px; color: white;">
        <h3>71wm Navigator</h3>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.radio(
        "Select Page:",
        ["Home", "Forecasts", "Analytics", "Settings"]
    )

if page == "Home":
    # ==========================================
    # HERO SECTION
    # ==========================================
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0284C7 0%, #082F49 100%); 
                padding: 40px; 
                border-radius: 16px; 
                color: white; 
                text-align: center; 
                margin-bottom: 30px;
                box-shadow: 0 8px 32px rgba(2, 132, 199, 0.3);">
        <h2 style="margin: 0; font-size: 36px; font-weight: 900;">🌩️ 71wm AI Weather Model</h2>
        <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">Real-time Weather Intelligence for UAE</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ==========================================
    # KEY METRICS CARDS
    # ==========================================
    st.markdown("<h3 style='color: #082F49; margin-top: 30px;'>System Status</h3>", unsafe_allow_html=True)
    
    metric1, metric2, metric3, metric4 = st.columns(4)
    
    with metric1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                    padding: 20px;
                    border-radius: 12px;
                    color: white;
                    text-align: center;
                    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);">
            <div style="font-size: 28px; font-weight: 900;">✅</div>
            <div style="font-size: 24px; font-weight: 900; margin: 10px 0;">Active</div>
            <div style="font-size: 14px; opacity: 0.9;">System Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
                    padding: 20px;
                    border-radius: 12px;
                    color: white;
                    text-align: center;
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);">
            <div style="font-size: 28px; font-weight: 900;">📍</div>
            <div style="font-size: 24px; font-weight: 900; margin: 10px 0;">36</div>
            <div style="font-size: 14px; opacity: 0.9;">Monitoring Stations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
                    padding: 20px;
                    border-radius: 12px;
                    color: white;
                    text-align: center;
                    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);">
            <div style="font-



elif page == "Forecasts":
    st.markdown("## Weather Forecasts")
    st.info("Forecast data coming soon")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Storm Probability")
        st.write("Data will appear here")
    with col2:
        st.subheader("Temperature Range")
        st.write("Data will appear here")

elif page == "Analytics":
    st.markdown("## Analytics Dashboard")
    st.info("Analytics coming soon")

elif page == "Settings":
    st.markdown("## System Settings")
    
    with st.expander("Email Configuration"):
        email_enabled = st.checkbox("Enable Email Alerts")
        if email_enabled:
            st.text_input("Sender Email")
            st.text_input("Password", type="password")
            st.text_input("Recipient Email")
    
    with st.expander("Advanced Settings"):
        st.slider("Refresh Interval (minutes)", 5, 60, 15)
        st.selectbox("Theme", ["Light", "Dark"])

st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 12px; color: #64748B;">
    <p>71wm AI Weather Model v1.0 | UAE Weather Forecasting System</p>
</div>
""", unsafe_allow_html=True)
