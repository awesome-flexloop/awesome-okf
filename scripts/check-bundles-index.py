#!/usr/bin/env python3
"""CI gate：doc/bundles 总索引（index.md）计数与目录树的三角对账。

背景：总索引 doc/bundles/index.md 是 bundles 目录树的人工投影，计数分散在四处
需人工保持一致——frontmatter（total_bundles/groups/domains）、正文计数行
（「当前共 **N 个知识包**……**N 个技术域、N 个分组**」）、14 个域节标题
（「### … · N 束 · M 组」）、各域分组表的「束数」列。复盘曾两次发现束入库后
计数未同步（节标题/表行/frontmatter 各自漂移），人工盘点还踩过三个坑：
PowerShell 数组拆包、首元素翻倍、锚点组误判（把 concepts/ 当成束子目录）。

本 gate 以目录树为唯一地面真值，机械导出域/组/束计数，再校验投影的每一条边：

  树结构计数规则（与 check-toctrees 的 bundle-root 治理同向）：
  - 域（domain）= doc/bundles 下的直接子目录；
  - 组（group）= 域下的直接子目录；
  - 束（bundle）——递归口径（支持任意层嵌套，如 jishu/ai/<org>/<repo>）：
      * 锚点束——目录直接含 concepts/examples/references 任一层目录时，
        该目录本身即 1 束（如 katex、cpython、rust 三组、containers 十一组）；
      * 导航目录——目录不含 marker、但含「带 index.md 的内容子目录」时，
        本身不计束，束数 = 各内容子目录递归求和（如 daojia 段/家导航、
        jishu/ai 组织导航）；
      * 叶子束——目录含 index.md、且无「带 index.md 的内容子目录」时计 1 束；
      * marker 目录（concepts/examples/references）不参与子目录递归；
      * 组级 log.md、无 index.md 的存根目录不计束。
    注：旧版浅层口径（组下含 index.md 的直接子目录=束）无法穿透 jishu 4 层
    嵌套（会少计 ~185 束），且曾把 daojia 的 4 个段导航误计为 4 束（实为 19
    叶子束）；递归口径以目录树为地面真值，机械导出真实束数。

  对账检查（任一不符即 CI 拦截）：
  1) frontmatter total_bundles/groups/domains == 树计数；
  2) 正文计数行三个数字 == frontmatter；
  3) 每个树中域都有节标题，节标题「N 束 · M 组」== 该域树计数；
  4) 各域分组表「束数」列之和 == 该域树束数（合并行同样适用：containers
     11 组仅 1 行链接域首页、束数 11；rust 3 组仅 1 行、束数 3）；
  5) 表内每个链接都能解析到 doc/bundles 下真实文件（禁止 ../ 越界）；
  6) 组注册覆盖：每个组目录在表中被代表——有直达行（dom/grp/index.md 或
     其 deeper 链接）或该域有合并行（dom/index.md）；
  7) 末尾 toctree 条目集合 == 域目录集合（无缺漏、无多余）。

说明：
- 扫描工作树（含未跟踪文件）。这是「新增束后一键对账」的正确语义——新束文件
  落地即可被 gate 看见并提示计数差异；CI 在干净 checkout 上运行，工作树即
  已提交事实。本地若混入他会话未提交 WIP，差异信息按「谁添加谁对账」处理。
- 仅 stdlib，与 check-utf8/check-toctrees 同构（CI 在 pip install 前运行）。

用法:
    python scripts/check-bundles-index.py               # 对账 doc/bundles/index.md
    python scripts/check-bundles-index.py --self-test   # 破坏性探针双向自检

退出码:
    0  总索引与目录树完全一致（CI 通过）；或自检通过
    1  存在计数漂移/断链/未注册组/缺失 toctree（CI gate 拦截）；或自检失效
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLES_DIR = ROOT / "doc" / "bundles"
EXCLUDE_DIRS = {"_build", "_static", ".git", ".spec"}
# OKF 三层内容目录名：组目录直接含任一项即「锚点组」（组本身=1 束）
MARKER_DIRS = ("concepts", "examples", "references")
INDEX_NAME = "index.md"

_FENCE_OPEN = re.compile(r"^(?P<fence>`{3,}|:{3,})\s*\{toctree\}")
_FENCE_CLOSE = re.compile(r"^(?:`{3,}|:{3,})\s*$")
# 域节标题：### <emoji> [标题](dom/index.md) … · N 束 · M 组
_SECTION = re.compile(
    r"^###\s+.*?\[(?P<title>[^\]]+)\]\((?P<link>[^)]+)\)"
    r".*?·\s*(?P<bundles>\d+)\s*束\s*·\s*(?P<groups>\d+)\s*组"
)
# 分组表数据行：| [组名](相对链接) | 束数 | 说明 |
_TABLE_ROW = re.compile(
    r"^\|\s*\[(?P<title>[^\]]*)\]\((?P<link>[^)]+)\)\s*\|\s*(?P<count>\d+)\s*\|"
)
_FRONTMATTER_NUM = re.compile(r"^(total_bundles|groups|domains)\s*:\s*(\d+)\s*$")
_COUNT_LINE_BUNDLES = re.compile(r"\*\*\s*(\d+)\s*个知识包\s*\*\*")
_COUNT_LINE_SPLIT = re.compile(r"\*\*\s*(\d+)\s*个(?:技术|学科)域、(\d+)\s*个分组\s*\*\*")


@dataclass
class Row:
    """分组表中的一行。"""

    title: str
    link: str
    count: int
    line: int


@dataclass
class Section:
    """一个域的节标题及其分组表行。"""

    domain: str
    title: str
    link: str
    bundles: int
    groups: int
    rows: list[Row] = field(default_factory=list)
    line: int = 0


@dataclass
class TreeInfo:
    """目录树地面真值：domain -> {group: 该组束数}。"""

    domains: dict[str, dict[str, int]]
    # 结构歧义（如锚点组同时含束子目录）：无法机械定口径，必须人工确认
    anomalies: list[str] = field(default_factory=list)

    @property
    def total_bundles(self) -> int:
        return sum(sum(g.values()) for g in self.domains.values())

    @property
    def total_groups(self) -> int:
        return sum(len(g) for g in self.domains.values())

    @property
    def total_domains(self) -> int:
        return len(self.domains)


@dataclass
class IndexInfo:
    """总索引 index.md 解析结果。"""

    frontmatter: dict[str, int]
    count_line: tuple[int, int, int] | None  # (知识包, 技术域, 分组)
    sections: dict[str, Section]
    toctree: set[str]


def _display(path: Path) -> str:
    """返回相对 ROOT 的路径；ROOT 外（如临时探针）回退绝对路径。"""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _is_content_dir(p: Path) -> bool:
    return p.is_dir() and not p.name.startswith(".") and p.name not in EXCLUDE_DIRS


def _count_bundles(d: Path) -> int:
    """递归计数：目录 d 下的束数。

    - 锚点束——目录直接含 concepts/examples/references 任一层目录时，该目录本身
      即 1 束；其内部子目录（text/、spec/、patterns/、commentaries/ 等带
      index.md 的组织性目录）属束内结构，**不**另行计束、不递归。
    - 导航目录——不含 marker、但含「带 index.md 的内容子目录」时，本身不计束，
      束数 = 各内容子目录递归求和（如 daojia 段/家导航、jishu/ai 组织导航）。
    - 叶子束——含 index.md、且无「带 index.md 的内容子目录」时计 1 束。
    """
    if any((d / m).is_dir() for m in MARKER_DIRS):
        return 1  # 锚点束：内部子目录属束内结构，不计
    bundle_subs = [
        sub.name
        for sub in d.iterdir()
        if _is_content_dir(sub)
        and sub.name not in MARKER_DIRS
        and (sub / INDEX_NAME).is_file()
    ]
    if bundle_subs:
        return sum(_count_bundles(d / s) for s in bundle_subs)
    return 1 if (d / INDEX_NAME).is_file() else 0


def scan_tree(bundles_root: Path) -> TreeInfo:
    """机械导出目录树的域/组/束计数（地面真值）。

    束计数规则见模块 docstring 与 _count_bundles：递归口径——锚点（直挂
    concepts/examples/references 任一）计 1 束；导航目录（含带 index.md 的内容
    子目录）递归求和；叶子束计 1。
    """
    domains: dict[str, dict[str, int]] = {}
    anomalies: list[str] = []
    if not bundles_root.is_dir():
        return TreeInfo(domains)
    for dom in sorted(bundles_root.iterdir()):
        if not _is_content_dir(dom):
            continue
        groups: dict[str, int] = {}
        for grp in sorted(dom.iterdir()):
            if not _is_content_dir(grp):
                continue
            groups[grp.name] = _count_bundles(grp)
        domains[dom.name] = groups
    return TreeInfo(domains, anomalies=anomalies)


def parse_index(index_path: Path) -> IndexInfo:
    """解析总索引：frontmatter 计数、计数行、域节标题+表行、toctree 条目。"""
    text = index_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # frontmatter（首个 --- ... --- 块）
    fm: dict[str, int] = {}
    if lines and lines[0].strip() == "---":
        for ln in lines[1:]:
            if ln.strip() == "---":
                break
            m = _FRONTMATTER_NUM.match(ln.strip())
            if m:
                fm[m.group(1)] = int(m.group(2))

    # 正文计数行
    count_line: tuple[int, int, int] | None = None
    mb = _COUNT_LINE_BUNDLES.search(text)
    ms = _COUNT_LINE_SPLIT.search(text)
    if mb and ms:
        count_line = (int(mb.group(1)), int(ms.group(1)), int(ms.group(2)))

    sections: dict[str, Section] = {}
    toctree: set[str] = set()
    current: Section | None = None
    in_toctree = False
    for i, ln in enumerate(lines, start=1):
        if _FENCE_OPEN.match(ln):
            in_toctree = True
            continue
        if in_toctree:
            if _FENCE_CLOSE.match(ln):
                in_toctree = False
                continue
            body = ln.strip()
            if body and not body.startswith(":"):
                # 条目形如 ai/index：归一化为域目录名
                toctree.add(body.split("/")[0])
            continue
        sec = _SECTION.match(ln)
        if sec:
            domain = sec.group("link").split("/")[0]
            current = Section(
                domain=domain,
                title=sec.group("title"),
                link=sec.group("link"),
                bundles=int(sec.group("bundles")),
                groups=int(sec.group("groups")),
                line=i,
            )
            sections[domain] = current
            continue
        if current is not None:
            row = _TABLE_ROW.match(ln)
            if row:
                current.rows.append(
                    Row(
                        title=row.group("title"),
                        link=row.group("link"),
                        count=int(row.group("count")),
                        line=i,
                    )
                )
            elif ln.startswith("#"):
                current = None  # 进入非域节（如 toctree 前的其他标题）
    return IndexInfo(frontmatter=fm, count_line=count_line, sections=sections, toctree=toctree)


def _resolve_row_link(link: str, bundles_root: Path) -> Path | None:
    """表行链接解析为真实文件；越界（../）或不存在返回 None。"""
    p = (bundles_root / link).resolve()
    root = bundles_root.resolve()
    if root not in p.parents and p != root:
        return None
    return p if p.exists() else None


def audit(bundles_root: Path, tree: TreeInfo, index: IndexInfo) -> list[str]:
    """三角对账：返回错误信息列表（空=通过）。"""
    # 结构歧义优先报告：口径未定，后续计数对账即使通过也不可信
    errors: list[str] = list(tree.anomalies)

    # 1) frontmatter 总数 vs 树
    fm = index.frontmatter
    for key, actual in (
        ("total_bundles", tree.total_bundles),
        ("groups", tree.total_groups),
        ("domains", tree.total_domains),
    ):
        if key not in fm:
            errors.append(f"frontmatter 缺字段: {key}")
        elif fm[key] != actual:
            unit = {"total_bundles": "束", "groups": "组", "domains": "域"}[key]
            errors.append(
                f"计数漂移: frontmatter {key}={fm[key]}，目录树实际 {actual} {unit}"
                f"（差 {actual - fm[key]:+d}）"
            )

    # 2) 正文计数行 vs frontmatter
    if index.count_line is None:
        errors.append("计数行缺失: 未找到「当前共 **N 个知识包**……**N 个技术域、N 个分组**」")
    else:
        cb, cd, cg = index.count_line
        if cb != fm.get("total_bundles"):
            errors.append(f"计数漂移: 计数行声明 {cb} 个知识包，frontmatter total_bundles={fm.get('total_bundles')}")
        if cd != fm.get("domains"):
            errors.append(f"计数漂移: 计数行声明 {cd} 个域，frontmatter domains={fm.get('domains')}")
        if cg != fm.get("groups"):
            errors.append(f"计数漂移: 计数行声明 {cg} 个分组，frontmatter groups={fm.get('groups')}")

    # 3) 域节标题覆盖与计数
    tree_domains = set(tree.domains)
    sec_domains = set(index.sections)
    for d in sorted(tree_domains - sec_domains):
        errors.append(f"缺节标题: 域 {d}/ 在目录树存在（{len(tree.domains[d])} 组），总索引无对应「###」节")
    for d in sorted(sec_domains - tree_domains):
        errors.append(f"幽灵节标题: 总索引有 {d}/ 域节，但目录树不存在该域目录")

    for d in sorted(tree_domains & sec_domains):
        sec = index.sections[d]
        tb = sum(tree.domains[d].values())
        tg = len(tree.domains[d])
        if sec.bundles != tb:
            errors.append(
                f"计数漂移: {d}/ 节标题（L{sec.line}）声明 {sec.bundles} 束，目录树实际 {tb} 束"
                f"（差 {tb - sec.bundles:+d}）"
            )
        if sec.groups != tg:
            errors.append(
                f"计数漂移: {d}/ 节标题（L{sec.line}）声明 {sec.groups} 组，目录树实际 {tg} 组"
                f"（差 {tg - sec.groups:+d}）"
            )

        # 4) 表内束数和 vs 树
        row_sum = sum(r.count for r in sec.rows)
        if row_sum != tb:
            errors.append(
                f"计数漂移: {d}/ 分组表束数列之和={row_sum}，目录树实际 {tb} 束"
                f"（差 {tb - row_sum:+d}；请核对 L{sec.line} 节内各表行）"
            )

        # 5) 表行链接可解析
        for r in sec.rows:
            if _resolve_row_link(r.link, bundles_root) is None:
                errors.append(f"断链: {d}/ 表行（L{r.line}）链接不存在或越界: 「{r.link}」")

        # 6) 组注册覆盖：直达行（dom/grp/...）或域合并行（dom/index.md）
        consolidated = f"{d}/index.md"
        linked_groups = {
            r.link.split("/")[1]
            for r in sec.rows
            if r.link.startswith(f"{d}/") and len(r.link.split("/")) >= 2
        }
        for g in sorted(tree.domains[d]):
            if g in linked_groups or consolidated in {r.link for r in sec.rows}:
                continue
            errors.append(
                f"分组未注册: 目录 {d}/{g}/ 在树中存在（{tree.domains[d][g]} 束），"
                f"但 {d}/ 节表中既无直达行也无域合并行"
            )

    # 7) toctree 域集合
    if index.toctree != tree_domains:
        for d in sorted(tree_domains - index.toctree):
            errors.append(f"toctree 缺条目: {d}/index（域 {d}/ 在树中存在但未列入末尾 toctree）")
        for d in sorted(index.toctree - tree_domains):
            errors.append(f"toctree 多余条目: {d}/index（域 {d}/ 在目录树不存在）")

    return errors


def run_scan(bundles_root: Path) -> list[str]:
    """对给定 bundles 根执行完整对账。"""
    if not bundles_root.is_dir():
        return [f"bundles 目录不存在: {_display(bundles_root)}"]
    index_path = bundles_root / INDEX_NAME
    if not index_path.is_file():
        return [f"总索引不存在: {_display(index_path)}"]
    tree = scan_tree(bundles_root)
    index = parse_index(index_path)
    return audit(bundles_root, tree, index)


# ---------------------------------------------------------------------------
# 自检探针
# ---------------------------------------------------------------------------

def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _pass_index() -> str:
    """与 _build_pass_tree 结构完全一致的总索引（3 束 / 2 组 / 2 域）。"""
    return """---
okf_version: "0.2"
type: bundles-index
total_bundles: 3
groups: 2
domains: 2
---

# 知识包总索引

> 当前共 **3 个知识包**，按技术生态分为 **2 个技术域、2 个分组**。

## 域分组导航

### α [Alpha 域](alpha/index.md) · 1 束 · 1 组

| 分组 | 束数 | 说明 |
| --- | --- | --- |
| [grpa 锚点组](alpha/grpa/index.md) | 1 | 锚点组示例 |

### β [Beta 域](beta/index.md) · 2 束 · 1 组

| 分组 | 束数 | 说明 |
| --- | --- | --- |
| [Beta 全部](beta/index.md) | 2 | 域合并行示例 |

```{toctree}
:hidden:

alpha/index
beta/index
```
"""


def _build_pass_tree(root: Path) -> None:
    """构造一致的迷你树：alpha 域 1 锚点组（1 束）；beta 域 1 普通组（2 束）。"""
    _write(root / "alpha" / INDEX_NAME, "# Alpha\n")
    _write(root / "alpha" / "grpa" / INDEX_NAME, "# grpa\n")
    _write(root / "alpha" / "grpa" / "concepts" / INDEX_NAME, "# concepts\n")
    _write(root / "beta" / INDEX_NAME, "# Beta\n")
    _write(root / "beta" / "grpb" / "b1" / INDEX_NAME, "# b1\n")
    _write(root / "beta" / "grpb" / "b2" / INDEX_NAME, "# b2\n")
    _write(root / INDEX_NAME, _pass_index())


def self_test() -> bool:
    """破坏性探针双向自检：验证 gate 既放行一致结构也拦截各类漂移。"""
    ok = True
    tmp = Path(tempfile.mkdtemp("checkbundlesindex"))
    try:
        # 通过用例：完全一致
        pas = tmp / "pass"
        _build_pass_tree(pas)
        errs = run_scan(pas)
        if errs:
            ok = False
            print(f"自检失败: pass 用例应放行，实际拦截: {errs}")
        else:
            print("自检: pass → 放行 正确")

        # 拦截用例：(名称, 变异函数) —— 每个变异必须产生至少 1 条错误
        def mutate_fm(p: Path) -> None:
            t = (p / INDEX_NAME).read_text(encoding="utf-8").replace("total_bundles: 3", "total_bundles: 9")
            (p / INDEX_NAME).write_text(t, encoding="utf-8")

        def mutate_count_line(p: Path) -> None:
            t = (p / INDEX_NAME).read_text(encoding="utf-8").replace("**3 个知识包**", "**9 个知识包**")
            (p / INDEX_NAME).write_text(t, encoding="utf-8")

        def mutate_header(p: Path) -> None:
            t = (p / INDEX_NAME).read_text(encoding="utf-8").replace("· 1 束 · 1 组", "· 2 束 · 1 组")
            (p / INDEX_NAME).write_text(t, encoding="utf-8")

        def mutate_table_sum(p: Path) -> None:
            t = (p / INDEX_NAME).read_text(encoding="utf-8").replace("](beta/index.md) | 2 |", "](beta/index.md) | 5 |")
            (p / INDEX_NAME).write_text(t, encoding="utf-8")

        def mutate_bad_link(p: Path) -> None:
            t = (p / INDEX_NAME).read_text(encoding="utf-8").replace(
                "alpha/grpa/index.md", "alpha/nonexistent/index.md"
            )
            (p / INDEX_NAME).write_text(t, encoding="utf-8")

        def mutate_unregistered(p: Path) -> None:
            # alpha 域用直达行（无合并行）：新增组目录即应被「未注册」拦截
            _write(p / "alpha" / "grpx" / "c1" / INDEX_NAME, "# c1\n")

        def mutate_toctree(p: Path) -> None:
            t = (p / INDEX_NAME).read_text(encoding="utf-8").replace("beta/index\n", "")
            (p / INDEX_NAME).write_text(t, encoding="utf-8")

        def mutate_groups_fm(p: Path) -> None:
            t = (p / INDEX_NAME).read_text(encoding="utf-8").replace("groups: 2", "groups: 8")
            (p / INDEX_NAME).write_text(t, encoding="utf-8")

        def mutate_add_leaf(p: Path) -> None:
            # 导航目录下新增一个叶子束（含 index.md）——递归口径应把它计入，
            # 树总数 3→4 而索引仍声明 3，必须被「计数漂移」拦截。
            _write(p / "beta" / "grpb" / "b3" / INDEX_NAME, "# b3\n")

        def mutate_anchor_internal(p: Path) -> None:
            # 锚点束内部新增带 index.md 的组织性子目录（如 text/、spec/）——
            # 递归口径规定锚点束内部子目录不另行计束，树总数应保持 3，
            # 索引与树仍一致，本变异**不应**产生任何错误（放行）。
            _write(p / "alpha" / "grpa" / "text" / INDEX_NAME, "# text\n")

        # (名称, 变异函数, 期望错误关键词, 期望是否拦截)
        cases = [
            ("fm-total 漂移", mutate_fm, None, True),
            ("fm-groups 漂移", mutate_groups_fm, None, True),
            ("计数行漂移", mutate_count_line, None, True),
            ("节标题漂移", mutate_header, None, True),
            ("表束数和漂移", mutate_table_sum, None, True),
            ("表行断链", mutate_bad_link, None, True),
            ("分组未注册", mutate_unregistered, None, True),
            ("toctree 缺条目", mutate_toctree, None, True),
            ("导航目录新增叶子束", mutate_add_leaf, None, True),
            ("锚点束内部子目录不计束", mutate_anchor_internal, None, False),
        ]
        for name, mutate, expect, should_block in cases:
            case_dir = tmp / name.replace(" ", "_")
            _build_pass_tree(case_dir)
            mutate(case_dir)
            errs = run_scan(case_dir)
            if should_block:
                if errs and (expect is None or any(expect in e for e in errs)):
                    print(f"自检: {name} → 拦截 正确（{errs[0]}）")
                elif not errs:
                    ok = False
                    print(f"自检失败: {name} 应拦截，实际放行")
                else:
                    ok = False
                    print(f"自检失败: {name} 应报含「{expect}」的错误，实际: {errs}")
            else:
                if errs:
                    ok = False
                    print(f"自检失败: {name} 应放行，实际拦截: {errs}")
                else:
                    print(f"自检: {name} → 放行 正确")

        if ok:
            print("自检通过: check-bundles-index.py 既能拦截计数漂移/断链/未注册，也能放行一致结构与锚点束内部子目录。")
        return ok
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return 0 if self_test() else 1

    errors = run_scan(BUNDLES_DIR)
    if errors:
        print(f"\n检测到 {len(errors)} 处总索引对账问题，CI gate 拦截：")
        for err in errors:
            print(f"  - {err}")
        print("\n修复方法：按目录树地面真值更新 doc/bundles/index.md 对应计数面")
        print("（frontmatter / 计数行 / 域节标题 / 分组表束数列 / toctree），重跑本 gate 至通过。")
        return 1

    tree = scan_tree(BUNDLES_DIR)
    print(
        f"bundles 总索引对账通过: {tree.total_domains} 域 / {tree.total_groups} 组 / "
        f"{tree.total_bundles} 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
