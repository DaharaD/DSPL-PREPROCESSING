import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from dash import Dash, dcc, html, Input, Output 
import dash_bootstrap_components as dbc

Food = pd.read_excel("cleaned_hdx_hapi_food_price_lka.xlsx")

# creating interactive elements
commodity = st.sidebar.selectbox('Select Commodity', Food['Commodity_Name'].unique())
price_type = st.sidebar.selectbox('Select Price Type', Food['Price_Type'].unique())
date_range = st.sidebar.date_input('Select Date Range', [Food['Reference_Period_Start'].min(), Food['Reference_Period_End'].max()])

# Filter data based on user input
filtered_df = Food[(Food['Commodity_Name'] == commodity) & (Food['Price_Type'] == price_type) & (Food['Reference_Period_Start'] >= pd.to_datetime(date_range[0])) & (Food['Reference_Period_End'] <= pd.to_datetime(date_range[1]))]

# Display data and charts
st.subheader(f'{commodity} Prices ({price_type})')
st.dataframe(filtered_df)

fig = px.line(
    filtered_df,
    x='Reference_Period_Start',
    y='Price',
    color='Commodity_Name',
    line_group='Admin1_Name',
    title="Price Trends by Commodity and District",
    markers=True
)
st.plotly_chart(fig)

fig = px.line(
    filtered_df,
    x='Reference_Period_End',
    y='Price',
    color='Commodity_Name',
    line_group='Admin1_Name',
    title="Price Trends by Commodity and District",
    markers=True
)
st.plotly_chart(fig)


fig_bar_all = px.bar(
    filtered_df,
    x='Commodity_Name',
    y='Price',
    color='Admin1_Name',
    title="Individual Prices by Commodity and District",
    barmode='group'
)
st.plotly_chart(fig_bar_all)

fig_box = px.box(
    filtered_df,
    x='Commodity_Name',
    y='Price',
    color='Commodity_Name',
    title="Price Distribution by Commodity"
)
st.plotly_chart(fig_box)

fig_map = px.scatter_mapbox(
    filtered_df,
    lat="Latitude",
    lon="Longitude",
    color="Commodity_Name",
    size="Price",
    hover_name="Commodity_Name",
    hover_data=["Admin1_Name", "Price", "Unit"],
    zoom=6,
    height=500,
    title="Geographic Distribution of Food Prices"
)
fig_map.update_layout(mapbox_style="carto-positron")
fig_map.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
st.plotly_chart(fig_map)

commodity_counts = filtered_df['Commodity_Name'].value_counts().reset_index()
commodity_counts.columns = ['Commodity_Name', 'Count']

commodity_counts = Food['Commodity_Name'].value_counts().reset_index()
commodity_counts.columns = ['Commodity_Name', 'Count']

fig_pie = px.pie(
    commodity_counts,
    values='Count',
    names='Commodity_Name',
    title="Overall Commodity Distribution",
    hole=0.2
)
st.plotly_chart(fig_pie)

