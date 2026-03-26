#!/bin/bash
set -e

# DBの準備完了待ち
echo "Waiting for database..."
while ! PGPASSWORD=postgres psql -h db -U postgres -d stock_ai -c '\q'; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL is up"

# Alembicバージョンを確認
alembic current

# マイグレーション実行
echo "Running migrations..."
alembic upgrade head

# メインプロセス起動
echo "Starting application..."
exec "$@"
