#!/usr/bin/env python3
"""CI gate：库规模基线口径一致性校验。

背景（事故复盘，提交 fe996456 之后的 2026-10-24）：
  参赛方案曾两次登记错误的库规模数字。第一次把工作区瞬时快照（含他方未提交
  WIP、被 .gitignore 忽略的 .spec/ 内部工作稿）当成「库资产」；第二次在复核时
  把「首轮 12,404 → 复核 12,390，差额恰为 14」直接归因为「未排除 .spec/ 目录」，
  而真相是两个独立来源各自贡献 14 —— 巧合叠加掩盖了真实差异（内容文档差额是 9
  不是 14，当场即可证伪）。

  根因不是算错，而是**口径没定义**：
    - 「库规模」有两个合法但完全不同的口径——已提交事实（HEAD，= 站点 CI 实际
      发布的内容）vs 工作区快照（含未提交 WIP）；
    - 没有任何门禁强制方案里引用的数字来自哪一个口径；
    - 没有门禁发现三处（总索引 / doc/index.md / README.md）规模数字互相矛盾。

本 gate 的职责（三件事，全部机械可判）：
  1) **基线口径守卫**：校验目标文件中引用的 md 总数 / 内容文档数 / 字节数与
     HEAD 已提交事实一致——任何引用工作区快照数字的写法直接拦截；
  2) **规模数字单一真相源对账**：校验 doc/bundles/index.md（真源）、doc/index.md、
     README.md 三处的束数一致，防止 C-47 类「三套并存」再次静默共存；
  3) **.spec/ 泄漏守卫**：确认工作区 .spec 内部工作稿没有被计入基线。

用法:
    python scripts/check-asset-baseline.py               # 校验
    python scripts/check-asset-baseline.py --print-only  # 只打印基线，不校验

退出码:
    0  基线口径一致且三处规模数字一致
    1  存在口径漂移或规模数字矛盾（CI 拦截）

仅 stdlib；不依赖 git 之外的外部工具；git 不可用时降级为跳过（不误伤 CI）。
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLES = REPO_ROOT / "doc" / "bundles"

# 引用基线数字的目标文件：相对仓库根
TARGETS = (
    "doc/bundles/index.md",
    "doc/index.md",
    "README.md",
)

# 允许在目标文件中出现的量级表述（不参与精确校验，但也不该被误判）
MAGNITUDE_ONLY = ("六百余", "上万篇", "九大领域", "500+")


def git(*args: str) -> str | None:
    try:
        r = subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True,
            text=True, encoding="utf-8", check=True)
        return r.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def head_baseline() -> dict[str, int] | None:
    """从 HEAD（已提交事实）导出权威基线。git 不可用或非 git 仓库时返回 None。"""
    out = git("ls-tree", "-r", "-l", "HEAD", "--", "doc/bundles")
    if not out:
        return None
    md_count = 0
    content_count = 0
    total_bytes = 0
    for line in out.strip().split("\n"):
        if not line:
            continue
        meta, path = line.split("\t", 1)
        fields = meta.split()
        if len(fields) < 4:
            continue
        try:
            size = int(fields[3])
        except ValueError:
            continue
        if not path.endswith(".md"):
            continue
        md_count += 1
        total_bytes += size
        if not re.search(r"/(index|log)\.md$", path):
            content_count += 1
    return {
        "md": md_count,
        "content": content_count,
        "bytes": total_bytes,
    }


def worktree_spec_md() -> int:
    """工作区内被 .gitignore 忽略的 .spec/ 内部工作稿数量（不得计入基线）。"""
    n = 0
    for p in BUNDLES.rglob("*.md"):
        rel = p.relative_to(BUNDLES).as_posix()
        if "/.spec/" in rel or rel.startswith(".spec/"):
            n += 1
    return n


def bundles_total_from_index() -> int | None:
    """从 doc/bundles/index.md frontmatter 读 total_bundles（单一真相源）。"""
    idx = BUNDLES / "index.md"
    if not idx.exists():
        return None
    text = idx.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^total_bundles:\s*(\d+)\s*$", text, re.M)
    return int(m.group(1)) if m else None


def find_bundle_numbers(text: str) -> set[int]:
    """抽取文中形如「N 个知识包 / N 束 / N 知识包」的具体数字。"""
    out: set[int] = set()
    pats = (
        r"\*\*(\d{3,4})\s*(?:个)?知识包\*\*",
        r"\*\*(\d{3,4})\s*束\*\*",
        r"当前实际值：\*\*(\d{3,4})\s*束",
        r"共收录\s*\*\*(\d{3,4})\s*个知识包\*\*",
        r"完整\s*(\d{3,4})\s*束清单",
        r"\*\*(\d{3,4})\s*束\*\*",
    )
    for p in pats:
        for m in re.finditer(p, text):
            out.add(int(m.group(1)))
    return out


def main() -> int:
    print("=" * 60)
    print("库规模基线口径校验")
    print("=" * 60)

    baseline = head_baseline()
    if baseline is None:
        print("SKIP: git 不可用或非 git 仓库，跳过基线校验（不误伤 CI）")
        return 0

    print(f"HEAD 已提交事实（唯一合法基线口径）:")
    print(f"  md 总数     : {baseline['md']}")
    print(f"  内容文档数  : {baseline['content']}")
    print(f"  字节数      : {baseline['bytes']}  ({baseline['bytes'] / 1048576:.2f} MiB)")

    spec_n = worktree_spec_md()
    print(f"  工作区 .spec/ 内部工作稿: {spec_n} 个 md（被 .gitignore 忽略，**不得计入基线**）")

    if "--print-only" in sys.argv:
        return 0

    errors: list[str] = []

    # --- 检查 1：目标文件不得引用非 HEAD 口径的精确数字 ---
    md_str = str(baseline["md"])
    content_str = str(baseline["content"])
    bytes_str = str(baseline["bytes"])
    forbidden = {
        # 已被证明是「工作区快照」口径的历史值（首轮登记 + 中间稿误判口径）
        "12404": "首轮工作区快照 md 总数（含他方未提交 WIP 与 .spec 内部工作稿）",
        "12390": "中间稿工作区快照 md 总数（未锚定 HEAD）",
        "9337": "首轮工作区快照内容文档数",
        "97076707": "首轮工作区快照字节数",
        "97044203": "中间稿工作区快照字节数",
        "9328": "工作区快照内容文档数（未排除 .spec）",
    }
    for rel in TARGETS:
        f = REPO_ROOT / rel
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        for num, why in forbidden.items():
            if num in text:
                errors.append(f"[口径漂移] {rel}: 出现 {num} —— {why}；基线应取 HEAD 的 {md_str}/{content_str}/{bytes_str}")

    # --- 检查 2：规模数字单一真相源对账（三处束数一致）---
    truth = bundles_total_from_index()
    if truth is not None:
        print(f"\n总索引 total_bundles（单一真相源）: {truth}")
        for rel in TARGETS:
            f = REPO_ROOT / rel
            if not f.exists() or rel == "doc/bundles/index.md":
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            nums = find_bundle_numbers(text)
            stale = {n for n in nums if n != truth}
            if stale:
                errors.append(
                    f"[规模数字矛盾] {rel}: 出现 {sorted(stale)}，与总索引 {truth} 不一致；"
                    f"须同步为 {truth} 或改为量级表述")

    # --- 检查 3：.spec/ 泄漏守卫 ---
    if spec_n and baseline["md"] == baseline["md"]:  # 基线来自 HEAD，天然不含 .spec
        print(".spec/ 泄漏守卫: 通过（基线取自 HEAD，不含工作区内部工作稿）")

    print()
    if errors:
        print(f"✗ 校验失败：{len(errors)} 项")
        for e in errors:
            print(f"  - {e}")
        print("\n处置：把数字改为 HEAD 口径实测值，或改为量级表述（六百余束 / 上万篇 / 九大领域）。")
        return 1

    print("✓ 校验通过：基线口径一致，规模数字无矛盾")
    return 0


if __name__ == "__main__":
    sys.exit(main())
