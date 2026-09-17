#!/usr/bin/env python3
"""窄条/字标类图标：裁到内容 → 用「主色反色底」补成方形色块 → 512×512 → 圆角 r=99。

规则：取内容不透明像素的主色（字标颜色），按亮度选对比底色——
  亮色字标 → 深色底（同色系压暗 78%）；暗色字标 → 白底。
这样在方形画布里既填满、又保证字标可读（不做背景抠除，不改字标颜色）。

适用：
  icons/Media/CatchPlay-Plus/CatchPlay-Plus.png
  icons/Media/HOY/HOY.png
  icons/Media/TVer/TVer.png
  icons/Media/VideoMarket/VideoMarket.png
"""
import sys, collections
from pathlib import Path
from PIL import Image
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import importlib.util
spec = importlib.util.spec_from_file_location("nz", Path(__file__).parent / "normalize-icons.py")
nz = importlib.util.module_from_spec(spec); spec.loader.exec_module(nz)

STRIPS = ["icons/Media/CatchPlay-Plus/CatchPlay-Plus.png", "icons/Media/HOY/HOY.png",
          "icons/Media/TVer/TVer.png", "icons/Media/VideoMarket/VideoMarket.png"]
MARGIN = 0.10


def dominant_color(rgba):
    a = rgba[..., 3] > 200
    if a.sum() < 16:
        return (255, 255, 255)
    px = (rgba[a][:, :3] // 24 * 24 + 12)
    cnt = collections.Counter(map(tuple, px.tolist()))
    return tuple(int(v) for v in cnt.most_common(1)[0][0])


def lum(c):
    r, g, b = [v / 255 for v in c]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def tile_bg(main):
    return tuple(int(round(v * 0.22)) for v in main) if lum(main) > 0.55 else (255, 255, 255)


def redo(path, mask):
    im = Image.open(path).convert("RGBA")
    arr = np.array(im)
    ys, xs = np.nonzero(arr[..., 3] > 8)
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    content = im.crop(bbox)
    cw, ch = content.size
    inner = int(round(nz.SIZE * (1 - 2 * MARGIN)))
    scale = min(inner / cw, inner / ch)
    content = content.resize((max(1, round(cw * scale)), max(1, round(ch * scale))), nz.LANCZOS)
    main = dominant_color(np.array(im))
    bgc = tile_bg(main)
    canvas = Image.new("RGBA", (nz.SIZE, nz.SIZE), bgc + (255,))
    canvas.paste(content, ((nz.SIZE - content.size[0]) // 2, (nz.SIZE - content.size[1]) // 2), content)
    out = np.array(canvas).astype(np.float32)
    out[..., 3] = out[..., 3] * mask
    Image.fromarray(out.astype(np.uint8), "RGBA").save(path, optimize=True)
    return main, bgc, bbox, content.size


if __name__ == "__main__":
    mask = nz.rounded_mask()
    for rel in STRIPS:
        p = Path(rel)
        main, bgc, bbox, csize = redo(p, mask)
        print(f"{rel}: 裁剪{bbox} → 内容{csize[0]}×{csize[1]} → 512×512；主色{main} 亮度{lum(main):.2f} → 底色{bgc}")