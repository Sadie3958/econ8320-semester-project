import pandas as pd
import requests
import os

# ---- QCEW Download Link (All State Industries) ---- #
url = "https://download.bls.gov/pub/time.series/en/en.data.1.AllData"

print("Downloading state employment data...")
data = requests.get(url).text

# ---- Load raw file into DataFrame ---- #
df = pd.read_csv(pd.compat.StringIO(data), sep="\t")

# ---- Clean Columns ---- #
df.columns = [col.strip().lower() for col in df.columns]
df = df.rename(columns={"series_id": "series", "value": "employment"})

# ---- Filter Agriculture (industry code starts with '11') ---- #
df_ag = df[df["series"].str.contains("11")]

# ---- Extract Year-Month ---- #
df_ag["year"] = df_ag["year"].astype(int)
df_ag["period"] = df_ag["period"].str.replace("M", "").astype(int)
df_ag["date"] = pd.to_datetime(df_ag["year"].astype(str) + "-" + df_ag["period"].astype(str) + "-01")

# ---- Extract State Code (characters 4–5) ---- #
df_ag["state"] = df_ag["series"].str[3:5]

# ---- Final Selection ---- #
df_final = df_ag[["date", "state", "employment"]].rename(columns={"employment": "ag_employment"})
df_final = df_final.dropna().sort_values(["state", "date"])

# Fix the date column assignment
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"])
elif "period" in df.columns:
    df["date"] = pd.to_datetime(df["period"].astype(str) + "-01-01")  # convert year to Jan 1
elif "year" in df.columns:
    df["date"] = pd.to_datetime(df["year"].astype(str) + "-01-01")
else:
    raise KeyError("No valid date column (date, period, year) found in the dataset.")

# ---- Save CSV ---- #
output_path = os.path.join("data", "state_ag_employment.csv")
df_final.to_csv(output_path, index=False)

print(f"Saved: {output_path}")
