#!/usr/bin/env python3
"""
detect_rtsp_with_logging.py - RTSP person detector (YOLO11n) with robust logging.
The original logic is preserved; all `print` calls are replaced with `logging`.
"""

import logging
import os
import subprocess
import time
from datetime import date, datetime

import cv2
from ultralytics import YOLO

# ------------------------------------------------------------------
# Logging configuration
# ------------------------------------------------------------------
TODAY = date.today().strftime("%Y-%m-%d")
LOG_DIR = f"/workspace/detect_rtsp_OUTPUT/{TODAY}"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "detection.log")
logging.basicConfig(
    level=logging.INFO,                       # change to DEBUG for more verbosity
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Load YOLO model
# ------------------------------------------------------------------
model = YOLO("yolo11n.pt")
logger.info("YOLO model 'yolo11n.pt' loaded.")

# ------------------------------------------------------------------
# RTSP stream URL
# ------------------------------------------------------------------
RTSP_URL = "rtsp://rtsp-url:9090"

# ------------------------------------------------------------------
# Helper - ensure a directory exists
# ------------------------------------------------------------------
def ensure_dir(path: str) -> None:
    """Create directory if it does not exist (no error if it already exists)."""
    os.makedirs(path, exist_ok=True)

# ------------------------------------------------------------------
# Main detection loop
# ------------------------------------------------------------------
frame_id = 0
logger.info("RTSP detection running. Press Ctrl+C to stop.")

def run_detection_loop() -> None:
    global frame_id

    # open the stream once
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

    while True:
        if not cap.isOpened():
            # This should never happen on the very first iteration, but
            # we handle it for safety.
            logger.warning("VideoCapture not open - attempting to reconnect.")
            cap.release()
            time.sleep(1)
            cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                logger.error("Re-connect failed - aborting loop.")
                break
            continue

        ret, frame = cap.read()
        if not ret:
            logger.warning("Stream disconnected - attempting to reconnect.")
            cap.release()
            # brief pause before trying again
            time.sleep(1)
            cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                logger.error("Re-connect failed - exiting loop.")
                break
            continue

        # ------------------------------------------------------------------
        # Person detection (class 0)
        # ------------------------------------------------------------------
        results = model(frame, classes=[0], verbose=False)   # only 'person'
        for result in results:
            for box in result.boxes:
                if box.conf.item() > 0.37:   # threshold - tweak as needed
                    logger.info("High-confidence detection: %.3f", box.conf.item())

                    save_path = os.path.join(
                        LOG_DIR, f"person_detected_{frame_id:06d}.jpg"
                    )
                    result.save(filename=save_path)
                    logger.info("Saved detection: %s", save_path)

                    # Timestamp in the log
                    now = datetime.now()
                    logger.info("Detection timestamp: %s", now.strftime("%Y-%m-%d %H:%M:%S"))

                    # ------------------------------------------------------------------
                    # Notify script - Home Assitant
                    # ------------------------------------------------------------------
                    logger.info("Calling home_notify.py")
                    try:
                        subprocess.run(
                            ["python", "/workspace/home_notify.py"],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                    except subprocess.CalledProcessError as exc:
                        logger.error("home_notify.py failed: %s", exc)

        # ------------------------------------------------------------------
        # Increment frame counter and short pause
        # ------------------------------------------------------------------
        frame_id += 1
        # a tiny sleep keeps the loop from hogging the CPU
        time.sleep(0.01)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    cap.release()
    logger.info("Stream ended - VideoCapture released.")


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------
if __name__ == "__main__":
    try:
        run_detection_loop()
    except KeyboardInterrupt:
        logger.info("Ctrl+C pressed - exiting.")