import yfinance as yf

print('=== Testing Yahoo Finance Market Data ===\n')

# 日経平均を試す
print('1. 日経平均 (^N225)')
try:
    ticker = yf.Ticker('^N225')
    hist = ticker.history(period='2d')
    print(f'   History empty: {hist.empty}')
    if not hist.empty:
        print(f'   Latest Close: {hist.iloc[-1]["Close"]}')
        print(f'   SUCCESS!')
    else:
        print(f'   FAILED: No data')
except Exception as e:
    print(f'   ERROR: {e}')

# TOPIXを試す
print('\n2. TOPIX (^TOPX)')
try:
    ticker = yf.Ticker('^TOPX')
    hist = ticker.history(period='2d')
    print(f'   History empty: {hist.empty}')
    if not hist.empty:
        print(f'   Latest Close: {hist.iloc[-1]["Close"]}')
        print(f'   SUCCESS!')
    else:
        print(f'   FAILED: No data')
except Exception as e:
    print(f'   ERROR: {e}')

# NYダウを試す
print('\n3. NYダウ (^DJI)')
try:
    ticker = yf.Ticker('^DJI')
    hist = ticker.history(period='2d')
    print(f'   History empty: {hist.empty}')
    if not hist.empty:
        print(f'   Latest Close: {hist.iloc[-1]["Close"]}')
        print(f'   SUCCESS!')
    else:
        print(f'   FAILED: No data')
except Exception as e:
    print(f'   ERROR: {e}')

# S&P500を試す
print('\n4. S&P500 (^GSPC)')
try:
    ticker = yf.Ticker('^GSPC')
    hist = ticker.history(period='2d')
    print(f'   History empty: {hist.empty}')
    if not hist.empty:
        print(f'   Latest Close: {hist.iloc[-1]["Close"]}')
        print(f'   SUCCESS!')
    else:
        print(f'   FAILED: No data')
except Exception as e:
    print(f'   ERROR: {e}')