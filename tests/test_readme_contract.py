#!/usr/bin/env python3
"""README generated 行的漂移防护（validator 侧 mutation + generator 侧硬失败）。

背景（2026-10-01 审计实测）
--------------------------
- README 分类表**合计行**此前被 validator `skip`，改成任意数字 CI 仍 PASS（实测 999 通过）；
- 独立仓库句（`当前 N 个图标均为 512×512 PNG`）由 `update-readme-badges.py` 生成却无人校验；
- `update-readme-badges.py` 命中不到目标时只打 `⚠` 并 `return 0`，
  「脚本执行完成」被误当成「文档已同步」。

本测试锁定：
  A. validator 对 generated 行篡改必须失败（合计行 / badge / 分类表行 / 独立仓库句）；
  B. 生成器在 generated 行缺失时必须非 0 退出（不再静默）。
所有改动都发生在仓库副本内。
"""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class _CopyRepoMixin:
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name) / "repo"
        shutil.copytree(REPO, cls.root,
                        ignore=shutil.ignore_patterns(".git", "__pycache__"))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def _readme(self):
        return self.root / "README.md"

    def _mutate(self, old, new):
        p = self._readme()
        s = p.read_text(encoding="utf-8")
        self.assertIn(old, s, "锚点文本不在 README 中：%s" % old)
        p.write_text(s.replace(old, new, 1), encoding="utf-8")

    def _run(self, script):
        return subprocess.run([sys.executable, "scripts/%s" % script], cwd=str(self.root),
                              capture_output=True, text=True, timeout=300)

    def tearDown(self):
        # 每次用例后恢复 README，保证用例彼此独立
        snapshot = self.root / "README.md"
        if hasattr(self, "_baseline_readme"):
            snapshot.write_text(self._baseline_readme, encoding="utf-8")

    def setUp(self):
        if not hasattr(self, "_baseline_readme"):
            type(self)._baseline_readme = self._readme().read_text(encoding="utf-8")


class ReadmeValidatorMutationTests(_CopyRepoMixin, unittest.TestCase):
    """A. 篡改 generated 行 ⇒ ci-validate-icons.py 必须失败。"""

    def test_baseline_copy_passes(self):
        res = self._run("ci-validate-icons.py")
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

    def test_total_row_tamper_fails(self):
        p = self._readme()
        m = re.search(r"^\| \*\*合计\*\* \| — \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|$",
                      p.read_text(encoding="utf-8"), re.M)
        self.assertIsNotNone(m, "README 未找到合计行")
        total_brands, total_icons = m.group(1), m.group(2)
        self._mutate("**合计** | — | **%s** | **%s**" % (total_brands, total_icons),
                     "**合计** | — | **999** | **%s**" % total_icons)
        res = self._run("ci-validate-icons.py")
        self.assertNotEqual(res.returncode, 0, "合计行被篡改但 validator 仍 PASS")
        self.assertIn("合计行", res.stdout + res.stderr)

    def test_icon_badge_tamper_fails(self):
        p = self._readme()
        m = re.search(r"badge/icons-(\d+)-blue", p.read_text(encoding="utf-8"))
        self.assertIsNotNone(m)
        self._mutate("badge/icons-%s-blue" % m.group(1), "badge/icons-999-blue")
        res = self._run("ci-validate-icons.py")
        self.assertNotEqual(res.returncode, 0, "icons badge 被篡改但 validator 仍 PASS")

    def test_brand_badge_tamper_fails(self):
        p = self._readme()
        m = re.search(r"badge/brands-(\d+)-green", p.read_text(encoding="utf-8"))
        self.assertIsNotNone(m)
        self._mutate("badge/brands-%s-green" % m.group(1), "badge/brands-999-green")
        res = self._run("ci-validate-icons.py")
        self.assertNotEqual(res.returncode, 0, "brands badge 被篡改但 validator 仍 PASS")

    def test_per_category_row_tamper_fails(self):
        s = self._readme().read_text(encoding="utf-8")
        # 分类表中除表头/分隔行/合计行外的第一条数据行（计数列必须是整数）
        row = None
        for cand in re.findall(r"^\| .*\|$", s, re.M):
            if "合计" in cand or cand.count("|") != 5:
                continue
            cells = [c.strip() for c in cand.strip().strip("|").split("|")]
            if len(cells) == 4 and cells[2].isdigit() and cells[3].isdigit():
                row = cand
                break
        self.assertIsNotNone(row, "README 未找到分类表数据行")
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        nb, ni = int(cells[2]), int(cells[3])
        self._mutate(row, "| %s | %s | %d | %d |" % (cells[0], cells[1], nb + 1, ni))
        res = self._run("ci-validate-icons.py")
        self.assertNotEqual(res.returncode, 0, "分类表行被篡改但 validator 仍 PASS")

    def test_standalone_repo_sentence_tamper_fails(self):
        p = self._readme()
        m = re.search(r"当前 (\d+) 个图标均为 512×512 PNG", p.read_text(encoding="utf-8"))
        self.assertIsNotNone(m, "README 未找到独立仓库句")
        self._mutate("当前 %s 个图标均为 512×512 PNG" % m.group(1),
                     "当前 999 个图标均为 512×512 PNG")
        res = self._run("ci-validate-icons.py")
        self.assertNotEqual(res.returncode, 0, "独立仓库句被篡改但 validator 仍 PASS")


class ReadmeGeneratorHardFailTests(_CopyRepoMixin, unittest.TestCase):
    """B. generated 行缺失 ⇒ update-readme-badges.py 必须非 0 退出。"""

    def test_generator_ok_on_intact_readme(self):
        res = self._run("update-readme-badges.py")
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("命中", res.stdout)

    def test_generator_fails_when_total_row_missing(self):
        self._mutate("| **合计** |", "| **小计** |")
        res = self._run("update-readme-badges.py")
        self.assertNotEqual(res.returncode, 0, "合计行缺失但生成器静默通过")
        self.assertIn("ERROR", res.stdout + res.stderr)

    def test_generator_fails_when_stats_sentence_missing(self):
        p = self._readme()
        m = re.search(r"覆盖 \*\*(\d+)\*\* 个品牌", p.read_text(encoding="utf-8"))
        self.assertIsNotNone(m, "README 未找到统计句（覆盖 **N** 个品牌）")
        self._mutate("覆盖 **%s** 个品牌" % m.group(1), "覆盖若干品牌")
        res = self._run("update-readme-badges.py")
        self.assertNotEqual(res.returncode, 0, "统计句缺失但生成器静默通过")
        self.assertIn("ERROR", res.stdout + res.stderr)


if __name__ == "__main__":
    unittest.main()
