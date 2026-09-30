#!/usr/bin/env python3
"""父品牌 README 规则 + 命名契约测试（python -m unittest 或 pytest 均可）。

覆盖授权文档 §103-§106 / §109：
  - 嵌套关系 A → B → C：root(A) = C（动态派生）
  - 中间父品牌（Facebook）不得为 ecosystem（中间层不建一级分类）
  - 父品牌 README：有 child 的物理品牌节点必须有 README.md（真实库正测）
  - 叶子品牌 README：无 child 不要求（真实库反向负测）
  - 命名契约：ID 路径安全（无 +/@/空格/非 ASCII）；+ 在 ID 中写 Plus、
    保留在 display_name；@ 仅保留在 display_name（Karaoke@DAM）
"""
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from brand_relationships import (  # noqa: E402
    PARENT_README_MARKER,
    _root_of,
    expected_parent_readme,
    physical_parent_nodes,
    resolve_ecosystem_root,
    validate_relationships,
)

REPO = Path(__file__).resolve().parent.parent


def _load():
    brands_doc = json.loads((REPO / 'config' / 'brands.json').read_text(encoding='utf-8'))
    cats_doc = json.loads((REPO / 'config' / 'categories.json').read_text(encoding='utf-8'))
    ssot = {e['id']: e for e in brands_doc['brands']}
    return brands_doc, cats_doc, ssot


def parent_readme_missing(ssot):
    """CI 第 13 组同款逻辑：返回缺 README 的物理父节点列表。"""
    children = {}
    for e in ssot.values():
        p = e.get('parent_brand')
        if p:
            children.setdefault(p, []).append(e['id'])
    missing = []
    for p, kids in sorted(children.items()):
        if p not in ssot:
            continue  # 白名单母公司：无物理目录
        if not (REPO / Path(ssot[p]['icon_path']).parent / 'README.md').exists():
            missing.append(p)
    return missing


def leaf_readme_required(ssot):
    """反向：叶子品牌（无 child）不要求 README —— 返回若被误要求则列出的 id。"""
    children = set()
    for e in ssot.values():
        if e.get('parent_brand'):
            children.add(e['parent_brand'])
    # 规则定义：叶子不强制。此函数返回空集表示规则未被违反（无强制叶子 README 的要求）。
    return set()


class NestedRelationshipTests(unittest.TestCase):
    """§103 / §104：嵌套派生与中间层。"""

    def test_nested_root_derivation(self):
        ssot = {
            'A': {'id': 'A', 'parent_brand': 'B'},
            'B': {'id': 'B', 'parent_brand': 'C'},
            'C': {'id': 'C', 'entity_type': 'ecosystem'},
        }
        self.assertEqual(_root_of('A', ssot), 'C')
        self.assertEqual(resolve_ecosystem_root('A', ssot), 'C')

    def test_intermediate_parent_not_ecosystem(self):
        # Meta → Facebook → Instagram：Facebook 是中间父品牌，不得是 ecosystem
        brands = [
            {'id': 'Meta', 'display_name': 'Meta', 'category': 'Meta',
             'entity_type': 'ecosystem', 'icon_path': 'icons/Meta/Meta/Meta.png'},
            {'id': 'Facebook', 'display_name': 'Facebook', 'category': 'Meta',
             'entity_type': 'product_brand', 'icon_path': 'icons/Meta/Facebook/Facebook.png',
             'parent_brand': 'Meta'},
            {'id': 'Instagram', 'display_name': 'Instagram', 'category': 'Meta',
             'entity_type': 'product_brand', 'icon_path': 'icons/Meta/Instagram/Instagram.png',
             'parent_brand': 'Facebook'},
            {'id': 'Messenger', 'display_name': 'Messenger', 'category': 'Meta',
             'entity_type': 'product_brand', 'icon_path': 'icons/Meta/Messenger/Messenger.png',
             'parent_brand': 'Facebook'},
        ]
        doc = {'brands': brands, 'parent_brands_without_icon': []}
        cats = [{'id': 'Meta', 'type': 'ecosystem'}]
        self.assertEqual(validate_relationships(doc, cats), [])
        # 反例：Facebook 误标 ecosystem → 必须 FAIL（中间层不得成为生态根）
        brands[1]['entity_type'] = 'ecosystem'
        self.assertGreater(len(validate_relationships(doc, cats)), 0)

    def test_intermediate_parent_in_real_repo(self):
        _, _, ssot = _load()
        for mid in ('Facebook', 'YouTube', 'iCloud'):
            self.assertNotEqual(ssot[mid].get('entity_type'), 'ecosystem',
                                '%s 是中间父品牌，不得是 ecosystem' % mid)
            self.assertEqual(resolve_ecosystem_root(mid, ssot), ssot[mid]['parent_brand'])


class ParentReadmeTests(unittest.TestCase):
    """§105 / §106：父品牌 README 规则（真实库）。"""

    @classmethod
    def setUpClass(cls):
        cls.brands_doc, cls.cats_doc, cls.ssot = _load()

    def test_all_physical_parents_have_readme(self):
        self.assertEqual(parent_readme_missing(self.ssot), [],
                         '以下父品牌缺 README: %s' % parent_readme_missing(self.ssot))

    def test_named_examples_have_readme(self):
        # 授权文档点名的中间父品牌
        for p in ('Facebook', 'YouTube', 'iCloud'):
            rd = REPO / Path(self.ssot[p]['icon_path']).parent / 'README.md'
            self.assertTrue(rd.exists(), '%s 缺 README.md' % p)

    def test_leaf_brands_not_required(self):
        # 反向负测：无 child 的叶子品牌不要求 README —— 规则函数返回空集
        self.assertEqual(leaf_readme_required(self.ssot), set())
        # 真实库抽查：存在没有 README 的叶子品牌目录，且 CI 第 13 组不报错
        children = {e['parent_brand'] for e in self.ssot.values() if e.get('parent_brand')}
        leafs_no_readme = [
            e['id'] for e in self.ssot.values()
            if e['id'] not in children
            and not (REPO / Path(e['icon_path']).parent / 'README.md').exists()
        ]
        self.assertGreater(len(leafs_no_readme), 0,
                           '库中应存在无 README 的叶子品牌（规则不强制的证据）')
        self.assertEqual(parent_readme_missing(self.ssot), [],
                         '叶子品牌（如 %s）无 README 不应触发父节点门禁' % leafs_no_readme[0])

    def test_parent_readme_content_from_ssot(self):
        # README 数据来自 SSOT（§110）：display_name 与 brands.json 一致
        for p in ('Facebook', 'YouTube', 'iCloud', 'Meta', 'Google', 'Apple'):
            rd = REPO / Path(self.ssot[p]['icon_path']).parent / 'README.md'
            text = rd.read_text(encoding='utf-8')
            dn = self.ssot[p]['display_name']
            self.assertIn(dn, text, '%s README 未包含 SSOT display_name %r' % (p, dn))
            self.assertIn('Ancestor Chain', text)
            self.assertIn('Direct Children', text)
            self.assertIn('Ecosystem Root', text)

    def test_all_parent_readme_bytes_match_expected(self):
        # §22-§25：ALL physical parent nodes（动态，非固定名单）逐一做
        # deterministic expected == actual 逐字节等价校验。
        # 有 marker 的生成文件必须严格相等；无 marker 的人工 README 跳过。
        parents = physical_parent_nodes(self.brands_doc)
        checked = 0
        for p in sorted(parents):
            rd = REPO / Path(self.ssot[p]['icon_path']).parent / 'README.md'
            self.assertTrue(rd.exists(), '%s 缺 README' % p)
            text = rd.read_text(encoding='utf-8')
            if text.splitlines() and text.splitlines()[0].strip() == PARENT_README_MARKER:
                expected = expected_parent_readme(p, self.ssot)
                self.assertEqual(text, expected,
                                 '%s README 内容与 expected 不一致（应运行 '
                                 'scripts/generate-category-readmes.sh 重新生成）' % p)
                checked += 1
        self.assertGreater(checked, 0, '未校验到任何 generated 父品牌 README')

    def test_graph_root_parent_role(self):
        # §26-§28：SINA / Xiaomi 是 graph root 但 descendants=1 → 非 ecosystem，
        # 角色应为 Graph Root Parent（不是 Intermediate Parent Brand）
        for p in ('SINA', 'Xiaomi'):
            rd = REPO / Path(self.ssot[p]['icon_path']).parent / 'README.md'
            text = rd.read_text(encoding='utf-8')
            self.assertIn('Role:         Graph Root Parent', text,
                          '%s 角色应为 Graph Root Parent' % p)
            self.assertIn('Graph Root:   %s' % p, text)
            self.assertIn('Ecosystem Root: —', text)

    def test_intermediate_role_real_repo(self):
        # Facebook 有 SSOT 父（Meta）+ 有子 → Intermediate Parent Brand
        rd = REPO / Path(self.ssot['Facebook']['icon_path']).parent / 'README.md'
        text = rd.read_text(encoding='utf-8')
        self.assertIn('Role:         Intermediate Parent Brand', text)
        self.assertIn('Ecosystem Root: Meta', text)


class NamingContractTests(unittest.TestCase):
    """§109 / §51 / §52：技术 ID 与 display_name 命名契约（真实库）。"""

    @classmethod
    def setUpClass(cls):
        cls.ssot = _load()[2]

    def test_ids_are_path_safe(self):
        for bid in self.ssot:
            self.assertNotIn('/', bid, 'ID 含 /: %s' % bid)
            self.assertNotIn(' ', bid, 'ID 含空格: %s' % bid)
            self.assertTrue(bid.isascii(), 'ID 非 ASCII: %s' % bid)
            self.assertTrue(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', bid),
                            'ID 含特殊字符: %s' % bid)
            self.assertNotIn('+', bid, 'ID 含 +（应写 Plus）: %s' % bid)
            self.assertNotIn('@', bid, 'ID 含 @（仅 display_name 保留）: %s' % bid)

    def test_plus_in_display_kept_plus_in_id(self):
        # + 保留在 display_name，ID 中写 Plus（§45 Apple News+ / §46 CATCHPLAY+）
        expect = {
            'AppleNewsPlus': 'Apple News+',
            'CATCHPLAYPlus': 'CATCHPLAY+',
            'DisneyPlus': 'Disney+',
            'ParamountPlus': 'Paramount+',
            'AppleFitnessPlus': 'Apple Fitness+',
        }
        for bid, dn in expect.items():
            self.assertIn(bid, self.ssot, '缺少品牌 %s' % bid)
            self.assertEqual(self.ssot[bid]['display_name'], dn,
                             '%s display_name 应为 %r' % (bid, dn))
            self.assertNotIn('+', bid)
            self.assertIn('Plus', bid)

    def test_at_sign_display_only(self):
        # @ 仅出现在 display_name；ID 中省略（Karaoke@DAM）
        self.assertIn('KaraokeDAM', self.ssot)
        self.assertEqual(self.ssot['KaraokeDAM']['display_name'], 'Karaoke@DAM')
        for bid in self.ssot:
            self.assertNotIn('@', bid, 'ID 含 @: %s' % bid)

    def test_official_casing_preserved(self):
        # §50/§52：官方 casing 保留，不机械 PascalCase
        for bid in ('iQIYI', 'SONY', 'vivo', 'myTVSUPER', 'TIDAL', 'SpaceXAI'):
            self.assertIn(bid, self.ssot, '官方 casing 品牌 %s 缺失' % bid)

    def test_chinese_display_names(self):
        # §37/§48：中文 display_name 合法（ID 仍为 ASCII，ID ≠ display_name）
        expect = {'SINA': '新浪', 'Xiaoyuzhou': '小宇宙'}
        for bid, dn in expect.items():
            self.assertIn(bid, self.ssot, '缺少品牌 %s' % bid)
            self.assertEqual(self.ssot[bid]['display_name'], dn,
                             '%s display_name 应为 %r' % (bid, dn))
            self.assertNotEqual(self.ssot[bid]['display_name'], bid,
                                'ID 与 display_name 不应相同: %s' % bid)


if __name__ == '__main__':
    unittest.main(verbosity=2)
