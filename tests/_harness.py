#!/usr/bin/env python3
"""tests/_harness.py —— 测试共享基础设施（唯一实现，避免每个测试文件各写一份）。

背景（2026-10-02 维护性审计 §7）
--------------------------------
此前 README/生成器契约测试各自 `shutil.copytree(REPO, ...)`、各自拼
`subprocess.run([sys.executable, 'scripts/...'])`，mutation 场景下的
「建副本 / 造 PNG / 跑校验器」三步全库重复，全部测试近 25% 时间花在这些重复动作上。

本模块提供三件事，**不改变任何生产逻辑**：
  1. `repo_copy()`：统一的仓库副本上下文（忽略 .git / __pycache__ / 中间产物）；
  2. `run_script()`：统一的脚本执行入口（默认在副本 cwd 内）；
  3. `ScratchRepo`：**共享副本 + 定向还原**——按类建一份副本，每个用例只改自己
     碰过的文件，用例结束从 pristine 还原（比「每用例整仓 copytree」快一个量级，
     同时保证用例彼此独立）。

纪律（对应 SKILL 的 validator-claim-verification §3）
----------------------------------------------------
- 任何会写仓库的脚本**只在副本里跑**；
- 还原必须显式列路径（restore(rels)），不允许「整仓还原」掩盖忘记登记的副作用；
- 本模块不缓存任何跨进程结果（无永久缓存 / 无数据库缓存）。
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IGNORE = shutil.ignore_patterns('.git', '__pycache__', '*.pyc')


@contextlib.contextmanager
def repo_copy(prefix='oasisic-copy-'):
    """整仓副本上下文（写操作只发生在副本内）。"""
    with tempfile.TemporaryDirectory(prefix=prefix) as td:
        root = Path(td) / 'repo'
        shutil.copytree(REPO, root, ignore=IGNORE)
        yield root


def run_script(rel, cwd, *args, timeout=300, check=False):
    """在 cwd 内执行脚本（.sh 走 bash，其余走当前解释器）。"""
    cmd = (['bash', str(rel)] if str(rel).endswith('.sh')
           else [sys.executable, str(rel)]) + list(args)
    res = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    if check and res.returncode != 0:
        raise AssertionError('%s 意外失败 (rc=%s)\n%s\n%s'
                             % (rel, res.returncode, res.stdout, res.stderr))
    return res


class ScratchRepo:
    """共享副本：类级建一份，用例级按路径还原。"""

    def __init__(self, prefix='oasisic-scratch-'):
        self._tmp = tempfile.TemporaryDirectory(prefix=prefix)
        self.root = Path(self._tmp.name) / 'repo'
        shutil.copytree(REPO, self.root, ignore=IGNORE)

    def close(self):
        self._tmp.cleanup()

    # --- 原始（pristine）侧读取 -------------------------------------------
    def pristine_bytes(self, rel):
        return (REPO / rel).read_bytes()

    def read(self, rel):
        return (self.root / rel).read_text(encoding='utf-8')

    def write(self, rel, text):
        (self.root / rel).write_text(text, encoding='utf-8')

    def read_bytes(self, rel):
        return (self.root / rel).read_bytes()

    def write_bytes(self, rel, data):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def exists(self, rel):
        return (self.root / rel).exists()

    # --- 还原（必须显式列路径）-------------------------------------------
    def restore(self, *rels):
        """从 pristine 还原指定路径（文件或目录）。恢复文件系统状态，保证用例独立。"""
        for rel in rels:
            dst = self.root / rel
            src = REPO / rel
            if dst.exists() or dst.is_symlink():
                if dst.is_dir() and not dst.is_symlink():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.is_dir():
                    shutil.copytree(src, dst, ignore=IGNORE)
                else:
                    shutil.copy2(src, dst)

    # --- 执行 -------------------------------------------------------------
    def run(self, rel, *args, timeout=300):
        return run_script(rel, self.root, *args, timeout=timeout)

    def validate(self):
        """跑图标契约校验器（唯一校验入口），返回 CompletedProcess。"""
        return self.run('scripts/ci-validate-icons.py')

    # --- JSON 辅助 --------------------------------------------------------
    def load_json(self, rel):
        return json.loads(self.read(rel))

    def mutate_json(self, rel, fn):
        """按函数变换后写回（缩进与仓库习惯一致，末尾保留换行）。"""
        doc = self.load_json(rel)
        fn(doc)
        self.write(rel, json.dumps(doc, ensure_ascii=False, indent=2) + '\n')

    def replace(self, rel, old, new, count=1):
        """替换并**断言真的落地**——变异没命中就报错，绝不允许假阴性。"""
        s = self.read(rel)
        assert old in s, '变异未落地：%s 中找不到 %r（锚点文本已过期）' % (rel, old)
        out = s.replace(old, new, count)
        assert out != s
        self.write(rel, out)


# --- PNG 素材（内容唯一，避免被 SHA-256 唯一性组先拦而掩盖目标组）---------
_PNG_CACHE = {}


def unique_png_bytes(seed=0, size=512):
    """内容唯一的合法 512×512 RGBA PNG 字节（按 seed 缓存，避免重复构建）。

    用 Pillow 生成（比纯 Python 逐像素快两个数量级；本函数的旧版逐像素实现
    是全库 mutation 测试的主要耗时来源）。Pillow 不可用时回退到最小合法 PNG。
    """
    key = (seed, size)
    if key in _PNG_CACHE:
        return _PNG_CACHE[key]
    try:
        from PIL import Image
        im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        px = im.load()
        for y in range(size):
            for x in range(size):
                if (x + y + seed) % 5 == 0:
                    px[x, y] = ((seed * 7 + x) % 256, (x * 3) % 256, (y * 5) % 256, 255)
        buf = io.BytesIO()
        im.save(buf, format='PNG', optimize=True)
        data = buf.getvalue()
    except ImportError:
        data = _minimal_png(seed, size)
    _PNG_CACHE[key] = data
    return data


def _minimal_png(seed, size):
    row = bytes((seed % 256, 0, 0, 0)) * size
    raw = b''.join(b'\x00' + row for _ in range(size))

    def chunk(tag, payload):
        c = struct.pack('>I', len(payload)) + tag + payload
        return c + struct.pack('>I', zlib.crc32(tag + payload) & 0xFFFFFFFF)

    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 6))
            + chunk(b'IEND', b''))


def write_unique_png(root, rel, seed):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(unique_png_bytes(seed))
    return p