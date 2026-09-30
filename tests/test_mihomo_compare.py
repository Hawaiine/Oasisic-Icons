#!/usr/bin/env python3
"""Oasisic ↔ mihomo-rules 关系对照语义测试（§24 / §99 / §100）。

覆盖状态：MATCH / OASISIC_MORE_PRECISE / MIHOMO_MORE_PRECISE / STALE /
NOT_CONSUMED / MISSING / AMBIGUOUS，以及 §68 的 OASISIC_ONLY。

§99 兼容性测试：Oasisic 表达更深祖先链（YouTubeMusic → YouTube → Google）而
mihomo 只给直接父（YouTubeMusic → YouTube）时必须判 **MATCH**，不得判 mismatch。
§100 stale 测试：直接父冲突（Grok: Oasisic→xAI vs mihomo→X）必须标记为需人工复核
（AMBIGUOUS / STALE），且对照函数**绝不修改**输入（尤其不得改 mihomo 侧）。
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from mihomo_compare import compare, oasisic_only  # noqa: E402


def ssot(*pairs):
    """pairs: (id, parent|None) -> {id: entry}。"""
    out = {}
    for bid, par in pairs:
        e = {'id': bid, 'display_name': bid}
        if par:
            e['parent_brand'] = par
        out[bid] = e
    return out


class MihomoCompareTests(unittest.TestCase):
    # ---- §99：语义层级比较，深链 vs 直接父 = 兼容 ----
    def test_deeper_oasisic_chain_is_match(self):
        oas = ssot(('Google', None), ('YouTube', 'Google'), ('YouTubeMusic', 'YouTube'))
        rows = compare(oas, {'YouTubeMusic': 'YouTube'})
        self.assertEqual(rows[0]['status'], 'MATCH')
        self.assertEqual(rows[0]['oasisic_root'], 'Google')

    def test_equal_direct_parent_is_match(self):
        oas = ssot(('Apple', None), ('iCloud', 'Apple'), ('iCloudPrivateRelay', 'iCloud'))
        rows = compare(oas, {'iCloudPrivateRelay': 'iCloud'})
        self.assertEqual(rows[0]['status'], 'MATCH')

    # ---- 精度差异 ----
    def test_oasisic_more_precise(self):
        # mihomo: Instagram -> Meta（直接跳到生态根）；Oasisic 更细：Instagram -> Facebook -> Meta
        oas = ssot(('Meta', None), ('Facebook', 'Meta'), ('Instagram', 'Facebook'))
        rows = compare(oas, {'Instagram': 'Meta'})
        self.assertEqual(rows[0]['status'], 'OASISIC_MORE_PRECISE')

    def test_mihomo_more_precise(self):
        # mihomo 侧自身有更细链：A -> B -> C；Oasisic 直接给 A -> C
        oas = ssot(('C', None), ('A', 'C'))
        rows = compare(oas, {'A': 'B', 'B': 'C'})
        row_a = [r for r in rows if r['mihomo_id'] == 'A'][0]
        self.assertEqual(row_a['status'], 'MIHOMO_MORE_PRECISE')

    # ---- §100：冲突 → 需人工复核，绝不自动修改 ----
    def test_conflicting_parent_requires_review(self):
        # Grok 情形：Oasisic Grok -> xAI；mihomo Grok -> X（X 为 xAI 的子品牌，非父）
        oas = ssot(('xAI', None), ('X', 'xAI'), ('Grok', 'xAI'))
        rows = compare(oas, {'Grok': 'X'})
        self.assertEqual(rows[0]['status'], 'AMBIGUOUS')
        self.assertIn(rows[0]['status'], ('AMBIGUOUS', 'STALE'))

    def test_stale_via_override(self):
        oas = ssot(('JioStar', None))
        oas['JioHotstar'] = {'id': 'JioHotstar', 'parent_brand': 'JioStar'}
        rows = compare(oas, {'Hotstar': 'Disney'}, aliases={'Hotstar': 'JioHotstar'},
                       overrides={'Hotstar': 'STALE'})
        self.assertEqual(rows[0]['status'], 'STALE')
        self.assertEqual(rows[0]['oasisic_parent'], 'JioStar')

    def test_compare_never_mutates_inputs(self):
        oas = ssot(('xAI', None), ('Grok', 'xAI'))
        mmap = {'Grok': 'X'}
        oas_snapshot = json.dumps(oas, sort_keys=True)
        mmap_snapshot = json.dumps(mmap, sort_keys=True)
        compare(oas, mmap)
        self.assertEqual(json.dumps(oas, sort_keys=True), oas_snapshot)
        self.assertEqual(json.dumps(mmap, sort_keys=True), mmap_snapshot)

    # ---- 集合差异 ----
    def test_not_consumed_mihomo_only(self):
        oas = ssot(('Apple', None))
        rows = compare(oas, {'AppleWatch': 'Apple'})
        self.assertEqual(rows[0]['status'], 'NOT_CONSUMED')
        self.assertIsNone(rows[0]['oasisic_id'])

    def test_missing_when_oasisic_has_no_parent(self):
        oas = ssot(('JioHotstar', None))
        rows = compare(oas, {'JioHotstar': 'JioStar'})
        self.assertEqual(rows[0]['status'], 'MISSING')

    def test_alias_resolves_renamed_brand(self):
        oas = ssot(('Apple', None), ('AppleNewsPlus', 'Apple'))
        rows = compare(oas, {'AppleNews': 'Apple'}, aliases={'AppleNews': 'AppleNewsPlus'})
        self.assertEqual(rows[0]['status'], 'MATCH')
        self.assertEqual(rows[0]['oasisic_id'], 'AppleNewsPlus')

    def test_oasisic_only_not_an_error(self):
        oas = ssot(('Google', None), ('YouTube', 'Google'), ('YouTubeMusic', 'YouTube'))
        only = oasisic_only(oas, {'YouTubeMusic': 'YouTube'})
        self.assertEqual(only, ['YouTube'])
        self.assertNotIn('Google', only)  # 无 parent，不算 OASISIC_ONLY


class RealRepoCompatibilityTests(unittest.TestCase):
    """对真实 brands.json 断言关系模型不漂移（§89 §91 §127）。"""

    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads((ROOT / 'config' / 'brands.json').read_text(encoding='utf-8'))
        cls.ssot = {b['id']: b for b in cls.doc['brands']}

    def test_direct_parent_semantics_preserved(self):
        # §91：直接父必须保留，不得被顶层生态覆盖
        expect = {
            'Instagram': 'Facebook', 'Messenger': 'Facebook',
            'WhatsApp': 'Facebook', 'Threads': 'Facebook',
            'YouTubeMusic': 'YouTube', 'iCloudPrivateRelay': 'iCloud',
        }
        for bid, par in expect.items():
            self.assertEqual(self.ssot[bid].get('parent_brand'), par, bid)

    def test_ancestor_chain_resolves_to_ecosystem_root(self):
        # §89/§127：祖先链 → 生态根
        expect_root = {
            'Instagram': 'Meta', 'Facebook': 'Meta',
            'YouTubeMusic': 'Google', 'iCloudPrivateRelay': 'Apple',
        }
        for bid, root in expect_root.items():
            cur, last = bid, bid
            while True:
                p = self.ssot.get(cur, {}).get('parent_brand')
                if not p:
                    break
                last = p
                cur = p
            self.assertEqual(last, root, bid)

    def test_no_ecosystem_root_has_parent(self):
        # §87：生态根必须是关系图顶端
        for b in self.doc['brands']:
            if b.get('entity_type') == 'ecosystem':
                self.assertFalse(b.get('parent_brand'), b['id'])


if __name__ == '__main__':
    unittest.main()
