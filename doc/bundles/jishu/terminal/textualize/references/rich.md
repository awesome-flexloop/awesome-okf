---
type: Reference
title: Rich 仓库信源登记
description: Textualize/Rich 仓库信源登记：仓库定位、本地路径、远程 URL、分支、commit 哈希、盘点日期与核心模块清单。
tags: [rich, textualize, source-code, terminal-rendering]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
status: stable
stale_after: 2027-03-01
sources: []
---

# Rich 仓库信源登记

Rich 是 Python 富文本与终端美化渲染库，提供 Console、Markup、Table、Panel、Progress、Syntax 等终端富媒体渲染能力，是 Textualize 生态的渲染基石。

## 信源信息

| 项目 | 值 |
|---|---|
| 仓库定位 | Python 终端富文本渲染库（rich text and beautiful formatting for the terminal） |
| 本地路径 | `external/dao/action/Textualize/rich` |
| 远程 URL | `git@github.com:Textualize/rich.git` |
| 分支 | `main` |
| commit hash | `9d8f9a372cc5916fd4781fec207ced7ddac2f08f` |
| 盘点日期 | 2026-09-01 |

## 核心模块清单

核心包 `rich/`（约 70 个模块）关键文件：

- `console.py`：Console 渲染入口
- `text.py`、`style.py`、`styled.py`：文本与样式系统
- `table.py`、`panel.py`、`columns.py`、`rule.py`、`padding.py`、`align.py`、`constrain.py`：结构化渲染组件
- `progress.py`、`progress_bar.py`、`spinner.py`、`status.py`、`live.py`、`live_render.py`：进度与动态渲染
- `markdown.py`、`syntax.py`、`highlighter.py`、`json.py`、`pretty.py`：内容格式化渲染
- `tree.py`、`layout.py`、`box.py`、`bar.py`：树形与布局渲染
- `segment.py`、`measure.py`、`region.py`、`control.py`、`cells.py`、`_ratio.py`：底层渲染原语
- `color.py`、`color_triplet.py`、`palette.py`、`_palettes.py`、`default_styles.py`、`theme.py`、`themes.py`、`terminal_theme.py`：颜色与主题
- `logging.py`、`traceback.py`、`prompt.py`、`emoji.py`、`markup.py`、`filesize.py`、`repr.py`、`inspect`（`_inspect.py`）：集成与工具

辅助目录：`tests/`（pytest 测试）、`docs/`（Sphinx 文档源）、`examples/`（示例脚本）、`benchmarks/`（ASV 基准测试）、`tools/`（辅助脚本）、`.faq/`。
