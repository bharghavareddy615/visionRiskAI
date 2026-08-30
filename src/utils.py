TARGET_CLASSES = {
    0: 'person',
    1: 'bicycle',
    2: 'car',
    3: 'motorcycle',
    5: 'bus',
    7: 'truck'
}

RISK_LEVELS_COLOR = {
    'LOW': (0, 255, 0),      # Green
    'MODERATE': (0, 255, 255), # Yellow
    'HIGH': (0, 165, 255),   # Orange (BGR context)
    'CRITICAL': (0, 0, 255)  # Red
}

def get_risk_level(score):
    if score <= 30:
        return 'LOW'
    elif score <= 60:
        return 'MODERATE'
    elif score <= 80:
        return 'HIGH'
    else:
        return 'CRITICAL'
