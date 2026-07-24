# Icon Quality Notes

> 扫描日期：2026-07-25
> 扫描方法：读取 PNG IHDR 区块，校验宽高尺寸

## 异常尺寸图标清单

以下图标尺寸不符合推荐标准（推荐 512×512 方形 PNG），建议后续替换为 512 方图。

| 路径 | 尺寸 | 问题 | 备注 |
|------|------|------|------|
| `icons/Media/CatchPlay-Plus-2.png` | 500×90 | 窄条（max/min=5.6），高度<100 | 同 CatchPlay-Plus-1 已正常 |
| `icons/Media/DMMTV-1.png` | 120×26 | 窄条（max/min=4.6），高度<100 | 已知问题 |
| `icons/Media/HOY.png` | 176×60 | 窄条（max/min=2.9），高度<100 | 已知问题 |
| `icons/Media/TVer.png` | 81×59 | 宽高均<100，非正方形 | 已知问题 |
| `icons/Media/VideoMarket.png` | 320×52 | 窄条（max/min=6.2），高度<100 | 已知问题 |
| `icons/DevOps/Docker.png` | 512×513 | 非正方形（差 1px） | 视觉几乎无影响，可忽略 |

## 说明

- 以上图标来自上游 `Semporia/Hand-Painted-icon` 或 `Qure` 源，非本仓库原创。
- 本清单仅记录异常，不替换实际 PNG 文件。替换时应优先从上游获取更新版本，或自绘 512×512 方图。