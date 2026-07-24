#!/usr/bin/env bash
# generate-icon-json.sh — 自动生成 Oasisic-Icons/surge-icon.json（Python 稳定排序）
set -euo pipefail

# 切换到仓库根目录（scripts/ 的父目录）
cd "$(dirname "$0")/.."

BASE_URL="https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main"
ICONS_DIR="icons"
OUTPUT="config/surge-icon.json"

python3 -c "
import json, os
from pathlib import Path

icons_dir = Path('$ICONS_DIR')
base_url = '$BASE_URL'
output = '$OUTPUT'

entries = []
for cat_dir in sorted(icons_dir.iterdir()):
    if not cat_dir.is_dir():
        continue
    category = cat_dir.name
    for png_file in cat_dir.glob('*.png'):
        name = png_file.stem
        url = f'{base_url}/{icons_dir.name}/{category}/{png_file.name}'
        entries.append({
            'name': name,
            'category': category,
            'url': url,
        })

# 按 (category, name) 稳定排序
entries.sort(key=lambda e: (e['category'], e['name']))

result = {
    'name': 'Oasisic-Icons',
    'description': 'Cross-platform Proxy Policy Group Icons / 跨平台代理策略组图标合集',
    'icons': entries,
}

with open(output, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
    f.write('\n')

print(f'✓ 已生成 {output} ({len(entries)} 个图标)')
"