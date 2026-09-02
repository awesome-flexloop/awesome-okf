---
type: Concept
title: 使用方式与最佳实践
description: The Agency 的四种使用方式（桌面应用/Claude Code 原生集成/参考定制/多工具双脚本流程）、与通用提示词方案的定位对比、Agent 选择与多 Agent 流水线编排、按需安装与 OpenCode 119 上限规避、激活提示词四要素与可度量交付。
tags: [agency-agents, usage, best-practices, installation, activation]
generated: { by: agent:learning-bundles-merge, at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: 2027-09-02
sources:
  - id: learning-agency-wiki
    resource: SpecWeave docs/knowledge/learning/03-agent-platforms-tools/agency-agents-wiki/（00-overview.md、06-usage-examples.md、09-best-practices.md）
    title: The Agency 完全指南（learning 侧合并来源）
---

# 使用方式与最佳实践

本篇覆盖 The Agency 的日常使用与落地实践。角色文件格式见 [Agent Markdown 模板规范](agent-md-template.md)，部门体系见 [Persona 部门分类体系](persona-division-structure.md)，多工具适配机制见[工具集成适配体系](integration-adapters.md)，编排框架见 [NEXUS 多 Agent 编排](nexus-orchestration.md)。

## 定位对比：为什么不是通用提示词

| 对比维度 | 通用 AI 提示词 | 提示词库 | AI 工具（黑盒） | The Agency |
|---------|--------------|--------------------------|---------------|-----------|
| **定位** | 一句「扮演开发者」的临时指令 | 零散的提示词收藏 | 封装好的傻瓜化工具 | 完整的 Agent 角色系统 |
| **专业化** | 泛泛而谈 | 单点可用 | 固定功能 | 深度专精 + 人格 + 流程 |
| **可交付** | 无明确产出物 | 无 | 固定输出 | 真实代码、流程、可度量结果 |
| **可定制** | 可改但无体系 | 可改但零散 | 黑盒不可改 | 透明、可 Fork、可性格化 |
| **多工具** | 依赖单一助手 | 依赖单一助手 | 绑定单一产品 | 一套角色适配 16 种工具 |
| **团队协作** | 无 | 无 | 无 | 多部门 Agent 协同 |

The Agency 的五个核心设计特性：**人格驱动**（每个 Agent 有独特的声音、沟通风格与做事方式）、**交付物导向**（强调真实产出而非空泛建议，直接给出可运行代码与模板）、**可度量成果**（每个 Agent 定义自己的成功指标，如「推理延迟 < 100ms」「WCAG AA 对比度 4.5:1」）、**多工具兼容**（一次定义、处处可用）、**可自定义**（纯文本 Markdown，MIT 许可）。

## 四种使用方式

| 方式 | 上手难度 | 是否需要命令行 | 适用人群 | 核心特点 |
|------|---------|---------------|---------|---------|
| **① 桌面应用** | 低 | 不需要 | 所有用户，尤其非技术用户 | 图形界面浏览全部 Agent，一键安装，自动更新 |
| **② Claude Code 集成** | 中 | 需要 | 已在用 Claude Code 的开发者 | 原生 `.md` 格式，无需转换，直接激活 |
| **③ 作为参考直接使用** | 低 | 可选 | 想自己定制 Agent 的进阶用户 | 浏览、复制、改编现成的 Agent 文件 |
| **④ 与其他工具配合** | 高 | 需要 | 使用 Cursor/Copilot/Codex 等多工具的用户 | `convert.sh` + `install.sh` 双脚本流程 |

### 方式一：桌面应用

官方原生桌面应用（macOS/Linux/Windows）解除对克隆仓库、运行脚本的依赖——打开应用即可浏览完整 Agent 名册，鼠标点击安装到 Claude Code、Cursor、Codex、Gemini 等工具，支持自动更新。macOS 可用 Homebrew 安装；桌面应用本质上是把仓库里的 Agent 文件复制到各工具目标目录，与命令行脚本安装的完全相同。桌面应用详见姊妹束 [agency-agents-app](../../agency-agents-app/index.md)。

### 方式二：Claude Code 原生集成

The Agency 最初为 Claude Code 打造，Agent 文件采用 Claude Code 原生支持的 Markdown + YAML frontmatter 格式，无需转换：

```bash
# 一键安装全部 Agent
./scripts/install.sh --tool claude-code

# 或手动复制某个部门
cp engineering/*.md ~/.claude/agents/
```

安装后在会话中通过名称引用激活：

```text
Hey Claude, activate Frontend Developer mode and help me build a React component
Use the Reality Checker agent to verify this feature is production-ready.
```

Claude Code 会把 `~/.claude/agents/` 下的每个 `.md` 文件识别为一个可用的 sub-agent，会话中自然语言点名即可让它「上线」。

### 方式三：作为参考直接使用

每个 Agent 文件都是结构完整的「专家档案」（身份与性格特质、核心使命与工作流、带代码示例的技术交付物、成功指标与沟通风格）。可直接浏览各部门目录，把需要的部分复制、改编到自己的项目或提示词体系——适合不想深度绑定某个工具、想把「专家方法论」内化到自己体系中的用户。

### 方式四：多工具双脚本流程

```bash
# 第一步：为所有支持的工具生成集成文件
./scripts/convert.sh

# 第二步：交互式安装（自动检测已安装的工具）
./scripts/install.sh

# 或直接指定目标工具
./scripts/install.sh --tool gemini-cli
```

转换与安装机制的完整说明见[工具集成适配体系](integration-adapters.md)。

## Agent 选择最佳实践

The Agency 的核心价值在于**专精**——不要用一个通用 Agent 处理所有事。选择时先问三个问题：①任务属于哪个领域？→ 对齐到对应部门；②需要什么深度的专长？→ 从部门内挑选最贴合的 Agent；③交付物是什么？→ 看 Agent 的「Technical Deliverables」是否对应你要的产出。

| 任务类型 | 推荐部门 | 推荐 Agent 示例 |
|---------|---------|----------------|
| 搭建 Web 应用 | Engineering | Frontend Developer、Backend Architect |
| 营销增长 | Marketing | Growth Hacker、SEO Specialist |
| 网络安全评估 | Security | Security Architect、Penetration Tester |
| 产品质量把关 | Testing | Evidence Collector、Reality Checker |
| 商业规划 | Product / Finance | Product Manager、Financial Analyst |
| 客服与运营 | Support | Support Responder、Analytics Reporter |

### 多 Agent 流水线编排

现实任务往往横跨多个领域，最佳做法是把任务拆成多个环节、每环节交给最擅长的 Agent。例如一次「产品发布」：

1. **Product Manager** — 定义需求与 PRD
2. **UI Designer / Frontend Developer** — 设计与实现界面
3. **Backend Architect** — 设计后端 API 与数据
4. **Testing（Evidence Collector）** — 收集证据、验证质量
5. **Marketing（Growth Hacker）** — 规划发售与增长
6. **Reality Checker** — 最终发布前的质量门

这种「多 Agent 接力」模式在官方 Use Cases 中反复出现（Building a Startup MVP、Enterprise Feature Development 等，都是 5-8 个 Agent 串成端到端流水线）。更系统的编排框架见 [NEXUS 多 Agent 编排](nexus-orchestration.md)。

## 安装最佳实践

### 按需安装，避免过度安装

强烈建议按需安装而非一次性装全部 270+ Agent，原因：①Agent 定义文件较长，装太多会占用宝贵的上下文；②装太多会让 AI 助手「选择困难」，降低激活精度；③部分工具有数量上限。

```bash
# 只装业务需要的部门
./scripts/install.sh --tool claude-code --division engineering,security

# 或只装几个具体 Agent
./scripts/install.sh --tool cursor --agent frontend-developer,ui-designer

# 查看有哪些部门可选
./scripts/install.sh --list teams
```

### OpenCode 的 119 上限规避

OpenCode 存在上游 bug，运行时只注册约 119 个 Agent。规避要点：使用 `--division`/`--agent` 安装子集确保不超 119；留意安装器警告；更换部门时先清理旧子集再装新的，避免新旧叠加超限。

### 用 dry-run 预览

`--dry-run` 只预览输出、不实际写入，适合正式安装前检查效果：

```bash
./scripts/install.sh --tool opencode --division engineering --dry-run
```

凡是涉及批量安装到多个工具、或不确定参数效果时，先跑一次 `--dry-run`，确认无误后再正式安装。

## 激活提示词四要素

激活 Agent 时，提示词质量直接决定输出质量。有效的激活提示词包含：

1. **引用 Agent**：明确点名要用的 Agent（自然语言或 `@agent` 语法）
2. **给出目标**：说明想要的最终结果
3. **提供上下文**：给出必要的背景、文件、约束
4. **定义交付**：说明可度量的交付物

反例（模糊）：「帮我做个网站。」

正例（清晰）：

```text
Use the Frontend Developer agent to build a landing page for my SaaS product.
Target: a responsive single-page React app. Context: use the brand colors in
design/brand.md. Deliverable: a working React component with a Core Web Vitals
score >= 90 and a short summary of what was built.
```

## 让 Agent 交付可度量成果

The Agency 的 Agent 天生「交付物导向」，但使用者要主动把成果量化，形成可验收标准：

- **明确指标**：如「性能分 ≥ 90」「测试通过率 100%」「覆盖 3 个平台」
- **要求证据**：Testing 部门的 Evidence Collector 默认找 3-5 个问题并要求视觉证明
- **设定质量门**：用 Reality Checker 在最终交付前做「生产就绪」认证
- **跟踪结果**：让 Analytics Reporter 把成果整理成可汇报的仪表盘/摘要

## 相关概念

- [Agent Markdown 模板规范](agent-md-template.md)
- [Persona 部门分类体系](persona-division-structure.md)
- [NEXUS 多 Agent 编排框架](nexus-orchestration.md)
- [工具集成适配体系](integration-adapters.md)
- [创建自定义 Persona 示例](../examples/create-custom-persona.md)
