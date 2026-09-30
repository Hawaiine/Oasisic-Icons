# 品牌归属审计报告 / Brand Ownership Audit

> **审计日期**：2026-09-30 · **范围**：PR #9 特性分支 `refactor/ecosystem-threshold-v2` 全库 **289** 个 Canonical Brand（含 5 个本轮新增生态根品牌）

> 本文件是 **研究/证据层**：记录每个品牌当前（现实世界）母公司判断与依据。
> SSOT 仍为 `config/brands.json`（`parent_brand` / `category` / `entity_type`）——本文件不替代 SSOT。[§65 §66 §97]

## 1. 方法与口径 / Methodology

对全库每一个 Canonical Brand（不是抽样、不是只扫已有 `parent_brand`）逐一执行：

1. 取 `brands.json` 中的 `id / category / entity_type / parent_brand` 与磁盘 PNG 实际主体；
2. 主动检索现实世界的**当前**控股关系（官方站点 / 官方公告 / 财报 / 公司登记信息 / 权威百科），不依赖历史 metadata；[§92 §93 §95]
3. 判断控股口径：**全资或多数控股**记为 `CONFIRMED_PARENT`；少数股权与合资公司一律不设母公司；[§102]
4. 不得仅凭品牌名推断归属（如 `DisneyPlus`、`ChinaMobileDisk` 均需证据）；
5. 对每个 `parent_brand` 统计 Canonical Child 数，套用硬规则：**children ≥ 2 → 必须存在一级生态分类**；
   children < 2 → `parent_brand` 照记，子品牌保留在功能分类，不新建生态分类。[§83 §84 §85]

**五类状态**（每个品牌必须落入其一，不允许「未审查」）：`CONFIRMED_PARENT` / `NO_PARENT` / `AMBIGUOUS_JV` / `RETIRED` / `SPECIAL_ENTITY`。[§91]

## 2. 来源 / Sources

- 官方站点与官方公告：Disney / NBCUniversal / WBD / Sony / PCCW / xAI / Microsoft / Apple / Alibaba / Baidu / ByteDance / China Mobile / China Telecom / 中华电信 / 台灣大哥大 / 遠傳 / TVB / 有线宽频 / KKCompany / DMM / 第一興商 / Red Bull / Rakuten / 楽天 / NTT docomo / Kadokawa / U-NEXT / Quora / Kakao / Snap / Valve / Kuaishou / SiriusXM / Block / Paramount / Fox / MetaBrainz / News Corp / Xperi / JioStar / LY Corporation 等；
- 季度/年度财报与投资者关系页：Liberty Media（F1）、EchoStar（Sling TV / DISH）、Comcast（Peacock）、Warner Bros. Discovery、PCCW Limited；
- 权威百科与公开报道（用于交叉验证，不单独作为重大关系的唯一依据）；[§68]
- 现场联网检索于 2026-09-30 执行（`as-of` 即该日期）。

## 3. 结论摘要 / Summary

| 状态 | 品牌数 |
|---|---:|
| CONFIRMED_PARENT（已确认母公司） | 116 |
| NO_PARENT（无母公司/独立实体/生态根） | 114 |
| AMBIGUOUS_JV（合资/股权分散，不设母公司） | 10 |
| RETIRED（已退役，保留图标） | 2 |
| SPECIAL_ENTITY（Country/System/Surge/Proxy/Crypto 特殊实体） | 47 |
| **合计** | **289** |

| 指标 | 审计前 | 审计后 |
|---|---:|---:|
| 分类数（含 1 个 reserved） | 35 | 42 |
| 生态分类数 | 10 | 17 |
| Canonical 品牌数 | 284 | 289 |
| 已记录 parent_brand 的品牌数 | 58 | 116 |
| 无图标母公司白名单条目 | 0 | 31 |

## 4. 本轮新发现并新建的生态 / Newly Discovered Ecosystems

| 生态（新一级分类） | Canonical Children | 子品牌 | 证据要点 |
|---|---:|---|---|

| **ChinaMobile** | 2 | ChinaMobileDisk / Migu | 中国移动云盘 + 咪咕（咪咕文化科技为中国移动全资子公司） |

| **Disney** | 3 | DisneyPlus / ESPN / Hulu | Disney 全资：Disney+/Hulu（2025 收购 Comcast 剩余股份）/ESPN（80%） |

| **NBCUniversal** | 2 | NBC / PeacockTV | NBC 为 NBCUniversal 电视网；Peacock 为 NBCUniversal 流媒体（Comcast） |

| **PCCW** | 2 | NowE / Viu | Viu 与 Now E 同属 PCCW Media Group / HKT |

| **Sony** | 3 | Crunchyroll / PlayStation / mora | Sony 全资体系：SIE（PlayStation）/索尼影视（Crunchyroll）/索尼音乐（mora） |

| **Warner Bros. Discovery** | 2 | HBOMax / discoveryPlus | HBO Max 与 discovery+ 均归属 WBD（拆分仍处进行中，2026-09 复核） |

| **xAI** | 2 | Grok / X | xAI 旗下：X（2025-03 收购 X Corp）与 Grok；xAI 于 2026-02 成为 SpaceX 全资子公司 |


## 5. 既有生态的补全与复核 / Existing Ecosystems Revalidated

| 生态 | 审计前 children | 审计后 children | 本轮新增 | 复核结论 |
|---|---:|---:|---|---|

| Alibaba | — | 7 | Youku | 关系全部复核通过 |

| Amazon | — | 5 | — | 关系全部复核通过 |

| Apple | — | 12 | Podcasts | 关系全部复核通过 |

| Baidu | — | 3 | iQIYI | 关系全部复核通过 |

| ByteDance | — | 5 | Doubao, Pipixia | 关系全部复核通过 |

| Meta | — | 5 | — | 关系全部复核通过 |

| Google | — | 11 | — | 关系全部复核通过 |

| NetEase | — | 2 | — | 关系全部复核通过 |

| Microsoft | — | 9 | LinkedIn, GitHub | 关系全部复核通过 |

| Tencent | — | 6 | — | 关系全部复核通过 |


## 6. 无自身图标的母公司白名单 / `parent_brands_without_icon`

以下母公司为已确认的现实世界母公司，但仓库暂无其品牌图标；**其 children < 2，不触发一级生态分类**，子品牌保留在原功能分类并记录 `parent_brand`。[§83 §100]

`Block`, `ButterflyEffect`, `ChunghwaTelecom`, `DMM`, `Daiichikosho`, `EchoStar`, `FarEasTone`, `Fox`, `KKCompany`, `Kadokawa`, `Kakao`, `Kuaishou`, `LibertyMedia`, `MangoSuperMedia`, `MoonshotAI`, `NTTDocomo`, `NewsCorp`, `PLAY`, `Paramount`, `Quora`, `Rakuten`, `RedBull`, `Sina`, `SiriusXM`, `Snap`, `TaiwanMobile`, `UNEXTHoldings`, `Valve`, `Xperi`, `ZhipuAI`, `iCABLE`


## 7. 全量矩阵 / Full Ownership Matrix（289 / 289）

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

| `CATCHPLAY` | Media | — | — | CATCHPLAY 为台湾独立影音平台 · 2026-09 | NO_PARENT | 无变更（复核通过） |

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

| `Grok` | AI | — | xAI | Grok 由 xAI 开发，xAI 于 2026-02 成为 SpaceX 全资子公司（xAI 官方「xAI joins SpaceX」）· 2026-09 | CONFIRMED_PARENT | 迁移 AI → xAI |

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

| `PeacockTV` | Media | — | NBCUniversal | Peacock 为 NBCUniversal（Comcast）流媒体服务（NBCUniversal 官方财报）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → NBCUniversal |

| `Perplexity` | AI | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `PikPak` | CloudStorage | — | — | 开发商归属未获权威来源证实，暂不设母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Pinduoduo` | Shopping | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Pinterest` | Social | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Pipixia` | Social | — | ByteDance | 皮皮虾由字节跳动旗下今日头条推出/运营（公开报道）· 2026-09 | CONFIRMED_PARENT | 迁移 Social → ByteDance |

| `Play` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `PlayStation` | Game | — | SONY | PlayStation 由 Sony Interactive Entertainment 运营，SIE 为索尼全资子公司（Sony 官方）· 2026-09 | CONFIRMED_PARENT | 迁移 Game → SONY |

| `Plex` | Media | — | — | Plex, Inc. 自有产品，无独立母公司实体 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `Podcasts` | Media | — | Apple | Apple Podcasts 为 Apple 自有应用（Apple 官方识别规范）· 2026-09 | CONFIRMED_PARENT | 迁移 Media → Apple |

| `Poe` | AI | — | Quora | Poe 为 Quora 旗下 AI 产品（Quora 官方）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Quora |

| `Poland` | Country | — | — | 特殊实体（Country），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

| `PrimeVideo` | Amazon | Amazon | Amazon | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Proxy` | System | — | — | 特殊实体（System），不参与普通母公司归属 [§87] | SPECIAL_ENTITY | 无变更（复核通过） |

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

| `Weibo` | Social | — | Sina | 微博由新浪（Sina Corporation）控股（微博年报/公开资料）· 2026-09 | CONFIRMED_PARENT | 补全 parent_brand = Sina |

| `WhatsApp` | Meta | Meta | Meta | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Wikipedia` | Utilities | — | — | 由维基媒体基金会（非营利）运营，无商业母公司 · 2026-09 | NO_PARENT | 无变更（复核通过） |

| `X` | Social | — | xAI | X Corp. 为 xAI 子公司（2025-03 xAI 全股票收购 X Corp）· 2026-09 | CONFIRMED_PARENT | 迁移 Social → xAI |

| `Xbox` | Microsoft | Microsoft | Microsoft | 本次全库复核：既有 parent_brand 关系仍成立 · 2026-09 | CONFIRMED_PARENT | 无变更（复核通过） |

| `Xiaomi` | Hardware | — | — | 独立实体（无控股母公司）· 2026-09 | NO_PARENT | 无变更（复核通过） |

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

| `xAI` | —(新增生态根) | — | —（生态根品牌） | 生态根品牌（entity_type=ecosystem），自身无母公司 | NO_PARENT | 迁移 —(新增生态根) → xAI（新生态根品牌） |


## 8. 边界与后续监控 / Boundaries & Follow-ups

- **CI 能力边界**：CI 只能验证 `brands.json` ↔ 磁盘 ↔ `categories.json` ↔ `surge-icon.json` 的结构一致性，**无法证明现实世界归属的完整性**；现实归属由本文件承担（研究层）。[§64 §96 §97]
- **本轮发现的高价值漏项**：`Hulu → Disney`、`ESPN → Disney`、`LinkedIn/GitHub → Microsoft`、`Youku → Alibaba`、`iQIYI → Baidu`、`Doubao/Pipixia → ByteDance`、`Podcasts → Apple`、`mora → Sony` 等，均在 PR 分支真实缺失，属本轮发现并修复。
- **易变关系**：`X / Grok → xAI`（xAI 2026-02 起为 SpaceX 全资子公司，品牌结构处于变动期）、`Lemino`（2026-10-01 起与 WOWOW 合资）、`HBO Max / discovery+`（WBD 拆分进行中）、`Speedtest`（Ookla 出售给 Accenture 已宣布、交割待确认）——后续需按 §95 重新验证。
- **退役品牌**：`Skype`（2025-05 停运）、`KKTV`（2025-12-31 停运并入 LINE TV）保留图标并标记退役，不参与生态归属。
- **后续监控建议**：品牌被收购/分拆/更名/关停时，必须重新验证 current state，并同步本文件与 `brands.json`。[§95]