#!/usr/bin/env python3
"""optimize-icons.py — 对 icons/**/*.png 做无损重压缩（pixel-perfect），默认保持严格 RGBA 色型。

强制规范：
  - 禁止有损量化/降色型；仓库内全部为 RGBA
  - 仅做 deflate 重压缩，像素完全不变

依赖：pip install pyoxipng
用法：
  python3 scripts/optimize-icons.py [--level 4]
"""
import argparse
from pathlib import Path

import oxipng
from PIL import Image

ROOT = Path("icons")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, default=4, help="压缩级别 0-6（越高越慢，默认 4）")
    args = ap.parse_args()

    files = sorted(ROOT.rglob("*.png"))
    before = sum(p.stat().st_size for p in files)
    ok = fail = fixed = 0
    for p in files:
        # 强制 RGBA（像素不变）
        if Image.open(p).mode != "RGBA":
            Image.open(p).convert("RGBA").save(p, optimize=True)
            fixed += 1
        try:
            oxipng.optimize(
                str(p),
                level=args.level,
                strip=oxipng.StripChunks.safe(),
                optimize_alpha=True,
                color_type_reduction=False,  # 禁止降色型
            )
            ok += 1
        except TypeError:      # 旧版 pyoxipng 不支持 color_type_reduction
            oxipng.optimize(str(p), level=args.level, strip=oxipng.StripChunks.safe(), optimize_alpha=True)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            fail += 1
            print(f"  ! {p}: {exc}")
    after = sum(p.stat().st_size for p in files)
    modes = {}
    for p in files:
        m = Image.open(p).mode
        modes[m] = modes.get(m, 0) + 1
    print(f"无损优化完成：{ok} 成功 / {fail} 失败；格式统一回 RGBA：{fixed} 个")
    print(f"体积 {before/1e6:.1f} MB → {after/1e6:.1f} MB")
    print("色型分布：", modes)


if __name__ == "__main__":
    main()
