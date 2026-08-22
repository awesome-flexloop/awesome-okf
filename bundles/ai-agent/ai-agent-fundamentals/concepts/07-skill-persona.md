---
type: Concept
title: 技能与 Persona 系统
description: 从 SKILL.md 声明式标准到 280+ Persona 角色库——Agent 能力扩展与人格定义的统一范式
tags: [ai-agent, skill, persona, skill.md, agent-persona, roleplay, knowledge-compilation]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T01:45:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-register
    resource: /references/ai-agent-sources.md
  - id: anthropics
    resource: /references/ai-agent-sources.md#anthropics
  - id: agency
    resource: /references/ai-agent-sources.md#agency-agents
  - id: book2skill
    resource: /references/ai-agent-sources.md#book-to-skill
  - id: adhd
    resource: /references/ai-agent-sources.md#i-have-adhd
  - id: zleap
    resource: /references/ai-agent-sources.md#zleap-agent
  - id: secondme
    resource: /references/ai-agent-sources.md#second-me
---

# 技能与 Persona 系统

技能（Skill）和 Persona 是 Agent 能力扩展的轻量级范式。与传统 SDK 集成不同，Skill 通常以**声明式 Markdown**（SKILL.md）为入口，包含指令、辅助脚本和资源文件，无需编写代码即可扩展 Agent 能力。Persona 则定义 Agent 的角色、风格和专业领域。本概念分析四种技能/Persona 实现：anthropics 参考实现、agency-agents 角色库、book-to-skill 知识编译、i-have-adhd 风格技能。

## SKILL.md 标准

### 开放标准

SKILL.md 是 [Agent Skills 开放标准](https://agentskills.io)定义的技能包格式。一个技能是一个**自包含文件夹**，以 `SKILL.md` 为入口文件：

```
my-skill/
├── SKILL.md          # 入口：YAML frontmatter + Markdown 指令
├── helpers/          # 辅助脚本（Python/Shell等）
├── templates/        # 模板文件
└── assets/           # 其他资源
```

### SKILL.md 基本结构

```markdown
---
name: my-skill-name
description: 一句话描述这个技能做什么、何时触发
---

# 技能名称

## 何时使用
描述触发条件：什么情况下应该加载这个技能

## 核心指令
Agent 加载此技能后应遵循的步骤和规则...

## 参考资料
- [相关文件](./helpers/script.py)
```

**核心设计原则**：
- **声明式**：技能通过自然语言指令定义行为，不需要代码注册
- **自包含**：技能文件夹包含所有需要的资源，不依赖外部状态
- **按需加载**：Agent 只在需要时加载相关技能，不占用常驻上下文
- **跨宿主兼容**：同一技能可以在 Claude Code、Cursor、Copilot CLI 等不同宿主上运行

## anthropics/skills：官方参考实现

Anthropic 官方发布的 `anthropics/skills` 仓库是 SKILL.md 标准的参考实现，展示了技能系统的多种用法。

### 技能类型分类

| 技能 | 类型 | 特点 |
|------|------|------|
| `algorithmic-art` | 生成类 | p5.js 算法艺术生成，含随机种子控制 |
| `canvas-design` | 设计类 | Canvas 视觉设计，含字体库 |
| `claude-api` | 文档类 | 多语言 API 文档（Python/TS/Go/Java/PHP/C#/Ruby/cURL） |
| `docx`/`pdf`/`pptx` | 文档类 | 二进制文档处理，含 OOXML XSD schema 验证 |
| `frontend-design` | 设计类 | 前端 UI 设计指导 |
| `mcp-builder` | 工具类 | MCP 服务器构建指导 |
| `skill-creator` | 元技能 | 创建新技能的技能（含评估脚本） |
| `doc-coauthoring` | 协作类 | 文档协作写作工作流 |
| `internal-comms` | 写作类 | 企业内部沟通写作 |

### 文档技能的工程化

`docx`、`pdf`、`pptx` 三个文档技能展示了"SKILL.md + Python 脚本 + Schema 验证"的工程化模式：

```
skills/docx/
├── SKILL.md              # 指令：如何创建/编辑 DOCX 文件
├── scripts/
│   ├── create_docx.py    # Python 生成脚本
│   └── validate_docx.py  # OOXML schema 验证
└── schemas/
    └── *.xsd             # OOXML XSD schema 文件
```

这种模式让 Agent 不仅"知道怎么做"（SKILL.md 指令），还"有工具做"（Python 脚本），并且"能验证做对了"（schema 验证）。

## agency-agents：280+ Persona 角色库

agency-agents 不是一个框架，而是一个精心制作的 **Agent Persona Markdown 文件集合**，展示了如何用纯 Markdown 定义专业角色。

### Persona 文件格式

每个 persona 是一个带 YAML frontmatter 的 Markdown 文件：

```markdown
---
name: Senior Frontend Engineer
description: Specializes in React, TypeScript, accessibility, and performance optimization
color: "#61DAFB"
emoji: "⚛️"
vibe: "Precise, pragmatic, accessibility-first"
---

# Senior Frontend Engineer

## Identity & Memory
You are a senior frontend engineer with 10+ years of experience...

## Core Mission
Build accessible, performant, and maintainable web applications...

## Critical Rules
- Always prioritize accessibility (WCAG 2.1 AA)
- Mobile-first responsive design
- Performance budget: LCP < 2.5s

## Core Capabilities
1. React/Next.js architecture
2. TypeScript type system mastery
3. CSS/layout systems
4. Performance optimization
5. Accessibility auditing

## Workflow Process
1. Understand requirements
2. Propose component structure
3. Implement with tests
4. Audit accessibility and performance

## Deliverables
- Production-ready code
- Accessibility audit report
- Performance metrics
```

### Persona 组织

280+ persona 按 18 个 division（部门）组织：

| Division | 数量 | 代表角色 |
|----------|------|---------|
| engineering | ~50 | Frontend/Backend/AI/DevOps/Security Engineer |
| marketing | ~40 | 抖音/小红书/B站/微信/百度营销专家（含中国市场） |
| specialized | ~60 | 多代理编排、MCP构建、身份信任图谱 |
| game-development | ~20 | Unity/Godot/Unreal/Roblox/Blender 专家 |
| design | 10 | UI/UX/品牌/视觉设计 |
| security | 12 | 渗透测试/安全审计/合规 |
| (其他12个division) | ~90 | 学术/财务/医疗/法律/销售/项目管理等 |

### 策略编排层

agency-agents 还提供了 `strategy/` 目录，包含多 Agent 协作的 playbook 和 runbook：

- **Playbooks**：6 阶段协作流程
  - `discovery` → `strategy` → `foundation` → `build` → `hardening` → `launch` → `operate`
- **Runbooks**：预定义场景
  - 企业功能开发、事件响应、营销活动、创业 MVP
- **Handoff Templates**：Agent 之间的交接模板
- **Agent Activation Prompts**：激活提示词

### 多宿主适配

agency-agents 提供 `scripts/convert.sh` 和 `scripts/install.sh`，可以将 persona 转换并安装到不同宿主：

| 宿主 | 安装位置 | 格式 |
|------|---------|------|
| Claude Code | `~/.claude/agents/*.md` | Markdown |
| Cursor | `.cursor/rules/*.mdc` | Cursor Rules |
| Codex | `~/.codex/agents/*.toml` | TOML |
| Gemini CLI | 配置目录 | Gemini 格式 |
| GitHub Copilot | 配置目录 | Copilot 格式 |
| Osaurus | `SKILL.md` 格式 | 标准 Skill |

## book-to-skill：编译时知识编译

book-to-skill 项目提供了**将书籍/文档自动编译为 Skill** 的工具链，代表了"知识即技能"的范式。

### 四层产出（前文详述）

| 文件 | Token 预算 | 内容 |
|------|-----------|------|
| `SKILL.md` | ~4,000 | 核心心智模型 + 章节/主题索引 |
| `chapters/chNN-*.md` | 800–3,000 | 每章一个文件，按需加载 |
| `glossary.md` | ~1,500 | 术语表 |
| `patterns.md` | ~2,000 | 技术/设计模式总结 |
| `cheatsheet.md` | ~1,200 | 决策规则速查 |

### 四种操作模式

1. **全量转换**：从零开始，完整提取+分析+生成
2. **仅分析**：只做分析不生成（调试用）
3. **从已有分析生成**：复用已有分析结果
4. **Fold-in（合并更新）**：向已有 Skill 合并新内容

## i-have-adhd：认知适配风格技能

i-have-adhd 展示了一种特殊的技能类型——**风格/人格技能**，它不添加新能力，而是系统性改变 Agent 的输出风格。

### 基于认知科学的规则设计

i-have-adhd 的 10 条规则基于 5 条 ADHD 认知科学事实：

| 认知事实 | 对应规则 |
|----------|---------|
| 工作记忆容量小 | 不要求读者"记住 X"，每轮重申当前状态 |
| 知道≠做到 | 缩小知道到行动的摩擦，第一步必须明显可做 |
| 启动最难 | 以行动开头（非计划/上下文），给出具体微小的下一步 |
| 时间估计模糊 | 给出具体分钟数 |
| 多巴胺稀缺 | 让完成成果可见，列表不超过 5 项 |

### 持久化机制

i-have-adhd 使用 `disable-model-invocation: true` 标记为纯风格技能（不调用工具），通过 SessionStart Hook 实现"常驻模式"：

```json
// hooks/hooks.json
{
  "hooks": [{
    "type": "SessionStart",
    "command": "always-on.sh"
  }]
}
```

`always-on.sh` 检查 `~/.claude/.i-have-adhd-always` 标记文件，存在则自动启用技能。

## Zleap-Agent：Skill 信任与风险审计

Zleap-Agent 的 Skill 系统在 SKILL.md 基础上增加了**信任和安全**维度：

```typescript
interface Skill {
    id: string;
    name: string;
    entryPath: string;          // SKILL.md 路径
    toolIds: string[];          // 技能需要的工具列表
    tokenBudget: number;        // Token 预算声明
    trustLevel: TrustLevel;     // 信任级别
    riskAudit: RiskAudit;       // 风险审计结果
    sensitivityAudit: SensitivityLevel;  // 敏感度审计
    invocationPolicy: InvocationPolicy;  // 调用策略
}

enum InvocationPolicy {
    implicit = "implicit",         // Agent 自动判断何时使用
    explicit_only = "explicit_only", // 必须用户明确调用
    disabled = "disabled"          // 禁用
}
```

### Skill 调用策略

| 策略 | 行为 | 适用场景 |
|------|------|---------|
| `implicit` | Agent 自行判断何时加载 | 通用辅助技能 |
| `explicit_only` | 用户必须明确要求 | 高风险操作（如发送邮件、部署） |
| `disabled` | 不加载 | 安全禁用 |

## Second-Me：Roleplay 人格多态

Second-Me 的 L2 层通过 LoRA 微调实现了最深层的 Persona 内化——不是通过 prompt 指令，而是通过模型权重。同一个 Second Me 可以在不同场景下切换不同人格（Roleplay），每个角色有对应的 prompt 策略和行为模式。

## 技能系统设计模式总结

| 模式 | 实现 | 扩展深度 | 灵活性 | 门槛 |
|------|------|---------|--------|------|
| **声明式 SKILL.md** | anthropics, i-have-adhd | 指令级 | 高（自然语言） | 低（写 Markdown） |
| **Persona 集合** | agency-agents | 角色定义 | 中（固定模板） | 低（写 Markdown） |
| **知识编译** | book-to-skill | 内容蒸馏+结构化 | 中（生成式） | 中（运行编译器） |
| **运行时 Skill** | Zleap-Agent | 带权限和预算的可执行单元 | 高（策略控制） | 中（注册+配置） |
| **模型内化** | Second-Me L2 | 权重级 | 低（需重训练） | 高（LoRA训练） |

## 相关概念

- [上下文管理](06-context-management.md) — 技能按需加载是上下文管理的重要策略
- [记忆架构](03-memory-architecture.md) — Persona 与记忆共同塑造 Agent 身份
- [插件化架构模式](08-plugin-architecture.md) — 运行时 Skill 注册与插件系统的关系
- [多智能体编排](04-multi-agent.md) — agency-agents 的多 persona 编排方法
