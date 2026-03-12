from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

payload = {
    "supplier_id": "SUP-001",
    "operational": {
        "daily_demand": 100,
        "current_inventory": 1500,
        "safety_stock": 200,
        "supplier_lead_time": 14
    },
    "risk": {
        "flood_severity": 0.8,
        "earthquake_risk": 0.2,
        "political_instability": 0.5,
        "transportation_disruption": 0.8,
        "regional_infrastructure_risk": 0.4
    }
}

try:
    response = client.post("/api/analyze", json=payload)
    print("Status:", response.status_code)
    print("Body:", response.json())
except Exception as e:
    import traceback
    traceback.print_exc()
