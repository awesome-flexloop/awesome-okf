---
type: Reference
title: textual-key-recorder 仓库信源登记
description: Textualize/textual-key-recorder 仓库信源登记：仓库定位、本地路径、远程 URL、分支、commit 哈希、盘点日期与核心模块清单。
tags: [textual-key-recorder, textualize, source-code, key-recording-tool]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
status: stable
stale_after: 2027-03-01
sources: []
---

# textual-key-recorder 仓库信源登记

textual-key-recorder 是按键录制工具，记录各按键在 Textual 应用中产生的按键名称，辅助 Textual 按键绑定开发与调试。

## 信源信息

| 项目 | 值 |
|---|---|
| 仓库定位 | Textual 按键名称录制工具（record what keys result in what names） |
| 本地路径 | `external/dao/action/Textualize/textual-key-recorder` |
| 远程 URL | `git@github.com:Textualize/textual-key-recorder.git` |
| 分支 | `main` |
| commit hash | `8c3176ca020b261f041a4d9d7dc927a279cc69c1` |
| 盘点日期 | 2026-09-01 |

## 核心模块清单

核心包 `textual_key_recorder/`：

- `app.py`：录制应用主体（Textual App）
- `screens/`：屏幕子包
- `dialogs/`：对话框子包
- `widgets/`：自定义组件子包
- `__init__.py`、`__main__.py`：包入口与命令行入口

辅助目录：`recordings/`（录制结果存放）；`pyproject.toml`（Poetry 管理）、`Makefile`。
