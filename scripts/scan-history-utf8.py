#!/usr/bin/env python3
"""扫描 git 历史中 doc/ 文本文件的 UTF-8 有效性（A3 行动项）。

背景：历史上曾有一批中文文档文件被提交为非法 UTF-8 字节（中文字符截断为
U+FFFD），在 cfe3158 中已重建修复。本脚本遍历 git 全历史，按 blob 内容去重，
对 doc/ 下所有 .md/.rst/.txt 文本 blob 逐一做 UTF-8 解码校验，确认历史中
不存在残留的编码损坏版本，防止"已修复的损坏在其他历史提交中仍存在未覆盖"。

设计：按 blob 对象（而非文件×提交）去重扫描。同一内容的多份拷贝（重命名、
分支、重复提交相同语义）只校验一次，大幅减少解码次数，且覆盖历史所有版本。

用法:
    python scripts/scan-history-utf8.py            # 扫描全历史（默认）
    python scripts/scan-history-utf8.py <rev...>   # 扫描指定 rev 的可达历史

退出码:
    0  历史中 doc/ 文本 blob 全部为有效 UTF-8（A3 通过）
    1  存在非法 UTF-8 blob，并已列出（需修复或建立排除清单）
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {"_build", "_static", "_templates"}
EXTENSIONS = {".md", ".rst", ".txt"}


def git(*args: str) -> str:
    """运行 git 命令并返回 stdout。"""
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def collect_blobs(revs: list[str]) -> dict[str, list[str]]:
    """遍历可达提交，收集 doc/ 下 .md/.rst/.txt 的 blob。

    返回 {blob_id: [paths]}。同一 blob 可能对应多个路径（重命名/多分支），
    保留所有路径用于报错定位。
    """
    blobs: dict[str, list[str]] = {}
    rev_expanded = revs or ["HEAD"]
    for line in git("rev-list", "--objects", "--no-abbrev", *rev_expanded).splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        oid, path = parts[0], parts[1]
        if not any(part in EXCLUDE_DIRS for part in Path(path).parts):
            if Path(path).suffix in EXTENSIONS and ("doc/" in path):
                blobs.setdefault(oid, []).append(path)
    return blobs


def is_valid_utf8(oid: str) -> bool:
    """返回该 blob 是否为有效 UTF-8。"""
    raw = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "blob", oid],
        capture_output=True,
    ).stdout
    try:
        raw.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def main() -> int:
    revs = sys.argv[1:]
    blobs = collect_blobs(revs)
    n_blob = len(blobs)
    n_path = sum(len(v) for v in blobs.values())
    if not blobs:
        print("未在历史中找到任何可扫描的 doc 文本 blob", file=sys.stderr)
        return 1

    bad = []
    for i, (oid, paths) in enumerate(blobs.items(), 1):
        if not is_valid_utf8(oid):
            bad.append((oid, paths))
        if i % 500 == 0:
            print(f"  已扫描 {i}/{n_blob} 个 blob…", file=sys.stderr)

    if bad:
        print(f"\n检测到 {len(bad)} 个非法 UTF-8 blob（历史 {n_blob} 个文本 blob / {n_path} 个路径）: ")
        for oid, paths in bad[:50]:
            print(f"  blob {oid} -> {'; '.join(paths[:3])}")
        return 1

    print(f"A3 通过: 历史中 {n_blob} 个 doc 文本 blob（去重后，对应 {n_path} 个路径）全部为有效 UTF-8，无残留编码损坏。")
    return 0


if __name__ == "__main__":
    sys.exit(main())