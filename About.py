import streamlit as st

def show_about():
    st.title("About This Dashboard")
    st.markdown("""
        This interactive dashboard provides a deep dive into **food price trends in Sri Lanka**.
        
        **Features:**
        - Filter by region, commodity, year
        - Animated plots and maps
        - Volatility and distribution insights
    """)
