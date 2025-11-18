import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from sklearn.cluster import KMeans

st.set_page_config(page_title="Aba Security Oracle", layout="wide", initial_sidebar_state="expanded")

st.title("ABA SECURITY ORACLE")
st.markdown("**Built by: Team Udo (resilience-)**")
st.markdown("**Advanced Crime Hotspot & Tactical Response System**")

# Load data
incidents = pd.read_csv("incidents.csv")
police = pd.read_csv("police.csv")

# Sidebar
with st.sidebar:
    st.header("Tactical Command Center")
    predict_date = st.date_input("Select date for prediction:", datetime.now() + timedelta(days=1))
    if st.button("GENERATE PREDICTION", type="primary", use_container_width=True):
        st.session_state.pred = predict_date

# Base map
m = folium.Map(location=[5.107, 7.369], zoom_start=13, tiles="CartoDB positron")
HeatMap(incidents[['lat','lon']].values.tolist(), radius=15, blur=22).add_to(m)

# Hotspots
kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
clusters = kmeans.fit_predict(incidents[['lat','lon']])
centers = kmeans.cluster_centers_
names = ["Ariaria", "Ngwa Road", "Osisioma", "Ogbor Hill", "Ekeoha", "Asa Road", "Faulks Road", "Port Harcourt Rd"]

for i, (lat, lon) in enumerate(centers):
    count = sum(clusters == i)
    color = "red" if count > 20 else "orange" if count > 10 else "lime"
    folium.Circle([lat, lon], radius=800, color=color, weight=3, fill=True, fillOpacity=0.4,
                  popup=f"<b>{names[i]}</b><br>Incidents: {count}").add_to(m)

# Police Stations
for _, row in police.iterrows():
    folium.CircleMarker([row.lat, row.lon], radius=11, color="darkblue", fill=True,
                        popup=f"<b>{row.get('name', 'Police Station')}</b>").add_to(m)

# Safe Escape Routes (CYAN)
safe_routes = [
    [[5.116, 7.355], [5.105, 7.370]],
    [[5.100, 7.380], [5.110, 7.360]],
]
for route in safe_routes:
    folium.PolyLine(route, color="cyan", weight=10, opacity=0.9,
                    popup="Recommended Escape Route").add_to(m)
    folium.RegularPolygonMarker(location=route[-1], fill_color="cyan", number_of_sides=3,
                                rotation=30, radius=12).add_to(m)

# Criminal Escape Routes (PURPLE — to be blocked)
criminal_routes = [
    [[5.095, 7.375], [5.080, 7.390]],
    [[5.120, 7.350], [5.140, 7.330]],
]
for route in criminal_routes:
    folium.PolyLine(route, color="purple", weight=8, opacity=0.9, dash_array='10 10',
                    popup="Criminal Escape Route — Deploy Checkpoint").add_to(m)

# YOUR EXACT LEGEND — WORD FOR WORD
legend_html = '''
<div style="position: fixed; bottom: 30px; left: 30px; width: 320px; height: 250px; 
     background-color: white; border:3px solid #2c3e50; z-index:9999; font-size:15px; 
     padding: 15px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
 <h4 style="margin:0 0 12px 0; text-align:center; color:#2c3e50;"><b>MAP LEGEND</b></h4>
 <hr style="border:1px solid #ddd; margin:10px 0;">
 <p><i style="background:red; width:22px; height:22px; float:left; margin:8px 8px 8px 0; opacity:0.7;"></i><b>Red</b> — High-Risk Crime Hotspot</p>
 <p><i style="background:orange; width:22px; height:22px; float:left; margin:8px 8px 8px 0; opacity:0.7;"></i><b>Orange</b> — Medium-Risk Zone</p>
 <p><i style="background:lime; width:22px; height:22px; float:left; margin:8px 8px 8px 0; opacity:0.7;"></i><b>Lime Green</b> — Low-Risk Area</p>
 <p><i style="background:darkblue; border-radius:50%; width:22px; height:22px; float:left; margin:8px 8px 8px 0;"></i><b>Blue Circle</b> — Police Station</p>
 <p><i style="background:cyan; width:45px; height:8px; float:left; margin:10px 8px 8px 0;"></i><b>Cyan Line</b> — Recommended Escape Route</p>
 <p><i style="background:purple; width:45px; height:8px; float:left; margin:10px 8px 8px 0; border:2px dashed purple;"></i><b>Purple Line</b> — Criminal Escape Route (Block!)</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Prediction
if 'pred' in st.session_state:
    d = st.session_state.pred
    mul = 1.0
    if d.weekday() == 0: mul *= 3.0
    if d.month in [5,6,7,8,9,10]: mul *= 1.7
    if d.day >= 25: mul *= 1.5
    mul = min(mul, 5.0)
    base = [10, 8, 12, 7, 9, 8, 7, 10]
    pred = [int(b * mul) for b in base]
    
    st.success(f"PREDICTION: {d.strftime('%A, %B %d, %Y')} — Risk ×{mul:.1f}")
    high = [f"{names[i]} ({pred[i]})" for i, p in enumerate(pred) if p >= 30]
    if high:
        st.error("HIGH ALERT: " + " | ".join(high))
        for i, c in enumerate(pred):
            if c >= 30:
                folium.Circle([centers[i][0], centers[i][1]], radius=1400, color="#8B0000", weight=10, fill=False).add_to(m)

# Show map
st_folium(m, width=1200, height=720, key=f"map_{st.session_state.get('pred', 'base')}")

st.caption("Live • Tactical • Professional • Built by Team Udo)
