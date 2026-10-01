<!-- generated: physical-hierarchy-audit (scripts/gen-physical-hierarchy-audit.py) -->

# 物理层级与全库关系矩阵（generated）

> 本文件由 `scripts/gen-physical-hierarchy-audit.py` 从 `config/brands.json` +
> `scripts/brand_relationships.py` 派生，禁止手工编辑（CI 第 17 组逐字节校验）。

## 1. 物理路径模型

```text
icons/<category>/<id>/<id>.png                     一级 direct child（category root 的直系子）
icons/<category>/<中间父…>/<id>/<id>.png           同类中间父品牌下的深层子品牌（可多层）
```

- 一级目录恒为 `category`，不因关系改变；
- 仅当直接父品牌**本身也有父品牌**（非 graph root）且同 category 且自身有图标时，才物理嵌套；
- cross-category 父品牌不迁移；白名单母公司（无图标）不制造伪目录。

## 2. 多层关系（需要嵌套的全部品牌）

| Child | Direct Parent | Ancestor Chain | Category | Current Path | Expected Path | Action |
|:---|:---|:---|:---|:---|:---|:---|
| `Grok` | `xAI` | Grok → xAI → SpaceXAI | `SpaceXAI` | `icons/SpaceXAI/xAI/Grok/Grok.png` | `icons/SpaceXAI/xAI/Grok/Grok.png` | KEEP |
| `Instagram` | `Facebook` | Instagram → Facebook → Meta | `Meta` | `icons/Meta/Facebook/Instagram/Instagram.png` | `icons/Meta/Facebook/Instagram/Instagram.png` | KEEP |
| `Messenger` | `Facebook` | Messenger → Facebook → Meta | `Meta` | `icons/Meta/Facebook/Messenger/Messenger.png` | `icons/Meta/Facebook/Messenger/Messenger.png` | KEEP |
| `Threads` | `Facebook` | Threads → Facebook → Meta | `Meta` | `icons/Meta/Facebook/Threads/Threads.png` | `icons/Meta/Facebook/Threads/Threads.png` | KEEP |
| `WhatsApp` | `Facebook` | WhatsApp → Facebook → Meta | `Meta` | `icons/Meta/Facebook/WhatsApp/WhatsApp.png` | `icons/Meta/Facebook/WhatsApp/WhatsApp.png` | KEEP |
| `YouTubeMusic` | `YouTube` | YouTubeMusic → YouTube → Google | `Google` | `icons/Google/YouTube/YouTubeMusic/YouTubeMusic.png` | `icons/Google/YouTube/YouTubeMusic/YouTubeMusic.png` | KEEP |
| `iCloudPrivateRelay` | `iCloud` | iCloudPrivateRelay → iCloud → Apple | `Apple` | `icons/Apple/iCloud/iCloudPrivateRelay/iCloudPrivateRelay.png` | `icons/Apple/iCloud/iCloudPrivateRelay/iCloudPrivateRelay.png` | KEEP |

多层关系（`child.parent_brand = P` 且 `P.parent_brand != null`）共 **7** 条。

## 3. cross-category 父品牌（VALID_CROSS_CATEGORY，不迁移）

| Child | Parent | Child Category | Parent Category | Path | Action |
|:---|:---|:---|:---|:---|:---|
| `189` | `ChinaTelecom` | `CloudStorage` | `Telecom` | `icons/CloudStorage/189/189.png` | KEEP（关系由 SSOT 表达） |
| `Mijia` | `Xiaomi` | `Home` | `Hardware` | `icons/Home/Mijia/Mijia.png` | KEEP（关系由 SSOT 表达） |
| `MusicBrainz` | `MetaBrainz` | `Music` | `Utilities` | `icons/Music/MusicBrainz/MusicBrainz.png` | KEEP（关系由 SSOT 表达） |

cross-category 关系共 **3** 条。

## 4. Parent without icon（白名单母公司，不制造伪目录）

| Parent (whitelist) | Children |
|:---|:---|
| `Block` | `TIDAL` |
| `ButterflyEffect` | `Manus` |
| `ChunghwaTelecom` | `HamiVideo` |
| `DMM` | `DMMTV` |
| `Daiichikosho` | `KaraokeDAM` |
| `EchoStar` | `SlingTV` |
| `FarEasTone` | `friDayVideo` |
| `Fox` | `Tubi` |
| `KKCompany` | `KKBOX` |
| `Kadokawa` | `Niconico` |
| `Kakao` | `KakaoTalk` |
| `Kuaishou` | `Kwai` |
| `LibertyMedia` | `F1TV` |
| `MangoSuperMedia` | `MangoTV` |
| `MoonshotAI` | `Kimi` |
| `NTTDocomo` | `dAnimeStore` |
| `NewsCorp` | `WSJ` |
| `PLAY` | `VideoMarket` |
| `Paramount` | `ParamountPlus` |
| `Quora` | `Poe` |
| `Rakuten` | `RakutenTV` |
| `RedBull` | `RedBullTV` |
| `SiriusXM` | `Pandora` |
| `Snap` | `Snapchat` |
| `TaiwanMobile` | `MyVideo` |
| `UNEXTHoldings` | `UNEXT` |
| `Valve` | `Steam` |
| `Xperi` | `TMDB` |
| `ZhipuAI` | `GLM` |
| `iCABLE` | `HOYTV` |

无图标母公司共 **30** 个（登记于 `parent_brands_without_icon`）。

## 5. 生态矩阵（§47）

| Ecosystem | Logical Root | Has Icon | Category | Canonical Descendants | Status |
|:---|:---|:---|:---|:---|:---|
| `Alibaba` | `Alibaba` | YES | `Alibaba` | 7 | Ecosystem |
| `Amazon` | `Amazon` | YES | `Amazon` | 5 | Ecosystem |
| `Apple` | `Apple` | YES | `Apple` | 12 | Ecosystem |
| `Baidu` | `Baidu` | YES | `Baidu` | 3 | Ecosystem |
| `ByteDance` | `ByteDance` | YES | `ByteDance` | 5 | Ecosystem |
| `ChinaMobile` | `ChinaMobile` | YES | `ChinaMobile` | 2 | Ecosystem |
| `Disney` | `Disney` | YES | `Disney` | 3 | Ecosystem |
| `Google` | `Google` | YES | `Google` | 11 | Ecosystem |
| `Meta` | `Meta` | YES | `Meta` | 5 | Ecosystem |
| `Microsoft` | `Microsoft` | YES | `Microsoft` | 9 | Ecosystem |
| `NBCUniversal` | `NBCUniversal` | YES | `NBCUniversal` | 2 | Ecosystem |
| `NetEase` | `NetEase` | YES | `NetEase` | 2 | Ecosystem |
| `PCCW` | `PCCW` | YES | `PCCW` | 2 | Ecosystem |
| `SONY` | `SONY` | YES | `SONY` | 3 | Ecosystem |
| `SpaceXAI` | `SpaceXAI` | YES | `SpaceXAI` | 3 | Ecosystem |
| `Tencent` | `Tencent` | YES | `Tencent` | 6 | Ecosystem |
| `WarnerBrosDiscovery` | `WarnerBrosDiscovery` | YES | `WarnerBrosDiscovery` | 2 | Ecosystem |

生态分类共 **17** 个；其中无根图标（PENDING，登记白名单）**0** 个。

## 6. 统计

- canonical product brands：**234**
- canonical ecosystem entities：**1**
- 物理父品牌节点：**26**
- 深层嵌套品牌（路径 ≥ 5 段）：**7**
- 生态根（含逻辑生态根）：**17**
