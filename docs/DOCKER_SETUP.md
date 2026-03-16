# Docker セットアップ手順

## macOS

### Docker Desktop をインストール

```bash
# Homebrew でインストール（推奨）
brew install --cask docker

# または公式サイトからダウンロード
# https://www.docker.com/products/docker-desktop
```

### インストール後の確認

```bash
# Docker バージョン確認
docker --version
docker-compose --version

# 動作確認
docker run hello-world
```

---

## Windows

### Docker Desktop をインストール

1. WSL2 を有効化（PowerShell で管理者実行）:
```powershell
wsl --install
```

2. Docker Desktop をダウンロード・インストール:
   https://www.docker.com/products/docker-desktop

3. インストール時に「WSL2 backend」を選択

### インストール後の確認

```powershell
# PowerShell またはコマンドプロンプトで
docker --version
docker-compose --version

# 動作確認
docker run hello-world
```

---

## Ubuntu / Linux

```bash
# Docker インストール
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# ユーザーを docker グループに追加（再起動が必要）
sudo usermod -aG docker $USER

# サービス起動
sudo systemctl start docker
sudo systemctl enable docker

# 動作確認
docker --version
docker-compose --version
docker run hello-world
```

---

## プロジェクトの起動

```bash
# リポジトリをクローン
git clone https://github.com/Milix-M/stock-ai-agent.git
cd stock-ai-agent

# 環境変数をコピー
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Docker Compose で起動
docker-compose up --build

# バックグラウンドで起動する場合
docker-compose up -d

# 停止
docker-compose down

# 完全削除（データベースデータも削除）
docker-compose down -v
```

---

## 起動後のアクセス

| サービス | URL |
|---|---|
| フロントエンド | http://localhost:5173 |
| バックエンドAPI | http://localhost:8000 |
| APIドキュメント | http://localhost:8000/docs |
| データベース | localhost:5432 |
| Redis | localhost:6379 |

---

## トラブルシューティング

### ポートが既に使用されている

```bash
# 使用中のポートを確認
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :8000  # Backend
lsof -i :5173  # Frontend

# プロセスを停止
kill -9 <PID>
```

### Docker Compose が見つからない

```bash
# docker-compose プラグインとしてインストール
docker compose up --build

# または旧式のコマンドを使用
docker-compose up --build
```

### メモリ不足（macOS/Windows）

Docker Desktop の設定でメモリを増やす:
- Settings → Resources → Memory: 4GB 以上推奨

### コンテナが起動しない

```bash
# ログを確認
docker-compose logs backend
docker-compose logs db
docker-compose logs frontend

# 完全にリセット
docker-compose down -v
docker-compose up --build
```
