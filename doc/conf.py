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
myst_heading_anchors = 3
myst_commonmark_only = False

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]
numfig = True
nitpicky = False

suppress_warnings = [
    "myst.xref_missing",
    "myst.domains",
    "ref.ref",
    "toc.external",
    "etoc.toctree",
]

copybutton_exclude = '.linenos, .gp'
copybutton_selector = ":not(.prompt) > div.highlight pre"

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
    "show_navbar_depth": 1,
    "max_navbar_depth": 7,
    "collapse_navbar": False,
    "use_download_button": True,
    "use_fullscreen_button": True,
    "footer_content_items": "author.html, copyright.html, last-updated.html, extra-footer.html",
}

# 移除侧边栏冗余搜索框：sphinx-book-theme 默认在侧边栏顶部注入搜索组件，
# 与顶部导航栏搜索框重复，故只保留侧边栏导航，移除搜索字段。
html_sidebars = {
    "**": [
        "sidebar-nav-bs.html",
    ],
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
    """source-read 钩子：为 frontmatter 块内无引号的裸日期/时间戳补上双引号。"""
    text = source[0]
    delims = list(_FRONTMATTER_DELIM.finditer(text))
    if len(delims) < 2:
        return
    fm = text[delims[0].end(): delims[1].start()]
    quoted = _ISO_DATETIME_RE.sub(r'\1"\2"', fm)
    if quoted != fm:
        source[0] = text[: delims[0].end()] + quoted + text[delims[1].start():]


def setup(app):
    app.connect("source-read", _quote_frontmatter_dates)


