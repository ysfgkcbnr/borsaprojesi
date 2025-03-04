# get_stock_data.py
import yfinance as yf

def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d", interval="1m")  # Son 1 günlük veriler, 1 dakikalık interval
    return data
