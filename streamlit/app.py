import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# Add year and month columns
df_national['year'] = df_national['date'].dt.year
df_national['month'] = df_national['date'].dt.month
df_state['year'] = df_state['date'].dt.year
df_state['month'] = df_state['date'].dt.month

# -------------------------
# Page Layout
# -------------------------
st.set_page_config(page_title="US Agriculture Employment Dashboard", layout="wide")
st.title("US Agriculture & Labor Dashboard")
st.markdown("Interactive visualization of national nonfarm, agriculture employment, and unemployment rates, with state comparisons.")

# -------------------------
# Year Filter
# -------------------------
years = df_national['year'].unique()
selected_years = st.multiselect("Select year(s) to display", options=years, default=years[-1])
df_national_filtered = df_national[df_national['year'].isin(selected_years)]
df_state_filtered = df_state[df_state['year'].isin(selected_years)]

# -------------------------
# National Employment Line Chart with Seasonal Peaks
# -------------------------
st.subheader("National Employment Trends")

# Calculate average monthly agricultural employment within selected year(s)
monthly_avg_ag = df_national_filtered.groupby('month')['ag_employment'].mean()
peak_months = monthly_avg_ag.sort_values(ascending=False).head(3).index.tolist()  # top 3 peak months

fig1 = go.Figure()
# Line for national nonfarm
fig1.add_trace(go.Scatter(x=df_national_filtered['date'], y=df_national_filtered['nonfarm_total'],
                          mode='lines', name='Nonfarm Total'))
# Line for ag employment
fig1.add_trace(go.Scatter(x=df_national_filtered['date'], y=df_national_filtered['ag_employment'],
                          mode='lines', name='Agricultural Employment'))

# Add markers for peak months
for month in peak_months:
    peak_dates = df_national_filtered[df_national_filtered['month'] == month]['date']
    peak_values = df_national_filtered[df_national_filtered['month'] == month]['ag_employment']
    fig1.add_trace(go.Scatter(x=peak_dates, y=peak_values,
                              mode='markers', name=f'Peak Month {month}', marker=dict(size=8, color='red')))

fig1.update_layout(title="National Nonfarm vs Agricultural Employment",
                   xaxis_title="Month", yaxis_title="Employees")
st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# National Unemployment Chart
# -------------------------
st.subheader("National Unemployment Rate")
fig2 = px.line(
    df_national_filtered,
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
states = df_state['state'].unique().tolist()
selected_states = st.multiselect(
    "Select states to display",
    options=states,
    default=["NE", "IA", "TX", "CA", "NY"]
)

df_filtered_states = df_state_filtered[df_state_filtered["state"].isin(selected_states)]

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
start_date = st.date_input("Start date", df_national_filtered["date"].min())
end_date = st.date_input("End date", df_national_filtered["date"].max())

df_national_final = df_national_filtered[
    (df_national_filtered["date"] >= pd.to_datetime(start_date)) & 
    (df_national_filtered["date"] <= pd.to_datetime(end_date))
]

st.markdown("### Filtered National Data Preview")
st.dataframe(df_national_final.tail(10))
