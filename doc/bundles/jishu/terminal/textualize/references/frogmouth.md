---
type: Reference
title: Frogmouth 仓库信源登记
description: Textualize/Frogmouth 仓库信源登记：仓库定位、本地路径、远程 URL、分支、commit 哈希、盘点日期与核心模块清单。
tags: [frogmouth, textualize, source-code, markdown-browser]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
status: stable
stale_after: 2027-03-01
sources: []
---

# Frogmouth 仓库信源登记

Frogmouth 是基于 Textual 的终端 Markdown 浏览器与书签管理器，支持本地与远程文档浏览、书签同步，是 Textual 生态的应用范例。

## 信源信息

| 项目 | 值 |
|---|---|
| 仓库定位 | 终端 Markdown 浏览器与书签管理应用（Textual 应用） |
| 本地路径 | `external/dao/action/Textualize/frogmouth` |
| 远程 URL | `git@github.com:Textualize/frogmouth.git` |
| 分支 | `main` |
| commit hash | `15c3e85a6e84b2e4a6845723acf12beb54c81eb2` |
| 盘点日期 | 2026-09-01 |

## 核心模块清单

核心包 `frogmouth/`：

- `app/`：应用主体（`app.py` 等）
- `screens/`：屏幕子包
- `dialogs/`：对话框子包
- `widgets/`：自定义组件子包
- `data/`：数据层（书签等持久化）
- `utility/`：工具函数
- `__init__.py`、`__main__.py`：包入口与命令行入口

辅助文件：`pyproject.toml`（Poetry 管理）、`Makefile`、`ChangeLog.md`、`README.md`。
