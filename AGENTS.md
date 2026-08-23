---
type: Playbook
title: Awesome OKF for Xuanspace 智能体协作入口
sources:
  - id: xuanspace-agents
    resource: https://github.com/xinetzone/xuanspace
    title: XuanSpace（玄境）智能体协作入口模板
---

# Awesome OKF for Xuanspace 智能体协作入口

> **🚨 启动协议（PRIORITY ZERO — 所有智能体必须在收到任务后立即执行）**
>
> **步骤 1**：读取本文件全文
>
> **步骤 2**：按「上下文路由表」确定本次任务需要读取的规范文件
>
> **步骤 3**：读取对应的规范文件（按需读取，不要一次加载全部）
>
> **步骤 3.5**（自检·必做）：在执行任何操作之前，逐项确认：
> - □ 是否已读取上下文路由表中与当前任务直接相关的入口？
> - □ 是否理解当前任务所属的内容敏感度级别？
> - □ 是否明确目标文档的存放位置（bundles/ 或 docs/）？
>
> **步骤 4**：在规范指导下执行任务
>
> ⚠️ **禁止在完成步骤 1-3.5 之前生成任何产出物。跳过此协议将导致文档路径错误、格式不符合规范。**

## 项目概述

**awesome-okf-xs** 是 Xuanspace（玄境）项目的**开源知识格式（Open Knowledge Format，OKF）文档库**。

- **定位**：以 [XuanSpace](https://github.com/xinetzone/xuanspace) 为基底（内容来源与规范模板），将玄境项目的知识资产以 OKF 格式组织、存储与发布
- **核心理念**：技术为器、思想为道，器以载道——xuanspace 承载"器"（代码与工具），本库承载"道"（知识与思想）
- **知识形态**：文档、复盘、洞察、模式、最佳实践等，统一以 OKF bundle 组织

本文件是 awesome-okf-xs 文档库 AI 智能体的最高优先级入口与上下文路由。所有智能体在启动时必须首先读取本文件，依据上下文路由表定位到具体的 `.agents/` 规范后执行任务。

## 核心规范入口表

| 规范 | 入口 | 说明 |
|---|---|---|
| 🚀 入门指南 | [.agents/ONBOARDING.md](.agents/ONBOARDING.md) | 快速开始、常用操作、文档库结构速览 |
| 📜 全局核心规则 | [.agents/global-core-rules.md](.agents/global-core-rules.md) | 启动协议、内容敏感度分流、OKF 文档规范 |
| 🧭 上下文路由表 | [.agents/context-routing.md](.agents/context-routing.md) | 任务类型→必读规范映射表 |
| 📄 文档元数据规范 | [.agents/rules/frontmatter.md](.agents/rules/frontmatter.md) | OKF v0.2 YAML frontmatter 规范 |

## 目录结构说明

```
awesome-okf-xs/
├── doc/                # Sphinx 文档工程
│   └── bundles/        # OKF bundle 文档（结构化知识束）
├── .agents/            # AI 智能体规范目录（本规范所在目录）
├── AGENTS.md           # 本文件 - 智能体入口
└── README.md           # 项目说明
```

### 目录用途

| 目录 | 适用场景 |
|---|---|
| `doc/bundles/` | 以 OKF bundle 形式组织的结构化知识文档 |

## 文档规范要点

- **语言**：正文使用中文，文件名使用 kebab-case 纯英文
- **格式**：Markdown，遵循 OKF v0.2 YAML frontmatter 规范（详见 [.agents/rules/frontmatter.md](.agents/rules/frontmatter.md)）
- **知识组织**：结构化的知识文档优先使用 OKF bundle 组织，存放在 `doc/bundles/` 下
- **路径引用**：Markdown 交叉引用使用相对路径，禁止 `file:///` 绝对路径
- **派生产物溯源**：源自外部（如 xuanspace 或其他项目）的知识文档须在 frontmatter 中标注 `sources` 字段