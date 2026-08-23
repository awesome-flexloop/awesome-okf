---
type: concept
title: "Clean 命令"
description: "myst clean命令的清理策略、构建目录管理与选择性清理机制"
tags: [myst-cli, clean, build-artifacts, cleanup]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/build/clean.ts"
    facts: [F-058, F-059, F-060]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/clean.ts"
    facts: [F-006]
---

# Clean 命令

`myst clean` 命令用于清理构建产物、临时文件、缓存和已安装的模板。支持选择性清理和一键全清理。

## 清理目标

| 目标 | CLI 选项 | 路径 | 默认清理 |
|------|----------|------|----------|
| PDF 导出 | `--pdf` | _build/exports/*.pdf | ✅ |
| LaTeX 导出 | `--tex` | _build/exports/*.tex | ✅ |
| Typst 导出 | `--typst` | _build/exports/*.typ | ✅ |
| DOCX 导出 | `--docx` | _build/exports/*.docx | ✅ |
| MD 导出 | `--md` | _build/exports/*.md | ✅ |
| JATS 导出 | `--jats/--xml` | _build/exports/*.xml | ✅ |
| MECA 导出 | `--meca` | _build/exports/*.meca | ✅ |
| CFF 导出 | `--cff` | _build/exports/*.cff | ✅ |
| 站点内容 | `--site` | _build/site/ | ✅ |
| 静态 HTML | `--html` | _build/html/ | ✅ |
| 临时文件 | `--temp` | _build/temp/ | ✅ |
| CLI 日志 | `--logs` | _build/logs/ | ✅ |
| 导出目录 | `--exports` | _build/exports/ | ✅ |
| Notebook执行缓存 | `--execute` | _build/execute/ | ✅ |
| Web请求缓存 | `--cache` | _build/cache/ | ❌（需 --cache 或 --all） |
| 模板缓存 | `--templates` | _build/templates/ | ❌（需 --templates 或 --all） |

> 默认清理（无参数时）排除 cache 和 templates，因为下载模板和填充缓存的成本较高。

## 清理选项集

```ts
// 全部清理（--all）
const ALL_OPTS = {
  docx: true, pdf: true, tex: true, xml: true, md: true, meca: true,
  site: true, html: true, temp: true, logs: true, cache: true,
  exports: true, execute: true, templates: true,
};

// 默认清理（无参数）
const DEFAULT_OPTS = {
  // 同 ALL_OPTS 但 cache: false, templates: false
};
```

## 清理流程

```
clean(session, files, opts)
  ├─ coerceOpts() 确定清理范围
  ├─ collectAllBuildExportOptions() 收集导出文件路径
  ├─ 收集要删除的路径
  │   ├─ exports 模式：收集各格式导出输出路径
  │   │   └─ pdftex 额外清理 tex 源文件和日志目录
  │   ├─ 构建目录：收集 _build 下的子目录
  │   └─ site 模式：添加 session.sitePath()
  ├─ deduplicatePaths() 去重（移除被子路径包含的父路径）
  ├─ 打印待删除路径列表
  ├─ 用户确认（--yes 跳过）
  ├─ 执行删除（fs.rmSync recursive）
  └─ 删除空的 _build 目录
```

## 路径去重

`deduplicatePaths()` 函数确保不会重复删除：如果 `_build/exports` 已在删除列表中，就不需要再单独列出 `_build/exports/file.pdf`。通过 `isSubpath()` 判断一个路径是否是另一个的子路径。

```ts
function isSubpath(item: string, folder: string): boolean {
  // item === folder → false（不是子路径）
  // item 的前 N 个 part 与 folder 完全匹配 → true
}
```

## 导出文件的精确清理

当指定文件参数时（如 `myst clean my-file.md`），clean 命令：
1. 通过 `collectAllBuildExportOptions()` 确定该文件的所有导出输出路径
2. 仅删除这些特定的输出文件，而非整个 exports 目录
3. PDF 导出额外清理关联的 LaTeX 中间目录

## 用户交互

默认情况下，clean 命令会列出所有待删除路径并要求用户确认：
- `-y` / `--yes`：跳过确认直接删除
- 无 `-y`：使用 inquirer 显示确认提示

## 相关概念

- [Build 管线](01-build-pipeline.md) — 构建产物的生成
- [会话与缓存](08-session-cache.md) — 缓存机制
