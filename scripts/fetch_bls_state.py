import os
import json
import requests
import pandas as pd
from datetime import datetime

BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# Load state series IDs
with open(os.path.join(os.path.dirname(__file__), "..", "json", "state_series.json")) as f:
    STATE_SERIES = json.load(f)

def fetch(series_ids, start_year=2005, end_year=datetime.now().year):
    headers = {'Content-type': 'application/json'}
    payload = {
        "seriesid": list(series_ids.values()),
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
        state_abbr = [k for k, v in STATE_SERIES.items() if v == sid][0]
        for obs in series.get("data", []):
            if obs.get("period", "").startswith("M"):
                year = int(obs["year"])
                month = int(obs["period"][1:])
                date = datetime(year, month, 1)
                value = obs.get("value")
                data.append({
                    "state": state_abbr,
                    "date": date,
                    "unemployment_rate": float(value) if value else None
                })
    return pd.DataFrame(data)

def main():
    resp = fetch(STATE_SERIES)
    df = parse(resp)
    df.to_csv(os.path.join(os.path.dirname(__file__), "..", "data", "state_unemployment.csv"), index=False)
    print("Wrote state unemployment data to data/state_unemployment.csv — shape:", df.shape)

if __name__ == "__main__":
    main()
