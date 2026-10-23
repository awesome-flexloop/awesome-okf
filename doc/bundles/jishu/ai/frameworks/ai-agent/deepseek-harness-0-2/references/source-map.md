---
type: reference
title: "源码路径与包清单登记"
description: "DeepSeek Harness 0.2.1-rc.2 的本地源码路径登记：仓库布局、52 个包分组与 342 个包目录、核心运行时源码文件位置、中文文档集位置，以及本束各页对应的源码依据。"
tags: [deepseek-harness, source-map, reference, dsh]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-local-mirror
    resource: https://github.com/deepseek-ai/deepseek-harness/tree/main
    title: 本地源码镜像 deepseek-harness（0.2.1-rc.2）
---

# 源码路径与包清单登记

本页是本束的**溯源索引**：每一页讲什么、对应仓库里哪个路径，方便二次核对。

## 1. 仓库根元信息（源码事实）

| 项 | 值 |
|----|-----|
| 包名 | `@deepseek-ai/dsh-root` |
| 版本 | `0.2.1-rc.2` |
| License | MIT |
| `type` | `module` |
| 包管理器 | `pnpm@11.28.5` |
| Node 引擎 | `^22.19.0 \|\| >=24.0.0` |
| workspaces | `vendor/*`、`packages/*/*`、`native/system`、`native/system/packages/*`、`apps/*`、`website` |

> `packages/*/*` 这一 glob 是**两层**结构：`packages/<组>/<包>`。这也是"52 组 / 342 包"计数的来源。

## 2. 顶层目录

```text
deepseek-harness/
├── apps/            # cli · desktop · desktop-host · plugin-market-generator · web
├── packages/        # 52 个分组目录，其下 342 个包目录
├── python/          # sdk（对外 Python 包）· sdk-runtime（原生运行时打包）
├── docs/            # 官方文档集（.md 英文 + .zh.md 中文 + .i18n.yaml）
├── vendor/          # vendored Cordis 生态：cordis · schemastery · cosmokit · loader · hmr · group · logger-console · timer · include
├── native/          # native/system 原生模块
├── website/         # 官网
└── scripts/         # 构建脚本（build.ts · primary-runtime/prepare.ts）
```

## 3. 52 个包分组

按字母序：

```text
acp  api  attachment  boot  browser-use  bundle  client  compaction
computer-use  context  core  credentials  deliverables  document
experimental  extensions  feedback  fs  goal  guard  host  identity
interaction  jobs  llm  lsp  mcp  plan  preset  ptc-runtime  sandbox
schedule  sdk  session  session-query  settings  shell  skill  spill
ssh  storage  subagent  subprocess  telemetry  terminal  test-support
todo  typert  util  web  workflow  workspace
```

## 4. 关键分组与包（按本束主题）

### 核心运行时 `packages/core/`

| 包 | 职责 | 关键源文件 |
|----|------|-----------|
| `core/agent-loop` | agent loop：turn/step 状态机、pre-step 准入、工具调用调度 | `src/agent.ts`、`src/tool-calls.ts`、`src/inbox.ts`、`src/runtime-context.ts`、`src/assistant-stream.ts`、`src/constants.ts` |
| `core/session` | SessionEvent 变体、信封、投影、修复、seq-ranges | `src/types.ts`、`src/index.ts`、`src/known-event-types.ts`、`src/surface.ts`、`src/fork.ts`、`src/repair.ts`、`src/seq-ranges.ts`、`src/tool-history.ts`、`src/request-header.ts`、`src/preparation.ts` |
| `core/tools` | `defineTool`、schema DSL、类型映射、展示层 | `src/schema.ts`、`src/types.ts`、`src/json-schema.ts`、`src/presentation.ts`、`src/ts-types.ts`、`src/py-types.ts`、`src/ptc.ts` |
| `core/agent` | agent 能力定义 | `src/` |
| `core/agent-tool-presentation` | 工具结果呈现 | `src/` |
| `core/system-prompt` | 系统提示词组装（两阶段） | `src/` |
| `core/scope` | 作用域 / 工具可见性 | `src/` |
| `core/agent-default-model` | 默认模型选择 | `src/` |

### LLM 抽象 `packages/llm/`

| 包 | 职责 |
|----|------|
| `llm/llm` | 适配器契约、`ContentBlockMap`、`StreamChunk` 联合、`BlockAssembler`、usage 约定 |
| `llm/llm-deepseek` | DeepSeek 适配器 |
| `llm/llm-deepseek-api-key` / `llm-deepseek-account` | 两种凭据提供方式 |
| `llm/llm-pi-ai` | Pi-AI 适配器 |
| `llm/llm-retry` | 重试策略 |
| `llm/token-meter` | token 计量（`TokenMeasurement`、baseline） |
| `llm/deepseek-llm-api-extensions` | 官方 API 线上扩展 |
| `llm/plugin-package-inventory-deepseek` | 插件包清单 |

关键源文件：`packages/llm/llm/src/types.ts`（`StreamChunk`）、`content.ts`、`message.ts`、`assembler.ts`、`error.ts`、`adapter-failure.ts`、`call-config.ts`、`retry-policy.ts`。

### 会话与持久化 `packages/session/`

| 包 | 职责 |
|----|------|
| `session/session-format` | 事件格式定义（当前 v4） |
| `session/session-format-catalog` | 格式目录 |
| `session/session-format-v0-to-v1` … `v3-to-v4` | 四段迁移链 |
| `session/session-persistence` / `session-persistence-jsonl` | 持久化 seam 与 JSONL 实现 |
| `session/session-projection` / `session-projection-cache` | 投影 |
| `session/session-log-deepseek` | DeepSeek 侧日志上传（默认开启，8 MiB/请求） |
| `session/session-stats` / `session-telemetry` / `session-telemetry-otel` | 统计与遥测 |
| `session/session-title` / `session-title-llm` / `session-title-first-prompt-llm` | 会话标题 |
| `session/session-turn-outline` | 轮次大纲 |
| `session/session-checkpoint-policy` | 检查点策略 |
| `session/working-directory` / `tool-working-directory` | 工作目录 |
| `session/session-format-*` 相关实验 | `packages/experimental/persistence-catalog` |

### 组合包 `packages/bundle/`

| 包 | 职责 |
|----|------|
| `bundle/base` | `dsh-base`：默认大组合包；配置入口 `packages/bundle/base/cordis.patch.yml` |
| `bundle/sdk-minimal` | Python SDK 随附的**极简独立** profile（空根 + 完整配置树，不含 `dsh-base`） |
| `bundle/sdk-app` | SDK server 配置项 |
| `bundle/acp-app` / `bundle/headless` / `bundle/web-app` | 其余应用形态组合包 |

### 文件系统与 Shell `packages/fs/` `packages/shell/`

`fs/`：`fs`（抽象）、`fs-local`（本地后端）、`fs-sandbox`、`fs-observation-policy`、`tool-fs`、`tool-fs-search`、`tool-str-replace-editor`。

`shell/`：`shell`（抽象）、`shell-env`、`bash-local`、`bash-sandbox`、`pwsh-local`、`pwsh-sandbox`、`tool-bash`、`tool-bash-persistent`、`tool-pwsh`、`tool-pwsh-persistent`。

### 子 Agent `packages/subagent/`

`subagent`（委派服务，`ctx.subagents`）、`subagent-spawn-in-process`、`subagent-fork-in-process`、`subagent-acp`、`subagent-codex`、`subagent-claude-code`、`subagent-dsh-sdk`、`tool-subagent`（模型可见委派工具，默认名 `subagent`）、`tool-subagent-control`（`send_message` / `interrupt_agent` / `list_agents`）。

关键源文件：`packages/subagent/tool-subagent/src/index.ts`、`packages/subagent/tool-subagent-control/src/index.ts`、`packages/subagent/tool-subagent-control/src/list-agents.ts`。

### 其余能力分组速查

| 分组 | 覆盖内容 |
|------|---------|
| `acp` | Agent Client Protocol 服务端 |
| `mcp` | MCP 客户端与服务器 |
| `lsp` | 语言服务器协议 |
| `skill` | Skills 加载与 rank |
| `sandbox` | 沙箱执行后端 |
| `guard` / `approval`（交互域） | 审批与守卫 |
| `storage` | 通用存储 seam |
| `workflow` / `schedule` / `jobs` | 工作流、定时、后台作业 |
| `browser-use` / `computer-use` | 浏览器与计算机操作 |
| `web` | Web 应用 |
| `client` | 客户端 UI 包（`ui-subagent`、`ui-settings-subagent` 等） |
| `telemetry` | 遥测 |
| `todo` / `plan` / `goal` | 任务与规划 |
| `credentials` / `identity` / `settings` | 凭据、身份、设置 |
| `spill` / `attachment` / `document` / `deliverables` | 产物与附件 |
| `ssh` / `terminal` / `subprocess` / `ptc-runtime` | 远程与进程 |

## 5. 官方文档集位置

仓库 `docs/` 每篇都有三件套：`<name>.md`（英文）、`<name>.zh.md`（中文）、`<name>.i18n.yaml`（翻译元信息）。

| 路径 | 内容 |
|------|------|
| `docs/architecture.zh.md` | 架构总览 |
| `docs/cordis-primer.zh.md` | Cordis 入门 |
| `docs/capability-seams.zh.md` | 能力 seam |
| `docs/event-producer-consumer.zh.md` | 事件生产/消费 |
| `docs/tool-execution-pipeline.zh.md` | 工具执行流水线 |
| `docs/tool-catalog.zh.md` | 工具目录 |
| `docs/config-catalog.zh.md` | 配置目录 |
| `docs/agent-lifecycle.zh.md` | agent 生命周期 |
| `docs/glossary.zh.md` | 术语表 |
| `docs/session-format-status.zh.md` | 会话格式状态 |
| `docs/persistence-catalog.zh.md` | 持久化目录 |
| `docs/subsystems/*.zh.md` | **67 篇**子系统文档 |
| `docs/user/guide/python-sdk.zh.md` | Python SDK 指南 |
| `docs/user/develop/basic/publish.zh.md` | 插件发布 |
| `docs/cookbook/` | 菜谱（含 adding-a-package） |
| `docs/upgrade-guide/` | 升级指南（v0.2.0-rc.2 / v0.2.1-alpha.x） |
| `apps/cli/reference/README.zh.md` | CLI 与 profile 分层参考 |

每个包目录还带自己的 `README.zh.md`，是**包级权威说明**（比总览文档更细）。

## 6. 本束页面 ↔ 源码依据对照

| 页面 | 主要源码依据 |
|------|-------------|
| [入门指引](../concepts/00-getting-started.md) | `apps/cli/reference/README.zh.md`、`packages/bundle/base/cordis.patch.yml` |
| [架构总览](../concepts/01-architecture-overview.md) | `docs/architecture.zh.md`、`docs/capability-seams.zh.md` |
| [Cordis 插件模型](../concepts/02-cordis-plugin-model.md) | `docs/cordis-primer.zh.md`、`vendor/cordis/`、`vendor/schemastery/` |
| [Profile 与组合包](../concepts/03-profile-and-bundle.md) | `apps/cli/reference/README.zh.md`、`packages/bundle/*/cordis.patch.yml` |
| [Agent 循环](../concepts/04-agent-loop.md) | `packages/core/agent-loop/src/agent.ts`、`docs/agent-lifecycle.zh.md` |
| [会话与持久化](../concepts/05-session-and-persistence.md) | `packages/core/session/src/`、`packages/session/session-format*` |
| [工具系统](../concepts/06-tool-system.md) | `packages/core/tools/src/`、`docs/tool-execution-pipeline.zh.md`、`docs/tool-catalog.zh.md` |
| [LLM 抽象层](../concepts/07-llm-abstraction.md) | `packages/llm/llm/src/`、`packages/compaction/` |
| [能力 seam 与子系统地图](../concepts/08-capability-seams.md) | `docs/subsystems/*.zh.md`、`docs/capability-seams.zh.md` |
| [安全模型](../concepts/09-security-model.md) | `packages/sandbox/`、`packages/interaction/`、`docs/subsystems/approval.zh.md` |
| [应用形态](../concepts/10-application-forms.md) | `apps/*`、`packages/bundle/*`、`python/sdk/` |
| [Headless 实战](../examples/00-headless-task.md) | `packages/bundle/headless/`、`apps/cli/src/` |
| [MCP 集成](../examples/01-mcp-integration.md) | `packages/mcp/` |
| [自定义工具](../examples/02-custom-tool.md) | `packages/core/tools/src/schema.ts`、`packages/fs/tool-fs/` |
| [插件与组合包](../examples/03-custom-plugin-bundle.md) | `docs/user/develop/basic/publish.zh.md`、`docs/cookbook/adding-a-package` |
| [Python SDK 嵌入](../examples/04-python-sdk-embedding.md) | `python/sdk/src/deepseek_harness/api.py`、`docs/user/guide/python-sdk.zh.md` |

## 相关

- [事实登记 F-001~F-048](facts.md)
- [架构总览](../concepts/01-architecture-overview.md)
