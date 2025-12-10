import os
import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_national_data():
    file_path = os.path.join("data", "national_bls_data.csv")
    return pd.read_csv(file_path, parse_dates=["date"])

@st.cache_data
def load_state_data():
    file_path = os.path.join("data", "state_unemployment.csv")
    return pd.read_csv(file_path, parse_dates=["date"])

df_national = load_national_data()
df_state = load_state_data()

# -------------------------
# Page Layout
# -------------------------
st.set_page_config(page_title="US Agriculture Employment Dashboard", layout="wide")
st.title("US Agriculture & Labor Dashboard")
st.markdown("Interactive visualization of national nonfarm, agriculture employment, and unemployment rates, with state comparisons.")

# -------------------------
# Employment Line Chart
# -------------------------
st.subheader("National Employment Trends")
fig1 = px.line(
    df_national,
    x="date",
    y=["nonfarm_total", "ag_employment"],
    labels={"value":"Employees", "date":"Month"},
    title="National Nonfarm vs Agricultural Employment"
)
st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# National Unemployment Chart
# -------------------------
st.subheader("National Unemployment Rate")
fig2 = px.line(
    df_national,
    x="date",
    y="unemployment_rate",
    labels={"unemployment_rate":"Unemployment Rate (%)", "date":"Month"},
    title="National Unemployment Rate"
)
st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# State Unemployment Chart
# -------------------------
st.subheader("State Unemployment Comparison")
states = df_state["state"].unique().tolist()
selected_states = st.multiselect(
    "Select states to display",
    options=states,
    default=["NE", "IA", "TX", "CA", "NY"]
)

df_filtered_states = df_state[df_state["state"].isin(selected_states)]

fig3 = px.line(
    df_filtered_states,
    x="date",
    y="unemployment_rate",
    color="state",
    labels={"unemployment_rate":"Unemployment Rate (%)", "date":"Month"},
    title="State Unemployment Rate Comparison"
)
st.plotly_chart(fig3, use_container_width=True)

# -------------------------
# Date Range Selector for National Data
# -------------------------
st.subheader("Filter National Data by Date")
start_date = st.date_input("Start date", df_national["date"].min())
end_date = st.date_input("End date", df_national["date"].max())

df_national_filtered = df_national[
    (df_national["date"] >= pd.to_datetime(start_date)) & 
    (df_national["date"] <= pd.to_datetime(end_date))
]

st.markdown("### Filtered National Data Preview")
st.dataframe(df_national_filtered.tail(10))
