import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pages import render_home

st.set_page_config(
    page_title="71wm AI Weather Model",
    page_icon="cloud",
    layout="wide"
)

try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

html_header = '<div style="text-align: center; margin-bottom: 30px;"><h1 style="color: #082F49; font-size: 48px;">71wm AI</h1><p style="color: #0284C7; font-size: 18px;">Weather Model - UAE</p><hr style="border: 2px solid #0284C7;"></div>'
st.markdown(html_header, unsafe_allow_html=True)

with st.sidebar:
    html_sidebar = '<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #0284C7, #082F49); border-radius: 12px; color: white;"><h3>Navigator</h3></div>'
    st.markdown(html_sidebar, unsafe_allow_html=True)
    
    page = st.radio(
        "Select Page:",
        ["Home", "Forecasts", "Analytics", "Settings"]
    )

if page == "Home":
    render_home()

elif page == "Forecasts":
    st.markdown("## Weather Forecasts")
    st.info("Forecast data coming soon")

elif page == "Analytics":
    st.markdown("## Analytics Dashboard")
    st.info("Analytics coming soon")

elif page == "Settings":
    st.markdown("## System Settings")
    with st.expander("Email Configuration"):
        st.text_input("Email")
        st.text_input("Password", type="password")

html_footer = '<div style="text-align: center; font-size: 12px; color: #64748B; margin-top: 50px;"><hr><p>71wm AI Weather Model v1.0</p></div>'
st.markdown(html_footer, unsafe_allow_html=True)
