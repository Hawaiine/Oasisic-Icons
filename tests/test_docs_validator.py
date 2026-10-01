#!/usr/bin/env python3
"""文档引用校验器（scripts/ci-validate-docs.py）测试。

覆盖需求矩阵（false positive / negative 双向）：
  - valid concrete path      → PASS
  - invalid concrete path    → FAIL（新增错误 current-state path 必须让 CI 失败）
  - placeholder path         → 跳过（不误判）
  - URL template             → 跳过（不误判）
  - historical / migration   → 位于 exclude 范围，合法旧 path 不导致 FAIL
  - inline code / fenced code / Markdown link / bare URL → 均纳入校验

不设任何 concrete-path 豁免清单：current / normative 文档中的 concrete path 必须真实存在，
需要长期保留的旧 path 只能位于 exclude 覆盖的历史 / 迁移文档。

另含设计红线测试：校验器不得引入第二套品牌/路径真相。
"""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "ci-validate-docs.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("ci_validate_docs", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VD = load_validator()


class TempRepo:
    """最小临时仓库：只放校验器关心的文件。"""

    def __init__(self, case: unittest.TestCase):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        case.addCleanup(self._tmp.cleanup)

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def png(self, rel: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\x89PNG\r\n\x1a\n")


class ConcretePathTests(unittest.TestCase):
    def test_valid_concrete_path_passes(self):
        t = TempRepo(self)
        t.png("icons/Communication/Telegram/Telegram.png")
        t.write("README.md", "见 `icons/Communication/Telegram/Telegram.png`。\n")
        self.assertEqual(VD.check_repo(t.root, quiet=True), 0)

    def test_invalid_concrete_path_fails(self):
        t = TempRepo(self)
        t.write("README.md", "见 `icons/Social/Telegram/Telegram.png`。\n")
        violations, checked = VD.scan_text(
            (t.root / "README.md").read_text(), "README.md", t.root)
        self.assertEqual(checked, 1)
        self.assertEqual(len(violations), 1)
        self.assertIn("README.md:1", violations[0])
        self.assertIn("icons/Social/Telegram/Telegram.png", violations[0])
        self.assertEqual(VD.check_repo(t.root, quiet=True), 1)

    def test_cli_exit_codes(self):
        bad = TempRepo(self)
        bad.write("README.md", "icons/Nowhere/Brand/Brand.png\n")
        self.assertEqual(VD.main(["--root", str(bad.root), "--quiet"]), 1)

        good = TempRepo(self)
        good.png("icons/Nowhere/Brand/Brand.png")
        good.write("README.md", "icons/Nowhere/Brand/Brand.png\n")
        self.assertEqual(VD.main(["--root", str(good.root), "--quiet"]), 0)


class NonConcreteTests(unittest.TestCase):
    def test_placeholder_path_skipped(self):
        t = TempRepo(self)
        t.write("README.md", "结构：`icons/<category>/<brand>/<brand>.png`\n")
        self.assertEqual(VD.check_repo(t.root, quiet=True), 0)

    def test_url_template_skipped(self):
        t = TempRepo(self)
        t.write("README.md",
                "https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/<分类>/<品牌名>/<文件名>.png\n")
        self.assertEqual(VD.check_repo(t.root, quiet=True), 0)

    def test_directory_notation_without_png_skipped(self):
        t = TempRepo(self)
        t.write("README.md", "新增 Spotify → `Music/Spotify/`\n")
        self.assertEqual(VD.check_repo(t.root, quiet=True), 0)


class ContextTests(unittest.TestCase):
    def test_inline_code_fenced_code_link_and_bare_url_all_checked(self):
        t = TempRepo(self)
        t.write("README.md", "\n".join([
            "行内：`icons/A/B/B.png`",
            "",
            "```",
            "icons/C/D/D.png",
            "```",
            "",
            "链接：[图标](icons/E/F/F.png)",
            "",
            "裸 URL：https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/G/H/H.png",
            "",
        ]) + "\n")
        text = (t.root / "README.md").read_text()
        violations, checked = VD.scan_text(text, "README.md", t.root)
        self.assertEqual(checked, 4)
        self.assertEqual(len(violations), 4)
        lines = sorted(int(v.split(":")[1]) for v in violations)
        self.assertEqual(lines, [1, 4, 7, 9])

    def test_url_with_existing_concrete_path_passes(self):
        t = TempRepo(self)
        t.png("icons/Media/Netflix/Netflix.png")
        t.write("README.md",
                "https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png\n")
        self.assertEqual(VD.check_repo(t.root, quiet=True), 0)


class ScopeTests(unittest.TestCase):
    def test_historical_and_migration_docs_excluded(self):
        t = TempRepo(self)
        t.write("README.md", "ok（无路径引用）\n")
        # 这些文件里的旧路径是合法历史记录，不得导致 FAIL
        t.write("docs/migrations/url-migration.md", "旧：icons/Social/Telegram/Telegram.png\n")
        t.write("docs/references/upstream-history.md", "旧：icons/Apple/AppleNews/AppleNews.png\n")
        t.write("docs/references/brand-migration.md", "旧：icons/Media/PeacockTV/PeacockTV.png\n")
        t.write("docs/references/category-migration.md", "旧：icons/DevOps/Docker/Docker.png\n")
        t.write("docs/references/brand-ownership-audit.md", "旧：icons/AI/SpaceXAI/SpaceXAI.png\n")
        self.assertEqual(VD.check_repo(t.root, quiet=True), 0)
        self.assertEqual(VD.collect_docs(t.root), ["README.md"])

    def test_non_included_docs_not_scanned(self):
        t = TempRepo(self)
        t.write("docs/references/brand-glossary.md", "icons/Ghost/Ghost/Ghost.png\n")
        t.write("docs/guides/usage.md", "icons/Ghost2/Ghost2/Ghost2.png\n")
        self.assertEqual(VD.collect_docs(t.root), ["docs/guides/usage.md"])
        self.assertEqual(VD.check_repo(t.root, quiet=True), 1)

    def test_icons_readme_is_scanned(self):
        t = TempRepo(self)
        t.write("icons/Apple/README.md", "icons/Apple/AppleNews/AppleNews.png\n")
        self.assertEqual(VD.collect_docs(t.root), ["icons/Apple/README.md"])
        self.assertEqual(VD.check_repo(t.root, quiet=True), 1)


class DesignRedlineTests(unittest.TestCase):
    def test_validator_does_not_build_second_source_of_truth(self):
        """只允许「读文档 → 抽路径 → 比对文件系统」，不得引入品牌/分类/别名真值。"""
        import io
        import tokenize

        src = SCRIPT.read_text(encoding="utf-8")
        code_tokens = [
            tok.string
            for tok in tokenize.generate_tokens(io.StringIO(src).readline)
            if tok.type not in (tokenize.COMMENT, tokenize.STRING, tokenize.NL, tokenize.NEWLINE)
        ]
        code = " ".join(code_tokens)
        for forbidden in ("brands.json", "expected_icon_path", "brand_relationships",
                          "import json", "categories.json", "surge-icon"):
            self.assertNotIn(forbidden, code,
                             f"校验器不得依赖 {forbidden}（避免成为第二 SSOT）")

    def test_real_repository_is_clean(self):
        """真实仓库（current-state 文档）必须 0 失效引用。"""
        result = subprocess.run([sys.executable, str(SCRIPT), "--quiet"],
                                cwd=REPO, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
