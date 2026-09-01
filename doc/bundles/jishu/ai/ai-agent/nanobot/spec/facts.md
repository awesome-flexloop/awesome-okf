---
type: spec
title: "Facts — nanobot"
---

# Facts — nanobot

本文件记录从 nanobot 源码中提取的可验证事实。每条事实均标注源文件路径与行号。不含推断性词汇。

## 项目元数据

- **F-001**: 包名为 `nanobot-ai`，版本为 `0.3.0`，描述为 "A lightweight personal AI assistant framework"。`pyproject.toml:2-4`
- **F-002**: 要求 Python `>=3.11`，许可证为 MIT，作者为 Xubin Ren 和 the nanobot contributors。`pyproject.toml:6-11`
- **F-003**: 控制台脚本入口为 `nanobot = "nanobot.cli.entry:main"`。`pyproject.toml:109-110`
- **F-004**: 构建系统使用 hatchling，构建后端为 `hatchling.build`。`pyproject.toml:117-119`
- **F-005**: 自定义构建钩子位于 `hatch_build.py`，在 `[tool.hatch.build.hooks.custom]` 中注册。`pyproject.toml:124-125`
- **F-006**: 打包包含 `nanobot/web/dist/**/*` 作为 artifacts，由 `cd webui && bun run build` 产出。`pyproject.toml:133-141`
- **F-007**: ruff 行长度限制为 100，目标 Python 版本为 py311，启用规则 E/F/I/N/W，忽略 E501。`pyproject.toml:162-168`
- **F-008**: basedpyright 类型检查模式为 strict，Python 版本为 3.11。`pyproject.toml:170-174`
- **F-009**: pytest 配置 `asyncio_mode = "auto"`，测试路径为 `tests` 和 `nanobot/channels`。`pyproject.toml:176-178`
- **F-010**: 覆盖率要求 `fail_under = 75`。`pyproject.toml:184-185`

## 核心依赖

- **F-011**: 核心依赖包括 `typer>=0.20.0`（CLI 框架）、`anthropic>=0.100.0`、`pydantic>=2.12.0`、`websockets>=15.0,<17.0`、`httpx[socks]>=0.28.0`、`mcp>=1.26.0`、`openai>=2.8.0`、`tiktoken>=0.12.0`、`jinja2>=3.1.0`、`dulwich>=0.22.0`、`rich>=14.0.0`、`croniter>=6.0.0`、`prompt-toolkit>=3.0.50`。`pyproject.toml:25-62`
- **F-012**: 可选依赖组包括 `api`（aiohttp）、`azure`（azure-identity）、`bedrock`（boto3）、`langfuse`、`olostep`、`dev`（pytest、ruff、basedpyright 等）。`pyproject.toml:64-107`

## 包初始化与版本

- **F-013**: `nanobot/__init__.py` 通过 `_resolve_version()` 读取已安装包版本，若包未安装则回退到读取 `pyproject.toml` 中的版本，最终回退为 `"0.3.0"`。`nanobot/__init__.py:37-54`
- **F-014**: `__version__` 由 `_resolve_version()` 赋值，`__logo__` 为 `"🐈"`。`nanobot/__init__.py:54-55`
- **F-015**: `nanobot/__init__.py` 使用 `_LAZY_EXPORTS` 字典实现延迟导入，公开导出 `Nanobot`、`RunResult`、`RunStream`、`StreamEvent` 等符号。`nanobot/__init__.py:57-91`
- **F-016**: `python -m nanobot` 入口调用 `nanobot.cli.entry:main`。`nanobot/__main__.py:1-8`

## Nanobot SDK 主类

- **F-017**: `Nanobot` 类位于 `nanobot/nanobot.py`，是编程式门面，持有 `AgentLoop`、`Config` 和 `MCPProvider`。`nanobot/nanobot.py:66-88`
- **F-018**: `Nanobot.from_config()` 接受 `config_path`、`workspace`、`model`、`model_preset` 参数，从配置文件创建实例。`nanobot/nanobot.py:90-140`
- **F-019**: `Nanobot` 暴露三个客户端属性：`sessions`（SessionClient）、`memory`（MemoryClient）、`runtime`（RuntimeClient）。`nanobot/nanobot.py:86-88`
- **F-020**: `Nanobot.run()` 方法接受 `message`、`session_key`（默认 `"sdk:default"`）、`channel`（默认 `"cli"`）、`chat_id`、`sender_id`、`media`、`ephemeral`、`attributes`、`hooks`、`model`、`model_preset` 参数，返回 `RunResult`。`nanobot/nanobot.py:142-201`
- **F-021**: `Nanobot.run_streamed()` 返回 `RunStream` 对象，内部使用 `asyncio.Queue(maxsize=256)` 传递 `StreamEvent`。`nanobot/nanobot.py:203-306`
- **F-022**: `Nanobot.stream()` 是异步生成器，yield `StreamEvent`。`nanobot/nanobot.py:308-343`
- **F-023**: `Nanobot` 支持异步上下文管理器协议（`__aenter__`/`__aexit__`），退出时调用 `aclose()` 释放资源。`nanobot/nanobot.py:345-357`

## CLI 入口层

- **F-024**: `nanobot/cli/entry.py` 的 `main()` 函数是控制台入口，通过 `_native_tui_candidate()` 判断是否可以仅加载 TUI 快速路径。`nanobot/cli/entry.py:35-51`
- **F-025**: 当参数为 `agent` 且不含 `--classic`、`--no-tui`、`-m`、`--message` 时，`main()` 走快速 TUI 路径，仅导入 typer 和 `nanobot.cli.agent.agent`。`nanobot/cli/entry.py:10-21,38-47`
- **F-026**: 非 TUI 快速路径时，`main()` 导入 `nanobot.cli.commands.app` 并执行。`nanobot/cli/entry.py:49-51`
- **F-027**: `nanobot/cli/entry.py` 在 Windows 上配置 UTF-8 控制台编码。`nanobot/cli/entry.py:24-32`

## CLI Agent 命令

- **F-028**: `agent()` 函数使用 typer 定义，接受 `--message/-m`、`--session/-s`、`--workspace/-w`、`--config/-c`、`--markdown/--no-markdown`、`--logs/--no-logs`、`--classic/--no-tui`、`--theme` 选项。`nanobot/cli/agent.py:54-80`
- **F-029**: 当无 message 且非 classic 模式时，启动原生 TUI（调用 `launch_tui()`），要求交互式终端。`nanobot/cli/agent.py:86-118`
- **F-030**: classic 模式下单发消息使用 `agent_loop.process_direct()` 直接调用，不经过 bus。`nanobot/cli/agent.py:237-268`
- **F-031**: classic 交互模式下，CLI 通过 `MessageBus` 发布 `InboundMessage`，并通过 `bus.consume_outbound()` 消费响应。`nanobot/cli/agent.py:270-442`
- **F-032**: `agent.py` 使用 `_CLASSIC_DEPENDENCIES` 字典实现延迟导入，避免加载 TUI 时引入 classic agent 栈。`nanobot/cli/agent.py:25-45`

## WebUI CLI 命令

- **F-033**: `webui()` 函数接受 `--port/-p`、`--gateway-port`、`--workspace/-w`、`--config/-c`、`--background`（已废弃）、`--dev`、`--no-open`、`--yes/-y` 选项。`nanobot/cli/webui.py:73-99`
- **F-034**: WebUI CLI 通过 `GatewayInstance.resolve()` 和 `GatewayClientLease` 管理共享本地网关生命周期。`nanobot/cli/webui.py:225-234`
- **F-035**: `--dev` 模式启动 Vite 开发服务器，通过 `run_webui_dev_server()` 作为 sidecar 运行。`nanobot/cli/webui.py:304-327`
- **F-036**: `nanobot webui --background` 已废弃，命令会提示使用 `nanobot gateway --background`。`nanobot/cli/webui.py:82-86,110-126`

## 消息总线

- **F-037**: `MessageBus` 类位于 `nanobot/bus/queue.py`，持有两个 `asyncio.Queue`：`inbound`（类型 `InboundMessage`）和 `outbound`（类型 `OutboundMessage`）。`nanobot/bus/queue.py:8-18`
- **F-038**: `MessageBus` 提供 `publish_inbound()`、`consume_inbound()`、`publish_outbound()`、`consume_outbound()` 四个异步方法。`nanobot/bus/queue.py:20-34`
- **F-039**: `MessageBus` 提供 `inbound_size` 和 `outbound_size` 只读属性，返回队列中待处理消息数量。`nanobot/bus/queue.py:36-44`

## SDK 类型系统

- **F-040**: `StreamEventType` 是字面量类型联合，包含 10 种事件类型：`run.started`、`text.delta`、`text.completed`、`reasoning.delta`、`reasoning.completed`、`tool.started`、`tool.completed`、`tool.failed`、`run.completed`、`run.failed`。`nanobot/sdk/types.py:11-22`
- **F-041**: 10 个 `STREAM_EVENT_*` 常量分别对应上述事件字符串值。`nanobot/sdk/types.py:24-46`
- **F-042**: `RunResult` 是使用 `@dataclass(slots=True)` 的数据类，字段包括 `content`、`tools_used`、`messages`、`usage`、`stop_reason`、`error`、`metadata`。`nanobot/sdk/types.py:49-59`
- **F-043**: `StreamEvent` 是 `@dataclass(slots=True)`，字段包括 `type`、`delta`、`content`、`result`、`name`、`tool_call_id`、`arguments`、`iteration`、`resuming`、`usage`、`error`、`metadata`。`nanobot/sdk/types.py:62-77`
- **F-044**: `SessionSnapshot` 数据类包含 `key`、`messages`、`metadata`、`created_at`、`updated_at`，提供 `to_dict()` 方法。`nanobot/sdk/types.py:80-98`
- **F-045**: `SessionInfo` 数据类包含 `key`、`created_at`、`updated_at`、`title`、`preview`、`path`，提供 `to_dict()` 方法。`nanobot/sdk/types.py:101-121`

## WebUI 开发服务器

- **F-046**: `nanobot/webui/dev.py` 定义 Vite 开发服务器常量 `WEBUI_DEV_HOST = "127.0.0.1"` 和 `WEBUI_DEV_PORT = 5173`。`nanobot/webui/dev.py:19-20`
- **F-047**: `WebUIDevServer` 类包装 `subprocess.Popen`，提供 `ensure_running()` 和 `stop()` 方法。`nanobot/webui/dev.py:27-54`
- **F-048**: `start_webui_dev_server()` 设置 `NANOBOT_API_URL` 环境变量指向网关目标 URL，等待 Vite 端口就绪（默认 15 秒超时）。`nanobot/webui/dev.py:124-192`
- **F-049**: 构建运行器优先使用 `bun`，不可用时回退到 `npm`。`nanobot/webui/dev.py:149-153`

## 构建钩子

- **F-050**: `hatch_build.py` 的 `WebUIBuildHook` 在 editable 安装时跳过 WebUI 构建。`hatch_build.py:54-59`
- **F-051**: 环境变量 `NANOBOT_SKIP_WEBUI_BUILD=1` 跳过构建，`NANOBOT_FORCE_WEBUI_BUILD=1` 强制重建。`hatch_build.py:61-63,73`
- **F-052**: 当 `webui/package.json` 不存在时，构建钩子假定 `nanobot/web/dist/` 已预构建。`hatch_build.py:65-69`

## Docker 与部署

- **F-053**: Dockerfile 使用多阶段构建，第一阶段 `node:24-bookworm-slim` 构建 WebUI，第二阶段基于 `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`。`Dockerfile:1-10`
- **F-054**: Docker 容器以非 root 用户 `nanobot`（UID 1000）运行，通过 entrypoint 在启动时 chown 数据目录后降权。`Dockerfile:57-70`
- **F-055**: Docker 暴露端口 `18790`（网关健康检查）和 `8765`（WebUI/WebSocket）。`Dockerfile:77`
- **F-056**: docker-compose.yml 定义三个服务：`nanobot-gateway`（端口 18790/8765）、`nanobot-api`（端口 8900）、`nanobot-cli`（profile: cli）。`docker-compose.yml:21-62`
- **F-057**: docker-compose 默认丢弃所有 Linux capabilities，仅添加 `CHOWN`、`SETGID`、`SETUID`，并启用 `no-new-privileges:true`。`docker-compose.yml:9-19`
- **F-058**: Docker 构建参数 `NANOBOT_CHANNELS` 默认为 `whatsapp`，可逗号分隔预安装频道依赖。`Dockerfile:46-49`

## 测试基础设施

- **F-059**: `conftest.py` 提供自动 fixture `_isolate_sessions_root`，将会话存储重定向到临时目录，避免测试写入真实 home。`conftest.py:26-49`
- **F-060**: `conftest.py` 在 Windows 上替换 `ssl.create_default_context` 以使用系统 CA 证书，避免每次客户端重新解析 certifi CA 包。`conftest.py:52-89`

## TUI（终端 UI）

- **F-061**: TUI 包名为 `@nanobot/tui`，版本 `0.1.0`，使用 Bun 运行 TypeScript，依赖 `@opentui/core` 版本 `0.5.3`。`tui/package.json:1-14`
- **F-062**: TUI 脚本包括 `start`（`bun src/index.ts`）、`build`（`bun scripts/build.ts`）、`check`（`tsc --noEmit`）、`test`（`bun test`）。`tui/package.json:6-11`
- **F-063**: `NanobotTui` 类位于 `tui/src/app.ts`，构造时创建 CliRenderer、Transcript、CommandMenu、SessionMenu、MentionMenu、BranchMenu、ContextPanel、DiffViewer、QueuePreview、RuntimeControls 等组件。`tui/src/app.ts:372-741`
- **F-064**: TUI 支持暗色和亮色两套调色板（`DARK`/`LIGHT`），主色调为橙色 `#EF8E30`（暗色）/`#B94D0B`（亮色）。`tui/src/app.ts:128-160`
- **F-065**: TUI 本地斜杠命令包括 `/sessions`、`/new-chat`、`/context`、`/diff`、`/branch`、`/detach`、`/exit`。`tui/src/app.ts:167-210`
- **F-066**: `NanobotClient` 位于 `tui/src/protocol.ts`，通过 WebSocket 连接网关，支持自动重连（指数退避，最大 8 秒）。`tui/src/protocol.ts:850-1019`
- **F-067**: TUI 协议定义 `InboundEvent` 联合类型，包含 `ready`、`attached`、`message_accepted`、`user_message`、`message`、`file_edit`、`delta`、`stream_end`、`reasoning_delta`、`reasoning_end`、`turn_end`、`goal_status`、`goal_state`、`session_updated`、`runtime_model_updated`、`turn_model_updated`、`error` 共 17 种事件。`tui/src/protocol.ts:57-135`
- **F-068**: TUI 出站事件类型包括 `new_chat`、`fork_chat`、`attach`、`set_workspace_scope`、`message`。`tui/src/protocol.ts:137-151`
- **F-069**: `host.ts` 定义 `TuiHost` 接口，有两种实现：`StandaloneHost`（独立运行）和 `HerdrHost`（嵌入 Herdr 终端时报告代理状态）。`tui/src/host.ts:11-17,41-168`
- **F-070**: `createTuiHost()` 检查环境变量 `HERDR_ENV=1` 和 `HERDR_PANE_ID` 决定使用哪种 host 实现。`tui/src/host.ts:185-192`
- **F-071**: TUI 退出时打印会话恢复命令 `nanobot agent --session websocket:<chatId>`。`tui/src/app.ts:348-351`

## WebUI（浏览器 UI）

- **F-072**: WebUI 包名为 `nanobot-webui`，使用 React 18、Vite 5、TypeScript 5，私有包。`webui/package.json:1-14`
- **F-073**: WebUI 依赖包括 `@radix-ui/react-*` 组件库、`react`/`react-dom`、`i18next`/`react-i18next`、`lucide-react`、`streamdown`、`remark-gfm`/`remark-math`/`rehype-katex`、`diff`、`qrcode`、`tailwind-merge`。`webui/package.json:15-38`
- **F-074**: WebUI 构建命令为 `tsc -p tsconfig.build.json && vite build`，测试命令为 `vitest run`。`webui/package.json:7-12`
- **F-075**: `App.tsx` 默认导出 `App` 组件，启动状态机包含 `loading`、`error`、`auth`、`ready` 四种状态。`webui/src/App.tsx:90-102,808-1015`
- **F-076**: WebUI 通过 `fetchBootstrap()` 获取引导信息，建立 WebSocket 连接，使用 Bearer token 认证。`webui/src/App.tsx:847-902`
- **F-077**: WebUI Shell 视图包括 `chat`、`settings`、`apps`、`automations`、`skills` 五种。`webui/src/App.tsx:118`
- **F-078**: WebUI 设置区域包含 12 个分区：overview、appearance、models、image、voice、browser、channels、apps、automations、skills、runtime、advanced。`webui/src/App.tsx:159-172`
- **F-079**: `api.ts` 定义 WebUI REST API 客户端，所有请求通过 `Authorization: Bearer <token>` 头部认证，基础路径为 `/api/`。`webui/src/lib/api.ts:82-128`
- **F-080**: `api.ts` 中的 API 函数覆盖会话管理（`listSessions`、`deleteSession`、`fetchWebuiThread`）、设置（`fetchSettings`、`updateSettings`）、模型配置（`createModelConfiguration`、`updateModelConfiguration`、`deleteModelConfiguration`）、频道（`configureChannel`、`validateChannel`、`startChannelConnect`）、MCP（`fetchMcpPresets`、`saveCustomMcpServer`）、技能（`fetchSkills`、`installMarketplaceSkill`）、自动化（`fetchAutomations`、`updateAutomation`）、配对（`fetchPairingRequests`、`runPairingAction`）等。`webui/src/lib/api.ts:183-1099`

## WebSocket 通道

- **F-081**: WebSocket 通道默认绑定 `127.0.0.1:8765`，路径为 `/`，`websocketRequiresToken` 默认为 `true`。`docs/websocket.md:22-36`
- **F-082**: WebSocket 最大入站消息默认为 37748736 字节（36 MB），可接受最多 4 张 8 MB base64 编码图片。`docs/websocket.md:220`
- **F-083**: 签发的令牌为单次使用，TTL 默认为 300 秒，未完成令牌上限为 10000。`docs/websocket.md:233,360-362`
- **F-084**: `chat_id` 格式为 `^[A-Za-z0-9_:-]{1,64}$`，作为能力令牌使用。`docs/websocket.md:394`

## 内存系统

- **F-085**: 内存分为两层：会话历史（`<config-dir>/sessions/<workspace-id>/*.jsonl`）和长期记忆（`<workspace>/memory/MEMORY.md` 和 `history.jsonl`）。`docs/concepts.md:127-131`
- **F-086**: Dream 是周期性整合任务，读取 `history.jsonl`、`SOUL.md`、`USER.md`、`MEMORY.md`，对长期记忆文件进行外科手术式编辑。`docs/memory.md:50-63`
- **F-087**: `history.jsonl` 每行是一个 JSON 对象，包含 `cursor`、`timestamp`、`content` 字段，采用仅追加方式。`docs/memory.md:36-48`
- **F-088**: Dream 配置位于 `agents.defaults.dream`，支持 `intervalH`（默认 2 小时）、`cron`、`modelOverride` 字段。`docs/memory.md:181-206`

## 架构文档

- **F-089**: AGENTS.md 描述核心数据流：Channels 发布 `InboundMessage` 到 MessageBus → AgentLoop 消费 → AgentRunner 执行 LLM 对话 → 发布 `OutboundMessage` 回频道。`AGENTS.md:33-38`
- **F-090**: AGENTS.md 列出的子系统包括 Agent Loop、LLM Providers、Channels、Tools、Memory、Session Management、Config、WebUI、API Server、Command Router、Heartbeat、Pairing、Skills、Security。`AGENTS.md:40-55`
- **F-091**: AGENTS.md 记录工具通过 `pkgutil` 扫描 + entry-point 插件自动发现。`AGENTS.md:45`
- **F-092**: AGENTS.md 记录频道是自包含包，通过 `pkgutil` 扫描自动发现，包括 Telegram、Discord、Slack、Feishu、Matrix、WhatsApp、QQ、WeChat、WeCom、DingTalk、Email、MoChat、MS Teams、WebSocket、Mattermost。`AGENTS.md:44`
- **F-093**: 配置基于 Pydantic，从 `~/.nanobot/config.json` 加载，支持 camelCase 和 snake_case 键。`AGENTS.md:48`
- **F-094**: API Server 提供 OpenAI 兼容的 HTTP API，端点为 `/v1/chat/completions` 和 `/v1/models`。`AGENTS.md:50`
