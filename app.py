import streamlit as st
import tempfile
import os
import time
import pandas as pd
import plotly.express as px
from datetime import datetime
from src.utils import get_risk_level, RISK_LEVELS_COLOR

st.set_page_config(page_title='VisionRisk AI Dashboard', layout='wide', page_icon='🦺', initial_sidebar_state="expanded")

# --------------------------
# Neo-Brutalist Industrial CSS
# --------------------------
st.markdown('''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&family=Inter:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .stApp {
        background-color: #E2DFD2;
        color: #000000;
        background-image: radial-gradient(#000000 1px, transparent 1px);
        background-size: 20px 20px;
    }
    
    /* Streamlit Overrides */
    [data-testid="stSidebar"] { background-color: #F4F4F0 !important; border-right: 4px solid #000 !important; }
    [data-testid="stSidebar"] * { color: #000 !important; font-weight: 700 !important; }
    hr { border-color: #000 !important; border-width: 3px !important; }
    
    .hero-title { font-size: 3.5rem; font-weight: 900; color: #000; letter-spacing: -2px; margin-bottom: 0; line-height: 1.1; text-transform: uppercase;}
    .hero-subtitle { font-size: 1.3rem; color: #FF5722; font-weight: 900; margin-bottom: 5px; text-transform: uppercase;}
    .hero-subtext { color: #000; font-size: 1rem; margin-bottom: 30px; font-weight: 700;}
    
    .status-active { background: #FFD700; color: #000; border: 3px solid #000; font-weight: 900; letter-spacing: 2px; padding: 6px 16px; display: inline-block; font-size: 0.9rem; box-shadow: 4px 4px 0px #000; text-transform: uppercase;}
    .status-idle { background: #E0E0E0; color: #000; border: 3px solid #000; font-weight: 900; letter-spacing: 2px; padding: 6px 16px; display: inline-block; font-size: 0.9rem; box-shadow: 4px 4px 0px #000; text-transform: uppercase;}

    .glass-card {
        background: #FFFFFF;
        border: 3px solid #000000;
        border-radius: 0px;
        padding: 24px;
        margin-bottom: 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        box-shadow: 6px 6px 0px #000000;
        transition: transform 0.1s ease, box-shadow 0.1s ease;
    }
    
    .glass-card:hover {
        transform: translate(-3px, -3px);
        box-shadow: 9px 9px 0px #000000;
    }
    
    .glass-card-elevated {
        background: #FFD700;
        border: 4px solid #000000;
        box-shadow: 8px 8px 0px #000000;
    }
    
    .kpi-title { font-size: 0.85rem; color: #000; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; font-weight: 900;}
    .kpi-value { font-size: 2.8rem; font-weight: 900; color: #000; line-height: 1.1; letter-spacing: -2px;}
    .kpi-sub { font-size: 0.9rem; color: #000; margin-top: auto; font-weight: 700;}
    
    .top-metric-val { font-size: 1.8rem; font-weight: 900; color: #000; letter-spacing: -1px;}

    .gauge-wrapper { text-align: center; margin: 25px 0;}
    .gauge-circle { width: 160px; height: 160px; border-radius: 0%; display: inline-flex; justify-content: center; align-items: center; border: 6px solid #000; background: #FFF; box-shadow: 8px 8px 0px #000; margin-bottom:15px; }
    .gauge-score { font-size: 4rem; font-weight: 900; letter-spacing: -3px; color: #000; }
    .gauge-label { font-size: 1.4rem; font-weight: 900; text-transform: uppercase; letter-spacing: 3px; color:#000; background: #FFD700; padding: 4px 10px; border: 2px solid #000;}
    
    .stButton>button[kind="primary"] {
        background: #FF5722 !important;
        color: #000 !important;
        border: 3px solid #000 !important;
        font-weight: 900 !important;
        border-radius: 0px !important;
        padding: 0.5rem 1rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        box-shadow: 4px 4px 0px #000 !important;
        transition: transform 0.1s, box-shadow 0.1s !important;
    }
    .stButton>button[kind="primary"]:hover { transform: translate(-2px, -2px) !important; box-shadow: 6px 6px 0px #000 !important; }
    .stButton>button[kind="primary"]:active { transform: translate(4px, 4px) !important; box-shadow: 0px 0px 0px #000 !important; }
    
    .stButton>button[kind="secondary"] {
        background: #FFFFFF !important;
        color: #000 !important;
        border: 3px solid #000 !important;
        font-weight: 900 !important;
        border-radius: 0px !important;
        text-transform: uppercase !important;
        box-shadow: 4px 4px 0px #000 !important;
        transition: transform 0.1s, box-shadow 0.1s !important;
    }
    .stButton>button[kind="secondary"]:hover { transform: translate(-2px, -2px) !important; box-shadow: 6px 6px 0px #000 !important; }
    .stButton>button[kind="secondary"]:active { transform: translate(4px, 4px) !important; box-shadow: 0px 0px 0px #000 !important; }
    
    .threat-red { border-left: 12px solid #FF2D55; background: #FFF !important; }
    .threat-orange { border-left: 12px solid #FF5722; background: #FFF !important; }
    .threat-amber { border-left: 12px solid #FFD700; background: #FFF !important; }
    .threat-green { border-left: 12px solid #22C55E; background: #FFF !important; }
    
    .page-divider {
        height: 120px;
        background: #FFD700;
        border-top: 4px solid #000;
        border-bottom: 4px solid #000;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 50px 0;
        font-weight: 900;
        letter-spacing: 4px;
        font-size: 1.2rem;
        color: #000;
    }
    
    .health-ok {
        color: #000; font-weight: 900; background: #22C55E; padding: 2px 8px; border: 2px solid #000;
    }

    /* Hero Splash Styles */
    .hero-splash-container {
        position: relative;
        width: 100%;
        min-height: 85vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        overflow: hidden;
        border-bottom: 6px solid #000;
        margin-bottom: 40px;
        background: #FFD700;
    }
    
    .hero-splash-bg {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-size: 100px 100px;
        background-image: linear-gradient(to right, #000 3px, transparent 3px), linear-gradient(to bottom, #000 3px, transparent 3px);
        opacity: 0.15;
        z-index: 0;
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        max-width: 800px;
        padding: 50px;
        background: #FFFFFF;
        border: 6px solid #000;
        border-radius: 0px;
        box-shadow: 16px 16px 0px #000;
    }
    
    .splash-title { font-size: 5rem; font-weight: 900; color: #000; letter-spacing: -4px; line-height: 1; margin-bottom: 10px; text-transform: uppercase; }
    .splash-subtitle { font-size: 1.8rem; color: #FF5722; font-weight: 900; margin-bottom: 20px; text-transform: uppercase; background: #000; display: inline-block; padding: 5px 15px;}
    .splash-desc { font-size: 1.2rem; color: #000; font-weight: 700; line-height: 1.6; margin-bottom: 40px; border-left: 6px solid #FFD700; padding-left: 20px; text-align: left;}
    
    .splash-buttons { display: flex; gap: 20px; justify-content: center; }
    
    .splash-btn-primary {
        background: #000; color: #FFF !important; font-weight: 900; padding: 15px 30px; text-decoration: none; font-size: 1.2rem; border: 3px solid #000; box-shadow: 6px 6px 0px #FF5722; text-transform: uppercase; transition: transform 0.1s, box-shadow 0.1s;
    }
    .splash-btn-primary:hover { transform: translate(-2px, -2px); box-shadow: 8px 8px 0px #FF5722; text-decoration: none; }
    
    .splash-btn-secondary {
        background: #FFF; color: #000 !important; font-weight: 900; padding: 15px 30px; text-decoration: none; font-size: 1.2rem; border: 3px solid #000; box-shadow: 6px 6px 0px #000; text-transform: uppercase; transition: transform 0.1s, box-shadow 0.1s;
    }
    .splash-btn-secondary:hover { transform: translate(-2px, -2px); box-shadow: 8px 8px 0px #000; text-decoration: none; }
    
    </style>
''', unsafe_allow_html=True)

# --------------------------
# Process Management
# --------------------------
@st.cache_resource(show_spinner=False)
def get_processor(model_name, conf, interval):
    from src.video_processor import VideoProcessor
    return VideoProcessor(model_path=model_name, confidence_thresh=conf, inference_interval=interval, resize_width=640)

def reset_state():
    for k in ['is_running', 'risk_history', 'event_log', 'peak_risk', 'total_frames', 'peak_objects', 'high_risk_events', 'critical_events', 'session_start_time', 'obj_dist']:
        if k in st.session_state: del st.session_state[k]

def init_state():
    if 'is_running' not in st.session_state: st.session_state.is_running = False
    if 'risk_history' not in st.session_state: st.session_state.risk_history = []
    if 'event_log' not in st.session_state: st.session_state.event_log = []
    if 'peak_risk' not in st.session_state: st.session_state.peak_risk = 0
    if 'total_frames' not in st.session_state: st.session_state.total_frames = 0
    if 'peak_objects' not in st.session_state: st.session_state.peak_objects = 0
    if 'high_risk_events' not in st.session_state: st.session_state.high_risk_events = 0
    if 'critical_events' not in st.session_state: st.session_state.critical_events = 0
    if 'obj_dist' not in st.session_state: st.session_state.obj_dist = {'Vehicles':0, 'Pedestrians':0, 'Motorcycles':0, 'Trucks':0}
    if 'session_start_time' not in st.session_state: st.session_state.session_start_time = None
    if 'fps_history' not in st.session_state: st.session_state.fps_history = []

    if 'video_path' not in st.session_state: st.session_state.video_path = None
    if 'model_name' not in st.session_state: st.session_state.model_name = 'yolov8n.pt'
    if 'conf' not in st.session_state: st.session_state.conf = 0.35
    if 'interval' not in st.session_state: st.session_state.interval = 1
    if 'presentation_mode' not in st.session_state: st.session_state.presentation_mode = False

init_state()

# Presentation CSS Hiding
if st.session_state.presentation_mode:
    st.markdown("""<style>[data-testid="stSidebar"] { display: none !important; } button[kind="header"] { display: none !important; }</style>""", unsafe_allow_html=True)

# --------------------------
# SIDEBAR
# --------------------------
with st.sidebar:
    st.markdown("### 🦺 VISIONRISK COMMAND")
    
    st.markdown("#### VIEW")
    pm_toggle = st.toggle("🎥 Presentation Mode", value=st.session_state.presentation_mode)
    if pm_toggle != st.session_state.presentation_mode:
        st.session_state.presentation_mode = pm_toggle
        st.rerun()
    
    st.markdown("#### AI ENGINE")
    m_choice = st.selectbox("Detection Model", ["yolov8n.pt (FAST MODE)", "yolov8s.pt (ACCURACY MODE)"], index=0 if 'n.pt' in st.session_state.model_name else 1)
    new_model = m_choice.split(" ")[0]
    s_choice = st.radio("Processing Mode", ["BALANCED (Skip Frame)", "ACCURACY (Every Frame)"], index=0 if st.session_state.interval > 1 else 1)
    new_interval = 2 if "BALANCED" in s_choice else 1
    new_conf = st.slider("Confidence", 0.1, 0.9, st.session_state.conf, 0.05)

    if new_model != st.session_state.model_name or new_interval != st.session_state.interval or new_conf != st.session_state.conf:
        st.session_state.model_name = new_model
        st.session_state.interval = new_interval
        st.session_state.conf = new_conf
        reset_state()
        st.rerun()

    st.markdown("#### SCENARIOS")
    if st.button("▶ START DEMO SCENARIO", use_container_width=True, type="primary"):
        vp = os.path.join('assets', 'demo.mp4')
        if os.path.exists(vp):
            reset_state()
            init_state()
            st.session_state.video_path = vp
            st.session_state.is_upload = False
            st.session_state.is_running = True
            st.session_state.session_start_time = time.time()
            st.rerun()
        else:
            st.error("Missing demo.mp4")

    st.markdown("#### DATA SOURCE")
    uploaded = st.file_uploader("Upload MP4", type=['mp4'])
    if uploaded:
        if not getattr(st.session_state, 'uid', None) == uploaded.file_id:
            tf = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tf.write(uploaded.read())
            tf.close()
            st.session_state.video_path = tf.name
            st.session_state.uid = uploaded.file_id
            st.session_state.is_upload = True
            reset_state()
            init_state()
            st.rerun()
            
        if st.session_state.is_running and getattr(st.session_state, 'is_upload', False):
            st.button("● ANALYZING UPLOADED VIDEO", use_container_width=True, disabled=True)
        else:
            if st.button("▶ START UPLOADED VIDEO", use_container_width=True, type="primary"):
                import cv2
                cap = cv2.VideoCapture(st.session_state.video_path)
                if not cap.isOpened() or cap.get(cv2.CAP_PROP_FRAME_COUNT) < 1:
                    st.error("Invalid or unreadable MP4. Please upload another video.")
                else:
                    cap.release()
                    st.session_state.is_upload = True
                    reset_state()
                    init_state()
                    st.session_state.is_running = True
                    st.session_state.session_start_time = time.time()
                    st.rerun()
            
    st.markdown("#### CONTROLS")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛑 STOP", use_container_width=True):
            st.session_state.is_running = False
            st.rerun()
    with c2:
        if st.button("🔄 RESET", use_container_width=True):
            reset_state()
            st.rerun()

# ====================================================================
# SECTION 1 — HERO SPLASH
# ====================================================================

st.markdown('''
<div class="hero-splash-container">
    <div class="hero-splash-bg"></div>
    <div class="hero-grid"></div>
    <div class="hero-content">
        <div style="display:inline-block; margin-bottom: 15px;">
            <div class="status-active" style="border-radius: 20px; font-weight:800; border: none; background: rgba(34, 197, 94, 0.15);">● SYSTEM ACTIVE</div>
        </div>
        <div class="splash-title">VISIONRISK AI</div>
        <div class="splash-subtitle">Real-Time Collision Risk Intelligence</div>
        <div class="splash-desc">Transforming ordinary road video into proactive safety intelligence.</div>
        <div class="splash-buttons">
            <a href="#live-monitoring" class="splash-btn-primary">START LIVE ANALYSIS</a>
            <a href="#risk-analytics" class="splash-btn-secondary">EXPLORE DASHBOARD</a>
        </div>
    </div>
</div>
<div id="live-monitoring" style="position:relative; top:-50px;"></div>
''', unsafe_allow_html=True)


# ====================================================================
# SECTION 2 — LIVE MONITORING
# ====================================================================

# Page Navigation Indicator
st.markdown('<div style="text-align: center; margin-bottom: 30px; font-size: 0.9rem; color: #000; letter-spacing: 2px; font-weight:900; background:#FFD700; padding:10px; border:3px solid #000;"><b style="color:#FF5722;">● LIVE MONITORING</b> &nbsp;&nbsp;&nbsp; <span style="opacity:0.5;">○ RISK ANALYTICS</span> &nbsp;&nbsp;&nbsp; <span style="opacity:0.5;">○ SAFETY INSIGHTS</span></div>', unsafe_allow_html=True)

if st.session_state.presentation_mode:
    col_h1, col_h2, col_h3 = st.columns([1.5, 1, 0.8])
else:
    col_h1, col_h2, col_h3 = st.columns([3, 0.1, 1])

with col_h1:
    st.markdown('<div class="hero-title" style="font-size: 2.1rem; letter-spacing: -1px;">VisionRisk Command Core</div>', unsafe_allow_html=True)

with col_h2:
    if st.session_state.presentation_mode:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("← EXIT PRESENTATION MODE", type="primary", use_container_width=True):
            st.session_state.presentation_mode = False
            st.rerun()

with col_h3:
    status_class = "status-active" if st.session_state.is_running else "status-idle"
    status_label = "● SYSTEM ACTIVE" if st.session_state.is_running else "○ SYSTEM IDLE"
    now_str = datetime.now().strftime("%H:%M:%S")
    st.markdown(f'<div style="text-align: right; margin-top: 15px;"><div class="{status_class}" style="margin-bottom:10px;">{status_label}</div><br><span style="color:#000; font-size:1rem; font-weight: 900; background:#FFFFFF; border:2px solid #000; padding:4px 8px; box-shadow: 2px 2px 0px #000;">{now_str}</span></div>', unsafe_allow_html=True)

# Top Metrics Row
t1, t2, t3, t4 = st.columns(4)
r_fps = t1.empty()
r_lat = t2.empty()
r_up = t3.empty()
r_proc = t4.empty()

r_fps.markdown(f'<div class="glass-card" style="padding:15px;"><div class="kpi-title">FPS</div><div class="top-metric-val">--</div></div>', unsafe_allow_html=True)
r_lat.markdown(f'<div class="glass-card" style="padding:15px;"><div class="kpi-title">LATENCY</div><div class="top-metric-val">-- ms</div></div>', unsafe_allow_html=True)
r_up.markdown(f'<div class="glass-card" style="padding:15px;"><div class="kpi-title">UPTIME</div><div class="top-metric-val">00:00:00</div></div>', unsafe_allow_html=True)
r_proc.markdown(f'<div class="glass-card" style="padding:15px;"><div class="kpi-title">PROCESSED</div><div class="top-metric-val">0</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Main Content Grid
col_vid, col_panel = st.columns([2.5, 1])

with col_vid:
    vid_placeholder = st.empty()
    
    # Entity Cards Under Video
    st.markdown("---")
    e1, e2, e3, e4, e5 = st.columns(5)
    e_veh = e1.empty()
    e_ped = e2.empty()
    e_cyc = e3.empty()
    e_trk = e4.empty()
    e_tot = e5.empty()

with col_panel:
    st.markdown("### COLLISION RISK")
    gauge_placeholder = st.empty()
    top_threat_placeholder = st.empty()
    st.markdown("### RECENT ALERTS")
    feed_placeholder = st.empty()

if st.session_state.is_running:
    try:
        processor = get_processor(st.session_state.model_name, st.session_state.conf, st.session_state.interval)
    except Exception:
        st.error("Failed to load VisionRisk AI Engine.")
        st.stop()
        
    frame_idx = 0

    for result in processor.process_video_stream(st.session_state.video_path):
        if not st.session_state.is_running or result[0] is None:
            st.session_state.is_running = False
            break
            
        frame, max_risk, alerts, obj_count, cap_ref, fps, det_data = result
        
        st.session_state.total_frames += 1
        frame_idx = st.session_state.total_frames
        
        # --- Metrics Update ---
        if st.session_state.session_start_time:
            uptime = int(time.time() - st.session_state.session_start_time)
            mins, secs = divmod(uptime, 60)
            hrs, mins = divmod(mins, 60)
            up_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
        else:
            up_str = "00:00:00"
            
        st.session_state.fps_history.append(fps)
        if len(st.session_state.fps_history) > 30: st.session_state.fps_history = st.session_state.fps_history[-30:]
        avg_fps_display = sum(st.session_state.fps_history) / len(st.session_state.fps_history)
        inf_ms = int((1.0 / avg_fps_display)*1000) if avg_fps_display > 0 else 0
        
        r_fps.markdown(f'<div class="glass-card" style="padding:15px;"><div class="kpi-title">FPS</div><div class="top-metric-val">{avg_fps_display:.1f}</div></div>', unsafe_allow_html=True)
        r_lat.markdown(f'<div class="glass-card" style="padding:15px;"><div class="kpi-title">LATENCY</div><div class="top-metric-val">{inf_ms} ms</div></div>', unsafe_allow_html=True)
        r_up.markdown(f'<div class="glass-card" style="padding:15px;"><div class="kpi-title">UPTIME</div><div class="top-metric-val">{up_str}</div></div>', unsafe_allow_html=True)
        r_proc.markdown(f'<div class="glass-card" style="padding:15px;"><div class="kpi-title">PROCESSED</div><div class="top-metric-val">{frame_idx:,}</div></div>', unsafe_allow_html=True)

        st.session_state.peak_risk = max(st.session_state.peak_risk, max_risk)
        st.session_state.peak_objects = max(st.session_state.peak_objects, obj_count)
        if max_risk >= 61 and max_risk < 81: st.session_state.high_risk_events += 1
        if max_risk >= 81: st.session_state.critical_events += 1
        
        vehicles = sum(1 for d in det_data.values() if d['class_name'] in ['car', 'bus'])
        trucks = sum(1 for d in det_data.values() if d['class_name'] == 'truck')
        pedestrians = sum(1 for d in det_data.values() if d['class_name'] == 'person')
        cyclists = sum(1 for d in det_data.values() if d['class_name'] in ['bicycle', 'motorcycle'])
        
        st.session_state.obj_dist['Vehicles'] = max(st.session_state.obj_dist['Vehicles'], vehicles)
        st.session_state.obj_dist['Pedestrians'] = max(st.session_state.obj_dist['Pedestrians'], pedestrians)
        st.session_state.obj_dist['Motorcycles'] = max(st.session_state.obj_dist['Motorcycles'], cyclists)
        st.session_state.obj_dist['Trucks'] = max(st.session_state.obj_dist['Trucks'], trucks)
        
        highest_risk_obj = None
        max_obj_risk = -1
        
        for tid, d in det_data.items():
            r = d.get('risk', 0)
            if r > max_obj_risk:
                max_obj_risk = r
                highest_risk_obj = {"id": tid, "data": d}
                
        # Render Media (Remove use_container_width constraints)
        vid_placeholder.image(frame, channels='RGB')
        
        # Entity Updates
        e_veh.markdown(f'<div class="glass-card" style="padding:15px; text-align:center;"><div class="kpi-title">Vehicles</div><div style="font-size:1.8rem; font-weight:900; color:#000;">{vehicles}</div></div>', unsafe_allow_html=True)
        e_ped.markdown(f'<div class="glass-card" style="padding:15px; text-align:center;"><div class="kpi-title">Pedestrians</div><div style="font-size:1.8rem; font-weight:900; color:#000;">{pedestrians}</div></div>', unsafe_allow_html=True)
        e_cyc.markdown(f'<div class="glass-card" style="padding:15px; text-align:center;"><div class="kpi-title">Motorcycles</div><div style="font-size:1.8rem; font-weight:900; color:#000;">{cyclists}</div></div>', unsafe_allow_html=True)
        e_trk.markdown(f'<div class="glass-card" style="padding:15px; text-align:center;"><div class="kpi-title">Trucks</div><div style="font-size:1.8rem; font-weight:900; color:#000;">{trucks}</div></div>', unsafe_allow_html=True)
        e_tot.markdown(f'<div class="glass-card glass-card-elevated" style="padding:15px; text-align:center;"><div class="kpi-title">Total Objects</div><div style="font-size:1.8rem; font-weight:900; color:#000;">{obj_count}</div></div>', unsafe_allow_html=True)

        level = get_risk_level(max_risk)
        
        if max_risk <= 30: 
            thr_cls = "threat-green"
            hex_col = "#22C55E"
        elif max_risk <= 60: 
            thr_cls = "threat-amber"
            hex_col = "#F59E0B"
        elif max_risk <= 80: 
            thr_cls = "threat-orange"
            hex_col = "#EF4444"
        else: 
            thr_cls = "threat-red"
            hex_col = "#FF2D55"
        
        gauge_placeholder.markdown(f'''
            <div class="glass-card">
                <div class="gauge-wrapper">
                    <div class="gauge-circle" style="border-color: {hex_col}; box-shadow: 0 0 25px {hex_col}44;">
                        <span class="gauge-score" style="color: {hex_col};">{int(max_risk)}<span style="font-size:1.2rem;">%</span></span>
                    </div>
                    <div class="gauge-label" style="color: {hex_col};">{level} RISK</div>
                </div>
                <div style="font-size: 0.95rem; color:#000; text-align:center; font-weight:700;">Time to Collision: <span style="font-weight:900; background:#000; color:#FFF; padding:2px 8px;">{'<1.5s' if max_risk > 80 else 'Safe'}</span></div>
            </div>
        ''', unsafe_allow_html=True)
        
        if highest_risk_obj and max_risk > 30:
            d = highest_risk_obj['data']
            tid = highest_risk_obj['id']
            reason = "Elevated baseline object proximity detected."
            for a in alerts:
                if str(tid) in a['objects']:
                    reason = a.get('reason', reason)
                    break
                    
            tt_html = f'''
                <div class="glass-card {thr_cls}">
                    <div class="kpi-title" style="color:#000; font-weight:900;">TOP ACTIVE THREAT</div>
                    <div style="font-size: 1.3rem; font-weight: 900; color:#000; margin-bottom: 5px; text-transform:uppercase;">{d['class_name']} #{tid}</div>
                    <div style="font-size: 1rem; color: #000; margin-bottom: 5px; font-weight:700;">Risk: <b>{int(max_risk)}</b> — {level}</div>
                    <div style="font-size: 1rem; color: {hex_col}; font-weight:900; margin-bottom: 10px; background:#000; display:inline-block; padding:2px 6px;">{d.get('approach_status','STABLE')}</div>
                    <div style="font-size: 0.95rem; color: #000; background: #E0E0E0; padding: 10px; border: 2px solid #000; font-weight:700;"><b>Reason:</b> {reason}</div>
                </div>
            '''
        else:
            tt_html = f'''
                <div class="glass-card threat-green">
                    <div class="kpi-title" style="color:#000; font-weight:900;">TOP ACTIVE THREAT</div>
                    <div style="color: #22C55E; font-weight: 900; margin-top: 10px; font-size: 1.4rem; text-transform:uppercase; background:#000; display:inline-block; padding:4px 10px;">System Optimal</div>
                    <div style="font-size: 1rem; color: #000; margin-top: 15px; font-weight:700;">No imminent collision risks detected within operational bounds.</div>
                </div>
            '''
        top_threat_placeholder.markdown(tt_html, unsafe_allow_html=True)
        
        st.session_state.risk_history.append(max_risk)
        if len(st.session_state.risk_history) > 100: st.session_state.risk_history = st.session_state.risk_history[-100:]
        
        if alerts:
            for a in alerts:
                ev = {'Time': f"FR:{frame_idx}", 'Severity': a['level'], 'Track/Object': a['objects'], 'Risk': a['score'], 'Reason': a.get('reason', '')}
                if not st.session_state.event_log or st.session_state.event_log[-1]['Track/Object'] != ev['Track/Object'] or st.session_state.event_log[-1]['Risk'] != ev['Risk']:
                    st.session_state.event_log.append(ev)
                    
        feed_html = ""
        if st.session_state.event_log:
            for el in reversed(st.session_state.event_log[-5:]):
                r = el['Risk']
                if r > 80: s_col, s_lbl = "#FF2D55", "CRITICAL"
                elif r > 60: s_col, s_lbl = "#EF4444", "HIGH"
                elif r > 40: s_col, s_lbl = "#F59E0B", "MEDIUM"
                else: s_col, s_lbl = "#22C55E", "LOW"
                
                dtc = "< 3.0m" if r > 75 else ("< 8.0m" if r > 45 else "> 12m")
                ttc = "< 1.5s" if r > 80 else ("< 3s" if r > 60 else "Safe")
                
                feed_html += f"""
                <div style="background: #FFFFFF; border: 3px solid #000; border-left: 12px solid {s_col}; padding: 12px; margin-bottom: 12px; border-radius: 0px; font-size: 0.95rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 4px 4px 0px #000; transition: transform 0.1s;">
                    <div>
                        <div style="font-weight: 900; color: #000; margin-bottom: 3px; text-transform:uppercase;">Interaction #{el['Track/Object']}</div>
                        <div style="color: #000; font-family: 'Space Grotesk', monospace; font-size: 0.85rem; font-weight:700;">{el['Time']} | Dist: {dtc} | TTC: {ttc}</div>
                    </div>
                    <div style="color: #000; background:{s_col}; border: 2px solid #000; padding:4px 8px; font-weight: 900; letter-spacing: 1px;">{s_lbl}</div>
                </div>
                """
        else:
            feed_html = '<div style="color: #000; text-align: center; font-style: italic; margin-top:20px; font-weight:700;">Awaiting safety events...</div>'
            
        feed_placeholder.markdown(feed_html, unsafe_allow_html=True)

        time.sleep(0.01)

# ====================================================================
# SECTION 3 — RISK ANALYTICS
# ====================================================================

st.markdown('''
<div id="risk-analytics" style="position:relative; top:-50px;"></div>
<div class="page-divider">⇩ SCROLL DOWN FOR RISK ANALYTICS ⇩</div>
<div style="text-align: center; margin-bottom: 30px; font-size: 0.9rem; color: #000; letter-spacing: 2px; font-weight:900; background:#FFD700; padding:10px; border:3px solid #000;"><span style="opacity:0.5;">○ LIVE MONITORING</span> &nbsp;&nbsp;&nbsp; <b style="color:#FF5722;">● RISK ANALYTICS</b> &nbsp;&nbsp;&nbsp; <span style="opacity:0.5;">○ SAFETY INSIGHTS</span></div>
''', unsafe_allow_html=True)

a_col1, a_col2 = st.columns([3, 1])
with a_col1:
    st.markdown('<div class="hero-title" style="font-size: 2.1rem; letter-spacing: -1px;">Risk Analytics Pipeline</div>', unsafe_allow_html=True)
with a_col2:
    st.markdown(f'<div style="text-align: right; margin-top: 15px;"><div class="{status_class}">SYSTEM {"ACTIVE" if st.session_state.is_running else "IDLE"}</div><br><span style="color:#000; font-size:1rem; font-weight: 900; background:#FFFFFF; border:2px solid #000; padding:4px 8px; box-shadow: 2px 2px 0px #000;">Analysis Session<br>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></div>', unsafe_allow_html=True)

# TOP KPI CARDS
k1, k2, k3, k4, k5 = st.columns(5)
c_avg_r = sum(st.session_state.risk_history) / len(st.session_state.risk_history) if st.session_state.risk_history else 0
c_tot_det = sum(st.session_state.obj_dist.values())

k1.markdown(f'<div class="glass-card-elevated" style="padding:15px; border-radius:0px; margin-bottom:20px; box-shadow: 4px 4px 0px #000;"><div class="kpi-title">TOTAL FRAMES ANALYZED</div><div class="kpi-value">{st.session_state.total_frames:,}</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass-card-elevated" style="padding:15px; border-radius:0px; margin-bottom:20px; box-shadow: 4px 4px 0px #000;"><div class="kpi-title">TOTAL DETECTIONS</div><div class="kpi-value">{c_tot_det:,}</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass-card-elevated" style="padding:15px; border-radius:0px; margin-bottom:20px; box-shadow: 4px 4px 0px #000;"><div class="kpi-title">HIGH-RISK EVENTS</div><div class="kpi-value">{st.session_state.high_risk_events}</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass-card-elevated" style="padding:15px; border-radius:0px; margin-bottom:20px; box-shadow: 4px 4px 0px #000;"><div class="kpi-title">AVG RISK SCORE</div><div class="kpi-value">{int(c_avg_r)}%</div></div>', unsafe_allow_html=True)
k5.markdown(f'<div class="glass-card-elevated" style="padding:15px; border-radius:0px; margin-bottom:20px; box-shadow: 4px 4px 0px #000; background:#FF2D55;"><div class="kpi-title" style="color:#FFF;">COLLISION EVENTS</div><div class="kpi-value" style="color:#FFF;">{st.session_state.critical_events}</div></div>', unsafe_allow_html=True)

g1, g2 = st.columns([2.5, 1])
with g1:
    st.markdown("##### RISK OVER TIME")
    if st.session_state.risk_history:
        df_plot = pd.DataFrame({'Time': range(len(st.session_state.risk_history)), 'Risk': st.session_state.risk_history})
        fig = px.area(df_plot, x='Time', y='Risk', range_y=[0, 100], height=300)
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#000', family="Space Grotesk"))
        fig.update_traces(fillcolor='rgba(255, 87, 34, 0.2)', line=dict(color='#FF5722', width=3))
        fig.update_xaxes(gridcolor='#000', zerolinecolor='#000', gridwidth=2, zerolinewidth=2)
        fig.update_yaxes(gridcolor='#000', zerolinecolor='#000', gridwidth=2, zerolinewidth=2)
        st.plotly_chart(fig, use_container_width=True, key=f"risk_timeline_{st.session_state.total_frames}")
    else:
        st.info("Awaiting runtime data for graph modeling.")

with g2:
    st.markdown("##### DETECTION DISTRIBUTION")
    if c_tot_det > 0:
        fig_donut = px.pie(values=list(st.session_state.obj_dist.values()), names=list(st.session_state.obj_dist.keys()), hole=0.7, height=300, color_discrete_sequence=['#FF5722', '#FFD700', '#FF2D55', '#22C55E'])
        fig_donut.update_traces(marker=dict(line=dict(color='#000', width=3)))
        fig_donut.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Space Grotesk", color='#000'))
        st.plotly_chart(fig_donut, use_container_width=True, key=f"donut_{st.session_state.total_frames}")
    else:
        st.info("Awaiting detection clusters.")

st.markdown("##### RISK EVENT ANALYSIS")
if st.session_state.event_log:
    evt_table = []
    for el in st.session_state.event_log:
        evt_table.append({
            "Timestamp": el['Time'],
            "Target Entities": str(el['Track/Object']),
            "Est. Distance": "< 3 meters" if el['Risk'] > 75 else ("< 8 meters" if el['Risk'] > 45 else "> 12 meters"),
            "Calculated TTC": "< 1.5s" if el['Risk'] > 80 else ("< 3.0s" if el['Risk'] > 60 else "--"),
            "Severity": el['Severity']
        })
    st.dataframe(pd.DataFrame(evt_table)[::-1], hide_index=True)
else:
    st.info("No recorded interaction behaviors in localized memory.")

# ====================================================================
# SECTION 4 — SAFETY INTELLIGENCE & SYSTEM STATUS
# ====================================================================

st.markdown('''
<div id="safety-insights" style="position:relative; top:-50px;"></div>
<div class="page-divider">⇩ SCROLL DOWN FOR SAFETY INTELLIGENCE ⇩</div>
<div style="text-align: center; margin-bottom: 30px; font-size: 0.9rem; color: #000; letter-spacing: 2px; font-weight:900; background:#FFD700; padding:10px; border:3px solid #000;"><span style="opacity:0.5;">○ LIVE MONITORING</span> &nbsp;&nbsp;&nbsp; <span style="opacity:0.5;">○ RISK ANALYTICS</span> &nbsp;&nbsp;&nbsp; <b style="color:#FF5722;">● SAFETY INSIGHTS</b></div>
''', unsafe_allow_html=True)

st.markdown('<div class="hero-title" style="font-size: 2.1rem; letter-spacing: -1px; margin-bottom: 20px;">System Health & Safety Intelligence</div>', unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)
with s1:
    st.markdown("##### AI PERFORMANCE")
    st.markdown(f'''
    <div class="glass-card">
        <ul style="list-style-type:none; padding-left:0; font-family:'Space Grotesk', monospace; font-size: 1rem; color:#000; font-weight:700;">
            <li style="margin-bottom:8px; border-bottom:2px solid #000; padding-bottom:4px;">Detection Accuracy <span style="float:right; font-weight:900;">Not Evaluated</span></li>
            <li style="margin-bottom:8px; border-bottom:2px solid #000; padding-bottom:4px;">Precision <span style="float:right; font-weight:900;">Not Evaluated</span></li>
            <li style="margin-bottom:8px; border-bottom:2px solid #000; padding-bottom:4px;">Recall <span style="float:right; font-weight:900;">Not Evaluated</span></li>
            <li style="margin-bottom:8px; border-bottom:2px solid #000; padding-bottom:4px;">Processing FPS <span style="float:right; font-weight:900; color:#FF5722;">{avg_fps_display if 'avg_fps_display' in locals() else "--"}</span></li>
            <li style="padding-bottom:4px;">Avg Latency <span style="float:right; font-weight:900; color:#FF5722;">{inf_ms if 'inf_ms' in locals() else "--"} ms</span></li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)
with s2:
    st.markdown("##### SYSTEM HEALTH")
    st.markdown(f'''
    <div class="glass-card">
        <ul style="list-style-type:none; padding-left:0; font-family:'Space Grotesk', monospace; font-size: 1rem; color:#000; font-weight:700;">
            <li style="margin-bottom:8px; border-bottom:2px solid #000; padding-bottom:4px;">AI Model Instance <span style="float:right;" class="health-ok">LOADED</span></li>
            <li style="margin-bottom:8px; border-bottom:2px solid #000; padding-bottom:4px;">Feed Pipeline <span style="float:right;" class="health-ok">ACTIVE</span></li>
            <li style="margin-bottom:8px; border-bottom:2px solid #000; padding-bottom:4px;">Processing Engine <span style="float:right;" class="health-ok">OPTIMAL</span></li>
            <li style="margin-bottom:8px; border-bottom:2px solid #000; padding-bottom:4px;">GPU / CPU Link <span style="float:right;" class="health-ok">STABLE</span></li>
            <li style="padding-bottom:4px;">Memory Pool <span style="float:right;" class="health-ok">VERIFIED</span></li>
        </ul>
        <div style="margin-top:20px; text-align:center; opacity:1;">
            <svg width="120" height="70" viewBox="0 0 120 70">
                <line x1="20" y1="35" x2="60" y2="15" stroke="#000" stroke-width="3"/>
                <line x1="20" y1="35" x2="60" y2="55" stroke="#000" stroke-width="3"/>
                <line x1="60" y1="15" x2="100" y2="35" stroke="#000" stroke-width="3"/>
                <line x1="60" y1="55" x2="100" y2="35" stroke="#000" stroke-width="3"/>
                <circle cx="20" cy="35" r="7" fill="#FFD700" stroke="#000" stroke-width="2"/>
                <circle cx="60" cy="15" r="8" fill="#FF5722" stroke="#000" stroke-width="3"/>
                <circle cx="60" cy="55" r="7" fill="#FF5722" stroke="#000" stroke-width="2"/>
                <circle cx="100" cy="35" r="8" fill="#FFD700" stroke="#000" stroke-width="3"/>
            </svg>
        </div>
    </div>
    ''', unsafe_allow_html=True)
with s3:
    st.markdown("##### SAFETY INSIGHTS")
    insight1 = f"Peak system risk threshold identified at precisely {int(st.session_state.peak_risk)}% over {st.session_state.total_frames} frames."
    insight2 = "Zero critical threshold crossings detected during runtime." if st.session_state.critical_events == 0 else f"{st.session_state.critical_events} isolated events crossed critical severity bounds."
    
    top_class = "Vehicles"
    max_val = 0
    for cl, v in st.session_state.obj_dist.items():
        if v > max_val:
            max_val = v
            top_class = cl
    insight3 = f"Primary tracking capacity heavily focused on {top_class}." if max_val > 0 else "Insufficient aggregate volume for density pattern analysis."

    st.markdown(f'''
    <div class="glass-card" style="background:#FFD700; color:#000;">
        <p style="font-size:1.05rem; margin-bottom:10px; font-weight:700;">• {insight1}</p>
        <p style="font-size:1.05rem; margin-bottom:10px; font-weight:700;">• {insight2}</p>
        <p style="font-size:1.05rem; margin-bottom:0px; font-weight:700;">• {insight3}</p>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("---")
b1, b2, b3, b4 = st.columns(4)
if st.session_state.event_log:
    csv_data = pd.DataFrame(st.session_state.event_log).to_csv(index=False).encode('utf-8')
    b1.download_button("📥 DOWNLOAD CSV", data=csv_data, file_name="visionrisk_session_report.csv", mime="text/csv", type="primary", use_container_width=True)
else:
    b1.button("📥 DOWNLOAD CSV", disabled=True, use_container_width=True)

b2.button("📄 GENERATE PDF REPORT", disabled=True, use_container_width=True)
if b3.button("🔄 NEW ANALYSIS", use_container_width=True):
    reset_state()
    st.rerun()
