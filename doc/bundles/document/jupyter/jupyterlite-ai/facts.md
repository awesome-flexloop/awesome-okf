---
type: Facts
okf_version: '0.2'
title: jupyterlite-ai 源码事实清单
generated: '2026-08-22'
tags:
- jupyter
- jupyterlite
- ai
- llm
sources:
- ../../../../../external/libs/jupyter/ai/package.json
- ../../../../../external/libs/jupyter/ai/pyproject.toml
- ../../../../../external/libs/jupyter/ai/python/jupyterlite-ai/pyproject.toml
- ../../../../../external/libs/jupyter/ai/python/jupyternaut-persona/pyproject.toml
- ../../../../../external/libs/jupyter/ai/packages/agent/src/index.ts
- ../../../../../external/libs/jupyter/ai/packages/agent/src/tokens.ts
- ../../../../../external/libs/jupyter/ai/packages/agent/src/providers/provider-registry.ts
- ../../../../../external/libs/jupyter/ai/packages/agent/src/providers/built-in-providers.ts
- ../../../../../external/libs/jupyter/ai/packages/agent/src/tools/tool-registry.ts
- ../../../../../external/libs/jupyter/ai/packages/agent/src/agent.ts
- ../../../../../external/libs/jupyter/ai/packages/agent/src/skills/skill-registry.ts
- ../../../../../external/libs/jupyter/ai/packages/ai/src/chat-model.ts
- ../../../../../external/libs/jupyter/ai/packages/persona/src/persona.ts
- ../../../../../external/libs/jupyter/ai/packages/persona/src/completion/completion-provider.ts
- ../../../../../external/libs/jupyter/ai/packages/ai/src/index.ts
- ../../../../../external/libs/jupyter/ai/packages/persona/src/index.ts
---

# jupyterlite-ai 源码事实清单

## 项目结构与元数据

- F-001: package.json:2 — 项目名称为 `jupyterlite-ai`，使用 yarn workspaces 管理 monorepo
- F-002: package.json:3-6 — workspaces 包含 `packages/*` 目录，所有前端包集中在 packages/ 下
- F-003: package.json:8-19 — 定义了 build、build:prod、clean、lint、lint:check、prettier、prettier:check、test、test:chrome、test:firefox 等脚本命令
- F-004: package.json:21-63 — devDependencies 包含 @jupyterlab/* 4.4.x 系列包、yjs、zustand、typescript、eslint、prettier 等开发依赖
- F-005: pyproject.toml:1-41 — 根目录 pyproject.toml 使用 hatchling 构建系统，name 为 `jupyterlite-ai`
- F-006: pyproject.toml:5 — 根 Python 包 requires-python 为 `>=3.8`
- F-007: pyproject.toml:8 — jupyter-releaser 配置 skip 包含 `check-links`，branches 为 `main`

## Python 包：jupyterlite-ai（Chat UI 扩展）

- F-008: python/jupyterlite-ai/pyproject.toml:6 — Python 包名为 `jupyterlite_ai`，描述为 "A serverless AI code completions and chat"
- F-009: python/jupyterlite-ai/pyproject.toml:9 — requires-python 为 `>=3.10`
- F-010: python/jupyterlite-ai/pyproject.toml:30-34 — 核心依赖为 `jupyter-chat-components >=0.6.0,<0.7`、`jupyter-secrets-manager >=0.5,<0.6`、`jupyterlab-ai-commands >=0.3.1,<0.4`
- F-011: python/jupyterlite-ai/pyproject.toml:46-50 — jupyter 可选依赖包含 `jupyterlab>=4.5.0`、`jupyterlite>=0.6.0`、`notebook>=7.5.0`
- F-012: python/jupyterlite-ai/pyproject.toml:66-68 — wheel 构建将 labextension 安装到 `share/jupyter/labextensions/@jupyterlite/ai`
- F-013: python/jupyterlite-ai/pyproject.toml:70-77 — 使用 hatch-jupyter-builder 钩子，build_cmd 为 `build:prod`，npm 命令为 `jlpm`
- F-014: python/jupyterlite-ai/pyproject.toml:82 — build-kwargs 的 path 为 `../..`（即 monorepo 根目录）

## Python 包：jupyternaut-persona（Agent 运行时扩展）

- F-015: python/jupyternaut-persona/pyproject.toml:6 — Python 包名为 `jupyternaut_persona`
- F-016: python/jupyternaut-persona/pyproject.toml:30-35 — 核心依赖在 jupyterlite_ai 基础上额外包含 `jupyter-mcp-manager >=0.2.0, <0.3`
- F-017: python/jupyternaut-persona/pyproject.toml:67-69 — wheel 构建将 labextension 安装到 `share/jupyter/labextensions/@jupyternaut/persona`

## 前端包：@jupyternaut/agent（核心 Agent 引擎）

- F-018: packages/agent/src/index.ts:1-16 — agent 包导出 agent、icons、tokens、providers（含 built-in providers/model info/models/provider registry/provider tools）、tools（commands/skills/tool-registry/web）、skills（parse-skill/skill-loader/skill-registry/types）等模块
- F-019: packages/agent/src/tokens.ts:82-85 — IToolRegistry Token 标识符为 `@jupyternaut/agent:IToolRegistry`，描述为 "Tool registry for AI agent functionality"
- F-020: packages/agent/src/tokens.ts:125-128 — ISkillRegistry Token 标识符为 `@jupyternaut/agent:ISkillRegistry`
- F-021: packages/agent/src/tokens.ts:320-323 — IProviderRegistry Token 标识符为 `@jupyternaut/agent:IProviderRegistry`
- F-022: packages/agent/src/tokens.ts:406-408 — IAISettingsModel Token 标识符为 `@jupyternaut/agent:IAISettingsModel`
- F-023: packages/agent/src/tokens.ts:603-605 — IAgentManager Token 标识符为 `@jupyternaut/agent:IAgentManager`
- F-024: packages/agent/src/tokens.ts:743 — SECRETS_NAMESPACE 常量值为 `@jupyternaut/agent:providers`，用于 secrets manager 的命名空间
- F-025: packages/agent/src/tokens.ts:744 — SECRETS_REPLACEMENT 常量值为 `***`，用于在设置中替换密钥显示
- F-026: packages/agent/src/tokens.ts:349-377 — IAIConfig 接口定义了 useSecretsManager、providers、defaultProvider、activeCompleterProvider、useSameProviderForChatAndCompleter、contextAwareness、codeExecution、systemPrompt、completionSystemPrompt、toolsEnabled、commandsRequiringApproval、commandsAutoRenderMimeBundles、trustedMimeTypesForAutoRender、showCellDiff、showFileDiff、diffDisplayMode、skillsPaths 等配置字段
- F-027: packages/agent/src/tokens.ts:204-272 — IProviderInfo 接口定义了 id、name、apiKeyRequirement（required/optional/none 三态）、defaultModels、modelInfo、supportsBaseURL、supportsHeaders、supportsToolCalling、description、baseUrls、providerToolCapabilities、cacheProviderOptions、factory 等字段
- F-028: packages/agent/src/tokens.ts:142 — IProviderWebSearchImplementation 类型仅支持 `'openai' | 'anthropic'` 两种内置实现
- F-029: packages/agent/src/tokens.ts:717-738 — ITokenUsage 接口定义了 inputTokens、outputTokens、lastRequestInputTokens、contextWindow 四个字段

## LLM Provider 注册系统

- F-030: packages/agent/src/providers/provider-registry.ts:10-89 — ProviderRegistry 类实现了 registerProvider（防重复注册，重复则抛异常）、getProviderInfo、createChatModel、createCompletionModel、getAvailableProviders 等方法，使用 Lumino Signal 机制通知 provider 变更
- F-031: packages/agent/src/providers/built-in-providers.ts:14-59 — Anthropic provider（id: 'anthropic'），支持 ephemeral 缓存（cacheControl: { type: 'ephemeral' }），内置 webSearch 和 webFetch 能力，factory 使用 `@ai-sdk/anthropic` 的 createAnthropic，需设置 `anthropic-dangerous-direct-browser-access: 'true'` header
- F-032: packages/agent/src/providers/built-in-providers.ts:64-98 — Google Generative AI provider（id: 'google'），默认模型为 gemini-2.5-flash，使用 `@ai-sdk/google` 的 createGoogleGenerativeAI
- F-033: packages/agent/src/providers/built-in-providers.ts:103-135 — Mistral provider（id: 'mistral'），默认模型为 mistral-large-latest，使用 `@ai-sdk/mistral` 的 createMistral
- F-034: packages/agent/src/providers/built-in-providers.ts:140-210 — OpenAI provider（id: 'openai'），内置 webSearch 能力（implementation: 'openai'），默认模型为 gpt-4o，使用 `@ai-sdk/openai` 的 createOpenAI
- F-035: packages/agent/src/providers/built-in-providers.ts:215-244 — Generic provider（id: 'generic'），apiKeyRequirement 为 'optional'，基于 `@ai-sdk/openai-compatible`，预置 localhost:4000（LiteLLM）和 localhost:11434/v1（Ollama）两个 base URL 建议

## Tool 注册系统

- F-036: packages/agent/src/tools/tool-registry.ts:8-64 — ToolRegistry 类提供 add/get/remove 三个方法管理工具注册，tools getter 返回副本防止外部修改，使用 Lumino Signal 通知变更
- F-037: packages/agent/src/tokens.ts:46-77 — IToolRegistry 接口定义了 tools（只读 Record）、namedTools（INamedTool[]）、toolsChanged Signal、add/get/remove 方法
- F-038: packages/agent/src/agent.ts:948-950 — execute_command 工具配置了专门的审批策略 `createExecuteCommandApprovalPolicy(this._settingsModel)`，其他工具默认不需要审批

## Skill 注册系统

- F-039: packages/agent/src/skills/skill-registry.ts:23-137 — SkillRegistry 类实现了 registerSkill（返回 DisposableDelegate 支持注销）、listSkills（支持 query 过滤，按名称排序）、getSkill、getSkillResource 方法
- F-040: packages/agent/src/skills/skill-registry.ts:115-132 — 内部 _registerSkillInternal 方法检测重复 skill 名称，重复时输出警告并跳过注册，使用 registrationId 防止注销误删
- F-041: packages/agent/src/skills/skill-registry.ts:72-77 — listSkills 的 query 过滤为大小写不敏感匹配，同时匹配 name 和 description 字段
- F-042: packages/agent/src/tokens.ts:92-120 — ISkillRegistry 接口定义了 skillsChanged Signal、registerSkill、listSkills、getSkill、getSkillResource 四个方法

## Agent 引擎核心：AgentManager

- F-043: packages/agent/src/agent.ts:312-313 — 默认配置常量：DEFAULT_TEMPERATURE = 0.7，DEFAULT_MAX_TURNS = 25
- F-044: packages/agent/src/agent.ts:109-307 — AgentManagerFactory 类管理全局 Agent 生命周期，负责 MCP 客户端初始化、settings 变更监听、MCP servers 变更监听、skill 变更刷新
- F-045: packages/agent/src/agent.ts:219-267 — _initializeMCPClients 方法仅连接 type 为 'http' 的 MCP server，使用 @ai-sdk/mcp 的 createMCPClient，fetch 绑定到 globalThis.fetch 避免浏览器 Illegal invocation 错误
- F-046: packages/agent/src/agent.ts:335-1356 — AgentManager 类实现了完整的 Agent 执行循环，包括模型创建、工具管理、流式响应处理、审批机制、token 统计、历史管理
- F-047: packages/agent/src/agent.ts:935-951 — Agent 使用 Vercel AI SDK 的 ToolLoopAgent 构建，配置了 prepareStep 钩子注入 cache provider options，stopWhen 使用 isStepCount(maxTurns) 控制最大轮次，toolApproval 仅对 execute_command 启用审批
- F-048: packages/agent/src/agent.ts:584-695 — generateResponse 方法实现多轮 tool-loop：在 while 循环中调用 agent.stream，处理文本增量、工具调用、工具结果、审批请求等流式事件，遇到审批时中断循环等待用户响应
- F-049: packages/agent/src/agent.ts:960-1057 — _processStreamResult 方法处理流式结果，分 case 处理 text-delta、tool-call、tool-result、tool-error、tool-output-denied、tool-approval-request、error、finish-step、abort 等事件类型
- F-050: packages/agent/src/agent.ts:1266-1312 — _getEnhancedSystemPrompt 方法动态增强系统提示词：注入 skills 快照（AGENT SKILLS 段）和 Web 检索策略（WEB RETRIEVAL POLICY 段，定义 browser_fetch → web_fetch → web_search 的降级链）
- F-051: packages/agent/src/agent.ts:1317-1329 — _getSupportedMimeTypesInstruction 方法从 IRenderMimeRegistry 获取当前会话支持的 MIME 类型列表，仅包含 factory.safe 为 true 的安全类型
- F-052: packages/agent/src/agent.ts:666-680 — API 错误处理：当遇到 400/404/413/415/422 状态码时，自动从历史中剥离附件内容并提示用户重新发送
- F-053: packages/agent/src/agent.ts:1446-1549 — sanitizeModelMessages 函数清理消息历史：确保 tool-call 与 tool-result 配对、tool-approval-request 与 tool-approval-response 配对，通过 JSON round-trip 丢弃不可序列化的消息
- F-054: packages/agent/src/agent.ts:779-793 — initializeAgent 使用 _initQueue Promise 链确保初始化串行化，防止并发初始化冲突
- F-055: packages/agent/src/agent.ts:809-868 — _prepareAgentConfig 方法构建运行时配置：根据 provider 支持情况和 settings 决定是否启用工具，合并 function tools、MCP tools、provider tools
- F-056: packages/agent/src/agent.ts:1227-1258 — API key 获取支持两种模式：secrets manager（通过 SECRETS_NAMESPACE 和 `${provider}:apiKey` 路径）和直接从 settings 获取，token 为空时自动禁用 secrets manager

## Chat 模型层：AIChatModel

- F-057: packages/ai/src/chat-model.ts:46-722 — AIChatModel 继承 @jupyter/chat 的 AbstractChatModel，实现了 AI 聊天模型的核心功能
- F-058: packages/ai/src/chat-model.ts:72 — 使用 Debouncer（3000ms 延迟）实现自动保存
- F-059: packages/ai/src/chat-model.ts:74-94 — 监听 personaRegistry.personaAdded 信号，当 persona 绑定到当前 model 时建立 agentManager 关联，requireMention 设为 false（即响应所有消息）
- F-060: packages/ai/src/chat-model.ts:103-115 — 设置 chat name 时，如果 messages 为空则自动尝试从备份目录恢复（`<chatBackupDirectory>/<name>.chat`）
- F-061: packages/ai/src/chat-model.ts:295-350 — sendMessage 方法：空消息检查（body/mime_model/attachments 均空且非 bot 消息时返回 null）、配置有效性检查、busy 状态时消息入队等待
- F-062: packages/ai/src/chat-model.ts:356-376 — _onPersonaBusyChanged：persona 从 busy 变为 free 时，自动排空消息队列，并在消息数≤5或无标题时自动请求生成标题
- F-063: packages/ai/src/chat-model.ts:399-431 — _updateQueueUI 使用 MIME type `application/vnd.jupyter.chat.components: 'message-queue'` 渲染消息队列 UI 组件
- F-064: packages/ai/src/chat-model.ts:483-512 — save 方法将聊天序列化为 JSON 文件（.chat 扩展名），支持自动创建备份目录
- F-065: packages/ai/src/chat-model.ts:520-573 — restore 方法从 .chat 文件恢复：解析 JSON、恢复 provider 选择、重建消息列表（含附件去重索引）、重建 agent 历史
- F-066: packages/ai/src/chat-model.ts:578-595 — requestTitle 方法使用 textResponse 向 LLM 发送系统提示词，要求生成不超过10个词的名词短语标题，聚焦主题而非动作
- F-067: packages/ai/src/chat-model.ts:600-657 — _serializeModel 将聊天状态序列化为 ExportedChat 格式，使用 attachmentMap 对附件去重（JSON 字符串作为 key），避免重复存储

## Persona 层：对话参与者桥接

- F-068: packages/persona/src/persona.ts:167-599 — Persona 类桥接 IAgentManager 和 IChatModel，监控 chat model 的新消息并在被提及时响应，保持对话历史跨多次提及
- F-069: packages/persona/src/persona.ts:585 — requireMention 默认为 true，即默认需要 @mention 才触发响应
- F-070: packages/persona/src/persona.ts:217-234 — _onMessagesUpdated 过滤未处理的非 bot 消息：requireMention 为 true 时仅响应包含 persona mention 的消息
- F-071: packages/persona/src/persona.ts:236-266 — _respond 方法：设置 busy 状态、处理附件（根据模型能力决定是否包含图片/PDF/音频）、调用 agent.generateResponse
- F-072: packages/persona/src/persona.ts:287-326 — _rebuildHistory 方法遍历 chat 消息，将非 AI 消息的附件重新处理（基于当前模型的多模态能力），构建 ModelMessage[] 调用 agent.setHistory
- F-073: packages/persona/src/persona.ts:328-358 — _onAgentEvent 处理所有 agent 事件类型：message_start/chunk/complete、tool_call_start/complete、tool_approval_request/resolved、error
- F-074: packages/persona/src/persona.ts:395-443 — 工具调用显示：使用 `application/vnd.jupyter.chat.components: 'grouped-tool-calls'` MIME 类型渲染工具调用状态，包含 toolCallId、title、kind、status、rawInput
- F-075: packages/persona/src/persona.ts:456-470 — execute_command 工具完成后，如果 output 包含 MIME bundles 且命令在 commandsAutoRenderMimeBundles 白名单中，自动渲染可信 MIME 类型的输出
- F-076: packages/persona/src/persona.ts:57-81 — extractToolSummary 函数为不同工具生成摘要：execute_command 显示 commandId，discover_commands/skills/web_search 显示 query，load_skill 显示 skill 名和资源名，browser_fetch/web_fetch 显示 URL

## AI 代码补全：AICompletionProvider

- F-077: packages/persona/src/completion/completion-provider.ts:40 — DEFAULT_COMPLETION_TEMPERATURE = 0.3（低于聊天的 0.7，更确定性）
- F-078: packages/persona/src/completion/completion-provider.ts:45-313 — AICompletionProvider 实现 JupyterLab IInlineCompletionProvider 接口，identifier 为 `@jupyternaut/persona:completer`
- F-079: packages/persona/src/completion/completion-provider.ts:88-155 — fetch 方法：支持 Fill-In-Middle（FIM）模式（`<PRE>...<SUF>...<MID>` 格式），Notebook 上下文提取（上方/下方单元格），清理 FIM 标签和代码块标记
- F-080: packages/persona/src/completion/completion-provider.ts:213-286 — _extractNotebookContext 方法提取 Notebook 上下文：收集当前单元格上方的代码单元格作为 codeBeforeCursor，下方的作为 codeAfterCursor，带 Cell N 编号标注
- F-081: packages/persona/src/completion/completion-provider.ts:121-123 — FIM 仅在 provider 支持 supportsFillInMiddle 且 suffix 有内容时启用

## MCP（Model Context Protocol）集成

- F-082: packages/agent/src/agent.ts:1 — 使用 `@ai-sdk/mcp` 的 createMCPClient 连接 MCP 服务器
- F-083: packages/agent/src/agent.ts:20 — 依赖 `jupyter-mcp-manager` 的 IMcpManager 接口管理 MCP 服务器配置
- F-084: packages/agent/src/agent.ts:239-247 — MCP HTTP transport 使用 `globalThis.fetch.bind(globalThis)` 绑定 fetch，防止浏览器中 unbound window.fetch 抛出 Illegal invocation
- F-085: packages/agent/src/agent.ts:153-164 — 新建 chat 时若 MCP 尚未初始化完成，通过 _initQueue 链等待 MCP 工具就绪后再传递给 agent

## Secrets Manager 集成

- F-086: packages/agent/src/tokens.ts:7 — 依赖 `jupyter-secrets-manager` 的 ISecretsManager 接口安全存储 API key
- F-087: packages/agent/src/agent.ts:137-139 — 当 token 为空时，自动禁用 secrets manager 功能
- F-088: packages/agent/src/agent.ts:1238-1244 — secrets manager 中 API key 的存储路径为 `SECRETS_NAMESPACE / ${provider}:apiKey`

## 前端包：@jupyterlite/ai（Chat UI 入口）

- F-089: packages/ai/src/index.ts — 定义了 chatCommandRegistryPlugin、clearCommandPlugin、skillsCommandPlugin 等 JupyterLab 插件，注册聊天命令、清除命令、技能命令
- F-090: packages/ai/src/index.ts — chatModelHandler 插件负责创建和管理 AIChatModel 实例
- F-091: packages/ai/src/index.ts — chatTracker 插件跟踪聊天面板生命周期
- F-092: packages/ai/src/index.ts — toolbarFactory 插件创建聊天工具栏按钮和控件

## 前端包：@jupyternaut/persona（Persona UI 与设置）

- F-093: packages/persona/src/index.ts — 定义了 providerRegistryPlugin（注册所有内置 LLM provider）、anthropicProviderPlugin、googleProviderPlugin 等插件
- F-094: packages/persona/src/index.ts — personaRegistry 管理 Persona 实例的创建和生命周期
- F-095: packages/persona/src/index.ts — settingsPanelPlugin 创建设置面板 UI，用于配置 API key、模型选择、工具开关等
- F-096: packages/persona/src/index.ts — diffManager 管理 cell/file diff 显示，支持 split 和 unified 两种模式
