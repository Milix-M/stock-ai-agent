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
│         Next.js (Frontend)          │
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
| **フロントエンド** | Next.js | App Router, TypeScript |
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
- [Next.js Documentation](https://nextjs.org/docs)
