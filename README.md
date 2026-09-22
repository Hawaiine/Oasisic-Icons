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
  <img src="https://img.shields.io/badge/icons-362-blue?style=flat-square" alt="Icons Count">
  <img src="https://img.shields.io/badge/brands-247-green?style=flat-square" alt="Brands Count">
  <img src="https://img.shields.io/badge/categories-21-orange?style=flat-square" alt="Categories Count">
</p>

---

## 📖 简介 / Introduction

**Oasisic-Icons** 是一套专为代理工具设计的策略组图标合集：当前共 **362** 个 PNG 图标，覆盖 **247** 个品牌，归入 **21** 个分类。

本项目为独立图标仓库，**362 个图标全部经过统一规范化处理**（512×512 / RGBA / Apple 风格 squircle 圆角），适配 Surge、Loon、Clash Meta / Mihomo、Stash、Quantumult X、Egern 等主流代理客户端。

> **画质规范（贡献与替换标准）**：512×512 方形 PNG，RGBA 模式，Apple 风格 squircle 圆角（圆角半径 ≈ 115px / 约 22.4%），保留原始底色。
> 仓库内全部图标已完成规范化：**362 / 362 均为 512×512 Apple 风格圆角（r≈115px、保留原始底色）**，经 `scripts/optimize-icons.py` 无损重压缩。处理明细与遗留项见 [`docs/references/icon-quality-notes.md`](docs/references/icon-quality-notes.md)。

---

## 🗂 目录与命名规范 / Structure & Naming

### 文件夹结构

所有图标统一采用以下结构：

```
icons/
└── <分类>/
    └── <品牌名>/
        ├── <品牌名>.png          ← 默认图标（必须存在，无任何后缀）
        ├── <品牌名>01.png        ← 变体 1（两位零填充，禁止使用连字符 -）
        ├── <品牌名>02.png        ← 变体 2
        └── ...
```

### 强制规则

1. **每个品牌必须有独立文件夹**，即使目前只有一个图标。
2. **默认图标永远命名为 `<品牌名>.png`**（无任何后缀），且必须存在。
3. **变体必须使用两位零填充数字**：`01`、`02`、`03`…（禁止 `-1`、`-2`、`1`、`2` 等形式）。
4. **品牌名使用 PascalCase**，尽量与 [mihomo-rules](https://github.com/Hawaiine/mihomo-rules/tree/main/ruleset) 的品牌名保持一致。
   - 例外：**官方品牌名的大小写优先**，已知保留官方写法的目录有 `iqiyi`（官方 iQIYI）、`friDay`、`myTVSUPER`；这些名称同时被消费方（mihomo-rules）的配置引用，不得为了「统一大小写」而改动。
5. **特殊字符处理**：`+` → `Plus`（例如 `DisneyPlus`）。
6. **GitHub 文件列表排序**：`<品牌名>.png` 永远排在最上方（`.` < `0`），因此默认图标天然置顶。

### 正确示例

```
icons/Music/Spotify/
├── Spotify.png          ← 默认（原始素材经 scripts/normalize-icons.py 规范化到 512×512）
├── Spotify01.png        ← 变体 1
└── ...

icons/Media/HBOMAX/
├── HBOMAX.png           ← 默认（512×512）
└── HBOMAX01.png         ← 变体 1

icons/Media/Wallpaper/
└── Wallpaper.png        ← 只有 1 个也必须放进品牌文件夹
```

### 错误示例（禁止）

- ❌ `Spotify-1.png` / `Spotify-2.png`（连字符变体）
- ❌ `Spotify1.png`（没有零填充）
- ❌ 直接把 PNG 放在分类目录下（不建品牌文件夹）
- ❌ 只保留品牌的一个变体（多版本品牌必须全部保留）

---

## 🚀 快速开始 / Quick Start

### 1. 通用直链格式

```
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/<分类>/<品牌>/<文件名>.png
```

示例：

```
# 默认图标
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png

# 变体（两位零填充）
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Music/Spotify/Spotify01.png

# 单文件品牌
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Tool/GitHub/GitHub.png
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
|---|---|---|---|
| 🤖 AI | 人工智能服务 | 7 | 7 |
| 🍎 Apple | 苹果生态 | 10 | 10 |
| 🌍 Country | 国家与地区旗帜 | 21 | 49 |
| ₿ Crypto | 加密货币与区块链 | 1 | 4 |
| 🛠 DevOps | 开发运维与云服务 | 6 | 6 |
| 💻 Development | 开发工具 | 1 | 1 |
| ☁️ Drive | 云盘与存储 | 10 | 12 |
| 🎓 Education | 教育平台 | 0 | 0 |
| 💰 Finance | 金融理财 | 0 | 0 |
| 🎮 Game | 游戏平台 | 7 | 13 |
| 🔧 General | 通用策略 | 21 | 48 |
| 🔍 Google | Google 服务 | 11 | 11 |
| 🏥 Health | 健康与运动 | 0 | 0 |
| 🎬 Media | 影音流媒体 | 70 | 82 |
| 🪟 Microsoft | 微软服务 | 4 | 11 |
| 🎵 Music | 音乐服务 | 12 | 12 |
| 📰 News | 新闻与资讯 | 2 | 2 |
| 💳 Payment | 支付 | 5 | 9 |
| 🌐 Proxy | 代理线路与协议 | 4 | 4 |
| 🛒 Shopping | 购物 | 6 | 10 |
| 👥 Social | 社交 | 30 | 35 |
| ⚡ Surge | Surge 应用图标 | 1 | 15 |
| 📡 Telecom | 运营商 | 4 | 7 |
| 🔩 Tool | 工具 | 14 | 14 |
| **合计** | — | **247** | **362** |

`Education` / `Finance` / `Health` 目前为空分类（仅保留目录与 README），便于后续按同一规范补充图标。

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

1. 目录：`icons/<分类>/<品牌名>/`
2. 默认图标：`<品牌名>.png`（无后缀，必须存在）
3. 变体图标：`<品牌名>01.png`、`<品牌名>02.png`（两位零填充，按原顺序编号）
4. 品牌名使用 PascalCase，与 [mihomo-rules](https://github.com/Hawaiine/mihomo-rules) 保持一致
5. 特殊字符：`+` → `Plus`
6. 官方品牌名大小写优先（`iqiyi` / `friDay` / `myTVSUPER` 等保留官方写法，同时是消费方引用的路径）
7. 多版本品牌必须**全部保留**其变体，不要以“清理冗余”为由删除

### 提交流程

1. Fork 本仓库
2. 按规范把图标放入 `icons/<分类>/<品牌名>/`
3. 本地运行 `python3 scripts/ci-validate-icons.py` 确保通过
4. 提交 Pull Request

---

## 📚 参考文档 / References

- [docs/references/icon-quality-notes.md](docs/references/icon-quality-notes.md) — 画质规范、规范化结果、遗留项说明
- [docs/references/icon-research.md](docs/references/icon-research.md) — 品牌分类体系、策略组命名、常见图标来源（中英对照）
- [docs/references/upstream-history.md](docs/references/upstream-history.md) — 上游来源历史参考
- [docs/references/brand-glossary.md](docs/references/brand-glossary.md) — 品牌中英对照表（文件夹名 ↔ 中文显示名）

## 📄 License

MIT License © 2026 [Hawaiine](https://github.com/Hawaiine)

---

## 🔗 相关项目 / Related

- [mihomo-rules](https://github.com/Hawaiine/mihomo-rules) — 代理规则集（本仓库图标的主要消费方）
