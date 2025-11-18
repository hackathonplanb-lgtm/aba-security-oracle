import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
import numpy as np

st.set_page_config(page_title="Aba Security Oracle", layout="wide", initial_sidebar_state="expanded")
st.title("ABA SECURITY ORACLE")
st.markdown("**Built by: Team Udo (resilience) – Deep-Funding-Hackathon**")
st.markdown("**Advanced Predictive Policing & Tactical Response System**")

# Load data
incidents = pd.read_csv("incidents.csv")
police = pd.read_csv("police.csv")

with st.sidebar:
    st.header("Command Center")
    predict_date = st.date_input("Predict for:", datetime.now() + timedelta(days=1))
    if st.button("GENERATE TACTICAL BRIEF", type="primary", use_container_width=True):
        st.session_state.date = predict_date

# Base map
m = folium.Map(location=[5.107, 7.369], zoom_start=13, tiles="CartoDB positron")

# 1. Heatmap + Hotspots
HeatMap(incidents[['lat','lon']].values.tolist(), radius=15).add_to(m)
kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
clusters = kmeans.fit_predict(incidents[['lat','lon']])
centers = kmeans.cluster_centers_
names = ["Ariaria","Ngwa Rd","Osisioma","Ogbor Hill","Ekeoha","Asa Rd","Faulks Rd","P.H. Rd"]

for i, (lat, lon) in enumerate(centers):
    count = sum(clusters == i)
    color = "red" if count > 20 else "orange" if count > 10 else "lime"
    folium.Circle([lat, lon], radius=800, color=color, fill=True, fillOpacity=0.3,
                  popup=f"<b>{names[i]}</b><br>Crimes: {count}").add_to(m)

# 2. Police stations + 2km coverage
for _, r in police.iterrows():
    folium.Circle([r.lat, r.lon], radius=2000, color="blue", weight=2, fill=False,
                  popup=f"<b>{r.get('name','Police')}</b><br>Coverage: 2km").add_to(m)
    folium.CircleMarker([r.lat, r.lon], radius=10, color="darkblue", fill=True,
                        popup=r.get("name","Police")).add_to(m)

# 3. Escape routes (simulated safe paths)
escape_routes = [
    [(5.116, 7.355), (5.105, 7.370)],  # From Osisioma → City center
    [(5.100, 7.380), (5.110, 7.360)],  # Ariaria → Safe zone
]
for route in escape_routes:
    folium.PolyLine(route, color="cyan", weight=6, opacity=0.8,
                    popup="Recommended Escape Route").add_to(m)
    folium.PolyLine(route, color="blue", weight=10, opacity=0.4).add_to(m)

# 4. Legend
legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; width: 200px; background: white; 
            border:2px solid grey; z-index:9999; padding: 10px; border-radius: 10px">
<h4>Legend</h4>
<i style="background:red; width:15px; height:15px; display:inline-block"></i> High Crime<br>
<i style="background:orange"></i> Medium Crime<br>
<i style="background:lime"></i> Low Crime<br>
<i style="background:blue; border-radius:50%"></i> Police Station<br>
<i style="background:cyan; width:20px; height:4px; display:inline-block"></i> Escape Route
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# 5. Prediction + GPT-style summary
if 'date' in st.session_state:
    d = st.session_state.date
    risk = "VERY HIGH" if d.weekday() == 0 and d.day >= 25 else "HIGH" if d.weekday() == 0 else "ELEVATED" if d.month in [5,6,7,8,9,10] else "MODERATE"
    st.error(f"TACTICAL BRIEF — {d.strftime('%A, %B %d')}")
    st.warning(f"**Threat Level:** {risk}")
    st.info("**Recommended Actions:**\n"
            "• Deploy 15–20 officers to Osisioma & Ariaria by 05:00\n"
            "• Set up checkpoints on Ngwa Road & Faulks Road\n"
            "• Use escape routes for VIP movement\n"
            "• Increase night patrol in Ekeoha & Ogbor Hill")

# Show map
st_folium(m, width=1200, height=700, key=f"final_{hash(str(st.session_state.get('date','')))}")

st.success("Live • Tactical • Built with OpenStreetMap • Team Udo Development")
