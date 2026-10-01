#!/usr/bin/env python3
"""SSOT / 派生文件 / 关系引擎 hardening 测试（§11 Final Closure）。

覆盖五类防线：
  1. JSON 重复 key 检测（brands.json / categories.json / surge-icon.json）——
     标准 json.load 静默丢弃重复 key，必须用 object_pairs_hook 显式捕获。
  2. brands.json 身份冲突：重复 id / 重复 display_name（精确匹配）。
  3. surge-icon.json 重复 icon key（与 brands.json id 集合一致性由 CI 组 8 负责，
     这里只查重复）。
  4. glossary 重复行：同一 Technical ID 在 brand-glossary.md 出现 > 1 次。
  5. 关系引擎深链/环终止：无 depth 硬编码，200 层链 + 大环均正常收敛。
"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from brand_relationships import (  # noqa: E402
    _ancestor_set,
    _root_of,
)


def load_no_dup_keys(path):
    """加载 JSON 并断言无重复 object key。返回 (data, dup_keys)。"""
    dups = []

    def hook(pairs):
        seen = set()
        for k, _ in pairs:
            if k in seen:
                dups.append(k)
            seen.add(k)
        return dict(pairs)

    data = json.loads(Path(path).read_text(), object_pairs_hook=hook)
    return data, dups


class JsonDupKeyTests(unittest.TestCase):
    def test_brands_json_no_duplicate_keys(self):
        _, dups = load_no_dup_keys(ROOT / 'config' / 'brands.json')
        self.assertEqual(dups, [], 'brands.json 重复 key: %s' % dups)

    def test_categories_json_no_duplicate_keys(self):
        _, dups = load_no_dup_keys(ROOT / 'config' / 'categories.json')
        self.assertEqual(dups, [], 'categories.json 重复 key: %s' % dups)

    def test_surge_icon_json_no_duplicate_keys(self):
        _, dups = load_no_dup_keys(ROOT / 'config' / 'surge-icon.json')
        self.assertEqual(dups, [], 'surge-icon.json 重复 key: %s' % dups)


class IdentityCollisionTests(unittest.TestCase):
    def setUp(self):
        data, _ = load_no_dup_keys(ROOT / 'config' / 'brands.json')
        self.brands = data['brands']

    def test_no_duplicate_brand_ids(self):
        ids = [b['id'] for b in self.brands]
        dups = sorted({i for i in ids if ids.count(i) > 1})
        self.assertEqual(dups, [], '重复品牌 id: %s' % dups)

    def test_no_duplicate_display_names(self):
        dnames = [b['display_name'] for b in self.brands]
        dups = sorted({d for d in dnames if dnames.count(d) > 1})
        self.assertEqual(dups, [], '重复 display_name: %s' % dups)

    def test_no_duplicate_icon_paths(self):
        paths = [b['icon_path'] for b in self.brands if b.get('icon_path')]
        dups = sorted({p for p in paths if paths.count(p) > 1})
        self.assertEqual(dups, [], '重复 icon_path: %s' % dups)


class SurgeDupKeyTests(unittest.TestCase):
    def test_surge_icons_no_duplicate_keys(self):
        data, dups = load_no_dup_keys(ROOT / 'config' / 'surge-icon.json')
        self.assertEqual(dups, [], 'surge-icon.json 重复 key: %s' % dups)
        icons = data.get('icons', [])
        # icons 是 array（每项 {name, category, url}）——查 name 值级重复
        self.assertIsInstance(icons, list)
        self.assertGreater(len(icons), 200, 'icons 表异常为空')
        from collections import Counter
        names = [i['name'] for i in icons]
        dup_names = sorted({n for n, c in Counter(names).items() if c > 1})
        self.assertEqual(dup_names, [], '重复 surge icon name: %s' % dup_names)


class GlossaryDupRowTests(unittest.TestCase):
    def test_no_duplicate_technical_ids(self):
        text = (ROOT / 'docs' / 'references' / 'brand-glossary.md').read_text()
        # 表格行：| Technical ID | Display Name |（排除 --- 分隔线）
        rows = re.findall(
            r'^\|\s*([A-Za-z0-9@+][A-Za-z0-9@+-]*)\s*\|\s*[^|]+\|$',
            text, re.MULTILINE)
        from collections import Counter
        dups = sorted({r for r, c in Counter(rows).items() if c > 1})
        self.assertEqual(dups, [], 'glossary 重复行: %s' % dups)
        self.assertGreater(len(rows), 200, 'glossary 行数异常')


class EngineDeepChainTests(unittest.TestCase):
    def test_root_of_terminates_on_deep_chain(self):
        """200 层链（远超旧 depth=100 上限）必须收敛到根。"""
        n = 200
        ssot = {}
        for i in range(n):
            parent = 'N%03d' % (i + 1) if i + 1 < n else None
            ssot['N%03d' % i] = {
                'id': 'N%03d' % i,
                'parent_brand': parent,
            }
        self.assertEqual(_root_of('N000', ssot), 'N199')
        # 最深层节点
        self.assertEqual(_root_of('N199', ssot), 'N199')

    def test_root_of_terminates_on_cycle(self):
        """大环（A1→A2→…→A200→A1）不得死循环。"""
        ssot = {}
        for i in range(200):
            ssot['A%d' % i] = {
                'id': 'A%d' % i,
                'parent_brand': 'A%d' % ((i + 1) % 200),
            }
        # 有向环：_root_of 走 seen 环检测终止，返回进入环前的最后一个节点
        root = _root_of('A0', ssot)
        self.assertIn(root, ssot, '环终止后必须返回图内节点')

    def test_ancestor_set_size_matches_chain(self):
        """深链祖先集合大小 = 链长（去重后），无截断。"""
        n = 200
        ssot = {}
        for i in range(n):
            parent = 'C%03d' % (i + 1) if i + 1 < n else None
            ssot['C%03d' % i] = {
                'id': 'C%03d' % i,
                'parent_brand': parent,
            }
        self.assertEqual(len(_ancestor_set('C000', ssot)), n - 1)


class LegacyMapTests(unittest.TestCase):
    """§64-§67：legacy 旧名必须来自单一来源（scripts/legacy_map.py），不散落硬编码。

    §34（2026-10-01）修订：`xAI` 已恢复为当前 canonical 品牌，不得再出现在
    legacy ID 表中；旧 `icons/xAI/` 目录改用完整前缀模式登记，避免与 canonical
    路径 `icons/SpaceXAI/xAI/xAI.png` 冲突。
    """

    def test_legacy_map_is_single_source(self):
        from legacy_map import (legacy_ids, legacy_path_segments,
                                legacy_scan_patterns)
        segs = set(legacy_path_segments())
        for s in ('DevOps', 'Drive', 'General', 'Tool'):
            self.assertIn(s, segs, '历史分类目录必须在 legacy map 中')
        for s in ('ChinaMobileDisk', 'PeacockTV', 'Podcasts', 'Twitter'):
            self.assertIn(s, segs, '历史品牌 ID 必须在 legacy map 中')
        self.assertNotIn('xAI', segs, 'xAI 已是当前 canonical ID，不得登记为 legacy 名')
        pats = set(legacy_scan_patterns())
        self.assertIn('icons/xAI/', pats, '旧 xAI 目录必须以完整前缀登记')
        self.assertNotIn('/xAI/', pats, '/xAI/ 段在 canonical 路径中合法，不得作为模式')
        # 注册表只允许显式扩容：新增重命名必须同步改这一行（有意保留的摩擦）
        self.assertEqual(legacy_ids(), {'ChinaMobileDisk', 'PeacockTV', 'Podcasts', 'Twitter'})

    def test_canonical_id_is_not_legacy(self):
        """§34：current canonical ID 绝不与 legacy ID 重叠。"""
        import json
        from legacy_map import legacy_ids
        repo = Path(__file__).resolve().parent.parent
        bd = json.loads((repo / 'config' / 'brands.json').read_text(encoding='utf-8'))
        legit = {e['id'] for e in bd['brands']} & legacy_ids()
        self.assertEqual(legit, set(), 'canonical ID 与 legacy ID 重叠: %s' % sorted(legit))

    def test_legacy_patterns_do_not_match_canonical_paths(self):
        """§34：legacy 模式不得命中任何当前 canonical icon 路径。"""
        import json
        from legacy_map import legacy_scan_patterns
        repo = Path(__file__).resolve().parent.parent
        bd = json.loads((repo / 'config' / 'brands.json').read_text(encoding='utf-8'))
        pats = legacy_scan_patterns()
        hits = [e['icon_path'] for e in bd['brands'] if e.get('icon_path')
                and any(p in e['icon_path'] for p in pats)]
        self.assertEqual(hits, [], 'legacy 模式命中当前 canonical 路径: %s' % hits)

    def test_repo_ssot_has_no_legacy_ids(self):
        import json
        from legacy_map import legacy_ids
        repo = Path(__file__).resolve().parent.parent
        bd = json.loads((repo / 'config' / 'brands.json').read_text(encoding='utf-8'))
        cd = json.loads((repo / 'config' / 'categories.json').read_text(encoding='utf-8'))
        legacy = legacy_ids()
        for e in bd['brands']:
            self.assertNotIn(e['id'], legacy, 'brands.json 不应残留旧 ID: %s' % e['id'])
        for c in cd['categories']:
            self.assertNotIn(c['id'], legacy, 'categories.json 不应残留旧 ID: %s' % c['id'])

    def test_repo_docs_have_no_legacy_path_refs(self):
        """非迁移文档不得再引用旧路径段（/xAI/、/PeacockTV/ …）。"""
        from legacy_map import legacy_scan_patterns
        repo = Path(__file__).resolve().parent.parent
        pats = legacy_scan_patterns()
        exempt = {'scripts/legacy_map.py'}
        offenders = []
        for rel in ('README.md', 'docs', 'scripts', '.github', 'config'):
            root = repo / rel
            if not root.exists():
                continue
            files = [root] if root.is_file() else [f for f in root.rglob('*') if f.is_file()]
            for f in files:
                r = f.relative_to(repo).as_posix()
                if r in exempt or r.startswith('docs/migrations/'):
                    continue
                # 字节码缓存 / 二进制资产跳过（否则扫描器会命中自身模式表的 .pyc）
                if '__pycache__' in r.split('/') or r.endswith(('.pyc', '.pyo', '.so', '.png')):
                    continue
                try:
                    text = f.read_text(encoding='utf-8', errors='ignore')
                except Exception:
                    continue
                for p in pats:
                    if p in text:
                        offenders.append('%s: %s' % (r, p))
        self.assertEqual(offenders, [], '存在 legacy 路径段引用: %s' % offenders)


if __name__ == '__main__':
    unittest.main()
