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
    return importlib.util.find_spec(mod) is not None


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
        "SITEMAP_URL_BASE", "https://awesome-flexloop.github.io/"
    )
elif not os.environ.get("READTHEDOCS"):
    if "sphinx_sitemap" not in extensions and _has("sphinx_sitemap"):
        extensions.append("sphinx_sitemap")
    html_baseurl = "http://127.0.0.1:8000/"
    sitemap_url_scheme = "{link}"
sitemap_locales = [None]

ogp_site_url = "https://awesome-okf-xs.readthedocs.io/"
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


