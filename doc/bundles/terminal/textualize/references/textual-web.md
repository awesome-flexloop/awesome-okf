---
type: Reference
title: textual-web 仓库信源登记
description: Textualize/textual-web 仓库信源登记：仓库定位、本地路径、远程 URL、分支、commit 哈希、盘点日期与核心模块清单。
tags: [textual-web, textualize, source-code, web-publishing]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
status: stable
stale_after: 2027-03-01
sources: []
---

# textual-web 仓库信源登记

textual-web 将 Textual 应用与终端发布到 Web 上，提供会话管理、网关客户端与本地/远程运行能力（目前处于 beta 阶段）。

## 信源信息

| 项目 | 值 |
|---|---|
| 仓库定位 | 将 Textual 应用与终端发布到 Web（publishes Textual apps and terminals on the web） |
| 本地路径 | `external/dao/action/Textualize/textual-web` |
| 远程 URL | `git@github.com:Textualize/textual-web.git` |
| 分支 | `main` |
| commit hash | `7d6741c9f7869881722d7d8dcf70a286cc270db9` |
| 盘点日期 | 2026-09-01 |

## 核心模块清单

核心包 `src/textual_web/`：

- `cli.py`：命令行入口
- `web.py`：Web 服务主体
- `config.py`、`constants.py`、`types.py`：配置与类型定义
- `session.py`、`session_manager.py`、`app_session.py`、`terminal_session.py`：会话管理
- `environment.py`：运行环境管理
- `ganglion_client.py`：网关（ganglion）客户端
- `packets.py`、`poller.py`、`exit_poller.py`、`retry.py`：通信与轮询
- `identity.py`、`slugify.py`：身份与标识
- `apps/`：内置应用子包
- `__init__.py`、`_two_way_dict.py`：包入口与工具

辅助目录：`examples/`（示例）；`pyproject.toml`（Poetry 管理）、`CHANGELOG.md`。
