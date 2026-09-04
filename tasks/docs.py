"""Sphinx 文档构建任务，包装 `invocations.docs` 并注入项目配置。

根 `build` 包装 `invocations.docs` 的构建语义并注入 `-b html`，
使 `invoke build` 等价于 `sphinx-build -b html <auto parallel> doc _build/html`；
默认 opts=None 时按运行环境自动注入并行 flag（_parallel_flag 三档分流）。
`clean/browse/tree/doctest` 直接复用 `invocations.docs` 原任务。

P3 新增 `build_invs`：按 9 域分片生成独立 objects.inv（供 PR 分片构建弥合 VC-5 裸文本）。
Example:
    invoke build-invs                    # 全 9 域
    invoke build-invs -d jishu           # 单域 (meta/guoxue/.../jishu)
"""
import os
import re
import shutil
import sys
from multiprocessing import cpu_count
from pathlib import Path

from invoke import task
from invocations import docs


# ---------------------------------------------------------------------------
# 全局常量：9 域白名单（与 conf.py _OKF_DOMAINS 同源，避免分散硬编码）
# ---------------------------------------------------------------------------
_OKF_DOMAINS = (
    "meta", "guoxue", "zhexue", "kexue", "wenxue",
    "yixue", "sheke", "yishu", "jishu",
)

# inventory builder 的 HTML/inv 输出父目录（每域独立，避免 9 域共用 objects.inv）
_INV_SCRATCH_ROOT = Path("_build") / "domain-inv-scratch"
_INV_OUTPUT_DIR = Path("_build") / "domain-invs"


# ---------------------------------------------------------------------------
# 并行构建策略（P1-D W-A2 · 对齐 mystx.tasks 行为）
#   分流规则（与 mystx 完全一致，零新增依赖）：
#     CI (GITHUB_ACTIONS)          → -j min(cpu_count, 8)   稳定优先，避免 IPC 爆炸
#     本地 POSIX (非 win32)         → -j max(1, cpu_count-1)  留 1 核给桌面响应
#     本地 Windows                  → 空串（不自加 -j）Sphinx 天然串行，避免告警
# ---------------------------------------------------------------------------

def _parallel_flag() -> str:
    """按运行环境返回 ``-j N`` 字符串；Windows 返回空串。"""
    if os.environ.get("GITHUB_ACTIONS"):
        try:
            n = max(1, min(cpu_count() or 1, 8))
        except NotImplementedError:
            n = 4
        return f"-j {n}"
    if sys.platform == "win32":
        return ""
    try:
        n = max(1, (cpu_count() or 2) - 1)
    except NotImplementedError:
        n = 1
    return f"-j {n}"


_J_FLAG_RE = re.compile(r"(?:^|\s)-j\s+(auto|\d+)")


def _sphinx_source(c) -> str:
    """对齐 invocations.docs：读取 conf 中 c.sphinx.source，无则默认 doc/。"""
    try:
        return c.sphinx.source
    except Exception:
        return "doc"


def _sphinx_target(c) -> str:
    try:
        return c.sphinx.target
    except Exception:
        return "_build/html"




@task(default=True, help=docs.build.help)
def build(
    c,
    clean: bool = False,
    browse: bool = False,
    nitpick: bool = False,
    opts: str | None = None,
    source: str | None = None,
    target: str | None = None,
) -> None:
    """构建 Sphinx HTML（走增量构建缓存，opts=None 自动按环境分流并行度）。

    默认行为（opts=None）：
      - ``-b html`` + ``_parallel_flag()`` 自动注入 CI/本地 POSIX/Windows 三档。

    显式传 opts 时完全尊重，不自动注入。
    如需强制全量重建：``invoke build -o "-b html -E"``。

    **VC-8 防回归**：opts 与 $SPHINXOPTS 若各含一个 ``-j``，直接 ValueError 报错退出，
    避免两处同时传 -j 取最后一个的歧义行为。
    """
    if clean:
        docs._clean(c)

    # --- 拼接 opts --------------------------------------------------------
    if opts is None:
        opts = "-b html"
        pf = _parallel_flag()
        if pf:
            opts = f"{opts} {pf}"
    opts = (opts or "").strip()

    # SPHINXOPTS 环境变量合并（对齐 xuanspace）
    env_sphinxopts = os.environ.get("SPHINXOPTS", "").strip()

    # --- VC-8 双 -j 防歧义 ------------------------------------------------
    j_opts = _J_FLAG_RE.findall(opts)
    j_env = _J_FLAG_RE.findall(env_sphinxopts)
    if j_opts and j_env:
        raise ValueError(
            f"[tasks/docs] 检测到 opts 和 $SPHINXOPTS 同时包含 -j flag："
            f"opts 传入 -j {j_opts[-1]!r}，环境变量 SPHINXOPTS 传入 -j {j_env[-1]!r}，"
            f"二选一即可，禁止重复传避免 Sphinx 静默取后者造成回归。"
        )
    if env_sphinxopts:
        opts = (opts + " " + env_sphinxopts).strip()

    if nitpick:
        opts += " -n -W -T"

    cmd = "sphinx-build{} {} {}".format(
        (" " + opts) if opts else "",
        source or _sphinx_source(c),
        target or _sphinx_target(c),
    )
    pty = c.config.get("run", {}).get("pty", sys.platform != "win32")
    c.run(cmd, pty=pty)
    if browse:
        docs._browse(c)


# ---------------------------------------------------------------------------
# P3：域级 objects.inv 预生成器（弥合 PR 分片模式下的 VC-5 裸文本）
# ---------------------------------------------------------------------------
@task(name="build-invs", help={
    "domain": "单域名 ∈ {meta, guoxue, zhexue, kexue, wenxue, yixue, sheke, yishu, jishu}；"
              "不传（None）= 全 9 域串行生成",
})
def build_invs(c, domain: str | None = None) -> None:
    """按 9 域分片生成独立 objects.inv → ``_build/domain-invs/<domain>.inv``。

    PR 流水线用法（弥合 VC-5 跨域 xref 裸文本降级）：
      1. Warmup：invoke build-invs（9 域 inv 生成 + cache 命中则跳过）
      2. Shard：OKF_BUILD_DOMAIN=jishu OKF_INV_DIR=_build/domain-invs invoke build
      3. Save：将 _build/domain-invs/* 回写 cache（save-always=true）

    单域示例：
        invoke build-invs -d jishu
    """
    # VC-18：白名单校验（与 conf.py VC-4 同一列表，不重复逻辑）
    if domain is not None:
        domain = domain.strip().lower()
        if domain not in _OKF_DOMAINS:
            raise ValueError(
                f"[tasks/docs] build_invs(domain={domain!r}) 非法。"
                f"合法值 ∈ {', '.join(_OKF_DOMAINS)}；None = 全 9 域"
            )
        to_build = [domain]
    else:
        to_build = list(_OKF_DOMAINS)

    # VC-15：所有目标域 doc/bundles/<domain> 目录必须存在；少 1 域整条任务非 0 退出
    project_root = Path(__file__).resolve().parents[1]
    for d in to_build:
        bundle_dir = project_root / "doc" / "bundles" / d
        assert bundle_dir.is_dir(), (
            f"[tasks/docs] build_invs 域 {d} doc/bundles/{d} 不存在，"
            f"请确认 OKF_DOMAINS 列表与实际目录一致"
        )

    # VC-17：先清理再重建（防止上次 Ctrl+C 留下 partial inv）
    shutil.rmtree(_INV_SCRATCH_ROOT, ignore_errors=True)
    shutil.rmtree(_INV_OUTPUT_DIR, ignore_errors=True)
    _INV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    prev_okf = os.environ.get("OKF_BUILD_DOMAIN")
    prev_okf_inv_dir = os.environ.get("OKF_INV_DIR")
    try:
        for d in to_build:
            # VC-12：先把域写入环境变量（优先级 > task 参数），build() 内部通过 _parallel_flag 等读取
            os.environ["OKF_BUILD_DOMAIN"] = d
            # 每域独立 scratch：scratch/d/html/objects.inv
            scratch_html = _INV_SCRATCH_ROOT / d / "html"
            scratch_doctree = _INV_SCRATCH_ROOT / d / "doctrees"
            scratch_html.mkdir(parents=True, exist_ok=True)
            scratch_doctree.mkdir(parents=True, exist_ok=True)

            # inventory builder：-b inventory 只生成 objects.inv（不渲染 HTML，速度 ≈ 0.3× full build）
            opts = f"-b inventory -d {scratch_doctree} --keep-going"
            pf = _parallel_flag()
            if pf:
                opts = f"{opts} {pf}"

            cmd = (
                f"sphinx-build {opts} "
                f"{_sphinx_source(c)} {scratch_html}"
            )
            pty = c.config.get("run", {}).get("pty", sys.platform != "win32")
            c.run(cmd, pty=pty)

            # VC-13：move 到 domain-invs/<domain>.inv；move 失败/不存在直接 AssertionError 带域名
            src_inv = scratch_html / "objects.inv"
            dst_inv = _INV_OUTPUT_DIR / f"{d}.inv"
            assert src_inv.is_file(), (
                f"[tasks/docs] build_invs({d})：Sphinx inventory builder "
                f"未输出 objects.inv（路径={src_inv}）。Sphinx 是否启用了 sphinx.ext.intersphinx？"
            )
            shutil.move(str(src_inv), str(dst_inv))
            # VC-17 第二道防线：size>1024 防 partial/空（meta 域 90 份 md 约=3033 bytes；
            #   jishu 域 7405 份 md 预估>50KB。1024=Sphinx inv 4行 header(≈200B)+
            #   zlib 最小压缩体≈800B 安全下限，防止写入空/截断 inv。
            #   旧阈值 8192 对 meta/wenxue 等小域过严。
            size = dst_inv.stat().st_size
            assert size > 1024, (
                f"[tasks/docs] build_invs({d})：inv 大小 {size} bytes ≤ 1024，"
                f"疑似 partial/空 inv；禁止写入 cache。请检查 Sphinx 日志。"
            )
    finally:
        if prev_okf is None:
            os.environ.pop("OKF_BUILD_DOMAIN", None)
        else:
            os.environ["OKF_BUILD_DOMAIN"] = prev_okf
        if prev_okf_inv_dir is None:
            os.environ.pop("OKF_INV_DIR", None)
        else:
            os.environ["OKF_INV_DIR"] = prev_okf_inv_dir



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
