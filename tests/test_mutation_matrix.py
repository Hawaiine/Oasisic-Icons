#!/usr/bin/env python3
"""校验器 mutation 矩阵：证明「闸门真的会红」（32 例）。

为什么需要它
------------
「CI 全绿」不等于「闸门有效」：绿屏是静默 no-op 的最佳藏身处。本模块对仓库**副本**
注入 32 种已知坏状态，逐例断言 `ci-validate-icons.py` 非 0 退出**且**报出预期的
那条错误（而不只是「失败了」）。这是全库唯一能证明「校验器不是永远绿」的可复跑证据。

共享基础设施（tests/_harness.py）
---------------------------------
- 每个类别一份**共享副本**，用例级只还原自己碰过的路径（不再每例整仓 copytree）；
- 唯一 PNG 素材用 Pillow 生成并按 seed 缓存（旧版逐像素纯 Python 实现是主要耗时来源）；
- 变异必须**证明落地**（`ScratchRepo.replace` 断言锚点存在），否则报错而非假阴性。

基线（2026-10-02，main = 8d554d9）
---------------------------------
    本矩阵（优化后）：见 CI 输出；
    审计期的一次性脚本（每例整仓副本 + 逐像素 PNG + 单跑校验器）：32 例 129s。

注意：`config/icon-mask-exemptions.json`（遮罩豁免台账）与其 CI 组随 PR #16 引入；
在其合并前，相关 2 例自动 skip，合并后自动生效（无需改本文件）。
"""
import json
import unittest

from _harness import REPO, ScratchRepo, write_unique_png

MASK_LEDGER = 'config/icon-mask-exemptions.json'
NEEDS_LEDGER = unittest.skipUnless(
    (REPO / MASK_LEDGER).exists(),
    '需要 config/icon-mask-exemptions.json（PR #16 引入的遮罩豁免台账）')


class _MutationBase(unittest.TestCase):
    """共享副本 + 定向还原 + 「必须被拦」断言。"""

    @classmethod
    def setUpClass(cls):
        cls.repo = ScratchRepo(prefix='oasisic-mut-%s-' % cls.__name__[:12])

    @classmethod
    def tearDownClass(cls):
        cls.repo.close()

    def blocked(self, touched, mutate, *expect, allow_generator=False, also_generator=False):
        """执行变异 → 断言「仓库的闸门」非 0 且报出预期错误 → 还原副本。

        touched: 变异涉及的所有路径（还原用，含新增文件/目录）。
        expect:  必需出现在输出里的归因字符串。传 tuple/list 表示「任选其一」，
                 用于跨版本闸门迁移的场景（例如 canonical-only 命名契约在 PR #16
                 合并前由生成器直接拦截、合并后同时由校验器 Naming 组拦截）。
        allow_generator: 校验器放行时补跑生成器（闸门可能有多个，任一拦住即可）。
        also_generator:  无论校验器结果如何都补跑生成器并合并其输出——用于闸门归属
                         跨版本的场景（canonical-only 命名：合并前生成器直接报
                         「non-canonical PNG detected」，合并后校验器 Naming 组同报）。
        """
        try:
            mutate()
            res = self.repo.validate()
            out = res.stdout + res.stderr
            if (res.returncode == 0 and allow_generator) or also_generator:
                gen = self.repo.run('scripts/generate-icon-json.sh')
                if gen.returncode != 0:
                    out += '\n--- generate-icon-json.sh ---\n' + gen.stdout + gen.stderr
                if res.returncode == 0:
                    res = gen
            self.assertNotEqual(
                res.returncode, 0,
                '变异未被拦截（rc=0）——闸门失效或该场景无人覆盖:\n%s' % out[-2000:])
            for needle in expect:
                if isinstance(needle, (tuple, list)):
                    self.assertTrue(
                        any(n in out for n in needle),
                        '校验器失败了，但没有报出预期的归因信息（%s 之一）:\n%s'
                        % (' / '.join(needle), out[-2000:]))
                else:
                    self.assertIn(needle, out,
                                  '校验器失败了，但没有报出预期的归因信息 %r:\n%s'
                                  % (needle, out[-2000:]))
        finally:
            self.repo.restore(*touched)


class SsotMutations(_MutationBase):
    """SSOT（config/brands.json / categories.json）损坏与漂移。"""

    def test_missing_brand_fails(self):
        def m():
            self.repo.mutate_json(
                'config/brands.json',
                lambda d: d.__setitem__('brands', [b for b in d['brands'] if b['id'] != 'Netflix']))
        self.blocked(['config/brands.json'], m,
                     '✗ Brands SSOT', '磁盘品牌不在 brands.json: icons/Media/Netflix')

    def test_icon_path_pointing_nowhere_fails(self):
        def m():
            def f(d):
                for b in d['brands']:
                    if b['id'] == 'Netflix':
                        b['icon_path'] = 'icons/Media/Netflix/Netflix_gone.png'
            self.repo.mutate_json('config/brands.json', f)
        self.blocked(['config/brands.json'], m,
                     '✗ Brands SSOT', 'Netflix_gone.png',
                     ('icon_path 与路径规则不一致', 'icon_path 文件不存在'))

    def test_broken_json_syntax_is_attributed_not_traceback(self):
        """2026-10-02 审计 §6：损坏的 SSOT 曾以原始 traceback 形式炸出。
        现在必须给出「哪个文件、哪一行、什么原因」，并归入所属校验组。"""
        def m():
            self.repo.write('config/brands.json', '{')
        self.blocked(['config/brands.json'], m,
                     '✗ Brands SSOT', 'JSON 解析失败', 'config/brands.json', '第 1 行')

    def test_deleted_brands_json_fails(self):
        def m():
            (self.repo.root / 'config' / 'brands.json').unlink()
        self.blocked(['config/brands.json'], m,
                     '✗ Brands SSOT', '缺少 config/brands.json')

    def test_deleted_category_fails(self):
        def m():
            self.repo.mutate_json(
                'config/categories.json',
                lambda d: d.__setitem__('categories',
                                        [c for c in d['categories'] if c['id'] != 'Game']))
        self.blocked(['config/categories.json'], m,
                     '✗ Category', '分类不在 SSOT 白名单中（icons/Game）')

    def test_broken_categories_json_fails(self):
        def m():
            self.repo.write('config/categories.json', '[[')
        self.blocked(['config/categories.json'], m,
                     '✗ Category', 'JSON 解析失败', 'config/categories.json', '第 1 行')


class PngContractMutations(_MutationBase):
    """canonical-only 命名契约：品牌目录内多/少文件都必须红。"""

    def test_numeric_suffix_png_fails(self):
        def m():
            write_unique_png(self.repo.root, 'icons/Media/Netflix/Netflix01.png', 11)
        self.blocked(['icons/Media/Netflix/Netflix01.png'], m,
                     'Netflix01.png',
                     ('✗ Naming', 'non-canonical PNG detected'),
                     also_generator=True)

    def test_hyphen_variant_png_fails(self):
        def m():
            write_unique_png(self.repo.root, 'icons/Media/Netflix/Netflix-dark.png', 12)
        self.blocked(['icons/Media/Netflix/Netflix-dark.png'], m,
                     'Netflix-dark.png',
                     ('✗ Naming', 'non-canonical PNG detected'),
                     also_generator=True)

    def test_renamed_canonical_png_fails(self):
        def m():
            d = self.repo.root / 'icons/Apple/iCloud'
            (d / 'iCloud.png').rename(d / 'iCloud_old.png')
        self.blocked(['icons/Apple/iCloud'], m,
                     '✗ Brands SSOT', 'icon_path 文件不存在: icons/Apple/iCloud/iCloud.png')


class OrphanMutations(_MutationBase):
    """物理资产与 SSOT 的双向一致性。"""

    def test_orphan_brand_dir_fails(self):
        """目录存在但 SSOT 无对应条目（内容唯一，避免被 SHA 唯一性组顶替归因）。"""
        def m():
            write_unique_png(self.repo.root, 'icons/System/OrphanX/OrphanX.png', 13)
        self.blocked(['icons/System/OrphanX'], m,
                     '✗ Brands SSOT', '磁盘品牌不在 brands.json: icons/System/OrphanX')

    def test_missing_brand_dir_fails(self):
        """SSOT 有条目但物理目录缺失。"""
        def m():
            import shutil as _sh
            _sh.rmtree(self.repo.root / 'icons/Media/Netflix')
        self.blocked(['icons/Media/Netflix'], m,
                     '✗ Brands SSOT', 'brands.json 品牌在磁盘不存在: Media/Netflix')


class DerivedArtifactMutations(_MutationBase):
    """派生文件（surge / 关系导出 / review queue）手改或被删。"""

    def _restore_all(self):
        return ['config/surge-icon.json', 'config/brand-relationships.json',
                'config/brand-review-queue.json']

    def test_surge_url_tampered_fails(self):
        def m():
            self.repo.replace('config/surge-icon.json', 'Netflix.png', 'Netflix_HACKED.png')
        self.blocked(self._restore_all(), m, '✗ Surge JSON', 'Netflix_HACKED.png')

    def test_surge_entry_removed_fails(self):
        def m():
            def f(d):
                d['icons'] = [e for e in d['icons'] if e.get('name') != 'Netflix']
            self.repo.mutate_json('config/surge-icon.json', f)
        self.blocked(self._restore_all(), m, '✗ Surge JSON', '条目数不一致')

    def test_surge_missing_fails(self):
        def m():
            (self.repo.root / 'config' / 'surge-icon.json').unlink()
        self.blocked(self._restore_all(), m, '✗ Surge JSON', '缺少 config/surge-icon.json')

    def test_relationship_parent_tampered_fails(self):
        def m():
            def f(d):
                for r in d['brands']:
                    if r.get('child') == 'Netflix':
                        r['parent'] = 'HackedParent'
            self.repo.mutate_json('config/brand-relationships.json', f)
        self.blocked(self._restore_all(), m, '✗ 关系派生导出', 'Netflix')

    def test_relationship_generated_marker_removed_fails(self):
        def m():
            self.repo.mutate_json('config/brand-relationships.json',
                                  lambda d: d.__setitem__('generated', False))
        self.blocked(self._restore_all(), m, '✗ 关系派生导出', 'generated: true')

    def test_relationship_export_missing_fails(self):
        def m():
            (self.repo.root / 'config' / 'brand-relationships.json').unlink()
        self.blocked(self._restore_all(), m,
                     '✗ 关系派生导出', '缺少 config/brand-relationships.json')

    def test_review_queue_marked_as_ssot_fails(self):
        def m():
            self.repo.mutate_json('config/brand-review-queue.json',
                                  lambda d: d.__setitem__('is_ssot', True))
        self.blocked(self._restore_all(), m, '✗ Review Queue', 'is_ssot: false')

    def test_review_queue_missing_fails(self):
        def m():
            (self.repo.root / 'config' / 'brand-review-queue.json').unlink()
        self.blocked(self._restore_all(), m,
                     '✗ Review Queue', '缺少 config/brand-review-queue.json')


class DocDriftMutations(_MutationBase):
    """generated 文档漂移（README / glossary / 关系矩阵 / 父节点 README）。"""

    def _restore_all(self):
        return ['README.md', 'docs/references/brand-glossary.md',
                'docs/references/physical-hierarchy-audit.md', 'icons/Apple/Apple']

    def test_readme_icon_count_tampered_fails(self):
        def m():
            self.repo.replace('README.md', 'badge/icons-294-blue', 'badge/icons-999-blue')
        self.blocked(self._restore_all(), m, '✗ README 统计', 'badge icons=999')

    def test_readme_category_row_removed_fails(self):
        """分类表是「generated 行」：整行删除必须红（含 emoji 前缀的真实行格式）。"""
        def m():
            import re
            s = self.repo.read('README.md')
            lines = s.splitlines(keepends=True)
            out = [l for l in lines
                   if not (l.startswith('|') and re.search(r'(?<![A-Za-z])Media(?![A-Za-z])', l))]
            assert len(out) < len(lines), '变异未落地：README 无独立 Media 分类行'
            self.repo.write('README.md', ''.join(out))
        self.blocked(self._restore_all(), m, '✗ README 表格', '缺失分类: Media')

    def test_glossary_display_name_tampered_fails(self):
        def m():
            self.repo.replace('docs/references/brand-glossary.md',
                              '| Netflix | Netflix |', '| Netflix | Netflix_HACKED |')
        self.blocked(self._restore_all(), m, '✗ Glossary', 'Netflix_HACKED')

    def test_glossary_row_removed_fails(self):
        def m():
            s = self.repo.read('docs/references/brand-glossary.md')
            lines = s.splitlines(keepends=True)
            out = [l for l in lines if not l.startswith('| Netflix |')]
            assert len(out) < len(lines), '变异未落地'
            self.repo.write('docs/references/brand-glossary.md', ''.join(out))
        self.blocked(self._restore_all(), m, '✗ Glossary', '缺失品牌: Netflix')

    def test_physical_hierarchy_doc_tampered_fails(self):
        def m():
            self.repo.replace('docs/references/physical-hierarchy-audit.md',
                              '| `Valve` | `Steam` |', '| `Valve` | `Steam_HACKED` |')
        self.blocked(self._restore_all(), m, '✗ 物理路径', '关系矩阵文档与重算不一致')

    def test_parent_readme_tampered_fails(self):
        def m():
            self.repo.replace('icons/Apple/Apple/README.md', 'iCloud', 'iCloudHACKED')
        self.blocked(self._restore_all(), m, '✗ README 父节点', '生成 README 内容与 expected 不一致: Apple')

    def test_readme_missing_fails(self):
        def m():
            (self.repo.root / 'README.md').unlink()
        self.blocked(self._restore_all(), m, '✗ README 表格', '缺少 README.md')


class AssetIntegrityMutations(_MutationBase):
    """资产完整性：坏 PNG / 尺寸 / 色型 / 字节重复 / 遮罩越界未登记。"""

    def test_truncated_png_fails(self):
        def m():
            self.repo.write_bytes('icons/Media/Netflix/Netflix.png',
                                  b'\x89PNG\r\n\x1a\n' + b'\x00' * 20)
        self.blocked(['icons/Media/Netflix/Netflix.png'], m,
                     '✗ PNG integrity', 'icons/Media/Netflix/Netflix.png')

    def test_wrong_dimensions_fail(self):
        def m():
            from PIL import Image
            p = self.repo.root / 'icons/Media/Netflix/Netflix.png'
            with Image.open(p) as im:
                im.convert('RGBA').resize((256, 256)).save(p)
        self.blocked(['icons/Media/Netflix/Netflix.png'], m,
                     '✗ Image spec', '尺寸非 512×512')

    def test_non_rgba_mode_fails(self):
        def m():
            from PIL import Image
            p = self.repo.root / 'icons/Media/Netflix/Netflix.png'
            with Image.open(p) as im:
                im.convert('RGB').save(p)
        self.blocked(['icons/Media/Netflix/Netflix.png'], m,
                     '✗ Image spec', '模式非 RGBA')

    def test_duplicate_png_bytes_fail(self):
        def m():
            self.repo.write_bytes('icons/CloudStorage/115/115.png',
                                  (self.repo.root / 'icons/Media/Netflix/Netflix.png').read_bytes())
        self.blocked(['icons/CloudStorage/115/115.png'], m,
                     '✗ SHA-256 uniqueness')

    @NEEDS_LEDGER
    def test_mask_exemption_entry_removed_fails(self):
        def m():
            def f(d):
                d['exemptions'] = [e for e in d['exemptions'] if 'Blacklist' not in e['path']]
            self.repo.mutate_json(MASK_LEDGER, f)
        self.blocked([MASK_LEDGER], m, '✗ Rounded mask 边界')

    @NEEDS_LEDGER
    def test_mask_ledger_missing_fails(self):
        def m():
            (self.repo.root / MASK_LEDGER).unlink()
        self.blocked([MASK_LEDGER], m, '✗ Rounded mask 边界')


if __name__ == '__main__':
    unittest.main(verbosity=2)
