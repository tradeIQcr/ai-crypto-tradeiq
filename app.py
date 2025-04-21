import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objs as go

st.set_page_config(page_title="AI Crypto TradeIQ", layout="wide")

st.title("📈 AI Crypto TradeIQ Dashboard")

# User input
symbol = st.text_input("Enter a symbol (e.g., BTC-USD, ETH-USD, AAPL):", "BTC-USD")
start_date = st.date_input("Start date", pd.to_datetime("2022-01-01"))
end_date = st.date_input("End date", pd.to_datetime("today"))

# Download data
try:
    data = yf.download(symbol, start=start_date, end=end_date)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Validate data
if data.empty or "Close" not in data.columns:
    st.error("No valid data found. Try a different symbol or date range.")
    st.stop()

close_series = data["Close"]
if data.empty or "Close" not in data.columns or data["Close"].dropna().empty:
    st.error("No valid data available to calculate indicators. Try a different date or symbol.")
    st.stop()

    

# Drop NaN rows
data.dropna(inplace=True)

# Calculate indicators with error handling
try:
    data["RSI"] = ta.momentum.RSIIndicator(close=data["Close"]).rsi()
except Exception as e:
    st.warning(f"RSI calculation failed: {e}")
    data["RSI"] = None

try:
    macd = ta.trend.MACD(data["Close"])
    data["MACD"] = macd.macd()
    data["MACD_signal"] = macd.macd_signal()
except Exception as e:
    st.warning(f"MACD calculation failed: {e}")
    data["MACD"] = data["MACD_signal"] = None

try:
    bb = ta.volatility.BollingerBands(close=data["Close"])
    data["BB_upper"] = bb.bollinger_hband()
    data["BB_lower"] = bb.bollinger_lband()
except Exception as e:
    st.warning(f"Bollinger Bands calculation failed: {e}")
    data["BB_upper"] = data["BB_lower"] = None

# Plot price with Bollinger Bands
st.subheader("Price Chart with Bollinger Bands")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close Price"))
if "BB_upper" in data.columns and data["BB_upper"].notnull().any():
    fig.add_trace(go.Scatter(x=data.index, y=data["BB_upper"], name="BB Upper", line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=data.index, y=data["BB_lower"], name="BB Lower", line=dict(dash='dot')))
fig.update_layout(xaxis_title="Date", yaxis_title="Price", height=400)
st.plotly_chart(fig, use_container_width=True)

# Plot RSI
if "RSI" in data.columns and data["RSI"].notnull().any():
    st.subheader("RSI Indicator")
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=data.index, y=data["RSI"], name="RSI"))
    fig_rsi.add_hline(y=70, line_dash="dot", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dot", line_color="green")
    fig_rsi.update_layout(xaxis_title="Date", yaxis_title="RSI", height=300)
    st.plotly_chart(fig_rsi, use_container_width=True)

# Plot MACD
if "MACD" in data.columns and data["MACD"].notnull().any():
    st.subheader("MACD Indicator")
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=data.index, y=data["MACD"], name="MACD"))
    fig_macd.add_trace(go.Scatter(x=data.index, y=data["MACD_signal"], name="Signal Line"))
    fig_macd.update_layout(xaxis_title="Date", yaxis_title="MACD", height=300)
    st.plotly_chart(fig_macd, use_container_width=True)

st.success("✅ App loaded successfully. Use the sidebar to test other tickers.")
