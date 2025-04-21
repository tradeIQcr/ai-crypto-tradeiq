import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objs as go
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="📈 AI Crypto TradeIQ Dashboard",
    layout="wide",
    page_icon="📈"
)

# Custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    .stAlert {
        padding: 0.5rem;
    }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📈 AI Crypto TradeIQ Dashboard")
st.markdown("""
    *A comprehensive trading dashboard with technical indicators for cryptocurrencies and stocks.*
""")

# Sidebar for user inputs
with st.sidebar:
    st.header("Settings")
    symbol = st.text_input("Enter symbol (e.g., BTC-USD, ETH-USD, AAPL):", "BTC-USD").upper()
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", datetime(2022, 1, 1))
    with col2:
        end_date = st.date_input("End date", datetime.today())
    
    st.markdown("---")
    st.markdown("**Technical Indicators**")
    show_rsi = st.checkbox("RSI", True)
    show_macd = st.checkbox("MACD", True)
    show_bb = st.checkbox("Bollinger Bands", True)

# Data loading with progress and error handling
@st.cache_data(ttl=3600)
def load_data(symbol, start_date, end_date):
    try:
        with st.spinner(f"Loading data for {symbol}..."):
            data = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                progress=False
            )
            if data.empty:
                raise ValueError("No data returned for this symbol/date range")
            return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

data = load_data(symbol, start_date, end_date)

if data is None:
    st.stop()

# Data validation
if data.empty or "Close" not in data.columns:
    st.error("No valid data found. Try a different symbol or date range.")
    st.stop()

# Convert to 1D Series for ta library
close_series = data["Close"].squeeze()  # This converts to 1D Series

# Drop NaN rows and ensure we have enough data
data = data.dropna()
if len(data) < 20:
    st.warning("Insufficient data points for accurate technical analysis. Try a longer date range.")
    st.stop()

# Calculate indicators with proper 1D data
def calculate_indicators(data, close_series):
    # RSI
    if show_rsi:
        try:
            data["RSI"] = ta.momentum.RSIIndicator(close=close_series, window=14).rsi()
        except Exception as e:
            st.warning(f"RSI calculation failed: {e}")
            data["RSI"] = None
    
    # MACD
    if show_macd:
        try:
            macd = ta.trend.MACD(close=close_series, window_slow=26, window_fast=12, window_sign=9)
            data["MACD"] = macd.macd()
            data["MACD_signal"] = macd.macd_signal()
            data["MACD_hist"] = macd.macd_diff()
        except Exception as e:
            st.warning(f"MACD calculation failed: {e}")
            data["MACD"] = data["MACD_signal"] = data["MACD_hist"] = None
    
    # Bollinger Bands
    if show_bb:
        try:
            bb = ta.volatility.BollingerBands(close=close_series, window=20, window_dev=2)
            data["BB_upper"] = bb.bollinger_hband()
            data["BB_middle"] = bb.bollinger_mavg()
            data["BB_lower"] = bb.bollinger_lband()
        except Exception as e:
            st.warning(f"Bollinger Bands calculation failed: {e}")
            data["BB_upper"] = data["BB_middle"] = data["BB_lower"] = None
    
    return data

data = calculate_indicators(data, close_series)

# Main dashboard layout
tab1, tab2 = st.tabs(["📊 Price Analysis", "📈 Indicators"])

with tab1:
    st.subheader(f"{symbol} Price Analysis")
    
    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(
        x=data.index,
        y=data["Close"],
        name="Close Price",
        line=dict(color='#1f77b4', width=2)
    ))
    
    if show_bb and "BB_upper" in data.columns and data["BB_upper"].notnull().any():
        fig_price.add_trace(go.Scatter(
            x=data.index,
            y=data["BB_upper"],
            name="BB Upper",
            line=dict(color='rgba(255, 0, 0, 0.3)', width=1)
        ))
        fig_price.add_trace(go.Scatter(
            x=data.index,
            y=data["BB_middle"],
            name="BB Middle",
            line=dict(color='rgba(0, 0, 255, 0.3)', width=1)
        ))
        fig_price.add_trace(go.Scatter(
            x=data.index,
            y=data["BB_lower"],
            name="BB Lower",
            line=dict(color='rgba(0, 255, 0, 0.3)', width=1),
            fill='tonexty',
            fillcolor='rgba(255, 0, 0, 0.1)'
        ))
    
    fig_price.update_layout(
        xaxis_title="Date",
        yaxis_title="Price",
        height=500,
        hovermode="x unified"
    )
    st.plotly_chart(fig_price, use_container_width=True)

with tab2:
    if show_rsi and "RSI" in data.columns and data["RSI"].notnull().any():
        st.subheader("Relative Strength Index (RSI)")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(
            x=data.index,
            y=data["RSI"],
            name="RSI",
            line=dict(color='purple', width=2)
        ))
        fig_rsi.add_hline(y=70, line_dash="dot", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dot", line_color="green")
        fig_rsi.update_layout(
            xaxis_title="Date",
            yaxis_title="RSI",
            height=400,
            yaxis_range=[0, 100]
        )
        st.plotly_chart(fig_rsi, use_container_width=True)
    
    if show_macd and "MACD" in data.columns and data["MACD"].notnull().any():
        st.subheader("Moving Average Convergence Divergence (MACD)")
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(
            x=data.index,
            y=data["MACD"],
            name="MACD",
            line=dict(color='blue', width=2)
        ))
        fig_macd.add_trace(go.Scatter(
            x=data.index,
            y=data["MACD_signal"],
            name="Signal Line",
            line=dict(color='orange', width=2)
        ))
        colors = ['green' if val >= 0 else 'red' for val in data["MACD_hist"]]
        fig_macd.add_trace(go.Bar(
            x=data.index,
            y=data["MACD_hist"],
            name="Histogram",
            marker_color=colors,
            opacity=0.5
        ))
        fig_macd.update_layout(
            xaxis_title="Date",
            yaxis_title="MACD",
            height=400
        )
        st.plotly_chart(fig_macd, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: grey;">
        <p>AI Crypto TradeIQ Dashboard • Data from Yahoo Finance</p>
    </div>
""", unsafe_allow_html=True)        
