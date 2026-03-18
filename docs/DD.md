# 詳細設計書（DD）- Stock AI Agent

## 1. システム構成

### 1.1 ディレクトリ構造

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPIエントリポイント
│   ├── config.py               # 環境変数・設定
│   ├── dependencies.py         # FastAPI依存性注入
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # 認証API
│   │   │   ├── users.py        # ユーザーAPI
│   │   │   ├── patterns.py     # パターンAPI
│   │   │   ├── stocks.py       # 銘柄API
│   │   │   ├── watchlist.py    # ウォッチリストAPI
│   │   │   ├── market.py       # マーケットAPI
│   │   │   ├── recommendations.py  # レコメンドAPI
│   │   │   └── notifications.py    # 通知API
│   │   └── deps.py             # API共通依存
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py             # SQLAlchemy Base
│   │   └── models.py           # 全モデル定義
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydanticスキーマ
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pattern_service.py
│   │   ├── stock_search_service.py
│   │   ├── stock_service.py
│   │   ├── recommendation_service.py
│   │   ├── llm_service.py
│   │   ├── notification_service.py
│   │   ├── watchlist_service.py
│   │   └── market_service.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── recommendation_tasks.py   # レコメンド生成
│   │   ├── stock_tasks.py            # 株価取得
│   │   └── monitoring_tasks.py       # 監視タスク
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── orchestrator.py
│   │   ├── memory.py
│   │   ├── tools.py
│   │   └── deps.py
│   ├── core/
│   │   └── security.py         # JWT・パスワード処理
│   └── db/
│       ├── __init__.py
│       └── session.py          # DBセッション管理
└── tests/                      # テストコード

frontend/
├── src/
│   ├── components/
│   │   ├── common/             # Button, Input, Card等
│   │   ├── auth/               # LoginForm, RegisterForm
│   │   ├── patterns/           # PatternList, PatternForm
│   │   ├── stocks/             # StockList, StockCard
│   │   └── dashboard/          # MarketOverview, Recommendations
│   ├── pages/                  # ページコンポーネント
│   ├── services/               # APIクライアント
│   ├── stores/                 # Zustandストア
│   ├── hooks/                  # カスタムフック
│   └── types/                  # TypeScript型定義
```

---

## 2. データベース設計

### 2.1 ER図

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│      User       │     │ InvestmentPattern│     │   Watchlist     │
├─────────────────┤     ├──────────────────┤     ├─────────────────┤
│ PK id: UUID     │1   N│ PK id: UUID      │     │ PK id: UUID     │
│ UK email: str   │────│ FK user_id: UUID │     │ FK user_id: UUID│
│ password_hash   │     │ name: str        │     │ stock_code: str │
│ display_name    │     │ raw_input: text  │     │ created_at      │
│ created_at      │     │ parsed_filters   │     └─────────────────┘
└─────────────────┘     │ is_active: bool  │              N│
         │1             │ created_at       │               │
         │              └──────────────────┘               │
         │N                                              N│
┌────────▼────────┐                            ┌────────▼────────┐
│ PushSubscription│                            │  Notification   │
├─────────────────┤                            ├─────────────────┤
│ PK id: UUID     │                            │ PK id: UUID     │
│ FK user_id: UUID│                            │ FK user_id: UUID│
│ endpoint: text  │                            │ type: str       │
│ p256dh: text    │                            │ title: str      │
│ auth: text      │                            │ body: text      │
│ created_at      │                            │ data: JSON      │
└─────────────────┘                            │ is_read: bool   │
                                               │ created_at      │
                                               └─────────────────┘
```

### 2.2 テーブル定義詳細

#### 2.2.1 users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    email_verified_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

**説明**: ユーザーアカウント情報を管理

#### 2.2.2 investment_patterns
```sql
CREATE TABLE investment_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    raw_input TEXT NOT NULL,
    parsed_filters JSONB NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_patterns_user_id ON investment_patterns(user_id);
CREATE INDEX idx_patterns_active ON investment_patterns(user_id, is_active);
```

**説明**: 投資パターンを保存。`parsed_filters`はJSONB形式で以下の構造:

```json
{
  "strategy": "dividend_focus",
  "filters": {
    "per_max": 15.0,
    "dividend_yield_min": 3.0
  },
  "sectors": ["銀行", "保険"],
  "sort_by": "dividend_yield",
  "sort_order": "desc"
}
```

#### 2.2.3 watchlists
```sql
CREATE TABLE watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, stock_code)
);

CREATE INDEX idx_watchlist_user ON watchlists(user_id);
CREATE INDEX idx_watchlist_code ON watchlists(stock_code);
```

**説明**: ウォッチリスト。銘柄コードのみ保存（外部API連携）。

#### 2.2.4 push_subscriptions
```sql
CREATE TABLE push_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint TEXT UNIQUE NOT NULL,
    p256dh TEXT NOT NULL,
    auth TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_push_user ON push_subscriptions(user_id);
```

**説明**: Web Push通知購読情報（VAPID）。

---

## 3. API詳細設計

### 3.1 認証API

#### POST /api/v1/auth/register
**機能**: ユーザー登録

**リクエスト**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "display_name": "ユーザー名"
}
```

**バリデーション**:
- email: メール形式、重複不可
- password: 8文字以上、大文字・小文字・数字を含む
- display_name: 2-100文字

**レスポンス (201)**:
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "display_name": "ユーザー名"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**エラー**:
- 400: バリデーションエラー
- 409: メールアドレス重複

#### POST /api/v1/auth/login
**機能**: ログイン

**リクエスト**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**レスポンス (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**エラー**:
- 401: 認証失敗

#### POST /api/v1/auth/refresh
**機能**: トークンリフレッシュ

**リクエスト**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**レスポンス (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### 3.2 パターンAPI

#### POST /api/v1/patterns/parse
**機能**: 自然言語パターン解析

**リクエスト**:
```json
{
  "input": "高配当株でPER15倍以下"
}
```

**処理フロー**:
1. LLMServiceでパース
2. フォールバックパース（LLM失敗時）
3. 結果返却

**レスポンス (200)**:
```json
{
  "raw_input": "高配当株でPER15倍以下",
  "parsed": {
    "strategy": "dividend_focus",
    "filters": {
      "per_max": 15
    },
    "sectors": [],
    "keywords": ["高配当"]
  }
}
```

#### POST /api/v1/patterns
**機能**: パターン作成＋即座レコメンド生成

**リクエスト**:
```json
{
  "name": "高配当割安株",
  "description": "高配当で割安な銘柄",
  "raw_input": "高配当株でPER15倍以下",
  "parsed_filters": {
    "strategy": "dividend_focus",
    "filters": {"per_max": 15},
    "sectors": []
  }
}
```

**処理フロー**:
1. パターンデータベース保存
2. `asyncio.create_task`で非同期レコメンド生成
3. レスポンス返却（レコメンドはバックグラウンド処理）

**レスポンス (201)**:
```json
{
  "id": "uuid",
  "name": "高配当割安株",
  "description": "高配当で割安な銘柄",
  "raw_input": "高配当株でPER15倍以下",
  "parsed_filters": {...},
  "is_active": true,
  "created_at": "2026-03-18T12:00:00Z"
}
```

---

### 3.3 レコメンドAPI

#### GET /api/v1/recommendations
**機能**: レコメンド取得

**クエリパラメータ**:
- `pattern_id`: 特定パターンでの絞り込み（任意）
- `limit`: 取得件数（デフォルト10、最大50）

**データ取得フロー**:
1. Redisキャッシュチェック（`recommendations:{user_id}:{pattern_id}`）
2. キャッシュミス時はDB検索（未実装）
3. キャッシュ有効期限: 1時間

**レスポンス (200)**:
```json
{
  "recommendations": [
    {
      "stock_code": "7203",
      "stock_name": "トヨタ自動車",
      "pattern_name": "高配当割安株",
      "match_score": 0.85,
      "matched_criteria": ["PER: 12.5倍", "配当: 3.2%"],
      "current_price": 2850,
      "change_percent": 1.5,
      "reason": "トヨタ自動車はあなたの高配当割安株パターンに適合しています"
    }
  ],
  "generated_at": "2026-03-18T12:00:00Z",
  "data_source": "yahoo_finance"
}
```

---

### 3.4 マーケットAPI

#### GET /api/v1/market/overview
**機能**: マーケット概況取得

**処理フロー**:
1. yfinanceで日経平均取得（`^N225`）
2. 3秒待機
3. yfinanceでNYダウ取得（`^DJI`）
4. レスポンス返却

**注意**: 同時リクエストを避けるため、順次実行＋3秒間隔

**レスポンス (200)**:
```json
{
  "indices": {
    "nikkei_225": {
      "name": "日経平均株価",
      "code": "N225",
      "current": 55239.40,
      "change": 1539.01,
      "change_percent": 2.87,
      "volume": 1200000000
    },
    "dow_jones": {
      "name": "NYダウ",
      "code": "DJI",
      "current": 46768.60,
      "change": -224.66,
      "change_percent": -0.48,
      "volume": 350000000
    }
  },
  "updated_at": "2026-03-18T12:00:00Z",
  "data_source": "yahoo_finance"
}
```

---

## 4. サービスクラス設計

### 4.1 PatternService

```python
class PatternService:
    """投資パターンビジネスロジック"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_pattern(
        self,
        user_id: str,
        name: str,
        description: str,
        raw_input: str,
        parsed_filters: dict
    ) -> InvestmentPattern:
        """パターン作成"""
    
    async def get_user_patterns(self, user_id: str) -> List[InvestmentPattern]:
        """ユーザーの全パターン取得"""
    
    async def get_active_patterns(self, user_id: str) -> List[InvestmentPattern]:
        """有効なパターンのみ取得"""
    
    async def toggle_pattern_active(self, pattern_id: str) -> InvestmentPattern:
        """有効/無効切り替え"""
```

### 4.2 StockSearchService

```python
class StockSearchService:
    """銘柄検索サービス（yfinance使用）"""
    
    # 人気銘柄リスト（検索対象）
    _popular_stocks = [...]  # 25銘柄
    
    async def search_stocks(self, query: str, limit: int = 10) -> List[StockSearchResult]:
        """銘柄検索（コード・名前で部分一致）"""
    
    async def get_stock_info(self, code: str) -> Optional[StockInfo]:
        """銘柄詳細情報取得"""
    
    async def get_price_data(self, code: str) -> Optional[PriceData]:
        """株価データ取得（yfinance使用）"""
```

### 4.3 LLMService

```python
class LLMService:
    """LLM連携サービス"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.client = AsyncOpenAI(...)
    
    async def parse_pattern(self, user_input: str) -> ParsedPattern:
        """
        自然言語をパターンに解析
        セクター情報も抽出
        """
    
    def _fallback_parse(self, user_input: str) -> ParsedPattern:
        """
        LLM失敗時のフォールバック
        正規表現でPER、配当、セクターを抽出
        """
```

---

## 5. タスク設計（Celery）

### 5.1 レコメンド生成タスク

```python
# app/tasks/recommendation_tasks.py

async def generate_recommendations_for_pattern(
    user_id: str,
    pattern_id: str
) -> dict:
    """
    レコメンド生成メイン処理
    
    検索順位:
    1. ウォッチリスト銘柄
    2. セクター一致銘柄（パターンに指定あり）
    3. 人気銘柄リスト
    
    スコアリング:
    - PER条件: +1
    - PBR条件: +1
    - 配当条件: +1
    - スコア≥1でレコメンド
    
    結果:
    - Redisにキャッシュ（TTL: 1時間）
    - プッシュ通知送信（マッチあり時）
    """
```

### 5.2 株価取得タスク

```python
# app/tasks/stock_tasks.py

@shared_task
def fetch_watchlist_prices():
    """
    ウォッチリスト銘柄の株価を取得
    平日9-15時、5分間隔で実行
    """

@shared_task
def generate_daily_recommendations():
    """
    全ユーザーの日次レコメンド生成
    平日16時に実行
    """
```

---

## 6. セキュリティ設計

### 6.1 認証・認可

| 項目 | 実装 | 詳細 |
|------|------|------|
| パスワードハッシュ | bcrypt | コストファクター12 |
| JWT署名 | HS256 | SECRET_KEY環境変数 |
| アクセストークン有効期限 | 24時間 | - |
| リフレッシュトークン有効期限 | 7日 | - |
| パスワードバリデーション | 正規表現 | 8文字以上、英数混在 |

### 6.2 API保護

```python
# 認証必須エンドポイントの保護
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """JWT検証＋ユーザー取得"""
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user = await get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401)
    return user

# 使用例
@router.get("/patterns")
async def list_patterns(
    current_user = Depends(get_current_user)  # 認証必須
):
    ...
```

### 6.3 レート制限

| エンドポイント | 制限 |
|----------------|------|
| /api/auth/* | 5回/分（IP単位） |
| /api/*（一般） | 100回/分（ユーザー単位） |
| yfinance呼び出し | 3秒間隔必須 |

---

## 7. エラー処理設計

### 7.1 エラーコード一覧

| コード | 内容 | HTTP Status |
|--------|------|-------------|
| AUTH_001 | 認証失敗 | 401 |
| AUTH_002 | トークン期限切れ | 401 |
| AUTH_003 | 権限不足 | 403 |
| VAL_001 | バリデーションエラー | 422 |
| VAL_002 | メール重複 | 409 |
| RES_001 | リソース不存在 | 404 |
| EXT_001 | 外部APIエラー | 503 |
| INT_001 | 内部サーバーエラー | 500 |

### 7.2 エラーレスポンス形式

```json
{
  "detail": "エラーメッセージ",
  "code": "AUTH_001",
  "errors": [
    {"field": "email", "message": "Invalid format"}
  ]
}
```

---

## 8. キャッシュ設計

### 8.1 Redisキャッシュ戦略

| キー | データ | TTL | 説明 |
|------|--------|-----|------|
| `recommendations:{user_id}:{pattern_id}` | レコメンド結果 | 1時間 | パターン別レコメンド |
| `market:overview` | マーケット概況 | 30秒 | 全ユーザー共用 |
| `stock:{code}:price` | 株価データ | 5分 | 銘柄別最新価格 |

### 8.2 キャッシュ更新タイミング

- **レコメンド**: パターン作成時・毎日16時
- **マーケット**: 30秒間隔自動更新
- **株価**: ページ表示時、または5分間隔

---

## 9. ログ設計

### 9.1 ログレベル

| レベル | 使用シーン | 出力先 |
|--------|------------|--------|
| DEBUG | 開発時詳細ログ | コンソール（開発のみ） |
| INFO | アクセスログ、主要処理 | コンソール |
| WARNING | 注意喚起（レート制限近い等） | コンソール |
| ERROR | エラー発生 | コンソール + 通知 |

### 9.2 ログ形式

```
[2026-03-18 12:00:00] [INFO] [auth] User login: user@example.com
[2026-03-18 12:00:01] [INFO] [recommendation] Generated 5 recommendations for user_id=xxx
[2026-03-18 12:00:02] [ERROR] [yfinance] Failed to fetch ^N225: 429 Too Many Requests
```

---

## 10. 変更履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2026-03-18 | 1.0.0 | 初版作成 |
