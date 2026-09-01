---
type: Reference
title: textual-demo 仓库信源登记
description: Textualize/textual-demo 仓库信源登记：仓库定位、本地路径、远程 URL、分支、commit 哈希、盘点日期与核心模块清单。
tags: [textual-demo, textualize, source-code, demo-app]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
status: stable
stale_after: 2027-03-01
sources: []
---

# textual-demo 仓库信源登记

textual-demo 是 Textual 的演示与教学应用，展示 Textual 构建终端应用的能力（如主题支持等），可作为学习范例运行。

## 信源信息

| 项目 | 值 |
|---|---|
| 仓库定位 | Textual 演示与教学应用（demonstration and teaching aid for building terminal apps） |
| 本地路径 | `external/dao/action/Textualize/textual-demo` |
| 远程 URL | `git@github.com:Textualize/textual-demo.git` |
| 分支 | `main` |
| commit hash | `babcbd1b742ba893e834fafb6f82930ae18cad65` |
| 盘点日期 | 2026-09-01 |

## 核心模块清单

核心包 `src/textual_demo/`：

- `run.py`：演示应用运行入口
- `__about__.py`：版本元数据
- `__init__.py`：包入口

辅助文件：`pyproject.toml`、`uv.lock`（uv 管理）、`.python-version`、`README.md`。
