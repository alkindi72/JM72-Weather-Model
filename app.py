import os
import re
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import requests
import base64
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="71wm AI Weather Model",
    page_icon="🌩️",
    layout="wide"
)

# ==========================================
# CUSTOM CSS
# ==========================================
css_content = """
html, body, [data-testid="stAppViewContainer"], .stApp, #root {
    background-color: #F8FAFC !important;
}
.block-container {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
    padding: 2rem !important;
    margin: 1rem auto !important;
    border: 1px solid #E2E8F0 !important;
    max-width: 95% !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"] {
    display: none !important;
}
.stApp p, .stApp span, .stApp label, h1, h2, h3, h4, h5, h6 {
    color: #082F49 !important;
    font-weight: 900 !important;
    font-size: 15px !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    border-bottom: 2px solid #CBD5E1 !important;
}
div[data-testid="stTabs"] button {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px 8px 0 0 !important;
    margin-right: 5px !important;
    padding: 10px 20px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    background-color: #082F49 !important;
    border-color: #082F49 !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] p {
    color: #FFFFFF !important;
}
.ai-broadcaster {
    background: linear-gradient(90deg, #F0F9FF, #E0F2FE);
    border-left: 5px solid #0284C7;
    padding: 15px 20px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: bold;
    color: #0369A1;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(2, 132, 199, 0.1);
}
div[data-testid="stSlider"] {
    background-color: #F1F5F9 !important;
    padding
