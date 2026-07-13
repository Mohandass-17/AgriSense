"""
import requests
import sys
import codecs

# PERFECT FIX: Handle Windows Emoji encoding
if sys.platform.startswith('win'):
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

def run_demo():
    print("🌾 AGRI-AGENT SYSTEM DEMO 🌾")
    payload = {"temperature": 22, "humidity": 75, "crop_type": "wheat"}
    try:
        r = requests.post("http://localhost:8000/disease/predict", json=payload)
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Server offline? Error: {e}")

if __name__ == "__main__":
    run_demo()
"""

import requests
import sys
import codecs

# FIX: Force UTF-8 for Windows Terminal (Prevents Emoji Crash)
if sys.platform.startswith('win'):
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

def run_test():
    print("🌾 AGRI-AGENT SYSTEM TEST 🌾")
    url = "http://localhost:8000/disease/predict"
    
    # Scenario: High humidity for Root Rot
    payload = {
        "device_id": "field-wheat-1",
        "temperature": 25,
        "humidity": 95,
        "crop_type": "wheat"
    }

    try:
        print("Sending sensor data to AI Agent...")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI Analysis: {result['status']}")
            if 'disease' in result:
                print(f"⚠️  Alert: {result['disease']} detected!")
                print(f"🏥 Remedy: {result['remedies']['organic_methods'][0]}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Failed: Ensure your server is running. {e}")

if __name__ == "__main__":
    run_test()