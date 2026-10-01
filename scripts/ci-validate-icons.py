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
 11. README 表格          主 README 分类清单：结构、全量覆盖、顺序与计数
 12. 生态一致性           关系图门禁（scripts/brand_relationships.py）：直接父品牌、
                          graph root ≠ ecosystem root、双向生态阈值（root descendants ≥ 2
                          必须 ecosystem）、canonical 实体过滤
 13. README 统计          主 README badge / intro 汇总数 / 统计口径行（SSOT entities ·
                          canonical · icon-backed · PNG · pending no-icon · categories ·
                          ecosystems）/ 生态根计数 / SpaceXAI 资产状态句 vs SSOT（防硬编码漂移）
 14. README 父节点        任何拥有 ≥1 child brand 的物理品牌节点必须有 README.md，且
                          生成 README 内容与 expected_parent_readme() 逐字节一致
 15. 关系派生导出         config/brand-relationships.json 必须与 brands.json + 关系引擎
                          逐项一致（parent / ancestor_chain / graph_root / ecosystem_root），
                          且标 generated: true + source=config/brands.json（不是第二个 SSOT）
 16. Review Queue         config/brand-review-queue.json 结构合法：状态 ∈ {OPEN, RESOLVED}，
                          issue_kind 合法，引用真实品牌 ID；不得用队列覆盖 SSOT

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


# 关系 / 物理路径解析器（唯一来源：scripts/brand_relationships.py）
sys.path.insert(0, str(Path('scripts').resolve()))
from brand_relationships import (  # noqa: E402
    ecosystem_category_ids,
    expected_ecosystem_readme_block,
    expected_icon_path,
    expected_parent_readme,
    is_canonical_brand,
    physical_parent_nodes,
    resolve_ecosystem_root,
    validate_physical_paths,
    validate_relationships,
)

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

# ---------- 3. Naming / 结构（递归：支持多层物理层级） ----------
# 物理模型（scripts/brand_relationships.py 文档头 / docs/references/brand-naming-contract.md）：
#   icons/<category>/<id>/<id>.png                     一级 direct child（category root 的直系子）
#   icons/<category>/<中间父>/<id>/<id>.png            同类中间父品牌下的深层子品牌
# 结构校验必须递归，不能只扫一级目录（否则深层嵌套会被漏检 / 误判为分类）。
brand_dirs = defaultdict(list)
for cat_dir in sorted(ICONS.iterdir()):
    if not cat_dir.is_dir():
        continue
    for item in sorted(cat_dir.iterdir()):
        if item.is_file() and item.suffix == '.png':
            fail('Naming', '扁平文件（应放入品牌文件夹）: %s' % item)
    for d in sorted(cat_dir.rglob('*')):
        if not d.is_dir():
            continue
        pngs = sorted(f for f in d.iterdir() if f.is_file() and f.suffix == '.png')
        subs = [x for x in d.iterdir() if x.is_dir()]
        if pngs:
            brand_dirs[d] = pngs
        elif subs:
            fail('Naming', '中间目录无自身图标（疑似为无图标母公司制造伪目录）: %s' % d)
        else:
            fail('Naming', '空目录（无 PNG）: %s' % d)

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
        cid = c['id']
        status = c.get('status', 'active')
        cdir = ICONS / cid
        cbrands = {d.name for d in cdir.iterdir() if d.is_dir()} if cdir.is_dir() else set()
        cpngs = list(cdir.rglob('*.png')) if cdir.is_dir() else []
        if status == 'active' and cid not in disk_cats:
            fail('Category', 'SSOT 声明的 active 分类在磁盘不存在: %s' % cid)
        elif status == 'reserved':
            # §78 预留分类语义：reserved = 已声明但尚无品牌 → 必须 0 品牌 0 PNG。
            if cbrands or cpngs:
                fail('Category', 'reserved 分类 %s 必须为空（0 品牌 0 PNG），实际 %d 品牌 %d PNG'
                     % (cid, len(cbrands), len(cpngs)))
        elif status == 'active' and not cpngs:
            # active = 有实际图标；空目录应显式标 reserved（防止「看起来活跃但空」漂移）。
            fail('Category', 'active 分类 %s 无任何 PNG（应改为 status=reserved 或补图标）' % cid)

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
bdata = []
if not BRANDS_PATH.exists():
    fail('Brands SSOT', '缺少 %s（品牌 SSOT）' % BRANDS_PATH)
else:
    brands_doc = json.loads(BRANDS_PATH.read_text(encoding='utf-8'))
    if not isinstance(brands_doc, dict):
        fail('Brands SSOT', 'brands.json 根必须是对象 {brands: [...]}')
        brands_doc = {'brands': []}
    aliases = set(brands_doc.get('parent_brands_without_icon', []))
    bdata = brands_doc.get('brands', [])
    _byid = {e.get('id'): e for e in bdata}
    seen_paths = set()
    for e in bdata:
        bid = e.get('id', '')
        if bid in ssot:
            fail('Brands SSOT', '品牌 ID 重复: %s' % bid)
        ssot[bid] = e
        ip = e.get('icon_path', '')
        et = e.get('entity_type', '')
        icon_status = e.get('icon_status')
        # 资产模型（canonical ecosystem，2026-10-01 收紧）：
        #   icon_status=pending 且无 icon_path：仅关系层存在（canonical=true +
        #     category=自身），无物理 leaf，不出现在物理层 / Surge；
        #   icon_status=generated_temporary：必须携带真实 icon_path（PNG 由第 2 组
        #     做像素级校验），不得复用 pending 豁免；
        #   其余所有条目（product_brand / country / system_icon / tool_app 及
        #     非 pending 的 ecosystem）缺 icon_path = 静默通过，必须 FAIL。
        pending_ecosystem = et == 'ecosystem' and icon_status == 'pending' and not ip
        if pending_ecosystem:
            if e.get('canonical') is not True:
                fail('Brands SSOT', 'pending ecosystem 必须 canonical=true: %s' % bid)
            if e.get('category') != bid:
                fail('Brands SSOT', 'ecosystem category 必须等于自身: %s' % bid)
        elif et == 'ecosystem' and icon_status == 'generated_temporary' and not ip:
            fail('Brands SSOT', 'icon_status=generated_temporary 必须携带真实 icon_path: %s' % bid)
        elif not ip:
            fail('Brands SSOT', 'SSOT 条目缺 icon_path（不得无图标静默通过）: %s' % bid)
        if ip in seen_paths and ip:
            fail('Brands SSOT', 'icon_path 重复: %s' % ip)
        seen_paths.add(ip)
        cat = e.get('category', '')
        if cats and cat not in {c['id'] for c in cats}:
            fail('Brands SSOT', '引用未知分类: %s (%s)' % (cat, bid))
        expected = expected_icon_path(bid, _byid)
        if pending_ecosystem:
            pass  # 无物理 leaf：不检查路径一致性 / 文件存在性
        elif ip != expected:
            fail('Brands SSOT', 'icon_path 与路径规则不一致: %s 应为 %s' % (ip, expected))
        elif not Path(ip).exists():
            fail('Brands SSOT', 'icon_path 文件不存在: %s' % ip)
        elif Path(ip).parent.name != bid:
            fail('Brands SSOT', 'category 与目录不一致: %s (%s)' % (ip, bid))
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
            # parent_brand 必须引用正式 SSOT 节点或 legacy alias；pending ecosystem 也属于正式 SSOT。
            if parent not in ssot and parent not in aliases:
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
            # Pending ecosystem roots are semantic SSOT nodes but have no physical parent README.
            if cur not in ssot and cur not in aliases:
                fail('Brands SSOT', 'parent_brand 链末端不存在: %s' % ' -> '.join(chain + [cur]))
    disk_brands = {str(bd.relative_to(ICONS)) for bd in brand_dirs}
    ssot_rel = {Path(e['icon_path']).parent.relative_to('icons').as_posix() for e in bdata if e.get('icon_path')}
    # 允许的「无自身 icon 的父品牌」（仅记录归属关系，图标缺失见 docs 审计记录）
    aliases = set()
    if isinstance(json.loads(BRANDS_PATH.read_text(encoding='utf-8')), dict):
        aliases = set(json.loads(BRANDS_PATH.read_text(encoding='utf-8')).get('parent_brands_without_icon', []))
    for rel in sorted(disk_brands - ssot_rel):
        fail('Brands SSOT', '磁盘品牌不在 brands.json: icons/%s' % rel)
    for rel in sorted(ssot_rel - disk_brands):
        fail('Brands SSOT', 'brands.json 品牌在磁盘不存在: %s' % rel)

# ---------- 8. surge-icon.json（§30-§34 双向集合一致性） ----------
# 存在性 → 升级为「与 brands.json SSOT 逐项对应」：
#   - surge ID 集合 == brands.json ID 集合（双向，可检测多余/缺失/旧 ID）
#   - surge name == brands.json.id；surge category == brands.json.category
#   - surge url == 由 brands.json.icon_path 派生的 canonical URL
#   - 保留：URL 存在 /icons/、无 jsDelivr、文件在磁盘存在
SURGE_BASE = 'https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main'
entries = []
if not JSON_PATH.exists():
    fail('Surge JSON', '缺少 %s' % JSON_PATH)
else:
    entries = json.loads(JSON_PATH.read_text(encoding='utf-8')).get('icons', [])
    if len(entries) != len(all_pngs):
        fail('Surge JSON', '条目数不一致: surge-icon.json=%d, 磁盘 PNG=%d' % (len(entries), len(all_pngs)))

    # canonical 映射：id -> (category, icon_path)
    canon = {e['id']: (e.get('category', ''), e.get('icon_path', '')) for e in bdata if e.get('icon_path')}

    # 逐条：name/category/url 与 SSOT 精确一致 + 文件存在 + 无 jsDelivr
    surge_ids = set()
    for it in entries:
        name = it.get('name', '')
        surge_ids.add(name)
        url = it.get('url', '')
        if '/icons/' not in url:
            fail('Surge JSON', 'URL 缺少 /icons/: %s' % url)
            continue
        if 'jsdelivr' in url.lower():
            fail('Surge JSON', 'URL 使用了 jsDelivr（禁止）: %s' % url)
            continue
        if not Path(url.split('main/', 1)[-1]).exists():
            fail('Surge JSON', 'JSON 引用但文件不存在: %s' % url)
            continue
        if name not in canon:
            fail('Surge JSON', 'surge entry name 不在 brands.json（多余/旧 ID）: %s' % name)
            continue
        cat, ipath = canon[name]
        if it.get('category', '') != cat:
            fail('Surge JSON', 'category 不符: %s surge=%r ssot=%r' % (name, it.get('category', ''), cat))
        expected_url = '%s/%s' % (SURGE_BASE, ipath) if ipath else ''
        if expected_url and url != expected_url:
            fail('Surge JSON', 'URL 与 icon_path 派生不符: %s surge=%r expected=%r' % (name, url, expected_url))

    # 双向：brands.json 每个品牌必须出现在 surge（缺失/旧 ID 检测）
    for bid in sorted(set(canon) - surge_ids):
        fail('Surge JSON', 'brands.json 品牌在 surge-icon.json 缺失: %s' % bid)

# ---------- 9. Glossary（§35-§39 ID + display_name 双向映射一致性） ----------
if not GLOSS_PATH.exists():
    fail('Glossary', '缺少 %s' % GLOSS_PATH)
else:
    gloss = {}
    for line in GLOSS_PATH.read_text(encoding='utf-8').splitlines():
        m = re.match(r'^\|\s*([\w.\-]+)\s*\|\s*([^|]+?)\s*\|\s*$', line)
        if m and m.group(1) not in ('英文文件夹',) and m.group(1)[0].isalnum():
            gloss[m.group(1)] = m.group(2)
    ssot_ids = set(ssot)
    for b in sorted(ssot_ids - set(gloss)):
        fail('Glossary', '缺失品牌: %s' % b)
    for b in sorted(set(gloss) - ssot_ids):
        fail('Glossary', '多余品牌（brands.json 无）: %s' % b)
    # §35-§39：每个品牌的 technical ID 与 display_name 必须与 brands.json 精确一致
    # 特殊命名（+ / @ / 中文 / 官方 casing）只要符合 Naming Contract 即 PASS，
    # 不视为 mismatch。
    for bid in sorted(set(gloss) & ssot_ids):
        exp_dn = ssot[bid].get('display_name', '')
        if gloss[bid] != exp_dn:
            fail('Glossary', 'display_name 不符: %s glossary=%r ssot=%r' % (bid, gloss[bid], exp_dn))

# ---------- 10. Legacy paths（历史引用仅允许在 docs/migrations/） ----------
# 旧名（历史分类目录 + 已重命名品牌 ID）统一登记在 scripts/legacy_map.py（单一来源），
# 不在本脚本硬编码；legacy_map.py 自身是唯一允许出现旧名的位置，扫描时豁免。
from legacy_map import legacy_scan_patterns, legacy_ids  # noqa: E402
LEGACY_PATTERNS = legacy_scan_patterns()
LEGACY_EXEMPT = {'scripts/legacy_map.py', 'docs/migrations'}
# 自命中防护（2026-10-01 CI 修复）：解释器在 import 时会把本模块（含模式表字面量）
# 编译进 __pycache__/*.pyc，而 .pyc 是二进制但含可读字符串——若被当作文本扫描，
# 扫描器会命中自己的模式表。二进制 / 字节码缓存一律跳过。
LEGACY_BINARY_SUFFIXES = ('.pyc', '.pyo', '.so', '.dylib', '.dll', '.exe', '.zip',
                          '.gz', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.ico',
                          '.pdf', '.woff', '.woff2')


def _legacy_scan_skip(rel):
    if rel in LEGACY_EXEMPT or rel.startswith('docs/migrations/'):
        return True  # 迁移文档 / legacy 映射源自身的旧名引用允许
    if '__pycache__' in rel.split('/') or rel.endswith(LEGACY_BINARY_SUFFIXES):
        return True  # 字节码缓存 / 二进制资产
    return False


scan_dirs = ['README.md', 'docs', 'scripts', '.github', 'config']
for d in scan_dirs:
    root = Path(d)
    if not root.exists():
        continue
    targets = [root] if root.is_file() else [f for f in root.rglob('*') if f.is_file()]
    for f in targets:
        rel = f.as_posix()
        if _legacy_scan_skip(rel):
            continue
        try:
            raw = f.read_bytes()
            if b'\x00' in raw[:1024]:
                continue  # 二进制内容（防未来新增未知后缀时再次自命中）
            text = raw.decode('utf-8', errors='ignore')
        except Exception:
            continue
        for pat in LEGACY_PATTERNS:
            for m in re.finditer(re.escape(pat), text):
                line_no = text.count('\n', 0, m.start()) + 1
                fail('Legacy paths', '%s:%d 引用 legacy 路径段 %s' % (rel, line_no, pat))

# 10b. 值级：config 的 id / 分类 id 不得仍是旧 ID（防「改名漏改 SSOT」）
_legacy = legacy_ids()
if bdata:
    for e in bdata:
        if e.get('id') in _legacy:
            fail('Legacy paths', 'brands.json 仍有旧品牌 ID: %s（应为迁移后的 canonical ID）' % e['id'])
for c in cats:
    if c.get('id') in _legacy:
        fail('Legacy paths', 'categories.json 仍有旧分类 ID: %s' % c['id'])

# ---------- 11. README 分类表结构 ----------
# header / separator / 全量覆盖 / 无重复 / 顺序 / 计数
README_TABLE_TITLE = '图标分类列表'
if not Path('README.md').exists():
    fail('README 表格', '缺少 README.md')
else:
    readme = Path('README.md').read_text(encoding='utf-8')
    ri = readme.find(README_TABLE_TITLE)
    if ri < 0:
        fail('README 表格', '未找到 %s 小节' % README_TABLE_TITLE)
    else:
        rj = readme.find('\n## ', ri + len(README_TABLE_TITLE))
        if rj < 0:
            rj = readme.find('\n### ', ri + len(README_TABLE_TITLE))
        rseg = readme[ri:rj if rj > 0 else len(readme)]
        trows = [l for l in rseg.splitlines() if l.strip().startswith('|')]
        if not trows:
            fail('README 表格', '分类小节内没有任何表格行')
        else:
            header = trows[0]
            if '分类' not in header or '品牌数' not in header:
                fail('README 表格', '表头非法（应为 分类/说明/品牌数/图标数）: %s' % header.strip())
            if len(trows) < 2 or not re.match(r'^\|[\s\-:|]+\|$', trows[1].strip()):
                fail('README 表格', '缺少 header 后的分隔行 |---|')
            data_rows = [r for r in trows[2:] if r.strip() != '|']
            # 每行 4 列 + 数字
            parsed = []
            for r in data_rows:
                cells = [c.strip() for c in r.strip().strip('|').split('|')]
                if len(cells) != 4:
                    fail('README 表格', '列数 != 4: %s' % r.strip())
                    continue
                name = cells[0].split(' ', 1)[1] if ' ' in cells[0] else cells[0]
                if cells[2].startswith('**') or '合计' in name:
                    continue  # 合计行单独校验
                if not (cells[2].isdigit() and cells[3].isdigit()):
                    fail('README 表格', '计数列非数字: %s' % r.strip())
                    continue
                parsed.append((name, int(cells[2]), int(cells[3])))
            cat_by_name = {c['display_name']: c for c in cats}
            seen = set()
            for name, nb, ni in parsed:
                if name in seen:
                    fail('README 表格', '分类重复: %s' % name)
                seen.add(name)
                if name not in cat_by_name:
                    fail('README 表格', '未知分类: %s' % name)
            for c in cats:
                if c['display_name'] not in seen:
                    fail('README 表格', '缺失分类: %s' % c['display_name'])
            # 顺序与 categories.json 一致
            if [n for n, _, _ in parsed] != [c['display_name'] for c in cats]:
                fail('README 表格', '表格顺序与 categories.json 不一致')
            # 计数与真实数据一致
            brand_by_cat = {}
            for e in bdata:
                brand_by_cat[e['category']] = brand_by_cat.get(e['category'], 0) + 1
            icon_by_cat = {}
            for p in all_pngs:
                c = str(p.relative_to(ICONS)).split('/')[0]
                icon_by_cat[c] = icon_by_cat.get(c, 0) + 1
            for name, nb, ni in parsed:
                cobj = cat_by_name.get(name)
                if not cobj:
                    continue
                cid = cobj['id']
                if nb != brand_by_cat.get(cid, 0) or ni != icon_by_cat.get(cid, 0):
                    fail('README 表格', '%s 计数不符: 表=%d/%d 实际=%d/%d' %
                         (name, nb, ni, brand_by_cat.get(cid, 0), icon_by_cat.get(cid, 0)))

# ---------- 12. 生态一致性（关系图：直接父品牌 + 动态生态根 + descendants 阈值） ----------
# 模型（scripts/brand_relationships.py）：
#   - parent_brand = 直接父品牌（immediate parent），如 Instagram → Facebook；
#   - graph root ≠ ecosystem root（Mijia → Xiaomi：graph root=Xiaomi，非生态→ecosystem root=None）；
#   - 生态阈值（双向）= graph root canonical descendants ≥ 2（直系子 + 孙 + …，仅 product_brand），
#     正向（ecosystem→≥2）+ 反向（root ≥2→必须 ecosystem），只作用于 graph root，中间层不升级。
# 负测（cycle / self-parent / missing parent / wrong root / threshold 双向 / canonical 过滤）
# 见 tests/test_brand_relationships.py。
cats_doc = json.loads(CATS_PATH.read_text(encoding='utf-8')) if CATS_PATH.exists() else {}
brands_doc = json.loads(BRANDS_PATH.read_text(encoding='utf-8')) if BRANDS_PATH.exists() else {}
for _rel_err in validate_relationships(brands_doc, cats_doc.get('categories', [])):
    fail('生态一致性', _rel_err)

# ---------- 13. README 统计（§42-§45：badge + intro 数字 vs SSOT/文件系统） ----------
# 主 README 的 badge 与正文统计句属 hardcoded statistics，必须与真实数据一致。
# 分类表逐行计数由第 11 组负责（不重复实现）；本组只校验 badge + intro 汇总数。
if Path('README.md').exists():
    _rd = Path('README.md').read_text(encoding='utf-8')
    _real_png = len(all_pngs)
    _real_brand = len(ssot)
    _real_cat = len([d for d in ICONS.iterdir() if d.is_dir()])
    _real_active = sum(1 for d in ICONS.iterdir()
                       if d.is_dir() and any(d.rglob('*.png')))
    for _label, _n in (('icons', _real_png), ('brands', _real_brand),
                       ('categories', _real_cat)):
        _m = re.search(r'badge/%s-(\d+)-' % _label, _rd)
        if _m is None:
            fail('README 统计', 'badge 未找到: %s' % _label)
        elif int(_m.group(1)) != _n:
            fail('README 统计', 'badge %s=%s 实际=%d' % (_label, _m.group(1), _n))
    _mi = re.search(r'当前共 \*\*(\d+)\*\* 个 PNG 图标，覆盖 \*\*(\d+)\*\* 个品牌，归入 \*\*(\d+)\*\* 个', _rd)
    if _mi is None:
        fail('README 统计', 'intro 统计句未找到')
    elif (int(_mi.group(1)), int(_mi.group(2)), int(_mi.group(3))) != (_real_png, _real_brand, _real_cat):
        fail('README 统计', 'intro 汇总 %s 实际=%d/%d/%d'
             % (_mi.groups(), _real_png, _real_brand, _real_cat))
    _ma = re.search(r'（其中 (\d+) 个活跃', _rd)
    if _ma is not None and int(_ma.group(1)) != _real_active:
        fail('README 统计', 'intro 活跃分类=%s 实际=%d' % (_ma.group(1), _real_active))

    # 显式统计口径行（2026-10-01）：SSOT entities / canonical / icon-backed / PNG /
    # pending no-icon / categories / ecosystems 必须逐项等于实时值——禁止把「SSOT 条目数」
    # 与「有图标条目数」混写成模糊的「brands = N」。
    _mm = re.search(
        r'\*\*仓库统计口径 / Repository metrics\*\*：'
        r'SSOT entities \*\*(\d+)\*\* · canonical entities \*\*(\d+)\*\* · '
        r'icon-backed entities \*\*(\d+)\*\* · PNG \*\*(\d+)\*\* · '
        r'pending no-icon entities \*\*(\d+)\*\* · categories \*\*(\d+)\*\* · '
        r'ecosystems \*\*(\d+)\*\*', _rd)
    _real_canonical = sum(1 for e in brands_doc.get('brands', []) if is_canonical_brand(e))
    _real_iconbacked = sum(1 for e in brands_doc.get('brands', []) if e.get('icon_path'))
    _real_pending = sum(1 for e in brands_doc.get('brands', []) if not e.get('icon_path'))
    _real_eco = sum(1 for e in brands_doc.get('brands', []) if e.get('entity_type') == 'ecosystem')
    if _mm is None:
        fail('README 统计', '统计口径行未找到（Repository metrics）')
    else:
        _expect = (_real_brand, _real_canonical, _real_iconbacked, _real_png,
                   _real_pending, _real_cat, _real_eco)
        _got = tuple(int(x) for x in _mm.groups())
        if _got != _expect:
            fail('README 统计', '统计口径行 %s 实际 SSOT/canonical/icon-backed/PNG/pending/categories/ecosystems=%s'
                 % (_got, _expect))
    _me = re.search(r'（拥有自身一级生态分类者，当前 (\d+) 个', _rd)
    if _me is None:
        fail('README 统计', '生态根计数句未找到')
    elif int(_me.group(1)) != _real_eco:
        fail('README 统计', '生态根计数=%s 实际=%d' % (_me.group(1), _real_eco))
    # 官方资产表述（2026-10-01）：必须区分 Official source asset / Repository asset（规范化派生）/
    # Logo artwork，且不得声称官方原文件逐字节落库——docstring 级别的防漂移守卫。
    for _needle in ('**Official source asset**', '**Repository asset**', '**Logo artwork**',
                    '不是**官方原文件的逐字节落库'):
        if _needle not in _rd:
            fail('README 统计', '官方资产表述缺少 %r（须区分 source asset 与规范化派生）' % _needle)
    # SpaceXAI 资产状态句必须与 SSOT 一致（pending ↔ official 迁移后不得残留旧文）
    _sp = next((e for e in brands_doc.get('brands', []) if e.get('id') == 'SpaceXAI'), None)
    if _sp is not None:
        _msp = re.search(r'`SpaceXAI` 资产状态（generated）：`icon_status=([a-z_]+)`；`icon_path=([^`]+)`', _rd)
        if _msp is None:
            fail('README 统计', 'SpaceXAI 资产状态句未找到（generated）')
        elif (_msp.group(1), _msp.group(2)) != (_sp.get('icon_status'),
                                                _sp.get('icon_path') or '（无物理资产）'):
            fail('README 统计', 'SpaceXAI 资产状态句=%s 实际=%s'
                 % (_msp.groups(), (_sp.get('icon_status'), _sp.get('icon_path'))))
else:
    fail('README 统计', '缺少 README.md')

# ---------- 14. README 父节点（Parent README Policy：存在 + 内容） ----------
# 规则（docs/references/brand-naming-contract.md）：
#   任何拥有 ≥1 个 child brand 的物理品牌节点（physical_parent_nodes，动态计算，
#   非固定名单），其 icon 目录必须有 README.md（生态根 + 中间父品牌 + 更深层父品牌）；
#   叶子品牌不强制。
#   内容校验（§22-§25）：带 generated marker 的 README 必须与 expected_parent_readme()
#   逐字节相等（数据全部来自 brands.json + 动态关系解析）；人工 README 只做最低结构检查。
for _p in sorted(physical_parent_nodes(brands_doc)):
    if _p not in ssot or not ssot[_p].get('icon_path'):
        continue  # pending ecosystem / no-icon parent has semantic relation but no physical README dir
    _d = Path(ssot[_p]['icon_path']).parent
    _rdp = _d / 'README.md'
    if not _rdp.exists():
        fail('README 父节点', '父品牌缺 README: %s' % _p)
        continue
    _text = _rdp.read_text(encoding='utf-8')
    _first = _text.splitlines()[0].strip() if _text.splitlines() else ''
    if _first == '<!-- generated: parent-brand-readme (scripts/generate-category-readmes.sh) -->':
        if _text != expected_parent_readme(_p, ssot, aliases, ecosystem_category_ids(
                cats_doc.get('categories', []))):
            fail('README 父节点', '生成 README 内容与 expected 不一致: %s（运行 '
                 'scripts/generate-category-readmes.sh 重新生成）' % _p)
    else:
        # 人工 README：最低结构（含 display_name + 至少一个关系字段）
        if ssot[_p]['display_name'] not in _text:
            fail('README 父节点', '人工 README 缺 display_name: %s' % _p)
        if not re.search(r'Ancestor Chain|Direct Children|Parent:', _text):
            fail('README 父节点', '人工 README 缺关系结构: %s' % _p)

# ---------- 14b. 生态分类 README 关系树（§16/§48） ----------
# ecosystem 分类的 README 必须带 marker 段落，且逐字节等于 resolver 渲染的树；
# 禁止把孙代品牌平铺成一级子品牌（SpaceXAI ├── X ├── xAI └── Grok 为非法）。
for _cid in sorted(ecosystem_category_ids(cats_doc.get('categories', []))):
    _cd = ICONS / _cid / 'README.md'
    if not _cd.exists():
        fail('README 父节点', '生态分类缺 README: icons/%s/README.md' % _cid)
        continue
    _ct = _cd.read_text(encoding='utf-8')
    _blk = expected_ecosystem_readme_block(_cid, ssot)
    if _blk not in _ct:
        fail('README 父节点', '生态分类 README 缺/错关系树（应逐字节包含 resolver 渲染）: icons/%s/README.md'
             % _cid)
    if _cid in ssot and _cid in ssot[_cid].get('icon_path', ''):
        pass

# ---------- 15. 关系派生导出（downstream artifact，禁止成为第二 SSOT） ----------
# config/brand-relationships.json 由 scripts/export-brand-relationships.py 从
# brands.json + brand_relationships.py 生成；本组逐项重算并比对，防止手工修改或漂移。
REL_PATH = Path('config/brand-relationships.json')
if not REL_PATH.exists():
    fail('关系派生导出', '缺少 %s（运行 scripts/export-brand-relationships.py）' % REL_PATH)
else:
    import subprocess as _sp
    _rel = json.loads(REL_PATH.read_text(encoding='utf-8'))
    if _rel.get('generated') is not True or _rel.get('source') != 'config/brands.json':
        fail('关系派生导出', '缺少 generated: true / source=config/brands.json 标注'
             '（派生文件必须标出来源，避免被当成第二个 SSOT）')
    _build_rel = None
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            'export_brand_relationships', Path('scripts/export-brand-relationships.py'))
        _mod = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)  # type: ignore[union-attr]
        _build_rel = _mod.build
    except Exception as _exc:  # noqa: BLE001
        fail('关系派生导出', '无法加载 scripts/export-brand-relationships.py: %s' % str(_exc)[:80])
    if _build_rel is not None:
        _expected = _build_rel(brands_doc, cats_doc.get('categories', []))
        _rows = {r['child']: r for r in _rel.get('brands', [])}
        _exp_rows = {r['child']: r for r in _expected['brands']}
        for _b in sorted(set(_exp_rows) - set(_rows)):
            fail('关系派生导出', '派生导出缺失品牌: %s' % _b)
        for _b in sorted(set(_rows) - set(_exp_rows)):
            fail('关系派生导出', '派生导出多余品牌（SSOT 无）: %s' % _b)
        for _b in sorted(set(_rows) & set(_exp_rows)):
            if _rows[_b] != _exp_rows[_b]:
                fail('关系派生导出', '派生导出与 SSOT/关系引擎不一致: %s（实=%s 期望=%s）'
                     % (_b, _rows[_b], _exp_rows[_b]))
        if _rel.get('whitelist_parents_without_icon') != _expected['whitelist_parents_without_icon']:
            fail('关系派生导出', '白名单母公司列表与 SSOT 不一致')

# ---------- 16. Review Queue（人工裁决队列，不得覆盖 SSOT） ----------
RQ_PATH = Path('config/brand-review-queue.json')
if not RQ_PATH.exists():
    fail('Review Queue', '缺少 %s' % RQ_PATH)
else:
    _rq = json.loads(RQ_PATH.read_text(encoding='utf-8'))
    _allowed_status = set(_rq.get('status_values') or [])
    _allowed_kinds = set(_rq.get('issue_kinds') or [])
    if _rq.get('is_ssot') is not False:
        fail('Review Queue', '必须显式声明 is_ssot: false（关系 SSOT 只能是 config/brands.json）')
    if _allowed_status != {'OPEN', 'RESOLVED'}:
        fail('Review Queue', 'status_values 必须恰为 {OPEN, RESOLVED}: %s' % sorted(_allowed_status))
    _seen = set()
    for _it in _rq.get('items', []):
        _iid = _it.get('id', '')
        if not _iid:
            fail('Review Queue', '条目缺少 id')
        if _iid in _seen:
            fail('Review Queue', '条目 id 重复: %s' % _iid)
        _seen.add(_iid)
        if _it.get('status') not in _allowed_status:
            fail('Review Queue', '状态非法: %s (%r)' % (_iid, _it.get('status')))
        if _it.get('issue_kind') not in _allowed_kinds:
            fail('Review Queue', 'issue_kind 非法: %s (%r)' % (_iid, _it.get('issue_kind')))
        _ch = _it.get('child')
        if _ch and _ch not in ssot and _ch not in aliases:
            fail('Review Queue', 'child 既不在 SSOT 也不在白名单: %s (%s)' % (_iid, _ch))
        _cp = _it.get('candidate_parent')
        if _cp and _cp not in ssot and _cp not in aliases:
            fail('Review Queue', 'candidate_parent 既不在 SSOT 也不在白名单: %s (%s)' % (_iid, _cp))
        if _it.get('status') == 'RESOLVED' and not _it.get('resolved_note'):
            fail('Review Queue', 'RESOLVED 条目必须带 resolved_note（记录裁决结论）: %s' % _iid)

# ---------- 17. 物理路径（递归多层嵌套，§5/§6/§9-§11/§19-§21） ----------
# 一级目录 = category；同类中间父品牌下的深层子品牌必须物理嵌套；icon_path 必须等于
# 统一解析器 expected_icon_path() 的结果（禁止手工随意填写，§21）。
for _p_err in validate_physical_paths(brands_doc, cats_doc.get('categories', []), '.'):
    fail('物理路径', _p_err)

# 审计文档（全库矩阵）必须与重算结果逐字节一致（§38/§46/§47）
_PHA = Path('docs/references/physical-hierarchy-audit.md')
if not _PHA.exists():
    fail('物理路径', '缺少 %s（运行 scripts/gen-physical-hierarchy-audit.py）' % _PHA)
else:
    try:
        import importlib.util as _ilu2
        _spec2 = _ilu2.spec_from_file_location(
            'gen_physical_hierarchy_audit', Path('scripts/gen-physical-hierarchy-audit.py'))
        _mod2 = _ilu2.module_from_spec(_spec2)
        _spec2.loader.exec_module(_mod2)  # type: ignore[union-attr]
        _exp_text, _ = _mod2.build(brands_doc, cats_doc.get('categories', []))
        if _PHA.read_text(encoding='utf-8') != _exp_text:
            fail('物理路径', '关系矩阵文档与重算不一致: %s（运行 '
                 'scripts/gen-physical-hierarchy-audit.py 重新生成）' % _PHA)
    except Exception as _exc2:  # noqa: BLE001
        fail('物理路径', '无法校验 %s: %s' % (_PHA, str(_exc2)[:80]))

# ---------- 结果：按验证组报告 ----------
expected_groups = ['PNG integrity', 'Image spec', 'Naming', 'Category',
                   'Canonical uniqueness', 'SHA-256 uniqueness', 'Brands SSOT',
                   'Surge JSON', 'Glossary', 'Legacy paths',
                   'README 表格', '生态一致性', 'README 统计', 'README 父节点',
                   '关系派生导出', 'Review Queue', '物理路径']
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
