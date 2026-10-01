#!/usr/bin/env python3
"""文档图标路径引用校验 / Docs concrete icon-path validator（CI: 文档引用组）

目的
----
防止 **current / normative documentation** 出现「用户复制后直接 404」的 concrete icon path。
历史教训：分类/物理层级重构后，`docs/guides/usage.md` 与 `README.md` 的示例仍指向旧路径，
文档照抄即 404，而当时 CI 只校验 README 统计与 SSOT 一致性，无法发现。

定位（红线，禁止越界）
--------------------
    文档  →  抽取 concrete path  →  比对 git 工作树

- **不**读取 `config/brands.json` 建第二份品牌表；
- **不**维护 category / alias 映射；
- **不**自行拼装 canonical path，**不**复制关系引擎逻辑；
- canonical path 的唯一真值仍是 `config/brands.json` + `scripts/brand_relationships.py`。

本脚本只回答一个问题：**文档声称存在的具体文件，是否真的存在。**

范围（显式 include / exclude，不使用关键词段落豁免）
---------------------------------------------------
include（白名单）：
    README.md, AGENTS.md, docs/guides/**/*.md,
    docs/references/brand-naming-contract.md, docs/references/icon-quality-notes.md,
    icons/**/README.md
exclude（黑名单，即使命中 include 也跳过）：
    docs/migrations/**（历史迁移表，旧路径是其记录对象，必须保留）
    docs/references/upstream-history.md
    docs/references/brand-migration.md
    docs/references/category-migration.md
    docs/references/brand-ownership-audit.md（历史审计快照）

> 刻意**不做**「段落里出现 Historical 就跳过」这类基于关键词的豁免——那会让 current 文档
> 用一个词逃过校验。需要豁免时使用下方 KNOWN_MISSING 显式登记（必须带理由）。

路径类型
--------
- concrete（`icons/Communication/Telegram/Telegram.png`）→ 必须存在。
- placeholder（`icons/<category>/<brand>/<brand>.png`）→ 正则天然不匹配（含 `<>`），跳过。
- URL template（`https://raw.githubusercontent.com/.../main/icons/<category>/...`）→ 同上。
- historical（migration / 历史快照中的旧路径）→ 位于 exclude 范围内，不校验。

用法
----
    python3 scripts/ci-validate-docs.py [--root DIR] [--quiet] [--list-files]

退出码：0 = 所有 concrete path 均存在；1 = 存在失效引用或豁免清单失真。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

GROUP_NAME = "文档引用（concrete icon path）"

# --- include / exclude（显式清单，路径相对仓库根） -------------------------------
INCLUDE_EXACT = (
    "README.md",
    "AGENTS.md",
    "docs/references/brand-naming-contract.md",
    "docs/references/icon-quality-notes.md",
)
INCLUDE_GLOBS = (
    "docs/guides/**/*.md",
    "icons/**/README.md",
)
EXCLUDE_GLOBS = (
    "docs/migrations/**",
    "docs/references/upstream-history.md",
    "docs/references/brand-migration.md",
    "docs/references/category-migration.md",
    "docs/references/brand-ownership-audit.md",
)

# 显式豁免：文档中「故意引用不存在路径」的示例（必须写明理由）。
# 值 = {相对路径: {"<path>": "<理由>"}}
# 约束：豁免项**必须仍然不存在**；一旦它变成真实路径，本脚本会报错要求清理（防止豁免清单腐化）。
KNOWN_MISSING = {
    "AGENTS.md": {
        "icons/SpaceXAI/Grok/Grok.png": "§4 禁止清单中的反例路径（该路径明确禁止存在）",
    },
    "docs/references/brand-naming-contract.md": {
        "icons/R/A/B/C/C.png": "通用嵌套示例路径（非真实文件，仅说明层级写法）",
    },
}

# `icons/<...>/<file>.png`；含 <> 的占位符不会匹配
PATH_RE = re.compile(r"icons/(?:[A-Za-z0-9._\-]+/)+[A-Za-z0-9._\-]+\.png")


def is_excluded(rel: str) -> bool:
    """显式黑名单：目录前缀（`.../**`）或精确文件路径。"""
    for pattern in EXCLUDE_GLOBS:
        if pattern.endswith("/**"):
            prefix = pattern[: -len("/**")] + "/"
            if rel == pattern[: -len("/**")] or rel.startswith(prefix):
                return True
        elif rel == pattern:
            return True
    return False


def collect_docs(root: Path) -> list[str]:
    """返回纳入校验的文档相对路径（已应用 include + exclude）。"""
    found: set[str] = set()
    for exact in INCLUDE_EXACT:
        if (root / exact).is_file():
            found.add(exact)
    for pattern in INCLUDE_GLOBS:
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                found.add(path.relative_to(root).as_posix())
    return sorted(p for p in found if not is_excluded(p))


def scan_text(text: str, rel: str, root: Path) -> tuple[list[str], int]:
    """扫描单个文档。

    返回 (violations, checked_path_count)：
      violations 形如 "<rel>:<line>: 不存在的图标路径 <path>"
    """
    violations: list[str] = []
    allowed = KNOWN_MISSING.get(rel, {})
    checked = 0
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in PATH_RE.finditer(line):
            token = match.group(0)
            if token in allowed:
                continue
            checked += 1
            if not (root / token).is_file():
                violations.append(f"{rel}:{lineno}: 引用了不存在的图标路径 {token}")
    return violations, checked


def check_repo(root: Path, quiet: bool = False, list_files: bool = False) -> int:
    """校验整仓文档引用。返回进程退出码。"""
    docs = collect_docs(root)
    violations: list[str] = []
    checked = 0
    for rel in docs:
        text = (root / rel).read_text(encoding="utf-8")
        v, c = scan_text(text, rel, root)
        violations.extend(v)
        checked += c

    # 豁免清单腐化检测：豁免项若已变成真实路径，说明文档已改进，必须清理清单
    stale_allow: list[str] = []
    for rel, entries in KNOWN_MISSING.items():
        for token, reason in entries.items():
            if (root / token).is_file():
                stale_allow.append(f"{rel}: 豁免项 {token} 现已存在（{reason}），请从 KNOWN_MISSING 移除")

    if not quiet:
        print(f"扫描文档（include 白名单 / exclude 黑名单见脚本头部）：{len(docs)} 个文件 / {checked} 处 concrete path")
        if list_files:
            for rel in docs:
                print(f"  · {rel}")

    for item in violations + stale_allow:
        print(f"  ✗ {item}")
    if violations or stale_allow:
        print(f"  {GROUP_NAME}：FAIL（{len(violations)} 处失效引用，{len(stale_allow)} 项豁免失真）")
        return 1
    print(f"  ✓ {GROUP_NAME}：PASS（{len(docs)} 个文档 / {checked} 处 concrete path 全部存在）")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="文档 concrete icon path 引用校验")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent),
                        help="仓库根目录（默认：本脚本的上一级目录）")
    parser.add_argument("--quiet", action="store_true", help="只输出结论与问题")
    parser.add_argument("--list-files", action="store_true", help="列出参与校验的文档")
    args = parser.parse_args(argv)
    return check_repo(Path(args.root).resolve(), quiet=args.quiet, list_files=args.list_files)


if __name__ == "__main__":
    sys.exit(main())
