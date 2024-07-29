import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import requests

# API'den veri çekme
def fetch_data(symbol, interval='1d', limit=1000):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df.astype(float)
    return df

# Hareketli Ortalamalar ve Sinyaller
def calculate_indicators(df):
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA50'] = df['close'].rolling(window=50).mean()
    df['Signal'] = 0
    df['Signal'][20:] = np.where(df['MA20'][20:] > df['MA50'][20:], 1, 0)
    df['Position'] = df['Signal'].diff()
    return df

# Grafik oluşturma
def plot_graph(ax, df, title):
    ax.clear()
    ax.plot(df['close'], label='Fiyat')
    ax.plot(df['MA20'], label='MA20')
    ax.plot(df['MA50'], label='MA50')
    ax.plot(df[df['Position'] == 1].index, df['MA20'][df['Position'] == 1], '^', markersize=10, color='g', lw=0, label='Buy Signal')
    ax.plot(df[df['Position'] == -1].index, df['MA20'][df['Position'] == -1], 'v', markersize=10, color='r', lw=0, label='Sell Signal')
    ax.set_title(title)
    ax.set_xlabel('Tarih')
    ax.set_ylabel('Fiyat')
    ax.legend()

# Güncellenmiş ve filtrelenmiş grafik seçimi
def update_graph(label):
    symbol = symbols[label]
    df = fetch_data(symbol)
    df = calculate_indicators(df)
    plot_graph(ax, df, f'{symbol} Alım-Satım Sinyalleri')
    plt.draw()

# Grafiklerin etiketleri ve düğmeler
def create_buttons(axs):
    buttons = []
    for i, symbol in enumerate(symbols):
        ax_button = plt.axes([0.1, 0.05 - 0.05 * i, 0.15, 0.04])
        button = Button(ax_button, symbol)
        button.on_clicked(lambda event, idx=i: update_graph(idx))
        buttons.append(button)
    return buttons

# Coin'leri tanımla ve grafikler oluştur
symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
df_dict = {symbol: fetch_data(symbol) for symbol in symbols}
df_dict = {symbol: calculate_indicators(df) for symbol, df in df_dict.items()}

fig, ax = plt.subplots(figsize=(12, 8))
plt.subplots_adjust(left=0.25, right=0.75, top=0.9, bottom=0.15)
buttons = create_buttons(ax)

# İlk grafiği göster
update_graph(0)

plt.show()
