#!/usr/bin/env bash
# generate-category-readmes.sh — 生成分类 README 与父品牌 README（SSOT + resolver）
set -euo pipefail
cd "$(dirname "$0")/.."

python3 <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from brand_relationships import (
    PARENT_README_MARKER, ecosystem_category_ids, expected_ecosystem_readme_block,
    expected_parent_readme, physical_parent_nodes,
)
from json_io import read_json_or_exit  # JSON 读取唯一入口（统一诊断）

brands_doc = read_json_or_exit('config/brands.json', 'brands.json (品牌 SSOT)')
ssot = {b['id']: b for b in brands_doc.get('brands', [])}
aliases = set(brands_doc.get('parent_brands_without_icon', []))
cats = read_json_or_exit('config/categories.json', 'categories.json (分类 SSOT)')['categories']
eco_cat_ids = ecosystem_category_ids(cats)
ICONS = Path('icons')
cat_dirs = sorted(p.name for p in ICONS.iterdir() if p.is_dir())

for cid in cat_dirs:
    c = next((x for x in cats if x['id'] == cid), None)
    name = '%s %s' % (c['emoji'], c['display_name']) if c else cid
    desc = c['description'] if c else cid
    members = sorted(bid for bid, e in ssot.items() if e.get('category') == cid)
    total = 0
    rows = []
    for bid in members:
        icon_path = ssot[bid].get('icon_path')
        d = Path(icon_path).parent if icon_path else None
        files = sorted(p.name for p in d.glob('*.png')) if d and d.is_dir() else []
        total += len(files)
        rows.append('| `%s` | `%s` |' % (bid, ' '.join(files)))
    lines = [
        '# %s / %s' % (name, desc), '',
        '> 共 **%d** 个图标，**%d** 个品牌' % (total, len(members)), '',
        '| 品牌 | 图标文件 |', '|:---|:---|',
    ] + rows + ['']
    if cid in eco_cat_ids:
        lines.append(expected_ecosystem_readme_block(cid, ssot))
    (ICONS / cid / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    print('  ✓ icons/%s/README.md (%d icons, %d brands)' % (cid, total, len(members)))

parents = physical_parent_nodes(brands_doc)
created = kept = skipped = 0
for bid in sorted(parents):
    e = ssot.get(bid)
    if not e or not e.get('icon_path'):
        # A pending ecosystem remains a semantic root but has no physical parent README.
        continue
    d = Path(e['icon_path']).parent
    rd = d / 'README.md'
    content = expected_parent_readme(bid, ssot, aliases, eco_cat_ids)
    if rd.exists():
        first = rd.read_text(encoding='utf-8').splitlines()[0] if rd.read_text(encoding='utf-8') else ''
        if first.strip() == PARENT_README_MARKER:
            rd.write_text(content, encoding='utf-8'); kept += 1
        else:
            skipped += 1
    else:
        rd.write_text(content, encoding='utf-8'); created += 1
print('父品牌 README: 新建 %d / 重新生成 %d / 保留人工 %d' % (created, kept, skipped))
PY
