import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def show_Insights(Food):
    st.title("Quick Insights For Policy Makers")
    st.markdown("Data Driven Quick Insights for Policy Makers")
    
    # Adding side bar filters
    st.sidebar.header("Filters For Top Trends In Tab 2")
    selected_commodities = st.sidebar.multiselect(
        "Select Commodities",
        options=Food['Commodity_Name'].unique(),
        default=Food['Commodity_Name'].unique()
    )
    
    # Applying filters
    filtered_data = Food[
        (Food['Commodity_Name'].isin(selected_commodities)) 
    ]
    
    # Creating and adding 6 tabs for policy makers to make quick decisions
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Price Alerts", 
        "Top Trends", 
        "Affordability",
        "Volatility",
        "Staple Foods",
        "Affordability Alerts"
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

    with tab6:
        st.header("Food Insecurity and Starvation Risk")
        st.subheader("Based on food prices vs. local income (UN/WB standards)")
        
        # Constants (adjust these for your country)
        DAILY_INCOME = 500  # Average daily wage in LKR
        FOOD_SPENDING_LIMIT = 0.3  # UN's 30% threshold
        
        def calculate_risk(data, region_type):
            # 1. Get average prices per region
            avg_prices = data.groupby([region_type, 'Commodity_Name'])['Price'].mean()
            
            # 2. Calculate risk: (monthly food cost) / (30% of monthly income)
            monthly_income = DAILY_INCOME * 30
            risk = (avg_prices / monthly_income) / FOOD_SPENDING_LIMIT
            
            # 3. Get top 5 riskiest regions
            top_risks = risk.groupby(region_type).mean().nlargest(5).clip(0, 1)
            
            return top_risks.to_frame('Risk %')
        
        # Display in 3 columns
        cols = st.columns(3)
        regions = [
            ('Market_Name', 'Riskiest Markets', 'Purples'),
            ('Admin2_Name', 'Riskiest Districts', 'Oranges'),
            ('Admin1_Name', 'Riskiest Provinces', 'Greens')
        ]
        
        for i, (region_col, title, color) in enumerate(regions):
            with cols[i]:
                st.markdown(f"**{title}**")
                risk_df = calculate_risk(filtered_data, region_col)
                st.dataframe(
                    risk_df.style.format("{:.0%}").background_gradient(color),
                    height=200
                )

    # Key descriptions for policy makers for easy understanding
    st.sidebar.markdown("Policy Insights")
    st.sidebar.markdown("""
    - Which prices need urgent attention
    - Long-term trends of essentials
    - Most burdensome foods for poor
    - Markets needing stabilization
    - Staple food affordability
    - Possibility of the population to starve based on UN/WB Standards)
    """)