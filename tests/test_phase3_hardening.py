#!/usr/bin/env python3
"""Phase 3「契约收口与 Fail-Fast 加固」回归测试（2026-10-01）。

本文件只锁定**本轮新增/收紧**的机器可判定契约，且每条都断言「违规 ⇒ 失败」，
而不是只断言「当前通过」——否则回归时无法区分「契约仍然生效」与「检查已经不再运行」。

覆盖：
  1. canonical-only 命名：品牌目录内除 `<id>.png` 外的任何 PNG（数字后缀 / 无关注图）
     ⇒ 校验器（第 3 组）与生成器都 FAIL；
  2. orphan 物理资产：含 PNG 的品牌目录若无对应 SSOT canonical 条目 ⇒ 生成器 FAIL；
  3. canonical PNG 缺失 ⇒ 生成器 FAIL（不得产出与磁盘不一致的清单）；
  4. 圆角遮罩边界（CI 第 18 组）：未登记越界 / 登记值与实测不符 / 已合规仍登记 /
     登记表缺失 / 登记指向不存在的文件 ⇒ FAIL；
     `config/icon-mask-exemptions.json` 是唯一豁免来源；
  5. Quality notes 统计（CI 第 19 组）：`docs/references/icon-quality-notes.md` §6 的
     数量/色型/体积与磁盘不符 ⇒ FAIL；生成器能把它们改回实测值（同一事实源）；
  6. fail-fast：`brands.json` / `categories.json` 缺失、损坏、结构非法，关系引擎
     不可导入或运行期抛错 ⇒ 生成链非 0 退出（禁止退化成空数据 / 静默 fallback）；
  7. `scripts/optimize-icons.py`：存在压缩失败的文件 ⇒ 非 0 退出；
  8. country 条目不得再豁免 `icon_path`（历史例外已删除，canonical 契约统一）。
"""
import importlib.util
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IGNORE = shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '.pytest_cache')

VALIDATOR = ['python3', 'scripts/ci-validate-icons.py']
GENERATOR = ['bash', 'scripts/generate-icon-json.sh']
UPDATER = ['python3', 'scripts/update-readme-badges.py']
NOTES_REL = 'docs/references/icon-quality-notes.md'
LEDGER_REL = 'config/icon-mask-exemptions.json'


def blank_png(path, seed=0):
    """一个体积最小的合法 512×512 RGBA PNG（四角透明），不依赖仓库内任一具体图标。"""
    w = h = 512
    raw = bytearray()
    for y in range(h):
        for x in range(w):
            if seed and (x + y) % 97 == 0:
                raw += bytes((seed % 256, 0, 0, 255))
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


def run(cmd, cwd, timeout=300, env=None):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          timeout=timeout, env=env)


class RepoFixture(unittest.TestCase):
    """每个测试类复制一份仓库（绝不污染工作区）。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix='oasisic-phase3-'))
        cls.repo = cls.tmp / 'repo'
        shutil.copytree(REPO, cls.repo, ignore=IGNORE, symlinks=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def track(self, rel):
        """登记夹具文件的原状态（内容或「原本不存在」），测试结束自动还原。

        夹具纪律：任何写 / 删 / 改名都必须先经 track()。否则同类中后续测试会读到被
        上一个测试破坏的状态，产生「看似产品缺陷、实为夹具泄漏」的假失败。
        """
        p = self.repo / rel
        existed = p.exists()
        data = p.read_bytes() if existed else None

        def restore():
            if existed:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
            elif p.exists():
                p.unlink()

        self.addCleanup(restore)
        return p

    def write(self, rel, text):
        p = self.track(rel)
        p.write_text(text, encoding='utf-8')
        return p

    def remove(self, rel):
        self.track(rel)
        os.remove(self.repo / rel)

    def rename(self, rel, new_rel):
        self.track(rel)
        dst = self.track(new_rel)
        os.rename(self.repo / rel, dst)
        return dst

    def assert_run_fails(self, res, needle):
        out = res.stdout + res.stderr
        self.assertNotEqual(res.returncode, 0,
                            '命令本应失败但返回 0。输出：\n%s' % out[-800:])
        self.assertIn(needle, out, '未出现预期提示 %r。输出：\n%s' % (needle, out[-1500:]))

    def validator(self):
        return run(VALIDATOR, self.repo)

    def generator(self):
        return run(GENERATOR, self.repo)

    def updater(self):
        return run(UPDATER, self.repo)

    def assert_validation_fails(self, needle, res=None):
        res = res if res is not None else self.validator()
        out = res.stdout + res.stderr
        self.assertNotEqual(res.returncode, 0,
                            '校验器本应失败但返回 0。输出尾部：\n%s' % out[-800:])
        self.assertIn(needle, out, '未出现预期提示 %r。输出：\n%s' % (needle, out[-1500:]))

    def assert_generator_fails(self, needle):
        res = self.generator()
        out = res.stdout + res.stderr
        self.assertNotEqual(res.returncode, 0,
                            '生成器本应失败但返回 0。输出尾部：\n%s' % out[-800:])
        self.assertIn(needle, out, '未出现预期提示 %r。输出：\n%s' % (needle, out[-1500:]))


class BaselineTests(RepoFixture):
    def test_validator_groups_are_all_present(self):
        """19 组必须全部真实执行（防止新增组被漏注册而永远不跑）。"""
        res = self.validator()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn('Validation Groups: 19', res.stdout)
        for group in ('Rounded mask 边界', 'Quality notes 统计'):
            self.assertIn('✓ %s' % group, res.stdout,
                          '第 18/19 组未出现在报告中：%s' % res.stdout[-600:])

    def test_generator_is_idempotent(self):
        first = self.generator()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        snapshot = (self.repo / 'config/surge-icon.json').read_bytes()
        second = self.generator()
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(snapshot, (self.repo / 'config/surge-icon.json').read_bytes())

    def test_updater_is_idempotent_when_nothing_is_stale(self):
        """生成器对已同步的 README / notes 必须逐字节不动（否则每次跑都有假 diff）。"""
        before = {rel: (self.repo / rel).read_bytes()
                  for rel in ('README.md', NOTES_REL)}
        res = self.updater()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        for rel, content in before.items():
            self.assertEqual(content, (self.repo / rel).read_bytes(),
                             '%s 在无漂移时被改写' % rel)


class CanonicalOnlyTests(RepoFixture):
    """品牌目录内只允许 <id>.png（变体不是当前契约）。"""

    NETFLIX = 'icons/Media/Netflix'

    def _add_second_png(self, name='Netflix01.png'):
        src = (self.repo / self.NETFLIX / 'Netflix.png').read_bytes()
        p = self.track('%s/%s' % (self.NETFLIX, name))
        p.write_bytes(src)
        return p

    def test_baseline_tree_passes(self):
        self.assertEqual(self.validator().returncode, 0)

    def test_validator_rejects_digit_suffix_png(self):
        self._add_second_png('Netflix01.png')
        self.assert_validation_fails('非 canonical PNG')
        self.assert_validation_fails('Netflix01.png')

    def test_validator_rejects_hyphen_suffix_png(self):
        self._add_second_png('Netflix-dark.png')
        self.assert_validation_fails('非 canonical PNG')

    def test_validator_rejects_unrelated_second_png(self):
        self._add_second_png('Extra.png')
        self.assert_validation_fails('非 canonical PNG')

    def test_generator_rejects_digit_suffix_png(self):
        self._add_second_png('Netflix01.png')
        self.assert_generator_fails('Netflix01.png')

    def test_missing_canonical_png_fails_generator(self):
        self.remove('%s/Netflix.png' % self.NETFLIX)
        self.assert_generator_fails('Netflix')

    def test_missing_canonical_png_fails_validator(self):
        self.remove('%s/Netflix.png' % self.NETFLIX)
        self.assert_validation_fails('Netflix')


class OrphanPhysicalAssetTests(RepoFixture):
    """磁盘上含 PNG 的品牌目录必须对应 SSOT canonical 条目。"""

    ORPHAN = 'icons/System/OrphanBrand'

    def _plant(self, filename='OrphanBrand.png'):
        blank_png(self.track('%s/%s' % (self.ORPHAN, filename)))

    def test_generator_rejects_orphan_brand_dir(self):
        self._plant()
        self.assert_generator_fails('orphan')

    def test_generator_rejects_orphan_dir_with_wrong_filename(self):
        self._plant('Other.png')
        self.assert_generator_fails('orphan')

    def test_validator_rejects_orphan_brand_dir(self):
        self._plant()
        res = self.validator()
        self.assertNotEqual(res.returncode, 0)
        self.assertIn('OrphanBrand', res.stdout + res.stderr)


class MaskBoundaryTests(RepoFixture):
    """CI 第 18 组：r=115 遮罩外不得存在可见 alpha（豁免必须与事实同步）。"""

    def _ledger(self):
        p = self.repo / LEDGER_REL
        return p, json.loads(p.read_text(encoding='utf-8'))

    def _write_ledger(self, doc):
        self.write(LEDGER_REL, json.dumps(doc, ensure_ascii=False, indent=2) + '\n')

    def test_baseline_passes(self):
        self.assertEqual(self.validator().returncode, 0)

    def test_unlisted_violation_fails(self):
        _, doc = self._ledger()
        doc['exemptions'] = [e for e in doc['exemptions'] if 'Blacklist' not in e['path']]
        self._write_ledger(doc)
        self.assert_validation_fails('Blacklist')
        self.assert_validation_fails('遮罩外存在可见 alpha')

    def test_value_mismatch_fails(self):
        _, doc = self._ledger()
        for e in doc['exemptions']:
            if 'NorthKorea' in e['path']:
                e['outside_mask_alpha'] = 1
        self._write_ledger(doc)
        self.assert_validation_fails('登记值与实测不符')

    def test_stale_exemption_fails(self):
        """已合规的图标仍被登记 ⇒ FAIL（豁免表不允许腐烂）。"""
        _, doc = self._ledger()
        doc['exemptions'].append({'path': 'icons/Media/Netflix/Netflix.png',
                                  'outside_mask_alpha': 0, 'reason': 'test'})
        self._write_ledger(doc)
        self.assert_validation_fails('豁免已失效')

    def test_missing_ledger_fails(self):
        self.remove(LEDGER_REL)
        self.assert_validation_fails(LEDGER_REL)

    def test_exemption_pointing_to_missing_file_fails(self):
        _, doc = self._ledger()
        doc['exemptions'][0]['path'] = 'icons/System/Ghost/Ghost.png'
        self._write_ledger(doc)
        self.assert_validation_fails('不存在的文件')

    def test_malformed_ledger_fails(self):
        self.write(LEDGER_REL, '{"exemptions": {}}')
        self.assert_validation_fails('结构非法')


class QualityNotesStatsTests(RepoFixture):
    """CI 第 19 组：icon-quality-notes.md §6 的数字必须有事实源。"""

    def test_baseline_passes(self):
        self.assertEqual(self.validator().returncode, 0)

    def _counts(self):
        """当前仓库的 (PNG 数, RGBA 数)——夹具断言必须由磁盘推导，不得硬编码统计值。"""
        files = list((self.repo / 'icons').rglob('*.png'))
        rgba = 0
        for f in files:
            with open(f, 'rb') as fh:
                head = fh.read(26)
            if len(head) == 26 and head[25] == 6:
                rgba += 1
        return len(files), rgba

    def _patch(self, old, new):
        q = self.repo / NOTES_REL
        t = q.read_text(encoding='utf-8')
        assert old in t, '夹具中找不到 %r' % old
        return self.write(NOTES_REL, t.replace(old, new))

    def test_count_drift_fails(self):
        n, _ = self._counts()
        self._patch('**%d / %d = 512×512**' % (n, n), '**%d / %d = 512×512**' % (n - 1, n - 1))
        self.assert_validation_fails('尺寸行')

    def test_mode_drift_fails(self):
        n, rgba = self._counts()
        self._patch('RGBA %d（其余色型 %d）' % (rgba, n - rgba),
                    'RGBA %d（其余色型 %d）' % (rgba, (n - rgba) + 3))
        self.assert_validation_fails('模式分布行')

    def test_volume_drift_fails(self):
        q = self.repo / NOTES_REL
        before = q.read_text(encoding='utf-8')
        row = [ln for ln in before.splitlines() if ln.startswith('| 体积 |')][0]
        self.write(NOTES_REL, before.replace(
            row, '| 体积 | 合计 ≈ 99.9 MB；平均 ≈1KB / 最大 2KB（3 B，`icons/x.png`） |'))
        self.assert_validation_fails('体积行')

    def test_scan_scope_drift_fails(self):
        q = self.repo / NOTES_REL
        before = q.read_text(encoding='utf-8')
        row = [ln for ln in before.splitlines() if ln.startswith('> 扫描范围：')][0]
        self.write(NOTES_REL, before.replace(
            row, '> 扫描范围：全库 PNG（含 7 个预留空分类 `A` `B`）'))
        self.assert_validation_fails('扫描范围句')

    def test_deleted_stat_line_makes_generator_fail(self):
        """统计行被删除 ⇒ 生成器必须失败（generated contract 不再静默通过）。"""
        n, _ = self._counts()
        self._patch('| 尺寸 | **%d / %d = 512×512**' % (n, n), '| 尺寸 | 见上')
        self.assert_run_fails(self.updater(), '尺寸行')

    def test_generator_repairs_drift(self):
        n, rgba = self._counts()
        self._patch('**%d / %d = 512×512**' % (n, n), '**1 / 1 = 512×512**')
        self._patch('RGBA %d（其余色型 %d）' % (rgba, n - rgba),
                    'RGBA 0（其余色型 %d）' % n)
        res = self.updater()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        fixed = (self.repo / NOTES_REL).read_text(encoding='utf-8')
        self.assertIn('**%d / %d = 512×512**' % (n, n), fixed)
        self.assertIn('RGBA %d（其余色型 %d）' % (rgba, n - rgba), fixed)
        self.assertEqual(self.validator().returncode, 0)


class FailFastTests(RepoFixture):
    """数据缺失 / 损坏 / 引擎故障一律非 0 退出，禁止静默 fallback。"""

    def test_missing_brands_json_fails(self):
        self.remove('config/brands.json')
        self.assert_run_fails(self.updater(), '缺少品牌 SSOT')

    def test_corrupt_brands_json_fails(self):
        self.write('config/brands.json', '{')
        self.assert_run_fails(self.updater(), '无法解析')

    def test_wrong_structure_brands_json_fails(self):
        self.write('config/brands.json', '{"brands": {}}')
        self.assert_run_fails(self.updater(), '结构非法')

    def test_missing_categories_json_fails(self):
        self.remove('config/categories.json')
        self.assert_run_fails(self.updater(), '缺少分类 SSOT')

    def test_corrupt_categories_json_fails(self):
        self.write('config/categories.json', '[]')
        self.assert_run_fails(self.updater(), '结构非法')

    def test_missing_relationship_engine_fails(self):
        """关系引擎不可导入 ⇒ 直接失败（此前会退化为 entry.get('canonical')）。"""
        self.rename('scripts/brand_relationships.py', 'scripts/brand_relationships.py.bak')
        self.assert_run_fails(self.updater(), 'brand_relationships')

    def test_runtime_error_in_engine_is_not_swallowed(self):
        """引擎运行期抛错 ⇒ 非 0（不得被 broad except 吞掉后继续输出统计）。"""
        cur = (self.repo / 'scripts/brand_relationships.py').read_text(encoding='utf-8')
        self.write('scripts/brand_relationships.py',
                   cur + '\n\ndef is_canonical_brand(entry):  # test override\n'
                         '    raise RuntimeError("engine boom")\n')
        self.assert_run_fails(self.updater(), 'engine boom')


class OptimizeExitCodeTests(unittest.TestCase):
    """optimize-icons.py 有失败文件时必须非 0 退出（此前只打印失败数）。"""

    def _tree(self, oxipng_src):
        tmp = Path(tempfile.mkdtemp(prefix='oasisic-optimize-'))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / 'scripts').mkdir()
        shutil.copy2(REPO / 'scripts/optimize-icons.py', tmp / 'scripts/optimize-icons.py')
        (tmp / 'stub').mkdir()
        (tmp / 'stub/oxipng.py').write_text(oxipng_src, encoding='utf-8')
        blank_png(tmp / 'icons/Test/Test.png', seed=3)
        return tmp

    def _run(self, tmp):
        env = dict(os.environ)
        env['PYTHONPATH'] = str(tmp / 'stub')
        return run(['python3', 'scripts/optimize-icons.py'], tmp, env=env)

    def test_all_success_exits_zero(self):
        tmp = self._tree(
            'class StripChunks:\n'
            '    @staticmethod\n'
            '    def safe():\n'
            '        return []\n\n'
            'def optimize(path, **kwargs):\n'
            '    return True\n')
        res = self._run(tmp)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn('0 失败', res.stdout)

    def test_one_failure_exits_nonzero(self):
        tmp = self._tree(
            'class StripChunks:\n'
            '    @staticmethod\n'
            '    def safe():\n'
            '        return []\n\n'
            'def optimize(path, **kwargs):\n'
            '    raise RuntimeError("compress boom")\n')
        res = self._run(tmp)
        self.assertNotEqual(res.returncode, 0,
                            '压缩失败却 exit 0：\n%s' % (res.stdout + res.stderr))
        self.assertIn('1 失败', res.stdout)


class CountryIconContractTests(unittest.TestCase):
    """§country 例外已删除：所有非 pending-ecosystem 条目都必须有 icon_path。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix='oasisic-country-'))
        spec = importlib.util.spec_from_file_location(
            'validate_brand_mod', REPO / 'scripts/validate-brand.py')
        cls.VB = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.VB)  # type: ignore[union-attr]
        cls.brands_doc = json.loads((REPO / 'config/brands.json').read_text(encoding='utf-8'))
        cls.cats_doc = json.loads((REPO / 'config/categories.json').read_text(encoding='utf-8'))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _entry(self, **kw):
        e = {'id': 'TestCountry', 'display_name': 'TestCountry', 'category': 'Country',
             'entity_type': 'country'}
        e.update(kw)
        return e

    def test_country_without_icon_path_is_rejected(self):
        res = self.VB.validate_brand(self._entry(), self.brands_doc, self.cats_doc, str(self.tmp))
        self.assertTrue(any('缺 icon_path' in x for x in res['errors']), res['errors'])

    def test_country_with_icon_path_is_accepted(self):
        e = self._entry()
        blank_png(self.tmp / 'icons/Country/TestCountry/TestCountry.png')
        e['icon_path'] = 'icons/Country/TestCountry/TestCountry.png'
        res = self.VB.validate_brand(e, self.brands_doc, self.cats_doc, str(self.tmp))
        self.assertFalse([x for x in res['errors'] if 'icon_path' in x], res['errors'])


if __name__ == '__main__':
    unittest.main()
