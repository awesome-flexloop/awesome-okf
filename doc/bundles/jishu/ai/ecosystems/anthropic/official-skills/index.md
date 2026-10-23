---
okf_version: "0.2"
type: index
title: "Anthropic 官方 Skills 库 Wiki"
description: "Anthropic官方Skills库中文文档——19个官方Skills逐个用途/结构/编写规范/可复用模式剖析、SKILL.md格式规范、skill-creator元技能、claude-api多语言参考、实测事实登记表与社区视角勘误。"
tags: [skills, claude-code, skill-creator, claude-api, docx, pdf, pptx, xlsx, frontend-design, mcp, authoring]
sources:
  - id: anthropic-skills-local
    resource: "external/libs/anthropics/skills"
    title: "Anthropic Skills 参考实现仓库（本地镜像）"
generated: { by: "process:source-code-to-okf-wiki R→I→E→V", at: "2026-10-24" }
status: stable
stale_after: 2027-04-24
---

# Anthropic 官方 Skills 库 Wiki

**Skills（技能包）** 是 Claude Code 和 Claude Agent 生态中的可复用能力包，通过标准化的 `SKILL.md` 文件封装特定领域的专业知识、工作流程和工具集。Skills 由 AI 代理根据用户请求语义**自动触发**，无需用户显式调用，就能在合适的场景下注入专业能力。

Anthropic 官方提供了 **19 个开箱即用的 Skills**，覆盖 API 开发、文档处理、设计创意、沟通写作四大类场景。本 bundle 是这些官方 Skills 的**逐个剖析 + 编写规范提炼 + 实测事实底账**。

## 源码目录全景

```
external/libs/anthropics/skills/          # 482 个文件，72 个 .py
├── README.md                    # 项目说明 + 安装方式 + 免责声明
├── THIRD_PARTY_NOTICES.md       # 第三方声明
├── .claude-plugin/
│   └── marketplace.json         # 5 个 plugin 分组，覆盖全部 19 个 skill
├── spec/
│   └── agent-skills-spec.md     # 3 行指针 → agentskills.io/specification
├── template/
│   └── SKILL.md                 # 最小 Skill 模板（name + description）
└── skills/                      # 19 个 Skill，SKILL.md 合计约 4000 行
```

| 指标 | 数值 | 事实编号 |
|------|------|---------|
| Skill 数量 | **19** | F-007 |
| SKILL.md 总行数 | 约 4000 行（32 ~ 616 行） | F-009 |
| 目录文件总数 | 482 | F-008 |
| Python 脚本数 | 72 | F-008 |
| Plugin 分组数 | 5 | F-004、F-005 |
| 许可证双轨 | 14 Apache-2.0 + 4 Anthropic 专有 + 1 无 LICENSE.txt | F-010、F-011 |

## Skills 核心概念

| 特性 | 说明 |
|------|------|
| **自动触发** | 基于 `description` 中的触发条件语义匹配，无需用户记忆命令 |
| **自包含目录** | 每个 Skill 是独立目录，含 SKILL.md + scripts/references/agents/examples 等资源 |
| **标准格式** | YAML frontmatter（6 个允许字段，name + description 必填）+ Markdown 指令正文 |
| **按需加载** | 三级渐进披露：metadata 常驻 → body 触发时加载 → resources 按需 |
| **可分发** | 支持本地安装、Git 分发、`.skill` 打包三种方式 |

四大扩展机制对比：Commands（用户显式斜杠命令）、Agents（子代理）、**Skills（自动触发能力包）**、Hooks（生命周期事件）。

## 文档导航

### 📚 概念文档（9 篇）

| 主题 | 说明 |
|------|------|
| [Skills生态概览](concepts/00-overview.md) | Skills 是什么、与 Commands/Agents/Hooks 的关系、触发机制、19 个 Skills 分类总览、安装使用方法 |
| [SKILL.md格式规范](concepts/01-skill-format.md) | 目录结构、frontmatter 六字段详解与硬约束、description 编写规范、body 组织方式、资源引用约定、打包分发 |
| [Skill Creator工具详解](concepts/02-skill-creator.md) | 元技能 5 步创建流程、3 个评估代理（analyzer/comparator/grader）、eval-viewer、description improver、评估方法论 |
| [Claude API Skill详解](concepts/03-claude-api-skill.md) | claude-api 多语言覆盖、API 漂移警告、默认配置、"Never guess SDK usage"原则 |
| [Skill 编写规范与可复用模式](concepts/04-authoring-patterns.md) | **跨 19 个 skill 反向提炼**：frontmatter 字段决策、description 三种强度、正文四种模式、资源目录分工、黑盒脚本契约、评估闭环 |
| [文档处理类 Skills 详解](concepts/05-document-skills.md) | docx/pdf/pptx/xlsx/doc-coauthoring：共享 office/ 子树、XML 原地编辑、三层 QA、公式强制重算、读者测试 |
| [设计与创意类 Skills 详解](concepts/06-design-skills.md) | algorithmic-art/canvas-design/theme-factory/frontend-design/brand-guidelines/slack-gif-creator/web-artifacts-builder |
| [API 与开发工具类 Skills 详解](concepts/07-dev-skills.md) | claude-api/mcp-builder/skill-creator/webapp-testing：TRIGGER+SKIP 探测、reference 加载时机标注、双跑评估、侦察—动作 |
| [沟通与写作类 Skills 详解](concepts/08-communication-skills.md) | internal-comms/academy-guide/discernment-nudge：薄壳路由、正向推荐规则、反触发清单 |

### 🎯 示例文档（2 篇）

| 示例 | 说明 |
|------|------|
| [从零造一个 Skill](examples/01-author-a-skill.md) | 以最小真实 Skill 演示 frontmatter 编写、目录组织、校验、打包、评估全流程，**命令可直接复制** |
| [场景到 Skill 的选型决策树](examples/02-skill-selection.md) | 19 个 skill 主决策树、六组边界误选对照、可复用命令示例、三个高频组合 |

### 📖 参考文档（3 篇）

| 参考 | 说明 |
|------|------|
| [全部Skills索引](references/skills-index.md) | 19 个 skill 的功能、**实测真实资源路径**、触发条件、体量速查、10 个主题、5 个 plugin 分组 |
| [事实登记表](references/facts.md) | **F-001~F-098 逐条实测底账**，含证据等级（S/D/U）与可复现复核路径 |
| [社区视角与勘误对照](references/community-view.md) | 知乎社区口径（单源）对照，12 条裁定 + 6 条源码独有事实 |

## 19 个官方 Skills 速查

| 分类 | Skills |
|------|--------|
| **API 与开发工具** | `claude-api`、`mcp-builder`、`skill-creator`、`webapp-testing` |
| **文档处理** | `docx`、`pdf`、`pptx`、`xlsx`、`doc-coauthoring` |
| **设计与创意** | `algorithmic-art`、`canvas-design`、`theme-factory`、`frontend-design`、`brand-guidelines`、`slack-gif-creator`、`web-artifacts-builder` |
| **沟通与写作** | `internal-comms`、`academy-guide`、`discernment-nudge` |

## 核心可复用模式速览

| 模式 | 出处 | 可复用性 |
|------|------|---------|
| **description 内嵌可执行排除探测** | claude-api | 🟢 照搬 |
| **reference 标注加载时机** | mcp-builder | 🟢 照搬 |
| **双跑评估闭环（with vs baseline）** | skill-creator | 🟢 照搬 |
| **三层 QA（内容/文件/视觉）** | pptx | 🟢 照搬 |
| **侦察—动作分离** | webapp-testing | 🟢 照搬 |
| **FIXED vs VARIABLE 显式切分** | algorithmic-art | 🟢 照搬 |
| **读者测试（预测问题→子代理作答）** | doc-coauthoring | 🟢 照搬 |
| **薄壳路由 + 兜底文件 + 匹配不上就问** | internal-comms | 🟢 照搬 |
| **强匹配才推荐、绝不编造** | academy-guide | 🟢 照搬 |
| **频率上限 + 跳过清单 + 输出锚定** | discernment-nudge | 🟢 照搬 |
| **主题用 Markdown 而非 JSON** | theme-factory | 🟡 需改写 |
| **共享子树整块复制而非抽公共包** | docx/pptx/xlsx | 🔴 仅理解原理 |

## 与其他子 bundle 的交叉链接

| 相关 bundle | 链接 | 关系说明 |
|------------|------|---------|
| **Claude Code Wiki** | [/claude-code/concepts/01-plugin-system.md](../claude-code/concepts/01-plugin-system.md) | Skills 是 Claude Code 插件体系四大扩展机制之一 |
| **Python SDK Wiki** | [/python-sdk/concepts/08-beta-agents.md](../python-sdk/concepts/08-beta-agents.md) | SDK Beta Skills API 是云端 API 层面概念，与本地文件系统级 Skills 不同 |
| **Python SDK 概览** | [/python-sdk/concepts/00-overview.md](../python-sdk/concepts/00-overview.md) | claude-api Skill 中 Python 部分的详细文档 |
| **Agent Skills 规范束** | [../../frameworks/ai-agent/anthropics-skills/index.md](../../frameworks/ai-agent/anthropics-skills/index.md) | 通用格式规范视角，本 bundle 是官方库实例视角 |

> ⚠️ **两个 bundle 的分工**：本 bundle（`official-skills`）聚焦**官方 19 个 skill 的逐个剖析与实测**；`ai-agent/anthropics-skills` 聚焦**SKILL.md 格式规范与渐进式加载机制**的通用说明。两者互补，不重复。

## 更新日志

完整变更记录见 [log.md](log.md)。

```{toctree}
:maxdepth: 3

concepts/index
examples/index
references/index
log
```
