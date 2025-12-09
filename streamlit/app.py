import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("../data/national_bls_data.csv", parse_dates=["date"])
    return df

df = load_data()

# -------------------------
# Page Layout
# -------------------------
st.set_page_config(page_title="US Agriculture Employment Dashboard", layout="wide")
st.title("US Agriculture & Labor Dashboard")
st.markdown("Interactive visualization of national nonfarm, agriculture employment, and unemployment rates.")

# -------------------------
# Employment Line Chart
# -------------------------
st.subheader("Employment Trends")
fig1 = px.line(
    df,
    x="date",
    y=["nonfarm_total", "ag_employment"],
    labels={"value":"Employees", "date":"Month"},
    title="National Nonfarm vs Agricultural Employment"
)
st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# Unemployment Line Chart
# -------------------------
st.subheader("Unemployment Rate")
fig2 = px.line(
    df,
    x="date",
    y="unemployment_rate",
    labels={"unemployment_rate":"Unemployment Rate (%)", "date":"Month"},
    title="National Unemployment Rate"
)
st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# Date Range Selector
# -------------------------
st.subheader("Filter by Date")
start_date = st.date_input("Start date", df["date"].min())
end_date = st.date_input("End date", df["date"].max())

filtered_df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]

st.markdown("### Filtered Data Preview")
st.dataframe(filtered_df.tail(10))

