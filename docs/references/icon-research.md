# 代理工具策略组图标资源参考

> 整理目标：为 [Hawaiine/PolicyIcons](https://github.com/Hawaiine/PolicyIcons) 项目提供开源图标资源、分类体系与常见品牌清单的参考。
>
> 适用工具：Surge / Clash / Loon / Quantumult X / Stash / Egern / sing-box 等。

---

## 1. 知名开源图标集合

### 1.1 Koolson / Qure
| 项目 | 地址 |
|------|------|
| GitHub | https://github.com/Koolson/Qure |
| jsDelivr CDN | https://cdn.jsdelivr.net/gh/Koolson/Qure |
| mini 订阅推荐 | `https://raw.githubusercontent.com/Koolson/Qure/master/Other/Quremini.json` |
| Color 订阅推荐 | `https://raw.githubusercontent.com/Koolson/Qure/master/Other/QureColor.json` |

- 定位：专为 Quantumult X 策略组设计的图标集，已被 Surge / Loon / Clash 等广泛采用。
- 规模：`IconSet/mini/`、`IconSet/Color/` 目录包含 500+ PNG 图标。
- 风格：mini 为纯白简洁风；Color 为彩色品牌风。
- 典型分类目录：
  - **Default**：Direct、Proxy、Reject、Static、Round Robin、SSID、Available
  - **Common**：Back、Final、ForeignMedia、DomesticMedia、HKMTMedia、Domestic、Global、Auto
  - **Inhibition**：Hijacking、AdWhite、AdBlack、Advertising
  - **Service**：Cloudflare、Apple、Google、Mail、Microsoft、Windows、Yahoo
  - **App**：Telegram、Telegram X、Speedtest、Spark、OneDrive、PayPal、Apple News、Twitter、Facebook、Instagram
  - **Area**：Russia、Singapore、United States、China、Japan、Korea、Hong Kong、Macao、United Kingdom、Canada、Turkey、Taiwan 等
  - **Media**：YouTube、bilibili、Netflix、Disney+、Spotify、TikTok、Hulu、TVB、Twitch、Vimeo、Prime Video、iQIYI、Pandora、Deezer、HBO、BBC iPlayer、FOX、ESPN+、DAZN、KKBOX、TIDAL、ViuTV、PBS 等
  - **Server**：IPLC、BGP、CN2 GIA、CN2 GT、Oracle、BBTEC、DMIT、SoftBank、KT、IIJ、SK、HiNet、NTT、PCCW、HKT、HGC、Tencent Cloud、Azure、AWS、GCP、Alibaba Cloud、Baidu Cloud 等

### 1.2 Orz-3 / mini
| 项目 | 地址 |
|------|------|
| GitHub | https://github.com/Orz-3/mini |
| Color 示例 | `https://raw.githubusercontent.com/Orz-3/mini/master/Color/` |
| 国家/地区图标 | `https://raw.githubusercontent.com/Orz-3/mini/master/` |

- 定位：为 Quantumult X 1.07 机场订阅 `img-url` 特性而生，后扩展为跨项目通用图标集。
- 特点：包含机场订阅图标、Task 图标、节点地区图标、策略组图标等。
- 广泛被 `Toperlock/Quantumult`、`czy13724/Quantumult-X` 等主流配置引用。

### 1.3 Semporia / Quantumult-X
| 项目 | 地址 |
|------|------|
| GitHub | https://github.com/Semporia/Quantumult-X |

- 定位：Bubble icon + Filter + Rewrite + Scripts。
- 适用：Quantumult X / Surge / Loon。
- 特点：提供泡泡风/Bubble 风格策略组图标，常见于圈 X 配置分享。

### 1.4 Repcz / Tool
| 项目 | 地址 |
|------|------|
| GitHub | https://github.com/Repcz/Tool |
| 官网 | https://repcz.github.io/Tool |

- 定位：多平台自动化配置构建项目。
- 支持平台：Egern / Loon / QuantumultX / Shadowrocket / Stash / Surfboard / Surge / mihomo / sing-box。
- 特点：CI 自动构建，图标资源分散在对应平台目录下，是规则集+配置+图标一体化参考。

### 1.5 fmz200 / wool_scripts
| 项目 | 地址 |
|------|------|
| GitHub | https://github.com/fmz200/wool_scripts |

- 定位：收集 Loon、Surge、QuantumultX、ShadowRocket、Egern 的配置与去广告规则。
- 图标路径：`icons/apps/`、`icons/airport/`、`icons/Twoandz9/` 等。
- 典型图标：AliYunDrive、pinduoduo、DegYax、iqZone、v2tun、Xray、BoxJS、Apple SpringLoaded 等。

### 1.6 limbopro / Zure（Qure 扩展）
| 项目 | 地址 |
|------|------|
| GitHub | https://github.com/limbopro/Zure |
| 配置示例 | https://github.com/limbopro/Profiles4limbo |

- 定位：在 Koolson/Qure 基础上扩展的自定义图标仓库。
- 特色图标：AI Platforms、Netflix Letter、Disney+、TikTok 等扩展版本。

### 1.7 Toperlock / Quantumult（主题图标）
| 项目 | 地址 |
|------|------|
| GitHub | https://github.com/Toperlock/Quantumult |
| 图标目录 | https://github.com/Toperlock/Quantumult/tree/main/icon |

- 定位：哆啦A梦（Doraemon）主题图标集，以及部分自绘图标。
- 特点：风格统一、系列化，适合追求视觉一致性的配置。

### 1.8 其他值得关注的 Fork / 衍生
| 项目 | 说明 |
|------|------|
| zgaoliang520/Koolson-Qure | Qure 的镜像/Fork，同步维护 |
| axaclin / mini | Orz-3/mini 的 Fork |
| fenxp / Qure | Koolson/Qure 的 Fork |
| MaroonYS / Qure | Qure 的 Fork |
| LovedGM/Quantumult-X-TuBiao | 自定义图标，含子鼠、地标建筑等系列 |

---

## 2. 免费图标源 / API

### 2.1 GitHub Raw / CDN 直链
这是代理工具社区最主流的图标托管方式，几乎所有主流图标集都通过 raw.githubusercontent.com 或 jsDelivr 提供直链。

| CDN | 示例 |
|-----|------|
| raw.githubusercontent.com | `https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/YouTube.png` |
| jsDelivr GitHub | `https://cdn.jsdelivr.net/gh/Koolson/Qure/IconSet/Color/YouTube.png` |
| gh-proxy 镜像 | `https://gh-proxy.com/https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/YouTube.png` |

> **注意**：国内网络访问 raw.githubusercontent.com 可能不稳定，可通过 jsDelivr 或 gh-proxy 镜像加速。

### 2.2 Simple Icons
| 资源 | 地址 |
|------|------|
| 官网 | https://simpleicons.org |
| GitHub | https://github.com/simple-icons/simple-icons |
| CDN | `https://cdn.simpleicons.org/{slug}/{color}` |
| 示例 | `https://cdn.simpleicons.org/youtube/red` |
| npm CDN | `https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{slug}.svg` |

- 特点：3,300+ 品牌 SVG 图标，CC0 协议，免费商用。
- 适合：生成任意品牌的矢量图标，可作为 Qure 未覆盖图标的补充来源。
- 颜色：可通过 URL 参数指定品牌色，如 `youtube/FF0000`。

### 2.3 Simple Icons API
| 端点 | 说明 |
|------|------|
| `https://api.simpleicons.org/{slug}` | 返回 SVG 与品牌色 |
| Parse Bot Marketplace | `simpleicons-org-api`，提供 search_icons / get_icon / list_icons |

### 2.4 Favicon API
| 资源 | 地址 |
|------|------|
| favicon.im | `https://favicon.im/api?url={domain}` |
| 说明 | 免费 Favicon 获取服务，无需认证，30M+ 月请求 |

> 可配合域名批量获取网站 favicon 作为策略组图标，但需注意版权与清晰度。

### 2.5 通用开源图标库（备用）
| 库 | 协议 | 说明 |
|----|------|------|
| Tabler Icons | MIT | 6000+ SVG，适合通用功能图标 |
| Bootstrap Icons | MIT | 官方 SVG 图标库 |
| Iconoir | 开源 | 大型开源图标库 |
| Remix Icon | MIT | 中性风格系统符号 |
| Font Awesome Free | CC-BY-4.0 | 2000+ 图标 |

---

## 3. 常见代理策略组类别清单

以下分类综合自主流 Surge / Clash / Loon / Quantumult X 配置实践。

### 3.1 节点类型 / 代理模式
| 英文 | 中文 | 说明 |
|------|------|------|
| Global / Proxy | 全球加速 / 全站代理 | 所有流量走代理 |
| Automatic / Auto | 自动选择 | url-test 自动测速选最优 |
| Fallback | 故障转移 | 主节点不可用时自动切换 |
| Load-Balance | 负载均衡 | 轮询或一致性哈希分发 |
| Select | 手动选择 | 用户手动切换节点 |
| DIRECT | 直连 | 不走代理 |
| REJECT | 拦截 | 拒绝连接 |
| SSID | 网络选择 | 根据 WiFi SSID 自动切换 |
| Smart | 智能选择 | Surge 智能策略组 |

### 3.2 地区 / 区域
| 英文 | 中文 | 常见后缀 |
|------|------|----------|
| Hong Kong | 香港 | 🇭🇰、HK |
| Taiwan | 台湾 | 🇨🇳、TW |
| Japan | 日本 | 🇯🇵、JP |
| Singapore | 新加坡 | 🇸🇬、SG |
| United States | 美国 | 🇺🇸、US |
| Korea | 韩国 | 🇰🇷、KR |
| Europe / EU | 欧盟 / 欧洲 | 🇪🇺、EU |
| Others | 其他 | 冷门节点兜底 |

### 3.3 流媒体媒体
| 英文 | 中文 | 常见图标来源 |
|------|------|--------------|
| YouTube | YouTube | Qure: YouTube.png |
| Netflix | Netflix / 奈飞 | Qure: Netflix.png |
| Disney+ | 迪士尼+ | Qure: Disney+.png |
| Spotify | Spotify | Qure: Spotify.png |
| TikTok | TikTok | Qure: TikTok.png |
| Twitch | Twitch | Qure: Twitch.png |
| Hulu | Hulu | Qure: Hulu.png |
| Amazon Prime Video | 亚马逊 Prime 视频 | Qure: Prime Video.png |
| HBO | HBO | Qure: HBO.png |
| BBC iPlayer | BBC iPlayer | Qure: BBC iPlayer.png |
| iQIYI | 爱奇艺 | Qure: iQIYI.png |
| Bilibili | 哔哩哔哩 / B站 | Qure: bilibili.png |
| WeTV | 腾讯视频国际版 | Qure: WeTV.png |
| ViuTV | ViuTV | Qure: ViuTV.png |
| TVB | TVB | Qure: TVB.png |
| AbemaTV | AbemaTV | Qure: AbemaTV.png |
| Bahamut | 巴哈姆特 | Qure: Bahamut.png |
| ESPN+ | ESPN+ | Qure: ESPN+.png |
| DAZN | DAZN | Qure: DAZN.png |
| Pandora | Pandora | Qure: Pandora.png |
| TIDAL | TIDAL | Qure: TIDAL.png |
| Deezer | Deezer | Qure: Deezer.png |
| YouTube Music | YouTube Music | Qure: YouTube Music.png |
| Vimeo | Vimeo | Qure: Vimeo.png |
| KKBOX | KKBOX | Qure: KKBOX.png |
| KKTV | KKTV | Qure: KKTV.png |
| LineTV | LineTV | Qure: LineTV.png |
| myTV SUPER | myTV SUPER | Qure: myTV SUPER.png |
| EncoreTVB | EncoreTVB | Qure: encoreTVB.png |
| All4 | All4 | Qure: All4.png |
| ITV Hub | ITV Hub | Qure: ITV Hub.png |
| PBS | PBS | Qure: PBS.png |
| My5 | My5 | Qure: My5.png |
| Flipps | Flipps | 部分地区可见 |
| Pornhub | Pornhub | Qure: Pornhub.png |

### 3.4 社交平台
| 英文 | 中文 | 说明 |
|------|------|------|
| Telegram | Telegram / TG | 即时通讯 |
| X / Twitter | X / Twitter | 社交媒体 |
| Instagram | Instagram | 图片社交 |
| Facebook | Facebook | 社交网络 |
| WeChat | 微信 | 即时通讯 |
| Weibo | 微博 | 社交媒体 |
| WhatsApp | WhatsApp | 即时通讯 |
| Discord | Discord | 社群聊天 |
| Snapchat | Snapchat | 图片社交 |
| Pinterest | Pinterest | 图片分享 |
| LinkedIn | LinkedIn | 职业社交 |
| Reddit | Reddit | 论坛社区 |
| Threads | Threads | Meta 社交 |
| TikTok Social | TikTok 社交功能 | 需与媒体区分 |

### 3.5 AI 服务 / 平台
| 英文 | 中文 | 说明 |
|------|------|------|
| OpenAI / ChatGPT | OpenAI / ChatGPT | 大语言模型 |
| Claude | Claude | Anthropic 模型 |
| Google AI / Bard | Google AI / Bard | Google 大模型 |
| Gemini | Gemini | Google 模型 |
| Copilot | Copilot | GitHub/微软 AI |
| Midjourney | Midjourney | AI 绘画 |
| Stable Diffusion | Stable Diffusion | AI 绘画开源 |
| DALL·E | DALL·E | OpenAI 绘画 |
| Poe | Poe | 多模型聚合平台 |
| Perplexity | Perplexity | AI 搜索引擎 |
| Hugging Face | Hugging Face | 模型托管平台 |
| Character.AI | Character.AI | AI 角色对话 |
| Notion AI | Notion AI | 笔记 AI |
| Slack AI | Slack AI | 办公 AI |
| Microsoft Copilot | Microsoft Copilot | 微软 AI |

### 3.6 游戏平台
| 英文 | 中文 | 说明 |
|------|------|------|
| Steam | Steam | PC 游戏平台 |
| Epic Games | Epic Games | 游戏平台 |
| Origin | Origin | EA 游戏平台 |
| PlayStation / Sony | PlayStation / 索尼 | 主机平台 |
| Nintendo | Nintendo | 任天堂 |
| Xbox | Xbox | 微软主机 |
| Blizzard | 暴雪 | 战网平台 |
| GOG | GOG | 数字游戏平台 |
| Ubisoft | Ubisoft / 育碧 | 游戏平台 |
| Riot Games | Riot Games | 英雄联盟等 |
| Minecraft | Minecraft | 我的世界 |
| Roblox | Roblox | 游戏平台 |
| Twitch Gaming | Twitch | 游戏直播 |
| Discord Gaming | Discord | 游戏社群 |

### 3.7 科技 / 开发工具
| 英文 | 中文 | 说明 |
|------|------|------|
| Apple | 苹果 | iOS / macOS 服务 |
| Google | 谷歌 | 搜索/云服务 |
| Microsoft | 微软 | Windows/Office/云 |
| GitHub | GitHub | 代码托管 |
| GitLab | GitLab | 代码托管 |
| Stack Overflow | Stack Overflow | 开发者社区 |
| JetBrains | JetBrains | IDE 工具 |
| Docker | Docker | 容器化 |
| npm / PyPI | 包管理 | 开发依赖 |
| Vercel | Vercel | 部署平台 |
| Netlify | Netlify | 部署平台 |
| Cloudflare | Cloudflare | CDN/安全 |
| Fastly | Fastly | CDN |
| DigitalOcean | DigitalOcean | 云服务商 |
| AWS | AWS | 亚马逊云 |
| Azure | Azure | 微软云 |
| GCP | Google Cloud | 谷歌云 |
| Oracle Cloud | Oracle Cloud | 甲骨文云 |
| Tencent Cloud | 腾讯云 | 云服务 |
| Alibaba Cloud | 阿里云 | 云服务 |
| Baidu Cloud | 百度云 | 云服务 |
| Heroku | Heroku | 云平台 |

### 3.8 金融 / 支付
| 英文 | 中文 | 说明 |
|------|------|------|
| PayPal | PayPal | 支付 |
| Stripe | Stripe | 支付 |
| Wise | Wise | 跨境转账 |
| Visa | Visa | 信用卡 |
| Mastercard | Mastercard | 信用卡 |
| American Express | 美国运通 | 信用卡 |
| Binance | Binance | 加密货币 |
| Coinbase | Coinbase | 加密货币 |
| Crypto.com | Crypto.com | 加密货币 |
| PayPal / Venmo | Venmo | 支付 |
| Revolut | Revolut | 数字银行 |
| Robinhood | Robinhood | 股票交易 |

### 3.9 效率 / 办公
| 英文 | 中文 | 说明 |
|------|------|------|
| Google Workspace | Google 办公套件 | Gmail/Docs/Drive |
| Microsoft 365 | Microsoft 365 | Office 套件 |
| Notion | Notion | 笔记/知识库 |
| Obsidian | Obsidian | 笔记软件 |
| Evernote | Evernote | 印象笔记 |
| Todoist | Todoist | 待办事项 |
| Slack | Slack | 团队沟通 |
| Zoom | Zoom | 视频会议 |
| Google Meet | Google Meet | 视频会议 |
| Microsoft Teams | Teams | 微软会议 |
| Webex | Webex | 思科会议 |
| Telegram Desktop | Telegram | 桌面版 |
| 1Password | 1Password | 密码管理 |
| LastPass | LastPass | 密码管理 |
| Dropbox | Dropbox | 云存储 |
| OneDrive | OneDrive | 微软云存储 |
| Google Drive | Google Drive | 谷歌云存储 |
| iCloud | iCloud | 苹果云存储 |
| Box | Box | 企业云存储 |
| Confluence | Confluence | 企业知识库 |
| Jira | Jira | 项目管理 |
| Trello | Trello | 项目管理 |
| Asana | Asana | 项目管理 |
| Monday.com | Monday.com | 项目管理 |

### 3.10 购物 / 电商
| 英文 | 中文 | 说明 |
|------|------|------|
| Amazon | 亚马逊 | 电商 |
| eBay | eBay | 电商 |
| Shopee | Shopee | 电商 |
| Lazada | Lazada | 电商 |
| Tmall | 天猫 | 电商 |
| Taobao | 淘宝 | 电商 |
| JD | 京东 | 电商 |
| Pinduoduo | 拼多多 | 电商 |
| Mercari | Mercari | 日本电商 |
| Rakuten | 乐天 | 日本电商 |
| Alibaba | 阿里巴巴 | B2B 电商 |

### 3.11 交通 / 出行
| 英文 | 中文 | 说明 |
|------|------|------|
| Uber | Uber | 网约车 |
| Lyft | Lyft | 网约车 |
| DiDi | 滴滴 | 网约车 |
| Grab | Grab | 东南亚出行 |
| Google Maps | 谷歌地图 | 地图 |
| Apple Maps | 苹果地图 | 地图 |
| Waze | Waze | 地图导航 |
| Citymapper | Citymapper | 公交导航 |
| Booking.com | Booking.com | 酒店预订 |
| Airbnb | Airbnb | 民宿预订 |
| Agoda | Agoda | 酒店预订 |
| Trip.com | Trip.com | 携程国际版 |
| Skyscanner | Skyscanner | 机票比价 |
| Kayak | Kayak | 旅行比价 |

### 3.12 音乐 / 音频
| 英文 | 中文 | 说明 |
|------|------|------|
| Spotify | Spotify | 音乐流媒体 |
| Apple Music | Apple Music | 苹果音乐 |
| YouTube Music | YouTube Music | 谷歌音乐 |
| SoundCloud | SoundCloud | 音乐分享 |
| NetEase Cloud Music | 网易云音乐 | 国内音乐 |
| QQ Music | QQ 音乐 | 腾讯音乐 |
| Kugou | 酷狗音乐 | 音乐平台 |
| Kuwo | 酷我音乐 | 音乐平台 |
| JOOX | JOOX | 腾讯国际音乐 |
| KKBOX | KKBOX | 亚洲音乐 |
| TIDAL | TIDAL | 高音质音乐 |
| Deezer | Deezer | 欧洲音乐 |
| Pandora | Pandora | 美国音乐 |
| Amazon Music | Amazon Music | 亚马逊音乐 |

### 3.13 新闻 / 内容
| 英文 | 中文 | 说明 |
|------|------|------|
| Google News | 谷歌新闻 | 新闻聚合 |
| Apple News | 苹果新闻 | 新闻聚合 |
| Twitter / X | X | 社交新闻 |
| Reddit | Reddit | 社区内容 |
| Medium | Medium | 博客平台 |
| Substack | Substack | 付费 Newsletter |
| YouTube | YouTube | 视频内容 |
| Bilibili | 哔哩哔哩 | 国内视频 |
| Douyin | 抖音 | 短视频 |
| Kuaishou | 快手 | 短视频 |
| Xiaohongshu | 小红书 | 社交电商 |
| Zhihu | 知乎 | 问答社区 |
| Weibo | 微博 | 社交媒体 |
| Toutiao | 今日头条 | 新闻资讯 |

### 3.14 广告 / 隐私 / 安全
| 英文 | 中文 | 说明 |
|------|------|------|
| Advertising | 广告拦截 | 通用广告 |
| AdWhite | 白名单广告 | 可接受广告 |
| AdBlack | 黑名单广告 | 强制拦截 |
| Hijacking | 运营劫持 | 运营商劫持 |
| Tracking | 追踪拦截 | 隐私追踪 |
| Privacy | 隐私保护 | 隐私规则 |
| Malware | 恶意软件 | 安全防护 |
| Phishing | 钓鱼网站 | 安全防护 |

### 3.15 基础设施 / 其他
| 英文 | 中文 | 说明 |
|------|------|------|
| Speedtest | 网速测试 | 测速 |
| GeoIP | IP 查询 | 地理位置 |
| IPLC | IPLC 专线 | 企业专线 |
| IEPL | IEPL 专线 | 企业专线 |
| BGP | BGP 线路 | 机房线路 |
| CN2 | CN2 线路 | 电信优质线路 |
| CN2 GIA | CN2 GIA | 电信精品线路 |
| CN2 GT | CN2 GT | 电信商业线路 |
| Oracle | Oracle | 甲骨文云 |
| DMIT | DMIT | 洛杉矶机房 |
| PCCW | PCCW | 香港电讯 |
| HKT | HKT | 香港电讯 |
| HGC | HGC | 香港宽频 |
| NTT | NTT | 日本电信 |
| SoftBank | SoftBank | 软银 |
| SK | SK | 韩国电信 |
| KT | KT | 韩国电信 |
| HiNet | HiNet | 台湾中华电信 |
| Azure | Azure | 微软云 |
| AWS | AWS | 亚马逊云 |
| GCP | GCP | 谷歌云 |
| Baidu Cloud | 百度云 | 百度云 |
| Tencent Cloud | 腾讯云 | 腾讯云 |
| Alibaba Cloud | 阿里云 | 阿里云 |

---

## 4. 常见品牌 / 服务与图标映射参考

下表汇总了主流配置中频繁出现的品牌/服务及其常见图标来源。

| 策略组名称 | 英文 slug / 文件名 | 常见图标来源 | 适用工具 |
|-----------|-------------------|-------------|---------|
| 全球加速 | Global | Qure: Global.png | 全部 |
| 自动选择 | Auto | Qure: Auto.png | 全部 |
| 故障切换 | Fallback / ULB | Qure: ULB.png | 全部 |
| 负载均衡 | Round Robin | Qure: Round Robin.png | 全部 |
| 直连 | Direct | Qure: Direct.png | 全部 |
| 拦截 | Reject | Qure: Reject.png | 全部 |
| 兜底 | Final | Qure: Final.png | 全部 |
| 广告拦截 | Advertising | Qure: Advertising.png | 全部 |
| 规则修正 | Unbreak | Qure: Back.png | 全部 |
| 隐私保护 | Privacy | Qure: Lab.png | 全部 |
| 运营劫持 | Hijacking | Qure: Hijacking.png | 全部 |
| 苹果服务 | Apple | Qure: Apple.png | 全部 |
| 谷歌服务 | Google | Qure: Google.png | 全部 |
| 微软服务 | Microsoft | Qure: Microsoft.png | 全部 |
| Telegram | Telegram | Qure: Telegram.png | 全部 |
| X / Twitter | X / Twitter | Qure: Twitter.png | 全部 |
| YouTube | YouTube | Qure: YouTube.png | 全部 |
| Netflix | Netflix | Qure: Netflix.png | 全部 |
| Disney+ | Disney+ | Qure: Disney+.png | 全部 |
| TikTok | TikTok | Qure: TikTok.png | 全部 |
| Spotify | Spotify | Qure: Spotify.png | 全部 |
| Bilibili | bilibili | Qure: bilibili.png | 全部 |
| 爱奇艺 | iQIYI | Qure: iQIYI.png | 全部 |
| 哔哩哔哩 | bilibili | Qure: bilibili.png | 全部 |
| 微信 | WeChat | Qure 缺失，可用 Simple Icons | 全部 |
| 微博 | Weibo | Qure: Weibo.png | 全部 |
| 钉钉 | DingTalk | Toperlock: dingtalk.png | 全部 |
| 京东 | JD | Orz-3/mini: jd.png | 全部 |
| 网易云音乐 | NetEase Music | Qure: NetEase Music.png | 全部 |
| ChatGPT | ChatGPT | Qure: ChatGPT.png | 全部 |
| OpenAI | OpenAI | Toperlock: ChatGPT.png | 全部 |
| Claude | Claude | Simple Icons: claude.svg | 全部 |
| Steam | Steam | Simple Icons: steam.svg | 全部 |
| Epic Games | Epic Games | Simple Icons: epicgames.svg | 全部 |
| Nintendo | Nintendo | Simple Icons: nintendo.svg | 全部 |
| PlayStation | PlayStation | Simple Icons: playstation.svg | 全部 |
| GitHub | GitHub | Qure: GitHub.png / Simple Icons | 全部 |
| GitLab | GitLab | Simple Icons: gitlab.svg | 全部 |
| PayPal | PayPal | Qure: PayPal.png | 全部 |
| Speedtest | Speedtest | Qure: Speedtest.png | 全部 |
| 香港 | Hong Kong | Qure: Hong Kong.png | 全部 |
| 台湾 | Taiwan | Qure: Taiwan.png | 全部 |
| 日本 | Japan | Qure: Japan.png | 全部 |
| 新加坡 | Singapore | Qure: Singapore.png | 全部 |
| 美国 | United States | Qure: United States.png | 全部 |
| 韩国 | Korea | Qure: Korea.png | 全部 |
| 中国 | China | Qure: China.png | 全部 |

---

## 5. 图标使用方式速查

| 工具 | 图标参数 | 示例 |
|------|---------|------|
| Surge | `icon-url` | `icon-url=https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/YouTube.png` |
| Quantumult X | `img-url` | `img-url=https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/YouTube.png` |
| Loon | `icon-url` | `icon-url=https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/YouTube.png` |
| Clash / Stash / Mihomo | `icon` | `icon: https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/YouTube.png` |
| Surge 机场订阅 | `img-url` | `img-url=https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/mini/Auto.png` |

> 注意：Quantumult X 更换图标后需清理本地缓存（iPhone：Quantumult X → Images 文件夹删除缓存文件），然后重启生效。

---

## 6. 建议的 PolicyIcons 项目资源结构参考

```
PolicyIcons/
├── README.md
├── IconSet/
│   ├── mini/          # 纯白图标（适合深色/浅色通用）
│   └── Color/         # 彩色图标（品牌原色）
├── manifest.json      # 图标清单：name, category, tags, source, url
├── categories/
│   ├── streaming.json # 流媒体类目
│   ├── social.json    # 社交类目
│   ├── ai.json        # AI 服务类目
│   ├── gaming.json    # 游戏类目
│   └── ...
└── scripts/
    └── generate.js    # 自动生成订阅 JSON / README 表格
```

---

## 7. 参考配置示例

以下为真实配置片段，展示图标在策略组中的实际使用：

```conf
# Surge / Loon / Quantumult X
static=YouTube, Automatic, 香港, 台湾, 日本, 狮城, 美国, proxy, img-url=https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/mini/YouTube.png

# Clash / Mihomo / Stash
- { name: YouTube, icon: https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/YouTube.png, type: select, proxies: [HongKong, Taiwan, Japan, Singapore, America, Proxy] }
```

---

## 8. 常见图标订阅链接汇总

| 名称 | 类型 | 链接 |
|------|------|------|
| Qure mini | JSON | `https://raw.githubusercontent.com/Koolson/Qure/master/Other/Quremini.json` |
| Qure Color | JSON | `https://raw.githubusercontent.com/Koolson/Qure/master/Other/QureColor.json` |
| Qure All Color | JSON | `https://raw.githubusercontent.com/Koolson/Qure/master/Other/QureColor-All.json` |
| Orz-3 mini | 目录浏览 | `https://github.com/Orz-3/mini/tree/master/Color` |
| Simple Icons | CDN | `https://cdn.simpleicons.org/{slug}` |

---

*本文档基于公开搜索与社区配置整理，仅供学习参考。图标版权归原作者所有，使用前请注意各仓库的 License 声明。*
