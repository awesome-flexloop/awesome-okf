---
type: Reference
title: "noxfile.py 源码解析"
description: "Jupyter Surveys文档构建自动化脚本的源码级解析：nox session定义、uv后端配置、mystmd构建与live preview命令。"
tags: ["nox", "mystmd", "构建自动化", "uv", "python"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/noxfile.py"
    lines: "1-27"
    description: "Nox自动化脚本"
---

# noxfile.py 源码解析

## 概述

[noxfile.py](../../../../../../external/libs/jupyter/surveys/noxfile.py) 是Jupyter Surveys仓库的文档构建自动化脚本，使用Nox（Python任务运行器）定义了两个session：`docs`（构建文档）和`docs-live`（实时预览）。

## 源码核心

### 导入与全局配置

```python
import nox

nox.options.sessions = ["docs"]
nox.options.default_venv_backend = "uv|virtualenv"
```

- **默认session**设为`docs`，即直接运行`nox`时默认构建文档
- **venv后端**优先使用`uv`（快速Python包管理器），回退到`virtualenv`

### docs session：构建文档站点

```python
@nox.session
def docs(session):
    session.install("-r", "docs/requirements.txt")
    session.run("myst", "init", "--ci")
    session.run("myst", "build", "--ci", "docs", "_build/html")
```

三个步骤：
1. **安装依赖**：从`docs/requirements.txt`安装文档构建依赖（包含mystmd等）
2. **初始化MyST**：`myst init --ci`在CI模式下初始化MyST项目配置
3. **构建站点**：`myst build --ci docs _build/html`将docs/目录构建为HTML到`_build/html/`

### docs-live session：实时预览

```python
@nox.session
def docs_live(session):
    session.install("-r", "docs/requirements.txt")
    session.run("myst", "init", "--ci")
    session.run(
        "myst",
        "start",
        "--ci",
        "--server",
        "--headless",
        "docs",
    )
```

- 启动MyST开发服务器（`myst start`），支持热重载
- `--server --headless`参数以headless模式启动服务器（适合CI/容器环境）

## 关键设计决策

| 决策 | 原因 |
|------|------|
| 使用uv作为首选venv后端 | uv比virtualenv快10-100倍，改善开发者体验 |
| --ci标志 | 确保在CI环境中非交互式运行，避免等待用户输入 |
| 两个分离的session | 构建（静态HTML）与预览（开发服务器）职责分离 |
| 不使用Makefile | Nox跨平台一致，Python生态标准工具 |

## 相关概念

- [MyST文档系统](../concepts/04-myst-docs-system.md)：mystmd CLI工具详解
- [本地构建文档](../examples/01-build-docs-locally.md)：使用nox构建文档的实战步骤
- [CI/CD部署](../concepts/07-cicd-deployment.md)：GitHub Actions如何调用nox
