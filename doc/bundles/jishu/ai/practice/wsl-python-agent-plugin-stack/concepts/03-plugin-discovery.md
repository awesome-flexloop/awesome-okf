---
okf_version: "0.2"
type: Concept
title: "插件发现机制四谱：entry points、pluggy、MCP 与 Agent Skills"
description: "四种插件发现与调用机制的对比——Python 标准 entry points（importlib.metadata）、pluggy 钩子总线、MCP 2026-07-28 无状态协议（Host/Client/Server 与 Resources/Prompts/Tools）、Agent Skills 渐进披露；进程边界是第一决策轴"
tags: [entry-points, pluggy, MCP, Agent-Skills, 插件架构, importlib-metadata, JSON-RPC]
generated: { by: "agent/seven-concepts-research", at: "2026-10-28T18:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-28T18:00:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: importlib-metadata
    resource: https://docs.python.org/3/library/importlib.metadata.html
  - id: pytest-plugins
    resource: https://docs.pytest.org/en/stable/how-to/plugins.html
  - id: pluggy-docs
    resource: https://pluggy.readthedocs.io/en/stable/
  - id: mcp-spec-2026
    resource: https://modelcontextprotocol.io/specification/2026-07-28
  - id: anthropic-skills
    resource: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
---

# 插件发现机制四谱：entry points、pluggy、MCP 与 Agent Skills

四种机制覆盖从「同进程函数」到「跨进程服务」再到「零运行时文件」的完整谱系。选择的第一轴是**进程边界**（故障半径与信任模型），第二轴才是功能类型。

## 机制一：entry points——Python 标准的包级发现

**原理**：发行版在 `pyproject.toml` 里声明入口点组，安装后落入发行版 metadata；宿主用 `importlib.metadata` 枚举并加载：

```toml
# 插件包的 pyproject.toml
[project.entry-points."agent_stack.tools"]
search = "agent_plugin_search:register"
fetch  = "agent_plugin_fetch:register"
```

```python
# 宿主的发现代码
from importlib.metadata import entry_points

for ep in entry_points(group="agent_stack.tools"):
    register = ep.load()   # 触发导入，拿到注册函数
    register(registry)
```

**关键行为**（官方文档核验）：

- 发现完全依赖**当前解释器环境的已安装发行版**——换 venv 就是换插件集合；插件装了不等于启用，宿主仍可做开关与优先级。
- Python 3.12 起旧的可迭代接口（`entry_points().get(group)`）移除，`entry_points(group=...)` 关键字过滤是唯一方式（3.10+ 可用，3.10 前需第三方 `importlib_metadata` 后备）。
- 真实生态范例：pytest 的 `pytest11` 入口点组（全部 `pip install` 的 pytest 插件由此被发现）、vLLM v1 的 `vllm.general_plugins` 组（零侵入加载厂商扩展）。

**适用**：进程内、完全信任、需要毫秒级调用延迟的扩展点。**不适用**：不可信代码、语言异构、需要崩溃隔离的能力。

## 机制二：pluggy——钩子总线（扩展点契约化）

pluggy 是 pytest 背后的插件管理库，在 entry points 之上补了**契约与编排**层：

- 宿主用 `@hookspec`（钩子规格）声明扩展点签名与调用语义（firstresult/trylast 等）；
- 插件用 `@hookimpl`（钩子实现）注册，可标注 `hookwrapper` 包裹其他实现；
- `PluginManager` 负责注册顺序、钩子执行的 result 处理（如全部收集/首个非 None）。

与纯 entry points 的差别：entry points 解决「**发现**」（从哪找到插件），pluggy 解决「**编排**」（多个插件对同一钩子的调用顺序与结果合成）。pytest 的三通道插件装载是其生态范本：内置插件（源码树内）+ 外部插件（`pytest11` entry points）+ conftest.py 本地插件（目录约定发现）——同一钩子总线上三种发现来源共存。

**适用**：宿主有清晰生命周期（会话开始/结束、工具调用前后），扩展点是**流程切面**而非独立能力。

## 机制三：MCP——进程间协议（2026-07-28 无状态版）

**协议骨架**（官方规范核验）：JSON-RPC 2.0 消息、三方角色（Host 发起连接的 LLM 应用 / Host 内的 Client 连接器 / 提供能力的 Server）、**无状态自包含请求 + 每请求能力协商**——2026-07-28 修订版移除了旧版的长连接握手模型（无 initialize 会话、无粘性会话 ID），使基础设施可直接路由 MCP 流量。

**Server 三特性**：

| 特性 | 面向 | 语义 |
|------|------|------|
| **Tools** | 模型执行 | 模型可调用的函数（带 schema 的输入输出） |
| **Resources** | 用户/模型消费 | 上下文数据（文件、数据库行、API 响应） |
| **Prompts** | 用户触发 | 模板化消息与工作流 |

**Client 特性**：Elicitation——Server 反向向用户请求补充信息（如缺参数时询问）。

**Extensions（可选、协商启用）**：Tasks（异步长任务的轮询/中途输入/持久句柄）、Skills over MCP（结构化技能指令经 MCP 发现消费）、MCP Apps（会话内嵌交互 UI）。

**传输**：stdio（本地子进程，Agent 本地工具的主流形态）与 Streamable HTTP（远程服务，默认无状态）。受 LSP（语言服务器协议）启发——「x 个应用 × y 个工具」的适配矩阵坍缩为「x + y」。

**安全三原则**（规范明示）：用户同意与控制、数据隐私、工具安全——**工具行为描述（如 annotations）应视为不可信输入**，除非来自可信 Server；Host 必须在调用任何工具前获得用户明确同意。

**适用**：不可信/第三方能力、需要崩溃隔离、跨语言（Node/Go/Rust 服务）、团队共享的远程能力。**代价**：每次调用的序列化开销、部署运维复杂度。

## 机制四：Agent Skills——文件约定的渐进披露

Anthropic Agent Skills 是**零运行时**的插件形态：一个技能 = 一个含 `SKILL.md`（YAML frontmatter 元数据 + 指令正文）及可选脚本/资源的目录。加载遵循**渐进披露**（Progressive Disclosure）三级：

1. **常驻**：只有技能名 + 描述（frontmatter）进入系统上下文——几十字节；
2. **按需**：模型判断任务相关时读取 SKILL.md 正文（数 KB）；
3. **执行**：正文指向的脚本/参考文件仅在需要时读取或执行。

存放层级：项目级 `.claude/skills/<name>/SKILL.md`（随 git 分发、团队共享）与个人级 `~/.claude/skills/`（私有）。判断「内容该进 CLAUDE.md 还是技能」的准则：每次会话都需要的进常驻上下文，某类任务才需要的进技能。

**适用**：**知识型**能力（领域流程、输出规范、排障手册）。它不提供函数调用——与 Tools 机制正交互补。

## 四谱对照总表

| 维度 | entry points | pluggy | MCP | Agent Skills |
|------|:---:|:---:|:---:|:---:|
| 进程边界 | 进程内 | 进程内 | 进程间 | 无运行时 |
| 发现来源 | 发行版 metadata | 注册顺序 + entry points | 连接配置（stdio 命令/URL） | 目录扫描 |
| 调用成本 | 函数调用 | 函数调用（受管编排） | JSON-RPC 序列化 + IPC | 文件读取 |
| 故障半径 | 与宿主同生共死 | 同左（可捕获异常） | 独立进程，崩溃可降级 | 无代码执行风险 |
| 信任模型 | 完全信任 | 宿主契约 + 完全信任 | 用户同意 + 描述不可信 | 内容审阅 |
| 语言绑定 | Python only | Python only | 语言无关 | 语言无关（Markdown） |
| 典型形态 | 能力注册 | 生命周期切面 | 工具/资源服务 | 领域知识 |

## 决策树

```mermaid
flowchart TD
    Q1{"插件是知识还是代码？"}
    Q1 -->|"知识/流程"| SKILL["Agent Skills<br/>SKILL.md 渐进披露"]
    Q1 -->|"代码" --> Q2{"需要崩溃隔离或<br/>第三方/跨语言？"}
    Q2 -->|"是"| MCP["MCP Server<br/>stdio 本地 / HTTP 远程"]
    Q2 -->|"否，完全信任"| Q3{"扩展点是能力<br/>还是流程切面？"}
    Q3 -->|"能力（可独立调用）"| EP["entry points<br/>声明组 + load()"]
    Q3 -->|"流程切面（生命周期）"| PLUGGY["pluggy<br/>hookspec/hookimpl"]
```

## 关键要点回顾

- 第一决策轴是进程边界：故障半径与信任模型先于功能分类。
- entry points 是发现机制（环境即插件集合），pluggy 是编排机制（顺序与结果合成）——两者常组合使用。
- MCP 2026-07-28 已转向无状态核心 + 每请求能力协商；安全模型（同意/不可信描述）是选它的架构理由，不只是生态理由。
- Agent Skills 用渐进披露把「上下文成本」变成可控变量——知识型能力的默认选择。
