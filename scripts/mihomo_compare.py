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
  MISMATCH              双方字段都表示直接父，但直接父不同 → 真实语义冲突，需人工 CURRENT OWNERSHIP REVIEW
  AMBIGUOUS             双方关系定义不同或证据不足，无法判定是否可比 → 需人工 CURRENT OWNERSHIP REVIEW
  MISSING               双方都有该品牌，但一方缺 parent 关系

设计约束
--------
- 本模块**不内置 mihomo 真实数据**，避免在 Oasisic 内制造第二份手工 SSOT；
  调用方传入已解析的 `mihomo_map`（来自 mihomo `scripts/lib/ownership_map.py` SUB_PARENT）。
- `STALE` / `*_MORE_PRECISE` 无法纯机械判定时，由调用方用 `overrides` 显式标注
  （需官方证据），机械可判定的情形自动归类。
- 函数永不写文件、永不修改 mihomo；mihomo-rules 只读。
- **关系遍历单一来源（2026-09-30 收口）**：root / ancestor 解析不得在本模块
  自行实现，必须复用 `brand_relationships` 的 resolver（`resolve_graph_root`
  / `_ancestor_set`），否则会出现「两套关系解析器结论不一致」的架构缺陷。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from brand_relationships import resolve_graph_root, _ancestor_set  # noqa: E402


def _oas_ancestors(bid, ssot):
    """Oasisic 侧祖先集合 —— 委托给 brand_relationships._ancestor_set（单一来源）。"""
    return _ancestor_set(bid, ssot)


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
        # graph root 解析复用 brand_relationships（单一来源，见模块 docstring）
        root = resolve_graph_root(oid, oasisic_ssot)
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
            st = 'MISMATCH'
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
