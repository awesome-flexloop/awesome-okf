---
type: Concept
title: Git Commit Generator 参考实现分析
description: trae-agents 仓库中唯一正式 Agent——git-commit-generator 的完整结构分析，包括 Prompt 设计、11 种 Conventional Commits 类型、工具最小化配置和参数建议
tags: [agents, git-commit, conventional-commits, reference-implementation, trae-agents, trae]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/agents-source.md
    title: "Trae Agents 源码信源"
---

# Git Commit Generator 参考实现分析

git-commit-generator 是 trae-agents 仓库中目前唯一的正式 Agent（状态 ✅ Stable），作为"参考实现"展示模板的每个章节应如何正确填写。分析它有助于理解一个高质量 Agent 配置的设计思路。

## 功能定位

Git Commit Generator 的功能是：**根据代码变更自动生成符合 Conventional Commits 规范的提交信息**。

开发者执行 `git diff` 后，将变更内容提供给该 Agent，Agent 分析变更类型和影响范围，输出规范的 commit message。

## Prompt 设计分析

### 11 种 Conventional Commits 类型

Prompt 中明确定义了 11 种提交类型，每种类型对应特定的使用场景：

| 类型 | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响代码运行） |
| `refactor` | 重构（既不是新功能也不是修 Bug） |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `build` | 构建系统或外部依赖 |
| `ci` | CI 配置 |
| `chore` | 其他不修改 src 或 test 的杂项 |
| `revert` | 回退之前的提交 |

### 提交信息格式

Prompt 严格规定输出格式：

```
<type>(<scope>): <subject>
```

格式规则：
- **祈使语气**：使用"add"而非"added"或"adds"
- **首字母小写**：subject 首字母不大写
- **末尾无句号**：subject 末尾不加句号
- **主题行限制**：subject 不超过 50 字符
- **正文换行**：正文每行不超过 72 字符
- **可选正文**：在 subject 后空一行写正文，解释"为什么"而非"怎么做"

### 5 条重要原则

Prompt 中规定了 5 条核心行为原则：

1. **准确性优先**：不猜测变更意图，基于 diff 内容准确判断
2. **简洁明了**：commit message 精炼表达核心变更
3. **遵循规范**：严格遵循 Conventional Commits 格式
4. **建设性建议**：发现多个不相关变更时建议拆分提交
5. **上下文感知**：理解代码上下文，生成有意义的 scope 描述

### 4 个示例覆盖主要场景

Prompt 包含 4 个精心设计的示例：

1. **文档更新**（docs）：简单的文档类提交
2. **新功能开发**（feat(auth)）：带 scope 的新功能提交
3. **Bug 修复**（fix(user-service)）：带 scope 的修复提交
4. **重构含 BREAKING CHANGE**（refactor(api)）：含破坏性变更的复杂提交

这 4 个示例覆盖了从简单到复杂的主要使用场景，让模型通过 few-shot learning 理解输出格式。

## 工具配置：最小化原则的典范

git-commit-generator 的工具配置完美体现了最小化原则：

| 工具 | 状态 | 原因 |
|------|------|------|
| 文件编辑 | ❌ 未勾选 | 只读取 diff，不需要修改文件 |
| 终端命令 | ✅ 勾选 | 需要执行 `git diff` 获取变更内容 |
| 网络搜索 | ❌ 未勾选 | 生成 commit message 不需要联网 |
| 浏览器自动化 | ❌ 未勾选 | 不需要浏览器操作 |
| 其他智能体调用 | ❌ 未勾选 | 独立完成任务，不需要协作 |

MCP 服务：不需要特殊的 MCP 服务，可选配置 filesystem MCP。

这种"只开一个工具"的配置方式，让 Agent 的行为边界极其清晰——它只能通过终端执行 git 命令获取 diff，然后生成文本，不会意外修改文件或访问网络。

## 参数配置建议

| 参数 | 推荐值 | 理由 |
|------|--------|------|
| 模型 | GPT-4 / Claude 3.5 / Gemini Pro | 代码理解能力强，格式遵循准确 |
| 温度 | 0.3-0.5 | 偏低温度确保输出准确稳定，不偏离规范 |
| 上下文长度 | 4K 足够 | git diff 通常不会太长，4K token 基本满足 |

温度设置 0.3-0.5（而非通用的 0.7）是因为 commit message 生成是一个**准确性优先**的任务，不需要创造性，需要的是对变更的准确分析和规范的格式输出。

## 参考价值

git-commit-generator 作为参考实现，展示了高质量 Agent 配置的几个关键特征：

1. **明确的角色边界**：只做一件事（生成 commit message），做到最好
2. **完整的类型体系**：11 种类型覆盖所有常见场景
3. **严格的格式约束**：通过规则+示例确保输出规范
4. **最小化工具权限**：只启用必要工具
5. **针对性的参数调优**：温度、模型选择匹配任务特性
6. **丰富的 few-shot 示例**：4 个示例覆盖简单到复杂场景

## 相关链接

- [TRAE Agents 仓库定位与"文档即配置"模式](00-introduction.md)
- [Agent 目录结构与模板规范](01-agent-structure.md)
- [创建自定义 Agent 示例](../examples/create-agent.md)
- [TRAE Agents 仓库资源索引](../references/agents-source.md)
