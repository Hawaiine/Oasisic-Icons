#!/usr/bin/env bash
# rename-icons.sh — 统一图标命名规范
# 规则：
#   1. (N) → -N        ChatGPT(1).png → ChatGPT-1.png
#   2. + → Plus         CatchPlay+(1).png → CatchPlayPlus-1.png, discovery+.png → DiscoveryPlus.png
#   3. SURGE → Surge    SURGE(8).png → Surge-8.png
#   4. 首字母大写       discovery+ → DiscoveryPlus
# 用法：bash rename-icons.sh [--dry-run]
set -euo pipefail

cd "$(dirname "$0")"
DRY_RUN="${1:-}"
RENAMES=()

rename_file() {
  local src="$1"
  local dir
  dir=$(dirname "$src")
  local base
  base=$(basename "$src")
  local new="$base"

  # 规则: SURGE → Surge（首字母大写，其余小写）
  # 但先处理特殊 case: SURGE(8).png → Surge-8.png
  new=$(echo "$new" | sed -E 's/^SURGE\(([0-9]+)\)\.png$/Surge-\1.png/')
  new=$(echo "$new" | sed -E 's/^SURGE\.png$/Surge.png/')

  # 规则: + → Plus（但保留扩展名）
  new=$(echo "$new" | sed 's/+/-Plus/g')

  # 规则: (N) → -N
  new=$(echo "$new" | sed -E 's/\(([0-9]+)\)/-\1/g')

  # 规则: 下划线 → 下划线（保留，Qure 来的图标用下划线）
  # 规则: 首字母大写（仅对 discovery+ 这类全小写的处理）
  new=$(echo "$new" | sed -E 's/^discovery/Discovery/')

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
if [ -n "$DRY_RUN" ]; then
  echo " 模式: 干跑 (dry-run)"
fi
echo "=========================================="

for dir in AI Apple Country Crypto DevOps Drive Education Finance Game General Google Health Media Microsoft Music News Payment Proxy Shopping Social Surge Telecom Tool; do
  for f in "$dir"/*.png; do
    [ -f "$f" ] || continue
    rename_file "$f"
  done
done

if [ -n "$DRY_RUN" ]; then
  echo ""
  echo "干跑完成，以上为即将变更的文件。执行 bash rename-icons.sh 实际重命名。"
fi