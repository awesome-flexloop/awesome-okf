---
type: reference
scope: omlmd
name: python-version-constraint
version: "0.1.6"
source:
  - https://github.com/containers/omlmd/blob/main/pyproject.toml
  - file:///d:/spaces/SpecWeave/external/dao/action/Containers/omlmd/pyproject.toml
description: |
  omlmd Python 版本约束的完整证据链与校准说明：
  为什么 python = "^3.9" 有效，以及 __future__ import annotations 如何使 3.9 成为可能。
---

# omlmd Python 版本约束来源

## 约束声明

```toml
python = "^3.9"   # poetry：>=3.9, <4.0
```

**ruff**: `target-version = "py39"`
**mypy**: `python_version = "3.9"`

README badge 声明：`python - 3.9|3.10|3.11|3.12`

## 证据链

### 证据 1：pyproject.toml 显式声明

[omlmd/pyproject.toml](file:///d:/spaces/SpecWeave/external/dao/action/Containers/omlmd/pyproject.toml#L16)

```toml
[tool.poetry.dependencies]
python = "^3.9"
```

同时 ruff 锁定 `py39`，mypy 锁定 `"3.9"`。

### 证据 2：全部源文件均有 `__future__` 保护（关键差异点）

[omlmd/omlmd/model_metadata.py:1](file:///d:/spaces/SpecWeave/external/dao/action/Containers/omlmd/omlmd/model_metadata.py#L1)

```python
from __future__ import annotations   # PEP 563
```

以下 5 个源文件均在第一行声明：

| 文件 | 行号 |
|------|------|
| `omlmd/cli.py` | L3 |
| `omlmd/helpers.py` | L1 |
| `omlmd/model_metadata.py` | L1 |
| `omlmd/provider.py` | L1 |
| `omlmd/listener.py` | L1 |

`from __future__ import annotations`（PEP 563）将所有注解保存为**字符串**而非立即求值，从而允许在 Python 3.9 中使用 `str | None`、`dict[str, Any]` 等语法（这些语法在 3.10+ 之前无法直接运行）。

### 证据 3：README 版本 badge

[omlmd/README.md](file:///d:/spaces/SpecWeave/external/dao/action/Containers/omlmd/README.md#L10)

```markdown
[![Python](https://img.shields.io/badge/python%20-3.9%7C3.10%7C3.11%7C3.12-blue)](https://github.com/containers/omlmd)
```

## Limitation（限制）

1. **Python 3.8 及以下不可使用 omlmd**：虽然 `__future__` 保护了注解语法，但依赖项（如 `click ^8.1.7`、`oras >=0.2.23`）可能要求更高版本。
2. **Python 3.9 是最低兼容版本**：文档中提到的"3.9、3.10、3.11、3.12"即完整支持列表，3.13 尚未验证。
3. **`dict[str, Any]` 语法本身在 3.9 可用**：PEP 585（容器类型泛型）从 3.9 开始原生支持，无需 `__future__`，但 `str | None` 需要 `__future__`。

## Prevention（预防措施）

### 安装前检查

```bash
# 快速验证 Python 版本
python --version
# 期望输出：Python 3.9.x 或更高，建议 3.10+

# 确认 Poetry 版本要求
poetry env info --python
```

### 推荐环境

```bash
# 使用 uv 快速创建兼容环境
uv venv --python 3.10
uv pip install omlmd

# 或使用 conda
conda create -n omlmd python=3.10
conda activate omlmd
pip install omlmd
```

### 若误用 Python 3.8 的症状

```
error: package 'omlmd' requires Python >=3.9
```

**应对**：升级 Python 至 3.9+。

### 若误用 Python 3.13 的症状

```
ModuleNotFoundError: No module named 'oras'   # oras 尚未发布 3.13 兼容版本
```

**应对**：降级至 3.12 或使用 `uv` 锁定已知兼容版本。

## 与 olot 的版本差异总结

| 维度 | omlmd | olot |
|------|-------|------|
| 最低 Python 版本 | 3.9 | 3.10 |
| 注解保护方式 | `from __future__ import annotations`（全文件） | 部分文件有，核心 API 无 |
| 核心 API 的注解安全性 | ✅ 3.9 兼容 | ❌ 必须 3.10+ |
| README badge | 明确列出 3.9~3.12 | 无版本信息 |

**选用建议**：
- 需要 **3.9 兼容**（如旧版服务器环境）→ 选 **omlmd**
- 需要 **最新 Python 特性**（如 3.12+）→ **两者均可**，olot 的代码更现代化
