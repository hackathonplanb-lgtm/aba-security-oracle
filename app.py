import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from sklearn.cluster import KMeans

# --------------------- PAGE CONFIG ---------------------
st.set_page_config(page_title="Aba Security Oracle", layout="wide", initial_sidebar_state="expanded")

# --------------------- TITLE & CREDIT ---------------------
st.title("ABA SECURITY ORACLE")
st.markdown("**Built by: Team Udo (resilience-lgtm) – Deep Funding Hackathon 2025**")
st.markdown("**Advanced Predictive Policing & AI Tactical Assistant**")

# --------------------- LOAD DATA ---------------------
incidents = pd.read_csv("incidents.csv")
police = pd.read_csv("police.csv")

# --------------------- SIDEBAR: AI CHAT + PREDICTION ---------------------
with st.sidebar:
    st.header("AI Tactical Assistant")
    
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # User input
    if prompt := st.chat_input("Ask anything about crime in Aba..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Simple but powerful AI response (you can later connect to Grok/Claude if you want)
        prompt = prompt.lower()
        response = "No response yet"
        
        if any(x in prompt for x in ["tomorrow", "next", "predict", "monday"]):
            response = "Tomorrow (especially if Monday + month-end) → **HIGH RISK** in Osisioma, Ariaria & Ekeoha. Deploy 30+ officers by 5AM and block purple routes."
        elif "safe route" in prompt or "escape" in prompt:
            response = "Use the **RED lines** on the map — they are the safest escape routes for civilians and VIPs."
        elif "dangerous" in prompt or "hotspot" in prompt:
            response = "Current top 3 hotspots: **Osisioma**, **Ariaria**, **Ngwa Road**. Avoid purple dashed lines — those are criminal escape paths."
        elif "police" in prompt or "station" in prompt:
            response = "Blue circles = Police stations. Nearest to Ariaria is Aba Central Division."
        else:
            response = "I am the Aba Security Oracle AI. Ask me about hotspots, escape routes, predictions, or deployment plans."
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

    st.divider()
    st.subheader("Generate Prediction")
    predict_date = st.date_input("Select date:", datetime.now() + timedelta(days=1))
    if st.button("GENERATE TACTICAL BRIEF", type="primary", use_container_width=True):
        st.session_state.pred = predict_date

# --------------------- MAP ---------------------
m = folium.Map(location=[5.107, 7.369], zoom_start=13, tiles="CartoDB positron")

# SPREAD OUT INCIDENTS (no clustering!)
for _, row in incidents.iterrows():
    folium.CircleMarker(
        location=[row.lat, row.lon],
        radius=5,
        color="crimson",
        fill=True,
        fillOpacity=0.7,
        popup=f"Incident on {row.get('date', 'N/A')}"
    ).add_to(m)

# Hotspots (still keep the 8 big circles)
kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
clusters = kmeans.fit_predict(incidents[['lat','lon']])
centers = kmeans.cluster_centers_
names = ["Ariaria", "Ngwa Road", "Osisioma", "Ogbor Hill", "Ekeoha", "Asa Road", "Faulks Road", "Port Harcourt Rd"]

for i, (lat, lon) in enumerate(centers):
    count = sum(clusters == i)
    color = "red" if count > 20 else "orange" if count > 10 else "lime"
    folium.Circle([lat, lon], radius=900, color=color, weight=4, fill=True, fillOpacity=0.35,
                  popup=f"<b>{names[i]}</b><br>Incidents: {count}").add_to(m)

# Police Stations
for _, row in police.iterrows():
    folium.CircleMarker([row.lat, row.lon], radius=12, color="darkblue", fill=True,
                        popup=f"<b>{row.get('name', 'Police Station')}</b>").add_to(m)

# SAFE ESCAPE ROUTES — RED
safe_routes = [[[5.116, 7.355], [5.105, 7.370]], [[5.100, 7.380], [5.110, 7.360]]]
for route in safe_routes:
    folium.PolyLine(route, color="red", weight=14, opacity=0.98,
                    popup="SAFE ESCAPE ROUTE — PROTECT").add_to(m)
    folium.RegularPolygonMarker(location=route[-1], fill_color="red", number_of_sides=3, rotation=30, radius=16).add_to(m)

# CRIMINAL ESCAPE ROUTES — PURPLE DASHED
criminal_routes = [[[5.095, 7.375], [5.080, 7.390]], [[5.120, 7.350], [5.140, 7.330]]]
for route in criminal_routes:
    folium.PolyLine(route, color="purple", weight=10, opacity=0.9, dash_array='15 15',
                    popup="CRIMINAL ROUTE — BLOCK!").add_to(m)

# BIGGER, BEAUTIFUL LEGEND
legend_html = '''
<div style="position: fixed; bottom: 30px; left: 30px; width: 380px; height: 300px; 
     background-color: white; border:4px solid #8B0000; z-index:9999; font-size:16px; 
     padding: 20px; border-radius: 15px; box-shadow: 0 6px 20px rgba(0,0,0,0.4);">
 <h4 style="margin:0 0 15px 0; text-align:center; color:#8B0000;"><b>MAP LEGEND</b></h4>
 <hr style="border:1.5px solid #8B0000; margin:12px 0;">
 <p style="color:red; font-weight:bold; margin:8px 0;"><i style="background:red; width:24px; height:24px; float:left; margin-right:12px; opacity:0.7;"></i>Red Circle — High-Risk Crime Hotspot</p>
 <p style="color:orange; font-weight:bold; margin:8px 0;"><i style="background:orange; width:24px; height:24px; float:left; margin-right:12px; opacity:0.7;"></i>Orange Circle — Medium-Risk Zone</p>
 <p style="color:green; font-weight:bold; margin:8px 0;"><i style="background:lime; width:24px; height:24px; float:left; margin-right:12px; opacity:0.7;"></i>Lime Circle — Low-Risk Area</p>
 <p style="color:blue; font-weight:bold; margin:8px 0;"><i style="background:darkblue; border-radius:50%; width:24px; height:24px; float:left; margin-right:12px;"></i>Blue Circle — Police Station</p>
 <p style="color:red; font-weight:bold; margin:10px 0;"><i style="background:red; width:60px; height:12px; float:left; margin-right:12px;"></i>Red Line — Recommended Safe Escape Route</p>
 <p style="color:purple; font-weight:bold; margin:10px 0;"><i style="background:purple; width:60px; height:10px; float:left; margin-right:12px; border:2px dashed purple;"></i>Purple Line — Criminal Escape Route (BLOCK!)</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# PREDICTION + RECOMMENDATIONS
if 'pred' in st.session_state:
    d = st.session_state.pred
    mul = 1.0
    if d.weekday() == 0: mul *= 3.0
    if d.month in [5,6,7,8,9,10]: mul *= 1.7
    if d.day >= 25: mul *= 1.5
    mul = min(mul, 5.0)
    base = [10, 8, 12, 7, 9, 8, 7, 10]
    pred = [int(b * mul) for b in base]
    
    st.success(f"TACTICAL BRIEF: {d.strftime('%A, %B %d, %Y')} — Threat Level ×{mul:.1f}")
    high = [f"{names[i]} ({pred[i]})" for i, p in enumerate(pred) if p >= 30]
    if high:
        st.error("HIGH ALERT ZONES: " + " | ".join(high))
        st.warning("DEPLOYMENT ORDERS:\n• 30–50 officers to high-risk zones by 05:00\n• Full checkpoint on purple routes\n• Protect all red escape routes")
        for i, c in enumerate(pred):
            if c >= 30:
                folium.Circle([centers[i][0], centers[i][1]], radius=1600, color="#8B0000", weight=14, fill=False).add_to(m)

# --------------------- DISPLAY MAP ---------------------
st_folium(m, width=1200, height=750, key=f"map_{hash(str(st.session_state.get('pred', '')))}")

st.caption("Live • AI-Powered • Tactical • Built by Team Udo — The Future of Security in Aba")
