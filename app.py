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

# Metric Type dropdown
metric_type = st.sidebar.selectbox(
    "Select Metric Type:",
    ["Employment", "Unemployment"]
)

# Metric options based on type
if metric_type == "Employment":
    metric_options = ["ag_employment", "nonfarm_total"]
else:
    metric_options = ["unemployment_rate"]

selected_metric = st.sidebar.selectbox(
    f"Select {metric_type} Metric:",
    metric_options,
    index=0
)

metric_labels = {
    "ag_employment": "Agricultural Employment",
    "nonfarm_total": "Total Nonfarm Employment",
    "unemployment_rate": "Unemployment Rate",
}

# SECTION 1 — NATIONAL LABOR MARKET SERIES
st.subheader("📈 National Labor Market Trends")

# Determine hover format
if selected_metric == "unemployment_rate":
    hover_template = "%{y:.1f}%<br>%{x|%b %Y}"
else:
    hover_template = "%{y:,.0f}<br>%{x|%b %Y}"  # commas for thousands

fig1 = px.line(
    national_df,
    x="date",
    y=selected_metric,
    title=f"National {metric_labels[selected_metric]}"
)

fig1.update_traces(hovertemplate=hover_template)
fig1.update_layout(
    yaxis_title=metric_labels[selected_metric],
    xaxis_title="Date",
    hovermode="x unified"
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
    fig2.update_traces(hovertemplate="%{y:.1f}%<br>%{x|%b %Y}")
    fig2.update_layout(
        yaxis_title="Unemployment Rate (%)",
        xaxis_title="Date",
        hovermode="x unified"
    )

    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("Please select at least one state to display unemployment data.")

# SECTION 3 — NOTE ABOUT STATE AGRICULTURAL DATA
st.info(
    "State-level agricultural employment data is not available as a clean monthly."
    "time series from BLS or USDA. This dashboard uses the national agricultural."
    "employment series instead."
)

# SECTION 4 — RAW DATA PREVIEW (OPTIONAL)
with st.expander("View Raw Data Tables"):
    st.write("### National Employment Data")
    st.dataframe(national_df)

    st.write("### State Unemployment Data")
    st.dataframe(unemployment_df)
