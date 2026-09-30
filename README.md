<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Surge/Surge/Surge.png">
    <img src="https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Surge/Surge/Surge.png" width="120" alt="Oasisic-Icons">
  </picture>
</p>

<h1 align="center">🎨 Oasisic-Icons</h1>

<p align="center">
  <b>跨平台代理策略组图标合集</b><br>
  <i>Cross-platform Proxy Policy Group Icon Collection</i>
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/Hawaiine/Oasisic-Icons?style=flat-square" alt="License">
  <img src="https://img.shields.io/github/stars/Hawaiine/Oasisic-Icons?style=flat-square" alt="Stars">
  <img src="https://img.shields.io/github/last-commit/Hawaiine/Oasisic-Icons?style=flat-square" alt="Last Commit">
  <img src="https://img.shields.io/github/repo-size/Hawaiine/Oasisic-Icons?style=flat-square" alt="Repo Size">
  <img src="https://img.shields.io/badge/icons-292-blue?style=flat-square" alt="Icons Count">
  <img src="https://img.shields.io/badge/brands-292-green?style=flat-square" alt="Brands Count">
  <img src="https://img.shields.io/badge/categories-42-orange?style=flat-square" alt="Categories Count">
</p>

---

## 📖 简介 / Introduction

**Oasisic-Icons** 是一套专为代理工具设计的策略组图标合集：当前共 **292** 个 PNG 图标，覆盖 **292** 个品牌，归入 **42** 个一级分类（其中 41 个活跃，`Finance` 为预留空分类）。

本项目为独立图标仓库，当前 292 个图标均为 512×512 PNG（RGBA 模式），适配 Surge、Loon、Clash Meta / Mihomo、Stash、Quantumult X、Egern 等主流代理客户端。

> **画质规范（贡献与替换标准）**：512×512 方形 PNG，RGBA 模式，Apple 风格 squircle 圆角（圆角半径 ≈ 115px / 约 22.4%），保留原始底色。
> 仓库内图标按该规范维护，均为 512×512、RGBA、保留原始底色，经 `scripts/optimize-icons.py` 无损重压缩；少量历史圆角边缘遗留项待处理，明细与遗留项见 [`docs/references/icon-quality-notes.md`](docs/references/icon-quality-notes.md)。

---

## 🗂 目录与命名规范 / Structure & Naming

### 文件夹结构

所有图标统一采用以下结构（多层物理层级，2026-10-01 定稿）：

```
icons/
└── <分类>/
    └── <品牌名>/
        └── <品牌名>.png                    ← 默认图标（必须存在，无任何后缀）
```

**同类中间父品牌下的深层子品牌**物理嵌套在父品牌目录内：

```
icons/
└── Meta/
    └── Facebook/
        ├── Facebook.png
        ├── README.md
        └── Instagram/
            └── Instagram.png               ← Instagram → Facebook → Meta
```

路径由 `scripts/brand_relationships.py::expected_icon_path()` 统一推导
（`brands.json.icon_path` 必须等于其输出，CI 第 7/17 组校验），全库矩阵见
[`docs/references/physical-hierarchy-audit.md`](docs/references/physical-hierarchy-audit.md)。

### 强制规则

1. **每个品牌必须有独立文件夹**，即使目前只有一个图标。
2. **默认图标永远命名为 `<品牌名>.png`**（无任何后缀），且必须存在。
3. **一个品牌当前只包含一个 PNG**：多版本变体已在 2026-09-29 全库移除（待后续统一重构后再引入）；命名规范保留 `<品牌名>NN.png`（两位零填充）供未来使用。
4. **品牌名使用 PascalCase**，尽量与 [mihomo-rules](https://github.com/Hawaiine/mihomo-rules/tree/main/ruleset) 的品牌名保持一致。
   - 例外：**官方品牌名的大小写优先**，保留官方写法的目录有 `iQIYI`、`friDayVideo`、`myTVSUPER` 等；这些名称同时被消费方（mihomo-rules）的配置引用，不得为了「统一大小写」而改动。
5. **特殊字符处理**：`+` → `Plus`（例如 `DisneyPlus`）。

### 正确示例

```
icons/Country/Japan/
└── Japan.png            ← 默认（原始素材经 scripts/normalize-icons.py 规范化到 512×512）

icons/Media/Netflix/
└── Netflix.png          ← 只有 1 个也必须放进品牌文件夹
```

### 错误示例（禁止）

- ❌ 直接把 PNG 放在分类目录下（不建品牌文件夹）
- ❌ 品牌文件夹缺少 `<品牌名>.png` 默认图标
- ❌ 使用连字符/无零填充的旧式变体命名（`Spotify-1.png`、`Spotify1.png`）

---

## 🚀 快速开始 / Quick Start

### 1. 通用直链格式

```
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/<分类>/[<中间父…>/]<品牌>/<文件名>.png
```

示例：

```
# 默认图标
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png

# 单文件品牌
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Development/GitHub/GitHub.png
```

> 本仓库只提供 `raw.githubusercontent.com` 直链，**不使用 jsDelivr 等 CDN**。

### 2. 批量图标订阅（JSON）

部分客户端支持一次性导入整套图标集（图标订阅 / 策略组图标订阅），订阅地址为：

```
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/config/surge-icon.json
```

在客户端的「策略组图标 / 图标订阅」入口中添加该 URL 即可（Loon、Stash、Egern、Clash Meta 等支持图标订阅的版本）。

> 注意：`config/surge-icon.json` 是**图标订阅清单**，不是脚本，请勿填写到 `script-path` 等脚本字段。

### 3. Surge / Loon 单条示例

```ini
# Surge：icon-url 必须写在策略组同一行
[Proxy Group]
Netflix = select, HK, TW, JP, SG, icon-url=https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png
```

```ini
# Loon：img-url（不是 icon），同样写在策略组同一行
[Proxy Group]
Netflix = select, HK, TW, JP, SG, img-url = https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png
```

### 4. Clash Meta / Mihomo 单条示例

```yaml
# config.yaml
proxy-groups:
  - name: Netflix
    type: select
    proxies: [HK, TW, JP, SG]
    icon: https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png

  - name: 🎬 Media
    type: select
    proxies: [Proxy]
    icon: https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png
```

> Mihomo / Clash Meta 的图标字段是 **`icon`（单数，字符串）**，不是复数列表，也不是 `"名称: URL"` 形式的字符串数组。

### 5. Quantumult X 单条示例

```ini
[policy]
static=Netflix, HK, TW, JP, SG, img-url=https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png
```

> QX 的图标 URL 只应写在 `[policy]` 段的 `static=..., img-url=...` 里，不要使用「URL 重写 / MITM 劫持」的写法。

---

## 📁 图标分类列表 / Categories

| 分类 | 说明 | 品牌数 | 图标数 |
|---|---|---:|---:|
| 🤖 AI | 人工智能服务与模型 | 11 | 11 |
| 🏢 Alibaba | 阿里巴巴生态 | 8 | 8 |
| 📦 Amazon | 亚马逊生态 | 6 | 6 |
| 🍎 Apple | 苹果生态 | 13 | 13 |
| 🔍 Baidu | 百度生态 | 4 | 4 |
| ▶️ ByteDance | 字节跳动生态 | 6 | 6 |
| 📶 ChinaMobile | 中国移动生态 | 3 | 3 |
| 🏰 Disney | 迪士尼生态 | 4 | 4 |
| 🏗️ Infrastructure | 基础设施与运维（云平台/网络/容器/NAS） | 7 | 7 |
| 💾 Cloud Storage | 云盘与文件存储 | 5 | 5 |
| 💬 Communication | 即时通讯与团队协作 | 6 | 6 |
| 🌍 Country | 国家与地区旗帜 | 21 | 21 |
| ₿ Crypto | 加密货币与区块链 | 1 | 1 |
| 💻 Development | 开发者工具与平台 | 1 | 1 |
| 📚 Education | 教育与学习平台 | 2 | 2 |
| 💰 Finance | 金融理财 | 0 | 0 |
| 📱 Meta | Meta 生态 | 6 | 6 |
| 🎮 Game | 游戏平台与服务 | 3 | 3 |
| 🔎 Google | Google 服务与生态 | 12 | 12 |
| 🔌 Hardware | 硬件与消费电子设备 | 8 | 8 |
| 🏥 Health | 健康与运动 | 1 | 1 |
| 🦚 NBCUniversal | NBC 环球生态 | 3 | 3 |
| 🎧 NetEase | 网易生态 | 3 | 3 |
| 🏠 Home | 智能家居与家庭设备 | 2 | 2 |
| 🎬 Media | 影音流媒体与视频 | 55 | 55 |
| 🪟 Microsoft | 微软服务与生态 | 10 | 10 |
| 🎵 Music | 音乐服务 | 10 | 10 |
| 📰 News | 新闻与资讯 | 1 | 1 |
| 💳 Payment | 支付与金融交易 | 5 | 5 |
| ☎️ PCCW | 电讯盈科生态 | 3 | 3 |
| 🌐 Proxy | 代理线路与协议 | 4 | 4 |
| 🛒 Shopping | 购物与电商 | 5 | 5 |
| 👥 Social | 社交媒体与社区 | 10 | 10 |
| 🕹️ Sony | 索尼生态 | 4 | 4 |
| ⚡ Surge | Surge 应用图标 | 1 | 1 |
| ⚙️ System | 代理系统图标与通用策略 | 20 | 20 |
| 📡 Telecom | 电信运营商 | 3 | 3 |
| 🐧 Tencent | 腾讯生态 | 7 | 7 |
| 🚗 Transport | 出行与交通 | 3 | 3 |
| 🧰 Utilities | 生产力工具与实用服务 | 9 | 9 |
| 🎞️ Warner Bros. Discovery | 华纳兄弟探索生态 | 3 | 3 |
| 🛰️ SpaceXAI | SpaceXAI 生态 | 3 | 3 |
| **合计** | — | **292** | **292** |
### 分类体系原则（方案 C，2026-09-29）

一级分类**不设中间层**：不设置 `Ecosystems / Services / Special` 等分类之上的中间层；分类之下的深度只由**真实父子层级**决定——直接父品牌是 category 根时保持 `icons/<分类>/<品牌>/`，直接父品牌本身也是中间品牌（同类且有自身图标）时嵌套为 `icons/<分类>/<中间父>/<品牌>/`。

**分类定义 SSOT**：分类的 ID、emoji、显示名、描述、排序、状态唯一来源为 [`config/categories.json`](config/categories.json)；分类 README 由 `scripts/generate-category-readmes.sh` 从该文件生成，禁止在脚本中硬编码。

**品牌语义 SSOT**：[`config/brands.json`](config/brands.json) 记录每个品牌的 canonical 归属（分类、实体类型、直接品牌父级、显示名）。`parent_brand` 只表达 Brand / Product Hierarchy；Developer / Provider / Platform Integration / Distribution 关系不写入该字段，相关当前事实由归属审计文档记录。`surge-icon.json` 与 `brand-glossary.md` 均由磁盘 + SSOT 派生，CI 校验三方一致。

**分类原则**：

1. **功能分类**（AI / Media / Music / …）按服务语义归类；
2. **生态分类**判定规则统一如下（机械、可自动验证，CI 动态校验，`scripts/brand_relationships.py`）：
   > **一个生态根（`entity_type: ecosystem`）拥有 ≥ 2 个 Canonical Descendants 时，为其建立独立一级品牌生态分类。**
   统计口径：只计算沿 `parent_brand` 链可达该生态根的 Canonical Brand（**descendants = 直系子 + 孙 + 更深后代**，不含 root 本身、aliases / 历史品牌 / 重复文件）；用 descendants 而非 direct children，避免中间层（如 Facebook）误触发分类爆炸。
   - descendants ≥ 2 → 建 `icons/<Root>/` 一级分类，descendants 统一迁入（`category = <Root>`，**保留 `parent_brand`**）；
   - 生态根有 root icon → 迁入 `icons/<Root>/<Root>/<Root>.png`；没有 root icon → 仍建目录，**不得伪造 root icon**，生态根登记 `parent_brands_without_icon`（白名单只表示无 root icon，不代表不建目录，且白名单内不得出现已有 canonical icon 的品牌）；
   - descendants < 2 → 不建一级目录（避免一级目录爆炸），留在功能分类，生态关系只写 `parent_brand` 元数据。
   当前生态分类（17 个，随 brands.json 动态扩展，不写死数量）：Alibaba / Amazon / Apple / Baidu / ByteDance / ChinaMobile / Disney / Google / Meta / Microsoft / NBCUniversal / NetEase / PCCW / SONY / SpaceXAI / Tencent / WarnerBrosDiscovery。
   其中 **SpaceXAI** 为 2026-10-01 新增：descendants = X / xAI / Grok = 3 ≥ 2；根品牌条目与根图标待官方标志（登记 `parent_brands_without_icon` 白名单 + `config/brand-review-queue.json`），**不得伪造根图标**。
3. **Canonical Brand 唯一**：同一品牌只允许出现在一个分类，跨语义需求用 `brands.json` 的 tags/aliases 表达，**绝不复制 PNG**；
4. **系统图标归 `System/`**：Direct / Reject / Proxy / SSID / Traffic 等无品牌策略图标不混入品牌分类；
5. **ownership evidence ≠ Brand Graph**：`brands.json` 是 canonical Brand / Icon / Relationship SSOT；现实世界的 corporate ownership 证据、来源与研究判断只记录在 [`docs/references/brand-ownership-audit.md`](docs/references/brand-ownership-audit.md)，不因「同属一家公司」自动新增 `parent_brand`；只有经 Brand / Product Hierarchy 语义确认的关系才进入关系图。
6. **category ≠ parent_brand ≠ 生态根**：category 回答「图标归哪个一级目录」，parent_brand 回答「直接属于哪个品牌」（**直接父品牌 / immediate parent**，如 Instagram → Facebook、YouTubeMusic → YouTube、iCloudPrivateRelay → iCloud），生态根回答「最终属于哪个生态」——生态根**不单独存字段**，由 `entity_type: ecosystem` 标记 + 沿 parent 链向上动态派生（`brand_relationships.resolve_ecosystem_root`），消费方零成本获得。
   **entity_type** 回答「实体本身是什么」：`ecosystem` 用于生态根品牌（拥有自身一级生态分类者，当前 16 个，随 brands.json 动态扩展），子品牌与中间层品牌一律 `product_brand`；**公司品牌但未构成独立生态者（如 SINA / Xiaomi / TVB）亦为 `product_brand`**，其子公司/产品经 `parent_brand` 关联，不建一级生态目录。`SpaceXAI` 生态分类已建立但其根条目/根图标待官方标志（见上），故当前无 `entity_type` 条目。

   **关系证据层角色（辅助审计，非 SSOT、非阻塞条件）**：`config/parent-edge-evidence.json` 与
   [`docs/references/parent-edge-semantic-audit.md`](docs/references/parent-edge-semantic-audit.md)
   （均由 `scripts/gen-parent-edge-evidence.py` 生成，可重放）对全部 **117** 条 live `parent_brand` edge
   记录 `relation_type` + `parent_brand_validity`，仅供复核与 review context：
   - 关系事实与判定由 `config/brands.json`（SSOT）+ `scripts/brand_relationships.py`（关系引擎）承担；
   - 该分级是 evidence-text triage，不是 real-world proof（117 条中 0 条记录 `source.url`），
     逐边补来源是**后续完善项**，不作为 PR 完成前提；
   - 当前分布 `BRAND_HIERARCHY 8 / CORPORATE_OWNERSHIP 42 / DEVELOPER_PROVIDER 7 /
     PLATFORM_INTEGRATION 0 / UNKNOWN 60`，即 **CONFIRMED 8 / OPEN_REVIEW 109 / REJECTED 0**；
   - 收购/持股/合资/开发者/平台等证据**不会**自动升级为 Brand Hierarchy；真正有歧义的关系进
     `config/brand-review-queue.json`，人工裁决后写回 `brands.json`。

   **下游同步接口**：`config/brand-relationships.json` 是从上述 SSOT + 关系引擎派生的机器可读导出
   （标 `generated: true` / `source: config/brands.json`，**不是第二个 SSOT**，CI 第 15 组逐项校验），
   供 mihomo-rules 等下游读取 `parent` / `ancestor_chain` / `graph_root` / `ecosystem_root`。

**归属审计（研究层）**：[`docs/references/brand-ownership-audit.md`](docs/references/brand-ownership-audit.md) 记录全库每个 Canonical Brand 的**当前现实世界母公司**判断、证据来源、状态（CONFIRMED_PARENT / NO_PARENT / AMBIGUOUS_JV / RETIRED / SPECIAL_ENTITY）与采取的动作。CI 只能验证结构一致性，**无法证明现实归属完整性**——该职责由该审计文档承担。

**未来判例**：

- 新增 Spotify → `Music/Spotify/`
- 新增 Amazon 服务（如 Amazon Gaming）→ `Amazon/<Brand>/`
- 某生态根新增第二个 descendant（直系或孙代均可）→ 生态根 descendants 达到 2，**立即建立** `icons/<Root>/` 一级生态分类并迁入（CI 动态校验）
- 新增中间层产品（如 YouTube 下新增 YouTube Shorts 类服务）→ 写直接父品牌（`parent_brand = YouTube`），物理路径随之嵌套到 `icons/Google/YouTube/<新品牌>/`；**不**为中间层另建一级分类（阈值看生态根 descendants，防止分类爆炸）
- 新增 Alibaba AI 产品 → `Alibaba/<Brand>/`（AI 属性写 tags）
- 品牌被收购 → 先查**当前**官方状态，再决定生态归属；历史收购关系不等于当前归属
- 品牌脱离母公司 → 按当前独立状态归回功能分类
（仅保留目录与 README），便于后续按同一规范补充图标。

---

## 📦 发布与使用 / Usage & Distribution

本项目图标已发布为独立仓库，**不依赖任何外部上游同步**。图标格式统一为：

- **512×512 PNG，RGBA 模式**
- **Apple 风格 squircle 圆角（r=115px / 22.4%）**
- **四角透明**，可直接用于 Surge / Loon / Mihomo / Egern 等客户端

**订阅地址（建议用 `raw.githubusercontent.com`，不要用 jsDelivr）：**

```
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/config/surge-icon.json
```

本地也可直接使用 `icons/` 目录下的 PNG。

**规范化工具：**

```bash
python3 scripts/normalize-icons.py --apply   # 512×512 / RGBA / r=115 圆角
python3 scripts/optimize-icons.py            # 无损重压缩（不降色型）
python3 scripts/ci-validate-icons.py         # 校验 PNG / 目录 / JSON 一致性
```

---

## 🤝 贡献指南 / Contributing

### 图标质量要求

#### 强制输出规范（不可妥协）

- **尺寸**：严格 512×512 像素正方形
- **格式**：PNG，RGBA 模式
- **形状**：Apple iOS 风格 squircle 圆角矩形，圆角半径 r = 115px（约 22.4% of 512）
- **圆角外侧**：完全透明（alpha = 0）
- **背景**：保留原图主体底色；禁止自动抠图、禁止强制透明底
- **体积**：在像素不变的前提下可做无损压缩（oxipng 等），禁止有损量化/降色型

#### 核心原则：像素保真（最重要，专门防止 Docker/AliCloud 类事故）

**唯一允许的像素修改：**
1. 几何：非正方形时补边 → 缩放到 512×512
2. 透明度：仅对最终图像执行 `alpha = alpha × rounded_mask(r=115)`，即只让圆角外的区域变透明，圆角矩形内部的每一个像素的 RGB 和 alpha 必须与缩放后的原图完全一致。

**绝对禁止：**
- ❌ 禁止背景去除、抠图、去白底、去黑底、色键、flood-fill 透明
- ❌ 禁止对 logo 本体做 alpha 阈值、二值化、描边清理、边缘收缩/扩张
- ❌ 禁止改颜色、调对比度、自动白平衡、滤镜美化、降噪到抹掉细节
- ❌ 禁止把“接近白色/接近背景色”的像素当成透明删掉
- ❌ 禁止填充 logo 里原本就有的透明空洞（例如字母 C、O 的镂空）
- ❌ 禁止二次圆角、禁止先裁成圆角再套一次 mask（会变糊、半径错误）
- ❌ 禁止有损压缩、调色板量化、转 JPEG 再转回

**细线 / 低对比 logo 特别注意（Docker 类）：**
- 容器、网格、细描边、浅色线稿必须完整保留，不得因缩放或“清理”而消失
- 缩放只用高质量重采样（Lanczos 或等价），不要用最近邻
- 不要过度锐化；若原图很小导致细线发虚，可轻度锐化，但绝不能抹掉笔画
- 处理后目视检查：原图中能看到的线、点、小色块，结果里仍必须可见

**带透明镂空的 logo 特别注意（AliCloud 类）：**
- 原图里已经是透明的区域（字母空洞、环形中心等）保持透明
- 原图里不透明的区域（白/彩 logo 实体）必须保持不透明
- 不要把白色 logo 误判成“背景”而变透明
- 正确做法永远是：只乘圆角 mask，不要对内部再做任何 alpha 操作

**窄条字标（极少见）：** 仅当明显是横条文字标时，才可裁内容后放在对比色圆角底块上，再套 r=115；普通 logo 不要走这条路径。

### 命名规范

1. 目录：`icons/<分类>/<品牌名>/`（若直接父品牌本身也是中间品牌，则为 `icons/<分类>/<中间父>/<品牌名>/`，见上）
2. 默认图标：`<品牌名>.png`（无后缀，必须存在）
3. 变体图标（当前全库未使用，命名规范保留）：`<品牌名>01.png`、`<品牌名>02.png`（两位零填充，按原顺序编号）
4. 品牌名使用 PascalCase，与 [mihomo-rules](https://github.com/Hawaiine/mihomo-rules) 保持一致
5. 特殊字符：`+` → `Plus`
6. 官方品牌名大小写优先（`iQIYI` / `friDayVideo` / `myTVSUPER` 等保留官方写法，同时是消费方引用的路径）

### 提交流程

1. Fork 本仓库
2. 按规范把图标放入 `icons/<分类>/<品牌名>/`（深层子品牌放入父品牌目录，路径以 `scripts/validate-brand.py` 的推导结果为准）
3. 本地运行 `python3 scripts/ci-validate-icons.py` 确保通过
4. 提交 Pull Request

---

## 📚 参考文档 / References

- [docs/references/icon-quality-notes.md](docs/references/icon-quality-notes.md) — 画质规范、规范化结果、遗留项说明
- [docs/references/icon-research.md](docs/references/icon-research.md) — 品牌分类体系、策略组命名、常见图标来源（中英对照）
- [docs/references/upstream-history.md](docs/references/upstream-history.md) — 上游来源历史参考
- [docs/references/brand-glossary.md](docs/references/brand-glossary.md) — 品牌中英对照表（文件夹名 ↔ 中文显示名）
- [docs/references/brand-ownership-audit.md](docs/references/brand-ownership-audit.md) — 全库品牌现实世界归属审计（证据层）、关系模型、mihomo-rules 对照
- [docs/references/brand-naming-contract.md](docs/references/brand-naming-contract.md) — 品牌命名与同步契约（ID / display_name / directory / filename / 特殊字符映射 / 父品牌 README 规则）

## 📄 License

MIT License © 2026 [Hawaiine](https://github.com/Hawaiine)

---

## 🔗 相关项目 / Related

- [mihomo-rules](https://github.com/Hawaiine/mihomo-rules) — 代理规则集（本仓库图标的主要消费方）
