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
失败时打印全部问题并以 exit 1 结束。
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ICONS = Path('icons')
JSON_PATH = Path('config/surge-icon.json')
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