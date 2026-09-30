#!/usr/bin/env bash
# generate-category-readmes.sh — 生成分类 README 与父品牌 README（全部由 SSOT + 关系解析器派生）
#
# 物理模型（2026-10-01 定稿）：
#   icons/<category>/<id>/<id>.png                     一级 direct child
#   icons/<category>/<中间父>/<id>/<id>.png            同类中间父品牌下的深层子品牌
# 因此本生成器**不得**再按「一级子目录 = 品牌」遍历文件系统（深层品牌会被漏掉、
# 中间目录会被误当成品牌）；所有数据一律来自 config/brands.json + expected_icon_path()。
set -euo pipefail

cd "$(dirname "$0")/.."

python3 <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('scripts').resolve()))
from brand_relationships import (  # noqa: E402
    PARENT_README_MARKER,
    ecosystem_category_ids,
    expected_ecosystem_readme_block,
    expected_icon_path,
    expected_parent_readme,
    physical_parent_nodes,
)

brands_doc = json.loads(Path('config/brands.json').read_text(encoding='utf-8'))
ssot = {b['id']: b for b in brands_doc.get('brands', [])}
aliases = set(brands_doc.get('parent_brands_without_icon', []))
cats_doc = json.loads(Path('config/categories.json').read_text(encoding='utf-8'))
cats = cats_doc['categories']
eco_cat_ids = ecosystem_category_ids(cats)

ICONS = Path('icons')
cat_dirs = sorted(p.name for p in ICONS.iterdir() if p.is_dir())

# ---------- 分类 README ----------
for cid in cat_dirs:
    c = next((x for x in cats if x['id'] == cid), None)
    name = '%s %s' % (c['emoji'], c['display_name']) if c else cid
    desc = c['description'] if c else cid
    members = sorted(bid for bid, e in ssot.items() if e.get('category') == cid)
    total = 0
    rows = []
    for bid in members:
        d = Path(ssot[bid]['icon_path']).parent
        files = sorted(p.name for p in d.glob('*.png')) if d.is_dir() else []
        total += len(files)
        rows.append('| `%s` | `%s` |' % (bid, ' '.join(files)))
    lines = [
        '# %s / %s' % (name, desc),
        '',
        '> 共 **%d** 个图标，**%d** 个品牌' % (total, len(members)),
        '',
        '| 品牌 | 图标文件 |',
        '|:---|:---|',
    ] + rows + ['']
    # 生态分类 README 额外输出真实关系树（§16/§48：不得把孙代品牌平铺成一级子品牌）
    if cid in eco_cat_ids:
        lines.append(expected_ecosystem_readme_block(cid, ssot))
    (ICONS / cid / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    print('  ✓ icons/%s/README.md (%d icons, %d brands)' % (cid, total, len(members)))

print('')
print('全部分类 README 生成完毕')

# ---------- 父品牌 README ----------
# 规则（docs/references/brand-naming-contract.md §Parent README Policy）：
# 任何拥有 ≥1 个 child brand（parent_brand 指向它）的物理品牌节点，必须在其
# icon 目录拥有 README.md（生态根 + 中间父品牌 + 更深层父品牌）。叶子品牌不强制。
# 带 marker 的生成文件可重复生成；无 marker 的视为人工文档，不覆盖（§36）。
parents = physical_parent_nodes(brands_doc)
created, skipped_manual, kept = 0, 0, 0
for bid in sorted(parents):
    d = Path(ssot[bid]['icon_path']).parent
    rd = d / 'README.md'
    content = expected_parent_readme(bid, ssot, aliases, eco_cat_ids)
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
