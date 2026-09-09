---
type: reference
title: LobsterAI 源码事实清单（R 阶段，基线 2026.9.4）
description: 按子系统组织的 LobsterAI 编号事实清单，全部陈述直接来自 vendor 源码阅读，证据位置逐条标注。
tags: [lobsterai, electron, ai-agent, facts, r-phase]
sources:
  - id: lobsterai-vendor
    resource: vendor/netease-youdao/LobsterAI
    title: LobsterAI 源码（固定基线 2026.9.4 @ 7592cd0）
---

# LobsterAI 源码事实清单（R 阶段）

> 本文档为 OKF Wiki R 阶段产物：仅登记可直接从源码读出的事实，不含概念解释与示例（属 E 阶段）。
> 所有数量陈述的计数方法在对应条目或「计数方法说明」中给出。

## 计数方法说明

- 内置技能数量：对 `SKILLs/*/SKILL.md` 执行 Glob 模式匹配计数，结果为 29 个；与 `SKILLs/skills.config.json` 中 `defaults` 条目数（29）一致。README 中"28 built-in skills"为过期声明（见 F-la-007）。
- 数据库表数量：逐条统计 `src/main/sqliteStore.ts` 中 `CREATE TABLE IF NOT EXISTS` 语句，结果为 13 张（见 F-la-016）。
- Redux slice 数量：对 `src/renderer/store/slices/*.ts` 执行 Glob 计数，结果为 21 个 `.ts`（13 个 slice 实现 + 8 个并置测试，见 F-la-042）。
- 测试文件数量：对 `tests/` 目录执行 LS 计数，结果为 38 个文件（含子目录内文件，见 F-la-073）。
- skins 测试数量：对 `src/main/skins/*.test.ts` 执行 Glob 计数，结果为 8 个（见 F-la-074）。

## 项目基线

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-la-001 | package.json 中 `name` 为 `lobsterai`，`version` 为 `2026.9.4`。 | vendor/netease-youdao/LobsterAI/package.json |
| F-la-002 | package.json `engines` 声明 Node.js 版本范围 `>=24.15.0 <25`。 | vendor/netease-youdao/LobsterAI/package.json（engines 字段） |
| F-la-003 | devDependencies 含 `electron` 版本 `40.2.1`；README 声明技术栈为 Electron 40 + React 18。 | vendor/netease-youdao/LobsterAI/package.json；README.md |
| F-la-004 | dependencies 含 `better-sqlite3` ^12.8.0、`@modelcontextprotocol/sdk` ^1.27.1、`@reduxjs/toolkit`、`nim-web-sdk-ng` 10.9.77-alpha.4、`zod` ^4.3.6。 | vendor/netease-youdao/LobsterAI/package.json（dependencies 字段） |
| F-la-005 | scripts 含 `electron:dev`（端口 5175）、`test`（值为 `vitest run`）、`dist:*` 系列打包脚本。 | vendor/netease-youdao/LobsterAI/package.json（scripts 字段） |
| F-la-006 | package.json `openclaw.plugins` 列出 10 个插件（逐条计数），每条含 `id`/`npm`/`version` 字段：dingtalk-connector、openclaw-lark、qqbot、discord、wecom-openclaw-plugin、openclaw-weixin、moltbot-popo、openclaw-nim-channel、openclaw-netease-bee、clawemail-email；其中 moltbot-popo 与 openclaw-nim-channel 带 `"optional": true`，moltbot-popo 带自定义 registry（`https://npm.nie.netease.com`），openclaw-nim-channel 的 `npm` 值为 git+https 形式。 | vendor/netease-youdao/LobsterAI/package.json（openclaw.plugins 字段） |
| F-la-007 | README 声称"28 built-in skills"；对 `SKILLs/*/SKILL.md` 的 Glob 实测为 29 个，README 该声明为过期声明。 | vendor/netease-youdao/LobsterAI/README.md；SKILLs/ 目录（Glob 计数） |
| F-la-008 | 项目内 AGENTS.md 声明架构分工：Cowork 为产品/会话层，OpenClaw 为唯一 Agent 运行时/网关；并规定 IPC 通道常量规范（`as const` 常量对象）与日志、i18n 规范。 | vendor/netease-youdao/LobsterAI/AGENTS.md |
| F-la-009 | README 声明依赖版本 openclaw v2026.6.1、dsh 0.1.1-rc.1。 | vendor/netease-youdao/LobsterAI/README.md |

## 主进程（src/main/）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-la-010 | 主窗口在 main.ts 约 13470 行以 `new BrowserWindow` 创建；Windows 下 `frame: false`、`titleBarStyle: 'hidden'`，macOS 下 `titleBarStyle: 'hiddenInset'` 且 `trafficLightPosition: { x: 12, y: 20 }`。 | vendor/netease-youdao/LobsterAI/src/main/main.ts（mainWindow 创建段） |
| F-la-011 | 主窗口 `webPreferences`：`nodeIntegration: false`、`contextIsolation: true`、`sandbox: true`、`webSecurity: true`、`preload: PRELOAD_PATH`、`backgroundThrottling: false`、`webviewTag: true`、`enableWebSQL: false`、`autoplayPolicy: 'document-user-activation-required'`、`disableDialogs: true`、`navigateOnDragDrop: false`。 | vendor/netease-youdao/LobsterAI/src/main/main.ts（mainWindow.webPreferences） |
| F-la-012 | 主窗口 `backgroundColor` 按主题取 `'#0F1117'`（dark）或 `'#F8F9FB'`（light），`show: false`、`autoHideMenuBar: true`；最小宽高为 `MIN_APP_WINDOW_WIDTH`/`MIN_APP_WINDOW_HEIGHT` 常量。 | vendor/netease-youdao/LobsterAI/src/main/main.ts |
| F-la-013 | `webContents.on('will-attach-webview')` 处理器强制重写 webview 的 `webPreferences`：`nodeIntegration=false`、`sandbox=true`、`contextIsolation=true`、`webSecurity=true`、`plugins=false`、`devTools=isDev`、`partition=ArtifactBrowserPartition.Default`、`preload=BROWSER_ANNOTATION_PRELOAD_PATH`。 | vendor/netease-youdao/LobsterAI/src/main/main.ts（will-attach-webview 处理器） |
| F-la-014 | 开发模式 `mainWindow.loadURL(DEV_SERVER_URL)`，加载失败回退 `resources/error.html`；生产模式 `mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))`。 | vendor/netease-youdao/LobsterAI/src/main/main.ts（loadURL/loadFile 调用段） |
| F-la-015 | `SqliteStore` 类提供 `static async create(userDataPath?)` 工厂方法；数据库迁移通过 `PRAGMA table_info()` 做 ad-hoc 列存在性检查（如 `messages_persisted` 列）。 | vendor/netease-youdao/LobsterAI/src/main/sqliteStore.ts（SqliteStore.create；迁移代码段） |
| F-la-016 | sqliteStore 创建 13 张表：`kv`、`cowork_sessions`（含 `claude_session_id`、`scheduled_task_id`、`fork_*` 列）、`cowork_messages`、`cowork_session_capsules`、`cowork_config`、`user_memories`、`user_memory_sources`、`agents`、`mcp_servers`、`mcp_launch_resolutions`、`user_plugins`、`subagent_runs`、`subagent_messages`。 | vendor/netease-youdao/LobsterAI/src/main/sqliteStore.ts（CREATE TABLE 段，逐条计数） |
| F-la-017 | `cowork_messages` 外键关联会话表且 `ON DELETE CASCADE`，并建有 `idx_cowork_messages_session_id` 索引。 | vendor/netease-youdao/LobsterAI/src/main/sqliteStore.ts |
| F-la-018 | `agents` 表共 20 列，含 `skill_ids`（JSON 存储）、`source`、`preset_id` 列。 | vendor/netease-youdao/LobsterAI/src/main/sqliteStore.ts（agents 建表语句，列数计数） |
| F-la-019 | `CoworkStore` 会话方法：`createSession`、`getSession`、`forkSession`（含 `getSessionForkMetadata` 私有辅助）、`updateSession`、`deleteSession`、`deleteSessions`、`listSessions`、`searchSessions`、`countSessions`、`countSearchSessions`、`setSessionPinned`、`resetRunningSessions`、`listSessionIdsByAgent`。 | vendor/netease-youdao/LobsterAI/src/main/coworkStore.ts（CoworkStore 类方法签名） |
| F-la-020 | `CoworkStore` 消息方法：`addMessage`、`insertMessageBeforeId`、`deleteMessage`、`replaceConversationMessages`、`replaceSessionMessages`、`updateMessage`、`getPagedSessionMessages`、`getSessionSearchMessagePage`、`getRecentConversationMessages`、`getAllConversationMessages`、`getSessionMessageRailIndex`、`getMessageTimestamp`。 | vendor/netease-youdao/LobsterAI/src/main/coworkStore.ts（CoworkStore 类方法签名） |
| F-la-021 | `CoworkStore` 配置与记忆方法：`getConfig`、`setConfig`、`listUserMemories`、`createUserMemory`、`updateUserMemory`、`deleteUserMemory`、`getUserMemoryStats`、`autoDeleteNonPersonalMemories`、`markMemorySourcesInactiveBySession`、`markOrphanImplicitMemoriesStale`。 | vendor/netease-youdao/LobsterAI/src/main/coworkStore.ts（CoworkStore 类方法签名） |
| F-la-022 | `CoworkStore` 其他方法：`listRecentCwds`（默认 limit 8）、`listRecentSessionCwds`、`listSessionCwds`、`getAppLanguage`（返回 `'zh' \| 'en'`）、`conversationSearch`、`recentChats`、`getContinuityCapsule`、`upsertContinuityCapsule`、`deleteContinuityCapsules`、`countSessionMessages`。 | vendor/netease-youdao/LobsterAI/src/main/coworkStore.ts（CoworkStore 类方法签名） |
| F-la-023 | `AgentManager` 类方法 `listAgents`/`getAgent`/`getDefaultAgent`/`createAgent`/`updateAgent`/`reorderAgents`/`deleteAgent` 委托 CoworkStore；预设 agent 方法为 `getPresetAgents`、`getAllPresetAgents`、`addPresetAgent`。 | vendor/netease-youdao/LobsterAI/src/main/agentManager.ts（AgentManager 类） |
| F-la-024 | trayManager 导出 `createTray(getWindow)`、`updateTrayMenu`、`updateTrayReminder`、`destroyTray` 与 `TrayReminderState` 接口。 | vendor/netease-youdao/LobsterAI/src/main/trayManager.ts |
| F-la-025 | `NimGateway extends EventEmitter`，方法含 `start`/`stop`/`updateConfig`/`reconnectIfNeeded`、`sendText`/`sendLongText`/`sendMedia`/`sendReplyWithMedia`/`sendTeamReply`/`sendQChatReply`、`sendNotification`/`sendConversationNotification`、`cleanupMediaFiles`、`parseV2Attachment`、`handleIncomingMessage`。 | vendor/netease-youdao/LobsterAI/src/main/im/nimGateway.ts（类与方法签名） |
| F-la-026 | `nimQChatClient.ts` 导出接口 `QChatMessagePayload`、`QChatInboundMessage`、`QChatClientOptions`；`NimQChatClient` 类方法含 `setNim`、`normalizeMessage`、`parseMessage`、`initListeners`、`activate`、`discoverJoinedServers`、`subscribeServer`、`sendText`、`stop`。 | vendor/netease-youdao/LobsterAI/src/main/im/nimQChatClient.ts |
| F-la-027 | `qqMediaDownload.ts` 常量 `MAX_FILE_SIZE = 25MB`、`INBOUND_DIR = 'qq-inbound'`；`getQQMediaDir()` 返回 userData 下目录；`mapQQMediaType` 将 image/video/audio/voice 映射为 document；`downloadQQAttachment(url, type, fileName?)` 返回 `{localPath, fileSize, mimeType}` 或 `null`；`cleanupOldQQMediaFiles(maxAgeDays = 7)` 默认清理 7 天前文件。 | vendor/netease-youdao/LobsterAI/src/main/im/qqMediaDownload.ts |
| F-la-028 | `IMGatewayManager extends EventEmitter`，方法含 `initialize`、`setConfig`、`getStatus`、`getStatusWithOpenClawRuntime`、`testGateway`、`startGateway`、`stopGateway`、`startAllEnabled`、`stopAll`、`isConnected`，以及各平台 connectivity 测试方法（`testTelegramOpenClawConnectivity`/`testDiscordOpenClawConnectivity`/`testFeishuOpenClawConnectivity`/`testDingTalkOpenClawConnectivity`/`testWecomOpenClawConnectivity`/`testWeixinOpenClawConnectivity`/`testNimOpenClawConnectivity`/`testPopoOpenClawConnectivity`/`testQQOpenClawConnectivity` 等，Email 为 `testEmailConnectivity`）与 `weixinQrLoginStart`/`weixinQrLoginWait`、`popoQrLoginStart`/`popoQrLoginPoll`。 | vendor/netease-youdao/LobsterAI/src/main/im/imGatewayManager.ts（类与方法签名） |
| F-la-029 | `McpStore` 类提供 MCP 服务器 CRUD：`listServers`、`getServer`、`createServer`、`updateServer`、`deleteServer`、`setEnabled`、`getEnabledServers`，以及 launch resolution 读写；配套接口 `McpServerRecord`、`McpServerFormData`。 | vendor/netease-youdao/LobsterAI/src/main/mcp/mcpStore.ts |
| F-la-030 | `mcpLaunchResolution.ts` 导出常量对象 `McpLaunchResolverKind`、`McpLaunchResolutionStatus` 及接口 `McpLaunchResolution`；工具函数 `createMcpLaunchSourceFingerprint(server)`、`normalizeMcpCommand(command?)`、`isNpxMcpServer(server)`。 | vendor/netease-youdao/LobsterAI/src/main/mcp/mcpLaunchResolution.ts |
| F-la-031 | `McpRuntime` 类方法含 `getStore`、`getLaunchResolverManager`、`ensureLaunchResolution`、`setMediaGenerationHandler`、`setBrowserToolHandler`、`getAskUserCallbackUrl`、`getBridgeSecret`、`getResolvedServersCache`、`refreshResolvedServersCache`、`startAskUserServer`、`askUserInternal`、`resolveAskUser`、`broadcastServersChanged`；配套 `McpRuntimeDeps` 接口。 | vendor/netease-youdao/LobsterAI/src/main/mcp/mcpRuntime.ts |
| F-la-032 | `mcpBridgeServer.ts` 导出 `McpBridgeServer` 类与请求/响应类型 `AskUserRequest`、`AskUserResponse`、`MediaGenerationRequest`、`MediaGenerationResponse`、`BrowserToolRequest`、`BrowserToolResponse`。 | vendor/netease-youdao/LobsterAI/src/main/libs/mcpBridgeServer.ts |
| F-la-033 | `SkillManager` 类（skillManager.ts，约 1396 行起）方法含 `syncBundledSkillsToUserData`、`listSkills`、`buildAutoRoutingPrompt`、`detectSkillsFromOpenClaw`、`syncSkillsFromOpenClaw`、`setSkillEnabled`、`downloadSkill`、`upgradeSkill`、`confirmPendingInstall`、`getSkillConfig`、`setSkillConfig`、`startWatching`；导出 `SkillRecord` 类型。 | vendor/netease-youdao/LobsterAI/src/main/skills/skillManager.ts |
| F-la-034 | `skills/index.ts` 仅重导出 `./openClawSync` 的 `OpenClawSkillReport` 类型与 `updatePluginSkillIdsFromReport` 函数。 | vendor/netease-youdao/LobsterAI/src/main/skills/index.ts |
| F-la-035 | `src/main/skins/` 共 20 个 `.ts` 文件（Glob 计数）：12 个实现文件（`index.ts`、`registerSkinElectron.ts`、`skinRuntimeController.ts`、`skinProtocol.ts`、`skinPresentation.ts`、`skinStore.ts`、`skinToolHandler.ts`、`skinMediaBridge.ts`、`skinImageValidation.ts`、`skinWorkflowRegistry.ts`、`skinPackKit.ts`、`skinPackKitLifecycle.ts`）与 8 个测试文件（对应 `*.test.ts`）；`index.ts` 导出 `notifySkinChanged`、`registerSkinElectronIntegration`、`SKIN_PRIVILEGED_SCHEME`、`SkinRuntimeController`。 | vendor/netease-youdao/LobsterAI/src/main/skins/（Glob 计数；index.ts） |
| F-la-036 | kits IPC 处理器（`ipcHandlers/kits/handlers.ts`）常量 `KITS_INSTALLED_KEY = KitStoreKeyValue.Installed`、`SKILLS_DIR_NAME = 'SKILLs'`、`SKILL_FILE_NAME = 'SKILL.md'`；`downloadBuffer(url)` 使用 60 秒超时并递归跟随 3xx 重定向。 | vendor/netease-youdao/LobsterAI/src/main/ipcHandlers/kits/handlers.ts |
| F-la-037 | preload.ts 以 `ipcRenderer.invoke`/`ipcRenderer.on` 暴露的 IPC 通道按命名空间分组，包括 `skills:*`、`kits:*`、`enterprise:*`、`api:fetch`/`api:stream`/`api:stream:cancel`、`window-*`/`window:*`、`store:*`、`cowork:session:*`、`cowork:config:*`、`cowork:memory:*`、`cowork:dreaming:*`、`cowork:stream:*`、`dialog:*`、`artifact:*`、`app:*`、`plugins:*`、`log:*`、`im:*`、`media:*`、`feishu:install:*`、`dingtalk:install:*`、`github-copilot:*`、`openai-codex-oauth:*`、`xai-oauth:*`、`network:status-change`。 | vendor/netease-youdao/LobsterAI/src/main/preload.ts（ipcRenderer 调用段） |
| F-la-038 | `cowork:stream:*` 推送通道共 9 个事件：`message`、`messageUpdate`、`sessionStatus`、`contextUsage`、`contextMaintenance`、`permission`、`permissionDismiss`、`complete`、`error`。 | vendor/netease-youdao/LobsterAI/src/main/preload.ts（ipcRenderer.on('cowork:stream:...') 段，逐条计数） |
| F-la-039 | IM 实例管理通道按平台参数化：`im:{platform}:instance:add`、`im:{platform}:instance:delete`、`im:{platform}:instance:config:set`，覆盖 telegram、discord、feishu、dingtalk、wecom、weixin、nim、qq、email 九个平台；另有 `im:pairing:list`/`im:pairing:approve`/`im:pairing:reject` 配对通道。 | vendor/netease-youdao/LobsterAI/src/main/preload.ts（im 命名空间段） |
| F-la-040 | preload 暴露 OAuth/安装流程通道：`github-copilot:request-device-code`/`poll-for-token`/`cancel-polling`/`sign-out`/`refresh-token`/`token-updated`、`openai-codex-oauth:start`/`cancel`/`logout`/`status`、`xai-oauth:start`/`cancel`/`logout`/`status`/`device-code`、`feishu:install:qrcode`/`poll`/`verify`、`dingtalk:install:qrcode`/`poll`/`verify`。 | vendor/netease-youdao/LobsterAI/src/main/preload.ts |

## 渲染进程（src/renderer/）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-la-041 | `App.tsx` 顶层视图路由包含 `CoworkView`、`KitsView`、`LibraryView`、`ScheduledTasksView`、`Settings`、`SkillsAndConnectorsView` 等组件，并集成 Redux store。 | vendor/netease-youdao/LobsterAI/src/renderer/App.tsx |
| F-la-042 | `src/renderer/store/slices/` 目录含 21 个 `.ts` 文件（Glob `src/renderer/store/slices/*.ts` 计数），包括 13 个 slice 实现文件（`coworkSlice.ts`、`agentSlice.ts`、`artifactSlice.ts` 等）与 8 个并置测试文件。 | vendor/netease-youdao/LobsterAI/src/renderer/store/slices/（Glob 计数） |

## 共享层（src/shared/cowork/）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-la-043 | `btw.ts` 定义 `CoworkBtwStatus` 枚举：`pending`、`answered`、`failed`、`stopped`。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/btw.ts |
| F-la-044 | `btw.ts` 常量：`COWORK_BTW_CONTEXT_MAX_CHARS = 16_000`、`EVENT_QUESTION/EVENT_RESULT = 120_000`、`IDENTIFIER = 512`、`THREAD_ENTRY_LIMIT = 50`、`THREAD_CONTENT = 500_000`、`EPHEMERAL_THREAD_LIMIT = 12`。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/btw.ts |
| F-la-045 | `btw.ts` 接口：`CoworkBtwEntry`、`CoworkBtwThread`、`CoworkBtwSubmitRequest`/`CoworkBtwSubmitResponse`、`CoworkBtwAbortRequest`/`CoworkBtwAbortResponse`。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/btw.ts |
| F-la-046 | `parseCoworkBtwCommand` 以正则 `/^\/(?:btw|side)(?=\s|$)/i` 匹配 `/btw`、`/side` 命令；`createCoworkRunId` 生成格式为 `btw-${Date.now()}-${rand}` 的运行 ID。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/btw.ts（parseCoworkBtwCommand、createCoworkRunId） |
| F-la-047 | `goal.ts` 定义 `CoworkGoalStatus` 枚举：`active`、`paused`、`blocked`、`usage_limited`、`budget_limited`、`complete`。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/goal.ts |
| F-la-048 | `CoworkGoal` 接口字段含 `id`、`objective`、`status`、`tokensUsed`、`tokenBudget`、`continuationTurns` 等；`normalizeCoworkGoal` 做规范化；`formatCoworkGoalTokenCount` 以 k/m 缩写格式化 token 数。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/goal.ts |
| F-la-049 | `rail.ts` 定义 `CoworkMessageRailIndexItem`（字段 `messageId`、`type: 'user' \| 'assistant'`、`sequence`、`messageOffset`、`timestamp`、`preview`、`contentLen`）；常量 `COWORK_RAIL_PREVIEW_MAX_LENGTH = 50`；函数 `stripCoworkRailPreviewMarkdown`、`getCoworkRailPreview`。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/rail.ts |
| F-la-050 | `steer.ts` 定义 `CoworkSteerStatus` 枚举：`pending`、`accepted`、`rejected`。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/steer.ts |
| F-la-051 | `CoworkSteerRejectReason` 枚举共 7 个取值：`no_active_turn`、`not_streaming`、`context_maintenance`、`runtime_unsupported`、`runtime_rejected`、`empty_input`、`unknown`。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/steer.ts |
| F-la-052 | `CoworkSteerRequest` 字段 `sessionId`、`text`、`clientSteerId`；`CoworkPendingSteer` 含 `attachments`、`imageAttachments`、`selectedTextSnippets`、`browserAnnotations`、`kitIds` 等字段；`CoworkQueuedMediaSelection` 的 `mode` 取值为 `'auto' \| 'image' \| 'video' \| 'none'`。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/steer.ts |
| F-la-053 | `constants.ts` 定义 `SESSION_AGNOSTIC_PERMISSION_SESSION_ID = '__askuser__'` 与 `ASK_USER_QUESTION_TOOL_NAME = 'AskUserQuestion'`。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/constants.ts |
| F-la-054 | `constants.ts` 定义分页常量：会话分页 50、消息分页 30、搜索上限 200 等（值直接读自常量定义）。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/constants.ts |
| F-la-055 | `CoworkIpcChannel` 常量对象（`as const`）包含 `CancelMediaTask: 'cowork:media:cancel'`、`ForkSession: 'cowork:session:fork'`、`SubmitBtw`/`AbortBtw`/`SubmitSteer`/`GoalCommand`、`StreamBtwResult`、`MemoryReadRaw` 等键。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/constants.ts（CoworkIpcChannel） |
| F-la-056 | `CoworkForkMode` 类型取值为 `none`、`conversation`、`worktree`。 | vendor/netease-youdao/LobsterAI/src/shared/cowork/constants.ts |

## 定时任务（src/scheduledTask/）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-la-057 | `design.md` 声明定时任务三层架构：Renderer → Main → OpenClaw Gateway。 | vendor/netease-youdao/LobsterAI/src/scheduledTask/design.md |
| F-la-058 | `design.md` 列出四大理念：OpenClaw 驱动、策略模式、来源推断、15 秒轮询。 | vendor/netease-youdao/LobsterAI/src/scheduledTask/design.md |
| F-la-059 | `types.ts` 定义 `Schedule` 判别联合，成员为 `ScheduleAt`、`ScheduleEvery`、`ScheduleCron`（以 kind 字段判别）。 | vendor/netease-youdao/LobsterAI/src/scheduledTask/types.ts（Schedule 类型） |
| F-la-060 | `types.ts` 定义 `ScheduledTaskPayload` 判别联合，成员为 `AgentTurnPayload`、`SystemEventPayload`；并定义 `ScheduledTask`、`ScheduledTaskRun`、`ScheduledTaskInput` 等接口。 | vendor/netease-youdao/LobsterAI/src/scheduledTask/types.ts |
| F-la-061 | `constants.ts` 枚举：`DeliveryMode` = `none`/`announce`/`webhook`；`SessionTarget` = `main`/`isolated`；`WakeMode` = `now`/`next-heartbeat`。 | vendor/netease-youdao/LobsterAI/src/scheduledTask/constants.ts |
| F-la-062 | `constants.ts` 枚举：`TaskStatus` = `success`/`error`/`skipped`/`running`；常量 `DefaultAgentId = 'main'`；另有 `ScheduleKind`、`PayloadKind`、`OriginKind`、`BindingKind`、`InternalTaskMarker`。 | vendor/netease-youdao/LobsterAI/src/scheduledTask/constants.ts |
| F-la-063 | `IpcChannel` 常量对象（`as const`）以 `scheduledTask:` 为前缀，键含 `list`、`get`、`create`、`update`、`delete`、`toggle`、`runManually`、`stop`、`listRuns`、`countRuns`、`listAllRuns`、`resolveSession`、`listChannels`、`listChannelConversations`、`statusUpdate`、`runUpdate`、`refresh`。 | vendor/netease-youdao/LobsterAI/src/scheduledTask/constants.ts（IpcChannel） |
| F-la-064 | `CronJobService` 类方法含 `addJob`、`updateJob`、`removeJob`、`listJobs`、`getJob`、`toggleJob`、`runJob`、`listRuns`、`countRuns`、`listAllRuns`、`startPolling`、`notifyGatewayReady`、`stopPolling`、`pollOnce`，以及 `mapGatewaySchedule`、`mapGatewayTaskState`、`mapGatewayJob`、`mapGatewayRun` 映射函数。 | vendor/netease-youdao/LobsterAI/src/scheduledTask/cronJobService.ts |

## 技能系统（SKILLs/）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-la-065 | `SKILLs/` 下共有 29 个 `SKILL.md`（Glob `SKILLs/*/SKILL.md` 计数，每个技能一个子目录）。 | vendor/netease-youdao/LobsterAI/SKILLs/（Glob 计数） |
| F-la-066 | `skills.config.json` 顶层 `version` 为 1；`defaults` 含 29 个条目，与 SKILL.md 数量一致；每个条目字段为 `order` 与 `enabled`。 | vendor/netease-youdao/LobsterAI/SKILLs/skills.config.json |
| F-la-067 | SKILL.md frontmatter 字段含 `name`、`description`、`official`、`version`；样例 `web-search/SKILL.md` 的 `official: true`、`version: 1.0.2`。 | vendor/netease-youdao/LobsterAI/SKILLs/web-search/SKILL.md |
| F-la-068 | `skills.config.json` `defaults` 全部条目及 order 值：docx:10、web-search:15、xlsx:20、pptx:30、pdf:40、remotion:50、develop-web-game:60、playwright:70、create-plan:80、canvas-design:90、frontend-design:100、stock-analyzer:110、stock-announcements:111、stock-explorer:112、content-planner:120、article-writer:121、daily-trending:122、local-tools:200、weather:210、imap-smtp-email:211、seedance:212、seedream:213、skin-creator:214、films-search:222、music-search:223、technology-news-search:224、youdaonote:298、skill-vetter:299、skill-creator:300。 | vendor/netease-youdao/LobsterAI/SKILLs/skills.config.json（defaults 段，共 29 条） |
| F-la-069 | `defaults` 中显式 `enabled: false` 的条目为 `skin-creator`（order 214）与 `technology-news-search`（order 224）；其余 27 个条目未显式置 false。 | vendor/netease-youdao/LobsterAI/SKILLs/skills.config.json |

## 测试（tests/ 与 vitest 配置）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-la-070 | `vitest.config.ts` 的 `test.include` 为 `['src/**/*.test.ts', 'tests/**/*.test.ts']`，`environment: 'node'`，`testTimeout: 20000`（注释说明为 I/O 密集型套件放宽默认 5 秒限制）。 | vendor/netease-youdao/LobsterAI/vitest.config.ts |
| F-la-071 | `vitest.config.ts` 的 `resolve.alias` 定义 `@shared` → `./src/shared`、`@` → `./src/renderer`。 | vendor/netease-youdao/LobsterAI/vitest.config.ts |
| F-la-072 | `tests/` 目录顶层共 38 个测试文件（LS 计数）；递归含子目录共 43 个。混合 `.test.ts`（Vitest）与 `.test.mjs`（node:test 旧版）两种命名。 | vendor/netease-youdao/LobsterAI/tests/（LS 计数） |
| F-la-073 | `tests/` 含两个子目录 `sqlite-backup/` 与 `openclaw-extensions/`。 | vendor/netease-youdao/LobsterAI/tests/（LS 目录列表） |
| F-la-074 | `src/main/skins/` 含 8 个 `*.test.ts`（Glob 计数），与对应实现文件并置同目录。 | vendor/netease-youdao/LobsterAI/src/main/skins/（Glob `*.test.ts` 计数） |
