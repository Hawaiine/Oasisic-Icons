#!/usr/bin/env python3
"""品牌关系图负测（python -m unittest 或 pytest 均可）。

验证 scripts/brand_relationships.py 的校验规则在异常输入下确实 FAIL：
  - parent_brand 循环（A→B→A）/ 自指 / 指向不存在（链末端/直接）
  - 生态分类无对应品牌条目 / 根 entity_type 非 ecosystem
  - 生态根 canonical descendants < 2（正向阈值负测：0 与 1）
  - 阈值正测：descendants = 2 / 3 / 嵌套 2（孙代）→ 通过
  - **反向阈值**：graph root descendants ≥ 2 但 entity_type 非 ecosystem → FAIL
  - **中间层不得升级**：Facebook descendants=2 但非 graph root → 不要求 ecosystem
  - **canonical 过滤**：country / system_icon / tool_app 不计入 descendants
  - 位于生态分类内但祖先链未经过根（错放分类）
  - 白名单混入已有 icon 的品牌
  - 生态根 icon 不在生态目录 / 无 icon 未登记白名单
  - resolve_graph_root / resolve_ecosystem_root 语义分离（Mijia→Xiaomi vs Instagram→Meta）
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from brand_relationships import (  # noqa: E402
    _descendants,
    is_canonical_brand,
    resolve_ecosystem_root,
    resolve_graph_root,
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


def _ssot(doc):
    return {e['id']: e for e in doc['brands']}


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
        self.assertTrue(any('icon_status' in e for e in errs),
                        '无 icon 的正式生态根必须明确 icon_status')

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

    # ---- 派生 API：graph root ≠ ecosystem root ----
    def test_resolve_root_middle_layer(self):
        doc = eco_doc([
            ('Google', None, 'ecosystem', 'Google'),
            ('YouTube', 'Google', 'product_brand', 'Google'),
            ('YouTubeMusic', 'YouTube', 'product_brand', 'Google'),
        ], ['Google'])
        ssot = _ssot(doc)
        # graph root 都是 Google
        self.assertEqual(resolve_graph_root('YouTubeMusic', ssot), 'Google')
        self.assertEqual(resolve_graph_root('YouTube', ssot), 'Google')
        # ecosystem root 也解析为 Google（Google 是 ecosystem）
        self.assertEqual(resolve_ecosystem_root('YouTubeMusic', ssot), 'Google')
        self.assertEqual(resolve_ecosystem_root('YouTube', ssot), 'Google')

    def test_resolve_root_no_parent(self):
        doc = eco_doc([('Netflix', None, 'product_brand', 'Media')], [])
        ssot = _ssot(doc)
        # graph root = 自身（无父）
        self.assertEqual(resolve_graph_root('Netflix', ssot), 'Netflix')
        # 非 ecosystem → ecosystem root = None
        self.assertIsNone(resolve_ecosystem_root('Netflix', ssot))

    def test_descendants_excludes_root_and_non_canonical(self):
        doc = eco_doc([
            ('Meta', None, 'ecosystem', 'Meta'),
            ('Facebook', 'Meta', 'product_brand', 'Meta'),
            ('Instagram', 'Facebook', 'product_brand', 'Meta'),
            ('WhatsApp', 'Facebook', 'product_brand', 'Meta'),
        ], ['Meta'])
        ssot = _ssot(doc)
        ds = _descendants('Meta', ssot)
        self.assertEqual(ds, {'Facebook', 'Instagram', 'WhatsApp'},
                         'descendants 不含 root 本身')
        self.assertEqual(len(_descendants('Facebook', ssot)), 2)


class ReverseThresholdTests(unittest.TestCase):
    """§4-§11：反向生态阈值 —— graph root descendants ≥ 2 → 必须 ecosystem。"""

    def test_reverse_root_not_ecosystem_fails(self):
        # Root 有 2 个 product_brand 子，但 Root.entity_type=product_brand → 必须 FAIL
        doc = eco_doc([
            ('Root', None, 'product_brand', 'Functional'),
            ('A', 'Root', 'product_brand', 'Functional'),
            ('B', 'Root', 'product_brand', 'Functional'),
        ], [])
        errs = validate_relationships(doc, [])
        self.assertTrue(any('canonical descendants ≥ 2' in e for e in errs),
                        'graph root descendants=2 非 ecosystem 必须 FAIL: %s' % errs)

    def test_reverse_root_zero_one_no_fail(self):
        # descendants=1：不要求 ecosystem（阈值仅 ≥2 触发）
        doc = eco_doc([
            ('Root', None, 'product_brand', 'Functional'),
            ('A', 'Root', 'product_brand', 'Functional'),
        ], [])
        self.assertEqual(validate_relationships(doc, []), [],
                         'graph root descendants=1 不应被要求 ecosystem')

    def test_intermediate_with_two_children_not_promoted(self):
        # Meta → Facebook → {Instagram, Messenger}：
        # Facebook descendants=2 但它是中间层（有 SSOT 父 Meta）→ 不得被要求升级 ecosystem
        doc = eco_doc([
            ('Meta', None, 'ecosystem', 'Meta'),
            ('Facebook', 'Meta', 'product_brand', 'Meta'),
            ('Instagram', 'Facebook', 'product_brand', 'Meta'),
            ('Messenger', 'Facebook', 'product_brand', 'Meta'),
        ], ['Meta'])
        errs = validate_relationships(doc, eco_cats(['Meta']))
        self.assertFalse(
            any('Facebook' in e and 'descendants ≥ 2' in e for e in errs),
            '中间层 Facebook 不得因 descendants≥2 被要求升级 ecosystem: %s' % errs)
        # Meta 是合法 ecosystem root，整体应通过
        self.assertEqual(errs, [])


class CanonicalFilterTests(unittest.TestCase):
    """§12-§17：canonical descendant 实体过滤 —— 只计 product_brand。"""

    def test_country_not_counted(self):
        # Root → {ProductA, ProductB, CountryX}：CountryX 非 product_brand，不计入
        doc = eco_doc([
            ('Root', None, 'ecosystem', 'Root'),
            ('ProductA', 'Root', 'product_brand', 'Root'),
            ('ProductB', 'Root', 'product_brand', 'Root'),
            ('CountryX', 'Root', 'country', 'Root'),
        ], ['Root'])
        ssot = _ssot(doc)
        ds = _descendants('Root', ssot)
        self.assertNotIn('CountryX', ds)
        self.assertEqual(ds, {'ProductA', 'ProductB'},
                         'country 实体不得计入 canonical descendants')

    def test_system_icon_and_tool_app_not_counted(self):
        doc = eco_doc([
            ('Root', None, 'ecosystem', 'Root'),
            ('ProductA', 'Root', 'product_brand', 'Root'),
            ('ProductB', 'Root', 'product_brand', 'Root'),
            ('SysIcon', 'Root', 'system_icon', 'Root'),
            ('ToolX', 'Root', 'tool_app', 'Root'),
        ], ['Root'])
        ssot = _ssot(doc)
        ds = _descendants('Root', ssot)
        self.assertEqual(ds, {'ProductA', 'ProductB'},
                         'system_icon / tool_app 不得计入 canonical descendants')

    def test_is_canonical_brand_predicate(self):
        # predicate 单一来源：只有 product_brand 为 True
        self.assertTrue(is_canonical_brand({'entity_type': 'product_brand'}))
        self.assertFalse(is_canonical_brand({'entity_type': 'ecosystem'}))
        self.assertFalse(is_canonical_brand({'entity_type': 'country'}))
        self.assertFalse(is_canonical_brand({'entity_type': 'system_icon'}))
        self.assertFalse(is_canonical_brand({'entity_type': 'tool_app'}))

    def test_filter_does_not_flip_threshold(self):
        # Root 有 2 product + 2 非 canonical → canonical=2，仍满足生态阈值（PASS）
        doc = eco_doc([
            ('Root', None, 'ecosystem', 'Root'),
            ('ProductA', 'Root', 'product_brand', 'Root'),
            ('ProductB', 'Root', 'product_brand', 'Root'),
            ('CountryX', 'Root', 'country', 'Root'),
            ('SysIcon', 'Root', 'system_icon', 'Root'),
        ], ['Root'])
        self.assertEqual(validate_relationships(doc, eco_cats(['Root'])), [],
                         '非 canonical 实体不应压低 canonical descendants 计数')


class ParentTypeTests(unittest.TestCase):
    """§49-§53：parent_brand 的父节点类型合法性。

    父品牌只能是 product_brand / ecosystem；country / system_icon / tool_app
    不是品牌节点，作为 parent_brand 必须 FAIL（否则会凭空制造
    「品牌挂在国家/系统图标下」的关系）。
    """

    def test_product_brand_parent_allowed(self):
        doc = eco_doc([('A', None, 'product_brand', 'Svc'),
                       ('B', 'A', 'product_brand', 'Svc')], [])
        self.assertEqual(validate_relationships(doc, []), [])

    def test_ecosystem_parent_allowed(self):
        doc = eco_doc([('E', None, 'ecosystem', 'E'),
                       ('C', 'E', 'product_brand', 'E'),
                       ('D', 'E', 'product_brand', 'E')], [])
        self.assertEqual(validate_relationships(doc, eco_cats(['E'])), [])

    def test_forbidden_parent_types_fail(self):
        for pt in ('country', 'system_icon', 'tool_app'):
            doc = eco_doc([('P', None, pt, 'System'),
                           ('C', 'P', 'product_brand', 'Svc')], [])
            errs = validate_relationships(doc, [])
            self.assertTrue(any('parent_brand 类型非法' in e for e in errs),
                            '%s 作为 parent_brand 必须 FAIL，实际: %s' % (pt, errs))

    def test_ecosystem_with_parent_fails(self):
        """§53：生态根不得再有 parent_brand。"""
        doc = eco_doc([('Top', None, 'product_brand', 'Top'),
                       ('E', 'Top', 'ecosystem', 'E'),
                       ('C', 'E', 'product_brand', 'E'),
                       ('D', 'E', 'product_brand', 'E')], [])
        errs = validate_relationships(doc, eco_cats(['E']))
        self.assertTrue(any('不应再有 parent_brand' in e for e in errs), errs)


class PhysicalParentScopeTests(unittest.TestCase):
    """§54-§55：只有 canonical product_brand 子节点才使父节点成为物理父节点。

    Parent README Policy 的作用域不得被非品牌子节点（system_icon 等）撑大。
    """

    def _doc(self, child_type):
        return {'brands': [
            {'id': 'Parent', 'display_name': 'Parent', 'category': 'Svc',
             'entity_type': 'product_brand', 'icon_path': 'icons/Svc/Parent/Parent.png'},
            {'id': 'Child', 'display_name': 'Child', 'category': 'Svc',
             'entity_type': child_type, 'icon_path': 'icons/Svc/Child/Child.png',
             'parent_brand': 'Parent'},
        ]}

    def test_non_canonical_child_does_not_require_readme(self):
        from brand_relationships import physical_parent_nodes
        for ct in ('system_icon', 'tool_app', 'country'):
            self.assertEqual(physical_parent_nodes(self._doc(ct)), set(),
                             '%s 子节点不应使 Parent 成为物理父节点' % ct)

    def test_canonical_child_requires_readme(self):
        from brand_relationships import physical_parent_nodes
        self.assertEqual(physical_parent_nodes(self._doc('product_brand')), {'Parent'})


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

    @staticmethod
    def _manifest():
        import json
        repo = Path(__file__).resolve().parent.parent
        return json.loads(
            (repo / 'config' / 'parent-edge-evidence.json').read_text(encoding='utf-8'))

    def test_real_repo_passes(self):
        errs = validate_relationships(self.brands_doc, self.cats_doc['categories'])
        self.assertEqual(errs, [])

    def test_real_repo_spot_checks(self):
        # 生态图内品牌 → ecosystem root 为生态根
        self.assertEqual(resolve_ecosystem_root('Instagram', self.ssot), 'Meta')
        self.assertEqual(resolve_ecosystem_root('YouTubeMusic', self.ssot), 'Google')
        self.assertEqual(resolve_ecosystem_root('iCloudPrivateRelay', self.ssot), 'Apple')
        # graph root ≠ ecosystem root：Mijia → Xiaomi（非生态）→ ecosystem root = None
        self.assertEqual(resolve_graph_root('Mijia', self.ssot), 'Xiaomi')
        self.assertIsNone(resolve_ecosystem_root('Mijia', self.ssot),
                          'Xiaomi 非 ecosystem，Mijia 的 ecosystem root 应为 None')
        self.assertEqual(resolve_graph_root('Weibo', self.ssot), 'SINA')
        self.assertIsNone(resolve_ecosystem_root('Weibo', self.ssot),
                          'SINA 非 ecosystem，Weibo 的 ecosystem root 应为 None')
        # 生态根：graph root = 自身，且 ecosystem root 也派生为自身
        for e in self.brands_doc['brands']:
            if e.get('entity_type') == 'ecosystem':
                self.assertEqual(resolve_graph_root(e['id'], self.ssot), e['id'],
                                 '生态根 %s graph root 应为自身' % e['id'])
                self.assertEqual(resolve_ecosystem_root(e['id'], self.ssot), e['id'],
                                 '生态根 %s ecosystem root 应为自身' % e['id'])

    # ---- §50：最终品牌树（SpaceXAI ├── X └── xAI └── Grok，2026-10-01 定稿） ----
    def test_spacexai_final_tree(self):
        """最终关系：X → SpaceXAI；xAI → SpaceXAI；Grok → xAI。"""
        self.assertEqual(self.ssot['X']['parent_brand'], 'SpaceXAI')
        self.assertEqual(self.ssot['xAI']['parent_brand'], 'SpaceXAI')
        self.assertEqual(self.ssot['Grok']['parent_brand'], 'xAI')

    def test_xai_is_canonical(self):
        """§6/§34：xAI 是当前 canonical 品牌，且不是 legacy 旧名。"""
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
        from legacy_map import legacy_ids
        self.assertIn('xAI', self.ssot, 'xAI 必须是当前 canonical SSOT 节点')
        self.assertEqual(self.ssot['xAI']['display_name'], 'xAI', '官方 casing 必须保留')
        self.assertNotIn('xAI', legacy_ids(), 'xAI 已是 canonical，不得列为 legacy ID')

    def test_xai_has_icon(self):
        """§6/§7：xAI 必须有独立图标（历史资产 R100 恢复，非伪造、非复制）。"""
        import hashlib
        repo = Path(__file__).resolve().parent.parent
        ip = self.ssot['xAI']['icon_path']
        self.assertEqual(ip, 'icons/SpaceXAI/xAI/xAI.png')
        p = repo / ip
        self.assertTrue(p.exists(), 'xAI 图标文件必须存在')
        # 与 SpaceXAI 共存时不得共用同一 SHA（CI 第 6 组），故这里只断言资产可追踪
        self.assertTrue(hashlib.sha256(p.read_bytes()).hexdigest())

    def test_xai_ancestor_chain(self):
        """xAI 直接父为正式 ecosystem SSOT SpaceXAI。"""
        self.assertEqual(self.ssot['xAI'].get('parent_brand'), 'SpaceXAI')
        self.assertEqual(resolve_graph_root('xAI', self.ssot), 'SpaceXAI')

    def test_grok_ancestor_chain(self):
        """Grok → xAI → SpaceXAI：直接父是 xAI，graph root 是 SpaceXAI。"""
        self.assertEqual(resolve_graph_root('Grok', self.ssot), 'SpaceXAI')
        from brand_relationships import _ancestor_set
        self.assertEqual(_ancestor_set('Grok', self.ssot), {'xAI', 'SpaceXAI'})

    def test_spacexai_is_top_level_ecosystem_category(self):
        """§8：SpaceXAI 生态分类存在；descendants = X/xAI/Grok = 3 ≥ 2。"""
        from brand_relationships import _descendants
        cats = {c['id']: c for c in self.cats_doc['categories']}
        self.assertIn('SpaceXAI', cats, 'SpaceXAI 生态分类必须存在')
        self.assertEqual(cats['SpaceXAI']['type'], 'ecosystem')
        ds = _descendants('SpaceXAI', self.ssot)
        self.assertEqual(ds, {'X', 'xAI', 'Grok'}, 'SpaceXAI canonical descendants 应为 3')
        self.assertGreaterEqual(len(ds), 2)
        # PR #10：正式 SSOT ecosystem 节点；根图标为官方 Brand Guidelines 资产。
        self.assertIn('SpaceXAI', self.ssot)
        self.assertEqual(self.ssot['SpaceXAI']['entity_type'], 'ecosystem')
        self.assertIs(self.ssot['SpaceXAI']['canonical'], True)
        self.assertEqual(self.ssot['SpaceXAI']['icon_status'], 'official')
        self.assertEqual(self.ssot['SpaceXAI']['icon_path'],
                         'icons/SpaceXAI/SpaceXAI/SpaceXAI.png')
        self.assertEqual(resolve_ecosystem_root('X', self.ssot), 'SpaceXAI')

    def test_spacex_not_in_brand_graph(self):
        """§35：SpaceX 只作 corporate context，不入图。"""
        self.assertNotIn('SpaceX', self.ssot)
        self.assertNotIn('SpaceX', self.brands_doc['parent_brands_without_icon'])

    def test_platform_relation_does_not_change_parent(self):
        """§38：平台可用性（Grok on X）不改变品牌父级，也不扩张 schema。"""
        self.assertEqual(self.ssot['Grok']['parent_brand'], 'xAI')
        for entry in self.brands_doc['brands']:
            self.assertNotIn('platform_brand', entry)
            self.assertNotIn('integration_brand', entry)
            self.assertNotIn('distribution_brand', entry)

    # ---- evidence 层：辅助审计，不是 SSOT / 不是阻塞条件（§14 §15 §52） ----
    def test_parent_edge_evidence_covers_every_live_edge(self):
        """每条 live parent_brand edge 都必须有独立的关系类型 + validity 记录（集合相等）。"""
        manifest = self._manifest()
        live = {(e['id'], e['parent_brand'])
                for e in self.brands_doc['brands'] if e.get('parent_brand')}
        audited = {(e['child'], e['parent']) for e in manifest['edges']}
        self.assertEqual(audited, live, 'evidence 清单必须与 live edge 集合完全一致')
        self.assertEqual(len(audited), len(live))
        self.assertEqual(set(manifest['relation_types']),
                         {'BRAND_HIERARCHY', 'CORPORATE_OWNERSHIP', 'DEVELOPER_PROVIDER',
                          'PLATFORM_INTEGRATION', 'UNKNOWN'})
        self.assertEqual(set(manifest['validity_values']),
                         {'CONFIRMED', 'OPEN_REVIEW', 'REJECTED'})
        for e in manifest['edges']:
            self.assertIn(e['relation_type'], manifest['relation_types'], e['child'])
            self.assertIn(e['parent_brand_validity'], manifest['validity_values'], e['child'])

    def test_evidence_layer_is_not_ssot_and_not_blocking(self):
        """§14/§15：evidence 层只是辅助审计，不得冒充 SSOT 或阻塞条件。"""
        manifest = self._manifest()
        self.assertEqual(manifest['role'], 'supporting_evidence_layer')
        self.assertIs(manifest['is_ssot'], False)
        self.assertIs(manifest['blocking'], False)
        audit = (Path(__file__).resolve().parent.parent
                 / 'docs' / 'references' / 'parent-edge-semantic-audit.md').read_text(encoding='utf-8')
        self.assertNotIn('BLOCKER A', audit, 'evidence 不再是 PR 阻塞条件')
        self.assertIn('supporting_evidence_layer', audit)

    def test_evidence_counts_are_recomputed_not_hardcoded(self):
        """§55：计数一律实时计算；不再把 115 等历史值写成当前事实。"""
        manifest = self._manifest()
        live = sum(1 for e in self.brands_doc['brands'] if e.get('parent_brand'))
        self.assertEqual(len(manifest['edges']), live)
        self.assertIn('0/%d' % live, manifest['self_reference_risk'])
        # 8 条品牌伞状措辞证据 → CONFIRMED；其余一律 OPEN_REVIEW（不得凭归属措辞升级）
        confirmed = {e['child'] for e in manifest['edges']
                     if e['parent_brand_validity'] == 'CONFIRMED'}
        for child in confirmed:
            self.assertEqual(next(e for e in manifest['edges'] if e['child'] == child)['relation_type'],
                             'BRAND_HIERARCHY', '%s 只允许 BRAND_HIERARCHY 判 CONFIRMED' % child)

    def test_corporate_ownership_alone_is_not_hierarchy_proof(self):
        """§16/§17：ownership-only 证据不得静默升级为 hierarchy。"""
        manifest = self._manifest()
        by_child = {e['child']: e for e in manifest['edges']}
        self.assertEqual(by_child['LinkedIn']['relation_type'], 'CORPORATE_OWNERSHIP')
        self.assertEqual(by_child['LinkedIn']['parent_brand_validity'], 'OPEN_REVIEW')

    def test_umbrella_word_alone_is_not_hierarchy_proof(self):
        """§70 Test A：「旗下」不得单独证明 BRAND_HIERARCHY。"""
        manifest = self._manifest()
        by_child = {e['child']: e for e in manifest['edges']}
        for child in ('F1TV', 'NowE', 'NBC', 'KakaoTalk', 'Snapchat', 'Viu', 'myTVSUPER'):
            self.assertEqual(by_child[child]['relation_type'], 'CORPORATE_OWNERSHIP',
                             '%s 只凭「旗下」不得判为品牌层级' % child)
            self.assertEqual(by_child[child]['parent_brand_validity'], 'OPEN_REVIEW')
        confirmed = {e['child'] for e in manifest['edges']
                     if e['parent_brand_validity'] == 'CONFIRMED'}
        self.assertTrue(confirmed.isdisjoint({'F1TV', 'NowE', 'NBC', 'KakaoTalk'}))

    def test_developer_or_platform_alone_is_not_parent(self):
        """§70 Test C/D：developer-only、platform-only 不得自动成为 parent。"""
        manifest = self._manifest()
        by_child = {e['child']: e for e in manifest['edges']}
        self.assertEqual(by_child['Kimi']['relation_type'], 'DEVELOPER_PROVIDER')
        self.assertEqual(by_child['Kimi']['parent_brand_validity'], 'OPEN_REVIEW')
        for e in manifest['edges']:
            if e['relation_type'] in ('DEVELOPER_PROVIDER', 'PLATFORM_INTEGRATION'):
                self.assertNotEqual(e['parent_brand_validity'], 'CONFIRMED',
                                    '%s 不得因 developer/platform 证据判 CONFIRMED' % e['child'])

    def test_brand_tree_edges_are_brand_hierarchy(self):
        """最终品牌树的三条边都是品牌层级，且逐条带证据/规则/来源结构。"""
        manifest = self._manifest()
        by_child = {e['child']: e for e in manifest['edges']}
        for child, parent in (('X', 'SpaceXAI'), ('xAI', 'SpaceXAI'), ('Grok', 'xAI')):
            e = by_child[child]
            self.assertEqual(e['parent'], parent)
            self.assertEqual(e['relation_type'], 'BRAND_HIERARCHY', child)
            self.assertEqual(e['parent_brand_validity'], 'CONFIRMED', child)
            self.assertTrue(e['evidence_quote'], child)
            self.assertTrue(e['decision_rule'].startswith('R'), child)
            self.assertIn('url_status', e['source'], child)
            self.assertTrue(e['rationale'], child)

    def test_generic_restatement_stays_unknown(self):
        """§70 Test E：泛化复述必须 UNKNOWN / OPEN_REVIEW。"""
        manifest = self._manifest()
        unknown = [e for e in manifest['edges'] if e['relation_type'] == 'UNKNOWN']
        self.assertTrue(unknown, '存在泛化复述 edge 时应为 UNKNOWN')
        for e in unknown:
            self.assertEqual(e['parent_brand_validity'], 'OPEN_REVIEW', e['child'])

    def test_source_urls_are_explicitly_unrecorded(self):
        """§74：不得伪造来源。当前无 URL 时必须显式标注 NOT_RECORDED。"""
        manifest = self._manifest()
        for e in manifest['edges']:
            self.assertIsNone(e['source']['url'], e['child'])
            self.assertEqual(e['source']['url_status'], 'NOT_RECORDED', e['child'])

    def test_parent_edge_evidence_is_deterministic(self):
        """manifest + audit 文档必须可由生成器确定性重放（0 diff）。"""
        import subprocess
        import sys
        repo = Path(__file__).resolve().parent.parent
        gen = repo / 'scripts' / 'gen-parent-edge-evidence.py'
        json_path = repo / 'config' / 'parent-edge-evidence.json'
        md_path = repo / 'docs' / 'references' / 'parent-edge-semantic-audit.md'
        before = (json_path.read_text(encoding='utf-8'), md_path.read_text(encoding='utf-8'))
        subprocess.run([sys.executable, str(gen)], cwd=str(repo), check=True,
                       capture_output=True)
        after = (json_path.read_text(encoding='utf-8'), md_path.read_text(encoding='utf-8'))
        self.assertEqual(before, after, 'parent edge evidence 生成器不幂等')


if __name__ == '__main__':
    unittest.main(verbosity=2)
