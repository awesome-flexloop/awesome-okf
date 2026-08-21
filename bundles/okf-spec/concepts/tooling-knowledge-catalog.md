---
type: Reference
title: OKF Knowledge Catalog CLI
description: Google Cloud Platform 官方维护的 OKF 工具链仓库（knowledge-catalog），包含规范源码、OKF 格式核心库、命令行工具和示例项目。
tags: [okf, tooling, cli, google-cloud, npm, reference-implementation]
generated: { by: reference_agent/trae-glm, at: 2026-08-21T08:00:00Z }
status: draft
stale_after: 2027-06-30T00:00:00Z
sources:
  - id: okf-md
    resource: https://okf.md/
    title: Open Knowledge Format (OKF) — A Markdown-based knowledge standard
  - id: okf-md-quickstart
    resource: https://okf.md/quickstart
    title: Your First OKF Bundle in 5 Minutes
  - id: github-kc
    resource: https://github.com/GoogleCloudPlatform/knowledge-catalog
    title: GoogleCloudPlatform/knowledge-catalog GitHub 仓库
---

# OKF Knowledge Catalog CLI

OKF Knowledge Catalog 是 Google Cloud Platform 在 GitHub 上维护的官方工具链仓库，托管于 [github.com/GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog)。它既是 OKF 规范的源码仓库，也是参考实现和 CLI 工具的官方来源。[^okf-md][^github-kc]

## 仓库结构

knowledge-catalog 仓库包含以下核心组件：

| 组件 | 路径 | 说明 |
|---|---|---|
| 规范文档 | `okf/SPEC.md` | OKF v0.2 正式规范的权威文本（即 [references/okf-spec.md](/references/okf-spec.md) 的来源） |
| 示例知识包 | `examples/` | 官方示例知识包（SaaS Metrics 等） |
| OKF 核心库 | `packages/okf/` | 发布为 npm 包 `@okf/okf`，提供知识包解析、验证、生成等核心功能 |
| CLI 工具 | `packages/cli/` | 命令行工具，通过 `npx okf` 调用 |
| Agent Skill | `packages/agent-skill/` | AI 智能体技能包的源码（见 [tooling-agent-skill.md](./tooling-agent-skill.md)） |

## CLI 功能

通过 `npx okf` 调用的命令行工具提供以下功能：

| 命令 | 说明 |
|---|---|
| `npx okf validate <path>` | 验证知识包合规性（与 validate.sh 功能相同） |
| `npx okf add-agent-skill` | 安装 OKF Agent Skill 到当前项目 |
| `npx okf init <path>` | 初始化一个新的知识包目录结构（创建 index.md、log.md 和示例概念文件） |
| `npx okf index <path>` | 扫描知识包目录自动生成/更新 index.md |

## npm 包

核心功能以 `@okf/okf` npm 包发布，提供编程接口：

- **解析器（Parser）**：将 OKF Markdown 文件解析为结构化对象（frontmatter + 正文）。
- **验证器（Validator）**：程序化检查知识包合规性，返回结构化的错误/警告/提示列表。
- **生成器（Generator）**：从结构化数据生成符合规范的 OKF Markdown 文件。
- **链接解析器（Link Resolver）**：解析和验证知识包间的交叉链接。

## 与本 bundle 的关系

本 `okf-spec` 知识包本身是 OKF 规范的中文文档化 bundle，而非官方工具链。理解官方工具链有助于：

1. **获得最新规范更新**：当 OKF 发布 v0.3+ 新版本时，规范文本将首先出现在 knowledge-catalog 仓库。
2. **使用官方 CLI**：通过 `npx okf` 命令初始化、验证和管理知识包，比手写脚本更可靠。
3. **集成到工作流**：将 `npx okf validate` 集成到 CI/CD 流水线，确保团队产出的知识包始终合规。

## 快速使用

```bash
# 安装 Agent Skill（见 tooling-agent-skill.md）
npx okf add-agent-skill

# 验证知识包
npx okf validate knowledge/metrics/

# 初始化新知识包
npx okf init knowledge/my-domain/
```

## 生态工具总览

| 工具 | 类型 | 用途 | 文档 |
|---|---|---|---|
| 在线 Validator | Web 应用 | 浏览器中快速检查知识包 | [tooling-validator.md](./tooling-validator.md) |
| Agent Skill | AI 技能包 | 让智能体创建/验证知识包 | [tooling-agent-skill.md](./tooling-agent-skill.md) |
| validate.sh | Shell 脚本 | 命令行验证（随 Skill 安装） | [tooling-agent-skill.md](./tooling-agent-skill.md) |
| Knowledge Catalog CLI | npm/CLI | 官方命令行工具 | 本文档 |
| @okf/okf npm 包 | TypeScript 库 | 程序化解析/验证/生成 | 本文档 |
| okf.md 网站 | 文档站点 | 规范、Quickstart、教程 | [references/okf-spec.md](/references/okf-spec.md) |

## 相关概念

- [OKF Validator](./tooling-validator.md) - 在线可视化验证工具
- [OKF Agent Skill](./tooling-agent-skill.md) - AI 智能体技能包
- [知识包目录结构](./bundle-structure.md) - 规范定义的目录布局
- [版本控制](./versioning.md) - OKF 版本规则与 v0.2 之后的演进
- [SaaS 指标快速入门](../examples/saas-metrics-quickstart.md) - Quickstart 教程示例

[^okf-md]: OKF 官方网站，见 [okf.md](https://okf.md/)。
[^okf-md-quickstart]: OKF Quickstart 教程，见 [okf.md/quickstart](https://okf.md/quickstart)。
[^github-kc]: GoogleCloudPlatform/knowledge-catalog 仓库，见 [github.com/GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog)。
