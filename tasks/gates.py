"""CI 质量门任务——封装 scripts/ 下的检查脚本为 invoke 任务。

用法::

    invoke gates.utf8          # UTF-8 有效性检查
    invoke gates.toctrees      # toctree 导航完整性检查
    invoke gates.bundles       # 总索引计数与目录树三角对账
    invoke gates.assetbaseline # 库规模基线口径校验（HEAD 锚定 + 三处规模数字一致 + 行尾归一）
    invoke gates.redline       # Python 红线守护（禁止 PEP 563 future import，AST 检测）
    invoke gates.all           # 运行全部质量门
"""
from pathlib import Path

from invoke import task

ROOT = Path(__file__).resolve().parent.parent  # tasks/gates.py → tasks/ → 项目根
SCRIPTS = ROOT / "scripts"
TESTS = ROOT / "tests"


@task
def utf8(c, self_test: bool = False):
    """检查 doc/ 下所有 Markdown 文件的 UTF-8 有效性。"""
    flag = " --self-test" if self_test else ""
    c.run(f"python {SCRIPTS / 'check-utf8.py'}{flag}")


@task
def toctrees(c, self_test: bool = False):
    """检查 doc/bundles 的 index.md/toctree 导航完整性。"""
    flag = " --self-test" if self_test else ""
    c.run(f"python {SCRIPTS / 'check-toctrees.py'}{flag}")


@task
def bundles(c, self_test: bool = False):
    """检查总索引计数与目录树一致（锚点组识别 + 束/组/域三角对账）。"""
    flag = " --self-test" if self_test else ""
    c.run(f"python {SCRIPTS / 'check-bundles-index.py'}{flag}")


@task
def assetbaseline(c, self_test: bool = False):
    """检查库规模基线口径（HEAD 锚定 + 三处规模数字一致 + 行尾归一 + .spec 泄漏守卫）。"""
    flag = " --self-test" if self_test else ""
    c.run(f"python {SCRIPTS / 'check-asset-baseline.py'}{flag}")


@task
def redline(c):
    """Python 红线守护：禁止 ``from __future__ import annotations``（PEP 563 样板）。

    依据父仓 AGENTS.md「Python 红线」条目：本仓 requires-python >= 3.14，
    注解默认按 PEP 649 惰性求值，该 future import 冗余且语义有别。
    采用 AST 检测（只认真实 ImportFrom 节点），注释与文档字符串不误报。
    """
    c.run(
        f"python -m pytest {TESTS / 'unit' / 'test_no_future_annotations.py'} -v",
        pty=False,
    )


@task(default=True)
def all(c):
    """运行全部 CI 质量门（utf8 + toctrees + bundles 计数对账 + 资产基线口径 + Python 红线，含自检探针）。"""
    c.run(f"python {SCRIPTS / 'check-utf8.py'}")
    c.run(f"python {SCRIPTS / 'check-utf8.py'} --self-test")
    c.run(f"python {SCRIPTS / 'check-toctrees.py'}")
    c.run(f"python {SCRIPTS / 'check-toctrees.py'} --self-test")
    c.run(f"python {SCRIPTS / 'check-bundles-index.py'}")
    c.run(f"python {SCRIPTS / 'check-bundles-index.py'} --self-test")
    c.run(f"python {SCRIPTS / 'check-asset-baseline.py'}")
    c.run(f"python {SCRIPTS / 'check-asset-baseline.py'} --self-test")
    c.run(
        f"python -m pytest {TESTS / 'unit' / 'test_no_future_annotations.py'} -v",
        pty=False,
    )
