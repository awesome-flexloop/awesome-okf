---
type: Facts
okf_version: '0.2'
generated: '2026-08-22'
tags:
- jupyter
- ai
- agent
- llm
- mcp
- tool-calling
- jupyterlab-extension
sources:
- ../../../../../external/libs/jupyter/jupyter-ai/pyproject.toml
- ../../../../../external/libs/jupyter/jupyter-ai/README.md
title: jupyter-ai 源码事实清单
---

# jupyter-ai Facts

## 项目元数据

- F-001: package.json:2 — 项目名称为 `jupyterlite-ai-monorepo`，是一个 JupyterLite AI 单仓库项目。
- F-002: package.json:3 — 版本号为 `0.19.0`。
- F-003: package.json:4 — 标记为 `private: true`，不发布到 npm。
- F-004: package.json:5 — 描述为 "Monorepo for JupyterLite AI - Agent and JupyterLab extension"。
- F-005: package.json:6-8 — 使用 Yarn workspaces 管理 `packages/*` 目录下的子包。
- F-006: packages/agent/package.json:2 — Agent 包名为 `@jupyternaut/agent`。
- F-007: packages/agent/package.json:4 — Agent 包描述为 "AI agent implementation for Jupyter using AI SDK"。
- F-008: packages/persona/package.json:2 — Persona 包名为 `@jupyternaut/persona`。
- F-009: packages/persona/package.json:4 — Persona 包描述为 "AI code completions and chat for JupyterLite"。
- F-010: packages/ai/package.json — AI 包为 `@jupyterlite/ai`，提供 JupyterLab 聊天界面集成。

## Monorepo 结构

- F-011: packages/ — 包含三个核心子包：`agent`（代理核心）、`persona`（角色/补全/聊天集成）、`ai`（聊天 UI 组件）。
- F-012: python/ — 包含两个 Python 包：`jupyterlite-ai` 和 `jupyternaut-persona`，用于 JupyterLab 扩展打包。
- F-013: ui-tests/ — 基于 Playwright 的 UI 端到端测试，包含 9 个测试 spec 文件。
- F-014: docs/ — 使用 Jupyter Book 构建文档，包含安装、使用、MCP 服务器、技能、Web 检索等章节。
- F-015: demo/ — 演示配置，包含 `jupyter_lite_config.json` 和 `pyproject.toml`。
- F-016: packages/agent/src/index.ts:3-16 — Agent 包公开 API 导出 agent、icons、tokens、providers、tools、skills 等所有模块。

## 核心依赖

- F-017: packages/agent/package.json:26 — 依赖 `@ai-sdk/anthropic: ^4.0.37`（Anthropic Claude 提供商）。
- F-018: packages/agent/package.json:27 — 依赖 `@ai-sdk/google: ^4.0.41`（Google Gemini 提供商）。
- F-019: packages/agent/package.json:28 — 依赖 `@ai-sdk/mcp: ^2.0.30`（MCP 协议客户端）。
- F-020: packages/agent/package.json:29 — 依赖 `@ai-sdk/mistral: ^4.0.28`（Mistral AI 提供商）。
- F-021: packages/agent/package.json:30 — 依赖 `@ai-sdk/openai: ^4.0.37`（OpenAI 提供商）。
- F-022: packages/agent/package.json:31 — 依赖 `@ai-sdk/openai-compatible: ^3.0.29`（通用 OpenAI 兼容提供商）。
- F-023: packages/agent/package.json:42 — 依赖核心 `ai: ^7.0.59`（Vercel AI SDK）。
- F-024: packages/agent/package.json:43 — 依赖 `jupyter-mcp-manager: ^0.2.0`（MCP 服务器管理）。
- F-025: packages/agent/package.json:44 — 依赖 `jupyter-secrets-manager: ^0.5.0`（密钥管理）。
- F-026: packages/agent/package.json:46 — 依赖 `zod: ^4.3.6`（参数 schema 验证）。
- F-027: packages/persona/package.json:46 — 依赖 `@jupyter/chat: ^0.24.1`（Jupyter 聊天组件库）。
- F-028: packages/persona/package.json:67-68 — UI 使用 `@mui/material: ^7` 和 `@mui/icons-material: ^7`。
- F-029: packages/persona/package.json:72 — 使用 `react: ^18.3.1` 构建 UI 组件。

## Agent 核心架构

- F-030: packages/agent/src/agent.ts:335 — `AgentManager` 类实现 `IAgentManager` 接口，管理 AI 代理生命周期和执行循环。
- F-031: packages/agent/src/agent.ts:109 — `AgentManagerFactory` 类实现 `IAgentManagerFactory`，作为工厂创建 AgentManager 实例。
- F-032: packages/agent/src/agent.ts:7 — 核心使用 AI SDK 的 `ToolLoopAgent` 实现多轮工具调用循环。
- F-033: packages/agent/src/agent.ts:312-313 — 默认参数：`DEFAULT_TEMPERATURE = 0.7`，`DEFAULT_MAX_TURNS = 25`。
- F-034: packages/agent/src/agent.ts:584-695 — `generateResponse()` 方法处理完整的用户消息→AI 响应→工具调用循环。
- F-035: packages/agent/src/agent.ts:935-951 — 使用 `new ToolLoopAgent(...)` 创建代理实例，配置 model、instructions、tools、temperature 等。
- F-036: packages/agent/src/agent.ts:947 — 使用 `stopWhen: isStepCount(maxTurns)` 限制最大工具调用轮次。
- F-037: packages/agent/src/agent.ts:948-950 — `toolApproval` 配置中对 `execute_command` 工具设置用户审批策略。

## 事件系统

- F-038: packages/agent/src/tokens.ts:464-501 — 定义 8 种代理事件类型：`message_start`、`message_chunk`、`message_complete`、`tool_call_start`、`tool_call_complete`、`tool_approval_request`、`tool_approval_resolved`、`error`。
- F-039: packages/agent/src/agent.ts:351 — 通过 Lumino Signal 机制发射 `_agentEvent` 事件。
- F-040: packages/agent/src/agent.ts:970-1049 — `_processStreamResult()` 方法处理流式结果，遍历 stream parts 并发射对应事件。
- F-041: packages/agent/src/agent.ts:356 — Token 使用量通过 `_tokenUsageChanged` Signal 通知 UI 更新。

## Token（依赖注入标识）

- F-042: packages/agent/src/tokens.ts:82-85 — `IToolRegistry` Token 标识工具注册表，ID 为 `@jupyternaut/agent:IToolRegistry`。
- F-043: packages/agent/src/tokens.ts:125-128 — `ISkillRegistry` Token 标识技能注册表，ID 为 `@jupyternaut/agent:ISkillRegistry`。
- F-044: packages/agent/src/tokens.ts:320-323 — `IProviderRegistry` Token 标识模型提供商注册表。
- F-045: packages/agent/src/tokens.ts:406-408 — `IAISettingsModel` Token 标识 AI 设置模型。
- F-046: packages/agent/src/tokens.ts:603-605 — `IAgentManager` Token 标识代理管理器。
- F-047: packages/agent/src/tokens.ts:635-637 — `IAgentManagerFactory` Token 标识代理管理器工厂。
- F-048: packages/agent/src/tokens.ts:710-712 — `IDiffManager` Token 标识差异管理器。

## 工具注册表（Tool Registry）

- F-049: packages/agent/src/tools/tool-registry.ts:8 — `ToolRegistry` 类实现 `IToolRegistry` 接口。
- F-050: packages/agent/src/tools/tool-registry.ts:12-14 — `tools` getter 返回工具的浅拷贝，防止外部修改。
- F-051: packages/agent/src/tools/tool-registry.ts:33-36 — `add()` 方法添加工具并发射 `toolsChanged` 信号。
- F-052: packages/agent/src/tools/tool-registry.ts:43-48 — `get()` 方法按名称获取工具，不存在返回 null。
- F-053: packages/agent/src/tools/tool-registry.ts:53-60 — `remove()` 方法移除工具，成功返回 true 并发射信号。

## 内置工具

- F-054: packages/agent/src/tools/commands.ts:96-143 — `createDiscoverCommandsTool()` 创建命令发现工具，支持多词搜索和加权排序。
- F-055: packages/agent/src/tools/commands.ts:167-221 — `createExecuteCommandTool()` 创建命令执行工具，支持参数传递和 Widget 结果序列化。
- F-056: packages/agent/src/tools/commands.ts:150-160 — `createExecuteCommandApprovalPolicy()` 创建命令审批策略，检查 `commandsRequiringApproval` 配置。
- F-057: packages/agent/src/tools/commands.ts:28-91 — `searchCommands()` 实现多字段加权搜索（label 权重 4、caption 权重 3、id 权重 2、description 权重 1）。
- F-058: packages/agent/src/tools/skills.ts:9-31 — `createDiscoverSkillsTool()` 创建技能发现工具，支持按查询过滤。
- F-059: packages/agent/src/tools/skills.ts:36-85 — `createLoadSkillTool()` 创建技能加载工具，支持加载技能定义和资源文件。
- F-060: packages/agent/src/tools/web.ts:106-239 — `createBrowserFetchTool()` 创建浏览器原生 URL 获取工具，支持 CORS、超时和内容截断。
- F-061: packages/agent/src/tools/web.ts:6-9 — Web 工具限制：默认最大内容 20000 字符（上限 100000），默认超时 20 秒（上限 120 秒）。
- F-062: packages/agent/src/tools/web.ts:24-98 — `readResponseText()` 使用流式读取和字符上限，避免大 payload 占用内存。
- F-063: packages/agent/src/tools/web.ts:158-165 — 仅支持 `http:` 和 `https:` 协议，拒绝其他协议。

## LLM 提供商系统

- F-064: packages/agent/src/providers/built-in-providers.ts:14-59 — 内置 Anthropic 提供商，支持 Claude Opus/Sonnet/Haiku 系列模型。
- F-065: packages/agent/src/providers/built-in-providers.ts:64-98 — 内置 Google 提供商，支持 Gemini 3.1/3/2.5 系列模型。
- F-066: packages/agent/src/providers/built-in-providers.ts:103-135 — 内置 Mistral 提供商，支持 Mistral Large/Medium/Small 等模型。
- F-067: packages/agent/src/providers/built-in-providers.ts:140-210 — 内置 OpenAI 提供商，支持 GPT-5/4/o 系列、o1/o3/o4 推理模型。
- F-068: packages/agent/src/providers/built-in-providers.ts:215-244 — 通用 OpenAI 兼容提供商，默认支持 LiteLLM（localhost:4000）和 Ollama（localhost:11434/v1）。
- F-069: packages/agent/src/providers/built-in-providers.ts:41 — Anthropic 配置 `cacheProviderOptions` 使用 ephemeral 缓存控制。
- F-070: packages/agent/src/providers/built-in-providers.ts:37-40 — Anthropic 提供商内置支持 webSearch（anthropic 实现）和 webFetch（anthropic 实现）。
- F-071: packages/agent/src/providers/built-in-providers.ts:195-197 — OpenAI 提供商内置支持 webSearch（openai 实现）。
- F-072: packages/agent/src/providers/built-in-providers.ts:51 — Anthropic 工厂函数设置 `anthropic-dangerous-direct-browser-access: 'true'` 头以支持浏览器直接访问。
- F-073: packages/agent/src/providers/provider-registry.ts:10 — `ProviderRegistry` 类实现 `IProviderRegistry` 接口。
- F-074: packages/agent/src/providers/provider-registry.ts:29-35 — `registerProvider()` 注册提供商，重复 ID 抛出错误。
- F-075: packages/agent/src/providers/models.ts:60-76 — `createModel()` 通过提供商注册表创建聊天模型实例。
- F-076: packages/agent/src/tokens.ts:204-272 — `IProviderInfo` 接口定义提供商元数据：id、name、apiKeyRequirement、defaultModels、factory 等。
- F-077: packages/agent/src/tokens.ts:221 — API Key 需求分为三档：`required`、`optional`、`none`。

## MCP 集成

- F-078: packages/agent/src/agent.ts:1 — 从 `@ai-sdk/mcp` 导入 `createMCPClient` 和 `MCPClient` 类型。
- F-079: packages/agent/src/agent.ts:48-51 — `IMCPClientWrapper` 接口包装 MCP 客户端，跟踪连接状态（name + client）。
- F-080: packages/agent/src/agent.ts:219-267 — `_initializeMCPClients()` 方法初始化 MCP 客户端，关闭旧连接并连接启用的 HTTP 类型服务器。
- F-081: packages/agent/src/agent.ts:235-237 — 仅连接 `type === 'http'` 的 MCP 服务器，跳过其他类型。
- F-082: packages/agent/src/agent.ts:246 — MCP HTTP 传输使用 `globalThis.fetch.bind(globalThis)` 避免浏览器中 "Illegal invocation" 错误。
- F-083: packages/agent/src/agent.ts:188-204 — `getMCPTools()` 从所有已连接的 MCP 服务器获取工具列表。
- F-084: packages/agent/src/agent.ts:153-164 — 新聊天可在 MCP 设置完成前创建，MCP 连接后自动重新初始化代理以传入 MCP 工具。

## 技能系统（Skills）

- F-085: packages/agent/src/skills/types.ts:9-12 — `ISkillSummary` 接口定义技能摘要：name + description。
- F-086: packages/agent/src/skills/types.ts:17-20 — `ISkillDefinition` 接口扩展摘要，包含 instructions 和 resources 列表。
- F-087: packages/agent/src/skills/types.ts:35-37 — `ISkillRegistration` 接口支持可选的 `loadResource` 函数用于加载资源文件。
- F-088: packages/agent/src/skills/skill-registry.ts:23 — `SkillRegistry` 类实现 `ISkillRegistry` 接口。
- F-089: packages/agent/src/skills/skill-registry.ts:34-53 — `registerSkill()` 返回 DisposableDelegate，支持注册/注销。
- F-090: packages/agent/src/skills/skill-registry.ts:59-78 — `listSkills()` 返回按名称排序的技能摘要，支持大小写不敏感的查询过滤。
- F-091: packages/agent/src/skills/skill-registry.ts:118-122 — 重复技能名注册时打印警告并跳过，不覆盖已有技能。
- F-092: packages/agent/src/agent.ts:1272-1289 — 系统提示中自动注入技能列表快照，指导代理使用 `load_skill` 和 `discover_skills` 工具。

## 设置模型（Settings Model）

- F-093: packages/agent/src/tokens.ts:327-334 — `IProviderParameters` 定义模型参数：temperature、maxOutputTokens、maxTurns、contextWindow 等。
- F-094: packages/agent/src/tokens.ts:336-347 — `IProviderConfig` 定义单个提供商配置：id、name、provider、model、apiKey、baseURL、headers、parameters 等。
- F-095: packages/agent/src/tokens.ts:349-377 — `IAIConfig` 定义全局 AI 配置：useSecretsManager、providers、defaultProvider、systemPrompt、toolsEnabled、skillsPaths 等。
- F-096: packages/agent/src/tokens.ts:365-366 — 支持 `commandsRequiringApproval`（需审批命令列表）和 `commandsAutoRenderMimeBundles`（自动渲染 MIME 的命令列表）。
- F-097: packages/agent/src/tokens.ts:743 — 密钥命名空间为 `@jupyternaut/agent:providers`。
- F-098: packages/agent/src/tokens.ts:744 — 密钥在设置中替换为 `***`。

## 密钥管理

- F-099: packages/agent/src/agent.ts:21 — 依赖 `ISecretsManager`（来自 jupyter-secrets-manager）。
- F-100: packages/agent/src/agent.ts:137-139 — 当 token 为空时禁用密钥管理器。
- F-101: packages/agent/src/agent.ts:1228-1248 — API Key 优先从 SecretsManager 获取（命名空间 `${provider}:apiKey`），否则从设置文件获取。
- F-102: packages/agent/src/agent.ts:1554-1560 — 使用模块级闭包变量存储 secretsToken，通过 setToken/getToken 访问。

## Persona（角色）系统

- F-103: packages/persona/src/persona.ts:167 — `Persona` 类实现 `IPersona` 接口，连接 IAgentManager 和 IChatModel。
- F-104: packages/persona/src/persona.ts:162-166 — Persona 在聊天 widget 打开期间保持存活，保留跨多轮 @提及的对话历史。
- F-105: packages/persona/src/persona.ts:585 — `requireMention` 属性默认为 true，控制是否需要 @提及才触发响应。
- F-106: packages/persona/src/persona.ts:217-234 — `_onMessagesUpdated()` 监听新消息，过滤已回复消息和 bot 消息，处理 @提及。
- F-107: packages/persona/src/persona.ts:249-257 — `_respond()` 处理附件，根据模型能力（图片/PDF/音频）调用 `processAttachments()`。
- F-108: packages/persona/src/persona.ts:287-326 — `_rebuildHistory()` 在模型切换时重建历史，重新处理附件。
- F-109: packages/persona/src/persona.ts:38-44 — 工具执行状态：`pending`、`awaiting_approval`、`approved`、`rejected`、`completed`、`error`。
- F-110: packages/persona/src/persona.ts:57-81 — `extractToolSummary()` 根据工具类型提取摘要（命令 ID、搜索查询、技能名称、URL）。
- F-111: packages/persona/src/persona.ts:134-157 — `extractMimeBundles()` 从工具输出中提取 MIME bundle，用于富输出渲染。

## 聊天模型（AIChatModel）

- F-112: packages/ai/src/chat-model.ts:46 — `AIChatModel` 继承 `AbstractChatModel`，实现 `IAIChatModel` 接口。
- F-113: packages/ai/src/chat-model.ts:72 — 使用 3000ms 防抖的 `Debouncer` 实现自动保存。
- F-114: packages/ai/src/chat-model.ts:483-512 — `save()` 方法将聊天序列化为 JSON 文件（`.chat` 扩展名）保存到 Contents Manager。
- F-115: packages/ai/src/chat-model.ts:520-573 — `restore()` 方法从 JSON 文件恢复聊天，包括消息、用户、附件和提供商信息。
- F-116: packages/ai/src/chat-model.ts:578-595 — `requestTitle()` 方法使用 AI 自动生成聊天标题（不超过 10 词的名词短语）。
- F-117: packages/ai/src/chat-model.ts:338-346 — Persona 忙碌时消息进入队列，通过 MIME 组件显示排队状态。
- F-118: packages/ai/src/chat-model.ts:600-657 — 序列化时使用 attachmentMap 去重附件，减少存储体积。

## 消息净化与历史管理

- F-119: packages/agent/src/agent.ts:1446-1549 — `sanitizeModelMessages()` 确保消息序列完整性：tool-call 必须有对应 tool-result，tool-approval-request 必须有对应 response。
- F-120: packages/agent/src/agent.ts:1495-1498 — 使用 JSON 序列化往返确保消息可序列化，不可序列化消息被丢弃。
- F-121: packages/agent/src/agent.ts:502-516 — `clearHistory()` 停止流式响应、清空历史、重置 token 使用量。
- F-122: packages/agent/src/agent.ts:522-525 — `setHistory()` 允许从预构建消息设置历史，经过 sanitize 处理。

## 流式响应与中断

- F-123: packages/agent/src/agent.ts:586 — 使用 `AbortController` 控制流式请求中断。
- F-124: packages/agent/src/agent.ts:531-543 — `stopStreaming()` 中止请求并拒绝所有待处理审批。
- F-125: packages/agent/src/agent.ts:360 — 使用 `PromiseDelegate<void>` 跟踪流式状态。
- F-126: packages/agent/src/agent.ts:608-657 — 主循环持续调用 agent.stream()，直到审批处理完成或流结束。

## 工具审批机制

- F-127: packages/agent/src/agent.ts:1130-1158 — `_handleApprovalRequest()` 发射审批请求事件，等待用户响应后注入 tool-approval-response 消息。
- F-128: packages/agent/src/agent.ts:1165-1173 — `_waitForApproval()` 返回 Promise，通过 Map 存储待审批项的 resolve 回调。
- F-129: packages/agent/src/agent.ts:550-560 — `approveToolCall()` 和 `rejectToolCall()` 分别批准/拒绝工具调用。
- F-130: packages/agent/src/agent.ts:1351-1354 — `_pendingApprovals` 使用 Map 存储待审批项，键为 toolCallId。

## Token 使用量追踪

- F-131: packages/agent/src/tokens.ts:717-738 — `ITokenUsage` 接口跟踪 inputTokens、outputTokens、lastRequestInputTokens、contextWindow。
- F-132: packages/agent/src/agent.ts:722-739 — `_updateTokenUsage()` 累积 token 计数并更新上下文窗口大小。
- F-133: packages/agent/src/agent.ts:428-430 — 切换提供商时重置 `lastRequestInputTokens`。

## 错误处理

- F-134: packages/agent/src/agent.ts:661-690 — 捕获非 AbortError 异常，对 400/404/413/415/422 等状态码自动剥离附件重试。
- F-135: packages/agent/src/agent.ts:674-680 — API 错误时自动从历史中剥离图片/文件附件，提示用户重新发送。
- F-136: packages/agent/src/agent.ts:744-760 — `_stripAttachments()` 从用户消息中移除非文本内容部分，替换为占位文本。

## Provider Cache Options

- F-137: packages/agent/src/agent.ts:1364-1383 — `mergeProviderOptions()` 按提供商 key 合并选项，保留提供商特定字段。
- F-138: packages/agent/src/agent.ts:1388-1409 — `addCacheProviderOptionsToTools()` 为运行时工具定义注入缓存选项。
- F-139: packages/agent/src/agent.ts:1414-1434 — `addCacheProviderOptionsToMessages()` 为最后一条消息注入缓存选项（用于 prompt caching）。

## 系统提示增强

- F-140: packages/agent/src/agent.ts:1266-1312 — `_getEnhancedSystemPrompt()` 在基础提示上追加技能列表和 Web 检索策略。
- F-141: packages/agent/src/agent.ts:1296-1309 — Web 检索策略定义了 browser_fetch → web_fetch → web_search 的降级链。
- F-142: packages/agent/src/agent.ts:926-933 — 富输出渲染指令告诉代理支持的 MIME 类型列表和渲染行为。
- F-143: packages/agent/src/agent.ts:1317-1329 — `_getSupportedMimeTypesInstruction()` 从 IRenderMimeRegistry 获取安全 MIME 类型列表。

## Web 检索策略

- F-144: packages/agent/src/agent.ts:1299-1300 — 用户询问特定 URL 时优先使用 browser_fetch。
- F-145: packages/agent/src/agent.ts:1301 — browser_fetch 因 CORS/网络失败时尝试 web_fetch。
- F-146: packages/agent/src/agent.ts:1302-1303 — web_fetch 因访问策略失败时必须回退到 browser_fetch 再搜索。
- F-147: packages/agent/src/agent.ts:1304 — 两种 fetch 方法都失败后才回退到 web_search。

## ESLint/代码规范

- F-148: package.json:76-88 — Interface 必须以 `I` 前缀开头（PascalCase + `^I[A-Z]` 正则）。
- F-149: package.json:104-110 — 使用单引号、强制大括号、严格相等、箭头函数优先。
- F-150: package.json:118-136 — 禁止从 `@mui/icons-material` 顶层导入图标，禁止 MUI 三级导入。
- F-151: package.json:155 — CSS 类名使用 kebab-case 模式，允许 Mui 前缀的 Material-UI 类名。
