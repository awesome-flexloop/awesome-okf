---
okf_version: "0.2"
type: "concept"
title: "pr-triage-board-bot 简介"
description: "PR分类看板机器人是什么、设计原则、核心能力、项目信息与在开源协作中的价值"
tags: [introduction, overview, github-action, project-board, pr-triage, jupyter]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: readme
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/README.md"
    title: "README.md"
  - id: package-json
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/package.json"
    title: "package.json"
  - id: license
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/LICENSE"
    title: "LICENSE"
  - id: main-source
    resource: /references/main-source.md
    title: "入口与CLI源码"
---

# pr-triage-board-bot 简介

## 什么是 pr-triage-board-bot

pr-triage-board-bot 是一个 GitHub Action 机器人，用于自动管理 GitHub Project 看板上的 PR（Pull Request）分类字段。它周期性地扫描组织内的开放PR，自动填充一组预定义的分类字段（作者类型、创建时间、代码变更规模、维护者参与度、CI状态、合并冲突、审批状态），帮助维护者快速识别需要关注的PR [F-001]。

典型的使用场景包括 JupyterHub、JupyterLab、GeoJupyter 等开源组织的PR分类看板——这些组织拥有数十个仓库和数百个开放PR，人工跟踪每个PR的状态成本极高。

## 设计原则

项目遵循三条核心设计原则：

1. **字段所有权原则**：机器人"拥有"Project字段的schema和字段值——人类对这些字段的手动修改会在下次运行时被机器人覆盖。但机器人不拥有看板的视图（Views/Tabs），视图由人类自定义，机器人不会修改 [F-066][F-067]。

2. **确定性计算原则**：所有字段值的计算必须是**确定性的**（deterministic）——只要PR内容和作者信息不变，多次运行的结果完全一致。这保证了幂等性和可预测性 [F-068]。

3. **组织无关原则**：机器人不内置任何特定组织的知识，所有组织相关信息通过参数传入，可以跨组织复用 [F-069]。

## 核心能力

机器人自动填充7个PR分类字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| Author Kind | 单选 | Bot / Maintainer / First Time Contributor / Early Contributor / Seasoned Contributor |
| Opened At | 日期 | PR创建日期（UTC日期，不含时间） |
| Total Lines Changed | 数字 | 增删行数总和（additions + deletions） |
| Maintainer Engagement | 单选 | 无维护者参与 / 单一维护者参与 / 多维护者参与 |
| CI Status | 单选 | 测试通过 / 测试失败 |
| Merge Conflicts | 单选 | 有合并冲突 / 无合并冲突 |
| Approval Status | 单选 | 请求修改 / 维护者批准 |

## 项目信息

| 属性 | 值 |
|------|-----|
| 包名 | `pr-triage-board-bot` |
| 版本 | 0.1.0 |
| 描述 | "A bot to manage a GitHub Project board for PR triage" |
| 许可证 | BSD-3-Clause（版权所有 Yuvi, 2025）|
| 作者 | yuvipanda |
| 运行时 | Node.js >23.0.0（ES Modules）|
| 语言 | TypeScript（SWC编译，target es2024）|
| 致谢 | 由 2i2c.org 初始构建，捐赠给 Jupyter 组织 |

## 技术栈

```
运行时：  Node.js 23+ (ESM)
语言：    TypeScript 5.9
编译：    SWC 1.13（快编译）+ tsc --noEmit（类型检查）
CLI框架： commander 14
API客户端：@octokit/core 7 + @octokit/auth-app 8 + @octokit/plugin-paginate-graphql 6 + @octokit/plugin-throttling 11
缓存：    memoize 10
```

## 与 Jupyter 生态的关系

pr-triage-board-bot 是 Jupyter 生态的**协作运维工具**，而非核心库：

- **使用者**：JupyterHub、JupyterLab、GeoJupyter 等组织用它自动维护PR看板
- **定位**：在 nbformat（Notebook格式）、jupyter-client（内核通信）、jupyter-notebook（应用层）、jupyter-docker-stacks（部署层）等核心技术组件之外，解决的是开源社区的协作效率问题
- **运行方式**：作为 GitHub Action 定时运行（默认每小时一次），也可手动触发或本地脚本运行

## 安装与部署

本项目不是npm包，而是作为 GitHub Action 直接引用：

```yaml
- uses: yuvipanda/pr-triage-board-bot@main
  with:
    organization: 'your-org'
    project-number: '1'
    gh-app-id: '12345'
    gh-app-installation-id: '67890'
    gh-app-private-key: ${{ secrets.GH_APP_PRIVATE_KEY }}
```

本地脚本运行方式见[5分钟快速上手](01-getting-started.md)。

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [架构总览](02-architecture-overview.md)
