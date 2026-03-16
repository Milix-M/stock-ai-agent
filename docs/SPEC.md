# 株AIエージェント - 要件定義書

## 1. プロジェクト概要

### 1.1 背景・目的
事前収集した株価情報に基づき、「オトクな株」や「変動があった株」を自動検知し、ユーザーに通知するWebアプリケーションを開発する。

### 1.2 ターゲットユーザー
- 個人投資家
- 特定の投資パターン（高配当、グロース等）を持つユーザー

### 1.3 提供価値
- 自分の投資パターンに合った銘柄の自動検出
- 株価変動のリアルタイム通知
- 自然言語で投資方針を登録できる簡便さ

---

## 2. 機能要件

### 2.1 コア機能

#### 2.1.1 ユーザー管理
| ID | 機能名 | 説明 | 優先度 |
|---|---|---|---|
| F-001 | ユーザー登録 | メール/パスワードによるアカウント作成 | 高 |
| F-002 | ログイン/ログアウト | JWT認証によるセッション管理 | 高 |
| F-003 | パスワードリセット | メールによるリセットフロー | 中 |

#### 2.1.2 投資パターン管理
| ID | 機能名 | 説明 | 優先度 |
|---|---|---|---|
| F-004 | パターン自然言語入力 | ユーザーが「高配当株でPER15倍以下」等を自然言語で入力 | 高 |
| F-005 | パターンAI解析 | LLMが自然言語を構造化データに変換 | 高 |
| F-006 | パターン保存/編集/削除 | 複数パターンのCRUD操作 | 高 |
| F-007 | パターンバリデーション | 設定値の妥当性チェック | 中 |

#### 2.1.3 株価データ収集・分析
| ID | 機能名 | 説明 | 優先度 |
|---|---|---|---|
| F-008 | 株価自動取得 | 定期的に株価データを取得・保存 | 高 |
| F-009 | 変動検知 | 前日比・前週比の閾値超過を検出 | 高 |
| F-010 | 出来高急増検知 | 出来高の異常値を検出 | 中 |
| F-011 | 移動平均線検知 | ゴールデン/デッドクロス検出 | 中 |
| F-012 | 「オトク」判定 | AI + ルールベースで投資適性を判定 | 高 |

#### 2.1.4 通知機能
| ID | 機能名 | 説明 | 優先度 |
|---|---|---|---|
| F-013 | ブラウザプッシュ通知 | Web Push APIによる通知送信 | 高 |
| F-014 | 通知設定 | 通知条件・頻度のカスタマイズ | 中 |
| F-015 | 通知履歴 | 過去の通知一覧表示 | 低 |

#### 2.1.5 レコメンデーション
| ID | 機能名 | 説明 | 優先度 |
|---|---|---|---|
| F-016 | AIレコメンド | ユーザーパターンに基づく銘柄提案 | 高 |
| F-017 | レコメンド理由表示 | なぜその銘柄かの説明 | 中 |

---

## 3. 非機能要件

### 3.1 パフォーマンス
- ページ表示: 初回3秒以内、遷移1秒以内
- API応答: 90%のリクエストが500ms以内
- 株価データ更新: 1日1回（市場終了後）

### 3.2 可用性
- 稼働率: 99.9%（メンテナンス時間除く）
- バックアップ: 日次DBバックアップ

### 3.3 セキュリティ
- HTTPS必須
- パスワードハッシュ化（bcrypt）
- JWT有効期限: アクセス24時間、リフレッシュ7日
- VAPIDキーによるプッシュ通知認証

### 3.4 スケーラビリティ
- 初期: 100ユーザー想定
- 将来的に1000ユーザーまで水平スケール可能な設計

---

## 4. 技術要件

### 4.1 システム構成

```
┌─────────────────────────────────────┐
│      Vite + React (Frontend)        │
│  ├─ サービスワーカー（Push受信）     │
│  ├─ 銘柄登録・パターン設定UI         │
│  └─ ダッシュボード                  │
└─────────────┬───────────────────────┘
              │ API
┌─────────────▼───────────────────────┐
│        FastAPI (Backend)            │
│  ├─ ユーザー管理（認証）             │
│  ├─ 投資パターン解析（LLM）          │
│  ├─ 株価データ取得・保存             │
│  └─ Web Push送信（pywebpush）        │
└─────────────┬───────────────────────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
 PostgreSQL  Redis   外部API
 (メインDB)  (Celery)  (株価/LLM)
```

### 4.2 技術スタック

| 層 | 技術 | バージョン/備考 |
|---|---|---|
| **フロントエンド** | Vite + React | React Router, TypeScript |
| **状態管理** | Zustand | 軽量なグローバル状態管理 |
| **UIコンポーネント** | Tailwind CSS + Headless UI | スタイリング |
| **HTTPクライアント** | TanStack Query (React Query) | キャッシュ、自動再取得 |
| **バックエンド** | FastAPI | Python 3.12+, async |
| **データベース** | PostgreSQL | 15+ |
| **時系列DB** | TimescaleDB | PostgreSQL拡張 |
| **タスクキュー** | Celery + Redis | 定期実行、非同期処理 |
| **株価API** | yfinance / Alpha Vantage | 開発/本番切り替え |
| **LLM** | OpenAI API / OpenRouter | 設定で切り替え |
| **Web Push** | pywebpush + VAPID | 標準Web Push API |
| **認証** | JWT (PyJWT) | アクセス/リフレッシュトークン |
| **インフラ（開発）** | Docker Compose | ローカル開発環境 |
| **インフラ（本番）** | Railway / Render / VPS | 未定 |

### 4.3 API仕様（概要）

| エンドポイント | メソッド | 説明 |
|---|---|---|
| /api/auth/register | POST | ユーザー登録 |
| /api/auth/login | POST | ログイン |
| /api/auth/refresh | POST | トークンリフレッシュ |
| /api/patterns | GET/POST/PUT/DELETE | 投資パターンCRUD |
| /api/patterns/parse | POST | 自然言語パターン解析 |
| /api/stocks | GET | 銘柄一覧・検索 |
| /api/stocks/{code} | GET | 銘柄詳細 |
| /api/watchlist | GET/POST/DELETE | ウォッチリスト管理 |
| /api/notifications/subscribe | POST | プッシュ通知購読 |
| /api/notifications/unsubscribe | POST | プッシュ通知解除 |
| /api/recommendations | GET | AIレコメンド取得 |

---

## 5. データモデル詳細

### 5.1 ER図

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│      User       │     │ InvestmentPattern│     │      Stock      │
├─────────────────┤     ├──────────────────┤     ├─────────────────┤
│ id (PK)         │1   N│ id (PK)          │     │ id (PK)         │
│ email (UK)      │────│ user_id (FK)     │     │ code (UK)       │
│ password_hash   │     │ name             │     │ name            │
│ display_name    │     │ description      │     │ market          │
│ created_at      │     │ filters (JSON)   │     │ sector          │
│ updated_at      │     │ is_active        │     │ created_at      │
└─────────────────┘     │ created_at       │     └─────────────────┘
         │1              └──────────────────┘              │1
         │                                                 │
         │N                                                │N
┌────────▼────────┐                              ┌────────▼────────┐
│ PushSubscription│                              │   StockPrice    │
├─────────────────┤                              ├─────────────────┤
│ id (PK)         │                              │ id (PK)         │
│ user_id (FK)    │                              │ stock_id (FK)   │
│ endpoint        │                              │ date            │
│ p256dh          │                              │ open            │
│ auth            │                              │ high            │
│ created_at      │                              │ low             │
└─────────────────┘                              │ close           │
                                                 │ volume          │
┌─────────────────┐                              │ adjusted_close  │
│   Watchlist     │                              └─────────────────┘
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ stock_id (FK)   │
│ created_at      │
└─────────────────┘

┌─────────────────┐
│  Notification   │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ type            │
│ title           │
│ body            │
│ data (JSON)     │
│ is_read         │
│ created_at      │
└─────────────────┘
```

### 5.2 テーブル定義

#### users
| カラム名 | 型 | 制約 | 説明 |
|---|---|---|---|
| id | UUID | PK | ユーザーID |
| email | VARCHAR(255) | UK, NOT NULL | メールアドレス |
| password_hash | VARCHAR(255) | NOT NULL | ハッシュ化パスワード |
| display_name | VARCHAR(100) | | 表示名 |
| email_verified_at | TIMESTAMP | | メール認証日時 |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | 更新日時 |

#### investment_patterns
| カラム名 | 型 | 制約 | 説明 |
|---|---|---|---|
| id | UUID | PK | パターンID |
| user_id | UUID | FK, NOT NULL | ユーザーID |
| name | VARCHAR(100) | NOT NULL | パターン名 |
| description | TEXT | | 説明 |
| raw_input | TEXT | NOT NULL | 自然言語入力原文 |
| parsed_filters | JSONB | NOT NULL | LLM解析結果 |
| is_active | BOOLEAN | DEFAULT true | 有効フラグ |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | 更新日時 |

#### stocks
| カラム名 | 型 | 制約 | 説明 |
|---|---|---|---|
| id | UUID | PK | 銘柄ID |
| code | VARCHAR(20) | UK, NOT NULL | 銘柄コード |
| name | VARCHAR(200) | NOT NULL | 銘柄名 |
| market | VARCHAR(50) | | 市場（東証プライム等） |
| sector | VARCHAR(100) | | 業種 |
| per | DECIMAL(10,2) | | PER |
| pbr | DECIMAL(10,2) | | PBR |
| dividend_yield | DECIMAL(5,2) | | 配当利回り(%) |
| market_cap | BIGINT | | 時価総額 |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | 更新日時 |

#### stock_prices (TimescaleDB ハイパーテーブル)
| カラム名 | 型 | 制約 | 説明 |
|---|---|---|---|
| id | UUID | PK | 価格ID |
| stock_id | UUID | FK, NOT NULL | 銘柄ID |
| date | DATE | NOT NULL | 日付 |
| open | DECIMAL(15,2) | | 始値 |
| high | DECIMAL(15,2) | | 高値 |
| low | DECIMAL(15,2) | | 安値 |
| close | DECIMAL(15,2) | NOT NULL | 終値 |
| volume | BIGINT | | 出来高 |
| adjusted_close | DECIMAL(15,2) | | 調整済み終値 |

#### watchlists
| カラム名 | 型 | 制約 | 説明 |
|---|---|---|---|
| id | UUID | PK | ID |
| user_id | UUID | FK, NOT NULL | ユーザーID |
| stock_id | UUID | FK, NOT NULL | 銘柄ID |
| alert_threshold | DECIMAL(5,2) | | 通知閾値(%) |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |

#### push_subscriptions
| カラム名 | 型 | 制約 | 説明 |
|---|---|---|---|
| id | UUID | PK | ID |
| user_id | UUID | FK, NOT NULL | ユーザーID |
| endpoint | TEXT | NOT NULL, UK | エンドポイントURL |
| p256dh | TEXT | NOT NULL | 公開鍵 |
| auth | TEXT | NOT NULL | 認証トークン |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |

#### notifications
| カラム名 | 型 | 制約 | 説明 |
|---|---|---|---|
| id | UUID | PK | ID |
| user_id | UUID | FK, NOT NULL | ユーザーID |
| type | VARCHAR(50) | NOT NULL | 通知タイプ |
| title | VARCHAR(200) | NOT NULL | タイトル |
| body | TEXT | NOT NULL | 本文 |
| data | JSONB | | 追加データ |
| is_read | BOOLEAN | DEFAULT false | 既読フラグ |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |

---

## 6. API仕様詳細

### 6.1 認証関連

#### POST /api/auth/register
**リクエスト**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "display_name": "ユーザー名"
}
```

**レスポンス (201)**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "display_name": "ユーザー名"
  },
  "access_token": "jwt_token",
  "refresh_token": "jwt_token"
}
```

**エラー (400, 409)**
```json
{"detail": "Email already registered"}
```

---

#### POST /api/auth/login
**リクエスト**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**レスポンス (200)**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "jwt_token",
  "token_type": "bearer"
}
```

---

### 6.2 投資パターン

#### POST /api/patterns/parse
自然言語からパターンを解析

**リクエスト**
```json
{
  "input": "高配当株でPER15倍以下、配当利回り3%以上"
}
```

**レスポンス (200)**
```json
{
  "raw_input": "高配当株でPER15倍以下、配当利回り3%以上",
  "parsed": {
    "strategy": "dividend_focus",
    "filters": {
      "per_max": 15,
      "dividend_yield_min": 3,
      "sort_by": "dividend_yield",
      "sort_order": "desc"
    },
    "keywords": ["高配当", "割安"]
  }
}
```

---

#### POST /api/patterns
**リクエスト**
```json
{
  "name": "高配当割安株",
  "description": "高配当で割安な銘柄",
  "raw_input": "高配当株でPER15倍以下、配当利回り3%以上",
  "parsed_filters": {
    "per_max": 15,
    "dividend_yield_min": 3
  }
}
```

**レスポンス (201)**
```json
{
  "id": "uuid",
  "name": "高配当割安株",
  "description": "高配当で割安な銘柄",
  "raw_input": "高配当株でPER15倍以下、配当利回り3%以上",
  "parsed_filters": {
    "per_max": 15,
    "dividend_yield_min": 3
  },
  "is_active": true,
  "created_at": "2026-03-16T12:00:00Z"
}
```

---

### 6.3 銘柄関連

#### GET /api/stocks
**クエリパラメータ**
- `q`: 検索キーワード（銘柄名・コード）
- `market`: 市場フィルタ
- `sector`: 業種フィルタ
- `page`: ページ番号（デフォルト1）
- `limit`: 1ページあたり件数（デフォルト20）

**レスポンス (200)**
```json
{
  "items": [
    {
      "id": "uuid",
      "code": "7203",
      "name": "トヨタ自動車",
      "market": "東証プライム",
      "sector": "輸送用機器",
      "per": 12.5,
      "pbr": 1.2,
      "dividend_yield": 3.2,
      "price_change_percent": 1.5
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 20
}
```

---

#### GET /api/stocks/{code}
**レスポンス (200)**
```json
{
  "id": "uuid",
  "code": "7203",
  "name": "トヨタ自動車",
  "market": "東証プライム",
  "sector": "輸送用機器",
  "per": 12.5,
  "pbr": 1.2,
  "dividend_yield": 3.2,
  "market_cap": 3500000000000,
  "prices": {
    "current": 2850,
    "open": 2810,
    "high": 2870,
    "low": 2800,
    "previous_close": 2808,
    "change": 42,
    "change_percent": 1.5,
    "volume": 12000000
  },
  "chart_data": {
    "daily": [...],
    "weekly": [...],
    "monthly": [...]
  }
}
```

---

### 6.4 レコメンデーション

#### GET /api/recommendations
**クエリパラメータ**
- `pattern_id`: 特定パターンでの絞り込み
- `limit`: 取得件数（デフォルト10）

**レスポンス (200)**
```json
{
  "recommendations": [
    {
      "stock": {
        "id": "uuid",
        "code": "7203",
        "name": "トヨタ自動車"
      },
      "match_score": 0.92,
      "reason": "PERが15倍以下で配当利回り3%を超えています。直近の決算も堅調です。",
      "matched_filters": {
        "per": 12.5,
        "dividend_yield": 3.2
      },
      "alerts": [
        {
          "type": "price_change",
          "message": "前日比+1.5%の上昇"
        }
      ]
    }
  ],
  "generated_at": "2026-03-16T12:00:00Z"
}
```

---

### 6.5 エラーレスポンス

| ステータス | エラーコード | 説明 |
|---|---|---|
| 400 | BAD_REQUEST | リクエスト形式不正 |
| 401 | UNAUTHORIZED | 認証エラー |
| 403 | FORBIDDEN | 権限不足 |
| 404 | NOT_FOUND | リソース不存在 |
| 409 | CONFLICT | リソース競合 |
| 422 | VALIDATION_ERROR | バリデーションエラー |
| 500 | INTERNAL_ERROR | サーバーエラー |

**エラーレスポンス形式**
```json
{
  "detail": "エラーメッセージ",
  "code": "ERROR_CODE",
  "errors": [
    {"field": "email", "message": "Invalid email format"}
  ]
}
```

---

## 7. 画面遷移・UI構成

### 7.1 画面一覧

| 画面ID | 画面名 | パス | 認証 | 説明 |
|---|---|---|---|---|
| P-001 | トップページ | `/` | 不要 | サービス紹介、ログイン導線 |
| P-002 | ログイン | `/login` | 不要 | メール/パスワード認証 |
| P-003 | 新規登録 | `/register` | 不要 | アカウント作成 |
| P-004 | ダッシュボード | `/dashboard` | 必要 | メイン画面、銘柄レコメンド表示 |
| P-005 | 銘柄一覧 | `/stocks` | 必要 | 全銘柄検索・一覧 |
| P-006 | 銘柄詳細 | `/stocks/[code]` | 必要 | 個別銘柄の詳細情報・チャート |
| P-007 | パターン設定 | `/patterns` | 必要 | 投資パターン一覧・管理 |
| P-008 | パターン作成 | `/patterns/new` | 必要 | 自然言語でパターン作成 |
| P-009 | ウォッチリスト | `/watchlist` | 必要 | 監視中銘柄一覧 |
| P-010 | 通知設定 | `/settings/notifications` | 必要 | 通知条件・プッシュ設定 |
| P-011 | プロフィール | `/settings/profile` | 必要 | ユーザー情報変更 |

### 7.2 画面遷移図

```
┌─────────┐    ┌─────────┐    ┌──────────┐
│  トップ  │───▶│  ログイン │───▶│ ダッシュボード│
│  (P-001) │    │  (P-002) │    │  (P-004)  │
└─────────┘    └─────────┘    └────┬─────┘
     │                               │
     │          ┌─────────┐         │
     └─────────▶│ 新規登録 │         │
                │ (P-003) │         │
                └─────────┘         │
                                    │
        ┌───────────────────────────┼───────────┐
        │                           │           │
        ▼                           ▼           ▼
   ┌─────────┐                ┌─────────┐  ┌─────────┐
   │銘柄一覧  │◀──────────────▶│銘柄詳細  │  │パターン  │
   │(P-005)  │                │(P-006)  │  │設定      │
   └─────────┘                └─────────┘  │(P-007)  │
                                           └────┬────┘
                                                │
                                                ▼
                                           ┌─────────┐
                                           │パターン  │
                                           │作成      │
                                           │(P-008)  │
                                           └─────────┘
```

### 7.3 主要画面構成

#### ダッシュボード (P-004)
```
┌─────────────────────────────────────────────────────────────┐
│  ヘッダー（ロゴ・ナビ・ユーザーアイコン）                      │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐ │
│  │  【本日のレコメンド】                                  │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │ │
│  │  │ 銘柄カード │ │ 銘柄カード │ │ 銘柄カード │ │ 銘柄カード │    │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │ │
│  └───────────────────────────────────────────────────────┘ │
│  ┌────────────────────────┐  ┌──────────────────────────┐ │
│  │ 【マーケット概況】      │  │ 【急騰・急落銘柄】        │ │
│  │ 日経平均: +1.2%        │  │ ・銘柄A +8.5%            │ │
│  │ TOPIX: +0.8%           │  │ ・銘柄B -5.2%            │ │
│  │                        │  │                          │ │
│  └────────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### パターン作成 (P-008)
```
┌─────────────────────────────────────────────────────────────┐
│  ヘッダー                                                   │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐ │
│  │  新しい投資パターンを作成                              │ │
│  │                                                       │ │
│  │  ┌───────────────────────────────────────────────┐   │ │
│  │  │  💡 例：高配当株でPER15倍以下、配当利回り3%以上   │   │ │
│  │  └───────────────────────────────────────────────┘   │ │
│  │                                                       │ │
│  │  [入力欄]                                             │ │
│  │                                                       │ │
│  │  [  AIで解析する  ]                                   │ │
│  │                                                       │ │
│  │  ┌───────────────────────────────────────────────┐   │ │
│  │  │ 【解析結果】                                   │   │ │
│  │  │ 条件: PER ≤ 15, 配当利回り ≥ 3%                │   │ │
│  │  │ [OK] [修正する]                                 │   │ │
│  │  └───────────────────────────────────────────────┘   │ │
│  │                                                       │ │
│  │  パターン名: [入力欄]                                 │ │
│  │                                                       │ │
│  │  [保存する]                                           │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 銘柄詳細 (P-006)
```
┌─────────────────────────────────────────────────────────────┐
│  ヘッダー                                                   │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐ │
│  │  7203 トヨタ自動車                          [★登録]  │ │
│  │  東証プライム / 輸送用機器                              │ │
│  │                                                       │ │
│  │  ¥2,850  +¥42 (+1.5%)                                  │ │
│  │                                                       │ │
│  │  [チャートエリア]                                      │ │
│  │  日次 | 週次 | 月次 | 年次                              │ │
│  │                                                       │ │
│  │  PER: 12.5  |  PBR: 1.2  |  配当利回り: 3.2%          │ │
│  │  時価総額: ¥35兆円                                     │ │
│  └───────────────────────────────────────────────────────┘ │
│  ┌────────────────────────┐  ┌──────────────────────────┐ │
│  │ 【関連ニュース】        │  │ 【AI分析】               │ │
│  │ ・ニュース1...         │  │ この銘柄はあなたの      │ │
│  │ ・ニュース2...         │  │ 「高配当割安株」パターン │ │
│  │ ・ニュース3...         │  │ に92%マッチしています    │ │
│  └────────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. 開発計画

### フェーズ1: MVP（2-3週間）
- ユーザー認証
- 基本的な株価取得・表示
- 単純な変動検知（閾値）
- ブラウザプッシュ通知

### フェーズ2: AI機能追加（2週間）
- 自然言語パターン入力
- LLMによるパターン解析
- AIレコメンド機能

### フェーズ3: 高度な分析（2週間）
- テクニカル指標（移動平均等）
- 出来高分析
- 通知履歴・設定

---

## 10. 用語集

| 用語 | 説明 |
|---|---|
| PER | 株価収益率（Price Earnings Ratio） |
| PBR | 株価純資産倍率（Price Book-value Ratio） |
| 移動平均線 | 一定期間の株価平均値を線で結んだもの |
| ゴールデンクロス | 短期移動平均線が長期移動平均線を上抜けること |
| VAPID | Voluntary Application Server Identification（Web Push認証方式） |
| LLMOps | 大規模言語モデルの運用管理 |

---

## 11. 参考資料

- [Web Push API - MDN](https://developer.mozilla.org/ja/docs/Web/API/Push_API)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Documentation](https://vitejs.dev/guide/)
- [React Router Documentation](https://reactrouter.com/)

---

## 12. ディレクトリ構造

### 12.1 リポジトリ全体

```
stock-ai-agent/
├── docker-compose.yml          # 開発環境構成
├── Makefile                    # 常用コマンド短縮
├── README.md
├── docs/
│   └── SPEC.md                 # 本書
├── backend/                    # FastAPIバックエンド
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml          # プロジェクト設定
│   ├── alembic/                # データベースマイグレーション
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # アプリケーションエントリポイント
│   │   ├── config.py           # 環境変数・設定
│   │   ├── dependencies.py     # FastAPI依存性注入
│   │   ├── core/               # コア機能
│   │   │   ├── __init__.py
│   │   │   ├── security.py     # JWT・パスワードハッシュ
│   │   │   └── exceptions.py   # カスタム例外
│   │   ├── api/                # APIエンドポイント
│   │   │   ├── __init__.py
│   │   │   ├── deps.py         # 認証依存
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py     # 認証API
│   │   │       ├── users.py    # ユーザーAPI
│   │   │       ├── patterns.py # パターンAPI
│   │   │       ├── stocks.py   # 銘柄API
│   │   │       ├── watchlist.py
│   │   │       ├── recommendations.py
│   │   │       └── notifications.py
│   │   ├── models/             # SQLAlchemyモデル
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── pattern.py
│   │   │   ├── stock.py
│   │   │   ├── stock_price.py
│   │   │   ├── watchlist.py
│   │   │   ├── push_subscription.py
│   │   │   └── notification.py
│   │   ├── schemas/            # Pydanticスキーマ
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── pattern.py
│   │   │   ├── stock.py
│   │   │   └── common.py
│   │   ├── services/           # ビジネスロジック
│   │   │   ├── __init__.py
│   │   │   ├── user_service.py
│   │   │   ├── pattern_service.py
│   │   │   ├── stock_service.py
│   │   │   ├── llm_service.py  # LLM連携
│   │   │   ├── notification_service.py
│   │   │   └── recommendation_service.py
│   │   ├── tasks/              # Celeryタスク
│   │   │   ├── __init__.py
│   │   │   ├── stock_fetcher.py    # 株価取得
│   │   │   ├── pattern_matcher.py  # パターンマッチング
│   │   │   └── notifier.py         # 通知送信
│   │   └── db/                 # データベース設定
│   │       ├── __init__.py
│   │       ├── session.py      # DBセッション
│   │       └── base.py         # Baseモデル
│   └── tests/
│       ├── conftest.py
│       ├── test_api/
│       └── test_services/
├── frontend/                   # Vite + Reactフロントエンド
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── public/
│   │   └── sw.js               # サービスワーカー（プッシュ通知）
│   └── src/
│       ├── main.tsx            # エントリポイント
│       ├── App.tsx
│       ├── vite-env.d.ts
│       ├── components/         # UIコンポーネント
│       │   ├── common/         # 共通コンポーネント
│       │   │   ├── Button.tsx
│       │   │   ├── Input.tsx
│       │   │   ├── Card.tsx
│       │   │   └── Layout.tsx
│       │   ├── auth/           # 認証関連
│       │   │   ├── LoginForm.tsx
│       │   │   └── RegisterForm.tsx
│       │   ├── patterns/       # パターン関連
│       │   │   ├── PatternList.tsx
│       │   │   ├── PatternForm.tsx
│       │   │   └── PatternCard.tsx
│       │   ├── stocks/         # 銘柄関連
│       │   │   ├── StockList.tsx
│       │   │   ├── StockDetail.tsx
│       │   │   ├── StockCard.tsx
│       │   │   └── StockChart.tsx
│       │   └── dashboard/      # ダッシュボード
│       │       ├── Dashboard.tsx
│       │       ├── MarketOverview.tsx
│       │       └── Recommendations.tsx
│       ├── pages/              # ページコンポーネント
│       │   ├── HomePage.tsx
│       │   ├── LoginPage.tsx
│       │   ├── RegisterPage.tsx
│       │   ├── DashboardPage.tsx
│       │   ├── StocksPage.tsx
│       │   ├── StockDetailPage.tsx
│       │   ├── PatternsPage.tsx
│       │   ├── PatternNewPage.tsx
│       │   ├── WatchlistPage.tsx
│       │   └── SettingsPage.tsx
│       ├── hooks/              # カスタムフック
│       │   ├── useAuth.ts
│       │   ├── useApi.ts       # TanStack Queryラッパー
│       │   ├── usePushNotification.ts
│       │   └── useStockData.ts
│       ├── services/           # APIクライアント
│       │   ├── api.ts          # axios設定
│       │   ├── auth.ts
│       │   ├── patterns.ts
│       │   ├── stocks.ts
│       │   └── notifications.ts
│       ├── stores/             # Zustandストア
│       │   ├── authStore.ts
│       │   ├── patternStore.ts
│       │   └── uiStore.ts
│       ├── types/              # TypeScript型定義
│       │   ├── user.ts
│       │   ├── pattern.ts
│       │   ├── stock.ts
│       │   └── api.ts
│       └── utils/              # ユーティリティ
│           ├── format.ts       # 数値・日付フォーマット
│           └── validation.ts   # バリデーション
└── infra/                      # インフラ設定
    ├── docker/
    │   ├── postgres/
    │   └── redis/
    └── k8s/                    # Kubernetesマニフェスト（将来用）
```

---

## 13. 環境変数

### 13.1 バックエンド (.env)

```bash
# アプリケーション
APP_ENV=development              # development | staging | production
APP_PORT=8000
APP_HOST=0.0.0.0
SECRET_KEY=your-secret-key-here  # JWT署名用（本番は必ず変更）

# データベース
DATABASE_URL=postgresql://postgres:postgres@db:5432/stock_ai
DATABASE_POOL_SIZE=10

# Redis（Celery用）
REDIS_URL=redis://redis:6379/0

# JWT設定
ACCESS_TOKEN_EXPIRE_MINUTES=1440     # 24時間
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM設定
LLM_PROVIDER=openai                  # openai | openrouter
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-...
OPENROUTER_HTTP_REFERER=https://your-app.com

# 株価API
STOCK_API_PROVIDER=yfinance          # yfinance | alpha_vantage
ALPHA_VANTAGE_API_KEY=...

# Web Push（VAPID）
VAPID_PUBLIC_KEY=...
VAPID_PRIVATE_KEY=...
VAPID_CLAIMS_SUB=mailto:admin@example.com

# メール（パスワードリセット用）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
FROM_EMAIL=noreply@example.com

# ログ
LOG_LEVEL=INFO                       # DEBUG | INFO | WARNING | ERROR
```

### 13.2 フロントエンド (.env)

```bash
# API設定
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws    # 将来的なWebSocket用

# プッシュ通知
VITE_VAPID_PUBLIC_KEY=...             # Web Push公開鍵

# 機能フラグ
VITE_ENABLE_ANALYTICS=false
```

---

## 14. Docker Compose構成

```yaml
version: '3.8'

services:
  # PostgreSQL + TimescaleDB
  db:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: stock_ai
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # FastAPIバックエンド
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/stock_ai
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - ./backend/.env
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Celery Worker
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/stock_ai
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
    depends_on:
      - db
      - redis
    command: celery -A app.tasks worker --loglevel=info

  # Celery Beat（定期実行）
  beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/stock_ai
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
    depends_on:
      - db
      - redis
    command: celery -A app.tasks beat --loglevel=info

  # Viteフロントエンド
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api/v1
    command: npm run dev -- --host

volumes:
  postgres_data:
  redis_data:
```

---

## 15. Celeryタスク詳細

### 15.1 タスク一覧

| タスク名 | スケジュール | 説明 |
|---|---|---|
| `fetch_daily_stock_prices` | 平日 16:00 JST | 全銘柄の日次株価を取得 |
| `update_stock_metrics` | 平日 16:30 JST | PER/PBR等の指標を更新 |
| `match_patterns` | 平日 17:00 JST | 全ユーザーのパターンと照合 |
| `send_price_alerts` | 平日 17:30 JST | 価格変動アラートを送信 |
| `cleanup_old_notifications` | 毎日 00:00 | 30日以上前の通知を削除 |

### 15.2 タスク実装例

```python
# app/tasks/stock_fetcher.py
from celery import shared_task
from app.services.stock_service import StockService
from app.db.session import SessionLocal

@shared_task(bind=True, max_retries=3)
def fetch_daily_stock_prices(self):
    """全銘柄の日次株価を取得"""
    db = SessionLocal()
    try:
        service = StockService(db)
        stocks = service.get_all_stocks()
        
        for stock in stocks:
            try:
                service.fetch_and_save_price(stock.code)
            except Exception as e:
                logger.error(f"Failed to fetch {stock.code}: {e}")
                continue
        
        return {"status": "success", "processed": len(stocks)}
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()

# app/tasks/pattern_matcher.py
@shared_task
def match_patterns():
    """全パターンを評価してマッチング結果を保存"""
    db = SessionLocal()
    try:
        matcher = PatternMatcher(db)
        patterns = db.query(InvestmentPattern).filter_by(is_active=True).all()
        
        results = []
        for pattern in patterns:
            matches = matcher.find_matches(pattern)
            results.extend(matches)
        
        # 通知キューに追加
        for match in results:
            notify_user.delay(match.user_id, match.stock_id, match.reason)
        
        return {"matches_found": len(results)}
    finally:
        db.close()
```

### 15.3 Celery設定

```python
# app/tasks/__init__.py
from celery import Celery
from app.config import settings

celery_app = Celery(
    "stock_ai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.stock_fetcher",
        "app.tasks.pattern_matcher",
        "app.tasks.notifier",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tokyo",
    enable_utc=True,
    beat_schedule={
        "fetch-prices": {
            "task": "app.tasks.stock_fetcher.fetch_daily_stock_prices",
            "schedule": crontab(hour=16, minute=0, day_of_week="mon-fri"),
        },
        "match-patterns": {
            "task": "app.tasks.pattern_matcher.match_patterns",
            "schedule": crontab(hour=17, minute=0, day_of_week="mon-fri"),
        },
    },
)
```

---

## 16. 認証フロー詳細

### 16.1 JWT認証シーケンス

```
┌─────────┐                    ┌─────────┐                    ┌─────────┐
│  Client │                    │ FastAPI │                    │   DB    │
└────┬────┘                    └────┬────┘                    └────┬────┘
     │                              │                              │
     │  POST /api/auth/login        │                              │
     │  {email, password}           │                              │
     │─────────────────────────────▶│                              │
     │                              │                              │
     │                              │  SELECT * FROM users         │
     │                              │  WHERE email = ?             │
     │                              │─────────────────────────────▶│
     │                              │                              │
     │                              │  password_hash照合           │
     │                              │◀─────────────────────────────│
     │                              │                              │
     │                              │  access_token生成            │
     │                              │  refresh_token生成           │
     │                              │                              │
     │  {access, refresh}           │                              │
     │◀─────────────────────────────│                              │
     │                              │                              │
     │  [以降のリクエスト]           │                              │
     │  Authorization: Bearer {token}│                              │
     │─────────────────────────────▶│                              │
     │                              │  JWT検証                     │
     │                              │  有効期限チェック             │
     │                              │                              │
     │  レスポンス                   │                              │
     │◀─────────────────────────────│                              │
     │                              │                              │
     │  POST /api/auth/refresh      │                              │
     │  {refresh_token}             │                              │
     │─────────────────────────────▶│                              │
     │                              │  refresh_token検証           │
     │                              │                              │
     │  {access_token}              │                              │
     │◀─────────────────────────────│                              │
```

### 16.2 JWTペイロード構造

**Access Token**
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "type": "access",
  "exp": 1710604800,
  "iat": 1710518400
}
```

**Refresh Token**
```json
{
  "sub": "user-uuid",
  "type": "refresh",
  "jti": "unique-token-id",
  "exp": 1711123200,
  "iat": 1710518400
}
```

### 16.3 トークンリフレッシュフロー

1. アクセストークン有効期限切れ（401）
2. フロントエンドがリフレッシュエンドポイントを呼び出し
3. リフレッシュトークンを検証
4. 新しいアクセストークンを発行
5. リクエストをリトライ

```typescript
// frontend/src/services/api.ts
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('/api/auth/refresh', {
          refresh_token: refreshToken
        });
        
        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // リフレッシュ失敗 → ログアウト
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
```

---

## 17. LLMプロンプト設計

### 17.1 パターン解析プロンプト

```python
PATTERN_PARSE_PROMPT = """
あなたは投資パターン解析のエキスパートです。
ユーザーの自然言語入力から、投資条件を構造化データに変換してください。

入力: {user_input}

以下のJSON形式で出力してください:
{{
  "strategy": "戦略タイプ (dividend_focus|growth|value|technical|hybrid)",
  "filters": {{
    "per_min": float or null,
    "per_max": float or null,
    "pbr_min": float or null,
    "pbr_max": float or null,
    "dividend_yield_min": float or null,
    "dividend_yield_max": float or null,
    "market_cap_min": int or null,
    "market_cap_max": int or null,
    "price_change_min": float or null,  # 変動率(%)
    "price_change_max": float or null,
    "volume_surge": bool,  # 出来高急増を検知
    "sectors": [str] or null,  # 業種フィルタ
    "markets": [str] or null   # 市場フィルタ
  }},
  "sort_by": "per|pbr|dividend_yield|market_cap|price_change",
  "sort_order": "asc|desc",
  "keywords": [str]  # 入力から抽出したキーワード
}}

ルール:
1. 数値は必ず数値型で出力（文字列ではない）
2. 単位は削除（"倍"、"%"、"円"など）
3. 不明な条件はnull
4. 日本語の市場名は英語に変換（"東証プライム" → "prime"）
"""
```

### 17.2 レコメンド理由生成プロンプト

```python
RECOMMENDATION_REASON_PROMPT = """
ユーザーに対して、なぜこの銘柄が推奨されるかを説明してください。

ユーザー情報:
- パターン名: {pattern_name}
- パターンフィルタ: {filters}

銘柄情報:
- コード: {stock_code}
- 名前: {stock_name}
- 現在価格: {current_price}円
- PER: {per}
- PBR: {pbr}
- 配当利回り: {dividend_yield}%
- 前日比: {price_change}%

マッチングスコア: {match_score}

以下の条件で説明を作成してください:
1. 3-4文程度の簡潔な説明
2. パターン条件との適合点を強調
3. 具体的な数値を含める
4. 投資判断に役立つ情報を含める
5. 過度な推奨は避け、事実に基づいた説明にする

出力は日本語で、自然な文章としてください。
"""
```

---

## 18. テスト戦略

### 18.1 テスト構成

```
tests/
├── unit/                      # 単体テスト
│   ├── test_models.py
│   ├── test_services.py
│   └── test_tasks.py
├── integration/               # 統合テスト
│   ├── test_api/
│   │   ├── test_auth.py
│   │   ├── test_patterns.py
│   │   └── test_stocks.py
│   └── test_db.py
├── e2e/                       # E2Eテスト
│   └── test_user_flows.py
├── fixtures/                  # テストデータ
│   ├── users.json
│   └── stocks.json
└── conftest.py               # 共通fixture
```

### 18.2 テスト方針

| 種別 | カバレッジ目標 | ツール | 実行タイミング |
|---|---|---|---|
| 単体テスト | 80%以上 | pytest | 毎コミット |
| 統合テスト | APIエンドポイント全網羅 | pytest + TestClient | PR時 |
| E2Eテスト | 主要フロー | Playwright | リリース前 |

### 18.3 テスト例

```python
# tests/integration/test_api/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAuth:
    def test_register_success(self):
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "display_name": "Test User"
        })
        assert response.status_code == 201
        assert "access_token" in response.json()

    def test_register_duplicate_email(self, existing_user):
        response = client.post("/api/v1/auth/register", json={
            "email": existing_user.email,
            "password": "SecurePass123!",
            "display_name": "Test User"
        })
        assert response.status_code == 409

    def test_login_success(self, existing_user):
        response = client.post("/api/v1/auth/login", json={
            "email": existing_user.email,
            "password": "password123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_invalid_credentials(self):
        response = client.post("/api/v1/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpass"
        })
        assert response.status_code == 401
```

---

## 19. デプロイメント構成

### 19.1 本番環境構成（Railway想定）

```
┌────────────────────────────────────────────────────────────┐
│                        Railway                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  PostgreSQL │  │    Redis    │  │   FastAPI Backend   │ │
│  │  (Managed)  │  │  (Managed)  │  │    (Auto Scale)     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│         │                │                     │            │
│         └────────────────┴─────────────────────┘            │
│                                               │             │
│  ┌────────────────────────────────────────────┘             │
│  │            Vite Frontend (Static)                        │
│  │            (Vercel / Cloudflare Pages)                   │
│  └─────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### 19.2 環境別設定

| 項目 | 開発 | ステージング | 本番 |
|---|---|---|---|
| DB | Docker | Railway Managed | Railway Managed |
| Redis | Docker | Railway Managed | Railway Managed |
| Worker | Docker | Railway | Railway |
| フロント | localhost:5173 | Vercel Preview | Vercel Production |
| ログレベル | DEBUG | INFO | WARNING |
| 株価API | yfinance | Alpha Vantage | Alpha Vantage |
| LLM | OpenAI | OpenAI | OpenRouter |

### 19.3 CI/CDパイプライン

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: docker-compose -f docker-compose.test.yml up --abort-on-container-exit

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        run: railway up --service backend
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Vercel
        run: vercel --prod
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
```

---

## 21. AIエージェントアーキテクチャ

### 21.1 マルチエージェント構成

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         エージェントオーケストレーター                      │
│                    （AgentOrchestrator - 中央制御）                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
           ▼                        ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   監視エージェント   │  │   分析エージェント   │  │   提案エージェント   │
│  (MonitoringAgent)  │  │  (AnalysisAgent)    │  │ (RecommendationAgent)│
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ 責任: 市場・銘柄の   │  │ 責任: データ分析・   │  │ 責任: ユーザーへの   │
│       継続的監視    │  │       洞察生成      │  │       提案・通知     │
│                     │  │                     │  │                     │
│ トリガー:           │  │ トリガー:           │  │ トリガー:           │
│ - 定期的スケジュール │  │ - 監視エージェント   │  │ - 分析エージェント   │
│ - 価格変動検知      │  │   からの依頼        │  │   からの依頼        │
│                     │  │ - ユーザー直接依頼   │  │ - 時間ベース        │
│                     │  │                     │  │                     │
│ 使用ツール:         │  │ 使用ツール:         │  │ 使用ツール:         │
│ - 株価取得          │  │ - ニュース検索      │  │ - パターンマッチング │
│ - アラート検知      │  │ - 決算データ取得    │  │ - 通知送信          │
│ - 閾値チェック      │  │ - テクニカル分析    │  │ - メール送信        │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
           │                        │                        │
           └────────────────────────┴────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────┐
                    │        共有メモリ            │
                    │    （Agent Shared Memory）   │
                    │                             │
                    │  - 監視状態                  │
                    │  - 分析結果                  │
                    │  - 提案履歴                  │
                    │  - ユーザー・フィードバック   │
                    └─────────────────────────────┘
```

### 21.2 エージェント定義

#### 監視エージェント (MonitoringAgent)

```python
class MonitoringAgent(BaseAgent):
    """
    市場・銘柄を継続的に監視し、重要な変化を検知するエージェント
    """
    
    name = "monitoring_agent"
    description = "株価・市場の継続的監視と変化検知"
    
    tools = [
        "fetch_stock_price",      # 株価取得
        "check_price_threshold",   # 価格閾値チェック
        "detect_volume_surge",     # 出来高急増検知
        "detect_moving_average",   # 移動平均線検知
        "get_market_overview",     # 市場概況取得
    ]
    
    async def run(self, context: AgentContext) -> AgentResult:
        """
        監視ループ:
        1. 全ウォッチリスト銘柄を取得
        2. 各銘柄の価格・出来高を確認
        3. 閾値超過を検知
        4. 分析エージェントに依頼 or 直接提案エージェントに依頼
        """
        pass
```

#### 分析エージェント (AnalysisAgent)

```python
class AnalysisAgent(BaseAgent):
    """
    データを分析し、洞察を生成するエージェント
    """
    
    name = "analysis_agent"
    description = "銘柄分析・ニュース分析・技術的分析"
    
    tools = [
        "search_news",            # ニュース検索
        "fetch_financial_data",   # 決算データ取得
        "technical_analysis",     # テクニカル分析
        "sentiment_analysis",     # 感情分析
        "compare_with_sector",    # セクター比較
    ]
    
    async def run(self, context: AgentContext) -> AgentResult:
        """
        分析フロー:
        1. 対象銘柄の基本情報取得
        2. 関連ニュース検索・分析
        3. 決算データ確認
        4. テクニカル指標計算
        5. 分析レポート生成
        6. 提案エージェントに依頼
        """
        pass
```

#### 提案エージェント (RecommendationAgent)

```python
class RecommendationAgent(BaseAgent):
    """
    ユーザーの投資パターンに基づき、最適な提案を生成するエージェント
    """
    
    name = "recommendation_agent"
    description = "パターンマッチング・提案生成・通知送信"
    
    tools = [
        "match_user_pattern",     # ユーザーパターンマッチング
        "generate_recommendation", # 提案生成
        "send_notification",      # 通知送信
        "send_email",             # メール送信
        "save_recommendation",    # 提案保存
    ]
    
    async def run(self, context: AgentContext) -> AgentResult:
        """
        提案フロー:
        1. ユーザーの投資パターンを取得
        2. 分析結果とパターンを照合
        3. マッチングスコア計算
        4. 提案理由生成（LLM使用）
        5. 通知送信判断
        6. ユーザーに通知
        """
        pass
```

### 21.3 エージェント間通信

```python
# エージェント間メッセージ形式
class AgentMessage(BaseModel):
    message_id: UUID                    # メッセージID
    from_agent: str                     # 送信元エージェント
    to_agent: str                       # 宛先エージェント
    message_type: MessageType           # メッセージタイプ
    payload: dict                       # ペイロード
    timestamp: datetime
    priority: Priority = Priority.NORMAL # 優先度

class MessageType(str, Enum):
    REQUEST_ANALYSIS = "request_analysis"      # 分析依頼
    REQUEST_RECOMMENDATION = "request_rec"     # 提案依頼
    ANALYSIS_COMPLETE = "analysis_complete"    # 分析完了
    RECOMMENDATION_READY = "rec_ready"         # 提案準備完了
    ALERT_TRIGGERED = "alert_triggered"        # アラート発火
    FEEDBACK_RECEIVED = "feedback_received"    # フィードバック受信

# メッセージブローカー（Redis使用）
class AgentMessageBroker:
    async def publish(self, message: AgentMessage):
        """メッセージを公開"""
        await redis.publish(f"agent:{message.to_agent}", message.json())
    
    async def subscribe(self, agent_name: str):
        """エージェント宛てメッセージを購読"""
        async for message in redis.subscribe(f"agent:{agent_name}"):
            yield AgentMessage.parse_raw(message)
```

### 21.4 エージェントツール定義

| ツール名 | 説明 | 使用エージェント |
|---|---|---|
| `fetch_stock_price` | 指定銘柄の最新株価を取得 | 監視エージェント |
| `check_price_threshold` | 価格が閾値を超えたかチェック | 監視エージェント |
| `detect_volume_surge` | 出来高の急増を検知 | 監視エージェント |
| `detect_moving_average` | 移動平均線クロスを検知 | 監視エージェント |
| `search_news` | 銘柄関連ニュースを検索 | 分析エージェント |
| `fetch_financial_data` | 決算データを取得 | 分析エージェント |
| `technical_analysis` | テクニカル指標を計算 | 分析エージェント |
| `sentiment_analysis` | ニュースの感情分析 | 分析エージェント |
| `match_user_pattern` | ユーザー投資パターンと照合 | 提案エージェント |
| `generate_recommendation` | LLMで提案理由を生成 | 提案エージェント |
| `send_notification` | ブラウザプッシュ通知を送信 | 提案エージェント |
| `save_to_memory` | 分析結果を共有メモリに保存 | 全エージェント |

### 21.5 エージェントワークフロー例

**シナリオ: ウォッチリスト銘柄の急騰検知**

```
[16:00 JST] Celery Beatが監視エージェントを起動
       │
       ▼
┌──────────────┐
│ 監視エージェント │
│ ・全銘柄の価格取得 │
│ ・前日比を計算    │
│ ・閾値(±5%)超過を検知 │
└──────┬───────┘
       │ 銘柄Aが+8%上昇を検知
       │ MessageType.ALERT_TRIGGERED
       ▼
┌──────────────┐
│ 分析エージェント │ ← 依頼を受信
│ ・銘柄Aのニュース検索 │
│ ・決算データ確認    │
│ ・テクニカル分析    │
│ ・分析レポート生成  │
└──────┬───────┘
       │ MessageType.ANALYSIS_COMPLETE
       ▼
┌──────────────┐
│ 提案エージェント │ ← 依頼を受信
│ ・ユーザーのパターン取得 │
│ ・マッチングスコア計算   │
│ ・LLMで提案理由生成     │
│ ・スコア90%超なら通知   │
└──────┬───────┘
       │ プッシュ通知送信
       ▼
┌──────────────┐
│ ユーザーへ通知   │
│ "銘柄Aが+8%、   │
│  あなたの高配当 │
│  パターンにマッチ" │
└──────────────┘
```

### 21.6 共有メモリ（Agent Shared Memory）

```python
# エージェント間で共有する状態・履歴
class AgentSharedMemory:
    """
    Redisベースの共有メモリ
    """
    
    async def save_monitoring_state(self, stock_code: str, state: dict):
        """監視状態を保存"""
        key = f"monitoring:{stock_code}"
        await redis.hset(key, mapping=state)
        await redis.expire(key, 86400)  # 24時間保持
    
    async def get_analysis_history(self, stock_code: str, limit: int = 10):
        """分析履歴を取得"""
        key = f"analysis_history:{stock_code}"
        return await redis.lrange(key, 0, limit - 1)
    
    async def save_user_feedback(self, user_id: str, recommendation_id: str, feedback: dict):
        """ユーザーフィードバックを保存（学習用）"""
        key = f"feedback:{user_id}"
        await redis.lpush(key, json.dumps({
            "recommendation_id": recommendation_id,
            "feedback": feedback,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    async def get_user_context(self, user_id: str) -> UserContext:
        """ユーザーコンテキストを取得"""
        # 過去のフィードバック、閲覧履歴、投資パターンを統合
        pass
```

### 21.7 AgentOps（エージェント監視）

```python
# エージェント実行の可視化・評価
class AgentOps:
    """
    エージェントの実行ログ、トレース、評価を管理
    """
    
    async def trace_execution(self, agent_name: str, task_id: str):
        """実行トレース開始"""
        trace = {
            "agent": agent_name,
            "task_id": task_id,
            "start_time": datetime.utcnow(),
            "steps": []
        }
        return trace
    
    async def log_step(self, trace_id: str, step: dict):
        """実行ステップを記録"""
        step["timestamp"] = datetime.utcnow()
        await redis.lpush(f"trace:{trace_id}", json.dumps(step))
    
    async def log_tool_usage(self, agent_name: str, tool_name: str, duration_ms: int, success: bool):
        """ツール使用ログ"""
        await redis.hincrby(f"agent_stats:{agent_name}", f"tool:{tool_name}:count", 1)
        await redis.hincrby(f"agent_stats:{agent_name}", f"tool:{tool_name}:duration", duration_ms)
    
    async def evaluate_recommendation(self, recommendation_id: str, user_action: str):
        """
        提案の効果を評価
        user_action: "clicked" | "ignored" | "dismissed" | "acted"
        """
        await redis.hset(f"rec_eval:{recommendation_id}", "user_action", user_action)
        await redis.hset(f"rec_eval:{recommendation_id}", "evaluated_at", datetime.utcnow().isoformat())
```

### 21.8 エージェント設定

```yaml
# config/agents.yml
agents:
  monitoring_agent:
    enabled: true
    schedule: "0 16 * * 1-5"  # 平日16:00
    config:
      price_check_interval: 300  # 5分間隔
      alert_threshold: 5.0       # ±5%
      volume_surge_ratio: 2.0    # 出来高2倍
  
  analysis_agent:
    enabled: true
    config:
      max_news_items: 10
      sentiment_threshold: 0.3
      technical_indicators: ["sma", "ema", "rsi", "macd"]
  
  recommendation_agent:
    enabled: true
    config:
      min_match_score: 0.7       # 通知閾値
      max_daily_notifications: 5 # 1日最大通知数
      cooldown_hours: 24         # 同一銘柄通知間隔
```

---

## 20. セキュリティ対策

### 20.1 対策一覧

| 項目 | 対策内容 | 実装場所 |
|---|---|---|
| SQLインジェクション | SQLAlchemy ORM使用（パラメータ化クエリ） | DB層 |
| XSS | React自動エスケープ + CSPヘッダー | フロント/サーバー |
| CSRF | SameSite Cookie + CORS制限 | サーバー |
| 認証 Bypass | JWT署名検証 + 有効期限チェック | ミドルウェア |
| レート制限 | slowapiによるIP/エンドポイント制限 | API層 |
| 機密情報漏洩 | .envファイル管理、ログ除外 | 設定 |
| プッシュ通知 | VAPID認証必須 | Web Push層 |

### 20.2 CSPヘッダー

```python
# app/main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.your-domain.com;"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response
```

---

## 21. AIエージェントアーキテクチャ

### 21.1 マルチエージェント構成

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         エージェントオーケストレーター                      │
│                    （AgentOrchestrator - 中央制御）                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
           ▼                        ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   監視エージェント   │  │   分析エージェント   │  │   提案エージェント   │
│  (MonitoringAgent)  │  │  (AnalysisAgent)    │  │ (RecommendationAgent)│
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ 責任: 市場・銘柄の   │  │ 責任: データ分析・   │  │ 責任: ユーザーへの   │
│       継続的監視    │  │       洞察生成      │  │       提案・通知     │
│                     │  │                     │  │                     │
│ トリガー:           │  │ トリガー:           │  │ トリガー:           │
│ - 定期的スケジュール │  │ - 監視エージェント   │  │ - 分析エージェント   │
│ - 価格変動検知      │  │   からの依頼        │  │   からの依頼        │
│                     │  │ - ユーザー直接依頼   │  │ - 時間ベース        │
│                     │  │                     │  │                     │
│ 使用ツール:         │  │ 使用ツール:         │  │ 使用ツール:         │
│ - 株価取得          │  │ - ニュース検索      │  │ - パターンマッチング │
│ - アラート検知      │  │ - 決算データ取得    │  │ - 通知送信          │
│ - 閾値チェック      │  │ - テクニカル分析    │  │ - メール送信        │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
           │                        │                        │
           └────────────────────────┴────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────┐
                    │        共有メモリ            │
                    │    （Agent Shared Memory）   │
                    │                             │
                    │  - 監視状態                  │
                    │  - 分析結果                  │
                    │  - 提案履歴                  │
                    │  - ユーザー・フィードバック   │
                    └─────────────────────────────┘
```

### 21.2 エージェント定義

#### 監視エージェント (MonitoringAgent)

```python
class MonitoringAgent(BaseAgent):
    """
    市場・銘柄を継続的に監視し、重要な変化を検知するエージェント
    """
    
    name = "monitoring_agent"
    description = "株価・市場の継続的監視と変化検知"
    
    tools = [
        "fetch_stock_price",      # 株価取得
        "check_price_threshold",   # 価格閾値チェック
        "detect_volume_surge",     # 出来高急増検知
        "detect_moving_average",   # 移動平均線検知
        "get_market_overview",     # 市場概況取得
    ]
    
    async def run(self, context: AgentContext) -> AgentResult:
        """
        監視ループ:
        1. 全ウォッチリスト銘柄を取得
        2. 各銘柄の価格・出来高を確認
        3. 閾値超過を検知
        4. 分析エージェントに依頼 or 直接提案エージェントに依頼
        """
        pass
```

#### 分析エージェント (AnalysisAgent)

```python
class AnalysisAgent(BaseAgent):
    """
    データを分析し、洞察を生成するエージェント
    """
    
    name = "analysis_agent"
    description = "銘柄分析・ニュース分析・技術的分析"
    
    tools = [
        "search_news",            # ニュース検索
        "fetch_financial_data",   # 決算データ取得
        "technical_analysis",     # テクニカル分析
        "sentiment_analysis",     # 感情分析
        "compare_with_sector",    # セクター比較
    ]
    
    async def run(self, context: AgentContext) -> AgentResult:
        """
        分析フロー:
        1. 対象銘柄の基本情報取得
        2. 関連ニュース検索・分析
        3. 決算データ確認
        4. テクニカル指標計算
        5. 分析レポート生成
        6. 提案エージェントに依頼
        """
        pass
```

#### 提案エージェント (RecommendationAgent)

```python
class RecommendationAgent(BaseAgent):
    """
    ユーザーの投資パターンに基づき、最適な提案を生成するエージェント
    """
    
    name = "recommendation_agent"
    description = "パターンマッチング・提案生成・通知送信"
    
    tools = [
        "match_user_pattern",     # ユーザーパターンマッチング
        "generate_recommendation", # 提案生成
        "send_notification",      # 通知送信
        "send_email",             # メール送信
        "save_recommendation",    # 提案保存
    ]
    
    async def run(self, context: AgentContext) -> AgentResult:
        """
        提案フロー:
        1. ユーザーの投資パターンを取得
        2. 分析結果とパターンを照合
        3. マッチングスコア計算
        4. 提案理由生成（LLM使用）
        5. 通知送信判断
        6. ユーザーに通知
        """
        pass
```

### 21.3 エージェント間通信

```python
# エージェント間メッセージ形式
class AgentMessage(BaseModel):
    message_id: UUID                    # メッセージID
    from_agent: str                     # 送信元エージェント
    to_agent: str                       # 宛先エージェント
    message_type: MessageType           # メッセージタイプ
    payload: dict                       # ペイロード
    timestamp: datetime
    priority: Priority = Priority.NORMAL # 優先度

class MessageType(str, Enum):
    REQUEST_ANALYSIS = "request_analysis"      # 分析依頼
    REQUEST_RECOMMENDATION = "request_rec"     # 提案依頼
    ANALYSIS_COMPLETE = "analysis_complete"    # 分析完了
    RECOMMENDATION_READY = "rec_ready"         # 提案準備完了
    ALERT_TRIGGERED = "alert_triggered"        # アラート発火
    FEEDBACK_RECEIVED = "feedback_received"    # フィードバック受信

# メッセージブローカー（Redis使用）
class AgentMessageBroker:
    async def publish(self, message: AgentMessage):
        """メッセージを公開"""
        await redis.publish(f"agent:{message.to_agent}", message.json())
    
    async def subscribe(self, agent_name: str):
        """エージェント宛てメッセージを購読"""
        async for message in redis.subscribe(f"agent:{agent_name}"):
            yield AgentMessage.parse_raw(message)
```

### 21.4 エージェントツール定義

| ツール名 | 説明 | 使用エージェント |
|---|---|---|
| `fetch_stock_price` | 指定銘柄の最新株価を取得 | 監視エージェント |
| `check_price_threshold` | 価格が閾値を超えたかチェック | 監視エージェント |
| `detect_volume_surge` | 出来高の急増を検知 | 監視エージェント |
| `detect_moving_average` | 移動平均線クロスを検知 | 監視エージェント |
| `search_news` | 銘柄関連ニュースを検索 | 分析エージェント |
| `fetch_financial_data` | 決算データを取得 | 分析エージェント |
| `technical_analysis` | テクニカル指標を計算 | 分析エージェント |
| `sentiment_analysis` | ニュースの感情分析 | 分析エージェント |
| `match_user_pattern` | ユーザー投資パターンと照合 | 提案エージェント |
| `generate_recommendation` | LLMで提案理由を生成 | 提案エージェント |
| `send_notification` | ブラウザプッシュ通知を送信 | 提案エージェント |
| `save_to_memory` | 分析結果を共有メモリに保存 | 全エージェント |

### 21.5 エージェントワークフロー例

**シナリオ: ウォッチリスト銘柄の急騰検知**

```
[16:00 JST] Celery Beatが監視エージェントを起動
       │
       ▼
┌──────────────┐
│ 監視エージェント │
│ ・全銘柄の価格取得 │
│ ・前日比を計算    │
│ ・閾値(±5%)超過を検知 │
└──────┬───────┘
       │ 銘柄Aが+8%上昇を検知
       │ MessageType.ALERT_TRIGGERED
       ▼
┌──────────────┐
│ 分析エージェント │ ← 依頼を受信
│ ・銘柄Aのニュース検索 │
│ ・決算データ確認    │
│ ・テクニカル分析    │
│ ・分析レポート生成  │
└──────┬───────┘
       │ MessageType.ANALYSIS_COMPLETE
       ▼
┌──────────────┐
│ 提案エージェント │ ← 依頼を受信
│ ・ユーザーのパターン取得 │
│ ・マッチングスコア計算   │
│ ・LLMで提案理由生成     │
│ ・スコア90%超なら通知   │
└──────┬───────┘
       │ プッシュ通知送信
       ▼
┌──────────────┐
│ ユーザーへ通知   │
│ "銘柄Aが+8%、   │
│  あなたの高配当 │
│  パターンにマッチ" │
└──────────────┘
```

### 21.6 共有メモリ（Agent Shared Memory）

```python
# エージェント間で共有する状態・履歴
class AgentSharedMemory:
    """
    Redisベースの共有メモリ
    """
    
    async def save_monitoring_state(self, stock_code: str, state: dict):
        """監視状態を保存"""
        key = f"monitoring:{stock_code}"
        await redis.hset(key, mapping=state)
        await redis.expire(key, 86400)  # 24時間保持
    
    async def get_analysis_history(self, stock_code: str, limit: int = 10):
        """分析履歴を取得"""
        key = f"analysis_history:{stock_code}"
        return await redis.lrange(key, 0, limit - 1)
    
    async def save_user_feedback(self, user_id: str, recommendation_id: str, feedback: dict):
        """ユーザーフィードバックを保存（学習用）"""
        key = f"feedback:{user_id}"
        await redis.lpush(key, json.dumps({
            "recommendation_id": recommendation_id,
            "feedback": feedback,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    async def get_user_context(self, user_id: str) -> UserContext:
        """ユーザーコンテキストを取得"""
        # 過去のフィードバック、閲覧履歴、投資パターンを統合
        pass
```

### 21.7 AgentOps（エージェント監視）

```python
# エージェント実行の可視化・評価
class AgentOps:
    """
    エージェントの実行ログ、トレース、評価を管理
    """
    
    async def trace_execution(self, agent_name: str, task_id: str):
        """実行トレース開始"""
        trace = {
            "agent": agent_name,
            "task_id": task_id,
            "start_time": datetime.utcnow(),
            "steps": []
        }
        return trace
    
    async def log_step(self, trace_id: str, step: dict):
        """実行ステップを記録"""
        step["timestamp"] = datetime.utcnow()
        await redis.lpush(f"trace:{trace_id}", json.dumps(step))
    
    async def log_tool_usage(self, agent_name: str, tool_name: str, duration_ms: int, success: bool):
        """ツール使用ログ"""
        await redis.hincrby(f"agent_stats:{agent_name}", f"tool:{tool_name}:count", 1)
        await redis.hincrby(f"agent_stats:{agent_name}", f"tool:{tool_name}:duration", duration_ms)
    
    async def evaluate_recommendation(self, recommendation_id: str, user_action: str):
        """
        提案の効果を評価
        user_action: "clicked" | "ignored" | "dismissed" | "acted"
        """
        await redis.hset(f"rec_eval:{recommendation_id}", "user_action", user_action)
        await redis.hset(f"rec_eval:{recommendation_id}", "evaluated_at", datetime.utcnow().isoformat())
```

### 21.8 エージェント設定

```yaml
# config/agents.yml
agents:
  monitoring_agent:
    enabled: true
    schedule: "0 16 * * 1-5"  # 平日16:00
    config:
      price_check_interval: 300  # 5分間隔
      alert_threshold: 5.0       # ±5%
      volume_surge_ratio: 2.0    # 出来高2倍
  
  analysis_agent:
    enabled: true
    config:
      max_news_items: 10
      sentiment_threshold: 0.3
      technical_indicators: ["sma", "ema", "rsi", "macd"]
  
  recommendation_agent:
    enabled: true
    config:
      min_match_score: 0.7       # 通知閾値
      max_daily_notifications: 5 # 1日最大通知数
      cooldown_hours: 24         # 同一銘柄通知間隔
```

---

## 22. 変更履歴

| 日付 | バージョン | 変更内容 |
|---|---|---|
| 2026-03-16 | 0.1.0 | 初版作成 |

| 項目 | 対策内容 | 実装場所 |
|---|---|---|
| SQLインジェクション | SQLAlchemy ORM使用（パラメータ化クエリ） | DB層 |
| XSS | React自動エスケープ + CSPヘッダー | フロント/サーバー |
| CSRF | SameSite Cookie + CORS制限 | サーバー |
| 認証 Bypass | JWT署名検証 + 有効期限チェック | ミドルウェア |
| レート制限 | slowapiによるIP/エンドポイント制限 | API層 |
| 機密情報漏洩 | .envファイル管理、ログ除外 | 設定 |
| プッシュ通知 | VAPID認証必須 | Web Push層 |

### 20.2 CSPヘッダー

```python
# app/main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.your-domain.com;"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response
```
