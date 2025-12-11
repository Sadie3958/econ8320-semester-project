import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="U.S. Labor Dashboard", layout="wide")

# Path to data folder relative to this app.py
DATA_PATH = os.path.join("..", "data")

"""
# U.S. Labor Market Dashboard  
_ECON 8320 Semester Project — Sadie Gingerich_

This dashboard visualizes monthly labor statistics using BLS CES and LAUS data.

---

### About the Data

This app includes:

• National Nonfarm Employment (CES)  
• National Agricultural Employment (CES 102 series)  
• State Unemployment Rates (LAUS)  

---

### Data Limitation: State-Level Agricultural Employment

One of the original project goals was to analyze **agricultural employment by state**.  
However, after attempting to retrieve data from BLS and USDA, there is **no publicly available monthly state-level agricultural employment dataset**.

Because of this limitation, this dashboard uses **national agricultural employment** instead.
"""

# ----------------------
# LOAD DATA
# ----------------------
@st.cache_data
def load_data():
    national_file = os.path.join(DATA_PATH, "national_unemployment.csv")
    unemployment_file = os.path.join(DATA_PATH, "state_unemployment.csv")

    try:
        national = pd.read_csv(national_file)
    except FileNotFoundError:
        st.error(f"❌ Cannot find {national_file}. Make sure the CSV exists.")
        st.stop()

    try:
        unemployment = pd.read_csv(unemployment_file)
    except FileNotFoundError:
        st.error(f"❌ Cannot find {unemployment_file}. Make sure the CSV exists.")
        st.stop()

    # Convert date columns
    national["date"] = pd.to_datetime(national["date"])
    unemployment["date"] = pd.to_datetime(unemployment["date"])

    return national, unemployment

national_df, unemployment_df = load_data()

# ----------------------
# SIDEBAR CONTROLS
# ----------------------
st.sidebar.header("Filters")

selected_states = st.sidebar.multiselect(
    "Select States (Unemployment):",
    sorted(unemployment_df["state"].unique()),
    default=["NE", "IA", "TX"]
)

# Only allow metrics that exist in CSV
available_metrics = [col for col in ["ag_employment", "nonfarm_total"] if col in national_df.columns]

selected_metric = st.sidebar.selectbox(
    "National Employment Metric:",
    available_metrics,
    index=0
)

metric_labels = {
    "ag_employment": "Agricultural Employment",
    "nonfarm_total": "Total Nonfarm Employment"
}

# ----------------------
# NATIONAL LABOR SERIES
# ----------------------
st.subheader("📈 National Labor Market Trends")

fig1 = px.line(
    national_df,
    x="date",
    y=selected_metric,
    title=f"National {metric_labels[selected_metric]}"
)
st.plotly_chart(fig1, use_container_width=True)

# ----------------------
# STATE UNEMPLOYMENT RATES
# ----------------------
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

# ----------------------
# STATE AGRICULTURAL NOTE
# ----------------------
st.info(
    "State-level agricultural employment data is not available as a clean monthly "
    "time series from BLS or USDA. This dashboard uses the national agricultural "
    "employment series instead."
)

# ----------------------
# RAW DATA PREVIEW
# ----------------------
with st.expander("📄 View Raw Data Tables"):
    st.write("### National Employment Data")
    st.dataframe(national_df)

    st.write("### State Unemployment Data")
    st.dataframe(unemployment_df)
