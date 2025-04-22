import streamlit as st

def show_about():
    st.title("About This Dashboard")
    st.markdown("""
        Purpose
This dashboard is designed to provide insights into food prices across various regions in Sri Lanka. It uses data from the Humanitarian Data Exchange (HDX) to track price trends, compare prices across different commodities, and visualize geographic distributions.

Data Source
The data is sourced from the Humanitarian Data Exchange (HDX) and includes information on food prices collected from various markets across Sri Lanka. The dataset includes details such as:

Region: The administrative region where the data was collected.
Commodity: The type of food item.
Price: The price of the commodity.
Date: The date when the price was recorded.
Features
Dashboard: Explore trends and movements in food prices using interactive charts and tables.
Filters: Filter data by region, food item, and date range to customize the view.
Visualizations: View line charts, scatter plots, histograms, and more to gain insights into the data.
How to Use
Use the sidebar to navigate between the Dashboard and About pages. Apply filters to customize the data view and explore different visualizations to gain insights into food prices in Sri Lanka.

Key Metrics
Total Records: The total number of records in the dataset.
Unique Food Items: The number of unique food items covered in the dataset.
Regions Covered: The number of regions from which data has been collected.
Visualizations
Price Trends Over Time: Line charts showing the price trends of various commodities over time.
Animated Price Spread by Region: Animated scatter plots showing the price movement of commodities across different regions.
Price Distribution Histogram by Commodity: Histograms showing the distribution of standardized prices for different commodities.
Average Monthly Prices by Commodity Category: Line charts summarizing the average monthly prices of different commodity categories.
Provider Admin1 and Admin2 Distribution: Count plots showing the distribution of records by province and district.
    """)

