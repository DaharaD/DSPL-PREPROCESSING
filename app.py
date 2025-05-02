import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from PIL import Image
import base64
import os
from About import show_about
from Insights import show_Insights

# setting the backround image for the dashboard
def set_background_from_url(url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("{url}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        .block-container {{
            background-color: rgba(0, 0, 0, 0.5);
            padding: 2rem;
            border-radius: 1rem;
        }}
        h1, h2, h3, h4, h5, h6, p, label {{
            color: #ffffff !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

image_url = "https://github.com/DaharaD/DSPL-PREPROCESSING/raw/main/Images/After%20hours%20%E2%80%94%20intothelife.jpeg"
set_background_from_url(image_url)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_excel("cleaned_hdx_hapi_food_price_lka.xlsx")
    return df

Food = load_data()

# Sidebar Navigation
st.sidebar.title("Navigation")
view = st.sidebar.radio("Go to", ["About", "Dashboard", "Animations", "Insights"])

if view == "About":
    show_about()
    st.stop()

elif view == "Insights":
    show_Insights(Food) 
    st.stop()

elif view == "Animations":
    st.title("Animated Food Price Visualizations")
    st.markdown("""
    Explore dynamic visualizations that bring Sri Lanka's food price trends to life. 
    These animations reveal temporal patterns, regional variations, and commodity comparisons.
    """)

    # Creating 3 tabs for the 3 animations types wch will appear in the animations page
    tab1, tab2, tab3 = st.tabs(["Price Evolution", "Ranking Race", "Regional Waves"])
    
    with tab1:
        st.subheader("Animated Price Evolution Over Time")
        st.markdown("Watch how prices change across regions and commodities over time.")
        
        Food['Quarter'] = Food['Reference_Period_Start'].dt.to_period('Q').astype(str)
        quarterly_avg = Food.groupby(['Quarter', 'Commodity_Name', 'Admin1_Name'])['Price'].mean().reset_index()
        
        selected_commodities = st.multiselect(
            "Select commodities to highlight (optional)",
            options=sorted(Food['Commodity_Name'].unique()),
            default=[]
        )
        
        fig = px.scatter(
            quarterly_avg,
            x='Quarter',
            y='Price',
            size='Price',
            color='Commodity_Name',
            hover_name='Admin1_Name',
            animation_frame='Quarter',
            animation_group='Commodity_Name',
            size_max=45,
            title='Price Bubbles Over Time',
            height=600,
            color_discrete_sequence=px.colors.qualitative.Plotly,
            category_orders={"Quarter": sorted(quarterly_avg['Quarter'].unique())}
        )
    
        if selected_commodities:
            fig.update_traces(
                marker=dict(size=10),
                selector=lambda t: t.name not in selected_commodities
            )
            fig.update_traces(
                marker=dict(size=20, line=dict(width=2, color='DarkSlateGrey')),
                selector=lambda t: t.name in selected_commodities
            )
        
        fig.update_layout(
            xaxis={'categoryorder':'category ascending'},
            showlegend=True,
            legend_title_text='Commodities'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Price Ranking Race")
        st.markdown("Track which commodities become most expensive over time.")
        
        # Prepare monthly rankings
        monthly_rank = Food.groupby(['Commodity_Name', pd.Grouper(key='Reference_Period_Start', freq='M')])['Price'].mean().reset_index()
        monthly_rank['Month'] = monthly_rank['Reference_Period_Start'].dt.strftime('%Y-%m')
    
        top_n = st.slider("Number of top commodities to show", 5, 20, 10)
        
        top_n_rank = monthly_rank.groupby('Month').apply(lambda x: x.nlargest(top_n, 'Price')).reset_index(drop=True)
        
        fig = px.bar(
            top_n_rank,
            x='Price',
            y='Commodity_Name',
            color='Commodity_Name',
            animation_frame='Month',
            orientation='h',
            title=f'Top {top_n} Most Expensive Commodities Each Month',
            range_x=[0, top_n_rank['Price'].max()*1.1],
            height=600
        )
        fig.update_layout(
            showlegend=False,
            yaxis={'categoryorder':'total ascending'},
            xaxis_title="Price (LKR)",
            yaxis_title="Commodity"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Regional Price Change Waves")
        st.markdown("Visualize how price changes propagate across regions over time.")
        
        # Calculate price changes
        Food['Price_Change'] = Food.groupby(['Commodity_Name','Admin1_Name'])['Price'].pct_change()
        geo_data = Food.dropna(subset=['Price_Change'])
        
        # this code here to help users to select the category
        selected_category = st.selectbox(
            "Select commodity category",
            options=Food['Commodity_Category'].unique()
        )
        geo_data = geo_data[geo_data['Commodity_Category'] == selected_category]
        
        # Creating an animated map
        fig = px.scatter_geo(
            geo_data,
            lat='Latitude',
            lon='Longitude',
            size=abs(geo_data['Price_Change'])*100,
            color='Price_Change',
            hover_name='Market_Name',
            animation_frame=geo_data['Reference_Period_Start'].dt.strftime('%Y-%m'),
            projection="natural earth",
            title=f'Regional {selected_category} Price Change Intensity',
            color_continuous_scale=px.colors.diverging.RdYlGn_r,
            range_color=[-0.5, 0.5],
            scope='asia',
            height=600
        )
        fig.update_geos(
            fitbounds="locations",
            visible=False,
            resolution=50,
            showcountries=True,
            countrycolor="Black"
        )
        fig.update_layout(
            geo=dict(
                landcolor='LightGrey',
                subunitcolor="Grey",
            ),
            margin={"r":0,"t":50,"l":0,"b":0}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Animation Controls Tips")
    st.markdown("""
    - Use the play button to start/stop animations
    - Drag the slider to move to specific time periods
    - Hover over elements to see detailed information
    - Use the filters to focus on specific commodities or categories
    """)
    
    st.stop()

# Dashboard Page Content (only shown when "Dashboard" is selected)
st.title("Sri Lanka's Food Prices Uncovered")
st.markdown("Track Real-time shifts and historical trends in food prices across Sri Lanka. From urban centers to remote markets, this dashboard reveals how economic conditions and local dynamics influence the cost of everyday essentials. Powered by curated data from the Humanitarian Data Exchange (HDX), it's your window into understanding affordability, market volatility, and regional disparities at a glance.")

# Sidebar filters
st.sidebar.title("Filter Data")
locations = st.sidebar.multiselect(
    "Select Region", 
    Food['Admin1_Name'].dropna().unique(), 
    default=Food['Admin1_Name'].dropna().unique()
)
items = st.sidebar.multiselect(
    "Select Food Item", 
    Food['Commodity_Name'].dropna().unique(), 
    default=Food['Commodity_Name'].dropna().unique()
)
years = st.sidebar.slider(
    "Select Year Range", 
    int(Food['Reference_Period_Start'].dt.year.min()), 
    int(Food['Reference_Period_Start'].dt.year.max()), 
    (2023, 2024)
)

# Apply filters
filtered = Food[
    (Food['Admin1_Name'].isin(locations)) &
    (Food['Commodity_Name'].isin(items)) &
    (Food['Reference_Period_Start'].dt.year >= years[0]) &
    (Food['Reference_Period_Start'].dt.year <= years[1])
]

# Key metrics
st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(filtered))
col2.metric("Unique Food Items", filtered['Commodity_Name'].nunique())
col3.metric("Regions Covered", filtered['Admin1_Name'].nunique())

# Data Table
st.subheader("Data Table")
st.dataframe(filtered)

# Additional Interactivity
commodity = st.sidebar.selectbox('Select Commodity', Food['Commodity_Name'].unique())
price_type = st.sidebar.selectbox('Select Price Type', Food['Price_Type'].unique())
date_range = st.sidebar.date_input(
    'Select Date Range', 
    [Food['Reference_Period_Start'].min(), Food['Reference_Period_End'].max()]
)

filtered_df = Food[
    (Food['Commodity_Name'] == commodity) &
    (Food['Price_Type'] == price_type) &
    (Food['Reference_Period_Start'] >= pd.to_datetime(date_range[0])) &
    (Food['Reference_Period_End'] <= pd.to_datetime(date_range[1]))
]

# Price Change Sparlines
st.subheader("Price Trends Sparklines")
weekly = filtered_df.set_index('Reference_Period_Start').resample('W')['Price'].mean()

fig = px.line(
    weekly,
    height=150,
    title="",
    markers=True
)
fig.update_layout(showlegend=False, margin=dict(t=10,b=10,l=10,r=10))
st.plotly_chart(fig, use_container_width=True)

# Charts 
st.subheader(f' {commodity} Price Analysis ({price_type})')

# Creating 3 tabs
tab1, tab2, tab3 = st.tabs(["Trend Analysis", "Regional Comparison", "Price Distribution"])
with tab1:
    # Small multiple area charts
    fig = px.area(
        filtered_df,
        x='Reference_Period_Start',
        y='Price',
        facet_col='Admin1_Name',
        facet_col_wrap=3,  # 3 charts per row
        height=400,
        title=f"{commodity} Prices by District"
    )
    fig.update_yaxes(matches=None)  # Allow different y-scales
    st.plotly_chart(fig, use_container_width=True)
    
    # Compact stats instead of dataframe
    latest = filtered_df.nlargest(1, 'Reference_Period_Start')
    st.metric("Latest Price", 
             f"{latest['Price'].values[0]:.2f} LKR", 
             f"{latest['Admin1_Name'].values[0]}")

with tab2:
    # Enhanced regional comparison
    fig_regional = px.bar(
        filtered_df,
        x='Admin1_Name',
        y='Price',
        color='Admin1_Name',
        title=f"{commodity} Prices Across Districts",
        labels={'Price': 'Price (LKR)', 'Admin1_Name': 'District'},
        height=500
    )
    fig_regional.update_layout(showlegend=False)
    st.plotly_chart(fig_regional, use_container_width=True)
    
    # Regional stats table
    regional_stats = filtered_df.groupby('Admin1_Name')['Price'].agg(['mean', 'min', 'max'])
    st.dataframe(
        regional_stats.style.format("{:.2f}"),
        use_container_width=True
    )

with tab3:
    # Enhanced distribution view
    fig_dist = px.box(
        filtered_df,
        x='Admin1_Name',
        y='Price',
        color='Admin1_Name',
        title=f"{commodity} Price Distribution by District",
        points='all',
        height=500
    )
    fig_dist.update_layout(showlegend=False)
    st.plotly_chart(fig_dist, use_container_width=True)    
    
    # Overall stats
    st.metric("Average Price", f"{filtered_df['Price'].mean():.2f} LKR")
    st.metric("Price Range", 
             f"{filtered_df['Price'].min():.2f} - {filtered_df['Price'].max():.2f} LKR")

#Price alert system
st.subheader("Price Alert System")
alert_threshold = st.sidebar.number_input("Set price alert threshold (LKR)", min_value=0)
exceeded = filtered[filtered['Price'] > alert_threshold]
if len(exceeded) > 0:
    st.warning(f"{len(exceeded)} records exceed {alert_threshold} LKR:")
    st.dataframe(exceeded[['Commodity_Name', 'Market_Name', 'Price']].sort_values('Price', ascending=False))

# Geomap 
st.subheader("Geographic Distribution of Food Prices")
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

# Overall distribution
st.subheader("Commodity Distribution")
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


# Create simplified pie chart
st.subheader("Commodity Distribution")
px.pie(
    Food, 
    names='Commodity_Name', 
    title="Share of Each Commodity in Dataset"
).update_traces(
    textposition='inside',
    textinfo='percent+label'
)

# Simplified grouped bar chart
st.subheader("Average Prices by Region & Category")
fig = px.bar(
    filtered.groupby(['Admin1_Name', 'Commodity_Category'])['Standardized_Price'].mean().reset_index(),
    x='Admin1_Name',
    y='Standardized_Price',
    color='Commodity_Category',
    barmode='group',
    title='Average Prices Across Regions',
    labels={'Standardized_Price': 'Avg Price', 'Admin1_Name': 'Region'},
    height=500
)
fig.update_layout(
    xaxis={'categoryorder':'total descending'},
    yaxis_title="Average Standardized Price"
)
st.plotly_chart(fig, use_container_width=True)

# Create a simple heatmap
st.subheader("Market Commodity Distribution")
fig = px.density_heatmap(
    filtered,
    x='Market_Name',
    y='Commodity_Category',
    title="Commodity Availability by Market",
    height=500
)
fig.update_layout(
    xaxis_title="Market",
    yaxis_title="Commodity Category",
    xaxis={'categoryorder':'total descending'}
)
st.plotly_chart(fig, use_container_width=True)

# Top 10 volatile commodities
st.subheader("Top 10 Volatile Commodities ")
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

# Create a box plot for price distribution across markets
st.subheader("Price Distribution by Market")
fig = px.box(
    filtered,
    x="Market_Name",
    y="Price",
    title="Price Distribution Across Markets",
    height=600
)
fig.update_layout(
    xaxis_title="Market",
    yaxis_title="Price (LKR)",
    xaxis={'categoryorder':'total descending'},  # Sort by median price
    showlegend=False
)
st.plotly_chart(fig, use_container_width=True)

# Monthly trend summary
st.subheader("Monthly prices by commodity category")
monthly = filtered.groupby(["Start_Month", "Commodity_Category"])["Price_Std"].mean().reset_index()
fig6 = px.line(
    monthly, 
    x="Start_Month", 
    y="Price_Std", 
    color="Commodity_Category", 
    markers=True, 
    title="Standard Monthly Prices by Commodity Category"
)
fig6.update_layout(height=500)
st.plotly_chart(fig6, use_container_width=True)

# Price Comparison Tool
st.subheader("Price Comparison Tool")
col1, col2 = st.columns(2)
with col1:
    compare_commodity = st.selectbox("Select Commodity to Compare", Food['Commodity_Name'].unique())
with col2:
    compare_regions = st.multiselect(
        "Select Regions to Compare", 
        Food['Admin1_Name'].unique(), 
        default=Food['Admin1_Name'].unique()[:3]
    )

compare_df = Food[
    (Food['Commodity_Name'] == compare_commodity) &
    (Food['Admin1_Name'].isin(compare_regions))
]

if not compare_df.empty:
    fig_compare = px.line(
        compare_df, 
        x='Reference_Period_Start', 
        y='Price', 
        color='Admin1_Name',
        title=f'{compare_commodity} Price Comparison Across Regions',
        markers=True,
        line_shape='spline'
    )
    st.plotly_chart(fig_compare, use_container_width=True)
    
    # Add statistical summary
    st.write("Statistical Summary")
    stats = compare_df.groupby('Admin1_Name')['Price'].agg(['mean', 'median', 'std', 'min', 'max'])
    st.dataframe(stats.style.background_gradient(cmap='Blues'))
else:
    st.warning("No data available for the selected filters.")

# Interactive Correlation Matrix
st.subheader("Price Correlations Between Commodities")
corr_region = st.selectbox(
    "Select Region for Correlation Analysis", 
    Food['Admin1_Name'].unique()
)

# Pivot data for correlation
corr_df = Food[Food['Admin1_Name'] == corr_region].pivot_table(
    index='Reference_Period_Start',
    columns='Commodity_Name',
    values='Price',
    aggfunc='mean'
).corr()

# Create heatmap
fig_corr = px.imshow(
    corr_df,
    labels=dict(x="Commodity", y="Commodity", color="Correlation"),
    x=corr_df.columns,
    y=corr_df.columns,
    color_continuous_scale='RdBu',
    zmin=-1,
    zmax=1,
    title=f"Price Correlation Matrix for {corr_region}"
)
fig_corr.update_layout(height=800)
st.plotly_chart(fig_corr, use_container_width=True)


st.subheader("Price Trends Overtime")
# Limit to 3 commodities max
selected_commodities = st.multiselect(
    "Select commodities (max 3)",
    options=sorted(filtered['Commodity_Name'].unique()),
    default=sorted(filtered['Commodity_Name'].unique())[:2],
    max_selections=3
)

if selected_commodities:
    # Aggregate to monthly national averages
    compare_data = filtered[filtered['Commodity_Name'].isin(selected_commodities)]
    compare_data['Month'] = compare_data['Reference_Period_Start'].dt.to_period('M').astype(str)
    national_avg = compare_data.groupby(['Month', 'Commodity_Name'])['Price'].mean().reset_index()
    
    fig = px.line(
        national_avg,
        x='Month',
        y='Price',
        color='Commodity_Name',
        line_dash='Commodity_Name',
        markers=True,
        title='National Average Price Comparison',
        labels={'Price': 'Price (LKR)'},
        template='plotly_white'
    )
    fig.update_layout(
        hovermode='x unified',
        legend_title_text='Commodity',
        xaxis=dict(tickangle=45),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please select at least one commodity")

# Geographic Map with Month & Commodity Category Filters
st.subheader("Interactive Price Map by Month & Commodity Category")
col1, col2 = st.columns(2)
with col1:
    selected_month = st.select_slider(
        "Select Month",
        options=sorted(filtered['Start_Month'].unique()),
        value=filtered['Start_Month'].min()
    )
with col2:
    selected_category = st.selectbox(
        "Select Commodity Category",
        options=filtered['Commodity_Category'].unique()
    )
month_category_filtered = filtered[filtered['Commodity_Category'] == selected_category]
if selected_month in month_category_filtered['Start_Month'].unique():
    month_category_filtered = month_category_filtered[month_category_filtered['Start_Month'] == selected_month]
else:
    st.warning(f"No {selected_category} data for month {selected_month}. Showing all months.")
month_category_filtered['Size_Adjusted'] = month_category_filtered['Price'] * 10  # Adjust multiplier
if not month_category_filtered.empty:
    fig_enhanced_map = px.scatter_mapbox(
        month_category_filtered,
        lat="Latitude",
        lon="Longitude",
        color="Commodity_Name",
        size="Size_Adjusted", 
        hover_name="Market_Name",
        hover_data=["Price", "Unit", "Reference_Period_Start"],
        zoom=6,
        height=600,
        title=f"Prices in {selected_category} (Month: {selected_month})",
    )
    fig_enhanced_map.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
    )
    st.plotly_chart(fig_enhanced_map, use_container_width=True)
else:
    st.error("No data available for the selected filters.")

# Top 10 Districts by Commodity Category Distribution (Interactive)
st.subheader("Top 10 Districts by Commodity Category")
top_admin2 = Food['Provider_Admin2_Name'].value_counts().nlargest(10).index
filtered_df = Food[Food['Provider_Admin2_Name'].isin(top_admin2)]

# Plot 1: Stacked bar chart by commodity category
fig1 = px.bar(
    filtered_df,
    y='Provider_Admin2_Name',
    color='Commodity_Category',
    title='Commodity Distribution in Top 10 Districts',
    labels={'Provider_Admin2_Name': 'District', 'count': 'Number of Records'},
    category_orders={'Provider_Admin2_Name': top_admin2},
    color_discrete_sequence=px.colors.qualitative.Pastel,
    height=500
)
fig1.update_layout(barmode='stack', yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig1, use_container_width=True)


#Commodity distribution across provinces
st.subheader("Commodity Distribution Across Provinces")
fig = px.bar(
    Food,
    x='Provider_Admin1_Name',
    color='Commodity_Category',
    title='Food Commodities by Province',
    labels={'Provider_Admin1_Name': 'Province', 'count': 'Number of Records'},
    color_discrete_sequence=px.colors.qualitative.Pastel,
    height=500
)
fig.update_layout(
    barmode='stack',
    xaxis={'categoryorder':'total descending'},
    hovermode='x unified',
    legend_title_text='Commodity Category'
)
st.plotly_chart(fig, use_container_width=True)


fig2 = px.bar(
    filtered_df['Provider_Admin2_Name'].value_counts().reset_index(),
    y='Provider_Admin2_Name',
    x='count',
    title='Total Records in Top 10 Districts',
    labels={'Provider_Admin2_Name': 'District', 'count': 'Number of Records'},
    color='count',
    color_continuous_scale='Bluered',
    height=500
)
fig2.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Market Price Comparison")
market_prices = filtered.groupby(['Market_Name', 'Commodity_Category'])['Price'].mean().unstack()
fig = px.imshow(
    market_prices,
    labels=dict(x="Category", y="Market", color="Price"),
    color_continuous_scale='Viridis',
    aspect="auto"
)
st.plotly_chart(fig, use_container_width=True)

# price characteristics by category chart
st.subheader("Price Characteristics by Category")
radar_data = filtered.groupby('Commodity_Category').agg({
    'Price': 'mean',
    'Price_Std': 'mean',
    'Price_Median': 'mean'
}).reset_index()
fig = px.line_polar(
    radar_data, 
    r='Price', 
    theta='Commodity_Category',
    line_close=True,
    template="plotly_dark"
)
st.plotly_chart(fig, use_container_width=True)

# regional affordability chart
avg_income = 50000 
filtered['Price_to_Income_Ratio'] = filtered['Price'] / avg_income * 100
st.subheader("Regional Affordability compared with income")
region_affordability = filtered.groupby('Admin1_Name').agg({
    'Price': 'median',
    'Price_to_Income_Ratio': 'median'
}).reset_index()
fig = px.scatter(
    region_affordability,
    x='Price',
    y='Price_to_Income_Ratio',
    size='Price',
    color='Admin1_Name',
    hover_name='Admin1_Name',
    log_x=True,
    size_max=40
)
st.plotly_chart(fig, use_container_width=True)

# Ranking food affordability from worst to best (districts) 
ranking = Food.groupby('Admin2_Name')['Price'].mean().reset_index()
st.subheader('Affordability Ranking compared with price')
fig = px.bar(ranking.sort_values('Price', ascending=False),
             x='Admin2_Name',
             y='Price',
             color='Price')
st.plotly_chart(fig, use_container_width=True)

# Calculate yearly volatility (simplified)
Food['Year'] = pd.to_datetime(Food['Reference_Period_Start']).dt.year
volatility = Food.groupby('Year')['Price'].std() / Food.groupby('Year')['Price'].mean()
volatility = volatility.sort_values(ascending=False).reset_index(name='Volatility')

st.subheader('Yearly Price Volatility Ranking')
fig = px.bar(volatility, 
             x='Year', 
             y='Volatility',
             color='Volatility',
             color_continuous_scale='reds',
             text='Volatility')
fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig.update_layout(yaxis_title='Price Volatility Index')
st.plotly_chart(fig, use_container_width=True)
st.dataframe(volatility.style.background_gradient(cmap='Reds'))

# All 11 urban districts
urban = ['Colombo', 'Gampaha', 'Kandy', 'Kalutara',
         'Galle', 'Matara', 'Negombo', 'Kurunegala',
         'Anuradhapura', 'Ratnapura', 'Badulla']

Food['Type'] = Food['Admin2_Name'].apply(lambda x: 'Urban' if x in urban else 'Rural')
prices = Food.groupby('Type')['Price'].median()

# Display results
st.subheader('Urban vs Rural Price Comparison')
st.bar_chart(prices)
st.write(f"Urban Median: LKR {prices['Urban']:,.0f}")
st.write(f"Rural Median: LKR {prices['Rural']:,.0f}")
st.write(f"Difference: LKR {prices['Rural']-prices['Urban']:,.0f}")

# Add near data table
st.download_button("Export Filtered Data", filtered.to_csv(), "food_prices.csv")

