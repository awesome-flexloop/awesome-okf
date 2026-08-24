"""Sphinx 文档构建任务，包装 `invocations.docs` 并注入项目配置。

根 `build` 包装 `invocations.docs` 的构建语义并注入 `-E -b html`，
使 `invoke build` 等价于 CI 原命令 `sphinx-build -E -b html doc _build/html`；
`clean/browse/tree/doctest` 直接复用 `invocations.docs` 原任务。
"""
from __future__ import annotations

import os
import sys

from invoke import task
from invocations import docs


@task(default=True, help=docs.build.help)
def build(
    c,
    clean: bool = False,
    browse: bool = False,
    nitpick: bool = False,
    opts: str = "-b html -E",
    source: str | None = None,
    target: str | None = None,
) -> None:
    """构建 Sphinx HTML（等价 `sphinx-build -E -b html doc _build/html`）。

    <opts> 附加 sphinx-build 参数（默认 `-b html -E`，传空串 `-o ""` 可取消）；
    其余参数语义与 `invocations.docs.build` 一致（clean/browse/nitpick/source/target）。
    """
    if clean:
        docs._clean(c)
    if opts is None:
        opts = ""
    if nitpick:
        opts += " -n -W -T"
    cmd = "sphinx-build{} {} {}".format(
        (" " + opts) if opts else "",
        source or c.sphinx.source,
        target or c.sphinx.target,
    )
    # `invocations.docs.build` 硬编码 pty=True，Windows 无 `pty` 模块会直接中止；
    # 这里对齐其命令构造，但把 pty 改为可配置：POSIX 默认 True（与 CI 行为一致）、
    # Windows 默认 False。可用配置键 run.pty 显式覆盖。
    pty = c.config.get("run", {}).get("pty", sys.platform != "win32")
    c.run(cmd, pty=pty)
    if browse:
        docs._browse(c)


# 复用 invocations.docs 的 clean：仅删 `sphinx.target`（本项目为 `_build/html`）。
# 外层加一个空父目录回收壳，避免留下空的 `_build`。
@task(name="clean")
def clean(c) -> None:
    """删除 Sphinx 构建输出目录 `_build/html`，并回收空父目录 `_build`。"""
    docs._clean(c)
    parent = os.path.dirname(c.sphinx.target)
    while parent and os.path.isdir(parent) and not os.listdir(parent):
        os.rmdir(parent)
        parent = os.path.dirname(parent)


# 直接复用 invocations.docs 的其余任务（browse/tree/doctest），不重实现。
browse = docs._browse
tree = docs.tree
doctest = docs.doctest
