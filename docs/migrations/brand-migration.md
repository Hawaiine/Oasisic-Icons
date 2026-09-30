# 品牌迁移记录 / Brand Migration

> 完整逐项迁移表（Old → New），含 Canonical 决策理由。URL 变化 = 路径变化，见「URL 迁移表」。
>
> **历史措辞说明**：本表早期行的「（X 仅记录 ownership）」是 2026-09 旧口径的残留描述，当时把
> corporate ownership 直接当作归属依据。2026-09-30 起 `parent_brand` 已收紧为**直接父品牌**
> 语义，实际归属一律以 `config/brands.json` 的 `parent_brand` 与
> `docs/references/brand-ownership-audit.md` 为准；本表该措辞仅为历史记录，不构成现状结论。

| Brand | 旧分类 | 新分类 | 旧路径 | 新路径 | 理由 |
|---|---|---|---|---|---|
| Manus | General | AI | `icons/General/Manus/Manus.png` | `icons/AI/Manus/Manus.png` | 独立 AI Agent（2026-07 腾讯财团回购 Meta 股份，恢复独立运营；非 Meta 生态） |
| Qwen | AI | Alibaba | `icons/AI/Qwen/Qwen.png` | `icons/Alibaba/Qwen/Qwen.png` | 阿里巴巴 AI 模型品牌（通义千问）；AI 属性经 tags 表达 |
| AliCloud | Drive | Alibaba | `icons/Drive/AliCloud/AliCloud.png` | `icons/Alibaba/AliCloud/AliCloud.png` | 阿里巴巴生态（云计算） |
| AliPay | Payment | Alibaba | `icons/Payment/AliPay/AliPay.png` | `icons/Alibaba/AliPay/AliPay.png` | 阿里巴巴生态（支付） |
| Alibaba | Shopping | Alibaba | `icons/Shopping/Alibaba/Alibaba.png` | `icons/Alibaba/Alibaba/Alibaba.png` | 阿里巴巴生态 |
| Taobao | Shopping | Alibaba | `icons/Shopping/Taobao/Taobao.png` | `icons/Alibaba/Taobao/Taobao.png` | 阿里巴巴生态（电商） |
| AmazonAlexa | AI | Amazon | `icons/AI/AmazonAlexa/AmazonAlexa.png` | `icons/Amazon/AmazonAlexa/AmazonAlexa.png` | Amazon 生态（智能音箱/AI 助手） |
| AWS | DevOps | Amazon | `icons/DevOps/AWS/AWS.png` | `icons/Amazon/AWS/AWS.png` | Amazon 生态（云计算） |
| Twitch | Game | Amazon | `icons/Game/Twitch/Twitch.png` | `icons/Amazon/Twitch/Twitch.png` | Amazon 100% 子公司（2014 收购，2026 现状确认）；游戏/直播属性经 tags 表达 |
| PrimeVideo | Media | Amazon | `icons/Media/PrimeVideo/PrimeVideo.png` | `icons/Amazon/PrimeVideo/PrimeVideo.png` | Amazon 生态（Prime 视频服务） |
| AmazonMusic | Music | Amazon | `icons/Music/AmazonMusic/AmazonMusic.png` | `icons/Amazon/AmazonMusic/AmazonMusic.png` | Amazon 生态（流媒体） |
| Amazon | Shopping | Amazon | `icons/Shopping/Amazon/Amazon.png` | `icons/Amazon/Amazon/Amazon.png` | Amazon 生态聚合 |
| Cloudflare | DevOps | Infrastructure | `icons/DevOps/Cloudflare/Cloudflare.png` | `icons/Infrastructure/Cloudflare/Cloudflare.png` | 云基础设施（CDN/安全） |
| Docker | DevOps | Infrastructure | `icons/DevOps/Docker/Docker.png` | `icons/Infrastructure/Docker/Docker.png` | 云基础设施（容器） |
| MikroTik | DevOps | Infrastructure | `icons/DevOps/MikroTik/MikroTik.png` | `icons/Infrastructure/MikroTik/MikroTik.png` | 网络基础设施 |
| OpenWrt | DevOps | Infrastructure | `icons/DevOps/OpenWrt/OpenWrt.png` | `icons/Infrastructure/OpenWrt/OpenWrt.png` | 网络基础设施（路由系统） |
| Oracle | DevOps | Infrastructure | `icons/DevOps/Oracle/Oracle.png` | `icons/Infrastructure/Oracle/Oracle.png` | 云基础设施（数据库/云） |
| Synology | DevOps | Infrastructure | `icons/DevOps/Synology/Synology.png` | `icons/Infrastructure/Synology/Synology.png` | 网络存储基础设施 |
| 115 | Drive | CloudStorage | `icons/Drive/115/115.png` | `icons/CloudStorage/115/115.png` | 云盘 |
| 123 | Drive | CloudStorage | `icons/Drive/123/123.png` | `icons/CloudStorage/123/123.png` | 云盘 |
| 189 | Drive | CloudStorage | `icons/Drive/189/189.png` | `icons/CloudStorage/189/189.png` | 云盘 |
| BaiduNetdisk | Drive | CloudStorage | `icons/Drive/BaiduNetdisk/BaiduNetdisk.png` | `icons/CloudStorage/BaiduNetdisk/BaiduNetdisk.png` | 云盘（Baidu 仅记录 ownership） |
| ChinaMobileDisk | Drive | CloudStorage | `icons/Drive/ChinaMobileDisk/ChinaMobileDisk.png` | `icons/CloudStorage/ChinaMobileDisk/ChinaMobileDisk.png` | 云盘（ChinaMobile 仅记录 ownership） |
| Dropbox | Drive | CloudStorage | `icons/Drive/Dropbox/Dropbox.png` | `icons/CloudStorage/Dropbox/Dropbox.png` | 云盘 |
| PikPak | Drive | CloudStorage | `icons/Drive/PikPak/PikPak.png` | `icons/CloudStorage/PikPak/PikPak.png` | 云盘 |
| Quark | Drive | CloudStorage | `icons/Drive/Quark/Quark.png` | `icons/CloudStorage/Quark/Quark.png` | 云盘（夸克，Baidu 仅记录 ownership） |
| NetEaseMail | General | Communication | `icons/General/NetEaseMail/NetEaseMail.png` | `icons/Communication/NetEaseMail/NetEaseMail.png` | 邮件通讯（NetEase ownership 记录） |
| DingTalk | Social | Communication | `icons/Social/DingTalk/DingTalk.png` | `icons/Communication/DingTalk/DingTalk.png` | 团队协作 |
| Discord | Social | Communication | `icons/Social/Discord/Discord.png` | `icons/Communication/Discord/Discord.png` | 即时通讯/社区 |
| KakaoTalk | Social | Communication | `icons/Social/KakaoTalk/KakaoTalk.png` | `icons/Communication/KakaoTalk/KakaoTalk.png` | 即时通讯 |
| LINE | Social | Communication | `icons/Social/LINE/LINE.png` | `icons/Communication/LINE/LINE.png` | 即时通讯 |
| Messenger | Social | Communication | `icons/Social/Messenger/Messenger.png` | `icons/Communication/Messenger/Messenger.png` | 即时通讯（Meta ownership 记录） |
| Skype | Social | Communication | `icons/Social/Skype/Skype.png` | `icons/Communication/Skype/Skype.png` | 即时通讯 |
| Snapchat | Social | Communication | `icons/Social/Snapchat/Snapchat.png` | `icons/Communication/Snapchat/Snapchat.png` | 即时通讯（Meta ownership 记录） |
| Telegram | Social | Communication | `icons/Social/Telegram/Telegram.png` | `icons/Communication/Telegram/Telegram.png` | 即时通讯 |
| WhatsApp | Social | Communication | `icons/Social/WhatsApp/WhatsApp.png` | `icons/Communication/WhatsApp/WhatsApp.png` | 即时通讯 |
| Lark | Tool | Communication | `icons/Tool/Lark/Lark.png` | `icons/Communication/Lark/Lark.png` | 团队协作（ByteDance ownership 记录） |
| GitHub | Tool | Development | `icons/Tool/GitHub/GitHub.png` | `icons/Development/GitHub/GitHub.png` | 开发者平台 |
| Adobe | Development | Utilities | `icons/Development/Adobe/Adobe.png` | `icons/Utilities/Adobe/Adobe.png` | 创意软件套件，非开发工具 → Utilities |
| Duolingo | Tool | Education | `icons/Tool/Duolingo/Duolingo.png` | `icons/Education/Duolingo/Duolingo.png` | 教育平台 |
| Z-Library | Tool | Education | `icons/Tool/Z-Library/Z-Library.png` | `icons/Education/Z-Library/Z-Library.png` | 教育/文献资源 |
| Honor | Telecom | Hardware | `icons/Telecom/Honor/Honor.png` | `icons/Hardware/Honor/Honor.png` | 手机品牌（Huawei 分家，独立品牌） |
| Huawei | Telecom | Hardware | `icons/Telecom/Huawei/Huawei.png` | `icons/Hardware/Huawei/Huawei.png` | 消费电子品牌 |
| LG | Telecom | Hardware | `icons/Telecom/LG/LG.png` | `icons/Hardware/LG/LG.png` | 消费电子品牌 |
| OPPO | Telecom | Hardware | `icons/Telecom/OPPO/OPPO.png` | `icons/Hardware/OPPO/OPPO.png` | 手机品牌 |
| SONY | Telecom | Hardware | `icons/Telecom/SONY/SONY.png` | `icons/Hardware/SONY/SONY.png` | 消费电子品牌 |
| Samsung | Telecom | Hardware | `icons/Telecom/Samsung/Samsung.png` | `icons/Hardware/Samsung/Samsung.png` | 手机/硬件品牌（非运营商） |
| Xiaomi | Telecom | Hardware | `icons/Telecom/Xiaomi/Xiaomi.png` | `icons/Hardware/Xiaomi/Xiaomi.png` | 消费电子品牌 |
| vivo | Telecom | Hardware | `icons/Telecom/vivo/vivo.png` | `icons/Hardware/vivo/vivo.png` | 手机品牌 |
| DJI | Tool | Hardware | `icons/Tool/DJI/DJI.png` | `icons/Hardware/DJI/DJI.png` | 消费无人机/硬件 |
| Keep | Tool | Health | `icons/Tool/Keep/Keep.png` | `icons/Health/Keep/Keep.png` | 健康/运动 App |
| Aqara | Telecom | Home | `icons/Telecom/Aqara/Aqara.png` | `icons/Home/Aqara/Aqara.png` | 智能家居 |
| Mijia | Telecom | Home | `icons/Telecom/Mijia/Mijia.png` | `icons/Home/Mijia/Mijia.png` | 智能家居（Xiaomi 生态，ownership 记录） |
| BBC | Social | Media | `icons/Social/BBC/BBC.png` | `icons/Media/BBC/BBC.png` | 新闻媒体/流媒体 |
| TMDB | Tool | Media | `icons/Tool/TMDB/TMDB.png` | `icons/Media/TMDB/TMDB.png` | 影视数据库（媒体） |
| Azure | DevOps | Microsoft | `icons/DevOps/Azure/Azure.png` | `icons/Microsoft/Azure/Azure.png` | 微软生态（Azure 云） |
| KKBOX | Media | Music | `icons/Media/KKBOX/KKBOX.png` | `icons/Music/KKBOX/KKBOX.png` | 音乐流媒体 |
| Douyin | Media | Social | `icons/Media/Douyin/Douyin.png` | `icons/Social/Douyin/Douyin.png` | 短视频社交（字节，与 TikTok 同产品族统一归 Social） |
| GeneralAI | AI | System | `icons/AI/GeneralAI/GeneralAI.png` | `icons/System/GeneralAI/GeneralAI.png` | 通用 AI 策略图标（无品牌） |
| Game | Game | System | `icons/Game/Game/Game.png` | `icons/System/Game/Game.png` | 通用游戏策略图标（无品牌） |
| AD | General | System | `icons/General/AD/AD.png` | `icons/System/AD/AD.png` | 广告拦截策略图标 |
| Area | General | System | `icons/General/Area/Area.png` | `icons/System/Area/Area.png` | 区域策略图标 |
| Auto | General | System | `icons/General/Auto/Auto.png` | `icons/System/Auto/Auto.png` | 自动选择策略图标 |
| Blacklist | General | System | `icons/General/Blacklist/Blacklist.png` | `icons/System/Blacklist/Blacklist.png` | 黑名单策略图标 |
| Bot | General | System | `icons/General/Bot/Bot.png` | `icons/System/Bot/Bot.png` | Bot 拦截策略图标 |
| Direct | General | System | `icons/General/Direct/Direct.png` | `icons/System/Direct/Direct.png` | 直连策略图标 |
| Final | General | System | `icons/General/Final/Final.png` | `icons/System/Final/Final.png` | 最终节点策略图标 |
| Global | General | System | `icons/General/Global/Global.png` | `icons/System/Global/Global.png` | 全球策略图标 |
| Lightning | General | System | `icons/General/Lightning/Lightning.png` | `icons/System/Lightning/Lightning.png` | 快线策略图标 |
| Mail | General | System | `icons/General/Mail/Mail.png` | `icons/System/Mail/Mail.png` | 邮件策略图标 |
| Play | General | System | `icons/General/Play/Play.png` | `icons/System/Play/Play.png` | 播放策略图标 |
| Proxy | General | System | `icons/General/Proxy/Proxy.png` | `icons/System/Proxy/Proxy.png` | 代理策略图标 |
| Reject | General | System | `icons/General/Reject/Reject.png` | `icons/System/Reject/Reject.png` | 拒绝策略图标 |
| SSID | General | System | `icons/General/SSID/SSID.png` | `icons/System/SSID/SSID.png` | Wi-Fi 策略图标 |
| Search | General | System | `icons/General/Search/Search.png` | `icons/System/Search/Search.png` | 搜索策略图标 |
| Traffic | General | System | `icons/General/Traffic/Traffic.png` | `icons/System/Traffic/Traffic.png` | 流量策略图标 |
| URL | General | System | `icons/General/URL/URL.png` | `icons/System/URL/URL.png` | URL 策略图标 |
| QQMail | General | Tencent | `icons/General/QQMail/QQMail.png` | `icons/Tencent/QQMail/QQMail.png` | 腾讯生态（QQ 邮箱） |
| TencentVideo | Media | Tencent | `icons/Media/TencentVideo/TencentVideo.png` | `icons/Tencent/TencentVideo/TencentVideo.png` | 腾讯生态（腾讯视频） |
| WeTV | Media | Tencent | `icons/Media/WeTV/WeTV.png` | `icons/Tencent/WeTV/WeTV.png` | 腾讯生态（WeTV 国际版） |
| QQMusic | Music | Tencent | `icons/Music/QQMusic/QQMusic.png` | `icons/Tencent/QQMusic/QQMusic.png` | 腾讯生态（QQ 音乐） |
| QQ | Social | Tencent | `icons/Social/QQ/QQ.png` | `icons/Tencent/QQ/QQ.png` | 腾讯生态（QQ） |
| Tencent | Social | Tencent | `icons/Social/Tencent/Tencent.png` | `icons/Tencent/Tencent/Tencent.png` | 腾讯生态 |
| WeChat | Social | Tencent | `icons/Social/WeChat/WeChat.png` | `icons/Tencent/WeChat/WeChat.png` | 腾讯生态（微信） |
| Airport | Tool | System | `icons/Tool/Airport/Airport.png` | `icons/System/Airport/Airport.png` | 通用机场/机场规则组语义，非具体机场品牌 → System |
| DiDi | Tool | Transport | `icons/Tool/DiDi/DiDi.png` | `icons/Transport/DiDi/DiDi.png` | 出行平台（滴滴） |
| SF-Express | Tool | Transport | `icons/Tool/SF-Express/SF-Express.png` | `icons/Transport/SF-Express/SF-Express.png` | 快递物流 |
| Uber | Tool | Transport | `icons/Tool/Uber/Uber.png` | `icons/Transport/Uber/Uber.png` | 出行平台 |
| Baidu | General | Utilities | `icons/General/Baidu/Baidu.png` | `icons/Utilities/Baidu/Baidu.png` | 通用服务/搜索引擎 |
| MetaBrainz | General | Utilities | `icons/General/MetaBrainz/MetaBrainz.png` | `icons/Utilities/MetaBrainz/MetaBrainz.png` | 音乐元数据（MusicBrainz 母公司） |
| Wikipedia | Social | Utilities | `icons/Social/Wikipedia/Wikipedia.png` | `icons/Utilities/Wikipedia/Wikipedia.png` | 百科/参考 |
| 1Password | Tool | Utilities | `icons/Tool/1Password/1Password.png` | `icons/Utilities/1Password/1Password.png` | 密码管理工具 |
| AdGuard | Tool | Utilities | `icons/Tool/AdGuard/AdGuard.png` | `icons/Utilities/AdGuard/AdGuard.png` | 广告拦截工具 |
| Notion | Tool | Utilities | `icons/Tool/Notion/Notion.png` | `icons/Utilities/Notion/Notion.png` | 笔记/生产力工具 |
| Obsidian | Tool | Utilities | `icons/Tool/Obsidian/Obsidian.png` | `icons/Utilities/Obsidian/Obsidian.png` | 笔记/生产力工具 |
| Speedtest | Tool | Utilities | `icons/Tool/Speedtest/Speedtest.png` | `icons/Utilities/Speedtest/Speedtest.png` | 网速测试工具 |
| Zoom | Tool | Utilities | `icons/Tool/Zoom/Zoom.png` | `icons/Utilities/Zoom/Zoom.png` | 视频会议工具 |

共 **96** 个品牌迁移（另有未列出的品牌分类未变）。
## 本轮增量：全库生态归属审计（2026-09-30）

> 25 个 Canonical 迁移，全部为 pure move（git R100，SHA-256 不变）。
>
> **历史记录**：本表记录**当时**状态。其中 `X` 行（`xAI 子公司`）已被同文件下节
> 「Final Seal Review 增量」修订——`X` 现为独立平台品牌（无 `parent_brand`），`SpaceXAI`
> 亦由生态降为 `product_brand`。现状一律以 `config/brands.json` 为准。

| Brand | 旧分类 | 新分类 | 旧路径 | 新路径 | 理由 |
|---|---|---|---|---|---|
| ChinaMobile | Telecom | ChinaMobile | `icons/Telecom/ChinaMobile/ChinaMobile.png` | `icons/ChinaMobile/ChinaMobile/ChinaMobile.png` | 中国移动生态根品牌（ChinaMobileDisk + 咪咕 ≥2） |
| ChinaMobileDisk | CloudStorage | ChinaMobile | `icons/CloudStorage/ChinaMobileDisk/ChinaMobileDisk.png` | `icons/ChinaMobile/ChinaMobileDisk/ChinaMobileDisk.png` | 中国移动自有云盘；ChinaMobile 生态 |
| Crunchyroll | Media | SONY | `icons/Media/Crunchyroll/Crunchyroll.png` | `icons/SONY/Crunchyroll/Crunchyroll.png` | Sony Pictures / Aniplex 全资；SONY 生态 |
| discoveryPlus | Media | WarnerBrosDiscovery | `icons/Media/discoveryPlus/discoveryPlus.png` | `icons/WarnerBrosDiscovery/discoveryPlus/discoveryPlus.png` | WBD「Discovery Global」业务；新建 WarnerBrosDiscovery 生态 |
| DisneyPlus | Media | Disney | `icons/Media/DisneyPlus/DisneyPlus.png` | `icons/Disney/DisneyPlus/DisneyPlus.png` | Disney 全资流媒体；新建 Disney 生态（3 children） |
| Doubao | AI | ByteDance | `icons/AI/Doubao/Doubao.png` | `icons/ByteDance/Doubao/Doubao.png` | 字节跳动 AI 助手；ByteDance 生态 |
| ESPN | Media | Disney | `icons/Media/ESPN/ESPN.png` | `icons/Disney/ESPN/ESPN.png` | Disney 持 80%（Hearst 20%）；新建 Disney 生态 |
| GitHub | Development | Microsoft | `icons/Development/GitHub/GitHub.png` | `icons/Microsoft/GitHub/GitHub.png` | Microsoft 全资子公司（2018 收购）；child ≥2 归入 Microsoft 生态 |
| Grok | AI | xAI | `icons/AI/Grok/Grok.png` | `icons/xAI/Grok/Grok.png` | xAI 开发（xAI 2026-02 起为 SpaceX 全资子公司）；新建 xAI 生态 |
| HBOMax | Media | WarnerBrosDiscovery | `icons/Media/HBOMax/HBOMax.png` | `icons/WarnerBrosDiscovery/HBOMax/HBOMax.png` | Warner Bros. Discovery 流媒体；新建 WarnerBrosDiscovery 生态（2 children） |
| Hulu | Media | Disney | `icons/Media/Hulu/Hulu.png` | `icons/Disney/Hulu/Hulu.png` | Disney 100% 持股（2025 收购 Comcast 剩余股份）；新建 Disney 生态 |
| iQIYI | Media | Baidu | `icons/Media/iQIYI/iQIYI.png` | `icons/Baidu/iQIYI/iQIYI.png` | 百度控股（多数投票权）；Baidu 生态 |
| LinkedIn | Social | Microsoft | `icons/Social/LinkedIn/LinkedIn.png` | `icons/Microsoft/LinkedIn/LinkedIn.png` | Microsoft 全资子公司（2016 收购）；child ≥2 归入 Microsoft 生态 |
| Migu | Media | ChinaMobile | `icons/Media/Migu/Migu.png` | `icons/ChinaMobile/Migu/Migu.png` | 咪咕文化科技为中国移动全资子公司；ChinaMobile 生态 |
| mora | Music | SONY | `icons/Music/mora/mora.png` | `icons/SONY/mora/mora.png` | Sony Music Solutions（索尼音乐娱乐日本）；SONY 生态 |
| NBC | Media | NBCUniversal | `icons/Media/NBC/NBC.png` | `icons/NBCUniversal/NBC/NBC.png` | NBCUniversal 旗下电视网；新建 NBCUniversal 生态（2 children） |
| NowE | Media | PCCW | `icons/Media/NowE/NowE.png` | `icons/PCCW/NowE/NowE.png` | PCCW / HKT 旗下；新建 PCCW 生态 |
| Peacock | Media | NBCUniversal | `icons/Media/PeacockTV/PeacockTV.png` | `icons/NBCUniversal/Peacock/Peacock.png` | NBCUniversal（Comcast）流媒体；新建 NBCUniversal 生态。2026-09-30 技术 ID `PeacockTV` → `Peacock`（目录/文件名同步，纯迁移 SHA 不变） |
| Pipixia | Social | ByteDance | `icons/Social/Pipixia/Pipixia.png` | `icons/ByteDance/Pipixia/Pipixia.png` | 字节跳动旗下短视频社区；ByteDance 生态 |
| PlayStation | Game | SONY | `icons/Game/PlayStation/PlayStation.png` | `icons/SONY/PlayStation/PlayStation.png` | Sony Interactive Entertainment（索尼全资）；SONY 生态 |
| ApplePodcasts | Media | Apple | `icons/Media/Podcasts/Podcasts.png` | `icons/Apple/ApplePodcasts/ApplePodcasts.png` | Apple Podcasts（Apple 自有应用）；Apple 生态。2026-09-30 会话按 Apple 子品牌命名规范重命名 Podcasts → ApplePodcasts |
| SONY | Hardware | SONY | `icons/Hardware/SONY/SONY.png` | `icons/SONY/SONY/SONY.png` | 索尼生态根品牌（PlayStation + Crunchyroll + mora ≥2）；id 保持 `SONY`，分类显示名规范为 Sony |
| Viu | Media | PCCW | `icons/Media/Viu/Viu.png` | `icons/PCCW/Viu/Viu.png` | PCCW Media Group 旗下 OTT；新建 PCCW 生态（2 children） |
| X | Social | xAI | `icons/Social/X/X.png` | `icons/xAI/X/X.png` | xAI 子公司（2025-03 xAI 收购 X Corp）；新建 xAI 生态（2 children） |
| Youku | Media | Alibaba | `icons/Media/Youku/Youku.png` | `icons/Alibaba/Youku/Youku.png` | 阿里巴巴集团在线视频平台；Alibaba 生态 |

## 本轮增量：会话新增品牌（2026-09-30）

> 3 个新增品牌（图标由用户提供，按规范 512×512 RGBA r=115 入库）+ 1 个重命名（Podcasts → ApplePodcasts，pure rename，git R100，SHA-256 不变）。

| Brand | 变更 | 路径 | 理由 |
|---|---|---|---|
| ApplePodcasts | 重命名（原 Podcasts） | `icons/Apple/ApplePodcasts/ApplePodcasts.png` | Apple 子品牌统一 `Apple` 前缀命名规范（对齐 AppleBooks/AppleMusic/AppleTV）；display_name 补全为「Apple Podcasts」 |
| Xiaoyuzhou | 新增（Media） | `icons/Media/Xiaoyuzhou/Xiaoyuzhou.png` | 小宇宙（Xiaoyuzhou）播客 App，用户提供的官方图标 |
| Proxmox | 新增（Infrastructure） | `icons/Infrastructure/Proxmox/Proxmox.png` | Proxmox 开源虚拟化平台，用户提供的官方图标 |
| SINA | 新增（Social） | `icons/Social/SINA/SINA.png` | 新浪（Sina Corporation）公司品牌，用户提供的官方图标；白名单 `Sina` 移除，子品牌 Weibo 的 parent_brand 指向 SINA |
| CATCHPLAYPlus | 重命名（原 CATCHPLAY） | `icons/Media/CATCHPLAY/CATCHPLAY.png` | `icons/Media/CATCHPLAYPlus/CATCHPLAYPlus.png` | 按全库 Plus 品牌命名惯例对齐（id/目录/文件名）；display_name 仍为「CATCHPLAY+」 |

## Final Seal Review 增量（2026-09-30）：X / Grok / SpaceXAI 关系厘清

> 四个品牌变更 + 1 个公司品牌降级，全部为 pure move（git R100，SHA-256 不变）。
> 决策依据：**官方当前证据**（SpaceXAI 官方 Terms / Privacy Policy）优先于历史 metadata。

| Brand | 旧分类 | 新分类 | 旧路径 | 新路径 | 理由 |
|---|---|---|---|---|---|
| SpaceXAI | SpaceXAI | AI | `icons/SpaceXAI/SpaceXAI/SpaceXAI.png` | `icons/AI/SpaceXAI/SpaceXAI.png` | 2026-07-06 官方**品牌标识**由 xAI 更名 SpaceXAI（非新增品牌）；canonical descendants = 1（仅 Grok）< 2 → **降为 product_brand**（公司品牌），不构成独立生态 |
| Grok | SpaceXAI | AI | `icons/SpaceXAI/Grok/Grok.png` | `icons/AI/Grok/Grok.png` | Grok 为 SpaceXAI 开发的 AI 产品（官方 Terms）；`parent_brand = SpaceXAI` 保留；分类回到功能分类 AI |
| X | SpaceXAI | Social | `icons/SpaceXAI/X/X.png` | `icons/Social/X/X.png` | **移除 `parent_brand`**：SpaceXAI 官方 Privacy Policy 明确「SpaceXAI is a separate company from X Corp.」，SpaceXAI 官方产品清单不含 X → X 为独立平台品牌，**不以 corporate ownership 推导品牌父级** |
| SpaceX（未入库） | — | — | — | — | **Corporate Owner only**：不建 `icons/SpaceX/`、不设 `parent_brand = SpaceX`；仅记录于归属审计 |

**口径说明**：`xAI → SpaceXAI` 属**品牌标识（brand identity）更名**——官方品牌层面证据为 2026-07-06
`@SpaceXAI` 账号发布「We are now @SpaceXAI」+ 新 logo + 官方页标题/页脚（Business Insider /
Yahoo Finance 同日报道）。**「法律实体更名」在 SEC / 公司登记层面未获正式文件证据，本文件不作此断言**；
官方 Terms 仅证明当前实体名为「SpaceXAI LLC」（Nevada），不足以推出更名日期。
