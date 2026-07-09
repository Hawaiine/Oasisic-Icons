#!/usr/bin/env bash
# sync-upstream.sh — 自动同步上游图标到 Oasisic-Icons
# 读取 config/icon-mapping.json，从上游仓库下载图标到对应分类目录
set -euo pipefail

# 切换到仓库根目录（scripts/ 的父目录）
cd "$(dirname "$0")/.."

MAPPING="config/icon-mapping.json"
ICONS_DIR="icons"
UPDATED=0
SKIPPED=0
FAILED=0

# 检查依赖
for cmd in curl python3; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "❌ 缺少依赖: $cmd"
    exit 1
  fi
done

CURL_OPTS=(-sL --retry 3 --retry-delay 5 --retry-all-errors)

echo "=========================================="
echo " Oasisic-Icons 上游同步开始"
echo " 时间: $(TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# 读取 mappings 并逐条处理
while IFS='|' read -r upstream filename target base_url; do
  dir="$ICONS_DIR/$(dirname "$target")"
  mkdir -p "$dir"

  src_url="$base_url/$filename"
  dest="$dir/$(basename "$target")"

  if [ -f "$dest" ]; then
    local_size=$(stat --printf='%s' "$dest" 2>/dev/null || echo 0)
    remote_size=$(curl -sI --retry 2 --retry-delay 5 "$src_url" 2>/dev/null | grep -i 'content-length' | awk '{print $2}' | tr -d '\r' || echo 0)
    if [ "$local_size" = "$remote_size" ] && [ "$remote_size" -gt 0 ]; then
      echo "  ⏭️  $target — 已是最新"
      SKIPPED=$((SKIPPED + 1))
      continue
    fi
  fi

  echo "  ↓ 下载: $upstream/$filename → $dest"
  if curl "${CURL_OPTS[@]}" -o "$dest" "$src_url"; then
    actual_size=$(stat --printf='%s' "$dest" 2>/dev/null || echo 0)
    if [ "$actual_size" -gt 0 ]; then
      echo "    ✓ $dest ($actual_size bytes)"
      UPDATED=$((UPDATED + 1))
    else
      echo "    ✗ $dest — 文件为空"
      rm -f "$dest"
      FAILED=$((FAILED + 1))
    fi
  else
    echo "    ✗ 下载失败"
    FAILED=$((FAILED + 1))
  fi

  # 避免 GitHub 限流，每请求间隔 300ms
  sleep 0.3
done < <(python3 -c "
import json
with open('$MAPPING') as f:
    data = json.load(f)
for m in data['mappings']:
    parts = m['source'].split('/', 1)
    upstream = parts[0]
    filename = parts[1]
    if data['upstreams'].get(upstream, {}).get('enabled', False):
        base = data['upstreams'][upstream]['base_url']
        print(f'{upstream}|{filename}|{m[\"target\"]}|{base}')
")

echo ""
echo "=========================================="
echo " 同步完成"
echo " 更新: $UPDATED  跳过: $SKIPPED  失败: $FAILED"
echo "=========================================="

# 如果有更新，自动生成 JSON
if [ "$UPDATED" -gt 0 ]; then
  echo ""
  echo "→ 重新生成 surge-icon.json..."
  bash scripts/generate-icon-json.sh
  echo "→ 重新生成完毕"
fi
