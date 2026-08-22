---
type: concept
title: "CLI 架构"
description: "myst-cli 基于 commander 的命令注册机制、选项工厂模式与命令树结构"
tags: [myst-cli, cli, commander, architecture]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/index.ts"
    facts: [F-001, F-002]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/build.ts"
    facts: [F-003, F-004]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/options.ts"
    facts: [F-007, F-008, F-009]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/index.ts"
    facts: [F-064]
---

# CLI 架构

myst-cli 使用 [commander](https://github.com/tj/commander.js) 库构建命令行界面，采用**工厂函数模式**注册命令和选项，而非在模块加载时直接创建全局命令实例。

## 命令树结构

myst-cli 的顶层命令由主包（mystmd）的 bin 入口组装，但核心命令工厂在 myst-cli 中定义：

```
myst (主命令)
├── build [files...]    # 构建导出
├── start               # 启动开发服务器
├── clean [files...]    # 清理构建产物
└── init                # 初始化项目（在 myst-cli/src/init/ 中）
```

## 工厂函数模式

每个子命令通过独立的工厂函数创建，返回配置好的 `Command` 实例：

```ts
// cli/build.ts
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

这种模式的好处是：
- **可测试**：工厂函数可在测试中独立调用，不依赖全局状态
- **可组合**：主入口可以灵活决定挂载哪些命令
- **无副作用**：import 模块不会自动注册命令

## 选项工厂

`options.ts` 提供了一套选项工厂函数，统一管理所有 CLI 选项的创建：

```ts
export function makePdfOption(description: string) {
  return new Option('--pdf', description).default(false);
}

export function makeExecuteParallelOption() {
  const defaultParallelism = Math.max(1, cpus().length - 1);
  return new Option('--execute-parallel <n>', '...')
    .argParser((value) => { /* 解析和验证 */ })
    .default(defaultParallelism);
}
```

### 选项分类

| 类别 | 选项 | 说明 |
|------|------|------|
| 格式导出 | `--pdf`, `--tex`, `--typst`, `--docx`, `--md`, `--jats`, `--meca`, `--cff`, `--site`, `--html` | 控制构建哪些格式 |
| 执行控制 | `--execute`, `--execute-parallel <n>` | Notebook 执行控制 |
| 输出控制 | `-o, --output <file>`, `--all`, `--force`, `--watch` | 输出文件和构建模式 |
| 质量控制 | `--strict`, `--check-links`, `--ci` | 严格模式、链接检查、CI标志 |
| 服务器 | `--port`, `--server-port`, `--keep-host`, `--headless`, `--template` | start 服务器选项 |
| 清理 | `--temp`, `--logs`, `--cache`, `--exports`, `--templates`, `-y, --yes` | clean 命令选项 |
| 资源 | `--max-size-webp <size>`, `--doi-bib` | 图片和引用资源控制 |

## 模块导出

`cli/index.ts` 重新导出四个子模块：

```ts
export * from './build.js';
export * from './clean.js';
export * from './options.js';
export * from './start.js';
```

myst-cli 主入口 `src/index.ts` 导出全部公共 API，包括 CLI、build、config、init、process、project、session、store、transforms、utils 等模块。

## 相关概念

- [Build 管线](01-build-pipeline.md) — build 命令的执行流程
- [Start 开发服务器](02-start-dev-server.md) — start 命令的服务器架构
- [Clean 命令](04-clean-command.md) — clean 命令的清理策略
