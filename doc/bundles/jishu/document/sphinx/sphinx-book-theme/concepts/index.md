# 概念文档（Concepts）

按"先定位、再结构、后机制、最后定制"的顺序排列。

## 入门

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | 定位、核心特性、与 pydata-sphinx-theme / Jupyter Book 的关系、维护状态与版本 |
| [01-getting-started.md](01-getting-started.md) | 安装、最小 `conf.py`、目录结构、首次构建与常见报错 |

## 结构与配置

| 文档 | 说明 |
|------|------|
| [02-theme-architecture.md](02-theme-architecture.md) | sphinx-theme-builder 构建链、模板继承、Python 入口、SCSS/JS 资产管线 |
| [03-layout-and-navigation.md](03-layout-and-navigation.md) | 页面分区模型、primary/secondary sidebar、navbar、footer、announcement |
| [04-theme-options.md](04-theme-options.md) | `theme.conf` 选项全表、`html_theme_options` 覆盖规则与类型陷阱 |

## 核心机制

| 文档 | 说明 |
|------|------|
| [05-header-buttons.md](05-header-buttons.md) | 下载/全屏/源码/仓库/启动按钮的数据结构与 URL 拼装 |
| [06-sidenotes-margin.md](06-sidenotes-margin.md) | 脚注转边注的 post-transform、`SideNoteNode`、`{margin}` 指令与 CSS 类 |
| [07-jupyter-interactivity.md](07-jupyter-interactivity.md) | MyST-NB 集成、Notebook 单元格标签、Thebe 与在线启动链路 |

## 定制与开发

| 文档 | 说明 |
|------|------|
| [08-customization-and-development.md](08-customization-and-development.md) | 自定义 CSS、模板覆盖、子主题、翻译、测试与发布流程 |

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-theme-architecture
03-layout-and-navigation
04-theme-options
05-header-buttons
06-sidenotes-margin
07-jupyter-interactivity
08-customization-and-development
```
