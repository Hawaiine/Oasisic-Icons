#!/usr/bin/env python3
"""normalize-icons.py — 按 Oasisic-Icons 规范统一图标：512×512 / RGBA / Apple 风格 squircle（r=115px） / 保留底色。

强制规范（不可妥协）：
  - 尺寸 512×512 正方形；格式 PNG RGBA；圆角 r=115px（约 22.4%），外侧完全透明
  - 保留原图主体底色，禁止自动抠图/去白底/降色型/有损量化
  - 像素保真：仅允许「几何补边缩放」和「alpha × rounded_mask(r=115)」
    圆角矩形内部每一个像素的 RGB 和 alpha 必须与缩放后的原图完全一致
  - 禁止：背景去除、alpha 阈值、二值化、描边清理、填充镂空、二次圆角、有损压缩
  - 细线/低对比 logo（Docker 类）和带透明镂空 logo（AliCloud 类）需特别注意

幂等：已是 512×512 + RGBA + 四角透明 + 遮罩外完全透明的文件会被跳过。
      （2026-10-01 修订：删除旧的「单像素反推半径」判据——最终 alpha = 原图 alpha ×
       圆角遮罩，无法从结果反推半径；见 is_compliant() docstring。）
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


def outside_mask_alpha(im, mask=None):
    """只读统计：圆角遮罩之外仍「可见」（alpha > 0）的像素数。

    0 = 遮罩外完全透明（符合规范）。该值是判定遮罩是否真的生效的唯一可靠证据：
    mask == 0 处 alpha > 0 ⇒ 文件不是由本模块的 r=115 遮罩产生的（例如历史 r≈99 资产）。

    尺寸非 512×512 时返回 None（合法性由调用方判定）：此前会抛底层
    `ValueError: operands could not be broadcast together`，对直接调用者不可读
    （2026-10-01 Phase 3 加固）。
    """
    if im.size != (SIZE, SIZE):
        return None
    m = rounded_mask() if mask is None else mask
    a = np.array(im.convert("RGBA"))[..., 3]
    return int(((m < 0.5) & (a > 0)).sum())


def is_compliant(im, mask=None):
    """True = 可安全跳过（确定无需再次规范化）；False = 确定存在结构问题。

    语义（2026-10-01 修订，替代旧的单像素半径判据）：

      最终 PNG 的 alpha = 原图 alpha × 圆角遮罩，因此**无法从结果反推原始圆角半径**，
      也不该用「某个点是否透明」推断半径——内容内缩较多的 logo 会让同一半径的文件
      表现不一致（旧实现把正确的 r=115 满幅文件误判为「待处理」，全库误判 225/295）。

    本函数只回答「能否确定该文件不需要再次执行规范化」，判据：

      1. 尺寸 512×512；
      2. 模式 RGBA；
      3. 四角 alpha == 0；
      4. 圆角遮罩之外不存在可见 alpha（mask == 0 且 alpha > 0 ⇒ 不合规）。

    - 「遮罩内 alpha == 0」（logo 自身透明区域）是正常情况，**不**构成不合规；
    - 历史 r≈99 / 内容越界等真实异常会在第 4 条被命中；
    - 无法仅凭内容判定的情况一律**不**返回 False —— 宁可漏掉需要人工复核的异常，
      也不能让 --apply 因误判重写大量正常文件。
    """
    if im.size != (SIZE, SIZE) or im.mode != "RGBA":
        return False
    a = np.array(im)[..., 3]
    corners_transparent = (
        int(a[0, 0]) == 0 and int(a[0, SIZE - 1]) == 0
        and int(a[SIZE - 1, 0]) == 0 and int(a[SIZE - 1, SIZE - 1]) == 0
    )
    if not corners_transparent:
        return False
    return outside_mask_alpha(im, mask) == 0


def noncompliance_reason(im, mask=None):
    """返回不合规原因（可读字符串）；合规返回 None。仅供 --report 展示。"""
    if im.size != (SIZE, SIZE):
        return "尺寸非 512×512: %s" % (im.size,)
    if im.mode != "RGBA":
        return "模式非 RGBA: %s" % im.mode
    a = np.array(im)[..., 3]
    if any(int(a[y, x]) != 0 for y, x in ((0, 0), (0, SIZE - 1), (SIZE - 1, 0), (SIZE - 1, SIZE - 1))):
        return "四角 alpha 非 0"
    n = outside_mask_alpha(im, mask)
    if n:
        return "圆角遮罩外存在可见 alpha: %d px（历史半径 / 未套用遮罩）" % n
    return None


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
        with Image.open(p) as im:
            im.load()
            ok = is_compliant(im, mask)
            reason = None if ok else noncompliance_reason(im, mask)
            (skipped if ok else todo).append((p, im.size, im.mode, reason))
    print(f"待处理 {len(todo)} 个 / 已合规跳过 {len(skipped)} 个 / 合计 {len(todo)+len(skipped)}")
    if args.report:
        for p, size, mode, reason in todo[:100]:
            print(f"   - {p}  {size[0]}×{size[1]} {mode} | {reason}")
        if len(todo) > 100:
            print(f"   ... 其余 {len(todo)-100} 个")

    if args.apply:
        changed = 0
        for p, *_ in todo:
            with Image.open(p) as im:
                im.load()
                out = render(im, mask)
            out.save(p, optimize=True)
            changed += 1
        print(f"✓ 已规范化 {changed} 个文件")

    if args.sheet:
        want = [(144, 144), (108, 108), (300, 300), (1000, 1000), (500, 90), (176, 60), (81, 59), (513, 513)]
        by_size = {}
        for p, size, *_ in todo:
            by_size.setdefault(size, p)
        picks = [by_size[s] for s in want if s in by_size]
        for p, *_ in todo:
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