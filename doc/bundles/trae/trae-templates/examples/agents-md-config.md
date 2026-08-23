---
type: Example
title: AGENTS.md 配置示例
description: 展示如何在项目根目录创建 AGENTS.md 文件作为 AI 开发契约，定义项目特定的 AI 行为规则，适合不使用完整 superpowers 工作流但需要 AI 行为约束的项目。
tags: [trae-templates, example, agents-md, ai-contract, configuration]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/templates-source.md
    title: Trae Templates 源码信源
---

## 示例目标

为一个 Next.js + FastAPI 全栈项目创建 AGENTS.md 文件，定义 AI Agent 在该项目中的行为规则。这比使用完整 superpowers-trae-init 更轻量，适合不需要全套 TDD 工作流但需要 AI 行为约束的项目。

## 最简 AGENTS.md 示例

以下是一个放在项目根目录的 `AGENTS.md` 文件示例：

```markdown
# Project AI Agent Contract

## Project Overview

这是一个全栈博客应用：
- 前端：Next.js 14 (App Router) + TypeScript + Tailwind CSS
- 后端：FastAPI + Python 3.10+
- 数据库：PostgreSQL（通过 docker-compose 启动）
- 包管理：pnpm（前端）、pip + venv（后端）

## Build & Run Commands

### Frontend (`frontend/`)
- Install: `cd frontend && pnpm install`
- Dev: `cd frontend && pnpm dev` (localhost:3000)
- Build: `cd frontend && pnpm build`
- Lint: `cd frontend && pnpm lint`
- Test: `cd frontend && pnpm test`

### Backend (`backend/`)
- Setup venv: `cd backend && python -m venv venv && source venv/bin/activate`
- Install: `cd backend && pip install -r requirements.txt`
- Dev: `cd backend && uvicorn app.main:app --reload` (localhost:8000)
- API Docs: http://localhost:8000/docs

### Database
- Start: `docker-compose up -d`
- Stop: `docker-compose down`

## Code Rules

1. **TypeScript**：前端必须使用 TypeScript，禁止使用 `any` 类型（除非标注 `// eslint-disable-next-line`）
2. **Python 类型提示**：后端所有函数必须添加类型提示
3. **组件规范**：React 组件使用函数组件 + Hooks，文件命名 PascalCase
4. **API 路由**：后端 API 按 RESTful 规范设计，所有端点返回 JSON
5. **错误处理**：前端使用 try/catch 包裹异步请求，后端使用 HTTP 异常
6. **环境变量**：敏感配置使用 .env 文件，禁止硬编码密钥
7. **提交规范**：commit message 遵循 Conventional Commits（feat/fix/docs/style/refactor/test/chore）

## Project Structure

```
.
├── frontend/          # Next.js 前端
│   ├── app/          # App Router 页面
│   ├── components/   # React 组件
│   └── lib/          # 工具函数和 API 客户端
├── backend/          # FastAPI 后端
│   └── app/
│       ├── main.py   # FastAPI 入口
│       ├── routers/  # API 路由
│       └── models/   # 数据模型
├── docker-compose.yml
└── AGENTS.md
```

## Do NOT

- 不要在未运行 lint/test 的情况下宣布代码完成
- 不要修改 docker-compose.yml 中的数据库密码
- 不要在 API 响应中返回用户密码字段
- 不要使用 `var` 声明变量
- 不要跳过错误处理
```

## AGENTS.md 编写要点

### 1. 项目概述

告诉 AI 项目是什么、使用什么技术栈。这帮助 AI 理解上下文，选择正确的工具和模式。

### 2. 构建和运行命令

**这是最重要的部分**——AI 必须知道如何启动项目、运行测试、构建产物。明确列出：
- 安装命令
- 开发服务器启动命令和端口
- 构建命令
- 测试命令
- Lint 命令

### 3. 代码规范

列出项目特定的代码规则，例如：
- 语言版本和特性限制
- 命名约定
- 文件组织规则
- 错误处理模式
- 提交规范

### 4. 项目结构

给出目录结构树，帮助 AI 理解代码应该放在哪里。

### 5. 禁止事项

明确列出"不要做什么"，防止 AI 犯常见错误。

## 配合 .trae/ 目录使用

AGENTS.md 可以与 `.trae/rules/` 下的模块化规则文件配合：

```
project-root/
├── AGENTS.md                # 主契约文件（入口）
├── .trae/
│   └── rules/
│       ├── frontend.md      # 前端特定规则
│       ├── backend.md       # 后端特定规则
│       └── testing.md       # 测试规范
├── frontend/
├── backend/
└── docker-compose.yml
```

在 AGENTS.md 中引用这些规则文件：

```markdown
## Additional Rules

- 前端开发遵循 [.trae/rules/frontend.md](.trae/rules/frontend.md)
- 后端开发遵循 [.trae/rules/backend.md](.trae/rules/backend.md)
- 测试编写遵循 [.trae/rules/testing.md](.trae/rules/testing.md)
```

## 简单项目的超简 AGENTS.md

对于非常简单的项目（如单文件脚本），AGENTS.md 可以极简：

```markdown
# AI Contract

## Commands
- Install: `pip install -r requirements.txt`
- Run: `python main.py`
- Test: `python -m pytest`

## Rules
- 使用 Python 类型提示
- 所有函数必须有 docstring
- 不要在 main.py 之外添加业务逻辑
```

## 与 superpowers-trae-init 的关系

| 维度 | 简单 AGENTS.md | superpowers-trae-init |
|------|---------------|----------------------|
| **复杂度** | 低（单文件） | 高（.trae/ 目录 + 25+ 技能） |
| **适用项目** | 小型项目、脚本、原型 | 中大型项目、团队协作 |
| **核心约束** | 项目特定规则 | 4 条铁律 + TDD 工作流 |
| **技能集** | 无（使用全局技能） | 25+ 项目级技能 |
| **配置方式** | 单个 Markdown 文件 | 复制 .trae/ 目录 + Core Memory |
| **灵活性** | 完全自定义 | 基于 superpowers 框架调整 |

**选择建议**：
- 快速原型/小项目 → 简单 AGENTS.md
- 团队项目/中大型应用 → superpowers-trae-init
- 可以先从 AGENTS.md 开始，需要时升级到 superpowers

## AGENTS.md 放置位置

| 位置 | 作用范围 | 适用场景 |
|------|----------|----------|
| 项目根目录 `AGENTS.md` | 整个项目 | 推荐：主契约文件 |
| `.trae/rules/*.md` | 项目级模块化规则 | 复杂项目的规则拆分 |
| 子目录 `AGENTS.md` | 特定子目录 | monorepo 中不同子项目有不同规范 |

## 验证 AGENTS.md 生效

创建 AGENTS.md 后，在 TRAE 中新开会话，测试：

1. 让 AI 在前端创建组件 → 检查是否使用 TypeScript 和函数组件
2. 让 AI 添加 API 端点 → 检查是否遵循 RESTful 规范和类型提示
3. 让 AI 运行代码 → 检查是否使用正确的启动命令
4. 故意让 AI 做违反规则的事 → 检查 AI 是否拒绝或警告

## 常见问题

**Q: AGENTS.md 和 README.md 有什么区别？**
A: README.md 是给人类看的项目说明，AGENTS.md 是给 AI Agent 看的行为契约。README 回答"这是什么项目"，AGENTS.md 回答"AI 应该怎么在这个项目中工作"。

**Q: 可以在 AGENTS.md 中要求 AI 使用特定 Skill 吗？**
A: 可以。例如"遇到 Bug 必须调用 systematic-debugging 技能"或"提交代码前使用 git-commit-generator 生成 commit message"。

**Q: AGENTS.md 需要提交到版本控制吗？**
A: 是的。AGENTS.md 是项目配置的一部分，应该随代码一起提交，确保所有团队成员使用相同的 AI 规则。

**Q: 中文还是英文？**
A: 建议与团队沟通语言一致。中文团队用中文写，国际团队用英文。也可以双语。

## 相关概念

- [AGENTS.md 开发契约](/concepts/07-agents-contract.md)
- [工具与 DevOps 模板](/concepts/06-tools-devops-templates.md)

## 相关内容

- [源码信源索引](/references/templates-source.md)
- [使用 superpowers-trae-init 初始化环境](/examples/use-superpowers-init.md)
