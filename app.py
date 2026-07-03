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
    st.markdown("## Welcome to 71wm AI Weather Model")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", "Active", "+2")
    with col2:
        st.metric("Stations", "36", "+5")
    with col3:
        st.metric("Forecast", "5 Days", "120h")
    
    st.markdown("---")
    st.markdown("""
    ### Features
    - Storm Detection
    - Temperature Analysis
    - Cloud Patterns
    - Data Dashboard
    - Smart Alerts
    """)

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
