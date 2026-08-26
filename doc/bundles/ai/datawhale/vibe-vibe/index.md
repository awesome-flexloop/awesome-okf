---
title: Vibe Vibe 知识包
type: index
bundle: vibe-vibe
description: Vibe Vibe 是 Datawhale 出品的国内首个系统化 Vibe Coding 开源教程，以 VitePress 构建中英文双语文档站，通过"个人主页+数字分身"连续案例和四大板块（基础/进阶/实践/文章），引导零基础学习者从想法走到产品上线。本知识包梳理其 Vibe 开发理念、Basic 入门教学设计与多语言文档架构。
concepts:
  - /datawhale/vibe-vibe/concepts/01-vibe-coding-philosophy.md
  - /datawhale/vibe-vibe/concepts/02-basic-getting-started.md
  - /datawhale/vibe-vibe/concepts/03-multilingual-docs-architecture.md
references:
  - /datawhale/vibe-vibe/references/source-repo.md
examples:
  - /datawhale/vibe-vibe/examples/01-docker-deploy.md
sources:
  - https://github.com/datawhalechina/vibe-vibe
---

# Vibe Vibe 知识包

Vibe Vibe 是 Datawhale 开源的 AI 辅助编程系统化教程，口号是"人人都能学会的 AI 编程（Vibe Coding）指南"。它以 VitePress 构建中英文双语静态文档站，通过四大板块引导零基础学习者从"我有一个想法"走到"我做出了一个产品"。

- **官方仓库**：https://github.com/datawhalechina/vibe-vibe
- **在线站点**：https://www.vibevibe.cn
- **许可证**：CC BY-NC-SA 4.0
- **支持语言**：简体中文、英语
- **当前版本**：Alpha v0.0.4（内部预览版）

## 核心理念

Vibe Vibe 践行 Andrej Karpathy 于 2025 年提出的 **Vibe Coding** 理念——**从 Coder 到 Commander**：学习者用自然语言与 AI 对话描述需求，AI 负责代码实现，人负责方向决策、结果审查与迭代。课程将 Vibe Coding 放在更大的"AI 创造"定位中理解：你负责方向、判断和审美，AI 帮你把作品做出来。

课程不是为了把学习者一次训练成资深工程师，而是培养三种能力：把想法做成真实作品的能力、一套可重复使用的 AI 协作方法、更强的产品判断与上线信心。

## 四大板块

| 板块 | 定位 | 适合人群 | 技术栈 |
|------|------|---------|--------|
| 基础篇 | AI 编程入门 + 心法 + 第一个项目 | 完全零基础、用过 ChatGPT 但没做过项目 | HTML/CSS/JS · AI 工具 · Git · 静态部署 |
| 进阶篇 | 16 章从 0 到上线的避坑指南 | 想了解完整项目交付流程的开发者 | Next.js 16 · React · TypeScript · Tailwind · shadcn/ui · Drizzle · PostgreSQL |
| 实践篇 | 分人群项目实战 + 进阶技能训练 | 想通过动手练习巩固所学 | 多种 |
| 优质文章篇 | 精选学习资源 + 行业前沿追踪 | 想持续学习、保持行业敏感度 | 无特定栈 |

## 概念文档

- [Vibe 开发理念](/ai/datawhale/vibe-vibe/concepts/01-vibe-coding-philosophy.md) — Vibe Coding 的起源与定义、从 Coder 到 Commander 的角色转变、AI 创造工作流、MVP 思维、AI 助教路由表（llms.txt）。
- [Basic 入门教学设计](/ai/datawhale/vibe-vibe/concepts/02-basic-getting-started.md) — 基础篇 v2 的"个人主页+数字分身"单一连续案例、7 个交付里程碑、独立 vibe coder 定位、与旧版结构对比。
- [多语言文档架构](/ai/datawhale/vibe-vibe/concepts/03-multilingual-docs-architecture.md) — 中英文双语的三层架构（内容层/配置层/重定向层）、VitePress 稳定版原生多语言、LocaleSwitch 组件、100+ 交互组件体系。

## 示例

- [Docker 私有化部署示例](/ai/datawhale/vibe-vibe/examples/01-docker-deploy.md) — 通过 docker-compose 一条命令启动本地 Vibe Vibe 站点，演示端口映射、健康检查与离线运行特性。

## 信源

- [官方仓库信源登记](/ai/datawhale/vibe-vibe/references/source-repo.md) — 仓库基本信息、关键文件索引、目录速览。

## 学习建议

1. **先理解理念**：从 [Vibe 开发理念](/ai/datawhale/vibe-vibe/concepts/01-vibe-coding-philosophy.md) 开始，理解"从 Coder 到 Commander"的角色转变与 AI 创造工作流。
2. **再看教学设计**：读 [Basic 入门教学设计](/ai/datawhale/vibe-vibe/concepts/02-basic-getting-started.md)，理解基础篇为何用单一连续案例替代知识点章节。
3. **了解工程架构**：关注多语言文档站的实现方式时，读[多语言文档架构](/ai/datawhale/vibe-vibe/concepts/03-multilingual-docs-architecture.md)。
4. **动手部署**：按 [Docker 部署示例](/ai/datawhale/vibe-vibe/examples/01-docker-deploy.md) 在本地启动站点，亲身体验双语切换与交互组件。

## 变更记录

详见 [log.md](/ai/datawhale/vibe-vibe/log.md)。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
