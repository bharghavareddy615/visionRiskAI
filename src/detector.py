from ultralytics import YOLO
from src.utils import TARGET_CLASSES

class VisionDetector:
    def __init__(self, model_path='yolov8n.pt'):
        # Load the pretrained YOLO model
        self.model = YOLO(model_path)
        
        # Bypass repetitive double-fusion crashes in Ultralytics AutoBackend
        if hasattr(self.model, 'model'):
            self.model.model.is_fused = lambda: True
            
        self.target_class_ids = list(TARGET_CLASSES.keys())

    def track(self, frame, tracker='botsort.yaml', persist=True):
        """
        Runs tracking on a frame and filters out non-target classes.
        Returns the original frame with tracking data.
        """
        # Run tracking, filtering only classes we care about
        results = self.model.track(
            frame, 
            persist=persist, 
            tracker=tracker, 
            classes=self.target_class_ids,
            verbose=False
        )
        return results[0]
