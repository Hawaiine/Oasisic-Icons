#!/usr/bin/env bash
# generate-category-readmes.sh — 为每个分类自动生成 README 清单
# 新结构：icons/<分类>/<品牌>/<品牌>.png + <品牌>01.png...
# 分类定义（emoji/显示名/描述）来自 config/categories.json（SSOT），不再硬编码。
set -euo pipefail

cd "$(dirname "$0")/.."
ICONS_DIR="icons"

generate_readme() {
  local dir="$1"
  local name="$2"
  local desc="$3"

  local total=0
  local brands=()

  # 新结构：每个品牌是一个子目录
  for brand_dir in "$dir"/*/; do
    [ -d "$brand_dir" ] || continue
    brand=$(basename "$brand_dir")
    # 统计该品牌下所有 .png 文件
    for f in "$brand_dir"*.png; do
      [ -f "$f" ] || continue
      total=$((total + 1))
    done
    brands+=("$brand")
  done

  cat > "$dir/README.md" << README_EOF
# ${name} / ${desc}

> 共 **${total}** 个图标，**${#brands[@]}** 个品牌

| 品牌 | 图标文件 |
|:---|:---|
README_EOF

  for brand in $(printf '%s\n' "${brands[@]}" | sort); do
    brand_dir="$dir/$brand"
    files=$(ls "$brand_dir"/*.png 2>/dev/null | xargs -I{} basename {} | sort | tr '\n' ' ' | sed 's/ $//')
    echo "| \`${brand}\` | \`${files}\` |" >> "$dir/README.md"
  done

  echo "  ✓ $dir ($total icons, ${#brands[@]} brands)"
}

# 分类元数据来自 SSOT：config/categories.json
while IFS=$'\t' read -r category name desc; do
  generate_readme "$ICONS_DIR/$category" "$name" "$desc"
done < <(python3 - "$ICONS_DIR" <<'PY'
import json, os, sys
icons_dir = sys.argv[1]
cats = {c["id"]: c for c in json.load(open("config/categories.json"))["categories"]}
for entry in sorted(os.scandir(icons_dir), key=lambda e: e.name):
    if not entry.is_dir():
        continue
    c = cats.get(entry.name)
    if c:
        print(f'{entry.name}\t{c["emoji"]} {c["display_name"]}\t{c["description"]}')
    else:
        print(f'{entry.name}\t{entry.name}\t{entry.name}')
PY
)

echo ""
echo "全部 README 生成完毕"
