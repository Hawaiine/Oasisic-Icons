#!/usr/bin/env bash
# rename-icons.sh — 旧结构/旧命名修复工具（幂等）
#
# 目标结构：icons/<分类>/<品牌名>/<品牌名>.png + <品牌名>01.png + <品牌名>02.png ...
#
# 本脚本修复以下历史遗留问题：
#   1. 分类根目录下的扁平文件 → 移入品牌文件夹
#        icons/Media/Netflix.png        → icons/Media/Netflix/Netflix.png
#        icons/Media/Netflix-2.png      → icons/Media/Netflix/Netflix02.png
#   2. 品牌文件夹内使用连字符的变体 → 两位零填充
#        icons/Media/Netflix/Netflix-1.png   → Netflix/Netflix01.png
#   3. 变体数字未零填充            → 补零
#        Netflix/Netflix1.png         → Netflix/Netflix01.png
#   4. 品牌名中的 `+`  → `Plus`（Disney+ → Disney-Plus）
#   5. `_N`（Qure 上游格式）        → 两位零填充
#
# 只做重命名，绝不改动任何 PNG 的像素内容；不删除文件；不做默认版本的“内容选择”
# （默认图标内容的选择属于人工决策，脚本仅在缺失 Brand.png 时报告）。
#
# 用法：bash scripts/rename-icons.sh [--dry-run]
set -euo pipefail

cd "$(dirname "$0")/.."

ICONS_DIR="icons"
DRY="${1:-}"
CHANGED=0

pad2() { printf '%02d' "$1"; }

say() {
  if [ -n "$DRY" ]; then
    echo "  [dry-run] $*"
  else
    echo "  ✓ $*"
  fi
}

move() {
  local src="$1" dst="$2"
  if [ "$src" = "$dst" ]; then return 0; fi
  local dst_dir
  dst_dir=$(dirname "$dst")
  if [ -e "$dst" ]; then
    echo "  ✗ 目标已存在，跳过: $dst"
    return 0
  fi
  if [ -n "$DRY" ]; then
    echo "  [dry-run] $src → $dst"
  else
    mkdir -p "$dst_dir"
    mv "$src" "$dst"
    echo "  ✓ $src → $dst"
  fi
  CHANGED=$((CHANGED + 1))
}

# `+` → `Plus`
normalize_brand() {
  local b="$1"
  b="${b//+/Plus}"
  printf '%s' "$b"
}

echo "=========================================="
echo " Oasisic-Icons 结构/命名修复"
[ -n "$DRY" ] && echo " 模式: 干跑 (dry-run)"
echo "=========================================="

for cat_dir in "$ICONS_DIR"/*/; do
  [ -d "$cat_dir" ] || continue
  cat_name=$(basename "$cat_dir")

  # ---- 1. 分类根目录下的扁平文件 ----
  for f in "$cat_dir"*.png; do
    [ -f "$f" ] || continue
    stem=$(basename "$f" .png)
    if [[ "$stem" =~ ^(.+)[-_]([0-9]+)$ ]]; then
      brand=$(normalize_brand "${BASH_REMATCH[1]}")
      num="${BASH_REMATCH[2]}"
      move "$f" "$cat_dir$brand/$brand$(pad2 "$num").png"
    else
      brand=$(normalize_brand "$stem")
      move "$f" "$cat_dir$brand/$brand.png"
    fi
  done

  # ---- 2/3/4. 品牌文件夹内部 ----
  for brand_dir in "$cat_dir"*/; do
    [ -d "$brand_dir" ] || continue
    raw_brand=$(basename "$brand_dir")
    brand=$(normalize_brand "$raw_brand")

    # 4. 目录名含 `+` → 重命名目录
    if [ "$raw_brand" != "$brand" ]; then
      move "$brand_dir" "$cat_dir$brand/"
      brand_dir="$cat_dir$brand/"
    fi

    for f in "$brand_dir"*.png; do
      [ -f "$f" ] || continue
      stem=$(basename "$f" .png)

      if [ "$stem" = "$brand" ]; then
        continue                       # 默认图标，正确
      fi
      if [[ "$stem" =~ ^"$brand"[0-9]{2}$ ]]; then
        continue                       # 两位零填充变体，正确
      fi
      if [[ "$stem" =~ ^"$brand"[-_]([0-9]+)$ ]]; then
        move "$f" "$brand_dir$brand$(pad2 "${BASH_REMATCH[1]}").png"
        continue
      fi
      if [[ "$stem" =~ ^"$brand"([0-9])$ ]]; then
        move "$f" "$brand_dir$brand$(pad2 "${BASH_REMATCH[1]}").png"
        continue
      fi
      echo "  ! 未知命名（需人工确认，未改动）: $f"
    done

    # 默认图标缺失提示（不自动选择内容）
    if ! compgen -G "$brand_dir$brand.png" > /dev/null; then
      echo "  ! 缺少默认图标: $brand_dir$brand.png"
    fi
  done
done

echo ""
if [ "$CHANGED" -eq 0 ]; then
  echo "无需修复：结构已符合规范。"
else
  echo "$( [ -n "$DRY" ] && echo '干跑完成，' || echo '完成，' )共 $CHANGED 处变更。"
fi