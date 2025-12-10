# scripts/fetch_bls_national.py
import os
import requests
import pandas as pd
from datetime import datetime
import json

# -----------------------------
# Load Series IDs Dynamically
# -----------------------------
json_path = os.path.join(os.path.dirname(__file__), "..", "json", "bls_series_list.json")
with open(json_path, "r") as f:
    series_config = json.load(f)

SERIES = series_config["national"]

BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

def fetch(series_ids, start_year=2005, end_year=datetime.now().year):
    headers = {'Content-type': 'application/json'}
    payload = {
        "seriesid": list(series_ids),
        "startyear": str(start_year),
        "endyear": str(end_year)
    }
    resp = requests.post(BLS_API_URL, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()

def parse(json_resp):
    data = []
    for series in json_resp.get("Results", {}).get("series", []):
        sid = series.get("seriesID")
        for obs in series.get("data", []):
            if obs.get("period", "").startswith("M"):
                year = int(obs["year"])
                month = int(obs["period"][1:])
                date = datetime(year, month, 1)
                value = obs.get("value")
                data.append({
                    "series_id": sid,
                    "date": date,
                    "value": float(value) if value else None
                })
    return pd.DataFrame(data)

def main():
    resp = fetch(SERIES.values())
    df = parse(resp)

    df_wide = df.pivot(index="date", columns="series_id", values="value").sort_index()

    # Rename columns according to JSON names
    rename_dict = {v: k for k, v in SERIES.items()}
    df_wide = df_wide.rename(columns=rename_dict)

    output_path = os.path.join(os.path.dirname(__file__), "..", "data", "national_bls_data.csv")
    df_wide.to_csv(output_path)

    print("Updated data saved to:", output_path)
    print("Shape:", df_wide.shape)

if __name__ == "__main__":
    main()
