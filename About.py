import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import os
from difflib import get_close_matches

def show_about():
    @st.cache_data
    def load_data():
        return pd.read_excel("cleaned_hdx_hapi_food_price_lka.xlsx")

    Food = load_data()

    st.title("Inside Sri Lanka’s Food Price Pulse")
    st.markdown("""
       Welcome to the Sri Lanka Food Prices Dashboard – a powerful, interactive tool designed to explore and analyze food price trends across the country. Powered by data from the Humanitarian Data Exchange (HDX), this platform helps policymakers, researchers, and the public make sense of how prices shift across regions, commodities, and time.
       From dynamic charts to image-based commodity insights, this dashboard transforms raw data into meaningful, actionable information—with clarity, simplicity, and style.
    """)

    st.subheader("Core")
    st.markdown("""
    - Interactive charts including line graphs, heatmaps, and bar charts
    - Filters by region, commodity, and unit
    - Monthly and yearly food price trend analysis
    - Automatic image matching with detailed commodity information
    - Real-time price statistics including average, minimum, and maximum values
    - Option to download filtered datasets
    - Optimized performance with fast load times using caching
    - Clean and intuitive multi-page navigation
    """)

    st.divider()

    st.subheader("Sample Visualization")

    # Dropdown filters
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

    st.divider()
    
    #Commodity Information Section 
    st.title("Commodity Details")
    st.subheader(f"Detailed Information for: {selected_commodity}")
    
    # Image Matching
    image_folder = "Commodities"
    valid_extensions = [".jpg", ".jpeg", ".png"]
    
    try:
        available_images = [f for f in os.listdir(image_folder) 
                          if os.path.splitext(f)[1].lower() in valid_extensions]
    except FileNotFoundError:
        st.error(f"Image folder '{image_folder}' not found!")
        available_images = []

    def find_image(commodity_name):
        for ext in valid_extensions:
            exact_name = f"{commodity_name}{ext}"
            if exact_name in available_images:
                return os.path.join(image_folder, exact_name)

        base = commodity_name.lower().replace(" ", "").replace("(", "").replace(")", "")
        candidates = {
            img: img.lower().replace(" ", "").replace("_", "").replace("-", "").replace("(", "").replace(")", "") 
            for img in available_images
        }
        match = get_close_matches(base, candidates.values(), n=1, cutoff=0.6)
        if match:
            for original_name, cleaned in candidates.items():
                if cleaned == match[0]:
                    return os.path.join(image_folder, original_name)
        return None

    image_path = find_image(selected_commodity)

    col_img, col_info = st.columns([1, 2])
    
    with col_img:
        if image_path and os.path.exists(image_path):
            st.image(image_path, caption=selected_commodity, use_column_width=True)
        else:
            st.warning("Image not available for this commodity.")

    #Description Table
    with col_info:
        commodity_data = Food[Food["Commodity_Name"] == selected_commodity]
        
        if not commodity_data.empty:
            latest_entry = commodity_data.sort_values("Reference_Period_Start", ascending=False).iloc[0]
            
            st.markdown("Market Information")
            st.markdown(f"""
            - **Market Name**: {latest_entry['Market_Name']}
            - **Category**: {latest_entry['Commodity_Category']}
            - **Current Price**: {latest_entry['Price']} {latest_entry['Unit']}
            - **Region**: {latest_entry['Provider_Admin1_Name']} > {latest_entry['Provider_Admin2_Name']}
            - **Last Updated**: {pd.to_datetime(latest_entry['Reference_Period_Start']).strftime('%Y-%m-%d')}
            """)
            
            # Price statistics
            avg_price = round(commodity_data['Price'].mean(), 2)
            min_price = commodity_data['Price'].min()
            max_price = commodity_data['Price'].max()
            
            st.markdown("Price Statistics")
            st.markdown(f"""
            - **Average Price**: {avg_price} {latest_entry['Unit']}
            - **Minimum Price**: {min_price} {latest_entry['Unit']}
            - **Maximum Price**: {max_price} {latest_entry['Unit']}
            """)
        else:
            st.error("No data found for the selected commodity.")

    # Additional images section
    st.markdown("Additional Images")
    matching_images = [
        os.path.join(image_folder, img) for img in available_images
        if selected_commodity.lower().replace(" ", "") in img.lower().replace(" ", "")
    ]
    
    if matching_images:
        cols = st.columns(min(3, len(matching_images)))
        for idx, img_path in enumerate(matching_images):
            with cols[idx % len(cols)]:
                st.image(img_path, use_column_width=True)
    else:
        st.info("No additional images available for this commodity.")

if __name__ == "__main__":
    st.set_page_config(page_title="About | Food Prices Dashboard", layout="centered")
    show_about()

