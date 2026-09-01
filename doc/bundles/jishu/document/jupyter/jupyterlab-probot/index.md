---
okf_version: "0.2"
type: "bundle"
bundle: jupyterlab-probot
title: jupyterlab-probot
description: JupyterLab 团队的 Probot GitHub App，提供自动标签、Binder 链接、CI 管理等维护自动化功能
source: https://github.com/jupyterlab/jupyterlab-probot
version: "2.0.0"
---

# jupyterlab-probot

> 一个 [Probot](https://github.com/probot/probot) 应用，用于 JupyterLab 相关仓库的维护自动化。

**jupyterlab-probot** 是 JupyterLab 团队开发的 GitHub App，基于 Probot 框架构建，帮助维护者自动化处理日常 GitHub 运维任务。

## 核心功能

| 功能 | 触发事件 | 说明 |
|------|---------|------|
| 🔖 自动标签 | `issues.opened` / `pull_request.opened` | 根据 Issue/PR 标题自动添加标签（如 "status:Need Triage"、"new packages"） |
| 🔗 Binder 链接 | `pull_request.opened` | 在 PR 上自动评论，提供 Binder 在线预览链接 |
| 🚫 CI 重复取消 | `workflow_run.requested` | 取消同一 PR 上已有的重复 Workflow Run，节省 CI 资源 |
| 🔄 CI 重启命令 | `issue_comment.created` | 评论 `@jupyterlab-probot please restart ci` 即可重启失败的 CI |

## Bundle 结构

```
jupyterlab-probot/
├── index.md              ← 本文件（Bundle 首页）
├── log.md                ← 生成日志与版本记录
├── concepts/             ← 概念文档
│   ├── index.md          ← 概念索引
│   ├── 00-introduction.md
│   ├── 01-getting-started.md
│   ├── 02-probot-architecture.md
│   ├── 03-config-system.md
│   ├── 04-event-handlers.md
│   └── 05-testing-deployment.md
├── examples/             ← 示例文档
│   ├── index.md          ← 示例索引
│   ├── 01-local-setup.md
│   └── 02-custom-config.md
└── references/           ← 参考文档
    ├── index.md          ← 参考索引
    ├── index-ts-source.md
    └── config-schema-source.md
```

## 快速导航

- 📚 **概念学习**：从 [concepts/](concepts/index.md) 开始，按编号顺序阅读
- 🛠️ **动手实践**：查看 [examples/](examples/index.md) 中的实操指南
- 📖 **源码参考**：深入 [references/](references/index.md) 阅读逐行注释的源码分析

## 快速开始

```bash
# 安装依赖
npm install

# 运行测试
npm test

# 启动 Bot（需配置 .env）
npm start
```

详细说明请阅读 [快速上手](concepts/01-getting-started.md)。

## 技术栈

- **框架**：Probot ^12.3.1
- **语言**：TypeScript
- **配置验证**：AJV ^8.6.2（JSON Schema）
- **测试**：Jest + nock（HTTP 请求录制/回放）
- **部署**：Glitch / Docker / Node.js 服务器

## 许可证

BSD-3-Clause（与 Jupyter 生态一致）


```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
