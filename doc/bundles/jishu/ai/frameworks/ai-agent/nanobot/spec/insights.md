---
type: spec
scope: nanobot
name: insights
version: "0.1.0"
source: local
description: 从 nanobot 源码中提炼的架构与工程洞察，包含陈述、证据、反常识点和行动建议。
---

# Insights — nanobot

## 洞察一：三端共享同一 Agent 核心，入口分层而非分叉

**陈述**

nanobot 的 CLI（classic Python prompt）、原生 TUI（Bun + TypeScript）和 WebUI（React）并非三套独立实现，而是共享同一个 AgentLoop 核心和 MessageBus 消息总线。差异仅在传输层：classic CLI 直接在进程内调用 `process_direct()` 或经 bus 收发；TUI/WebUI 通过 WebSocket 协议连接到网关进程。

**证据**

- `Nanobot` SDK 门面持有 `AgentLoop`，`run()` 内部调用 `self._loop.process_direct()`。F-017、F-020
- classic CLI 单发模式直接调用 `agent_loop.process_direct()`，交互模式通过 `MessageBus.publish_inbound()` / `consume_outbound()` 收发。F-030、F-031
- TUI 的 `NanobotClient` 通过 WebSocket 连接网关，协议定义 17 种入站事件和 5 种出站事件。F-066、F-067、F-068
- WebUI 的 `App.tsx` 通过 `fetchBootstrap()` 获取 WebSocket URL 和 token，建立连接后通过同一协议通信。F-076
- `MessageBus` 仅持有两个 `asyncio.Queue`，是通道与核心之间的唯一解耦层。F-037、F-038

**反常识**

TUI 并非 Python 渲染的终端界面，而是一个独立的 Bun/TypeScript 应用（`@nanobot/tui`，依赖 `@opentui/core`），通过 WebSocket 与 Python 网关通信。这意味着终端用户体验与浏览器体验共享同一套网络协议，而非 Python 进程内调用。

**行动**

- 扩展 Agent 能力时，只需修改 Python 核心（AgentLoop/Tools/Providers），三端自动受益。
- 调试协议问题时，TUI 和 WebUI 可互换连接同一网关，便于隔离前端与后端缺陷。
- 新增客户端时，参考 `tui/src/protocol.ts` 的类型定义实现 WebSocket 协议即可。

## 洞察二：启动性能通过延迟导入和快速路径分层优化

**陈述**

nanobot 的 CLI 入口 `main()` 实现了两级启动优化：当检测到 `nanobot agent`（无 `--classic`、`-m` 等参数）时，仅导入 typer 和 `agent` 模块走 TUI 快速路径，避免加载完整的 classic agent 依赖图（Provider、ToolRegistry、CronService 等）。同时，`nanobot/__init__.py` 使用 `_LAZY_EXPORTS` 字典实现公共 API 的延迟导入，`agent.py` 也通过 `_CLASSIC_DEPENDENCIES` 字典延迟加载 classic 栈。

**证据**

- `entry.py` 的 `_native_tui_candidate()` 检查参数，快速路径仅导入 `nanobot.cli.agent.agent`。F-024、F-025
- `agent.py` 的 `_CLASSIC_DEPENDENCIES` 字典将 `AgentLoop`、`StreamRenderer` 等符号延迟到实际需要时才导入。F-032
- `__init__.py` 的 `__getattr__` 在首次访问 `Nanobot` 等符号时才动态导入对应模块。F-015
- 非快速路径才导入完整的 `nanobot.cli.commands.app`。F-026

**反常识**

`nanobot/cli/agent.py` 文件顶部并不导入 `AgentLoop`、`MessageBus`、`make_provider` 等核心运行时组件。这些导入被推迟到 classic 模式分支内部（第 120-139 行），使得 TUI 启动时不加载任何 LLM provider、工具注册表或 cron 服务代码。这是一种"按入口裁剪导入图"的策略，而非传统的"模块级全量导入"。

**行动**

- 新增 CLI 子命令时，若其仅服务于 classic 模式，应将重依赖放入函数内部导入。
- 在 `__init__.py` 中新增公共导出时，必须同时注册到 `_LAZY_EXPORTS` 字典。
- 测量启动时间时，应区分 TUI 快速路径和 classic 全量路径。

## 洞察三：WebUI 构建产物嵌入 Python Wheel，前后端版本强绑定

**陈述**

nanobot 的 React WebUI 源码位于 `webui/` 目录，但其构建产物 `nanobot/web/dist/` 被声明为 hatch 构建 artifact 并打包进 Python wheel。自定义构建钩子 `WebUIBuildHook` 在非 editable 安装时自动执行 `bun run build`（或 `npm run build`），确保发布包始终包含与 Python 代码匹配的前端版本。Docker 多阶段构建也在第一阶段编译 WebUI，再将产物复制到 Python 运行时镜像。

**证据**

- `pyproject.toml` 的 `[tool.hatch.build]` 将 `nanobot/web/dist/**/*` 列入 artifacts。F-006
- `hatch_build.py` 的 `WebUIBuildHook.initialize()` 在非 editable 安装时调用 `build_webui_bundle()`。F-050
- editable 安装跳过 WebUI 构建，开发者使用 `bun run dev` 的 Vite HMR。F-050
- Dockerfile 第一阶段 `node:24-bookworm-slim` 执行 `npm run build`，产物复制到 `/app/nanobot/web/dist/`。F-053
- `nanobot/webui/dev.py` 的 Vite 开发服务器在 `127.0.0.1:5173` 运行，代理 API/WS 到网关。F-046、F-048

**反常识**

WebUI 并非独立部署的前端应用，而是作为 Python 包的静态资源由网关直接提供服务。这意味着用户 `pip install nanobot-ai` 后无需单独安装 Node.js 或构建前端即可使用浏览器界面。但从源码安装（editable 模式）时，WebUI 不会自动构建，需开发者手动运行 `bun run build` 或使用 `nanobot webui --dev`。

**行动**

- 发布新版本时，hatch 构建钩子会自动打包最新 WebUI，无需手动操作。
- 从源码开发时，使用 `nanobot webui --dev` 启动 Vite HMR，无需反复构建。
- CI 中验证 wheel 内容时应检查 `nanobot/web/dist/index.html` 是否存在。
- Docker 部署时，`NANOBOT_CHANNELS` 构建参数控制预装频道，与 WebUI 构建无关。

## 洞察四：安全模型以最小权限和纵深防御为核心

**陈述**

nanobot 在多个层面实施最小权限原则：Docker 容器以非 root 用户（UID 1000）运行，docker-compose 默认丢弃所有 Linux capabilities 仅保留 chown/setuid/setgid 并启用 `no-new-privileges`；WebSocket 通道默认绑定 `127.0.0.1` 且要求令牌认证；`chat_id` 被明确文档化为能力令牌（capability）；静态令牌使用 `hmac.compare_digest` 进行时序安全比较。

**证据**

- Dockerfile 创建 `nanobot` 用户（UID 1000），entrypoint 以 root 启动执行 chown 后通过 setpriv 降权。F-054
- docker-compose 配置 `cap_drop: [ALL]`，仅 `cap_add: [CHOWN, SETGID, SETUID]`，`security_opt: [no-new-privileges:true]`。F-057
- WebSocket 默认 `websocketRequiresToken: true`，绑定 `127.0.0.1`。F-081
- WebSocket 签发令牌单次使用、TTL 300 秒、上限 10000 个。F-083
- 文档明确 `chat_id` 是能力令牌，认证是唯一防线。F-084
- 当 WebSocket host 为 `0.0.0.0` 时，通道拒绝启动除非配置了 token/tokenIssueSecret/trustedProxyAuth。

**反常识**

尽管 nanobot 是"个人 AI 助手框架"，其默认配置并非"开放便利"而是"本地安全"：WebSocket 默认要求令牌、默认绑定 loopback、Docker 默认非 root。要将服务暴露到 LAN 或公网，用户必须显式修改配置并设置认证密钥，而非通过关闭安全选项来实现。这种"默认安全，按需开放"的设计与许多自托管工具的"默认开放"策略相反。

**行动**

- Docker 部署时必须将 `gateway.host` 和 `channels.websocket.host` 设为 `0.0.0.0` 并配置 `tokenIssueSecret`。
- 多租户场景下，需在 nanobot 之外实现按用户的认证网关，因为 `chat_id` 本身不做租户隔离。
- 使用 Cloudflare Tunnel 时，配置 `trustedProxyAuth` 实现无令牌引导，但必须确保 nanobot 端口不直接暴露。
