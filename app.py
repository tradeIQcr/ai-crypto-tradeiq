import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

st.set_page_config(page_title="Crypto AI Dashboard", layout="wide")

st.title("Crypto AI Trade Dashboard")

# Sidebar
st.sidebar.header("Select Cryptocurrency")
symbol = st.sidebar.selectbox("Crypto Symbol", ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"])

start_date = st.sidebar.date_input("Start Date", datetime.date(2022, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

# Fetch data
@st.cache_data
def load_data(symbol, start, end):
    df = yf.download(symbol, start=start, end=end)
    df.reset_index(inplace=True)
    return df

data = load_data(symbol, start_date, end_date)

# Display data
st.subheader(f"{symbol} Price Chart")
st.line_chart(data.set_index("Date")["Close"])

st.subheader("Recent Data")
st.dataframe(data.tail())
