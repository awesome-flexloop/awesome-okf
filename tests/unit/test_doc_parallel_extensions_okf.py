"""P0-A2 awesome-okf-xs Sphinx 扩展并行性集成测试（来自七概念 P1-A 审计样板）。

三条用例：
1. test_target_exts_load：TARGET_EXTS 全部真实加载（严格子集断言，V-5 采纳修正：
   环境未装某扩展导致 conf.py _has() 没 append 时，直接 fail 而非 silently pass）
2. test_parallel_allowed_true：setup() 返回 + 所有扩展 parallel_safe 后
   is_parallel_allowed(read|write) = True
3. test_each_ext_parallel_safe_not_none：每条 TARGET_EXTS 及 Sphinx 默认全部扩展
   的 parallel_read_safe / parallel_write_safe 非 None

运行方式：
    cd projects/awesome-okf-xs
    python -m pytest tests/unit/test_doc_parallel_extensions_okf.py -v
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]       # awesome-okf-xs/
DOC  = ROOT / "doc"
sys.path.insert(0, str(DOC))

# 用户层面 TARGET_EXTS = conf.py 字面量（基础 1 + optional 10）+ 主题类扩展
# 注意：_optional_extensions 中声明的扩展只要环境装了就会被 _has() 动态 append
# 这里直接枚举 conf.py 字面量，当环境未装时用例 1 会 fail（V-5 严格子集断言）
TARGET_EXTS = [
    # 必装基础扩展（F-020 = 1）
    "myst_parser",
    # _optional_extensions（F-021 = 10）
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
    # conf.py html_theme 分支可能加载的主题扩展（环境装了会被自动注册到 app.extensions）
    "mystx",
    "sphinx_book_theme",
    "pydata_sphinx_theme",
]


@pytest.fixture(scope="module")
def sphinx_app(tmp_path_factory):
    """module-scoped Sphinx app：parallel=0 避免 Windows Manager() 崩溃，
    然后手动设置 app.parallel=4（扩展元数据的实例属性与 N 无关）。"""
    from sphinx.application import Sphinx

    srcdir   = str(DOC)
    tmp_root = tmp_path_factory.mktemp("okf-doc-build")
    outdir   = str(tmp_root / "html")
    doctreed = str(tmp_root / ".doctrees")

    app = Sphinx(srcdir, srcdir, outdir, doctreed, "html", parallel=0)
    app.parallel = 4
    yield app


class TestDocParallelExtensionsOkf:
    def test_target_exts_load(self, sphinx_app):
        """[V-5 严格子集] 用户声明的 14 条 TARGET_EXTS 必须全部出现在
        app.extensions.keys() 中；环境缺任何一条直接 fail，不再 silently pass。"""
        loaded   = set(sphinx_app.extensions.keys())
        expected = set(TARGET_EXTS)
        missing  = sorted(expected - loaded)
        assert not missing, (
            "以下 TARGET_EXTS 声明但环境未实际加载（conf.py _has() 检测未通过，"
            "需要 pip install 对应依赖或从 TARGET_EXTS 列表中移除）:\n  - "
            + "\n  - ".join(missing)
        )
        # 额外提示：多加载了哪些扩展（不失败，仅调试信息）
        extra = sorted(loaded - expected)
        print(f"[INFO] 声明 {len(expected)} 条、实际加载 {len(loaded)} 条，"
              f"额外自动加载 {len(extra)} 条（Sphinx 默认扩展等，非问题）")

    def test_parallel_allowed_true(self, sphinx_app):
        """read/write 两阶段都允许并行。"""
        assert sphinx_app.is_parallel_allowed("read")  is True
        assert sphinx_app.is_parallel_allowed("write") is True

    def test_each_ext_parallel_safe_not_none(self, sphinx_app):
        """全量 60+ 条扩展 + TARGET_EXTS 14 条，每条的 parallel_read_safe /
        parallel_write_safe 非 None；Fail-Fast 钩子不触发。"""
        blockers: list[str] = []
        for name, ext in sphinx_app.extensions.items():
            pr = getattr(ext, "parallel_read_safe",  None)
            pw = getattr(ext, "parallel_write_safe", None)
            if pr is None or pw is None:
                blockers.append(f"{name}(read={pr!r}, write={pw!r})")
        assert not blockers, (
            "以下扩展 parallel_safe=None，会导致 A-1 的 Fail-Fast 钩子在 CI 崩溃：\n  - "
            + "\n  - ".join(blockers)
        )
