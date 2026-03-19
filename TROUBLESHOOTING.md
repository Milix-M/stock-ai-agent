# 登録時のNetwork Error - トラブルシューティングガイド

## 問題の概要

手元（Linuxサーバー）では正常に動いているが、れおさんの環境では「Network Error」が続いている。

## すでに試した解決策

1. ✅ リフレッシュトークンAPIの修正（JSONボディ形式）
2. ✅ CORSエラーの修正（Vite proxy設定）
3. ✅ DBスキーマの更新（`stock_code`カラム追加）
4. ✅ Dockerネットワーク内のDNS解決（`extra_hosts`追加）
5. ✅ Vite proxy設定の改善（Hostヘッダー転送）

## 手元での検証結果

```bash
curl -s -X POST http://localhost:5173/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test-final@example.com","password":"TestPass123!","display_name":"ほむら"}'

# 結果: {"access_token":"...","refresh_token":"...","token_type":"bearer"}  ✅ 成功
```

## れおさんの環境で想定されるエラー

1. `net::ERR_NAME_NOT_RESOLVED` - `backend`というホスト名が解決できない
2. `net::ERR_EMPTY_RESPONSE` - サーバーからの応答が空

## WSL2環境の推奨設定

### 1. WSL2のネットワーク設定

**WSL2でDocker Desktopを使用している場合：**
- Docker Desktopの「Resources」→「WSL Integration」を有効にする
- ファイアウォールでWSL2へのアクセスを許可する

**WSL2で直接Dockerを使用している場合：**
- WSL2のhostsファイルに`127.0.0.1 backend`を追加する

### 2. ブラウザから直接バックエンドにアクセスしない

Viteのproxy設定を使用しているため、フロントエンドは`http://localhost:5173/api/v1/*`でリクエストを送り、Viteが自動的にバックエンドに転送する。

### 3. ポート転送の確認

以下のポートが開いているか確認する：

```bash
# WSL2ターミナルから
netstat -an | grep -E ":(5173|8000)"
```

### 4. localhostと127.0.0.1の違い

Windowsでは`localhost`と`127.0.0.1`は同じだが、WSL2では異なる：

- `localhost` → Windowsのネットワークスタック（WinInetなど）
- `127.0.0.1` → WSL2内部のLinuxスタック

フロントエンドが`http://localhost:5173`にアクセスしている場合、Viteが`localhost`を解決してWindows側にルーティングしてしまい、Dockerコンテナ内のバックエンドに到達できない可能性がある。

### 5. 解決策A: WSL2のhostsファイルを更新

```bash
# WSL2ターミナルで実行
sudo bash -c 'echo "127.0.0.1 backend" >> /etc/hosts'
```

### 6. 解決策B: docker-compose.ymlを変更してWindowsポートに公開

れおさんがDocker Desktopを使用している場合、フロントエンドとバックエンドのポートをWindowsホストに公開する：

```yaml
# docker-compose.yml（バックエンドのみ変更）
backend:
  ports:
    - "8000:8000"  # 追加: Windowsホストに公開
```

### 7. 解決策C: Docker Desktopのネットワーク設定を確認

Docker Desktopを使用している場合：

1. Docker Desktopを開く
2. 「Settings」→「Resources」
3. 「WSL Integration」が有効になっているか確認
4. 必要なら、有効にしてDocker Desktopを再起動

### 8. 解決策D: PowerShellでDNSキャッシュをクリア

```powershell
# PowerShell（管理者）で実行
Clear-DnsClientCache
ipconfig /flushdns
```

## 確認ステップ

1. ブラウザを完全に更新する（Ctrl+F5またはCmd+Shift+R）
2. 別のメールアドレスで登録を試みる
3. ブラウザの開発者ツール（F12）を開いて以下を確認する：
   - Networkタブ：どのURLにリクエストが失敗しているか
   - Consoleタブ：具体的なエラーメッセージ
4. 問題が続く場合、以下の情報を教えてほしい：
   - どのブラウザを使用しているか
   - WSL2またはDocker Desktopを使用しているか
   - ブラウザから`http://localhost:8000/api/v1/auth/register`に直接アクセスできるか

## 追加の確認

```bash
# Dockerコンテナ間の通信を確認
cd /home/ubuntu/.openclaw/workspace/stock-ai-agent
docker exec frontend ping -c 2 backend
```

このコマンドが成功すれば、コンテナ間の通信は正常だ。
