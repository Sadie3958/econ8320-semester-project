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

• National Nonfarm Employment (CES)  
• National Agricultural Employment (CES 102 series)  
• State Unemployment Rates (LAUS)  
• Weekly Hours in Agriculture (CES)  
• Average Hourly Earnings in Agriculture (CES)

---

### Data Limitation: State-Level Agricultural Employment

One of the original project goals was to analyze **agricultural employment by state**.  
However, after attempting to retrieve data from:

- BLS CES (no state-level agriculture series published)  
- USDA ERS (endpoint unavailable; 404 errors)  
- USDA NASS (no monthly employment series)  

…there is **no publicly available monthly state-level agricultural employment dataset**.

Because of this limitation, this dashboard uses **national agricultural employment** instead.  
This limitation is documented in the final project report.
"""

# LOAD DATA

@st.cache_data
def load_data():
    national = pd.read_csv("data/national_employment.csv")
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

selected_metric = st.sidebar.selectbox(
    "National Employment Metric:",
    [
        "ag_employment",
        "total_nonfarm",
        "avg_weekly_hours",
        "avg_hourly_earnings"
    ],
    index=0
)

metric_labels = {
    "ag_employment": "Agricultural Employment",
    "total_nonfarm": "Total Nonfarm Employment",
    "avg_weekly_hours": "Average Weekly Hours (Agriculture)",
    "avg_hourly_earnings": "Average Hourly Earnings (Agriculture)",
}

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
