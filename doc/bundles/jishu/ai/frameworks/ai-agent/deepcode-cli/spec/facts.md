---
type: spec
title: "Facts — deepcode-cli"
---

# Facts — deepcode-cli

> R 阶段事实清单。每条事实均引用确切文件路径与行号，不含推断性描述。

## 项目元信息

- **F-001**: 根 `package.json` 中 `name` 字段为 `"@vegamo/deepcode-monorepo"`，`version` 为 `"0.2.1"`，`private` 为 `true`。（`package.json:2-4`）
- **F-002**: 根 `package.json` 中 `description` 为 `"Deep Code — CLI, core library, and VSCode companion"`。（`package.json:5`）
- **F-003**: 根 `package.json` 中 `license` 为 `"MIT"`，`packageManager` 为 `"npm@10.9.4"`，`type` 为 `"module"`。（`package.json:6-8`）
- **F-004**: 根 `package.json` 中 `workspaces` 数组包含 `"packages/*"`。（`package.json:9-11`）
- **F-005**: 根 `package.json` 中 `repository.url` 为 `"git+https://github.com/lessweb/deepcode-cli.git"`。（`package.json:12-15`）

## TypeScript 配置

- **F-006**: 根 `tsconfig.json` 启用 `strict: true`、`noImplicitAny: true`、`strictNullChecks: true` 等严格选项。（`tsconfig.json:3-16`）
- **F-007**: 根 `tsconfig.json` 设置 `target: "ES2022"`、`module: "ESNext"`、`moduleResolution: "bundler"`、`jsx: "react-jsx"`。（`tsconfig.json:25-29`）
- **F-008**: 根 `tsconfig.json` 的 `references` 指向 `./packages/core`、`./packages/cli`、`./packages/vscode-ide-companion` 三个子包。（`tsconfig.json:33-37`）

## 三包结构

- **F-009**: `packages/cli/package.json` 中 `name` 为 `"@vegamo/deepcode-cli"`，`bin.deepcode` 指向 `"./dist/cli.js"`，`engines.node` 为 `">=22"`。（`packages/cli/package.json:2,12-14,24-26`）
- **F-010**: `packages/core/package.json` 中 `name` 为 `"@vegamo/deepcode-core"`，`main` 为 `"./dist/index.js"`，`types` 为 `"./dist/index.d.ts"`。（`packages/core/package.json:2,7-8`）
- **F-011**: `packages/vscode-ide-companion/package.json` 中 `name` 为 `"deepcode-vscode"`，`publisher` 为 `"vegamo"`，`type` 为 `"commonjs"`，`engines.vscode` 为 `"^1.85.0"`。（`packages/vscode-ide-companion/package.json:2-4,8,16-18`）
- **F-012**: `packages/cli/package.json` 依赖 `ink`、`react`、`yargs`、`chalk`、`gradient-string`、`ignore`、`read-package-up`。（`packages/cli/package.json:35-45`）
- **F-013**: `packages/core/package.json` 依赖 `openai`、`ejs`、`gray-matter`、`zod`、`undici`、`chalk`、`ignore`。（`packages/core/package.json:30-38`）

## 权限系统

- **F-014**: `PermissionScope` 类型包含 10 个值：`read-in-cwd`、`read-out-cwd`、`write-in-cwd`、`write-out-cwd`、`delete-in-cwd`、`delete-out-cwd`、`query-git-log`、`mutate-git-log`、`network`、`mcp`。（`packages/core/src/settings.ts:26-36`）
- **F-015**: `PermissionDefaultMode` 类型为 `"allowAll" | "askAll"`。（`packages/core/src/settings.ts:38`）
- **F-016**: `PermissionSettings` 类型包含 `allow?: PermissionScope[]`、`deny?: PermissionScope[]`、`ask?: PermissionScope[]`、`defaultMode?: PermissionDefaultMode`。（`packages/core/src/settings.ts:40-45`）
- **F-017**: `normalizePermissions` 函数在未指定 `defaultMode` 时返回 `"allowAll"`。（`packages/core/src/settings.ts:262-269`）
- **F-018**: `mergePermissions` 函数合并用户设置与项目设置的权限列表，项目设置的 `defaultMode` 优先于用户设置。（`packages/core/src/settings.ts:271-287`）
- **F-019**: `PLAN_MODE_FORCE_ASK_SCOPES` 常量包含 `write-in-cwd`、`write-out-cwd`、`delete-in-cwd`、`delete-out-cwd`、`mutate-git-log`。（`packages/core/src/session.ts:78-84`）

## 设置与配置

- **F-020**: `DEFAULT_MODEL` 常量值为 `"deepseek-v4-flash"`，`DEFAULT_BASE_URL` 为 `"https://api.deepseek.com"`。（`packages/core/src/settings.ts:674-675`）
- **F-021**: `DEFAULT_CONTEXT_WINDOW` 为 `256 * 1024`（262144），`DEEPSEEK_V4_CONTEXT_WINDOW` 为 `1024 * 1024`（1048576）。（`packages/core/src/settings.ts:132-133`）
- **F-022**: `getUserSettingsPath()` 返回 `path.join(os.homedir(), ".deepcode", "settings.json")`。（`packages/core/src/settings.ts:681-683`）
- **F-023**: `getProjectSettingsPath(projectRoot)` 返回 `path.join(projectRoot, ".deepcode", "settings.json")`。（`packages/core/src/settings.ts:689-691`）
- **F-024**: `collectDeepcodeEnv` 函数收集以 `DEEPCODE_` 为前缀的进程环境变量，去除前缀后返回。（`packages/core/src/settings.ts:443-455`）
- **F-025**: `resolveSettingsSources` 按优先级合并设置：系统环境变量 > 项目设置 > 项目环境变量 > 用户设置 > 用户环境变量 > 默认值。（`packages/core/src/settings.ts:521-630`）
- **F-026**: `telemetryEnabled` 默认值为 `true`，`reasoningEffort` 默认值为 `"max"`，`debugLogEnabled` 默认值为 `false`，`multimodal` 默认值为 `"default"`。（`packages/core/src/settings.ts:586-608`）

## MCP 集成

- **F-027**: `McpServerConfig` 类型包含 `command: string`、`args?: string[]`、`env?: Record<string, string>`。（`packages/core/src/settings.ts:20-24`）
- **F-028**: `MCP_STARTUP_TIMEOUT_MS` 默认值为 30000 毫秒，可通过环境变量 `DEEPCODE_MCP_TIMEOUT` 覆盖。（`packages/core/src/mcp/mcp-manager.ts:5-7`）
- **F-029**: `MCP_CALL_TOOL_TIMEOUT_MS` 常量值为 60000 毫秒。（`packages/core/src/mcp/mcp-manager.ts:8`）
- **F-030**: MCP 工具命名空间格式为 `mcp__<serverName>__<toolName>`，通过 `buildMcpNamespacedName` 函数生成。（`packages/core/src/mcp/mcp-manager.ts:33-57`）
- **F-031**: `API_TOOL_NAME_MAX_LENGTH` 常量值为 64，`API_TOOL_NAME_PATTERN` 正则为 `/^[a-zA-Z0-9_-]+$/`。（`packages/core/src/mcp/mcp-manager.ts:9-10`）
- **F-032**: `McpServerStatus` 类型的 `status` 字段取值为 `"starting" | "ready" | "failed" | "reconnecting"`。（`packages/core/src/mcp/mcp-manager.ts:20-31`）
- **F-033**: `McpManager` 类内部维护 `clients`、`tools`、`prompts`、`resources` 四个数组。（`packages/core/src/mcp/mcp-manager.ts:60-73`）
- **F-034**: `McpManager.isMcpTool(name)` 通过检查名称是否以 `"mcp__"` 开头来判断。（`packages/core/src/mcp/mcp-manager.ts:336-338`）
- **F-035**: `McpClient` 通过 `child_process.spawn` 启动 MCP 服务器进程，使用 stdio 管道通信。（`packages/core/src/mcp/mcp-client.ts:141-146`）
- **F-036**: MCP 协议握手发送 `initialize` 请求，`protocolVersion` 为 `"2025-03-26"`，`clientInfo.name` 为 `"deepcode-cli"`，`clientInfo.version` 为 `"0.1.0"`。（`packages/core/src/mcp/mcp-client.ts:191-198`）
- **F-037**: `McpClient` 支持的协议版本为 `"2025-03-26"` 和 `"2024-11-05"`。（`packages/core/src/mcp/mcp-client.ts:204`）
- **F-038**: `McpClient` 实现 `tools/list`、`tools/call`、`prompts/list`、`prompts/get`、`resources/list`、`resources/read` 六个 JSON-RPC 方法。（`packages/core/src/mcp/mcp-client.ts:221-282`）
- **F-039**: 列表类方法（listTools、listPrompts、listResources）支持分页，最多遍历 100 页。（`packages/core/src/mcp/mcp-client.ts:225,246,267`）
- **F-040**: `McpClient` 在命令为 `npx` 时自动添加 `-y` 参数（若未已有）。（`packages/core/src/mcp/mcp-client.ts:393-405`）
- **F-041**: Windows 平台上 `createMcpSpawnSpec` 使用 `shell: true` 并将命令与参数合并为单字符串。（`packages/core/src/mcp/mcp-client.ts:425-437`）

## CLI 命令与会话

- **F-042**: CLI 入口 `cli.tsx` 使用 `ink` 的 `render` 函数挂载 `AppContainer` 组件，设置 `exitOnCtrlC: false`。（`packages/cli/src/cli.tsx:1,137-147`）
- **F-043**: CLI 参数解析使用 `yargs`，支持 `--prompt/-p`、`--exec/-x`、`--resume/-r`、`--fork/-f`、`--last/-l`、`--version/-v`、`--help/-h`。（`packages/cli/src/cli-args.ts:87-113,167-171`）
- **F-044**: `--exec/-x` 模式要求同时提供非空的 `--prompt/-p`，不启动 TUI。（`packages/cli/src/cli-args.ts:148-150`）
- **F-045**: 会话 ID 使用 UUID v4 格式验证，正则为 `/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i`。（`packages/cli/src/cli-args.ts:13`）
- **F-046**: EPILOG 中列出的斜杠命令包括 `/skills`、`/model`、`/plan`、`/new`、`/init`、`/resume`、`/fork`、`/continue`、`/undo`、`/mcp`、`/raw`、`/exit`。（`packages/cli/src/cli-args.ts:53-77`）
- **F-047**: `runExecMode` 函数返回退出码：`0` 成功、`1` 失败、`130` 中断。（`packages/cli/src/exec-runner.ts:84,120,141,144`）
- **F-048**: `SessionStatus` 类型包含 8 个状态：`failed`、`pending`、`processing`、`waiting_for_user`、`completed`、`interrupted`、`ask_permission`、`permission_denied`。（`packages/core/src/session.ts:211-219`）
- **F-049**: `SessionManager` 类内部持有 `mcpManager = new McpManager()` 实例。（`packages/core/src/session.ts:392`）
- **F-050**: `MAX_SESSION_ENTRIES` 常量值为 50。（`packages/core/src/session.ts:72`）
- **F-051**: 会话索引存储路径为 `~/.deepcode/projects/<projectCode>/sessions-index.json`。（`packages/cli/src/cli.tsx:39`）
- **F-052**: `getProjectCode` 函数将项目路径转换为短标识符，超过 64 字符时使用 SHA-256 哈希前 16 字符加目录名前缀。（`packages/core/src/session.ts:98-114`）

## Core 库导出

- **F-053**: `packages/core/src/index.ts` 导出 `SessionManager`、`McpManager`、`McpClient`、`ToolExecutor` 等核心类。（`packages/core/src/index.ts:38,69,96-97`）
- **F-054**: Core 库导出 8 个工具处理器：`handleBashTool`、`handleReadTool`、`handleWriteTool`、`handleEditTool`、`handleUpdatePlanTool`、`handleUnderstandImageTool`、`handleWebSearchTool`、`handleAskUserQuestionTool`。（`packages/core/src/index.ts:86-93`）

## VSCode 扩展

- **F-055**: VSCode 扩展贡献命令 `deepcode.openView`（标题 "Open Deep Code"）。（`packages/vscode-ide-companion/package.json:44-53`）
- **F-056**: VSCode 扩展在活动栏注册视图容器 `deepcode`，包含 webview 视图 `deepcode.chatView`。（`packages/vscode-ide-companion/package.json:54-72`）

## MCP 文档

- **F-057**: `docs/mcp.md` 文档说明 MCP 工具命名格式为 `mcp__<服务名>__<工具名>`，示例 `mcp__github__search_code`。（`docs/mcp.md:15`）
- **F-058**: `docs/mcp.md` 文档说明 MCP 配置位于 `~/.deepcode/settings.json` 的 `mcpServers` 字段。（`docs/mcp.md:19,30`）
- **F-059**: `docs/mcp.md` 文档说明在 TUI 中输入 `/mcp` 可查看 MCP 服务器状态和工具列表。（`docs/mcp.md:149`）
