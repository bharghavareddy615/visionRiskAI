import cv2
import time
from src.detector import VisionDetector
from src.risk_engine import RiskEngine
from src.utils import TARGET_CLASSES, RISK_LEVELS_COLOR, get_risk_level

class VideoProcessor:
    def __init__(self, model_path='yolov8n.pt', confidence_thresh=0.35, inference_interval=1, resize_width=640):
        try:
            self.detector = VisionDetector(model_path=model_path)
            self.confidence_thresh = confidence_thresh
            self.inference_interval = inference_interval
            self.resize_width = resize_width
        except Exception as e:
            raise RuntimeError(f"YOLO loading failed: {str(e)}")
        self.risk_engine = RiskEngine()

    def process_video_stream(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            yield None, 0, [], 0, cap, 0
            return

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        frame_idx = 0
        last_max_risk = 0
        last_alerts = []
        last_updated_detections = {}
        
        while cap.isOpened():
            start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_idx += 1
            
            # Frame Downsizing logic for huge performance boosts
            orig_h, orig_w = frame.shape[:2]
            proc_frame = frame
            scale_factor = 1.0
            if self.resize_width and orig_w > self.resize_width:
                scale_factor = self.resize_width / float(orig_w)
                proc_h = int(orig_h * scale_factor)
                proc_frame = cv2.resize(frame, (self.resize_width, proc_h))

            # Skip interference on interval logic
            if frame_idx % self.inference_interval == 0 or frame_idx == 1:
                # Track objects through wrapper to ensure class filtering applies natively
                results = [self.detector.track(proc_frame, tracker='botsort.yaml', persist=True)]
                
                detections = {}
                if len(results) > 0 and results[0].boxes and results[0].boxes.id is not None:
                    boxes = results[0].boxes.xyxy.cpu().numpy()
                    track_ids = results[0].boxes.id.cpu().numpy().astype(int)
                    class_ids = results[0].boxes.cls.cpu().numpy().astype(int)
                    confidences = results[0].boxes.conf.cpu().numpy()
                    
                    for box, track_id, class_id, conf in zip(boxes, track_ids, class_ids, confidences):
                        if class_id in TARGET_CLASSES and conf >= self.confidence_thresh:
                            if scale_factor != 1.0:
                                box = box / scale_factor
                                
                            detections[track_id] = {
                                'box': box.tolist(),
                                'class_id': class_id,
                                'class_name': TARGET_CLASSES[class_id],
                                'conf': conf
                            }

                # Analyze Risk Engine
                max_risk, alerts, updated_detections = self.risk_engine.analyze_frame(
                    detections, frame_width, frame_height
                )
                
                last_max_risk = max_risk
                last_alerts = alerts
                last_updated_detections = updated_detections
            
            # Draw overlays using latest available detections
            for tid, data in last_updated_detections.items():
                x1, y1, x2, y2 = map(int, data['box'])
                risk_score = data.get('risk', 0)
                level = get_risk_level(risk_score)
                color = RISK_LEVELS_COLOR[level]
                
                # Bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Object Info
                conf_pct = int(data.get('conf', 0) * 100)
                status = data.get('approach_status', 'STABLE')
                label = f"{data['class_name']} #{tid} | {status} {conf_pct}%"
                
                cv2.rectangle(frame, (x1, max(0, y1 - 20)), (x1 + len(label)*8, y1), color, -1)
                cv2.putText(frame, label, (x1, max(15, y1 - 5)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1)

            # Global overlay prominent
            global_level = get_risk_level(last_max_risk)
            color = RISK_LEVELS_COLOR[global_level]
            warning_text = f"GLOBAL STATUS: {global_level} RISK"
            cv2.rectangle(frame, (10, 10), (10 + len(warning_text)*20, 60), (0,0,0), -1)
            cv2.putText(frame, warning_text, (20, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            # Convert to RGB for Streamlit
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # FPS tracking
            elapsed = time.time() - start_time
            fps = int(1.0 / elapsed) if elapsed > 0 else 0
            
            # Yield frame and metadata
            yield rgb_frame, last_max_risk, last_alerts, len(last_updated_detections), cap, fps, last_updated_detections
            
        cap.release()
