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
