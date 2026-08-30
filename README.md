# VisionRisk AI
> "See Risk. Understand Risk. Act Early."  
> *Transforming ordinary video into actionable visual safety intelligence.*

## 1. Problem
Traditional traffic and pedestrian safety systems rely on after-the-fact reporting or simple presence detection. There is a lack of real-time, explainable intelligence that highlights *why* a situation is dangerous before an accident occurs, particularly in complex mixed-traffic environments (heavy vehicles vs. vulnerable road users).

## 2. Solution
VisionRisk AI is a real-time visual risk detection prototype. By combining state-of-the-art YOLOv8 object tracking with a deterministic, explainable risk heuristic engine, the dashboard processes standard MP4 video feeds to instantly highlight potential collision vectors and unsafe proximity dynamically.

## 3. Key Features
- **Real-Time YOLOv8 Object Tracking:** Persistent, high-confidence identification of pedestrians, bicycles, motorcycles, cars, buses, and trucks.
- **Explainable Analytics Engine:** Rather than a black-box AI score, the system calculates exact relative bounds and yields human-readable alerts (e.g., "A heavy vehicle and vulnerable road user are dangerously close.").
- **Dynamic Streamlit Dashboard:** A polished, SaaS-designed UI featuring live metric cards, rolling risk trend charts, and an event log.
- **Local & Video Processing:** Entirely local inference ensures data privacy and fast frame-by-frame analysis without heavy latency.

## 4. How it Works
1. **Upload or Demo:** Submit standard video footage into the portal.
2. **Detection & Tracking:** The system strips out background noise and continuously identifies predefined safety-critical objects.
3. **Risk Scoring:** The backend compares bounding box distances, computes approach velocity via centroid tracking, and checks object classes (applying multipliers for vulnerable entities).
4. **Overlay & Alert:** It visualizes the danger in real time through an embedded stream and logs it in a tabular history.

## 5. Architecture
```
[ Video Input ] -> [ Streamlit Session State ]
                          |
                          v
                 [ src/video_processor ]
                     /              \\
    [ src/detector ]                  [ src/risk_engine ]
    (YOLOv8 BotSORT Tracker)        (Relative Movement & Bounds Heuristic)
                     \\              /
                      v            v
               [ Output Metrics & Annotated RGB Frames ]
                          |
                          v
                [ Streamlit UI Dashboard ]
```

## 6. Technology Stack
- **Python 3.x**
- **Ultralytics (YOLOv8):** Inference and Object Tracking
- **OpenCV (cv2):** Frame extraction and geometry annotation
- **Streamlit:** Interactive web UI and state management
- **Plotly & Pandas:** Risk metric visualization and tabular logs

## 7. Installation
```bash
# Clone the repository and navigate into the directory
# Install requirements
pip install -r requirements.txt
```

## 8. Usage
```bash
streamlit run app.py
```
*Navigate to `http://localhost:8501/` in your browser.*

## 9. Risk Scoring Methodology
Risk scores (0–100) are generated through an explainable heuristic:
- **0–30 LOW:** Safe distance, stationary, or non-conflicting vectors.
- **31–60 MODERATE:** Decreasing distance between vehicles.
- **61–80 HIGH:** Unsafe proximity detected. Overlays trigger warnings.
- **81–100 CRITICAL:** Extreme proximity combined with approaching vectors, particularly involving heavy machinery and vulnerable targets.
> *Note: Bounding boxes are scaled against frame dimensions to proxy physical distance. Class permutations apply multipliers (e.g., Car vs. Pedestrian > Car vs. Car).*

## 10. Limitations
- **Prototype Status:** The risk engine is an explainable decision-support heuristic, not a certified safety or collision-prediction system. 
- **2D Limitation:** It operates in a 2D plane based on pixel bounds; perspective warping without formal camera calibration can distort distances.
- **Processing Power:** The demo speed is bound by the host CPU/GPU capabilities.

## 11. Future Scope
- Integrating homography/perspective translation for accurate 3D metric calculations.
- Using specialized pose-estimation to gauge pedestrian intent (looking away vs. looking at traffic).
- End-to-end deep learning approach for temporal collision prediction models (e.g., taking sequences of frames into an LSTM/Transformer).

## 12. Screenshots
*(Placeholder: Insert screenshots of the working dashboard here)*

## 13. Demo Instructions
To experience the easiest demo for a hackathon presentation:
1. Ensure `assets/demo.mp4` contains a 10-30 second traffic video clip. 
2. Launch `streamlit run app.py`.
3. Check **"Use Demo Mode"** in the sidebar.
4. Click **"Start Analysis"**.
5. Observe the metrics update live within the 2-minute pitch window!
