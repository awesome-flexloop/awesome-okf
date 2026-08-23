---
type: category
title: "📖 Jupyter Book v2 / MySTmd 生态"
okf_version: "0.2"
description: "Executable Books 新一代技术文档工具链源码级中文教程——8个知识束、128篇内容文档（70概念+25示例+33信源），覆盖MyST解析引擎、CLI工具链、语法扩展、多格式导出、Notebook执行、交互式代码运行、JupyterLab集成与主题系统"
total_bundles: 8
total_content_docs: 128
total_md_files: 191
verified: grep-verified
generated: true
status: stable
---

# 📖 Jupyter Book v2 / MySTmd 生态

Jupyter Book v2 与 MySTmd 是 Executable Books 组织推出的新一代技术文档工具链，采用 TypeScript 实现统一的 Markdown 解析引擎、多格式导出、Notebook 执行和交互式发布能力。本组知识束收录其核心项目的系统化中文源码教程，覆盖从 Markdown 解析到多格式发布的完整管线。

所有知识束遵循 [OKF v0.2 规范](../../meta/okf-spec/index.md)，通过源码深度阅读（R→I→E→V→C 五阶段链路）生成，所有 API 引用均经 Grep 级源码验证。

## 🏗️ 生态架构管线

```
┌─────────────────────────────────────────────────────────────────┐
│                     📝 Markdown / MyST / Notebook 源文件         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│ 🔍 mystmd 核心引擎                                               │
│   myst-parser (micromark/mdast 插件) → myst-transforms (转换管线)│
│   myst-frontmatter (元数据) → myst-common (类型/工具)            │
│   myst-config (配置) → myst-spec (语法规范)                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │ AST (MDAST)
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│ 🎨 myst-syntax   │ │ ⚡ myst-     │ │ 📤 myst-exporters │
│ 指令/角色/UI扩展  │ │   execute    │ │ HTML/LaTeX/DOCX  │
│ directives/roles │ │ Notebook执行 │ │ JATS/MD/Typst    │
│ ext-button/card  │ │ (构建时)     │ │ jtex 模板引擎    │
│ grid/tabs/proof  │ └──────┬───────┘ └──────────────────┘
│ exercise/reactive│        │
└──────────────────┘        │ 执行输出
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 🌐 myst-cli 命令行工具                                           │
│   build (多格式构建) → start (开发服务器) → init (项目初始化)     │
│   clean → templates → migrate → toc → session cache             │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│ 📚 jupyter-book  │ │ 🎭 myst-theme│ │ 🔮 thebe         │
│ v2 CLI (Python)  │ │ Book/Article │ │ (运行时交互)     │
│ 封装myst-cli     │ │ 主题 + CSS   │ │ Binder/Jupyter   │
│ Node.js 环境管理 │ │ Remix 路由   │ │ Pyodide Lite     │
└──────────────────┘ └──────┬───────┘ │ React Hooks      │
                            │         └──────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 🔬 jupyterlab-myst                                               │
│ JupyterLab 扩展——在Notebook中渲染MyST富内容                       │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 知识束概览

| 层次 | 知识束 | Tier | 内容文档数 |
|------|--------|------|-----------|
| 核心引擎 | [mystmd](mystmd/index.md) | Tier 1 | 26 |
| 工具链 | [myst-cli](myst-cli/index.md) | Tier 1 | 19 |
| 语法层 | [myst-syntax](myst-syntax/index.md) | Tier 2 | 16 |
| 输出层 | [myst-exporters](myst-exporters/index.md) | Tier 2 | 16 |
| 应用层 | [jupyter-book](jupyter-book/index.md) | Tier 2 | 10 |
| 执行层 | [myst-execute](myst-execute/index.md) | Tier 2 | 15 |
| IDE集成 | [jupyterlab-myst](jupyterlab-myst/index.md) | Tier 3 | 13 |
| 表现层 | [myst-theme](myst-theme/index.md) | Tier 2 | 13 |

## 📖 推荐学习路径

```
📖 mystmd          理解MyST解析引擎核心（unified/micromark/mdast插件体系、转换管线）
  → 📖 myst-cli    掌握命令行工具（build/start/init，项目配置与构建流程）
    → 🎨 myst-syntax  学习指令/角色/UI扩展（自定义Markdown语法扩展）
      → 📤 myst-exporters  掌握多格式导出（HTML/PDF/DOCX/JATS/Typst）
        → ⚡ myst-execute  理解Notebook执行与Thebe交互
          → 📚 jupyter-book  使用Jupyter Book v2封装层
            → 🎭 myst-theme  定制主题外观
              → 🔬 jupyterlab-myst  JupyterLab集成
```

## 信源与验证

- **源码根目录**：`external/libs/ai/jupyter-book/`
- **生成方法**：source-code-to-okf-wiki 技能（R→I→E→V→C 五阶段链路）
- **方法论指导**：seven-concepts-cmd（R→I→E 知识沉淀场景）
- **与旧版关系**：现有 [myst/](../myst/index.md) 分组覆盖旧版 Executable Books Python 生态（MyST-Parser/MyST-NB/markdown-it-py 等 Sphinx 扩展），本分组覆盖新一代 TypeScript 实现的 Jupyter Book v2 / MySTmd 引擎

```{toctree}
:hidden:

mystmd/index
myst-cli/index
myst-syntax/index
myst-exporters/index
jupyter-book/index
myst-execute/index
jupyterlab-myst/index
myst-theme/index
```
