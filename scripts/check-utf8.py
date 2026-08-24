#!/usr/bin/env python3
"""CI gate：扫描 doc/ 下所有 Markdown 文件的 UTF-8 有效性。

背景：曾因 12 个中文文档文件被提交为非法 UTF-8 字节（中文字符截断为
U+FFFD），导致 GitHub Actions Sphinx 构建触发 UnicodeDecodeError 失败。
本脚本在 Sphinx 解析前扫描源文件，任何非法 UTF-8 字节即非零退出，
作为 CI 构建的前置质量门，防止此类损坏再次进入仓库。

用法:
    python scripts/check-utf8.py            # 扫描 doc/（默认，递归）
    python scripts/check-utf8.py [PATH...]  # 扫描指定目录/文件

退出码:
    0  全部文件为有效 UTF-8（CI 通过）
    1  存在非法 UTF-8 文件，并已列出（CI gate 拦截）
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# 默认扫描 Sphinx 源目录，跳过构建产物
DEFAULT_SCAN = (ROOT / "doc",)
EXCLUDE_DIRS = {"_build", "_static", "_templates", ".git"}
EXTENSIONS = {".md", ".rst", ".txt"}


def iter_targets(paths) -> list[Path]:
    """展开输入路径为待检查文件列表。"""
    files: list[Path] = []
    for base in paths:
        p = Path(base)
        if not p.exists():
            print(f"错误: 路径不存在: {p}", file=sys.stderr)
            continue
        if p.is_file():
            files.append(p)
        else:
            for f in p.rglob("*"):
                if f.is_file() and any(part in EXCLUDE_DIRS for part in f.parts):
                    continue
                if f.suffix in EXTENSIONS:
                    files.append(f)
    return files


def check_file(path: Path) -> bool:
    """返回该文件是否为有效 UTF-8。"""
    try:
        path.read_bytes().decode("utf-8")
        return True
    except UnicodeDecodeError as exc:
        print(f"非法 UTF-8: {path.relative_to(ROOT)}  (偏移 {exc.start})")
        return False
    except OSError as exc:
        print(f"读取失败: {path.relative_to(ROOT)}: {exc}", file=sys.stderr)
        return False


def main() -> int:
    args = sys.argv[1:]
    targets = DEFAULT_SCAN if not args else [Path(a) for a in args]
    files = iter_targets(targets)
    if not files:
        print("未找到任何可扫描文件", file=sys.stderr)
        return 1

    bad = [f for f in files if not check_file(f)]
    if bad:
        print(f"\n检测到 {len(bad)} 个非法 UTF-8 文件，CI gate 拦截。")
        return 1

    print(f"UTF-8 检查通过: {len(files)} 个文件均为有效 UTF-8。")
    return 0


if __name__ == "__main__":
    sys.exit(main())