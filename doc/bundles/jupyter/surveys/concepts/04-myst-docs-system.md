---
type: concept
title: "MyST文档系统"
description: "MyST Markdown文档引擎的核心概念：mystmd CLI、myst.yml配置、listing指令自动发现、book-theme主题、与Jupyter Notebook集成。"
tags: ["myst", "mystmd", "文档构建", "markdown", "静态站点", "book-theme"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/docs/myst.yml"
    lines: "1-25"
    description: "MyST站点配置"
  - resource: "../../../../../../external/libs/jupyter/surveys/noxfile.py"
    lines: "1-27"
    description: "Nox构建脚本"
---

# MyST文档系统

Jupyter Surveys使用**MyST Markdown**（Markedly Structured Text）作为文档引擎。MyST是专为科学计算和技术文档设计的Markdown扩展，支持Jupyter Notebook集成、交叉引用、学术引用等高级功能。

## 什么是MyST？

MyST是CommonMark Markdown的超集，新增了：
- **指令（Directives）**：可扩展的块级元素（如代码块、图表、列表）
- **角色（Roles）**：内联语义标记（如引用、数学、变量）
- **交叉引用**：自动编号和链接到图表、章节、公式
- **Jupyter集成**：直接嵌入可执行的代码单元格

Jupyter Surveys使用的MyST实现是**mystmd**（MyST Markdown CLI工具），一个Node.js编写的命令行工具，支持将MyST文档构建为静态HTML站点。

## mystmd CLI核心命令

| 命令 | 用途 |
|------|------|
| `myst init` | 初始化MyST项目（创建myst.yml等配置） |
| `myst build` | 构建静态HTML站点 |
| `myst start` | 启动开发服务器（热重载预览） |
| `myst clean` | 清理构建产物 |

### 构建流程

```bash
# 初始化（CI模式，非交互）
myst init --ci

# 构建：source目录 → 输出目录
myst build --ci docs _build/html
```

- `--ci`标志：非交互式运行，适合自动化环境
- `docs`：源文件目录
- `_build/html`：HTML输出目录

## myst.yml 配置详解

[myst.yml](../references/myst-config-source.md) 是MyST项目的核心配置文件：

### 项目元数据（project段）

```yaml
project:
  title: Jupyter Surveys        # 站点标题
  github: https://github.com/jupyter/surveys  # GitHub仓库链接
  license:
    code: CC0-1.0               # 代码许可证
    content: CC0-1.0            # 内容许可证
  plugins:
    - jupyterlab-myst           # 启用JupyterLab MyST插件
```

**jupyterlab-myst插件**：支持在Markdown中嵌入交互式Jupyter单元格，文档中的代码块可以直接执行。

### 目录树（TOC）

```yaml
site:
  toc:
    - file: index.md
    - title: Survey Datasets
      children:
        - pattern: "surveys/*/index.md"      # 一级glob
        - pattern: "surveys/*/*/index.md"    # 二级glob
```

**glob模式的力量**：使用`pattern`而非显式文件列表，意味着：
- 新增数据集目录后**无需修改配置**，自动出现在导航中
- 支持嵌套层级（`*/*/`匹配二级子目录）
- 文件按文件系统顺序排列

### 主题配置

```yaml
  template: book-theme          # 使用书籍主题
  options:
    show_footer: false          # 隐藏页脚
    logo: surveys/logo.png      # Logo路径
    logo_text: Jupyter Surveys  # Logo文字
```

**book-theme**：MyST的内置主题，提供：
- 左侧可折叠目录导航
- 顶部导航栏
- 响应式布局（移动端适配）
- 深色/浅色模式切换
- 搜索功能

## Listing指令：自动文件列表

MyST的`listing`指令是Jupyter Surveys文档自动化的关键：

````markdown
:::{listing}
:glob: surveys/*/index.md
:::
````

这个指令会在构建时自动展开为匹配glob模式的文件列表，生成带链接的卡片式目录。这比手动维护链接列表更可靠——新增文件自动出现，删除文件不会产生断链。

## 文档源文件组织

```
docs/
├── myst.yml              # 站点配置
├── index.md              # 首页
└── surveys/              # 数据集文档（通过glob引用surveys/根目录）
    └── logo.png          # Logo图片
```

注意：`docs/`目录只包含站点配置和首页，数据集文档直接在`surveys/`数据目录中（与数据文件共存）。MyST通过TOC的glob模式跨目录引用这些文件。

## 构建产物

运行`myst build`后，`_build/html/`目录包含：

```
_build/html/
├── index.html            # 首页
├── surveys/
│   ├── index.html        # 数据集列表页
│   └── 2015-12-notebook-ux/
│       └── index.html    # 各数据集页面
├── _static/              # 静态资源（CSS/JS/图片）
└── mermaid/              # Mermaid图表（如有）
```

## 本地开发 vs CI构建

| 环境 | 命令 | 特点 |
|------|------|------|
| 本地开发 | `nox -s docs-live` | 热重载，浏览器自动刷新 |
| 本地构建 | `nox -s docs` | 生成静态HTML，验证构建无错 |
| CI构建 | `nox -s docs` + `BASE_URL` | 子路径部署，非交互模式 |

## 相关内容

- [本地构建文档](../examples/01-build-docs-locally.md)：完整构建教程
- [noxfile.py解析](../references/noxfile-source.md)：构建脚本详解
- [myst.yml配置解析](../references/myst-config-source.md)：配置文件全字段说明
- [CI/CD部署](07-cicd-deployment.md)：GitHub Actions自动化构建
