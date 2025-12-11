# U.S. Labor Market Dashboard — Econ 8320 Semester Project

A **Streamlit dashboard** visualizing U.S. labor statistics using BLS CES and LAUS data.

## Features

* National Nonfarm Employment
* National Agricultural Employment
* State Unemployment Rates

> **Note:** Average weekly hours and average hourly earnings were excluded due to unavailable monthly data.

## Repository Structure

```
project_root/
├─ data/                  # CSV data files
│  ├─ national_employment.csv
│  └─ state_unemployment.csv
├─ json/                  # BLS series JSON mappings
├─ scripts/               # Data-fetching scripts
├─ streamlit/
│  └─ app.py              # Streamlit dashboard
├─ requirements.txt
```

## Quick Start

1. Clone the repo and navigate to it:

```
git clone <your_repo_url>
cd econ8320-semester-project
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Launch the dashboard:

```
streamlit run streamlit/app.py
```

## Updating Data

* Run `scripts/fetch_bls_national.py` for national data.
* Run `scripts/fetch_bls_state.py` for state unemployment.
* Run `scripts/get_state_ag_data.py` for optional state agriculture data.

Updated CSVs in `data/` will automatically refresh the dashboard.

## Limitations

* No state-level agricultural employment series is publicly available monthly — the dashboard uses national data instead.

## Usage

* Sidebar filters allow selection of states and national metrics.
* Expand **Raw Data Tables** to inspect underlying datasets.

## License

Academic use only.
