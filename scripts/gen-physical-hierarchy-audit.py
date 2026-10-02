#!/usr/bin/env python3
"""生成 docs/references/physical-hierarchy-audit.md —— 全库关系 / 物理层级矩阵（§46/§47）。

全部数据由 SSOT + 关系解析器动态派生（§38：不得手工维护计数或名单）；
CI 第 17 组校验本文件与重算结果逐字节一致。
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'scripts'))
from json_io import read_json_or_exit  # noqa: E402

from brand_relationships import (  # noqa: E402
    _ancestor_set_ordered,
    _descendants,
    ecosystem_category_ids,
    expected_icon_path,
    is_canonical_brand,
    physical_parent_nodes,
    resolve_ecosystem_root,
    resolve_graph_root,
)

OUT = REPO / 'docs' / 'references' / 'physical-hierarchy-audit.md'
MARKER = '<!-- generated: physical-hierarchy-audit (scripts/gen-physical-hierarchy-audit.py) -->'


def build(brands_doc, cats_list):
    brands = brands_doc.get('brands', [])
    ssot = {e['id']: e for e in brands if e.get('id')}
    aliases = set(brands_doc.get('parent_brands_without_icon', []))
    eco_cat_ids = ecosystem_category_ids(cats_list)

    multi = sorted(b['id'] for b in brands
                   if b.get('parent_brand') in ssot
                   and ssot[b['parent_brand']].get('parent_brand'))
    cross = sorted(b['id'] for b in brands
                   if b.get('parent_brand') in ssot
                   and ssot[b['parent_brand']].get('category') != b.get('category'))
    no_icon_parent = sorted({b['parent_brand'] for b in brands
                             if b.get('parent_brand') and b['parent_brand'] not in ssot})
    nested = sorted(b['id'] for b in brands
                    if len((b.get('icon_path') or '').split('/')) >= 5)

    lines = [
        MARKER,
        '',
        '# 物理层级与全库关系矩阵（generated）',
        '',
        '> 本文件由 `scripts/gen-physical-hierarchy-audit.py` 从 `config/brands.json` +',
        '> `scripts/brand_relationships.py` 派生，禁止手工编辑（CI 第 17 组逐字节校验）。',
        '',
        '## 1. 物理路径模型',
        '',
        '```text',
        'icons/<category>/<id>/<id>.png                     一级 direct child（category root 的直系子）',
        'icons/<category>/<中间父…>/<id>/<id>.png           同类中间父品牌下的深层子品牌（可多层）',
        '```',
        '',
        '- 一级目录恒为 `category`，不因关系改变；',
        '- 仅当直接父品牌**本身也有父品牌**（非 graph root）且同 category 且自身有图标时，才物理嵌套；',
        '- cross-category 父品牌不迁移；白名单母公司（无图标）不制造伪目录。',
        '',
        '## 2. 多层关系（需要嵌套的全部品牌）',
        '',
        '| Child | Direct Parent | Ancestor Chain | Category | Current Path | Expected Path | Action |',
        '|:---|:---|:---|:---|:---|:---|:---|',
    ]
    for bid in multi:
        e = ssot[bid]
        chain = ' → '.join([bid] + _ancestor_set_ordered(bid, ssot))
        exp = expected_icon_path(bid, ssot)
        cur = e.get('icon_path')
        lines.append('| `%s` | `%s` | %s | `%s` | `%s` | `%s` | %s |'
                     % (bid, e.get('parent_brand'), chain, e.get('category'), cur, exp,
                        'KEEP' if cur == exp else 'MOVE'))
    lines += ['', '多层关系（`child.parent_brand = P` 且 `P.parent_brand != null`）共 **%d** 条。' % len(multi), '']

    lines += [
        '## 3. cross-category 父品牌（VALID_CROSS_CATEGORY，不迁移）',
        '',
        '| Child | Parent | Child Category | Parent Category | Path | Action |',
        '|:---|:---|:---|:---|:---|:---|',
    ]
    for bid in cross:
        e = ssot[bid]
        lines.append('| `%s` | `%s` | `%s` | `%s` | `%s` | KEEP（关系由 SSOT 表达） |'
                     % (bid, e['parent_brand'], e['category'],
                        ssot[e['parent_brand']]['category'], e['icon_path']))
    lines += ['', 'cross-category 关系共 **%d** 条。' % len(cross), '']

    lines += [
        '## 4. Parent without icon（白名单母公司，不制造伪目录）',
        '',
        '| Parent (whitelist) | Children |',
        '|:---|:---|',
    ]
    kids_by_parent = {}
    for b in brands:
        p = b.get('parent_brand')
        if p and p not in ssot:
            kids_by_parent.setdefault(p, []).append(b['id'])
    for p in no_icon_parent:
        lines.append('| `%s` | %s |' % (p, ', '.join('`%s`' % k for k in sorted(kids_by_parent[p]))))
    lines += ['', '无图标母公司共 **%d** 个（登记于 `parent_brands_without_icon`）。' % len(no_icon_parent), '']

    lines += [
        '## 5. 生态矩阵（§47）',
        '',
        '| Ecosystem | Logical Root | Has Icon | Category | Canonical Descendants | Status |',
        '|:---|:---|:---|:---|:---|:---|',
    ]
    roots = sorted(eco_cat_ids)
    for r in roots:
        has_entry = r in ssot
        has_icon = bool(has_entry and ssot[r].get('icon_path'))
        kids = _descendants(r, ssot)   # graph-root 后代的 canonical 过滤由引擎负责
        status = 'Ecosystem' if (has_entry or r in aliases) else 'MISSING'
        lines.append('| `%s` | `%s` | %s | `%s` | %d | %s |'
                     % (r, r, 'YES' if has_icon else 'NO / PENDING', r, len(kids), status))
    lines += ['',
              '生态分类共 **%d** 个；其中无根图标（PENDING，登记白名单）**%d** 个。'
              % (len(roots), sum(1 for r in roots if not (r in ssot and ssot[r].get('icon_path')))), '']

    lines += [
        '## 6. 统计',
        '',
        '- canonical product brands：**%d**' % sum(1 for b in brands if is_canonical_brand(b)),
        '- canonical ecosystem entities：**%d**' % sum(1 for b in brands if b.get('entity_type') == 'ecosystem' and b.get('canonical') is True),
        '- 物理父品牌节点：**%d**' % len(physical_parent_nodes(brands_doc)),
        '- 深层嵌套品牌（路径 ≥ 5 段）：**%d**' % len(nested),
        '- 生态根（含逻辑生态根）：**%d**' % len(roots),
        '',
    ]
    doc = {'multi': multi, 'cross': cross, 'no_icon_parent': no_icon_parent,
           'nested': nested, 'ecosystem_roots': roots}
    return '\n'.join(lines), doc


def main():
    brands_doc = read_json_or_exit(REPO / 'config/brands.json', 'brands.json (品牌 SSOT)')
    cats_doc = read_json_or_exit(REPO / 'config/categories.json', 'categories.json (分类 SSOT)')
    text, info = build(brands_doc, cats_doc.get('categories', []))
    OUT.write_text(text, encoding='utf-8')
    print('✓ 已生成 %s' % OUT.relative_to(REPO))
    print('  多层关系 %d / cross-category %d / 无图标母公司 %d / 嵌套品牌 %d / 生态 %d'
          % (len(info['multi']), len(info['cross']), len(info['no_icon_parent']),
             len(info['nested']), len(info['ecosystem_roots'])))


if __name__ == '__main__':
    main()
