# scripts/fetch_bls_national.py
import os
import requests
import pandas as pd
from datetime import datetime

BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

SERIES = {
    "nonfarm_total": "CES0000000001",       # national total nonfarm payroll
    "unemployment_rate": "LNS14000000",     # national unemployment rate (CPS)
    "agriculture_employment": "LNS12032184" # national agriculture employment (CPS) — change if you choose a different ID
}

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

    # pivot to wide format: one column per series
    df_wide = df.pivot(index="date", columns="series_id", values="value").sort_index()

    # rename columns
    rename = {
        SERIES["nonfarm_total"]: "nonfarm_total",
        SERIES["unemployment_rate"]: "unemployment_rate",
        SERIES["agriculture_employment"]: "ag_employment"
    }
    df_wide = df_wide.rename(columns=rename)
    df_wide.to_csv(os.path.join(os.path.dirname(__file__), "..", "data", "national_bls_data.csv"))
    print("Wrote data to data/national_bls_data.csv — shape:", df_wide.shape)

if __name__ == "__main__":
    main()
