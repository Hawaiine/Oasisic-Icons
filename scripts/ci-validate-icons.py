#!/usr/bin/env python3
"""Oasisic-Icons CI 校验

校验规则（结构规范 icons/<分类>/<品牌>/<文件>.png）：
  1. 所有 PNG 文件合法（>50B 且以 PNG 魔数开头）
  2. 分类根目录下不允许出现扁平 .png（必须放进品牌文件夹）
  3. 不允许 `-1` / `-2` / `_1` 等旧式连字符/下划线变体命名
  4. 每个品牌文件夹必须存在默认图标 <品牌名>.png
  5. 变体文件名必须是 <品牌名> + 两位零填充数字（如 Japan01.png）
  6. 品牌文件夹不能为空
  7. config/surge-icon.json 条目数 == 磁盘 PNG 数，且每条 URL 都能对应到真实文件、不含 jsDelivr
  8. 分类白名单：icons/ 下的目录必须都在 config/categories.json（SSOT）中
  9. Canonical Brand 唯一性：同一品牌目录名不得出现在两个分类
 10. 图片内容唯一性：SHA-256 相同即视为重复图标，直接失败
 11. SSOT 一致性：config/brands.json 与磁盘一一对应（品牌、分类、icon_path）
 12. Glossary 一致性：brand-glossary.md 条目数与 brands.json 一致、无缺失/多余
失败时打印全部问题并以 exit 1 结束。
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
errors = []


def fail(msg):
    errors.append(msg)


# ---------- 1. PNG 合法性 ----------
all_pngs = sorted(ICONS.rglob('*.png'))
if not all_pngs:
    fail('icons/ 下没有任何 PNG 文件')
for p in all_pngs:
    b = p.read_bytes()
    if len(b) < 50 or not b.startswith(b'\x89PNG\r\n\x1a\n'):
        fail('非法图标（非 PNG 或过小）: %s (size=%d)' % (p, len(b)))

# ---------- 结构：分类 -> 品牌 -> 文件 ----------
brand_dirs = defaultdict(list)
for cat_dir in sorted(ICONS.iterdir()):
    if not cat_dir.is_dir():
        continue
    for item in sorted(cat_dir.iterdir()):
        if item.is_file() and item.suffix == '.png':
            fail('扁平文件（应放入品牌文件夹）: %s' % item)   # 规则 2
            continue
        if not item.is_dir():
            continue
        pngs = sorted(f for f in item.iterdir() if f.is_file() and f.suffix == '.png')
        if not pngs:
            fail('空的品牌文件夹（无 PNG）: %s' % item)       # 规则 6
        brand_dirs[item] = pngs

for brand_dir, pngs in brand_dirs.items():
    brand = brand_dir.name
    names = [f.name for f in pngs]
    if '%s.png' % brand not in names:
        fail('缺少默认图标 %s/%s.png' % (brand_dir, brand))   # 规则 4
    for name in names:
        if name == '%s.png' % brand:
            continue
        if re.search(r'[-_]\d+\.png$', name):
            fail('旧式连字符/下划线变体命名: %s/%s' % (brand_dir, name))  # 规则 3
            continue
        if not re.fullmatch(re.escape(brand) + r'\d{2}\.png', name):
            fail('变体命名不规范（应为 %s01.png 形式）: %s/%s' % (brand, brand_dir, name))  # 规则 5

# ---------- 7. surge-icon.json 一致性 ----------
entries = []
if not JSON_PATH.exists():
    fail('缺少 %s' % JSON_PATH)
else:
    sj = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    entries = sj.get('icons', [])
    if len(entries) != len(all_pngs):
        fail('条目数不一致: surge-icon.json=%d, 磁盘 PNG=%d' % (len(entries), len(all_pngs)))
    for it in entries:
        url = it.get('url', '')
        if '/icons/' not in url:
            fail('URL 缺少 /icons/: %s' % url)
            continue
        if 'jsdelivr' in url.lower():
            fail('URL 使用了 jsDelivr（禁止）: %s' % url)
            continue
        rel = url.split('main/', 1)[-1]
        if not Path(rel).exists():
            fail('JSON 引用但文件不存在: %s' % rel)

# ---------- 8. 分类白名单（SSOT） ----------
if not CATS_PATH.exists():
    fail('缺少 %s（分类 SSOT）' % CATS_PATH)
else:
    cat_ids = {c['id'] for c in json.loads(CATS_PATH.read_text(encoding='utf-8'))['categories']}
    disk_cats = {d.name for d in ICONS.iterdir() if d.is_dir()}
    for c in sorted(disk_cats - cat_ids):
        fail('分类不在 SSOT 白名单中（icons/%s）: 请更新 config/categories.json' % c)
    # SSOT 中 active 分类必须在磁盘存在；reserved 允许不存在或为空
    for c in json.loads(CATS_PATH.read_text(encoding='utf-8'))['categories']:
        if c.get('status', 'active') == 'active' and c['id'] not in disk_cats:
            fail('SSOT 声明的 active 分类在磁盘不存在: %s' % c['id'])

# ---------- 9. Canonical Brand 唯一性 ----------
brand_to_cats = defaultdict(set)
for brand_dir in brand_dirs:
    brand_to_cats[brand_dir.name].add(brand_dir.parent.name)
for brand, cats in sorted(brand_to_cats.items()):
    if len(cats) > 1:
        fail('Canonical Brand 重复: %s 同时存在于 %s（只允许一个分类）' % (brand, sorted(cats)))

# ---------- 10. 图片内容唯一性（SHA-256） ----------
hash_to_paths = defaultdict(list)
for p in all_pngs:
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    hash_to_paths[h].append(str(p))
for h, paths in sorted(hash_to_paths.items()):
    if len(paths) > 1:
        fail('重复图标内容（SHA-256=%s…）: %s' % (h[:12], ' / '.join(paths)))

# ---------- 11. brands.json SSOT 一致性 ----------
ssot = {}
if not BRANDS_PATH.exists():
    fail('缺少 %s（品牌 SSOT）' % BRANDS_PATH)
else:
    bdata = json.loads(BRANDS_PATH.read_text(encoding='utf-8'))['brands']
    for e in bdata:
        if e['id'] in ssot:
            fail('brands.json 中品牌 ID 重复: %s' % e['id'])
        ssot[e['id']] = e
    disk_brands = {str(bd.relative_to(ICONS)): bd.name for bd in brand_dirs}
    ssot_paths = {e['icon_path'].split('/')[1] + '/' + e['icon_path'].split('/')[2]: e['id']
                  for e in bdata}
    for rel in sorted(disk_brands - set(ssot_paths)):
        fail('磁盘品牌不在 brands.json: icons/%s' % rel)
    for rel in sorted(set(ssot_paths) - disk_brands):
        fail('brands.json 品牌在磁盘不存在: icons/%s' % rel)
    for e in bdata:
        if e['category'] not in {c['id'] for c in json.loads(CATS_PATH.read_text(encoding='utf-8'))['categories']}:
            fail('brands.json 引用未知分类: %s (%s)' % (e['category'], e['id']))
        if not (ICONS / e['category'] / e['id'] / (e['id'] + '.png')).exists():
            fail('brands.json icon_path 文件不存在: %s' % e['icon_path'])

# ---------- 12. Glossary 一致性 ----------
gloss = set()
if not GLOSS_PATH.exists():
    fail('缺少 %s' % GLOSS_PATH)
else:
    for line in GLOSS_PATH.read_text(encoding='utf-8').splitlines():
        m = re.match(r'^\|\s*([\w.\-]+)\s*\|\s*([^|]+?)\s*\|\s*$', line)
        if m and m.group(1) not in ('英文文件夹',) and m.group(1)[0].isalnum():
            gloss.add(m.group(1))
    ssot_ids = set(ssot) if BRANDS_PATH.exists() else set()
    for b in sorted(ssot_ids - gloss):
        fail('Glossary 缺失品牌: %s' % b)
    for b in sorted(gloss - ssot_ids):
        fail('Glossary 多余品牌（brands.json 无）: %s' % b)

# ---------- 结果 ----------
if errors:
    print('✗ 校验失败，共 %d 项问题：' % len(errors))
    for e in errors[:50]:
        print('  - %s' % e)
    if len(errors) > 50:
        print('  ... 其余 %d 项省略' % (len(errors) - 50))
    sys.exit(1)

print('✓ PNG 合法: %d 个' % len(all_pngs))
print('✓ 品牌文件夹: %d 个，均有默认图标 <品牌名>.png' % len(brand_dirs))
print('✓ 无分类根目录扁平 png、无 -1/-2 旧式命名、变体均为两位零填充')
print('✓ surge-icon.json 条目数 %d == 磁盘 PNG 数 %d' % (len(entries), len(all_pngs)))
print('✓ 分类白名单（categories.json SSOT）通过: %d 个分类' % len([d for d in ICONS.iterdir() if d.is_dir()]))
print('✓ Canonical Brand 唯一: 无跨分类重复品牌')
print('✓ SHA-256 去重通过: 0 个重复图标内容')
print('✓ brands.json SSOT 一致: %d 品牌一一对应' % len(ssot))
print('✓ Glossary 一致: %d 条目 == brands.json' % len(gloss))
