#!/usr/bin/env python3
"""normalize-icons.py — 按 Oasisic-Icons 规范统一图标：512×512 / RGBA / Apple 风格 squircle（r=115px） / 保留底色。

强制规范（不可妥协）：
  - 尺寸 512×512 正方形；格式 PNG RGBA；圆角 r=115px（约 22.4%），外侧完全透明
  - 保留原图主体底色，禁止自动抠图/去白底/降色型/有损量化
  - 像素保真：仅允许「几何补边缩放」和「alpha × rounded_mask(r=115)」
    圆角矩形内部每一个像素的 RGB 和 alpha 必须与缩放后的原图完全一致
  - 禁止：背景去除、alpha 阈值、二值化、描边清理、填充镂空、二次圆角、有损压缩
  - 细线/低对比 logo（Docker 类）和带透明镂空 logo（AliCloud 类）需特别注意

幂等：已是 512×512 + RGBA + 四角透明 + 半径正确的文件会被跳过。
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

LANCZOS = getattr(Image, "Resampling", Image).LANCZOS
SIZE = 512
RADIUS = 115  # Apple iOS squircle ≈ 22.37% of 512px = 114.5px；取整 115px
ICONS = Path("icons")


def rounded_mask(size=SIZE, radius=RADIUS):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return np.array(m, dtype=np.float32) / 255.0


def is_compliant(im):
    if im.size != (SIZE, SIZE) or im.mode != "RGBA":
        return False
    a = np.array(im)[..., 3]
    corners_transparent = (
        int(a[0, 0]) == 0 and int(a[0, SIZE - 1]) == 0
        and int(a[SIZE - 1, 0]) == 0 and int(a[SIZE - 1, SIZE - 1]) == 0
    )
    if not corners_transparent:
        return False
    # 圆角半径必须匹配：radius+1 处应为透明；若仍 opaque 说明旧半径 < RADIUS
    return int(a[RADIUS + 1, 0]) == 0


def border_color(rgba):
    """最外圈不透明像素的中位色（非正方形图标补边用）；透明底 logo 返回 None。"""
    a = rgba[..., 3]
    opaque = a > 128
    if opaque.mean() < 0.35:
        return None
    ring = np.zeros_like(opaque)
    ring[0, :] = ring[-1, :] = ring[:, 0] = ring[:, -1] = True
    sel = ring & opaque
    if sel.sum() < 8:
        return None
    return tuple(int(v) for v in np.median(rgba[sel][:, :3], axis=0))


def render(im, mask):
    """按规范渲染：补正方形 → 缩放 512 → 圆角遮罩。返回 RGBA Image。"""
    rgba = im.convert("RGBA")
    w, h = rgba.size
    if w != h:
        side = max(w, h)
        bgc = border_color(np.array(rgba))
        canvas = Image.new("RGBA", (side, side), (bgc + (255,)) if bgc else (0, 0, 0, 0))
        canvas.paste(rgba, ((side - w) // 2, (side - h) // 2), rgba)
        rgba = canvas
    if rgba.size != (SIZE, SIZE):
        rgba = rgba.resize((SIZE, SIZE), LANCZOS)
    arr = np.array(rgba).astype(np.float32)
    arr[..., 3] = arr[..., 3] * mask
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--sheet", metavar="OUT.png")
    ap.add_argument("--sample", type=int, default=8)
    args = ap.parse_args()

    mask = rounded_mask()
    todo, skipped = [], []
    for p in sorted(ICONS.rglob("*.png")):
        im = Image.open(p)
        (skipped if is_compliant(im) else todo).append((p, im.size, im.mode))
    print(f"待处理 {len(todo)} 个 / 已合规跳过 {len(skipped)} 个 / 合计 {len(todo)+len(skipped)}")
    if args.report:
        for p, size, mode in todo[:100]:
            print(f"   - {p}  {size[0]}×{size[1]} {mode}")
        if len(todo) > 100:
            print(f"   ... 其余 {len(todo)-100} 个")

    if args.apply:
        changed = 0
        for p, _, _ in todo:
            render(Image.open(p), mask).save(p, optimize=True)
            changed += 1
        print(f"✓ 已规范化 {changed} 个文件")

    if args.sheet:
        want = [(144, 144), (108, 108), (300, 300), (1000, 1000), (500, 90), (176, 60), (81, 59), (513, 513)]
        by_size = {}
        for p, size, _ in todo:
            by_size.setdefault(size, p)
        picks = [by_size[s] for s in want if s in by_size]
        for p, _, _ in todo:
            if len(picks) >= args.sample:
                break
            if p not in picks:
                picks.append(p)
        cell, pad = 150, 14
        cols = min(4, max(1, len(picks)))
        rows = (len(picks) + cols - 1) // cols
        W = cols * (cell * 2 + pad * 3)
        H = rows * (cell + pad * 3) + 60
        sheet = Image.new("RGB", (W, H), (24, 24, 28))
        d = ImageDraw.Draw(sheet)
        d.text((pad, 16), "BEFORE  (原始)          ->          AFTER  (512x512 RGBA r=115)", fill=(255, 255, 255))
        for i, p in enumerate(picks):
            r, c = divmod(i, cols)
            x0 = c * (cell * 2 + pad * 3) + pad
            y0 = r * (cell + pad * 3) + pad + 44
            src = Image.open(p)
            before = src.convert("RGBA").copy()
            before.thumbnail((cell, cell), LANCZOS)
            after = render(src, mask)
            after.thumbnail((cell, cell), LANCZOS)
            tile_bg = Image.new("RGB", (cell, cell), (64, 64, 72))
            for im, dx in ((before, 0), (after, cell + pad)):
                tile = tile_bg.copy()
                tile.paste(im, ((cell - im.size[0]) // 2, (cell - im.size[1]) // 2), im)
                sheet.paste(tile, (x0 + dx, y0))
            d.text((x0, y0 - 13), f"{p.parent.name}/{p.name}  ({src.size[0]}x{src.size[1]})", fill=(225, 225, 225))
        sheet.save(args.sheet)
        print("对比图:", args.sheet)


if __name__ == "__main__":
    main()