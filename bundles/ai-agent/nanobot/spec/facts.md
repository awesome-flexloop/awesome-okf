# Nanobot 事实清单

> R 阶段产出。所有事实编号 F-xxx，仅记录源码中可验证的客观内容，不含推断。路径均相对于 nanobot 源码仓库根目录。

## 项目元数据

- F-001: 文件 pyproject.toml 第1-3行，`[project]` 中 `name = "nanobot-ai"`、`version = "0.3.0"`、`description = "A lightweight personal AI assistant framework"`
- F-002: 文件 pyproject.toml 第6行，`requires-python = ">=3.11"`
- F-003: 文件 pyproject.toml 第7行，`license = {text = "MIT"}`；第8-11行 authors 含 Xubin Ren 与 the nanobot contributors
- F-004: 文件 pyproject.toml 第25-62行，`dependencies` 列表包含 typer、anthropic、pydantic、pydantic-settings、websockets、websocket-client、httpx、ddgs、loguru、rich、qrcode、croniter、prompt-toolkit、questionary、mcp、openai、tiktoken、jinja2、dulwich 等
- F-005: 文件 pyproject.toml 第64-81行，`[project.optional-dependencies]` 定义 `api`(aiohttp)、`azure`(azure-identity)、`bedrock`(boto3)、`documents` 等 extras
- F-006: 文件 nanobot/__init__.py 第54行 `__version__ = _resolve_version()`；第55行 `__logo__ = "🐈"`；第37-43行 `_read_pyproject_version` 从 pyproject.toml 读 `project.version`

## 入口

- F-007: 文件 nanobot/__main__.py 第5行 `from nanobot.cli.entry import main`；第7-8行 `if __name__ == "__main__": main()`

## 顶层 SDK 门面（nanobot/nanobot.py）

- F-008: 文件 nanobot/nanobot.py 第1行 docstring `"High-level programmatic interface to nanobot."`
- F-009: 文件 nanobot/nanobot.py 第44-63行，`__all__` 导出 `Nanobot`、`RunResult`、`RunStream`、`SessionInfo`、`SessionSnapshot`、`STREAM_EVENT_*` 常量、`StreamEvent`、`StreamEventType`
- F-010: 文件 nanobot/nanobot.py 第66行 `class Nanobot`
- F-011: 文件 nanobot/nanobot.py 第76-88行 `Nanobot.__init__(self, loop: AgentLoop, *, config: Config | None = None, mcp_provider: MCPProvider | None = None)`；第86-88行依次赋值 `self.sessions = SessionClient(loop)`、`self.memory = MemoryClient(loop)`、`self.runtime = RuntimeClient(loop)`
- F-012: 文件 nanobot/nanobot.py 第90-98行 `@classmethod def from_config(config_path=None, *, workspace=None, model=None, model_preset=None) -> Nanobot`
- F-013: 文件 nanobot/nanobot.py 第142-156行 `async def run(self, message, *, session_key="sdk:default", channel="cli", chat_id="direct", sender_id="user", media=None, ephemeral=False, attributes=None, hooks=None, model=None, model_preset=None) -> RunResult`
- F-014: 文件 nanobot/nanobot.py 第203-217行 `async def run_streamed(...) -> RunStream`，内部创建 `asyncio.Queue(maxsize=256)`、`SDKStreamEmitter`、`SDKStreamingHook`、`SDKCaptureHook`
- F-015: 文件 nanobot/nanobot.py 第308-322行 `async def stream(...) -> AsyncIterator[StreamEvent]`，内部调用 `run_streamed` 后 `async for event in run.stream_events()`
- F-016: 文件 nanobot/nanobot.py 第345-351行 `async def aclose()`；第353-357行 `async def __aenter__`/`__aexit__`

## 消息总线（nanobot/bus/）

- F-017: 文件 nanobot/bus/queue.py 第8行 `class MessageBus`
- F-018: 文件 nanobot/bus/queue.py 第16-18行 `__init__` 定义 `self.inbound: asyncio.Queue[InboundMessage]` 与 `self.outbound: asyncio.Queue[OutboundMessage]`
- F-019: 文件 nanobot/bus/queue.py 第20-22行 `async publish_inbound`、第24-26行 `async consume_inbound`、第28-30行 `async publish_outbound`、第32-34行 `async consume_outbound`；第36-43行 `inbound_size`/`outbound_size` 两个 property
- F-020: 文件 nanobot/bus/__init__.py 第3-4行从 events 导入 `InboundMessage`/`OutboundMessage`、从 queue 导入 `MessageBus`；第6行 `__all__ = ["MessageBus", "InboundMessage", "OutboundMessage"]`
- F-021: 文件 nanobot/bus/events.py 第24-49行 `@dataclass class InboundMessage`，字段 `channel/sender_id/chat_id/content/timestamp/media/metadata/session_key_override/require_existing_session/input_role`；第39-42行 `session_key` property 返回 `session_key_override` 或 `f"{channel}:{chat_id}"`；第44-49行 `is_user_input` property
- F-022: 文件 nanobot/bus/events.py 第52-68行 `@dataclass class OutboundMessage`，字段 `channel/chat_id/content/reply_to/media/metadata/buttons/event`
- F-023: 文件 nanobot/bus/events.py 第13行 `OUTBOUND_META_AGENT_UI = "_agent_ui"`；第17-21行 `INBOUND_META_RUNTIME_CONTROL = "_runtime_control"` 等内部元数据键
- F-024: 文件 nanobot/bus/outbound_events.py 第17-18行 `class OutboundEvent` 标记基类；第21-30行 `ProgressEvent`、第38-41行 `StreamDeltaEvent`、第44-49行 `StreamEndEvent`、第52-53行 `StreamedResponseEvent`、第57-62行 `TurnEndEvent`（均为 `@dataclass(frozen=True)` 子类）
- F-025: 文件 nanobot/bus/outbound_events.py 第106-122行 `outbound_message_for_event(...)`；第125-130行 `outbound_event_from_message(msg)`；第157-240行 `_legacy_event_from_metadata` 将旧元数据标志桥接为类型化事件

## SDK 值对象（nanobot/sdk/types.py）

- F-026: 文件 nanobot/sdk/types.py 第11-22行 `StreamEventType: TypeAlias = Literal["run.started", "text.delta", "text.completed", "reasoning.delta", "reasoning.completed", "tool.started", "tool.completed", "tool.failed", "run.completed", "run.failed"]`
- F-027: 文件 nanobot/sdk/types.py 第24-33行定义 `STREAM_EVENT_RUN_STARTED` 等 10 个常量；第35-46行 `STREAM_EVENT_TYPES` 元组按序包含全部 10 个值
- F-028: 文件 nanobot/sdk/types.py 第49-59行 `@dataclass(slots=True) class RunResult`，字段 `content/tools_used/messages/usage/stop_reason/error/metadata`
- F-029: 文件 nanobot/sdk/types.py 第62-77行 `@dataclass(slots=True) class StreamEvent`，字段 `type/delta/content/result/name/tool_call_id/arguments/iteration/resuming/usage/error/metadata`
- F-030: 文件 nanobot/sdk/types.py 第80-98行 `SessionSnapshot` 及 `to_dict`；第101-121行 `SessionInfo` 及 `to_dict`
- F-031: 文件 nanobot/sdk/types.py 第124-138行 `snapshot_from_session`、第141-160行 `snapshot_from_payload`、第163-174行 `result_from_response`

## SDK 客户端与流式（nanobot/sdk/）

- F-032: 文件 nanobot/sdk/clients.py 第26-27行 `SessionClient._RESERVED_MESSAGE_KEYS = {"role", "content", RUNTIME_CONTEXT_HISTORY_META}`、`_VALID_ROLES = {"user", "assistant", "tool", "system"}`
- F-033: 文件 nanobot/sdk/clients.py 第32-65行 `SessionClient.ingest`；第67-75行 `get`；第77-89行 `list`；第91-99行 `export`；第101-136行 `restore`；第138-144行 `clear`；第146-148行 `delete`；第150-152行 `flush`
- F-034: 文件 nanobot/sdk/clients.py 第155-178行 `MemoryClient` 方法 `read`/`write`/`append_history`/`read_history`
- F-035: 文件 nanobot/sdk/clients.py 第181-229行 `RuntimeClient`，含 `model`/`workspace` property 与 `add_context_provider`/`on_session_turn_persisted`/`compact_session`/`compact_idle_session`
- F-036: 文件 nanobot/sdk/streaming.py 第26-40行 `RunStream.__init__(task, queue)`；第46-68行 `stream_events`；第70-76行 `wait`；第78-80行 `text`；第82-84行 `cancel`；第86-100行 `aclose`
- F-037: 文件 nanobot/sdk/streaming.py 第120-169行 `SDKStreamEmitter`（`emit`/`text_delta`/`text_completed`/`close`）；第172-224行 `SDKStreamingHook(AgentHook)`（`before_execute_tools`/`emit_reasoning`/`emit_reasoning_end`/`after_iteration`）
- F-038: 文件 nanobot/sdk/runtime.py 第9-15行 `ensure_single_model_selector`；第18-48行 `build_process_direct_kwargs`
- F-039: 文件 nanobot/sdk/__init__.py 第1行 docstring `"Internal helpers for the high-level nanobot Python SDK."`

## 懒加载导出（nanobot/__init__.py）

- F-040: 文件 nanobot/__init__.py 第57-80行 `_LAZY_EXPORTS` 字典将 `Nanobot`/`RunStream`/`RunResult`/`SessionInfo`/`SessionSnapshot`/`STREAM_EVENT_*`/`StreamEvent`/`StreamEventType`/`SessionTurnPersisted` 等名称映射到 `".nanobot"`/`".bus.runtime_events"` 等模块
- F-041: 文件 nanobot/__init__.py 第83-91行 `__getattr__(name)` 通过 `import_module(module_path, __name__)` 惰性导入并缓存到 `globals()`

## CLI（nanobot/cli/）

- F-042: 文件 nanobot/cli/entry.py 第10-21行 `_native_tui_candidate(args)`；第35-51行 `main()` 判断是否为原生 TUI 候选，是则构建 `typer.Typer(add_completion=False)` 注册 `agent` 并 `command.main(args=sys.argv[2:])`，否则导入 `nanobot.cli.commands.app` 调用
- F-043: 文件 nanobot/cli/agent.py 第54-80行 `agent()` 命令选项 `--message/-m`、`--session/-s`、`--workspace/-w`、`--config/-c`、`--markdown/--no-markdown`、`--logs/--no-logs`、`--classic/--no-tui`、`--theme`
- F-044: 文件 nanobot/cli/agent.py 第86行 `native_tui = message is None and not classic`；第147行 `session_id = session_id or "cli:direct"`
- F-045: 文件 nanobot/cli/agent.py 第157行 `bus = MessageBus()`；第165行 `cron = CronService(cron_store_path)`；第166行 `tools = ToolRegistry()`；第167行 `mcp_provider = MCPProvider.from_config(runtime_config, tools)`；第172-180行 `AgentLoop.from_config(...)`
- F-046: 文件 nanobot/cli/agent.py 第237-268行 `message is not None` 时 `run_once` 直接调用 `agent_loop.process_direct(...)`；第302-444行 交互模式 `run_interactive` 通过 `bus.publish_inbound(InboundMessage(...))` 与 `bus.consume_outbound()` 循环
- F-047: 文件 nanobot/cli/webui.py 第73-99行 `webui()` 命令选项 `--port/-p`、`--gateway-port`、`--workspace/-w`、`--config/-c`、`--background`、`--dev`、`--no-open`、`--yes/-y`；第225-230行 `GatewayInstance.resolve` 与 `GatewayRuntime`
- F-048: 文件 nanobot/cli/commands.py 第85-90行 `app = typer.Typer(name="nanobot", ...)`；第100-107行 `@app.callback()` `main` 带 `--version/-v` 回调
- F-049: 文件 nanobot/cli/commands.py 第115-121行 `onboard`、第284-290行 `trigger`、第318-326行 `serve`、第634-640行 `status` 命令；第411行 `app.command(name="webui")(webui)`；第440行 `app.command(name="agent")(agent)`；第419-432行 `app.add_typer(..., name="gateway")`；第448-449行 `sessions_app`、第486-487行 `channels_app`、第554-555行 `plugins_app`、第711行 `provider_app`
- F-050: 文件 nanobot/cli/commands.py 第28-40行 `logger.remove()` 后 `logger.add(sys.stderr, format=...)`，格式含 time/level/`extra[channel]`/message

## TUI 与 WebUI

- F-051: 文件 tui/package.json 第1-11行 `name "@nanobot/tui"`、`private: true`、`version "0.1.0"`、`type "module"`、scripts `start: "bun src/index.ts"`；第12-14行 dependency `"@opentui/core": "0.5.3"`
- F-052: 文件 webui/package.json 第1-14行 `name "nanobot-webui"`、scripts `dev: "vite"`、`build: "tsc -p tsconfig.build.json && vite build"`；第28-29行 `react: "^18.3.1"`、`react-dom: "^18.3.1"`；第63行 `vite: "^5.4.11"`
- F-053: 文件 nanobot/cli/tui_launcher.py 第34-39行 `class TuiUnavailableError(RuntimeError)`、`class TuiSessionError(ValueError)`；第73-80行 `launch_tui(...) -> int`；第64行 `_TUI_DETACH_EXIT_CODE = 90`
- F-054: 文件 nanobot/cli/tui_launcher.py 第92-110行 通过环境变量 `NANOBOT_TUI_BOOTSTRAP_URL`/`NANOBOT_TUI_API_URL`/`NANOBOT_TUI_MODEL`/`NANOBOT_TUI_MODEL_PRESET`/`NANOBOT_TUI_WORKSPACE`/`NANOBOT_TUI_THEME` 等传给 TUI 子进程
- F-055: 文件 nanobot/cli/tui_launcher.py 第154-200行 `_resolve_tui_command()` 依次尝试环境变量 `NANOBOT_TUI_BIN`、源码 checkout（要求 Bun）、打包的 `tui/bin/<asset>`、下载版本匹配的 release 归档

## 文档（docs/）

- F-056: 文件 docs/concepts.md 第7-19行 Runtime Shape 表列出六部分：Agent loop / Providers / Channels / Tools / Memory / Gateway
- F-057: 文件 docs/concepts.md 第26-30行 默认实例路径 `~/.nanobot/config.json`、`~/.nanobot/workspace/`、`~/.nanobot/sessions/<workspace-id>/`
- F-058: 文件 docs/concepts.md 第69-75行 单轮流程五步：channel publish → 选择 session key 构建上下文 → provider 收到请求 → 工具执行回填 → 回复保存并回传 channel
- F-059: 文件 docs/concepts.md 第87行 gateway 健康端点位于 `gateway.port`（默认 `18790`），浏览器 WebUI 默认在 `8765` 提供
- F-060: 文件 docs/memory.md 第17-23行 记忆分层：`session.messages` / `memory/history.jsonl` / `SOUL.md`、`USER.md`、`memory/MEMORY.md` / `GitStore`
- F-061: 文件 docs/memory.md 第30-47行 Consolidator 压缩摘要写入 append-only、cursor-based 的 `memory/history.jsonl`；第50-63行 Dream 按 cron 定期读取 history.jsonl + SOUL.md + USER.md + MEMORY.md 并单次编辑长期文件
- F-062: 文件 docs/python-sdk.md 第466-594行 给出 `Nanobot.from_config`/`bot.run`/`RunStream`/`StreamEvent`/`RunResult` 的 API 参考表与签名
- F-063: 文件 docs/my-tool.md 第35-102行 my 工具的 `check`/`set` action 用法；第104-115行 受保护参数表（`max_iterations`/`context_window_tokens`/`model`/`model_preset`）