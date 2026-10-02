#!/usr/bin/env bash
# generate-icon-json.sh — 自动生成 Oasisic-Icons/surge-icon.json
#
# 数据模型（2026-10-01 定稿，canonical / brand-level）：
#   1 brand == 1 canonical asset == 1 surge entry
#
#   - 条目由 config/brands.json（SSOT）驱动，**不由磁盘上任意 PNG 驱动**；
#   - name = brand.id；category = brand.category；
#     url  = ICON_RAW_BASE + '/' + brand.icon_path
#            （基址唯一来源 scripts/site_constants.py，生成器与校验器共用）；
#   - icon_path 必须逐字等于关系引擎 expected_icon_path() 的推导结果，且文件必须存在；
#   - 品牌目录内出现非 canonical PNG（`<id>01.png` 数字后缀 / 额外图）→ 报错并 exit 1：
#     canonical-only 契约下 `<id>.png` 是唯一合法资产名，数字后缀**不是**当前支持的契约；
#   - 反向一致性（physical tree → SSOT）：磁盘上任何含 PNG 的品牌目录都必须对应一个
#     SSOT canonical 条目，否则视为 orphan（未注册/已删除资产）→ 报错并 exit 1；
#   - 无 icon_path 的条目（icon_status=pending 的生态根）不产生 surge 条目。
#
# 幂等：连续执行两次输出逐字节一致（CI 亦逐项校验，见 ci-validate-icons.py 第 8 组）。
set -euo pipefail

cd "$(dirname "$0")/.."

python3 - <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('scripts').resolve()))
from brand_relationships import expected_icon_path  # 唯一物理路径解析器
from json_io import read_json_or_exit  # JSON 读取唯一入口（统一诊断）
from site_constants import ICON_RAW_BASE

output = Path('config/surge-icon.json')
brands = read_json_or_exit('config/brands.json', 'brands.json (品牌 SSOT)')['brands']
ssot = {b['id']: b for b in brands}

entries = []
errors = []
for brand in sorted(brands, key=lambda e: (e.get('category', ''), e.get('id', ''))):
    bid = brand['id']
    icon_path = brand.get('icon_path')
    if not icon_path:
        # pending 生态根（官方标志待补）：无物理 leaf，不产生 surge 条目。
        continue

    expected = expected_icon_path(bid, ssot)
    if expected != icon_path:
        errors.append('%s: icon_path=%r 与关系引擎推导 %r 不一致（禁止手写路径）'
                      % (bid, icon_path, expected))
        continue

    icon_file = Path(icon_path)
    if not icon_file.exists():
        errors.append('%s: icon_path 指向的文件不存在: %s' % (bid, icon_path))
        continue

    # canonical 资产模型：品牌目录内只允许 <id>.png，其余 PNG 一律显式报错。
    extra = sorted(p.name for p in icon_file.parent.glob('*.png') if p.stem != bid)
    if extra:
        for name in extra:
            errors.append('unregistered/non-canonical PNG detected: %s/%s'
                          % (icon_file.parent.as_posix(), name))
        continue

    entries.append({
        'name': bid,
        'category': brand['category'],
        'url': '%s/%s' % (ICON_RAW_BASE, icon_path),
    })

# 反向一致性（physical tree → SSOT）：含 PNG 的品牌目录必须能对应 SSOT canonical 条目。
# 复用关系引擎 expected_icon_path()，不在此重新实现路径解析。
expected_paths = {p for p in (expected_icon_path(bid, ssot) for bid in ssot) if p}
for d in sorted(Path('icons').rglob('*')):
    if not d.is_dir():
        continue
    pngs = sorted(p.name for p in d.iterdir() if p.is_file() and p.suffix == '.png')
    if not pngs:
        continue
    canon = '%s/%s.png' % (d.as_posix(), d.name)
    if canon not in expected_paths:
        errors.append('orphan physical brand directory（SSOT 无对应 canonical 条目）: '
                      '%s（含 %d 个 PNG）' % (d.as_posix(), len(pngs)))

if errors:
    print('ERROR: surge-icon.json 未生成（canonical / brand-level 资产模型校验失败）：',
          file=sys.stderr)
    for err in errors:
        print('  - %s' % err, file=sys.stderr)
    print('Canonical asset model is currently brand-level: '
          '1 brand = 1 canonical asset = 1 surge entry.', file=sys.stderr)
    print('Register/rename/remove the asset per docs/references/brand-naming-contract.md;',
          file=sys.stderr)
    print('Canonical-only: <id>.png is the only valid asset name; digit-suffixed PNGs '
          '(<id>NN.png) are not a supported contract and are never registered.',
          file=sys.stderr)
    sys.exit(1)

entries.sort(key=lambda e: (e['category'], e['name']))
result = {
    'name': 'Oasisic-Icons',
    'description': 'Cross-platform Proxy Policy Group Icons / 跨平台代理策略组图标合集',
    'icons': entries,
}
output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'✓ 已生成 {output} ({len(entries)} 个图标)')
PY
