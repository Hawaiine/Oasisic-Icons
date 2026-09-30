# Parent Edge Semantic Evidence Audit

> 本文档由 `scripts/gen-parent-edge-evidence.py` 生成，与 `config/parent-edge-evidence.json` 同源，请勿手工编辑。它是对全部 live `parent_brand` edge 的**证据分级**，不修改 `config/brands.json`。

## Contract

`parent_brand` is valid only when the child is presented as a sub-brand/product brand under the immediate parent, or the parent is the direct brand umbrella. Corporate ownership, developer/provider status, platform hosting, and distribution are **not** sufficient by themselves.

## Decision rules（按顺序，先命中先判定）

| # | Rule | Classification | Condition |
|---:|---|---|---|
| 1 | `R1_GENERIC_RESTATEMENT` | `AMBIGUOUS` | evidence contains the generic restatement '既有 parent_brand 关系仍成立' |
| 2 | `R2_PLATFORM_INTEGRATION` | `PLATFORM_RELATION_ONLY` | evidence contains platform-integration language ('平台使用' / '可通过 X' / 'available on') |
| 3 | `R3_DEVELOPER` | `DEVELOPER_PROVIDER_ONLY` | evidence contains '开发' (developer/provider statement) |
| 4 | `R4_BRAND_UMBRELLA` | `BRAND_HIERARCHY_CONFIRMED` | evidence contains an umbrella noun (品牌/产品/服务/应用/电视网/流媒体/OTT/旗下) |
| 5 | `R5_EQUITY_CONTROL` | `CORPORATE_OWNERSHIP_ONLY` | evidence contains an equity/control term (全资/多数/控股/收购/持有/股权/子公司/归属/运营/集团) |
| 6 | `R6_DEFAULT` | `AMBIGUOUS` | no rule matched |

> **重要限制**：分级是 evidence 字符串的确定性函数，不是现实世界归属的证明；`BRAND_HIERARCHY_CONFIRMED` 也只表示**证据文本**具备品牌伞状措辞，仍需人工按 primary source 复核。若后续修订 §7 矩阵的证据文本，必须重跑本生成器，计数会随之变化。

## Results

| Classification | Count | Interpretation |
|---|---:|---|
| `BRAND_HIERARCHY_CONFIRMED` | 20 | The evidence string names the child as a brand/product/service under the parent (umbrella language). |
| `CORPORATE_OWNERSHIP_ONLY` | 28 | The evidence string records equity/control/operation; it does not by itself state a brand umbrella. |
| `DEVELOPER_PROVIDER_ONLY` | 7 | The evidence string records development/operation, not a brand umbrella. |
| `PLATFORM_RELATION_ONLY` | 0 | The evidence string records platform access/hosting/distribution only. |
| `AMBIGUOUS` | 60 | Generic restatement, organisation-unit language, or no matchable evidence. |
| **Total** | **115** | **All live edges extracted from `config/brands.json`.** |

## Architecture finding

**BLOCKER:** 旧方法论把「全资或多数控股」直接记为 `CONFIRMED_PARENT`，这只证明 corporate control，不必然证明 Brand / Product Hierarchy。因此本 manifest 不把 ownership-only、developer/provider-only 与泛化复述的行静默升级为已闭合。

当前 SSOT 的 115 条边**未被修改**。后续闭合必须逐边补 primary-source Brand Hierarchy 证据，或由人工明确裁决。

### BRAND_HIERARCHY_CONFIRMED

`189 → ChinaTelecom`, `ApplePodcasts → Apple`, `ChinaMobileDisk → ChinaMobile`, `DisneyPlus → Disney`, `F1TV → LibertyMedia`, `KakaoTalk → Kakao`, `Kwai → Kuaishou`, `Mijia → Xiaomi`, `MyVideo → TaiwanMobile`, `NBC → NBCUniversal`, `NowE → PCCW`, `ParamountPlus → Paramount`, `Peacock → NBCUniversal`, `Pipixia → ByteDance`, `Poe → Quora`, `RakutenTV → Rakuten`, `Snapchat → Snap`, `Viu → PCCW`, `friDayVideo → FarEasTone`, `myTVSUPER → TVB`

### CORPORATE_OWNERSHIP_ONLY

`Crunchyroll → SONY`, `DMMTV → DMM`, `ESPN → Disney`, `GitHub → Microsoft`, `HBOMax → WarnerBrosDiscovery`, `HOYTV → iCABLE`, `HamiVideo → ChunghwaTelecom`, `Hulu → Disney`, `KKBOX → KKCompany`, `LinkedIn → Microsoft`, `MangoTV → MangoSuperMedia`, `Migu → ChinaMobile`, `Niconico → Kadokawa`, `Pandora → SiriusXM`, `PlayStation → SONY`, `RedBullTV → RedBull`, `SlingTV → EchoStar`, `TIDAL → Block`, `TMDB → Xperi`, `Tubi → Fox`, `UNEXT → UNEXTHoldings`, `VideoMarket → PLAY`, `WSJ → NewsCorp`, `Weibo → SINA`, `Youku → Alibaba`, `dAnimeStore → NTTDocomo`, `iQIYI → Baidu`, `mora → SONY`

### DEVELOPER_PROVIDER_ONLY

`Doubao → ByteDance`, `GLM → ZhipuAI`, `Grok → SpaceXAI`, `KaraokeDAM → Daiichikosho`, `Kimi → MoonshotAI`, `Manus → ButterflyEffect`, `Steam → Valve`

### PLATFORM_RELATION_ONLY

*(none)*

### AMBIGUOUS

`AWS → Amazon`, `AliCloud → Alibaba`, `AliPay → Alibaba`, `AmazonAlexa → Amazon`, `AmazonMusic → Amazon`, `AppStore → Apple`, `AppleArcade → Apple`, `AppleBooks → Apple`, `AppleFitnessPlus → Apple`, `AppleMusic → Apple`, `AppleNewsPlus → Apple`, `AppleTV → Apple`, `Azure → Microsoft`, `BaiduNetdisk → Baidu`, `Bing → Microsoft`, `Copilot → Microsoft`, `DingTalk → Alibaba`, `Douyin → ByteDance`, `Facebook → Meta`, `Gmail → Google`, `GoogleAI → Google`, `GoogleDrive → Google`, `GoogleMaps → Google`, `GoogleNews → Google`, `GooglePhotos → Google`, `GooglePlay → Google`, `GoogleTranslate → Google`, `GoogleVoice → Google`, `Instagram → Facebook`, `Lark → ByteDance`, `Messenger → Facebook`, `MicrosoftStore → Microsoft`, `MusicBrainz → MetaBrainz`, `NetEaseCloudMusic → NetEase`, `NetEaseMail → NetEase`, `OneDrive → Microsoft`, `Outlook → Microsoft`, `PrimeVideo → Amazon`, `QQ → Tencent`, `QQMail → Tencent`, `QQMusic → Tencent`, `Quark → Alibaba`, `Qwen → Alibaba`, `SiriAI → Apple`, `Taobao → Alibaba`, `TencentVideo → Tencent`, `TestFlight → Apple`, `Threads → Facebook`, `Tieba → Baidu`, `TikTok → ByteDance`, `Twitch → Amazon`, `WeChat → Tencent`, `WeTV → Tencent`, `WhatsApp → Facebook`, `Xbox → Microsoft`, `YouTube → Google`, `YouTubeMusic → YouTube`, `discoveryPlus → WarnerBrosDiscovery`, `iCloud → Apple`, `iCloudPrivateRelay → iCloud`
