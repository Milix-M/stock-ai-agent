#!/bin/bash
set -e

# DBの準備完了待ち
echo "Waiting for database..."
while ! PGPASSWORD=postgres psql -h db -U postgres -d stock_ai -c '\q'; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL is up"

# マイグレーション実行（失敗時はstampでリカバリ）
echo "Running migrations..."
if ! alembic upgrade head 2>&1; then
  echo "Migration failed, attempting to stamp and retry..."
  CURRENT=$(alembic current 2>&1 | grep -oP '^\s*\(\K[0-9]+')
  if [ -z "$CURRENT" ]; then
    CURRENT=0
  fi
  echo "Current version: $CURRENT"
  
  # 各バージョンを順にstamp
  for v in 001 002 003 004; do
    if [ "$v" -gt "$CURRENT" ]; then
      echo "Stamping version $v..."
      alembic stamp $v 2>/dev/null || true
    fi
  done
  
  echo "Retrying migrations..."
  alembic upgrade head
fi

# メインプロセス起動
echo "Starting application..."
exec "$@"
