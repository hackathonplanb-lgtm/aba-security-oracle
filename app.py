import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import numpy as np
from sklearn.cluster import KMeans

st.set_page_config(page_title="Aba Security Oracle", layout="wide", initial_sidebar_state="expanded")

st.title("🔮 ABA SECURITY ORACLE")
st.markdown("**Built by: Team Great (resilience-lgtm) – Deep-Fuding-Hackathon-sketch**")
st.markdown("**Real-Time Predictive Policing System for Aba, Abia State**")

# Load data
incidents = pd.read_csv("incidents.csv")
police = pd.read_csv("police.csv")

# Sidebar
with st.sidebar:
    st.header("Prediction Command Center")
    predict_date = st.date_input("Select date to predict:", datetime.now() + timedelta(days=1))
    if st.button("🔥 RUN PREDICTION", type="primary", use_container_width=True):
        st.session_state.pred_date = predict_date

m = folium.Map(location=[5.107, 7.369], zoom_start=13, tiles="CartoDB positron")
HeatMap(incidents[['lat','lon']].values.tolist(), radius=14, blur=20).add_to(m)

# Current hotspots
kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
clusters = kmeans.fit_predict(incidents[['lat','lon']])
centers = kmeans.cluster_centers_
names = ["Ariaria", "Ngwa Road", "Osisioma", "Ogbor Hill", "Ekeoha", "Asa Road", "Faulks Road", "Port Harcourt Rd"]

for i, (lat, lon) in enumerate(centers):
    count = sum(clusters == i)
    color = "red" if count > 20 else "orange" if count > 10 else "lime"
    folium.Circle([lat, lon], radius=700, color=color, fill=True, fillOpacity=0.4,
                  popup=f"<b>{names[i]}</b><br>Past crimes: {count}").add_to(m)

# POLICE
for _, r in police.iterrows():
    folium.CircleMarker([r.lat, r.lon], radius=9, color="blue", fill=True, 
                         popup=r.get("name","Police Station")).add_to(m)

# === PREDICTION ENGINE ===
if 'pred_date' in st.session_state:
    d = st.session_state.pred_date
    mul = 1.0
    triggers = []
    
    if d.month in [5,6,7,8,9,10]: 
        mul *= 2.5; triggers.append("Rainy Season")
    if d.weekday() == 0: 
        mul *= 5.0; triggers.append("Sit-at-Home Monday")
    if d.day >= 25: 
        mul *= 2.0; triggers.append("Salary Week")
    if d.weekday() in [2,5]: 
        mul *= 3.0; triggers.append("Ariaria Big Market Day")
    
    base = [15,12,18,10,14,11,9,13]
    pred = [int(b * mul) for b in base]
    
    # TEXT PREDICTION
    st.success(f"**PREDICTION FOR {d.strftime('%A, %B %d, %Y')}** ×{mul:.1f} risk")
    st.warning("⚠️ **HIGH-RISK ZONES TODAY:**")
    high = []
    for i, c in enumerate(pred):
        if c >= 40:
            high.append(f"**{names[i]}**: {c} crimes expected")
            folium.Circle([centers[i][0], centers[i][1]], radius=1500, color="#8B0000", weight=8, fill=False,
                          popup=f"<b>ALERT: {c} crimes predicted</b>").add_to(m)
        elif c >= 20:
            folium.Circle([centers[i][0], centers[i][1]], radius=1000, color="red", weight=5, fill=False).add_to(m)
    
    if high:
        st.error(" → " + " | ".join(high))
    else:
        st.info("Moderate risk across Aba today")

# Show map
st_folium(m, width=1200, height=650, key=f"map_{hash(str(st.session_state.get('pred_date','')))}")

st.caption("Live • On-Demand • Built by Chibuike Okeke")
