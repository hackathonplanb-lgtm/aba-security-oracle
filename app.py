import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from sklearn.cluster import KMeans

# WIDE LAYOUT + CLASSY ANIMATIONS
st.set_page_config(page_title="Aba Security Oracle", layout="wide", initial_sidebar_state="expanded")

# CUSTOM CSS — GLOWING LEGEND + ANIMATIONS + WIDE SIDEBAR
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
    
    section[data-testid="stSidebar"] {width: 440px !important;}
    
    .title-animation {
        animation: fadeInDown 1.5s ease-out;
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        background: linear-gradient(90deg, #8B0000, #FF4500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    @keyframes fadeInDown {
        0% {opacity: 0; transform: translateY(-50px);}
        100% {opacity: 1; transform: translateY(0);}
    }
    
    @keyframes fadeInUp {
        0% {opacity: 0; transform: translateY(50px);}
        100% {opacity: 1; transform: translateY(0);}
    }
    
    .map-container {animation: fadeInUp 2s ease-out;}
    
    /* GLOWING LEGEND ON HOVER/CLICK */
    .legend-glow {
        transition: all 0.5s ease;
        cursor: pointer;
    }
    .legend-glow:hover {
        box-shadow: 0 0 30px #FFFF00, 0 0 60px #FFD700 !important;
        transform: scale(1.02);
        border: 5px solid #FFD700 !important;
    }
</style>
""", unsafe_allow_html=True)

# TITLE WITH ANIMATION
st.markdown('<h1 class="title-animation">ABA SECURITY ORACLE</h1>', unsafe_allow_html=True)
st.markdown("**Built by: Team Udo (resilience-lgtm) – Deep Funding Hackathon 2025**")
st.markdown("**Advanced Predictive Policing • AI Tactical Command System**")

# Load data
incidents = pd.read_csv("incidents.csv")
police = pd.read_csv("police.csv")

# SIDEBAR — WIDE & CLEAN
with st.sidebar:
    st.header("AI Tactical Assistant")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Commander, I am ready. What is your order?"}]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ask about deployment, routes, or threat level..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        prompt_l = prompt.lower()
        resp = "Analyzing..."
        if any(x in prompt_l for x in ["monday", "tomorrow", "risk"]):
            resp = "HIGH THREAT on Monday/month-end. Deploy 40+ officers to Osisioma & Ariaria by 0500. Block all purple routes."
        elif "safe" in prompt_l or "escape" in prompt_l:
            resp = "Use the RED lines — they are the only safe escape corridors. Protect them at all costs."
        else:
            resp = "Ask: safest route • deployment plan • hotspot status • prediction"
        st.session_state.messages.append({"role": "assistant", "content": resp})
        with st.chat_message("assistant"): st.markdown(resp)

    st.divider()
    predict_date = st.date_input("Select date:", datetime.now() + timedelta(days=1))
    if st.button("GENERATE TACTICAL BRIEF", type="primary", use_container_width=True):
        st.session_state.pred = predict_date

# MAP
m = folium.Map(location=[5.107, 7.369], zoom_start=13, tiles="CartoDB positron")

# Individual incidents
for _, row in incidents.iterrows():
    folium.CircleMarker([row.lat, row.lon], radius=6, color="#8B0000", fill=True, fillOpacity=0.7).add_to(m)

# Hotspots
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
                        popup=f"<b>{row.get('name','Police Station')}</b>").add_to(m)

# Safe Routes — RED
for route in [[[5.116,7.355],[5.105,7.370]], [[5.100,7.380],[5.110,7.360]]]:
    folium.PolyLine(route, color="red", weight=16, opacity=1).add_to(m)
    folium.RegularPolygonMarker(location=route[-1], fill_color="red", number_of_sides=3, rotation=30, radius=18).add_to(m)

# Criminal Routes — PURPLE
for route in [[[5.095,7.375],[5.080,7.390]], [[5.120,7.350],[5.140,7.330]]]:
    folium.PolyLine(route, color="purple", weight=12, opacity=0.9, dash_array='20 20').add_to(m)

# FINAL PERFECT LEGEND — TALLER, SPACED, RED TEXT ONLY, GLOW ON HOVER
legend_html = '''
<div class="legend-glow" style="position: fixed; bottom: 40px; left: 40px; width: 440px; height: 380px; 
     background: linear-gradient(145deg, #ffffff, #f0f0f0); border:5px solid #8B0000; 
     border-radius: 20px; z-index:9999; font-size:18px; padding: 28px; 
     box-shadow: 0 10px 30px rgba(0,0,0,0.5); line-height: 2.4; font-weight: bold;">
 <h4 style="margin:0 0 20px 0; text-align:center; color:#8B0000; font-size:22px;">MAP LEGEND</h4>
 <hr style="border:2px solid #8B0000; margin:18px 0;">
 <p style="color:red; margin:12px 0;"><i style="background:red; width:30px; height:30px; float:left; margin-right:20px; opacity:0.8; border-radius:50%;"></i>Red Circle — High-Risk Crime Hotspot</p>
 <p style="color:red; margin:12px 0;"><i style="background:orange; width:30px; height:30px; float:left; margin-right:20px; opacity:0.8; border-radius:50%;"></i>Orange Circle — Medium-Risk Zone</p>
 <p style="color:red; margin:12px 0;"><i style="background:lime; width:30px; height:30px; float:left; margin-right:20px; opacity:0.8; border-radius:50%;"></i>Lime Circle — Low-Risk Area</p>
 <p style="color:red; margin:12px 0;"><i style="background:darkblue; width:30px; height:30px; float:left; margin-right:20px; border-radius:50%;"></i>Blue Circle — Police Station</p>
 <p style="color:red; margin:18px 0;"><i style="background:red; width:90px; height:16px; float:left; margin-right:20px;"></i>Red Line — Recommended Safe Escape Route</p>
 <p style="color:red; margin:18px 0;"><i style="background:purple; width:90px; height:14px; float:left; margin-right:20px; border:3px dashed purple;"></i>Purple Line — Criminal Escape Route (BLOCK!)</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# PREDICTION
if 'pred' in st.session_state:
    d = st.session_state.pred
    mul = min(5.0, (1.0 + (d.weekday()==0)*2 + (d.month in [5,6,7,8,9,10])*0.7 + (d.day>=25)*0.5)*3)
    base = [10,8,12,7,9,8,7,10]
    pred = [int(b * mul) for b in base]
    
    st.success(f"TACTICAL BRIEF: {d.strftime('%A, %B %d, %Y')} — THREAT ×{mul:.1f}")
    high = [f"{names[i]} ({pred[i]})" for i, p in enumerate(pred) if p >= 30]
    if high:
        st.error("HIGH ALERT: " + " | ".join(high))
        st.warning("• Deploy 40+ officers to red zones\n• Block all purple routes\n• Protect red escape corridors")
        for i, c in enumerate(pred):
            if c >= 30:
                folium.Circle([centers[i][0], centers[i][1]], radius=1800, color="#8B0000", weight=16, fill=False).add_to(m)

# MAP WITH ANIMATION
st.markdown('<div class="map-container">', unsafe_allow_html=True)
st_folium(m, width=1450, height=820, key=f"glow_map_{hash(str(st.session_state.get('pred', '')))}")
st.markdown('</div>', unsafe_allow_html=True)

st.caption("Live • AI-Powered • Tactical • Built by Team Udo — Securing Aba Tomorrow")
