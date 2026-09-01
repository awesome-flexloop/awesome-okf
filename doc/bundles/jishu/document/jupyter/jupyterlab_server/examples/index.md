---
okf_version: "0.2"
type: index
title: "代码示例"
description: "jupyterlab_server 实战代码示例索引"
---

# 代码示例

本目录提供 jupyterlab_server 的实战代码示例，涵盖基础启动、REST API调用、Python API编程使用等场景。

## 示例清单

| 序号 | 示例 | 内容 | 难度 |
|------|------|------|------|
| 00 | [基础使用](00-basic-usage.md) | 命令行启动、自定义Lab应用、配置文件、测试fixtures | ⭐ |
| 01 | [设置系统API](01-settings-api.md) | REST API CRUD、Python API、Schema验证、overrides覆盖 | ⭐⭐ |
| 02 | [工作区与国际化](02-workspaces-i18n.md) | 工作区CRUD、slugify、CLI、翻译Bundle、Schema翻译 | ⭐⭐ |

## 如何运行示例

示例中的curl命令需要先启动jupyterlab_server：

```bash
pip install jupyterlab_server
python -m jupyterlab_server --ServerApp.token="" --ServerApp.password=""
```

Python代码示例可以直接在Python解释器或Jupyter Notebook中运行。

```{toctree}
:hidden:
:maxdepth: 7

00-basic-usage
01-settings-api
02-workspaces-i18n
```
