from pathlib import Path
import os
import sys
import subprocess
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


def setup(app):
    """Sphinx setup 钩子：创建 bundles 符号链接/联接。"""
    import platform
    doc_dir = ROOT / 'doc'
    bundles_link = doc_dir / 'bundles'
    bundles_target = ROOT / 'bundles'

    if not bundles_target.exists():
        raise FileNotFoundError(f"bundles 目录不存在: {bundles_target}")

    if bundles_link.is_symlink() or bundles_link.exists():
        try:
            resolved = bundles_link.resolve()
            if resolved == bundles_target.resolve():
                return
        except (OSError, RuntimeError):
            pass
        if bundles_link.is_dir() and not bundles_link.is_symlink():
            raise RuntimeError(
                f"{bundles_link} 已作为普通目录存在，请删除后重试。"
                f"该路径应由 Sphinx 自动创建为指向 {bundles_target} 的链接。"
            )
        if bundles_link.is_symlink():
            bundles_link.unlink()

    if platform.system() == 'Windows':
        try:
            os.symlink(
                str(bundles_target), str(bundles_link), target_is_directory=True
            )
        except OSError:
            subprocess.run(
                ['cmd', '/c', 'mklink', '/J',
                 str(bundles_link), str(bundles_target)],
                check=True, capture_output=True
            )
    else:
        os.symlink(
            str(bundles_target), str(bundles_link), target_is_directory=True
        )
