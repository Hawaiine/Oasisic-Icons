# AGENTS.md — Oasisic-Icons 长期项目规范

本文件是仓库级 Agent 规范（长期稳定规则，不是变更日志、不复制 README）。
改动本仓库前先读本文件；与 README / docs 冲突时，以本文件 + `config/` 为准。

## 1. SSOT 与派生

- **唯一 SSOT**：`config/brands.json`（品牌 / 图标 / 关系）与 `config/categories.json`（分类元数据）。
- 派生文件（`config/surge-icon.json`、`config/brand-relationships.json`、`docs/references/brand-glossary.md`、
  `docs/references/physical-hierarchy-audit.md`、各级 `README.md`、`docs/references/icon-quality-notes.md`）
  **不得成为第二 SSOT**：不得手工编辑，必须由生成器重算。
- 派生链：`brands.json` → 关系引擎 → 物理路径解析器 → 生成器 → CI 校验。

## 2. 目录 / 命名 / 物理路径

- `category` = 第一层物理目录：`icons/<category>/`。
- `parent_brand` = **immediate Brand/Product parent**，不表示 ownership / 收购 / 持股 / 开发者 / provider /
  平台 / distribution / hosting / integration。
- `category` 与 `parent_brand` **互相独立**，不得互相自动覆盖。
- `category == graph root` 时**不重复**该节点目录：`icons/<category>/<brand>/<brand>.png`。
- 存在同类中间父品牌时**递归嵌套**：`icons/<category>/<parent>/<brand>/<brand>.png`（可继续加深）。
- cross-category parent **不机械迁移**，子品牌保留自身 category 与物理位置，语义边保留在 SSOT。
- 无自身图标的 parent **不制造伪目录、不复制他人资产**：语义边留在 SSOT，现实歧义进 Review Queue。
- `expected_icon_path()`（`scripts/brand_relationships.py`）是**唯一物理路径解析器**；
  任何脚本 / 生成器 / CI 不得自行拼装路径。

## 3. 关系与生态

- 关系计算唯一入口：`scripts/brand_relationships.py`（direct parent / ancestor chain / graph root /
  ecosystem root / cycle detection / missing parent / parent type validation / physical path）。
- `ecosystem` **动态计算**：graph root + canonical descendants ≥ 2（阈值按生态根 descendants 计），
  不手工维护生态清单、不硬编码数量。
- 平台集成事实（例：Grok 可通过 X 平台使用）**不得**倒推 `parent_brand`。
- 真正无法机器判定的现实世界关系进 `config/brand-review-queue.json`（`is_ssot: false`），
  人工裁决后写回 `brands.json`，再把队列项置 `RESOLVED`。

## 4. 冻结的最终品牌树（不得重新讨论）

```text
SpaceXAI
├── X
└── xAI
    └── Grok
```

直接父品牌：`X → SpaceXAI`、`xAI → SpaceXAI`、`Grok → xAI`。
`SpaceX` = corporate ownership background only，不进入 Brand Graph。
路径：`icons/SpaceXAI/X/X.png`、`icons/SpaceXAI/xAI/xAI.png`、`icons/SpaceXAI/xAI/Grok/Grok.png`、
生态根 `icons/SpaceXAI/SpaceXAI/SpaceXAI.png`。
禁止：`Grok → X`、`Grok → SpaceXAI`、`icons/SpaceXAI/Grok/Grok.png`。

## 5. 资产模型（图标）

- 规范：512×512、PNG、RGBA、Apple 风格 squircle 圆角（r ≈ 115px，约 22.4%），四角 alpha=0，保留原始底色。
- 图标内容**不得重绘 / 改色 / 去背景**；若使用官方素材，只允许放入项目标准容器（缩放 + 圆角遮罩）。
- 官方资产优先，来源必须可追溯（记录在 Review Queue / 审计文档 / commit message）；
  官方资产不可得时 `icon_status = pending`（可无 `icon_path`），**禁止伪造**、禁止复用其它品牌资产。
- 同一图像内容不得服务两个品牌（SHA-256 唯一性由 CI 拦截）。
- 统计口径必须显式区分：SSOT entities / canonical entities / icon-backed entities / PNG /
  pending no-icon entities / categories / ecosystems（由 `scripts/update-readme-badges.py` 写入 README）。

## 6. 校验与新增品牌

- 提交前必须全绿：
  ```
  python3 scripts/ci-validate-icons.py
  python3 -m unittest discover -s tests -v
  git diff --check
  ```
  生成器必须幂等（连续两轮运行 0 diff）。
- 新增品牌顺序：metadata（`brands.json`）→ validation（`scripts/validate-brand.py`）→
  resolver（`brand_relationships.py`）→ generator（README / Surge / Glossary / export）→ CI。
- 不得手工改生成结果来"修好"CI；应修 SSOT、生成器或校验器。
- CI 绿灯只证明**结构一致性**，不证明现实世界归属正确；后者由
  `docs/references/brand-ownership-audit.md`（研究层）承担。

## 7. 下游与边界

- 本仓库是 SSOT；**mihomo-rules 等下游是 consumer**，不得在本仓库为下游改关系事实。
- 已知下游差异（如 mihomo 侧旧的 `Grok → X`）记为 DOWNSTREAM_STALE，单独同步。
- 不修改 `main` 之外的仓库；GitHub 变更默认走 PR。
