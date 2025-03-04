from django.shortcuts import render
import yfinance as yf


def index(request):
    # Hisse senedi sembollerini belirleyin
    tickers = ['THYAO.IS', 'GARAN.IS', 'SAHOL.IS']

    # Verileri çekmek için bir sözlük oluşturuyoruz
    data = {}

    for ticker in tickers:
        # Yfinance ile hisse verisini çekiyoruz
        df = yf.download(ticker, period='1d', interval='1m')

        # Fiyat değişim oranını ekliyoruz
        df['Price Change (%)'] = df['Close'].pct_change() * 100

        # NaN değerleri temizliyoruz
        df = df.dropna(subset=['Price Change (%)'])

        # Sadece gerekli sütunları alıyoruz: 'Close', 'Price Change (%)', 'Volume'
        data[ticker] = df[['Close', 'Price Change (%)', 'Volume']].reset_index()

    # Verileri render ederken 'data' isimli dictionary'yi şablona gönderiyoruz
    return render(request, 'index.html', {'data': data})
