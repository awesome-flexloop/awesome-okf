---
type: Reference
title: Trogon 仓库信源登记
description: Textualize/Trogon 仓库信源登记：仓库定位、本地路径、远程 URL、分支、commit 哈希、盘点日期与核心模块清单。
tags: [trogon, textualize, source-code, cli-tui-generator]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
status: stable
stale_after: 2027-03-01
sources: []
---

# Trogon 仓库信源登记

Trogon 为命令行应用自动生成友好的终端用户界面（TUI），通过内省 CLI 参数结构生成 Textual 交互表单，降低 CLI 使用门槛。

## 信源信息

| 项目 | 值 |
|---|---|
| 仓库定位 | 为 CLI 应用自动生成友好终端界面（auto-generate friendly TUIs for command line apps） |
| 本地路径 | `external/dao/action/Textualize/trogon` |
| 远程 URL | `git@github.com:Textualize/trogon.git` |
| 分支 | `main` |
| commit hash | `eaa9e68c403cae6aff0a80957d8876b284fd76b0` |
| 盘点日期 | 2026-09-01 |

## 核心模块清单

核心包 `trogon/`：

- `trogon.py`：Trogon 应用主体（Textual App）
- `typer.py`：Typer/Click 集成入口
- `introspect.py`：CLI 参数结构内省
- `run_command.py`、`detect_run_string.py`：命令执行与探测
- `constants.py`：常量定义
- `widgets/`：自定义组件子包
- `trogon.scss`：界面样式
- `__init__.py`：包入口

辅助目录：`examples/`（示例）、`tests/`（测试）；`pyproject.toml`（Poetry 管理）。
