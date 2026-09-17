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
  <img src="https://img.shields.io/badge/icons-336-blue?style=flat-square" alt="Icons Count">
  <img src="https://img.shields.io/badge/brands-254-green?style=flat-square" alt="Brands Count">
  <img src="https://img.shields.io/badge/categories-24-orange?style=flat-square" alt="Categories Count">
</p>

---

## 📖 简介 / Introduction

**Oasisic-Icons** 是一套专为代理工具设计的策略组图标合集，包含 **336** 个 PNG 图标，覆盖 **254** 个品牌，归入 **24** 个分类。

> 所有图标均为 **512×512 RGBA 圆角矩形**（圆角半径 ≈ 99px），保留原始底色。适配 Surge、Loon、Clash Meta / Mihomo、Quantumult X 等主流代理客户端。

---

## 🗂 目录与命名规范 / Structure & Naming

### 文件夹结构

所有图标统一采用以下结构：

```
icons/
└── <分类>/
    └── <品牌名>/
        ├── <品牌名>.png          ← 默认主版本（必须存在，无任何后缀）
        ├── <品牌名>01.png        ← 变体1（两位零填充，禁止使用连字符 -）
        ├── <品牌名>02.png        ← 变体2
        └── ...
```

### 强制规则

1. **每个品牌必须有独立文件夹**，即使目前只有一个图标。
2. **默认图标永远命名为 `<品牌名>.png`**（无任何后缀）。
3. **变体必须使用两位零填充数字**：`01`、`02`、`03`...（禁止 `-1`、`-2`、`1`、`2` 等形式）。
4. **品牌名使用 PascalCase**，尽量与 [mihomo-rules](https://github.com/Hawaiine/mihomo-rules/tree/main/ruleset) 的品牌名保持一致。
5. **特殊字符处理**：`+` → `Plus`（例如 `Disney-Plus`）。
6. **GitHub 文件列表排序**：`<品牌名>.png` 永远排在最上方（`.` < `0`）。

### 正确示例

```
icons/Music/Spotify/
├── Spotify.png          ← 默认
├── Spotify01.png
└── Spotify02.png

icons/Media/Netflix/
└── Netflix.png          ← 只有一个也必须放进文件夹
```

### 错误示例（禁止）

- ❌ `Spotify-1.png` / `Spotify-2.png`
- ❌ `Spotify1.png`（没有零填充）
- ❌ 直接把文件放在分类目录下（不建品牌文件夹）

---

## 🚀 快速开始 / Quick Start

### 通用直链格式

```
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/<分类>/<品牌>/<文件名>.png
```

示例：
```
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Music/Spotify/Spotify.png
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix01.png
```

### Surge / Loon 批量订阅

```yaml
# Surge
[Script]
http-request ^https?://raw\.githubusercontent\.com/Hawaiine/Oasisic-Icons/main/icons/.* script-path = https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/config/surge-icon.json

# Loon
[Plugin]
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/config/surge-icon.json type=omicron
```

### Clash Meta / Mihomo 单独配置示例

```yaml
# config.yaml
proxy-groups:
  - name: "🎬 Media"
    type: select
    proxies:
      - "Proxy"
    icons:
      - "Netflix: https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png"
      - "YouTube: https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Google/YouTube/YouTube.png"
```

### Quantumult X 示例

```
[revert]
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/ = reject

[mitm]
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/ = mitm

[policy]
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/ = policy-group-icon
```

---

## 📁 图标分类列表 / Categories

| 分类 | 说明 | 图标数 |
|------|------|--------|
| 🤖 AI | 人工智能服务 | 8 |
| 🍎 Apple | 苹果生态 | 12 |
| 🌍 Country | 国家与地区旗帜 | 50 |
| ₿ Crypto | 加密货币 | 4 |
| 🛠 DevOps | 开发运维工具 | 7 |
| 💻 Development | 开发工具 | 1 |
| 📁 Drive | 云存储服务 | 10 |
| 🎓 Education | 教育 | 0 |
| 💰 Finance | 金融 | 0 |
| 🎮 Game | 游戏平台 | 7 |
| ⚙️ General | 通用图标 | 56 |
| 🔍 Google | 谷歌服务 | 11 |
| 🏥 Health | 健康 | 0 |
| 🎬 Media | 流媒体与视频 | 70 |
| 🪟 Microsoft | 微软服务 | 3 |
| 🎵 Music | 音乐服务 | 12 |
| 📰 News | 新闻资讯 | 3 |
| 💳 Payment | 支付工具 | 5 |
| 🌐 Proxy | 代理服务 | 4 |
| 🛒 Shopping | 购物平台 | 6 |
| 💬 Social | 社交网络 | 32 |
| ⚡ Surge | Surge 专属 | 16 |
| 📱 Telecom | 电信运营商 | 4 |
| 🔧 Tool | 实用工具 | 15 |

---

## 🤖 自动化同步说明 / Automated Sync

本项目通过 GitHub Actions 实现自动化上游图标同步：

1. **每日自动同步**：从 Qure、Semporia 等上游源同步最新图标。
2. **自动校验**：CI 会自动检查 PNG 合法性、文件夹结构、变体命名规范、JSON 一致性。
3. **自动生成**：每次同步后自动重新生成 `surge-icon.json` 和分类 README。

---

## 🤝 贡献指南 / Contributing

### 图标质量要求

- **尺寸**：512×512 像素
- **格式**：PNG，RGBA 模式
- **形状**：圆角矩形，圆角半径 ≈ 99px
- **背景**：保留原始底色（不要误杀成透明）
- **大小**：建议 < 50KB

### 命名规范

1. 默认图标：`Brand.png`（无后缀）
2. 变体图标：`Brand01.png`、`Brand02.png`（两位零填充）
3. 品牌名使用 PascalCase，与 mihomo-rules 保持一致
4. 特殊字符：`+` → `Plus`

### 提交流程

1. Fork 本仓库
2. 按规范添加图标到对应分类文件夹
3. 确保 CI 通过
4. 提交 Pull Request

---

## 📄 License

MIT License © 2026 [Hawaiine](https://github.com/Hawaiine)

---

## 🔗 相关项目 / Related

- [mihomo-rules](https://github.com/Hawaiine/mihomo-rules) — 代理规则集
- [Qure](https://github.com/Koolson/Qure) — 上游图标源
- [Semporia/Hand-Painted-icon](https://github.com/Semporia/Hand-Painted-icon) — 上游图标源
