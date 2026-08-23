---
type: concept
title: "Build 管线"
description: "myst-cli build命令的多格式导出管线架构，从选项解析、导出收集到格式分发的完整流程"
tags: [myst-cli, build, pipeline, export, formats]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/build/build.ts"
    facts: [F-010, F-011, F-012, F-013, F-014, F-015]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/build.ts"
    facts: [F-003, F-004]
---

# Build 管线

build 命令是 myst-cli 最核心的功能，负责将 MyST Markdown 文件构建为多种输出格式。管线采用**收集→执行**两阶段架构。

## 支持的导出格式

| 格式 | CLI 选项 | ExportFormats 枚举 | 输出说明 |
|------|----------|-------------------|----------|
| PDF | `--pdf` | `pdf`, `pdftex`, `typst` | 通过 LaTeX 或 Typst 生成 |
| LaTeX | `--tex` | `tex`, `pdftex` | .tex 源文件 |
| Typst | `--typst` | `typst` | .typ 文件和 PDF |
| Word | `--word, --docx` | `docx` | .docx 文件 |
| Markdown | `--md` | `md` | 简化的 MyST→MD |
| JATS XML | `--jats, --xml` | `xml` | 学术出版 XML |
| MECA | `--meca` | `meca` | 期刊投稿压缩包 |
| CFF | `--cff` | `cff` | Citation File Format |
| 站点 | `--site` | - | 交互式网站（_build/site/） |
| 静态HTML | `--html` | - | 静态 HTML（_build/html/） |

> 注意：`--pdf` 会同时触发 pdf、pdftex、typst 三种格式，因为 PDF 可以通过 LaTeX 和 Typst 两个后端生成。

## 管线执行流程

```
┌─────────────────────────────────────────────────┐
│           build(session, files, opts)            │
├─────────────────────────────────────────────────┤
│ 1. collectAllBuildExportOptions()               │
│    ├─ 解析文件参数为绝对路径                      │
│    ├─ 参数校验（-o 需单文件单格式）               │
│    ├─ findCurrentProjectAndLoad() 加载项目       │
│    ├─ 三种模式处理：                             │
│    │   ├─ -o 模式：单文件命名输出                │
│    │   ├─ 显式文件：逐文件收集导出               │
│    │   └─ 项目模式：遍历所有项目页面             │
│    └─ 返回 ExportWithInputOutput[]              │
│                                                  │
│ 2. localArticleExport() 执行单文件导出           │
│    └─ 按格式分发到各导出器                       │
│                                                  │
│ 3. 站点构建（可选）                              │
│    ├─ --html → buildHtml()                      │
│    └─ 默认 → buildSite()                        │
│                                                  │
│ 4. writeJsonLogs() 写入 myst.build.json          │
│ 5. session.dispose() 清理资源                    │
└─────────────────────────────────────────────────┘
```

## 格式决策逻辑

`getAllowedExportFormats()` 实现了智能的格式选择：

```ts
// 场景1: myst build --pdf
// → 仅导出 pdf/pdftex/typst

// 场景2: myst build --all
// → 导出所有格式 (docx + pdf + tex + typst + xml + md + meca + cff)

// 场景3: myst build my-file.md
// → explicit=true, any=false, override=true → 所有格式
// （用户给了文件但没说格式，默认全导出）

// 场景4: myst build my-file.md --pdf
// → 仅导出 pdf 格式

// 场景5: myst build (无参数，有站点配置)
// → exportSite()=true → 执行站点构建 + 项目frontmatter中声明的导出
```

`--force` 标志的作用：忽略 frontmatter 中的 exports 声明，强制构建命令行指定的格式。

## 构建输出目录结构

```
_build/
├── site/           # 站点输出（--site）
│   ├── content/    # JSON 内容
│   └── public/     # 静态资源
├── html/           # 静态 HTML 输出（--html）
├── exports/        # 单文件导出（PDF/DOCX/TEX等）
├── temp/           # 中间产物（LaTeX 编译中间文件等）
├── cache/          # 缓存（HTTP 响应、DOI 数据等）
├── templates/      # 下载的模板
├── logs/           # 构建日志
├── execute/        # Notebook 执行缓存
└── myst.build.json # 构建日志元数据
```

## 站点构建条件

`exportSite()` 函数决定是否触发站点构建：

- 显式指定 `--site`、`--html` 或 `--all` → 总是构建
- 无参数 + 存在站点配置 + 无 `--force` + 无显式格式 → 自动构建站点
- `--watch` 模式在 build 中仅提示使用 `myst start`，不支持 build 中的watch

## 相关概念

- [CLI 架构](00-cli-architecture.md) — 命令和选项定义
- [项目加载与TOC](05-project-load-toc.md) — 项目发现和页面收集
- [会话与缓存](08-session-cache.md) — Session 和缓存机制
