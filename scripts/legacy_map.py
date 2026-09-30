#!/usr/bin/env python3
"""Legacy 名称 / 路径的**单一来源**（CI 第 10 组与测试共用）。

设计约束（2026-09-30 §64-67，2026-10-01 §34 重设计）：
  - 任何「已迁移的分类目录」或「已重命名的品牌 ID」都必须登记在这里；
  - 不得把旧名字散落硬编码进 CI 脚本 / 测试（否则新增 rename 时必然漏扫）；
  - 本模块自身是唯一允许出现旧名的位置，扫描时自动豁免。

**current canonical ≠ legacy（2026-10-01 修订）**：
  `xAI` 现为当前 canonical 品牌 ID，其 canonical 路径
  `icons/SpaceXAI/xAI/xAI.png` 天然含 `/xAI/` 路径段。若继续把 `xAI` 当作
  「路径段级 legacy 名」，当前合法路径会被误判为旧路径。故：
    - `LEGACY_OLD_DIR_PATTERNS` 用**完整旧目录前缀**（`icons/xAI/`）登记这一类
      「旧目录名与当前 canonical 段名同形」的情况——前缀匹配不会被
      `icons/SpaceXAI/xAI/` 命中；
    - 一个 ID 不允许同时出现在 `LEGACY_BRAND_IDS` 与 `config/brands.json`
      （见 tests/test_hardening.py::test_canonical_id_is_not_legacy）。

扫描语义：旧名以**路径段**形式出现才算引用，避免误伤普通文本中的历史叙述。
"""

# 方案 C 扁平化前的历史分类目录（已全部迁移至新分类体系）——一级目录名。
LEGACY_CATEGORIES = (
    'DevOps',
    'Drive',
    'General',
    'Tool',
)

# 旧品牌 ID → 当前 canonical ID（技术 ID 迁移 / 品牌重命名）。
# 注意：只登记**不再是当前 canonical ID** 的旧名。`xAI` 已恢复为当前 canonical
# 品牌，因此不在本表中（见模块 docstring §34）。
LEGACY_BRAND_IDS = {
    'PeacockTV': 'Peacock',
    'Podcasts': 'ApplePodcasts',
    'Twitter': 'X',
}

# 旧目录前缀：旧目录名与当前 canonical 品牌 ID 同形，必须用完整前缀登记
# （`xAI` 生态目录于 2026-07 更名为 `SpaceXAI`，2026-10-01 该目录下的资产恢复为
#  xAI 品牌图标，故 `/xAI/` 段本身已合法，只有 `icons/xAI/` 旧目录非法）。
LEGACY_OLD_DIR_PATTERNS = (
    'icons/xAI/',
)


def legacy_path_segments():
    """返回所有「不得再作为路径段出现」的旧名（分类 + 品牌 ID）。

    仅用于文档与测试的自省；实际扫描请用 legacy_scan_patterns()。
    """
    return tuple(LEGACY_CATEGORIES) + tuple(LEGACY_BRAND_IDS)


def legacy_scan_patterns():
    """返回应被检出的旧路径模式。

    三类：
      - 历史分类一级目录：`icons/<cat>/`
      - 已重命名品牌 ID 的路径段：`/<id>/`
      - 旧目录前缀（与当前 canonical 段名同形者）：`icons/xAI/`
    """
    pats = ['icons/%s/' % c for c in LEGACY_CATEGORIES]
    pats += ['/%s/' % s for s in LEGACY_BRAND_IDS]
    pats += list(LEGACY_OLD_DIR_PATTERNS)
    return tuple(pats)


def legacy_ids():
    """返回所有旧品牌 ID 集合（用于 config 值级校验：id 不得是旧 ID）。"""
    return set(LEGACY_BRAND_IDS)
