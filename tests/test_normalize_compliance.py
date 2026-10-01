#!/usr/bin/env python3
"""normalize-icons.py 合规判据（is_compliant）测试（2026-10-01 判据修订）。

背景
----
旧实现用「单像素 `(RADIUS + 1, 0)` 是否透明」反推圆角半径。但最终 PNG 的
alpha = 原图 alpha × 圆角遮罩，该像素是否透明只取决于**内容是否覆盖**，与半径无关：

  - 正确的 r=115 满幅文件被判 False（实测全库误判 225/295，`--apply` 会重写它们）；
  - 内容内缩（留白较多）的文件反而被判 True。

新语义（本测试锁定的契约）
--------------------------
    True  = 可安全跳过（确定无需再次规范化）
    False = **确定**存在结构问题（尺寸 / 模式 / 四角 alpha / 遮罩外可见 alpha）

无法仅凭内容判定的情况一律**不**返回 False：宁可漏掉需要人工复核的异常，
也不能让 `--apply` 因误判重写大量正常文件。
"""
import importlib.util
import unittest
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "normalize-icons.py"


def load_normalizer():
    spec = importlib.util.spec_from_file_location("normalize_icons", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NZ = load_normalizer()
MASK = NZ.rounded_mask()


def mask_of(radius):
    m = Image.new("L", (NZ.SIZE, NZ.SIZE), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, NZ.SIZE - 1, NZ.SIZE - 1], radius=radius, fill=255)
    return np.array(m, dtype=np.float32) / 255.0


def apply_mask(im, mask):
    arr = np.array(im.convert("RGBA")).astype(np.float32)
    arr[..., 3] = arr[..., 3] * mask
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def full_bleed():
    return Image.new("RGBA", (NZ.SIZE, NZ.SIZE), (200, 30, 40, 255))


def content_inset():
    """四周留白的 logo（遮罩内也有大量透明区域）。"""
    im = Image.new("RGBA", (NZ.SIZE, NZ.SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(im).rectangle([160, 200, 350, 320], fill=(10, 90, 210, 255))
    return im


class CompliantDetectionTests(unittest.TestCase):
    def test_full_bleed_r115_is_compliant(self):
        im = NZ.render(full_bleed(), MASK)
        self.assertIsNone(NZ.noncompliance_reason(im, MASK))
        self.assertTrue(NZ.is_compliant(im, MASK))

    def test_content_inset_logo_is_compliant(self):
        """内容内缩不得被误判（旧实现正是在这里表现不一致）。"""
        im = NZ.render(content_inset(), MASK)
        self.assertEqual(NZ.outside_mask_alpha(im, MASK), 0)
        self.assertTrue(NZ.is_compliant(im, MASK))

    def test_cannot_infer_radius_does_not_mean_non_compliant(self):
        """无法凭内容判定半径时不得返回 False（留白 ≠ 不合规）。"""
        im = NZ.render(content_inset(), MASK)
        self.assertFalse(NZ.outside_mask_alpha(im, MASK) > 0)
        self.assertTrue(NZ.is_compliant(im, MASK))

    def test_alpha_outside_mask_is_non_compliant(self):
        im = NZ.render(full_bleed(), MASK)
        arr = np.array(im)
        arr[5:20, 5:20, 3] = 255          # 在遮罩之外（左上角区域）制造可见 alpha
        broken = Image.fromarray(arr, "RGBA")
        self.assertGreater(NZ.outside_mask_alpha(broken, MASK), 0)
        self.assertFalse(NZ.is_compliant(broken, MASK))
        self.assertIn("遮罩外", NZ.noncompliance_reason(broken, MASK))

    def test_legacy_radius_is_non_compliant(self):
        """历史 r≈99 资产：遮罩外残留 alpha ⇒ 检出，无需反推半径。"""
        legacy = apply_mask(full_bleed(), mask_of(99))
        self.assertGreater(NZ.outside_mask_alpha(legacy, MASK), 0)
        self.assertFalse(NZ.is_compliant(legacy, MASK))

    def test_opaque_corner_is_non_compliant(self):
        self.assertFalse(NZ.is_compliant(full_bleed(), MASK))
        self.assertEqual(NZ.noncompliance_reason(full_bleed(), MASK), "四角 alpha 非 0")

    def test_wrong_size_is_non_compliant(self):
        im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        self.assertFalse(NZ.is_compliant(im, MASK))
        self.assertIn("尺寸", NZ.noncompliance_reason(im, MASK))

    def test_non_rgba_is_non_compliant(self):
        self.assertFalse(NZ.is_compliant(Image.new("RGB", (NZ.SIZE, NZ.SIZE), (1, 2, 3)), MASK))

    def test_outside_mask_alpha_is_size_safe(self):
        """非 512×512 输入返回 None（明确的"无法判定"），而不是抛底层广播异常。

        2026-10-01 Phase 3：此前外边界的统计 helper 对整个数组做 mask 比较，
        非 512 输入会抛 numpy broadcasting / ValueError，把「尺寸不合法」伪装成崩溃。
        """
        for size in ((256, 256), (512, 511), (1024, 1024)):
            with self.subTest(size=size):
                self.assertIsNone(NZ.outside_mask_alpha(Image.new("RGBA", size, (0, 0, 0, 255)), MASK))
        # full_bleed 是「未套遮罩」的满幅图；套上遮罩后越界 alpha 必须为 0
        self.assertEqual(NZ.outside_mask_alpha(apply_mask(full_bleed(), MASK), MASK), 0)
        self.assertGreater(NZ.outside_mask_alpha(full_bleed(), MASK), 0)


class IdempotencyTests(unittest.TestCase):
    def test_render_is_idempotent_on_masked_file(self):
        """已遮罩文件再 render 一次像素不变 ⇒ --apply 对合规文件无像素影响。"""
        once = NZ.render(full_bleed(), MASK)
        twice = NZ.render(once, MASK)
        self.assertTrue(np.array_equal(np.array(once), np.array(twice)))


class RealRepositoryTests(unittest.TestCase):
    """真实仓库回归保护：正确资产不得被误判，误判面必须收敛。"""

    def _load(self, rel):
        with Image.open(REPO / rel) as im:
            im.load()
            return im.copy()

    def test_known_good_assets_are_compliant(self):
        for rel in ("icons/Alibaba/AlibabaCloud/AlibabaCloud.png",
                    "icons/Tencent/TencentCloud/TencentCloud.png",
                    "icons/Baidu/Tieba/Tieba.png",
                    "icons/Media/Netflix/Netflix.png"):
            with self.subTest(rel=rel):
                self.assertTrue(NZ.is_compliant(self._load(rel), MASK),
                                f"{rel} 不应被判为待处理")

    def test_false_positive_surface_stays_small(self):
        """旧判据误判 225/295；新判据只应命中真实异常（远小于 5%）。"""
        files = sorted((REPO / "icons").rglob("*.png"))
        flagged = 0
        for p in files:
            with Image.open(p) as im:
                im.load()
                if not NZ.is_compliant(im, MASK):
                    flagged += 1
        self.assertLess(flagged, len(files) * 0.05,
                        "待处理面异常膨胀（疑似判据回归）：%d/%d" % (flagged, len(files)))

    def test_repo_assets_have_no_alpha_outside_mask_or_are_known_legacy(self):
        """任何被标记的文件都必须能在 --report 里给出明确原因。"""
        for p in sorted((REPO / "icons").rglob("*.png")):
            with Image.open(p) as im:
                im.load()
                ok = NZ.is_compliant(im, MASK)
                if not ok:
                    self.assertIsNotNone(NZ.noncompliance_reason(im, MASK),
                                         f"{p} 被标记但无原因")


if __name__ == "__main__":
    unittest.main()
