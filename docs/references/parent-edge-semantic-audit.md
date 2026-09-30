# Parent Edge Semantic Evidence Audit

> This document is a conservative architecture audit of every live `parent_brand` edge. It records whether the current repository evidence proves the Oasisic Brand/Product Hierarchy contract; it does not alter `config/brands.json`.

## Contract

`parent_brand` is valid only when the child is presented as a sub-brand/product brand under the immediate parent, or the parent is the direct brand umbrella. Corporate ownership, developer/provider status, platform hosting, and distribution are not sufficient by themselves.

## Results

| Classification | Count | Interpretation |
|---|---:|---|
| `BRAND_HIERARCHY_CONFIRMED` | 8 | Evidence currently supports a direct Brand/Product Hierarchy interpretation. |
| `CORPORATE_OWNERSHIP_ONLY` | 41 | Ownership/control/operation is evidenced, but direct Brand Hierarchy is not explicitly evidenced. |
| `DEVELOPER_PROVIDER_ONLY` | 8 | Developer/provider/operation is evidenced, but direct Brand Hierarchy is not explicitly evidenced. |
| `PLATFORM_RELATION_ONLY` | 0 | Platform/hosting/distribution only; none currently classified here. |
| `AMBIGUOUS` | 58 | Current row is generic or otherwise insufficient for a semantic closure claim. |
| **Total** | **115** | **All live edges extracted from `config/brands.json`.** |

## Architecture finding

**BLOCKER:** the previous methodology treated “全资或多数控股” as `CONFIRMED_PARENT`. That proves corporate control, not necessarily a direct Brand/Product Hierarchy relationship. The manifest therefore keeps ownership-only, developer/provider-only, and generic legacy rows open instead of silently upgrading them.

The current SSOT edges are intentionally unchanged in this audit. A future closure pass must either add edge-specific hierarchy evidence or explicitly adjudicate each open row.

**Grok note:** `Grok → SpaceXAI` remains the Oasisic SSOT decision, but the current evidence row proves SpaceXAI developer/provider and branding control, not an independently documented direct-brand-umbrella statement. It remains `DEVELOPER_PROVIDER_ONLY` and is an architecture review item.

### BRAND_HIERARCHY_CONFIRMED

`ApplePodcasts → Apple`, `ChinaMobileDisk → ChinaMobile`, `Kwai → Kuaishou`, `Mijia → Xiaomi`, `MusicBrainz → MetaBrainz`, `Peacock → NBCUniversal`, `Youku → Alibaba`, `discoveryPlus → WarnerBrosDiscovery`

### CORPORATE_OWNERSHIP_ONLY

`189 → ChinaTelecom`, `Crunchyroll → SONY`, `DMMTV → DMM`, `DisneyPlus → Disney`, `ESPN → Disney`, `F1TV → LibertyMedia`, `GitHub → Microsoft`, `HBOMax → WarnerBrosDiscovery`, `HOYTV → iCABLE`, `HamiVideo → ChunghwaTelecom`, `Hulu → Disney`, `KKBOX → KKCompany`, `KakaoTalk → Kakao`, `LinkedIn → Microsoft`, `MangoTV → MangoSuperMedia`, `Migu → ChinaMobile`, `MyVideo → TaiwanMobile`, `NBC → NBCUniversal`, `Niconico → Kadokawa`, `NowE → PCCW`, `Pandora → SiriusXM`, `ParamountPlus → Paramount`, `PlayStation → SONY`, `Poe → Quora`, `RakutenTV → Rakuten`, `RedBullTV → RedBull`, `SlingTV → EchoStar`, `Snapchat → Snap`, `TIDAL → Block`, `TMDB → Xperi`, `Tubi → Fox`, `UNEXT → UNEXTHoldings`, `VideoMarket → PLAY`, `Viu → PCCW`, `WSJ → NewsCorp`, `Weibo → SINA`, `dAnimeStore → NTTDocomo`, `friDayVideo → FarEasTone`, `iQIYI → Baidu`, `mora → SONY`, `myTVSUPER → TVB`

### DEVELOPER_PROVIDER_ONLY

`Doubao → ByteDance`, `GLM → ZhipuAI`, `Grok → SpaceXAI`, `KaraokeDAM → Daiichikosho`, `Kimi → MoonshotAI`, `Manus → ButterflyEffect`, `Pipixia → ByteDance`, `Steam → Valve`

### PLATFORM_RELATION_ONLY

*(none)*

### AMBIGUOUS

`AWS → Amazon`, `AliCloud → Alibaba`, `AliPay → Alibaba`, `AmazonAlexa → Amazon`, `AmazonMusic → Amazon`, `AppStore → Apple`, `AppleArcade → Apple`, `AppleBooks → Apple`, `AppleFitnessPlus → Apple`, `AppleMusic → Apple`, `AppleNewsPlus → Apple`, `AppleTV → Apple`, `Azure → Microsoft`, `BaiduNetdisk → Baidu`, `Bing → Microsoft`, `Copilot → Microsoft`, `DingTalk → Alibaba`, `Douyin → ByteDance`, `Facebook → Meta`, `Gmail → Google`, `GoogleAI → Google`, `GoogleDrive → Google`, `GoogleMaps → Google`, `GoogleNews → Google`, `GooglePhotos → Google`, `GooglePlay → Google`, `GoogleTranslate → Google`, `GoogleVoice → Google`, `Instagram → Facebook`, `Lark → ByteDance`, `Messenger → Facebook`, `MicrosoftStore → Microsoft`, `NetEaseCloudMusic → NetEase`, `NetEaseMail → NetEase`, `OneDrive → Microsoft`, `Outlook → Microsoft`, `PrimeVideo → Amazon`, `QQ → Tencent`, `QQMail → Tencent`, `QQMusic → Tencent`, `Quark → Alibaba`, `Qwen → Alibaba`, `SiriAI → Apple`, `Taobao → Alibaba`, `TencentVideo → Tencent`, `TestFlight → Apple`, `Threads → Facebook`, `Tieba → Baidu`, `TikTok → ByteDance`, `Twitch → Amazon`, `WeChat → Tencent`, `WeTV → Tencent`, `WhatsApp → Facebook`, `Xbox → Microsoft`, `YouTube → Google`, `YouTubeMusic → YouTube`, `iCloud → Apple`, `iCloudPrivateRelay → iCloud`
