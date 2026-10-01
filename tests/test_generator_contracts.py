#!/usr/bin/env python3
"""生成器 / 校验器契约测试（Surge catalog，canonical / brand-level 模型）。

锁定的契约（2026-10-01 定稿）
-----------------------------
    1 brand == 1 canonical asset == 1 surge entry

    - `config/surge-icon.json` 由 `config/brands.json`（SSOT）驱动生成，
      **不由磁盘上任意 PNG 驱动**；
    - 每个 entry：name = brand.id，category = brand.category，
      url = ICON_RAW_BASE + '/' + expected_icon_path(brand)；
    - 品牌目录内出现非 canonical PNG（`<id>01.png` 等）⇒ 生成器显式失败（非 0），
      不得静默产出与磁盘状态不一致的清单；
    - 生成器幂等：连续执行两次输出逐字节一致；
    - 基址唯一来源 `scripts/site_constants.py`（禁止再有第二份字面量）。
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT_DIR = REPO / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from brand_relationships import expected_icon_path  # noqa: E402
from site_constants import ICON_RAW_BASE  # noqa: E402

SURGE = REPO / "config" / "surge-icon.json"
BRANDS = REPO / "config" / "brands.json"
GENERATOR = "scripts/generate-icon-json.sh"


def load_ssot():
    return json.loads(BRANDS.read_text(encoding="utf-8"))["brands"]


def load_catalog():
    return json.loads(SURGE.read_text(encoding="utf-8"))["icons"]


def run_generator(cwd):
    return subprocess.run(["bash", GENERATOR], cwd=str(cwd),
                          capture_output=True, text=True, timeout=180)


class CatalogShapeTests(unittest.TestCase):
    """对当前仓库产物本身的契约校验（只读）。"""

    def test_entry_count_equals_icon_backed_brands(self):
        ssot = load_ssot()
        expected = sum(1 for b in ssot if b.get("icon_path"))
        self.assertEqual(len(load_catalog()), expected)

    def test_every_name_is_a_brand_id(self):
        ids = {b["id"] for b in load_ssot()}
        for entry in load_catalog():
            self.assertIn(entry["name"], ids)

    def test_every_entry_has_exactly_name_category_url(self):
        for entry in load_catalog():
            self.assertEqual(list(entry), ["name", "category", "url"])

    def test_urls_derive_from_expected_icon_path(self):
        ssot = {b["id"]: b for b in load_ssot()}
        for entry in load_catalog():
            with self.subTest(name=entry["name"]):
                brand = ssot[entry["name"]]
                self.assertEqual(entry["url"], "%s/%s" % (ICON_RAW_BASE,
                                                          expected_icon_path(brand["id"], ssot)))
                self.assertEqual(entry["category"], brand["category"])

    def test_no_non_canonical_png_in_repo(self):
        offenders = [str(p.relative_to(REPO)) for p in (REPO / "icons").rglob("*.png")
                     if p.stem != p.parent.name]
        self.assertEqual(offenders, [], "品牌目录内存在非 canonical PNG：%s" % offenders)

    def test_url_base_has_single_source(self):
        literal = "raw.githubusercontent.com/Hawaiine/Oasisic-Icons"
        hits = sorted(p.name for p in SCRIPT_DIR.iterdir()
                      if p.suffix in (".py", ".sh")
                      and literal in p.read_text(encoding="utf-8", errors="ignore")
                      and p.name != "site_constants.py")
        self.assertEqual(hits, [], "基址字面量必须只存在于 site_constants.py，实际还有：%s" % hits)


class GeneratorBehaviorTests(unittest.TestCase):
    """在仓库副本内实际执行生成器（不触碰真实工作区）。"""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name) / "repo"
        shutil.copytree(REPO, cls.root,
                        ignore=shutil.ignore_patterns(".git", "__pycache__"))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_generator_reproduces_committed_catalog(self):
        before = (self.root / "config" / "surge-icon.json").read_bytes()
        res = run_generator(self.root)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual((self.root / "config" / "surge-icon.json").read_bytes(), before)

    def test_second_run_is_byte_identical(self):
        run_generator(self.root)
        first = (self.root / "config" / "surge-icon.json").read_bytes()
        run_generator(self.root)
        self.assertEqual((self.root / "config" / "surge-icon.json").read_bytes(), first)

    def test_non_canonical_png_fails_and_keeps_catalog(self):
        entry = next(e for e in load_catalog() if e["name"] == "Netflix")
        brand_dir = self.root / Path(entry["url"].split("/main/", 1)[1]).parent
        variant = brand_dir / "Netflix01.png"
        shutil.copy(brand_dir / "Netflix.png", variant)
        before = (self.root / "config" / "surge-icon.json").read_bytes()
        try:
            res = run_generator(self.root)
        finally:
            variant.unlink()
        self.assertNotEqual(res.returncode, 0, "非 canonical PNG 必须让生成器失败")
        self.assertIn("unregistered/non-canonical PNG detected", res.stdout + res.stderr)
        self.assertIn("Netflix01.png", res.stdout + res.stderr)
        self.assertEqual((self.root / "config" / "surge-icon.json").read_bytes(), before,
                         "失败时不应改写 surge-icon.json")


if __name__ == "__main__":
    unittest.main()
