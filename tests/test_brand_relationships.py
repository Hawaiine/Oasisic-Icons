#!/usr/bin/env python3
"""品牌关系图负测（python -m unittest 或 pytest 均可）。

验证 scripts/brand_relationships.py 的校验规则在异常输入下确实 FAIL：
  - parent_brand 循环（A→B→A）
  - parent_brand 自指（A→A）
  - parent_brand 指向不存在的品牌（链末端缺失 / 直接缺失）
  - 生态分类无对应品牌条目 / 根 entity_type 非 ecosystem
  - 生态根 canonical descendants < 2（阈值负测：0 与 1）
  - 阈值正测：descendants = 2 / 3 / 嵌套 2（孙代）→ 通过
  - 位于生态分类内但祖先链未经过根（错放分类）
  - 白名单混入已有 icon 的品牌
  - 生态根 icon 不在生态目录 / 无 icon 未登记白名单
  - resolve_ecosystem_root 动态派生正确性（含中间层）
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from brand_relationships import (  # noqa: E402
    _descendants,
    _root_of,
    resolve_ecosystem_root,
    validate_relationships,
)


def eco_doc(brands, eco_cats, whitelist=()):
    return {
        'brands': [
            {
                'id': b,
                'display_name': b,
                'category': cat,
                'entity_type': et,
                'icon_path': 'icons/%s/%s/%s.png' % (cat, b, b),
                **({ 'parent_brand': p } if p else {}),
            }
            for b, p, et, cat in brands
        ],
        'parent_brands_without_icon': list(whitelist),
    }


def eco_cats(names):
    return [{'id': n, 'type': 'ecosystem'} for n in names]


class RelationshipTests(unittest.TestCase):
    def _errs(self, doc, cats):
        return validate_relationships(doc, cats)

    # ---- 正常图 ----
    def test_valid_chain_passes(self):
        doc = eco_doc([
            ('Meta', None, 'ecosystem', 'Meta'),
            ('Facebook', 'Meta', 'product_brand', 'Meta'),
            ('Instagram', 'Facebook', 'product_brand', 'Meta'),
            ('WhatsApp', 'Facebook', 'product_brand', 'Meta'),
            ('Threads', 'Facebook', 'product_brand', 'Meta'),
        ], ['Meta'])
        self.assertEqual(self._errs(doc, eco_cats(['Meta'])), [])

    def test_valid_middle_layer_no_explosion(self):
        # YouTube 是中间层（parent=Google, 1 直系子 YouTubeMusic），不应要求 YouTube 生态分类
        doc = eco_doc([
            ('Google', None, 'ecosystem', 'Google'),
            ('YouTube', 'Google', 'product_brand', 'Google'),
            ('YouTubeMusic', 'YouTube', 'product_brand', 'Google'),
            ('Gmail', 'Google', 'product_brand', 'Google'),
        ], ['Google'])
        self.assertEqual(self._errs(doc, eco_cats(['Google'])), [])

    # ---- 负测：循环 / 自指 / 缺失 ----
    def test_cycle_fails(self):
        doc = eco_doc([
            ('A', 'B', 'product_brand', 'X'),
            ('B', 'A', 'product_brand', 'X'),
        ], [])
        self.assertTrue(any('循环' in e for e in self._errs(doc, [])),
                        'A→B→A 必须 FAIL')

    def test_self_parent_fails(self):
        doc = eco_doc([('A', 'A', 'product_brand', 'X')], [])
        self.assertTrue(any('自指' in e for e in self._errs(doc, [])))

    def test_missing_direct_parent_fails(self):
        doc = eco_doc([('Instagram', 'Facebook', 'product_brand', 'X')], [])
        self.assertTrue(any('不存在' in e for e in self._errs(doc, [])))

    def test_missing_chain_end_fails(self):
        doc = eco_doc([
            ('A', 'B', 'product_brand', 'X'),
            ('B', 'C', 'product_brand', 'X'),  # C 不在 SSOT 且不在白名单
        ], [])
        self.assertTrue(any('链末端不存在' in e for e in self._errs(doc, [])))

    def test_missing_chain_end_whitelisted_passes(self):
        doc = eco_doc([('A', 'B', 'product_brand', 'X')], [], whitelist=('B',))
        self.assertEqual(self._errs(doc, []), [])

    # ---- 负测：生态根 / 分类 ----
    def test_eco_root_no_category_fails(self):
        doc = eco_doc([
            ('Meta', None, 'ecosystem', 'Social'),
            ('A', 'Meta', 'product_brand', 'Meta'),
            ('B', 'Meta', 'product_brand', 'Meta'),
        ], ['Meta'])
        errs = self._errs(doc, eco_cats(['Meta']))
        self.assertTrue(any('未以自身为一级分类' in e for e in errs))

    def test_eco_root_descendants_zero_fails(self):
        doc = eco_doc([('Meta', None, 'ecosystem', 'Meta')], ['Meta'])
        errs = self._errs(doc, eco_cats(['Meta']))
        self.assertTrue(any('descendants < 2' in e for e in errs),
                        'descendants=0 必须 FAIL')

    def test_eco_root_descendants_one_fails(self):
        doc = eco_doc([
            ('Meta', None, 'ecosystem', 'Meta'),
            ('A', 'Meta', 'product_brand', 'Meta'),
        ], ['Meta'])
        errs = self._errs(doc, eco_cats(['Meta']))
        self.assertTrue(any('descendants < 2' in e for e in errs),
                        'descendants=1 必须 FAIL')

    def test_eco_root_descendants_two_passes(self):
        doc = eco_doc([
            ('Meta', None, 'ecosystem', 'Meta'),
            ('A', 'Meta', 'product_brand', 'Meta'),
            ('B', 'Meta', 'product_brand', 'Meta'),
        ], ['Meta'])
        self.assertEqual(self._errs(doc, eco_cats(['Meta'])), [],
                         'descendants=2 必须 PASS')

    def test_eco_root_nested_descendants_two_passes(self):
        # Meta → ChildA → ChildB：root 直系子仅 1，但 canonical descendants=2 → 生态必须
        doc = eco_doc([
            ('Meta', None, 'ecosystem', 'Meta'),
            ('ChildA', 'Meta', 'product_brand', 'Meta'),
            ('ChildB', 'ChildA', 'product_brand', 'Meta'),
        ], ['Meta'])
        self.assertEqual(self._errs(doc, eco_cats(['Meta'])), [],
                         '嵌套 descendants=2 必须 PASS')

    def test_eco_category_no_brand_fails(self):
        doc = eco_doc([('A', 'Meta', 'product_brand', 'Meta'),
                       ('B', 'Meta', 'product_brand', 'Meta')], ['Meta'])
        errs = self._errs(doc, eco_cats(['Meta']))
        self.assertTrue(any('无对应品牌条目' in e for e in errs))

    def test_eco_category_wrong_entity_type_fails(self):
        doc = eco_doc([
            ('Meta', None, 'product_brand', 'Meta'),
            ('A', 'Meta', 'product_brand', 'Meta'),
            ('B', 'Meta', 'product_brand', 'Meta'),
        ], ['Meta'])
        errs = self._errs(doc, eco_cats(['Meta']))
        self.assertTrue(any('entity_type 非 ecosystem' in e for e in errs))

    def test_brand_inside_eco_cat_wrong_chain_fails(self):
        doc = eco_doc([
            ('Meta', None, 'ecosystem', 'Meta'),
            ('A', 'Meta', 'product_brand', 'Meta'),
            ('B', 'Meta', 'product_brand', 'Meta'),
            ('C', 'Google', 'product_brand', 'Meta'),  # 在 Meta/ 但祖先链无 Meta
        ], ['Meta'])
        errs = self._errs(doc, eco_cats(['Meta']))
        self.assertTrue(any('祖先链未经过根' in e for e in errs))

    # ---- 负测：白名单 / root icon ----
    def test_whitelist_containing_ssot_brand_fails(self):
        doc = eco_doc([('Meta', None, 'ecosystem', 'Meta'),
                       ('A', 'Meta', 'product_brand', 'Meta'),
                       ('B', 'Meta', 'product_brand', 'Meta')], ['Meta'],
                      whitelist=('Meta',))
        errs = self._errs(doc, eco_cats(['Meta']))
        self.assertTrue(any('含已有 icon' in e for e in errs))

    def test_eco_root_with_parent_fails(self):
        # §87：生态根不得再声明 parent_brand（必须是关系图顶端；中间层一律 product_brand）
        doc = eco_doc([
            ('Umbrella', None, 'product_brand', 'X'),
            ('Meta', 'Umbrella', 'ecosystem', 'Meta'),
            ('Instagram', 'Meta', 'product_brand', 'Meta'),
            ('WhatsApp', 'Meta', 'product_brand', 'Meta'),
        ], ['Meta'])
        errs = self._errs(doc, eco_cats(['Meta']))
        self.assertTrue(any('不应再有 parent_brand' in e for e in errs), errs)

    def test_eco_root_icon_outside_eco_dir_fails(self):
        doc = eco_doc([
            ('Meta', None, 'ecosystem', 'Meta'),
            ('A', 'Meta', 'product_brand', 'Meta'),
            ('B', 'Meta', 'product_brand', 'Meta'),
        ], ['Meta'])
        doc['brands'][0]['icon_path'] = 'icons/Social/Meta/Meta.png'
        errs = self._errs(doc, eco_cats(['Meta']))
        self.assertTrue(any('不在生态目录内' in e for e in errs))

    def test_eco_root_no_icon_fails(self):
        doc = eco_doc([
            ('Meta', None, 'ecosystem', 'Meta'),
            ('A', 'Meta', 'product_brand', 'Meta'),
            ('B', 'Meta', 'product_brand', 'Meta'),
        ], ['Meta'])
        doc['brands'][0]['icon_path'] = ''
        errs = self._errs(doc, eco_cats(['Meta']))
        self.assertTrue(any('无 icon' in e for e in errs),
                        'SSOT 条目的生态根必须带 icon')

    def test_eco_category_no_root_brand_whitelisted_passes(self):
        # 生态分类 + root 无 SSOT 条目 + 白名单登记 → 合法（root 无图标场景）
        doc = eco_doc([
            ('A', 'Meta', 'product_brand', 'Meta'),
            ('B', 'Meta', 'product_brand', 'Meta'),
        ], ['Meta'], whitelist=('Meta',))
        self.assertEqual(self._errs(doc, eco_cats(['Meta'])), [])

    def test_eco_category_no_root_brand_not_whitelisted_fails(self):
        doc = eco_doc([
            ('A', 'Meta', 'product_brand', 'Meta'),
            ('B', 'Meta', 'product_brand', 'Meta'),
        ], ['Meta'])
        errs = self._errs(doc, eco_cats(['Meta']))
        self.assertTrue(any('无对应品牌条目且未登记白名单' in e for e in errs))

    # ---- 派生 API ----
    def test_resolve_root_middle_layer(self):
        doc = eco_doc([
            ('Google', None, 'ecosystem', 'Google'),
            ('YouTube', 'Google', 'product_brand', 'Google'),
            ('YouTubeMusic', 'YouTube', 'product_brand', 'Google'),
        ], ['Google'])
        ssot = {e['id']: e for e in doc['brands']}
        self.assertEqual(resolve_ecosystem_root('YouTubeMusic', ssot), 'Google')
        self.assertEqual(resolve_ecosystem_root('YouTube', ssot), 'Google')

    def test_resolve_root_no_parent(self):
        doc = eco_doc([('Netflix', None, 'product_brand', 'Media')], [])
        ssot = {e['id']: e for e in doc['brands']}
        self.assertEqual(resolve_ecosystem_root('Netflix', ssot), 'Netflix')

    def test_descendants_excludes_root_and_non_canonical(self):
        doc = eco_doc([
            ('Meta', None, 'ecosystem', 'Meta'),
            ('Facebook', 'Meta', 'product_brand', 'Meta'),
            ('Instagram', 'Facebook', 'product_brand', 'Meta'),
            ('WhatsApp', 'Facebook', 'product_brand', 'Meta'),
        ], ['Meta'])
        ssot = {e['id']: e for e in doc['brands']}
        ds = _descendants('Meta', ssot)
        self.assertEqual(ds, {'Facebook', 'Instagram', 'WhatsApp'},
                         'descendants 不含 root 本身')
        self.assertEqual(len(_descendants('Facebook', ssot)), 2)


class RealRepoTests(unittest.TestCase):
    """对当前真实 brands.json 跑关系校验 + 生态根派生抽查。"""

    @classmethod
    def setUpClass(cls):
        import json
        repo = Path(__file__).resolve().parent.parent
        cls.brands_doc = json.loads(
            (repo / 'config' / 'brands.json').read_text(encoding='utf-8'))
        cls.cats_doc = json.loads(
            (repo / 'config' / 'categories.json').read_text(encoding='utf-8'))
        cls.ssot = {e['id']: e for e in cls.brands_doc['brands']}

    def test_real_repo_passes(self):
        errs = validate_relationships(self.brands_doc, self.cats_doc['categories'])
        self.assertEqual(errs, [])

    def test_real_repo_spot_checks(self):
        self.assertEqual(resolve_ecosystem_root('Instagram', self.ssot), 'Meta')
        self.assertEqual(resolve_ecosystem_root('YouTubeMusic', self.ssot), 'Google')
        self.assertEqual(resolve_ecosystem_root('iCloudPrivateRelay', self.ssot), 'Apple')
        self.assertEqual(resolve_ecosystem_root('Mijia', self.ssot), 'Xiaomi')
        self.assertEqual(resolve_ecosystem_root('Weibo', self.ssot), 'SINA')
        # 17 个生态根全部派生为自身
        for e in self.brands_doc['brands']:
            if e.get('entity_type') == 'ecosystem':
                self.assertEqual(resolve_ecosystem_root(e['id'], self.ssot), e['id'],
                                 '生态根 %s 派生应为自身' % e['id'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
