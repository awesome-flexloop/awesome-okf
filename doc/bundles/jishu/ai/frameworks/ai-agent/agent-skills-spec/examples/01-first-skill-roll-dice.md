---
type: Example
title: 创建第一个 Skill 实战：roll-dice
description: 以官方 quickstart 为蓝本从零创建第一个技能——在 .agents/skills/roll-dice/ 写不足 20 行的 SKILL.md，验证发现与激活，再用 skills-ref validate 做格式门禁收尾。
tags: [agent-skills, skill-format, quickstart, tutorial, roll-dice]
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-08-29" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29" }
status: stable
stale_after: 2027-08-29
sources:
  - id: quickstart-mdx
    resource: /references/spec-sources.md
    title: docs/skill-creation/quickstart.mdx
  - id: spec-mdx
    resource: /references/spec-sources.md
    title: docs/specification.mdx 命名与校验约束
---

# 创建第一个 Skill 实战：roll-dice

本例按官方 quickstart 教程复刻一个最小但完整的技能：`roll-dice`（掷骰子）。它演示 Agent Skills 的全部核心机制——目录结构、frontmatter、渐进式披露的三阶段生命周期——并穿插两个最容易出错的格式要点：`name` 必须与文件夹名一致、`description` 是智能体决定是否激活的依据。整个技能的 SKILL.md 单文件**不足 20 行**（F-016）。

前置说明：Agent Skills 是开放格式，同一技能可在 Claude Code 与 OpenAI Codex 等兼容智能体中工作（F-016）；本例以 VS Code 为载体，VS Code 默认在 `.agents/skills/` 目录查找技能（F-016）。文中提示 "Tool-use reliability varies across models"——工具调用的可靠性因模型而异（F-016）。

## 第 1 步：创建目录与 SKILL.md

在项目根目录创建技能目录（`.agents/skills/` 是跨客户端共享惯例，见 [/concepts/06-client-integration.md](/concepts/06-client-integration.md)）：

```bash
mkdir -p .agents/skills/roll-dice
```

创建 `.agents/skills/roll-dice/SKILL.md`，内容如下（不足 20 行）：

````markdown
---
name: roll-dice
description: Roll a random dice roll. Use when the user asks for a dice
  roll, a random number between 1 and 6, or wants to play a dice game.
---

# Roll Dice

Roll a six-sided die and return the result.

## Instructions

1. Generate a random integer between 1 and 6.
2. Report the result to the user.

Example: run this command
```bash
echo $((RANDOM % 6 + 1))
```
````

三个组成部分的分工（F-016）：

| 部分 | 作用 | 格式要点 |
|---|---|---|
| `name: roll-dice` | 技能标识 | **必须与文件夹名 `roll-dice` 一致**（F-005、F-016） |
| `description` | 智能体决定是否激活该技能的依据 | 用祈使式措辞 + 显式适用场景（F-036） |
| 正文 | 激活后智能体遵循的指令 | 智能体决定激活后加载整个文件（F-010） |

## 第 2 步：验证技能被发现（Discovery）

重启会话后，智能体在启动时扫描默认技能目录，只读 `name` 与 `description`（F-017）。验证方式：向智能体询问"你有哪些可用技能"或触发一次任务，观察技能是否出现在技能列表中。

此时该技能在上下文中只占约 100 tokens——两个元数据字段，而非整个文件（F-012）。

## 第 3 步：触发激活与执行（Activation → Execution）

发送一条匹配 description 的请求：

```text
Roll a dice for me
```

预期行为链（F-017）：

1. **Activation**：用户请求与 `roll-dice` 的 description 匹配 → 智能体加载完整 SKILL.md 正文；
2. **Execution**：按正文指令执行——运行 `echo $((RANDOM % 6 + 1))`，把结果报告给用户，按请求适配（例如用户要求掷两个骰子时跑两次）。

这一过程使用 progressive disclosure：正文与脚本只在激活后进入上下文（F-017）。

## 第 4 步：格式门禁收尾

发布前用参考校验器做一次严格校验（规范 Validation 一节给出的命令，F-015）：

```bash
skills-ref validate .agents/skills/roll-dice
# 输出: Valid skill: .agents/skills/roll-dice（退出码 0）
```

若把 `name` 改成与目录名不一致的值（如 `roll_dice`），校验会失败并给出错误消息：

```bash
skills-ref validate .agents/skills/roll-dice
# Validation failed for .agents/skills/roll-dice:
#   - Skill name 'roll_dice' contains invalid characters. ...
#   - Directory name 'roll-dice' must match skill name 'roll_dice'
# 退出码 1
```

三子命令的完整用法见 [/examples/02-skills-ref-cli.md](/examples/02-skills-ref-cli.md)。

## 常见错误对照

| 错误做法 | 后果 | 正确姿势 |
|---|---|---|
| 目录名与 `name` 不一致 | 严格校验报 "must match skill name"；宽松客户端仅警告加载（F-047、F-059） | 保持 `name == 目录名` |
| description 只写 "Helps with games." | 触发不可靠（F-007 差例） | 写明 what + when + 关键词（F-007） |
| 把 SKILL.md 放进 `.agents/skills/` 根而非子目录 | 扫描规则要求"含有 SKILL.md 的**子目录**"（F-045） | 每个技能一个子目录 |
| 大写 `Roll-Dice` | 报 "must be lowercase"（F-005、F-059） | 全小写 kebab-case |

## 延伸

- 想给技能加脚本与参考文档 → [/concepts/00-skill-anatomy.md](/concepts/00-skill-anatomy.md)
- 想让技能更可靠 → [/concepts/03-authoring-principles.md](/concepts/03-authoring-principles.md) 与 [/concepts/04-eval-driven-iteration.md](/concepts/04-eval-driven-iteration.md)

## 相关概念

- [/concepts/00-skill-anatomy.md](/concepts/00-skill-anatomy.md) —— 本例目录结构的完整规范
- [/concepts/01-progressive-disclosure.md](/concepts/01-progressive-disclosure.md) —— 第 2-3 步背后的加载契约
- [/concepts/05-description-optimization.md](/concepts/05-description-optimization.md) —— description 写不好时如何系统优化
- [/examples/02-skills-ref-cli.md](/examples/02-skills-ref-cli.md) —— 第 4 步校验命令的完整实战
