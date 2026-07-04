#!/usr/bin/env bash
# generate-icon-json.sh — 自动生成 Oasisic-Icons/surge-icon.json
set -euo pipefail

BASE_URL="https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main"
OUTPUT="surge-icon.json"

echo '{'
echo '  "name": "Oasisic-Icons",'
echo '  "description": "Cross-platform Proxy Policy Group Icons / 跨平台代理策略组图标合集",'
echo '  "icons": ['

first=true
for dir in AI Apple Country Crypto DevOps Drive Education Finance Game General Google Health Media Microsoft Music News Payment Proxy Shopping Social Surge Telecom Tool; do
  for icon in "$dir"/*.png; do
    [ -f "$icon" ] || continue
    name=$(basename "$icon" .png)
    name=$(echo "$name" | sed 's/["\\]/\\&/g')
    [ "$first" = true ] && first=false || echo ','
    echo -n "    {\"name\": \"$name\", \"category\": \"$dir\", \"url\": \"$BASE_URL/$dir/$(basename "$icon" | sed 's/"/\\"/g')\"}"
  done
done

echo ''
echo '  ]'
echo '}'