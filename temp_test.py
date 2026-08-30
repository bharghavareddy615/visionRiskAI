import sys
from src.video_processor import VideoProcessor
vp = VideoProcessor()
highest_risk = 0
reasons = []
frames = 0
max_objs = 0
for frame, risk, alerts, objs, cap in vp.process_video_stream('test.mp4'):
    frames += 1
    max_objs = max(max_objs, objs)
    if risk > highest_risk: highest_risk = risk
    if alerts: reasons.extend([a['reason'] for a in alerts])
    if frames % 100 == 0: print(f"Processed {frames} frames...")
print(f"Total Frames: {frames}, Max Risk: {highest_risk}, Max Objects: {max_objs}")
print("Alerts triggered:", set(reasons))