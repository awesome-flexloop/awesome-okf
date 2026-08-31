from pathlib import Path
import os
import sys
import importlib.util
import importlib.metadata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'doc'))

project = "awesome-okf-xs"
author = "xinetzone"
try:
    release = importlib.metadata.version("awesome-okf-xs")
except importlib.metadata.PackageNotFoundError:
    release = "0.1.0"
version = release

language = 'zh_CN'


def _has(mod: str) -> bool:
    try:
        return importlib.util.find_spec(mod) is not None
    except (ImportError, ModuleNotFoundError):
        return False


extensions = ["myst_parser"]

_optional_extensions = [
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_tippy",
    "sphinx_sitemap",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinx.ext.graphviz",
    "sphinx_contributors",
    "sphinxext.opengraph",
    "sphinxcontrib.mermaid",
]
for _ext in _optional_extensions:
    if _has(_ext):
        extensions.append(_ext)

myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "deflist",
    "colon_fence",
    "replacements",
    "substitution",
]
# 将 ```mermaid 代码块映射为 sphinxcontrib-mermaid 指令，
# 实现 Markdown 中直接书写 mermaid 图表的原生体验
myst_fence_as_directive = ["mermaid"]
myst_heading_anchors = 3
myst_commonmark_only = False
# 将文档 frontmatter title 注入为 H1，避免无 title 的文档从 H2 开始导致跳级
myst_title_to_header = True

templates_path = ["_templates"]
# `.spec` 为 OKF 生成流程的内部工作目录（含 file:/// 机器绝对路径），不发布；
# 排除以免 Sphinx 对未收录的 .spec/*.md 报 toc.not_included（曾被误用 toctree 引用压制）
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**.ipynb_checkpoints",
    "**/.spec/**",
    "**/.spec",
]
numfig = True
nitpicky = False

suppress_warnings = [
    "myst.xref_missing",
    "myst.domains",
    "ref.ref",
    "toc.external",
    "etoc.toctree",
    "ref.footnote",
    # 内联代码的高亮失败（未知 lexer / lexer 解析错误）在工具类文档中大量存在，
    # 属噪音而非内容错误：置灰并不影响阅读，故统一抑制。
    "misc.highlighting_failure",
    # tippy 提示词需联网抓取 RTD/Wikipedia/DOI，离线构建必然失败并重复告警。
    "tippy.rtd",
    "tippy.wiki",
    "tippy.doi",
]

# tippy 关卡：断开所有需联网的 tooltip 数据源（wiki/doi/rtd），
# 避免离线/CI 环境每次构建重复触发 requests 网络失败警告并拖慢构建。
tippy_enable_wikitips = False
tippy_enable_doitips = False
tippy_rtd_urls = []  # 不登记 RTD 预取源，杜绝 fetch_rtd_tips
# 兜底：命中即跳过该链接，使其既不生成 tooltip 也不进入任何 fetch 集合
tippy_skip_urls = [
    "https://*.readthedocs.io/*",
    "https://www.readthedocs.org/",
    "https://en.wikipedia.org/wiki/",  # 双保险：即便 wikitips 误开也不联网
    "https://doi.org/",
]

copybutton_exclude = '.linenos, .gp'
copybutton_selector = ":not(.prompt) > div.highlight pre"

# --- sphinxcontrib-mermaid 配置 ------------------------------------------
# 使用运行时 JS 渲染（CDN 加载 mermaid.min.js），零构建依赖；
# 版本锁定以避免 CDN 更新导致的渲染不稳定
mermaid_version = "11.4.1"
# mermaid 初始化参数：使用默认主题，支持中文
mermaid_init_js = """
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: '"Noto Sans SC", "Microsoft YaHei", sans-serif',
});
"""

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.14", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
    "myst-parser": ("https://myst-parser.readthedocs.io/en/latest", None),
}

extlinks = {}

if os.environ.get("GITHUB_ACTIONS"):
    html_baseurl = os.environ.get(
        "SITEMAP_URL_BASE", "https://awesome-flexloop.github.io/awesome-okf/"
    )
elif not os.environ.get("READTHEDOCS"):
    if "sphinx_sitemap" not in extensions and _has("sphinx_sitemap"):
        extensions.append("sphinx_sitemap")
    html_baseurl = "http://127.0.0.1:8000/"
# sitemap 链接使用实际文件布局（根路径），避免默认 {lang}/{version}/{link}
# 前缀造成 sitemap URL 与部署文件不一致（404）
sitemap_url_scheme = "{link}"
sitemap_locales = [None]

ogp_site_url = "https://awesome-flexloop.github.io/awesome-okf/"
# 禁用社交卡片图片生成：matplotlib 渲染卡片文本时会把标题中的 $...$
# （如 bundles/katex 文档）当作数学模式解析并崩溃，故仅保留 meta 标签。
ogp_social_cards = {"enable": False}

if _has("mystx"):
    html_theme = "mystx"
elif _has("sphinx_book_theme"):
    html_theme = "sphinx_book_theme"
else:
    html_theme = "alabaster"

html_title = "Awesome OKF for Xuanspace"
html_static_path = ["_static"]
html_css_files = ["local.css"]
html_last_updated_fmt = '%Y-%m-%d, %H:%M:%S'

html_theme_options = {
    "repository_url": "https://github.com/awesome-flexloop/awesome-okf",
    "use_repository_button": True,
    "repository_branch": "main",
    "use_source_button": True,
    "use_edit_page_button": False,
    "use_issues_button": True,
    "path_to_docs": "doc",
    "toc_title": "目录",
    "show_navbar_depth": 10,
    # 侧边栏导航深度：域(L2)→分组(L3)→bundle(L4)。
    # 全深度（6-7 级）会令每页内嵌约 5000 条导航（5640 页 × ~1MB ≈ 5-6GB），
    # 超出 GitHub Pages 1GB 站点限制导致部署失败；bundle 深层页面经各 bundle
    # 首页的手工导航表进入。
    "max_navbar_depth": 4,
    "collapse_navbar": False,
    "use_download_button": True,
    "use_fullscreen_button": True,
    "footer_content_items": "author.html, copyright.html, last-updated.html, extra-footer.html",
    # 移除顶部导航栏搜索框（保留左侧边栏搜索框）
    "navbar_persistent": [],
}

# --- frontmatter 裸日期/时间戳自动加引号 -------------------------------
# myst_parser 会把无引号的 YAML 日期解析为 datetime.date 对象，进而在
# dict_to_fm_field_list 中 json.dumps 时报 "Object of type date is not
# JSON serializable"。此钩子在解析前为 frontmatter 内的裸日期/时间戳补上
# 双引号，避免逐个文件修改。覆盖行级（`stale_after: 2027-02-23`）与
# 嵌套 map（`at: 2026-08-23 }` / `at: 2026-08-23T10:00:00+08:00 }`）两种场景。
import re as _re

_ISO_DATETIME_RE = _re.compile(
    r"([A-Za-z_][A-Za-z0-9_-]*\s*:\s*)"
    r"(\d{4}-\d{2}-\d{2}(?:[Tt]\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2}|Z)?)?)"
)

_FRONTMATTER_DELIM = _re.compile(r"^(?:---|\+\+\+|\.\.\.)\s*$", _re.MULTILINE)


def _quote_frontmatter_dates(app, docname, source):
    """source-read 钩子：为 frontmatter 块内无引号的裸日期/时间戳补上双引号。

    仅当日期/时间戳本身构成完整值时才加引号：值尾允许行尾、行内空白后直接
    换行，或 flow map/list 的闭合标点（``}``/``]``/``,``）。必须避免误伤
    以日期开头的长纯标量（如 ``description: 2026-08-28对博文……``）——
    早期版本无条件替换会在中文值中间插入孤立引号，导致 myst 报
    ``Malformed YAML [myst.topmatter]``。
    """
    text = source[0]
    delims = list(_FRONTMATTER_DELIM.finditer(text))
    # 仅处理真正的 frontmatter：首条定界符必须位于文件起始；否则正文中的
    # 水平线（``---`` transition）会被误当作 frontmatter 栅栏，导致正文被
    # 注入引号。
    if len(delims) < 2 or delims[0].start() != 0:
        return
    fm = text[delims[0].end(): delims[1].start()]

    def _repl(match: _re.Match) -> str:
        # 同一行日期之后的剩余内容（跨行的 key: 值 中日期总在值首行）。
        line_tail = fm[match.end():].split("\n", 1)[0].strip()
        if line_tail == "" or line_tail[-1] in "}]," or line_tail.startswith("#"):
            return match.expand(r'\1"\2"')
        return match.group(0)

    quoted = _ISO_DATETIME_RE.sub(_repl, fm)
    if quoted != fm:
        source[0] = text[: delims[0].end()] + quoted + text[delims[1].start():]


def _dedupe_injected_h1(app, doctree):
    """去除 myst_title_to_header 注入的重复 H1。

    ``myst_title_to_header = True`` 会把 frontmatter title 注入为文档首个 H1；
    若正文自带 H1，doctree 便有两个顶级 section：注入项仅含标题、无正文内容。
    Sphinx TocTreeCollector 会为每个 section 生成一条 TOC 条目，第二条（正文
    H1，携带全部子目录）的链接为 ``#anchor`` 形式；pydata/sphinx_book_theme
    侧边栏会整体删除含 ``#anchor`` 的 li（连嵌套子 ul 一起 decompose），
    导致侧边栏只剩一级导航——这是嵌套目录丢失的根因。

    必须以 priority<500（小于 TocTreeCollector 的默认 500）注册，确保在
    ``process_doc`` 构建 ``env.tocs`` 之前清理 doctree。
    """
    from docutils import nodes

    sections = [n for n in doctree.children if isinstance(n, nodes.section)]
    if len(sections) < 2:
        return
    first = sections[0]
    # 注入 H1 的特征：该 section 只有标题、无任何正文子节点
    if len(first.children) <= 1:
        doctree.remove(first)


def setup(app):
    app.connect("source-read", _quote_frontmatter_dates)
    app.connect("doctree-read", _dedupe_injected_h1, priority=400)


