---
type: Reference
title: AI Agent 框架源码信源登记
description: 本知识包所依据的 12 个 AI Agent 开源项目源码路径、版本与关键文件索引
tags: [ai-agent, source, reference, agent-frameworks, hermes, cordis, veadk]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T01:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: hermes-agent
    resource: /references/ai-agent-sources.md#hermes-agent
    title: hermes-agent v0.20.0
  - id: veadk-python
    resource: /references/ai-agent-sources.md#veadk-python
    title: veadk-python
  - id: zleap-agent
    resource: /references/ai-agent-sources.md#zleap-agent
    title: Zleap-Agent
  - id: deepseek-harness
    resource: /references/ai-agent-sources.md#deepseek-harness
    title: deepseek-harness (dsh)
  - id: cordis
    resource: /references/ai-agent-sources.md#cordis
    title: Cordis 元框架
  - id: agency-agents
    resource: /references/ai-agent-sources.md#agency-agents
    title: agency-agents persona 集合
  - id: anthropics-skills
    resource: /references/ai-agent-sources.md#anthropics
    title: anthropics/skills
  - id: book-to-skill
    resource: /references/ai-agent-sources.md#book-to-skill
    title: book-to-skill
  - id: i-have-adhd
    resource: /references/ai-agent-sources.md#i-have-adhd
    title: i-have-adhd
  - id: intelligent-terminal
    resource: /references/ai-agent-sources.md#intelligent-terminal
    title: intelligent-terminal
  - id: second-me
    resource: /references/ai-agent-sources.md#second-me
    title: Second-Me (mindverse)
---

# AI Agent 框架源码信源登记

本知识包基于 SpecWeave 仓库外部依赖目录 `external/libs/models/ai/` 下 12 个 AI Agent 相关开源项目的源码深度阅读生成。所有文档中的 API、类名、方法签名、架构描述均溯源至这些源码文件。

## 源码位置

所有源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/models/ai/
```

## 项目清单

### hermes-agent

| 属性 | 值 |
|------|-----|
| 路径 | `external/libs/models/ai/hermes-agent/` |
| 语言 | Python |
| 版本 | v0.20.0 |
| 定位 | 高度可配置的通用 AI Agent 框架，支持多模型、多工具集、多平台部署 |
| 许可证 | 开源（详见项目 LICENSE） |

**关键目录与文件**：

| 文件/目录 | 用途 |
|-----------|------|
| `agent/__init__.py` | AIAgent 类导出入口 |
| `agent/base.py` | Agent 基类与核心接口定义 |
| `agent/loop.py` | 工具调用循环主逻辑 |
| `agent/moa_loop.py` | Mixture of Agents 多代理编排循环 |
| `agent/agent_init.py` | Agent 模块化初始化实现 |
| `toolsets.py` | 工具集注册表（40+ 核心工具，1000+ 行） |
| `tools/registry.py` | ToolRegistry 单例注册表 |
| `skills/` | 技能管理模块 |
| `cli/` | 命令行入口 |
| `transports/` | Telegram/Discord 等平台传输层 |
| `lsp/` | LSP（Language Server Protocol）集成 |
| `pet/` | PET（Prompt Engineering Toolkit）模块 |

**核心类**：`AIAgent`（75+ 可配置参数）、`ToolRegistry`、`MoAClient`、`MoAChatCompletions`

### veadk-python

| 属性 | 值 |
|------|-----|
| 路径 | `external/libs/models/ai/veadk-python/` |
| 语言 | Python |
| 定位 | 字节跳动开源的视觉增强 Agent 开发套件 |
| 许可证 | 开源（详见项目 LICENSE） |

**关键目录与文件**：

| 文件/目录 | 用途 |
|-----------|------|
| `veadk/__init__.py` | 懒加载入口 |
| `veadk/agent.py`（751 行） | Agent 类完整定义（模型配置、记忆集成、工具管理） |
| `veadk/runner.py`（789 行） | Runner 类（Agent 生命周期与运行时管理） |
| `veadk/config.py` | 配置系统 |
| `veadk/consts.py` | 常量定义 |
| `veadk/memory/short_term_memory.py` | 短期记忆 |
| `veadk/memory/long_term_memory.py` | 长期记忆（7+ 后端实现） |
| `veadk/runtime/base_runtime.py` | 运行时抽象基类 |
| `veadk/runtime/codex/runtime.py` | Codex 运行时委托 |
| `veadk/runtime/piagent/runtime.py` | PiAgent 运行时委托 |
| `veadk/agents/` | 多智能体模块 |
| `veadk/tools/` | 工具集成 |
| `veadk/knowledgebase/knowledgebase.py` | 知识库管理 |
| `veadk/agent_builder.py` | Agent 构建器 |

**核心类**：`Agent`（继承 LlmAgent）、`Runner`、`ShortTermMemory`、`LongTermMemory`、`BaseRuntime`

### Zleap-Agent

| 属性 | 值 |
|------|-----|
| 路径 | `external/libs/models/ai/Zleap-Agent/` |
| 语言 | TypeScript (Node.js 20+, pnpm 9 monorepo) |
| 定位 | Workspace-first 的 Agent Harness，上下文隔离架构 |
| 存储 | PostgreSQL + pgvector |

**关键目录与文件**：

| 文件/目录 | 用途 |
|-----------|------|
| `packages/ai/src/registry.ts` | ProviderRegistry / ModelRegistry（模型抽象） |
| `packages/core/src/runtime.ts` | AgentRuntime（注册中心、会话创建、运行循环） |
| `packages/core/src/workspace.ts` | WorkSpaceRegistry（工作区隔离） |
| `packages/core/src/tools.ts` | ToolRegistry（工具注册） |
| `packages/agent/` | Agent 运行时、Workspace 执行、记忆压缩、MCP 运行时 |
| `packages/core/` | 共享类型、注册表基类、Hook 系统 |
| `packages/store/` | PostgreSQL 存储、向量召回（RRF） |
| `packages/cli/` | Ink/React TUI 终端界面 |
| `packages/web/` | Next.js Web UI |

**核心类**：`AgentRuntime`、`WorkSpaceRegistry`、`ToolRegistry`、`ProviderRegistry`、`ModelRegistry`、`AgentEventBus`

### deepseek-harness (dsh)

| 属性 | 值 |
|------|-----|
| 路径 | `external/libs/models/ai/deepseek-harness/` |
| 语言 | TypeScript (pnpm monorepo, Node ^22.19 \|\| >=24) |
| 定位 | DeepSeek 开源的插件化 Agent Harness，Cordis 驱动 |
| 理论基础 | 论文《A Programming Paradigm for Spatiotemporal Composability》 |

**关键目录与文件**：

| 文件/目录 | 用途 |
|-----------|------|
| `packages/core/` | Session、system-prompt、tools、agent、agent-loop |
| `packages/llm/` | LLM Service Definition/Consumer + DeepSeek providers |
| `packages/shell/` | bash 能力 + local/pwsh providers |
| `packages/fs/` | 文件系统能力 + 策略 |
| `packages/mcp/` | MCP 协议实现 |
| `packages/web/` | Web 能力（search/fetch） |
| `packages/subagent/` | 子代理委派 |
| `packages/sandbox/` | 沙箱执行 |
| `packages/session/` | SQLite 持久化会话 |
| `packages/compaction/` | 上下文压缩 |
| `packages/guard/` | 循环卫生 + 工具超时守卫 |
| `packages/plan/` | Plan 模式 |
| `vendor/` | Vendored Cordis 源码 |
| `apps/cli/` | CLI 入口 |
| `apps/web/` | Web UI（Vite） |
| `python/` | Python SDK + runtime |

**核心模式**：一切皆插件、Capability Seam（Service Definition + Provider + Consumer）、声明式 cordis.yml 组合

### Cordis

| 属性 | 值 |
|------|-----|
| 路径 | `external/libs/models/ai/cordis/` |
| 语言 | TypeScript (Yarn 4 monorepo) |
| 定位 | 时空可组合性元框架，deepseek-harness 的底层插件引擎 |
| 许可证 | MIT |

**关键目录与文件**：

| 文件/目录 | 用途 |
|-----------|------|
| `packages/core/src/context.ts` | Context（原型链式扩展：extend/isolate/intercept） |
| `packages/core/src/registry.ts` | RegistryService（插件注册、依赖注入） |
| `packages/core/src/events.ts` | EventsService（5 种事件分发模式） |
| `packages/core/src/fiber.ts` | Fiber（插件生命周期管理：PENDING→LOADING→ACTIVE→FAILED/DISPOSED） |
| `packages/core/src/service.ts` | Service\<T\> 抽象基类 |
| `packages/loader/` | YAML 配置加载器 |
| `packages/hmr/` | 热更新支持 |
| `packages/group/` | 插件分组 |

**核心类**：`Context`、`RegistryService`、`EventsService`、`Fiber`、`Service<T>`

### agency-agents

| 属性 | 值 |
|------|-----|
| 路径 | `external/libs/models/ai/agency-agents/` |
| 类型 | Markdown 文件集合（280+ agent persona） |
| 定位 | AI Agent Persona 角色库，跨 18 个专业部门 |
| 许可证 | MIT |

**关键目录**：

| 目录 | 用途 |
|------|------|
| `engineering/` | 工程角色（前端/后端/AI/DevOps/安全等，~50个） |
| `marketing/` | 营销角色（含中国市场：抖音/小红书/B站/微信等，~40个） |
| `specialized/` | 综合专家（多代理编排、MCP构建等，~60个） |
| `game-development/` | 游戏开发（Unity/Godot/Unreal等，~20个） |
| `design/` | 设计角色（UI/UX/品牌等，10个） |
| `strategy/` | 策略手册（playbooks/runbooks/handoff-templates） |
| `integrations/` | 多工具适配脚本（Claude Code/Cursor/Codex/Gemini等） |
| `scripts/` | 安装/转换/检查脚本 |

### anthropics/skills

| 属性 | 值 |
|------|-----|
| 路径 | `external/libs/models/ai/anthropics/skills/` |
| 类型 | Claude Skills 参考实现（Markdown + Python） |
| 定位 | Anthropic 官方发布的 Agent Skills 示例库 |
| 标准 | 兼容 [Agent Skills 开放标准](https://agentskills.io) |

**关键技能**：`algorithmic-art`、`canvas-design`、`claude-api`（多语言文档）、`docx`、`frontend-design`、`mcp-builder`、`pdf`、`pptx`、`skill-creator`

### book-to-skill

| 属性 | 值 |
|------|-----|
| 路径 | `external/libs/models/ai/book-to-skill/` |
| 语言 | Python 3.9+（hatchling 构建） |
| 定位 | 将书籍/文档编译为结构化 Agent Skill 的工具 |
| 核心创新 | "编译时知识蒸馏"范式，声称节省 24×–51× token |

**关键文件**：

| 文件 | 用途 |
|------|------|
| `book_to_skill/cli.py` | CLI 入口 |
| `book_to_skill/utils.py` | 主流程（章节检测、多源解析） |
| `book_to_skill/parsers/` | 7 种格式解析器（pdf/epub/docx/html/rtf/calibre/text） |
| `book_to_skill/sanitize.py` | 文本清洗 |
| `tools/validate_skill.py` | SKILL.md 合规校验 |
| `SKILL.md` | 自身也是一个 Agent Skill |

### i-have-adhd

| 属性 | 值 |
|------|-----|
| 路径 | `external/libs/models/ai/i-have-adhd/` |
| 类型 | 纯声明式 SKILL.md + Hook 脚本 |
| 定位 | ADHD 友好型 Agent 输出风格技能 |
| 科学基础 | 认知科学 5 条 ADHD 阅读事实 → 10 条输出规则 |

**关键文件**：

| 文件 | 用途 |
|------|------|
| `skills/i-have-adhd/SKILL.md` | 核心 10 条规则定义 |
| `hooks/hooks.json` | SessionStart 钩子配置 |
| `hooks/always-on.sh` | 常驻模式检测脚本 |
| `evals/rubric.md` | 评估标准 |

### intelligent-terminal

| 属性 | 值 |
|------|-----|
| 路径 | `external/libs/models/ai/intelligent-terminal/` |
| 语言 | C++/XAML + Rust |
| 定位 | 微软 Windows Terminal 实验性分支，内置原生 Agent 集成 |
| 协议 | [ACP (Agent Client Protocol)](https://agentclientprotocol.com) |

**关键目录与文件**：

| 文件/目录 | 用途 |
|-----------|------|
| `src/cascadia/TerminalApp/TerminalPage.cpp` | Agent 集成主入口 |
| `src/cascadia/TerminalApp/AgentPaneContent.cpp` | Agent 面板 XAML 封装 |
| `src/cascadia/TerminalProtocol/TerminalProtocol.idl` | WinRT COM 接口定义 |
| `tools/wta/src/master/mod.rs` | wta-master：Agent CLI 生命周期管理（Rust） |
| `tools/wta/src/app.rs` | wta-helper：每标签页 ACP 会话（Rust） |
| `doc/bot.md` | Bot 架构文档 |

**架构**：helper+master 双进程、COM 进程外服务器、OSC 133 错误事件总线、预热启动+Stash 面板模式

### Second-Me (mindverse)

| 属性 | 值 |
|------|-----|
| 路径 | `external/libs/models/ai/mindverse/`（Second-Me 项目） |
| 语言 | Python + TypeScript |
| 定位 | 本地 AI 自我（AI-native Memory），分层记忆建模 + LoRA 个性化 |
| 部署 | Docker（GPU/CUDA/CPU/Apple MLX） |

**关键目录与文件**：

| 文件/目录 | 用途 |
|-----------|------|
| `lpm_kernel/L0/` | 第0层：原始记忆摄取（l0_generator.py, models.py） |
| `lpm_kernel/L1/bio.py` | 第1层：记忆分块（Chunk 类）、记忆类型、分析类型 |
| `lpm_kernel/L1/l1_generator.py` | L1 身份洞察生成器 |
| `lpm_kernel/L1/shade_generator.py` | 人格阴影生成器 |
| `lpm_kernel/L2/train.py` | 第2层：LoRA 训练主逻辑 |
| `lpm_kernel/L2/dpo/` | DPO 偏好对齐训练 |
| `lpm_kernel/L2/data_pipeline/` | 数据流水线（SelfQA、GraphRAG 索引） |
| `lpm_kernel/api/domains/kernel2/` | 聊天/提示策略/角色/知识服务 |
| `lpm_kernel/api/domains/space/` | AI Space 多人协作 |
| `lpm_kernel/file_data/` | 多格式文件处理（ChromaDB 向量存储） |
| `lpm_frontend/` | Next.js 前端 |

**核心概念**：三层记忆架构 L0→L1→L2、Me-Alignment 算法、Roleplay 人格切换、AI Space 去中心化协作

## 跨项目架构概念索引

| 架构概念 | 主要实现项目 | 对应概念文档 |
|----------|-------------|-------------|
| Agent 核心循环 | hermes-agent, veadk-python, Zleap-Agent, deepseek-harness | [01-agent-loop.md](../concepts/01-agent-loop.md) |
| 工具系统 | hermes-agent (ToolRegistry), Zleap-Agent (ToolRegistry), deepseek-harness (Service Seam) | [02-tool-system.md](../concepts/02-tool-system.md) |
| 记忆架构 | veadk-python (ST/LT Memory), Zleap-Agent (pgvector+RRF), Second-Me (L0-L2 HMM) | [03-memory-architecture.md](../concepts/03-memory-architecture.md) |
| 多代理编排 | hermes-agent (MoA), Zleap-Agent (Workspace Pipeline), deepseek-harness (subagent) | [04-multi-agent.md](../concepts/04-multi-agent.md) |
| Provider 抽象 | hermes-agent (适配器), Zleap-Agent (ProviderRegistry), veadk-python (runtime委托) | [05-provider-abstraction.md](../concepts/05-provider-abstraction.md) |
| 上下文管理 | Zleap-Agent (记忆压缩), deepseek-harness (compaction), book-to-skill (分层加载) | [06-context-management.md](../concepts/06-context-management.md) |
| 技能/Persona | anthropics (SKILL.md), agency-agents (280+ persona), book-to-skill, i-have-adhd | [07-skill-persona.md](../concepts/07-skill-persona.md) |
| 插件架构 | Cordis (Context/Fiber/Service), deepseek-harness (一切皆插件), Zleap-Agent (Registry) | [08-plugin-architecture.md](../concepts/08-plugin-architecture.md) |
| Agent 通信协议 | intelligent-terminal (ACP), deepseek-harness (MCP), Zleap-Agent (MCP) | [09-agent-protocols.md](../concepts/09-agent-protocols.md) |
