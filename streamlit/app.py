import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="U.S. Labor Dashboard", layout="wide")

"""
# U.S. Labor Market Dashboard  
_ECON 8320 Semester Project — Sadie Gingerich_

This dashboard visualizes monthly labor statistics using BLS CES and LAUS data.

---

### About the Data

This app includes:

• National Nonfarm Employment  
• National Agricultural Employment  
• State Unemployment Rates  

---

### Data Limitation: State-Level Agricultural Employment

State-level agricultural employment data is not available as a clean monthly time series.
"""

# LOAD DATA
@st.cache_data
def load_data():
    national = pd.read_csv("data/national_bls_data.csv")
    unemployment = pd.read_csv("data/state_unemployment.csv")

    # Convert date columns
    national["date"] = pd.to_datetime(national["date"])
    unemployment["date"] = pd.to_datetime(unemployment["date"])

    return national, unemployment

national_df, unemployment_df = load_data()

# SIDEBAR CONTROLS
st.sidebar.header("Filters")

selected_states = st.sidebar.multiselect(
    "Select States (Unemployment):",
    sorted(unemployment_df["state"].unique()),
    default=["NE", "IA", "TX"]
)

# Only include metrics that actually exist in the CSV
available_metrics = [col for col in ["ag_employment", "nonfarm_total", "avg_weekly_hours", "avg_hourly_earnings"] if col in national_df.columns]

metric_labels = {
    "ag_employment": "Agricultural Employment",
    "nonfarm_total": "Total Nonfarm Employment",
    "avg_weekly_hours": "Average Weekly Hours (Agriculture)",
    "avg_hourly_earnings": "Average Hourly Earnings (Agriculture)",
}

selected_metric = st.sidebar.selectbox(
    "National Employment Metric:",
    available_metrics,
    index=0
)

# SECTION 1 — NATIONAL AGRICULTURAL + LABOR SERIES
st.subheader("📈 National Labor Market Trends")

fig1 = px.line(
    national_df,
    x="date",
    y=selected_metric,
    title=f"National {metric_labels[selected_metric]}"
)
st.plotly_chart(fig1, use_container_width=True)

# SECTION 2 — STATE UNEMPLOYMENT RATES
st.subheader("📊 State Unemployment Rates (LAUS)")

if selected_states:
    df_states = unemployment_df[unemployment_df["state"].isin(selected_states)]

    fig2 = px.line(
        df_states,
        x="date",
        y="unemployment_rate",
        color="state",
        title="State Unemployment Rate Over Time"
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("Please select at least one state to display unemployment data.")

# SECTION 3 — NOTE ABOUT STATE AGRICULTURAL DATA
st.info(
    "State-level agricultural employment data is not available as a clean monthly "
    "time series from BLS or USDA. This dashboard uses the national agricultural "
    "employment series instead."
)

# SECTION 4 — RAW DATA PREVIEW (OPTIONAL)
with st.expander("📄 View Raw Data Tables"):
    st.write("### National Employment Data")
    st.dataframe(national_df)

    st.write("### State Unemployment Data")
    st.dataframe(unemployment_df)
