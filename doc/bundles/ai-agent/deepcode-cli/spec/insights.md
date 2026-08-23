---
type: spec
scope: deepcode-cli
name: insights
version: "0.1.0"
source: https://github.com/lessweb/deepcode-cli
description: deepcode-cli 源码逆向分析得出的核心洞察，包含架构决策、权限模型与 MCP 集成的反常识发现
---

# Insights — deepcode-cli

## 1. 三层设置合并模型中环境变量的最高优先级

**陈述**：deepcode-cli 的设置解析采用系统环境变量 > 项目设置 > 项目环境变量 > 用户设置 > 用户环境变量 > 默认值的六层合并优先级，其中以 `DEEPCODE_` 为前缀的系统环境变量拥有最高优先级，可覆盖任何配置文件中的值。

**证据**：
- F-025：`resolveSettingsSources` 函数按此优先级链合并 model、thinkingEnabled、reasoningEffort 等字段。
- F-024：`collectDeepcodeEnv` 收集所有 `DEEPCODE_` 前缀变量。
- F-026：telemetryEnabled 默认 true、reasoningEffort 默认 "max" 等默认值仅在所有上层来源均未提供时生效。

**反常识**：项目设置文件（`.deepcode/settings.json`）的优先级高于用户设置文件（`~/.deepcode/settings.json`），但项目设置文件中 `env` 字段内的值优先级低于系统环境变量。这意味着即使在项目配置中设置了 `env.MODEL`，终端中导出的 `DEEPCODE_MODEL` 仍会覆盖它。

**行动**：在 CI/CD 或容器环境中部署时，通过 `DEEPCODE_*` 环境变量注入配置最为可靠；本地开发时项目级 `.deepcode/settings.json` 可覆盖用户级配置，但无法覆盖 shell 中已导出的环境变量。

---

## 2. MCP 工具命名的哈希消歧机制

**陈述**：MCP 工具通过 `mcp__<server>__<tool>` 命名空间暴露给 LLM。当生成的命名超过 64 字符或包含非法字符时，系统会截断名称并附加 SHA-256 哈希前 8 位作为后缀；若仍冲突则追加递增序号。

**证据**：
- F-030：`buildMcpNamespacedName` 函数实现命名空间构建。
- F-031：`API_TOOL_NAME_MAX_LENGTH` 为 64，名称只允许 `[a-zA-Z0-9_-]`。
- F-032：`McpServerStatus` 追踪每个服务器的工具数量与名称列表。
- mcp-manager.ts:504-523：`sanitizeApiToolNamePart` 将非法字符替换为下划线，`hashToolName` 生成 8 字符十六进制哈希。

**反常识**：MCP 服务器名称和工具名称中的非 ASCII 字符（如中文、点号、斜杠）会被替换为下划线，而非直接拒绝。这意味着两个名称仅在非法字符位置不同的工具可能产生相同的净化名称，此时哈希后缀才发挥消歧作用。此外，工具描述在名称被截断/哈希时会附加 `MCP source: <server>: <originalName>` 行，帮助 LLM 识别原始工具名。

**行动**：配置 MCP 服务器时使用简短的 ASCII 名称（如 `github` 而非 `my-github-mcp-server-prod`），可避免工具名被哈希截断，提升 LLM 工具调用的可读性和可靠性。

---

## 3. 权限系统的 allowAll 默认模式与 Plan Mode 强制询问

**陈述**：deepcode-cli 默认权限模式为 `allowAll`，即不在 ask/deny 列表中的权限作用域默认放行。但 Plan Mode 激活时，写操作和 Git 变更操作（write-in-cwd、write-out-cwd、delete-in-cwd、delete-out-cwd、mutate-git-log）会被强制加入询问列表，无论配置如何。

**证据**：
- F-017：`normalizePermissions` 在未指定 defaultMode 时返回 "allowAll"。
- F-019：`PLAN_MODE_FORCE_ASK_SCOPES` 包含 5 个高危作用域。
- F-014：PermissionScope 共定义 10 个作用域，区分 cwd 内外。
- F-018：项目设置的 defaultMode 优先于用户设置。

**反常识**：权限系统按"工作目录内外"二分（read-in-cwd vs read-out-cwd），而非简单的读/写/执行分类。这意味着在 `allowAll` 模式下，agent 可以读取和写入工作目录外的文件——包括用户主目录下的敏感文件——只要操作不涉及被显式 deny 的作用域。此外，`--exec` 非交互模式遇到 `ask_permission` 状态会直接失败退出，无法在命令行中批准权限。

**行动**：在不可信环境中运行时，应将 `defaultMode` 设为 `"askAll"` 或将高危作用域加入 `deny` 列表。使用 `--exec` 模式前，需预先在 settings.json 的 `permissions.allow` 中配置所需权限，否则执行将中断。

---

## 4. 三包 monorepo 中 core 包的无 UI 依赖设计

**陈述**：项目采用 cli/core/vscode-ide-companion 三包结构，其中 `@vegamo/deepcode-core` 包不依赖任何 UI 框架（无 React、无 Ink），仅依赖 openai、ejs、gray-matter、zod 等纯逻辑库。CLI 包和 VSCode 扩展包均通过 `file:../core` 引用 core 包。

**证据**：
- F-010：core 包入口为 `dist/index.js`，导出类型声明。
- F-012：CLI 包依赖 ink、react、yargs 等 UI/CLI 库。
- F-013：core 包依赖 openai、ejs、gray-matter、zod、undici。
- F-053：core 包通过 index.ts 统一导出 SessionManager、McpManager、ToolExecutor 等。
- F-054：core 导出 8 个工具处理器。
- F-008：tsconfig references 确认三包结构。

**反常识**：VSCode 扩展包（`deepcode-vscode`）使用 `commonjs` 模块类型，而 CLI 和 core 包使用 `module`（ESM）。这种差异意味着 core 包在被 VSCode 扩展消费时需要兼容 CJS 解析，但 core 自身的 `package.json` 只声明了 ESM 入口（`"import": "./dist/index.js"`），没有 `require` 条件导出。实际互操作通过 esbuild 打包解决。

**行动**：若要为 deepcode-cli 开发第三方前端（如 Web UI、Electron 应用），可直接依赖 `@vegamo/deepcode-core`，自行实现 `renderMarkdown`、`onAssistantMessage` 等回调即可复用全部会话管理、工具执行和 MCP 能力，无需引入 Ink/React。
