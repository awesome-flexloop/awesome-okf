---
type: concept
title: "模板系统"
description: "myst-cli的模板管理机制：站点模板、文档导出模板、模板下载安装与myst-templates包集成"
tags: [myst-cli, templates, myst-templates, theming, site-template]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/build/site/start.ts"
    facts: [F-062]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/options.ts"
    facts: [F-152]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/session/types.ts"
    facts: [F-029]
---

# 模板系统

myst-cli 使用模板系统来控制站点外观和文档导出格式。模板分为**站点模板**（控制网站主题和布局）和**导出模板**（控制 PDF/DOCX 等格式的排版）。

## 模板存储位置

模板下载后缓存到构建目录：

```
_build/
└── templates/        # 已下载的模板缓存
```

可通过 `myst clean --templates` 清理模板缓存（不包含在默认清理中）。

## 站点模板

### 默认模板

init 命令生成的默认站点配置使用 `book-theme` 模板：

```yaml
site:
  template: book-theme
```

### 模板选项

站点模板支持通过 `site.options` 配置：

```yaml
site:
  template: book-theme
  options:
    favicon: favicon.ico
    logo: site_logo.png
```

### 命令行覆盖

`myst start --template <path-to-template>` 可以临时指定模板文件，覆盖 myst.yml 中的配置。这在开发自定义模板时很有用。

### 模板安装

在站点启动或构建时，通过 `installSiteTemplate()` 和 `getSiteTemplate()` 函数：
1. 检查本地模板缓存
2. 如果不存在，从远程下载模板
3. 缓存到 `_build/templates/` 目录
4. 返回 MystTemplate 实例供渲染使用

Session 中通过 `$siteTemplate` 属性缓存当前站点模板实例。

## 导出模板

各导出格式（PDF、LaTeX、DOCX、Typst 等）使用专门的模板控制排版：

| 格式 | 模板用途 |
|------|----------|
| PDF (LaTeX) | LaTeX 文档类、导言区、页面布局 |
| PDF (Typst) | Typst 模板文件、排版规则 |
| DOCX | Word 模板（.docx 参考文档） |
| JATS | JATS XML 结构模板 |
| MD | Markdown 输出格式控制 |

导出模板通过 myst-templates 包管理，支持：
- 模板列表查询
- 模板下载和缓存
- 模板渲染（填充 frontmatter 和内容）
- 模板版本管理

## MystTemplate 类型

Session 缓存中的 `$siteTemplate` 类型为 `MystTemplate`（来自 myst-templates 包），提供：
- 模板渲染接口
- 模板选项验证
- 静态资源路径解析

## 模板与开发服务器

`myst start` 命令中模板的生命周期：

```
startServer()
  ├─ getSiteTemplate() 获取/下载模板
  ├─ installSiteTemplate() 安装到构建目录
  ├─ 模板渲染页面内容
  └─ watchContent() 中模板文件变化触发重建
```

## 相关概念

- [Start 开发服务器](02-start-dev-server.md) — 开发服务器中模板的使用
- [Build 管线](01-build-pipeline.md) — 导出格式的模板应用
- [Clean 命令](04-clean-command.md) — 模板缓存清理
