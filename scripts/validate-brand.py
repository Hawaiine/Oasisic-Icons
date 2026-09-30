#!/usr/bin/env python3
"""validate-brand.py —— 新增 / 修改品牌条目的**统一校验入口**（确定性，不做 AI 猜测）。

用法：

    python3 scripts/validate-brand.py \
        --id Example --display-name "Example" --category Music \
        --entity-type product_brand --parent-brand ExampleParent \
        [--png icons/Music/Example/Example.png] [--json]

校验链（全部为确定性检查；任一 error → exit 1）：

  1. ID：非空、字符集合法（`[A-Za-z0-9@+._-]`，无路径分隔符）、不与现有 ID 重复、
     不与现有 ID **大小写撞车**、归一化后（去非字母数字）不与现有 ID 撞车、不是 legacy ID；
  2. display_name：非空、不与现有精确重复；ID 与 display_name 归一化不一致时给出
     **warning**（官方 casing / 特殊字符映射需人工确认，如 `iQIYI` / `myTVSUPER` / `Karaoke@DAM`）；
  3. category：必须存在于 `config/categories.json`；
  4. entity_type：必须合法；`ecosystem` 额外要求 `category == id`、无 `parent_brand`、
     canonical descendants ≥ 2；
  5. parent_brand：必须存在于 `config/brands.json` 或 `parent_brands_without_icon` 白名单，
     不得自指，父节点类型只能是 `product_brand` / `ecosystem`；
  6. icon：路径必须等于 `icons/<category>/<id>/<id>.png` 且文件存在；Pillow 可用时校验
     512×512 / RGBA / 四角 alpha=0，并检查 SHA-256 不与其它图标重复；
  7. 关系图：把候选条目并入 SSOT 后调用 `scripts/brand_relationships.py`
     （**单一关系引擎**，不重复实现阈值/环/根逻辑），把引擎报错原样返回；
  8. 无法确定 parent 时**不猜**：不传 `--parent-brand` 且非生态根/图根时直接报错，
     并提示把候选写进 `config/brand-review-queue.json` 由人工裁决（§41）。

机器可读输出：`--json` 打印 `{ok, errors, warnings, derived}`；否则打印人类可读摘要。
`validate_brand()` 为纯函数，供 `tests/test_brand_registration.py` 直接调用。
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'scripts'))

from brand_relationships import (  # noqa: E402
    _ancestor_set_ordered,
    resolve_ecosystem_root,
    resolve_graph_root,
    validate_relationships,
)
from legacy_map import legacy_ids  # noqa: E402

ENTITY_TYPES = {'ecosystem', 'product_brand', 'country', 'system_icon', 'tool_app'}
ID_RE = re.compile(r'^[A-Za-z0-9@+][A-Za-z0-9@+._-]*$')


def _norm(s):
    return re.sub(r'[^0-9a-z]', '', s.lower())


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_brand(entry, brands_doc, cats_doc, repo_root='.', include_engine=True):
    """校验单个候选品牌条目，返回 {'errors': [...], 'warnings': [...]}。

    entry: {id, display_name, category, entity_type, icon_path?, parent_brand?}
    """
    errors, warns = [], []
    root = Path(repo_root)
    ssot = {e['id']: e for e in brands_doc.get('brands', []) if e.get('id')}
    aliases = set(brands_doc.get('parent_brands_without_icon', []))
    cat_ids = {c['id'] for c in (cats_doc or {}).get('categories', [])}

    bid = entry.get('id', '')
    dn = entry.get('display_name', '')
    cat = entry.get('category', '')
    et = entry.get('entity_type', '')
    parent = entry.get('parent_brand')
    legacy = legacy_ids()

    # 1. ID
    if not bid:
        errors.append('id 不能为空')
    else:
        if not ID_RE.match(bid) or '/' in bid or bid in ('.', '..'):
            errors.append('id 非法（只允许 [A-Za-z0-9@+._-] 且不含路径分隔符）: %r' % bid)
        if bid in legacy:
            errors.append('id 与 legacy 旧名冲突（当前 canonical 不得使用旧 ID）: %s' % bid)
        for other in ssot:
            if other == bid:
                errors.append('id 已存在（新增请用不同 ID；改名请走迁移流程）: %s' % bid)
            elif other.lower() == bid.lower():
                errors.append('id 与现有 ID 大小写撞车: %s vs %s' % (bid, other))
            elif _norm(other) == _norm(bid):
                errors.append('id 归一化后与现有 ID 撞车（如 A@B 与 AB）: %s vs %s' % (bid, other))
        for other in aliases:
            if _norm(other) == _norm(bid) and other != bid:
                errors.append('id 归一化后与白名单母公司撞车: %s vs %s' % (bid, other))

    # 2. display_name
    if not dn.strip():
        errors.append('display_name 不能为空')
    else:
        for other, e in ssot.items():
            if e.get('display_name') == dn and other != bid:
                errors.append('display_name 与现有品牌重复: %r（%s）' % (dn, other))
        if dn.isascii() and bid:
            mapped = dn.replace(' ', '').replace('@', '').replace('+', 'Plus')
            if mapped.lower() != bid.lower():
                warns.append('ID 与 display_name 归一化不一致（%r vs %r）：若为官方 casing / '
                             '特殊字符映射（iQIYI / myTVSUPER / Karaoke@DAM / AppleNewsPlus）'
                             '需人工确认，勿机械 PascalCase' % (bid, dn))

    # 3. category
    if not cat:
        errors.append('category 不能为空')
    elif cat not in cat_ids:
        errors.append('category 不在 config/categories.json: %s' % cat)

    # 4. entity_type
    if et not in ENTITY_TYPES:
        errors.append('entity_type 非法（允许 %s）: %r' % (sorted(ENTITY_TYPES), et))
    if et == 'ecosystem':
        if cat and cat != bid:
            errors.append('生态根必须以自身为一级分类（category=%s != id=%s）' % (cat, bid))
        if parent:
            errors.append('生态根不得有 parent_brand（中间层一律 product_brand）: %s' % parent)

    # 5. parent_brand
    if parent:
        if parent == bid:
            errors.append('parent_brand 不得自指: %s' % bid)
        elif parent not in ssot and parent not in aliases:
            errors.append('parent_brand 不存在且未登记白名单: %s -> %s' % (bid, parent))
        elif parent in ssot:
            pt = ssot[parent].get('entity_type')
            if pt not in ('product_brand', 'ecosystem'):
                errors.append('parent_brand 类型非法（父 entity_type=%s）: %s -> %s'
                              % (pt, bid, parent))
    elif et == 'product_brand':
        warns.append('无 parent_brand：若 %s 是图根（Graph Root Parent）可忽略；'
                     '若只是「尚不确定父品牌」，请把候选写入 config/brand-review-queue.json，'
                     '不要把猜测写进 SSOT（§41）' % bid)

    # 6. icon
    icon = entry.get('icon_path')
    if et != 'country' and not icon and bid and cat:
        icon = 'icons/%s/%s/%s.png' % (cat, bid, bid)
    if icon:
        expected = 'icons/%s/%s/%s.png' % (cat, bid, bid)
        if icon != expected:
            errors.append('icon_path 与命名契约不一致: %s（应为 %s）' % (icon, expected))
        p = root / icon
        if not p.exists():
            errors.append('icon 文件不存在: %s' % icon)
        else:
            if p.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
                errors.append('icon 不是合法 PNG: %s' % icon)
            try:
                from PIL import Image
                with Image.open(p) as im:
                    im.load()
                    if im.size != (512, 512):
                        errors.append('icon 尺寸非 512×512: %s %s' % (icon, im.size))
                    if im.mode != 'RGBA':
                        errors.append('icon 模式非 RGBA: %s %s' % (icon, im.mode))
                    elif im.size == (512, 512):
                        corners = [im.getpixel((x, y))[3]  # type: ignore[call-overload,index]
                                   for x, y in ((0, 0), (511, 0), (0, 511), (511, 511))]
                        if any(c != 0 for c in corners):
                            errors.append('icon 四角 alpha 非 0: %s %s' % (icon, corners))
            except ImportError:
                warns.append('Pillow 不可用，跳过像素级图像校验')
            except Exception as exc:  # noqa: BLE001
                errors.append('icon 解码失败: %s (%s)' % (icon, str(exc)[:60]))
            try:
                if p.exists():
                    h = _sha(p)
                    for other, e in ssot.items():
                        if other == bid:
                            continue  # 同一条目自身不算重复
                        op = e.get('icon_path')
                        if op and (root / op).exists() and _sha(root / op) == h:
                            errors.append('icon 与现有品牌图标内容相同（SHA-256 重复）: %s ↔ %s'
                                          % (bid, other))
            except OSError:
                pass

    # 7. 关系图（单一引擎）
    if include_engine and bid and et and not any('id 非法' in e for e in errors):
        cand = {e['id']: dict(e) for e in brands_doc.get('brands', []) if e.get('id')}
        cand[bid] = dict(entry)
        if icon:
            cand[bid]['icon_path'] = icon
        doc = {'brands': list(cand.values()),
               'parent_brands_without_icon': list(aliases)}
        for err in validate_relationships(doc, (cats_doc or {}).get('categories', [])):
            if bid in err:
                errors.append('关系引擎: %s' % err)

    return {'errors': errors, 'warnings': warns}


def derive(entry, brands_doc):
    ssot = {e['id']: e for e in brands_doc.get('brands', []) if e.get('id')}
    ssot[entry.get('id', '')] = entry
    bid = entry['id']
    return {
        'graph_root': resolve_graph_root(bid, ssot),
        'ecosystem_root': resolve_ecosystem_root(bid, ssot),
        'ancestor_chain': _ancestor_set_ordered(bid, ssot),
    }


def main():
    ap = argparse.ArgumentParser(description='Oasisic-Icons 新增/修改品牌条目校验')
    ap.add_argument('--id', required=True)
    ap.add_argument('--display-name', required=True)
    ap.add_argument('--category', required=True)
    ap.add_argument('--entity-type', default='product_brand')
    ap.add_argument('--parent-brand', default=None)
    ap.add_argument('--png', default=None, help='图标相对路径（默认按命名契约推导）')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    brands_doc = json.loads((REPO / 'config' / 'brands.json').read_text(encoding='utf-8'))
    cats_doc = json.loads((REPO / 'config' / 'categories.json').read_text(encoding='utf-8'))
    entry = {'id': args.id, 'display_name': args.display_name, 'category': args.category,
             'entity_type': args.entity_type}
    if args.parent_brand:
        entry['parent_brand'] = args.parent_brand
    if args.png:
        entry['icon_path'] = args.png

    res = validate_brand(entry, brands_doc, cats_doc, REPO)
    res['derived'] = derive(entry, brands_doc)
    res['ok'] = not res['errors']
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print('Brand: %s (%s) → %s' % (args.id, args.display_name, args.category))
        for w in res['warnings']:
            print('  ⚠ %s' % w)
        for e in res['errors']:
            print('  ✗ %s' % e)
        print('  derived: graph_root=%s ecosystem_root=%s chain=%s'
              % (res['derived']['graph_root'], res['derived']['ecosystem_root'],
                 ' → '.join([args.id] + res['derived']['ancestor_chain'])))
        print('RESULT: %s' % ('PASS' if res['ok'] else 'FAIL'))
    sys.exit(0 if res['ok'] else 1)


if __name__ == '__main__':
    main()
