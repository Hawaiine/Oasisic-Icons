#!/usr/bin/env bash
# generate-icon-json.sh — 自动生成 Oasisic-Icons/surge-icon.json（Python 稳定排序）
set -euo pipefail

cd "$(dirname "$0")/.."

python3 - <<'PY'
import json
from pathlib import Path

base_url = 'https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main'
output = Path('config/surge-icon.json')
brands = json.loads(Path('config/brands.json').read_text(encoding='utf-8'))['brands']

entries = []
for brand in sorted(brands, key=lambda e: (e.get('category', ''), e.get('id', ''))):
    icon_path = brand.get('icon_path')
    if not icon_path:
        # A pending/generated ecosystem without an asset has no URL entry.
        continue
    directory = Path(icon_path).parent
    for png_file in sorted(directory.glob('*.png')):
        entries.append({
            'name': png_file.stem,
            'category': brand['category'],
            'url': f'{base_url}/{directory.as_posix()}/{png_file.name}',
        })

entries.sort(key=lambda e: (e['category'], e['name']))
result = {
    'name': 'Oasisic-Icons',
    'description': 'Cross-platform Proxy Policy Group Icons / 跨平台代理策略组图标合集',
    'icons': entries,
}
output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'✓ 已生成 {output} ({len(entries)} 个图标)')
PY
