---
type: Reference
title: textual-dev 仓库信源登记
description: Textualize/textual-dev 仓库信源登记：仓库定位、本地路径、远程 URL、分支、commit 哈希、盘点日期与核心模块清单。
tags: [textual-dev, textualize, source-code, dev-tools]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
status: stable
stale_after: 2027-03-01
sources: []
---

# textual-dev 仓库信源登记

textual-dev 是 Textual 的开发者工具包，提供 `textual` 命令行应用（含实时预览、控制台、CSS 热重载等开发辅助能力）。

## 信源信息

| 项目 | 值 |
|---|---|
| 仓库定位 | Textual 开发工具包（Development tools for Textual，提供 `textual` CLI） |
| 本地路径 | `external/dao/action/Textualize/textual-dev` |
| 远程 URL | `git@github.com:Textualize/textual-dev.git` |
| 分支 | `main` |
| commit hash | `e563f96f32d582b7cf22622a401f537c40349adc` |
| 盘点日期 | 2026-09-01 |

## 核心模块清单

核心包 `src/textual_dev/`：

- `cli.py`：`textual` 命令行入口
- `server.py`、`service.py`、`client.py`：开发服务器与客户端通信
- `redirect_output.py`：输出重定向
- `renderables.py`：开发界面渲染对象
- `previews/`：应用预览子包
- `tools/`：开发工具子包
- `__init__.py`、`__main__.py`：包入口

辅助目录：`tests/`（测试）；`pyproject.toml`（Poetry 管理）、`Makefile`。
