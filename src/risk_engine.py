import math
from src.utils import get_risk_level

class RiskEngine:
    def __init__(self):
        # Store previous centers for velocity: { track_id: (cx, cy) }
        self.prev_centers = {}
        # Track persistent risks: { (id1, id2): {'ema': float, 'missed': int, 'consecutive_high_risk': int} }
        self.risk_persistence = {}
        self.PERSISTENCE_FRAMES = 5

    def get_center(self, box):
        x1, y1, x2, y2 = box
        # Anchor to bottom-center of bounding box for realistic distance proxies
        return ((x1 + x2) / 2, y2)

    def calculate_distance(self, c1, c2):
        return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

    def analyze_frame(self, detections, frame_width, frame_height):
        """
        detections format:
        {
            track_id: {'box': [x1, y1, x2, y2], 'class_id': int, 'class_name': str}
        }
        """
        max_risk_score = 0
        alerts = []
        track_ids = list(detections.keys())
        
        # Calculate centers
        current_centers = {}
        for tid, data in detections.items():
            current_centers[tid] = self.get_center(data['box'])

        # Compare every pair
        for i in range(len(track_ids)):
            for j in range(i + 1, len(track_ids)):
                id1, id2 = track_ids[i], track_ids[j]
                data1, data2 = detections[id1], detections[id2]
                
                c1, c2 = current_centers[id1], current_centers[id2]
                dist = self.calculate_distance(c1, c2)
                
                # Perspective-aware depth proxy: Normalize via relative bounding box sizing.
                w1, h1 = data1['box'][2] - data1['box'][0], data1['box'][3] - data1['box'][1]
                w2, h2 = data2['box'][2] - data2['box'][0], data2['box'][3] - data2['box'][1]
                
                # Average size of the two objects to approximate local depth/scale
                scale_proxy = (max(w1, h1) + max(w2, h2)) / 2
                
                norm_dist = dist / scale_proxy if scale_proxy > 0 else 1.0

                # Base risk threshold: Objects within 2.5x of their own scale represent proximity
                if norm_dist < 2.5:
                    base_risk = min(100, (2.5 - norm_dist) / 2.5 * 100)
                else:
                    base_risk = 0

                
                # Vulnerability Multiplier (Pedestrians and bicycles are more vulnerable)
                vulnerable = ['person', 'bicycle', 'motorcycle']
                heavy = ['car', 'bus', 'truck']
                c1_vul = data1['class_name'] in vulnerable
                c2_vul = data2['class_name'] in vulnerable
                c1_hev = data1['class_name'] in heavy
                c2_hev = data2['class_name'] in heavy
                is_vulnerable = c1_vul or c2_vul
                is_heavy = c1_hev or c2_hev
                
                if is_vulnerable and is_heavy:
                    base_risk *= 1.5  # Increase risk for vulnerable vs heavy
                elif is_heavy and is_heavy:
                    base_risk *= 1.0 # Standard
                else:
                    base_risk *= 0.8 # Lower risk between pedestrians
                    
                # Relative movement check
                # Decreasing distance means they are approaching each other
                relative_approach = 1.0
                approach_status = "STABLE"
                if id1 in self.prev_centers and id2 in self.prev_centers:
                    prev_c1 = self.prev_centers[id1]
                    prev_c2 = self.prev_centers[id2]
                    prev_dist = self.calculate_distance(prev_c1, prev_c2)
                    
                    if dist < prev_dist - 2:
                        relative_approach = 1.3
                        approach_status = "APPROACHING"
                    elif dist > prev_dist + 5:
                        relative_approach = 0.5
                        approach_status = "MOVING AWAY"
                
                score = min(100, base_risk * relative_approach)
                
                # Persistence Check (Smooth the risk to avoid flickering)
                pair_key = tuple(sorted([id1, id2]))
                if pair_key not in self.risk_persistence:
                    self.risk_persistence[pair_key] = {'ema': score, 'missed': 0, 'consecutive_high_risk': 0, 'last_risk': score}
                
                # EMA Smoothing
                alpha = 0.3 # 30% new score, 70% historical score for stability
                self.risk_persistence[pair_key]['ema'] = (alpha * score) + ((1 - alpha) * self.risk_persistence[pair_key]['ema'])
                self.risk_persistence[pair_key]['missed'] = 0
                
                ema_score = self.risk_persistence[pair_key]['ema']
                last_score = self.risk_persistence[pair_key].get('last_risk', ema_score)
                
                # Risk Hysteresis (5-point flapping buffer)
                smoothed_score = ema_score
                if last_score >= 61 and ema_score >= 55 and ema_score < 61:
                    smoothed_score = 61 # artificially keep HIGH
                elif last_score >= 31 and last_score < 61 and ema_score >= 26 and ema_score < 31:
                    smoothed_score = 31 # artificially keep MODERATE
                
                self.risk_persistence[pair_key]['last_risk'] = smoothed_score
                
                # Debounce alerts directly
                if smoothed_score >= 61:
                    self.risk_persistence[pair_key]['consecutive_high_risk'] += 1
                else:
                    self.risk_persistence[pair_key]['consecutive_high_risk'] = max(0, self.risk_persistence[pair_key]['consecutive_high_risk'] - 1)
                
                consecutive_high = self.risk_persistence[pair_key]['consecutive_high_risk']
                
                # Record risk on objects
                if 'risk' not in detections[id1] or smoothed_score > detections[id1]['risk']:
                    detections[id1]['risk'] = smoothed_score
                    detections[id1]['approach_status'] = approach_status
                if 'risk' not in detections[id2] or smoothed_score > detections[id2]['risk']:
                    detections[id2]['risk'] = smoothed_score
                    detections[id2]['approach_status'] = approach_status

                if smoothed_score > max_risk_score:
                    max_risk_score = smoothed_score
                
                if smoothed_score >= 61 and consecutive_high >= 3:
                    reason = ""
                    if (c1_vul and c2_hev) or (c2_vul and c1_hev):
                        if relative_approach > 1.0:
                            reason = "A heavy vehicle and vulnerable road user are in close proximity with increasing relative movement."
                        else:
                            reason = "A heavy vehicle and vulnerable road user are dangerously close."
                    elif c1_hev and c2_hev:
                        if relative_approach > 1.0:
                            reason = "Two heavy vehicles are in dangerously close proximity and approaching each other."
                        else:
                            reason = "Two heavy vehicles are in suspiciously close bounds."
                    else:
                        reason = "Multiple vulnerable objects detected in close proximity."
                        
                    alerts.append({
                        'score': int(smoothed_score),
                        'level': get_risk_level(smoothed_score),
                        'objects': f"{data1['class_name']} #{id1} and {data2['class_name']} #{id2}",
                        'reason': reason,
                        'approach': approach_status
                    })

        # Set default risk for objects not involved in interactions
        for tid in track_ids:
            if 'risk' not in detections[tid]:
                detections[tid]['risk'] = 0

        # Update previous centers
        self.prev_centers = current_centers
        
        # Cleanup persistence for IDs no longer in frame
        keys_to_remove = []
        for pair_key in self.risk_persistence.keys():
            k1, k2 = pair_key
            if k1 not in track_ids or k2 not in track_ids:
                self.risk_persistence[pair_key]['missed'] += 1
                if self.risk_persistence[pair_key]['missed'] > self.PERSISTENCE_FRAMES:
                    keys_to_remove.append(pair_key)
        for k in keys_to_remove:
            del self.risk_persistence[k]
            
        return int(max_risk_score), alerts, detections
