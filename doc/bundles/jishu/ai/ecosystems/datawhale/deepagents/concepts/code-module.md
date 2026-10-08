---
title: Code 终端编码 Agent
type: concept
bundle: /datawhale/deepagents
related:
  - /datawhale/deepagents/concepts/core-sdk
  - /datawhale/deepagents/concepts/monorepo-architecture
  - /datawhale/deepagents/concepts/acp-protocol
  - /datawhale/deepagents/concepts/evals-suite
sources:
  - https://github.com/datawhalechina/deepagents/blob/main/libs/code/README.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/code/AGENTS.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/code/ARCHITECTURE.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/code/pyproject.toml
---

# Code 终端编码 Agent

`deepagents-code`（位于 `libs/code/`，命令名 `dcode`）是 Deep Agents 项目的旗舰产品——一个预构建的终端编码 Agent，类似 Claude Code 或 Cursor，由任何支持工具调用的 LLM 驱动。

> 包版本：0.1.59（Beta），要求 Python 3.12+，精确钉住 `deepagents==0.7.8`。

## 安装与启动

```bash
# 基础安装（OpenAI、Anthropic、Gemini 默认包含）
curl -LsSf https://langch.in/dcode | bash

# 带额外模型提供商
DEEPAGENTS_CODE_EXTRAS="nvidia,ollama" curl -LsSf https://langch.in/dcode | bash

# 启动
dcode
```

## 功能特性

- **交互式 TUI** — 基于 Textual 框架的富终端界面，支持流式响应
- **会话恢复** — 跨会话从上次中断处继续
- **Web 搜索** — 基于实时信息的回答
- **远程沙箱** — 在隔离环境中运行代码（LangSmith、AgentCore、Daytona、Modal、Runloop 等）
- **持久化记忆** — Agent 跨对话记住上下文
- **自定义技能** — 通过 slash 命令扩展 Agent
- **Headless 模式** — 非交互运行，用于脚本和 CI（`-x` 标志）
- **人在回路** — 在执行前批准或拒绝工具调用

## 客户端/服务器架构

Code 包采用双进程架构：

```text
┌──────────────────── 终端客户端 ─────────────────────┐
│  呈现交互式或 headless 输出                           │
│  收集用户输入和审批                                   │
└──────────────────────────┬───────────────────────────┘
                           │ 流式协议
                           ▼
┌──────────────────── Agent 服务器 ────────────────────┐
│  运行编码 Agent 图                                    │
│  连接模型、工具、记忆、技能和后端                      │
└──────────────────────────────────────────────────────┘
```

- **客户端**：拥有呈现和输入，基于 Textual TUI 框架
- **服务器**：拥有 Agent 运行时，连接模型、工具、记忆、技能和后端
- 边界保持狭窄，使 UI 响应灵敏，同时让 Agent 使用 LangGraph 的流式、检查点和恢复行为

## 请求流程

1. 客户端接收用户输入
2. 客户端将输入发送到 Agent 服务器
3. 服务器运行 Agent 并流式返回事件
4. 客户端渲染事件并收集所需的人工响应
5. 会话状态被保留，对话可稍后继续

## TUI 工程规范

Code 包的 AGENTS.md 包含密集的 Textual 工程规范：

### 渲染安全

- 优先使用 Textual 的 `Content` 而非 Rich 的 `Text` 进行小部件渲染
- **禁止在 Rich 标记中使用 f-string 插值**（`f"[bold]{var}[/bold]"`），使用 `Content.from_markup("[bold]$var[/bold]", var=value)` 自动转义
- Markdown 消息使用 `_escape_markdown()` 和 `_markdown_table()` 转义外部内容
- `App.notify()` 默认 `markup=True`，动态内容必须传 `markup=False`

### 字形和动画

- 字形（勾选、箭头、光标等）从 `get_glyphs()` 获取，支持 Unicode/ASCII 降级
- 动画 spinner 复用 `tui/widgets/loading.py` 的 `Spinner` 类，不自定义帧元组

### UI 组件组织

- 根抽象放 `tui/screens/` 和 `tui/modals/`
- 可复用组件放 `tui/widgets/`
- UI 组件模块通常不超过 200 行
- 子组件不得导入父组件，通过事件向上通信、数据向下传递

### 输入表面命名

REPL 有多个文本输入表面，使用精确术语：
- **Chat input**（聊天输入框）：主输入区，`ChatInput` 小部件
- **Inline prompt**（内联提示）：消息流中的多行 `TextArea`
- **Modal field**（模态字段）：模态屏内的单行 `Input`
- **Filter input**（过滤输入）：选择器中的过滤 `Input`

## 斜杠命令

斜杠命令定义在 `deepagents_code/command_registry.py` 的 `COMMANDS` 元组中，每个 `SlashCommand` 条目声明：
- 命令名称
- 描述
- `bypass_tier`（队列绕过分类）
- 可选 `hidden_keywords`（模糊匹配）
- 可选 `aliases`（别名）

添加新斜杠命令需要：(1) 添加 COMMANDS 条目，(2) 设置 bypass_tier，(3) 在 `app.py` 的 `_handle_command` 添加处理分支，(4) 运行 `make commands-catalog`，(5) 运行 `make lint && make test`。

## 模型提供商系统

Code 支持 LangChain 聊天模型提供商作为可选依赖。添加新提供商需要更新：

1. `model_config.py` — `PROVIDER_API_KEY_ENV`（API 密钥环境变量映射）
2. `model_config.py` — `PROVIDER_BASE_URL_ENV`（端点环境变量，如适用）
3. `pyproject.toml` — `[project.optional-dependencies]` 添加提供商包
4. `model_config.py` — `RETRY_PARAM_BY_PROVIDER`（如支持 max_retries）
5. `tui/widgets/auth.py` — `PROVIDER_DISPLAY_NAMES` 和 `PROVIDER_API_KEY_URLS`
6. 对应测试文件

`PROVIDER_BASE_URL_ENV` 要求根据源码验证（而非命名推断），规范名称在前，OpenAI 兼容提供商不得列出共享的 `OPENAI_BASE_URL`。

## 启动性能

- 不得在模块级别或参数解析路径导入重型包（deepagents、LangChain、LangGraph）
- 顶层导入保持最小，重型导入延迟到实际需要时
- 使用 `importlib.metadata.version("package-name")` 读取版本而不导入包
- 启动热路径上的功能检查必须轻量
- 后台工作进程生成子进程必须设置超时

## SDK 版本钉住

`deepagents-code` 在 `pyproject.toml` 中精确钉住 `deepagents==0.7.8`。开发依赖新 SDK 功能的 PR 必须同时升级此 pin。CI 在发布时验证 pin 不旧于当前 SDK 版本（可通过 `dangerous-skip-sdk-pin-check` 标签绕过）。

## 安全模型

默认信任运行目录。人在回路审批门控模型请求的工具调用，但项目工件在审批提示前已被读取。对于不可信仓库，应使用远程沙箱。详见 `THREAT_MODEL.md`。

## GitHub Action

根 `action.yml` 定义了 GitHub Action，以非交互方式运行 `dcode`，支持 prompt、model、API keys、shell_allow_list、max_turns 等输入。输出包括 response（原始未过滤输出）、exit_code 和 cache_hit。

## 与其他概念的关系

- 核心SDK与三层架构 是 dcode 构建于其上的 Agent 框架。
- ACP协议集成 允许 dcode 通过 `--acp` 标志嵌入编辑器。
- Evals评估套件 对 dcode 的编码能力进行基准测试。
- CLI部署工具 是从 code 拆分出的独立部署工具。
- Talon运行时宿主 依赖 deepagents-code 作为其 Agent 运行时。
