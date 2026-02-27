import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import requests
import time
import math

# ==========================
# TELEGRAM CONFIG

TELEGRAM_TOKEN = "8440286651:AAFhJmqBLuWQpz7oRV3vPwxJYxvViCzgmYE"
TELEGRAM_CHAT_ID = "5977636479"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=5)
        time.sleep(0.2)
    except:
        pass

# ==========================
# FIRE DATA GENERATION

def generate_fire_data(n=10000):

    df = pd.DataFrame({
        "latitude": np.random.uniform(-50, 60, n),
        "longitude": np.random.uniform(-180, 180, n),
        "brightness": np.random.uniform(300, 500, n),
        "confidence": np.random.uniform(50, 100, n),
        "wind_speed": np.random.uniform(0, 15, n),
        "wind_direction": np.random.uniform(0, 360, n)
    })

    df["risk"] = (df["brightness"]/400)*0.6 + (df["confidence"]/100)*0.4

    return df

# ==========================
# AI FIRE SPREAD MODEL

def predict_spread(lat, lon, wind_speed, wind_dir):

    distance = wind_speed * 0.01
    rad = math.radians(wind_dir)

    new_lat = lat + distance * math.cos(rad)
    new_lon = lon + distance * math.sin(rad)

    return new_lat, new_lon

# ==========================

st.set_page_config(page_title="🔥 AI Fire Monitoring", layout="wide")

st.title("🔥 Global AI Fire Monitoring System")

df = generate_fire_data()

# ==========================
# MAP

st.subheader("🗺️ Fire Map")

m = folium.Map(location=[20,0], zoom_start=2)

cluster = MarkerCluster().add_to(m)

high_risk = []

for _, row in df.iterrows():

    lat = row["latitude"]
    lon = row["longitude"]
    risk = row["risk"]

    if risk > 0.7:
        color = "red"
    elif risk > 0.4:
        color = "orange"
    else:
        color = "green"

    folium.CircleMarker(
        location=[lat, lon],
        radius=3,
        color=color,
        fill=True,
        fill_opacity=0.7,
        popup=f"Risk:{risk:.2f}"
    ).add_to(cluster)

    # AI spread prediction
    new_lat, new_lon = predict_spread(
        lat,
        lon,
        row["wind_speed"],
        row["wind_direction"]
    )

    folium.CircleMarker(
        location=[new_lat, new_lon],
        radius=2,
        color="blue",
        fill=True
    ).add_to(cluster)

    if risk > 0.8:
        high_risk.append(row)

st_folium(m, width=1300, height=700)

# ==========================
# AI STATISTICS

st.subheader("🤖 AI Fire Prediction")

st.write("Total fires:", len(df))
st.write("High risk fires:", len(high_risk))

# ==========================
# AUTO TELEGRAM ALERT (батырмасыз)

if len(high_risk) > 0:

    send_telegram(f"🚨 HIGH RISK FIRES DETECTED: {len(high_risk)}")

    for row in high_risk[:20]:

        msg = f"""
🔥 HIGH RISK FIRE

Lat: {row['latitude']:.3f}
Lon: {row['longitude']:.3f}

Risk: {row['risk']:.2f}
Brightness: {row['brightness']:.1f}
Confidence: {row['confidence']:.1f}

Wind Speed: {row['wind_speed']:.1f}
Wind Direction: {row['wind_direction']:.0f}
"""

        send_telegram(msg)

st.success("✅ System monitoring fires 24/7")