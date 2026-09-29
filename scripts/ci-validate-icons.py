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

# ---------- 结果：按验证组报告 ----------
expected_groups = ['PNG integrity', 'Image spec', 'Naming', 'Category',
                   'Canonical uniqueness', 'SHA-256 uniqueness', 'Brands SSOT',
                   'Surge JSON', 'Glossary', 'Legacy paths']
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
