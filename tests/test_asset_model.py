#!/usr/bin/env python3
"""canonical ecosystem 资产模型 mutation tests（2026-10-01 收紧）。

三条不变量（对 scripts/brand_relationships.py / ci-validate-icons.py 的 mutation
防护——改坏任何一条即测试 FAIL）：

  A. pending（icon_status=pending + 无 icon_path）：
     - 关系引擎放行（仅关系层存在，canonical=true + category=自身）；
     - expected_icon_path() 返回 None（无物理 leaf，不建目录/PNG）；
     - validate_physical_paths() 跳过（物理层缺席）；
     - Surge：不出现在 surge-icon.json（无 icon_path 派生 URL 的对象）。

  B. generated_temporary：
     - **必须**携带 icon_path（真实 PNG）——无 icon_path 时关系引擎 / 物理层 /
       CI 第 7 组全部 FAIL，不得复用 pending 豁免；
     - 有 icon_path 时正常走路径一致性 + 文件存在校验。

  C. 普通 canonical 品牌（entity_type != ecosystem，含 product_brand /
     country / system_icon / tool_app）：
     - 缺 icon_path 一律 FAIL（不得无图标静默通过）。
"""
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'scripts'))
from brand_relationships import (  # noqa: E402
    expected_icon_path,
    validate_physical_paths,
    validate_relationships,
)


def _doc(brands, eco_cats=(), whitelist=()):
    return {'brands': brands, 'parent_brands_without_icon': list(whitelist)}


def _eco_cats(ids):
    return [{'id': n, 'type': 'ecosystem'} for n in ids]


class AssetModelPendingTests(unittest.TestCase):
    """不变量 A：pending 生态根可无 icon_path，且物理层/Surge 缺席。"""

    def _doc_pending(self):
        return _doc([
            {'id': 'Root', 'display_name': 'Root', 'category': 'Root',
             'entity_type': 'ecosystem', 'canonical': True,
             'icon_status': 'pending'},
            {'id': 'ChildA', 'display_name': 'ChildA', 'category': 'Root',
             'entity_type': 'product_brand', 'icon_path': 'icons/Root/ChildA/ChildA.png',
             'parent_brand': 'Root'},
            {'id': 'ChildB', 'display_name': 'ChildB', 'category': 'Root',
             'entity_type': 'product_brand', 'icon_path': 'icons/Root/ChildB/ChildB.png',
             'parent_brand': 'Root'},
        ], eco_cats=['Root'])

    def test_pending_no_icon_passes_relationship_engine(self):
        errs = validate_relationships(self._doc_pending(), _eco_cats(['Root']))
        self.assertEqual(errs, [], 'pending 生态根（无 icon_path）必须放行: %s' % errs)

    def test_pending_expected_icon_path_is_none(self):
        doc = self._doc_pending()
        ssot = {e['id']: e for e in doc['brands']}
        self.assertIsNone(expected_icon_path('Root', ssot),
                          'pending 生态根无物理 leaf：expected_icon_path 必须为 None')
        # 子品牌路径推导不受根 pending 影响（直系子平铺）
        self.assertEqual(expected_icon_path('ChildA', ssot),
                         'icons/Root/ChildA/ChildA.png')

    def test_pending_skipped_in_physical_validation(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for rel in ('icons/Root/ChildA/ChildA.png', 'icons/Root/ChildB/ChildB.png'):
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b'\x89PNG\r\n\x1a\n')
            doc = self._doc_pending()
            errs = validate_physical_paths(doc, _eco_cats(['Root']), root)
            self.assertEqual(errs, [],
                             'pending 根无物理 leaf：物理校验必须跳过根，子品牌正常: %s' % errs)

    def test_pending_root_must_be_canonical_and_self_category(self):
        doc = self._doc_pending()
        doc['brands'][0]['canonical'] = False
        errs = validate_relationships(doc, _eco_cats(['Root']))
        # 引擎层不检查 canonical 字段（CI 第 7 组负责）；但 category 必须等于自身
        self.assertNotIn('canonical', ' '.join(errs))
        doc2 = self._doc_pending()
        doc2['brands'][0]['category'] = 'Other'
        errs2 = validate_relationships(doc2, _eco_cats(['Root']))
        self.assertTrue(any('未以自身为一级分类' in e for e in errs2),
                        'pending 根 category 仍必须等于自身: %s' % errs2)

    def test_pending_not_in_surge(self):
        """Surge 派生口径：无 icon_path 的条目（唯一合法形态 = pending 生态根）
        不得出现在 surge-icon.json。对真实仓库做数据级断言。"""
        brands_doc = json.loads(
            (REPO / 'config' / 'brands.json').read_text(encoding='utf-8'))
        surge_doc = json.loads(
            (REPO / 'config' / 'surge-icon.json').read_text(encoding='utf-8'))
        surge_names = {i['name'] for i in surge_doc.get('icons', [])}
        no_icon = [e['id'] for e in brands_doc['brands'] if not e.get('icon_path')]
        for bid in no_icon:
            self.assertNotIn(bid, surge_names,
                             '无 icon_path 条目 %s 不得出现在 surge-icon.json' % bid)
            e = next(x for x in brands_doc['brands'] if x['id'] == bid)
            self.assertEqual(
                (e.get('entity_type') == 'ecosystem'
                 and e.get('icon_status') == 'pending' and e.get('canonical') is True),
                True,
                '唯一合法的无 icon_path 形态是 pending 生态根: %s' % bid)
        # 反向：有 icon_path 的品牌全部在 surge（数量与名单一致）
        with_icon = {e['id'] for e in brands_doc['brands'] if e.get('icon_path')}
        self.assertEqual(with_icon, surge_names,
                         'surge 名单必须恰为有 icon_path 的 SSOT 品牌集合')


class AssetModelGeneratedTemporaryTests(unittest.TestCase):
    """不变量 B：generated_temporary 必须携带真实 icon_path。"""

    def _mk(self, icon_path=None):
        doc = _doc([
            {'id': 'Root', 'display_name': 'Root', 'category': 'Root',
             'entity_type': 'ecosystem', 'canonical': True,
             'icon_status': 'generated_temporary',
             **({} if icon_path is None else {'icon_path': icon_path})},
            {'id': 'ChildA', 'display_name': 'ChildA', 'category': 'Root',
             'entity_type': 'product_brand', 'icon_path': 'icons/Root/ChildA/ChildA.png',
             'parent_brand': 'Root'},
            {'id': 'ChildB', 'display_name': 'ChildB', 'category': 'Root',
             'entity_type': 'product_brand', 'icon_path': 'icons/Root/ChildB/ChildB.png',
             'parent_brand': 'Root'},
        ], eco_cats=['Root'])
        return doc

    def test_generated_temporary_without_icon_path_fails_engine(self):
        doc = self._mk()
        errs = validate_relationships(doc, _eco_cats(['Root']))
        self.assertTrue(
            any('generated_temporary' in e and 'icon_path' in e for e in errs),
            'generated_temporary 无 icon_path 必须 FAIL: %s' % errs)

    def test_generated_temporary_with_icon_path_passes_engine(self):
        doc = self._mk('icons/Root/Root/Root.png')
        errs = validate_relationships(doc, _eco_cats(['Root']))
        self.assertEqual(errs, [], 'generated_temporary + 合法 icon_path 必须放行: %s' % errs)

    def test_generated_temporary_physical_validation_requires_real_png(self):
        import tempfile
        doc = self._mk('icons/Root/Root/Root.png')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for rel in ('icons/Root/Root/Root.png', 'icons/Root/ChildA/ChildA.png',
                         'icons/Root/ChildB/ChildB.png'):
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b'\x89PNG\r\n\x1a\n')
            self.assertEqual(validate_physical_paths(doc, _eco_cats(['Root']), root), [])
            # mutation：文件缺失 → 必须 FAIL（generated_temporary 不豁免物理存在性）
            (root / 'icons/Root/Root/Root.png').unlink()
            errs = validate_physical_paths(doc, _eco_cats(['Root']), root)
            self.assertTrue(any('icon 文件不存在' in e for e in errs),
                            'generated_temporary 的 PNG 缺失必须被物理校验拦截: %s' % errs)

    def test_generated_temporary_icon_must_be_in_eco_dir(self):
        doc = self._mk('icons/Other/Root/Root.png')
        errs = validate_relationships(doc, _eco_cats(['Root']))
        self.assertTrue(any('不在生态目录内' in e for e in errs),
                        'generated_temporary 图标必须位于生态目录内: %s' % errs)

    def test_generated_temporary_must_not_reuse_pending_exemption(self):
        """核心 mutation 防护：若 expected_icon_path / physical 校验把
        generated_temporary 当作 pending 跳过（返回 None / continue），
        无 icon_path 的生成临时图标就会静默通过——此处强制拦截。"""
        import tempfile
        doc = self._mk()
        ssot = {e['id']: e for e in doc['brands']}
        # 解析器：generated_temporary 无 icon_path 时不得返回 None
        self.assertEqual(expected_icon_path('Root', ssot), 'icons/Root/Root/Root.png')
        # 物理层：pending 判定不得命中 generated_temporary
        with tempfile.TemporaryDirectory() as td:
            errs = validate_physical_paths(doc, _eco_cats(['Root']), Path(td))
            self.assertTrue(any('icon_path 与路径规则不符' in e for e in errs),
                            'generated_temporary 不得走 pending 豁免: %s' % errs)


class AssetModelRegularBrandTests(unittest.TestCase):
    """不变量 C：普通 canonical 品牌（非 ecosystem）缺 icon_path 一律 FAIL。"""

    def test_product_brand_without_icon_fails(self):
        doc = _doc([
            {'id': 'P', 'display_name': 'P', 'category': 'Svc',
             'entity_type': 'product_brand'},
            {'id': 'Q', 'display_name': 'Q', 'category': 'Svc',
             'entity_type': 'product_brand', 'icon_path': 'icons/Svc/Q/Q.png',
             'parent_brand': 'P'},
        ])
        errs = validate_relationships(doc, [])
        self.assertTrue(any('SSOT 条目缺 icon_path' in e and 'P' in e for e in errs),
                        'product_brand 无 icon_path 不得静默通过: %s' % errs)

    def test_country_system_icon_tool_app_without_icon_fail(self):
        for et in ('country', 'system_icon', 'tool_app'):
            doc = _doc([{'id': 'X1', 'display_name': 'X1', 'category': 'System',
                         'entity_type': et}])
            errs = validate_relationships(doc, [])
            self.assertTrue(any('SSOT 条目缺 icon_path' in e for e in errs),
                            '%s 无 icon_path 不得静默通过: %s' % (et, errs))

    def test_ecosystem_without_icon_and_without_pending_fails(self):
        # 生态根无 icon_path 且未登记 icon_status → 静默漂移，必须 FAIL
        doc = _doc([
            {'id': 'Root', 'display_name': 'Root', 'category': 'Root',
             'entity_type': 'ecosystem'},
            {'id': 'ChildA', 'display_name': 'ChildA', 'category': 'Root',
             'entity_type': 'product_brand', 'icon_path': 'icons/Root/ChildA/ChildA.png',
             'parent_brand': 'Root'},
            {'id': 'ChildB', 'display_name': 'ChildB', 'category': 'Root',
             'entity_type': 'product_brand', 'icon_path': 'icons/Root/ChildB/ChildB.png',
             'parent_brand': 'Root'},
        ], eco_cats=['Root'])
        errs = validate_relationships(doc, _eco_cats(['Root']))
        self.assertTrue(any('无 icon_path' in e and 'Root' in e for e in errs),
                        '无 icon_path 且未登记 icon_status 的生态根必须 FAIL: %s' % errs)

    def test_ci_surge_count_excludes_pending_only(self):
        """CI 第 8 组口径复算：surge 条目数 == 有 icon_path 的 SSOT 品牌数 ==
        磁盘 PNG 数；pending 生态根（无 icon_path）三方一致地被排除。"""
        brands_doc = json.loads(
            (REPO / 'config' / 'brands.json').read_text(encoding='utf-8'))
        surge_doc = json.loads(
            (REPO / 'config' / 'surge-icon.json').read_text(encoding='utf-8'))
        n_png = len(list((REPO / 'icons').rglob('*.png')))
        n_with_icon = sum(1 for e in brands_doc['brands'] if e.get('icon_path'))
        n_surge = len(surge_doc.get('icons', []))
        self.assertEqual(n_surge, n_png,
                         'surge 条目数必须等于磁盘 PNG 数（%d != %d）' % (n_surge, n_png))
        self.assertEqual(n_surge, n_with_icon,
                         'surge 条目数必须等于有 icon_path 的 SSOT 品牌数（pending 排除）')


if __name__ == '__main__':
    unittest.main(verbosity=2)
