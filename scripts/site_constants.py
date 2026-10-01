#!/usr/bin/env python3
"""发布面常量（唯一来源）——生成器与校验器共用，禁止各自手写字面量。

为什么单独成模块
----------------
Surge 订阅基址被 **生成器**（`generate-icon-json.sh`）与 **校验器**
（`ci-validate-icons.py`）同时消费。此前两处各写一份字面量：任何一侧改动都会让
generator 产出与 validator 期望**静默分叉**（一侧改了 URL，另一侧继续按旧值校验，
或者更糟——两边都改但改成了不同的值）。

边界（§9 单一事实）
------------------
- 本模块只放「发布面 / 对外 URL」常量；
- 关系、物理路径、分类、生态规则**不在这里**，它们属于
  `scripts/brand_relationships.py`（唯一关系引擎）；
- 消费者必须 `import` 本模块，不得再写字面量副本
  （由 `tests/test_generator_contracts.py` 断言单一来源）。
"""

# 图标直链基址：所有对外 URL = ICON_RAW_BASE + '/' + 仓库内相对 icon_path
# 例：https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/AI/Anthropic/Anthropic.png
# 仓库不使用 jsDelivr 等第三方 CDN（见 README「只提供 raw.githubusercontent.com 直链」）。
ICON_RAW_BASE = 'https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main'
