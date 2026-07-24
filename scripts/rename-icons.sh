#!/usr/bin/env bash
# rename-icons.sh — 统一图标命名规范
# 规则：
#   1. (N) → -N          ChatGPT(1).png → ChatGPT-1.png
#   2. _N → -N           Cryptocurrency_1.png → Cryptocurrency-1.png (Qure 上游格式)
#   3. + → -Plus         CatchPlay+(1).png → CatchPlay-Plus-1.png, discovery+.png → Discovery-Plus.png
#   4. SURGE → Surge      SURGE(8).png → Surge-8.png
#   5. Hongkong → HongKong（统一大小写）
#   6. BiliBili → Bilibili（统一大小写）
#   7. NeteaseMusic → NetEaseMusic（统一大小写）
#   8. Duolingguo → Duolingo（拼写修正）
# 用法：bash rename-icons.sh [--dry-run]
set -euo pipefail

cd "$(dirname "$0")/.."

ICONS_DIR="icons"
DRY_RUN="${1:-}"

rename_file() {
  local src="$1"
  local dir
  dir=$(dirname "$src")
  local base
  base=$(basename "$src")
  local new="$base"

  # SURGE → Surge（先处理括号/无括号两种）
  new=$(echo "$new" | sed -E 's/^SURGE\(([0-9]+)\)\.png$/Surge-\1.png/')
  new=$(echo "$new" | sed -E 's/^SURGE\.png$/Surge.png/')

  # + → Plus
  new=$(echo "$new" | sed 's/+/-Plus/g')

  # (N) → -N
  new=$(echo "$new" | sed -E 's/\(([0-9]+)\)/-\1/g')

  # _N → -N（Qure 上游格式）
  new=$(echo "$new" | sed -E 's/_([0-9]+)\.png$/-\1.png/')

  # 拼写/大小写修正
  new=$(echo "$new" | sed -E 's/^discovery/Discovery/')
  new=$(echo "$new" | sed -E 's/^Duolingguo-/Duolingo-/')
  new=$(echo "$new" | sed -E 's/^Duolingguo\./Duolingo./')
  new=$(echo "$new" | sed -E 's/^Hongkong-/HongKong-/')
  new=$(echo "$new" | sed -E 's/^Hongkong\./HongKong./')
  new=$(echo "$new" | sed -E 's/^BiliBili-/Bilibili-/')
  new=$(echo "$new" | sed -E 's/^BiliBili\./Bilibili./')
  new=$(echo "$new" | sed -E 's/^NeteaseMusic-/NetEaseMusic-/')
  new=$(echo "$new" | sed -E 's/^NeteaseMusic\./NetEaseMusic./')
  new=$(echo "$new" | sed -E 's/^Apple_News\./AppleNews./')

  if [ "$base" != "$new" ]; then
    if [ -n "$DRY_RUN" ]; then
      echo "  ${src} → ${dir}/${new}"
    else
      mv "$src" "${dir}/${new}"
      echo "  ✓ ${base} → ${new}"
    fi
  fi
}

echo "=========================================="
echo " Oasisic-Icons 图标重命名"
[ -n "$DRY_RUN" ] && echo " 模式: 干跑 (dry-run)"
echo "=========================================="

for dir in "$ICONS_DIR"/*/; do
  [ -d "$dir" ] || continue
  for f in "$dir"*.png; do
    [ -f "$f" ] || continue
    rename_file "$f"
  done
done

[ -n "$DRY_RUN" ] && echo "" && echo "干跑完成，以上为即将变更的文件。"
