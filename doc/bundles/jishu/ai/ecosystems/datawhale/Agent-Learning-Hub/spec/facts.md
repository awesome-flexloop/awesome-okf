---
type: spec
title: "Facts - Agent-Learning-Hub"
---

# Facts - Agent-Learning-Hub

> R阶段事实采集，零推测，每条事实指向源码位置。

## F-001 项目基本信息

- 项目名称：Agent Learning Hub
- 一句话定位：A curated AI Agent learning roadmap for people who want to build useful, reliable agents instead of collecting random links
- 仓库只维护一个核心展示面：README.md
- 目标：把社区优秀分享、官方博客、论文、开源项目和真实工程经验，整理成可照着执行的 AI Agent 学习 todo list
- 维护者：陈思州（https://github.com/jjyaoao），Datawhale 成员
- 来源：README.md:1-9

## F-002 项目文件组成

- 仓库包含两个核心文件：`README.md` 和 `index.html`
- `README.md`：Markdown 格式的完整学习路线图，包含所有内容
- `index.html`：README 内容的交互式 Web 版本，单文件 HTML（内嵌 CSS + JS），使用 marked.js 渲染 Markdown
- 来源：README.md 全文；index.html 全文

## F-003 index.html 交互功能

- 顶部导航三个标签页：学习路线、项目阶梯、精选资源
- 左侧侧边栏：按阶段/层级/分类展示导航，带计数徽章
- 进度条：统计勾选完成的 checklist 项百分比，数据存储于 localStorage
- 搜索功能：实时过滤内容，高亮匹配关键词
- 暗色/亮色主题切换，主题偏好存储于 localStorage
- 笔记编辑器：每个阶段可添加 Markdown 笔记，支持预览，存储于 localStorage
- 响应式布局：移动端侧边栏抽屉式展开
- 外部依赖：marked.js（CDN 加载，https://cdn.jsdelivr.net/npm/marked/marked.min.js）
- 来源：index.html:7-252（CSS）、288-607+（JS 数据与逻辑）

## F-004 当前优先学习方向（5项）

| 优先级 | 方向 | 理由 |
|--------|------|------|
| 1 | Claude Code / Codex-style coding agents | 真实代码库、shell、文件编辑、测试、权限、上下文压缩，最好的 agent 工程样本 |
| 2 | Agent harness engineering | agent 能力很大一部分来自 harness：工具协议、权限、状态、反馈、回放、CI、评测 |
| 3 | OpenClaw / Hermes-style personal agents | 长运行、本地优先、跨应用、记忆、skills、消息入口，像"个人操作系统" |
| 4 | Skills / MCP / A2A / ACP | skills 负责能力复用，MCP 连接工具，A2A 连接 agent，ACP 连接宿主应用 |
| 5 | Evaluation and safety | 没有 eval、trace、权限边界的 agent 只能算 demo |

- 明确不建议重押老式 crew/role-play 框架
- 来源：README.md:18-30

## F-005 Learning Todo List 阶段结构（Stage 0-8，共9阶段）

| 阶段 | 标题 | 核心内容 | 产出物 |
|------|------|---------|--------|
| Stage 0 | Understand What An Agent Is | 区分 chatbot/workflow/agent/multi-agent；agent 基本循环 observe→think→act；何时不该用 agent | 一页短笔记回答"为什么需要 agent 而非 workflow" |
| Stage 1 | Build A Minimal Agent Loop | LLM API 对话、结构化 JSON、工具函数定义、tool call 解析与执行、最大步数/超时/错误处理 | 50-150 行最小 agent |
| Stage 2 | Learn Tool Use, RAG, And Memory | RAG（chunk/embed/retrieve/citation）、多类型工具接入、短期/会话/长期记忆、工具失败处理、来源引用 | 资料研究助手 |
| Stage 3 | Study One Modern Agent Harness | 读懂 harness 目录结构、agent loop/tool registry/permission gate/session store/context compaction、trace 观察、裸 loop vs harness 对比 | 可调试的 agent harness demo |
| Stage 4 | Multi-Agent Is Coordination, Not Magic | planner/executor/reviewer/critic/router 角色、supervisor/graph 管理、职责边界与 schema、循环/争论/漂移处理、判断何时单 agent 更好 | 小型多 agent 系统（research→write→review→revise） |
| Stage 5 | Learn Skills, Protocols, And Capability Packaging | Skill vs Tool vs Prompt vs MCP 区别、Claude Code Skills 文件结构、OpenClaw Skills 加载与安全、写 SKILL.md、smoke test | 可复用 skill（code-review/research-report 等） |
| Stage 6 | Browser And Computer-Use Agents | browser agent vs API tool 区别、Playwright/browser-use、安全限制、页面变化/弹窗/失败处理、截图/DOM/动作日志 | 只操作公开网页的 browser agent |
| Stage 7 | Evaluation, Observability, And Safety | 固定测试集、成功率/失败原因/成本/延迟记录、trace 分析、危险工具人工确认、prompt injection 风险、回归测试 | agent eval 表格（≥20 任务） |
| Stage 8 | Ship A Real Agent | 明确用户/任务/成功标准、日志/trace/重试/超时/成本上限、权限边界、部署方式（CLI/Web/Slack/Action）、README | 别人能 clone 跑的 agent 项目 |

- 每个阶段包含 checklist 项、推荐阅读、开源项目参考（部分阶段）、产出物
- 来源：README.md:32-202

## F-006 Project Ladder（11级项目阶梯）

| 级别 | 项目 | 学到什么 |
|------|------|---------|
| 1 | Calculator Agent | 最小 tool call loop |
| 2 | Web Research Agent | 搜索、筛选、引用、总结 |
| 3 | PDF QA Agent | RAG、chunk、retrieval、citation |
| 4 | Coding Review Agent | 读取 diff、风险排序、测试建议 |
| 5 | Browser Agent | 页面观察、点击、提取、失败恢复 |
| 6 | Claude Code-like Nano Agent | shell、文件编辑、权限、session、compact |
| 7 | OpenClaw-like Gateway | channel、routing、session、memory、heartbeat、delivery |
| 8 | Reusable Skill Pack | SKILL.md、脚本、模板、触发条件、smoke test |
| 9 | Multi-Agent Writer | planner、writer、reviewer 协作 |
| 10 | Personal Agent | OpenClaw/Hermes-style 记忆、skills、消息入口 |
| 11 | Production Harness | evals、trace、权限、CI、runner、回放 |

- 来源：README.md:204-218

## F-007 Curated Resources 分类结构

资源精选分为以下子类：

1. **Official Guides And Blogs**（官方指南与博客）：15 条，含 Anthropic Building effective agents、Claude Code 系列文档、OpenAI agent 指南、Gemini 文档、Google ADK、MCP 等
2. **Project Map**（项目地图）：按学习目的分 7 层——Build From Scratch、Personal/Always-On Agents、Coding Agents、Agent Harness/SuperAgent Runtime、Deep Research/RAG Agents、Tutorial Encyclopedias、Browser/Multimodal Agents
3. **Skills, Protocols, And Tooling**：Skills、MCP、A2A、ACP、Skill Quality 五个概念，每个附学习资源
4. **Modern Agent Systems**（现代 Agent 系统）：13 个系统，含 Claude Code、learn-claude-code、claw0、hello-agents、OpenClaw、Hermes Agent、CyberClaw、DeerFlow、smolagents、LangGraph、Qwen-Agent、Pydantic AI、pi
5. **Legacy Or Optional Frameworks**（遗留或可选框架）：CrewAI、AutoGen、LangChain Agents（标注不建议作为主线）
6. **Papers**（论文）：17 篇，含 ReAct、Toolformer、Reflexion、Generative Agents、Voyager、AutoGen、AgentBench、WebArena、SWE-bench、GAIA、OSWorld、τ-bench、SWE-agent、Dive into Claude Code、AI Harness Engineering 等
7. **GitHub Repositories**（GitHub 仓库）：23 个仓库，含 hello-agents、learn-claude-code、claw0、OpenClaw、Hermes Agent、CyberClaw、DeerFlow、GenAI_Agents、smolagents、codex、opencode、aider、goose、LangGraph、openai-agents-python、Qwen-Agent、browser-use、UI-TARS-desktop、SWE-agent、OpenHands、ai-agents-for-beginners 等
8. **Thoughtful Blogs**（深度博客）：Lilian Weng、Simon Willison、LangChain Blog、Google Developers Blog
9. **Claude Code Study Path**（Claude Code 学习路径）：官方文档→复刻项目→架构解析→工程对照，含 7 个资源

- 来源：README.md:220-371

## F-008 Learning Principles（8条学习原则）

1. Build first, then read deeper.
2. Prefer small reliable agents over impressive demos.
3. Use tools with strict schemas.
4. Add evals before you add more agents.
5. Trace every important run.
6. Treat multi-agent as a coordination problem.
7. Keep humans in the loop for risky actions.
8. Respect platform rules, copyrights, and data access boundaries.

- 来源：README.md:373-382

## F-009 How To Use（四类使用方式）

- 新手：按 Learning Todo List 从上到下做，每完成一项打勾
- 已会 LLM 应用：从 Stage 2 或 Stage 3 开始，重点补 Agent loop、工具调用、评测和工程化
- 想做项目：直接看 Project Ladder，每档做一个可运行作品
- 只想找资料：看 Curated Resources，优先读官方文档和经典论文
- 来源：README.md:11-16

## F-010 Contributing 贡献指南

- 欢迎的贡献：官方文档和工程博客、高质量论文和 benchmark、有可运行代码的开源仓库、有原创见解的技术博客、帮助练习特定技能的小项目
- 避免的贡献：搬运的平台帖子、无实质内容的课程广告、私有或付费材料、绕过平台规则的抓取内容
- 来源：README.md:384-399
