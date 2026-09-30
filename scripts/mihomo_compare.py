#!/usr/bin/env python3
"""Oasisic ↔ mihomo-rules 品牌关系对照（只读、纯函数、不联网、不改 mihomo）。

语义前提
--------
mihomo-rules 的 `SUB_PARENT` 语义 = **子品牌 → 直接父品牌**（immediate parent），
与 Oasisic `parent_brand` 同构。因此对照必须比较**语义层级**而不是字符串是否相等：
mihomo 通常只表达直接父，Oasisic 可能同时表达直接父 + 祖先链——只要直接父一致即
`MATCH`（例：mihomo `YouTubeMusic → YouTube`，Oasisic `YouTubeMusic → YouTube → Google`
仍算 MATCH，不算 mismatch）。

状态定义（与 docs/references/brand-ownership-audit.md §9 同口径）
---------------------------------------------------------------
  MATCH                 双方直接父一致（含 Oasisic 另有更深祖先链的情形）
  OASISIC_MORE_PRECISE  Oasisic 直接父更细：mihomo 的直接父位于 Oasisic 祖先链上
  MIHOMO_MORE_PRECISE   mihomo 直接父更细：Oasisic 的直接父位于 mihomo 自身链上
  STALE                 mihomo 使用历史/失效直接父（改名或并购后仍留旧映射）
  NOT_CONSUMED          仅 mihomo 有该品牌（Oasisic 不消费，非错误）
  OASISIC_ONLY          仅 Oasisic 有该品牌（mihomo 不消费，非错误）
  AMBIGUOUS             双方都有但直接父冲突且无法判定包含关系 → 需人工 CURRENT OWNERSHIP REVIEW
  MISSING               双方都有该品牌，但一方缺 parent 关系

设计约束
--------
- 本模块**不内置 mihomo 真实数据**，避免在 Oasisic 内制造第二份手工 SSOT；
  调用方传入已解析的 `mihomo_map`（来自 mihomo `scripts/lib/ownership_map.py` SUB_PARENT）。
- `STALE` / `*_MORE_PRECISE` 无法纯机械判定时，由调用方用 `overrides` 显式标注
  （需官方证据），机械可判定的情形自动归类。
- 函数永不写文件、永不修改 mihomo；mihomo-rules 只读。
"""


def _oas_ancestors(bid, ssot):
    """Oasisic 侧祖先集合（沿 parent_brand 向上，断在缺失父/白名单外）。"""
    seen, cur = set(), ssot.get(bid, {}).get('parent_brand')
    while cur:
        if cur in seen:
            break
        seen.add(cur)
        if cur not in ssot:
            break
        cur = ssot[cur].get('parent_brand')
    return seen


def _mm_ancestors(bid, mihomo_map):
    """mihomo 侧祖先集合（沿 SUB_PARENT 自身向上）。"""
    seen, cur = set(), mihomo_map.get(bid)
    while cur:
        if cur in seen:
            break
        seen.add(cur)
        cur = mihomo_map.get(cur)
    return seen


def _row(mid, oid, opar, mpar, root, status):
    return {
        'mihomo_id': mid,
        'oasisic_id': oid,
        'oasisic_parent': opar,
        'mihomo_parent': mpar,
        'oasisic_root': root,
        'status': status,
    }


def compare(oasisic_ssot, mihomo_map, aliases=None, overrides=None):
    """对照 mihomo 的每一条 SUB_PARENT，返回状态行列表（§134 交集矩阵）。

    oasisic_ssot: {id: entry}，entry 至少含 parent_brand（可含 category 等）。
    mihomo_map:   {child_id: parent_id}，即 mihomo SUB_PARENT。
    aliases:      {mihomo_id: oasisic_id}，用于已改名品牌（如 AppleNews→AppleNewsPlus）。
    overrides:    {mihomo_id: status}，人工证据判定（STALE / *_MORE_PRECISE 等）。
    """
    aliases = aliases or {}
    overrides = overrides or {}
    rows = []
    for mid in sorted(mihomo_map):
        mpar = mihomo_map[mid]
        oid = aliases.get(mid, mid)
        e = oasisic_ssot.get(oid)
        if e is None:
            rows.append(_row(mid, None, None, mpar, None, 'NOT_CONSUMED'))
            continue
        opar = e.get('parent_brand')
        root = oid
        cur = opar
        seen = {oid}
        while cur:
            if cur in seen:
                break
            seen.add(cur)
            root = cur
            if cur not in oasisic_ssot:
                break
            cur = oasisic_ssot[cur].get('parent_brand')
        if mid in overrides:
            st = overrides[mid]
        elif not opar or not mpar:
            st = 'MISSING'
        elif opar == mpar:
            st = 'MATCH'
        elif mpar in _oas_ancestors(oid, oasisic_ssot):
            st = 'OASISIC_MORE_PRECISE'
        elif opar in _mm_ancestors(mpar, mihomo_map):
            st = 'MIHOMO_MORE_PRECISE'
        else:
            st = 'AMBIGUOUS'
        rows.append(_row(mid, oid, opar, mpar, root, st))
    return rows


def oasisic_only(oasisic_ssot, mihomo_map, aliases=None):
    """返回 Oasisic 侧「有 parent_brand 但 mihomo 不消费」的品牌 id（§68，非错误）。"""
    aliases = aliases or {}
    consumed = set(mihomo_map) | set(aliases.values())
    return sorted(
        bid for bid, e in oasisic_ssot.items()
        if e.get('parent_brand') and bid not in consumed
    )
