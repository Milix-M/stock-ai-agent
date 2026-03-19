#!/bin/bash
# Dockerコンテナ内の/etc/hostsを更新して、backendサービス名を解決可能にする

# frontendコンテナ内でbackendサービス名を解決できるようにする
# 127.0.0.1 に backend ホスト名を割り当てる

sudo docker compose exec frontend sh -c 'echo "127.0.0.1 backend" >> /etc/hosts'

echo "frontendコンテナの/etc/hostsを更新しました"
echo "これでhttp://backend:8000のURL解決が可能になります"
