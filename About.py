import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import os

def load_data():
    Food = pd.read_excel("cleaned_hdx_hapi_food_price_lka.xlsx")
    return Food

Food = load_data()

def show_about():
    st.title("About This Dashboard")
    st.markdown("""
       This interactive dashboard visualizes food price trends in Sri Lanka using data from the Humanitarian Data Exchange (HDX). 
                It enables users to explore price fluctuations by region, commodity, and time period. Key features include 
                animated plots, heatmaps, interactive filters, and geographic distributions, offering valuable insights for policymakers, researchers, and the public.
    """)

    st.subheader("Key Features")
    st.markdown("""
    - Interactive visualizations (line charts, heatmaps, bar charts)
    - Region and commodity filters
    - Monthly and yearly price comparisons
    - Download options for filtered data
    - Clean, responsive layout with multi-page navigation
    """)

    st.divider()

    st.subheader("Sample Visualization")

    # Dropdown filters for demo plot
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_region = st.selectbox("Select a Region", sorted(Food["Admin1_Name"].dropna().unique()))

    with col2:
        selected_commodity = st.selectbox("Select a Commodity", sorted(Food["Commodity_Name"].dropna().unique()))

    with col3:
        selected_unit = st.selectbox("Select a Unit", sorted(Food["Unit"].dropna().unique()))

# Filter data
    filtered_df = Food[(Food["Admin1_Name"] == selected_region) & (Food["Commodity_Name"] == selected_commodity)]

    if not filtered_df.empty:
        fig = px.line(
            filtered_df.sort_values("Reference_Period_Start"),
            x="Reference_Period_Start",
            y="Price",
            title=f"Price Trend for {selected_commodity} in {selected_region}",
            labels={"Price": "Price (LKR)", "Reference_Period_Start": "Date"},
            markers=True,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

# Filter data
    filtered_df = Food[(Food["Admin1_Name"] == selected_region) & (Food["Commodity_Name"] == selected_commodity)]

    if not filtered_df.empty:
        fig = px.line(
            filtered_df.sort_values("Reference_Period_Start"),
            x="Reference_Period_Start",
            y="Price",
            title=f"Price Trend for {selected_commodity} in {selected_region}",
            labels={"Price": "Price (LKR)", "Reference_Period_Start": "Date"},
            markers=True,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")