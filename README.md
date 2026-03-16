# Stock AI Agent

個人投資家向けのAI株価監視・通知アプリケーション。

## 概要

- 自然言語で投資パターンを登録
- AIエージェントが市場を監視・分析
- ブラウザプッシュ通知で変動をお知らせ

## 技術スタック

- **Frontend**: Vite + React + React Router (TypeScript)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL + TimescaleDB
- **Task Queue**: Celery + Redis
- **AIエージェント**: PydanticAI
- **エージェント連携**: Redis Pub/Sub (独自実装)
- **Push Notification**: Web Push API (VAPID)

## クイックスタート

### 方法1: Docker Compose（推奨）

```bash
# 開発環境起動
docker-compose up --build

# バックグラウンドで起動
docker-compose up -d

# 停止
docker-compose down

# 完全削除（データも）
docker-compose down -v
```

起動後:
- フロントエンド: http://localhost:5173
- バックエンドAPI: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs

### 方法2: ローカル開発

#### 前提条件
- Python 3.12+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

#### セットアップ

```bash
# 1. リポジトリをクローン
git clone <repository-url>
cd stock-ai-agent

# 2. 環境変数を設定
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# .envファイルを編集して必要な値を設定

# 3. 依存関係をインストール
make install
# または手動で:
# cd backend && pip install -r requirements.txt
# cd frontend && npm install
```

#### 起動

```bash
# ターミナル1: バックエンド
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ターミナル2: フロントエンド
cd frontend
npm run dev
```

## 開発コマンド

```bash
# バックエンド起動
make backend

# フロントエンド起動
make frontend

# Docker Compose起動
make dev

# テスト実行
make test

# リンター実行
make lint
```

## プロジェクト構造

```
stock-ai-agent/
├── docker-compose.yml      # 開発環境構成
├── Makefile                # 常用コマンド
├── docs/
│   └── SPEC.md             # 詳細仕様書
├── backend/                # FastAPIバックエンド
│   ├── app/
│   │   ├── main.py         # アプリケーションエントリ
│   │   ├── config.py       # 設定
│   │   ├── api/v1/         # APIエンドポイント
│   │   ├── models/         # SQLAlchemyモデル
│   │   ├── schemas/        # Pydanticスキーマ
│   │   ├── services/       # ビジネスロジック
│   │   ├── agents/         # AIエージェント (予定)
│   │   ├── tasks/          # Celeryタスク
│   │   └── db/             # データベース設定
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Vite + Reactフロントエンド
│   ├── src/
│   │   ├── pages/          # ページコンポーネント
│   │   ├── components/     # UIコンポーネント
│   │   ├── hooks/          # カスタムフック
│   │   ├── services/       # APIクライアント
│   │   └── stores/         # Zustandストア
│   ├── package.json
│   └── Dockerfile
└── infra/                  # インフラ設定
    └── docker/
```

## 環境変数

### バックエンド (.env)

```bash
# 必須
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/stock_ai
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here

# LLM
OPENAI_API_KEY=sk-...
# または
OPENROUTER_API_KEY=sk-...

# 株価API (本番)
ALPHA_VANTAGE_API_KEY=...
```

### フロントエンド (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## ドキュメント

詳細仕様は [docs/SPEC.md](./docs/SPEC.md) を参照。

## ライセンス

MIT
