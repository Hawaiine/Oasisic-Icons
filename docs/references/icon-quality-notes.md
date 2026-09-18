# Icon Quality Notes

> 最后扫描：2026-09-18（图标规范化：全部统一为 512×512 之后）
> 扫描方法：遍历 `icons/**/*.png`，读取 Pillow 报告的尺寸 / 色彩模式，并统计文件体积
> 扫描范围：424 个 PNG（252 个品牌目录 / 24 个分类）

## 1. 项目标准

贡献与替换图标时的目标标准：

- 尺寸：**512×512** 正方形
- **形状**：圆角矩形（Apple 风格 squircle / 超椭圆），圆角半径 ≈ **115px**（约 22.4%，对齐 Apple iOS 图标视觉曲线），圆角外为透明
- 背景：**保留原始底色**（不做背景抠除，白色底图不得误杀成透明）
- 模式：**RGBA**（`scripts/optimize-icons.py` 重压缩时显式禁用降色型，仓库内全部为 RGBA）
- 体积：单文件 ≤ 300KB（当前平均 ≈65KB；`scripts/optimize-icons.py` 无损重压缩，**不做有损量化**）

## 2. 现状（规范化后）

| 项目 | 结果 |
|------|------|
| 尺寸 | **424 / 424 = 512×512**（已全量统一） |
| 圆角 | 统一 r=115px（≈22.4%，Apple squircle），四角透明（`alpha=0`） |
| 用户手动更新的图标 | 71 个已合规文件**像素未改动**（规范化脚本自动跳过） |
| 规范化处理 | 354 个文件由 `scripts/normalize-icons.py` 从原始尺寸（144×144 / 108×108 / 非方形）转换 |
| 窄条字标 | 4 个（CatchPlay-Plus / HOY / TVer / VideoMarket）由 `scripts/normalize-strips.py` 处理：裁到内容后以白色圆角底块承载（保留原始字标颜色，不抠背景） |
| 体积 | 合计 ≈ 27.7 MB；平均 64KB / 中位 58KB / 最大 292KB（`icons/Telecom/ChinaBroadnet/ChinaBroadnet.png`） |
| 模式分布 | RGBA 424（其余色型 0） |

## 3. 需要留意

- `icons/Media/VideoMarket/VideoMarket.png`：字标在白色底块上对比度偏低（原始素材即浅灰字），如介意可从上游取新素材。
- 部分图标由小尺寸上采样得到（原 144×144 / 108×108 → 512×512），在超大尺寸下会显得偏软。
  需要超清版本时应先替换源图（放入对应品牌目录的默认文件名），再运行规范化脚本。
- 仓库**不做有损量化**（不改变任何图标的像素内容）：当前最大单文件 292KB（`icons/Telecom/ChinaBroadnet/ChinaBroadnet.png`），客户端按 URL 按需拉取，无实际负担。如需从源头减小体积，应替换为更小/更干净的源图后重跑 `scripts/normalize-icons.py`。

## 4. 工具

| 脚本 | 作用 |
|------|------|
| `scripts/normalize-icons.py` | 按标准规范化：`--report` 查看待处理 / `--sheet out.png` 生成前后对比 / `--apply` 写入（幂等） |
| `scripts/normalize-strips.py` | 处理窄条字标类图标（裁内容 + 白色圆角底块） |
| `scripts/optimize-icons.py` | pyoxipng 无损重压缩（`pip install pyoxipng`） |
| `scripts/ci-validate-icons.py` | CI 校验：PNG 合法性、目录/命名规范、订阅 JSON 一致性 |

## 5. 历史记录

| 时间 | 事项 |
|------|------|
| 2026-07-25 | 首次扫描：发现 500×90 / 120×26 / 176×60 / 81×59 等异常尺寸图标 |
| 2026-09-17 | 结构重构（`<分类>/<品牌>/<品牌>.png` + 两位零填充变体），并把被误删的多版本变体从 `2e771d1` 恢复 |
| 2026-09-18 | 规范化：全量统一 512×512 RGBA（圆角 r=115 (Apple squircle)），并做无损重压缩 |

本仓库为独立最高上游，所有图标已统一规范化；本文只记录处理方式。