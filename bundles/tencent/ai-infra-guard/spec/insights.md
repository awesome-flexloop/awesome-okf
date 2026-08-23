---
type: spec-insights
title: AI-Infra-Guard 架构洞察
---

# AI-Infra-Guard 架构洞察

> I阶段产出。基于 facts.md 中 F-001 ~ F-068 事实提炼。

## 核心洞察一：Go 内核 + Python 卫星的多语言混合架构

**陈述**：AI-Infra-Guard 的核心扫描引擎（指纹识别、漏洞匹配、HTTP 探测、WebSocket 调度）用 Go 实现，而 AI 密集型任务（MCP 代码审计、Agent 安全评估、Prompt 越狱测试）通过子进程调用 Python 脚本完成，两者通过 stdout JSON 行协议通信。

**证据**：
- F-024~F-030：Runner 纯 Go 实现，含 httpx、fastdialer、ratelimit、fingerprint engine、advisory engine
- F-047~F-050：McpTask/AgentTask/ModelRedteamReport/SkillTask 均调用 `uv run --no-project main.py` 或 `cli_run.py`
- F-051：`ParseStdoutLine` 解析 Python stdout 首字符为 `{` 的 JSON 行
- F-046：AIInfraScanAgent 是唯一纯 Go 实现的任务类型

**反常识**：通常安全工具要么全 Go（快速、单二进制），要么全 Python（AI 生态丰富）。AIG 选择了"能 Go 则 Go，需 AI 则 Python"的混合策略——Go 负责高并发网络探测和规则匹配，Python 负责 LLM 驱动的语义分析。这不是技术债务，而是刻意的架构边界划分。

**行动**：理解系统时先分清"哪部分在 Go 进程内"和"哪部分是 Python 子进程"。扩展新扫描能力时，网络/规则类用 Go，LLM 推理类用 Python，通过 `TaskInterface` + `ParseStdoutLine` 协议接入。

## 核心洞察二：分布式 Server-Agent 架构，WebSocket 双向通信 + SSE 前端推送

**陈述**：系统由 Server（Gin HTTP + WebSocket）、Agent Workers（独立 Go 二进制）、Frontend（React SPA）三部分组成。Server 通过 WebSocket 向 Agent 下发任务，Agent 通过 8 种事件类型回传进度，Server 通过 SSE 向前端实时推送。

**证据**：
- F-007：REST API `/api/v1/app/tasks`、WebSocket `/api/v1/agents/ws`、SSE `/api/v1/app/tasks/sse/:sessionId`
- F-016：TaskManager 使用 round-robin (`dispatchCounter`) 在多个 Agent 间分发任务
- F-012~F-014：AgentConnection 管理心跳（pingPeriod/pongWait）、注册、事件转发
- F-020：8 种事件类型：liveStatus, planUpdate, newPlanStep, statusUpdate, toolUsed, actionLog, resultUpdate, error
- F-039~F-040：Agent 客户端通过 `RegisterTaskFunc` 注册能力，Capabilities 上报给 Server

**反常识**：Agent 不是简单的"远程执行器"——它自己维护任务计划（3-4 步 SubTask）、工具状态（doing/done）、动作日志，Server 只做路由和存储。这种"胖 Agent、瘦调度"的设计让 Agent 可以独立运行复杂工作流，Server 无需理解每种任务的内部逻辑。

**行动**：调试任务问题时，在 Agent 日志中搜索 sessionId 可追踪完整执行链。部署多 Agent 时，Server 自动负载均衡，无需额外配置。

## 核心洞察三：自研声明式 DSL 驱动指纹与漏洞匹配

**陈述**：指纹识别和漏洞匹配都由同一套自研 DSL 引擎驱动，支持 body/header/icon/hash 四种匹配源，= / == / != / ~= 四种操作符，&& / || 逻辑组合，以及 version > >= < <= 语义化版本比较。

**证据**：
- F-031~F-035：parser 包含词法分析（Token）、语法分析（AST：dslExp/logicExp/bracketExp）、求值器（Eval/AdvisoryEval）
- F-032：比较操作符 `=`(contains)、`==`(exact)、`!=`、`~=`(regex)；版本操作符 `>`/`>=`/`<`/`<=`
- F-037：VersionVul.Rule 是字符串，加载时编译为 `*parser.Rule`
- F-038：GetAdvisories 对匹配的指纹名调用 RuleCompile.AdvisoryEval
- F-034：hash matcher 不能与其他 matcher 共存（hashUsage 校验）

**反常识**：没有使用 Lua/WASM/Rego 等嵌入式规则语言，而是自研了一个极简 DSL。这降低了规则编写门槛（安全研究员可直接写 YAML），但也意味着 DSL 能力有上限——不支持算术、变量赋值、循环。

**行动**：添加新指纹/漏洞规则时只需写 YAML，无需改代码。理解规则匹配原理可阅读 parser/synax.go 的 Eval 方法。

## 核心洞察四：四种任务类型覆盖 AI 基础设施安全的四个维度

**陈述**：系统定义了 7 种任务类型常量，但实际由 5 个 TaskInterface 实现处理，覆盖：基础设施漏洞扫描（纯 Go）、MCP 插件安全（Python AI 审计）、大模型越狱评测（Python 自动化红队）、Agent 安全评估（Python 动态测试）、Skill 代码审计（Python AI 审计）。

**证据**：
- F-041：7 个任务类型常量（含 Test-Demo 和 Model-Jailbreak）
- F-046：AIInfraScanAgent — 指纹+CVE+端口扫描+AI 未授权分析
- F-047：McpTask — code 模式（代码审计）/ url 模式（恶意行为检测）
- F-048：AgentTask — Agent Provider YAML 驱动的安全评估
- F-049：ModelRedteamReport — 多模型并行越狱评测，支持数据集
- F-050：SkillTask — Skill 项目代码审计

**反常识**：四种核心任务并非简单并列——它们共享同一套 Agent 通信协议、任务计划模型（SubTask/Tool/ActionLog）、前端渲染逻辑。差异仅在 `Execute()` 内部实现和 Python 子系统的入口脚本。

**行动**：新增任务类型只需实现 TaskInterface 接口（GetName + Execute），并在 cmd/agent/main.go 中注册。前端无需改动即可展示进度。

## 核心洞察五：数据即规则——YAML 驱动的可扩展知识库

**陈述**：142 个指纹、2014 个 CVE、15 个 MCP 插件规则、17 个评测集全部以 YAML/JSON 文件存储，程序启动时加载编译，支持中英文双语漏洞库。

**证据**：
- F-061：142 个指纹 .yaml 文件
- F-062：2014 个漏洞 .yaml 文件，按组件分目录（dify/vllm/ray/n8n 等），vuln/ 和 vuln_en/ 双语
- F-063：15 个 MCP 插件规则 .yaml
- F-064：17 个评测集 .json（advbench/JailBench/CBRN 等）
- F-025：Runner 初始化时加载 FPTemplates 和 AdvTemplates 目录
- F-003：--fps/--vul 参数可指定自定义数据路径
- F-053：MCP Scanner.RegisterPlugin 从 data/mcp/ 加载

**反常识**：漏洞库规模（2014）远大于指纹库（142）——平均每个指纹组件关联约 14 个 CVE。这不是"一个指纹一个漏洞"的简单映射，而是一个组件可能有多个版本区间的漏洞，且中英文各一份导致文件数翻倍。

**行动**：更新安全能力优先更新数据文件而非代码。自定义扫描可通过 --fps/--vul 指定私有规则库。

---

## 知识地图

```
ai-infra-guard/
│
├── 入门层（先读）
│   ├── 00-architecture.md      ← 洞察二：整体架构
│   └── 01-task-types.md        ← 洞察四：四种任务
│
├── 核心层（理解引擎）
│   ├── 02-fingerprint-dsl.md   ← 洞察三：指纹DSL
│   ├── 03-vuln-matching.md     ← 洞察三：漏洞匹配
│   └── 04-websocket-protocol.md ← 洞察二：通信协议
│
├── 进阶层（扩展开发）
│   ├── 05-python-bridge.md     ← 洞察一：Go/Python桥接
│   └── 06-mcp-scan.md          ← MCP安全扫描
│
├── 示例层
│   ├── cli-scan.md             ← 命令行扫描
│   ├── custom-fingerprint.md   ← 自定义指纹
│   └── docker-deploy.md        ← Docker部署
│
└── 信源层（事实溯源）
    ├── go-server.md            ← WebSocket/HTTP Server
    ├── scan-engine.md          ← Runner/指纹/漏洞引擎
    ├── vuln-struct.md          ← 漏洞数据结构
    ├── python-subsystems.md    ← 三个Python子系统
    └── data-rules.md           ← 数据文件与规则格式
```

## 事实覆盖矩阵

| 概念文档 | 覆盖事实编号 |
|---------|------------|
| 00-architecture | F-006~F-010, F-012~F-016, F-039, F-067 |
| 01-task-types | F-041~F-050, F-061~F-064 |
| 02-fingerprint-dsl | F-031~F-035, F-061, F-066 |
| 03-vuln-matching | F-036~F-038, F-062, F-028 |
| 04-websocket-protocol | F-009~F-023, F-052 |
| 05-python-bridge | F-047~F-051, F-058~F-060 |
| 06-mcp-scan | F-053~F-057, F-063 |
