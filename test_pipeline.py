import urllib.request
import os

url = "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/person-bicycle-car-detection.mp4"
if not os.path.exists("test.mp4"):
    urllib.request.urlretrieve(url, "test.mp4")

from src.video_processor import VideoProcessor
vp = VideoProcessor()

frames = 0
for frame, max_risk, alerts, obj_count, cap, fps, dets in vp.process_video_stream("test.mp4"):
    frames += 1
    if frames > 10:
        break

print(f"Successfully processed {frames} frames.")
print(f"Last frame risk: {max_risk}, objects: {obj_count}, alerts: {len(alerts)}")
