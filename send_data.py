import json
import requests
import time

def send_dummy_data():
    url = "http://127.0.0.1:8000/update"
    
    try:
        with open('dummy_data.json', 'r') as f:
            dummy_data = json.load(f)
    except FileNotFoundError:
        print("Error: dummy_data.json not found.")
        return

    for i, data in enumerate(dummy_data):
        print(f"[{i+1}/{len(dummy_data)}] Sending data for {data['name']} ({data['side']})...")
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print(f"Success: {response.json().get('msg')}")
            else:
                print(f"Failed: Status Code {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error sending data: {e}")
        
        time.sleep(1) # Small delay between sends

if __name__ == "__main__":
    send_dummy_data()
