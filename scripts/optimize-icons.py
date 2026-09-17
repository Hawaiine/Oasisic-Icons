#!/usr/bin/env python3
"""optimize-icons.py — 用 pyoxipng 对 icons/**/*.png 做无损重压缩（不改像素，可能降色型以省体积）。

依赖：pip install pyoxipng
用法：python3 scripts/optimize-icons.py [--level 4]
"""
import argparse
from pathlib import Path

import oxipng

ROOT = Path("icons")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, default=4, help="压缩级别 0-6（越高越慢，默认 4）")
    args = ap.parse_args()

    files = sorted(ROOT.rglob("*.png"))
    before = sum(p.stat().st_size for p in files)
    ok = fail = 0
    for p in files:
        try:
            oxipng.optimize(str(p), level=args.level, strip=oxipng.StripChunks.safe(), optimize_alpha=True)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            fail += 1
            print(f"  ! {p}: {exc}")
    after = sum(p.stat().st_size for p in files)
    print(f"无损优化完成：{ok} 成功 / {fail} 失败")
    print(f"体积 {before/1e6:.1f} MB → {after/1e6:.1f} MB（节省 {(before-after)/before*100:.1f}%）")


if __name__ == "__main__":
    main()