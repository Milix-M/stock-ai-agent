import yfinance as yf
import time

print('=== TOPIX 代替ティッカー テスト ===\n')

# TOPIX関連のティッカー候補
tickers = [
    ('^TOPX', 'TOPIX'),
    ('^TPX', 'TOPIX ( alternate)'),
    ('1306.T', 'TOPIX ETF'),
    ('^N225', '日経平均（比較用）'),
]

for symbol, name in tickers:
    print(f'{name} ({symbol}):')
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='2d')
        
        if hist.empty or len(hist) < 2:
            print(f'  ❌ No data')
        else:
            latest = hist.iloc[-1]
            previous = hist.iloc[-2]
            change = latest['Close'] - previous['Close']
            change_pct = (change / previous['Close']) * 100
            print(f'  ✓ Current: {latest["Close"]:,.2f}')
            print(f'  ✓ Change: {change:+.2f} ({change_pct:+.2f}%)')
    except Exception as e:
        print(f'  ❌ Error: {e}')
    print()
    time.sleep(3)