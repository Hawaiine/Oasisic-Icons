# 上游来源参考 / Upstream Sources Reference

> **重要声明**：本文档仅作历史追溯与素材来源记录，**不构成任何同步承诺**。  
> Oasisic-Icons 现已确立为**独立最高上游**，不再自动同步任何外部图标库。  
> 如需新增/替换图标，请直接提交 PR 到本仓库，并遵循 `README.md` 与 `docs/references/icon-quality-notes.md` 的规范。

---

## 1. 早期素材来源 / Early Sources

### 1.1 Qure（Koolson/Qure）

- **仓库地址**：https://github.com/Koolson/Qure
- **使用时期**：项目早期至 2026-09-17 结构重构前
- **素材规模**：曾为主要图标来源，覆盖大量主流品牌
- **目录结构**：按客户端分类（`Color/`、`Mini/` 等），命名与本仓库规范不同
- **与本仓库的关系**：
  - 早期直接引用 Qure 对应目录的 PNG
  - 2026-09-17 结构重构后，所有图标已统一归入 `icons/<分类>/<品牌>/<品牌>.png` 结构
  - 2026-09-18 全量规范化：全部转为 512×512 / RGBA / r=115 Apple squircle
  - **2026-09-19 正式确立本仓库为独立最高上游，停止自动同步**

### 1.2 Semporia/Hand-Painted-icon

- **仓库地址**：https://github.com/Semporia/Hand-Painted-icon
- **使用时期**：项目早期至 2026-09-17
- **素材规模**：手绘风格图标集，部分品牌仅有此源有素材
- **特点**：风格统一，但数量少于 Qure
- **与本仓库的关系**：
  - 早期作为 Qure 的补充来源，填补部分品牌空白
  - 2026-09 重构后，所有素材已融入本仓库目录结构
  - **Semporia 映射条目在重构过程中被清理**：原因是在统一目录结构后，原映射表已失去意义；且该仓库更新频率低、风格与本仓库规范化后的视觉标准差异较大，继续维护映射条目反而增加噪音
  - 现仅保留历史记录，不再维护映射关系

### 1.3 官方品牌资源

- **来源**：各品牌官方网站、Favicon、公开 CDN（如 `brandmark.io`、品牌官网 `/favicon.ico`）
- **特点**：像素级准确，但尺寸/色型/圆角/底色不统一
- **与本仓库的关系**：
  - 作为权威依据，优先于第三方图标集
  - 经 `scripts/normalize-icons.py` 统一为 512×512 / RGBA / r=115px Apple squircle
  - 本仓库保留从官方资源补充/替换图标的渠道，无需经过第三方中转

---

## 2. 自动同步机制的历史 / History of Auto-Sync

### 2.1 曾经存在的同步机制

| 组件 | 路径/标识 | 用途 | 状态 |
|------|----------|------|------|
| 上游映射表 | `config/icon-mapping.json` | 记录品牌 → Qure/Semporia 路径映射 | **已删除**（2026-09-19） |
| 同步脚本 | `scripts/sync-upstream.sh` | 每日自动从上游拉取图标 | **已删除**（2026-09-19） |
| CI 工作流 | `.github/workflows/daily-sync.yml` | GitHub Actions 每日 08:00 CST 触发同步 | **已删除**（2026-09-19） |

### 2.2 映射条目数量变化

- **峰值**：约 200+ 条目（覆盖 Qure Color/Mini 目录 + Semporia 部分品牌）
- **重构后**：条目逐步失效——因目录结构统一、文件名规范化，原始映射路径不再适用
- **最终清理**：2026-09-19 随 `icon-mapping.json` 删除而彻底移除

### 2.3 为何停止自动同步

1. **质量不一致**：上游图标尺寸、色型、圆角、底色各异，每次同步都需要大量人工校正
2. **规范漂移**：上游更新会破坏本仓库已建立的命名/结构/质量规范
3. **维护成本**：映射表需要持续维护，但收益递减（本仓库已覆盖 95%+ 常用品牌）
4. **独立可控**：本仓库已完成全量规范化（512×512 / RGBA / r=115），成为事实上的最高上游

---

## 3. 关键时间线 / Key Milestones

| 时间 | 事件 | 影响 |
|------|------|------|
| 2026-07-25 | 首次全量扫描，发现异常尺寸图标（500×90、120×26、176×60、81×59 等） | 确认需要规范化 |
| 2026-09-17 | 结构重构：统一为 `icons/<分类>/<品牌>/<品牌>.png` + 两位零填充变体；恢复被误删的多版本变体（从 `2e771d1` 基线） | 目录结构标准化 |
| 2026-09-18 | 全量规范化：全部图标转为 512×512 / RGBA / r=115 (Apple squircle)；执行无损重压缩（pyoxipng） | 画质统一 |
| 2026-09-18 | 确立「严格 RGBA」规范：禁止降色型；体积指标改为 ≤300KB | 规范升级 |
| 2026-09-18 | Surge 去重：删除 `Surge01.png`（与默认图同内容），顺延编号 02→01 … 15→14 | 去重完成 |
| 2026-09-19 | 确立本仓库为独立最高上游；删除 `config/icon-mapping.json`、`scripts/sync-upstream.sh`、`.github/workflows/daily-sync.yml` | **停止自动同步** |
| 2026-09-19 | 圆角半径从 r=99 更新为 r=115（Apple squircle ≈22.4%），对齐 iOS 图标视觉曲线 | 规范细化 |
| 2026-09-19 | 规范文档全面升级：新增「强制输出规范」「像素保真红线」「禁止清单」「自检流程」 | 规范文档化 |
| 2026-09-19 | README「自动化同步说明」改为「发布与使用」；新增 `docs/references/upstream-history.md` 和 `docs/references/brand-glossary.md` | 文档独立化 |

---

## 4. 当前规范与建议 / Current Standards & Recommendations

### 4.1 新增图标准备流程

1. 优先从**官方品牌资源**获取素材（官网、Favicon、公开 CDN）
2. 运行 `python3 scripts/normalize-icons.py --apply` 规范化到 512×512 / RGBA / r=115
3. 运行 `python3 scripts/optimize-icons.py` 无损重压缩
4. 运行 `python3 scripts/ci-validate-icons.py` 校验通过
5. 提交 PR 到本仓库

### 4.2 替代 upstream 的素材获取建议

| 来源 | 用途 | 说明 |
|------|------|------|
| 官方品牌官网 / favicon | 权威素材 | 优先采用 |
| brandmark.io | 官方 logo 下载 | 仅用于缺失品牌的兜底 |
| simple-icons | 矢量图标补充 | 矢量图转 PNG 后规范化 |
| 用户贡献 PR | 社区素材 | 直接提交到本仓库 |

### 4.3 不再维护的映射关系

以下外部源不再有任何自动或手动的映射维护：

- ~~Qure（Koolson/Qure）~~ — 历史参考，不再同步
- ~~Semporia/Hand-Painted-icon~~ — 历史参考，不再同步
- ~~任何其他第三方图标集~~ — 如需引用，请直接 PR 到本仓库

---

## 5. 相关文档 / Related Documents

- `README.md` — 项目主文档（规范、使用方式、贡献指南）
- `docs/references/icon-quality-notes.md` — 画质规范、规范化结果、遗留项说明
- `docs/references/icon-research.md` — 品牌分类体系、策略组命名、常见图标来源（中英对照）
- `docs/references/brand-glossary.md` — 品牌文件夹名 ↔ 中文显示名对照表
- `scripts/normalize-icons.py` — 规范化脚本（512×512 / RGBA / r=115）
- `scripts/optimize-icons.py` — 无损重压缩脚本（不降色型）

---

**最后更新**：2026-09-19  
**维护者**：Hawaiine / Oasisic-Icons Contributors
