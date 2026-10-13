---
type: Example
title: "REA：CLI 与 MCP 使用示例"
description: "从 npx rea-agents setup 初始化到 rea analyze <path> 单次分析，再到接入 agent 客户端的 MCP 配置要点——CLI/MCP 双入口可照做流程（证据 F-010/011/013/014/056）"
tags: [rea, example, cli, mcp, setup, analyze, agent-integration]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T10:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: rea-tools-doc
    resource: "https://rea.tools/zh-CN/"
---

# 示例：CLI 与 MCP 使用示例

> 命令接口来自固定源码与官方文档核对，未在本机运行 REA。路径与地址须替换为授权目标的实际值；执行前检查当前版本帮助和 Provider 状态。

## 目标

在一台满足 Node 版本要求的机器上完成 REA 初始化，先用 CLI 单次分析验证工具链，再接入 agent 客户端走 MCP。

## 输入

- 一台满足 Node 支持范围的机器（`^22.19.0 || ^24.11.0 || >=26.0.0`，F-007），npm 存量 `npm@11.16.0`（F-008）。
- 目标分析文件（目录 / `.asar` / native 二进制等）。
- 若做 native/Android/EVM 等域分析，需已装相应分析工具（Ghidra/IDA/Hopper/JADX 等），见 [provider-setup.md](provider-setup.md)。

## 步骤

### 1. 初始化 setup

```bash
npx rea-agents@latest setup
```

先审阅配置计划并确认写入，再重启客户端。`npx` 执行不等于全局安装；以下 `rea` 调用要求命令已在 PATH，否则使用 `npx -y rea-agents@latest <command>`。bin 注册两个名称不证明当前 shell 能找到它们。

### 2. 冒烟：CLI 单次分析

```bash
rea analyze "D:/analysis/notes-example" --json
```

对目录 / `.asar` 文件，在未给 `--provider`、`--snapshot` 或原生格式/架构/入口覆盖时，通用入口可自动走静态 JavaScript 应用图工作流。F-016 的 `analyze→binary_overview` 是原生分析别名，不代表上述 JavaScript 路由。

核对返回结果的目标身份、范围与未解析项，不以进程退出成功代替证据检查。路径须替换为真实目录。

### 3. 验证工具链就绪（doctor 类）

```bash
rea doctor
```

以及 `rea capabilities`、`rea providers`（F-014）可查看能力与 Provider 就绪状态。

**预期**：可确认各 Provider（Ghidra/JADX 等）是否就绪，比直接走 MCP 更好排障（对应 insights「洞察三」行动）。

### 4. 其他代表性单次命令

```bash
rea inspect "D:/analysis/target.exe" --json
rea decompile "D:/analysis/target.exe" 0x406400 --json
rea function "D:/analysis/target.exe" 0x406400 --json
rea search "D:/analysis/target.exe" "Export" --kind strings --mode literal --json
rea trace "D:/analysis/target.exe" "Export" --json
rea xrefs "D:/analysis/target.exe" 0x406400 --json
```

这些是独立调用，不是必须串行执行的脚本；地址只展示选择器形态，须换成当前目标已确认地址并配置合适 Provider。`compare-bundles`、`evidence-export`、`capture-process` 在此仅作为命令名称列举，完整请求见对应官方文档；尤其进程捕获会启动选定命令。

> 注意：CLI 顶层命令共 129 个（F-013），命令与 MCP 工具名并非 1:1（F-016）；存在约 50+ 个「仅有 MCP、无专用 CLI」的工具（F-017）。

### 5. 进入 MCP 服务模式

```bash
rea --mcp        # 或 rea mcp（单参进入 MCP 服务模式，加载 dist/mcp/main.js）
rea mcp doctor   # 单独走 dist/mcpDoctor.js（F-011）
```

### 6. 接入 agent 客户端（MCP 配置要点）

- 包的 MCP 服务标识（mcpName）为 `io.github.morluto/rea`（F-004），不强制作为客户端的本地配置键。
- 各 agent 客户端通常以「运行 `rea --mcp`（stdio）」方式暴露给 agent；把该命令配置为 MCP server 即可。
- 在 agent 端应**直接使用 MCP 工具名全集**（如 `binary_overview`、`procedure_pseudo_code`、`binary_session`），而非依赖 CLI 命令名（F-016/F-017）。
- 完整工具定义及输入/输出 schema 读取 `tools/list`（含当前不可用工具）；`binary_session` 提供活动服务身份、Provider 绑定和分组工具可用性，不返回完整 schema 目录（F-029）。

## 输出 / 验收

- [ ] setup 计划已确认，客户端已重启，实际执行入口可识别（F-010/F-137）
- [ ] `rea analyze <path>` 返回结构化结果（F-056）
- [ ] `rea doctor` 报告各 Provider 就绪状态（F-014）
- [ ] `rea --mcp` 进入 MCP 服务模式（F-011）
- [ ] agent 客户端可 `tools/list`；`io.github.morluto/rea` 是包的服务标识，不强制作为客户端本地配置键（F-004/F-029）

## 反模式提醒

- 不要在 agent 端依赖 CLI 命令名——存在大量「仅有 MCP、无专用 CLI」工具，且命令↔工具并非 1:1（F-016/F-017）。
- 不要把 `rea analyze` 的返回当作本地事实文件的长期形态：结果以 evidence/unknowns 结构化，后期应通过 `evidence-export`/`binary_session` 交互（F-014/F-029）。

## 阅读下一步

- [分析工具安装与 Provider 接入](provider-setup.md)——按目标域检查依赖；静态 JS 调查不要求先安装 Ghidra/JADX
- [安装、setup 与 CLI/MCP 双入口](../concepts/05-cli-and-setup.md)——双入口概念说明
