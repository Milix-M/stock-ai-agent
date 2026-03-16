# Stock AI Agent

個人投資家向けのAI株価監視・通知アプリケーション。

## 概要

- 自然言語で投資パターンを登録
- AIが「オトクな株」を自動検出
- ブラウザプッシュ通知で変動をお知らせ

## 技術スタック

- **Frontend**: Vite + React + React Router (TypeScript)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL + TimescaleDB
- **Task Queue**: Celery + Redis
- **LLM**: OpenAI API / OpenRouter
- **Push Notification**: Web Push API (VAPID)

## 開発環境のセットアップ

```bash
# リポジトリのクローン
git clone <repository-url>
cd stock-ai-agent

# Docker Composeで起動
docker-compose up -d

# 依存関係のインストール（バックエンド）
cd backend
pip install -r requirements.txt

# 依存関係のインストール（フロントエンド）
cd ../frontend
npm install
```

## プロジェクト構造

```
stock-ai-agent/
├── docs/               # ドキュメント
│   └── requirements.md # 要件定義書
├── backend/            # FastAPIバックエンド
├── frontend/           # Next.jsフロントエンド
├── docker-compose.yml  # 開発環境構成
└── README.md
```

## ライセンス

MIT
