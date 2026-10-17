---
okf_version: "0.2"
type: bundle
title: 秒悟 CLI 部署与开放平台集成指南
description: 秒悟（Meoo）官方 CLI 与开放平台的中文教程束——本地 Agent 经 meoo cli 接管云端数据库/登录/部署的个人路径、meoo aliyun 自有阿里云 BYOC 路径、团队 AK/SK 签发成员 token 接入 Agent/CI 的集成路径；含 7 篇概念页与 3 条文档级可复现命令流，全部事实回溯 docs.meoo.com 四源 74 条编号事实
tags: [meoo, miaowu, cli, open-api, deployment, byoc, aliyun, hmac, ci, local-agent]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-18T00:00:00+08:00"
status: stable
stale_after: "2027-01-18"
sources:
  - id: cli
    resource: https://docs.meoo.com/features/cli
    title: Meoo CLI 使用指南
  - id: cli-aliyun
    resource: https://docs.meoo.com/features/cli-aliyun
    title: MEOO CLI 进阶：部署到你自己的阿里云账号
  - id: open
    resource: https://docs.meoo.com/open
    title: Meoo 开放平台
  - id: cli-open-guide
    resource: https://docs.meoo.com/open/guides/cli
    title: CLI 开放集成接入
---

# 秒悟 CLI 部署与开放平台集成指南

> **类型**：开发者操作教程（含 `examples/`——3 条文档级可复现命令流，未做运行验证）
> **源站分区**：功能特性 › 应用构建能力（CLI/CLI 进阶）＋ Meoo开放能力（开放平台/接入流程）
> **数据时点**：2026-10-18；平台套餐、集成权益与版本矩阵以 `docs.meoo.com` 最新页面为准（`stale_after` 2027-01-18）

## 本文概要

本束解决一个问题：**怎样不靠秒悟网页控制台，让 Agent 或 CI 完成 Meoo 应用的部署与云资源操作。** 官方文档把答案拆在四个页面里，本束按读者身份重组为三条故事线：

1. **个人开发者路径**——本地 Coding Agent（Claude Code/Codex/Cursor/Qoder 等）装好 meoo cli，浏览器授权后，用对话驱动建库、预览、部署到 CDN 或云端全栈镜像；
2. **自有云 BYOC 路径**——用 `meoo aliyun` 命令族把 ROS 资源栈开进自己的阿里云账号，资源与账单全部自管；
3. **团队集成路径**——接入方在服务端用团队 AK/SK 经 HMAC 签发成员短期 token，注入 `MEOO_TOKEN` 让自有 Agent/CI 使用秒悟能力。

## 读者地图：按身份选路径

| 你是谁 | 阅读顺序 | 关键产物 |
|---|---|---|
| 想把作品变成链接的个人开发者/创作者 | [01](concepts/01-cli-positioning.md) → [02](concepts/02-cli-install-login.md) → [04](concepts/04-local-agent-workflow.md) | 可分享的 CDN 链接 |
| 项目带服务端（SSR/API/后台） | 加读 [03](concepts/03-deploy-static-vs-fullstack.md) | 全栈云端部署 |
| 有合规/自付账单要求，要落自己阿里云 | [05](concepts/05-aliyun-byoc-deploy.md) | 自有账号下的 ECS/RDS/SLB |
| 平台/中台团队，要给自家 Agent 或 CI 接能力 | [00](concepts/00-open-platform-overview.md) → [06](concepts/06-team-skill-cli-integration.md) | token 签发服务 + CI 直发 |
| 只想复制命令照做 | 直接进 [examples/](examples/index.md) | 3 条分阶段命令流 |

## 三个必须先知道的口径

1. **Node.js 有三个版本数字，各管一段**：本机装 CLI 要 Node 20+（F-005）；集成运行环境要 Node 18+（F-046）；全栈云端构建镜像固定 Node 24.15.0（F-024）。不要互相套用。
2. **AK/SK 不是业务凭证**：团队 AK/SK 只能签成员短期 token，不能直调项目/Agent/Release（F-033）；业务调用一律 Bearer Token。
3. **权益有时效条件（⚠️ dated）**：集成权益仅建议开发预发、团队 AK/SK 暂需人工创建、全栈项目数限时免费 Free 1/Pro 4/MAX 8（F-027、F-036、F-037）；完整清单见 [verification.md](references/verification.md)。

## 文档结构

### concepts/ — 概念解析（7 篇）

| 文档 | 主题 |
|------|------|
| [00-open-platform-overview.md](concepts/00-open-platform-overview.md) | 开放平台四能力域、三身份模式、三功能流程、五条接入红线 |
| [01-cli-positioning.md](concepts/01-cli-positioning.md) | CLI 定位：本地 Agent 接管云端工作；场景/人群；与网页端/API 分工 |
| [02-cli-install-login.md](concepts/02-cli-install-login.md) | 个人安装（自动话术/手动 npm）、Node 前置、浏览器设备授权 |
| [03-deploy-static-vs-fullstack.md](concepts/03-deploy-static-vs-fullstack.md) | 静态 vs 全栈决策表、云端构建版本矩阵、监听与脚本约束 |
| [04-local-agent-workflow.md](concepts/04-local-agent-workflow.md) | 对话驱动四拍工作流、localhost:3015、同步云端、FAQ 坑点 |
| [05-aliyun-byoc-deploy.md](concepts/05-aliyun-byoc-deploy.md) | 阿里云 BYOC：ROS 编排、RAM 权限、询价、运维命令族 |
| [06-team-skill-cli-integration.md](concepts/06-team-skill-cli-integration.md) | 团队集成：签 token、装 Skill、注入环境变量、CI 直发、token 生命周期 |

### examples/ — 命令流（3 条，文档级复现）

| 文档 | 内容 |
|------|------|
| [01-static-and-fullstack-deploy.md](examples/01-static-and-fullstack-deploy.md) | 安装→授权→预览→静态/全栈部署→同步 |
| [02-aliyun-byoc.md](examples/02-aliyun-byoc.md) | 配置→检查→询价→部署→运维/清理 |
| [03-team-token-ci-publish.md](examples/03-team-token-ci-publish.md) | 签 token→装 Skill→注入→核验→CI 直发 |

### references/ — 信源登记与核验

| 文档 | 说明 |
|------|------|
| [source-ledger.md](references/source-ledger.md) | F-001–F-074 编号事实（74 条四源分段）+ S1–S4 信源台账 + 放弃核验清单 + 转写噪声登记 |
| [verification.md](references/verification.md) | 13 项 P0 核验：逐字回验、Node 三口径语境、5 条 dated、CLI 两页非重复六重证据 |

## 主题关联

- [miaowu-product-guide](../miaowu-product-guide/index.md)：姊妹束——秒悟**产品功能全景**（Agent 模式、模型、Web/小程序构建、云服务、AI 服务、素材中心、技能与连接器）；本束讲「怎么用命令行/API 部署集成」，两束互补
- [miaowu-meoo-practice-cases](../miaowu-meoo-practice-cases/index.md)：同分组既有束——秒悟实训案例（网页侧 5 步搭建法与 7 个实操场景）
- [miaowu-bounty-plaza](../miaowu-bounty-plaza/index.md)：同分组既有束——AI Builder 共创计划技能索引

## 已知边界

- **文档级复现，无运行验证**：未实际安装、登录、签 token 或开通任何云资源；命令可用性以 2026-10-18 源页文字层为准。
- **深页未覆盖**：HMAC 签名细节（`/open/team-integration`）、API 字段目录、OAuth、全链路/仅部署/仅生成三指南、通用协议与安全页均在抓取清单外，仅登记为延伸阅读，不产生无来源事实。
- **截图信息缺失**：授权页、阿里云配置成功例等以截图承载，本束只转写文字层，不脑补界面路径。
- **厂商单源**：74 条事实均来自 `docs.meoo.com` 自身页面；时效条目已逐条标 ⚠️ dated。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
examples/index
log
```
