import pandas as pd
import requests
import random

# Fetch Raw Data
raw_df = pd.read_csv("https://raw.githubusercontent.com/just4jc/Northwind-Traders-Dataset/refs/heads/main/supplier.csv")

# Create the required schema
new_data = {
    "supplier_id": raw_df["companyName"],
    "location": raw_df["city"] + ", " + raw_df["country"],
    # Generate realistic random data for operational metrics
    "daily_demand": [random.randint(50, 500) for _ in range(len(raw_df))],
    "current_inventory": [random.randint(200, 5000) for _ in range(len(raw_df))],
    "safety_stock": [random.randint(50, 500) for _ in range(len(raw_df))],
    "supplier_lead_time": [random.randint(5, 45) for _ in range(len(raw_df))],
    "days_of_delay": [random.randint(0, 10) for _ in range(len(raw_df))],
    # Generate realistic random data for risk metrics (0.0 to 1.0)
    "flood_severity": [round(random.uniform(0, 0.5), 2) for _ in range(len(raw_df))],
    "earthquake_risk": [round(random.uniform(0, 0.5), 2) for _ in range(len(raw_df))],
    "political_instability": [round(random.uniform(0, 0.8), 2) for _ in range(len(raw_df))],
    "transportation_disruption": [round(random.uniform(0, 0.4), 2) for _ in range(len(raw_df))],
    "regional_infrastructure_risk": [round(random.uniform(0, 0.3), 2) for _ in range(len(raw_df))]
}

df_formatted = pd.DataFrame(new_data)
csv_filename = "northwind_suppliers_formatted.csv"
df_formatted.to_csv(csv_filename, index=False)
print(f"Saved formatted data to {csv_filename}")

# Upload the data
API_URL = "http://127.0.0.1:8000/api"
print("Uploading test CSV...")
with open(csv_filename, "rb") as f:
    files = {"file": (csv_filename, f, "text/csv")}
    response = requests.post(f"{API_URL}/upload", files=files)

print(f"Upload Status Code: {response.status_code}")
print(f"Upload Response: {response.json()}")
