#!/usr/bin/env python3
"""generate-brand-glossary.py — 由 config/brands.json 派生 docs/references/brand-glossary.md

规则：
  - 一个品牌一行：`| <id> | <display_name> |`
  - 按 id 的 ASCII 序分节（大写字母 → 小写字母 → 非字母归入 `#`），节顺序：`#` 在最前，其后 A–Z
  - 抬头统计句中的品牌数按 brands.json 实时计算
CI 校验（Glossary 组）要求本文件与 brands.json 双向一致，任何手工改动都会被拦截。
"""
import collections
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BRANDS = REPO / "config/brands.json"
OUT = REPO / "docs/references/brand-glossary.md"

TITLE = "# 品牌术语表 / Brand Glossary\n"
NOTE = ("> 本文件由 `config/brands.json` 派生（CI 校验一致性）。\n"
        "> 共 **{n}** 个品牌 / 文件夹标识。Technical ID 为目录名；Display Name 为官方真实品牌名。\n")
HEADER = ("| 英文文件夹 / Folder | 中文显示名 / Display Name |\n"
          "|---------------------|--------------------------|\n")


def build(brands):
    groups = collections.defaultdict(list)
    for e in sorted(brands, key=lambda x: x["id"]):
        k = e["id"][0].upper()
        groups[k if k.isalpha() else "#"].append(e)

    parts = [TITLE, NOTE.format(n=len(brands))]
    for key in ["#"] + [chr(c) for c in range(65, 91)]:
        if not groups.get(key):
            continue
        parts.append("\n## %s\n\n" % key)
        parts.append(HEADER)
        for e in groups[key]:
            parts.append("| %s | %s |\n" % (e["id"], e["display_name"]))
    return "".join(parts)


def main():
    brands = json.loads(BRANDS.read_text(encoding="utf-8"))["brands"]
    text = build(brands)
    old = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    if old != text:
        OUT.write_text(text, encoding="utf-8")
        print("✓ 已生成 %s（%d 个品牌）" % (OUT.relative_to(REPO), len(brands)))
    else:
        print("✓ %s 已是最新（%d 个品牌，幂等）" % (OUT.relative_to(REPO), len(brands)))


if __name__ == "__main__":
    main()
