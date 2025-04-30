import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def show_Insights(Food):
    st.title("Quick Insights For Policy Makers")
    st.markdown("Data Driven Quick Insights for Policy Makers")
    
    # Converting data colums to ensure proper format 
    Food['Reference_Period_Start'] = pd.to_datetime(Food['Reference_Period_Start'])
    
    # Adding side bar filters
    st.sidebar.header("Filters")
    selected_commodities = st.sidebar.multiselect(
        "Select Commodities",
        options=Food['Commodity_Name'].unique(),
        default=Food['Commodity_Name'].unique()
    )
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=[Food['Reference_Period_Start'].min(), Food['Reference_Period_Start'].max()],
        min_value=Food['Reference_Period_Start'].min(),
        max_value=Food['Reference_Period_Start'].max()
    )
    
    # Applying filters
    filtered_data = Food[
        (Food['Commodity_Name'].isin(selected_commodities)) &
        (Food['Reference_Period_Start'] >= pd.to_datetime(date_range[0])) &
        (Food['Reference_Period_Start'] <= pd.to_datetime(date_range[1]))
    ]
    
    # Creating and adding 5 tabs for policy makers to make quick decisions
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Price Alerts", 
        "Top Trends", 
        "Affordability",
        "Volatility",
        "Staple Foods"
    ])
    
    with tab1:
        st.header("Critical Price Changes (Last 6 Months)")
        recent = filtered_data[filtered_data['Reference_Period_Start'] >= datetime.now() - pd.DateOffset(months=6)]
        if not recent.empty:
            changes = recent.groupby('Commodity_Name')['Price'].agg(['first','last'])
            changes['change'] = ((changes['last'] - changes['first'])/changes['first'])*100
            top5 = changes.nlargest(5, 'change').reset_index()
            
            fig = px.bar(top5, y='Commodity_Name', x='change', 
                        color='change', color_continuous_scale='reds',
                        title="Biggest Price Increases (%)",
                        labels={'change': 'Price Increase %'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for the selected filters and time period")
    
    with tab2:
        st.header("Price Trends")
        # yearly averages
        yearly_avg = filtered_data.groupby(
            [filtered_data['Reference_Period_Start'].dt.year, 'Commodity_Name']
        )['Price'].mean().reset_index()
        
        # creating a line chart
        fig = px.line(yearly_avg, 
                     x='Reference_Period_Start', 
                     y='Price', 
                     color='Commodity_Name',
                     title="Yearly Price Changes")
        st.plotly_chart(fig)
    
    with tab3:
        st.header("Essential Food Affordability")
        if not filtered_data.empty:
            # Calculate days of wages needed (assuming 500 LKR daily wage)
            filtered_data['days_wage'] = (filtered_data['Price'] / 500) * 30
            
            fig = px.box(filtered_data, x='Commodity_Name', y='days_wage',
                        color='Commodity_Name',
                        title="Days of Wages Needed to Buy Essentials",
                        labels={'days_wage': 'Days of wages needed', 'Commodity_Name': 'Commodity'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for the selected filters")
    
    with tab4:
        st.header("Market Volatility Index")
        if not filtered_data.empty:
            volatility = filtered_data.groupby('Commodity_Name')['Price'].std().nlargest(10).reset_index()
            
            fig = px.bar(volatility, x='Price', y='Commodity_Name',
                        color='Price', orientation='h',
                        color_continuous_scale='thermal',
                        title="Most Volatile Commodities",
                        labels={'Price': 'Price Standard Deviation'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for the selected filters")
    
    with tab5:
        st.header("Staple Food Prices")
        staples = filtered_data[filtered_data['Commodity_Category'].isin(['Cereals and Tubers', 'Oil and Fats'])]
        if not staples.empty:
            latest = staples.sort_values('Reference_Period_Start').groupby('Commodity_Name').last()
            
            fig = px.treemap(latest.reset_index(),
                            path=['Commodity_Name'],
                            values='Price',
                            color='Price',
                            title="Current Staple Food Prices",
                            hover_data=['Price'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No staple food data available for the selected filters")

    # Key descriptions for policy makers for easy understanding
    st.sidebar.markdown("Policy Insights")
    st.sidebar.markdown("""
    - Which prices need urgent attention
    - Long-term trends of essentials
    - Most burdensome foods for poor
    - Markets needing stabilization
    - Staple food affordability
    """)