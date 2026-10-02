#!/usr/bin/env python3
"""统计 icons/ 目录下的 PNG 数量、品牌数、分类数，并更新 README.md 与质量说明的统计。

覆盖范围（2026-09-29 补全）：
  - README badge（icons / brands / categories）
  - README 正文统计句（「当前共 **N** 个 PNG 图标，覆盖 **N** 个品牌，归入 **N** 个…分类」）
  - README 独立仓库句（「当前 N 个图标均为 512×512 PNG」）
  - README 分类表逐行 品牌数/图标数 + 合计行
  - docs/references/icon-quality-notes.md 扫描范围句 + §6 现状表统计行（尺寸 / 模式分布 / 体积，2026-10-01 Phase 3 扩围）

修复历史（静默失同步）：
  1. 统计句正则写死「个分类」结尾，实际正文是「个活跃分类」→ 正则永不命中，
     正文数字长期静默失同步（徽章在更新、正文不动，看起来"脚本跑过了"）。
     修正为「个(?=[^，\n]*分类)」，允许中间修饰词（活跃 / 功能 …）。
  2. 分类表 品牌数/图标数、合计行、icon-quality-notes 扫描范围从未被脚本覆盖，
     只能手工维护 → 纳入自动更新。

2026-10-01 审计修订：
  3. 删除 2 条**永久失效**的正则（`**N 个图标全部经过统一规范化处理**`、
     `**N / N 均为 512×512 Apple 风格圆角**`）——README 已无对应句子（文档重构后
     未同步），保留只会制造「脚本跑过了」的假信号；不恢复旧文案。
  4. icon-quality-notes 扫描范围句正则改为匹配**当前真实文本**并写入实时预留分类。
  5. generated 目标未命中不再只打 ⚠：属于 generated contract 的行（badge / 统计句 /
     活跃分类句 / 独立仓库句 / 分类表行 / 合计行 / 统计口径行 / 生态计数 /
     扫描范围句）缺失时 **print ERROR + exit 1**。
"""
import re
import sys
from pathlib import Path
from collections import Counter

REPO = Path(".")
ICONS = REPO / "icons"
sys.path.insert(0, str((REPO / "scripts").resolve()))
from json_io import JsonLoadError, describe, load_json  # noqa: E402
# 关系引擎必须可用（2026-10-01 Phase 3）：canonical 语义的唯一来源是
# scripts/brand_relationships.py。此前是 broad `except Exception` + 退化为
# `entry.get('canonical')`，会把引擎自身错误吞成"看起来正常"的统计数字。
# 现在：加载失败或执行失败都直接非 0 退出（fail-fast），不做静默 fallback。
# （2026-10-02 维护强化：JSON 读取统一走 json_io，给「路径 + 行列 + 原因」诊断。）
from brand_relationships import is_canonical_brand  # noqa: E402


def ssot_brands():
    """品牌 SSOT（config/brands.json）。统计一律以 SSOT 为准，不从目录层级推导——
    多层物理层级（icons/<category>/<中间父>/<id>/）会让「一级子目录 = 品牌」的
    假设失效（§21/§38：统计必须由程序从 SSOT 动态计算）。

    fail-fast：文件缺失 / JSON 损坏 / 结构非法 / 编码错误一律立即非 0 退出。
    **数据不存在或损坏 ≠ 空数据**——`except: return []` / `doc.get("brands", [])`
    会把 SSOT 故障写成「0 品牌」，让 README 生成"成功"。
    加载失败由 json_io 抛 JsonLoadError（带路径 + 行列 + 原因，main 统一转 exit 1）；
    结构非法在此处显式拒绝（load_json 只保证「合法 JSON」，不保证 schema）。
    """
    doc = load_json(REPO / "config" / "brands.json")
    if not isinstance(doc, dict) or not isinstance(doc.get("brands"), list):
        raise SystemExit("ERROR: 品牌 SSOT config/brands.json 结构非法（应为 {brands: [...]}）")
    return doc["brands"]


def ssot_metrics():
    """显式统计口径（SSOT entities / canonical / icon-backed / pending no-icon / ecosystems）。

    口径必须区分「SSOT 条目」与「有图标的条目」：pending ecosystem 是正式 SSOT 节点
    但没有 PNG，把两者混写成「brands = N」会造成 293/292 口径漂移（2026-10-01 修正）。
    """
    brands = ssot_brands()
    return {
        'ssot_entities': len(brands),
        'canonical_entities': sum(1 for b in brands if is_canonical_brand(b)),
        'icon_backed': sum(1 for b in brands if b.get('icon_path')),
        'pending_no_icon': sum(1 for b in brands if not b.get('icon_path')),
        'ecosystems': sum(1 for b in brands if b.get('entity_type') == 'ecosystem'),
    }


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
    """分类显示名 -> 目录 id（README 表格里写的是 display_name，目录用的是 id）。

    fail-fast：categories.json 缺失/损坏/结构非法一律非 0 退出，
    不再退化为 `{}`（空映射会让分类表行静默错配）。
    加载失败由 json_io 抛 JsonLoadError（main 统一转 exit 1）；
    结构非法在此显式拒绝（`['categories']` 裸下标对合法但错构的 JSON 会 KeyError，
    不如显式诊断清楚）。
    """
    doc = load_json(REPO / 'config/categories.json')
    cs = doc.get('categories') if isinstance(doc, dict) else None
    if not isinstance(cs, list):
        raise SystemExit("ERROR: 分类 SSOT config/categories.json 结构非法（应为 {categories: [...]}）")
    return {c['display_name']: c['id'] for c in cs}


def update_readme(n_png, n_brands, n_cats, cats, spacexai_present=False):
    """更新 README 的 generated 行；返回未命中的 generated 目标名列表。

    spacexai_present：SSOT 中是否存在 SpaceXAI 条目——只有存在时「资产状态句」
    才是必须命中的 generated 行。
    """
    readme = REPO / "README.md"
    s = readme.read_text()
    before = s

    # badge（整行重写：旧正则 [^"]*" 会吞掉结尾引号与后续属性，导致 HTML 损坏）
    s, nb_icons = re.subn(
        r'<img src="https://img\.shields\.io/badge/icons-\d+-blue[^\n]*',
        f'<img src="https://img.shields.io/badge/icons-{n_png}-blue?style=flat-square" alt="Icons Count">',
        s,
    )
    s, nb_brands = re.subn(
        r'<img src="https://img\.shields\.io/badge/brands-\d+-green[^\n]*',
        f'<img src="https://img.shields.io/badge/brands-{n_brands}-green?style=flat-square" alt="Brands Count">',
        s,
    )
    s, nb_cats = re.subn(
        r'<img src="https://img\.shields\.io/badge/categories-\d+-orange[^\n]*',
        f'<img src="https://img.shields.io/badge/categories-{n_cats}-orange?style=flat-square" alt="Categories Count">',
        s,
    )
    n_badge = nb_icons + nb_brands + nb_cats

    # 显式统计口径行 —— 2026-10-01 新增：禁止把「SSOT 条目数」与「有图标条目数」
    # 混写成模糊的「brands = N」。字段口径见 scripts/update-readme-badges.py::ssot_metrics。
    m = ssot_metrics()
    s, n7 = re.subn(
        r'^\*\*仓库统计口径 / Repository metrics\*\*：.*$',
        ('**仓库统计口径 / Repository metrics**：'
         'SSOT entities **{ssot_entities}** · canonical entities **{canonical_entities}** · '
         'icon-backed entities **{icon_backed}** · PNG **{png}** · '
         'pending no-icon entities **{pending_no_icon}** · categories **{cats}** · '
         'ecosystems **{ecosystems}**').format(png=n_png, cats=n_cats, **m),
        s, flags=re.M,
    )

    # 生态根计数（「当前 N 个」）—— 与 SSOT entity_type=ecosystem 实时一致，禁止手工维护
    s, n8 = re.subn(
        r'（拥有自身一级生态分类者，当前 \d+ 个',
        '（拥有自身一级生态分类者，当前 %d 个' % m['ecosystems'],
        s,
    )

    # SpaceXAI 资产状态句（generated）—— 根图标从 pending 变为 official 后必须同步，
    # 且不得再出现「当前无 entity_type 条目」这类旧文。
    _sp = next((b for b in ssot_brands() if b.get('id') == 'SpaceXAI'), None)
    if _sp is not None:
        _ip = _sp.get('icon_path') or '（无物理资产）'
        s, n9 = re.subn(
            r'^(\s*)`SpaceXAI` 资产状态（generated）：.*$',
            r'\1`SpaceXAI` 资产状态（generated）：`icon_status=%s`；`icon_path=%s`。'
            % (_sp.get('icon_status', 'official'), _ip),
            s, flags=re.M,
        )
    else:
        n9 = 0

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

    # 独立图标仓库句（「当前 N 个图标均为 512×512 PNG」）—— 本次新增覆盖
    s, n3 = re.subn(
        r'当前 \d+ 个图标均为 512×512 PNG',
        f'当前 {n_png} 个图标均为 512×512 PNG',
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
    print(f"    命中：badge {n_badge} / 统计句 {n1} / 活跃分类句 {n1b} / 独立仓库句 {n3} "
          f"/ 分类表行 {n5} / 合计行 {n6} / 统计口径行 {n7} "
          f"/ 生态计数 {n8} / SpaceXAI 资产状态句 {n9}")
    # generated contract：以下行缺失即契约破裂（措辞被改 / 行被删），必须让调用方失败
    missing = []
    for name, hits in (("badge", n_badge), ("正文统计句", n1), ("活跃分类句", n1b),
                       ("独立仓库句", n3), ("分类表行", n5), ("合计行", n6),
                       ("统计口径行", n7), ("生态计数", n8)):
        if hits == 0:
            missing.append(name)
    if spacexai_present and n9 == 0:
        missing.append("SpaceXAI 资产状态句")
    return missing


def png_color_type(path):
    """直读 PNG IHDR color type（无第三方依赖）：6 = truecolor+alpha = RGBA。

    与 ci-validate-icons.py 的同一判据必须一致（同一字节、同一含义）。
    """
    with open(path, "rb") as fh:
        head = fh.read(26)
    if len(head) != 26 or head[12:16] != b"IHDR":
        return None
    return head[25]


def update_quality_notes(n_png, n_brands, n_cats, reserved_ids):
    """同步 docs/references/icon-quality-notes.md 的 generated 统计行。

    正则匹配**当前真实文本**（`> 扫描范围：全库 PNG（含 N 个预留空分类 `X`）`）。
    注：文档重构后失效的旧格式（`N 个 PNG（N 个品牌目录 / N 个分类…）`）已删除，
    不恢复旧文案；预留分类变化时本行随 SSOT/文件系统实时更新。

    2026-10-01 Phase 3 扩围：此前只有「扫描范围句」由本脚本生成，§6 现状表的
    尺寸 / 模式分布 / 体积三行既不由脚本生成、也不被 CI 校验，于是长期停留在
    293（实际 294）——一个没有事实源的数字。现在四行全部由磁盘实测推导：
    数量来自 `icons/**/*.png` 枚举，色型来自 PNG IHDR color type 直读，
    体积来自文件字节数。返回值按行分别报告，非空 ⇒ 调用方非 0 退出。
    """
    p = REPO / "docs/references/icon-quality-notes.md"
    if not p.exists():
        print("  · icon-quality-notes.md 不存在，跳过")
        return ["icon-quality-notes（文件不存在）"]
    s = p.read_text(encoding="utf-8")
    old = s
    files = sorted(ICONS.rglob("*.png"))
    sizes = {f: f.stat().st_size for f in files}
    n = len(files)
    rgba = sum(1 for f in files if png_color_type(f) == 6)
    total = sum(sizes.values())
    big = max(files, key=lambda f: sizes[f]) if files else None
    ids = ''.join(' `%s`' % c for c in reserved_ids)
    subs = [
        ("扫描范围句",
         r'> 扫描范围：全库 PNG（含 \d+ 个预留空分类[^）]*）',
         '> 扫描范围：全库 PNG（含 %d 个预留空分类%s）' % (len(reserved_ids), ids)),
        ("尺寸行",
         r'\*\*\d+ / \d+ = 512×512\*\*',
         '**%d / %d = 512×512**' % (n, n)),
        ("模式分布行",
         r'RGBA \d+（其余色型 \d+）',
         'RGBA %d（其余色型 %d）' % (rgba, n - rgba)),
        ("体积行",
         r'合计 ≈ [\d.]+ MB；平均 ≈ ?\d+ ?KB / 最大 ≈? ?\d+ ?KB（[\d,]+ B，`[^`]+`）',
         '合计 ≈ %.1f MB；平均 ≈%.0fKB / 最大 %.0fKB（%s B，`%s`）' % (
             total / 1e6,
             (total / n / 1024.0) if n else 0.0,
             (sizes[big] / 1024.0) if big else 0.0,
             '{:,}'.format(sizes[big]) if big else '0',
             big.relative_to(REPO).as_posix() if big else '')),
    ]
    missing = []
    for label, pattern, repl in subs:
        s, k = re.subn(pattern, lambda m, _r=repl: _r, s)
        print(f"  {'✓' if k else '⚠'} icon-quality-notes {label}：命中 {k}")
        if not k:
            missing.append("icon-quality-notes %s" % label)
    if s != old:
        p.write_text(s, encoding="utf-8")
    return missing


def main():
    try:
        n_png, n_brands, n_cats = count()
        cats = per_category()
        reserved_ids = sorted(cid for cid, (b, i) in cats.items() if b == 0 and i == 0)
        spacexai_present = any(b.get('id') == 'SpaceXAI' for b in ssot_brands())
        print(f"统计：{n_png} PNG / {n_brands} 品牌 / {n_cats} 分类"
              f"（预留空分类 {len(reserved_ids)} 个）")
        # try 覆盖到写入前最后一次 SSOT 读取（display_to_id 读 categories.json）：
        # 此前只包 count()/per_category()，categories.json 故障会漏出裸 Traceback
        # 而非统一诊断（2026-10-02 rebase 合并 #16/#18 时由 mutation 矩阵暴露）。
        # README 写入在 display_to_id() 之后，故此处抛错时未产生任何半写。
        missing = update_readme(n_png, n_brands, n_cats, cats, spacexai_present)
        missing += update_quality_notes(n_png, n_brands, n_cats, reserved_ids)
    except JsonLoadError as exc:
        print('ERROR: %s' % describe(exc, 'SSOT'))
        print('       SSOT 不可读时统计/写入一律中止（不得以 0 覆盖文档）。')
        return 1
    if missing:
        print("ERROR: 以下 generated 目标未命中（README / docs 措辞可能已改，或对应行被删除）：")
        for name in missing:
            print("    - %s" % name)
        print("       生成器不再静默通过：请同步修正本脚本正则，或恢复对应 generated 行。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
