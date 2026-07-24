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

# === PNG 校验函数 ===
# 参数: 文件路径
# 返回: 0=合法PNG, 1=非法
validate_png() {
  local f="$1"
  # 最小尺寸（至少包含 PNG 头 + IHDR）
  local sz
  sz=$(stat --printf='%s' "$f" 2>/dev/null || echo 0)
  [ "$sz" -ge 50 ] || return 1
  # PNG 魔数: \x89PNG\r\n\x1a\n
  local magic
  magic=$(od -A n -t x1 -N 8 "$f" 2>/dev/null | tr -d ' \n')
  [ "$magic" = "89504e470d0a1a0a" ] || return 1
  return 0
}

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

  # 本地已存在，先校验 PNG 合法性
  if [ -f "$dest" ]; then
    if validate_png "$dest"; then
      # 合法 PNG：做 size 对比跳过
      local_size=$(stat --printf='%s' "$dest" 2>/dev/null || echo 0)
      remote_size=$(curl -sI --retry 2 --retry-delay 5 "$src_url" 2>/dev/null | grep -i 'content-length' | awk '{print $2}' | tr -d '\r' || echo 0)
      if [ "$remote_size" -gt 0 ] && [ "$local_size" -ne "$remote_size" ]; then
        diff_note=""
        [ "$local_size" -gt "$remote_size" ] && diff_note="（较大，可能已升级）" || diff_note="（较小，可能已替换）"
        echo "  🔒 $target — 本地与上游不一致${diff_note}，跳过"
        SKIPPED=$((SKIPPED + 1))
        continue
      fi
      if [ "$local_size" = "$remote_size" ] && [ "$remote_size" -gt 0 ]; then
        echo "  ⏭️  $target — 已是最新"
        SKIPPED=$((SKIPPED + 1))
        continue
      fi
    else
      # 本地文件非法（404假文件/损坏）→ 删除并重新下载
      echo "  ⚠️  $target — 本地文件损坏（非 PNG 或过小），删除重下"
      rm -f "$dest"
    fi
  fi

  echo "  ↓ 下载: $upstream/$filename → $dest"
  if curl "${CURL_OPTS[@]}" -o "$dest" "$src_url"; then
    # 下载后校验
    if validate_png "$dest"; then
      actual_size=$(stat --printf='%s' "$dest" 2>/dev/null || echo 0)
      echo "    ✓ $dest ($actual_size bytes)"
      UPDATED=$((UPDATED + 1))
    else
      echo "    ✗ $dest — 下载文件非合法 PNG（可能是上游 404）"
      rm -f "$dest"
      FAILED=$((FAILED + 1))
    fi
  else
    echo "    ✗ 下载失败"
    rm -f "$dest"
    FAILED=$((FAILED + 1))
  fi

  # 避免 GitHub 限流，每请求间隔 300ms
  sleep 0.3
done < <(python3 -c "
import json
with open('$MAPPING') as f:
    data = json.load(f)
for m in data['mappings']:
    if m.get('locked', False):
        continue
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