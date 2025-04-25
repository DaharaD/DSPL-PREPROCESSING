import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import os

def show_about():
    def load_data():
        Food = pd.read_excel("cleaned_hdx_hapi_food_price_lka.xlsx")
        return Food

    Food = load_data()

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
            filtered_df.sort_values("Reference_Period_End"),
            x="Reference_Period_End",
            y="Price",
            title=f"Price Trend for {selected_commodity} in {selected_region}",
            labels={"Price": "Price (LKR)", "Reference_Period_End": "Date"},
            markers=True,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")


from difflib import get_close_matches
@st.cache_data
def load_data():
    return pd.read_excel("cleaned_hdx_hapi_food_price_lka.xlsx")

data = load_data()

# Sidebar
st.sidebar.header("Commodity Filter")
commodity_names = sorted(data["Commodity_Name"].unique())
selected_commodity = st.sidebar.selectbox("Choose a Commodity", commodity_names)

filtered_data = data[data["Commodity_Name"] == selected_commodity]

st.title("About This Commodity")
st.subheader(f"Selected Commodity: {selected_commodity}")

# === Image Matching === #
image_folder = "Commodities"
valid_extensions = [".jpg", ".jpeg", ".png"]
available_images = [f for f in os.listdir(image_folder) if os.path.splitext(f)[1].lower() in valid_extensions]

# Try exact match first
def find_image(commodity_name):
    for ext in valid_extensions:
        exact_name = f"{commodity_name}{ext}"
        if exact_name in available_images:
            return os.path.join(image_folder, exact_name)

    # Fallback to fuzzy matching
    base = commodity_name.lower().replace(" ", "").replace("(", "").replace(")", "")
    candidates = {img: img.lower().replace(" ", "").replace("_", "").replace("-", "").replace("(", "").replace(")", "") for img in available_images}
    match = get_close_matches(base, candidates.values(), n=1, cutoff=0.6)
    if match:
        for original_name, cleaned in candidates.items():
            if cleaned == match[0]:
                return os.path.join(image_folder, original_name)

    return None

image_path = find_image(selected_commodity)

if image_path and os.path.exists(image_path):
    st.image(image_path, caption=selected_commodity, use_column_width=True)
else:
    st.warning("⚠ Image not available for this commodity.")

# === Show Description Table === #
if not filtered_data.empty:
    info = filtered_data.iloc[0][[
        "Market_Name", "Commodity_Category", "Price", "Unit",
        "Provider_Admin1_Name", "Provider_Admin2_Name"
    ]]
    st.markdown("Commodity Market Information")
    st.markdown(f"""
    - *Market Name*: {info['Market_Name']}
    - *Category*: {info['Commodity_Category']}
    - *Price*: {info['Price']} {info['Unit']}
    - *Region*: {info['Provider_Admin1_Name']} > {info['Provider_Admin2_Name']}
    """)
else:
    st.error("No data found for the selected commodity.")