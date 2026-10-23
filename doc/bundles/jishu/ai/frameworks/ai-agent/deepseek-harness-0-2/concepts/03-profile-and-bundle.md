---
type: concept
title: "Profile 与组合包——配置树的四层叠加"
description: "dsh 的两种 manifest（bundle 与 profile）、四层 patch 叠加顺序与整行替换语义、dsh-base 的组成，以及 --dump-config 的调试价值。"
tags: [deepseek-harness, profile, bundle, cordis, patch, configuration]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 apps/cli/reference/README.zh.md 与 packages/boot/app-boot
---

# Profile 与组合包：配置树的四层叠加

## 1. 两种 manifest，别搞混

| | 组合包（bundle） | Profile |
|---|---|---|
| 是什么 | npm 包 | `$DSH_HOME/profiles/<name>` 目录 |
| 回答什么问题 | "我**贡献什么**" | "我**由哪些 bundle 按什么顺序**组成" |
| 声明字段 | `package.json` 的 `dsh.bundle`（指向 patch 文件，或有序文件列表） | `package.json` 的 `dsh.profile`（列出 `bundles` 数组） |

```json
// 组合包
{ "name": "my-bundle", "dsh": { "bundle": { "patch": "./cordis.patch.yml" } } }

// Profile
{ "name": "demo", "dsh": { "profile": { "bundles": ["@deepseek-ai/dsh-base", "my-bundle"] } } }
```

## 2. 四层叠加（后应用者胜）

从**空根条目列表**起：

```text
① profile manifest 的 dsh.profile.bundles 各组合包 patch（按数组顺序）
② profile 自身的 $DSH_HOME/profiles/<name>/cordis.patch.yml
③ home 级 $DSH_HOME/cordis.patch.yml（机器共享偏好，优先级高于 profile 层）
④ 每个 --patch <path> overlay（按 argv 顺序）
```

**关键语义：patch 替换目标行的整个 `config`，不做深度合并。** 覆盖某个插件时，必须把想保留的键**全部重述**一遍——这是最容易踩的坑。

patch 也能 `insert` 新行。**行序无语义**：激活由服务可用性驱动。

`preset` patch 在目标声明的 `config.plugins` 内应用同样的操作，沿用相同层优先级。

## 3. dsh-base：共享的第一层

`dsh-base` 是 `web` / `headless` / `sdk` / `acp` profile 的共享核心（`packages/bundle/base/cordis.patch.yml`，96 行插件条目）。它大致包含：

| 域 | 条目 |
|---|---|
| 基础 | `timer`、`hmr`（`root: []`，仅监视配置）、`storage` + `storage-json` + `storage-domain` |
| 模型 | `llm`、`llm-deepseek`（`dsh-llm-deepseek-api-key`）、`llm-pi-ai` |
| 运行时 | `session`、`session-persistence-jsonl`、`session-query-sqlite`、`agent`、`agent-loop`、`tools`、`system-prompt`、`working-directory` |
| 能力 | `tool-fs` / `tool-bash` / `tool-pwsh`（按 `process.platform` 互斥门控）、`web` + `tool-web`、`lsp`、`skill` + `skill-filesystem` |
| 安全 | `sandbox` + `sandbox-policy` + `bash-sandbox`/`pwsh-sandbox`、`approval`、`permission-presets` |
| 协作 | `subagent` + `tool-subagent`、`plan-mode`、`compaction-basic`、`token-meter`、`goal`、`commands`、`otel` + `session-telemetry-otel` |

`dsh-sdk-minimal` 是刻意的例外：它拥有完整的显式 SDK 配置树，**不应用 `dsh-base`**。

> base 不是给用户直接 import 的库，而是组合包层。

## 4. 组合包解析顺序

组合包名称**先从 dsh 安装目录解析，再从 profile 目录解析**：

- 内置组合包（`@deepseek-ai/dsh-base`、`dsh-web-app`、`dsh-headless`、`dsh-sdk-app`、`dsh-sdk-minimal`、`dsh-acp-app`）始终来自当前运行的 dsh 所属安装
- 树外组合包来自 profile 中由 pnpm 管理的 `node_modules`

挂载配置行前，launcher 会遍历安装与所选 bundle，把生成的不可变 runtime resolution 安装到 Node 的解析器中。**启动不会创建共享或 profile 自有的 fallback 链接。**

## 5. 五套内置 profile 的初始化

首次使用时从随附模板自动初始化：

| Profile | 组合 | patch 应用时机 | HMR |
|---|---|---|---|
| `web` | base + web-app | 实时应用 | 启用 |
| `headless` | base + headless | 只在启动时 | 禁用 |
| `sdk` | base + sdk-app | 只在启动时 | 禁用 |
| `sdk-minimal` | 独立组合包 | 只在启动时 | 不包含 |
| `acp` | base + acp-app | 只在启动时 | 禁用 |

其他缺失的 profile 会显式报错，并提示运行 `dsh plugin --profile <name> add <package>`。

## 6. --dump-config：最实用的调试手段

```sh
dsh --profile web --dump-default-config   # 只看组合包层
dsh --profile web --dump-config            # 再叠加 profile / home / --patch 层
dsh --profile web --dump-config-schema     # JSON Schema 2020-12
```

要点：

- 输出是**一份可加载的 YAML**，用 `# ==` 注释标明每行来自哪个文件、哪一层 patch
- `!!js` 表达式**保持未求值**
- 未匹配到任何行的 patch 会连同层标签报告到 stderr
- dump 会初始化缺失的 profile 文件
- dump **不运行应用的命令行参数提供方**，展示的是解析应用参数之前的组合配置树；若调用中包含应用参数，dump 会拒绝该调用
- 三种 dump flag **互斥**，且都拒绝保留的 `desktop` profile

`--dump-config-schema` 的输出里有根 `x-cordis` 注释（`profile`/`complete`/`entries`/`diagnostics`/`patchSchema`）与 `x-cordis` 字段级注释（`secret`、`credential-ref`、`ms` 等 role 元信息、`volatile` 实时更新元信息）。若存在错误诊断或 `partial`/`unsupported`/`error` 条目，`complete` 为 false。

## 7. 应用参数边界（常踩）

启动器自己的 flag 必须写在最前，遇到第一个无法识别的 token 就结束；从该 token 起的内容通过 `ctx.cmdlineArgs` 原样交给 profile。

```sh
dsh web --port 8080      # --port 归 Web 应用解析
dsh --profile web --help # 只打印 Web 应用的帮助，不启动
dsh --help               # 启动器自身帮助（没有可交付参数的 profile）
```

需要把字面量 `--` 送达应用时写 `-- --`（启动器解析器会消耗掉一个 `--`）。

## 下一步

- [能力 seam 与子系统地图](08-capability-seams.md)——base 里那些插件分别做什么
- [写插件与组合包实战](../examples/03-custom-plugin-bundle.md)
