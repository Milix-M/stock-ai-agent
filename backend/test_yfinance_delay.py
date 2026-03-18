import yfinance as yf
import time

print('=== yfinance with 3-second delay test ===\n')

def fetch_with_delay(ticker_symbol, delay=3):
    """遅延付きでデータを取得"""
    print(f'Fetching {ticker_symbol}...')
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period='2d')
        
        if hist.empty or len(hist) < 2:
            print(f'  ❌ No data')
            return None
        
        latest = hist.iloc[-1]
        previous = hist.iloc[-2]
        
        change = latest['Close'] - previous['Close']
        change_percent = (change / previous['Close']) * 100
        
        print(f'  ✓ Current: {latest["Close"]:,.2f}')
        print(f'  ✓ Change: {change:+.2f} ({change_percent:+.2f}%)')
        
        time.sleep(delay)
        return {
            'current': latest['Close'],
            'change': change,
            'change_percent': change_percent
        }
    except Exception as e:
        print(f'  ❌ Error: {e}')
        time.sleep(delay)
        return None

# 順番に取得（同時リクエストを避ける）
print('1. 日経平均 (^N225)')
nikkei = fetch_with_delay('^N225', delay=3)

print('\n2. TOPIX (^TOPX)')
topix = fetch_with_delay('^TOPX', delay=3)

print('\n3. NYダウ (^DJI)')
dow = fetch_with_delay('^DJI', delay=3)

print('\n=== 結果 ===')
print(f'日経平均: {"✓ OK" if nikkei else "✗ Failed"}')
print(f'TOPIX: {"✓ OK" if topix else "✗ Failed"}')
print(f'NYダウ: {"✓ OK" if dow else "✗ Failed"}')