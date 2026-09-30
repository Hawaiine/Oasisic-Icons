#!/usr/bin/env python3
"""品牌关系图校验（直接父品牌语义 + 双向生态阈值 + 动态派生 graph/ecosystem root）。

纯函数模块：输入 brands.json 数据 + categories.json，返回错误列表（空 = 通过）。
ci-validate-icons.py 将其并入「生态一致性」组；tests/test_brand_relationships.py
用同一函数跑负测（cycle / self-parent / missing parent / wrong root / threshold 双向）。

数据模型（2026-09 重构，2026-09-30 收口）：
- parent_brand = 直接父品牌（immediate parent），不再一律指向顶层生态。
  例：Instagram → Facebook；YouTubeMusic → YouTube；iCloudPrivateRelay → iCloud。
- **Graph Root ≠ Ecosystem Root**（2026-09-30 明确区分）：
  - graph root = 沿 parent_brand 向上走到的关系图最高节点（无 parent，或 parent
    不在 SSOT）；
  - ecosystem root = graph root 且 entity_type=ecosystem（构成独立一级生态分类）。
  例：Mijia → Xiaomi：graph root = Xiaomi，但 Xiaomi 当前不满足/未构成独立生态，
  故 ecosystem root = None。Meta：graph root = Meta = ecosystem root。
- 生态阈值（**双向**）：
  - 正向：entity_type=ecosystem → canonical descendants ≥ 2；
  - 反向：有 SSOT 条目的 graph root canonical descendants ≥ 2 → 必须声明
    entity_type=ecosystem（白名单母公司无条目/无 icon，登记白名单即豁免）。
    阈值**只作用于 graph root**，中间层节点（Facebook
    有 2+ descendants）不得因此升级成一级生态。
- canonical descendant = entity_type=product_brand 的后代（`is_canonical_brand`）；
  country / system_icon / tool_app / ecosystem 不计入阈值统计。
- category 回答「图标放哪个一级目录」，parent_brand 回答「直接属于哪个品牌」，
  两者独立（如 Mijia: category=Home, parent_brand=Xiaomi）。
- 生态根**不存字段**——消费方调用 resolve_ecosystem_root() 动态派生。

父品牌 README（docs/references/brand-naming-contract.md §Parent README Policy）：
- 任何拥有 ≥1 个 child brand 的物理品牌节点（physical_parent_nodes），其 icon
  目录必须拥有 README.md；叶子品牌不强制。
- brand_role 三态：Ecosystem Root（graph root + ecosystem）/ Graph Root Parent
  （graph root + 有子 + 无独立生态）/ Intermediate Parent Brand（有父 + 有子）。
- expected_parent_readme() 产出确定性内容（CI 第 13 组做逐字节等价校验；
  无 marker 的人工 README 只做最低结构检查）。

CI 只验证**结构一致性**（图无环、无自指、父存在、root 解析正确、双向阈值、
父 README 内容一致）；现实世界归属的完整性与证据由
docs/references/brand-ownership-audit.md 承担。
"""
import re
import sys
from pathlib import Path

# 允许作为脚本直接运行时 import 同目录模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

# 父品牌 README 生成标记（单一来源：生成器与 CI/tests 都必须引用此常量，
# 不得各自硬编码——标记必须指向真实存在的生成入口）。
PARENT_README_MARKER = '<!-- generated: parent-brand-readme (scripts/generate-category-readmes.sh) -->'

# ---------------------------------------------------------------------------
# 物理路径模型（2026-10-01 定稿，§5/§6/§9/§10/§11/§21）
#
#   一级目录 = category（不因关系改变）
#   同一 category 内，若 child 的直接父品牌本身也有父品牌（中间父品牌），
#   则 child 必须物理嵌套在父品牌目录下：
#
#       icons/<category>/<中间父…>/<id>/<id>.png
#
#   例：icons/Meta/Facebook/Instagram/Instagram.png
#       icons/SpaceXAI/xAI/Grok/Grok.png
#
#   不嵌套（保持 icons/<category>/<id>/<id>.png）：
#     - 直接父品牌就是 category 根（一级 direct child，如 AppleMusic → Apple）；
#     - 直接父品牌属其它 category（cross-category，如 Mijia → Xiaomi，不机械迁移）；
#     - 直接父品牌无自身图标（parent_brands_without_icon，无目录可嵌套，如 Kimi → MoonshotAI）。
#
#   expected_icon_path() 是唯一路径推导入口：brands.json / 文件系统 / Surge /
#   Glossary / CI / 生成器全部跟随它，禁止在别处再写第二套路径规则。
# ---------------------------------------------------------------------------


def _ancestor_set(bid, ssot):
    """返回 bid 的全部祖先品牌集合（不含自身）。

    终止条件（无 arbitrary depth 上限）：
    - 环：cur 已在 seen → break（循环检测负责终止）；
    - 链断：cur 不在 SSOT（白名单母公司）→ break。
    深链（A1→…→A101→Root）由 seen 去重自然收敛，不设 magic number。
    """
    seen = set()
    cur = ssot.get(bid, {}).get('parent_brand')
    while cur:
        if cur in seen:
            break
        seen.add(cur)
        if cur not in ssot:
            break
        cur = ssot.get(cur, {}).get('parent_brand')
    return seen


def is_canonical_brand(entry):
    """判断一个品牌记录是否为 canonical active product brand。

    canonical descendant（阈值统计）只计入 product_brand；
    ecosystem（根自身）/ country / system_icon / tool_app 不计入。
    可复用的单一 predicate——不要在多处散落 `if entity_type == ...`。
    """
    return entry.get('entity_type') == 'product_brand'


def _descendants(root, ssot):
    """返回 root 的全部 canonical descendants（product_brand 后代，不含 root 本身）。

    root 可以是 SSOT 品牌或白名单母公司（无自身条目）。
    """
    return {bid for bid, e in ssot.items()
            if bid != root and is_canonical_brand(e) and root in _ancestor_set(bid, ssot)}


def _root_of(bid, ssot):
    """沿 parent_brand 链向上，返回 graph root（关系图最高节点）。

    无 arbitrary depth 上限：终止靠 seen 环检测 + 链断（无 parent / parent 不
    在 SSOT 白名单母公司）。深链（A1→…→A101→Root）自然收敛，不设 magic number。
    注意：graph root ≠ ecosystem root（见 resolve_ecosystem_root）。
    """
    seen = {bid}
    last = bid
    cur = ssot.get(bid, {}).get('parent_brand')
    while cur:
        if cur in seen:
            break
        seen.add(cur)
        last = cur
        if cur not in ssot:
            break
        cur = ssot.get(cur, {}).get('parent_brand')
    return last


def resolve_graph_root(bid, ssot):
    """对外 API：派生某品牌所在关系图的 graph root（动态，不存储）。

    graph root 是图结构顶端，**不保证**是独立生态：
    resolve_graph_root('Mijia') == 'Xiaomi'（Xiaomi 无独立生态分类）。
    """
    return _root_of(bid, ssot)


def ecosystem_category_ids(cats_list):
    """返回 type=ecosystem 的一级生态分类 ID 集合（categories.json 单一来源）。"""
    return {c['id'] for c in (cats_list or []) if c.get('type') == 'ecosystem'}


def resolve_ecosystem_root(bid, ssot, eco_cat_ids=None):
    """对外 API：派生某品牌所属的独立生态根（动态，不存储）。

    两种合法生态根（§13/§14/§26）：
      1. graph root 有 SSOT 条目且 entity_type == ecosystem；
      2. graph root 无 SSOT 条目（官方标志待补 → 登记 parent_brands_without_icon）
         但存在 type=ecosystem 的一级生态分类 → 它仍是该生态的逻辑生态根。
         「无图标」不等于「不是生态」（§26）：ecosystem identity = YES，
         icon availability = PENDING，两者独立。

    若 graph root 两者皆不满足，返回 None（如 Mijia → Xiaomi → None）。
    """
    g = _root_of(bid, ssot)
    if g in ssot and ssot[g].get('entity_type') == 'ecosystem':
        return g
    if eco_cat_ids and g not in ssot and g in eco_cat_ids:
        return g
    return None


def expected_icon_path(bid, ssot):
    """唯一物理路径推导入口：由 category + 可表达的物理父层级推出 canonical icon_path。

    算法（§5/§6/§10/§11）：
      - 从直接父品牌向上收集「同 category 且自身有图标」的祖先链；遇到白名单
        母公司（不在 SSOT）或跨 category 父品牌即停止（停止点以上的祖先也不可
        嵌套——那一层物理目录并不存在）；
      - 把该前缀按「根→叶」反序拼进路径，跳过与 category 同名的那一级
        （category 目录本身就是一级）。
    纯函数：只读关系数据，不读文件系统。
    """
    e = ssot.get(bid)
    if not e:
        return None
    cat = e.get('category', '')
    chain = []
    seen = {bid}                         # 环保护：路径推导绝不允许死循环
    cur = e.get('parent_brand')
    while cur:
        if cur in seen:                  # 自指 / 环（关系引擎会报错，这里只保证终止）
            break
        seen.add(cur)
        if cur not in ssot:
            break                        # 白名单母公司：无目录，不能嵌套（§11）
        if ssot[cur].get('category') != cat:
            break                        # 跨分类父品牌：不机械迁移（§10）
        nxt = ssot[cur].get('parent_brand')
        if not nxt or nxt in seen:
            break                        # §6：graph root 的直系子品牌保持平铺
                                         #（AppleMusic → Apple、myTVSUPER → TVB）
        chain.append(cur)
        cur = nxt
    parts = [cat]
    for a in reversed(chain):
        if a != cat:
            parts.append(a)
    parts.append(bid)
    return 'icons/%s/%s.png' % ('/'.join(parts), bid)


def physical_brand_dir(bid, ssot):
    """品牌物理目录（= icon_path 的父目录）。派生，不存储。"""
    ip = ssot.get(bid, {}).get('icon_path') or expected_icon_path(bid, ssot)
    return str(Path(ip).parent) if ip else None


def validate_physical_paths(brands_doc, cats_list, repo_root='.'):
    """物理路径校验（§19/§20）：返回错误列表，空 = 通过。

    覆盖：category 一级目录合法；品牌目录 basename == id；叶子文件名 == id.png；
    icon_path 必须等于 expected_icon_path()（§21 禁止手工随意填写）；
    同类深层中间父品牌必须物理嵌套；cross-category 父品牌不得被机械嵌套；
    白名单母公司不得被制造出伪目录（§11）。
    """
    errs = []
    ssot = {e['id']: e for e in brands_doc.get('brands', []) if e.get('id')}
    aliases = set(brands_doc.get('parent_brands_without_icon', []))
    cat_ids = {c['id'] for c in (cats_list or [])}
    root = Path(repo_root)

    def fail(msg):
        errs.append(msg)

    for bid, e in sorted(ssot.items()):
        cat = e.get('category', '')
        ip = e.get('icon_path', '')
        exp = expected_icon_path(bid, ssot)
        if cat not in cat_ids:
            fail('category 非法: %s -> %s' % (bid, cat))
            continue
        if ip != exp:
            fail('icon_path 与路径规则不符: %s 应为 %s' % (ip, exp))
            continue
        path = root / ip
        if not path.exists():
            fail('icon 文件不存在: %s' % ip)
            continue
        if path.parent.name != bid:
            fail('品牌目录 basename != id: %s（目录 %s）' % (bid, path.parent.name))
        if path.name != '%s.png' % bid:
            fail('叶子文件名 != id.png: %s' % ip)
        if path.relative_to(root / 'icons').parts[0] != cat:
            fail('一级目录 != category: %s' % ip)
        par = e.get('parent_brand')
        # §5/§6：只有「父品牌自身**也有**父品牌」（非 graph root 的中间父品牌）
        # 才要求物理嵌套；graph root 的直系子品牌保持平铺
        # （AppleMusic → Apple、AWS → Amazon）。
        if (par and par in ssot and ssot[par].get('category') == cat
                and ssot[par].get('parent_brand')):
            pdir = (root / ssot[par]['icon_path']).parent
            if pdir == path.parent:
                fail('同类父品牌目录冲突（未嵌套）: %s' % bid)
            elif pdir not in path.parents:
                fail('同类深层父品牌未物理嵌套: %s 应位于 %s 之下'
                     % (bid, str(pdir.relative_to(root))))
        if par and par in ssot and ssot[par].get('category') != cat:
            other = ssot[par]['category']
            if other in path.relative_to(root / 'icons').parts:
                fail('cross-category 父品牌被机械迁移: %s 出现在 %s/' % (bid, other))
        if par and par not in ssot:
            if par not in aliases:
                fail('parent_brand 既不在 SSOT 也不在白名单: %s -> %s' % (bid, par))
            ghost = root / 'icons' / cat / par
            if ghost.exists():
                fail('为无图标母公司制造了伪目录: %s（%s 无自身图标）'
                     % (str(ghost.relative_to(root)), par))
    return errs


def physical_parent_nodes(brands_doc):
    """全部物理父节点：拥有 ≥1 个 **canonical child brand** 的 SSOT 节点。

    只有 canonical product_brand 子节点才使父节点成为物理父节点：
    system_icon / tool_app / country 等非品牌子节点不计入——否则会出现
    「仅因某个 SystemIcon 挂在 Parent 下，Parent 就必须有父 README」的误判。
    白名单母公司（parent_brands_without_icon）无自身图标/目录，不属物理节点。
    这是 Parent README Policy 的作用域（CI 第 14 组 / 生成器 / 测试共用）。
    """
    ssot = {e['id']: e for e in brands_doc.get('brands', []) if e.get('id')}
    child_map = {}
    for e in brands_doc.get('brands', []):
        p = e.get('parent_brand')
        if p and is_canonical_brand(e):
            child_map.setdefault(p, []).append(e['id'])
    return {p for p in child_map if p in ssot}


def brand_role(bid, ssot, aliases=None):
    """父品牌节点角色（三态）：

    - Ecosystem Root:         graph root + entity_type=ecosystem（独立一级生态）
    - Graph Root Parent:      graph root + 有子 + 未构成独立生态
                               （如 SINA → Weibo、Xiaomi → Mijia）
    - Intermediate Parent Brand: 有父（SSOT 内父品牌**或**白名单母公司，如
                              Facebook / YouTube / xAI → SpaceXAI）+ 有子

    阈值若未来使某 Graph Root Parent 的 descendants ≥ 2，CI 反向规则会要求
    其声明 entity_type=ecosystem，届时角色自动变为 Ecosystem Root。
    注意（§15）：父品牌即使无自身图标（白名单母公司），child 依然是
    Intermediate Parent Brand，不得因父无条目而降级成 Graph Root Parent。
    """
    e = ssot.get(bid)
    if e is None:
        return None
    aliases = set(aliases or ())
    p = e.get('parent_brand')
    if p and (p in ssot or p in aliases):
        return 'Intermediate Parent Brand'
    if e.get('entity_type') == 'ecosystem':
        return 'Ecosystem Root'
    return 'Graph Root Parent'


def expected_parent_readme(bid, ssot, aliases=None, eco_cat_ids=None):
    """生成父品牌 README 的确定性规范内容（供 CI 等价校验与生成器共用）。

    数据全部来自 SSOT + 动态关系解析；任何手工改动都会在第 13 组被拦截。
    """
    e = ssot[bid]
    dn = e['display_name']
    role = brand_role(bid, ssot, aliases)
    parent = e.get('parent_brand') or '—'
    gr = _root_of(bid, ssot)
    er = resolve_ecosystem_root(bid, ssot, eco_cat_ids) or '—'
    chain = [bid] + list(_ancestor_set_ordered(bid, ssot))
    kids = sorted(x['id'] for x in ssot.values()
                  if x.get('parent_brand') == bid and is_canonical_brand(x))
    if role == 'Ecosystem Root':
        title = '# %s / %s 生态根品牌' % (dn, dn)
    elif role == 'Graph Root Parent':
        title = '# %s 父品牌（Graph Root）' % dn
    else:
        # 生态父品牌标题中的「生态名」取逻辑生态根的 display_name；根无 SSOT 条目
        # （官方标志待补的白名单母公司，如 SpaceXAI）时退回其 id，禁止 KeyError。
        _eco = er if er != '—' else gr
        _eco_dn = ssot[_eco]['display_name'] if _eco in ssot else _eco
        title = '# %s / %s 生态父品牌' % (dn, _eco_dn)
    lines = [
        PARENT_README_MARKER,
        '',
        title,
        '',
        '```text',
        'Brand:        %s' % bid,
        'Display Name: %s' % dn,
        'Role:         %s' % role,
        'Parent:       %s' % parent,
        'Graph Root:   %s' % gr,
        'Ecosystem Root: %s' % er,
        'Ancestor Chain: %s' % ' → '.join(chain),
        'Direct Children: %d' % len(kids),
        '```',
        '',
        '| Child | Display Name |',
        '|:---|:---|',
    ]
    for k in kids:
        lines.append('| `%s` | %s |' % (k, ssot[k]['display_name']))
    lines.append('')
    return '\n'.join(lines)


def _ancestor_set_ordered(bid, ssot):
    """返回按 直接父 → … → graph root 顺序排列的祖先链（不含自身）。

    无 arbitrary depth 上限：终止靠 seen 环检测 + 链断，深链自然收敛。
    """
    out = []
    seen = {bid}
    cur = ssot.get(bid, {}).get('parent_brand')
    while cur:
        if cur in seen:
            break
        out.append(cur)
        seen.add(cur)
        if cur not in ssot:
            break
        cur = ssot.get(cur, {}).get('parent_brand')
    return out


ECO_TREE_MARKER = '<!-- generated: ecosystem-tree (scripts/generate-category-readmes.sh) -->'


def _tree_lines(bid, ssot, prefix=''):
    """递归渲染直接子品牌（canonical product_brand），按 id 稳定排序。"""
    kids = sorted(x['id'] for x in ssot.values()
                  if x.get('parent_brand') == bid and is_canonical_brand(x))
    out = []
    for i, k in enumerate(kids):
        last = (i == len(kids) - 1)
        out.append('%s%s %s' % (prefix, '└──' if last else '├──', k))
        out.extend(_tree_lines(k, ssot, prefix + ('    ' if last else '│   ')))
    return out


def expected_ecosystem_tree(root, ssot):
    """生态关系树的确定性渲染（R0 逻辑生态根 + 全部后代，逐层嵌套）。

    生态分类 README 用它表达真实层级，禁止出现把孙代品牌平铺成一级子品牌的树
    （§16/§48：SpaceXAI ├── X └── xAI └── Grok）。
    """
    return '\n'.join(['```text', root] + _tree_lines(root, ssot, '') + ['```'])


def expected_ecosystem_readme_block(root, ssot):
    """生态分类 README 的树段落（带 marker，供生成器写入 / CI 逐字节校验）。"""
    return '%s\n\n%s\n' % (ECO_TREE_MARKER, expected_ecosystem_tree(root, ssot))


def validate_relationships(brands_doc, cats_list):
    """校验品牌关系图，返回错误字符串列表（空列表 = 通过）。

    brands_doc: brands.json 解析后的 dict（含 brands / parent_brands_without_icon）
    cats_list:  categories.json 的 categories 列表
    """
    errs = []

    ssot = {}
    for e in brands_doc.get('brands', []):
        bid = e.get('id', '')
        if bid:
            ssot[bid] = e
    aliases = set(brands_doc.get('parent_brands_without_icon', []))
    cats = cats_list or []
    eco_cat_ids = {c['id'] for c in cats if c.get('type') == 'ecosystem'}

    def fail(msg):
        errs.append(msg)

    # ---- 1. parent_brand：非自指、存在（或在白名单）、无环、链末端存在 ----
    for bid, e in ssot.items():
        p = e.get('parent_brand')
        if not p:
            continue
        if p == bid:
            fail('parent_brand 自指: %s' % bid)
            continue
        if p not in ssot:
            if p not in aliases:
                fail('parent_brand 不存在: %s -> %s' % (bid, p))
            continue
        # 循环检测 + 链末端存在性
        chain, seen = [bid], {bid}
        cur = p
        while cur in ssot and ssot[cur].get('parent_brand'):
            nxt = ssot[cur]['parent_brand']
            if nxt in seen:
                fail('parent_brand 循环: %s' % ' -> '.join(chain + [nxt]))
                break
            seen.add(nxt)
            chain.append(nxt)
            cur = nxt
        else:
            # 循环未 break：cur 已走出 ssot（其 parent 不在 ssot）或到达顶端
            if cur not in ssot and cur not in aliases:
                fail('parent_brand 链末端不存在: %s' % ' -> '.join(chain + [cur]))

    # ---- 2. 白名单纯净：不得含已有 canonical icon 的品牌 ----
    for a in aliases:
        if a in ssot:
            fail('parent_brands_without_icon 含已有 icon 的品牌: %s' % a)

    # ---- 2b. 父节点类型合法性（§49-§53）：父品牌只能是 product_brand / ecosystem ----
    # country / system_icon / tool_app 不是品牌节点，不得作为 parent_brand
    # （否则会凭空制造「品牌挂在国家/系统图标下」的关系）。
    ALLOWED_PARENT_TYPES = {'product_brand', 'ecosystem'}
    for bid, e in sorted(ssot.items()):
        p = e.get('parent_brand')
        if not p or p not in ssot:
            continue
        pt = ssot[p].get('entity_type')
        if pt not in ALLOWED_PARENT_TYPES:
            fail('parent_brand 类型非法: %s -> %s（父 entity_type=%s，仅允许 %s）'
                 % (bid, p, pt, sorted(ALLOWED_PARENT_TYPES)))

    # ---- 3. 正向：entity_type=ecosystem 品牌 → category=自身 + 对应生态分类 + descendants≥2 + root icon ----
    eco_roots = {bid for bid, e in ssot.items() if e.get('entity_type') == 'ecosystem'}
    for root in sorted(eco_roots):
        e = ssot[root]
        if e.get('category') != root:
            fail('entity_type=ecosystem 的 %s 未以自身为一级分类: %s' % (root, e.get('category')))
        if root not in eco_cat_ids:
            fail('entity_type=ecosystem 的 %s 无对应生态分类（type=ecosystem）' % root)
        ds = _descendants(root, ssot)
        if len(ds) < 2:
            fail('生态根 %s 的 canonical descendants < 2（%d 个，仅计 product_brand）' % (root, len(ds)))
        p = e.get('parent_brand')
        if p:
            fail('entity_type=ecosystem 的 %s 不应再有 parent_brand（生态根必须是关系图顶端；'
                 '中间层品牌一律 product_brand）: %s' % (root, p))
        ipath = e.get('icon_path', '')
        if not ipath:
            fail('生态根 %s 无 icon（brands.json 条目必须带 canonical icon；'
                 '若 root 确实无图标，不要建 brands.json 条目，改登记白名单）' % root)
        elif not ipath.startswith('icons/%s/' % root):
            fail('生态根 %s 的 icon 不在生态目录内: %s' % (root, ipath))

    # ---- 4. 位于生态分类内的非根品牌 → 祖先链必须经过该分类的 root ----
    for bid, e in ssot.items():
        c = e.get('category')
        if c in eco_cat_ids and bid != c:
            if c not in _ancestor_set(bid, ssot):
                fail('位于生态分类 %s/ 但祖先链未经过根 %s: %s（parent=%s）'
                     % (c, c, bid, e.get('parent_brand') or '无'))

    # ---- 5. 反向：生态分类 → 根品牌（有 SSOT 条目则 entity_type=ecosystem；无条目则须登记白名单）+ descendants≥2 ----
    for cid in sorted(eco_cat_ids):
        e = ssot.get(cid)
        if not e:
            if cid not in aliases:
                fail('生态分类 %s 无对应品牌条目且未登记白名单' % cid)
            continue
        if e.get('entity_type') != 'ecosystem':
            fail('生态分类 %s 的根品牌 entity_type 非 ecosystem: %s' % (cid, e.get('entity_type')))
        if len(_descendants(cid, ssot)) < 2:
            fail('生态分类 %s 的根 canonical descendants < 2' % cid)

    # ---- 6. 反向阈值（2026-09-30 新增）：graph root canonical descendants ≥ 2 → 必须 ecosystem ----
    # 阈值只作用于「有 SSOT 条目的」graph root，中间层节点不适用：
    # Facebook（有 SSOT 父 Meta）即使 descendants ≥ 2 也不得被要求升级生态。
    # 白名单母公司（无 SSOT 条目、无 icon）天然无法声明 entity_type=ecosystem，
    # 其白名单登记本身就是反向阈值的豁免（见第 5 组：生态分类无条目→须登记白名单）。
    for bid, e in ssot.items():
        if e.get('entity_type') == 'ecosystem':
            continue  # 已由第 3 组正向规则覆盖（含 descendants ≥ 2）
        if e.get('parent_brand') and e['parent_brand'] in ssot:
            continue  # 中间层（有 SSOT 内父品牌）：阈值不适用，不得升级
        ds = _descendants(bid, ssot)
        if len(ds) >= 2:
            fail('graph root %s 的 canonical descendants ≥ 2（%d 个）但 entity_type 非 ecosystem: %s'
                 '（双向阈值规则：此类 root 必须声明 entity_type=ecosystem + 建立一级生态分类；'
                 '若确实不应成生态，请调整子品牌的 parent_brand 引用）'
                 % (bid, len(ds), e.get('entity_type')))

    return errs


if __name__ == '__main__':
    # 直接运行：对当前仓库做关系校验（供手动排查）
    import json
    repo = Path(__file__).resolve().parent.parent
    brands_doc = json.loads((repo / 'config' / 'brands.json').read_text(encoding='utf-8'))
    cats_doc = json.loads((repo / 'config' / 'categories.json').read_text(encoding='utf-8'))
    problems = validate_relationships(brands_doc, cats_doc.get('categories', []))
    if problems:
        for p in problems:
            print('✗', p)
        sys.exit(1)
    print('Relationship graph: PASS (%d brands, %d ecosystem roots, %d physical parent nodes)'
          % (len(brands_doc.get('brands', [])),
             len({b['id'] for b in brands_doc.get('brands', [])
                  if b.get('entity_type') == 'ecosystem'}),
             len(physical_parent_nodes(brands_doc))))
