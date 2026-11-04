#!/usr/bin/env python3
"""CI gate：校验 Markdown 章节锚点（`#fragment`）在目标文件中真实可解析。

背景：`check-toctrees.py` 校验导航链可达，`check-links.py` 类校验目标文件存在——
两者都**不校验 `#fragment` 片段**。于是「改了标题、没改引用」能在所有既有门禁全绿
的前提下留下坏链：正文渲染出来点击无反应。本仓实战即出现全仓数百处。

**判定规则必须与部署一致**（本脚本的规则来自 Sphinx 9.2.0 + myst-parser 5.1.0
真身实测，不是手抄的猜测）：

| 引用形式 | 命中什么才算有效 | 依据 |
|---|---|---|
| 同文档 `#frag` | 标题的 **MyST slug**（GitHub 风格、保留 CJK）／标题的 **docutils id**／**HTML 锚点** `<a id=...>` | MyST `render_link_anchor` 用 slug 匹配同文档标题 |
| 跨文档 `file.md#frag` | 目标文件的 **docutils id** 或 **HTML 锚点** | docutils 跨文档引用只认目标文档已注册的 id |

**关键陷阱（MyST 5.x 实测）**：
- MyST **行内** `{#id}`：id 生效，但**标题文本残留** `{#id}`，且会与自动 id 拼接
  （`hosted-network` → `hosted-network-hosted-network`）⇒ 不可用；
- MyST **行外** `{#id}`：**完全不生效** ⇒ 不可用；
- 纯中文标题的 docutils id 为空（docutils 会剔除全部非 ASCII 字符），回落到
  `idN` **全局递增序号** ⇒ 跨文档不可稳定引用 ⇒ 必须用 **HTML 锚点**：
  `<a id="xxx"></a>`（独占一行、前后留空行）。
- slug 与 docutils id 是**两套规则**：slug 保留 CJK，docutils id 剔除 CJK 且
  **去掉首尾数字**（`4.1 统一模型` → `''`）。

**用法**:
    python scripts/check-section-anchors.py                 # 扫描 doc/（默认，递归）
    python scripts/check-section-anchors.py PATH...         # 扫描指定目录/文件
    python scripts/check-section-anchors.py --self-test     # 破坏性探针双向自检

退出码:
    0  无断链（CI 通过）；或自检通过
    1  存在断链 / 目标缺失（CI gate 拦截）；或自检发现 gate 失效

注意：仓库现存大量**纯中文标题的跨文档锚点引用**（MyST 结构性限制，非笔误）。
本脚本将其单列为「不可锚定」警告类，不计入退出码——判定「笔误」与「结构性
限制」必须分开，否则门禁会因存量噪声被整体忽略。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCAN = (ROOT / "doc",)
EXCLUDE_DIRS = {"_build", "_static", ".git", ".spec", "__pycache__"}

FENCE_RE = re.compile(r"^\s*(```|~~~)")
ATX_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
SETEXT_RE = re.compile(r"^(=+|-+)\s*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
HTML_ANCHOR_RE = re.compile(r'<a\s[^>]*\bid="([^"]+)"', re.I)
EXTERNAL_SCHEMES = ("http://", "https://", "mailto:", "tel:", "ftp://", "file://")

# --- 真身规则：优先用现场库，缺失时用等价内置实现 ---------------------------
try:  # docutils 的 make_id（跨文档 id 的唯一权威来源）
    from docutils.nodes import make_id as _docutils_make_id

    HAVE_DOCUTILS = True
except ImportError:  # pragma: no cover - 环境降级
    HAVE_DOCUTILS = False

try:  # MyST 的 default_slugify（同文档 #frag 的匹配规则）
    from myst_parser.mdit_to_docutils.base import default_slugify as _myst_slugify

    HAVE_MYST = True
except ImportError:  # pragma: no cover - 环境降级
    HAVE_MYST = False


def make_id(text: str) -> str:
    """标题的 docutils id（跨文档引用用）。

    docutils 语义：lower → ASCII 标点剔除 → 剔除全部非 ASCII（NFKD+ascii ignore）
    → 空白折叠为 `-` → **去掉首尾的连字符与数字**。纯中文标题结果为空。
    """
    if HAVE_DOCUTILS:
        return _docutils_make_id(text)
    s = text.lower()
    s = re.sub(r"[!\"$%&'()*+,/:;<=>?@\[\\\]^`{|}~]", "", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", "-", " ".join(s.split()))
    return re.sub(r"^[-0-9]+|-+$", "", s)


def myst_slug(text: str) -> str:
    """标题的 MyST slug（同文档 `#frag` 匹配用；GitHub 风格，保留 CJK）。"""
    if HAVE_MYST:
        return _myst_slugify(text)
    s = text.lower().replace(" ", "-")
    return re.sub(r"[^\w\-一-鿿]", "", s, flags=re.UNICODE)


def strip_inline(text: str) -> str:
    t = text.strip()
    t = re.sub(r"`([^`]*)`", r"\1", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*([^*]+)\*", r"\1", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"<[^>]+>", "", t)
    return t.strip()


def collect_titles(path: Path) -> list[str]:
    """收集文件内的标题原文（跳过围栏代码块内的伪标题）。"""
    titles: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return titles
    in_fence = False
    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = ATX_RE.match(line)
        if m:
            titles.append(strip_inline(m.group(2)))
        elif (
            i + 1 < len(lines)
            and SETEXT_RE.match(lines[i + 1])
            and line.strip()
            and not ATX_RE.match(line)
        ):
            titles.append(strip_inline(line))
    return titles


def collect_ids(path: Path) -> dict[str, set[str]]:
    """返回 {docutils_ids, slugs, html_anchors}。"""
    docutils_ids: set[str] = set()
    slugs: set[str] = set()
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {"docutils": docutils_ids, "slug": slugs, "html": set()}
    for t in collect_titles(path):
        did = make_id(t)
        if did:
            docutils_ids.add(did)
        slugs.add(myst_slug(t))
    html_ids = set(HTML_ANCHOR_RE.findall(text))
    return {"docutils": docutils_ids, "slug": slugs, "html": html_ids}


def iter_targets(target: Path):
    if target.is_file():
        yield target
        return
    for p in sorted(target.rglob("*.md")):
        rel = p.relative_to(target)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        yield p


def scan(targets) -> tuple[list[str], list[str]]:
    """返回 (断链清单, 不可锚定清单)。"""
    files: list[Path] = []
    for t in targets:
        files.extend(iter_targets(t))
    files = sorted(set(files))

    ids: dict[Path, dict[str, set[str]]] = {f: collect_ids(f) for f in files}

    broken: list[str] = []
    unanchorable: list[str] = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        in_fence = False
        for i, line in enumerate(text.splitlines()):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for raw in LINK_RE.findall(line):
                target = raw.strip()
                # Sphinx/RST 风格允许尖括号包裹路径（<../x.md#frag>）
                if target.startswith("<") and target.endswith(">"):
                    target = target[1:-1].strip()
                if target.startswith(EXTERNAL_SCHEMES):
                    continue
                if "#" not in target:
                    path_part = target
                    frag = ""
                else:
                    path_part, _, frag = target.partition("#")
                    frag = frag.strip()
                if path_part == "":
                    if not frag:
                        continue
                    own = ids[f]
                    if frag in own["slug"] or frag in own["docutils"] \
                            or frag in own["html"]:
                        continue
                    broken.append(f"{f.name}:{i + 1} 锚点不存在 #{frag}")
                    continue
                resolved = (f.parent / path_part).resolve()
                if not resolved.is_file():
                    broken.append(
                        f"{f.name}:{i + 1} 目标文件不存在 {path_part}"
                        f"（相对路径层级是否算错？）")
                    continue
                if not frag:
                    continue
                other = ids.get(resolved)
                if other is None:
                    # 目标不在扫描范围内：只校验文件存在
                    continue
                if frag in other["docutils"] or frag in other["html"]:
                    continue
                if frag in other["slug"]:
                    # slug 只在同文档有效；跨文档需 docutils id 或 HTML 锚点
                    unanchorable.append(
                        f"{f.name}:{i + 1} 跨文档引用 #{frag} 命中目标标题的 "
                        f"MyST slug，但 slug 仅同文档有效——跨文档需用 "
                        f"docutils id 或 `<a id=...>` HTML 锚点")
                    continue
                broken.append(f"{f.name}:{i + 1} 锚点不存在 {target}")
    return broken, unanchorable


def self_test() -> int:
    """破坏性探针双向自检：证明每条规则确实能命中，而不是恒真通过。"""
    print("=" * 60)
    print("check-section-anchors.py 自检探针")
    print("=" * 60)
    print(f"  真身库：docutils={'有' if HAVE_DOCUTILS else '无(降级)'} "
          f"myst={'有' if HAVE_MYST else '无(降级)'}")
    failures: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")
        if not cond:
            failures.append(name)

    import shutil
    import tempfile

    tmp = Path(tempfile.mkdtemp("checksectionanchors"))
    try:
        # 探针 1：docutils id 语义——中文标题为空、ASCII 标题去首尾数字
        check("纯中文标题 docutils id 为空", make_id("四、未闭环项") == "",
              f"got={make_id('四、未闭环项')!r}")
        check("数字前缀被去掉（非保留）", make_id("4.1 统一模型") == "",
              f"got={make_id('4.1 统一模型')!r}")
        check("ASCII 词标题 id 保留", make_id("六、Hosted Network 辨析")
              == "hosted-network",
              f"got={make_id('六、Hosted Network 辨析')!r}")

        # 探针 2：MyST slug 语义——保留 CJK
        check("slug 保留 CJK", "庞朴" in myst_slug("五、庞朴「一分为三」"),
              f"got={myst_slug('五、庞朴「一分为三」')!r}")

        # 探针 3：同文档断链必须被命中，正确锚点不得误报
        (tmp / "a.md").write_text(
            "# 四、未闭环项\n\n正文\n\n"
            "见 [正确](#四未闭环项) 与 [错误](#完全不存在的锚点)\n",
            encoding="utf-8",
        )
        broken, unanchorable = scan([tmp])
        check("同文档断链被命中",
              any("完全不存在的锚点" in b for b in broken), f"broken={broken}")
        check("同文档正确锚点不误报",
              not any("四未闭环项" in b for b in broken), f"broken={broken}")

        # 探针 4：HTML 锚点必须被识别
        (tmp / "b.md").write_text(
            "## 五、未闭环项\n\n<a id=\"open-items\"></a>\n\n正文\n",
            encoding="utf-8",
        )
        (tmp / "c.md").write_text(
            "见 [跨文档 HTML 锚点](b.md#open-items)\n", encoding="utf-8"
        )
        broken, unanchorable = scan([tmp])
        check("跨文档 HTML 锚点被识别",
              not any("open-items" in b for b in broken), f"broken={broken}")

        # 探针 5：跨文档 docutils id 必须被识别
        (tmp / "d.md").write_text(
            "## 六、Hosted Network 辨析\n\n正文\n", encoding="utf-8"
        )
        (tmp / "e.md").write_text(
            "见 [跨文档 docutils id](d.md#hosted-network)\n", encoding="utf-8"
        )
        broken, unanchorable = scan([tmp])
        check("跨文档 docutils id 被识别",
              not any("hosted-network" in b for b in broken), f"broken={broken}")

        # 探针 6：跨文档用 slug 必须落入「不可锚定」而非静默放过
        (tmp / "f.md").write_text(
            "## 五、庞朴「一分为三」：中国哲学内部的独立印证\n\n正文\n",
            encoding="utf-8",
        )
        (tmp / "g.md").write_text(
            "见 [跨文档 slug](f.md#五庞朴一分为三中国哲学内部的独立印证)\n",
            encoding="utf-8",
        )
        broken, unanchorable = scan([tmp])
        check("跨文档 slug 归入不可锚定",
              any("slug" in u for u in unanchorable),
              f"unanchorable={unanchorable}")
        check("跨文档 slug 不误判为普通断链",
              not any("庞朴" in b for b in broken), f"broken={broken}")

        # 探针 7：目标文件缺失（相对路径层级错）必须被命中
        (tmp / "h.md").write_text(
            "见 [层级错](../../iot/oray/index.md)\n", encoding="utf-8"
        )
        broken, unanchorable = scan([tmp])
        check("目标文件缺失被命中",
              any("目标文件不存在" in b for b in broken), f"broken={broken}")

        # 探针 8：围栏代码块内的伪标题与伪链接不得参与判定
        (tmp / "i.md").write_text(
            "```\n# 伪标题\n```\n\n见 [伪链接](#伪标题)\n", encoding="utf-8"
        )
        broken, unanchorable = scan([tmp])
        check("围栏内伪链接不参与判定",
              not any("伪链接" in b for b in broken), f"broken={broken}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failures:
        print(f"自检失败：{len(failures)} 项 — {failures}")
        return 1
    print("自检通过：所有校验规则均可命中（规则本身有效）")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    targets = [Path(a) for a in args if not a.startswith("-")] or list(DEFAULT_SCAN)
    missing = [t for t in targets if not t.exists()]
    if missing:
        print(f"错误: 路径不存在: {missing[0]}", file=sys.stderr)
        return 2

    broken, unanchorable = scan(targets)
    n = sum(1 for t in targets for _ in iter_targets(t))
    print(f"扫描文件：{n}")

    if unanchorable:
        print(f"\n不可锚定警告（{len(unanchorable)} 处）——MyST 结构性限制，"
              f"非笔误，不计入失败：")
        for u in unanchorable[:20]:
            print(f"  ! {u}")
        if len(unanchorable) > 20:
            print(f"  ... 其余 {len(unanchorable) - 20} 处")

    if broken:
        print(f"\n断链（{len(broken)} 处）——CI gate 拦截：")
        for b in broken[:40]:
            print(f"  - {b}")
        if len(broken) > 40:
            print(f"  ... 其余 {len(broken) - 40} 处")
        print("\n处置：① 目标标题为纯中文时，跨文档引用须改用 `<a id=...>` HTML 锚点；")
        print("      ② 目标文件不存在时核对相对路径层级；③ 其余按 docutils id 规则修正 fragment。")
        return 1

    print(f"\n锚点检查通过：全部章节锚点可解析。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
