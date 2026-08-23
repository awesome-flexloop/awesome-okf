---
type: reference
title: "myst-cli CLI入口源码"
description: "myst-cli CLI命令注册、选项定义与commander集成源码分析"
tags: [myst-cli, cli, commander, entrypoint]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/index.ts"
    facts: [F-001, F-002]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/build.ts"
    facts: [F-003, F-004]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/start.ts"
    facts: [F-005]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/clean.ts"
    facts: [F-006]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/options.ts"
    facts: [F-007, F-008, F-009]
---

# CLI 入口源码分析

## 模块结构

`cli/` 目录包含4个文件：

| 文件 | 职责 |
|------|------|
| `index.ts` | 模块入口，重新导出所有子模块 |
| `build.ts` | build 命令工厂函数 `makeBuildCommand()` |
| `start.ts` | start 命令工厂函数 `makeStartCommand()` |
| `clean.ts` | clean 命令工厂函数 `makeCleanCommand()` |
| `options.ts` | 选项工厂函数集合 |

## commander 命令定义模式

所有命令采用工厂函数模式创建，返回配置好的 commander `Command` 实例：

```ts
export function makeBuildCommand() {
  const command = new Command('build')
    .description('Build PDF, LaTeX, Word and website exports from MyST files')
    .argument('[files...]', 'list of files to export')
    .addOption(makePdfOption('Build PDF output'))
    .addOption(makeTexOption('Build LaTeX outputs'))
    // ... 更多选项
  return command;
}
```

这种模式允许调用方（通常是 mystmd 的主 bin 入口）灵活组合命令树，而不是在模块加载时立即注册全局命令。

## 选项工厂

`options.ts` 为每种选项类型提供独立的工厂函数，返回 `Option` 实例：

| 工厂函数 | 选项 | 默认值 | 说明 |
|----------|------|--------|------|
| `makePdfOption()` | `--pdf` | false | PDF导出 |
| `makeTexOption()` | `--tex` | false | LaTeX导出 |
| `makeTypstOption()` | `--typst` | false | Typst导出 |
| `makeDocxOption()` | `--word, --docx` | false | Word文档导出 |
| `makeMdOption()` | `--md` | false | Markdown导出 |
| `makeJatsOption()` | `--jats, --xml` | false | JATS XML导出 |
| `makeMecaOptions()` | `--meca` | false | MECA压缩包导出 |
| `makeCffOption()` | `--cff` | false | CFF引用导出 |
| `makeSiteOption()` | `--site` | false | 站点构建 |
| `makeHtmlOption()` | `--html` | false | 静态HTML |
| `makeAllOption()` | `-a, --all` | false | 全部导出 |
| `makeExecuteOption()` | `--execute` | false | 执行Notebook |
| `makeExecuteParallelOption()` | `--execute-parallel <n>` | cpus-1 | 并行执行数 |
| `makeWatchOption()` | `--watch` | false | 监视模式 |
| `makeForceOption()` | `--force` | false | 忽略frontmatter强制导出 |
| `makeStrictOption()` | `--strict` | false | 严格模式（警告即错误） |
| `makeCheckLinksOption()` | `--check-links` | false | 检查外部链接 |
| `makeNamedExportOption()` | `-o, --output <output>` | - | 指定输出文件名 |
| `makePortOption()` | `--port <port>` | PORT env | 应用服务器端口 |
| `makeServerPortOption()` | `--server-port <port>` | SERVER_PORT env | 内容服务器端口 |
| `makeKeepHostOption()` | `--keep-host` | false | 保留HOST环境变量 |
| `makeHeadlessOption()` | `--headless` | false | 无头模式 |
| `makeTemplateOption()` | `--template <path>` | - | 指定模板文件 |
| `makeCIOption()` | `--ci` | false | CI环境标志 |
| `makeMaxSizeWebpOption()` | `--max-size-webp <size>` | 1.5MB | WebP转换阈值 |
| `makeYesOption()` | `-y, --yes` | false | 自动确认 |
| `makeDOIBibOption()` | `--doi-bib` | false | 生成DOI BibTeX文件 |
| `makeTempOption()` | `--temp` | false | 清理临时文件 |
| `makeLogsOption()` | `--logs` | false | 清理日志 |
| `makeCacheOption()` | `--cache` | false | 清理缓存 |
| `makeExportsOption()` | `--exports` | false | 清理导出 |
| `makeTemplatesOption()` | `--templates` | false | 清理模板 |

## 命令汇总

| 命令 | 描述 | 关键选项 |
|------|------|----------|
| `build [files...]` | 构建导出 | --pdf/--tex/--docx/--html/--site/--all/--output/--watch/--execute |
| `start` | 启动开发服务器 | --port/--server-port/--headless/--template/--keep-host/--execute |
| `clean [files...]` | 清理构建产物 | --pdf/--tex/--site/--temp/--cache/--exports/--templates/--all/--yes |
