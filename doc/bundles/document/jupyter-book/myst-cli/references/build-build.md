---
type: reference
title: "myst-cli Build管线源码"
description: "build/build.ts 中的多格式导出管线、格式解析、站点构建与导出收集逻辑"
tags: [myst-cli, build, pipeline, export, formats]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/build/build.ts"
    facts: [F-010, F-011, F-012, F-013, F-014, F-015]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/build/index.ts"
    facts: [F-016]
---

# Build 管线源码分析

## 核心类型

```ts
type FormatBuildOpts = {
  site?: boolean; docx?: boolean; pdf?: boolean; tex?: boolean;
  typst?: boolean; xml?: boolean; md?: boolean; meca?: boolean;
  cff?: boolean; html?: boolean; all?: boolean; force?: boolean; output?: string;
};

export type BuildOpts = FormatBuildOpts & CollectionOptions & RunExportOptions & StartOptions;
```

## 格式解析逻辑

### getRequestedExportFormats()

仅返回用户显式通过 CLI 标志请求的格式：

```ts
export function getRequestedExportFormats(opts: FormatBuildOpts) {
  const formats = [];
  if (docx) formats.push(ExportFormats.docx);
  if (pdf) formats.push(ExportFormats.pdf);
  // ...
  return formats;
}
```

### getAllowedExportFormats()

更智能的格式决策，处理三种场景：
1. **显式格式**：用户指定了 --pdf/--docx 等标志
2. **--all 模式**：启用全部格式
3. **显式文件但无格式**（`myst build file.md`）：也启用全部格式

```ts
const any = hasAnyExplicitExportFormat(opts);
const override = all || (!any && explicit);
// override 为 true 时，所有格式都被启用
if (docx || override) formats.push(ExportFormats.docx);
if (pdf || override) formats.push(ExportFormats.pdf, ExportFormats.pdftex, ExportFormats.typst);
// ...
```

特别注意：`--pdf` 会触发 pdf + pdftex + typst 三种格式（因为 PDF 有 LaTeX 和 Typst 两个后端路径）。

### exportSite()

判断是否需要执行站点构建：

```ts
export function exportSite(session: ISession, opts: FormatBuildOpts) {
  const { force, site, html, all } = opts;
  const siteConfig = selectors.selectCurrentSiteConfig(session.store.getState());
  return site || html || all || (siteConfig && !force && !hasAnyExplicitExportFormat(opts));
}
```

当存在站点配置且用户没有指定特定单文件导出格式时，默认也执行站点构建。

## collectAllBuildExportOptions() 收集流程

这是 build 管线中最复杂的函数，负责收集所有导出任务：

1. **路径解析**：将文件参数转换为绝对路径
2. **参数校验**：`-o` 输出选项要求恰好一个文件和一个格式
3. **项目加载**：通过 `findCurrentProjectAndLoad()` 和 `loadProjectFromDisk()` 加载项目配置
4. **三种模式处理**：
   - **命名输出模式**（-o）：解析输出扩展名确定格式，单文件单格式导出
   - **显式文件模式**：对每个文件收集导出选项，如果 frontmatter 无 exports 定义则强制使用请求的格式
   - **项目模式**（无文件参数）：遍历所有项目路径，收集所有页面的导出选项

返回值为 `ExportWithInputOutput[]`，每个元素包含格式、输入文件、输出路径和项目路径。

## build() 主函数执行流程

```
1. collectAllBuildExportOptions() → 收集所有导出任务
2. 构建 buildLog 记录输入和导出列表
3. 如果有导出任务:
   a. 打印导出列表日志
   b. localArticleExport() → 执行单文件导出
4. 如果需要站点构建:
   a. 检查站点配置是否存在
   b. --html 模式: buildHtml()
   c. 默认模式: buildSite()
5. writeJsonLogs() → 写入 myst.build.json
6. session.dispose() → 清理资源
```

## 构建输出目录

| 目录 | 用途 | 清理选项 |
|------|------|----------|
| `_build/site/` | 站点构建内容 | `--site` |
| `_build/exports/` | 导出文件（PDF/DOCX等） | `--exports` |
| `_build/temp/` | 中间构建产物 | `--temp` |
| `_build/cache/` | 缓存文件 | `--cache` |
| `_build/logs/` | CLI 日志 | `--logs` |
| `_build/templates/` | 下载的模板 | `--templates` |
| `_build/html/` | 静态 HTML | `--html` |
| `_build/execute/` | Notebook 执行缓存 | `--execute` |

## build/index.ts 导出

build 模块重新导出以下子模块：
- build（主构建函数和选项类型）
- clean（清理逻辑）
- docx（Word 导出）
- pdf（PDF 导出）
- site（站点构建）
- tex（LaTeX 导出）
- types（类型定义）
- utils（工具函数）
- html（HTML 导出）
- meca（MECA 导出）
- jats（JATS XML 导出）
- typst（Typst 导出）
- legacy（遗留兼容）
