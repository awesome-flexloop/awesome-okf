---
type: reference
title: "myst-cli 构建编排与导入转换器"
description: "myst-cli build 层的多格式导出编排（localArticleExport）、jats-to-myst/tex-to-myst 导入转换器源码"
tags: [myst-exporters, reference, build, import, jats-to-myst]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-cli/src/build/utils/localArticleExport.ts"
    facts: [F-039]
  - path: "myst-cli/src/build/build.ts"
    facts: [F-038]
  - path: "jats-to-myst/src/index.ts"
    facts: [F-032, F-033, F-034]
  - path: "tex-to-myst/src/index.ts"
    facts: [F-035]
---

# myst-cli 构建编排与导入转换器

本文档登记两部分源码：(1) myst-cli build 层如何编排各格式导出器完成项目级多格式构建；(2) 导入转换器（jats-to-myst、tex-to-myst）的入口和结构。

## 构建编排源码

### build.ts

- **路径**：`myst-cli/src/build/build.ts`
- 核心函数 `build(session, files, opts)`：
  1. 确定是否执行 site 构建（`exportSite()` 判断）
  2. 收集导出配置（`collectAllBuildExportOptions()`）
  3. 执行 `localArticleExport()` 进行单文件多格式导出
  4. 执行 site 构建（`buildSite()` 或 `buildHtml()`）
  5. 写入构建日志（`myst.build.json`）
- `getAllowedExportFormats(opts)`: 根据 CLI flag 解析导出格式列表
  - `--pdf` 触发 pdf + pdftex + typst 三种格式
  - `--tex` 触发 tex + pdftex
  - `--all` 触发所有格式

### localArticleExport.ts

- **路径**：`myst-cli/src/build/utils/localArticleExport.ts`
- `localArticleExport(session, exportOptionsList, opts)`: 主导出函数，MECA 最后执行
- `_localArticleExport()`: 按 format 字段分发到具体 run 函数：

| format | 导出函数 | 输出 |
|--------|---------|------|
| `tex` | `runTexExport` / `runTexZipExport` | .tex / .zip |
| `typst` | `runTypstExport` / `runTypstZipExport` / `runTypstPdfExport` | .typ / .zip / .pdf |
| `docx` | `runWordExport` | .docx |
| `xml` | `runJatsExport` | .xml (JATS) |
| `md` | `runMdExport` | .md |
| `meca` | `runMecaExport` | .meca (打包) |
| `cff` | `runCffExport` | CITATION.cff |
| `pdf`/`pdftex` | 先 `runTexExport` → `createPdfGivenTexExport` | .pdf (latexmk) |

- 支持 watch 模式：chokidar 监听文件变化自动重新导出
- 每个导出创建 sessionClone 隔离状态

## 导入转换器

### jats-to-myst

- **路径**：`jats-to-myst/src/index.ts`
- **包结构**：src/ 下有 index.ts、types.ts；tests/ 有 basic.spec.ts

**导出 API**：

| 符号 | 类型 | 说明 |
|------|------|------|
| `JatsParser` | Class | JATS XML→MDAST 解析器（栈式构建） |
| `jatsToMystPlugin` | Plugin | unified 插件 |
| `jatsToMystTransform` | Function | **高层入口**，接收 XML 字符串或 Jats 对象，返回 `{ tree, jats, file, references }` |
| `DEFAULT_HANDLERS` | Object | 默认 JATS 元素→MyST 节点映射 |

**JatsParser 核心方法**（与 JatsSerializer 对称）：
- `openNode(name, attributes?, isLeaf?)`: 压入新节点
- `closeNode()`: 弹出节点并添加到父级
- `pushNode(el?)`: 将节点添加到栈顶的 children
- `text(text?)`: 添加/合并文本节点
- `renderChildren(node)`: 遍历子节点查表分发
- `renderInline(node, name, attributes?)`: 便捷方法：openNode→渲染子节点→closeNode
- `addLeaf(name, attributes?)`: 便捷方法：openNode(isLeaf=true)→closeNode

**JATS→MyST 映射要点**：
- JATS `ref-type` → MyST `kind`：sec→heading, fig→figure, dispFormula→equation, table→table, bibr→cite
- fig-group → tabSet/tabItem（多图转为标签页）
- fig → container + image + caption（对 eLife/JOSS/PLOS/PMC 有特殊 URL 处理）
- xref 根据 ref-type 分发为 cite 或 crossReference
- 自动提取 referenceData（参考文献 HTML 片段和 DOI）

### tex-to-myst

- **路径**：`tex-to-myst/src/index.ts`
- **导出**：类型 + `TexParser` 类 + `DEFAULT_HANDLERS`
- **成熟度**：低于 jats-to-myst（LaTeX 解析复杂度更高），核心逻辑在 `./parser.js`

## 相关概念

- [00-exporter-architecture](../concepts/00-exporter-architecture.md)：统一导出接口架构
- [09-import-converters](../concepts/09-import-converters.md)：导入转换器详解
- [03-latex-import](../examples/03-latex-import.md)：LaTeX 导入示例
