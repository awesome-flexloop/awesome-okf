---
type: Concept
title: 构建系统
description: 理解 hatchling 构建后端、pyproject.toml 配置、PEP 517/621 标准、shared-data 机制，以及如何构建和分发 Jupyter Server 扩展的 Python wheel。
tags: [build-system, hatchling, pep-517, pep-621, wheel, packaging]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:10:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pyproject
    resource: /references/pyproject-source.md
    title: pyproject.toml 模板字段全解析
---

## 现代 Python 打包标准

本模板使用现代 Python 打包标准，不使用传统的 setup.py 或 setup.cfg：

| 标准 | 全称 | 作用 |
|------|------|------|
| PEP 517 | 构建后端接口 | 定义构建系统的标准接口（build-backend） |
| PEP 518 | 构建依赖 | 指定构建系统依赖（build-system.requires） |
| PEP 621 | 项目元数据 | 在 pyproject.toml 中声明项目元数据 |
| PEP 660 | 可编辑安装 | 定义 pip install -e 的标准 |

所有配置统一在 `pyproject.toml` 文件中，替代了分散在 setup.py、setup.cfg、MANIFEST.in 等多个文件中的配置。

## Hatchling 构建后端

```toml
[build-system]
requires = ["hatchling>=1.5"]
build-backend = "hatchling.build"
```

[Hatchling](https://hatch.pypa.io/latest/) 是 [Hatch](https://hatch.readthedocs.io/) 项目的构建后端，是一个现代、快速、标准兼容的 PEP 517 构建后端。

为什么选择 hatchling 而不是 setuptools：
- **原生 PEP 621 支持**：不需要额外插件
- **自动包发现**：自动发现 Python 包目录，无需手动配置 `packages`
- **shared-data 支持**：原生支持将非代码文件安装到 sys.prefix 下的任意位置
- **无遗留配置**：不需要 setup.py 或 setup.cfg
- **速度快**：比 setuptools 更快的构建速度

## 项目元数据（PEP 621）

```toml
[project]
name = "my-server-extension"
authors = [{name = "Your Name", email = "you@example.com"}]
dynamic = ["version"]
readme = "README.md"
requires-python = ">=3.8"
keywords = ["Jupyter", "Extension"]
classifiers = [...]
dependencies = ["jupyter_server>=1.6,<3"]
```

### name

分发名称（PyPI 上的名称），可以包含连字符。Python 导入名与分发名可以不同（通过目录名映射），但推荐保持一致或用下划线替代连字符。

### dynamic = ["version"]

声明 `version` 字段是动态获取的（从代码中读取），而不是静态声明在 pyproject.toml 中。版本源由 `[tool.hatch.version]` 指定。

### dependencies

核心运行时依赖列表。模板只依赖 `jupyter_server>=1.6,<3`：
- `>=1.6`：需要 ExtensionApp 等现代 API
- `<3`：排除 Jupyter Server 3.0（可能有 breaking changes）

依赖声明遵循 [PEP 440](https://peps.python.org/pep-0440/) 版本规范。

## 版本管理

```toml
[tool.hatch.version]
path = "my_server_extension/__init__.py"
```

hatchling 从 `__init__.py` 文件中读取 `__version__` 变量作为包版本：

```python
# my_server_extension/__init__.py
__version__ = "0.1.0"
```

这是"单源版本"模式——版本号只在一个地方定义（`__init__.py`），构建时和运行时使用同一个值。

## 可选依赖组

```toml
[project.optional-dependencies]
test = ["pytest>=7.0", "pytest-jupyter[server]>=0.6"]
lint = ["black>=22.6.0", "mdformat>0.7", "mdformat-gfm>=0.3.5", "ruff>=0.0.156"]
typing = ["mypy>=0.990"]
```

用户可以选择性安装：

```bash
pip install -e ".[test]"           # 安装测试依赖
pip install -e ".[test,lint]"      # 安装测试 + lint 依赖
pip install -e ".[test,lint,typing]"  # 安装所有开发依赖
```

## shared-data——Jupyter 配置安装

这是 Jupyter 扩展构建中最关键的配置：

```toml
[tool.hatch.build.targets.wheel.shared-data]
"jupyter-config" = "etc/jupyter"
```

shared-data 机制将源目录映射到 wheel 中的目标路径，pip install 时解压到 `{sys.prefix}/` 下：

```
源：项目根目录/jupyter-config/jupyter_server_config.d/my_extension.json
  ↓ (wheel 打包时)
wheel 内：etc/jupyter/jupyter_server_config.d/my_extension.json
  ↓ (pip install 时)
安装到：{sys.prefix}/etc/jupyter/jupyter_server_config.d/my_extension.json
```

这就是 Jupyter Server 能自动发现扩展的原因——配置文件被安装到了 Jupyter 扫描的标准目录。

### setuptools 等价配置

如果使用 setuptools，需要在 setup.py 中配置 data_files：

```python
# setuptools 方式（更复杂）
from setuptools import setup
import sys

setup(
    name="my_extension",
    data_files=[
        (
            "etc/jupyter/jupyter_server_config.d",
            ["jupyter-config/jupyter_server_config.d/my_extension.json"],
        ),
    ],
)
```

hatchling 的 shared-data 配置明显更简洁。

## 构建命令

### 安装 build 工具

```bash
pip install build
```

### 构建 wheel 和 sdist

```bash
python -m build
```

执行后在 `dist/` 目录生成两个文件：
- `my_server_extension-0.1.0-py3-none-any.whl`（wheel，二进制分发包）
- `my_server_extension-0.1.0.tar.gz`（sdist，源码分发包）

wheel 文件名格式：`{name}-{version}-{python_tag}-{abi_tag}-{platform_tag}.whl`
- `py3`：纯 Python 3，无 C 扩展
- `none`：无 ABI 依赖
- `any`：跨平台

### 只构建 wheel

```bash
python -m build --wheel
```

### 只构建 sdist

```bash
python -m build --sdist
```

## 本地测试构建产物

```bash
# 从 sdist 安装
pip install dist/my_server_extension-0.1.0.tar.gz

# 从 wheel 安装
pip install dist/my_server_extension-0.1.0-py3-none-any.whl

# 验证安装
jupyter server extension list
# 应显示 my_server_extension OK
```

## 禁止的旧方式

RELEASE.md 中明确说明：

> `python setup.py sdist bdist_wheel` is deprecated and will not work for this package.

不要使用 `python setup.py` 命令，它已被弃用。始终使用 `python -m build`。

## 开发安装

```bash
pip install -e .
```

PEP 660 可编辑安装模式：
- 安装包到环境中，但源码保持在原位置
- 修改源码后立即生效（无需重新安装）
- Jupyter Server 的 `--autoreload` 模式可以自动重新加载修改后的代码

## 验证 pyproject.toml

模板 CI 中包含 pyproject 验证步骤：

```bash
pipx run 'validate-pyproject[all]' pyproject.toml
```

使用 `validate-pyproject` 工具检查 pyproject.toml 格式是否正确。使用 `pipx run` 在隔离环境中运行，不污染项目环境。

## 相关概念

- [配置发现机制](/concepts/06-config-discovery.md)
- [打包发布指南](/concepts/12-packaging-release.md)
- [CI/CD 工作流](/concepts/09-ci-workflows.md)
- [pyproject.toml 字段全解析](/references/pyproject-source.md)
