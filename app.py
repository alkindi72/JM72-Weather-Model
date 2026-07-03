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
    with col4:
        st.metric("Coverage", "UAE")
    
    st.markdown("---")
    
    # ==========================================
    # CHART 1: Temperature Trend
    # ==========================================
    st.markdown("<h3 style='color: #082F49;'>Temperature Forecast (Next 5 Days)</h3>", unsafe_allow_html=True)
    
    dates = pd.date_range(start=datetime.now(), periods=120, freq='H')
    temps = 35 + np.sin(np.arange(120)/24) * 5 + np.random.normal(0, 1, 120)
    
    df_temp = pd.DataFrame({
        'Time': dates,
        'Temperature': temps
    })
    
    fig_temp = px.line(
        df_temp,
        x='Time',
        y='Temperature',
        title='Temperature Trend',
        labels={'Temperature': 'Temp (C)', 'Time': 'Date/Time'},
        color_discrete_sequence=['#0284C7']
    )
    fig_temp.update_layout(
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    st.plotly_chart(fig_temp, use_container_width=True)
    
    # ==========================================
    # CHART 2: Storm Probability
    # ==========================================
    st.markdown("<h3 style='color: #082F49;'>Storm Probability (Next 5 Days)</h3>", unsafe_allow_html=True)
    
    storm_prob = 15 + np.sin(np.arange(120)/20) * 20 + np.random.normal(0, 3, 120)
    storm_prob = np.clip(storm_prob, 0, 100)
    
    df_storm = pd.DataFrame({
        'Time': dates,
        'Probability': storm_prob
    })
    
    fig_storm = px.area(
        df_storm,
        x='Time',
        y='Probability',
        title='Storm Risk Level',
        labels={'Probability': 'Risk (%)', 'Time': 'Date/Time'},
        color_discrete_sequence=['#EF4444']
    )
    fig_storm.update_layout(
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    st.plotly_chart(fig_storm, use_container_width=True)
    
    # ==========================================
    # CHART 3: Humidity Distribution
    # ==========================================
    st.markdown("<h3 style='color: #082F49;'>Humidity Levels Across Stations</h3>", unsafe_allow_html=True)
    
    stations = ['Abu Dhabi', 'Dubai', 'Sharjah', 'Al Ain', 'Fujairah', 'Ras Al Khaimah']
    humidity = [65, 72, 68, 55, 78, 75]
    
    df_humidity = pd.DataFrame({
        'Station': stations,
        'Humidity': humidity
    })
    
    fig_humidity = px.bar(
        df_humidity,
        x='Station',
        y='Humidity',

    

    
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
