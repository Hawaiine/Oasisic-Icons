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

    def test_spacexai_final_state(self):
        """§9-§41：Grok → SpaceXAI；X 独立；SpaceXAI 非生态；SpaceX 不入图。"""
        # Grok：SpaceXAI 开发的产品（官方 Terms 证据）
        self.assertEqual(self.ssot['Grok']['parent_brand'], 'SpaceXAI')
        self.assertEqual(resolve_graph_root('Grok', self.ssot), 'SpaceXAI')
        # SpaceXAI：公司品牌，descendants=1 < 2 → 非生态
        self.assertEqual(self.ssot['SpaceXAI']['entity_type'], 'product_brand')
        self.assertIsNone(resolve_ecosystem_root('Grok', self.ssot),
                          'SpaceXAI descendants=1，不构成生态')
        # X：独立平台品牌（官方 Privacy Policy：SpaceXAI 与 X Corp. 分离）
        self.assertNotIn('parent_brand', self.ssot['X'],
                         'X 不应有 parent_brand（不以 corporate ownership 推导）')
        self.assertEqual(resolve_graph_root('X', self.ssot), 'X')
        self.assertIsNone(resolve_ecosystem_root('X', self.ssot))
        # SpaceX：corporate owner only，不进入 brand graph
        self.assertNotIn('SpaceX', self.ssot)
        # xAI 旧 ID 不得残留
        self.assertNotIn('xAI', self.ssot)

    def test_platform_integration_is_not_parent_brand(self):
        """Grok 在 X 上可用是 platform integration，不改变其品牌父级。"""
        self.assertEqual(self.ssot['Grok']['parent_brand'], 'SpaceXAI')
        for entry in self.brands_doc['brands']:
            self.assertNotIn('platform_brand', entry)
            self.assertNotIn('integration_brand', entry)
            self.assertNotIn('distribution_brand', entry)

    def test_parent_edge_evidence_covers_every_live_edge(self):
        """每条 live parent_brand edge 都必须有独立的语义证据分类。"""
        import json
        repo = Path(__file__).resolve().parent.parent
        manifest = json.loads(
            (repo / 'config' / 'parent-edge-evidence.json').read_text(encoding='utf-8'))
        live = {
            (e['id'], e['parent_brand'])
            for e in self.brands_doc['brands'] if e.get('parent_brand')
        }
        audited = {(e['child'], e['parent']) for e in manifest['edges']}
        self.assertEqual(audited, live)
        self.assertEqual(len(audited), 115)
        allowed = set(manifest['allowed_classifications'])
        self.assertTrue(all(e['classification'] in allowed for e in manifest['edges']))

    def test_corporate_ownership_alone_is_not_hierarchy_proof(self):
        """ownership-only evidence must remain reviewable, not silently confirmed."""
        import json
        repo = Path(__file__).resolve().parent.parent
        manifest = json.loads(
            (repo / 'config' / 'parent-edge-evidence.json').read_text(encoding='utf-8'))
        by_child = {e['child']: e for e in manifest['edges']}
        self.assertEqual(by_child['GitHub']['classification'], 'CORPORATE_OWNERSHIP_ONLY')
        self.assertEqual(by_child['GitHub']['review_status'], 'OPEN_REVIEW')

    def test_parent_edge_audit_counts_and_grok_boundary(self):
        """固定当前审计口径，避免 ownership 证据静默升级为 hierarchy。"""
        import json
        from collections import Counter
        repo = Path(__file__).resolve().parent.parent
        manifest = json.loads(
            (repo / 'config' / 'parent-edge-evidence.json').read_text(encoding='utf-8'))
        counts = Counter(e['classification'] for e in manifest['edges'])
        self.assertEqual(counts, Counter({
            'AMBIGUOUS': 58,
            'CORPORATE_OWNERSHIP_ONLY': 41,
            'DEVELOPER_PROVIDER_ONLY': 8,
            'BRAND_HIERARCHY_CONFIRMED': 8,
        }))
        grok = next(e for e in manifest['edges'] if e['child'] == 'Grok')
        self.assertEqual(grok['parent'], 'SpaceXAI')
        self.assertEqual(grok['classification'], 'DEVELOPER_PROVIDER_ONLY')
        self.assertEqual(grok['review_status'], 'OPEN_REVIEW')


if __name__ == '__main__':
    unittest.main(verbosity=2)
