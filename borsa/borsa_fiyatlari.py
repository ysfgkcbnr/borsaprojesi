from django.shortcuts import render
import yfinance as yf


def index(request):
    # Hisse senedi sembollerini belirleyin
    tickers = ['THYAO.IS', 'GARAN.IS', 'SAHOL.IS']

    # Verileri çekmek için bir sözlük oluşturuyoruz
    data = {ticker: yf.download(ticker, period='1d', interval='1m') for ticker in tickers}

    # Fiyat değişim oranı ve volume bilgilerini ekleyin
    for ticker, df in data.items():
        df['Price Change (%)'] = df['Close'].pct_change() * 100
        df = df.dropna(subset=['Price Change (%)'])
        data[ticker] = df[['Close', 'Price Change (%)', 'Volume']].reset_index()

    return render(request, 'index.html', {'data': data})
