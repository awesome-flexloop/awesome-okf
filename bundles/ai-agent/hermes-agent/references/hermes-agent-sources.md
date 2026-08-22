---
type: Reference
title: Hermes Agent 源码信源登记
description: hermes-agent v0.20.0 源码路径、版本信息、核心目录与关键文件清单
tags: [hermes-agent, source, reference, v0.20, ai-agent, nous-research]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T12:00:00+08:00" }
verified: { by: "process:source-dir-scan", at: "2026-08-22T12:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: hermes-agent-self
    resource: references/hermes-agent-sources.md
    title: 本文件（信源登记簿自身）
---

# Hermes Agent 源码信源登记

## 项目概览

| 属性 | 值 |
|------|-----|
| 项目名 | hermes-agent |
| 版本 | **0.20.0** |
| 描述 | "The self-improving AI agent — creates skills from experience, improves them during use, and runs anywhere" |
| 语言 | Python（>=3.11, <3.14） |
| 作者 | Nous Research |
| 许可证 | MIT |
| 核心特色 | 自改进 AI Agent：从经验中创建技能、使用中迭代改进、跨平台运行；支持 MoA（Mixture-of-Agents）、多 Provider 抽象、插件化架构、100+ 内置工具、ACP 协议适配 |

## 版本标识

版本号定义于 `pyproject.toml`：

```toml
[project]
name = "hermes-agent"
version = "0.20.0"
description = "The self-improving AI agent — creates skills from experience, improves them during use, and runs anywhere"
requires-python = ">=3.11,<3.14"
```

Python 版本硬性上界 `<3.14` 以避免 Rust 扩展缺少 cp314 wheel 的问题。

## 源码位置

hermes-agent 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/models/ai/hermes-agent/
```

## 核心目录结构

| 目录 | 用途 | 关键文件 |
|------|------|---------|
| `agent/` | 核心智能体逻辑 | `agent_init.py`、`moa_loop.py`、`iteration_budget.py`、`tool_executor.py`、`prompt_builder.py`、`system_prompt.py` |
| `agent/lsp/` | Language Server Protocol 集成 | `__init__.py`、`client.py`、`manager.py`、`servers.py` |
| `agent/transports/` | Provider 数据格式转换层 | `base.py`、`types.py`、`chat_completions.py`、`anthropic.py`、`codex.py`、`bedrock.py` |
| `agent/pet/` | Petdex 宠物动画引擎 | `__init__.py`、`constants.py`、`render.py`、`state.py` |
| `agent/monitoring/` | 运行时监控 | `events.py`、`policy.py` |
| `agent/verify/` | 验证与配方执行 | `recipes.py`、`runner.py` |
| `tools/` | 工具实现（~100 个模块） | `registry.py`、`terminal_tool.py`、`file_operations.py`、`browser_tool.py`、`delegate_tool.py`、`mcp_tool.py` |
| `tools/environments/` | 代码执行环境后端 | `base.py`、`local.py`、`docker.py`、`ssh.py`、`modal.py`、`daytona.py` |
| `tools/computer_use/` | 计算机使用工具 | `tool.py`、`backend.py`、`cua_backend.py`、`permissions.py`、`vision_routing.py` |
| `providers/` | 模型 Provider 抽象基类 | `base.py`（`ProviderProfile`） |
| `plugins/` | 插件系统 | `plugin_utils.py`、`model-providers/`（36+）、`platforms/`（22+）、`web/`、`memory/`、`image_gen/` 等 |
| `gateway/` | 网关层（多平台会话管理） | `config.py`、`session.py`、`run.py`、`delivery.py`、`slash_commands.py` |
| `acp_adapter/` | ACP 协议适配 | `server.py`、`session.py`、`auth.py`、`entry.py`、`events.py`、`tools.py` |
| `hermes_cli/` | CLI 命令系统 | `main.py`、`commands.py`、`config.py`、`setup.py`、`doctor.py` 等 80+ 命令模块 |
| `cron/` | 定时任务调度 | `scheduler.py`、`jobs.py`、`blueprint_catalog.py`、`executions.py` |
| `apps/` | 桌面应用（TypeScript/React） | `desktop/`（Tauri + React）、`shared/` |
| `locales/` | 国际化翻译文件 | `en.yaml`、`zh.yaml`、`ja.yaml` 等 17 种语言 |
| `tests/` | 测试套件 | `agent/`、`acp/`、`cron/`、`gateway/`、`tools/`、`e2e/` |
| `scripts/` | 构建与开发脚本 | `install.sh`、`release.py`、`lint_diff.py` |
| `docker/` | Docker 构建资源 | `entrypoint.sh`、`main-wrapper.sh`、`SOUL.md` |
| `nix/` | Nix 包管理配置 | `hermes-agent.nix`、`python.nix`、`devShell.nix` |
| `native/` | 原生扩展 | `fts5_cjk/`（CJK 全文搜索 FTS5 分词器） |

## 关键文件清单

### 入口与配置

| 文件 | 用途 |
|------|------|
| `pyproject.toml` | 项目元数据、依赖声明（精确版本钉扎）、构建配置 |
| `setup.py` | Nix 构建守卫，非 Nix 环境下阻止 wheel/sdist 构建 |
| `run_agent.py` | AIAgent 核心类定义与对话主循环入口 |
| `cli.py` | 交互式终端界面（基于 `prompt_toolkit`） |
| `hermes_bootstrap.py` | Windows UTF-8 stdio 初始化引导模块 |

### Agent 核心

| 文件 | 用途 |
|------|------|
| `agent/agent_init.py` | AIAgent 初始化实际实现体（~1400 行），委托自 `AIAgent.__init__` |
| `agent/iteration_budget.py` | 线程安全迭代计数器，使用 `threading.Lock` 保护 |
| `agent/moa_loop.py` | Mixture-of-Agents（MoA）多模型协作运行时 |
| `agent/tool_executor.py` | 工具调用执行引擎 |
| `agent/prompt_builder.py` | 对话提示词构建器 |
| `agent/system_prompt.py` | 系统提示词生成与管理 |
| `agent/redact.py` | 集中式敏感信息脱敏（密钥、PII） |
| `agent/context_engine.py` | 上下文压缩与管理引擎 |

### Provider 抽象与传输

| 文件 | 用途 |
|------|------|
| `providers/base.py` | `ProviderProfile` 基类，声明推理 provider 行为配置 |
| `agent/transports/base.py` | `ProviderTransport` 抽象基类，定义消息/工具/响应转换接口 |
| `agent/transports/types.py` | `ToolCall`、`Usage`、`NormalizedResponse` 归一化 dataclass 类型 |
| `agent/transports/chat_completions.py` | OpenAI Chat Completions 协议 transport 实现 |
| `agent/transports/anthropic.py` | Anthropic Claude 协议 transport 实现 |
| `agent/transports/codex.py` | OpenAI Codex 协议 transport 实现 |
| `agent/transports/bedrock.py` | AWS Bedrock 协议 transport 实现 |

### 工具系统

| 文件 | 用途 |
|------|------|
| `tools/registry.py` | `ToolRegistry` 单例注册表，工具注册/发现/缓存 |
| `toolsets.py` | 工具集定义与解析 DAG，核心工具列表与 webhook 安全工具列表 |
| `tools/terminal_tool.py` | 终端命令执行工具 |
| `tools/file_operations.py` | 文件读写操作工具 |
| `tools/browser_tool.py` | 浏览器自动化工具 |
| `tools/delegate_tool.py` | 子 Agent 委托工具 |
| `tools/mcp_tool.py` | MCP（Model Context Protocol）工具集成 |
| `tools/skills_tool.py` | 技能管理工具 |
| `tools/memory_tool.py` | 记忆存取工具 |
| `tools/environments/base.py` | 代码执行环境抽象基类 |
| `tools/computer_use/tool.py` | 计算机使用（屏幕/键鼠操作）工具入口 |

### 插件与平台

| 文件 | 用途 |
|------|------|
| `plugins/plugin_utils.py` | 线程安全单例原语（`lazy_singleton`、`SingletonSlot`） |
| `gateway/config.py` | 网关配置加载、验证与布尔类型强制 |
| `gateway/session.py` | 网关会话管理、PII 哈希、自动续期窗口 |
| `acp_adapter/__init__.py` | ACP（Agent Communication Protocol）适配器入口 |

## 核心类/函数索引

> 基于 facts.md F-001 ~ F-080 提取，所有类名/函数名/文件路径均来自实际源码。

### 核心类

| 类名 | 所在文件 | 职责描述 |
|------|---------|---------|
| `AIAgent` | `run_agent.py` | AI Agent 核心类，管理对话流、工具执行和响应处理；`__init__` 委托给 `agent.agent_init.init_agent` |
| `IterationBudget` | `agent/iteration_budget.py` | 线程安全迭代计数器，父 agent 默认 500 次、子 agent 默认 50 次；提供 `consume()`/`refund()`/`used`/`remaining` |
| `ProviderTransport` | `agent/transports/base.py` | Provider 数据格式转换抽象基类（ABC），定义 `convert_messages`/`convert_tools`/`build_kwargs`/`normalize_response` 抽象方法 |
| `ToolCall` | `agent/transports/types.py` | 工具调用归一化 dataclass，含 `id`/`name`/`arguments`（JSON 字符串）/`provider_data` 字段 |
| `Usage` | `agent/transports/types.py` | Token 用量 dataclass，含 `prompt_tokens`/`completion_tokens`/`total_tokens`/`cached_tokens` |
| `NormalizedResponse` | `agent/transports/types.py` | Provider 响应归一化 dataclass，含 `content`/`tool_calls`/`finish_reason`/`reasoning`/`usage`/`provider_data` |
| `ToolEntry` | `tools/registry.py` | 工具条目类（`__slots__`），封装 `name`/`schema`/`handler`/`check_fn`/`is_async`/`emoji` 等属性 |
| `ToolRegistry` | `tools/registry.py` | 工具单例注册表，收集工具 schema 和 handler；支持跨 toolset 覆盖授权、别名管理、TTL 缓存 |
| `ProviderProfile` | `providers/base.py` | 推理 Provider 行为配置基类，声明 `name`/`api_mode`/`aliases`/`auth_type`/视觉支持/模型目录/请求级参数等 |
| `_RefAccounting` | `agent/moa_loop.py` | MoA reference model 用量追踪类（`__slots__`），追踪 token 用量和估算成本（USD） |
| `SingletonSlot[T]` | `plugins/plugin_utils.py` | 带参数的懒加载泛型槽，线程安全（`threading.Lock`），提供 `get()`/`peek()`/`reset()` |
| `_GuardedSdist` | `setup.py` | 继承 `setuptools.command.sdist.sdist`，非 Nix 构建环境抛出 `RuntimeError` |

### 核心函数

| 函数名 | 所在文件 | 职责描述 |
|--------|---------|---------|
| `init_agent(agent, ...)` | `agent/agent_init.py` | `AIAgent.__init__` 的实际实现体（~1400 行），执行属性初始化、provider 自动检测、凭证解析、上下文引擎引导 |
| `build_tool_call(id, name, arguments, **provider_fields)` | `agent/transports/types.py` | `ToolCall` 工厂函数，dict 类型 arguments 自动 JSON 序列化，额外参数收集到 `provider_data` |
| `map_finish_reason(reason, mapping)` | `agent/transports/types.py` | 将 provider 特定 stop reason 映射到标准集合，未知/None 回退 `"stop"` |
| `discover_builtin_tools(tools_dir)` | `tools/registry.py` | 内置工具发现函数，AST 扫描模块顶层 `registry.register(...)` 调用，使用 `(mtime_ns, size)` 磁盘缓存避免重复扫描 |
| `_redact_reference_text(text)` | `agent/moa_loop.py` | MoA PII 隐私脱敏，先调用集中式 `redact_sensitive_text`，再替换邮箱/电话为 `[redacted]` 标记 |
| `_run_references_parallel()` | `agent/moa_loop.py` | 并发执行所有 reference model 调用（`ThreadPoolExecutor`，最多 8 并发），支持用户中断与延迟计费记录 |
| `_reference_messages(messages)` | `agent/moa_loop.py` | 构建顾问视图消息：丢弃 system prompt、内联 tool_calls、折叠 tool 结果为 head+tail 预览 |
| `lazy_singleton(fn)` | `plugins/plugin_utils.py` | 双重检查锁定单例装饰器，零参数工厂函数，附 `.reset()` 方法；仅依赖 stdlib `threading` |
| `get_toolset(name, *, include_registry=True)` | `toolsets.py` | 获取指定工具集定义（包含工具列表与元数据） |
| `resolve_toolset(name, visited=None, *, include_registry=True)` | `toolsets.py` | 解析工具集依赖 DAG，返回展开后的工具名列表（支持循环检测） |
| `_coerce_bool(value, default=True)` | `gateway/config.py` | 布尔配置值类型强制，支持字符串 `"true"/"1"/"yes"/"on"` → True，`"false"/"0"/"no"/"off"` → False |
| `_hash_id(value)` | `gateway/session.py` | PII 哈希辅助函数（SHA-256 前 12 位十六进制） |

## 架构模块映射

| 模块 | 代码路径 | 职责 |
|------|---------|------|
| Agent 核心循环 | `agent/`（不含子目录） | Agent loop、初始化、提示词构建、工具执行、上下文管理、MoA、记忆、计费、重试、错误分类 |
| LSP 集成 | `agent/lsp/` | Language Server Protocol 客户端管理、诊断信息、代码补全 |
| Provider Transport | `agent/transports/` | 多 Provider 协议适配层：消息格式转换、工具 schema 映射、响应归一化 |
| Pet 宠物引擎 | `agent/pet/` | CLI/TUI 界面动画精灵渲染与状态管理 |
| 运行时监控 | `agent/monitoring/` | 事件追踪与策略执行 |
| 验证引擎 | `agent/verify/` | 验证配方（recipes）执行与测试运行 |
| 工具注册表 | `tools/registry.py` | 工具注册、发现、TTL 缓存、覆盖授权、别名管理 |
| 工具集定义 | `toolsets.py` | 核心工具列表、webhook 安全工具集、DAG 解析、自定义工具集创建 |
| 工具实现 | `tools/*.py` | ~100 个工具模块：终端、文件、浏览器、委托、MCP、技能、记忆、图像/视频、TTS、视觉、Home Assistant、看板、Discord、飞书、定时任务、安全、唤醒词等 |
| 执行环境后端 | `tools/environments/` | 代码执行沙箱：local、docker、ssh、modal、daytona、singularity、vercel_sandbox |
| 计算机使用 | `tools/computer_use/` | 屏幕截图、键鼠操作、视觉路由、CUA（Computer Use Agent）后端 |
| Provider 配置 | `providers/base.py` | ProviderProfile 基类，声明各模型 provider 的能力配置 |
| 插件基础设施 | `plugins/plugin_utils.py` | 线程安全单例原语（`lazy_singleton`、`SingletonSlot`） |
| 模型 Provider 插件 | `plugins/model-providers/` | 36 个 provider 插件（anthropic、deepseek、gemini、openai-codex、ollama-cloud、bedrock、xai、alibaba、kimi-coding 等） |
| 平台适配器插件 | `plugins/platforms/` | 22 个平台插件（telegram、discord、slack、feishu、wecom、whatsapp、teams、email、a2a、homeassistant、line、irc、matrix 等） |
| 搜索 Provider 插件 | `plugins/web/` | 8 个搜索 provider（brave_free、ddgs、exa、firecrawl、parallel、searxng、tavily、xai） |
| 记忆插件 | `plugins/memory/` | 8 个记忆后端（byterover、hindsight、holographic、honcho、mem0、openviking、retaindb、supermemory） |
| 图像生成插件 | `plugins/image_gen/` | 7 个图像生成 provider（deepinfra、fal、krea、openai、openai-codex、openrouter、xai） |
| 视频生成插件 | `plugins/video_gen/` | 3 个视频生成 provider（deepinfra、fal、xai） |
| 浏览器插件 | `plugins/browser/` | 3 个浏览器自动化 provider（browser_use、browserbase、firecrawl） |
| 网关配置 | `gateway/config.py` | 网关配置加载、平台连接、home channels、会话重置策略 |
| 网关会话 | `gateway/session.py` | 会话上下文追踪、持久化存储、重置策略、动态系统提示注入、PII 哈希 |
| 网关运行时 | `gateway/`（其余文件） | 网关启动/停止、消息投递、流事件、Slash 命令、会话租约、扩缩容、状态管理 |
| ACP 协议适配 | `acp_adapter/` | Agent Communication Protocol：服务器、会话管理、认证、权限、事件、工具桥接 |
| CLI 命令系统 | `hermes_cli/` | 80+ CLI 命令模块：配置、模型、插件、技能、网关、MCP、看板、定时任务、备份、调试 |
| 定时任务 | `cron/` | 定时任务调度器、作业管理、蓝图目录、执行记录、生命周期守卫 |
| 桌面应用 | `apps/desktop/` | Tauri + React 桌面端应用 |
| 国际化 | `locales/` | 17 种语言翻译文件（YAML 格式） |
| 原生扩展 | `native/fts5_cjk/` | SQLite FTS5 CJK 分词器（C 语言） |
