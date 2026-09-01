---
type: Concept
title: Tutorials 实战教程
description: Tutorials 提供 6 篇按难度三级分布的实战案例，从看懂代码到提交 PR 的完整 Vibecoding 学习路径。
tags: [trae-learning, trae, vibecoding, tutorial, hands-on, learning-path]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/learning-source.md
    title: "Trae Learning 源码信源"
---

# Tutorials 实战教程

Tutorials 部分包含 7 篇文档（1 篇索引 + 6 篇实战教程），按难度分为三级，提供从"看懂代码"到"独立提交"的完整学习路径。

## 难度分级

`tutorials/index.md` 将 6 个教程分为三级：

| 级别 | 教程 | 难度 |
|------|------|------|
| 入门项目 | getting-started、rest-api | ⭐ - ⭐⭐ |
| 进阶项目 | react-components、automated-testing | ⭐⭐ - ⭐⭐⭐ |
| 高级主题 | system-design、performance-optimization | ⭐⭐⭐⭐ |

难度标注帮助学习者根据自身水平选择起点，降低选择焦虑。

## Vibecoding 教程范式

所有教程遵循"描述需求→AI 生成→理解代码→迭代改进"的四步 Vibecoding 范式，而非传统教程"逐行手写"模式：

1. **描述需求**：用自然语言告诉 AI 要做什么
2. **AI 生成**：AI 生成完整代码
3. **理解代码**：阅读 AI 生成的代码，理解关键逻辑（"看懂再提交"）
4. **迭代改进**：运行验证，发现问题后反馈给 AI 修改

## 入门项目

### getting-started.md：天气查询页面（⭐）

- **技术栈**：纯 HTML + CSS + JavaScript
- **外部 API**：OpenWeatherMap API
- **步骤**：描述需求 → 看懂代码 → 填入 API Key 运行 → 迭代改进
- **目标**：体验最基础的 AI 辅助开发流程，无需框架知识

### rest-api.md：Node.js + Express 任务管理 API（⭐⭐）

- **技术栈**：Node.js + Express
- **功能**：CRUD 操作（GET/POST/PUT/DELETE /tasks）
- **步骤**：生成项目骨架 → 逐个实现路由 → 加入请求校验 → 整理为 MVC 结构
- **目标**：学习后端 API 开发，理解从骨架到架构的递进

## 进阶项目

### react-components.md：React + TypeScript TodoList（⭐⭐）

- **技术栈**：React + TypeScript（create-react-app --template typescript）
- **功能**：TodoList 应用
- **步骤**：生成 TodoList 组件 → 拆分为 TodoInput/TodoItem/TodoList 三个子组件 → 加 localStorage 持久化
- **特色**：提供完整代码参考，强调组件拆分思维

### automated-testing.md：自动化测试（⭐⭐⭐）

- **前置**：基于 REST API 教程项目
- **技术栈**：Jest + supertest
- **步骤**：AI 生成测试用例 → 运行并修复 → 覆盖更多场景
- **延伸**：指导配置 GitHub Actions CI
- **目标**：建立测试意识，学习 AI 辅助测试编写

## 高级主题

### system-design.md：短链服务设计（⭐⭐⭐⭐）

- **案例**：类 bit.ly 的短链服务
- **步骤**：从模糊需求开始（让 AI 提问）→ 估算规模（日活 100 万/短链保留 3 年）→ 设计数据模型（PostgreSQL/Base62 编码/索引）→ 讨论关键决策点并实现核心路径
- **目标**：学习系统设计思维，理解从需求到实现的完整决策链

### performance-optimization.md：性能优化（⭐⭐⭐⭐）

- **核心原则**："先测量再优化"
- **覆盖范围**：
  - 前端：React 重渲染、长列表、打包体积
  - 后端：数据库慢查询、N+1 问题、缓存
- **工作流**：测量 → 定位 → 优化 → 验证 → 提交（五步）
- **目标**：建立数据驱动的优化思维，避免盲目优化

## 学习路径建议

建议的学习顺序：

1. 先完成 Guide 部分（建立 Vibecoding 理念）
2. getting-started（体验 AI 开发流程）
3. rest-api（后端基础）
4. react-components（前端组件化）
5. automated-testing（测试实践）
6. 根据兴趣选择 system-design 或 performance-optimization（高级主题）

## 相关链接

- [Guide 基础教程](03-guide-content.md)
- [Trae Learning 学习站简介](00-introduction.md)
- [VitePress 站点架构](01-vitepress-setup.md)
- [添加新教程文档示例](../examples/add-tutorial.md)
