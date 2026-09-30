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
echo "全部分类 README 生成完毕"

# ---------- 父品牌 README ----------
# 规则（docs/references/brand-naming-contract.md §Parent README Policy）：
# 任何拥有 ≥1 个 child brand（parent_brand 指向它）的物理品牌节点，
# 必须在其 icon 目录拥有 README.md（生态根 + 中间父品牌 + 更深层父品牌）。
# 叶子品牌不强制。数据全部来自 brands.json + 动态关系解析（不在 README 里
# 手工维护计数）。带 marker 的生成文件可重复生成；无 marker 的视为人工文档，
# 不覆盖（§36）。
python3 <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('scripts').resolve()))
from brand_relationships import (PARENT_README_MARKER, expected_parent_readme,
                                 physical_parent_nodes)

brands_doc = json.loads(Path('config/brands.json').read_text(encoding='utf-8'))
ssot = {b['id']: b for b in brands_doc.get('brands', [])}
parents = physical_parent_nodes(brands_doc)

created, skipped_manual, kept = 0, 0, 0
for bid in sorted(parents):
    d = Path(ssot[bid]['icon_path']).parent
    rd = d / 'README.md'
    content = expected_parent_readme(bid, ssot)
    if rd.exists():
        first = rd.read_text(encoding='utf-8').splitlines()[0] if rd.read_text(encoding='utf-8') else ''
        if first.strip() == PARENT_README_MARKER:
            rd.write_text(content, encoding='utf-8')
            kept += 1
            print('  ↻ %s/README.md（重新生成）' % d)
        else:
            skipped_manual += 1
            print('  ⚠ %s/README.md 已存在（人工文档，不覆盖）' % d)
    else:
        rd.write_text(content, encoding='utf-8')
        created += 1
        print('  ✓ %s/README.md（新建）' % d)
print('')
print('父品牌 README: 新建 %d / 重新生成 %d / 保留人工 %d（共 %d 个父节点）'
      % (created, kept, skipped_manual, created + kept + skipped_manual))
PY
