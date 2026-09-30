#!/usr/bin/env python3
"""Legacy 名称 / 路径的**单一来源**（CI 第 10 组与测试共用）。

设计约束（2026-09-30 §64-67）：
  - 任何「已迁移的分类目录」或「已重命名的品牌 ID」都必须登记在这里；
  - 不得把旧名字散落硬编码进 CI 脚本 / 测试（否则新增 rename 时必然漏扫）；
  - 本模块自身是唯一允许出现旧名的位置，扫描时自动豁免。

扫描语义：旧名以**路径段**形式（`/<segment>/`）出现才算引用，避免误伤
普通文本中的历史叙述（如需在正文提到历史，用不带斜杠的写法）。
"""

# 方案 C 扁平化前的历史分类目录（已全部迁移至新分类体系）
LEGACY_CATEGORIES = (
    'DevOps',
    'Drive',
    'General',
    'Tool',
)

# 旧品牌 ID → 当前 canonical ID（技术 ID 迁移 / 品牌重命名）
# 说明：Twitter → X 为历史品牌名；xAI → SpaceXAI 为 2026-07 官方品牌标识 rename。
LEGACY_BRAND_IDS = {
    'PeacockTV': 'Peacock',
    'Podcasts': 'ApplePodcasts',
    'xAI': 'SpaceXAI',
    'Twitter': 'X',
}


def legacy_path_segments():
    """返回所有「不得再作为路径段出现」的旧名（分类 + 品牌 ID）。"""
    return tuple(LEGACY_CATEGORIES) + tuple(LEGACY_BRAND_IDS)


def legacy_scan_patterns():
    """返回应被检出的旧路径段模式（`/<seg>/`）。"""
    return tuple('/%s/' % s for s in legacy_path_segments())


def legacy_ids():
    """返回所有旧品牌 ID 集合（用于 config 值级校验：id 不得是旧 ID）。"""
    return set(LEGACY_BRAND_IDS)
