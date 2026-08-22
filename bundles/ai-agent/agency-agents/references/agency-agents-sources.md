---
type: Reference
title: The Agency (agency-agents) 源码信源登记
description: AI Agent Persona 角色集合库目录结构、部门体系、Agent 文件格式规范、脚本工具与多工具集成信源清单
tags: [agency-agents, persona, agent, prompt, markdown, source, reference]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T23:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: agency-agents-github
    resource: https://github.com/msitarzewski/agency-agents
    title: The Agency GitHub 仓库
---

# The Agency (agency-agents) 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | The Agency |
| 许可证 | MIT |
| 作者 | Michael Sitarzewski |
| 描述 | AI Agent Persona（AI 专家角色）集合库，每个 Agent 是一个专门领域的专家角色定义，包含人格、工作流、交付物和成功指标 |
| 定位 | Agent 文件为非可执行的 Markdown 提示词定义，不包含可执行代码 |
| 配套应用 | Agency Agents App（原生桌面应用，支持 macOS/Linux/Windows） |
| 源码位置 | `d:\spaces\SpecWeave\external\libs\models\ai\agency-agents\` |
| Agent 总数 | 约 270 个 |

## 目录结构

```
agency-agents/
├── README.md                    # 项目说明
├── LICENSE                      # MIT 许可证
├── CONTRIBUTING.md              # 贡献指南（英文）
├── CONTRIBUTING_zh-CN.md        # 贡献指南（中文）
├── SECURITY.md                  # 安全策略
├── divisions.json               # 部门定义单一真相源
├── tools.json                   # 支持的工具集成定义
├── .gitignore
├── .gitattributes               # 强制 LF 行尾
├── .github/workflows/           # CI 工作流（4个）
├── academic/                    # 学术部门（6 agents）
├── design/                      # 设计部门（10 agents）
├── engineering/                 # 工程部门（58 agents）
├── finance/                     # 金融部门（5 agents）
├── game-development/            # 游戏开发部门（21 agents）
│   ├── blender/                 # Blender 引擎子目录
│   ├── godot/                   # Godot 引擎子目录
│   ├── roblox-studio/           # Roblox Studio 子目录
│   ├── unity/                   # Unity 引擎子目录
│   └── unreal-engine/           # Unreal Engine 子目录
├── gis/                         # GIS 部门（13 agents）
├── healthcare/                  # 医疗部门（3 agents）
├── marketing/                   # 营销部门（36 agents）
├── paid-media/                  # 付费媒体部门（7 agents）
├── product/                     # 产品部门（5 agents）
├── project-management/          # 项目管理部门（7 agents）
├── sales/                       # 销售部门（9 agents）
├── security/                    # 安全部门（12 agents）
├── spatial-computing/           # 空间计算部门（6 agents）
├── specialized/                 # 专项部门（57 agents）
├── support/                     # 支持部门（6 agents）
├── testing/                     # 测试部门（9 agents）
├── examples/                    # 多 Agent 协作示例
├── scripts/                     # 安装/转换/检查脚本
│   ├── i18n/                    # 中文本地化支持
│   ├── lib.sh                   # 共享 Bash 工具库
│   ├── install.sh               # 交互式安装向导
│   ├── convert.sh               # 格式转换（输出到 integrations/）
│   ├── lint-agents.sh           # Agent Markdown Lint
│   ├── check-divisions.sh       # 部门一致性校验
│   ├── check-tools.sh           # 工具定义一致性校验
│   ├── check-runbooks.sh        # Runbook 一致性校验
│   ├── check-agent-originality.sh # 防重复检查
│   ├── build-hermes-plugin.py   # Hermes 插件构建
│   └── check-hermes-plugin.py   # Hermes 插件验证
├── integrations/                # 各工具转换输出目录（生成文件，不提交 Git）
└── strategy/                    # NEXUS 编排框架手册
    ├── nexus-strategy.md        # NEXUS 完整操作条令
    ├── QUICKSTART.md            # 5分钟快速上手
    ├── EXECUTIVE-BRIEF.md       # 高管摘要
    ├── runbooks.json            # 机器可读 Runbook 清单
    ├── coordination/            # Agent 激活提示词、交接模板
    ├── playbooks/               # 7 阶段 Playbook
    └── runbooks/                # 4 场景 Runbook Markdown
```

## 部门（Division）体系

共 17 个部门，在 `divisions.json` 中配置 `label`（显示名）、`icon`（Lucide 图标名 PascalCase）、`color`（品牌色 hex）：

| 目录名 | Agent 数量 | 说明 |
|--------|-----------|------|
| academic | 6 | 学术 |
| design | 10 | 设计 |
| engineering | 58 | 工程（最大的纯代码部门） |
| finance | 5 | 金融 |
| game-development | 21 | 游戏开发（唯一含引擎子目录的部门） |
| gis | 13 | 地理信息系统 |
| healthcare | 3 | 医疗 |
| marketing | 36 | 营销（第二大部门） |
| paid-media | 7 | 付费媒体 |
| product | 5 | 产品 |
| project-management | 7 | 项目管理 |
| sales | 9 | 销售 |
| security | 12 | 安全 |
| spatial-computing | 6 | 空间计算 |
| specialized | 57 | 专项（最大部门） |
| support | 6 | 客户支持 |
| testing | 9 | 测试 |
| **总计** | **~270** | |

## 关键文件清单

### 配置文件

| 文件 | 内容 |
|------|------|
| `divisions.json` | 17 个部门的 label/icon/color 定义，单一真相源 |
| `tools.json` | 16 种 AI 工具集成配置（id/label/format/installKind/dest 等） |
| `.gitattributes` | 强制 `*.md text eol=lf`，禁止 CRLF |
| `.gitignore` | 排除 `integrations/*` 生成文件（仅保留 README.md） |

### Agent 模板与示例

| 文件 | 内容 |
|------|------|
| `engineering/engineering-frontend-developer.md` | 标准 Agent 范例：完整 emoji 标题、代码示例、Deliverable Template |
| `marketing/marketing-seo-specialist.md` | 非 emoji 标题变体示例，含非标准 `tools` 字段 |
| `marketing/marketing-carousel-growth-engine.md` | 含 `services` 字段（外部服务依赖声明）的 Agent 范例 |
| `specialized/specialized-mcp-builder.md` | specialized 前缀命名范例 |

### 脚本工具

| 文件 | 内容 |
|------|------|
| `scripts/lib.sh` | 共享 Bash 库：get_field()、get_body()、slugify()、agent_slug()、is_agent_file()、TUI 原语 |
| `scripts/install.sh` | 交互式安装向导，支持安装到各种 AI 工具配置目录 |
| `scripts/convert.sh` | Agent .md → 各工具特定格式转换，输出到 integrations/ |
| `scripts/lint-agents.sh` | Lint 检查：frontmatter 必需字段、章节分类(soul/agents)、CRLF、内容长度 |
| `scripts/check-divisions.sh` | 校验 divisions.json 与实际目录、脚本、CI 工作流一致性 |
| `scripts/check-tools.sh` | 校验 tools.json 与 install.sh、convert.sh 一致性 |
| `scripts/check-runbooks.sh` | 校验 runbooks.json 中引用的 Agent slug 存在性 |
| `scripts/check-agent-originality.sh` | 检查新增 Agent 与现有 Agent 相似度（防重复） |
| `scripts/build-hermes-plugin.py` | 构建 Hermes 懒加载路由插件（plugin.yaml + __init__.py + data/agents.json） |
| `scripts/check-hermes-plugin.py` | 验证 Hermes 插件工具契约 |
| `scripts/i18n/agent-names-zh.json` | 130+ 条英文名→中文翻译映射 |
| `scripts/i18n/localize-agents-zh.ps1` | PowerShell 脚本：替换已安装 Agent 的 name/description 为中文 |

### CI/CD 工作流

| 文件 | 内容 |
|------|------|
| `.github/workflows/lint-agents.yml` | Lint Agent 文件，PR 时检查变更文件 |
| `.github/workflows/check-divisions.yml` | 检查部门一致性 |
| `.github/workflows/check-runbooks.yml` | 检查 Runbook 一致性 |
| `.github/workflows/check-tools.yml` | 检查工具定义一致性 |

### 示例与编排

| 文件 | 内容 |
|------|------|
| `examples/README.md` | 示例索引 |
| `examples/nexus-spatial-discovery.md` | 8 个 Agent 并行空间计算产品发现 |
| `examples/workflow-startup-mvp.md` | 7 Agent 协作 SaaS MVP 4 周工作流 |
| `examples/workflow-landing-page.md` | 落地页构建工作流 |
| `examples/workflow-book-chapter.md` | 书籍章节写作工作流 |
| `examples/workflow-with-memory.md` | 基于 MCP Memory 的持久化记忆工作流 |
| `strategy/nexus-strategy.md` | NEXUS 7 阶段流水线定义 |
| `strategy/QUICKSTART.md` | NEXUS 3 种部署模式（Full/Sprint/Micro） |
| `strategy/runbooks.json` | 4 个机器可读场景 Runbook |

### 集成配置

| 文件 | 内容 |
|------|------|
| `integrations/mcp-memory/README.md` | MCP 记忆集成模式和示例 |

## Agent Markdown 文件格式规范

### YAML Frontmatter

**必需字段**（缺少导致 CI 失败）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | Agent 显示名称 |
| `description` | string | Agent 功能描述 |
| `color` | string | 品牌色（颜色名或 hex 码，如 `cyan`、`"#dc2626"`） |

**可选字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `emoji` | string | 角色表情符号 |
| `vibe` | string | 一句话人格钩子 |
| `services` | array | 外部服务依赖（name/url/tier: free/freemium/paid） |
| `tools` | array | 所需工具列表（非标准扩展字段） |

Frontmatter 示例：
```yaml
---
name: Frontend Developer
description: Expert frontend developer specializing in modern web technologies...
color: cyan
emoji: 🖥️
vibe: Builds responsive, accessible web apps with pixel-perfect precision.
---
```

### 正文标准章节

| 章节 | 语义组 | 说明 |
|------|--------|------|
| `# {Agent Name}` | — | 标题 |
| `## 🧠 Your Identity & Memory` | Persona | 角色、人格、记忆、经验 |
| `## 🎯 Your Core Mission` | Operations | 核心使命与职责 |
| `## 🚨 Critical Rules You Must Follow` | Persona | 关键规则约束 |
| `## 📋 Your Technical Deliverables` | Operations | 技术交付物与代码示例 |
| `## 🔄 Your Workflow Process` | Operations | 分步工作流程 |
| `## 💭 Your Communication Style` | Persona | 沟通风格与语气 |
| `## 🔄 Learning & Memory` | Persona | 学习记忆模式 |
| `## 🎯 Your Success Metrics` | Operations | 可量化成功指标 |
| `## 🚀 Advanced Capabilities` | Operations | 高级能力 |

章节分类规则（lint-agents.sh）：
- **soul 组**（映射 OpenClaw SOUL.md）：含 identity、learning.*memory、communication、style、critical.rule 关键词的标题
- **agents 组**（映射 OpenClaw AGENTS.md）：其余标题
- 两组至少各需一个，否则产生 WARN

## 工具集成体系

项目支持 **16 种** AI 编码工具/平台：

| 工具 | installKind | format | scope |
|------|-------------|--------|-------|
| Claude Code | per-agent | identity（原生 Markdown） | user |
| Codex | per-agent | codex-toml | user |
| Gemini CLI | per-agent | gemini-md | user |
| GitHub Copilot | per-agent | identity（原生 Markdown） | user/project |
| Qwen | per-agent | qwen-md | user |
| Cursor | per-agent | cursor-mdc | project |
| opencode | per-agent | opencode-md | user |
| Osaurus | per-agent | — | user |
| Aider | roster | aider-conventions | project |
| Antigravity | per-agent | — | user |
| Kimi | per-agent | kimi-agent | user |
| OpenClaw | per-agent | openclaw-workspace | user |
| Windsurf | roster | windsurf-rules | project |
| Hermes | plugin | — | — |
| Vibe (Mistral) | per-agent | — | user |
| ZCode | per-agent | zcode-md | user |

三种安装机制：
- **per-agent**：每个 Agent 一个独立文件
- **roster**：所有 Agent 合并为一个文件（如 Aider 的 CONVENTIONS.md）
- **plugin**：CLI 专用构建产物，app 不可安装

## NEXUS 编排框架

**NEXUS**（Network of EXperts, Unified in Strategy）是多 Agent 编排框架：

- **3 种部署模式**：
  - NEXUS-Full：全量 Agent，12-24 周
  - NEXUS-Sprint：15-25 Agent，2-6 周
  - NEXUS-Micro：5-10 Agent，1-5 天

- **7 阶段流水线**（含质量门控）：
  1. Phase 0 Discovery
  2. Phase 1 Strategy
  3. Phase 2 Foundation
  4. Phase 3 Build
  5. Phase 4 Hardening
  6. Phase 5 Launch
  7. Phase 6 Operate

- **4 个场景 Runbook**：Startup MVP、Enterprise Feature、Marketing Campaign、Incident Response

## 核心函数/工具索引

| 函数/工具 | 文件 | 说明 |
|-----------|------|------|
| `get_field()` | `scripts/lib.sh` | 从 frontmatter 提取字段值 |
| `get_body()` | `scripts/lib.sh` | 提取 Markdown 正文（去 frontmatter） |
| `slugify()` | `scripts/lib.sh` | 名称转 kebab-case slug |
| `agent_slug()` | `scripts/lib.sh` | 从文件路径提取 Agent slug |
| `is_agent_file()` | `scripts/lib.sh` | 判断是否为有效 Agent 文件（首行为 `---`） |
| `validate_skill()` (概念) | `scripts/lint-agents.sh` | Lint 校验流程：frontmatter→字段→章节→CRLF |

## 设计原则

1. **强人格**（Strong Personality）：避免泛化的 "helpful assistant"
2. **清晰交付物**（Clear Deliverables）：包含可运行代码示例
3. **成功指标**（Success Metrics）：可量化
4. **经过验证的工作流**（Proven Workflows）：非理论方法
5. **学习记忆**（Learning Memory）：跨会话记忆模式

## 安全约束

- 禁止在 Agent Markdown 文件中存储 API 密钥、令牌或凭证
- 禁止在 Agent 文件中添加可执行代码
- 要求 LF 行尾（`.gitattributes` 强制）
