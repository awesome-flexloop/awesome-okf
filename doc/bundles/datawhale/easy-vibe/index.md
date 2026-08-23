---
title: Easy-Vibe 知识束
type: index
bundle: easy-vibe
description: Easy-Vibe 是 Datawhale 出品的 AI Vibe Coding 教程，以 VitePress 构建 10 语言文档站，采用三阶段渐进路径把零基础学习者带到可交付产品水平。本知识束梳理其 Vibe Coding 理念、多语言架构与部署工具链。
concepts:
  - /datawhale/easy-vibe/concepts/01-vibe-coding-philosophy.md
  - /datawhale/easy-vibe/concepts/02-multilingual-docs-architecture.md
  - /datawhale/easy-vibe/concepts/03-deployment-toolchain.md
references:
  - /datawhale/easy-vibe/references/source-repo.md
examples:
  - /datawhale/easy-vibe/examples/01-local-dev-quickstart.md
sources:
  - https://github.com/datawhalechina/easy-vibe
---

# Easy-Vibe 知识束

Easy-Vibe 是 Datawhale（数据whale）开源的 AI Vibe Coding 实战教程，口号是"从零开始学 AI 编程，把想法真正做成产品"。它不是一个软件库，而是一个以 VitePress（Vue 3）构建的多语言文档站，通过三阶段渐进路径，引导零基础学习者从"用自然语言描述需求"走到"独立交付全栈与跨平台应用"。

- **官方仓库**：https://github.com/datawhalechina/easy-vibe
- **在线文档**：https://datawhalechina.github.io/easy-vibe/
- **许可证**：CC BY-NC-SA 4.0
- **支持语言**：简体中文、英语、繁体中文、日语、韩语、西班牙语、法语、德语、阿拉伯语、越南语（共 10 种）

## 核心理念

Easy-Vibe 把 **Vibe Coding**（用自然语言编程）作为 AI 时代的编程新范式：编程从描述你想要什么开始，AI 负责实现，人负责决策与迭代。课程反转了传统"语法→算法→工程"的学习顺序，先让学习者做出可演示的产品原型，再按需补齐全栈与计算机基础知识。

学习路径分为三阶段加一个附录知识库：

| 阶段 | 主题 | 产出 |
|------|------|------|
| Stage 1 | 新手入门与产品原型 | AI IDE 使用、创意验证、可演示原型 |
| Stage 2 | 初中级全栈开发 | 可上线的全栈 AI 应用（含支付） |
| Stage 3 | 高级开发 | Claude Code 深度使用、跨平台应用 |
| 附录 | 9 大领域知识体系 | 80+ 交互式专题 |

## 概念文档

- [Vibe Coding 理念](/datawhale/easy-vibe/concepts/01-vibe-coding-philosophy.md) — 自然语言编程范式、三阶段路径、附录知识库、AI 友好教学设计。
- [多语言文档站架构](/datawhale/easy-vibe/concepts/02-multilingual-docs-architecture.md) — 10 语言内容层、localeMap 配置层、顺序构建加文件锁的构建层、base 路径自适应、首页语言重定向。
- [部署与工具链](/datawhale/easy-vibe/concepts/03-deployment-toolchain.md) — 本地开发、Prettier/ESLint/Husky 质量保障、Vercel/GitHub Pages/魔搭 Docker 三平台部署、PDF/EPUB 电子书发布。

## 示例

- [本地运行与构建示例](/datawhale/easy-vibe/examples/01-local-dev-quickstart.md) — 依赖安装、开发服务器、生产构建、预览命令，以及 AI IDE 一键运行方式。

## 信源

- [官方仓库信源登记](/datawhale/easy-vibe/references/source-repo.md) — 仓库基本信息、关键文件索引、目录速览。

## 学习建议

1. **先理解理念**：从 [Vibe Coding 理念](/datawhale/easy-vibe/concepts/01-vibe-coding-philosophy.md) 开始，理解课程为何这样组织，而非把它当成普通前端教程合集。
2. **再看架构**：如果你关注多语言文档站工程化，读[多语言文档站架构](/datawhale/easy-vibe/concepts/02-multilingual-docs-architecture.md)，重点理解"为什么顺序构建"等反直觉决策。
3. **动手实践**：按[本地运行示例](/datawhale/easy-vibe/examples/01-local-dev-quickstart.md)把站点跑起来，亲身体验欢迎页动画、语言切换与交互组件。
4. **深入工具链**：需要部署或二次开发时，参考[部署与工具链](/datawhale/easy-vibe/concepts/03-deployment-toolchain.md)。

## 变更记录

详见 [log.md](/datawhale/easy-vibe/log.md)。
