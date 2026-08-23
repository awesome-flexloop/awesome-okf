---
okf_version: "0.2"
type: group
title: "📖 MyST Markdown 与 Executable Books 生态"
description: "Executable Books 组织开源项目源码级中文教程——19个知识束、225篇内容文档（151概念+43示例+31信源）、360个.md文件，覆盖 MyST Markdown 解析器、Sphinx 集成、Jupyter Notebook 支持、主题设计、UI 组件扩展与基础设施工具"
total_bundles: 19
total_content_docs: 225
total_md_files: 360
verified: grep-verified
generated: true
status: stable
---

# 📖 MyST Markdown 与 Executable Books 生态

[Executable Books](https://executablebooks.org) 是 [Jupyter Book](https://jupyterbook.org) 和 [MyST Markdown](https://mystmd.org) 等现代技术文档工具链的核心开源组织，致力于构建"可执行的书籍"——将 Markdown 文本、Jupyter Notebook 代码执行、交互式组件融为一体的下一代出版平台。本组知识束收录其 19 个核心项目的系统化中文源码教程，覆盖从 Markdown 解析到 Sphinx 扩展、从 Notebook 执行缓存到主题设计的完整技术栈。

所有知识束遵循 [OKF v0.2 规范](../../meta/okf-spec/index.md)，通过源码深度阅读（R→I→E→V→C 五阶段链路）生成，所有 API 引用均经 Grep 级源码验证。

## 📊 知识束概览

| 层次 | 知识束 | 概念 | 示例 | 信源 | 内容文档 |
|------|--------|------|------|------|---------|
| **解析核心** | [markdown-it-py](markdown-it-py/index.md) | 18 | 3 | 2 | 23 |
| **解析核心** | [mdurl](mdurl/index.md) | 4 | 1 | 1 | 6 |
| **解析核心** | [mdit-py-plugins](mdit-py-plugins/index.md) | 10 | 3 | 1 | 14 |
| **Sphinx集成** | [MyST-Parser](MyST-Parser/index.md) | 16 | 5 | 2 | 23 |
| **Sphinx集成** | [MyST-NB](MyST-NB/index.md) | 13 | 5 | 2 | 20 |
| **格式化工具** | [mdformat-myst](mdformat-myst/index.md) | 5 | 1 | 3 | 9 |
| **格式化工具** | [mdformat-footnote](mdformat-footnote/index.md) | 4 | 1 | 3 | 8 |
| **格式化工具** | [rst-to-myst](rst-to-myst/index.md) | 11 | 2 | 5 | 18 |
| **Sphinx扩展** | [sphinx-book-theme](sphinx-book-theme/index.md) | 10 | 2 | 1 | 13 |
| **Sphinx扩展** | [sphinx-design](sphinx-design/index.md) | 10 | 2 | 1 | 13 |
| **Sphinx扩展** | [sphinx-copybutton](sphinx-copybutton/index.md) | 5 | 2 | 1 | 8 |
| **Sphinx扩展** | [sphinx-togglebutton](sphinx-togglebutton/index.md) | 4 | 2 | 1 | 7 |
| **Sphinx扩展** | [sphinx-tabs](sphinx-tabs/index.md) | 6 | 3 | 1 | 10 |
| **Sphinx扩展** | [sphinx-exercise](sphinx-exercise/index.md) | 6 | 3 | 1 | 10 |
| **Sphinx扩展** | [sphinx-proof](sphinx-proof/index.md) | 6 | 2 | 1 | 9 |
| **Sphinx扩展** | [sphinx-external-toc](sphinx-external-toc/index.md) | 5 | 1 | 1 | 7 |
| **基础设施** | [jupyter-cache](jupyter-cache/index.md) | 8 | 3 | 2 | 13 |
| **基础设施** | [github-activity](github-activity/index.md) | 5 | 1 | 1 | 7 |
| **基础设施** | [web-compile](web-compile/index.md) | 5 | 1 | 1 | 7 |
| **合计** | **19 知识束** | **151** | **43** | **31** | **225** |

> 注："内容文档"指 concepts/examples/references 目录下的实质性文档（不含各目录 index.md 导航页）。含导航索引、日志文件、spec 元数据共 **360 个 .md 文件**。

## MyST 解析核心层

| 知识束 | 简介 |
|--------|------|
| [markdown-it-py](markdown-it-py/index.md) | Python 版 markdown-it 解析器——CommonMark 合规的 Markdown 解析引擎，4 种解析预设（zero/commonmark/default/js-default）、Ruler 链式规则管理、Token 流架构、Core/Block/Inline 三链协作、插件系统 |
| [mdurl](mdurl/index.md) | Markdown URL 工具库——URL 编解码（percent-encoding）、格式化、解析四大 API、UTF-16 Surrogates 处理、缓存优化 |
| [mdit-py-plugins](mdit-py-plugins/index.md) | markdown-it-py 插件集合——22 个内置插件（GFM/脚注/容器/任务列表/数学公式等）、三链协作注册模式、闭包工厂模式、env 数据通道 |

## MyST Sphinx 集成层

| 知识束 | 简介 |
|--------|------|
| [MyST-Parser](MyST-Parser/index.md) | MyST Markdown 的 Sphinx 解析器——docutils+Sphinx 桥接、Markdown→docutils AST 转换、12+ 扩展语法开关（dollarmath/amsmath/deflist/colon_fence等）、配置系统、CLI 工具 |
| [MyST-NB](MyST-NB/index.md) | MyST 对 Jupyter Notebook 的支持——Notebook 解析与执行、MIME 输出渲染（text/html/image/png/latex等）、Glue 跨单元格引用、ANSI 语法高亮、执行缓存集成 |

## 格式化与迁移工具层

| 知识束 | 简介 |
|--------|------|
| [mdformat-myst](mdformat-myst/index.md) | mdformat MyST 语法插件——角色/指令/块中断/目标/数学公式渲染、指令选项 YAML 自动格式化、双层转义机制 |
| [mdformat-footnote](mdformat-footnote/index.md) | mdformat 脚注插件——脚注四分类算法（body_referenced/nested_only/fence_only/orphans）、依赖图构建、ID 重分配 |
| [rst-to-myst](rst-to-myst/index.md) | RST→MyST 转换器——三阶段转换流水线（RST→docutils AST→markdown-it tokens→MyST）、Visitor 模式、Mock Sphinx 应用、扩展需求自动推断 |

## Sphinx 扩展套件层

### 主题与导航

| 知识束 | 简介 |
|--------|------|
| [sphinx-book-theme](sphinx-book-theme/index.md) | Jupyter Book 主题——基于 PyData Sphinx Theme 的薄继承层、头部按钮系统、Margin 边注指令、全屏/TOC 隐藏/Thebe 交互、SCSS 样式体系 |
| [sphinx-external-toc](sphinx-external-toc/index.md) | 外部目录扩展——`_toc.yml` 驱动站点导航、Sphinx toctree 桥接、多文档结构映射 |

### UI 组件

| 知识束 | 简介 |
|--------|------|
| [sphinx-design](sphinx-design/index.md) | 设计组件扩展——卡片(cards)/网格(grids)/标签页(tabs)/下拉(dropdowns)/徽章(badges)/按钮(buttons)等 UI 组件、CSS 类名系统 |
| [sphinx-copybutton](sphinx-copybutton/index.md) | 代码块复制按钮——一键复制代码块内容、JS/CSS 静态资源注入、配置选项 |
| [sphinx-togglebutton](sphinx-togglebutton/index.md) | 内容折叠按钮——collapsible 可折叠区域、点击展开/收起、提示文本定制 |
| [sphinx-tabs](sphinx-tabs/index.md) | 标签页组件——多标签页切换、分组同步、代码示例多语言展示 |

### 学术内容

| 知识束 | 简介 |
|--------|------|
| [sphinx-exercise](sphinx-exercise/index.md) | 练习环境——exercise/solution 指令、答案隐藏显示、编号管理 |
| [sphinx-proof](sphinx-proof/index.md) | 数学证明环境——theorem/proof/lemma/corollary/definition 等定理类指令、自定义节点类型 |

## 基础设施工具层

| 知识束 | 简介 |
|--------|------|
| [jupyter-cache](jupyter-cache/index.md) | Notebook 执行缓存——MyST-NB 的执行后端依赖、SQLite 数据库缓存层、Notebook 读取/执行/缓存命中、多项目隔离、CLI 管理工具 |
| [github-activity](github-activity/index.md) | GitHub 活动 Changelog 生成器——CLI 工具、GitHub API 调用、按标签/PR/Issue 生成 Markdown 变更日志 |
| [web-compile](web-compile/index.md) | Web 资源编译器——SCSS→CSS 编译、JS 压缩、主题开发构建工具 |

## 推荐学习路径

### 路径一：Markdown 解析基础（理解 MyST 底层）
```
📝 mdurl（URL处理工具）
  → 🔤 markdown-it-py（CommonMark解析引擎）
    → 🔌 mdit-py-plugins（插件系统实践）
      → 📄 MyST-Parser（Sphinx中的Markdown）
```

### 路径二：Jupyter Book 实战（构建可执行书籍）
```
📄 MyST-Parser（MyST语法）
  → 📓 MyST-NB（Notebook支持）
    → 💾 jupyter-cache（执行缓存）
      → 🎨 sphinx-book-theme（书籍主题）
        → 🧩 sphinx-design（UI组件）
```

### 路径三：Sphinx 扩展开发（从易到难）
```
📋 sphinx-copybutton（最简单：JS注入）
  → 🔘 sphinx-togglebutton（折叠交互）
    → 📑 sphinx-tabs（标签页组件）
      → 🎴 sphinx-design（综合设计系统）
```

## 生态架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Jupyter Book（书籍出版平台）                        │
│                     sphinx-book-theme + _toc.yml                     │
├─────────────────────────────────────────────────────────────────────┤
│  Sphinx 扩展套件                                                     │
│  ┌────────────┬─────────────┬─────────────┬──────────────────────┐ │
│  │ sphinx-    │ sphinx-     │ sphinx-     │ sphinx-exercise/    │ │
│  │ design     │ copybutton  │ tabs        │ proof/togglebutton  │ │
│  │ (UI组件)   │ (复制按钮)   │ (标签页)     │ (学术/折叠)          │ │
│  └────────────┴─────────────┴─────────────┴──────────────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│  MyST Sphinx 集成层                                                  │
│  ┌─────────────────────────┐  ┌──────────────────────────────────┐ │
│  │    MyST-Parser          │  │         MyST-NB                  │ │
│  │  Markdown→docutils AST  │  │ Notebook解析·执行·渲染·Glue引用   │ │
│  └──────────┬──────────────┘  └──────────┬───────────────────────┘ │
├─────────────┼────────────────────────────┼─────────────────────────┤
│  解析核心   │ mdformat-myst              │ jupyter-cache            │
│             │ mdformat-footnote          │ (Notebook执行缓存)        │
│  ┌──────────▼────────────────────────────▼──────────────────────┐  │
│  │              markdown-it-py (CommonMark 解析引擎)              │  │
│  │  Core链 / Block链 / Inline链 / Ruler规则管理 / Token流架构     │  │
│  │        mdit-py-plugins (22个插件)   mdurl (URL工具)            │  │
│  └───────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│  工具链：rst-to-myst（迁移）· github-activity（Changelog）· web-compile │
└─────────────────────────────────────────────────────────────────────┘
```

## 与其他分组的关系

- 依赖 [📄 Sphinx 文档工程生态](../sphinx/index.md)：MyST-Parser/MyST-NB 及各 Sphinx 扩展均基于 Sphinx 扩展 API 开发
- 互补 [📓 Jupyter 数据科学生态](../jupyter/index.md)：MyST-NB 与 Jupyter Notebook/nbformat 紧密集成
- 格式化工具与 [🔧 通用开发工具](../../build/tooling/index.md) 中的 Copier/PyInvoke 类似，属于开发辅助工具

## 信源与验证

- **源码根目录**：`external/libs/ai/executablebooks/`
- **生成方法**：source-code-to-okf-wiki 技能（R→I→E→V→C 五阶段链路）
- **方法论指导**：seven-concepts-cmd（R→I→E 知识沉淀场景）
- **API 验证**：核心项目 34 个关键 API 经 Grep 级源码验证通过
- **链接验证**：1379 个内部链接 0 断链
- **frontmatter**：360 个文件 YAML 元数据完整合规

```{toctree}
:hidden:

markdown-it-py/index
mdurl/index
mdit-py-plugins/index
MyST-Parser/index
MyST-NB/index
mdformat-myst/index
mdformat-footnote/index
rst-to-myst/index
sphinx-book-theme/index
sphinx-design/index
sphinx-copybutton/index
sphinx-togglebutton/index
sphinx-tabs/index
sphinx-exercise/index
sphinx-proof/index
sphinx-external-toc/index
jupyter-cache/index
github-activity/index
web-compile/index
```
