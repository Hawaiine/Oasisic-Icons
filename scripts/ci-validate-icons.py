#!/usr/bin/env python3
"""CI 校验脚本：检查所有图标合法性 + surge-icon.json 一致性"""
import json
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
    rel = Path('icons') / it['category'] / f'{it["name"]}.png'
    if not rel.exists():
        print(f'  ✗ JSON 引用但文件不存在: {rel}')
        exit(1)
print('  ✓ 所有 JSON 条目均有对应文件')