---
type: Reference
title: textual-serve 仓库信源登记
description: Textualize/textual-serve 仓库信源登记：仓库定位、本地路径、远程 URL、分支、commit 哈希、盘点日期与核心模块清单。
tags: [textual-serve, textualize, source-code, web-serving]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
status: stable
stale_after: 2027-03-01
sources: []
---

# textual-serve 仓库信源登记

textual-serve 让任意 Textual 应用成为 Web 应用——只需约 3 行代码即可将 Textual 应用运行在浏览器中，提供应用服务化与下载管理能力。

## 信源信息

| 项目 | 值 |
|---|---|
| 仓库定位 | Textual 应用 Web 服务化（every Textual application is now a web application） |
| 本地路径 | `external/dao/action/Textualize/textual-serve` |
| 远程 URL | `git@github.com:Textualize/textual-serve.git` |
| 分支 | `main` |
| commit hash | `fa5cf5f5b4273c97ed286a55747106701ddc9917` |
| 盘点日期 | 2026-09-01 |

## 核心模块清单

核心包 `src/textual_serve/`：

- `server.py`：Web 服务器主体
- `app_service.py`：应用服务管理
- `download_manager.py`：下载管理
- `_binary_encode.py`：二进制编码工具
- `static/`：静态资源子目录
- `templates/`：页面模板子目录
- `__init__.py`：包入口

辅助目录：`examples/`（示例）；`pyproject.toml`、`requirements.lock` / `requirements-dev.lock`（uv 管理）。
