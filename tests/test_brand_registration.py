#!/usr/bin/env python3
"""新增品牌自动化 / 关系派生导出 / Review Queue 的测试。

覆盖（§39-§43 §71）：
  - `scripts/validate-brand.py::validate_brand` 的确定性校验：ID 撞车（精确 / 大小写 /
    归一化）、legacy ID、display_name 重复、category / entity_type 合法性、
    parent_brand 存在性与类型、icon 命名契约与文件存在性、SHA 重复、
    生态根约束（category=自身 / 无 parent / descendants ≥ 2 由关系引擎给出）；
  - `scripts/export-brand-relationships.py`：派生导出与 SSOT + 关系引擎逐项一致、
    标 `generated: true` + `source`、可确定性重放（0 diff）；
  - `config/brand-review-queue.json`：结构合法、`is_ssot: false`、状态取值、引用真实 ID。
"""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


VB = _load(ROOT / 'scripts' / 'validate-brand.py', 'validate_brand_mod')
EXPORT = _load(ROOT / 'scripts' / 'export-brand-relationships.py', 'export_rel_mod')

REAL_BRANDS = json.loads((ROOT / 'config' / 'brands.json').read_text(encoding='utf-8'))
REAL_CATS = json.loads((ROOT / 'config' / 'categories.json').read_text(encoding='utf-8'))

# 一个体积最小的合法 512×512 RGBA PNG（四角透明），避免依赖仓库内某张具体图标
import zlib  # noqa: E402
import struct  # noqa: E402


def _blank_png(path, seed=0):
    w = h = 512
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter type
        for x in range(w):
            inset = 120
            inside = inset <= x < w - inset and inset <= y < h - inset
            if inside:
                raw += bytes((seed % 256, 128, 200, 255))
            else:
                raw += bytes((0, 0, 0, 0))
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 6))
    png += chunk(b'IEND', b'')
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(png)


class ValidateBrandTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='oasisic-brand-'))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.brands_doc = json.loads(json.dumps(REAL_BRANDS))
        self.cats_doc = json.loads(json.dumps(REAL_CATS))

    def _entry(self, **kw):
        e = {'id': 'TestBrand', 'display_name': 'TestBrand', 'category': 'Music',
             'entity_type': 'product_brand', 'parent_brand': 'Apple'}
        e.update(kw)
        return e

    def _prepare_icon(self, entry):
        icon = f"icons/{entry['category']}/{entry['id']}/{entry['id']}.png"
        full = self.tmp / icon
        _blank_png(full, seed=len(entry['id']))
        return icon

    def test_accepts_valid_new_brand(self):
        e = self._entry()
        icon = self._prepare_icon(e)
        e['icon_path'] = icon
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertEqual(res['errors'], [], res['errors'])

    def test_rejects_duplicate_id(self):
        e = self._entry(id='Apple', display_name='Apple2')
        e['icon_path'] = 'icons/Music/Apple/Apple.png'
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('id 已存在' in x for x in res['errors']), res['errors'])

    def test_rejects_case_collision(self):
        e = self._entry(id='apple', display_name='apple')
        e['icon_path'] = 'icons/Music/apple/apple.png'
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('大小写撞车' in x for x in res['errors']), res['errors'])

    def test_rejects_normalization_collision(self):
        """§24：A@B 与 AB 归一化后不得静默撞车。"""
        self.brands_doc['brands'].append({'id': 'AB', 'display_name': 'AB',
                                          'category': 'Music', 'entity_type': 'product_brand',
                                          'icon_path': 'icons/Music/AB/AB.png'})
        e = self._entry(id='A@B', display_name='A@B')
        e['icon_path'] = 'icons/Music/A@B/A@B.png'
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('归一化后与现有 ID 撞车' in x for x in res['errors']), res['errors'])

    def test_rejects_legacy_id(self):
        """§34：canonical 新品牌不得使用 legacy 旧 ID。"""
        e = self._entry(id='Twitter', display_name='Twitter')
        e['icon_path'] = 'icons/Music/Twitter/Twitter.png'
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('legacy' in x for x in res['errors']), res['errors'])

    def test_rejects_duplicate_display_name(self):
        e = self._entry(id='FreshName', display_name='Apple')
        e['icon_path'] = 'icons/Music/FreshName/FreshName.png'
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('display_name 与现有品牌重复' in x for x in res['errors']), res['errors'])

    def test_rejects_unknown_category(self):
        e = self._entry(category='NoSuchCategory')
        e['icon_path'] = 'icons/NoSuchCategory/TestBrand/TestBrand.png'
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('category 不在 config/categories.json' in x for x in res['errors']),
                        res['errors'])

    def test_rejects_illegal_entity_type(self):
        e = self._entry(entity_type='brandish')
        e['icon_path'] = 'icons/Music/TestBrand/TestBrand.png'
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('entity_type 非法' in x for x in res['errors']), res['errors'])

    def test_rejects_missing_parent(self):
        e = self._entry(parent_brand='NoSuchParent')
        e['icon_path'] = 'icons/Music/TestBrand/TestBrand.png'
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('parent_brand 不存在' in x for x in res['errors']), res['errors'])

    def test_rejects_non_brand_parent_type(self):
        """父节点只能是 product_brand / ecosystem。"""
        self.brands_doc['brands'].append({'id': 'CtryIcon', 'display_name': 'CtryIcon',
                                          'category': 'Country', 'entity_type': 'country',
                                          'icon_path': 'icons/Country/CtryIcon/CtryIcon.png'})
        e = self._entry(parent_brand='CtryIcon')
        e['icon_path'] = 'icons/Music/TestBrand/TestBrand.png'
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('parent_brand 类型非法' in x for x in res['errors']), res['errors'])

    def test_rejects_wrong_icon_path_and_missing_file(self):
        e = self._entry(icon_path='icons/Music/WrongName/WrongName.png')
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('icon_path 与命名契约不一致' in x for x in res['errors']), res['errors'])
        e2 = self._entry()
        e2['icon_path'] = 'icons/Music/TestBrand/TestBrand.png'
        res2 = VB.validate_brand(e2, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('icon 文件不存在' in x for x in res2['errors']), res2['errors'])

    def test_rejects_duplicate_icon_content(self):
        """CI 第 6 组同口径：两个品牌不得共用同一 SHA 图标。"""
        # 在 tmp 仓库内造一个既有品牌 + 一张图标，再让候选品牌用内容相同的图标
        _blank_png(self.tmp / 'icons/Music/Existing/Existing.png', seed=7)
        self.brands_doc['brands'].append({
            'id': 'Existing', 'display_name': 'Existing', 'category': 'Music',
            'entity_type': 'product_brand',
            'icon_path': 'icons/Music/Existing/Existing.png'})
        e = self._entry()
        icon = f"icons/{e['category']}/{e['id']}/{e['id']}.png"
        _blank_png(self.tmp / icon, seed=7)
        e['icon_path'] = icon
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('SHA-256 重复' in x for x in res['errors']), res['errors'])

    def test_rejects_ecosystem_with_parent_and_wrong_category(self):
        e = self._entry(id='EcoX', entity_type='ecosystem', category='Music',
                        parent_brand='Apple')
        e['icon_path'] = 'icons/Music/EcoX/EcoX.png'
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('生态根必须以自身为一级分类' in x for x in res['errors']), res['errors'])
        self.assertTrue(any('生态根不得有 parent_brand' in x for x in res['errors']), res['errors'])

    def test_ecosystem_without_two_descendants_rejected_by_engine(self):
        self.cats_doc['categories'].append({'id': 'EcoY', 'display_name': 'EcoY',
                                            'emoji': '🧪', 'description': 'test',
                                            'type': 'ecosystem', 'status': 'active',
                                            'sort_order': 99})
        e = self._entry(id='EcoY', display_name='EcoY', category='EcoY',
                        entity_type='ecosystem', parent_brand=None)
        e['icon_path'] = self._prepare_icon(e)
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertTrue(any('descendants < 2' in x for x in res['errors']), res['errors'])

    def test_parent_unknown_yields_warning_not_silent_guess(self):
        """§41：无法确定 parent 时给 warning + 提示走 Review Queue，绝不静默猜。"""
        e = self._entry(parent_brand=None)
        e['icon_path'] = self._prepare_icon(e)
        res = VB.validate_brand(e, self.brands_doc, self.cats_doc, self.tmp)
        self.assertEqual(res['errors'], [], res['errors'])
        self.assertTrue(any('review-queue' in w for w in res['warnings']), res['warnings'])


class RelationshipExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(
            (ROOT / 'config' / 'brand-relationships.json').read_text(encoding='utf-8'))
        cls.expected = EXPORT.build(REAL_BRANDS)

    def test_marked_as_generated_derivative(self):
        self.assertIs(self.doc['generated'], True)
        self.assertEqual(self.doc['source'], 'config/brands.json')

    def test_rows_match_ssot_and_engine(self):
        self.assertEqual(self.doc['brands'], self.expected['brands'])

    def test_final_tree_in_export(self):
        by = {r['child']: r for r in self.doc['brands']}
        self.assertEqual(by['X']['parent'], 'SpaceXAI')
        self.assertEqual(by['xAI']['parent'], 'SpaceXAI')
        self.assertEqual(by['Grok']['parent'], 'xAI')
        self.assertEqual(by['Grok']['ancestor_chain'], ['xAI', 'SpaceXAI'])
        self.assertEqual(by['Grok']['graph_root'], 'SpaceXAI')

    def test_export_is_deterministic(self):
        p = ROOT / 'config' / 'brand-relationships.json'
        before = p.read_text(encoding='utf-8')
        subprocess.run([sys.executable, str(ROOT / 'scripts' / 'export-brand-relationships.py')],
                       cwd=str(ROOT), check=True, capture_output=True)
        self.assertEqual(before, p.read_text(encoding='utf-8'), '关系导出生成器不幂等')


class ReviewQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q = json.loads(
            (ROOT / 'config' / 'brand-review-queue.json').read_text(encoding='utf-8'))
        cls.brands = {b['id'] for b in REAL_BRANDS['brands']}
        cls.aliases = set(REAL_BRANDS.get('parent_brands_without_icon', []))

    def test_is_not_a_second_ssot(self):
        self.assertIs(self.q['is_ssot'], False)
        self.assertEqual(set(self.q['status_values']), {'OPEN', 'RESOLVED'})

    def test_items_are_well_formed_and_reference_real_ids(self):
        ids = set()
        for it in self.q['items']:
            self.assertTrue(it['id'] and it['id'] not in ids, it)
            ids.add(it['id'])
            self.assertIn(it['status'], self.q['status_values'], it['id'])
            self.assertIn(it['issue_kind'], self.q['issue_kinds'], it['id'])
            child = it.get('child')
            self.assertTrue(child in self.brands or child in self.aliases,
                            'child 必须引用真实品牌或白名单母公司: %s' % child)
            cp = it.get('candidate_parent')
            self.assertTrue(cp is None or cp in self.brands or cp in self.aliases, it['id'])

    def test_spacexai_logo_item_present_and_open(self):
        it = next(i for i in self.q['items'] if i['child'] == 'SpaceXAI')
        self.assertEqual(it['status'], 'OPEN')
        self.assertEqual(it['issue_kind'], 'official_logo_missing')
        self.assertIn('SpaceXAI', self.aliases)


if __name__ == '__main__':
    unittest.main(verbosity=2)
