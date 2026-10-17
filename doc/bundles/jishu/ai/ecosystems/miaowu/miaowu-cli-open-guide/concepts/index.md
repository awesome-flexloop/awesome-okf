---
type: concept
title: concepts 索引
description: miaowu-cli-open-guide bundle 概念文档导航——开放平台总览、个人 CLI 路径（定位/安装/部署/工作流）、阿里云 BYOC 与团队集成共 7 篇
tags: [meoo, miaowu, cli, open-api]
---

# concepts/ 索引

本目录存放秒悟 CLI 部署与开放平台集成的教程化概念页，共 7 篇，按「总览 → 个人路径 → BYOC → 团队路径」组织。

## 文档列表

| 文档 | 说明 |
|------|------|
| [00-open-platform-overview.md](00-open-platform-overview.md) | 开放平台总览：四能力域、三身份模式、三功能流程与五条接入红线 |
| [01-cli-positioning.md](01-cli-positioning.md) | CLI 定位：本地 Agent 接管云端工作、场景人群、与网页端/API 的分工 |
| [02-cli-install-login.md](02-cli-install-login.md) | 个人安装：Node 20+ 前置、自动话术/手动 npm、浏览器设备授权与 `meoo login` |
| [03-deploy-static-vs-fullstack.md](03-deploy-static-vs-fullstack.md) | 静态 vs 全栈部署决策、`--runtime image`、云端构建版本矩阵与运行约束 |
| [04-local-agent-workflow.md](04-local-agent-workflow.md) | 本地 Agent 协作四拍：建项→localhost:3015 预览→CDN 部署→同步云端，含 FAQ 坑点 |
| [05-aliyun-byoc-deploy.md](05-aliyun-byoc-deploy.md) | 自有阿里云 BYOC：ROS 编排、RAM 六权限、先询价后部署、update/status/delete/rollback |
| [06-team-skill-cli-integration.md](06-team-skill-cli-integration.md) | 团队 Skill+CLI：AK/SK 签 token、MEOO_TOKEN 注入、项目命令序列与 CI 直发 |

## 阅读建议

- **只想把自己的项目快速上线**：01 → 02 → 04，部署形态拿不准时加读 03；
- **要部署到公司/自己的阿里云账号**：加读 05；
- **要为团队 Agent/CI 做平台集成**：00 → 06，并配合 [examples/03](../examples/03-team-token-ci-publish.md)；
- 所有命令与数字的逐字出处在 [references/source-ledger.md](../references/source-ledger.md)（F-001–F-074），时效与冲突判定在 [references/verification.md](../references/verification.md)。

```{toctree}
:hidden:
:maxdepth: 2

00-open-platform-overview
01-cli-positioning
02-cli-install-login
03-deploy-static-vs-fullstack
04-local-agent-workflow
05-aliyun-byoc-deploy
06-team-skill-cli-integration
```
