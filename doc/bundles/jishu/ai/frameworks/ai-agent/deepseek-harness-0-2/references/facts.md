---
type: reference
title: "事实登记 F-001~F-048"
description: "本束 48 条编号事实的登记表，区分「源码事实」（可在 dsh 0.2.1-rc.2 源码中直接验证）与「文档主张」（官方文档表述），供复核与引用时溯源。"
tags: [deepseek-harness, facts, reference, verification]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 0.2.1-rc.2
---

# 事实登记 F-001~F-048

每条事实标注**证据等级**：

- **S（源码事实）**——可在 dsh 0.2.1-rc.2 源码/配置中直接读到，复核路径一并给出。
- **D（文档主张）**——来自官方中文文档或包 README 的表述，本束转述时保留其口径。

## 1. 仓库与工程

| 编号 | 事实 | 等级 | 复核路径 |
|------|------|------|---------|
| F-001 | 仓库版本为 `0.2.1-rc.2`，License MIT，包名 `@deepseek-ai/dsh-root` | S | `package.json` |
| F-002 | 包管理器 `pnpm@11.28.5`；Node 引擎 `^22.19.0 \|\| >=24.0.0` | S | `package.json` |
| F-003 | workspaces 含 `packages/*/*`，即包布局为两层 `packages/<组>/<包>` | S | `package.json` |
| F-004 | `packages/` 下 52 个一级分组目录、342 个二级包目录 | S | 目录计数 |
| F-005 | Cordis 生态被 vendored 进 `vendor/`：`cordis`、`schemastery`、`cosmokit`、`loader`、`hmr`、`group`、`logger-console`、`timer`、`include` | S | `vendor/` |
| F-006 | 应用层共 5 个：`cli`、`desktop`、`desktop-host`、`plugin-market-generator`、`web` | S | `apps/` |
| F-007 | 官方文档集为 `.md`（英）+ `.zh.md`（中）+ `.i18n.yaml`（翻译元）三件套；`docs/subsystems/` 有 67 篇中文子系统文档 | S | `docs/` |

## 2. 架构与插件模型

| 编号 | 事实 | 等级 | 复核路径 |
|------|------|------|---------|
| F-008 | 架构主张是"一切皆插件（everything-is-a-plugin）"：无特权内核，模型适配器、工具注册表、会话日志、agent loop 本身均为可替换插件 | D | `docs/architecture.zh.md` |
| F-009 | Cordis 四抽象为 Context / Service / Plugin / Fiber；Service 是 class 而非 interface | D | `docs/cordis-primer.zh.md` |
| F-010 | 插件三形态：函数式（导出 `apply`）、对象式、类式（继承 `Service`） | D | `docs/user/develop/basic/publish.zh.md` |
| F-011 | 配置 schema 必须导出 `interface Config` 与同名 `const Config: Schema<Config>`（Schemastery），导出普通对象不工作 | D | 同上 |
| F-012 | Cordis 支持声明合并，插件可扩展既有 event type 与 config 字段 | D | `docs/cordis-primer.zh.md` |
| F-013 | 依赖注入通过 `inject` 声明，值为被注入 ctx 键名数组 | D | 同上 |
| F-014 | `ctx.effect` 维护副作用栈，disposer 按**逆序**执行 | D | 同上 |
| F-015 | Fiber 生命周期为 `PENDING → LOADING → ACTIVE → UNLOADING → DISPOSED`，另有 `FAILED` | D | 同上 |
| F-016 | Cordis 支持五种事件模式：emit / parallel / serial / bail / waterfall；瀑布事件必须调用 `next()` | D | 同上 |
| F-017 | HMR 由 `vendor/hmr` 的 Loader 机制处理模块替换；base 以 `root: []` 启用配置监听 | D | `docs/development.zh.md` |

## 3. Profile 与组合包

| 编号 | 事实 | 等级 | 复核路径 |
|------|------|------|---------|
| F-018 | 配置叠加共四层：bundle patch → profile `cordis.patch.yml` → home `$DSH_HOME/cordis.patch.yml` → `--patch` overlay | D | `apps/cli/reference/README.zh.md` |
| F-019 | patch 是**整行替换** config，不做深合并 | D | 同上 |
| F-020 | `packages/bundle/base/cordis.patch.yml` 是 `dsh-base` 的配置入口 | S | `packages/bundle/base/` |
| F-021 | `sdk-minimal` 的组合包在**空根**之上插入完整配置树，且**不包含** `dsh-base`，因此基础 profile 新增工具不会隐式出现 | D | `packages/bundle/sdk-minimal/README.zh.md` |
| F-022 | headless / SDK / ACP profile 在 YAML 中**禁用 HMR**（保证一条 stdio 连接不观察到依赖被替换） | D | `packages/bundle/*/README.zh.md` |
| F-023 | `dsh plugin` 把参数转发给 `pnpm`（add / remove / why / update 等），pnpm 必须在 PATH 上 | D | `docs/user/develop/basic/publish.zh.md` |
| F-024 | 相对路径 spec 会先锚定到**调用目录**；组合包声明 `"dsh": { "bundle": { "patch": "./cordis.patch.yml" } }` 的依赖会被记录进 `dsh.profile.bundles` | D | 同上 |
| F-025 | 安装后**须重启 profile**——组合包成员变化属于启动边界 | D | 同上 |
| F-026 | git 安装需作者提供自包含 `prepare` 脚本，且使用方要在 profile 的 `pnpm-workspace.yaml` 里授权 `allowBuilds`（pnpm ≥10 默认阻止） | D | 同上 |
| F-027 | 组合包 `package.json` 用 `engines.dsh` 声明兼容版本范围（如 `>=0.2.0 <0.3.0`） | D | 同上 |
| F-028 | 插件行在 patch 中按**包名**引用，而非相对路径 | D | 同上 |
| F-029 | `--dump-config-schema` 输出 JSON Schema 2020-12，`x-cordis` 注释保留 `secret`、`credential-ref`、`ms` role 元信息 | D | 同上 |

## 4. Agent 循环

| 编号 | 事实 | 等级 | 复核路径 |
|------|------|------|---------|
| F-030 | step = 一次模型请求 + 其触发的工具调用；turn = 零或多个 step | S | `packages/core/agent-loop/src/agent.ts` |
| F-031 | `turn/start` 在循环领取排队输入或运行 pre-step **之前**开启；`turn/end` 以 `TurnEndReason` 关闭 | S | `packages/core/session/src/types.ts` |
| F-032 | `agent/pre-step` 是准入关口（拒绝会关闭 turn 且不产生 step） | D | `docs/subsystems/core.zh.md` |
| F-033 | `agent/request` 只允许**替换配置**，不改变请求结构 | D | 同上 |
| F-034 | 取消语义区分 `TOOL_OUTCOME_UNKNOWN` / `TOOL_NOT_STARTED` / `ABORTED_BEFORE_DISPATCH`，缺失的工具结果会被补记 | D | 同上 |
| F-035 | turn 边界**不**等待 flush；逐请求持久化检查点由 `dsh-session-checkpoint-policy` 拥有 | S | `packages/core/session/src/types.ts` |
| F-036 | `RequestHeaderReason` 取值为 `initial` / `resume` / `change` / `series` | S | 同上 |

## 5. 会话与持久化

| 编号 | 事实 | 等级 | 复核路径 |
|------|------|------|---------|
| F-037 | `SessionEventMap` 有 **14** 个核心变体：turn/start、turn/end、step/start、step/end、user/message、developer/message、system/message、assistant/message、assistant/attempt、tool/call、tool/result、request/header、request/context、session/end-seed | S | `packages/core/session/src/types.ts` |
| F-038 | 事件信封为 `{ type, seq, time, data, ignorable?, surfaceOp?, sourceEventSeqs? }`；`surfaceOp`/`sourceEventSeqs` 只在 surface 事件上携带 | S | 同上 |
| F-039 | `Session.deriveMessages()` 把事件投影为模型消息；`tool/result` 投影为**一等 tool-role 消息**（非 ContentBlock） | D | `packages/core/session/src/index.ts` |
| F-040 | assistant 消息内容为空则**跳过**，不进 transcript | D | 同上 |
| F-041 | 派生缓存含 `derived`/`derivedNodes`/`derivedGeneration`；`contentGeneration` 变化整体重建，纯尾部增长只处理新增节点；返回**新数组**，内部 Message 共享且深冻结 | D | 同上 |
| F-042 | 会话格式有迁移链 v0→v1→v2→v3→v4（`session-format-v0-to-v1` … `v3-to-v4` 四个包） | S | `packages/session/` |
| F-043 | `session/end-seed` 标记区分"继承/恢复的历史"与"本会话自有的工作"；只有 `Session` 构造函数与 `buildForkSeed` 可创建该标记 | S | `packages/core/session/src/types.ts` |

## 6. 工具、LLM 与安全

| 编号 | 事实 | 等级 | 复核路径 |
|------|------|------|---------|
| F-044 | 工具结果是一等 `ToolResultMessage`；`tool/result` 的 `meta` 必须可 JSON 序列化，`Session.append` 会用 `isJsonValue` 运行时校验，非可序列化载荷在源头即被拒 | S | `packages/core/session/src/types.ts` |
| F-045 | `usage` 随 `assistant/message` 一起携带（**不存在独立的 usage 记录**）；适配器未上报时 `usage` 缺席 | S | 同上 |
| F-046 | `sdk-minimal` 组合包**固定使用 `danger-full-access`**，持久 shell 可修改运行时可见的任何路径 | D | `packages/bundle/sdk-minimal/README.zh.md` |
| F-047 | `session-log-deepseek` 默认随 DeepSeek 请求上传未被接受的日志事件，每次请求上限 8 MiB；可在 profile patch 中设 `session-log-deepseek.enabled: false` 关闭 | D | `packages/session/session-log-deepseek/README.zh.md` |
| F-048 | Python SDK 不内含 Python 版 agent loop，而是延迟启动随包附带的 `dsh --profile <profile>` 原生进程，协议为 JSON-RPC over stdio；普通 SDK 运行不需要系统 Node.js | D | `python/sdk/src/deepseek_harness/api.py`、`docs/user/guide/python-sdk.zh.md` |

## 附：Python SDK 配置默认值（源码事实，来自 `DeepSeekHarnessConfig`）

| 字段 | 默认 |
|------|------|
| `provider` | `deepseek-official` |
| `model` | `deepseek-v4-flash` |
| `profile` | `sdk` |
| `patches` | `()` |
| `initialize_timeout_seconds` | `30.0` |
| `shutdown_timeout_seconds` | `1.0` |
| `reasoning_effort` / `max_tokens` / `cwd` / `runtime_cwd` / `dsh_bin` / `dsh_home` / `base_url` / `api_key` / `request_timeout_seconds` | `None` |

`RunResult` 字段：`session_id`、`final_response`、`finish_reason`、`events`、`notifications`。

## 相关

- [源码路径与包清单登记](source-map.md)
- [架构总览](../concepts/01-architecture-overview.md)
