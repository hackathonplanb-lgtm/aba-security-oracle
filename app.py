import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from sklearn.cluster import KMeans

# WIDER SIDEBAR + WIDE LAYOUT
st.set_page_config(
    page_title="Aba Security Oracle",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

# Custom CSS to make sidebar wider and legend text perfectly spaced
st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        width: 420px !important;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("ABA SECURITY ORACLE")
st.markdown("**Built by: Team Udo (resilience-lgtm) – Deep Funding Hackathon 2025**")
st.markdown("**Advanced Predictive Policing & AI Tactical Assistant**")

# Load data
incidents = pd.read_csv("incidents.csv")
police = pd.read_csv("police.csv")

# SIDEBAR — NOW WIDER & CLEAN
with st.sidebar:
    st.header("AI Tactical Assistant")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello Commander. How can I assist you today?"}]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ask about hotspots, routes, or deployment..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        prompt_lower = prompt.lower()
        response = "I am analyzing the situation..."
        
        if any(x in prompt_lower for x in ["tomorrow", "monday", "risk", "predict"]):
            response = "High threat expected on Monday or month-end. Prioritize Osisioma, Ariaria & Ekeoha. Deploy 40+ officers by 0500hrs and block all purple routes."
        elif "safe" in prompt_lower or "escape" in prompt_lower or "route" in prompt_lower:
            response = "Use the RED lines on the map — they are the safest escape routes. Protect them at all costs."
        elif "dangerous" in prompt_lower or "hotspot" in prompt_lower:
            response = "Top 3 danger zones: **Osisioma**, **Ariaria**, **Ngwa Road**. Criminals use purple dashed lines to escape — set checkpoints there."
        else:
            response = "Ask me anything: safest route, deployment plan, hotspot status, or prediction for any date."
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

    st.divider()
    predict_date = st.date_input("Select date for prediction:", datetime.now() + timedelta(days=1))
    if st.button("GENERATE TACTICAL BRIEF", type="primary", use_container_width=True):
        st.session_state.pred = predict_date

# MAP
m = folium.Map(location=[5.107, 7.369], zoom_start=13, tiles="CartoDB positron")

# Spread incidents — no clustering
for _, row in incidents.iterrows():
    folium.CircleMarker(
        location=[row.lat, row.lon],
        radius=6,
        color="#8B0000",
        fill=True,
        fillOpacity=0.7
    ).add_to(m)

# Hotspots — big, clean circles
kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
clusters = kmeans.fit_predict(incidents[['lat','lon']])
centers = kmeans.cluster_centers_
names = ["Ariaria", "Ngwa Road", "Osisioma", "Ogbor Hill", "Ekeoha", "Asa Road", "Faulks Road", "Port Harcourt Rd"]

for i, (lat, lon) in enumerate(centers):
    count = sum(clusters == i)
    color = "red" if count > 20 else "orange" if count > 10 else "lime"
    folium.Circle([lat, lon], radius=900, color=color, weight=4, fill=True, fillOpacity=0.35,
                  popup=f"<b>{names[i]}</b><br>Incidents: {count}").add_to(m)

# Police
for _, row in police.iterrows():
    folium.CircleMarker([row.lat, row.lon], radius=12, color="darkblue", fill=True,
                        popup=f"<b>{row.get('name', 'Police Station')}</b>").add_to(m)

# Safe Routes — RED
safe_routes = [[[5.116, 7.355], [5.105, 7.370]], [[5.100, 7.380], [5.110, 7.360]]]
for route in safe_routes:
    folium.PolyLine(route, color="red", weight=16, opacity=1.0).add_to(m)
    folium.RegularPolygonMarker(location=route[-1], fill_color="red", number_of_sides=3, rotation=30, radius=18).add_to(m)

# Criminal Routes — PURPLE DASHED
criminal_routes = [[[5.095, 7.375], [5.080, 7.390]], [[5.120, 7.350], [5.140, 7.330]]]
for route in criminal_routes:
    folium.PolyLine(route, color="purple", weight=12, opacity=0.9, dash_array='20 20').add_to(m)

# BIGGER, SPACED-OUT, BEAUTIFUL LEGEND
legend_html = '''
<div style="position: fixed; bottom: 40px; left: 40px; width: 420px; height: 340px; 
     background-color: white; border:5px solid #8B0000; z-index:9999; font-size:17px; 
     padding: 25px; border-radius: 18px; box-shadow: 0 8px 25px rgba(0,0,0,0.5); line-height: 2.1; 
     color: red;"> 
 <h4 style="margin:0 0 20px 0; text-align:center; color:#CC0000; font-size:20px;"><b>MAP LEGEND</b></h4>
 <hr style="border:2px solid #8B0000; margin:15px 0;">
 <p style="margin:10px 0;"><i style="background:red; width:28px; height:28px; float:left; margin-right:18px; opacity:0.8;"></i><b>Red Circle</b> — High-Risk Crime Hotspot</p>
 <p style="margin:10px 0;"><i style="background:orange; width:28px; height:28px; float:left; margin-right:18px; opacity:0.8;"></i><b>Orange Circle</b> — Medium-Risk Zone</p>
 <p style="margin:10px 0;"><i style="background:lime; width:28px; height:28px; float:left; margin-right:18px; opacity:0.8;"></i><b>Lime Circle</b> — Low-Risk Area</p>
 <p style="margin:10px 0;"><i style="background:darkblue; border-radius:50%; width:28px; height:28px; float:left; margin-right:18px;"></i><b>Blue Circle</b> — Police Station</p>
 <p style="margin:15px 0;"><i style="background:red; width:80px; height:14px; float:left; margin-right:18px;"></i><b>Red Line</b> — Recommended Safe Escape Route</p>
 <p style="margin:15px 0;"><i style="background:purple; width:80px; height:12px; float:left; margin-right:18px; border:3px dashed purple;"></i><b>Purple Line</b> — Criminal Escape Route (BLOCK!)</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Prediction + Tactical Orders
if 'pred' in st.session_state:
    d = st.session_state.pred
    mul = 1.0
    if d.weekday() == 0: mul *= 3.0
    if d.month in [5,6,7,8,9,10]: mul *= 1.7
    if d.day >= 25: mul *= 1.5
    mul = min(mul, 5.0)
    base = [10, 8, 12, 7, 9, 8, 7, 10]
    pred = [int(b * mul) for b in base]
    
    st.success(f"TACTICAL BRIEF: {d.strftime('%A, %B %d, %Y')} — Threat ×{mul:.1f}")
    high = [f"{names[i]} ({pred[i]})" for i, p in enumerate(pred) if p >= 30]
    if high:
        st.error("HIGH ALERT: " + " | ".join(high))
        st.warning("DEPLOYMENT ORDERS:\n• 40+ officers to red zones by 0500hrs\n• Full roadblocks on purple routes\n• Protect all red escape corridors")
        for i, c in enumerate(pred):
            if c >= 30:
                folium.Circle([centers[i][0], centers[i][1]], radius=1800, color="#8B0000", weight=16, fill=False).add_to(m)

# SHOW MAP
st_folium(m, width=1400, height=800, key=f"map_final_{hash(str(st.session_state.get('pred', '')))}")

st.caption("Live • AI-Powered • Tactical • Built by Team Udo — The Future of Security in Aba")
