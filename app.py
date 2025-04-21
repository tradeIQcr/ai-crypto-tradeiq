import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import datetime

st.set_page_config(page_title="Crypto AI Dashboard", layout="wide")
st.title("Crypto AI Trade Dashboard")

# Sidebar
st.sidebar.header("Select Cryptocurrency")
symbol = st.sidebar.selectbox("Crypto Symbol", ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"])
start_date = st.sidebar.date_input("Start Date", datetime.date(2022, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

# Load data
@st.cache_data
def load_data(symbol, start, end):
    df = yf.download(symbol, start=start, end=end)
    df.reset_index(inplace=True)
    return df

data = load_data(symbol, start_date, end_date)

if data.empty or "Close" not in data:
    st.error("No data available. Please try a different date range or symbol.")
else:
    # Remove rows with NaN values
    data.dropna(inplace=True)

    # Technical indicators
data["RSI"] = ta.momentum.RSIIndicator(close=data["Close"]).rsi()
macd = ta.trend.MACD(data["Close"])
data["MACD"] = macd.macd()
data["MACD_signal"] = macd.macd_signal()
bb = ta.volatility.BollingerBands(data["Close"])
data["BB_upper"] = bb.bollinger_hband()
data["BB_lower"] = bb.bollinger_lband()


    # Chart
    st.subheader(f"{symbol} Price Chart")
    st.line_chart(data.set_index("Date")[["Close", "BB_upper", "BB_lower"]])

    st.subheader("Technical Indicators")
    st.line_chart(data.set_index("Date")[["RSI", "MACD", "MACD_signal"]])

    st.subheader("Recent Data")
    st.dataframe(data.tail())
