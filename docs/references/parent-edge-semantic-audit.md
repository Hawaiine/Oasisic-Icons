# Parent Edge Semantic Evidence Audit

> 本文档由 `scripts/gen-parent-edge-evidence.py` 生成，与 `config/parent-edge-evidence.json` 同源，请勿手工编辑。它是对全部 live `parent_brand` edge 的**关系类型分级**，不修改 `config/brands.json`。

## 能力边界 / Capability boundary

本分级是 **evidence-text triage**：只回答「审计文档 §7 那一行证据文字描述的是哪一类关系」，
**不回答**「现实世界是否真的如此」。`keyword hit ≠ relationship proof`。

**自证循环风险（已记录，未消除）**：证据文字来自 `brand-ownership-audit.md` 这一人工研究摘要，生成器不重新取证，无法独立验证该摘要。消除风险需逐边补 `source.url` + 人工复核；当前 **0 / 115** 条 edge 记录了 source URL。

## Decision rules（按顺序，先命中先判定）

| # | Rule | relation_type | parent_brand_validity | Condition |
|---:|---|---|---|---|
| 1 | `R1_GENERIC_RESTATEMENT` | `UNKNOWN` | `OPEN_REVIEW` | evidence is the generic restatement '既有 parent_brand 关系仍成立' |
| 2 | `R2_DEVELOPER_PROVIDER` | `DEVELOPER_PROVIDER` | `OPEN_REVIEW` | evidence contains developer/provider language (开发/推出) |
| 3 | `R3_CORPORATE_OWNERSHIP` | `CORPORATE_OWNERSHIP` | `OPEN_REVIEW` | evidence contains ownership/control language (旗下/全资/多数/控股/收购/持有/股权/子公司/归属/集团/属/运营) |
| 4 | `R4_BRAND_UMBRELLA` | `BRAND_HIERARCHY` | `CONFIRMED` | evidence contains brand-umbrella language (品牌/自有应用/自有产品/产品/服务) and no ownership/control or developer term |
| 5 | `R5_PLATFORM_INTEGRATION` | `PLATFORM_INTEGRATION` | `OPEN_REVIEW` | evidence contains platform-access language ('平台使用' / '可通过 X' / 'available on' / '平台可访问') and no other signal |
| 6 | `R6_DEFAULT` | `UNKNOWN` | `OPEN_REVIEW` | no rule matched |

> **R3 必须在 R4 之前**：只凭「旗下」「集团」等归属措辞不能证明 direct brand umbrella。
> 旧版把「旗下」当作伞状证据，曾把 `F1TV → LibertyMedia`、`NowE → PCCW` 等纯归属关系误判为品牌层级，本版已修正。
> 同理，开发/提供方措辞（R2）先于平台措辞（R5）：Grok 的证据同时含两者，旧版整条判成 platform，掩盖了 developer 事实。

## relation_type 分布

| relation_type | Count | Interpretation |
|---|---:|---|
| `BRAND_HIERARCHY` | 5 | 证据文字以品牌伞状措辞描述子品牌/产品 → 当前契约下判 CONFIRMED。 |
| `CORPORATE_OWNERSHIP` | 42 | 仅归属/控制/运营措辞 → 不足以证明 direct brand umbrella，OPEN_REVIEW。 |
| `DEVELOPER_PROVIDER` | 8 | 仅开发/提供方措辞 → 不足以证明 direct brand umbrella，OPEN_REVIEW。 |
| `PLATFORM_INTEGRATION` | 0 | 平台可访问/托管 → 不是 parent_brand，OPEN_REVIEW。 |
| `UNKNOWN` | 60 | 泛化复述或无法归类 → OPEN_REVIEW。 |
| **Total** | **115** | **All live edges extracted from `config/brands.json`.** |

## parent_brand_validity 分布

| validity | Count |
|---|---:|
| `CONFIRMED` | 5 |
| `OPEN_REVIEW` | 110 |
| `REJECTED` | 0 |
| **Total** | **115** |

> `CONFIRMED` 只在 `relation_type = BRAND_HIERARCHY` 时给出，即证据文字本身已具备品牌伞状措辞。
> 这不等于 primary-source 已闭合：全部 edge 的 `source.url` 仍为 `NOT_RECORDED`。

## Architecture finding

**BLOCKER A（未闭合）**：115 条 edge 的 `relation_type` 来自**证据文字**而非独立 primary source，分类可能受关键字影响。真正闭合需逐边补 `source.url` 并人工裁决；本轮 0/115 已记录 URL。

**未修改 SSOT**：`config/brands.json` 的 115 条 `parent_brand` 本轮未被修改。

### BRAND_HIERARCHY

`ApplePodcasts → Apple`, `ChinaMobileDisk → ChinaMobile`, `Kwai → Kuaishou`, `Mijia → Xiaomi`, `Peacock → NBCUniversal`

### CORPORATE_OWNERSHIP

`189 → ChinaTelecom`, `Crunchyroll → SONY`, `DMMTV → DMM`, `DisneyPlus → Disney`, `ESPN → Disney`, `F1TV → LibertyMedia`, `GitHub → Microsoft`, `HBOMax → WarnerBrosDiscovery`, `HOYTV → iCABLE`, `HamiVideo → ChunghwaTelecom`, `Hulu → Disney`, `KKBOX → KKCompany`, `KakaoTalk → Kakao`, `LinkedIn → Microsoft`, `MangoTV → MangoSuperMedia`, `Migu → ChinaMobile`, `MyVideo → TaiwanMobile`, `NBC → NBCUniversal`, `Niconico → Kadokawa`, `NowE → PCCW`, `Pandora → SiriusXM`, `ParamountPlus → Paramount`, `PlayStation → SONY`, `Poe → Quora`, `RakutenTV → Rakuten`, `RedBullTV → RedBull`, `SlingTV → EchoStar`, `Snapchat → Snap`, `TIDAL → Block`, `TMDB → Xperi`, `Tubi → Fox`, `UNEXT → UNEXTHoldings`, `VideoMarket → PLAY`, `Viu → PCCW`, `WSJ → NewsCorp`, `Weibo → SINA`, `Youku → Alibaba`, `dAnimeStore → NTTDocomo`, `friDayVideo → FarEasTone`, `iQIYI → Baidu`, `mora → SONY`, `myTVSUPER → TVB`

### DEVELOPER_PROVIDER

`Doubao → ByteDance`, `GLM → ZhipuAI`, `Grok → SpaceXAI`, `KaraokeDAM → Daiichikosho`, `Kimi → MoonshotAI`, `Manus → ButterflyEffect`, `Pipixia → ByteDance`, `Steam → Valve`

### PLATFORM_INTEGRATION

*(none)*

### UNKNOWN

`AWS → Amazon`, `AliCloud → Alibaba`, `AliPay → Alibaba`, `AmazonAlexa → Amazon`, `AmazonMusic → Amazon`, `AppStore → Apple`, `AppleArcade → Apple`, `AppleBooks → Apple`, `AppleFitnessPlus → Apple`, `AppleMusic → Apple`, `AppleNewsPlus → Apple`, `AppleTV → Apple`, `Azure → Microsoft`, `BaiduNetdisk → Baidu`, `Bing → Microsoft`, `Copilot → Microsoft`, `DingTalk → Alibaba`, `Douyin → ByteDance`, `Facebook → Meta`, `Gmail → Google`, `GoogleAI → Google`, `GoogleDrive → Google`, `GoogleMaps → Google`, `GoogleNews → Google`, `GooglePhotos → Google`, `GooglePlay → Google`, `GoogleTranslate → Google`, `GoogleVoice → Google`, `Instagram → Facebook`, `Lark → ByteDance`, `Messenger → Facebook`, `MicrosoftStore → Microsoft`, `MusicBrainz → MetaBrainz`, `NetEaseCloudMusic → NetEase`, `NetEaseMail → NetEase`, `OneDrive → Microsoft`, `Outlook → Microsoft`, `PrimeVideo → Amazon`, `QQ → Tencent`, `QQMail → Tencent`, `QQMusic → Tencent`, `Quark → Alibaba`, `Qwen → Alibaba`, `SiriAI → Apple`, `Taobao → Alibaba`, `TencentVideo → Tencent`, `TestFlight → Apple`, `Threads → Facebook`, `Tieba → Baidu`, `TikTok → ByteDance`, `Twitch → Amazon`, `WeChat → Tencent`, `WeTV → Tencent`, `WhatsApp → Facebook`, `Xbox → Microsoft`, `YouTube → Google`, `YouTubeMusic → YouTube`, `discoveryPlus → WarnerBrosDiscovery`, `iCloud → Apple`, `iCloudPrivateRelay → iCloud`
