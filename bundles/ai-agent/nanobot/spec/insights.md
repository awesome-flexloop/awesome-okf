---
type: spec
title: Nanobot 架构洞察
description: 基于 63 条源码事实提炼的 nanobot 架构洞察与知识地图
tags: [nanobot, agent, sdk, spec, insights]
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# Nanobot 架构洞察

> I 阶段产出。基于 63 条源码事实（F-001~F-063）提炼。

## 核心洞察

### 洞察 1：一个核心循环，多个入口收敛

- **陈述**：nanobot 的运行时本质只有一条 `AgentLoop` 处理路径，CLI 一次性消息、CLI 交互、WebUI/WebSocket、聊天频道、OpenAI 兼容 API 等所有入口最终都汇聚到 `AgentLoop`（或其 `process_direct` 方法）来消费消息、调用 provider、执行工具并回传回复。
- **证据**：F-045（`AgentLoop.from_config(...)`）、F-046（`-m` 消息直接 `process_direct`，交互模式经总线）、F-056（docs 列六部件，Agent loop 居中）、F-059（gateway/WebUI 只是同一 loop 的长期运行外壳）。
- **反常识**：并非所有入口都走 `MessageBus`。`nanobot agent -m "..."` 的一次性消息绕过总线直接调用 `agent_loop.process_direct`，只有交互模式与频道才 `publish_inbound` 到总线（F-046）。初次接触者容易误以为"消息一定先经过总线"。
- **行动**：概念文档应明确区分"直连路径"（SDK/一次性 CLI）与"总线路径"（交互 CLI/频道/gateway），标注二者在 `process_direct` 处汇合。

### 洞察 2：双向异步队列的消息总线，事件语义外置为类型

- **陈述**：`MessageBus` 只有一对 `asyncio.Queue`（inbound/outbound）解耦 channel 与 agent core；运行时/UI 语义不藏在 metadata 保留标志里，而是挂在 `OutboundMessage.event` 字段上的一族 `@dataclass(frozen=True)` 事件类型。
- **证据**：F-017/F-018/F-019（MessageBus 两队列四方法）、F-024（OutboundEvent 标记基类 + ProgressEvent/StreamDeltaEvent/StreamEndEvent/StreamedResponseEvent/TurnEndEvent）、F-025（`_legacy_event_from_metadata` 桥接旧标志）。
- **反常识**：`outbound_events.py` 保留了一整套 `_legacy_event_from_metadata` 回退逻辑，把 `_stream_delta`/`_stream_end`/`_progress` 等旧 metadata 标志翻译成类型化事件——说明"事件类型化"是渐进迁移结果，新代码应直接设置 `event` 字段（F-025）。
- **行动**：概念文档需讲清"队列负责路由、`event` 字段负责语义"的构图，并提醒扩展者不要再用保留 metadata 标志。

### 洞察 3：SDK 门面用"组合客户端 + 懒加载导出"避免重依赖

- **陈述**：顶层 `Nanobot` 门面在构造时组合 `SessionClient`/`MemoryClient`/`RuntimeClient` 三个轻量客户端，而包 `__init__` 通过 `_LAZY_EXPORTS` + `__getattr__` 延迟导入，使 `import nanobot` 不立即拉入 agent loop、provider 等重模块。
- **证据**：F-011（构造时赋值三个客户端）、F-040/F-041（`_LAZY_EXPORTS` 字典与 `__getattr__` 惰性导入）、F-012（`from_config` 真正触发 `ToolRegistry`/`MCPProvider`/`AgentLoop` 的构建）。
- **反常识**：`nanobot/__init__.py` 的 `__all__` 列出的 `Nanobot`/`RunResult` 等名称并非在该文件顶部 import，而是靠模块级 `__getattr__` 首次访问时才 `import_module` 并缓存（F-039/F-040/F-041）。这与"`__all__` 对应顶层 import"的常见直觉不符。
- **行动**：参考文档需标注 `Nanobot.from_config()` 是重工作的触发点，纯 `import nanobot` 成本低；SDK 使用者应优先用 `from_config` 而不是手工构造 `AgentLoop`。

### 洞察 4：流式事件双轨映射，SDK 流式是 Hook 的再封装

- **陈述**：SDK 的流式能力 `stream()/run_streamed()` 内部没有独立的流式协议，而是通过 `SDKStreamingHook`（继承 `AgentHook`）把 agent 生命周期钩子（工具开始/结束、推理增量、迭代结束）翻译成公共 `StreamEvent`，再由 `SDKStreamEmitter` 写入一个有界队列，最终由 `RunStream` 消费。
- **证据**：F-036（RunStream 单消费者迭代器）、F-037（SDKStreamingHook 的 `before_execute_tools`/`emit_reasoning`/`after_iteration`）、F-014（run_streamed 构造 `asyncio.Queue(maxsize=256)` + emitter + hook）、F-020/F-029（StreamEvent 字段与类型）。
- **反常识**：`RunStream.stream_events()` 是"单消费者"约束——只能消费一次，中途退出会取消底层 run（F-036）。这为防止半消费流在背压下滞留后台任务而刻意设计，不是可重复迭代的普通生成器。
- **行动**：示例文档应强调流式"要么消费到底、要么 wait/text、要么 cancel/aclose"三种收尾语义，避免留下悬挂任务。

### 洞察 5：my 工具把运行时自省约束在沙箱边界内

- **陈述**：my 工具（`nanobot/agent/tools/self.py` 语义，docs 记录其 `check`/`set` 两个 action）让 agent 能读取自身模型、迭代数、token 用量等状态，并可受限修改 `max_iterations`/`model_preset` 等参数，但通过 blocked/read-only 分类与敏感字段过滤阻止 agent 触碰 `bus`/`tools`/`_mcp_servers`/`api_key` 等边界。
- **证据**：F-063（docs/my-tool.md 的 check/set 与受保护参数表）。
- **反常识**：my 工具"从不改写 config.json"——实例级修改只存内存，唯一跨重启持久的是 `model_preset`（写入当前 session 的选择器）（F-063 相关 docs）。这颠覆了"自修改工具 = 改配置文件"的直觉。
- **行动**：示例文档（custom-tool）演示 my 工具 `check`/`set` 用法时，需标注 blocked/read-only 边界，帮助读者理解为什么 `my(action="set", key="model")` 会被拒绝。

## 知识地图

### 文档清单

**concepts/（5 篇）**

1. `00-overview.md` — 项目定位、六部件运行时、入口点、配置与工作区、技术栈。覆盖 F-001~F-007、F-056~F-059、F-062。
2. `01-agent-core.md` — `Nanobot` 门面、三个客户端、`RunResult`、`process_direct` 与 hook。覆盖 F-008~F-016、F-032~F-035、F-040/F-041。
3. `02-bus-system.md` — `MessageBus`、`InboundMessage`/`OutboundMessage`、`OutboundEvent` 家族、事件常量。覆盖 F-017~F-025。
4. `03-cli-sdk.md` — CLI 入口（entry/agent/webui/commands）、SDK 流式（`RunStream`/`SDKStreamEmitter`/`SDKStreamingHook`）、`StreamEvent` 常量。覆盖 F-042~F-050、F-026~F-039。
5. `04-tui-webui.md` — TypeScript TUI、React WebUI、`tui_launcher` 与 gateway 架构概览。覆盖 F-051~F-055。

**examples/（2 篇）**

1. `quick-start.md` — SDK 一次问答、会话延续、流式输出（基于 docs/python-sdk.md）。
2. `custom-tool.md` — my 工具 `check`/`set` 用法与安全边界（基于 docs/my-tool.md）。

**references/（2 篇）**

1. `agent-api.md` — `Nanobot` SDK 完整 API 签名与源码位置。
2. `bus-sdk-api.md` — `MessageBus` 与 SDK 类型/事件常量签名与源码位置。

### 学习路径

```
00-overview（理解整体架构与入口）
    ↓
01-agent-core（掌握 Nanobot 门面与客户端）
    ↓
02-bus-system（理解消息总线与事件语义）
    ↓
03-cli-sdk（掌握 CLI 与 SDK 流式）
    ↓
04-tui-webui（TUI/WebUI 架构概览）
    同时可读 examples/（动手实践）+ references/（API 速查）
```