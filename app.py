import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import requests

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="71wm AI Weather Model",
    page_icon="🌩️",
    layout="wide"
)

# ==========================================
# LOAD CUSTOM CSS
# ==========================================
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    st.warning("CSS file not found")

# ==========================================
# LOGO
# ==========================================
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="color: #082F49; font-size: 48px;">71wm AI</h1>
    <p style="color: #0284C7; font-size: 18px;">Weather Model - United Arab Emirates</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR MENU
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #0284C7, #082F49); border-radius: 12px; color: white;">
        <h2>Navigation Menu</h2>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.radio(
        "Select Page",
        ["Home", "Forecasts", "Analytics", "Settings"]
    )

# ==========================================
# PAGE CONTENT
# ==========================================
if page == "Home":
    st.markdown("## Welcome to 71wm AI Weather Model")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Status", "Active", "+2")
    with col2:
        st.metric("Stations", "36", "+5")
    with col3:
        st.metric("Forecast Range", "5 Days", "120 hrs")
    
    st.markdown("---")
    
    st.markdown("""
    ### Key Features
    
    - 🌩️ Storm Detection & Forecasting
    - 🌡️ Temperature Analysis
    - ☁️ Cloud Pattern Recognition
    - 📊 Real-time Data Dashboard
    - 📧 Automated Alert System
    """)

elif page == "Forecasts":
    st.markdown("## Weather Forecasts")
    st.info("Forecast data will be displayed here")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Storm Probability")
        st.write("No data yet")
    with col2:
        st.subheader("Temperature Range")
        st.write("No data yet")

elif page == "Analytics":
    st.markdown("## Analytics Dashboard")
    st.info("Analytics will be displayed here")

elif page == "Settings":
    st.markdown("## System Settings")
    
    with st.expander("Email Configuration"):
        email_enabled = st.checkbox("Enable Email Alerts")
        if email_enabled:
            st.text_input("Sender Email")
            st.text_input("Password", type="password")
            st.text_input("Recipient Email")
    
    with
