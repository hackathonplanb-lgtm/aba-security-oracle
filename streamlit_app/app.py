
import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import numpy as np
from sklearn.cluster import KMeans

st.set_page_config(page_title="Aba Security Oracle", layout="wide")
st.title("ABA SECURITY ORACLE")
st.markdown("**Built by: Chibuike Okeke (hackathonplanb-lgtm) – B.Sc Computer Science 2025**")
st.markdown("**Real-Time Crime Prediction & Hotspot Mapping System for Aba, Abia State**")

# Load data
incidents = pd.read_csv("incidents.csv")
police = pd.read_csv("police.csv")

# Sidebar prediction
with st.sidebar:
    st.header("Prediction Engine")
    predict_date = st.date_input("Select date to predict:", datetime.now() + timedelta(days=1))
    if st.button("Run Prediction", type="primary"):
        st.session_state.date = str(predict_date)

# Map
m = folium.Map(location=[5.107, 7.369], zoom_start=13, tiles="CartoDB positron")
HeatMap(incidents[['lat','lon']].values.tolist(), radius=14).add_to(m)

# Current hotspots
kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
clusters = kmeans.fit_predict(incidents[['lat','lon']])
centers = kmeans.cluster_centers_
names = ["Ariaria","Ngwa Rd","Osisioma","Ogbor Hill","Ekeoha","Asa Rd","Faulks Rd","P.H. Rd"]

for i, (lat, lon) in enumerate(centers):
    count = sum(clusters == i)
    color = "red" if count > 20 else "orange" if count > 10 else "lime"
    folium.Circle([lat, lon], radius=700, color=color, fill=True, fillOpacity=0.4,
                  popup=f"<b>{names[i]}</b><br>Crimes: {count}").add_to(m)

# ON-DEMAND PREDICTION
if "date" in st.session_state:
    d = datetime.strptime(st.session_state.date, "%Y-%m-%d")
    mul = 1.0
    if d.month in [5,6,7,8,9,10]: mul *= 2.5
    if d.weekday() == 0: mul *= 5.0
    if d.day >= 25: mul *= 2.0
    if d.weekday() in [2,5]: mul *= 3.0
    base = [15,12,18,10,14,11,9,13]
    pred = [int(b * mul) for b in base]
    
    for i, c in enumerate(pred):
        if c > 15:
            folium.Circle([centers[i][0], centers[i][1]], radius=1200, color="darkred", weight=7, fill=False,
                          popup=f"<b>PREDICTED: {c} crimes</b><br>{names[i]}").add_to(m)
    st.success(f"Prediction for {d.strftime('%A, %B %d, %Y')} ×{mul:.1f} risk")

# Police
for _, r in police.iterrows():
    folium.CircleMarker([r.lat, r.lon], radius=9, color="blue", fill=True, popup=r.get("name","Police")).add_to(m)

st_folium(m, width=1200, height=650)
st.caption("Live • On-Demand • Built by Chibuike Okeke")
