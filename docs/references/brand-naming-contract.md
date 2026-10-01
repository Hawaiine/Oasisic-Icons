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
| `directory` | `icons/<category>/[<中间父…>/]<id>/`（末级与 id 一致，多层见 §1.1） | 随 id 迁移 |
| `filename` | `<id>.png` / `<id>NN.png`（与 id 一致） | 随 id 迁移 |

### 1.1 物理路径模型（多层嵌套，2026-10-01 定稿）

三个概念必须分开：

```text
category      = 图标属于哪个一级分类（恒为一级目录，不因关系改变）
parent_brand  = 品牌的直接父品牌（关系 SSOT）
physical path = category + 可表达的物理父层级
```

路径规则：

```text
icons/<category>/<id>/<id>.png                     一级 direct child（category root 的直系子）
icons/<category>/<中间父…>/<id>/<id>.png           同类中间父品牌下的深层子品牌（可多层）
```

判定（`scripts/brand_relationships.py::expected_icon_path`，唯一推导入口）：

| 情形 | 物理路径 | 例 |
|:---|:---|:---|
| 直接父品牌 = category 根（graph root） | 平铺 `icons/<cat>/<id>/` | `AppleMusic → Apple`：`icons/Apple/AppleMusic/AppleMusic.png` |
| 直接父品牌本身**也有**父品牌（同类中间父） | 嵌套 `icons/<cat>/<父>/<id>/` | `Instagram → Facebook → Meta`：`icons/Meta/Facebook/Instagram/Instagram.png` |
| 直接父品牌属**其它 category** | 平铺（cross-category，不迁移） | `Mijia → Xiaomi`：`icons/Home/Mijia/Mijia.png` |
| 直接父品牌**无自身图标**（白名单母公司） | 平铺（无目录可嵌套） | `Kimi → MoonshotAI`：`icons/AI/Kimi/Kimi.png` |

- `brands.json.icon_path` 必须等于该解析器的输出（CI 第 7/17 组拦截手写路径），
  Surge / Glossary / README / 生成器全部跟随，不得另写第二套路径规则；
- 多层嵌套可继续加深（`icons/R/A/B/C/C.png`），不设层数上限；
- 物理路径变化**不是** brand rename（§22）：`icons/Google/YouTubeMusic/…` →
  `icons/Google/YouTube/YouTubeMusic/…` 属 physical restructure，ID / display_name 不变；
- 全库矩阵（多层关系 / cross-category / 无图标母公司 / 生态）见
  [`physical-hierarchy-audit.md`](physical-hierarchy-audit.md)（generated，CI 第 17 组校验）。

`parent_brand` = **直接父品牌**（immediate parent）。祖先链与生态根一律动态派生
（`scripts/brand_relationships.py` 的 `resolve_ecosystem_root`），不存字段。

**关系类型边界（Final Trust Audit）**：`parent_brand` 只表达 Brand / Product Hierarchy（如
`Google → YouTube → YouTubeMusic`、`Meta → Facebook → Instagram`、`Apple → iCloud →
iCloudPrivateRelay`，以及最终品牌树 `SpaceXAI → xAI → Grok`）。Developer / Provider / Brand Owner 与
Platform Integration / Distribution **不是** `parent_brand`：官方资料既支持「SpaceXAI 品牌体系持有
Grok 品牌权利」，也支持「Grok 可通过 X 平台使用」；后者是 `Grok ↔ X` 的平台集成关系，
**不得**倒推 `Grok.parent_brand = X`。当前全库没有通用 platform/integration relation schema；
除非未来出现全库级消费需求，不为单一案例扩张 SSOT，平台关系保留在证据审计层（辅助审计，
非 SSOT、非阻塞条件）。

**最终品牌树（2026-10-01 用户确认）**：

```text
SpaceXAI
├── X
└── xAI
    └── Grok
```

直接父品牌：`X → SpaceXAI`、`xAI → SpaceXAI`、`Grok → xAI`。`xAI` 是**当前 canonical 品牌**
（独立 ID / display_name / 图标），**不是 legacy 旧名**（见 `scripts/legacy_map.py` 与
 `tests/test_hardening.py`）；`SpaceXAI` 为正式 canonical 顶层生态 SSOT（descendants = 3 ≥ 2），icon_status=pending，根图标待官方标志，不得伪造。

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

## 8. Legacy 单一来源与「canonical ≠ legacy」

- 旧分类目录 / 旧品牌 ID 只登记在 `scripts/legacy_map.py`（CI 第 10 组与测试共用），
  不得散落在脚本或测试里。
- **当前 canonical ID 绝不与 legacy ID 重叠**（`tests/test_hardening.py::test_canonical_id_is_not_legacy`）；
  `xAI` 恢复为 canonical 后必须从 legacy 表移除。
- 旧目录名与当前 canonical 段名同形时（历史 xAI 生态一级目录 vs 当前 canonical 路径
  `icons/SpaceXAI/xAI/xAI.png`），用**完整旧目录前缀**模式登记（前缀字面量见 `scripts/legacy_map.py`），
  而不用 `/段/` 通配，避免当前合法路径被误判为旧路径
  （`tests/test_hardening.py::test_legacy_patterns_do_not_match_canonical_paths`）。

## 9. 新增品牌自动化入口（§39-§43 §71）

| 能力 | 入口 | CI 门禁 |
|:---|:---|:---|
| 命名 / 分类 / 关系 / 文件 / 图标校验 | `python3 scripts/validate-brand.py --id … --display-name … --category … --entity-type … [--parent-brand …] [--png …]` | 复用关系引擎（`brand_relationships.validate_relationships`） |
| 关系机器可读导出（下游消费） | `python3 scripts/export-brand-relationships.py` → `config/brand-relationships.json` | 第 15 组「关系派生导出」（逐项一致 + `generated: true`） |
| 无法机器判定的现实关系 | `config/brand-review-queue.json`（人工裁决队列，`is_ssot: false`） | 第 16 组「Review Queue」（结构 + 引用真实性） |

规则：

- `validate-brand.py` **只做确定性检查**：不猜 `parent_brand`。父品牌无法确定时输出 warning
  并指向 review queue；决定后写回 `brands.json`（唯一关系 SSOT），再把队列项置 `RESOLVED`。
- `config/brand-relationships.json` **不是第二个 SSOT**：它必须标 `generated: true` 且
  `source: config/brands.json`；手工修改会被第 15 组拒绝。
- 官方 casing 不机械 PascalCase：`iQIYI` / `SONY` / `vivo` / `myTVSUPER` / `TIDAL` / `xAI` /
  `SpaceXAI` 按官方拼写保留；`validate-brand.py` 对 ID 与 display_name 归一化不一致的候选给出
  warning 供人工确认。

## Final Physical Path Contract (PR #10)

- `category` is the first physical directory layer: `icons/<category>/`.
- `parent_brand` is the immediate Brand/Product parent only; it is not ownership, developer, provider, platform, hosting, distribution, or integration.
- `category` and `parent_brand` are independent. If category equals the graph/root parent, do not repeat that node as a directory.
- A same-category intermediate parent is represented recursively: `icons/<category>/<parent>/<brand>/<brand>.png`; deeper chains continue recursively.
- Cross-category parents retain the child category and are marked `CROSS_CATEGORY_VALID`; they are not mechanically migrated.
- A parent without its own icon must not create a fake directory or copied asset; the semantic edge remains in SSOT and unresolved real-world questions go to Review Queue.
- Every leaf is `<id>/<id>.png`. `scripts/brand_relationships.py::expected_icon_path()` is the only physical-path resolver used by CI and generators.

Frozen example:

```text
SpaceXAI
├── X
└── xAI
    └── Grok

icons/SpaceXAI/X/X.png
icons/SpaceXAI/xAI/xAI.png
icons/SpaceXAI/xAI/Grok/Grok.png
```

The canonical pipeline is: `brands.json` → relationship resolver → physical path resolver → generated README/Surge/Glossary/export → CI. Generated files are not a second SSOT.
