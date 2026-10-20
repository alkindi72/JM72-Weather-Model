#!/usr/bin/env python3
"""
Standalone alert checker for Render Cron Jobs.
Add this as a Cron Job in Render dashboard:
- Command: python check_alerts.py
- Schedule: */15 * * * *   (every 15 minutes)
"""
import os, sys, requests
from datetime import datetime

print(f"[{datetime.utcnow().isoformat()}Z] Running alert check...")

# Wake the main app by requesting it (keeps it warm and triggers alert logic)
APP_URL = os.getenv("APP_URL", "https://jm72-weather-model.onrender.com")
try:
    r = requests.get(APP_URL, timeout=30)
    print(f"App ping status: {r.status_code}")
except Exception as e:
    print(f"Ping failed: {e}")

print("Alert check finished")
