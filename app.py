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
    st.warning("CSS file not found - using default styling")

# ==========================================
# LOGO
# ==========================================
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="color: #082F49; font-size: 48px;">🌩️ 71wm AI</h1>
    <p style="color: #0284C7; font-size: 18px; font-weight: bold;">Weather Model - United Arab Emirates</p>
    <hr style="border: 2px solid #0284C7; margin: 20px 0;">
</div>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR MENU
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #0284C7, #082F49); border-radius: 12px; color: white; margin-bottom: 20px;">
        <h3>71wm Navigator</h3>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.radio(
        "Select Page:",
        ["🏠 Home", "🌩️ Forecasts", "📊 Analytics", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; font-size: 12px; color: #64748B;">
        <p><b>Version:</b> 1.0</p>
        <p><b>Status:</b> Active</p>
        <p><b>Last Update:</b> Today</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# PAGE CONTENT
# ==========================================

if "🏠 Home" in page:
    st.markdown("## Welcome to 71wm AI Weather Model")
    st.markdown("Real-time weather forecasting for the UAE")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("System Status", "Active", "+2")
    with col2:
        st.metric("Total Stations", "36", "+5")
    with col3:
        st.metric("Forecast Range", "5 Days", "120 hrs")
    
    st.markdown("---")
    
    st.markdown("""
    ### Key Features
    
    🌩️ **Storm Detection** - Real-time convective activity tracking
    
    🌡️ **Temperature Analysis** - Thermal range forecasting
    
    ☁️ **Cloud Patterns** - Al-Kous and drizzle detection
    
    📊 **Data Dashboard** - 36-station matrix system
    
    📧 **Smart Alerts** - Automated email notifications
    """)

elif "🌩️ Forecasts" in page:
    st.markdown("##
