import requests
import pandas as pd
import numpy as np
import time
import sys
import os

# Generate dummy data
def generate_data(filename='data.csv'):
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    values = np.sin(np.linspace(0, 10, 100)) + np.random.normal(0, 0.1, 100)
    df = pd.DataFrame({'date': dates, 'value': values})
    df.to_csv(filename, index=False)
    print(f"Generated {filename}")
    return filename

def wait_for_service(url, name, retries=10):
    print(f"Waiting for {name} at {url}...")
    for i in range(retries):
        try:
            requests.get(url)
            print(f"{name} is up!")
            return True
        except:
            time.sleep(2)
            print(f"Retrying {name} ({i+1}/{retries})...")
    print(f"{name} failed to start.")
    return False

def test_system():
    gateway_url = "http://localhost:8000"
    
    # Wait for gateway
    if not wait_for_service(gateway_url, "Gateway"):
        sys.exit(1)

    # 1. Upload
    filename = generate_data()
    with open(filename, 'rb') as f:
        files = {'file': (filename, f, 'text/csv')}
        response = requests.post(f"{gateway_url}/upload", files=files)
    
    if response.status_code == 200:
        print("Upload successful!")
        data_preview = response.json()['preview']
    else:
        print(f"Upload failed: {response.text}")
        sys.exit(1)

    # 2. Forecast Classical (ARIMA)
    payload = {
        "data": data_preview,
        "target_column": "value",
        "date_column": "date",
        "model": "arima",
        "horizon": 5
    }
    print("Testing Classical (ARIMA)...")
    resp = requests.post(f"{gateway_url}/forecast/classical", json=payload)
    if resp.status_code == 200:
        print("Classical Forecast Success:", resp.json()['forecast'])
    else:
        print("Classical Forecast Failed:", resp.text)

    # 3. Forecast ML (Random Forest)
    payload['model'] = 'rf'
    print("Testing ML (Random Forest)...")
    resp = requests.post(f"{gateway_url}/forecast/ml", json=payload)
    if resp.status_code == 200:
        print("ML Forecast Success:", resp.json()['forecast'])
    else:
        print("ML Forecast Failed:", resp.text)

    # 4. Forecast DL (LSTM)
    payload['model'] = 'lstm'
    print("Testing DL (LSTM)...")
    resp = requests.post(f"{gateway_url}/forecast/dl", json=payload)
    if resp.status_code == 200:
        print("DL Forecast Success:", resp.json()['forecast'])
    else:
        print("DL Forecast Failed:", resp.text)

if __name__ == "__main__":
    test_system()
