---
type: concept
title: "能力 seam 与子系统地图"
description: "dsh 各能力子系统的职责、ctx 键与关键配置：MCP、Subagent、Agent Team、Skills、Filesystem/Shell/Terminal、LSP、Storage/Persistence、Workflow/Schedule/Jobs、Browser-use/Computer-use 等。"
tags: [deepseek-harness, subsystems, mcp, subagent, skills, lsp, storage, workflow]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 docs/subsystems/*.zh.md 与 docs/tool-catalog.zh.md
---

# 能力 seam 与子系统地图

> 每个 seam 都由 **Service Definition / Service Provider / Consumer** 三角色构成。本页给出各子系统的职责、ctx 键与关键配置项。

## 1. 总览表

| 子系统 | 职责 | ctx 键 | 关键包 |
|---|---|---|---|
| **MCP** | 把外部 MCP 服务器的工具/资源/指令适配为普通 Harness 工具 | `ctx.mcpResources` | `dsh-mcp-client`、`dsh-mcp-resources` |
| **Subagent** | 统一 activation API 管理本地会话与外部执行（Codex/Claude Code/ACP/DSH SDK） | `ctx.subagents` | `dsh-subagent`、`dsh-tool-subagent`、`dsh-tool-subagent-control` |
| **Agent Team** | 实验性隐式 Root Team：持久 teammate 名册 + 共享任务 DAG + mailbox | `ctx.agentTeams` | `dsh-experimental-agent-team`、`dsh-experimental-tool-agent-team` |
| **Skills** | 分层 skill 注册表，模型按需加载技能正文 | `ctx.skills`、`ctx.sessionSkillCatalog` | `dsh-skill`、`dsh-skill-filesystem`、`dsh-tool-skill` |
| **Filesystem** | 带守卫的原子文本操作 + 观测策略 | `ctx.fs` | `dsh-fs`、`dsh-fs-local`、`dsh-fs-observation-policy` |
| **Shell** | bash / PowerShell 执行 seam | `ctx.shell`、`ctx.shellEnv` | `dsh-shell`、`dsh-bash-local`、`dsh-pwsh-local`、`dsh-tool-bash` |
| **Terminal** | 持久 PTY 会话，跨调用保留 cwd/环境/REPL 状态 | `ctx.terminals` | `dsh-terminal`、`dsh-experimental-tool-terminal` |
| **LSP** | 单一 seam 暴露 4 项语义代码导航 | `ctx.lsp` | `dsh-lsp`、`dsh-lsp-stdio`、`dsh-tool-lsp` |
| **Storage** | 持久保存一切非会话事件日志数据（hub + 后端 + 数据形式） | `ctx.storage`、`ctx.storageDomain` | `dsh-storage`、`dsh-storage-json`、`dsh-storage-sqlite` |
| **Persistence** | 会话事件日志的持久性 seam | `ctx.sessionPersistence` | `dsh-session-persistence-jsonl` |
| **Workflow** | 让模型写编排脚本、批量启动 subagent | `ctx.workflowEngine` | `dsh-workflow`、`dsh-workflow-ptc`、`dsh-tool-workflow` |
| **Schedule** | 宿主级提醒，独立于 Session 生命周期，到期投递回原 Session | `ctx.schedule` | `dsh-schedule`、`dsh-tool-schedule` |
| **Jobs** | 后台任务注册表：统一 id/所有权/控制 | `ctx.jobs`、`ctx.jobController` | `dsh-jobs`、`dsh-jobs-local`、`dsh-tool-jobs` |
| **Browser-use** | 模型通过提供方检查与操作网页，浏览器状态跨轮次保留 | `ctx.browserUse` | `dsh-browser-use`、`dsh-experimental-browser-use-stagehand-native` |
| **Computer-use** | 模型观察并操作本地桌面 | `ctx.computerUse` | `dsh-computer-use`、`dsh-experimental-computer-use-cua-driver-*` |
| **Approval** | 回答"这个具体操作能否继续" | `ctx.approval` | `dsh-user-approval` |
| **Permission Presets** | 把沙箱模式 + 审批策略捆成具名预设 | `ctx.permissionPresets` | `dsh-permission-presets` |
| **Sandbox** | 把子进程 argv 包进文件效果策略，跨平台隔离执行 | `ctx.sandbox`、`ctx.sandboxPolicy` | `dsh-sandbox`、`dsh-sandbox-local`、`dsh-sandbox-policy` |
| **Plan mode** | 先出 markdown 计划交用户评审，批准后才执行 | `ctx.planMode` | `dsh-plan-mode` |
| **Todo / Goal** | 待办整表替换式写入；带 revision 的目标 CAS | — | `dsh-tool-todo`、`dsh-goal`、`dsh-tool-goal` |
| **Webhook** | fire-and-forget 的外部投递回调 | `ctx.webhookRuntime` | `dsh-webhook`、`dsh-webhook-github` |
| **Attachment** | 内容寻址的附件存储 | `ctx.attachments`、`ctx.fileUploads` | `dsh-attachment` |

## 2. MCP 集成

- 传输：`stdio` 与 `streamable-http`
- 工具以 `mcp__<serverName>__<tool>` 命名空间暴露
- 关键配置：`serverName`、`transport`、`command`/`args`/`env`/`cwd` 或 `url`/`headers`、`toolCallTimeoutMs`、`failOnStartupError`、`maxInstructionBytes`（默认 32768）、`reconnect{ enabled, initialDelayMs=500, maxDelayMs=30000, maxAttempts=10 }`
- 客户端级审批复用 `approval/*`；资源工具走常规 `tool/call`/`tool/result` 管线

详见 [接入 MCP 服务器](../examples/01-mcp-integration.md)。

## 3. 子 Agent 与 Agent Team

**Subagent** 的能力集 `SubagentCapabilities { agentOptions, agentPreset, outputSchema, depthLimit }`；工具名默认 `subagent`（别名 `subagent_fork`），`maxDepth` 限制委派深度。

provider 家族：`subagent-spawn-in-process`、`subagent-fork-in-process`、`subagent-codex`、`subagent-claude-code`、`subagent-acp`、`subagent-dsh-sdk`。

**Agent Team**（实验性）是"可继续 subagent"之上的协作层：

- `TeamMemberSnapshot.phase`：`provisioning → active` / `failed`
- `TeamTaskSnapshot.revision`（CAS 乐观并发）、`blockedBy`、`writeScopes`（**提示性**路径前缀，不是锁）
- 事件：`team/member`、`team/task`、`agent/inbox/spliced`
- 工具：`spawn_teammate`、`team_task_create|get|list|update`、`wait_agent`

## 4. Skills 分层

本地发现的 rank（数值小者优先）：

| rank | 来源 |
|---|---|
| 100 | `project-dsh`（`<projectRoot>/.dsh/skills`） |
| 200 | `project-agents` |
| 300 | `custom` |
| 400 | `user-dsh` |
| 500 | `user-agents` |
| 600 | `bundled` |

frontmatter 支持 `disable-model-invocation`、`user-invocable`；`catalogDescriptionMaxLength` = 500。

## 5. LSP

单一 seam 暴露 4 项操作：`goToDefinition`、`findReferences`、`goToImplementation`、`hover`。坐标为 **0-based UTF-16**（工具层转 1-based）；提供方需声明 `extensionToLanguage`；错误码 `LSP_UNAVAILABLE` / `LSP_CONFLICT`。

> **换提供方不改模型可见 schema**——这是 seam 设计的一致性约束，`lsp` / `web` / `browser-use` 都明确如此。

## 6. Storage 与 Persistence

- Storage 后端：`json` / `sqlite`；`ctx.storage.mount(form, facility)` 挂载领域层
- 错误码：`already-open`、`backend-not-found`、`facet-unsupported`、`duplicate-mount`
- Persistence 的 `create`/`open`/`stat`/`list` 返回 `SessionHandle { read, append, flush, close }`；**单写者所有权**；`flush` 是持久化屏障；未知事件词汇 fail-closed

## 7. Workflow / Schedule / Jobs

**Workflow**：`WorkflowStartRequest { script, meta, args?, subagentProvider?, maxTotalAgents?, parent, signal? }`；`WorkflowMeta { name, description, whenToUse?, phases? }`；结果 `WorkflowResult { value, stopReason, error?, agentsStarted }`。事件：`workflow/start|phase|log|agent-start|agent-end|end`。

**Schedule**：规则类型 `after` / `at` / `every` / `daily` / `weekly` / `cron`；`deliveryHistoryDays` = 30、`deliveryHistoryRecords` = 200；`title` 必填且 ≤ 120 字符。到期后投递回**原 Session**。

**Jobs**：`JobId = '<kind>-<short-uuid>'`；`JobStatus = running|stopping|completed|killed|failed`；`maxConcurrentJobsPerOwner` = 10、`retainBytes` = 262144、`settledRetainBytes` = 16384、`pumpPollMs` = 150。

## 8. Browser-use / Computer-use

- Browser 提供方：Playwright MCP、Chrome DevTools MCP、Stagehand（`stagehand_act/extract/navigate/observe/screenshot/tabs` 六个工具）；浏览器状态**跨轮次保留**；Session 所有权，attach 模式独占保留
- Computer-use 提供方：Cua Driver MCP / Cua Driver 原生；macOS CUA 经 User Questions 申请应用授权

## 9. 插件管理器与市场

- `ctx.pluginManager` + 工具 `plugin_manager`；CLI `dsh plugin --profile <name> <pnpm args...>`
- 注册表顺序：`options.registry` → 配置的 `registry` → `fallbackRegistries`（默认 `['https://registry.npmmirror.com/']`）
- `ctx.pluginMarket` + 工具 `plugin_market`（只读、无需批准）；**无索引源时不发任何请求**；索引在 Worker Thread 中按严格 UTF-8 解码与校验，文本搜索用 MiniSearch（支持 CJK 双字组合）

## 下一步

- [安全模型](09-security-model.md)
- [接 MCP](../examples/01-mcp-integration.md) / [写自定义工具](../examples/02-custom-tool.md)
