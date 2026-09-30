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
from pathlib import Path

ICONS = Path('icons')
MARKER = '<!-- generated: parent-brand-readme (scripts/generate-parent-readmes.py) -->'
brands_doc = json.loads(Path('config/brands.json').read_text(encoding='utf-8'))
brands = brands_doc.get('brands', [])
ssot = {b['id']: b for b in brands}

children = {}
for b in brands:
    p = b.get('parent_brand')
    if p:
        children.setdefault(p, []).append(b['id'])

def ancestors(bid):
    """沿 parent_brand 向上（含直接父），断在白名单外/环。"""
    out, seen, cur = [], {bid}, ssot.get(bid, {}).get('parent_brand')
    while cur:
        if cur in seen:
            break
        out.append(cur)
        seen.add(cur)
        cur = ssot.get(cur, {}).get('parent_brand')
    return out

def root_of(bid):
    a = ancestors(bid)
    return a[-1] if a else None

created, skipped_manual, kept = 0, 0, 0
for bid, kids in sorted(children.items()):
    if bid not in ssot:
        continue  # 白名单母公司：无物理目录，不适用目录级 README
    d = Path(ssot[bid]['icon_path']).parent
    rd = d / 'README.md'
    dn = ssot[bid]['display_name']
    parent = ssot[bid].get('parent_brand')
    root = root_of(bid)
    role = 'Ecosystem Root' if ssot[bid].get('entity_type') == 'ecosystem' else 'Intermediate Parent Brand'
    if root is None:
        root = bid if role == 'Ecosystem Root' else None
    lines = [
        MARKER,
        '',
        '# %s / %s 生态中的%s' % (dn, root or dn, '根品牌' if role == 'Ecosystem Root' else '父品牌'),
        '',
        '```text',
        'Brand:        %s' % bid,
        'Display Name: %s' % dn,
        'Role:         %s' % role,
        'Parent:       %s' % (parent or '—'),
    ]
    chain = [bid] + ancestors(bid)
    lines.append('Ancestor Chain: %s' % ' → '.join(chain))
    lines.extend(['Direct Children: %d' % len(kids), 'Ecosystem Root: %s' % (root or '—'), '```', '',
                  '| Child | Display Name |', '|:---|:---|'])
    for k in sorted(kids):
        lines.append('| `%s` | %s |' % (k, ssot[k]['display_name']))
    lines.append('')
    content = '\n'.join(lines)
    if rd.exists():
        first = rd.read_text(encoding='utf-8').splitlines()[0] if rd.read_text(encoding='utf-8') else ''
        if first.strip() == MARKER:
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
