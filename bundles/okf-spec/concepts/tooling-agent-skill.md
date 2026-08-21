---
type: Reference
title: OKF Agent Skill
description: OKF 官方为 AI 智能体（Claude Code、Codex、Gemini CLI 等）提供的技能包，包含创建/读取/验证知识包的提示词模板和 validate.sh 脚本。
tags: [okf, tooling, agent, skill, claude-code, codex, gemini]
generated: { by: reference_agent/trae-glm, at: 2026-08-21T08:00:00Z }
status: draft
stale_after: 2027-06-30T00:00:00Z
sources:
  - id: okf-md-skill
    resource: https://okf.md/skill
    title: Install the Agent Skill
  - id: okf-md-quickstart
    resource: https://okf.md/quickstart
    title: Your First OKF Bundle in 5 Minutes
---

# OKF Agent Skill

OKF Agent Skill 是为 AI 编程智能体设计的技能包，让智能体能够以标准化方式创建、读取和验证 OKF 知识包。[^okf-md-skill]

## 支持的智能体

- **Claude Code** — Anthropic 的命令行 AI 编程助手
- **Codex** — OpenAI 的 AI 编程工具
- **Gemini CLI** — Google 的命令行 AI 编程助手
- 其他支持自定义技能/提示词模板的 AI 智能体

## 一键安装

在项目根目录执行以下命令即可安装 OKF Agent Skill：

```bash
npx okf add-agent-skill
```

该命令会：

1. 创建 `.agents/skills/okf/` 目录（Claude Code 使用此路径）
2. 放入 `SKILL.md` 提示词模板——智能体读取此文件即"学会"OKF 规范
3. 放入 `validate.sh` 脚本——可执行的知识包验证工具
4. 其他智能体（Codex/Gemini）的技能文件放在对应路径

安装后，智能体在项目目录中工作时会自动加载 OKF 技能提示词，从而正确创建和验证知识包。

## SKILL.md 的作用

`SKILL.md` 是一份面向智能体的指令文件，它：

- 告诉智能体 OKF 是什么以及为什么使用它
- 提供创建概念文档时的 frontmatter 模板
- 指导何时添加 sources、generated、verified 等可选字段
- 解释交叉链接、索引、日志的格式要求
- 提供反模式提醒（常见错误）

这意味着你不需要在每次对话中重复向智能体解释 OKF 规范——安装 Skill 后，智能体"自带"OKF 知识。

## validate.sh

安装后获得的 `validate.sh` 脚本是命令行验证工具：

```bash
.agents/skills/okf/validate.sh knowledge/my-bundle/
```

- 检查指定路径下的知识包是否符合 v0.2 规范
- 报告错误（Errors）、警告（Warnings）和提示（Hints）
- 发现错误时返回非零退出码，适合 CI/CD 集成
- 完全本地运行，不需要网络连接

**CI 集成示例：**

```yaml
# GitHub Actions 示例
- name: Validate OKF knowledge
  run: .agents/skills/okf/validate.sh knowledge/metrics/
```

## Quickstart 中的使用示例

根据官方 Quickstart 教程，安装 Skill 后，你可以直接对智能体说：

> "Create a new knowledge bundle at `knowledge/metrics/` with a single concept: MRR. Include sources and a verified tier."

智能体将自动：

1. 创建知识包目录结构（`knowledge/metrics/`）
2. 创建 `index.md` 和 `log.md`
3. 编写 `concepts/mrr.md`，包含正确的 frontmatter（type、title、description、tags、generated、sources、verified）
4. 写入正文解释 MRR 概念
5. 运行 `validate.sh` 验证
6. 验证通过后更新 `index.md` 索引
7. 在 `log.md` 中记录变更

这种"一句话创建知识包"的体验是 Agent Skill 的核心价值。

## 与在线 Validator 的关系

| 特性 | Agent Skill + validate.sh | 在线 Validator |
|---|---|---|
| 适用场景 | 开发流程/CI 集成 | 快速可视化检查 |
| 安装要求 | `npx okf add-agent-skill` | 零安装，浏览器打开即用 |
| 运行环境 | 本地命令行 | 浏览器客户端 JavaScript |
| 智能体集成 | ✅ 内置 SKILL.md 提示词 | ❌ |
| 退出码 | ✅ 非零退出码支持 CI | ❌ |

## 相关概念

- [OKF Validator](./tooling-validator.md) - 在线可视化验证工具
- [OKF Knowledge Catalog CLI](./tooling-knowledge-catalog.md) - 官方生态 CLI 工具
- [合规性](./conformance.md) - validate.sh 检查的规范依据
- [知识包目录结构](./bundle-structure.md) - Skill 创建的目录布局
- [SaaS 指标快速入门](../examples/saas-metrics-quickstart.md) - Quickstart 教程示例

[^okf-md-skill]: OKF Agent Skill 安装页，见 [okf.md/skill](https://okf.md/skill)。
[^okf-md-quickstart]: OKF Quickstart 教程，见 [okf.md/quickstart](https://okf.md/quickstart)。
