# US Agriculture & Labor Dashboard - Streamlit App
# Author: Sadie (Lamplot) Gingerich
# Description: Interactive dashboard showing national nonfarm employment, agricultural employment, and unemployment rates, with state-level unemployment comparison.
# Data sources: BLS Public API, processed into CSV files in the repository

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load Data Functions
# Load national and state data from CSVs
# Using @st.cache_data to prevent reloading on every app interaction
@st.cache_data
def load_national_data():
    """
    Load national BLS data from CSV.
    Columns include: date, nonfarm_total, ag_employment, unemployment_rate
    """
    file_path = os.path.join("data", "national_bls_data.csv")
    return pd.read_csv(file_path, parse_dates=["date"])

@st.cache_data
def load_state_data():
    """
    Load state unemployment data from CSV.
    Columns include: date, state, unemployment_rate
    """
    file_path = os.path.join("data", "state_unemployment.csv")
    return pd.read_csv(file_path, parse_dates=["date"])

# Load data into DataFrames
df_national = load_national_data()
df_state = load_state_data()

# Adding helper columns for year and month
df_national['year'] = df_national['date'].dt.year
df_national['month'] = df_national['date'].dt.month
df_state['year'] = df_state['date'].dt.year
df_state['month'] = df_state['date'].dt.month

# Page Layout
st.set_page_config(page_title="US Agriculture Employment Dashboard", layout="wide")
st.title("US Agriculture & Labor Dashboard")
st.markdown(
    """
    Interactive visualization of national nonfarm, agricultural employment, and unemployment rates,
    with state-level comparisons. Use the filters below to explore trends over time.
    """
)

# Year Filter
# Allow user to select which year(s) to display in the charts
years = df_national['year'].unique()
selected_years = st.multiselect(
    "Select year(s) to display",
    options=years,
    default=years[-1]  # default to most recent year
)
# Filter national and state DataFrames by selected years
df_national_filtered = df_national[df_national['year'].isin(selected_years)]
df_state_filtered = df_state[df_state['year'].isin(selected_years)]

# National Employment Line Chart with Seasonal Peaks
st.subheader("National Employment Trends")

# Calculate average monthly agricultural employment to identify seasonal peaks
monthly_avg_ag = df_national_filtered.groupby('month')['ag_employment'].mean()
peak_months = monthly_avg_ag.sort_values(ascending=False).head(3).index.tolist()  # top 3 peak months

# Initialize Plotly figure
fig1 = go.Figure()

# Add national nonfarm employment line
fig1.add_trace(go.Scatter(
    x=df_national_filtered['date'],
    y=df_national_filtered['nonfarm_total'],
    mode='lines',
    name='Nonfarm Total'
))

# Add national agricultural employment line
fig1.add_trace(go.Scatter(
    x=df_national_filtered['date'],
    y=df_national_filtered['ag_employment'],
    mode='lines',
    name='Agricultural Employment'
))

# Highlight top 3 peak months for agricultural employment
for month in peak_months:
    peak_dates = df_national_filtered[df_national_filtered['month'] == month]['date']
    peak_values = df_national_filtered[df_national_filtered['month'] == month]['ag_employment']
    fig1.add_trace(go.Scatter(
        x=peak_dates,
        y=peak_values,
        mode='markers',
        name=f'Peak Month {month}',
        marker=dict(size=8, color='red')
    ))

fig1.update_layout(
    title="National Nonfarm vs Agricultural Employment",
    xaxis_title="Month",
    yaxis_title="Employees"
)
st.plotly_chart(fig1, use_container_width=True)

# National Unemployment Line Chart
st.subheader("National Unemployment Rate")
fig2 = px.line(
    df_national_filtered,
    x="date",
    y="unemployment_rate",
    labels={"unemployment_rate": "Unemployment Rate (%)", "date": "Month"},
    title="National Unemployment Rate"
)
st.plotly_chart(fig2, use_container_width=True)

# State Unemployment Line Chart
st.subheader("State Unemployment Comparison")

# Allow user to select states to display
states = df_state['state'].unique().tolist()
selected_states = st.multiselect(
    "Select states to display",
    options=states,
    default=["NE", "IA", "TX", "CA", "NY"]
)

# Filter state DataFrame for selected states
df_filtered_states = df_state_filtered[df_state_filtered["state"].isin(selected_states)]

# Line chart for state unemployment
fig3 = px.line(
    df_filtered_states,
    x="date",
    y="unemployment_rate",
    color="state",
    labels={"unemployment_rate": "Unemployment Rate (%)", "date": "Month"},
    title="State Unemployment Rate Comparison"
)
st.plotly_chart(fig3, use_container_width=True)

# State Unemployment Map
st.subheader("State Unemployment Map")

# Get the most recent available date for each state
latest_dates = df_state_filtered.groupby('state')['date'].max().reset_index()
df_latest = pd.merge(df_state_filtered, latest_dates, on=['state','date'], how='inner')

# Choropleth map using Plotly
fig_map = px.choropleth(
    df_latest,
    locations="state",
    locationmode="USA-states",
    color="unemployment_rate",
    color_continuous_scale="Reds",
    scope="usa",
    labels={"unemployment_rate": "Unemployment Rate (%)"},
    title="Latest State Unemployment Rates"
)
st.plotly_chart(fig_map, use_container_width=True)

# Date Range Selector for National Date
st.subheader("Filter National Data by Date")

start_date = st.date_input("Start date", df_national_filtered["date"].min())
end_date = st.date_input("End date", df_national_filtered["date"].max())

# Filter national data by selected date range
df_national_final = df_national_filtered[
    (df_national_filtered["date"] >= pd.to_datetime(start_date)) &
    (df_national_filtered["date"] <= pd.to_datetime(end_date))
]

# Display last 10 rows of filtered data
st.markdown("### Filtered National Data Preview")
st.dataframe(df_national_final.tail(10))
