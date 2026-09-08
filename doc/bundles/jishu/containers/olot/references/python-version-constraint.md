---
type: reference
scope: olot
name: python-version-constraint
version: "1.2.2"
source:
  - https://github.com/containers/olot/blob/main/pyproject.toml
  - file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/pyproject.toml
description: |
  olot Python 版本约束的完整证据链与校准说明：
  为什么 requires-python 是 >=3.10（不是 3.9），以及运行时与开发时双重约束的来源。
---

# olot Python 版本约束来源

## 约束声明

```toml
requires-python = ">=3.10"
```

**ruff**: `target-version = "py310"`
**mypy**: `python_version = "3.10"`

## 证据链

### 证据 1：pyproject.toml 显式声明

[olot/pyproject.toml](file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/pyproject.toml#L14)

```toml
requires-python = ">=3.10"
```

同时 ruff 和 mypy 均锁定 `py310` / `"3.10"`，表明项目设计时以 3.10 为最低目标版本。

### 证据 2：`basics.py` 裸管道注解（决定性证据）

[olot/olot/basics.py](file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/olot/basics.py#L54-L62)

该文件**无** `from __future__ import annotations`，但直接使用：

```python
def oci_layers_on_top(
    ocilayout: str | os.PathLike,           # PEP 604 union syntax
    modelcard: os.PathLike | None = None,   # PEP 604 union syntax
    labels: dict[str, str] | None = None,   # PEP 585 generic syntax
    annotations: dict[str, str] | None = None,
    root_dir: str | os.PathLike | None = None,
):
```

`str | os.PathLike` 是 PEP 604 语法（Python 3.10 引入），在 3.9 下会抛出 `SyntaxError`。
`dict[str, str]` 是 PEP 585 语法（Python 3.9 引入，但作为**运行时**类型注解仅在 3.9+ 有效）。

**结论**：这些注解在函数签名中作为**运行时求值**（无 `__future__` 保护），因此 Python 3.9 无法解析。

### 证据 3：其他文件的 `__future__` 保护是次级证据

[olot/olot/oci/oci_config.py:5](file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/olot/oci/oci_config.py#L5) 等 7 个文件有
`from __future__ import annotations`，但这只是让类型检查器安静，**不解决 basics.py 的问题**。

## 与 omlmd 的关键差异

| 维度 | olot | omlmd |
|------|------|-------|
| `requires-python` | `>=3.10` | `^3.9`（即 `>=3.9, <4.0`） |
| `basics.py` / 核心 API 是否有 `__future__` | **无** | 全部 5 个源文件**有** |
| 裸管道注解（`X | Y`）是否可运行 | 不可（SyntaxError） | 可（`__future__` 延迟求值） |
| ruff target | `py310` | `py39` |
| mypy python_version | `"3.10"` | `"3.9"` |
| README badge | 无版本标注 | `python - 3.9\|3.10\|3.11\|3.12` |

**根本原因**：olot 的核心 API（`oci_layers_on_top`）使用了未受保护的 PEP 604 运行时注解，而 omlmd 的所有源文件均通过 `from __future__ import annotations` 实现了 3.9 兼容。

## Limitation（限制）

1. **Python 3.9 及以下不可使用 olot**：`import olot` 时会立即报 `SyntaxError`，定位在 `olot/basics.py` 的 `oci_layers_on_top` 函数签名。
2. **虚拟环境必须 >= 3.10**：`uv`、`conda`、`pyenv` 创建的 env 版本需 >= 3.10。
3. **CI 矩阵最低版本应为 3.10**：若 CI 有 3.9 测试步骤，会直接失败。

## Prevention（预防措施）

### 安装前检查

```bash
# 快速验证 Python 版本
python --version
# 期望输出：Python 3.10.x 或更高

# 或使用 pyenv 指定版本
pyenv install 3.10
pyenv local 3.10
```

### 在 CI 中锁定版本

```yaml
# GitHub Actions 示例
python-version: ['3.10', '3.11', '3.12']
# 禁止使用 '3.9'
```

### 若误用 Python 3.9 的症状

```
SyntaxError: unsupported operand type(s) for |: 'type' and 'type'
  File ".../olot/basics.py", line 54
    ocilayout: str | os.PathLike,
               ^
```

**应对**：升级 Python 至 3.10+，无需修改 olot 代码。
