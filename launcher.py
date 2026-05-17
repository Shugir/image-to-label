import subprocess
import threading
import time
import webbrowser
import sys
import os

def resource_path(relative):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)

def open_browser():
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

threading.Thread(target=open_browser, daemon=True).start()

subprocess.run([
    sys.executable, "-m", "streamlit", "run",
    resource_path("app.py"),
    "--server.headless", "true",
    "--server.port", "8501",
])
