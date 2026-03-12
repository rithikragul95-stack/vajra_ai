import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api"

def test_upload():
    print("Uploading test CSV...")
    with open("test_suppliers.csv", "rb") as f:
        files = {"file": ("test_suppliers.csv", f, "text/csv")}
        response = requests.post(f"{API_URL}/upload", files=files)
    
    print(f"Upload Status Code: {response.status_code}")
    print(f"Upload Response: {response.json()}")
    
    print("\nFetching updated suppliers list...")
    response = requests.get(f"{API_URL}/suppliers")
    if response.status_code == 200:
        suppliers = response.json()
        print(f"Found {len(suppliers)} suppliers:")
        for s in suppliers:
            print(f" - {s.get('supplier_id')}: Alert Level: {s.get('alert_level')}, CVI Score: {s.get('cvi_score')}")
    else:
        print(f"Failed to fetch suppliers: {response.status_code}")

if __name__ == "__main__":
    test_upload()
