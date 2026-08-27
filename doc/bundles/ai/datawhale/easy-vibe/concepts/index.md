# 概念索引

本目录收录 Easy-Vibe 项目的 3 个核心概念，帮助理解其教学理念、架构设计与工程实践。

## 概念清单

### [01 Vibe Coding 理念](01-vibe-coding-philosophy.md)

Easy-Vibe 把"用自然语言描述需求、由 AI 实现、人来决策与迭代"作为编程新范式，以"产品原型→全栈交付→跨平台进阶"三阶段路径把零基础学习者带到可交付产品的水平。

### [02 多语言文档站架构](02-multilingual-docs-architecture.md)

以 VitePress 构建支持 10 种语言的文档站，采用 locale 隔离目录、侧边栏工厂函数、顺序构建加文件锁、SEO 元数据生成与组件 i18n 扫描，保障大规模多语言内容的构建确定性。

### [03 部署与工具链](03-deployment-toolchain.md)

覆盖本地开发、多语言静态站点构建、三平台部署（Vercel/GitHub Pages/魔搭 Docker）与多语言 PDF/EPUB 电子书发布，并通过 Husky、Prettier、ESLint 保障代码质量。

## 阅读顺序建议

1. 先读 [Vibe Coding 理念](01-vibe-coding-philosophy.md)，理解项目"是什么、教什么、为谁服务"。
2. 再读 [多语言文档站架构](02-multilingual-docs-architecture.md)，理解 10 语言内容如何组织与构建。
3. 最后读 [部署与工具链](03-deployment-toolchain.md)，理解从源码到多形态产物的完整链路。

```{toctree}
:hidden:
:maxdepth: 7

01-vibe-coding-philosophy
02-multilingual-docs-architecture
03-deployment-toolchain
```
