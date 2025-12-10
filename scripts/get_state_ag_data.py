import requests
import pandas as pd
import json
import datetime as dt
import os

# ---------- Load State Agricultural Series JSON ----------
json_path = os.path.join("json", "state_ag_series.json")
with open(json_path, "r") as file:
    series_dict = json.load(file)

state_mapping = series_dict["11"]  # industry 11 agriculture

# ---------- BLS API URL ----------
BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# ---------- Parameters ----------
years = list(range(2020, dt.datetime.now().year + 1))  # 2020 to current
years_param = {"startyear": min(years), "endyear": max(years)}

data_records = []

# ---------- Collect Data Per State ----------
for state, series_id in state_mapping.items():
    payload = {"seriesid": [series_id], **years_param}
    response = requests.post(BLS_URL, json=payload).json()

    if "Results" in response:
        entries = response["Results"]["series"][0]["data"]
        for item in entries:
            record = {
                "date": f"{item['year']}-{item['periodName']}-01",
                "state": state,
                "ag_employment": int(item["value"])
            }
            data_records.append(record)

# ---------- Convert to DataFrame ----------
df = pd.DataFrame(data_records)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["state", "date"])

# ---------- Save CSV ----------
output_path = os.path.join("data", "state_ag_employment.csv")
df.to_csv(output_path, index=False)

print(f"Saved {output_path}")
