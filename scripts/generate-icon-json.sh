#!/usr/bin/env bash
# generate-icon-json.sh — 自动生成 Oasisic-Icons/surge-icon.json
set -euo pipefail

# 切换到仓库根目录（scripts/ 的父目录）
cd "$(dirname "$0")/.."

BASE_URL="https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main"
ICONS_DIR="icons"
OUTPUT="config/surge-icon.json"

{
  echo '{'
  echo '  "name": "Oasisic-Icons",'
  echo '  "description": "Cross-platform Proxy Policy Group Icons / 跨平台代理策略组图标合集",'
  echo '  "icons": ['

  first=true
  for dir in "$ICONS_DIR"/*/; do
    [ -d "$dir" ] || continue
    category=$(basename "$dir")
    for icon in "$dir"*.png; do
      [ -f "$icon" ] || continue
      name=$(basename "$icon" .png)
      name=$(echo "$name" | sed 's/["\]/\\&/g')
      [ "$first" = true ] && first=false || echo ','
      echo -n "    {\"name\": \"$name\", \"category\": \"$category\", \"url\": \"$BASE_URL/$ICONS_DIR/$category/$(basename "$icon" | sed 's/"/\\"/g')\"}"
    done
  done

  echo ''
  echo '  ]'
  echo '}'
} > "$OUTPUT"

echo "✓ 已生成 $OUTPUT ($(grep -c '"category"' "$OUTPUT") 个图标)"
