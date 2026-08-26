---
okf_version: "0.2"
type: group
title: "🤖 AI Agent 框架"
description: "AI Agent 运行时框架与架构模式——从工具调用循环到多代理编排、记忆系统、插件架构的源码级中文教程"
total_bundles: 21
---

# 🤖 AI Agent 框架

本组存放 AI Agent 运行时框架与架构模式的源码中文教程，覆盖 Python/TypeScript/C++/Rust/Go 五种语言生态中 21 个开源项目的核心架构设计。从 Agent 基础概念到生产级框架实现，从插件架构到多Agent编排，从通信协议到 Coding Agent 源码解读，构建完整的 AI Agent 知识体系。

## 推荐学习路径

```
🧱 ai-agent-fundamentals  Agent跨项目基础（6大架构模式对比）—— 必读起点
  ↓
🔌 cordis                 插件元框架（DI容器+Fiber生命周期+事件总线）—— 架构底座
  ↓
┌────────────────────────────────────────────────────────────┐
│  选一个Tier 1主力框架深入学习（根据语言/场景偏好）：          │
│  🐍 hermes-agent      多Provider/平台Python框架            │
│  🐍 veadk-python      火山引擎SDK（豆包+A2A/A2UI）         │
│  📘 zleap-agent       Workspace-first（TS+Rust Tauri）    │
│  📘 deepseek-harness  Cordis插件架构（50+包TS monorepo）  │
│  💻 intelligent-terminal Windows Terminal（C++/Rust+ACP） │
└────────────────────────────────────────────────────────────┘
  ↓
┌────────────────────────────────────────────────────────────┐
│  Tier 2-3 专项深入（按需选读）：                              │
│  🧠 second-me          个人AI分身（三层记忆HMM+LoRA）       │
│  👥 agency-agents      270+ Persona角色库+NEXUS编排       │
│  🖥️ agency-agents-app  Tauri+Svelte5桌面工作台            │
│  📋 anthropics-skills  Anthropic Skills规范最佳实践        │
│  📚 book-to-skill      书籍→技能编译器                     │
│  🧩 i-have-adhd        ADHD认知辅助技能（10条规则）        │
└────────────────────────────────────────────────────────────┘
```

---

## 知识包导航

### 🧱 跨项目基础

| 知识包 | 文档数 | 一句话简介 |
|--------|--------|-----------|
| [ai-agent-fundamentals](ai-agent-fundamentals/index.md) | 6+3+1=10 | Agent跨项目架构模式——6大核心模式对比（核心循环/Provider/插件/多Agent/记忆/MCP-ACP），4框架代码级对比，框架选型指南 |

### ⚙️ Tier 1：大型框架/运行时

| 知识包 | 语言 | 文档数 | 一句话简介 |
|--------|------|--------|-----------|
| [hermes-agent](hermes-agent/index.md) | Python | 10+4+1=15 | 渐进式披露多Agent框架——Think-Act-Observe循环、ToolRegistry(100+工具)、34+模型Provider、8种记忆插件、MCP/ACP双协议、Gateway多平台网关(22+消息平台)、Cron调度 |
| [veadk-python](veadk-python/index.md) | Python | 10+4+1=15 | 火山引擎Agent SDK——Agent/Runner双层架构、豆包/方舟原生集成、A2A/A2UI协议、RAG知识库(8种向量后端)、双层记忆、Sequential/Parallel/Loop/Supervisor组合模式、Tunnel内网桥接 |
| [zleap-agent](zleap-agent/index.md) | TS/Rust | 10+4+1=15 | Workspace-first Agent——Run→Work→WorkStep三级Fiber状态机、PostgreSQL+pgvector双线记忆(A/B线+RRF融合)、飞书/微信/Feishu CLI网关、子Agent委派、pg-boss定时任务 |
| [deepseek-harness](deepseek-harness/index.md) | TypeScript | 10+4+1=15 | DeepSeek Agent框架——Cordis插件架构(50+包)、Phase状态机+Inbox双队列、defineTool类型安全工具、Event-Sourcing会话、MCP/ACP双协议、Skill分层系统 |
| [intelligent-terminal](intelligent-terminal/index.md) | C++/Rust | 10+4+1=15 | Windows Terminal原生Agent——双进程架构(Helper+Master)、COM协议服务器、命名管道传输、ACP JSON-RPC 2.0、OSC 133自动修复、Agent Pane XAML UI、wtcli命令工具 |

### 🔌 Tier 2：中型框架/库

| 知识包 | 语言 | 文档数 | 一句话简介 |
|--------|------|--------|-----------|
| [cordis](cordis/index.md) | TypeScript | 7+3+1=11 | 可组合插件元框架——Context DI容器、Proxy代理构造、Fiber六状态生命周期、5种事件派发模式、Reflect元数据、Timer调度，hermes/zleap/deepseek-harness共同的架构底座 |
| [second-me](second-me/index.md) | Python/TS | 7+3+1=11 | 个人AI数字分身——L0→L1→L2三层记忆HMM、LoRA微调(r=64/alpha=16)+DPO对齐、GGUF量化+llama.cpp本地推理、14步训练流水线、Flask API、Space多Agent策略 |

### 🎯 Tier 3：专项工具/应用/技能

| 知识包 | 类型 | 文档数 | 一句话简介 |
|--------|------|--------|-----------|
| [agency-agents](agency-agents/index.md) | 角色库 | 4+1+1=6 | 270+专业Agent Persona库——17部门分类体系、Markdown模板规范、NEXUS 7阶段编排框架(Full/Sprint/Micro三模式)、16种工具集成适配、convert.sh多格式转换 |
| [agency-agents-app](agency-agents-app/index.md) | 桌面应用 | 3+1+1=5 | Agency Agents桌面工作台——Tauri 2(Rust)+Svelte 5(Runes)、三源Catalog模型、五状态安装协调、35个Tauri命令、⌘K命令面板、Preset Teams策展 |
| [anthropics-skills](anthropics-skills/index.md) | 技能规范 | 4+1+1=6 | Anthropic官方Skills参考——SKILL.md格式标准(6字段)、三级渐进式加载、.skill分发包、eval双slave评估基准、A/B盲比、17个内置Skill分类 |
| [book-to-skill](book-to-skill/index.md) | 知识工具 | 4+1+1=6 | 书籍→Agent Skill编译器——确定性文本提取、7种文档格式解析器、13语言章节检测、四层产出流水线、多层安全防护 |
| [i-have-adhd](i-have-adhd/index.md) | 辅助技能 | 3+1+1=5 | ADHD认知辅助技能——10条ADHD友好输出规则、Session Hooks偏好持久化、10+IDE/Agent平台集成、Always-On跨应用模式 |
| [cli-anything](cli-anything/index.md) | CLI框架 | 8+3+6=17 | Agent原生CLI接口框架——ReplSkin双语终端外壳、SKILL.md自动生成(AST+Jinja2)、PreviewBundle v1三层持久化协议、CLI-Hub包管理器(注册表+pip安装器)、Matrix技能矩阵、Cursor/Claude/Codex多平台插件适配、四层测试与真实软件原则 |

### 💻 Tier 4：Coding Agent 源码解读

| 知识包 | 语言 | 文档数 | 一句话简介 |
|--------|------|--------|-----------|
| [codewhale](codewhale/index.md) | Rust | 8+2+1=11 | CodeWhale Coding Agent——21 crate Cargo workspace、Fleet多Agent控制平面、Workflow双轨引擎(TOML+JS)、MCP安全三重防护、Skill四层所有权架构、ExecPolicy沙箱(Seatbelt/bwrap) |
| [deepseek-reasonix](deepseek-reasonix/index.md) | Go/TS | 8+2+1=11 | DeepSeek Reasonix——ACP v1协议(JSON-RPC/Factory/inbox)、Agent运行循环(arbiter/governor/compaction)、Bot网关(QQ/飞书适配器)、Checkpoint恢复(fork/branch)、Fleet DAG调度、Wails桌面应用 |
| [openai-codex](openai-codex/index.md) | TS/Rust/Py | 7+2+1=10 | OpenAI Codex CLI——三语言架构(Node.js CLI+Rust TUI+Python SDK)、Bazel构建、三层沙箱防御(平台沙箱/execpolicy/SafetyCheck)、AGENTS.md目录树发现、Skills显式/隐式调用 |
| [nanobot](nanobot/index.md) | Python/TS | 6+1+1=8 | Nanobot Agent——Python Agent核心(AgentLoop/Runner)、MessageBus消息总线+WebSocket协议、SDK类型系统(StreamEvent/RunResult)、CLI/TUI(Bun+OpenTUI)/WebUI(React+Vite)三端架构 |
| [deepcode-cli](deepcode-cli/index.md) | TypeScript | 5+1+1=7 | DeepCode CLI——三包monorepo(cli/core/vscode-ide-companion)、10种权限作用域(read-in-cwd/network/git等)、MCP客户端(mcp__server__tool命名空间)、12个斜杠命令 |
| [opencode](opencode/index.md) | TypeScript | 5+1+1=7 | OpenCode Terminal Coding Agent——Bun+Turbo+SST技术栈、SessionV2会话模型(Context Epoch)、V2配置规范、infra模块(app/console/lake/stage/stats/secret)、Cloudflare+AWS混合云部署 |
| [pi-cli](pi-cli/index.md) | TypeScript | 5+1+1=7 | Pi AI CLI——9包monorepo(ai/tui/agent/client/server/evals等)、AI包(models/oauth/cli/compat/images)、TUI差分渲染引擎、5个内置prompt(cl/is/pr/sa/wr)、锁步版本控制 |

---

## 跨项目概念对照

以下核心概念在多个框架中有不同实现，建议对照学习：

| 核心概念 | hermes-agent | zleap-agent | deepseek-harness | veadk-python | intelligent-terminal | cordis |
|---------|-------------|-------------|-----------------|-------------|---------------------|--------|
| Agent循环 | AIAgent Think-Act-Observe | Run→Work→WorkStep Fiber | Phase+Inbox双队列 | Agent+Runner双层 | Helper→Master双进程 | — |
| 插件系统 | Plugin注册表 | Service扩展 | Cordis Context/Service | 配置式组合 | COM+注册表 | Context+Fiber+Plugin |
| 工具注册 | ToolRegistry单例(100+) | MCP+内置工具 | defineTool+Cascade | Tool延迟注册 | wtcli+SendEvent | — |
| 记忆系统 | MemoryManager+8插件 | PG+pgvector双线 | Session/Scope/Compaction | Short+Long双层 | — | — |
| 多Agent | Gateway+LRU缓存 | Workspace Handoff | SubagentProvider | Sequential/Parallel/Loop | 多Agent CLI支持 | — |
| 通信协议 | MCP+ACP+22平台 | Gateway(飞书/微信) | MCP stdio/HTTP+ACP | A2A/A2UI/Tunnel | ACP JSON-RPC+命名管道 | — |
| 事件系统 | Cordis Events | Event Bus | Cordis Waterfall | 回调钩子 | COM事件队列 | 5种dispatch模式 |

---

> **信任声明**：本分组索引基于 21 个 AI Agent 开源项目源码逐模块分析生成，所有知识包均经 OKF 五阶段流程（R→I→E→V→C）验证。
> 
> **生成时间**：2026-08-23 | **维护者**：OKF Wiki Bot
> 
> **内容统计**：21 个知识包，共 213 个内容文档（140 概念 + 48 示例 + 25 信源），1500+ 条零推测事实，21 个 facts.md 信源底稿

```{toctree}
:maxdepth: 7

ai-agent-fundamentals/index
hermes-agent/index
veadk-python/index
zleap-agent/index
deepseek-harness/index
intelligent-terminal/index
cordis/index
second-me/index
agency-agents/index
agency-agents-app/index
anthropics-skills/index
book-to-skill/index
i-have-adhd/index
codewhale/index
deepseek-reasonix/index
openai-codex/index
nanobot/index
deepcode-cli/index
opencode/index
pi-cli/index
```
