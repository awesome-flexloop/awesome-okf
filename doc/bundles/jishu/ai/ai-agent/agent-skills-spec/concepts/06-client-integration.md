---
type: Concept
title: 客户端生态与集成：发现、披露、激活与长会话管理
description: 智能体客户端如何支持 Agent Skills——46 家客户端名录、三层加载契约、.agents/skills/ 惯例与扫描上界、宽松校验四规则、双激活路径、结构化包裹与上下文压缩豁免。
tags: [agent-skills, skill-format, client-integration, discovery, activation, ecosystem]
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-08-29" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29" }
status: stable
stale_after: 2027-08-29
sources:
  - id: client-mdx
    resource: /references/spec-sources.md
    title: docs/client-implementation/adding-skills-support.mdx
  - id: clients-jsx
    resource: /references/spec-sources.md
    title: docs/snippets/clients.jsx 客户端名录数据
  - id: home-mdx
    resource: /references/spec-sources.md
    title: docs/home.mdx 开放标准定位
---

# 客户端生态与集成：发现、披露、激活与长会话管理

Agent Skills 是"lightweight, open format for extending AI agent capabilities"，最初由 Anthropic 开发，作为开放标准发布并被越来越多的智能体产品采纳（F-042）。本文面向客户端（智能体产品）实现者，整合 adding-skills-support.mdx 的完整生命周期指南；也帮助技能作者理解"我的技能会被如何发现和使用"。

## 生态规模

`docs/clients.mdx` 从 `docs/snippets/clients.jsx` 导入 `clients` 数组渲染 `ClientShowcase` 组件；该数组共 **46 个条目**，每条字段为 `name`、`description`、`url`、`lightSrc`、`darkSrc`、可选 `scale`、`instructionsUrl`、可选 `sourceCodeUrl`。名录包含 Claude、Claude Code、ChatGPT & Codex、Gemini CLI、GitHub Copilot、VS Code、Cursor、Goose、OpenHands、Letta、Factory、Kiro、Spring AI、Roo Code、TRAE（sourceCodeUrl 指向 github.com/bytedance/trae-agent）等（F-041）。

## 集成的两个根本差异

客户端之间的集成差异归结为两个因素（F-043）：

1. **技能住在哪里**：本地智能体扫文件系统；云端/沙箱需要 API、远程注册表或捆绑资产等替代发现机制。
2. **模型如何访问技能内容**：有文件读取能力则直接读 SKILL.md；否则提供专用工具或程序化注入提示词。

## 三层加载契约

| 层级 | 内容 | 加载时机 | 开销 |
|---|---|---|---|
| Tier 1 Catalog | name + description | 会话启动时 | 每技能约 50-100 tokens |
| Tier 2 Instructions | 完整 `SKILL.md` 正文 | 技能激活时 | 推荐 <5000 tokens |
| Tier 3 Resources | 脚本、引用、资产 | 指令引用时按需 | 开销不定 |

装了 20 个技能的智能体不必预付 20 套完整指令的 token 成本——只付当次会话实际用到的（F-043）。

## 发现：位置与扫描规则

**发现位置**（F-044）：多数本地智能体至少扫 project-level（相对工作目录）与 user-level（相对 home 目录）两个作用域；每个作用域内同时扫客户端自有目录与 `.agents/skills/` 约定路径：

| 作用域 | 客户端自有目录 | 跨客户端惯例 |
|---|---|---|
| 项目级 | `<project>/.<your-client>/skills/` | `<project>/.agents/skills/` |
| 用户级 | `~/.<your-client>/skills/` | `~/.agents/skills/` |

`.agents/skills/` 是"广泛采用的跨客户端技能共享惯例"；**规范本身不强制技能目录住在哪里**（只定义目录内放什么）。部分实现还扫 `.claude/skills/`（项目级与用户级）以兼容既有技能；其他附加位置包括上溯至 git 根的祖先目录（monorepo 场景）、XDG 配置目录、用户自定义路径。

**扫描规则**（F-045）：

- 在每个技能目录里找"含有名为恰好 `SKILL.md` 的文件的子目录"（README.md 等被忽略）；
- 跳过 `.git/`、`node_modules/` 等目录；
- 可选遵守 `.gitignore` 避免扫描构建产物；
- **设合理上界**——如最大深度 4-6 层、最多 2000 个目录——防止大目录树失控扫描。

**命名冲突与信任**（F-046）：两个技能同名时的确定性优先规则——现有实现的普遍惯例是"项目级技能覆盖用户级技能"；同一作用域内 first-found 或 last-found 均可，但须择一并保持一致，冲突时记录 warning 告知用户技能被遮蔽。项目级技能来自可能不受信任的仓库，应考虑用信任检查门控其加载，防止不受信仓库向智能体上下文静默注入指令。云端/沙箱中项目级技能随克隆仓库走，用户级与组织级技能需从外部源供给（克隆配置仓库、接受技能 URL/包、Web UI 上传），内置技能可打包为部署物内静态资产；技能可用后，解析、披露、激活的其余生命周期完全相同。

## 解析与宽松校验

解析分两段：`---` 分隔符间的 YAML frontmatter 与其后的 Markdown 正文（正文经 trim 后即技能 body）。对"技术上非法但彼解析器接受的 YAML"（最常见：未加引号的值含冒号）考虑回退方案——包引号或转为 YAML block scalar 后重试（F-047）。

**宽松校验四规则**（F-047）：

| 情形 | 处理 |
|---|---|
| name 与父目录名不匹配 | **警告但加载** |
| name 超 64 字符 | **警告但加载** |
| description 缺失或为空 | **跳过该技能并记录错误**（description 对披露必不可少） |
| YAML 完全不可解析 | **跳过并记录错误** |

文档附 Note 说明该宽松方案**有意放宽**规范对 name 的严格约束以兼容其他客户端编写的技能——这与 skills-ref 的严格校验形成对照（见 [/concepts/07-skills-ref-reference-implementation.md](/concepts/07-skills-ref-reference-implementation.md)）。

**技能记录**（F-048）：至少三个字段 `name`、`description`、`location`（SKILL.md 绝对路径），存入以 `name` 为键的内存 map 便于激活期快速查找；body 可在发现时存储（激活更快）也可激活时从 location 读取（省内存且能吃到技能文件变更）；技能基目录（location 的父目录）用于后续解析相对路径与枚举捆绑资源。

## 披露：Tier 1 目录构建

为每个已发现技能在结构化格式（XML/JSON/列表均可）中给出 `name`、`description`、可选 `location`（F-049）。XML 示例：

```xml
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extracts text and tables from PDF files</description>
    <location>/path/to/pdf-processing/SKILL.md</location>
  </skill>
</available_skills>
```

每个技能约占 50-100 tokens。`location` 的双重作用：支撑文件读取式激活 + 给模型解析正文中相对引用（如 `scripts/evaluate.py`）提供基路径；若专用激活工具的结果中已带技能目录路径，目录中可省略 `location`（F-049）。

**放置与过滤**（F-050）：两种常见放置——系统提示词加标签小节（更简单、兼容面广）或嵌入专用激活工具的 description（保持系统提示词干净、发现与激活天然耦合）。随目录附简短行为指令，按激活机制分两版：文件读取版 "use your file-read tool to load the SKILL.md at the listed location before proceeding… resolve them against the skill's directory (the parent of SKILL.md)"；专用工具版 "call the activate_skill tool with the skill's name"。被过滤的技能（用户禁用、权限拒绝、声明 `disable-model-invocation` 旗标）应从目录中**完全隐藏**而非列出后在激活时拦截；无可用技能时整个省略目录与行为指令——不显示空的 `<available_skills/>` 也不注册无有效选项的技能工具。

## 激活：Tier 2 的两条路径

多数实现依赖模型自身判断而非 harness 侧触发匹配/关键词检测（F-051）。两条实现路径：

| 路径 | 机制 | 适用 |
|---|---|---|
| 文件读取式激活 | 模型用标准文件读取工具按 location 读 SKILL.md | 无需专门基础设施 |
| 专用工具激活 | 如 `activate_skill` 工具 | 模型不能直接读文件时必需；相对原始文件读取的优势：控制返回内容、以结构化标签包裹、列出捆绑资源、施加权限/征得同意、统计激活 |

工程要点（F-051）：把工具的 `name` 参数约束为有效技能名集合（如 schema 中的 enum）以防模型幻觉出不存在的技能名；无技能时不注册该工具。用户显式激活的常见形态是斜杠命令或提及语法（`/skill-name` 或 `$skill-name`），可配自动补全。模型收到的内容两选项——完整文件（含 frontmatter；`compatibility` 等字段可在激活期提供信息）或仅正文（剥离 frontmatter；现有带专用激活工具的实现中多数采用后者）。

## 长会话上下文管理

**结构化包裹**（F-052）示例：

```xml
<skill_content name="pdf-processing">
…Skill directory: …Relative paths in this skill are relative to the skill directory.
<skill_resources><file>…</file></skill_resources>
</skill_content>
```

收益：模型可区分技能指令与其他会话内容、harness 可在上下文压缩中识别技能内容、捆绑资源被浮现但不急切加载。

其余管理纪律（F-052）：

- 专用工具可枚举支持文件但**不应急切读取**（模型按需用文件读取工具加载）；大目录可封顶枚举并注明可能不完整；
- 有权限系统时应把技能目录加入允许清单，避免每次引用捆绑资源都弹确认；
- 上下文压缩/截断旧消息时**豁免技能内容**（丢失技能指令会无错误地静默劣化表现），可标记工具输出受保护或借结构化标签识别；
- 考虑去重激活（已在上下文中的技能跳过再注入）；
- 子代理委派为可选高级模式——技能在独立子代理会话中运行并向主会话返回工作摘要。

## 相关概念

- [/concepts/01-progressive-disclosure.md](/concepts/01-progressive-disclosure.md) —— 三层契约的规范面
- [/concepts/00-skill-anatomy.md](/concepts/00-skill-anatomy.md) —— 规范对"目录内放什么"的定义
- [/concepts/07-skills-ref-reference-implementation.md](/concepts/07-skills-ref-reference-implementation.md) —— 三个接触点的程序化参考实现
- [/examples/01-first-skill-roll-dice.md](/examples/01-first-skill-roll-dice.md) —— 技能在 `.agents/skills/` 中被发现的过程
