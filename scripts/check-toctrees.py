#!/usr/bin/env python3
"""CI gate：扫描 doc/bundles 的 index.md/toctree 导航完整性。

背景：OKF（Open Knowledge Format）bundle 以 index.md 为导航入口，每个 index.md
通过 `{toctree}` 引用其内容文档（含子目录的 index.md）。复盘曾发现两类破坏：
- 内容文档未被任何 index.md 的 toctree 引用（孤立/未收录，触发 Sphinx
  ``toc.not_included`` 告警）；
- 父 toctree 引用了 ``xxx/index`` 但其目录缺失 index.md（断链）。

本脚本在 Sphinx 解析前扫描 index.md 的 toctree 链（引用语义，基于 Sphinx docname）：
  1) 校验每个 toctree 引用都能解析到真实存在的 .md——含「被 toctree 引用为目录
     index 的 xxx/index.md 必须存在」；
  2) 从 doc/index.md 沿 index.md 的 toctree 链做 BFS，校验所有 .md 内容文档均可达；
  3) 目录文件清单一致性：对每个含 toctree 的 index.md，校验其目录内全部内容
        （子目录 index 与直接 .md 文件）均已列入该 toctree（无「缺失条目」）。
       这是 1)/2) 的盲区补充——某文件虽可经其他路径可达，但其所在目录的
       index.md toctree 却未收录自身内容，构成目录文件清单不一致；
  4) bundle 根目录(含子目录)必须存在 index.md（项目级治理强化，非 OKF 标准要求）：
       对 doc/bundles 下「含非隐藏子目录却缺 index.md」的目录报「缺失 index.md」。

刻意不做「每个含 .md 的叶子目录都有 index.md」的机械要求：trae-skills 等 bundle 允许
根 index.md 的 toctree 直接逐条列出 concepts/spec 等子目录下的内容文件，此时这些
子目录本身无需 index.md；只要全部 .md 可由 doc/index.md 出发经 toctree 链可达即合法。

用法:
    python scripts/check-toctrees.py               # 扫描 doc/（默认，递归）
    python scripts/check-toctrees.py [PATH...]     # 扫描指定 index.md/目录（仅断链检查）
    python scripts/check-toctrees.py --self-test   # 破坏性探针双向自检

退出码:
    0  全部 index.md 的 toctree 引用有效、全部内容文档可达（CI 通过）；或自检通过
    1  存在断链 / 不可达内容 / 缺失 index.md（CI gate 拦截）；或自检发现 gate 失效
"""
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCAN = (ROOT / "doc",)
# `.spec` 为 OKF 生成流程的内部工作目录（含机器本地 file:/// 绝对路径），
# 被 .gitignore 的 `*.spec` 排除、永不提交；不得作为发布内容扫描或引用。
EXCLUDE_DIRS = {"_build", "_static", ".git", ".spec"}
INDEX_NAME = "index.md"

# MyST `{toctree}` 指令的开/闭围栏（支持反引号与冒号围栏）
_FENCE_OPEN = re.compile(r"^(?P<fence>`{3,}|:{3,})\s*\{toctree\}(?:\s*\{(?:hidden|glob)\})?\s*$")
_FENCE_CLOSE = re.compile(r"^(?:`{3,}|:{3,})\s*$")
# 非文件目标的 toctree 条目（角色/URL/锚点），静默跳过
_SKIP_ENTRY = re.compile(r"^(https?://|mailto:|[#{\[]|genindex|modindex|search)$")
_OPTION = re.compile(r"^\s*:")


def _is_internal_hidden_ref(entry: str) -> bool:
    """toctree 条目是否指向内部隐藏工作目录（如 `.spec`）。

    `.spec` 等隐藏目录被 EXCLUDE_DIRS 排除、永不提交，禁止被发布 toctree 引用。
    无论本地是否存在同名工作文件，此类引用在 CI 版本库中必然悬空，须确定性拦截，
    避免 gate 因本地多出手文件而误放行（环境相关门禁反模式）。
    """
    e = entry.strip()
    m = re.match(r"^.+\s*<\s*([^>]+?)\s*>$", e)  # RST 风格 `标题 <docname>`
    if m:
        e = m.group(1)
    e = e.replace("\\", "/").lstrip("/")
    return any(seg.startswith(".") and seg not in (".", "..") for seg in e.split("/"))


def _display(path: Path) -> str:
    """返回相对 ROOT 的路径；ROOT 外（如临时探针）回退绝对路径。"""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def iter_index_files(paths) -> list[Path]:
    """展开输入路径（目录/文件）为待检查的 index.md 列表（跳过构建产物目录）。"""
    files: list[Path] = []
    for base in paths:
        p = Path(base)
        if not p.exists():
            print(f"错误: 路径不存在: {p}", file=sys.stderr)
            continue
        if p.is_file():
            if p.name == INDEX_NAME:
                files.append(p)
        else:
            for f in p.rglob(INDEX_NAME):
                if f.is_file() and not any(part in EXCLUDE_DIRS for part in f.parts):
                    files.append(f)
    return sorted(set(files))


def index_files_under(doc_dir: Path) -> list[Path]:
    return iter_index_files([doc_dir])


def extract_entries(path: Path) -> list[str]:
    """提取单个 index.md 内所有 `{toctree}` 块的条目（原始 docname 字符串）。"""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"读取失败: {_display(path)}: {exc}", file=sys.stderr)
        return []
    lines = text.splitlines()
    entries: list[str] = []
    i, n = 0, len(lines)
    while i < n:
        if not _FENCE_OPEN.match(lines[i]):
            i += 1
            continue
        i += 1
        while i < n and not _FENCE_CLOSE.match(lines[i]):
            body = lines[i].strip()
            if body and not _OPTION.match(body):
                entries.append(body)
            i += 1
        i += 1  # 跳过闭围栏
    return entries


def resolve_target(src_dir: Path, entry: str, srcdir: Path) -> Path | None:
    """把一条 toctree 条目解析为真实 .md 路径；无法解析/非目标条目返回 None。

    解析规则（对齐 Sphinx docname 语义）：
    - 相对条目相对各自 index.md 所在目录（src_dir）解析；
    - 以 '/' 开头的绝对 docname 相对扫描根（srcdir）解析；
    - 条目 ``xxx/index`` → ``xxx/index.md``；``xxx/yyy`` → ``xxx/yyy.md``；
    - 条目为目录名且含 index.md → ``<目录>/index.md``；
    - 兼容 ``标题 <docname>`` 与显式 ``.md/.rst/.txt`` 后缀。
    """
    e = entry.strip()
    if not e or _SKIP_ENTRY.match(e):
        return None
    tm = re.match(r"^.+\s*<\s*([^>]+?)\s*>$", e)  # RST 风格 `标题 <docname>`
    if tm:
        e = tm.group(1)
    e = e.replace("\\", "/")
    is_abs = e.startswith("/")
    pure = re.sub(r"\.(md|rst|txt)$", "", e).lstrip("/")
    base = srcdir if is_abs else src_dir
    cand = base / (pure + ".md")
    if cand.exists():
        return cand
    d = base / pure
    if d.is_dir():
        idx = d / INDEX_NAME
        if idx.exists():
            return idx
    return None


def check_broken(index_files: list[Path], srcdir: Path) -> tuple[list[str], dict[Path, set[Path]]]:
    """校验每个 index.md 的 toctree 引用均能解析到真实 .md；返回错误与邻接边。"""
    errors: list[str] = []
    edges: dict[Path, set[Path]] = {}
    for idx in index_files:
        src_dir = idx.parent
        targets: set[Path] = set()
        for ent in extract_entries(idx):
            if _is_internal_hidden_ref(ent):
                errors.append(
                    f"断链: {_display(idx)} 的 toctree 引用内部隐藏目录: 「{ent}」"
                    "（.spec 等工作目录被排除、永不提交，禁止发布引用）"
                )
                continue
            t = resolve_target(src_dir, ent, srcdir)
            if t is None:
                hint = "（目录缺 index.md）" if ent.endswith("/index") else ""
                errors.append(f"断链: {_display(idx)} 的 toctree 引用不存在: 「{ent}」{hint}")
            else:
                targets.add(t)
        edges[idx] = targets
    return errors, edges


def all_md_under(srcdir: Path) -> set[Path]:
    return {
        f
        for f in srcdir.rglob("*")
        if f.is_file()
        and f.suffix == ".md"
        and not any(part in EXCLUDE_DIRS for part in f.parts)
    }


def check_reachable(
    srcdir: Path, edges: dict[Path, set[Path]], all_md: set[Path]
) -> list[str]:
    """从 doc/index.md 沿 index.md 的 toctree 链 BFS，校验所有 .md 均可达。"""
    seed = srcdir / INDEX_NAME
    if not seed.exists():
        return [f"缺失根 index.md: {_display(seed)}"]
    reached: set[Path] = set()
    frontier = [seed]
    while frontier:
        f = frontier.pop()
        if f in reached:
            continue
        reached.add(f)
        for t in edges.get(f, ()):
            if t not in reached:
                frontier.append(t)
    unreached = sorted(all_md - reached, key=str)
    return [f"未收录(不可达): {_display(u)}" for u in unreached]


def expected_entries(src_dir: Path) -> set[str]:
    """计算目录内容隐含的应列 toctree 条目集合（docname 形式）。

    对齐 fix_toctrees.collect_entries 语义：
    - 子目录含 index.md → ``<subdir>/index``；
    - 子目录无 index.md → 逐条列出其直接 .md 文件 ``<subdir>/<file>``；
    - 目录内直接 .md 文件（index/README 除外）→ ``<file>``；
    - 跳过隐藏项与内部工作目录（.spec 在 EXCLUDE_DIRS，与 _build/_static 同级）。
    """
    expected: set[str] = set()
    try:
        items = list(src_dir.iterdir())
    except OSError:
        return expected
    for item in items:
        if item.name.startswith(".") or item.name in EXCLUDE_DIRS:
            continue
        if item.is_dir():
            if (item / INDEX_NAME).exists():
                expected.add(f"{item.name}/index")
            else:
                for f in item.glob("*.md"):
                    if f.name.lower() != "readme.md":
                        expected.add(f"{item.name}/{f.stem}")
        elif item.is_file() and item.suffix == ".md":
            if item.name != INDEX_NAME and item.name.lower() != "readme.md":
                expected.add(item.stem)
    return expected


def _to_docname(entry: str) -> str | None:
    """把 toctree 条目归一化为相对其 index.md 所在目录的 docname；非本地文件目标返回 None。

    绝对 docname（``/xxx``，相对 srcdir）为跨目录引用，不参与单目录一致性比对。
    """
    e = entry.strip()
    if not e or _SKIP_ENTRY.match(e):
        return None
    tm = re.match(r"^.+\s*<\s*([^>]+?)\s*>$", e)  # RST 风格 `标题 <docname>`
    if tm:
        e = tm.group(1)
    e = e.replace("\\", "/")
    if e.startswith("/"):
        return None
    return re.sub(r"\.(md|rst|txt)$", "", e)


def check_consistency(index_files: list[Path]) -> list[str]:
    """校验每个含 toctree 的 index.md：目录内全部内容均已列入（无缺失条目）。

    覆盖 check_broken/check_reachable 的盲区：文件虽可经其他路径全局可达，
    但其所在目录的 index.md toctree 未收录自身内容（目录文件清单不一致）。
    """
    errors: list[str] = []
    for idx in index_files:
        entries = extract_entries(idx)
        if not entries:
            continue  # 无 toctree 的 index.md 不在本检查范围
        listed = {
            d
            for e in entries
            if (d := _to_docname(e)) is not None
        }
        for m in sorted(expected_entries(idx.parent) - listed):
            errors.append(f"缺失条目: {_display(idx)} 的 toctree 未收录 {m}")
    return errors


def check_bundle_root_index(srcdir: Path) -> list[str]:
    """bundle 根目录(含子目录)必须生成 index.md（项目级治理强化，非 OKF 标准要求）。

    OKF v0.2 中 bundle 根 index.md 为 MAY（可选，见 okf-spec 的 bundle-structure.md），
    但本项目治理强化为 MUST：bundle 根是整束内容的导航入口，缺 index.md 会使该 bundle
    的内容无法经 doc/index.md 出发的 toctree 链被发现，构成「结构性孤立」。

    粒度：仅要求「含非隐藏子目录的目录（bundle 根）」有 index.md；对「含 .md 但无
    子目录」的叶目录不强制——trae-skills 等 bundle 允许根 index.md 的 toctree 直接
    逐条列出子目录内容文件，叶目录本身无需 index.md。

    扫描范围限定在 bundles 版本库：优先扫 ``srcdir/bundles``；若 srcdir 无 bundles
    子目录（如自检探针的临时目录），则直接扫 srcdir 自身侧，以便破坏性探针能验证拦截。
    """
    bundles_root = srcdir / "bundles" if (srcdir / "bundles").is_dir() else srcdir
    if not bundles_root.is_dir():
        return []
    dirs: list[Path] = [bundles_root]
    for d in bundles_root.rglob("*"):
        if d.is_dir() and not any(
            part in EXCLUDE_DIRS or part.startswith(".")
            for part in d.relative_to(bundles_root).parts
        ):
            dirs.append(d)
    errors: list[str] = []
    for d in dirs:
        if (d / INDEX_NAME).exists():
            continue
        has_content_subdir = any(
            it.is_dir() and it.name not in EXCLUDE_DIRS and not it.name.startswith(".")
            for it in d.iterdir()
        )
        if has_content_subdir:
            errors.append(f"缺失 index.md: {_display(d)}")
    return errors


def run_scan(srcdir: Path) -> list[str]:
    """对给定 doc 根执行完整扫描（断链 + 可达性 + 目录文件清单一致性 + bundle 根 index）。"""
    index_files = index_files_under(srcdir)
    if not index_files:
        return ["未找到任何 index.md"]
    errors, edges = check_broken(index_files, srcdir)
    errors += check_reachable(srcdir, edges, all_md_under(srcdir))
    errors += check_consistency(index_files)
    errors += check_bundle_root_index(srcdir)
    return errors


def self_test() -> bool:
    """破坏性探针双向自检：验证 gate 既能拦截坏结构也能放行好结构。"""
    ok = True
    tmp = Path(tempfile.mkdtemp("checktoctrees"))
    try:
        # 通过用例：index.md 的 toctree 引用内容文档 → 全部可达
        a = tmp / "pass"
        (a / "notes").mkdir(parents=True)
        (a / "notes" / "x.md").write_text("# x\n", encoding="utf-8")
        (a / INDEX_NAME).write_text("```{toctree}\n:hidden:\n\nnotes/x\n```\n", encoding="utf-8")
        # 拦截用例：引用不存在的文档
        b = tmp / "broken"
        b.mkdir()
        (b / INDEX_NAME).write_text("```{toctree}\n\nmissing\n```\n", encoding="utf-8")
        # 拦截用例：内容文档未被任何 toctree 引用（孤立）
        c = tmp / "orphan"
        (c / "notes").mkdir(parents=True)
        (c / "notes" / "x.md").write_text("# x\n", encoding="utf-8")
        (c / "notes" / "y.md").write_text("# y\n", encoding="utf-8")
        (c / INDEX_NAME).write_text("```{toctree}\n\nnotes/x\n```\n", encoding="utf-8")
        # 拦截用例：被引用为 目录/index 但缺 index.md
        d = tmp / "missingidx"
        d.mkdir()
        (d / INDEX_NAME).write_text("```{toctree}\n\nsub/index\n```\n", encoding="utf-8")
        # 拦截用例：目录文件清单不一致——extra.md 可经根 toctree 全局可达，
        # 但其所在目录 a/index.md 的 toctree 未收录自身内容（仅 reachable 检查漏判）
        e = tmp / "consistency"
        (e / "a" / "notes").mkdir(parents=True)
        (e / "a" / "notes" / "x.md").write_text("# x\n", encoding="utf-8")
        (e / "a" / "notes" / INDEX_NAME).write_text("```{toctree}\n\nx\n```\n", encoding="utf-8")
        (e / "a" / "extra.md").write_text("# extra\n", encoding="utf-8")
        (e / "a" / INDEX_NAME).write_text("```{toctree}\n\nnotes/index\n```\n", encoding="utf-8")
        (e / INDEX_NAME).write_text("```{toctree}\n\na/index\na/extra\n```\n", encoding="utf-8")
        # 拦截用例：bundle 根目录(含子目录)缺失 index.md
        f = tmp / "missingbundle"
        (f / "concepts").mkdir(parents=True)
        (f / "concepts" / "x.md").write_text("# x\n", encoding="utf-8")
        (f / "concepts" / INDEX_NAME).write_text("```{toctree}\n\nx\n```\n", encoding="utf-8")

        for name, expect_ok in (("pass", True), ("broken", False), ("orphan", False), ("missingidx", False), ("consistency", False), ("missingbundle", False)):
            errors = run_scan(tmp / name)
            actual_ok = not errors
            if actual_ok == expect_ok:
                state = "放行" if expect_ok else "拦截"
                print(f"自检: {name} → {state} 正确")
            else:
                print(f"自检失败: {name} 期望{'放行' if expect_ok else '拦截'}，实际{'通过' if actual_ok else '拦截'}")
                ok = False
        print("自检通过: check-toctrees.py 既能拦截断链/孤立，也能放行完整 toctree 链。")
        return ok
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return 0 if self_test() else 1

    path_args = [a for a in args if not a.startswith("--")]
    default_mode = not path_args
    targets = list(DEFAULT_SCAN) if default_mode else [Path(a) for a in path_args]

    if default_mode:
        errors = run_scan(ROOT / "doc")
    else:
        index_files = iter_index_files(targets)
        if not index_files:
            print("未找到任何 index.md", file=sys.stderr)
            return 1
        errors, _ = check_broken(index_files, ROOT / "doc")

    if errors:
        print(f"\n检测到 {len(errors)} 处 toctree 导航问题，CI gate 拦截：")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。")
    return 0


if __name__ == "__main__":
    sys.exit(main())