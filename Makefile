.PHONY: help install backend frontend dev test lint clean

help:
	@echo "Stock AI Agent - 開発コマンド"
	@echo ""
	@echo "  make install     - 依存関係をインストール"
	@echo "  make backend     - バックエンドサーバーを起動"
	@echo "  make frontend    - フロントエンド開発サーバーを起動"
	@echo "  make dev         - Docker Composeで開発環境を起動"
	@echo "  make test        - テストを実行"
	@echo "  make lint        - リンターを実行"
	@echo "  make clean       - 一時ファイルを削除"

# インストール
install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

# バックエンド起動
backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# フロントエンド起動
frontend:
	cd frontend && npm run dev

# Docker Composeで開発環境起動
dev:
	docker-compose up --build

# Docker Composeでバックグラウンド起動
dev-d:
	docker-compose up --build -d

# Docker Compose停止
dev-stop:
	docker-compose down

# Docker Compose完全削除（データも）
dev-clean:
	docker-compose down -v

# テスト
test:
	cd backend && pytest -v

# リンター
lint:
	cd backend && black . && isort . && flake8
	cd frontend && npm run lint

# クリーン
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf frontend/node_modules
	rm -rf frontend/dist
