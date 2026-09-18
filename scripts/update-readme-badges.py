#!/usr/bin/env python3
"""统计 icons/ 目录下的 PNG 数量、品牌数、分类数，并更新 README.md 的 badge。"""
import re
from pathlib import Path
from collections import Counter

REPO = Path(".")
ICONS = REPO / "icons"

def count():
    files = list(ICONS.rglob("*.png"))
    brands = Counter()
    categories = set()
    for p in files:
        rel = p.relative_to(ICONS)
        parts = rel.parts
        if len(parts) >= 2:
            categories.add(parts[0])
            brands[(parts[0], parts[1])] += 1
    return len(files), len(brands), len(categories)

def update_readme(n_png, n_brands, n_cats):
    readme = REPO / "README.md"
    s = readme.read_text()
    # badge
    s = re.sub(
        r'<img src="https://img\.shields\.io/badge/icons-\d+-blue[^"]*"',
        f'<img src="https://img.shields.io/badge/icons-{n_png}-blue',
        s,
    )
    s = re.sub(
        r'<img src="https://img\.shields\.io/badge/brands-\d+-green[^"]*"',
        f'<img src="https://img.shields.io/badge/brands-{n_brands}-green',
        s,
    )
    s = re.sub(
        r'<img src="https://img\.shields\.io/badge/categories-\d+-orange[^"]*"',
        f'<img src="https://img.shields.io/badge/categories-{n_cats}-orange',
        s,
    )
    # 正文统计句
    s = re.sub(
        r'当前共 \*\*\d+\*\* 个 PNG 图标，覆盖 \*\*\d+\*\* 个品牌，归入 \*\*\d+\*\* 个分类',
        f'当前共 **{n_png}** 个 PNG 图标，覆盖 **{n_brands}** 个品牌，归入 **{n_cats}** 个分类',
        s,
    )
    # 规范化完成句
    s = re.sub(
        r'\*\*\d+ / \d+ 均为 512×512 Apple 风格圆角',
        f'**{n_png} / {n_png}** 均为 512×512 Apple 风格圆角',
        s,
    )
    readme.write_text(s)
    print(f"✓ README badge 已更新：{n_png} 图标 / {n_brands} 品牌 / {n_cats} 分类")

if __name__ == "__main__":
    n_png, n_brands, n_cats = count()
    print(f"统计：{n_png} PNG / {n_brands} 品牌 / {n_cats} 分类")
    update_readme(n_png, n_brands, n_cats)
