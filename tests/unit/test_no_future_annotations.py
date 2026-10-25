"""守护门禁：禁止 ``from __future__ import annotations``（PEP 563 样板）。

背景（2026-10-25 复盘 F-3x）：子仓 ``scripts/check-asset-baseline.py`` 在
「上一轮已修复」的记录中被标注为已移除该行，但实测 HEAD 中该行仍在——
**修复声明与修复实际落地脱钩**，靠人工记忆无法发现。

本仓 ``pyproject.toml`` 声明 ``requires-python = ">=3.14"``，注解默认按
PEP 649 惰性求值，该 future import 纯属冗余且语义有别（PEP 563 强制把
注解字符串化，与 PEP 649 的惰性求值不同）。代码生成有语料惯性反复加回，
故在测试层硬阻断——任何文件加回即红。

检测基于 AST（只认真实的 ImportFrom 节点），注释、文档字符串与本守护
自身的字符串常量均不误报。扫描范围：``scripts/``、``tasks/``、``tests/``
（``.temp/`` 为临时目录，不受版本控制，按项目约定不进扫描）。

运行方式：
    cd projects/awesome-okf-xs
    python -m pytest tests/unit/test_no_future_annotations.py -v
"""

import ast
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]  # tests/unit/ → tests/ → 仓根
_SCAN_DIRS = ("scripts", "tasks", "tests")


def _py_files() -> list[Path]:
    files: list[Path] = []
    for dirname in _SCAN_DIRS:
        base = _PROJECT_ROOT / dirname
        if not base.exists():
            continue
        files.extend(sorted(base.rglob("*.py")))
    return files


def _has_future_annotations(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.module != "__future__":
            continue
        if any(alias.name == "annotations" for alias in node.names):
            return True
    return False


@pytest.mark.parametrize(
    "path",
    _py_files(),
    ids=lambda p: p.relative_to(_PROJECT_ROOT).as_posix(),
)
def test_no_future_annotations(path: Path) -> None:
    assert not _has_future_annotations(path), (
        f"{path.relative_to(_PROJECT_ROOT).as_posix()} 含冗余的 PEP 563 future import；"
        "Python 3.14+ 已默认 PEP 649 惰性注解，直接删除该行"
    )


def test_scan_scope_is_not_empty() -> None:
    """守护自身有效性自检：扫描范围非空。

    若扫描目录改名/删除导致探针恒零，本守护会退化为「零断言通过」——
    与 E-05 同类盲区：规则未被证伪能力等于没有规则。
    """
    files = _py_files()
    assert files, (
        f"扫描范围 {_SCAN_DIRS} 下未找到任何 .py 文件；"
        "守护探针恒零 = 校验形同虚设，请检查目录结构是否改名"
    )
