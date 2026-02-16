import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    print("Starting integration test...")
    
    # 1. Test Prediction
    payload = {
        "period": "20260216001",
        "history": ["Big", "Small", "Big"],
        "sensor_outputs": {
            "CID Sensor": "Big",
            "Dragon Logic": "Big",
            "Trend Sensor": "Small"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        print(f"Prediction Response: {response.json()}")
        
        # 2. Test Update
        update_payload = {
            "period": "20260216001",
            "history": ["Big", "Small", "Big"],
            "sensor_outputs": {
                "CID Sensor": "Big",
                "Dragon Logic": "Big",
                "Trend Sensor": "Small"
            },
            "prediction": response.json()["prediction"],
            "actual_outcome": "Small",
            "bet_amount": 10,
            "confidence": response.json()["confidence"]
        }
        update_response = requests.post(f"{BASE_URL}/update", json=update_payload)
        print(f"Update Response: {update_response.json()}")
        
        # 3. Test Stats
        stats_response = requests.get(f"{BASE_URL}/stats")
        print(f"Stats Response: {stats_response.json()}")
        
    except Exception as e:
        print(f"Test failed: {e}. Make sure the server is running.")

if __name__ == "__main__":
    test_flow()
