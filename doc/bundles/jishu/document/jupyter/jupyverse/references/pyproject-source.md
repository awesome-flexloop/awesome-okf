---
type: Reference
title: "pyproject.toml 信源"
description: "jupyverse 项目的构建配置、依赖声明和可选功能组定义。"
tags: [pyproject, build, dependencies, configuration]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: pyproject
    resource: /external/libs/jupyter/jupyverse/pyproject.toml
    title: jupyverse pyproject.toml
---

# pyproject.toml 信源

## 基本信息

| 属性 | 值 |
|------|-----|
| 包名 | jupyverse |
| 版本 | 0.14.15 |
| 描述 | A set of FPS plugins implementing a Jupyter server |
| Python 版本 | >= 3.10 |
| 构建系统 | uv_build >=0.11.32,<0.12 |
| 许可证 | BSD-3-Clause |

## 核心依赖

```
fps[click,fastapi,anycorn] >=0.6.3,<0.7.0
fps-contents >=0.11.4,<0.12.0
fps-file-watcher >=0.2.2,<0.3.0
fps-kernel-subprocess >=0.2.3,<0.3.0
fps-kernels >=0.11.5,<0.12.0
fps-terminals >=0.10.2,<0.11.0
fps-nbconvert >=0.10.2,<0.11.0
fps-lab >=0.11.6,<0.12.0
fps-frontend >=0.10.2,<0.11.0
rich-click >=1.6.1,<2
```

## 可选依赖组（extras）

| 组名 | 包含包 |
|------|--------|
| jupyterlab | fps-jupyterlab |
| notebook | fps-notebook |
| collaboration | jupyter-collaboration-ui, jupyter-docprovider, fps-file-id, fps-yjs, fps-ystore-sqlite, fps-yrooms |
| auth | fps-auth, fps-login |
| auth-fief | fps-auth-fief |
| auth-jupyterhub | fps-auth-jupyterhub |
| noauth | fps-noauth |
| file-watcher-poll | fps-file-watcher-poll |
| kernel-web-worker | fps-kernel-web-worker |
| resource-usage | fps-resource-usage |
| webdav | fps-webdav |
| jupyterlab-git | fps-jupyterlab-git |
| jupyterlab-lsp | fps-jupyterlab-lsp |

## uv workspace 成员

api/* 和 plugins/* 下的所有包都是 workspace 成员，共 16 个 jupyverse-* API 包和 25 个 fps-* 插件包。
