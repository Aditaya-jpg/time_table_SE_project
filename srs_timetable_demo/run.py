"""
One-Command Runner for the College Timetable Scheduling Demo
Starts the FastAPI backend and serves the interactive timetable visualizer.
"""

import sys
import os
import webbrowser
import threading
import time

# Ensure srs_timetable_demo is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import uvicorn
from backend.app import app


def open_browser(port: int):
    time.sleep(1.2)
    url = f"http://localhost:{port}"
    print(f"\n[Launcher] Launching web browser at {url} ...\n")
    webbrowser.open(url)


def main():
    port = 8000
    # Allow overriding port via argument
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    print("=" * 72)
    print("  COLLEGE TIMETABLE SCHEDULING APPLICATION • SRS CP-SAT DEMO")
    print("=" * 72)
    print(f" * Backend Framework  : FastAPI (Python {sys.version.split()[0]})")
    print(f" * Constraint Solver  : Google OR-Tools CP-SAT")
    print(f" * Post-Solve Audit   : Independent 10-Point Constraint Validator")
    print(f" * Server Listening on: http://localhost:{port}")
    print(f" * Interactive Web UI : http://localhost:{port}/")
    print("=" * 72)
    print(" Press CTRL+C to terminate the application.\n")

    # Launch browser automatically in background
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Run Uvicorn server
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
