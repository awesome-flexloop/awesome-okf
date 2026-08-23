---
type: spec
scope: opencode
name: facts
version: "0.1.0"
source: local
description: "OpenCode 项目源码事实清单，基于 2026-08-23 代码快照"
---

# OpenCode 源码事实清单

以下事实均来自源码文件，标注文件路径与行号。不包含推断性描述。

## 项目元数据与构建

- **F-001**: 项目名称为 `opencode`，描述为 "AI-powered development tool"，私有包，使用 ESM 模块类型。`package.json:3-6`
- **F-002**: 包管理器固定为 `bun@1.3.14`。`package.json:7`
- **F-003**: 仓库地址为 `https://github.com/anomalyco/opencode`，许可证为 MIT。`package.json:120-124`
- **F-004**: 使用 Turbo 2.10.2 作为 monorepo 构建编排工具。`package.json:110`
- **F-005**: 使用 SST 4.13.1 作为基础设施即代码部署框架。`package.json:82`
- **F-006**: 工作区包含 `packages/*`、`packages/console/*`、`packages/stats/*`、`packages/sdk/js`、`packages/slack`。`package.json:26-32`
- **F-007**: TypeScript 配置继承自 `@tsconfig/bun/tsconfig.json`。`tsconfig.json:3`
- **F-008**: Bun 配置启用精确版本安装（`exact = true`），并设置最低发布时间为 3 天（259200 秒）。`bunfig.toml:1-5`
- **F-009**: 根目录测试被禁止，`bunfig.toml` 中 `test.root` 指向不存在的 `./do-not-run-tests-from-root`。`bunfig.toml:7-8`
- **F-010**: Prettier 配置为不使用分号（`semi: false`），打印宽度 120。`package.json:125-128`

## 核心包结构

- **F-011**: `@opencode-ai/core` 版本为 1.18.21，导出路径使用通配符 `./*` 映射到 `./src/*.ts`。`packages/core/package.json:3-4,18-24`
- **F-012**: `opencode` 主包版本为 1.18.21，二进制入口为 `./bin/opencode`。`packages/opencode/package.json:3-4,18-20`
- **F-013**: `@opencode-ai/tui` 包版本为 1.18.21，基于 `@opentui/core`、`@opentui/solid` 和 `solid-js` 构建终端 UI。`packages/tui/package.json:3-4,55-57,66`
- **F-014**: CLI 入口使用 yargs 18.0.0 解析命令行参数，脚本名为 `opencode`。`packages/opencode/src/index.ts:1,45-47`
- **F-015**: CLI 注册的子命令包括 run、generate、serve、debug、mcp、github、web、pr、session、db、agent、providers、models、upgrade、uninstall、stats、export、import、attach、tui、acp、plug、account。`packages/opencode/src/index.ts:81-103`
- **F-016**: CLI 全局选项包括 `--print-logs`、`--log-level`（DEBUG/INFO/WARN/ERROR）、`--pure`（无外部插件运行）。`packages/opencode/src/index.ts:53-65`

## 运行时与框架

- **F-017**: 使用 Effect 4.0.0-beta.83 作为核心函数式编程框架。`package.json:66`
- **F-018**: 使用 AI SDK 6.0.168（`ai` 包）作为 LLM 抽象层。`package.json:67`
- **F-019**: 使用 Hono 4.10.7 作为 HTTP 服务器框架。`package.json:69`
- **F-020**: 使用 Zod 4.1.8 进行 schema 验证。`package.json:80`
- **F-021**: 使用 Drizzle ORM 1.0.0-rc.2 配合 SQLite 进行数据持久化。`package.json:64-65`
- **F-022**: Core 包通过条件导入支持 Bun 和 Node 双运行时，`#sqlite`、`#pty`、`#fff` 均有 bun/node 双实现。`packages/core/package.json:25-40`
- **F-023**: 使用 `@lydell/node-pty` 1.2.0-beta.12 实现伪终端功能。`package.json:95`
- **F-024**: 使用 SolidJS 1.9.10 作为 TUI 和 Web 的 UI 框架。`package.json:92`

## V2 会话核心

- **F-025**: V2 会话将 prompt 录入与模型执行分离，`SessionV2.prompt(...)` 先写入持久化 `session_input` 行，再调度 `SessionExecution.wake(sessionID)`。`AGENTS.md:153`
- **F-026**: `sessions.create` 支持可选 ID，省略时自动生成；复用已有 ID 返回现有会话。`specs/v2/session.md:8-11`
- **F-027**: `sessions.prompt` 支持 `resume?: boolean`，省略或 true 时录入后调度执行，false 时仅录入。`specs/v2/session.md:13-20`
- **F-028**: `sessions.interrupt(sessionID)` 中断当前进程上的活跃执行，等待清理完成，空闲或缺失会话为空操作。`specs/v2/session.md:22-27`
- **F-029**: `sessions.active()` 返回当前进程拥有的前台会话排干记录，进程重启后为空。`specs/v2/session.md:29-33`
- **F-030**: `SessionExecution` 和 `SessionStore` 为进程全局；`SessionRunner`、目录、模型解析器、工具注册表按 Location 缓存。`specs/v2/session.md:48`
- **F-031**: 每个 provider turn 仅发起一次显式 `llm.stream(request)` 调用。`specs/v2/session.md:50`
- **F-032**: 进程全局 `SessionRunCoordinator` 序列化每个本地会话的执行，同时允许不同会话并发运行。`specs/v2/session.md:167`

## V2 工具系统

- **F-033**: V2 工具使用不透明类型 `Tool.Definition<Input, Output>`，通过 `Tool.make` 构造，包含 description、input codec、output codec、execute 函数。`specs/v2/tools.md:7-27`
- **F-034**: 工具调用上下文包含 `sessionID`、`agent`、`assistantMessageID`、`toolCallID` 四个字段。`specs/v2/tools.md:40-46`
- **F-035**: 工具注册时以 record key 作为模型面向名称，Location 注册优先于进程应用注册。`specs/v2/tools.md:59-65,90`
- **F-036**: 工具执行流程为：解析注册→解码输入→调用执行→编码输出→投影为模型内容→限制输出大小→持久化结算。`specs/v2/tools.md:137-146`
- **F-037**: 内置工具包括 read、bash、apply_patch、grep、glob、edit、write、webfetch、websearch、todo、todowrite、task、skill、lsp 等。`packages/opencode/src/tool/` 目录文件列表

## V2 配置系统

- **F-038**: V2 配置文件名为 `opencode.json` 或 `opencode.jsonc`，从全局配置目录、祖先项目目录和 `.opencode` 目录发现。`specs/v2/config.md:16`
- **F-039**: V2 不支持旧版 `config.json` 文件名。`specs/v2/config.md:16`
- **F-040**: 配置字段 `plugin` 重命名为复数 `plugins`，支持包字符串或 `{ package, options? }` 对象条目。`specs/v2/config.md:92-108`
- **F-041**: 配置字段 `provider` 重命名为复数 `providers`，不保留旧版单数键的兼容别名。`specs/v2/config.md:175,206`
- **F-042**: 配置字段 `agent` 重命名为复数 `agents`，`permission` 重命名为 `permissions`，`snapshot` 重命名为 `snapshots`，`attachment` 重命名为 `attachments`。`specs/v2/config.md:248,294,119,127`
- **F-043**: MCP 配置嵌套在 `mcp.servers` 下，本地服务器使用 `type: "local"`，远程服务器使用 `type: "remote"`。`specs/v2/config.md:311-346`
- **F-044**: `.opencode/opencode.jsonc` 中配置了两个引用：`effect`（GitHub 仓库）和 `opencode-local`（本地路径）。`.opencode/opencode.jsonc:5-14`
- **F-045**: `.opencode/tui.json` 配置了 TUI 插件数组，包含一个默认禁用的 `tui-smoke.tsx` 插件。`.opencode/tui.json:1-18`

## 内置 Agent

- **F-046**: 内置两个主 agent：`build`（默认全权限开发 agent）和 `plan`（只读分析 agent）。`README.md:104-108`
- **F-047**: `plan` agent 默认拒绝文件编辑，运行 bash 命令前请求权限。`README.md:106-107`
- **F-048**: 包含一个 `general` 子 agent，用于复杂搜索和多步任务，可通过 `@general` 调用。`README.md:110-111`
- **F-049**: 按 `Tab` 键可在 build 和 plan agent 之间切换。`README.md:102`

## 部署与基础设施

- **F-050**: SST 配置中 app 名称为 `opencode`，生产环境移除策略为 `retain` 并启用保护，home 设置为 `cloudflare`。`sst.config.ts:4-9`
- **F-051**: SST 配置使用 AWS provider 7.30.0（区域 us-east-1）、Stripe 0.0.28、PlanetScale 0.4.1、Honeycomb 0.49.0。`sst.config.ts:11-27`
- **F-052**: 生产域名 `opencode.ai`，dev 阶段域名 `dev.opencode.ai`，其他阶段为 `${stage}.dev.opencode.ai`。`infra/stage.ts:1-5`
- **F-053**: 短域名生产为 `opncd.ai`，dev 为 `dev.opncd.ai`。`infra/stage.ts:36-39`
- **F-054**: API 部署为 Cloudflare Worker，域名为 `api.${domain}`，处理函数为 `packages/function/src/api.ts`。`infra/app.ts:13-15`
- **F-055**: Web 文档站使用 Astro 部署在 `docs.${domain}`，路径为 `packages/web`。`infra/app.ts:52-54`
- **F-056**: Web 应用部署为 Cloudflare StaticSite 在 `app.${domain}`，路径为 `packages/app`。`infra/app.ts:62-68`
- **F-057**: Console 控制台使用 SolidStart 部署在根域名，路径为 `packages/console/app`。`infra/console.ts:248-250`
- **F-058**: 数据湖使用 AWS S3 Tables（Iceberg 格式），通过 Kinesis Firehose 摄入，Athena 查询，单次查询扫描上限 2TB。`infra/lake.ts:16-19,64-78,160-196`
- **F-059**: 数据湖摄入服务为 ECS/Fargate 服务（ARM64，1 vCPU，4GB 内存），生产环境最小 2 副本最大 32 副本。`infra/lake.ts:218-239`
- **F-060**: Stats 应用部署为 SolidStart 在 `stats.${domain}`，使用独立的 `opencode-stats` PlanetScale 数据库。`infra/stats.ts:164-172,107-110`
- **F-061**: 密钥管理使用 SST Secret，包括 GITHUB_APP_ID、GITHUB_APP_PRIVATE_KEY、ADMIN_SECRET、DISCORD_SUPPORT_BOT_TOKEN、FEISHU_APP_ID 等。`infra/app.ts:3-10`

## GitHub Action

- **F-062**: GitHub Action 名称为 "opencode GitHub Action"，使用 composite 类型，品牌图标为 code，颜色为 orange。`github/action.yml:1-5`
- **F-063**: Action 输入参数包括 model（必填）、agent、share、prompt、use_github_token、mentions、variant、oidc_base_url。`github/action.yml:7-39`
- **F-064**: Action 触发关键词为 `/opencode` 或 `/oc`。`github/index.ts:247-248`
- **F-065**: Action 启动本地 opencode 服务器在 `127.0.0.1:4096`，通过 `createOpencodeClient` 连接。`github/index.ts:231-241`
- **F-066**: Action 支持三种场景：Issue（创建新分支并提 PR）、本地 PR（直接推送到分支）、Fork PR（推送到 fork 分支）。`github/index.ts:160-210`

## 包依赖架构

- **F-067**: 运行时依赖方向为 Schema → Core 和 Protocol → Server，Client 可依赖 Schema 和 Protocol 但不可依赖 Core 或 Server。`AGENTS.md:3`
- **F-068**: `sdk-next` 组合 Client、Core 和 Server，用于嵌入式场景。`AGENTS.md:3`
- **F-069**: 修改公共 Protocol 或 Server `HttpApi` 后需从 `packages/client` 运行 `bun run generate`，不可直接编辑 `src/generated`。`AGENTS.md:2`
- **F-070**: Core 包集成了 20+ AI SDK provider，包括 Anthropic、OpenAI、Google、Amazon Bedrock、Azure、Cerebras、Cohere、Groq、Mistral、xAI 等。`packages/core/package.json:64-83`

## 其他

- **F-071**: 默认分支为 `dev`，本地 `main` ref 可能不存在。`AGENTS.md:4-5`
- **F-072**: 分支名最多三个单词，用连字符分隔，不使用斜杠或类型前缀。`AGENTS.md:9`
- **F-073**: 提交信息遵循 Conventional Commits 格式 `type(scope): summary`，有效类型为 feat、fix、docs、chore、refactor、test。`AGENTS.md:15-17`
- **F-074**: 项目根目录无 `src/` 目录，所有源码位于 `packages/` 下各包子目录中。目录结构验证
- **F-075**: 项目无 `script/hooks/` 目录。目录结构验证
- **F-076**: CONTEXT.md 定义了 OpenCode 会话运行时的术语表，包括 System Context、Session History、Context Source、Context Epoch、Session Drain 等核心概念。`CONTEXT.md:1-200`
- **F-077**: `.opencode/env.d.ts` 声明了 `*.txt` 模块类型，默认导出为 string。`.opencode/env.d.ts:1-3`
- **F-078**: 项目使用 Husky 9.1.7 管理 git hooks，prepare 脚本运行 `husky`。`package.json:19,104`
- **F-079**: 使用 oxlint 1.60.0 作为代码检查工具，lint 脚本直接运行 `oxlint`。`package.json:15,105`
- **F-080**: 项目包含 17 个 patchedDependencies，包括 effect、solid-js、多个 AI SDK provider、@modelcontextprotocol/sdk 等。`package.json:146-163`
