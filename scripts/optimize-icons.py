#!/usr/bin/env python3
"""optimize-icons.py — 对 icons/**/*.png 做无损重压缩（pixel-perfect），默认保持严格 RGBA 色型。

- 默认：先保证 PNG 色型为 RGBA（像素不变），再用 pyoxipng 重压缩且**不降色型** → 符合项目规范「RGBA」
- --allow-color-reduction：允许 pyoxipng 降为等价的调色板/灰度+透明（体积更小，mode 会变）

依赖：pip install pyoxipng
  （无系统二进制时可 python3 -m pip install --target /tmp/pylibs pyoxipng && PYTHONPATH=/tmp/pylibs ...）
用法：
  python3 scripts/optimize-icons.py [--level 4] [--allow-color-reduction]
"""
import argparse
from pathlib import Path

import oxipng
from PIL import Image

ROOT = Path("icons")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, default=4, help="压缩级别 0-6（越高越慢，默认 4）")
    ap.add_argument("--allow-color-reduction", action="store_true",
                    help="允许降色型（体积更小，但 PNG 模式可能不再是 RGBA）")
    args = ap.parse_args()

    files = sorted(ROOT.rglob("*.png"))
    before = sum(p.stat().st_size for p in files)
    ok = fail = fixed = 0
    for p in files:
        if not args.allow_color_reduction and Image.open(p).mode != "RGBA":
            Image.open(p).convert("RGBA").save(p, optimize=True)   # 统一回 RGBA（像素不变）
            fixed += 1
        try:
            kw = dict(level=args.level, strip=oxipng.StripChunks.safe(), optimize_alpha=True)
            if not args.allow_color_reduction:
                kw["color_type_reduction"] = False
            oxipng.optimize(str(p), **kw)
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