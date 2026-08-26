---
type: bundle
title: sphinx-design
description: sphinx-design 中文 Wiki 教程——为 Sphinx 文档添加美观响应式 Web 组件的扩展
okf_version: '0.2'
tags:
- sphinx
- extension
- design
- web-components
- bootstrap
- responsive
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- "https://github.com/executablebooks/sphinx-design"
- "https://sphinx-design.readthedocs.io/"
---

# sphinx-design

> 为 Sphinx 文档添加美观、响应式 Web 组件的扩展——卡片、网格、标签页、折叠、徽章、按钮、图标，零前端依赖。

## 📦 项目概览

| 属性 | 值 |
|---|---|
| Python 包名 | `sphinx_design` |
| Sphinx 扩展名 | `"sphinx_design"` |
| 版本 | 动态获取（pyproject.toml） |
| Python 要求 | >= 3.11 |
| 运行时依赖 | `sphinx>=7.2,<10`（仅此一个） |
| 许可证 | MIT |
| 作者 | Chris Sewell (Executable Books) |
| 仓库 | [executablebooks/sphinx-design](https://github.com/executablebooks/sphinx-design) |
| 文档 | [sphinx-design.readthedocs.io](https://sphinx-design.readthedocs.io/) |

## 🗺️ 推荐学习路径

```
00 简介 → 01 快速上手 → 02 扩展架构
                         ↓
          03 设计系统(CSS类名)
            ↓           ↓
     04 网格布局    05 卡片组件
            ↓           ↓
     06 折叠与标签页  ←─┘
            ↓
     07 徽章与按钮
            ↓
     08 图标与文章信息
            ↓
     09 配置与自定义指令
```

**快速入门路径**（30分钟上手）：[00 简介](concepts/00-introduction.md) → [01 快速上手](concepts/01-getting-started.md) → [04 网格布局](concepts/04-grids.md) → [05 卡片组件](concepts/05-cards.md) → [示例集](examples/grid-layouts.md)

**深入理解路径**（理解架构）：[02 扩展架构](concepts/02-extension-architecture.md) → [03 设计系统](concepts/03-design-system.md) → [06 折叠与标签页](concepts/06-dropdown-tabs.md) → [09 配置与自定义指令](concepts/09-configuration.md)

## 🧩 组件清单

| 组件类别 | 指令/角色 | 说明 |
|---|---|---|
| **布局** | `grid` / `grid-item` / `grid-item-card` / `div` | 12列响应式网格、通用容器 |
| **内容** | `card` / `card-carousel` | 卡片、横向滚动卡片轮播 |
| **交互** | `dropdown` | 原生HTML5折叠容器（零JS） |
| **交互** | `tab-set` / `tab-item` / `tab-set-code` | CSS标签页+JS同步持久化 |
| **行内** | `:bdg[-link/-ref][-color][-line]:` | 徽章（纯色/轮廓/链接/引用） |
| **行内** | `button-link` / `button-ref` | 按钮（外链/内引，支持富文本） |
| **图标** | `:octicon:` / `:fas:/:fab:/:far:` / `:material-*:` | Octicon/FontAwesome/Material图标 |
| **信息** | `article-info` | 文章元信息栏（头像/作者/日期/阅读时间） |

## 💡 核心洞察

1. **Bootstrap 移植，零运行时依赖**：sphinx-design 将 Bootstrap 设计系统完整移植为 Sphinx 扩展，CSS 使用 `sd-` 前缀命名空间避免冲突，核心仅依赖 sphinx 本身。

2. **两阶段渲染架构**：交互组件在解析时生成语义化 AST（非 HTML 友好），Post-Transform 阶段特化为 HTML 结构（`<details>/<summary>`、radio+label），确保 LaTeX 等非 HTML 输出有降级渲染。

3. **Marker-Class Stash/Graft 模式**：通过两个 PostTransform + marker class 的 AOP 方式，在不修改 Sphinx resolver 的前提下解决了交叉引用富文本丢失问题（issue #228）。

4. **配置式自定义指令**：`sd_custom_directives` 允许在 conf.py 中声明式创建新指令（继承内置指令+预设参数/选项），无需写 Python 代码。

## 📚 文档导航

### 概念文档

| 序号 | 主题 |
|---|---|
| 00 | [sphinx-design 简介](concepts/00-introduction.md) |
| 01 | [快速上手](concepts/01-getting-started.md) |
| 02 | [扩展架构与两阶段渲染](concepts/02-extension-architecture.md) |
| 03 | [设计系统与CSS类名体系](concepts/03-design-system.md) |
| 04 | [网格布局系统](concepts/04-grids.md) |
| 05 | [卡片组件](concepts/05-cards.md) |
| 06 | [折叠与标签页](concepts/06-dropdown-tabs.md) |
| 07 | [徽章与按钮](concepts/07-badges-buttons.md) |
| 08 | [图标系统与文章信息栏](concepts/08-icons-article-info.md) |
| 09 | [配置与自定义指令](concepts/09-configuration.md) |

### 示例文档

| 主题 |
|---|
| [网格布局示例集](examples/grid-layouts.md) |
| [卡片与交互组件示例](examples/cards-and-components.md) |

### 参考文档

| 主题 |
|---|
| [源码参考与配置速查](references/source-reference.md) |

## ⚡ 快速示例

```rst
.. grid:: 2
   :gutter: 3

   .. grid-item-card:: 🚀 快速开始
      :link: getting-started
      :link-type: ref
      :shadow: md

      几分钟内上手，零配置使用。

   .. grid-item-card:: 📖 API 参考
      :link: api-reference
      :link-type: ref
      :shadow: md

      完整的指令和配置参考。
```

## 🔗 相关知识包

- [sphinx-copybutton](https://github.com/executablebooks/sphinx-copybutton) — 一键复制代码块按钮扩展
- [sphinx-external-toc](https://github.com/executablebooks/sphinx-external-toc) — 外部 `_toc.yml` 站点导航扩展
- [myst 系列](https://github.com/executablebooks/MyST-Parser) — MyST Markdown 生态与 Executable Books 工具链

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
