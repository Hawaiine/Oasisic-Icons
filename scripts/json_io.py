#!/usr/bin/env python3
"""统一 JSON / 文本读取入口（唯一实现，禁止各脚本各写一份）。

为什么存在
----------
此前每个脚本各自 `json.loads(path.read_text())`，损坏的 SSOT 会抛原始
`JSONDecodeError` traceback：退出码仍是 1（fail-closed 正确），但维护者看到的是
Python 栈而不是「哪个文件、哪一行、什么原因」。审计（2026-10-02）确认这是
维护者体验问题，本模块统一归因。

契约
----
- **fail-fast**：读不到 / 解析不了 → 抛 `JsonLoadError`，**不返回空 dict / 空 list**。
  历史上 `ssot_brands()` 等处的 broad `except` 会把「SSOT 损坏」退化成「0 个品牌」，
  让后续校验静默变成 no-op —— 那是最坏的一类隐藏。
- **不吞异常**：不捕获 `KeyboardInterrupt` / `SystemExit`。
- 错误信息包含：绝对/相对路径、行列位置、原因。

调用方约定
----------
库函数（被测试 import）让 `JsonLoadError` 向上传播；CLI 入口用
`read_json_or_exit()` 把异常转成 `✗ ...` + 退出码 1。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonLoadError(Exception):
    """JSON 读取/解析失败的统一异常（含路径、行列、原因）。"""

    def __init__(self, path, reason: str, line: int | None = None, col: int | None = None):
        self.path = Path(path)
        self.reason = reason
        self.line = line
        self.col = col
        loc = ''
        if line is not None:
            loc = ' 第 %d 行第 %d 列' % (line, col if col is not None else 0)
        super().__init__('JSON 读取失败: %s%s — %s' % (self.path, loc, reason))


def describe(exc: JsonLoadError, what: str = 'JSON') -> str:
    """单行诊断（供 CLI 打印；不打印 traceback）。"""
    loc = ''
    if exc.line is not None:
        loc = ' (第 %d 行第 %d 列)' % (exc.line, exc.col if exc.col is not None else 0)
    return '%s 解析失败: %s%s — %s' % (what, exc.path, loc, exc.reason)


def load_json(path):
    """读取并解析 JSON；失败抛 JsonLoadError（绝不返回空数据）。"""
    p = Path(path)
    try:
        raw = p.read_text(encoding='utf-8')
    except FileNotFoundError as e:
        raise JsonLoadError(p, '文件不存在 (%s)' % e.strerror) from None
    except (OSError, PermissionError) as e:
        raise JsonLoadError(p, '读取失败: %s' % e) from None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise JsonLoadError(p, e.msg, e.lineno, e.colno) from None


def read_json_or_exit(path, what: str = 'JSON'):
    """CLI 入口用：失败即 `✗ …` + exit 1（fail-fast，不静默降级）。"""
    import sys
    try:
        return load_json(path)
    except JsonLoadError as e:
        print('✗ %s' % describe(e, what))
        sys.exit(1)