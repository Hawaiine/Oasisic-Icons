# Brand Naming & Synchronization Contract

本文件是 Oasisic-Icons 的命名与同步规范（单一契约文档，不拆分）。
机器校验入口：`scripts/ci-validate-icons.py`（Brands SSOT / Naming / README 父节点 组）
+ `tests/test_parent_readme.py`（命名契约 + 父品牌 README 负测）。

---

## 1. 四个命名层的职责

| 层 | 职责 | 稳定性 |
|:---|:---|:---|
| `id` | 机器稳定技术标识（路径安全、ASCII、无空格） | 只迁移不修改 |
| `display_name` | 用户可见官方品牌名（保留官方 casing 与符号） | 随官方改名 |
| `directory` | `icons/<category>/<id>/`（与 id 一致） | 随 id 迁移 |
| `filename` | `<id>.png` / `<id>NN.png`（与 id 一致） | 随 id 迁移 |

`parent_brand` = **直接父品牌**（immediate parent）。祖先链与生态根一律动态派生
（`scripts/brand_relationships.py` 的 `resolve_ecosystem_root`），不存字段。

**关系类型边界（Final Trust Audit）**：`parent_brand` 只表达 Brand / Product Hierarchy（如
`Google → YouTube → YouTubeMusic`、`Meta → Facebook → Instagram`、`Apple → iCloud →
iCloudPrivateRelay`）。Developer / Provider / Brand Owner 与 Platform Integration / Distribution
不是 `parent_brand`：例如官方资料同时支持「SpaceXAI 开发 Grok」与「Grok 可通过 X 平台使用」，
前者决定 `Grok.parent_brand = SpaceXAI`，后者是 `Grok ↔ X` 的平台集成关系，不得倒推
`Grok.parent_brand = X`。当前全库没有通用 platform/integration relation schema；除非未来出现
全库级消费需求，不为单一案例扩张 SSOT，平台关系保留在证据审计层。

## 2. Technical ID 规则

- 仅 `[A-Za-z0-9]` 开头，后续允许 `[A-Za-z0-9._-]`；ASCII、无空格、无 `/`。
- **不机械 PascalCase**：官方 casing 保留（`iQIYI`、`SONY`、`vivo`、`myTVSUPER`、
  `TIDAL`、`SpaceXAI`）。
- 数字开头 ID 是合法既有资产（`115`、`123`、`189`、`1Password`）。

## 3. Special Character Mapping

| 符号 | ID 中的写法 | display_name | 实例 |
|:---|:---|:---|:---|
| `+` | `Plus` | 保留 `+` | `AppleNewsPlus` → `Apple News+`；`CATCHPLAYPlus` → `CATCHPLAY+`；`DisneyPlus` → `Disney+`；`ParamountPlus` → `Paramount+`；`AppleFitnessPlus` → `Apple Fitness+` |
| `@` | 省略 | 保留 `@` | `KaraokeDAM` → `Karaoke@DAM` |

映射表只收录仓库中**实际存在**的案例，不凭空扩大（`&` 等暂无实例，出现时再按
「ID 去符号 + display_name 保留官方拼写」的原则个案评估）。

**符号归一化必须经过 collision check**：新增/重命名 ID 前，按本表归一化规则推演
（`+`→`Plus`、`@`→省略），与全库现有 ID 比对——若归一化后撞车（例：未来同时出现
`A@B` 与 `AB`，去符号后均为 `AB`），不得静默择一，必须报告并在有官方依据的前提下
个案处理（如保留一个符号拼写变体 `At` 后缀）。

## 4. Display Name 规则

- 以**官方当前品牌**为准；中文 display_name 合法（`SINA` → `新浪`、`Weibo` → `微博`）。
- 大小写/空格/符号偏离官方当前名称即为缺陷，需修订 display_name（通常不需要改 ID）。

## 5. Synchronization Rules（改动影响矩阵）

| 改动 | 必须同步 |
|:---|:---|
| display_name 修订 | brands.json、surge-icon.json（名称字段）、glossary、父级/分类 README（重跑生成器）、audit 文档 |
| id 重命名（迁移） | brands.json（id + icon_path + parent_brand 引用）、`git mv` 目录/文件名、surge-icon.json、glossary、迁移文档（Old→New 记录）、测试、mihomo 兼容性说明 |
| parent_brand 变更 | brands.json、关系图 CI（`validate_relationships`）、父级 README（重跑生成器）、audit 文档证据 |
| 新增品牌 | brands.json、icons 目录 + PNG（512×512 RGBA r=115 圆角）、categories.json（如新生态）、surge-icon.json、glossary、主 README 分类表、CI |

## 6. Parent README Policy

> **任何拥有 ≥1 个 child brand 的物理品牌节点，其 icon 目录必须拥有 `README.md`。**
> 覆盖：一级生态根、中间父品牌（如 Facebook/YouTube/iCloud）、更深层父品牌。
> 叶子品牌不强制。Country / System / Surge 特殊目录不套用。

- 数据全部来自 brands.json + 动态关系解析（不在 README 手工维护计数）。
- Role 三态：`Ecosystem Root`（graph root + 独立生态）/ `Graph Root Parent`
  （graph root + 有子 + 无独立生态，如 SINA/Xiaomi）/ `Intermediate Parent Brand`
  （有父有子，如 Facebook）。
- 生成器：`scripts/generate-category-readmes.sh`（父品牌段）；带
  `<!-- generated: parent-brand-readme (scripts/generate-category-readmes.sh) -->`
  marker 的文件可重复生成，无 marker 的视为人工文档不覆盖。
- CI 门禁：`ci-validate-icons.py` 第 14 组「README 父节点」（存在 + 内容逐字节一致）。
- 白名单母公司（`parent_brands_without_icon`）无物理目录，不适用目录级 README。

## 7. 生态 README vs 父品牌 README

- 一级生态 README（分类级）：由生成器按 `icons/<分类>/README.md` 生成，
  列全量品牌清单（含计数）。
- 父品牌 README（品牌目录级）：列该节点的 Role / Parent / Ancestor Chain /
  Direct Children / Ecosystem Root。
- 两者不混用；父品牌 README 不参与分类品牌数统计。
