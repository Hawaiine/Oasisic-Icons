#!/usr/bin/env python3
"""统计 icons/ 目录下的 PNG 数量、品牌数、分类数，并更新 README.md 与质量说明的统计。

覆盖范围（2026-09-29 补全）：
  - README badge（icons / brands / categories）
  - README 正文统计句（「当前共 **N** 个 PNG 图标，覆盖 **N** 个品牌，归入 **N** 个…分类」）
  - README 独立仓库句（「当前 N 个图标均为 512×512 PNG」）
  - README 分类表逐行 品牌数/图标数 + 合计行
  - docs/references/icon-quality-notes.md 扫描范围句

历史上失效的两处（本次修复）：
  1. 统计句正则写死「个分类」结尾，实际正文是「个活跃分类」→ 正则永不命中，
     正文数字长期静默失同步（徽章在更新、正文不动，看起来"脚本跑过了"）。
     修正为「个(?=[^，\n]*分类)」，允许中间修饰词（活跃 / 功能 …）。
  2. 分类表 品牌数/图标数、合计行、icon-quality-notes 扫描范围从未被脚本覆盖，
     只能手工维护 → 本次纳入自动更新。
"""
import json
import re
from pathlib import Path
from collections import Counter

REPO = Path(".")
ICONS = REPO / "icons"


def ssot_brands():
    """品牌 SSOT（config/brands.json）。统计一律以 SSOT 为准，不从目录层级推导——
    多层物理层级（icons/<category>/<中间父>/<id>/）会让「一级子目录 = 品牌」的
    假设失效（§21/§38：统计必须由程序从 SSOT 动态计算）。"""
    try:
        doc = json.loads((REPO / "config/brands.json").read_text(encoding="utf-8"))
    except Exception:
        return []
    return doc.get("brands", [])


def count():
    files = list(ICONS.rglob("*.png"))
    brands = ssot_brands()
    # 分类数 = icons/ 下目录总数（含预留空分类），不能从 PNG 推导
    categories = {p.name for p in ICONS.iterdir() if p.is_dir()}
    return len(files), len(brands), len(categories)


def per_category():
    """分类 -> (品牌数, 图标数)；品牌数来自 SSOT，图标数来自递归扫描。

    预留空分类（无 PNG）返回 (0, 0)。"""
    by_cat = Counter(b.get("category") for b in ssot_brands())
    cats = {}
    for cat_dir in sorted(p for p in ICONS.iterdir() if p.is_dir()):
        pngs = list(cat_dir.rglob("*.png"))
        cats[cat_dir.name] = (by_cat.get(cat_dir.name, 0), len(pngs))
    return cats


def display_to_id():
    """分类显示名 -> 目录 id（README 表格里写的是 display_name，目录用的是 id）。"""
    try:
        cs = json.loads((REPO / 'config/categories.json').read_text(encoding='utf-8'))['categories']
    except Exception:
        return {}
    return {c['display_name']: c['id'] for c in cs}


def update_readme(n_png, n_brands, n_cats, cats):
    readme = REPO / "README.md"
    s = readme.read_text()
    before = s

    # badge（整行重写：旧正则 [^"]*" 会吞掉结尾引号与后续属性，导致 HTML 损坏）
    s = re.sub(
        r'<img src="https://img\.shields\.io/badge/icons-\d+-blue[^\n]*',
        f'<img src="https://img.shields.io/badge/icons-{n_png}-blue?style=flat-square" alt="Icons Count">',
        s,
    )
    s = re.sub(
        r'<img src="https://img\.shields\.io/badge/brands-\d+-green[^\n]*',
        f'<img src="https://img.shields.io/badge/brands-{n_brands}-green?style=flat-square" alt="Brands Count">',
        s,
    )
    s = re.sub(
        r'<img src="https://img\.shields\.io/badge/categories-\d+-orange[^\n]*',
        f'<img src="https://img.shields.io/badge/categories-{n_cats}-orange?style=flat-square" alt="Categories Count">',
        s,
    )

    # 正文统计句 —— 修复点 1：允许「个<修饰>分类」（活跃分类 / 功能分类…）
    # 旧正则 r'…归入 \*\*\d+\*\* 个分类' 永不命中，正文数字长期失同步。
    s, n1 = re.subn(
        r'当前共 \*\*\d+\*\* 个 PNG 图标，覆盖 \*\*\d+\*\* 个品牌，归入 \*\*\d+\*\* 个(?=[^，\n]*分类)',
        f'当前共 **{n_png}** 个 PNG 图标，覆盖 **{n_brands}** 个品牌，归入 **{n_cats}** 个',
        s,
    )

    # 活跃分类数（「其中 N 个活跃」）—— 2026-09-30 补：此前写死，Finance 等预留
    # 空分类增减后正文数字失同步。活跃 = 目录存在且有 ≥1 个 PNG 的分类。
    active = sum(1 for b, i in cats.values() if i > 0)
    s, n1b = re.subn(
        r'（其中 \d+ 个活跃',
        f'（其中 {active} 个活跃',
        s,
    )

    # 全量规范化句
    s, n2 = re.subn(
        r'\*\*\d+ 个图标全部经过统一规范化处理\*\*',
        f'**{n_png} 个图标全部经过统一规范化处理**',
        s,
    )

    # 独立图标仓库句（「当前 N 个图标均为 512×512 PNG」）—— 本次新增覆盖
    s, n3 = re.subn(
        r'当前 \d+ 个图标均为 512×512 PNG',
        f'当前 {n_png} 个图标均为 512×512 PNG',
        s,
    )

    # 规范化完成句
    s, n4 = re.subn(
        r'\*\*\d+ / \d+ 均为 512×512 Apple 风格圆角',
        f'**{n_png} / {n_png} 均为 512×512 Apple 风格圆角',
        s,
    )

    # 分类表逐行 —— 本次新增覆盖：| <emoji> Name | 说明 | 品牌数 | 图标数 |
    # 行首允许 emoji / 符号前缀；分类名取纯 ASCII 标识（与目录名一致）；
    # 说明列用 [^|]* 惰性匹配，避免贪婪吞并后续列。
    d2i = display_to_id()

    def fix_row(m):
        prefix, name, gap, desc, sep = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        actual = cats.get(d2i.get(name, name))
        if actual is None:
            return m.group(0)          # 表里有、目录里没有 → 保持原样，不臆改
        b_real, i_real = actual
        # sep 只含管道符前的空格；管道符后的空格由 \s*\d+ 未捕获吞掉。
        # 重建时显式补回单空格（表格统一单空格风格），保证逐字节幂等。
        return f'{prefix}{name}{gap}{desc}{sep} {b_real} | {i_real} |'

    # 行内空白一律 [ \t]（禁用 \s）：\s*$ 会把表格后的换行/空行一并吞进匹配，
    # 重建后空行丢失（已在 2026-09-29 测试中复现）。
    # 分类名允许内部空格（Cloud Storage / Warner Bros. Discovery / Sony 等）
    s, n5 = re.subn(
        r'^(\|[ \t]*(?:[^\w\s|]+[ \t]*)?)([A-Za-z][\w.]*(?:[ \t]+[A-Za-z][\w.]*)*)([ \t]*\|[ \t]*)([^|]*?)([ \t]*\|)[ \t]*\d+([ \t]*\|)[ \t]*\d+([ \t]*\|)[ \t]*$',
        fix_row,
        s,
        flags=re.M,
    )

    # 合计行：| **合计** | — | **N** | **N** |
    s, n6 = re.subn(
        r'^\|[ \t]*\*\*合计\*\*[ \t]*\|[ \t]*—[ \t]*\|[ \t]*\*\*\d+\*\*[ \t]*\|[ \t]*\*\*\d+\*\*[ \t]*\|[ \t]*$',
        f'| **合计** | — | **{n_brands}** | **{n_png}** |',
        s, flags=re.M,
    )

    if s != before:
        readme.write_text(s)

    print(f"✓ README 已更新：{n_png} 图标 / {n_brands} 品牌 / {n_cats} 分类")
    print(f"    命中：统计句 {n1} / 活跃分类句 {n1b} / 规范化句 {n2} / 独立仓库句 {n3} "
          f"/ 规范化完成句 {n4} / 分类表行 {n5} / 合计行 {n6}")
    for name, hits in (("统计句", n1), ("活跃分类句", n1b), ("分类表", n5), ("合计行", n6)):
        if hits == 0:
            print(f"    ⚠ {name}未命中 —— README 措辞/格式可能已改，请同步修正本脚本正则")


def update_quality_notes(n_png, n_brands, n_cats, reserved):
    """同步 docs/references/icon-quality-notes.md 的扫描范围句 —— 本次新增覆盖。"""
    p = REPO / "docs/references/icon-quality-notes.md"
    if not p.exists():
        print("  · icon-quality-notes.md 不存在，跳过")
        return
    s = p.read_text()
    old = s
    s, n = re.subn(
        r'> 扫描范围：\d+ 个 PNG（\d+ 个品牌目录 / \d+ 个分类，含 \d+ 个预留空分类）',
        f'> 扫描范围：{n_png} 个 PNG（{n_brands} 个品牌目录 / {n_cats} 个分类，含 {reserved} 个预留空分类）',
        s,
    )
    if s != old:
        p.write_text(s)
    print(f"  {'✓' if n else '⚠'} icon-quality-notes 扫描范围句：命中 {n}")


if __name__ == "__main__":
    n_png, n_brands, n_cats = count()
    cats = per_category()
    reserved = sum(1 for b, i in cats.values() if b == 0 and i == 0)
    print(f"统计：{n_png} PNG / {n_brands} 品牌 / {n_cats} 分类（预留空分类 {reserved} 个）")
    update_readme(n_png, n_brands, n_cats, cats)
    update_quality_notes(n_png, n_brands, n_cats, reserved)
