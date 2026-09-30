#!/usr/bin/env python3
"""物理层级 / 路径派生 / 逻辑生态根 测试（§5/§6/§9-§11/§13-§16/§20/§21/§44/§48）。

覆盖：
  - 最终品牌树三个直接父关系（Grok→xAI、X→SpaceXAI、xAI→SpaceXAI）；
  - SpaceXAI 作为**逻辑生态根**（无 SSOT 条目 + type=ecosystem 分类）；
  - 祖先链（Grok / xAI）；
  - 多层物理路径：同类中间父品牌必须嵌套，graph root 直系子品牌保持平铺；
  - cross-category 父品牌不得被机械迁移；
  - 白名单母公司（无图标）不得制造伪目录；
  - 生态分类 README 的关系树必须由 resolver 渲染（禁止平铺树）。
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'scripts'))

from brand_relationships import (  # noqa: E402
    ECO_TREE_MARKER,
    _ancestor_set,
    ecosystem_category_ids,
    expected_ecosystem_tree,
    expected_icon_path,
    resolve_ecosystem_root,
    resolve_graph_root,
    validate_physical_paths,
)

BRANDS = json.loads((REPO / 'config/brands.json').read_text(encoding='utf-8'))
CATS = json.loads((REPO / 'config/categories.json').read_text(encoding='utf-8'))['categories']
SSOT = {b['id']: b for b in BRANDS['brands']}
ALIASES = set(BRANDS['parent_brands_without_icon'])
ECO_CATS = ecosystem_category_ids(CATS)


class FinalTreeTests(unittest.TestCase):
    def test_grok_parent_is_xai(self):
        self.assertEqual(SSOT['Grok']['parent_brand'], 'xAI')

    def test_x_parent_is_spacexai(self):
        self.assertEqual(SSOT['X']['parent_brand'], 'SpaceXAI')

    def test_xai_parent_is_spacexai(self):
        self.assertEqual(SSOT['xAI']['parent_brand'], 'SpaceXAI')

    def test_grok_ancestor_chain(self):
        self.assertEqual(_ancestor_set('Grok', SSOT), {'xAI', 'SpaceXAI'})
        self.assertEqual(resolve_graph_root('Grok', SSOT), 'SpaceXAI')

    def test_xai_ancestor_chain(self):
        self.assertEqual(_ancestor_set('xAI', SSOT), {'SpaceXAI'})
        self.assertEqual(resolve_graph_root('xAI', SSOT), 'SpaceXAI')

    def test_spacex_is_not_in_graph(self):
        self.assertNotIn('SpaceX', SSOT)


class LogicalEcosystemTests(unittest.TestCase):
    def test_space_xai_is_logical_ecosystem(self):
        # §13/§14/§26：SpaceXAI 无 brands.json 条目（官方标志待补），但
        # categories.json 有 type=ecosystem 分类 → 仍是逻辑生态根。
        self.assertNotIn('SpaceXAI', SSOT)
        self.assertIn('SpaceXAI', ECO_CATS)
        self.assertIn('SpaceXAI', ALIASES)
        for bid in ('xAI', 'X', 'Grok'):
            self.assertEqual(resolve_ecosystem_root(bid, SSOT, ECO_CATS), 'SpaceXAI',
                             '%s 的逻辑生态根必须是 SpaceXAI' % bid)

    def test_non_ecosystem_root_has_no_ecosystem(self):
        # 反向：graph root 非生态（Xiaomi/Mijia）→ ecosystem root 仍为 None
        self.assertIsNone(resolve_ecosystem_root('Mijia', SSOT, ECO_CATS))

    def test_backward_compatible_signature(self):
        # 不传 eco_cat_ids 时保持严格语义（仅 entity_type=ecosystem 才算）
        self.assertIsNone(resolve_ecosystem_root('xAI', SSOT))


class PhysicalPathTests(unittest.TestCase):
    def test_physical_path_matches_relationship(self):
        # §21：icon_path 必须由统一解析器推出（全库）
        for bid, e in sorted(SSOT.items()):
            self.assertEqual(e['icon_path'], expected_icon_path(bid, SSOT), bid)

    def test_intermediate_parent_nesting(self):
        # §5/§7：同类中间父品牌下的子品牌必须嵌套
        expected = {
            'Instagram': 'icons/Meta/Facebook/Instagram/Instagram.png',
            'Messenger': 'icons/Meta/Facebook/Messenger/Messenger.png',
            'WhatsApp': 'icons/Meta/Facebook/WhatsApp/WhatsApp.png',
            'Threads': 'icons/Meta/Facebook/Threads/Threads.png',
            'YouTubeMusic': 'icons/Google/YouTube/YouTubeMusic/YouTubeMusic.png',
            'iCloudPrivateRelay': 'icons/Apple/iCloud/iCloudPrivateRelay/iCloudPrivateRelay.png',
            'Grok': 'icons/SpaceXAI/xAI/Grok/Grok.png',
        }
        for bid, path in expected.items():
            self.assertEqual(SSOT[bid]['icon_path'], path, bid)
            self.assertTrue((REPO / path).exists(), path)

    def test_deep_parent_physical_path(self):
        # 深层品牌必须在父品牌目录之下（物理层级可见）
        for child, parent in (('Grok', 'xAI'), ('Instagram', 'Facebook'),
                              ('YouTubeMusic', 'YouTube'),
                              ('iCloudPrivateRelay', 'iCloud')):
            cdir = (REPO / SSOT[child]['icon_path']).parent
            pdir = (REPO / SSOT[parent]['icon_path']).parent
            self.assertIn(pdir, cdir.parents, '%s 应位于 %s 之下' % (child, parent))

    def test_direct_children_of_graph_root_stay_flat(self):
        # §6：graph root 的直系子品牌保持 icons/<category>/<id>/<id>.png
        for bid in ('AppleMusic', 'AppleTV', 'AWS', 'AliCloud', 'Weibo', 'myTVSUPER',
                    'X', 'SINA' if 'SINA' in SSOT else 'Apple'):
            e = SSOT.get(bid)
            if not e:
                continue
            parts = e['icon_path'].split('/')
            self.assertEqual(len(parts), 4, '%s 不应被嵌套: %s' % (bid, e['icon_path']))
            self.assertEqual(parts[:2], ['icons', e['category']], bid)

    def test_cross_category_parent(self):
        # §10：cross-category 父品牌不得被机械迁移（Mijia → Xiaomi）
        self.assertEqual(SSOT['Mijia']['category'], 'Home')
        self.assertEqual(SSOT['Xiaomi']['category'], 'Hardware')
        self.assertEqual(SSOT['Mijia']['icon_path'], 'icons/Home/Mijia/Mijia.png')
        self.assertNotIn('Hardware', SSOT['Mijia']['icon_path'].split('/'))

    def test_parent_without_icon(self):
        # §11：白名单母公司无目录 → 子品牌保持平铺，且不得制造伪目录
        for child, parent in (('Kimi', 'MoonshotAI'), ('GLM', 'ZhipuAI'),
                              ('Steam', 'Valve'), ('Tidal' if 'Tidal' in SSOT else 'TIDAL', 'Block')):
            e = SSOT.get(child)
            if not e:
                continue
            self.assertEqual(e['parent_brand'], parent)
            self.assertEqual(e['icon_path'],
                             'icons/%s/%s/%s.png' % (e['category'], child, child))
            self.assertFalse((REPO / 'icons' / e['category'] / parent).exists(),
                             '不得为无图标母公司 %s 制造目录' % parent)

    def test_validate_physical_paths_clean_on_repo(self):
        self.assertEqual(validate_physical_paths(BRANDS, CATS, REPO), [])

    def test_never_nest_grandchild_under_wrong_parent(self):
        # §17 反例：Grok 不得留在 icons/SpaceXAI/Grok/
        self.assertFalse((REPO / 'icons/SpaceXAI/Grok').exists())
        for stale in ('icons/Meta/Instagram', 'icons/Meta/Messenger', 'icons/Meta/WhatsApp',
                      'icons/Meta/Threads', 'icons/Google/YouTubeMusic',
                      'icons/Apple/iCloudPrivateRelay'):
            self.assertFalse((REPO / stale).exists(), '旧平铺路径仍存在: %s' % stale)


class ResolverGeneralizationTests(unittest.TestCase):
    """合成用例：规则必须对任意深链成立（不得只针对已知 7 个品牌，§37）。"""

    @staticmethod
    def _doc(entries):
        return {'brands': entries, 'parent_brands_without_icon': []}

    def test_three_level_chain(self):
        doc = self._doc([
            {'id': 'Root', 'category': 'Root', 'parent_brand': None},
            {'id': 'Mid', 'category': 'Root', 'parent_brand': 'Root'},
            {'id': 'Leaf', 'category': 'Root', 'parent_brand': 'Mid'},
        ])
        ssot = {b['id']: b for b in doc['brands']}
        self.assertEqual(expected_icon_path('Mid', ssot), 'icons/Root/Mid/Mid.png')
        self.assertEqual(expected_icon_path('Leaf', ssot), 'icons/Root/Mid/Leaf/Leaf.png')

    def test_four_level_chain(self):
        doc = self._doc([
            {'id': 'R', 'category': 'R', 'parent_brand': None},
            {'id': 'A', 'category': 'R', 'parent_brand': 'R'},
            {'id': 'B', 'category': 'R', 'parent_brand': 'A'},
            {'id': 'C', 'category': 'R', 'parent_brand': 'B'},
        ])
        ssot = {b['id']: b for b in doc['brands']}
        self.assertEqual(expected_icon_path('C', ssot), 'icons/R/A/B/C/C.png')

    def test_cross_category_chain_is_not_nested(self):
        doc = self._doc([
            {'id': 'OtherRoot', 'category': 'Other', 'parent_brand': None},
            {'id': 'Mid', 'category': 'Other', 'parent_brand': 'OtherRoot'},
            {'id': 'Leaf', 'category': 'Mine', 'parent_brand': 'Mid'},
        ])
        ssot = {b['id']: b for b in doc['brands']}
        self.assertEqual(expected_icon_path('Leaf', ssot), 'icons/Mine/Leaf/Leaf.png')

    def test_whitelisted_parent_chain_is_not_nested(self):
        doc = self._doc([
            {'id': 'Root', 'category': 'C', 'parent_brand': None},
            {'id': 'Mid', 'category': 'C', 'parent_brand': 'Root'},
            {'id': 'Leaf', 'category': 'C', 'parent_brand': 'Ghost'},   # Ghost 无条目
        ])
        ssot = {b['id']: b for b in doc['brands']}
        self.assertEqual(expected_icon_path('Leaf', ssot), 'icons/C/Leaf/Leaf.png')

    def test_validator_rejects_un_nested_deep_child(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for rel in ('icons/R/R/R.png', 'icons/R/A/A.png', 'icons/R/Leaf/Leaf.png'):
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b'\x89PNG\r\n\x1a\n')
            doc = self._doc([
                {'id': 'R', 'category': 'R', 'parent_brand': None, 'icon_path': 'icons/R/R/R.png'},
                {'id': 'A', 'category': 'R', 'parent_brand': 'R', 'icon_path': 'icons/R/A/A.png'},
                {'id': 'Leaf', 'category': 'R', 'parent_brand': 'A',
                 'icon_path': 'icons/R/Leaf/Leaf.png'},
            ])
            errs = validate_physical_paths(doc, [{'id': 'R'}], root)
            self.assertTrue(any('未物理嵌套' in e or '路径规则不符' in e for e in errs), errs)

    def test_validator_flags_ghost_dir_for_whitelisted_parent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for rel in ('icons/C/Kid/Kid.png', 'icons/C/Ghost/README.md'):
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b'x')
            doc = {'brands': [{'id': 'Kid', 'category': 'C', 'parent_brand': 'Ghost',
                               'icon_path': 'icons/C/Kid/Kid.png'}],
                   'parent_brands_without_icon': ['Ghost']}
            errs = validate_physical_paths(doc, [{'id': 'C'}], root)
            self.assertTrue(any('伪目录' in e for e in errs), errs)


class EcosystemTreeTests(unittest.TestCase):
    def test_ecosystem_tree_is_nested_not_flat(self):
        # §48：SpaceXAI ├── X └── xAI └── Grok
        tree = expected_ecosystem_tree('SpaceXAI', SSOT)
        self.assertIn('SpaceXAI', tree)
        self.assertIn('├── X', tree)
        self.assertIn('└── xAI', tree)
        self.assertIn('└── Grok', tree)
        self.assertNotIn('├── Grok', tree, '严禁把 Grok 平铺成 SpaceXAI 的一级子品牌')

    def test_category_readme_contains_resolver_tree(self):
        text = (REPO / 'icons' / 'SpaceXAI' / 'README.md').read_text(encoding='utf-8')
        self.assertIn(ECO_TREE_MARKER, text)
        self.assertIn(expected_ecosystem_tree('SpaceXAI', SSOT), text)


if __name__ == '__main__':
    unittest.main()
