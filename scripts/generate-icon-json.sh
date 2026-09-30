#!/usr/bin/env bash
# generate-icon-json.sh — 自动生成 Oasisic-Icons/surge-icon.json（Python 稳定排序）
set -euo pipefail

cd "$(dirname "$0")/.."

BASE_URL="https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main"
ICONS_DIR="icons"
OUTPUT="config/surge-icon.json"

python3 -c "
import json
from pathlib import Path

base_url = '$BASE_URL'
output = '$OUTPUT'

# SSOT 驱动（§21）：icon_path 由统一解析器确定，支持多层物理层级
# （icons/<category>/<中间父>/<id>/<id>.png）。禁止再按「一级子目录 = 品牌」遍历。
brands = json.loads(Path('config/brands.json').read_text(encoding='utf-8'))['brands']

entries = []
for b in sorted(brands, key=lambda e: (e.get('category', ''), e.get('id', ''))):
    icon_path = b.get('icon_path')
    if not icon_path:
        continue
    d = Path(icon_path).parent
    for png_file in sorted(d.glob('*.png')):
        entries.append({
            'name': png_file.stem,
            'category': b['category'],
            'url': f'{base_url}/{d.as_posix()}/{png_file.name}',
        })

entries.sort(key=lambda e: (e['category'], e['name']))

result = {
    'name': 'Oasisic-Icons',
    'description': 'Cross-platform Proxy Policy Group Icons / 跨平台代理策略组图标合集',
    'icons': entries,
}

with open(output, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
    f.write('\\n')

print(f'✓ 已生成 {output} ({len(entries)} 个图标)')
"
