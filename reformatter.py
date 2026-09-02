import re
import codecs

with codecs.open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update init_state
init_state_new = """def init_state():
    if 'page' not in st.session_state: st.session_state.page = 'home'
    if 'is_running' not in st.session_state: st.session_state.is_running = False"""
content = re.sub(r"def init_state\(\):\n\s*if 'is_running' not in st\.session_state: st\.session_state\.is_running = False", init_state_new, content)

# 2. Add css to completely hide sidebar globally in the CSS block
css_hide = """    /* Hide sidebar and full page */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu {visibility: hidden;}"""
content = content.replace("#MainMenu {visibility: hidden;}", css_hide)

# 3. Restructure everything below init_state()
content = content.split("init_state()\n")[0] + "init_state()\n"

content += """
def go_home():
    st.session_state.page = 'home'
    st.session_state.is_running = False
    reset_state()

def go_command():
    st.session_state.page = 'command'

# ====================================================================
# PAGE ROUTING
# ====================================================================
if st.session_state.page == 'home':
    # Hide sidebar overrides just in case for home page
    st.markdown('''
    <div class="hero-splash-container" style="min-height: 95vh; border:none; margin:0; background:transparent;">
        <div class="hero-splash-bg"></div>
        <div class="hero-content">
            <div style="display:inline-block; margin-bottom: 15px;">
                <div class="status-active" style="border-radius: 20px; font-weight:800; border: none; background: rgba(34, 197, 94, 0.15);">● SYSTEM READY</div>
            </div>
            <div class="splash-title">VISIONRISK AI</div>
            <div class="splash-subtitle" style="box-shadow:none;">Real-Time Collision Risk Intelligence</div>
            <div class="splash-desc" style="display:block; margin-bottom:30px; background:transparent;">Transforming ordinary road video into proactive safety intelligence.</div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.button("⚡ START LIVE ANALYSIS", use_container_width=True, type="primary", on_click=go_command)
        
    st.markdown('''
        </div>
    </div>
    ''', unsafe_allow_html=True)

elif st.session_state.page == 'command':
    st.button("← BACK TO HOME", on_click=go_home, type="secondary")
    st.markdown("<hr style='border:none; border-bottom: 2px dashed #222; margin: 10px 0 30px 0;'>", unsafe_allow_html=True)
    
    # --------------------------
    # CONTROLS PANEL (Full Width)
    # --------------------------
    st.markdown('<div class="hero-title" style="font-size: 2.1rem; letter-spacing: -1px; margin-bottom: 20px;">🦺 VisionRisk Command Core</div>', unsafe_allow_html=True)
    
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
    with ctrl_col1:
        m_choice = st.selectbox("Detection Model", ["yolov8n.pt (FAST MODE)", "yolov8s.pt (ACCURACY MODE)"], index=0 if 'n.pt' in st.session_state.model_name else 1)
        new_model = m_choice.split(" ")[0]
        s_choice = st.radio("Processing Mode", ["BALANCED (Skip Frame)", "ACCURACY (Every Frame)"], index=0 if st.session_state.interval > 1 else 1)
        new_interval = 2 if "BALANCED" in s_choice else 1
    
    with ctrl_col2:
        new_conf = st.slider("Confidence", 0.1, 0.9, st.session_state.conf, 0.05)
        st.markdown("#### ACTIONS")
        act_col1, act_col2 = st.columns(2)
        if act_col1.button("🛑 STOP", use_container_width=True):
            st.session_state.is_running = False
            st.rerun()
        if act_col2.button("🔄 RESET", use_container_width=True):
            reset_state()
            st.rerun()
            
    with ctrl_col3:
        st.markdown("#### SCENARIOS")
        if st.button("▶ START DEMO SCENARIO", use_container_width=True, type="primary"):
            import os, time
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
                
    with ctrl_col4:
        st.markdown("#### DATA SOURCE")
        import tempfile, time
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
                st.button("● ANALYZING...", use_container_width=True, disabled=True)
            else:
                if st.button("▶ START UPLOADS", use_container_width=True, type="primary"):
                    import cv2
                    cap = cv2.VideoCapture(st.session_state.video_path)
                    if not cap.isOpened() or cap.get(cv2.CAP_PROP_FRAME_COUNT) < 1:
                        st.error("Invalid MP4.")
                    else:
                        cap.release()
                        st.session_state.is_upload = True
                        reset_state()
                        init_state()
                        st.session_state.is_running = True
                        st.session_state.session_start_time = time.time()
                        st.rerun()

    if new_model != st.session_state.model_name or new_interval != st.session_state.interval or new_conf != st.session_state.conf:
        st.session_state.model_name = new_model
        st.session_state.interval = new_interval
        st.session_state.conf = new_conf
        reset_state()
        st.rerun()

    st.markdown("---")
    
    # --------------------------
    # LIVE MONITORING (Existing)
    # --------------------------
    
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
        import time
        from datetime import datetime
        from src.utils import get_risk_level
        
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
                    
            vid_placeholder.image(frame, channels='RGB')
            
            e_veh.markdown(f'<div class="glass-card" style="padding:15px; text-align:center;"><div class="kpi-title">Vehicles</div><div style="font-size:1.8rem; font-weight:900; color:#E0E0E0;">{vehicles}</div></div>', unsafe_allow_html=True)
            e_ped.markdown(f'<div class="glass-card" style="padding:15px; text-align:center;"><div class="kpi-title">Pedestrians</div><div style="font-size:1.8rem; font-weight:900; color:#E0E0E0;">{pedestrians}</div></div>', unsafe_allow_html=True)
            e_cyc.markdown(f'<div class="glass-card" style="padding:15px; text-align:center;"><div class="kpi-title">Motorcycles</div><div style="font-size:1.8rem; font-weight:900; color:#E0E0E0;">{cyclists}</div></div>', unsafe_allow_html=True)
            e_trk.markdown(f'<div class="glass-card" style="padding:15px; text-align:center;"><div class="kpi-title">Trucks</div><div style="font-size:1.8rem; font-weight:900; color:#E0E0E0;">{trucks}</div></div>', unsafe_allow_html=True)
            e_tot.markdown(f'<div class="glass-card glass-card-elevated" style="padding:15px; text-align:center;"><div class="kpi-title">Total Objects</div><div style="font-size:1.8rem; font-weight:900; color:#E0E0E0;">{obj_count}</div></div>', unsafe_allow_html=True)

            level = get_risk_level(max_risk)
            
            if max_risk <= 30: 
                thr_cls = "threat-green"
                hex_col = "#00FFD1"
            elif max_risk <= 60: 
                thr_cls = "threat-amber"
                hex_col = "#F5C518"
            elif max_risk <= 80: 
                thr_cls = "threat-orange"
                hex_col = "#FF9500"
            else: 
                thr_cls = "threat-red"
                hex_col = "#FF3B3B"
            
            gauge_placeholder.markdown(f'''
                <div class="glass-card">
                    <div class="gauge-wrapper">
                        <div class="gauge-circle" style="border-color: {hex_col}; box-shadow: 0 0 25px {hex_col}44;">
                            <span class="gauge-score" style="color: {hex_col};">{int(max_risk)}<span style="font-size:1.2rem;">%</span></span>
                        </div>
                        <div class="gauge-label" style="color: {hex_col};">{level} RISK</div>
                    </div>
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
                        <div class="kpi-title" style="color:#00FFD1; font-weight:900;">TOP ACTIVE THREAT</div>
                        <div style="font-size: 1.3rem; font-weight: 900; color:#FFF; margin-bottom: 5px; text-transform:uppercase;">{d['class_name']} #{tid}</div>
                        <div style="font-size: 1rem; color: #E0E0E0; margin-bottom: 5px; font-weight:700;">Risk: <b>{int(max_risk)}</b> — {level}</div>
                        <div style="font-size: 1rem; color: {hex_col}; font-weight:900; margin-bottom: 10px; background:#0A0A0A; display:inline-block; padding:2px 6px; border:1px solid {hex_col};">{d.get('approach_status','STABLE')}</div>
                        <div style="font-size: 0.95rem; color: #FFF; background: #222; padding: 10px; border: 2px solid #333; font-weight:700;"><b>Reason:</b> {reason}</div>
                    </div>
                '''
            else:
                tt_html = f'''
                    <div class="glass-card threat-green">
                        <div class="kpi-title" style="color:#00FFD1; font-weight:900;">TOP ACTIVE THREAT</div>
                        <div style="color: #00FFD1; font-weight: 900; margin-top: 10px; font-size: 1.4rem; text-transform:uppercase; background:#0A0A0A; display:inline-block; padding:4px 10px; border:1px solid #00FFD1;">System Optimal</div>
                        <div style="font-size: 1rem; color: #E0E0E0; margin-top: 15px; font-weight:700;">No imminent collision risks detected within operational bounds.</div>
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
                    if r > 80: s_col, s_lbl = "#FF3B3B", "CRITICAL"
                    elif r > 60: s_col, s_lbl = "#FF9500", "HIGH"
                    elif r > 40: s_col, s_lbl = "#F5C518", "MEDIUM"
                    else: s_col, s_lbl = "#00FFD1", "LOW"
                    
                    dtc = "< 3.0m" if r > 75 else ("< 8.0m" if r > 45 else "> 12m")
                    ttc = "< 1.5s" if r > 80 else ("< 3s" if r > 60 else "Safe")
                    
                    feed_html += f'''
                    <div style="background: #0A0A0A; border: 2px solid #333; border-left: 6px solid {s_col}; padding: 12px; margin-bottom: 12px; font-size: 0.95rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 4px 4px 0px {s_col}; transition: transform 0.1s;">
                        <div>
                            <div style="font-weight: 900; color: #FFF; margin-bottom: 3px; text-transform:uppercase;">Interaction #{el['Track/Object']}</div>
                            <div style="color: #E0E0E0; font-family: 'Space Grotesk', monospace; font-size: 0.85rem; font-weight:700;">{el['Time']} | Dist: {dtc} | TTC: {ttc}</div>
                        </div>
                        <div style="color: {s_col}; background:#0A0A0A; border: 1px solid {s_col}; padding:4px 8px; font-weight: 900; letter-spacing: 1px;">{s_lbl}</div>
                    </div>
                    '''
            else:
                feed_html = '<div style="color: #666; text-align: center; font-style: italic; margin-top:20px; font-weight:700;">Awaiting safety events...</div>'
                
            feed_placeholder.markdown(feed_html, unsafe_allow_html=True)
            time.sleep(0.01)

    # --------------------------
    # RISK ANALYTICS 
    # --------------------------
    st.markdown("<hr style='border:none; border-bottom: 2px dashed #222; margin: 30px 0;'>", unsafe_allow_html=True)
    
    a_col1, a_col2 = st.columns([3, 1])
    with a_col1:
        st.markdown('<div class="hero-title" style="font-size: 2.1rem; letter-spacing: -1px;">Risk Analytics Pipeline</div>', unsafe_allow_html=True)
    with a_col2:
        st.markdown(f'<div style="text-align: right; margin-top: 15px;"><div class="status-active">SYSTEM {"ACTIVE" if st.session_state.is_running else "IDLE"}</div><br><span style="color:#FFF; font-size:1rem; font-weight: 900; background:#0A0A0A; border:1px solid #333; padding:4px 8px;">Analysis Session<br>{datetime.now().strftime("%Y-%m-%d %H:%M")}</span></div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    c_avg_r = sum(st.session_state.risk_history) / len(st.session_state.risk_history) if st.session_state.risk_history else 0
    c_tot_det = sum(st.session_state.obj_dist.values())

    k1.markdown(f'<div class="glass-card-elevated" style="padding:15px; margin-bottom:20px;"><div class="kpi-title">TOTAL FRAMES ANALYZED</div><div class="kpi-value">{st.session_state.total_frames:,}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="glass-card-elevated" style="padding:15px; margin-bottom:20px;"><div class="kpi-title">TOTAL DETECTIONS</div><div class="kpi-value">{c_tot_det:,}</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="glass-card-elevated" style="padding:15px; margin-bottom:20px;"><div class="kpi-title">HIGH-RISK EVENTS</div><div class="kpi-value">{st.session_state.high_risk_events}</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="glass-card-elevated" style="padding:15px; margin-bottom:20px;"><div class="kpi-title">AVG RISK SCORE</div><div class="kpi-value">{int(c_avg_r)}%</div></div>', unsafe_allow_html=True)
    k5.markdown(f'<div class="glass-card-elevated" style="padding:15px; margin-bottom:20px; border-color:#FF3B3B; box-shadow:4px 4px 0px #FF3B3B;"><div class="kpi-title" style="color:#FF3B3B;">COLLISION EVENTS</div><div class="kpi-value" style="color:#FFF;">{st.session_state.critical_events}</div></div>', unsafe_allow_html=True)

    g1, g2 = st.columns([2.5, 1])
    with g1:
        st.markdown("##### RISK OVER TIME")
        if st.session_state.risk_history:
            df_plot = pd.DataFrame({'Time': range(len(st.session_state.risk_history)), 'Risk': st.session_state.risk_history})
            fig = px.area(df_plot, x='Time', y='Risk', range_y=[0, 100], height=300)
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#FFF', family="Space Grotesk"))
            fig.update_traces(fillcolor='rgba(0, 255, 209, 0.2)', line=dict(color='#00FFD1', width=3))
            fig.update_xaxes(gridcolor='#333', zerolinecolor='#333', gridwidth=1, zerolinewidth=1)
            fig.update_yaxes(gridcolor='#333', zerolinecolor='#333', gridwidth=1, zerolinewidth=1)
            st.plotly_chart(fig, use_container_width=True, key=f"risk_timeline_{st.session_state.total_frames}")
        else:
            st.info("Awaiting runtime data for graph modeling.")

    with g2:
        st.markdown("##### DETECTION DISTRIBUTION")
        if c_tot_det > 0:
            fig_donut = px.pie(values=list(st.session_state.obj_dist.values()), names=list(st.session_state.obj_dist.keys()), hole=0.7, height=300, color_discrete_sequence=['#00FFD1', '#F5C518', '#FF3B3B', '#FF9500'])
            fig_donut.update_traces(marker=dict(line=dict(color='#0A0A0A', width=2)))
            fig_donut.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Space Grotesk", color='#FFF'))
            st.plotly_chart(fig_donut, use_container_width=True, key=f"donut_{st.session_state.total_frames}")
        else:
            st.info("Awaiting detection clusters.")
"""

with codecs.open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

