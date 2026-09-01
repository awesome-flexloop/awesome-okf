---
type: spec
title: "Facts — pi-cli"
---

# Facts — pi-cli

> R Phase (Facts). 每条事实引用精确文件路径与行号。无推断词。

- **F-001**: 项目根 `package.json` 中 `name` 字段为 `"pi-monorepo"`，`private` 为 `true`，`type` 为 `"module"`。（`package.json:2-4`）
- **F-002**: monorepo workspaces 包含 `packages/*`、`packages/session-backends/*` 以及 `packages/coding-agent/examples/extensions/` 下的多个示例扩展目录。（`package.json:5-13`）
- **F-003**: `build` 脚本按顺序构建 tui、telemetry、ai、agent、session-backends/sqlite-node、protocol、client、server、coding-agent 共9个包。（`package.json:16`）
- **F-004**: `check` 脚本运行 `biome check --write --error-on-warnings .`，随后执行 pinned-deps、ts-imports、shrinkwrap、install-lock、tsgo 类型检查、browser-smoke 共6项检查。（`package.json:18`）
- **F-005**: Node 引擎要求 `>=22.19.0`。（`package.json:63-65`）
- **F-006**: 项目版本号为 `0.0.3`。（`package.json:66`）
- **F-007**: devDependencies 包含 `@biomejs/biome 2.3.5`、`typescript 5.9.3`、`esbuild 0.28.1`、`husky 9.1.7`、`tsx 4.22.1`。（`package.json:51-62`）
- **F-008**: README 列出三个核心包：`@earendil-works/pi-coding-agent`（交互式编码代理 CLI）、`@earendil-works/pi-agent-core`（带工具调用和状态管理的代理运行时）、`@earendil-works/pi-ai`（统一多提供商 LLM API）。（`README.md:17-19`）
- **F-009**: README 还列出 `@earendil-works/pi-telemetry`（厂商中立遥测契约）和 `@earendil-works/pi-tui`（带差分渲染的终端 UI 库）。（`README.md:30-34`）
- **F-010**: Pi 不内置文件系统、进程、网络或凭证访问的权限系统，默认以启动用户和进程的权限运行。（`README.md:40`）
- **F-011**: README 文档化了三种容器化/沙箱模式：Gondolin 扩展、Plain Docker、OpenShell。（`README.md:42-46`）
- **F-012**: 开发命令包括 `npm install --ignore-scripts`、`npm run build`、`npm run build:offline`、`npm run check`、`./test.sh`、`./pi-test.sh`。（`README.md:54-61`）
- **F-013**: AGENTS.md 规定代码风格：禁止 `any`（除非绝对必要）、禁止内联导入（`await import()`）、仅使用可擦除 TypeScript 语法（无 parameter properties、enum、namespace/module）。（`AGENTS.md:18-23`）
- **F-014**: AGENTS.md 规定禁止直接修改 `packages/ai/src/models.generated.ts`，必须更新 `packages/ai/scripts/generate-models.ts` 后重新生成。（`AGENTS.md:27`）
- **F-015**: AGENTS.md 规定代码变更后必须运行 `npm run check`，禁止未经用户要求运行 `npm run build` 或 `npm test`。（`AGENTS.md:31-32`）
- **F-016**: AGENTS.md 规定锁步版本控制：所有包共享一个版本号，patch = 修复+新增，minor = 破坏性变更，无 major 发布。（`AGENTS.md:129`）
- **F-017**: `tsconfig.json` 配置了路径别名，将 `@earendil-works/pi-ai` 映射到 `./packages/ai/src/index.ts`，`@earendil-works/pi-tui` 映射到 `./packages/tui/src/index.ts`。（`tsconfig.json:11,32`）
- **F-018**: `packages/ai/src/index.ts` 是核心无副作用入口，重新导出 typebox 的 `Type`、auth 模块、models、models-store、types、utils 等，但不导出 provider factories 或 OAuth 实现。（`packages/ai/src/index.ts:1-47`）
- **F-019**: `packages/ai/src/cli.ts` 是可执行脚本（shebang `#!/usr/bin/env node`），支持 `login [provider]` 和 `list` 两个命令，凭证保存到当前目录的 `auth.json` 文件。（`packages/ai/src/cli.ts:1,8,82-86`）
- **F-020**: `packages/ai/src/models.ts` 定义了 `Provider<TApi>` 接口，包含 `id`、`name`、`auth`、`getModels()`、`refreshModels()`、`stream()`、`streamSimple()` 等成员。（`packages/ai/src/models.ts:97-149`）
- **F-021**: `packages/ai/src/models.ts` 定义了 `Models` 接口，提供 `getProviders()`、`getModel()`、`refresh()`、`checkAuth()`、`getAvailable()`、`getAuth()`、`login()`、`logout()`、`stream()`、`complete()` 等方法。（`packages/ai/src/models.ts:156-223`）
- **F-022**: `createModels()` 工厂函数返回 `MutableModels` 实例，默认使用 `InMemoryCredentialStore` 和 `InMemoryModelsStore`。（`packages/ai/src/models.ts:735-737,264-266`）
- **F-023**: `createProvider()` 函数从部件构建 provider，支持静态基线模型列表和通过 `fetchModels` 获取的动态模型覆盖，支持单个 `api` 实现或按 `model.api` 分派的 map。（`packages/ai/src/models.ts:762-862`）
- **F-024**: `packages/ai/src/oauth.ts` 仅为类型导出文件，重新导出 `OAuthAuthInfo`、`OAuthCredentials`、`OAuthDeviceCodeInfo`、`OAuthLoginCallbacks`、`OAuthPrompt`、`OAuthSelectOption`、`OAuthSelectPrompt` 类型。（`packages/ai/src/oauth.ts:1-10`）
- **F-025**: `packages/ai/src/types.ts` 定义了10种已知 API 类型：`openai-completions`、`mistral-conversations`、`openai-responses`、`azure-openai-responses`、`openai-codex-responses`、`anthropic-messages`、`bedrock-converse-stream`、`google-generative-ai`、`google-vertex`、`pi-messages`。（`packages/ai/src/types.ts:17-27`）
- **F-026**: `packages/ai/src/types.ts` 列出了40个已知 provider ID，包括 `amazon-bedrock`、`anthropic`、`google`、`openai`、`deepseek`、`github-copilot`、`xai`、`groq`、`openrouter`、`mistral`、`moonshotai`、`kimi-coding`、`qwen-token-plan`、`xiaomi` 等。（`packages/ai/src/types.ts:35-76`）
- **F-027**: `packages/ai/src/types.ts` 定义 `Model<TApi>` 接口，包含 `id`、`name`、`api`、`provider`、`baseUrl`、`reasoning`、`input`、`cost`、`contextWindow`、`maxTokens`、`samplingParams`、`headers`、`compat` 字段。（`packages/ai/src/types.ts:821-850`）
- **F-028**: `packages/ai/src/types.ts` 定义 `AssistantMessage` 接口，包含 `content`（TextContent/ThinkingContent/ToolCall 数组）、`api`、`provider`、`model`、`usage`、`stopReason`、`timestamp` 等字段。（`packages/ai/src/types.ts:427-447`）
- **F-029**: `packages/ai/src/types.ts` 定义了7种停止原因：`pending`、`stop`、`length`、`toolUse`、`error`、`aborted`、`deferred`。（`packages/ai/src/types.ts:405`）
- **F-030**: `packages/ai/src/compat.ts` 是临时兼容入口，保留旧的全局 pi-ai API 表面（api-dispatch `stream()`/`complete()`、api-registry、生成目录读取、图片生成），标注将在 coding-agent ModelManager 迁移后删除。（`packages/ai/src/compat.ts:1-11`）
- **F-031**: `packages/ai/src/compat.ts` 在模块加载时调用 `registerBuiltInApiProviders()` 注册10个内置 API 实现。（`packages/ai/src/compat.ts:213`）
- **F-032**: `packages/ai/src/images.ts` 导出 `generateImages()` 函数，通过 `getImagesApiProvider()` 解析图片 API 提供商并调用其 `generateImages()` 方法。（`packages/ai/src/images.ts:14-21`）
- **F-033**: `packages/tui/src/index.ts` 导出组件包括 `Box`、`Editor`、`HStack`、`Image`、`Input`、`Loader`、`Markdown`、`ScrollView`、`SelectList`、`SettingsList`、`Spacer`、`Text`、`TruncatedText`、`VStack`。（`packages/tui/src/index.ts:13-44`）
- **F-034**: `packages/tui/src/index.ts` 导出模糊搜索函数 `fuzzyFilter`、`fuzzyMatch`，LaTeX 渲染函数 `renderLatex`，键盘处理模块 `Key`、`matchesKey`、`parseKey`，以及键绑定管理器 `KeybindingsManager`。（`packages/tui/src/index.ts:48-76`）
- **F-035**: `packages/tui/src/tui.ts` 定义 `Component` 接口，要求实现 `render(width: number): string[]` 和 `invalidate(): void` 方法，可选 `handleInput()` 和 `wantsKeyRelease`。（`packages/tui/src/tui.ts:23-47`）
- **F-036**: `packages/tui/src/tui.ts` 中 `TuiBase` 类实现差分渲染，最小渲染间隔为 16ms（`MIN_RENDER_INTERVAL_MS = 16`），支持 overlay 栈和焦点管理。（`packages/tui/src/tui.ts:343,549-642`）
- **F-037**: `packages/tui/src/tui.ts` 支持终端背景色查询（OSC 11）和配色方案通知（DSR `CSI ? 996 n`），深色方案回复 `CSI ? 997 ; 1 n`，浅色回复 `CSI ? 997 ; 2 n`。（`packages/tui/src/tui.ts:1214-1262`）
- **F-038**: `packages/agent/README.md` 描述 `@earendil-works/pi-agent-core` 为有状态代理，构建于 `@earendil-works/pi-ai` 之上，支持工具执行和事件流。（`packages/agent/README.md:1-3`）
- **F-039**: agent 支持两种工具执行模式：`parallel`（默认，预检顺序执行、允许的工具并发执行）和 `sequential`（逐个执行）。（`packages/agent/README.md:113-120`）
- **F-040**: agent 事件类型包括 `agent_start`、`agent_end`、`turn_start`、`turn_end`、`message_start`、`message_update`、`message_end`、`tool_execution_start`、`tool_execution_update`、`tool_execution_end`。（`packages/agent/README.md:160-173`）
- **F-041**: `packages/client/README.md` 描述 `@earendil-works/pi-client` 为传输无关的远程 pi 会话客户端，通过长度前缀 CBOR 消息交换，无 Node 特定导入。（`packages/client/README.md:1-3`）
- **F-042**: client 支持 `exclusive` 和 `shared` 两种会话租约模式，exclusive 在任何租约存在时失败，shared 在 exclusive 租约存在时失败。（`packages/client/README.md:30`）
- **F-043**: `packages/server/README.md` 标注该包为实验性（Experimental），API 和行为可能随时变更或移除。（`packages/server/README.md:3`）
- **F-044**: server 包导出 `PiServer` 会话服务器，通过 `PiServerListener` 接口组合传输监听器，使用 `@earendil-works/pi-protocol` 的长度前缀 CBOR 消息。（`packages/server/README.md:9,36`）
- **F-045**: `.pi/prompts/cl.md` 是发布前审计 changelog 条目的 prompt，流程包括查找最后发布标签、列出提交、检查每个包的 `[Unreleased]` 段。（`.pi/prompts/cl.md:1-4,8-16`）
- **F-046**: `.pi/prompts/is.md` 是分析 GitHub issue 的 prompt，支持 bug 和功能请求，要求独立验证行为、完整读取相关代码文件、不实现只分析和提议。（`.pi/prompts/is.md:1-5,14-27`）
- **F-047**: `.pi/prompts/pr.md` 是 PR 审查 prompt，输出结构化审查包含 What it does、Good、Bad、Ugly、Tests、Open questions 六个部分。（`.pi/prompts/pr.md:14-21`）
- **F-048**: `.pi/prompts/sa.md` 是更新 GitHub 安全公告的 prompt，要求不发布公告、不更改状态、不请求 CVE 除非用户明确同意，禁止在公告正文中包含 PoC 材料。（`.pi/prompts/sa.md:7,159`）
- **F-049**: `.pi/prompts/wr.md` 是端到端完成任务的 prompt（Wrap it），按顺序执行更新 changelog、起草评论、提交、推送、关闭 issue，禁止使用 `git add .` 或 `git add -A`。（`.pi/prompts/wr.md:5,16-28,35-36`）
- **F-050**: `packages/ai/src/models.ts` 导出 `calculateCost()` 函数，根据模型费率和使用量计算成本，支持分层定价（tiers），Anthropic 1小时缓存写入按基础输入费率2倍计费。（`packages/ai/src/models.ts:878-898`）
- **F-051**: `packages/ai/src/models.ts` 定义思考级别为 `"off" | "minimal" | "low" | "medium" | "high" | "xhigh" | "max"`，`getSupportedThinkingLevels()` 和 `clampThinkingLevel()` 函数处理模型能力映射。（`packages/ai/src/models.ts:900-932`）
