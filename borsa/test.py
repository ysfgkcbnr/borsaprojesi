import yfinance as yf
bist = yf.Ticker("XU100.IS")
print(bist.history(period="1d"))