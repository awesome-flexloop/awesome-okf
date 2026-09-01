---
type: Reference
title: Rich-CLI 仓库信源登记
description: Textualize/rich-cli 仓库信源登记：仓库定位、本地路径、远程 URL、分支、commit 哈希、盘点日期与核心模块清单。
tags: [rich-cli, textualize, source-code, cli-tool]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
status: stable
stale_after: 2027-03-01
sources: []
---

# Rich-CLI 仓库信源登记

Rich-CLI 是基于 Rich 构建的命令行工具箱，提供 `rich` 命令在终端高亮渲染多种文件类型（Markdown、JSON 等），并支持命令行文本标记与格式化输出。

## 信源信息

| 项目 | 值 |
|---|---|
| 仓库定位 | 终端富输出命令行工具箱（command line toolbox for fancy output，built with Rich） |
| 本地路径 | `external/dao/action/Textualize/rich-cli` |
| 远程 URL | `git@github.com:Textualize/rich-cli.git` |
| 分支 | `main` |
| commit hash | `46f4d2469097be395558768714a5f07ebccf1412` |
| 盘点日期 | 2026-09-01 |

## 核心模块清单

核心包 `src/rich_cli/`：

- `__main__.py`：CLI 主入口（参数解析与渲染调度）
- `markdown.py`：Markdown 渲染扩展
- `pager.py`：分页器集成
- `win_vt.py`：Windows 虚拟终端支持
- `__init__.py`：包入口

辅助目录：`tests/`（测试）、`test_data/`（测试数据）、`imgs/`（截图）；`pyproject.toml`（Poetry 管理）、`CHANGELOG.md`。
