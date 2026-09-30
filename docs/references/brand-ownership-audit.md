# 品牌归属审计报告 / Brand Ownership Audit

> **审计日期**：2026-09-30 · **范围**：PR #9 特性分支 `refactor/ecosystem-threshold-v2` 全库 **292** 个 Canonical Brand（含 **16 个 ecosystem root** + 3 个 2026-09-30 会话新增品牌）

> 本文件是 **研究/证据层**：记录每个品牌当前（现实世界）母公司判断与依据。
> SSOT 仍为 `config/brands.json`（`parent_brand` / `category` / `entity_type`）——本文件不替代 SSOT。[§65 §66 §97]

## 1. 方法与口径 / Methodology

对全库每一个 Canonical Brand（不是抽样、不是只扫已有 `parent_brand`）逐一执行：

1. 取 `brands.json` 中的 `id / category / entity_type / parent_brand` 与磁盘 PNG 实际主体；
2. 主动检索现实世界的**当前**控股关系（官方站点 / 官方公告 / 财报 / 公司登记信息 / 权威百科），不依赖历史 metadata；[§92 §93 §95]
3. 判断控股口径：**全资或多数控股**记为 `CONFIRMED_PARENT`；少数股权与合资公司一律不设母公司；[§102]
4. 不得仅凭品牌名推断归属（如 `DisneyPlus`、`ChinaMobileDisk` 均需证据）；
5. 对每个 graph root 统计 **Canonical Descendants**（直系子 + 孙 + 更深，沿 `parent_brand` 链可达，
   不含 root 本身，仅 `entity_type=product_brand` 计入），套用**双向**硬规则：**descendants ≥ 2 →
   必须存在一级生态分类且 root 为 ecosystem；descendants < 2 → 不要求生态分类**，`parent_brand`
   照记，子品牌保留在功能分类，不新建生态分类。[§83 §84 §85]
   用 descendants 而非 direct children，否则中间层品牌（如 Facebook 直系 4 子）会误触发分类爆炸。

**五类状态**（每个品牌必须落入其一，不允许「未审查」）：`CONFIRMED_PARENT` / `NO_PARENT` / `AMBIGUOUS_JV` / `RETIRED` / `SPECIAL_ENTITY`。[§91]

### 关系模型 / Relationship Model（2026-09 定稿）

- **`parent_brand` = 直接父品牌（immediate parent）**，不表示公司股权结构、不表示历史所有者。
  例：`Instagram → Facebook`、`YouTubeMusic → YouTube`、`iCloudPrivateRelay → iCloud`。
- **关系类型边界（Final Trust Audit）**：`parent_brand` 只表达 Brand / Product Hierarchy；Developer /
  Provider / Brand Owner 与 Platform Integration / Distribution 不写入该字段。当前官方证据同时支持
  「SpaceXAI 开发 Grok」与「Grok 可通过 X 平台使用」：前者决定 `Grok → SpaceXAI`，后者是
  `Grok ↔ X` 的平台集成关系，**不**证明 `Grok → X`。仓库当前没有通用 platform/integration
  schema，本轮不为单一案例扩张 SSOT；平台关系留在审计证据层。
- **graph root ≠ ecosystem root**（2026-09-30 语义拆分，`brand_relationships`）：
  - **graph root** = 沿 `parent_brand` 链向上走到的最高节点（`resolve_graph_root`）。
  - **ecosystem root** = graph root 且 `entity_type: ecosystem`（`resolve_ecosystem_root`）。
  例：`Meta` graph root = ecosystem root = Meta；`Mijia → Xiaomi`：graph root = Xiaomi，
  但 Xiaomi 当前不构成独立生态（descendants = 1 < 2），ecosystem root = None。
  **不单独存字段**——消费方沿 `parent_brand` 链向上动态派生。
- **`category` ≠ `parent_brand` ≠ 生态根**：category 决定图标一级目录；parent_brand 决定直接归属；
  生态根由链动态解析（`Mijia`: category=Home, parent_brand=Xiaomi, graph root=Xiaomi, 无生态根）。
- **生态阈值（双向）**：有 SSOT 条目的 graph root 的 **canonical descendants（直系子+孙+…，不含 root
  本身，仅 product_brand）≥ 2** 必须为 ecosystem（反向门禁，CI 第 12 组）；entity_type=ecosystem
  必须 descendants ≥ 2（正向）。用 descendants 而非 direct children，避免中间层（Facebook 有 4
  直系子）误触发分类爆炸；中间层节点（有 SSOT 父品牌）不适用阈值，不得因此升级。
- **ownership ≠ brand architecture**：同属一家公司不自动新增 parent_brand；一旦关系成立且 descendants ≥ 2，
  生态目录规则立即适用。证据只存本文件，不写入 `brands.json`。
- **X / Grok / xAI / SpaceXAI / SpaceX 专项**（2026-09-30 Final Seal Review 复核）：五者身份分离——
  - `xAI` → `SpaceXAI`：**品牌身份 rename**（官方品牌标识 2026-07-06 更名完成，见下条），非新增品牌；
  - `Grok`：SpaceXAI 开发的 AI 产品 → `parent_brand = SpaceXAI`（官方 Terms / Privacy Policy 明确
    「Grok，由 SpaceXAI 的大语言模型驱动」）；**同时**，X 官方 Help Center 将 Grok 描述为「available
    to X users / on the X platform」，这是 Platform Integration / Distribution 关系，不是品牌父级；
  - `X`：**独立平台品牌**，`parent_brand = null` —— 官方 Privacy Policy 明确「**SpaceXAI is a
    separate company from X Corp.**」，且「X 的使用（含 X 平台上的 Grok）由 X 的条款管辖，**不适用**
    SpaceXAI 政策」；SpaceXAI 官方产品清单仅 Grok / Grokipedia，**不含 X**。`parent_brand` 回答
    「直接品牌父级」，**不以 corporate ownership 或 platform integration 推导**（§13）；
  - `SpaceXAI`：canonical brand，但 **canonical descendants = 1（仅 Grok）< 2 → 不构成独立生态**，
    故 `entity_type = product_brand`（公司品牌），目录 `icons/AI/SpaceXAI/`；
  - `SpaceX`：**Corporate Owner only**，不进入 Oasisic Brand Graph（不建 `icons/SpaceX/`、
    不设 `parent_brand = SpaceX`）。
  **证据链接（primary source）**：SpaceXAI [Privacy Policy](https://x.ai/legal/privacy-policy)（effective 2026-08-24）、
  [Consumer Terms](https://x.ai/legal/terms-of-service)（updated 2026-09-11）、[Consumer FAQ](https://x.ai/legal/faq)、
  [Brand Guidelines](https://x.ai/legal/brand-guidelines)；X [About Grok Help Center](https://help.x.com/en/using-x/about-grok)。
（2026-09-30 定稿）：`xAI` → `SpaceXAI` 为**品牌标识（brand
  identity）更名**——官方品牌层面证据：**2026-07-06** `@SpaceXAI` 账号发布「We are now @SpaceXAI」、
  debuting 新 logo、官方页标题与页脚均用 SpaceXAI（Business Insider / Yahoo Finance 同日报道一致）。
  **「法律实体更名」在 SEC / 公司登记层面未获正式文件证据，本文件不作此断言**；官方 Terms 仅证明
  **当前**实体名为「SpaceXAI LLC」（Nevada 注册，Austin, TX），不足以推出具体更名日期。故统一表述为
  「**brand rebrand / corporate branding**」，不写「2026-07 法律实体更名」。
- **Parent README Policy**（2026-09-30 定稿）：任何拥有 ≥1 个 child brand 的物理品牌节点，
  其 icon 目录必须拥有 `README.md`（生态根 + 中间父品牌 + 更深层父品牌）；叶子品牌不强制；
  Country / System / Surge 特殊目录不套用；白名单母公司无物理目录不适用。
  生成器 `scripts/generate-category-readmes.sh`（父品牌段），CI 第 14 组「README 父节点」门禁。
  完整契约见 `docs/references/brand-naming-contract.md`（ID / display_name / directory / filename /
  特殊字符映射 / 同步矩阵）。

## 2. 来源 / Sources

- 官方站点与官方公告：Disney / NBCUniversal / WBD / Sony / PCCW / SpaceXAI（原 xAI）/ Microsoft / Apple / Alibaba / Baidu / ByteDance / China Mobile / China Telecom / 中华电信 / 台灣大哥大 / 遠傳 / TVB / 有线宽频 / KKCompany / DMM / 第一興商 / Red Bull / Rakuten / 楽天 / NTT docomo / Kadokawa / U-NEXT / Quora / Kakao / Snap / Valve / Kuaishou / SiriusXM / Block / Paramount / Fox / MetaBrainz / News Corp / Xperi / JioStar / LY Corporation 等；
- 季度/年度财报与投资者关系页：Liberty Media（F1）、EchoStar（Sling TV / DISH）、Comcast（Peacock）、Warner Bros. Discovery、PCCW Limited；
- 权威百科与公开报道（用于交叉验证，不单独作为重大关系的唯一依据）；[§68]
- 现场联网检索于 2026-09-30 执行（`as-of` 即该日期）。

## 3. 结论摘要 / Summary

| 状态 | 品牌数 |
|---|---:|
| CONFIRMED_PARENT（已确认母公司） | 117 |
| NO_PARENT（无母公司/独立实体/生态根） | 115 |
| AMBIGUOUS_JV（合资/股权分散，不设母公司） | 10 |
| RETIRED（已退役，保留图标） | 2 |
| SPECIAL_ENTITY（Country/System/Surge/Proxy/Crypto 特殊实体） | 48 |
| **合计** | **292** |

| 指标 | 审计前 | 审计后 |
|---|---:|---:|
| 分类数（含 1 个 reserved） | 35 | 42 |
| 生态分类数 | 10 | 17 |
| Canonical 品牌数 | 284 | 292 |
| 已记录 parent_brand 的品牌数 | 58 | 116 |
| 无图标母公司白名单条目 | 0 | 30 |

## 4. 本轮新发现并新建的生态 / Newly Discovered Ecosystems

| 生态（新一级分类） | Canonical Children | 子品牌 | 证据要点 |
|---|---:|---|---|

| **ChinaMobile** | 2 | ChinaMobileDisk / Migu | 中国移动云盘 + 咪咕（咪咕文化科技为中国移动全资子公司） |

| **Disney** | 3 | DisneyPlus / ESPN / Hulu | Disney 全资：Disney+/Hulu（2025 收购 Comcast 剩余股份）/ESPN（80%） |

| **NBCUniversal** | 2 | NBC / Peacock | NBC 为 NBCUniversal 电视网；Peacock 为 NBCUniversal 流媒体（Comcast） |

| **PCCW** | 2 | NowE / Viu | Viu 与 Now E 同属 PCCW Media Group / HKT |

| **Sony** | 3 | Crunchyroll / PlayStation / mora | Sony 全资体系：SIE（PlayStation）/索尼影视（Crunchyroll）/索尼音乐（mora） |

| **Warner Bros. Discovery** | 2 | HBOMax / discoveryPlus | HBO Max 与 discovery+ 均归属 WBD（拆分仍处进行中，2026-09 复核） |

（`SpaceXAI` 原列于生态清单，2026-09-30 Final Seal Review 复核后**移出**：官方证据表明 `X` 非
SpaceXAI 的品牌子级（Privacy Policy 明确与 X Corp. 分离），`SpaceXAI` canonical descendants = 1
（仅 `Grok`）< 2，不构成独立生态 → `entity_type=product_brand`，`parent_brand` 仅保留
`Grok → SpaceXAI`。）


## 5. 既有生态的补全与复核 / Existing Ecosystems Revalidated

> 2026-09-30 起 `parent_brand` 语义改为**直接父品牌**（immediate parent），生态根由 `entity_type: ecosystem` 标记并沿 parent 链动态派生（不存 `ecosystem_root` 字段）。下表 `descendants` 为含孙代的可达后代数，`direct children` 为直接父品牌指向数。

| 生态根 | direct children | descendants | 本轮变更 | 复核结论 |
|---|---:|---:|---|---|
| Alibaba | 7 | 7 | — | 关系全部复核通过 |
| Amazon | 5 | 5 | — | 关系全部复核通过 |
| Apple | 11 | 12 | iCloudPrivateRelay 父改为 iCloud（中间层） | 关系全部复核通过；Podcasts → ApplePodcasts 重命名（2026-09-30） |
| Baidu | 3 | 3 | — | 关系全部复核通过 |
| ByteDance | 5 | 5 | — | 关系全部复核通过 |
| ChinaMobile | 2 | 2 | — | 关系全部复核通过 |
| Disney | 3 | 3 | — | 关系全部复核通过（JioHotstar 2025 与 JioCinema 合并、现属 JioStar，不并入 Disney children，独立 NO_PARENT 处理） |
| Google | 10 | 11 | YouTubeMusic 父改为 YouTube（中间层） | 关系全部复核通过 |
| Meta | 1 | 5 | Facebook 保留为中间层；Instagram / Messenger / Threads / WhatsApp 父改 Facebook | 关系全部复核通过；descendants=5 ≥ 2，生态成立 |
| Microsoft | 9 | 9 | — | 关系全部复核通过 |
| NBCUniversal | 2 | 2 | Peacock display_name 改为官方现名 Peacock | 关系全部复核通过 |
| NetEase | 2 | 2 | — | 关系全部复核通过 |
| PCCW | 2 | 2 | — | 关系全部复核通过 |
| SONY | 3 | 3 | — | 关系全部复核通过 |
| Tencent | 6 | 6 | — | 关系全部复核通过 |
| WarnerBrosDiscovery | 2 | 2 | — | 关系全部复核通过（HBOMax 2025-05 已改回 HBO Max，display_name 当前正确） |
（`SpaceXAI` 复核后**移出生态表**：descendants = 1（仅 Grok）< 2；`rename xAI → SpaceXAI` 为
2026-07-06 官方品牌标识更名，详见 §2 专项。）

**中间层品牌（直接父品牌语义新增，2026-09-30）**：`Facebook`（直系 4 子：Instagram / Messenger / Threads / WhatsApp，生态根 Meta）、`YouTube`（直系 1 子：YouTubeMusic，生态根 Google）、`iCloud`（直系 1 子：iCloudPrivateRelay，生态根 Apple）。中间层不建一级目录（阈值看生态根 descendants），仅承担 `parent_brand` 直接父关系。


## 6. 无自身图标的母公司白名单 / `parent_brands_without_icon`

以下母公司为已确认的现实世界母公司，但仓库暂无其品牌图标；**其 children < 2，不触发一级生态分类**，子品牌保留在原功能分类并记录 `parent_brand`。[§83 §100]

`Block`, `ButterflyEffect`, `ChunghwaTelecom`, `DMM`, `Daiichikosho`, `EchoStar`, `FarEasTone`, `Fox`, `KKCompany`, `Kadokawa`, `Kakao`, `Kuaishou`, `LibertyMedia`, `MangoSuperMedia`, `MoonshotAI`, `NTTDocomo`, `NewsCorp`, `PLAY`, `Paramount`, `Quora`, `Rakuten`, `RedBull`, `SiriusXM`, `Snap`, `TaiwanMobile`, `UNEXTHoldings`, `Valve`, `Xperi`, `ZhipuAI`, `iCABLE`


## 7. 全量矩阵 / Full Ownership Matrix（292 / 292）

> `Current Category` / `Parent Brand` 为**审计前**状态（`HEAD` = 009d994）；`Proposed Parent` 为本轮最终值。

| Brand | Current Category | Parent Brand | Proposed Parent | Evidence | Status | Action |
|---|---|---|---|---|---|---|

| `115` | CloudStorage | — | — | 广东一一五科技股份有限公司自有产品 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `123` | CloudStorage | — | — | 123 云盘由独立运营主体提供，无控股母公司记录 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `189` | CloudStorage | — | ChinaTelecom | 189 网盘（天翼云盘）为中国电信旗下云存储产品（中国电信官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = ChinaTelecom |

| `1Password` | Utilities | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `ABEMA` | Media | — | — | ABEMA 为 CyberAgent × テレビ朝日 共同出资公司 · 2026-09 | AMBIGUOUS_JV | 无变更（复核通过） |

| `AD` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `AMC` | Media | — | — | AMC Networks 为独立上市公司（Dolan 家族控制），与 AMC Theatres 无关 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `AWS` | Amazon | Amazon | Amazon | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `AdGuard` | Utilities | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Adobe` | Utilities | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Airport` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `AliCloud` | Alibaba | Alibaba | Alibaba | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `AliPay` | Alibaba | Alibaba | Alibaba | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Alibaba` | Alibaba | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 无变更（复核通过） |

| `Amazon` | Amazon | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 无变更（复核通过） |

| `AmazonAlexa` | Amazon | Amazon | Amazon | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `AmazonMusic` | Amazon | Amazon | Amazon | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Anthropic` | AI | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `AppStore` | Apple | Apple | Apple | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Apple` | Apple | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 无变更（复核通过） |

| `AppleArcade` | Apple | Apple | Apple | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `AppleBooks` | Apple | Apple | Apple | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `AppleFitnessPlus` | Apple | Apple | Apple | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `AppleMusic` | Apple | Apple | Apple | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `AppleNewsPlus` | Apple | Apple | Apple | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `AppleTV` | Apple | Apple | Apple | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Aqara` | Home | — | — | Aqara 由 Lumi United Technology 运营（独立公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Area` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Argentina` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Australia` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Auto` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Azure` | Microsoft | Microsoft | Microsoft | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `BBC` | Media | — | — | 英国公共广播机构（Royal Charter），无商业母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `BGP` | Proxy | — | — | 特殊实体（Proxy），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Bahamut` | Media | — | — | 巴哈姆特电通（Gamer.com.tw）为台湾独立站点 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Baidu` | Baidu | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 无变更（复核通过） |

| `BaiduNetdisk` | Baidu | Baidu | Baidu | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Bangumi` | Media | — | — | 独立社区项目（Bangumi 番组计划）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `BestBuy` | Shopping | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Binance` | Payment | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Bing` | Microsoft | Microsoft | Microsoft | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Blacklist` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Bluesky` | Social | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Bot` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `ByteDance` | ByteDance | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 无变更（复核通过） |

| `CATCHPLAYPlus` | Media | — | — | CATCHPLAY+ 为台湾独立影音平台 · 2026-09；2026-09-30 会话按 Plus 命名惯例重命名 CATCHPLAY → CATCHPLAYPlus | NO_PARENT | 无变更（复核通过） |

| `CN-Taiwan` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Canada` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `China` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `ChinaBroadnet` | Telecom | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `ChinaMobile` | Telecom | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 迁移 Telecom → ChinaMobile（新生态根品牌） |

| `ChinaMobileDisk` | CloudStorage | — | ChinaMobile | 中国移动云盘为中国移动自有云存储产品（中国移动官方）· 2026-09 | CONFIRMED_PARENT | 迁移 CloudStorage → ChinaMobile |

| `ChinaTelecom` | Telecom | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `ChinaUnicom` | Telecom | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Cloudflare` | Infrastructure | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Copilot` | Microsoft | Microsoft | Microsoft | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Crunchyroll` | Media | — | SONY | Crunchyroll LLC 为索尼（Sony Pictures/Aniplex）全资子公司（Sony Pictures 官方公告）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → SONY |

| `Cryptocurrency` | Crypto | — | — | 特殊实体（Crypto），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Cursor` | Development | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `DAZN` | Media | — | — | DAZN Group 为 Access Industries 私募持股（非品牌级母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `DJI` | Hardware | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `DMMTV` | Media | — | DMM | DMM TV 由合同会社 DMM.com 运营（DMM TV 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = DMM |

| `DeepSeek` | AI | — | — | 深度求索为独立公司，与幻方量化（High-Flyer）同源但非其子公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Deezer` | Music | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `DiDi` | Transport | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `DingTalk` | Alibaba | Alibaba | Alibaba | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Direct` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Discord` | Communication | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Disney` | —(新增生态根) | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 迁移 —(新增生态根) → Disney（新生态根品牌） |

| `DisneyPlus` | Media | — | Disney | Disney 官方流媒体品牌（Disney+）；Disney 全资 · 2026-09 | CONFIRMED_PARENT | 迁移 Media → Disney |

| `Docker` | Infrastructure | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Douban` | Social | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Doubao` | AI | — | ByteDance | 豆包由字节跳动开发（字节跳动官方）· 2026-09 | CONFIRMED_PARENT | 迁移 AI → ByteDance |

| `Douyin` | ByteDance | ByteDance | ByteDance | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Dropbox` | CloudStorage | — | — | 独立上市公司（NASDAQ: DBX）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Duolingo` | Education | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `ESPN` | Media | — | Disney | Disney 持 80%、Hearst 20%（ESPN Inc. 股权结构，Disney 财报）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → Disney |

| `Egypt` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Emby` | Media | — | — | Emby LLC 自有产品（产品即公司），无独立母公司实体 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `EpicGames` | Game | — | — | 独立公司；腾讯持股约 40% 为少数股权，非控股 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `F1TV` | Media | — | LibertyMedia | F1 TV 属 Formula One（Liberty Media 旗下）（Liberty Media 财报）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = LibertyMedia |

| `Facebook` | Meta | Meta | Meta | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Fan` | Media | — | — | 未识别到对应商业实体，暂不设母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Fileball` | Media | — | — | 独立开发者产品，无母公司实体 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Final` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `FujiTV` | Media | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `GIA` | Proxy | — | — | 特殊实体（Proxy），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `GLM` | AI | — | ZhipuAI | GLM 由 Z.ai（原智谱 Zhipu AI）开发（Z.ai 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = ZhipuAI |

| `Game` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `GeneralAI` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Germany` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `GitHub` | Development | — | Microsoft | GitHub 为 Microsoft 全资子公司（2018 收购，GitHub/Microsoft 官方）· 2026-09 | CONFIRMED_PARENT | 迁移 Development → Microsoft |

| `Global` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Gmail` | Google | Google | Google | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Google` | Google | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 无变更（复核通过） |

| `GoogleAI` | Google | Google | Google | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `GoogleDrive` | Google | Google | Google | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `GoogleMaps` | Google | Google | Google | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `GoogleNews` | Google | Google | Google | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `GooglePhotos` | Google | Google | Google | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `GooglePlay` | Google | Google | Google | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `GoogleTranslate` | Google | Google | Google | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `GoogleVoice` | Google | Google | Google | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Grok` | AI | — | SpaceXAI | Grok 由 SpaceXAI 开发（官方 Terms / Privacy Policy 明确「SpaceXAI 开发、由其大语言模型驱动」）· 2026-09-30 | CONFIRMED_PARENT | 分类回到 AI（SpaceXAI 非生态）；`parent_brand = SpaceXAI`；品牌标识 2026-07-06 rename |

| `HBOMax` | Media | — | WarnerBrosDiscovery | HBO Max 归属 Warner Bros. Discovery（WBD 官方/2026-08 第三方核对）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → WarnerBrosDiscovery |

| `HOYTV` | Media | — | iCABLE | HOY TV 由有线宽频（i-CABLE Communications）运营（i-CABLE 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = iCABLE |

| `HamiVideo` | Media | — | ChunghwaTelecom | Hami Video 由中华电信（Chunghwa Telecom）运营（中华电信官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = ChunghwaTelecom |

| `Hanxiaoquan` | Media | — | — | 韩小圈由上海宝云网络科技开发（独立公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `HongKong` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Honor` | Hardware | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Huawei` | Hardware | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Hulu` | Media | — | Disney | Disney 2025 年收购 Comcast 剩余 33% 股份后 100% 持股（Disney 官方/Disney 财报）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → Disney |

| `IEPL` | Proxy | — | — | 特殊实体（Proxy），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `IPLC` | Proxy | — | — | 特殊实体（Proxy），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `India` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Infuse` | Media | — | — | Firecore LLC 自有产品，无独立母公司实体 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Instagram` | Meta | Meta | Meta | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `JD` | Shopping | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Japan` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Jellyfin` | Media | — | — | 开源社区项目（Jellyfin 基金会），无商业母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `JioHotstar` | Media | — | — | JioHotstar 属 JioStar（Reliance × Disney 合资）· 2026-09 | AMBIGUOUS_JV | 无变更（复核通过） |

| `KKBOX` | Music | — | KKCompany | KKBOX 由 KKCompany Technologies 运营（KKCompany 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = KKCompany |

| `KKTV` | Media | — | — | KKTV 于 2025-12-31 停止运营并与 LINE TV 合并（KKCompany 公告）· 2026-09 | RETIRED | 保留图标并标记退役（不迁移、不设母公司） |

| `KakaoTalk` | Communication | — | Kakao | KakaoTalk 为 Kakao Corp. 旗下即时通讯（Kakao 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Kakao |

| `KaraokeDAM` | Media | — | Daiichikosho | DAM 卡拉 OK 系统由第一興商（Daiichikosho）开发运营（第一興商官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Daiichikosho |

| `Keep` | Health | — | — | Keep 为独立上市公司（运动科技）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Kimi` | AI | — | MoonshotAI | Kimi 由 Moonshot AI 开发（Moonshot 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = MoonshotAI |

| `Korea` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Kwai` | Social | — | Kuaishou | Kwai 为快手（Kuaishou Technology）海外短视频产品（Kuaishou 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Kuaishou |

| `LG` | Hardware | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `LINE` | Communication | — | — | LINE 属 LY Corporation，为 SoftBank × NAVER（A Holdings 50/50）合资公司，非单一母公司 · 2026-09 | AMBIGUOUS_JV | 无变更（复核通过） |

| `LINETV` | Media | — | — | LINE TV 属 LY Corporation 合资体系（同上）· 2026-09 | AMBIGUOUS_JV | 无变更（复核通过） |

| `Lark` | ByteDance | ByteDance | ByteDance | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Lemino` | Media | — | — | Lemino 原属 NTT docomo；2026-10-01 起与 WOWOW 成立合资公司运营，归属变动期 · 2026-09 | AMBIGUOUS_JV | 无变更（复核通过） |

| `LiTV` | Media | — | — | 立视科技（LiTV）为台湾独立 OTT 服务商 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Lightning` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `LinkedIn` | Social | — | Microsoft | LinkedIn 为 Microsoft 全资子公司（2016 收购，Microsoft 官方）· 2026-09 | CONFIRMED_PARENT | 迁移 Social → Microsoft |

| `Mail` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `MangoTV` | Media | — | MangoSuperMedia | 芒果 TV 由芒果超媒（湖南广电控股）运营（芒果超媒公开资料）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = MangoSuperMedia |

| `Manus` | AI | — | ButterflyEffect | Manus 由 Butterfly Effect（Monica 团队）开发 · 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = ButterflyEffect |

| `Meituan` | Shopping | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Messenger` | Meta | Meta | Meta | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Meta` | Meta | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 无变更（复核通过） |

| `MetaBrainz` | Utilities | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Microsoft` | Microsoft | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 无变更（复核通过） |

| `MicrosoftStore` | Microsoft | Microsoft | Microsoft | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Migu` | Media | — | ChinaMobile | 咪咕文化科技有限公司为中国移动全资子公司（中国移动官方/维基百科）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → ChinaMobile |

| `Mijia` | Home | — | Xiaomi | 米家为小米（Xiaomi）智能家居品牌（小米官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Xiaomi |

| `MikroTik` | Infrastructure | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `MiniMax` | AI | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Muse` | AI | — | — | 视觉主体为蓝色渐变「M」字标，未能确认唯一品牌实体（存在多个同名候选），暂不设母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `MusicBrainz` | Music | — | MetaBrainz | MusicBrainz 为 MetaBrainz Foundation 项目（MetaBrainz 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = MetaBrainz |

| `MusicJapan` | Music | — | — | 应用级名称，未识别到控股母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Musixmatch` | Music | — | — | 独立公司（Musixmatch S.p.A.），无母公司实体 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `MyVideo` | Media | — | TaiwanMobile | MyVideo 为台湾大哥大（Taiwan Mobile）旗下 OTT（MyVideo 官方 ©2026 TaiwanMobile）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = TaiwanMobile |

| `NBA` | Media | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `NBC` | Media | — | NBCUniversal | NBC 为 NBCUniversal 旗下电视网（NBCUniversal 官方）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → NBCUniversal |

| `NBCUniversal` | —(新增生态根) | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 迁移 —(新增生态根) → NBCUniversal（新生态根品牌） |

| `NHK` | Media | — | — | 日本公共广播机构（特殊法人），无商业母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `NetEase` | NetEase | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 无变更（复核通过） |

| `NetEaseCloudMusic` | NetEase | NetEase | NetEase | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `NetEaseMail` | NetEase | NetEase | NetEase | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Netflix` | Media | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Netherlands` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Niconico` | Media | — | Kadokawa | Niconico 由 Dwango/Kadokawa 集团运营（Kadokawa 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Kadokawa |

| `Nigeria` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Nintendo` | Game | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `NorthKorea` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Notion` | Utilities | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `NousResearch` | AI | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `NowE` | Media | — | PCCW | Now E / Now TV 为 PCCW/HKT 旗下（PCCW Media 官方）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → PCCW |

| `OKX` | Payment | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `OPPO` | Hardware | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Obsidian` | Utilities | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `OneDrive` | Microsoft | Microsoft | Microsoft | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `OpenAI` | AI | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `OpenWrt` | Infrastructure | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Oracle` | Infrastructure | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Outlook` | Microsoft | Microsoft | Microsoft | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `PCCW` | —(新增生态根) | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 迁移 —(新增生态根) → PCCW（新生态根品牌） |

| `Pandora` | Music | — | SiriusXM | Pandora 由 SiriusXM 持有运营（SiriusXM 官方/2019 收购）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = SiriusXM |

| `ParamountPlus` | Media | — | Paramount | Paramount+ 为 Paramount（Paramount Skydance）旗下流媒体（Paramount 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Paramount |

| `PayPal` | Payment | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Peacock` | Media | — | NBCUniversal | Peacock 为 NBCUniversal（Comcast）流媒体服务（NBCUniversal 官方财报）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → NBCUniversal；2026-09-30 display_name「Peacock TV」→「Peacock」+ 技术 ID `PeacockTV`→`Peacock`（目录/文件名同步，纯迁移） |

| `Perplexity` | AI | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `PikPak` | CloudStorage | — | — | 开发商归属未获权威来源证实，暂不设母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Pinduoduo` | Shopping | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Pinterest` | Social | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Pipixia` | Social | — | ByteDance | 皮皮虾由字节跳动旗下今日头条推出/运营（公开报道）· 2026-09 | CONFIRMED_PARENT | 迁移 Social → ByteDance |

| `Play` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `PlayStation` | Game | — | SONY | PlayStation 由 Sony Interactive Entertainment 运营，SIE 为索尼全资子公司（Sony 官方）· 2026-09 | CONFIRMED_PARENT | 迁移 Game → SONY |

| `Plex` | Media | — | — | Plex, Inc. 自有产品，无独立母公司实体 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `ApplePodcasts` | Media → Apple | — | Apple | Apple Podcasts 为 Apple 自有应用（Apple 官方识别规范）· 2026-09；2026-09-30 会话按 Apple 子品牌命名规范重命名 Podcasts → ApplePodcasts（目录/文件名/icon_path/display_name 全同步） | CONFIRMED_PARENT | 迁移 Media → Apple + 重命名 ApplePodcasts |

| `Poe` | AI | — | Quora | Poe 为 Quora 旗下 AI 产品（Quora 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Quora |

| `Poland` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `PrimeVideo` | Amazon | Amazon | Amazon | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Proxy` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |
| `Proxmox` | —(2026-09-30 新增) | — | — | Proxmox（开源虚拟化平台）品牌图标按用户提供的官方图标入库 · 2026-09-30 | NO_PARENT | 新增品牌（图标用户提供） |

| `QQ` | Tencent | Tencent | Tencent | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `QQMail` | Tencent | Tencent | Tencent | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `QQMusic` | Tencent | Tencent | Tencent | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Qobuz` | Music | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Quark` | Alibaba | Alibaba | Alibaba | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Qwen` | Alibaba | Alibaba | Alibaba | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Radiko` | Media | — | — | radiko 由日本民营广播电台共同出资的株式会社 radiko 运营 · 2026-09 | AMBIGUOUS_JV | 无变更（复核通过） |

| `RakutenTV` | Media | — | Rakuten | Rakuten TV 为乐天集团（Rakuten Group）旗下服务（Rakuten 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Rakuten |

| `ReadJapan` | Media | — | — | 未识别到对应商业实体，暂不设母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `RedBullTV` | Media | — | RedBull | Red Bull TV 由 Red Bull GmbH 运营（Red Bull 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = RedBull |

| `Reddit` | Social | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Reject` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `SF-Express` | Transport | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `SONY` | Hardware | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 迁移 Hardware → SONY（新生态根品牌） |

| `SOOP` | Media | — | — | SOOP（原 AfreecaTV）为韩国独立上市公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `SSID` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `STARZ` | Media | — | — | STARZ 已于 2025-05 从 Lionsgate 分拆独立上市（Lionsgate 官方）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `SWIFT` | Payment | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Samsung` | Hardware | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Search` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Singapore` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `SiriAI` | Apple | Apple | Apple | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |
| `SINA` | —(2026-09-30 新增) | — | — | 新浪（Sina Corporation）公司品牌图标按用户提供的官方图标入库 · 2026-09-30 | NO_PARENT | 新增品牌（图标用户提供）；白名单 `Sina` 移除，子品牌 Weibo 的 parent 指向 SINA |

| `Skype` | Communication | — | — | Microsoft 于 2025-05 停运 Skype，转为 Teams 生态；品牌退役，保留图标 · 2026-09 | RETIRED | 保留图标并标记退役（不迁移、不设母公司） |

| `SlingTV` | Media | — | EchoStar | Sling TV 属 EchoStar（DISH 集团）（EchoStar 财报）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = EchoStar |

| `Snapchat` | Communication | — | Snap | Snapchat 为 Snap Inc. 旗下产品（Snap 官方/NYSE: SNAP）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Snap |

| `SoundCloud` | Music | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Spain` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Speedtest` | Utilities | — | — | Ookla 于 2026-03 宣布出售给 Accenture，交割状态未确认，暂不设母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Spotify` | Music | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `StarPlus` | Media | — | — | Star Plus 现属 JioStar（Reliance × Disney 合资）· 2026-09 | AMBIGUOUS_JV | 无变更（复核通过） |

| `Steam` | Game | — | Valve | Steam 由 Valve Corporation 开发运营（Valve 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Valve |

| `Surge` | Surge | — | — | 特殊实体（Surge），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Synology` | Infrastructure | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `TELASA` | Media | — | — | TELASA 为 KDDI × テレビ朝日 合资公司运营 · 2026-09 | AMBIGUOUS_JV | 无变更（复核通过） |

| `TIDAL` | Music | — | Block | TIDAL 由 Block, Inc. 持多数股权（Block 官方/2026 股权结构）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Block |

| `TMDB` | Media | — | Xperi | TMDB 由 Xperi（TiVo）运营（TMDB 官方论坛说明）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Xperi |

| `TVB` | Media | — | — | TVB 股权分散（邵氏兄弟约 25%），无控股母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `TVer` | Media | — | — | TVer 由在京民放 5 家电视台共同出资设立 · 2026-09 | AMBIGUOUS_JV | 无变更（复核通过） |

| `Taobao` | Alibaba | Alibaba | Alibaba | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Telegram` | Communication | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Tencent` | Tencent | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 无变更（复核通过） |

| `TencentVideo` | Tencent | Tencent | Tencent | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `TestFlight` | Apple | Apple | Apple | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Thailand` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Threads` | Meta | Meta | Meta | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Tieba` | Baidu | Baidu | Baidu | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `TikTok` | ByteDance | ByteDance | ByteDance | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Traffic` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Tubi` | Media | — | Fox | Tubi 100% 归 Fox Corporation（Fox 官方/2020 收购）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Fox |

| `Turkey` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Twitch` | Amazon | Amazon | Amazon | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `UK` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `UNEXT` | Media | — | UNEXTHoldings | U-NEXT 由 U-NEXT HOLDINGS 运营（U-NEXT 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = UNEXTHoldings |

| `URL` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `US` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `Uber` | Transport | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `UnionPay` | Payment | — | — | 中国银联为多家银行共同出资的股份制公司，无单一母公司 · 2026-09 | AMBIGUOUS_JV | 无变更（复核通过） |

| `VideoMarket` | Media | — | PLAY | VideoMarket 由株式会社 PLAY 运营（VideoMarket 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = PLAY |

| `Vimeo` | Media | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Viu` | Media | — | PCCW | Viu 为 PCCW Media Group 旗下 OTT（PCCW Media 官方/APOS 2026）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → PCCW |

| `WOWOW` | Media | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `WSJ` | News | — | NewsCorp | 《华尔街日报》由 Dow Jones 出版，Dow Jones 为 News Corp 子公司（News Corp 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = NewsCorp |

| `Wallpaper` | Media | — | — | 应用级通用名称，无对应商业母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `WarnerBrosDiscovery` | —(新增生态根) | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 迁移 —(新增生态根) → WarnerBrosDiscovery（新生态根品牌） |

| `WeChat` | Tencent | Tencent | Tencent | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `WeTV` | Tencent | Tencent | Tencent | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Weibo` | Social | — | SINA | 微博由新浪（Sina Corporation）控股（微博年报/公开资料）· 2026-09；2026-09-30 SINA 公司图标入库后 parent 指向带图标条目 SINA | CONFIRMED_PARENT | parent_brand = SINA |

| `WhatsApp` | Meta | Meta | Meta | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Wikipedia` | Utilities | — | — | 由维基媒体基金会（非营利）运营，无商业母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `X` | Social | — | —（无品牌父级） | X Corp. 与 SpaceXAI 为**独立公司**（SpaceXAI 官方 Privacy Policy 明确「SpaceXAI is a separate company from X Corp.」；X 的使用（含 X 上的 Grok）由 X 条款管辖）· 2026-09-30 | NO_PARENT | **移除** `parent_brand`（原 xAI——不以 corporate ownership 推导品牌父级）；category 回到 Social |

| `Xbox` | Microsoft | Microsoft | Microsoft | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Xiaomi` | Hardware | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |
| `Xiaoyuzhou` | —(2026-09-30 新增) | — | — | 小宇宙（Xiaoyuzhou）播客 App 品牌图标按用户提供的官方图标入库 · 2026-09-30 | NO_PARENT | 新增品牌（图标用户提供） |

| `YouTube` | Google | Google | Google | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `YouTubeMusic` | Google | Google | Google | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Youku` | Media | — | Alibaba | 优酷为阿里巴巴集团在线视频平台（Alibaba 官方站点）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → Alibaba |

| `Z-Library` | Education | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Zhihu` | Social | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Zoom` | Utilities | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `bilibili` | Media | — | — | 独立上市公司；腾讯 18% / 阿里 7.6% 多为少数股权与投票权分离，无控股母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `dAnimeStore` | Media | — | NTTDocomo | d Anime Store 由 Docomo Anime Store 株式会社运营（NTT docomo 集团）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = NTTDocomo |

| `discoveryPlus` | Media | — | WarnerBrosDiscovery | discovery+ 归 WBD「Discovery Global」业务（discovery+ 官方页 ©2026 Warner Bros. Discovery）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → WarnerBrosDiscovery |

| `eBay` | Shopping | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `friDayVideo` | Media | — | FarEasTone | friDay 影音为远传电信（FarEasTone）旗下服务（远传官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = FarEasTone |

| `iCloud` | Apple | Apple | Apple | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `iCloudPrivateRelay` | Apple | Apple | Apple | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `iQIYI` | Media | — | Baidu | 爱奇艺最大股东为百度，百度持多数投票权（爱奇艺年报/公开报道）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → Baidu |

| `mora` | Music | — | SONY | mora 由 Sony Music Solutions（索尼音乐娱乐日本集团）运营（mora 官方）· 2026-09 | CONFIRMED_PARENT | 迁移 Music → SONY |

| `myTVSUPER` | Media | — | TVB | myTV SUPER 为电视广播有限公司（TVB）旗下（TVB 官方站点）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = TVB |

| `pixiv` | Social | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `rednote` | Social | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `vivo` | Hardware | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `SpaceXAI` | —(公司品牌) | — | —（公司品牌，无品牌父级） | 公司品牌（`entity_type=product_brand`）；canonical descendants = 1（仅 Grok）< 2 → **不构成独立生态**；2026-07-06 由 xAI 官方品牌标识更名而来 | NO_PARENT | 迁移 新生态根(xAI) → SpaceXAI（**降为 product_brand**，目录 icons/AI/SpaceXAI/） |


## 8. 边界与后续监控 / Boundaries & Follow-ups

- **CI 能力边界**：CI 只能验证 `brands.json` ↔ 磁盘 ↔ `categories.json` ↔ `surge-icon.json` 的结构一致性，**无法证明现实世界归属的完整性**；现实归属由本文件承担（研究层）。[§64 §96 §97]
- **本轮发现的高价值漏项**：`Hulu → Disney`、`ESPN → Disney`、`LinkedIn/GitHub → Microsoft`、`Youku → Alibaba`、`iQIYI → Baidu`、`Doubao/Pipixia → ByteDance`、`Podcasts → Apple`、`mora → Sony` 等，均在 PR 分支真实缺失，属本轮发现并修复。
- **本轮厘清的关系（Final Seal Review 定稿）**：`Grok → SpaceXAI`（产品关系，官方 Terms 证据）；`X` **无品牌父级**（官方 Privacy Policy 明确 SpaceXAI 与 X Corp. 为独立公司，不以 corporate ownership 推导 `parent_brand`）；`SpaceX` = corporate owner only，不进入 Brand Graph。
- **仍易变关系（后续需按 §95 复验）**：`Lemino`（2026-10-01 起与 WOWOW 合资）、`discovery+`（WBD 拆分进行中，与 Max 整合预期）、`Speedtest`（Ookla 出售给 Accenture 已宣布、交割待确认）。`HBOMax` 经核实 2025-05 已由 "Max" 改回 "HBO Max"，当前 display_name 正确（官方页 max.com 现标题为 HBO Max）；`JioHotstar` 经核实为 Hotstar 与 JioCinema 于 2025 年合并后的现行官方名称（JioStar 旗下），**不改名**，且不属于 Disney 生态。
- **退役品牌**：`Skype`（2025-05 停运）、`KKTV`（2025-12-31 停运并入 LINE TV）保留图标并标记退役，不参与生态归属。
- **后续监控建议**：品牌被收购/分拆/更名/关停时，必须重新验证 current state，并同步本文件与 `brands.json`。[§95]
## 9. mihomo-rules 对照 / mihomo-rules Compatibility Matrix

> **对照源语义**：mihomo-rules `scripts/lib/ownership_map.py` 的 `SUB_PARENT` 是**直接父品牌映射**，并由 mihomo 的祖先链解析、父子规则剥离和「子品牌先于父品牌」排序直接消费；本审计不把它解释为 platform/distribution 字段。共 **34 对**，2026-09-30 只读审计，未修改 mihomo-rules。
> 2026-09-30 起 Oasisic `parent_brand` 采用**直接父品牌**语义，因此 Grok 的 `mihomo: X` vs `Oasisic: SpaceXAI` 是真实直接父冲突，状态为 `MISMATCH`，不自动同步。
> Peacock 注记：Peacock 不在 SUB_PARENT 中（34 对无 Peacock），2026-09-30 技术 ID 由旧名（PeacockTV）
> 迁移为 `Peacock`，对 mihomo 对照**零影响**；mihomo 4 个 config 中 Peacock 的**旧技术 ID 图标 URL**
> 属既有 stale 引用（早于 NBCUniversal 生态迁移），不在本仓修改范围。

| 品牌 | Oasisic parent_brand | mihomo SUB_PARENT | Oasisic 生态根（派生） | 结论 |
|---|---|---|---|---|
| AWS | Amazon | Amazon | Amazon | MATCH |
| AppStore | Apple | Apple | Apple | MATCH |
| AppleFitnessPlus | Apple | Apple | Apple | MATCH |
| AppleMusic | Apple | Apple | Apple | MATCH |
| AppleNews | —（现为 AppleNewsPlus） | Apple | — | NOT_CONSUMED（ID 改名）：Oasisic canonical=AppleNewsPlus（Apple News+）；经 alias 对照后直接父双方均为 Apple → 语义 MATCH |
| AppleTV | Apple | Apple | Apple | MATCH |
| Azure | Microsoft | Microsoft | Microsoft | MATCH |
| Bing | Microsoft | Microsoft | Microsoft | MATCH |
| Copilot | Microsoft | Microsoft | Microsoft | MATCH |
| GitHub | Microsoft | Microsoft | Microsoft | MATCH |
| Gmail | Google | Google | Google | MATCH |
| GoogleAI | Google | Google | Google | MATCH |
| GoogleDrive | Google | Google | Google | MATCH |
| GoogleMaps | Google | Google | Google | MATCH |
| GoogleNews | Google | Google | Google | MATCH |
| GooglePhotos | Google | Google | Google | MATCH |
| GooglePlay | Google | Google | Google | MATCH |
| GoogleVoice | Google | Google | Google | MATCH |
| Grok | SpaceXAI | X | —（X 现无品牌父级） | **MISMATCH**：mihomo `SUB_PARENT` 与 Oasisic `parent_brand` 都是直接父语义；mihomo= X，Oasisic=SpaceXAI。X 平台集成事实不能把该冲突改写为 platform relation / AMBIGUOUS；本轮不自动修改 mihomo |
| Hotstar | —（现为 JioHotstar） | Disney | — | STALE（mihomo 侧）+ NOT_CONSUMED：Oasisic canonical=JioHotstar（2025 Hotstar×JioCinema 合并后现名，属 JioStar 合资，AMBIGUOUS_JV），**不属 Disney 生态**；建议 mihomo 后续更新 |
| Hulu | Disney | Disney | Disney | MATCH |
| Instagram | Facebook | Facebook | Meta | MATCH |
| Messenger | Facebook | Facebook | Meta | MATCH |
| OneDrive | Microsoft | Microsoft | Microsoft | MATCH |
| Outlook | Microsoft | Microsoft | Microsoft | MATCH |
| PrimeVideo | Amazon | Amazon | Amazon | MATCH |
| SiriAI | Apple | Apple | Apple | MATCH |
| Threads | Facebook | Facebook | Meta | MATCH |
| WhatsApp | Facebook | Facebook | Meta | MATCH |
| Xbox | Microsoft | Microsoft | Microsoft | MATCH |
| YouTube | Google | Google | Google | MATCH |
| YouTubeMusic | YouTube | YouTube | Google | MATCH |
| iCloud | Apple | Apple | Apple | MATCH |
| iCloudPrivateRelay | iCloud | iCloud | Apple | MATCH |

**结论**：34 对中 **31 对 MATCH / 1 对 MISMATCH（Grok）/ 2 对 NOT_CONSUMED**（AppleNews / Hotstar）；`Grok` 的两边字段都表示直接父品牌，mihomo=`X`、Oasisic=`SpaceXAI`，是需要人工决定的真实语义冲突；不能用 X 平台集成事实伪造 MATCH 或 AMBIGUOUS。`Hotstar→Disney` 为 downstream stale，现名 JioHotstar 属 JioStar 合资、不属 Disney。

**状态口径**（与 `scripts/mihomo_compare.py` 一致）：`MATCH` / `OASISIC_MORE_PRECISE` / `MIHOMO_MORE_PRECISE` / `MISMATCH` / `STALE` / `NOT_CONSUMED` / `OASISIC_ONLY` / `AMBIGUOUS` / `MISSING`。对照以**语义层级**为准而非字符串相等：mihomo 只表达直接父、Oasisic 另有更深祖先链时仍判 `MATCH`（如 `YouTubeMusic → YouTube` vs `YouTubeMusic → YouTube → Google`）；双方直接父都已明确但值不同则判 `MISMATCH`。机械可判定项由 `compare()` 自动归类，`STALE` / `*_MORE_PRECISE` 由带证据的 `overrides` 标注。
**长期方向**：Oasisic `brands.json`（id / display_name / parent_brand / entity_type + 派生生态根）作为品牌关系 SSOT，mihomo-rules 后续可消费其 parent_brand 生成 SUB_PARENT，减少双仓手工维护。本轮**未修改** mihomo-rules。
