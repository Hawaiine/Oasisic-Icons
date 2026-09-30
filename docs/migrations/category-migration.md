# 分类迁移记录 / Category Migration

> 方案 C 彻底重构（2026-09-29）。基线 `2d9af1f`（24 分类 / 280 品牌 / 367 PNG）→ 31 分类 / 280 品牌 / 367 PNG。
> 数量守恒已验证（git 移动，未改图片内容；SHA-256 前后一致）。

## 一级分类变化

| 旧分类 | 处置 | 说明 |
|---|---|---|
| DevOps | 已删除 | → 拆入 Infrastructure（Cloudflare/Docker/MikroTik/OpenWrt/Oracle/Synology）+ Amazon/AWS + Microsoft/Azure |
| Drive | 已删除 | → CloudStorage（云盘）+ Alibaba/AliCloud |
| General | 已删除 | → System（16 个系统图标）+ AI/Manus + Tencent/QQMail + Communication/NetEaseMail + Utilities/Baidu/MetaBrainz |
| Tool | 已删除 | → Development/GitHub、Education/Duolingo+Z-Library、Hardware/DJI、System/Airport、Transport/DiDi+Uber+SF-Express、Media/TMDB、Health/Keep、Utilities/其余 7 个 |
| Telecom | 重组 | → 只保留 4 家运营商；8 个手机品牌 → Hardware，Aqara/Mijia → Home |
| Media | 重组 | → 移出 PrimeVideo（Amazon）、TencentVideo/WeTV（Tencent）、Douyin（Social）、KKBOX（Music）、BBC（保留 Media） |
| Social | 重组 | → 移出通讯类 8 个 → Communication，腾讯系 4 个 → Tencent |

**新增分类（11）**（品牌数为最终状态）：

| 分类 | 来源 | 品牌数 |
|---|---|---|
| Amazon | 新增 | 6 |
| Alibaba | 新增 | 5 |
| Tencent | 新增 | 7 |
| Infrastructure | 新增（初建名 Cloud，终审重命名） | 6 |
| CloudStorage | 新增 | 8 |
| Communication | 新增 | 11 |
| Hardware | 新增 | 9 |
| Home | 新增 | 2 |
| System | 新增 | 20 |
| Transport | 新增 | 3 |
| Utilities | 新增 | 10 |

**分类内调整（终审）**：

| 变更 | 说明 |
|---|---|
| Cloud → Infrastructure 重命名 | 成员含 MikroTik（路由器）/OpenWrt（路由系统）/Synology（NAS），「Cloud」语义不覆盖；统一主题为基础设施与运维 |
| Airport: Transport → System | 通用机场规则组语义，非具体机场品牌 |
| Adobe: Development → Utilities | 创意软件套件，非开发者工具 |
| Health: reserved → active | Keep 已存在，reserved 与 SSOT 矛盾 |

## 本轮增量：生态归属审计新增生态（2026-09-30）

> 依据「parent_brand ≥2 children → 必须一级生态分类」硬规则，本轮由全库归属审计新发现并建立 7 个生态分类（35 → 42 分类，10 → 17 生态）。

| 新分类 | 显示名 | 依据（≥2 confirmed children） |
|---|---|---|
| `Disney` | Disney | DisneyPlus, ESPN, Hulu |
| `NBCUniversal` | NBCUniversal | NBC, PeacockTV |
| `WarnerBrosDiscovery` | Warner Bros. Discovery | HBOMax, discoveryPlus |
| `ChinaMobile` | ChinaMobile | ChinaMobileDisk, Migu |
| `SONY` | Sony | Crunchyroll, PlayStation, mora |
| `PCCW` | PCCW | NowE, Viu |
| `xAI` | xAI | Grok, X |

## 修正增量（2026-10-01）：恢复 SpaceXAI 生态分类

> 2026-09-30 曾依当时结论移除 `SpaceXAI` 生态分类（42 → 41）；2026-10-01 按用户确认的最终品牌树
> 恢复（41 → 42 分类，生态 16 → 17）。

| 新分类 | 显示名 | 依据（≥2 canonical descendants） | 根图标状态 |
|---|---|---|---|
| `SpaceXAI` | SpaceXAI | X / xAI / Grok = 3 ≥ 2 | **待官方标志**：根条目与根图标未建，登记白名单 + Review Queue，不得伪造 |
