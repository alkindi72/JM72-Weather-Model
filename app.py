import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="71wm AI", page_icon="cloud", layout="wide")

try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

st.markdown("<h1 style='text-align: center; color: #082F49;'>71wm AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #0284C7;'>Weather Model - UAE</p>", unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.markdown("<h3>Navigation</h3>", unsafe_allow_html=True)
    page = st.radio("Select Page:", ["Home", "Forecasts", "Analytics", "Settings"])

if page == "Home":
    st.markdown("<h2 style='color: #082F49;'>Welcome to 71wm AI</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Status", "Active")
    with col2:
        st.metric("Stations", "36")
    with col3:
        st.metric("Forecast", "5 Days")
    

    
    st.markdown("---")
    
    st.markdown("<h3 style='color: #082F49;'>Features</h3>", unsafe_allow_html=True)
    st.markdown("- Storm Detection")
    st.markdown("- Temperature Analysis")
    st.markdown("- Cloud Patterns")
    st.markdown("- Real-time Alerts")

elif page == "Forecasts":
    st.markdown("<h2>Weather Forecasts</h2>", unsafe_allow_html=True)
    st.info("Forecast data coming soon")

elif page == "Analytics":
    st.markdown("<h2>Analytics Dashboard</h2>", unsafe_allow_html=True)
    st.info("Analytics coming soon")

elif page == "Settings":
    st.markdown("<h2>System Settings</h2>", unsafe_allow_html=True)
    with st.expander("Email Configuration"):
        st.text_input("Email")
        st.text_input("Password", type="password")

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 12px; color: #64748B;'>71wm AI v1.0</p>", unsafe_allow_html=True)
