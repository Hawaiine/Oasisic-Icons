#!/usr/bin/env python3
"""Oasisic-Icons CI 校验（按验证组报告，结构规范 icons/<分类>/<品牌>/<文件>.png）

验证组（Validation Groups）：
  1. PNG integrity        文件可被 Pillow 正常解码
  2. Image spec           512×512、RGBA、四角 alpha=0（圆角卡样式图标要求）
  3. Naming               默认图标 <品牌名>.png 存在；变体 <品牌名>NN.png 两位零填充；
                          无 -1/-2/_1 旧式命名；无分类根目录扁平 png；品牌文件夹非空
  4. Category             icons/ 目录 ⊆ categories.json 白名单；active 分类在磁盘存在
  5. Canonical uniqueness 同一品牌名不得出现在两个分类
  6. SHA-256 uniqueness   图片内容相同即视为重复图标，直接失败
  7. Brands SSOT          brands.json：id 唯一、icon_path 唯一、category 合法、
                          category 与目录一致、icon_path 与保存值精确一致
                          （icons/<category>/<id>/<id>.png）、parent_brand 存在/非自指/无环、
                          entity_type 合法、磁盘与 JSON 双向一一对应
  8. Surge JSON           surge-icon.json 条目数 == 磁盘 PNG 数、URL 对应真实文件、无 jsDelivr
  9. Glossary             brand-glossary.md 与 brands.json 双向一致
 10. Legacy paths         README/docs/scripts/.github/config 禁止引用已删除的 legacy 路径
                          （docs/migrations/ 内的历史记录性引用除外）

全部组 PASS 输出 'Validation Groups: N / All groups: PASS' 并以 exit 0 结束；
任一组失败输出全部问题并以 exit 1 结束。
"""
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ICONS = Path('icons')
JSON_PATH = Path('config/surge-icon.json')
CATS_PATH = Path('config/categories.json')
BRANDS_PATH = Path('config/brands.json')
GLOSS_PATH = Path('docs/references/brand-glossary.md')

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

groups = {}  # group name -> list of errors

def fail(group, msg):
    groups.setdefault(group, []).append(msg)


# ---------- 扫描 ----------
all_pngs = sorted(ICONS.rglob('*.png'))
if not all_pngs:
    fail('PNG integrity', 'icons/ 下没有任何 PNG 文件')

# ---------- 1/2. PNG 解码 + 尺寸/模式/四角 alpha ----------
for p in all_pngs:
    if not HAVE_PIL:
        fail('PNG integrity', 'Pillow 不可用，无法解码校验: %s' % p)
        continue
    b = p.read_bytes()
    if len(b) < 50 or not b.startswith(b'\x89PNG\r\n\x1a\n'):
        fail('PNG integrity', '非法图标（非 PNG 或过小）: %s (size=%d)' % (p, len(b)))
        continue
    try:
        with Image.open(p) as im:
            im.load()
            spec = (im.size, im.mode)
            corners = None
            if im.size == (512, 512) and im.mode == 'RGBA':
                corners = [im.getpixel((x, y))[3]  # type: ignore[call-overload,index]
                           for x, y in ((0, 0), (511, 0), (0, 511), (511, 511))]
    except Exception as e:
        fail('PNG integrity', '解码失败: %s (%s)' % (p, str(e)[:60]))
        continue
    if spec[0] != (512, 512):
        fail('Image spec', '尺寸非 512×512: %s %s' % (p, '×'.join(map(str, spec[0]))))
    if spec[1] != 'RGBA':
        fail('Image spec', '模式非 RGBA: %s (%s)' % (p, spec[1]))
    if corners is not None and any(c != 0 for c in corners):
        fail('Image spec', '四角 alpha 非 0: %s %s' % (p, corners))

# ---------- 3. Naming / 结构 ----------
brand_dirs = defaultdict(list)
for cat_dir in sorted(ICONS.iterdir()):
    if not cat_dir.is_dir():
        continue
    for item in sorted(cat_dir.iterdir()):
        if item.is_file() and item.suffix == '.png':
            fail('Naming', '扁平文件（应放入品牌文件夹）: %s' % item)
            continue
        if not item.is_dir():
            continue
        pngs = sorted(f for f in item.iterdir() if f.is_file() and f.suffix == '.png')
        if not pngs:
            fail('Naming', '空的品牌文件夹（无 PNG）: %s' % item)
        brand_dirs[item] = pngs

for brand_dir, pngs in brand_dirs.items():
    brand = brand_dir.name
    names = [f.name for f in pngs]
    if '%s.png' % brand not in names:
        fail('Naming', '缺少默认图标 %s/%s.png' % (brand_dir, brand))
    for name in names:
        if name == '%s.png' % brand:
            continue
        if re.search(r'[-_]\d+\.png$', name):
            fail('Naming', '旧式连字符/下划线变体命名: %s/%s' % (brand_dir, name))
            continue
        if not re.fullmatch(re.escape(brand) + r'\d{2}\.png', name):
            fail('Naming', '变体命名不规范（应为 %s01.png 形式）: %s/%s' % (brand, brand_dir, name))

# ---------- 4. Category 白名单 ----------
cats = []
if not CATS_PATH.exists():
    fail('Category', '缺少 %s（分类 SSOT）' % CATS_PATH)
else:
    cats = json.loads(CATS_PATH.read_text(encoding='utf-8'))['categories']
    cat_ids = {c['id'] for c in cats}
    disk_cats = {d.name for d in ICONS.iterdir() if d.is_dir()}
    for c in sorted(disk_cats - cat_ids):
        fail('Category', '分类不在 SSOT 白名单中（icons/%s）: 请更新 config/categories.json' % c)
    for c in cats:
        if c.get('status', 'active') == 'active' and c['id'] not in disk_cats:
            fail('Category', 'SSOT 声明的 active 分类在磁盘不存在: %s' % c['id'])

# ---------- 5. Canonical Brand 唯一 ----------
brand_to_cats = defaultdict(set)
for brand_dir in brand_dirs:
    brand_to_cats[brand_dir.name].add(brand_dir.parent.name)
for brand, cats_ in sorted(brand_to_cats.items()):
    if len(cats_) > 1:
        fail('Canonical uniqueness',
             'Canonical Brand 重复: %s 同时存在于 %s（只允许一个分类）' % (brand, sorted(cats_)))

# ---------- 6. SHA-256 唯一 ----------
hash_to_paths = defaultdict(list)
for p in all_pngs:
    hash_to_paths[hashlib.sha256(p.read_bytes()).hexdigest()].append(str(p))
for h, paths in sorted(hash_to_paths.items()):
    if len(paths) > 1:
        fail('SHA-256 uniqueness', '重复图标内容（SHA-256=%s…）: %s' % (h[:12], ' / '.join(paths)))

# ---------- 7. brands.json SSOT ----------
ENTITY_TYPES = {'ecosystem', 'product_brand', 'country', 'system_icon', 'tool_app'}
ssot = {}
aliases = set()
bdata = []
if not BRANDS_PATH.exists():
    fail('Brands SSOT', '缺少 %s（品牌 SSOT）' % BRANDS_PATH)
else:
    brands_doc = json.loads(BRANDS_PATH.read_text(encoding='utf-8'))
    if not isinstance(brands_doc, dict):
        fail('Brands SSOT', 'brands.json 根必须是对象 {brands: [...]}')
        brands_doc = {'brands': []}
    aliases = set(brands_doc.get('parent_brands_without_icon', []))
    bdata = brands_doc.get('brands', [])
    seen_paths = set()
    for e in bdata:
        bid = e.get('id', '')
        if bid in ssot:
            fail('Brands SSOT', '品牌 ID 重复: %s' % bid)
        ssot[bid] = e
        ip = e.get('icon_path', '')
        if ip in seen_paths:
            fail('Brands SSOT', 'icon_path 重复: %s' % ip)
        seen_paths.add(ip)
        cat = e.get('category', '')
        if cats and cat not in {c['id'] for c in cats}:
            fail('Brands SSOT', '引用未知分类: %s (%s)' % (cat, bid))
        expected = 'icons/%s/%s/%s.png' % (cat, bid, bid)
        if ip != expected:
            fail('Brands SSOT', 'icon_path 与 canonical 规则不一致: %s 应为 %s' % (ip, expected))
        elif not Path(ip).exists():
            fail('Brands SSOT', 'icon_path 文件不存在: %s' % ip)
        elif Path(ip).parent.name != bid:
            fail('Brands SSOT', 'category 与目录不一致: %s (%s)' % (ip, bid))
        et = e.get('entity_type', '')
        if et not in ENTITY_TYPES:
            fail('Brands SSOT', 'entity_type 非法: %s (%s, 允许 %s)' % (et, bid, sorted(ENTITY_TYPES)))
    # parent_brand：存在、非自指、无环
    for bid, e in ssot.items():
        parent = e.get('parent_brand')
        if not parent:
            continue
        if parent == bid:
            fail('Brands SSOT', 'parent_brand 自指: %s' % bid)
            continue
        if parent not in ssot:
            # 允许：父品牌尚无自身图标（记录于 parent_brands_without_icon）
            if parent not in aliases:
                fail('Brands SSOT', 'parent_brand 不存在: %s -> %s' % (bid, parent))
            continue
        chain, seen = [bid], {bid}
        cur = parent
        while cur in ssot and ssot[cur].get('parent_brand'):
            cur = ssot[cur]['parent_brand']
            if cur in seen:
                fail('Brands SSOT', 'parent_brand 循环: %s' % ' -> '.join(chain + [cur]))
                break
            seen.add(cur)
            chain.append(cur)
        else:
            if cur not in ssot:
                fail('Brands SSOT', 'parent_brand 链末端不存在: %s' % ' -> '.join(chain + [cur]))
    disk_brands = {str(bd.relative_to(ICONS)) for bd in brand_dirs}
    ssot_rel = {Path(e['icon_path']).parent.relative_to('icons').as_posix() for e in bdata}
    # 允许的「无自身 icon 的父品牌」（仅记录归属关系，图标缺失见 docs 审计记录）
    aliases = set()
    if isinstance(json.loads(BRANDS_PATH.read_text(encoding='utf-8')), dict):
        aliases = set(json.loads(BRANDS_PATH.read_text(encoding='utf-8')).get('parent_brands_without_icon', []))
    for rel in sorted(disk_brands - ssot_rel):
        fail('Brands SSOT', '磁盘品牌不在 brands.json: icons/%s' % rel)
    for rel in sorted(ssot_rel - disk_brands):
        fail('Brands SSOT', 'brands.json 品牌在磁盘不存在: %s' % rel)

# ---------- 8. surge-icon.json ----------
entries = []
if not JSON_PATH.exists():
    fail('Surge JSON', '缺少 %s' % JSON_PATH)
else:
    entries = json.loads(JSON_PATH.read_text(encoding='utf-8')).get('icons', [])
    if len(entries) != len(all_pngs):
        fail('Surge JSON', '条目数不一致: surge-icon.json=%d, 磁盘 PNG=%d' % (len(entries), len(all_pngs)))
    for it in entries:
        url = it.get('url', '')
        if '/icons/' not in url:
            fail('Surge JSON', 'URL 缺少 /icons/: %s' % url)
            continue
        if 'jsdelivr' in url.lower():
            fail('Surge JSON', 'URL 使用了 jsDelivr（禁止）: %s' % url)
            continue
        if not Path(url.split('main/', 1)[-1]).exists():
            fail('Surge JSON', 'JSON 引用但文件不存在: %s' % url)

# ---------- 9. Glossary ----------
if not GLOSS_PATH.exists():
    fail('Glossary', '缺少 %s' % GLOSS_PATH)
else:
    gloss = set()
    for line in GLOSS_PATH.read_text(encoding='utf-8').splitlines():
        m = re.match(r'^\|\s*([\w.\-]+)\s*\|\s*([^|]+?)\s*\|\s*$', line)
        if m and m.group(1) not in ('英文文件夹',) and m.group(1)[0].isalnum():
            gloss.add(m.group(1))
    ssot_ids = set(ssot)
    for b in sorted(ssot_ids - gloss):
        fail('Glossary', '缺失品牌: %s' % b)
    for b in sorted(gloss - ssot_ids):
        fail('Glossary', '多余品牌（brands.json 无）: %s' % b)

# ---------- 10. Legacy paths（历史引用仅允许在 docs/migrations/） ----------
# 用拼接构造模式串，避免 CI 脚本被自身扫描命中
LEGACY_PATTERNS = ['icons/%s/' % name for name in
                   ('Dev' + 'Ops', 'Dri' + 've', 'Gene' + 'ral', 'Too' + 'l')]
scan_dirs = ['README.md', 'docs', 'scripts', '.github', 'config']
for d in scan_dirs:
    root = Path(d)
    if not root.exists():
        continue
    targets = [root] if root.is_file() else [f for f in root.rglob('*') if f.is_file()]
    for f in targets:
        try:
            text = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        rel = str(f)
        if rel.startswith('docs/migrations/'):
            continue  # 迁移文档的历史性引用允许
        for pat in LEGACY_PATTERNS:
            for m in re.finditer(re.escape(pat), text):
                line_no = text.count('\n', 0, m.start()) + 1
                fail('Legacy paths', '%s:%d 引用 legacy 路径 %s' % (rel, line_no, pat))

# ---------- 11. README 分类表结构 ----------
# header / separator / 全量覆盖 / 无重复 / 顺序 / 计数
README_TABLE_TITLE = '图标分类列表'
if not Path('README.md').exists():
    fail('README 表格', '缺少 README.md')
else:
    readme = Path('README.md').read_text(encoding='utf-8')
    ri = readme.find(README_TABLE_TITLE)
    if ri < 0:
        fail('README 表格', '未找到 %s 小节' % README_TABLE_TITLE)
    else:
        rj = readme.find('\n## ', ri + len(README_TABLE_TITLE))
        if rj < 0:
            rj = readme.find('\n### ', ri + len(README_TABLE_TITLE))
        rseg = readme[ri:rj if rj > 0 else len(readme)]
        trows = [l for l in rseg.splitlines() if l.strip().startswith('|')]
        if not trows:
            fail('README 表格', '分类小节内没有任何表格行')
        else:
            header = trows[0]
            if '分类' not in header or '品牌数' not in header:
                fail('README 表格', '表头非法（应为 分类/说明/品牌数/图标数）: %s' % header.strip())
            if len(trows) < 2 or not re.match(r'^\|[\s\-:|]+\|$', trows[1].strip()):
                fail('README 表格', '缺少 header 后的分隔行 |---|')
            data_rows = [r for r in trows[2:] if r.strip() != '|']
            # 每行 4 列 + 数字
            parsed = []
            for r in data_rows:
                cells = [c.strip() for c in r.strip().strip('|').split('|')]
                if len(cells) != 4:
                    fail('README 表格', '列数 != 4: %s' % r.strip())
                    continue
                name = cells[0].split(' ', 1)[1] if ' ' in cells[0] else cells[0]
                if cells[2].startswith('**') or '合计' in name:
                    continue  # 合计行单独校验
                if not (cells[2].isdigit() and cells[3].isdigit()):
                    fail('README 表格', '计数列非数字: %s' % r.strip())
                    continue
                parsed.append((name, int(cells[2]), int(cells[3])))
            cat_by_name = {c['display_name']: c for c in cats}
            seen = set()
            for name, nb, ni in parsed:
                if name in seen:
                    fail('README 表格', '分类重复: %s' % name)
                seen.add(name)
                if name not in cat_by_name:
                    fail('README 表格', '未知分类: %s' % name)
            for c in cats:
                if c['display_name'] not in seen:
                    fail('README 表格', '缺失分类: %s' % c['display_name'])
            # 顺序与 categories.json 一致
            if [n for n, _, _ in parsed] != [c['display_name'] for c in cats]:
                fail('README 表格', '表格顺序与 categories.json 不一致')
            # 计数与真实数据一致
            brand_by_cat = {}
            for e in bdata:
                brand_by_cat[e['category']] = brand_by_cat.get(e['category'], 0) + 1
            icon_by_cat = {}
            for p in all_pngs:
                c = str(p.relative_to(ICONS)).split('/')[0]
                icon_by_cat[c] = icon_by_cat.get(c, 0) + 1
            for name, nb, ni in parsed:
                cobj = cat_by_name.get(name)
                if not cobj:
                    continue
                cid = cobj['id']
                if nb != brand_by_cat.get(cid, 0) or ni != icon_by_cat.get(cid, 0):
                    fail('README 表格', '%s 计数不符: 表=%d/%d 实际=%d/%d' %
                         (name, nb, ni, brand_by_cat.get(cid, 0), icon_by_cat.get(cid, 0)))

# ---------- 12. 生态一致性（动态：children ≥ 2 → 一级生态目录） ----------
# 统一硬规则：一个 parent_brand 拥有 ≥2 个 Canonical Child Brands 时，
# 必须存在对应一级生态分类（type=ecosystem），子品牌统一归入该分类。
# 反向：type=ecosystem 的分类必须对应 ≥2 children 的父品牌。
# 白名单 parent_brands_without_icon 仅表示无 root icon，不豁免目录规则。
cat_by_id = {c['id']: c for c in cats}
brand_by_id_cat = {b['id']: b.get('category') for b in bdata}
children_of = {}
for e in bdata:
    p = e.get('parent_brand')
    if p:
        children_of.setdefault(p, []).append(e['id'])
eco_cat_ids = {c['id'] for c in cats if c.get('type') == 'ecosystem'}
# (a) 白名单纯净：不得含已有 canonical icon 的品牌
for a in aliases:
    if a in ssot:
        fail('生态一致性', 'parent_brands_without_icon 含已有 icon 的品牌: %s' % a)
# (b) 正向：children ≥ 2 → 必须有一级生态分类
for p, chs in children_of.items():
    if len(chs) < 2:
        continue
    if p not in eco_cat_ids:
        fail('生态一致性', '≥2 子品牌但无一级生态分类: %s (%d 子)' % (p, len(chs)))
        continue
    parent = ssot.get(p)
    if not parent:
        fail('生态一致性', '生态分类 %s 无对应品牌条目' % p)
        continue
    if parent.get('entity_type') != 'ecosystem':
        fail('生态一致性', '生态分类 %s 的父品牌 entity_type 应为 ecosystem: 实际 %s'
             % (p, parent.get('entity_type')))
    if parent.get('category') != p:
        fail('生态一致性', '父品牌 %s 的 category 应为自身 %s: 实际 %s'
             % (p, p, parent.get('category')))
    # 有 root icon：路径必须在生态分类内；无 root icon：须登记白名单
    if p in ssot:
        ipath = ssot[p].get('icon_path', '')
        if ipath and not ipath.startswith('icons/%s/' % p):
            fail('生态一致性', '父品牌 %s 的 icon 不在生态目录内: %s' % (p, ipath))
        if not ipath and p not in aliases:
            fail('生态一致性', '父品牌 %s 无 icon 但未登记白名单' % p)
    elif p not in aliases:
        fail('生态一致性', '父品牌 %s 无品牌条目也未登记白名单' % p)
    # (c) 每个子品牌必须保留 parent_brand 且 category 归入生态分类
    for c2 in chs:
        ce = ssot.get(c2)
        if not ce:
            continue
        if ce.get('parent_brand') != p:
            fail('生态一致性', '子品牌 %s 的 parent_brand 应为 %s: 实际 %s'
                 % (c2, p, ce.get('parent_brand')))
        if ce.get('category') != p:
            fail('生态一致性', '子品牌 %s 的 category 应为 %s: 实际 %s'
                 % (c2, p, ce.get('category')))
# (d) 反向：ecosystem 分类必须对应 ≥2 children 的父品牌
for cid in eco_cat_ids:
    if len(children_of.get(cid, [])) < 2:
        fail('生态一致性', '生态分类 %s 对应父品牌子品牌数 <2' % cid)
    if cid not in ssot:
        fail('生态一致性', '生态分类 %s 无对应品牌条目' % cid)
# (e) entity_type=ecosystem 必须拥有自身一级分类（无孤儿生态实体）
for bid, e in ssot.items():
    if e.get('entity_type') == 'ecosystem' and e.get('category') != bid:
        fail('生态一致性', 'entity_type=ecosystem 的 %s 未以自身为一级分类: %s'
             % (bid, e.get('category')))
# (f) 漏标拦截：位于生态分类内的非根品牌必须声明 parent_brand 且指向该分类
for bid, e in ssot.items():
    c = e.get('category')
    if c in eco_cat_ids and bid != c:
        if e.get('parent_brand') != c:
            fail('生态一致性', '位于生态分类 %s/ 但未标注 parent_brand=%s: %s（实际 %s）'
                 % (c, c, bid, e.get('parent_brand') or '无'))

# ---------- 结果：按验证组报告 ----------
expected_groups = ['PNG integrity', 'Image spec', 'Naming', 'Category',
                   'Canonical uniqueness', 'SHA-256 uniqueness', 'Brands SSOT',
                   'Surge JSON', 'Glossary', 'Legacy paths',
                   'README 表格', '生态一致性']
any_fail = False
print('Validation Groups: %d' % len(expected_groups))
for g in expected_groups:
    errs = groups.get(g, [])
    if errs:
        any_fail = True
        print('✗ %s（%d 项问题）' % (g, len(errs)))
        for e in errs[:20]:
            print('    - %s' % e)
        if len(errs) > 20:
            print('    ... 其余 %d 项省略' % (len(errs) - 20))
    else:
        print('✓ %s' % g)
if any_fail:
    sys.exit(1)
print('All groups: PASS')
print('  PNG %d / brands %d / categories %d' % (len(all_pngs), len(brand_dirs),
                                                 len([d for d in ICONS.iterdir() if d.is_dir()])))
