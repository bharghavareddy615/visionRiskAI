import sys
from streamlit.testing.v1 import AppTest

print("Initializing AppTest...")
at = AppTest.from_file('app.py', default_timeout=120)
at.run()

print("App loaded. Toggling Demo Mode...")
at.sidebar.checkbox[0].set_value(True).run()
if not at.session_state.video_path:
    print("Failed to load demo video in session state.")
    sys.exit(1)

print("Starting Analysis...")
try:
    at.button[0].click().run(timeout=120)
except Exception as e:
    print(f"Exception during run: {e}")

if at.exception:
    print("EXCEPTIONS ENCOUNTERED:")
    for e in at.exception:
        print(e.message)
    sys.exit(1)
    
print("NO EXCEPTIONS THROWN.")
if at.metric:
    print(f"Final Risk Metric: {at.metric[0].value}")
    print(f"Final Alerts: {at.metric[3].value}")
else:
    print("No metrics rendered.")
