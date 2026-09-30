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


def _ancestor_set(bid, ssot, depth=100):
    """返回 bid 的全部祖先品牌集合（不含自身）。链断在：无 parent / parent 不在 SSOT。"""
    seen = set()
    cur = ssot.get(bid, {}).get('parent_brand')
    while cur and depth > 0:
        if cur in seen:
            break
        seen.add(cur)
        if cur not in ssot:
            break
        cur = ssot.get(cur, {}).get('parent_brand')
        depth -= 1
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


def _root_of(bid, ssot, depth=100):
    """沿 parent_brand 链向上，返回 graph root（关系图最高节点）。

    链断在：无 parent / parent 不在 SSOT（白名单母公司）/ 环。
    注意：graph root ≠ ecosystem root（见 resolve_ecosystem_root）。
    """
    seen = {bid}
    last = bid
    cur = ssot.get(bid, {}).get('parent_brand')
    while cur and depth > 0:
        if cur in seen:
            break
        seen.add(cur)
        last = cur
        if cur not in ssot:
            break
        cur = ssot.get(cur, {}).get('parent_brand')
        depth -= 1
    return last


def resolve_graph_root(bid, ssot):
    """对外 API：派生某品牌所在关系图的 graph root（动态，不存储）。

    graph root 是图结构顶端，**不保证**是独立生态：
    resolve_graph_root('Mijia') == 'Xiaomi'（Xiaomi 无独立生态分类）。
    """
    return _root_of(bid, ssot)


def resolve_ecosystem_root(bid, ssot):
    """对外 API：派生某品牌所属的独立生态根（动态，不存储）。

    返回 bid 的 graph root；若该 graph root 的 entity_type 不是 ecosystem，
    返回 None（如 Mijia → Xiaomi → None）。
    注意：本 API 于 2026-09-30 收口为严格语义（此前对非生态 graph root 也
    返回 root 本身，语义已废弃）。
    """
    g = _root_of(bid, ssot)
    if g in ssot and ssot[g].get('entity_type') == 'ecosystem':
        return g
    return None


def physical_parent_nodes(brands_doc):
    """全部物理父节点：拥有 ≥1 个 child brand 的 SSOT 节点。

    白名单母公司（parent_brands_without_icon）无自身图标/目录，不属物理节点。
    这是 Parent README Policy 的作用域（CI 第 13 组 / 生成器 / 测试共用）。
    """
    ssot = {e['id']: e for e in brands_doc.get('brands', []) if e.get('id')}
    child_map = {}
    for e in brands_doc.get('brands', []):
        p = e.get('parent_brand')
        if p:
            child_map.setdefault(p, []).append(e['id'])
    return {p for p in child_map if p in ssot}


def brand_role(bid, ssot):
    """父品牌节点角色（三态）：

    - Ecosystem Root:         graph root + entity_type=ecosystem（独立一级生态）
    - Graph Root Parent:      graph root + 有子 + 未构成独立生态
                               （如 SINA → Weibo、Xiaomi → Mijia）
    - Intermediate Parent Brand: 有（SSOT 内）父 + 有子（如 Facebook、YouTube）

    阈值若未来使某 Graph Root Parent 的 descendants ≥ 2，CI 反向规则会要求
    其声明 entity_type=ecosystem，届时角色自动变为 Ecosystem Root。
    """
    e = ssot.get(bid)
    if e is None:
        return None
    p = e.get('parent_brand')
    if p and p in ssot:
        return 'Intermediate Parent Brand'
    if e.get('entity_type') == 'ecosystem':
        return 'Ecosystem Root'
    return 'Graph Root Parent'


def expected_parent_readme(bid, ssot):
    """生成父品牌 README 的确定性规范内容（供 CI 等价校验与生成器共用）。

    数据全部来自 SSOT + 动态关系解析；任何手工改动都会在第 13 组被拦截。
    """
    e = ssot[bid]
    dn = e['display_name']
    role = brand_role(bid, ssot)
    parent = e.get('parent_brand') or '—'
    gr = _root_of(bid, ssot)
    er = gr if (gr in ssot and ssot[gr].get('entity_type') == 'ecosystem') else '—'
    chain = [bid] + list(_ancestor_set_ordered(bid, ssot))
    kids = sorted(x['id'] for x in ssot.values() if x.get('parent_brand') == bid)
    if role == 'Ecosystem Root':
        title = '# %s / %s 生态根品牌' % (dn, dn)
    elif role == 'Graph Root Parent':
        title = '# %s 父品牌（Graph Root）' % dn
    else:
        title = '# %s / %s 生态父品牌' % (dn, ssot[gr]['display_name'])
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


def _ancestor_set_ordered(bid, ssot, depth=100):
    """返回按 直接父 → … → graph root 顺序排列的祖先链（不含自身）。"""
    out = []
    seen = {bid}
    cur = ssot.get(bid, {}).get('parent_brand')
    while cur and depth > 0:
        if cur in seen:
            break
        out.append(cur)
        seen.add(cur)
        if cur not in ssot:
            break
        cur = ssot.get(cur, {}).get('parent_brand')
        depth -= 1
    return out


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
