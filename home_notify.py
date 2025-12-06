#!/usr/bin/env python3
"""
home_notify.py - This code will send notofication to Homeassiatnt app on registered mobile device when its called.
"""

import os
import requests
import logging
import time
import dotenv
from dotenv import load_dotenv

# ------------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------------
dotenv.load_dotenv()
auth_token = os.getenv("AUTH_TOKEN")
api_url = os.getenv("API_URL")


# ------------------------------------------------------------------
# Validate required environment variables
# ------------------------------------------------------------------
if not auth_token or not api_url:
    raise ValueError("AUTH_TOKEN and API_URL must be set in .env file")


headers = {
    "Authorization": f"Bearer {auth_token}",
    "Content-Type": "application/json"
}

# ------------------------------------------------------------------
# Using Frigate with Homeassitant to display alert info.
# ------------------------------------------------------------------
payload = {
    "message": "Motion[Person] Detected",
    "data": {
      "image": "https://homeassistant-url:8123/media-browser/browser/imagelocation-to-be-displayed-on-phone-alert",
      "url": "/frigate-proxy/ingress",
      "clickAction": "/frigate-proxy/ingress"
    }
}

# ------------------------------------------------------------------------------------------------------------------------------------
# Read status from file. NOTE: Before using the script populate the file with time. Example: echo "1761859309" > /tmp/last_api_call.txt
# ------------------------------------------------------------------------------------------------------------------------------------
with open("/tmp/last_api_call.txt", "r") as f:
    last_api_call = f.read().strip()
    print(last_api_call)
current_time = int(time.time())
print("CurrentTime:", current_time)
print("LastAPICallTime:", last_api_call)
if int(current_time) - int(last_api_call) >= 30:
    # Make API call
    try:
       response = requests.post(api_url, json=payload, headers=headers)
       print(f"API response: {response.status_code}")
       print("Notified.")
       # Update timestamp  - Save status to file
       status = current_time
       with open("/tmp/last_api_call.txt", "w") as f:
            f.write(str(status))
    except Exception as e:
       print(f"API call failed: {e}")
else:
    print("Waiting 30 seconds before notifying again.")