#!/usr/bin/env bash
# generate-icon-json.sh — 生成完整的 surge-icon.json
# Usage: ./generate-icon-json.sh
set -euo pipefail

BASE_URL="https://raw.githubusercontent.com/Hawaiine/PolicyIcons/main"
OUTPUT="surge-icon.json"

echo '{'
echo '  "name": "PolicyIcons",'
echo '  "description": "Cross-platform Proxy Policy Group Icons / 跨平台代理策略组图标合集",'
echo '  "icons": ['

first=true
for dir in AI Apple Country Drive Game General Google Media Microsoft Music Payment Shopping Social Surge Telecom Tool; do
  for icon in "$dir"/*.png; do
    [ -f "$icon" ] || continue
    name=$(basename "$icon" .png)
    # Sanitize name for JSON
    name=$(echo "$name" | sed 's/["\\]/\\&/g')
    [ "$first" = true ] && first=false || echo ','
    echo -n "    {\"name\": \"$name\", \"category\": \"$dir\", \"url\": \"$BASE_URL/$dir/$(basename "$icon" | sed 's/"/\\"/g')\"}"
  done
done

echo ''
echo '  ]'
echo '}'