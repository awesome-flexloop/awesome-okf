---
okf_version: "0.2"
type: Concept
title: "工具、技能与 MCP：能力扩展的三条路径"
description: "MAF 的工具类型与审批边界、代理即工具、MCP 集成、Agent Skills 的目录规范与四阶段渐进式披露、文件/代码/类三种技能形态"
tags: [工具, 工具审批, MCP, Agent Skills, 渐进式披露, SKILL.md]
generated: { by: "blog-article-to-okf-bundle", at: "2026-11-10T14:56:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T14:56:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: learn-tools
    resource: https://learn.microsoft.com/zh-cn/agent-framework/agents/tools/
  - id: learn-skills
    resource: https://learn.microsoft.com/zh-cn/agent-framework/agents/skills
  - id: learn-agents
    resource: https://learn.microsoft.com/zh-cn/agent-framework/agents/
---

# 工具、技能与 MCP：能力扩展的三条路径

代理的能力边界由三样东西决定：它能调用什么（工具）、它知道怎么做事（技能）、它能连到哪些外部系统（MCP）。MAF 把这三条路径分开设计，各有自己的扩展点与安全边界。

## 工具类型：从函数到托管工具

官方工具清单（F-045）可以按“谁执行”分成三组：

| 组别 | 工具 | 执行位置 |
|------|------|---------|
| **客户端执行** | 函数工具、Shell 工具 | 你的应用进程或本地沙箱 |
| **提供程序执行** | 代码解释器、文件搜索、Web 搜索、托管 MCP 工具、图像生成、本机计算机使用、Bing Grounding、Azure AI 搜索、SharePoint、Microsoft Fabric、内存搜索、浏览器自动化 | 模型/云服务侧 |
| **配置包** | Microsoft Foundry 工具箱 | Foundry 项目内命名、带版本的托管工具配置包 |

这个划分决定了审批与安全责任：客户端执行的工具，你可以在调用前拦截；提供程序执行的工具，审批行为由提供程序决定。

## 工具审批：框架能力，但有边界

工具审批用于“在模型收到结果之前，通过人工循环决策限制工具调用”（F-045 的审批段）。它适用于**客户端本地调用工具**的提供程序；服务端托管工具遵循提供程序自己的审批行为。

用 Go 时，可以通过 `tool.ApprovalRequiredFunc` 标记工具，或使用实现 `tool.ApprovalRequiredTool` 的工具（例如本地 shell 工具）；审批请求与响应通过工具自动调用中间件流动（F-045 的 Go 说明）。

三条实践建议：

1. 高风险工具（写文件、发消息、执行 shell、访问生产数据库）一律走审批，不要依赖系统提示。
2. 审批规则要能“记住选择”，否则长任务会被反复打断；Harness 的 `ToolApprovalAgent` 就是为此设计的（F-041）。
3. 不要用审批替代参数校验。审批是“人是否同意”，校验是“参数是否合法”，两者不能互相替代。

## 工具调用是模型生成的

文档开篇就警告：工具调用与参数由模型生成，应用代码在执行副作用之前必须验证与授权；高风险工具应使用审批与最小权限（F-046）。

这句话的工程含义是：**工具函数的第一行应该是校验，而不是业务逻辑**。模型可能传错类型、传越界值、传注入内容；工具实现不能假设调用方是善意的。

## 代理即工具

MAF 支持把一个代理包装成另一个代理可调用的函数工具（F-047）。这适合“专家代理”模式：主代理负责路由与整合，专家代理各自带指令与工具。

设计时注意两点：

1. 工具描述就是主代理的“路由依据”，要写清何时该调用、输入输出是什么。
2. 专家代理的失败要转换成主代理能理解的错误信息，否则主代理会盲目重试。

## MCP：把外部系统变成工具

MCP（Model Context Protocol）在 MAF 中有两种形态（F-045）：

1. **托管 MCP 工具**：由提供程序运行时调用 MCP 服务器。
2. **本地 MCP 工具**：在本地或自定义主机上运行的 MCP 服务器。

Python 的 `Agent` 在 `async with` 或显式 `open()/close()` 中管理 MCP 连接；`close()` 会发布运行期间延迟连接的 MCP 工具（F-020）。这意味着：**忘记关闭代理，可能留下未释放的 MCP 连接**。

## Agent Skills：可移植的能力包

技能是指令、脚本与资源的可移植包，遵循开放规范并实现渐进式披露（F-048）。它解决的问题不是“再加一个工具”，而是“把一套领域工作流封装成可复用、可审计、可跨产品迁移的单元”。

适用场景（F-048）：

1. 封装领域专业知识（费用政策、法律流程、数据分析管道）。
2. 扩展代理能力而不改核心指令。
3. 把多步骤任务变成可重复、可审计的工作流。
4. 在不同“技能兼容”的产品间复用同一技能。

### 目录结构

```text
expense-report/
├── SKILL.md                  # 必需：frontmatter + 指令
├── scripts/
│   └── validate.py           # 可执行代码
├── references/
│   └── POLICY_FAQ.md         # 按需加载的参考文档
└── assets/
    └── expense-report-template.md
```

（F-049）

### SKILL.md 规范

```yaml
---
name: expense-report
description: File and validate employee expense reports according to company policy. Use when asked about expense submissions, reimbursement rules, or spending limits.
license: Apache-2.0
compatibility: Requires python3
metadata:
  author: contoso-finance
  version: "2.1"
---
```

字段约束（F-050）：

| 字段 | 必需 | 约束 |
|------|------|------|
| `name` | 是 | ≤64 字符；小写字母、数字、连字符；不得以连字符开头/结尾或连续；必须与父目录同名 |
| `description` | 是 | ≤1024 字符；说明做什么、何时用；含触发关键词 |
| `license` | 否 | 许可证名或指向捆绑许可证文件 |
| `compatibility` | 否 | ≤500 字符；环境要求 |
| `metadata` | 否 | 任意键值映射 |
| `allowed-tools` | 否 | 空格分隔的预批准工具列表；实验性 |

一个反直觉的点：`name` 必须与父目录同名，大小写与连字符都受限；`description` 超过 1024 字符或 YAML 无效会导致技能**加载失败**，而不是降级（F-050）。写技能时先把 frontmatter 校验跑通，再写正文。

### 四阶段渐进式披露

技能的价值在于“不占上下文”。官方用四阶段控制 token（F-051、F-052）：

| 阶段 | 机制 | 预算 |
|------|------|------|
| 宣告 | 技能名与描述注入系统提示 | 每技能约 100 tokens |
| 加载 | `load_skill` 取完整 `SKILL.md` | 建议 <5000 tokens |
| 读资源 | `read_skill_resource` 按需取参考/模板/资产 | 按需 |
| 跑脚本 | `run_skill_script` 执行捆绑脚本 | 按需 |

工具暴露规则：`load_skill` 始终可用；`read_skill_resource` 仅当至少一个技能有资源时暴露；`run_skill_script` 仅当至少一个技能有脚本时暴露（F-052）。

对长时运行的 Python 代理，可以用 `UnloadSkillsCompactionStrategy` 在相关工作完成后卸载技能说明与资源，避免上下文被“已完成的技能”长期占用（F-053）。

### 三种技能形态

技能不一定是文件。官方支持（F-054）：

1. **基于文件**：`SKILL.md` + 目录资源，适合跨产品复用。
2. **代码定义**：在代码里声明技能、动态资源与脚本。
3. **基于类**：用类组织技能逻辑，适合与现有代码库集成。

文件形态支持多个技能目录、自定义资源与脚本发现、脚本执行（F-054）。这让你可以把技能放在应用目录、用户目录或包内资源里。

### 技能与 Harness

Harness 的 `AgentSkillsProvider` 直接从文件系统发现并执行技能（F-040）。技能默认值因语言而异：.NET/Go 默认启用，Python 需提供程序或路径选择加入（F-039）。

### 技能不是“提示词模板”

一个常见误区是把技能当成“更长的系统提示”。技能的关键差异是：

1. **可发现**：代理先看到名称与描述，再决定是否加载。
2. **可分层**：正文、资源、脚本按需取，不一次性塞进上下文。
3. **可审计**：目录与脚本是文件，能进版本控制、能做代码审查。
4. **可移植**：同一技能可被不同代理产品使用。

## 选型建议

| 需求 | 选择 |
|------|------|
| 调一个内部 API | 函数工具 |
| 连一个外部系统的标准接口 | MCP（本地或托管） |
| 封装一套领域流程 + 脚本 + 参考文档 | Agent Skill |
| 让一个专家代理被主代理调用 | 代理即工具 |
| 需要沙箱执行代码 | 代码解释器 / CodeAct（见 [Build 2026 与迁移](09-build2026-migration.md)） |

## 已知边界

1. `allowed-tools` 是实验性字段，不同代理实现的支持度不同（F-050、F-055）。
2. 服务端托管工具的审批行为由提供程序决定，框架不能统一拦截（F-045）。
3. 技能的脚本执行权限由运行环境决定；技能本身不提供沙箱。
4. 本知识包不覆盖 MCP 协议本身的规范，只讲 MAF 的接入方式。
