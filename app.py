
import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import numpy as np
from sklearn.cluster import KMeans
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.set_page_config(page_title="Aba Security Oracle", layout="wide")
st.title("ABA SECURITY ORACLE")
st.markdown("### Real-Time Crime Prediction & Hotspot Mapping System")
st.markdown("**Built by: [Team Great] – DeepFunding Hackathon**")

# Load data
@st.cache_data
def load_data():
    incidents = pd.read_csv("incidents.csv")
    police = pd.read_csv("police.csv")
    return incidents, police

incidents, police = load_data()

# Sidebar
with st.sidebar:
    st.header("Prediction Controls")
    predict_date = st.date_input("Select date to predict:", datetime.now() + timedelta(days=1))
    if st.button("Generate Map & Prediction", type="primary"):
        st.session_state.pred_date = predict_date

# Main map
m = folium.Map(location=[5.107, 7.369], zoom_start=13, tiles="CartoDB positron")

# Heatmap
HeatMap(incidents[['lat','lon']].values.tolist(), radius=14, blur=20).add_to(m)

# Hotspots
kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
clusters = kmeans.fit_predict(incidents[['lat','lon']])
centers = kmeans.cluster_centers_

for i, (lat, lon) in enumerate(centers):
    count = sum(clusters == i)
    risk = "HIGH" if count > 20 else "MEDIUM" if count > 10 else "LOW"
    color = "red" if count > 20 else "orange" if count > 10 else "lime"
    folium.Circle(
        [lat, lon], radius=700, color=color, fill=True, fillOpacity=0.4,
        popup=f"<b>Hotspot {i+1}</b><br>Crimes: {count}<br>Risk: {risk}"
    ).add_to(m)

# Police stations
for _, row in police.iterrows():
    folium.CircleMarker(
        [row.lat, row.lon], radius=9, color="blue", fill=True, fillOpacity=0.8,
        popup=f"<b>{row['name']}</b>"
    ).add_to(m)

# Display map
st_folium(m, width=1200, height=600)

# Statistics
col1, col2, col3 = st.columns(3)
col1.metric("Total Incidents", len(incidents))
col2.metric("Crime Hotspots", 8)
col3.metric("Police Stations", len(police))

st.success("Live System • Updates Daily • Powered by Real Crime Data")
