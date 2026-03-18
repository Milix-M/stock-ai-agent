import yfinance as yf

print('=== yfinance テスト ===')

# 方法1: ティッカーオブジェクトの情報を確認
print('\n1. ^N225 の info():')
ticker = yf.Ticker('^N225')
try:
    info = ticker.info
    print(f'   取得できたキー数: {len(info)}')
    if info:
        print(f'   サンプルキー: {list(info.keys())[:5]}')
        print(f'   regularMarketPrice: {info.get("regularMarketPrice")}')
except Exception as e:
    print(f'   エラー: {e}')

# 方法2: 異なる期間で履歴を取得
print('\n2. ^N225 history(period="1d"):')
try:
    hist = ticker.history(period='1d')
    print(f'   件数: {len(hist)}')
    if not hist.empty:
        print(f'   最新: {hist.iloc[-1].to_dict()}')
except Exception as e:
    print(f'   エラー: {e}')

# 方法3: fast_info を試す（新しいAPI）
print('\n3. ^N225 fast_info:')
try:
    fast_info = ticker.fast_info
    print(f'   last_price: {fast_info.get("last_price")}')
    print(f'   previous_close: {fast_info.get("previous_close")}')
except Exception as e:
    print(f'   エラー: {e}')

# 方法4: 米国指数も試す
print('\n4. ^GSPC (S&P500):')
try:
    sp = yf.Ticker('^GSPC')
    hist = sp.history(period='1d')
    print(f'   件数: {len(hist)}')
    if not hist.empty:
        print(f'   最新Close: {hist.iloc[-1]["Close"]}')
except Exception as e:
    print(f'   エラー: {e}')

# 方法5: 個別株（日本）
print('\n5. 7203.T (トヨタ):')
try:
    toyota = yf.Ticker('7203.T')
    hist = toyota.history(period='2d')
    print(f'   件数: {len(hist)}')
    if not hist.empty:
        print(f'   最新Close: {hist.iloc[-1]["Close"]}')
        print(f'   前日Close: {hist.iloc[-2]["Close"]}')
        change = ((hist.iloc[-1]['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close']) * 100
        print(f'   変動率: {change:.2f}%')
except Exception as e:
    print(f'   エラー: {e}')

# 方法6: 複数ティッカー一括取得
print('\n6. 複数インデックス一括取得:')
try:
    tickers = yf.Tickers('^N225 ^TOPX ^DJI')
    for symbol in ['^N225', '^TOPX', '^DJI']:
        try:
            hist = tickers.tickers[symbol].history(period='1d')
            print(f'   {symbol}: {len(hist)} 件')
        except:
            print(f'   {symbol}: エラー')
except Exception as e:
    print(f'   エラー: {e}')