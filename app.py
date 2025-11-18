import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
import numpy as np
import requests # Needed for real-time LLM API calls

# --- CONFIGURATION AND SETUP ---

# WIDE LAYOUT + FUTURISTIC ANIMATIONS
st.set_page_config(
    page_title="Aba Security Oracle | Tactical AI Command",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
GEMINI_API_KEY = "" # <<-- PASTE YOUR GEMINI API KEY HERE -->>
GEMINI_MODEL = "gemini-2.5-flash-preview-09-2025"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
SYSTEM_INSTRUCTION = (
    "You are 'Aba Oracle', a highly advanced Tactical AI Assistant for the Aba Security Command. "
    "Your persona is authoritative, precise, and focused on proactive security measures. "
    "Use real-time data or grounded search results to inform your tactical advice. "
    "Responses must be concise (max 3 sentences) and action-oriented. "
    "Focus on deployment, threat levels, specific locations, and route safety. "
    "Always maintain a military/command tone."
)

# CUSTOM CSS — CYBER-TACTICAL THEME
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap');
    
    /* Global Dark Theme */
    [data-testid="stAppViewContainer"] {
        background: #0D1117; /* Dark Slate Blue/Black */
        color: #00FFD1;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        width: 440px !important;
        background-color: #1a1e28;
        border-right: 2px solid #00BFFF;
        box-shadow: 5px 0 20px rgba(0, 191, 255, 0.2);
    }
    
    /* Header Animation */
    .title-animation {
        animation: neon-glow 1.5s ease-out infinite alternate;
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        text-shadow: 0 0 10px #FF4500, 0 0 20px #8B0000;
        color: #FF4500;
    }
    @keyframes neon-glow {
        from {text-shadow: 0 0 5px #FF4500, 0 0 10px #8B0000;}
        to {text-shadow: 0 0 15px #FFD700, 0 0 30px #FF4500;}
    }

    /* Custom KPI Cards (Glassmorphism/HUD Effect) */
    .oracle-kpi {
        background: rgba(33, 37, 43, 0.6);
        padding: 15px 25px;
        border-radius: 12px;
        border: 1px solid rgba(0, 191, 255, 0.4);
        box-shadow: 0 0 15px rgba(0, 191, 255, 0.3);
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .kpi-title {
        color: #00BFFF;
        font-size: 1.1rem;
        font-weight: 500;
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00FFD1; /* Neon Teal */
        text-shadow: 0 0 5px #00FFD1;
    }

    /* Enhanced Map Legend Styling (Glow on Hover) */
    .legend-glow {
        transition: all 0.5s ease;
        cursor: pointer;
        background: rgba(33, 37, 43, 0.9) !important;
        border: 2px solid #8B0000 !important;
        box-shadow: 0 0 25px #FF4500;
        color: #F0F0F0;
    }
    .legend-glow:hover {
        box-shadow: 0 0 40px #FFFF00, 0 0 80px #FFD700 !important;
        transform: scale(1.01);
        border: 5px solid #FFD700 !important;
    }
    .legend-glow p {
        color: #F0F0F0 !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: #8B0000;
        border: none;
        color: white;
        border-radius: 8px;
        font-family: 'Orbitron', sans-serif;
        box-shadow: 0 0 10px #FF4500;
    }
</style>
""", unsafe_allow_html=True)

# --- UTILITY FUNCTIONS ---

def get_kpi_html(title, value, color="#00FFD1"):
    """Generates custom HTML for KPI cards."""
    return f"""
    <div class="oracle-kpi">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value" style="color: {color}; text-shadow: 0 0 8px {color};">{value}</div>
    </div>
    """

def generate_ai_response(prompt):
    """
    Handles communication with the Gemini API for tactical advice.
    
    This function is structured to show the necessary API payload for 
    Grounding (Google Search) and System Instructions.
    """
    if not GEMINI_API_KEY:
        # Fallback for demonstration when API Key is missing
        prompt_l = prompt.lower()
        if any(x in prompt_l for x in ["monday", "tomorrow", "risk"]):
            return "ANALYSIS (SIMULATED): HIGH THREAT on projected target date. Deploy 40+ officers to Osisioma & Ariaria by 0500 hours. Block all Purple routes. Awaiting live data feed."
        elif "safest" in prompt_l or "escape" in prompt_l:
            return "ANALYSIS (SIMULATED): Execute tactical retreat via RED lines only. These are designated secure corridors. All other routes are unverified. Threat level: MODERATE."
        elif "police" in prompt_l or "station" in prompt_l:
            return f"ANALYSIS (SIMULATED): {len(st.session_state.police_data)} current police deployment points. Nearest HIGH-RISK hotspot: Ariaria. Status: Alert."
        else:
            return "ORACLE STATUS: Standby. Commander, query too vague. Provide specific request regarding deployment, threat status, or real-time security intelligence. (Note: Integrate your Gemini API Key for live-data capability.)"

    try:
        # 1. Construct the API Payload for grounded generation
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "tools": [{"google_search": {}}], # Enable Google Search Grounding
            "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        }

        # 2. Make the API request (using exponential backoff is recommended in production)
        response = requests.post(
            GEMINI_API_URL,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=15 # Set a reasonable timeout
        )
        response.raise_for_status() # Raise an exception for bad status codes
        
        result = response.json()
        candidate = result.candidates[0]
        
        if candidate and candidate.content and candidate.content.parts and candidate.content.parts[0].text:
            text = candidate.content.parts[0].text
            # 3. Extract and display sources (citations) if available
            sources = []
            grounding_metadata = candidate.groundingMetadata
            if grounding_metadata and grounding_metadata.groundingAttributions:
                sources = grounding_metadata.groundingAttributions
                source_links = "\n\n**Sources:** " + " | ".join(
                    [f"[{i+1}]({attr.get('web', {}).get('uri', '#')})" 
                     for i, attr in enumerate(sources)]
                )
                return text + source_links
            
            return text
        
        return "ERROR: Oracle experienced a data processing failure. Retrying..."

    except requests.exceptions.RequestException as e:
        return f"CRITICAL FAILURE: Network error or API misconfiguration. Check console logs. Error: {e}"
    except Exception as e:
        return f"ANALYSIS ERROR: Unhandled exception in LLM processing. Error: {e}"

# --- DATA LOADING AND INITIAL PROCESSING ---

@st.cache_data
def load_data():
    """Loads incident and police data."""
    try:
        # Assuming these files are available in the running directory
        incidents = pd.read_csv("incidents.csv")
        police = pd.read_csv("police.csv")
        return incidents, police
    except FileNotFoundError:
        st.error("CRITICAL: Data files (incidents.csv, police.csv) not found. Using dummy data.")
        # Generate robust dummy data if files are missing
        np.random.seed(42)
        incidents = pd.DataFrame({
            'lat': np.random.uniform(5.08, 5.14, 100),
            'lon': np.random.uniform(7.33, 7.40, 100),
            'type': np.random.choice(['Robbery', 'Vandalism', 'Assault'], 100)
        })
        police = pd.DataFrame({
            'lat': np.random.uniform(5.08, 5.14, 5),
            'lon': np.random.uniform(7.33, 7.40, 5),
            'name': [f'Station {i+1}' for i in range(5)]
        })
        return incidents, police

incidents, police = load_data()
st.session_state.police_data = police # Store for use in LLM query

# --- MAIN DASHBOARD LAYOUT ---

# TITLE WITH ANIMATION
st.markdown('<h1 class="title-animation">ABA SECURITY ORACLE</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="color:#00BFFF; text-align:center; font-family:Orbitron;">AI-Powered Tactical Command System</h3>', unsafe_allow_html=True)

# 1. SIDEBAR — AI TACTICAL ASSISTANT
with st.sidebar:
    st.header("AI TACTICAL ASSISTANT")
    st.markdown("---")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Oracle Online. Commander, state your query for immediate tactical assessment."}]
    
    # Display chat messages
    chat_container = st.container(height=400, border=False)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # Chat input logic
    if prompt := st.chat_input("Ask about deployment, routes, or global threat level..."):
        # 1. Display User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"): st.markdown(prompt)

        # 2. Get AI Response
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("TRANSMITTING... ORACLE IS COMPUTING. Estimated latency 5s."):
                    resp = generate_ai_response(prompt)
                st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})

    st.markdown("---")
    
    # Prediction Control
    predict_date = st.date_input(
        "PREDICTION TARGET DATE", 
        datetime.now() + timedelta(days=1),
        min_value=datetime.now()
    )
    if st.button("GENERATE TACTICAL BRIEF", type="primary", use_container_width=True):
        st.session_state.pred = predict_date
        st.experimental_rerun() # Rerun to update the main page based on the session state change


# 2. MAIN TABS (Map & Metrics)
tab1, tab2 = st.tabs(["[1] TACTICAL MAP DISPLAY", "[2] PREDICTIVE METRICS & ANALYSIS"])

with tab2:
    st.subheader("PREDICTIVE ANALYSIS CONSOLE")
    
    if 'pred' in st.session_state:
        d = st.session_state.pred
        
        # Simple Prediction Logic (based on day of week and month-end)
        mul = min(6.0, (1.0 + (d.weekday()==0)*2 + (d.month in [5,6,7,8,9,10])*0.8 + (d.day>=25)*0.6)*3)
        base = [10, 8, 12, 7, 9, 8, 7, 10]
        pred = [int(b * mul) for b in base]
        
        total_incidents = sum(pred)
        high_risk_zones = sum(1 for p in pred if p >= 30)
        
        # Display KPIs in 3 columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(get_kpi_html(
                "TARGET DATE THREAT LEVEL", 
                f"x{mul:.1f}", 
                color="#FF4500" if mul >= 4.0 else "#FFD700"
            ), unsafe_allow_html=True)
            
        with col2:
            st.markdown(get_kpi_html(
                "PREDICTED INCIDENTS", 
                f"{total_incidents}", 
                color="#FFD700"
            ), unsafe_allow_html=True)

        with col3:
            st.markdown(get_kpi_html(
                "HIGH-RISK ZONES", 
                f"{high_risk_zones} / 8", 
                color="#8B0000" if high_risk_zones >= 3 else "#00FFD1"
            ), unsafe_allow_html=True)

        st.subheader(f"ZONE BREAKDOWN for: {d.strftime('%A, %B %d, %Y')}")
        
        # Display detailed prediction table
        kmeans_data = incidents[['lat', 'lon']]
        kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
        kmeans.fit(kmeans_data)
        centers = kmeans.cluster_centers_
        names = ["Ariaria", "Ngwa Road", "Osisioma", "Ogbor Hill", "Ekeoha", "Asa Road", "Faulks Road", "Port Harcourt Rd"]

        
        prediction_df = pd.DataFrame({
            'Hotspot': names,
            'Predicted Incidents': pred,
            'Risk Level': [
                'CRITICAL' if p >= 40 else 'HIGH' if p >= 30 else 'MEDIUM' if p >= 15 else 'LOW' 
                for p in pred
            ],
            'Tactical Recommendation': [
                'Full Containment & Patrol' if p >= 30 else 'Increased Surveillance' if p >= 15 else 'Standard Patrol'
                for p in pred
            ]
        })
        
        # Custom styling for the DataFrame
        def color_risk(val):
            if val == 'CRITICAL': return 'background-color: #8B0000; color: white'
            if val == 'HIGH': return 'background-color: #FF4500; color: black'
            if val == 'MEDIUM': return 'background-color: #FFD700; color: black'
            return 'background-color: #008000; color: white'

        st.dataframe(
            prediction_df.style.applymap(color_risk, subset=['Risk Level']),
            use_container_width=True,
            hide_index=True
        )
        
    else:
        st.info("Execute 'GENERATE TACTICAL BRIEF' in the sidebar to run predictive models for a future date.")

with tab1:
    # --- MAP GENERATION ---
    st.subheader("REAL-TIME GEOSPATIAL THREAT VISUALIZATION")
    
    # Initialize Map
    m = folium.Map(
        location=[5.107, 7.369], 
        zoom_start=13, 
        tiles="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
        attr='CartoDB DarkMatter'
    )
    
    # K-Means Hotspots (Re-run K-Means for consistency with Tab 2)
    kmeans_data = incidents[['lat', 'lon']]
    kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(kmeans_data)
    centers = kmeans.cluster_centers_
    names = ["Ariaria", "Ngwa Road", "Osisioma", "Ogbor Hill", "Ekeoha", "Asa Road", "Faulks Road", "Port Harcourt Rd"]
    
    # Hotspot Circles based on current incident count
    for i, (lat, lon) in enumerate(centers):
        count = sum(clusters == i)
        
        # Current Risk Color Logic
        if count > 25: color, glow = "red", "#FF4500"
        elif count > 15: color, glow = "orange", "#FFD700"
        else: color, glow = "lime", "#00FF00"
        
        folium.Circle([lat, lon], 
                      radius=count * 30 + 300, # Size proportional to incidents
                      color=color, 
                      weight=4, 
                      fill=True, 
                      fillOpacity=0.25,
                      popup=f"<b>{names[i]}</b><br>Incidents: {count}").add_to(m)

    # Individual Police Deployment (Blue Icons)
    for _, row in police.iterrows():
        folium.CircleMarker([row.lat, row.lon], 
                            radius=15, 
                            color="#00BFFF", # Neon Blue
                            weight=3, 
                            fill=True, 
                            fillOpacity=0.8,
                            popup=f"<b>{row.get('name','Police Station')}</b><br>STATUS: ACTIVE").add_to(m)

    # Safe Routes — RED (Tactical Escape Corridors)
    for route in [[[5.116,7.355],[5.105,7.370]], [[5.100,7.380],[5.110,7.360]]]:
        folium.PolyLine(route, color="red", weight=18, opacity=1, tooltip="SECURE CORRIDOR").add_to(m)
        folium.RegularPolygonMarker(location=route[-1], fill_color="#FF4500", number_of_sides=3, rotation=30, radius=20).add_to(m)

    # Criminal Routes — PURPLE (Threat Vectors)
    for route in [[[5.095,7.375],[5.080,7.390]], [[5.120,7.350],[5.140,7.330]]]:
        folium.PolyLine(route, color="purple", weight=14, opacity=0.9, dash_array='20 10', tooltip="THREAT VECTOR - BLOCK").add_to(m)

    # Prediction Overlay (Show larger rings for predicted high risk)
    if 'pred' in st.session_state:
        pred_date = st.session_state.pred
        st.markdown(f'<h4 style="color:#FFD700;">ACTIVE PREDICTION OVERLAY: {pred_date.strftime("%Y-%m-%d")}</h4>', unsafe_allow_html=True)
        
        base_pred = [10, 8, 12, 7, 9, 8, 7, 10]
        mul = min(6.0, (1.0 + (pred_date.weekday()==0)*2 + (pred_date.month in [5,6,7,8,9,10])*0.8 + (pred_date.day>=25)*0.6)*3)
        pred_values = [int(b * mul) for b in base_pred]
        
        for i, c in enumerate(pred_values):
            if c >= 30: # CRITICAL/HIGH risk threshold
                folium.Circle(
                    [centers[i][0], centers[i][1]], 
                    radius=2000, 
                    color="#FF4500", 
                    weight=10, 
                    fill=False,
                    tooltip=f"PREDICTED CRITICAL THREAT: {names[i]} ({c} incidents)"
                ).add_to(m)

    # FINAL LEGEND - Embedded HTML with Glow Styling
    legend_html = '''
    <div class="legend-glow" style="position: fixed; bottom: 40px; left: 40px; width: 440px; height: 450px; 
          border-radius: 20px; z-index:9999; font-size:18px; padding: 28px; 
          line-height: 2.2; font-weight: bold;">
    <h4 style="margin:0 0 20px 0; text-align:center; color:#FF4500; font-size:24px; font-family:Orbitron;">TACTICAL LEGEND</h4>
    <hr style="border:1px solid #FF4500; margin:18px 0;">
    <p style="margin:12px 0;"><i style="background:red; width:30px; height:30px; float:left; margin-right:20px; opacity:0.8; border-radius:50%;"></i>Current High-Risk Cluster</p>
    <p style="margin:12px 0;"><i style="background:orange; width:30px; height:30px; float:left; margin-right:20px; opacity:0.8; border-radius:50%;"></i>Current Medium-Risk Zone</p>
    <p style="margin:12px 0;"><i style="background:lime; width:30px; height:30px; float:left; margin-right:20px; opacity:0.8; border-radius:50%;"></i>Current Low-Risk Zone</p>
    <p style="margin:12px 0;"><i style="background:#00BFFF; width:30px; height:30px; float:left; margin-right:20px; border-radius:50%;"></i>Police Deployment Point</p>
    <hr style="border:1px solid #00BFFF; margin:18px 0;">
    <p style="margin:18px 0;"><i style="background:red; width:90px; height:18px; float:left; margin-right:20px;"></i>Red Line — SECURE ESCAPE CORRIDOR</p>
    <p style="margin:18px 0;"><i style="background:purple; width:90px; height:14px; float:left; margin-right:20px; border:3px dashed purple;"></i>Purple Line — KNOWN THREAT VECTOR (BLOCK!)</p>
    <p style="margin:18px 0; color:#FFD700;"><i style="border: 5px dashed #FF4500; width: 30px; height: 30px; float:left; margin-right: 20px; border-radius: 50%;"></i>Orange Circle — **PREDICTED** Critical Threat</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Render the Map
    st_folium(
        m, 
        width=1500, 
        height=820, 
        key=f"tactical_map_{hash(str(st.session_state.get('pred', '')))}"
    )

st.caption("Aba Security Oracle • Version 2.0 • Live AI Integration • Built by Team Udo – Securing Aba Tomorrow")
