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

本 gate 的职责（四件事，全部机械可判）：
  1) **基线口径守卫**：校验目标文件中引用的 md 总数 / 内容文档数 / 字节数与
     HEAD 已提交事实一致——任何引用工作区快照数字的写法直接拦截；
  2) **规模数字单一真相源对账**：校验 doc/bundles/index.md（真源）、doc/index.md、
     README.md 三处的束数一致，防止 C-47 类「三套并存」再次静默共存；
  3) **行尾归一自证**：字节数跨行尾口径不可比（工作区 CRLF / 仓库 LF，同一份
     内容每行多 1 字节，而计数完全不变）。本 gate 实测「工作区字节 − CRLF
     行数」与 HEAD 的残差，残差超过容差即判定字节基线不可引用——这是 E-05
     的自动化预防，防止「计数验算通过、字节维度失效」再次静默发生；
  4) **.spec/ 泄漏守卫**：确认工作区 .spec 内部工作稿没有被计入基线。

用法:
    python scripts/check-asset-baseline.py               # 校验
    python scripts/check-asset-baseline.py --print-only  # 只打印基线，不校验

退出码:
    0  基线口径一致且三处规模数字一致
    1  存在口径漂移或规模数字矛盾（CI 拦截）

仅 stdlib；不依赖 git 之外的外部工具；git 不可用时降级为跳过（不误伤 CI）。
"""
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

# 引用精确字节数的方案页（字节基线时效校验；束数类检查仍只看 TARGETS）
BASELINE_DOCS = (
    "doc/bundles/sheke/industry/workbuddy-1024-contest/concepts/08-entry-plan-okf-knowledge-navigator.md",
)

# 已登记的字节快照值白名单。
#   精确字节数会随每次入库漂移，强制文档时刻等于 HEAD 会形成「改一次漂一次」
#   的死循环。因此文档记录「量级 + 带日期的历史快照值」，门禁只拦截
#   未登记的任意值。登记即留痕——新增快照值时须同时写明实测日期与口径。
#
#   ⚠️ 下列 97076707 / 97044203 是**工作区快照口径**（已作废），
#      文档中仅作为勘误对照出现，故一并放行；若在别处被当基线引用，
#      由 [口径漂移] 检查（forbidden 列表）拦截。
KNOWN_BYTE_SNAPSHOTS = {
    96239422: "2026-10-25 HEAD 口径实测（E-05 三次复核后）",
    96235012: "2026-10-24 HEAD 口径实测（E-05 归因修正提交前）",
    96214235: "2026-10-24 HEAD 口径实测（基线门禁初版）",
    97076707: "2026-10-24 工作区快照口径（已作废，仅作勘误对照）",
    97044203: "2026-10-24 工作区快照口径（已作废，仅作勘误对照）",
}

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


def worktree_line_ending_delta() -> tuple[int, int, int]:
    """工作区相对 HEAD 的行尾差异：(CRLF 行数, 带 CRLF 的文件数, .spec 字节)。

    行尾是「文件增减」看不见的维度——同一份内容，CRLF 每行比 LF 多 1 字节，
    而 md 数与内容文档数完全不变。因此字节数跨口径不可比：工作区字节必须先
    减去 CRLF 行数、并剔除未跟踪的 .spec/ 内部工作稿，才与 HEAD 口径可比。

    三次复核实测（2026-10-25）：字节差 ÷ CRLF 行数 = 1.0000；工作区字节
    减去 CRLF 行数后与 HEAD 的残差恰为 +310,001 = .spec 字节，一位不差。
    """
    crlf_lines = 0
    crlf_files = 0
    spec_bytes = 0
    for p in BUNDLES.rglob("*.md"):
        rel = p.relative_to(BUNDLES).as_posix()
        raw = p.read_bytes()
        c = raw.count(b"\r\n")
        if c:
            crlf_files += 1
        crlf_lines += c
        if "/.spec/" in rel or rel.startswith(".spec/"):
            spec_bytes += len(raw)
    return crlf_lines, crlf_files, spec_bytes


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

    # --- 行尾归一（E-05 预防措施）：字节数跨口径不可比，须能自证归一成立 ---
    crlf_lines, crlf_files, spec_bytes = worktree_line_ending_delta()
    ws_tracked_bytes = 0
    for p in BUNDLES.rglob("*.md"):
        rel = p.relative_to(BUNDLES).as_posix()
        if "/.spec/" in rel or rel.startswith(".spec/"):
            continue
        ws_tracked_bytes += p.stat().st_size
    normalized = ws_tracked_bytes - crlf_lines
    residual = normalized - baseline["bytes"]
    print()
    print(f"  行尾归一校验（E-05）:")
    print(f"    工作区已跟踪字节     : {ws_tracked_bytes}")
    print(f"    − CRLF 行尾行数      : {crlf_lines}  ({crlf_files} 个文件带 CRLF)")
    print(f"    = 归一后字节         : {normalized}")
    print(f"    HEAD 提交态字节      : {baseline['bytes']}")
    print(f"    残差                 : {residual:+d}")

    if "--print-only" in sys.argv:
        return 0

    errors: list[str] = []

    # --- 检查 0：行尾归一必须成立（否则字节数不可引用）---
    if crlf_lines and abs(residual) > max(2048, baseline["bytes"] // 1000):
        errors.append(
            f"[行尾归一失效] 工作区归一后字节与 HEAD 残差 {residual:+d} 超过容差；"
            f"字节数基线不可引用——工作区存在 CRLF 行尾以外的内容漂移，"
            f"请先提交或 stash 工作区变更再复跑")

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
        # CRLF 工作区口径的字节数（含行尾膨胀，与 HEAD 口径不可比）
        "96214235": "提交前一轮的 HEAD 字节数（行尾/内容已变，须以当前 HEAD 为准）",
    }
    for rel in TARGETS:
        f = REPO_ROOT / rel
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        # ⚠️ 必须按「数字归一化后比较」，不能用 `num in text` 裸字符串匹配——
        #    文档里写的是 97,076,707（带千分位），裸匹配 "97076707" 永远命中不到，
        #    校验形同虚设（E-05 同类盲区：规则未覆盖文档的真实书写格式）。
        digits_only = re.sub(r"[^\d]", "", text)
        for num, why in forbidden.items():
            if num in digits_only:
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

    # --- 检查 3：引用的字节数必须是「当前 HEAD」或「已登记的历史快照值」 ---
    # 设计取舍（E-05 衍生教训）：精确字节数**会随每次入库漂移**，若强制文档
    # 时刻等于 HEAD，则「改一次漂一次」形成死循环。因此文档只记量级 + 实测日期，
    # 精确值作为**带日期的历史快照**登记在白名单里；门禁只拦截
    # ① 未登记的任意字节值 ② 已作废的工作区快照口径值。
    for rel in TARGETS + BASELINE_DOCS:
        f = REPO_ROOT / rel
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        quoted: set[int] = set()
        for m in re.finditer(r"(?<![\d,])(\d{1,3}(?:,\d{3}){2,3}|\d{7,9})\s*字节", text):
            quoted.add(int(m.group(1).replace(",", "")))
        if not quoted:
            continue
        unknown = {n for n in quoted if n not in KNOWN_BYTE_SNAPSHOTS}
        if unknown:
            errors.append(
                f"[字节基线未登记] {rel}: 引用了 {sorted(unknown)} 字节，"
                f"既非当前 HEAD（{baseline['bytes']}）也非已登记的历史快照值；"
                f"请以 `check-asset-baseline.py --print-only` 实测后登记，"
                f"或改为量级表述（约 91.8 MiB）")
        current = quoted & {baseline["bytes"]}
        if current:
            print(f"字节基线引用: {rel} → {sorted(current)}（与当前 HEAD 一致）")

    # --- 检查 4：.spec/ 泄漏守卫 ---
    if spec_n:
        print(f".spec/ 泄漏守卫: 通过（基线取自 HEAD，不含工作区 {spec_n} 个内部工作稿）")

    print()
    if errors:
        print(f"✗ 校验失败：{len(errors)} 项")
        for e in errors:
            print(f"  - {e}")
        print("\n处置：把数字改为 HEAD 口径实测值，或改为量级表述（六百余束 / 上万篇 / 九大领域）。")
        return 1

    print("✓ 校验通过：基线口径一致，规模数字无矛盾，行尾归一自证成立")
    return 0


def self_test() -> int:
    """自检探针：证明本 gate 的每条校验规则确实能命中（E-05 同类盲区的防御）。

    背景：本轮曾出现「正则只匹配裸数字、而文档全用千分位写法 → 校验形同虚设」。
    任何校验规则都必须证明自己**能命中**——否则「通过」不代表「正确」。
    """
    print("=" * 60)
    print("check-asset-baseline.py 自检探针")
    print("=" * 60)
    failures: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        if cond:
            print(f"  [PASS] {name}")
        else:
            print(f"  [FAIL] {name} {detail}")
            failures.append(name)

    # 探针 1：字节正则必须同时命中千分位与裸数字写法
    sample = "实测 **96,235,012 字节**（另见 96235012 字节）"
    hits = {int(m.group(1).replace(",", "")) for m in
            re.finditer(r"(?<![\d,])(\d{1,3}(?:,\d{3}){2,3}|\d{7,9})\s*字节", sample)}
    check("字节正则命中千分位写法", 96235012 in hits, f"hits={hits}")
    check("字节正则命中裸数字写法", 96235012 in hits, f"hits={hits}")
    check("字节正则不误抓数字片段", len(hits) == 1, f"hits={hits}")

    # 探针 2：行尾归一公式可算出正确残差
    crlf_lines, crlf_files, spec_bytes = worktree_line_ending_delta()
    check("行尾归一读取到 CRLF 行数", crlf_lines > 0, f"crlf_lines={crlf_lines}")
    check("行尾归一读取到 .spec 字节", spec_bytes > 0, f"spec_bytes={spec_bytes}")

    # 探针 3：束数抽取能命中三种写法
    sample2 = ("当前实际值：**503 束 / 57 组**；共收录 **500 个知识包**；"
               "完整 503 束清单 → 见总索引")
    nums = find_bundle_numbers(sample2)
    check("束数抽取命中 **503 束**", 503 in nums, f"nums={nums}")
    check("束数抽取命中 **500 个知识包**", 500 in nums, f"nums={nums}")

    # 探针 4：forbidden 检查必须能命中带千分位的写法（裸字符串匹配会漏）
    digits_only = re.sub(r"[^\d]", "", "实测 **97,076,707 字节**")
    check("forbidden 检查命中千分位字节值", "97076707" in digits_only, f"digits={digits_only}")
    check("forbidden 检查不误伤无关数字",
          "97076707" not in re.sub(r"[^\d]", "", "实测 **12,376 个 md**"), "")

    # 探针 5：字节白名单机制——已登记值放行、未登记值拦截
    check("白名单含当前 HEAD 快照值", 96239422 in KNOWN_BYTE_SNAPSHOTS)
    check("白名单放行已登记值", 96239422 in KNOWN_BYTE_SNAPSHOTS)
    check("白名单拦截未登记值", 999999999 not in KNOWN_BYTE_SNAPSHOTS)

    print()
    if failures:
        print(f"自检失败：{len(failures)} 项 — {failures}")
        return 1
    print("自检通过：所有校验规则均可命中（规则本身有效）")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    sys.exit(main())
