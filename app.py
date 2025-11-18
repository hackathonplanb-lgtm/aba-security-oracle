import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from sklearn.cluster import KMeans

st.set_page_config(page_title="Aba Security Oracle", layout="wide", initial_sidebar_state="expanded")

st.title("ABA SECURITY ORACLE")
st.markdown("**Built by: Team Great (resilience-lgtm) – B.Sc Computer Science 2025**")
st.markdown("**Advanced Crime Hotspot & Tactical Response System**")

# Load data
incidents = pd.read_csv("incidents.csv")
police = pd.read_csv("police.csv")

# Sidebar
with st.sidebar:
    st.header("Tactical Command")
    predict_date = st.date_input("Predict for:", datetime.now() + timedelta(days=1))
    if st.button("GENERATE PREDICTION", type="primary", use_container_width=True):
        st.session_state.pred = predict_date

# Create map
m = folium.Map(location=[5.107, 7.369], zoom_start=13, tiles="CartoDB positron")

# 1. Crime Heatmap
HeatMap(incidents[['lat','lon']].values.tolist(), radius=15, blur=22).add_to(m)

# 2. 8 Hotspots (clean circles)
kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
clusters = kmeans.fit_predict(incidents[['lat','lon']])
centers = kmeans.cluster_centers_
names = ["Ariaria", "Ngwa Road", "Osisioma", "Ogbor Hill", "Ekeoha", "Asa Road", "Faulks Road", "Port Harcourt Rd"]

for i, (lat, lon) in enumerate(centers):
    count = sum(clusters == i)
    risk = "HIGH" if count > 20 else "MEDIUM" if count > 10 else "LOW"
    color = "red" if count > 20 else "orange" if count > 10 else "lime"
    folium.Circle(
        location=[lat, lon],
        radius=800,
        color=color,
        weight=3,
        fill=True,
        fillOpacity=0.4,
        popup=folium.Popup(f"<b>{names[i]}</b><br>Crimes: {count}<br>Risk: {risk}", max_width=300)
    ).add_to(m)

# 3. Police Stations (blue)
for _, row in police.iterrows():
    folium.CircleMarker(
        location=[row.lat, row.lon],
        radius=10,
        color="darkblue",
        fill=True,
        fillOpacity=1,
        popup=folium.Popup(f"<b>{row.get('name', 'Police Station')}</b>", max_width=300)
    ).add_to(m)

# 4. Escape Routes (cyan arrows)
escape_routes = [
    [[5.116, 7.355], [5.105, 7.370]],  # Osisioma → Center
    [[5.100, 7.380], [5.110, 7.360]],  # Ariaria → Safe zone
    [[5.090, 7.350], [5.120, 7.380]],  # South → North
]
for route in escape_routes:
    folium.PolyLine(
        route,
        color="cyan",
        weight=8,
        opacity=0.9,
        popup="Safe Escape Route"
    ).add_to(m)
    # Arrow at end
    folium.RegularPolygonMarker(
        location=route[-1],
        fill_color='cyan',
        number_of_sides=3,
        rotation=30,
        radius=10
    ).add_to(m)

# 5. Legend (clean & beautiful)
legend_html = '''
<div style="position: fixed; bottom: 20px; left: 20px; width: 220px; height: 180px; 
            background-color: white; border:2px solid grey; z-index:9999; font-size:14px; padding: 10px;
            border-radius: 10px;">
<h4 style="margin:5px">Legend</h4>
<i style="background:red; width:18px; height:18px; float:left; margin:5px; opacity:0.7"></i> High Crime Zone<br>
<i style="background:orange; width:18px; height:18px; float:left; margin:5px; opacity:0.7"></i> Medium Crime Zone<br>
<i style="background:lime; width:18px; height:18px; float:left; margin:5px; opacity:0.7"></i> Low Crime Zone<br><br>
<i style="background:darkblue; border-radius:50%; width:18px; height:18px; float:left; margin:5px"></i> Police Station<br>
<i style="background:cyan; width:30px; height:4px; float:left; margin:8px 5px"></i> Escape Route
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# 6. Realistic Prediction (only when button clicked)
if 'pred' in st.session_state:
    d = st.session_state.pred
    mul = 1.0
    if d.weekday() == 0: mul *= 3.0
    if d.month in [5,6,7,8,9,10]: mul *= 1.7
    if d.day >= 25: mul *= 1.5
    mul = min(mul, 5.0)
    
    base = [10, 8, 12, 7, 9, 8, 7, 10]
    pred = [int(b * mul) for b in base]
    
    st.success(f"Prediction: {d.strftime('%A, %B %d, %Y')} — Risk ×{mul:.1f}")
    high = [f"{names[i]} ({pred[i]})" for i, p in enumerate(pred) if p >= 30]
    if high:
        st.error("HIGH ALERT: " + " | ".join(high))
        # Add red alert rings
        for i, c in enumerate(pred):
            if c >= 30:
                folium.Circle([centers[i][0], centers[i][1]], radius=1200, color="#8B0000", weight=8, fill=False).add_to(m)
    else:
        st.info("Moderate risk expected")

# Show map
st_folium(m, width=1200, height=700, key=f"map_{st.session_state.get('pred', 'none')}")

st.caption("Live • Tactical • OpenStreetMap • AI-Assisted Development")
