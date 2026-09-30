#!/usr/bin/env python3
"""品牌关系图校验（直接父品牌语义 + 动态可派生生态根）。

纯函数模块：输入 brands.json 数据 + categories.json，返回错误列表（空 = 通过）。
ci-validate-icons.py 将其并入「生态一致性」组；tests/test_brand_relationships.py
用同一函数跑负测（cycle / self-parent / missing parent / wrong root / threshold）。

数据模型（2026-09 重构）：
- parent_brand = 直接父品牌（immediate parent），不再一律指向顶层生态。
  例：Instagram → Facebook；YouTubeMusic → YouTube；iCloudPrivateRelay → iCloud。
- 生态根（ecosystem root）= 顶层生态，由 entity_type=ecosystem 标记，
  **不单独存 ecosystem_root 字段**——消费方沿 parent_brand 链向上走到
  无 parent（或 parent 不在 SSOT）的顶端即得生态根（动态派生）。
- category 回答「图标放哪个一级目录」，parent_brand 回答「直接属于哪个品牌」，
  两者独立（如 Mijia: category=Home, parent_brand=Xiaomi, 生态根=Xiaomi）。
- 生态阈值：生态根的 **canonical descendants**（直系子 + 孙 + …，不含 root 本身、
  不含 variants/aliases/历史）≥ 2 → 必须有一级生态分类。用 descendants 而非
  direct children，否则中间层（Facebook 有 4 直系子）会误触发分类爆炸。

CI 只验证**结构一致性**（图无环、无自指、父存在、root 解析正确、阈值满足）；
现实世界归属的完整性与证据由 docs/references/brand-ownership-audit.md 承担。
"""
import sys
from pathlib import Path

# 允许作为脚本直接运行时 import 同目录模块
sys.path.insert(0, str(Path(__file__).resolve().parent))


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


def _descendants(root, ssot):
    """返回 root 的全部 canonical descendants（祖先集合含 root 的品牌，不含 root 本身）。"""
    return {bid for bid in ssot if bid != root and root in _ancestor_set(bid, ssot)}


def _root_of(bid, ssot, depth=100):
    """沿 parent_brand 链向上，返回顶端生态根（无 parent，或 parent 不在 SSOT 的最近顶端）。"""
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


def resolve_ecosystem_root(bid, ssot):
    """对外 API：派生某品牌的生态根（动态，不存储）。"""
    return _root_of(bid, ssot)


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
            fail('生态根 %s 的 canonical descendants < 2（%d 个）' % (root, len(ds)))
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
    print('Relationship graph: PASS (%d brands, %d ecosystem roots)'
          % (len(brands_doc.get('brands', [])),
             len({b for b in brands_doc.get('brands', []) if b.get('entity_type') == 'ecosystem'})))
