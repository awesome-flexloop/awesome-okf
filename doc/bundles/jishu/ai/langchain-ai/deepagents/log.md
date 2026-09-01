---
type: log
scope: deepagents
name: log
version: "0.7.8"
source: https://github.com/langchain-ai/deepagents
description: deepagents OKF bundle 变更日志
---

# 变更日志

## 2026-08-23 — v0.7.8 初始 bundle

**OKF 版本**：0.2
**深度**：中等
**覆盖范围**：核心 SDK + ACP + CLI + lca-deepagents 变体

### 新增

- 初始 bundle 结构创建
- `spec/facts.md`：64条从源码验证的编号事实，覆盖项目元信息、公共 API、图组装、子代理系统、异步子代理、文件系统中间件、上下文管理、内存与技能、后端系统、Harness Profiles、ACP 集成、CLI、GitHub Action、lca-deepagents 变体、架构文档
- `spec/insights.md`：5个架构设计洞察
  1. 三层栈定位：不发明运行时，只组装最佳实践
  2. 中间件即能力：模型调用前后的可编程拦截点
  3. 子代理的上下文隔离与状态传播
  4. 后端抽象与 DeltaChannel：持久化的两个维度
  5. Profile 系统：模型特化的正交调优
- `concepts/`：4篇核心概念
  - `overview.md`：总览与三层架构
  - `planning-subagents.md`：子代理架构详解
  - `todo-context.md`：上下文管理机制
  - `acp-protocol.md`：ACP 协议概念
- `references/`：6篇技术参考
  - `api.md`：核心 API 参考
  - `middleware-stack.md`：中间件栈排序与规则
  - `backends.md`：后端系统参考
  - `profiles.md`：Profile 机制参考
  - `acp-protocol.md`：ACP 协议 API 参考
  - `lca-variant.md`：lca-deepagents 变体说明
- `examples/`：1篇使用示例
  - `lca-variant.md`：Chinook Sales Assistant 综合示例
- 所有交叉链接以 `/langchain-ai/deepagents/` 开头
- 所有正文为中文
- 所有文件名为 kebab-case

### 源码参考

- 主仓库：`external/libs/ai/langchain-ai/deepagents/`（SDK 版本 0.7.8）
- 变仓库：`external/libs/ai/langchain-ai/lca-deepagents/`（课程材料，固定 deepagents==0.7.0）
- 参考 bundle：`projects/awesome-okf-xs/bundles/deepseek/lplb/`
