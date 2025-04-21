import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from dash import Dash, dcc, html, Input, Output 
import dash_bootstrap_components as dbc

Food = pd.read_excel("cleaned_hdx_hapi_food_price_lka.xlsx")

from PIL import Image
import base64
import os

# Page config
st.set_page_config(
    page_title="Sri Lanka Food Price Dashboard",
    page_icon="🌾",
    layout="wide",
)

# Set background image
def set_background(image_file):
    with open(image_file, "rb") as img:
        encoded_string = base64.b64encode(img.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded_string}");
                background-size: cover;
                background-attachment: fixed;
            }}
            .block-container {{
                background-color: rgba(139, 0, 0, 0.9);
                padding: 2rem;
                border-radius: 1rem;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

if os.path.exists("assets/background.jpg"):
    set_background("assets/background.jpg")


# Sidebar filters
st.sidebar.title("Filter Data")
locations = st.sidebar.multiselect("Select Region", Food['Admin1_Name'].dropna().unique(), default=Food['Admin1_Name'].dropna().unique())
items = st.sidebar.multiselect("Select Food Item", Food['Commodity_Name'].dropna().unique(), default=Food['Commodity_Name'].dropna().unique())
years = st.sidebar.slider("Select Year Range", int(Food['Reference_Period_Start'].dt.year.min()), int(Food['Reference_Period_Start'].dt.year.max()), (2015, 2024))

# Apply filters
filtered = Food[
    (Food['Admin1_Name'].isin(locations)) &
    (Food['Commodity_Name'].isin(items)) &
    (Food['Reference_Period_Start'].dt.year >= years[0]) &
    (Food['Reference_Period_Start'].dt.year <= years[1])
]

st.title("Sri Lanka Food Price Dashboard")
st.markdown("Explore trends and movements in food prices across Sri Lanka using data from the Humanitarian Data Exchange (HDX).")

# Key metrics
st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(filtered))
col2.metric("Unique Food Items", filtered['Commodity_Name'].nunique())
col3.metric("Regions Covered", filtered['Admin1_Name'].nunique())

# Line chart
st.subheader("Price Trends Over Time")
fig1 = px.line(filtered, x='Reference_Period_Start', y='Price', color='Commodity_Category', line_group='Admin1_Name', hover_data=['Unit'], markers=True)
fig1.update_layout(height=500)
st.plotly_chart(fig1, use_container_width=True)

# Animated scatter
st.subheader("Animated Price Spread by Region")
animated_fig = px.scatter(
    filtered,
    x="Admin1_Name",
    y="Price",
    animation_frame=filtered["Reference_Period_Start"].dt.strftime("%Y-%m"),
    color="Commodity_Name",
    size="Price",
    hover_name="Commodity_Name",
    title="Price Movement Over Time",
    size_max=50
)
st.plotly_chart(animated_fig, use_container_width=True)

# Data Explorer
st.subheader("Data Table")
st.dataframe(filtered)


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

heat = filtered.groupby(['Admin1_Name', 'Commodity_Category'])['Standardized_Price'].mean().reset_index()
fig2 = px.density_heatmap(
    heat,
    x="Admin1_Name",
    y="Commodity_Category",
    z="Standardized_Price",
    color_continuous_scale="Reds",
    title="Average Prices by Region and Commodity"
)
fig2.update_layout(height=600)
st.plotly_chart(fig2, use_container_width=True)

fig3 = px.box(
    filtered,
    x="Market_Name",
    y="Standardized_Price",
    color="Commodity_Category",
    points="all",
    title="Market-Wise Price Spread"
)
fig3.update_layout(xaxis_tickangle=-45, height=600)
st.plotly_chart(fig3, use_container_width=True)

volatility = filtered.groupby("Commodity_Name")["Price_Std"].mean().sort_values(ascending=False).head(10).reset_index()
fig4 = px.bar(
    volatility,
    x="Commodity_Name",
    y="Price_Std",
    color="Commodity_Name",
    title="Top 10 Most Volatile Commodities (Based on Std Dev)"
)
fig4.update_layout(height=500)
st.plotly_chart(fig4, use_container_width=True)

fig5 = px.histogram(
    filtered,
    x="Standardized_Price",
    color="Commodity_Name",
    nbins=40,
    title="Price Distribution Histogram by Commodity"
)
fig5.update_layout(height=500)
st.plotly_chart(fig5, use_container_width=True)

monthly = filtered.groupby(["Start_Month", "Commodity_Category"])["Price_Mean"].mean().reset_index()
fig6 = px.line(
    monthly,
    x="Start_Month",
    y="Price_Mean",
    color="Commodity_Category",
    markers=True,
    title="Average Monthly Prices by Commodity Category"
)
fig6.update_layout(height=500)
st.plotly_chart(fig6, use_container_width=True)



