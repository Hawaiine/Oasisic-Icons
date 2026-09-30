#!/usr/bin/env python3
"""导出机器可读的品牌关系数据（下游消费用），由 `config/brands.json` + 关系引擎派生。

定位（§21 / §58）：**不是第二个 SSOT**。
  - 关系原始事实只存于 `config/brands.json`；
  - 本文件是**派生导出**（`generated: true`、`source: config/brands.json`），
    供 mihomo-rules 等下游稳定读取 `child → parent`、祖先链与生态根，
    避免下游从自己的旧数据反推 Oasisic SSOT；
  - CI 第 15 组要求本文件与 SSOT + 关系引擎逐项一致且可确定性重放（0 diff），
    手工修改会被拦截。

输出字段（每个品牌一条，按 child 排序）：
  child / display_name / category / entity_type / parent / ancestor_chain /
  graph_root / ecosystem_root / is_graph_root / is_ecosystem_root /
  icon_path / physical_path / physical_parent

physical_path 由统一路径解析器 expected_icon_path() 生成（多层物理层级：
icons/<category>/<中间父…>/<id>/<id>.png），下游不应自行拼接路径。
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'scripts'))

from brand_relationships import (  # noqa: E402
    _ancestor_set_ordered,
    ecosystem_category_ids,
    expected_icon_path,
    is_canonical_brand,
    resolve_ecosystem_root,
    resolve_graph_root,
)

BRANDS = REPO / 'config' / 'brands.json'
OUT = REPO / 'config' / 'brand-relationships.json'


def build(brands_doc, cats_list=None):
    brands = brands_doc.get('brands', [])
    ssot = {e['id']: e for e in brands if e.get('id')}
    eco_cat_ids = ecosystem_category_ids(cats_list)
    rows = []
    for bid in sorted(ssot):
        e = ssot[bid]
        gr = resolve_graph_root(bid, ssot)
        er = resolve_ecosystem_root(bid, ssot, eco_cat_ids)
        rows.append({
            'child': bid,
            'display_name': e.get('display_name', ''),
            'category': e.get('category', ''),
            'entity_type': e.get('entity_type', ''),
            'parent': e.get('parent_brand'),
            'ancestor_chain': _ancestor_set_ordered(bid, ssot),
            'graph_root': gr,
            'ecosystem_root': er,
            'is_graph_root': gr == bid,
            'is_ecosystem_root': e.get('entity_type') == 'ecosystem',
            'icon_path': e.get('icon_path'),
            'physical_path': expected_icon_path(bid, ssot),
            'physical_parent': (e.get('parent_brand') if (
                e.get('parent_brand') in ssot
                and ssot[e['parent_brand']].get('category') == e.get('category')
                and ssot[e['parent_brand']].get('parent_brand')) else None),
        })
    return {
        'schema_version': 1,
        'generated': True,
        'source': 'config/brands.json',
        'generated_by': 'scripts/export-brand-relationships.py',
        'note': ('派生导出（下游消费用），不是第二个 SSOT：关系事实只存于 config/brands.json，'
                 '手工修改本文件会被 CI 第 15 组拒绝。parent 为直接父品牌（immediate parent）；'
                 'ecosystem_root 为沿 parent 链动态派生：graph root 有 SSOT 条目且 entity_type=ecosystem，'
                 '或 graph root 无条目（parent_brands_without_icon，官方标志待补）但存在 type=ecosystem 的一级生态分类'
                 '（逻辑生态根，如 SpaceXAI）。physical_path 由统一路径解析器 expected_icon_path() 生成，'
                 '支持多层物理层级（icons/<category>/<中间父…>/<id>/<id>.png）。'),
        'relation_semantics': {
            'parent': 'immediate brand parent (Brand / Product Hierarchy only)',
            'excluded': ['corporate_ownership', 'developer_provider',
                         'platform_integration', 'distribution'],
            'generated_roots': ['graph_root', 'ecosystem_root'],
        },
        'ecosystem_categories': sorted(ecosystem_category_ids(cats_list)),
        'physical_path_model': {
            'rule': 'icons/<category>/<intermediate-parents…>/<id>/<id>.png',
            'resolver': 'scripts/brand_relationships.py::expected_icon_path',
            'flat_when': ['parent is the category root (direct child)',
                          'parent is in another category (cross-category)',
                          'parent has no icon (parent_brands_without_icon)'],
        },
        'whitelist_parents_without_icon': sorted(
            brands_doc.get('parent_brands_without_icon', [])),
        'brands': rows,
    }


def main():
    brands_doc = json.loads(BRANDS.read_text(encoding='utf-8'))
    cats_doc = json.loads((REPO / 'config' / 'categories.json').read_text(encoding='utf-8'))
    doc = build(brands_doc, cats_doc.get('categories', []))
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    canon = sum(1 for r in doc['brands'] if is_canonical_brand(r))
    print('✓ 已生成 %s（%d 个品牌；canonical %d；生态根 %d）'
          % (OUT.relative_to(REPO), len(doc['brands']), canon,
             sum(1 for r in doc['brands'] if r['is_ecosystem_root'])))


if __name__ == '__main__':
    main()
