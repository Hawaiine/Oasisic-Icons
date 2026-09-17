#!/usr/bin/env python3
"""CI 校验脚本：检查所有图标合法性 + surge-icon.json 一致性"""
import json, re
from pathlib import Path

bad = []
for p in Path('icons').rglob('*.png'):
    b = p.read_bytes()
    if len(b) < 50 or not b.startswith(b'\x89PNG\r\n\x1a\n'):
        bad.append((str(p), len(b)))
if bad:
    for f, sz in bad:
        print(f'  ✗ 非法图标: {f} (size={sz})')
    exit(1)
print('  ✓ 所有 PNG 文件合法')

# 检查文件夹结构：每个品牌必须在独立文件夹内
structure_ok = True
for cat_dir in Path('icons').iterdir():
    if not cat_dir.is_dir():
        continue
    for item in cat_dir.iterdir():
        if item.is_file() and item.suffix == '.png':
            print(f'  ✗ 扁平文件（应在品牌文件夹内）: {item}')
            structure_ok = False
if not structure_ok:
    exit(1)
print('  ✓ 所有图标均在品牌文件夹内')

# 检查变体命名规范
bad_names = []
for p in Path('icons').rglob('*.png'):
    stem = p.stem
    brand = p.parent.name
    if stem == brand:
        continue  # 默认图标，OK
    if re.match(r'^[A-Za-z0-9]+[0-9]{2}$', stem):
        continue  # 零填充变体，OK
    bad_names.append(str(p))
if bad_names:
    print(f'  ✗ 变体命名不规范（应使用两位零填充）:')
    for f in bad_names[:10]:
        print(f'    {f}')
    exit(1)
print('  ✓ 变体命名规范（两位零填充）')

sj = json.loads(Path('config/surge-icon.json').read_text())
disk = list(Path('icons').rglob('*.png'))
count_json = len(sj['icons'])
count_disk = len(disk)
if count_json != count_disk:
    print(f'  ✗ mismatch: surge-icon.json={count_json}, disk={count_disk}')
    exit(1)
print(f'  ✓ surge-icon.json 条目数 {count_json} == 磁盘 PNG 数 {count_disk}')

for it in sj['icons']:
    assert '/icons/' in it['url'], f'URL 缺少 /icons/: {it["url"]}'
    # 从 URL 提取相对路径验证
    url_path = it['url'].split('main/')[-1]
    rel = Path('.') / url_path
    if not rel.exists():
        print(f'  ✗ JSON 引用但文件不存在: {rel}')
        exit(1)
print('  ✓ 所有 JSON 条目均有对应文件')
