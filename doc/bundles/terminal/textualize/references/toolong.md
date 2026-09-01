---
type: Reference
title: TooLong 仓库信源登记
description: Textualize/toolong 仓库信源登记：仓库定位、本地路径、远程 URL、分支、commit 哈希、盘点日期与核心模块清单。
tags: [toolong, textualize, source-code, log-viewer]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
status: stable
stale_after: 2027-03-01
sources: []
---

# TooLong 仓库信源登记

TooLong（toolong）是终端日志查看应用，支持查看、tail、合并与搜索日志文件（含 JSONL），构建于 Textual 之上。

## 信源信息

| 项目 | 值 |
|---|---|
| 仓库定位 | 终端日志查看/追踪/合并/搜索应用（view, tail, merge, and search log files） |
| 本地路径 | `external/dao/action/Textualize/toolong` |
| 远程 URL | `git@github.com:Textualize/toolong.git` |
| 分支 | `main` |
| commit hash | `5aa22ee878026f46d4d265905c4e1df4d37842ae` |
| 盘点日期 | 2026-09-01 |

## 核心模块清单

核心包 `src/toolong/`：

- `cli.py`：命令行入口解析
- `ui.py`：Textual 应用界面主体
- `log_file.py`、`log_lines.py`、`log_view.py`、`line_panel.py`：日志文件与视图层
- `watcher.py`、`poll_watcher.py`、`selector_watcher.py`：文件监视（tail）机制
- `format_parser.py`、`timestamps.py`：日志格式与时间戳解析
- `highlighter.py`：日志高亮
- `find_dialog.py`、`goto_screen.py`、`help.py`：对话框与屏幕
- `messages.py`：消息定义
- `scan_progress_bar.py`：扫描进度条
- `__init__.py`、`__main__.py`：包入口

辅助文件：`pyproject.toml`（Poetry 管理）、`README.md`。
