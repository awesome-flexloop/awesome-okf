---
type: concept
title: 静态部署与全栈部署：选型决策与云端构建环境
description: 用一张决策表区分 meoo deploy 的两种形态——CDN 静态发布与 --runtime image 全栈云端构建；覆盖适配框架、后端逻辑归属、典型命令，以及全栈云端构建镜像的完整版本矩阵、监听约定与 setup/start 脚本约束
tags: [meoo, miaowu, cli, deployment, cdn, fullstack, runtime]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
sources:
  - id: cli
    resource: https://docs.meoo.com/features/cli
    title: Meoo CLI 使用指南
---

# 静态部署与全栈部署：选型决策与云端构建环境

## 1. 核心决策：项目有没有「服务端进程」

`meoo deploy` 有两种形态，分水岭只有一个问题：**运行时是否需要常驻的服务端进程？** 源页 FAQ 给出的官方对比（F-021）整理如下：

| 对比项 | 静态部署 | 全栈应用部署 |
|---|---|---|
| 适合项目 | React/Vue/Taro SPA、个人主页、活动页、纯前端工具 | Next.js SSR、Nuxt SSR、Express、FastAPI、Django、Spring Boot、Go HTTP 服务 |
| 是否有服务端进程 | 没有 | 有 |
| 发布方式 | 构建前端产物并发布到 CDN | 上传源码，云端构建并运行服务 |
| 后端逻辑 | 使用 Meoo Cloud / Edge Functions | 可以保留项目自带服务端 |
| 典型命令 | `meoo deploy` | 首次 `meoo deploy --runtime image`，后续可直接 `meoo deploy` |

选型速查：

- 产物是一堆 HTML/JS/CSS、刷新由前端路由处理、数据靠外部 API → **静态**；
- 有 SSR 渲染、有自己监听端口的 HTTP 服务、有服务端框架启动命令 → **全栈**。

对 Agent 表达时不要让它猜。源页给了标准补充话术（F-017，逐字）：

```text
这个项目需要服务端进程，请使用全栈应用部署。
```

## 2. 两条路径各自意味着什么

**静态路径**：CLI 构建前端产物并发布到 CDN，终端输出可分享链接（F-015）。不需要注册登录、不存数据的纯静态页**不用开通云服务，也不消耗云服务额度**（F-023）。需要数据库/登录/存储时，后端能力改用 Meoo Cloud / Edge Functions 承接（F-021），产品功能侧的说明见同组束 [miaowu-product-guide](../../miaowu-product-guide/index.md)。

**全栈路径**：上传源码到 Meoo 云端，在官方构建镜像里构建并运行服务，允许保留项目原有服务端架构（F-021）。第一次必须显式带 `--runtime image`（F-022，逐字）：

```bash
meoo deploy --runtime image
```

首跑之后，后续部署直接 `meoo deploy` 即可（F-022）。

**不需要自己写 Dockerfile，也不需要本机装 Docker**（F-026）——告诉 Agent 项目有服务端进程后，Agent 会补齐部署所需配置并调用 CLI 完成云端构建。

## 3. 全栈云端构建环境（版本矩阵）

云端构建/运行在 Meoo 提供的 Linux 容器中，规格固定（F-024，逐项逐字）：

| 类别 | 版本/路径 |
|---|---|
| OS | Linux，构建/运行目录 `/code` |
| Java | OpenJDK 21 |
| Node.js | 24.15.0 |
| npm | 11.13.0 |
| pnpm | 10.33.3 |
| Yarn | 1.22.22 |
| Python | 3.13 |
| Go | 1.26.0 |
| 常用工具 | `git`、`curl`、`wget`、`unzip`、`rsync`、`build-essential`、`pkg-config` |

> 版本口径提醒：这个 24.15.0 是**云端镜像内**的版本，与本机装 CLI 要求的 Node.js 20+（F-005）、集成运行环境的 Node.js 18+（F-046）是三件不同的事，见 [verification.md](../references/verification.md) 核验项二。

## 4. 全栈运行约束（照做才能启动）

四条硬约束（F-025）：

1. **监听地址必须是** `0.0.0.0:${PORT:-9000}`——不能只绑 `127.0.0.1`，也不要把端口写死（平台通过 `PORT` 注入，缺省回退 9000）；
2. `scripts/setup.sh` 在**远端构建时**执行（装依赖、做构建的入口）；
3. `scripts/start.sh` 在**容器启动时**执行（启动服务的入口）；
4. **本地文件存储不持久**——容器会冷启动/重建，需要持久化的数据走云数据库或外部服务。

> 洞察（运维型）：`setup.sh` 与 `start.sh` 的阶段分离等价于 build 期与 run 期分离；把「装依赖」误放进 `start.sh` 会让每次冷启动都变慢甚至失败，把「启动服务」误放进 `setup.sh` 则服务根本不会常驻。配合「本地文件不持久」，可迁移模式是：**容器内一切皆可弃，状态全部外置**。

## 5. 额度边界

全栈项目数受套餐限制，源页在「限时免费体验」条件下给出的数字为（F-027）⚠️ dated：

| 套餐 | 可部署全栈项目数 |
|---|---|
| Free | 1 个 |
| Pro | 4 个 |
| MAX | 8 个 |

额度不足时可到 `https://docs.meoo.com/pricing` 查套餐，或到 `https://meoo.com` 删除不用的项目/实例释放资源（F-027）。「限时免费」意味着该数字可能随时调整，正式规划前以官方页最新值为准。

## 6. 老项目迁移与路径切换

- 以前写好的项目可以搬上来：纯前端走静态、带服务端走全栈；**迁移前先备份代码**，再让 Agent 检查项目类型、列出改造点并执行部署（F-028）。
- 如果不想用 Meoo 托管，而是部署到自己的阿里云账号（ECS/RDS/SLB、账单自付），那是另一条 `meoo aliyun deploy` 路径，见 [05](05-aliyun-byoc-deploy.md)。

## 7. 坑点与边界

- **误判形态是最大坑**：有服务端却走静态部署，服务不会运行；纯前端误走全栈，会背上不必要的构建复杂度。用 F-017 话术消除歧义。
- **绑 localhost 导致外部不可达**：必须 `0.0.0.0` 开头（F-025）。
- **把文件传容器本地当存储**：冷启动/重建即丢失（F-025）。
- **首跑漏掉 `--runtime image`**：首次全栈部署的必带参数（F-022）。
- **本地预览与部署是两件独立的事**：可反复本地验证后再上线（F-018），工作流见 [04](04-local-agent-workflow.md)。

## 8. 延伸阅读

- [04 本地 Agent 协作工作流](04-local-agent-workflow.md)
- [05 自有阿里云 BYOC 部署](05-aliyun-byoc-deploy.md)
- 端到端命令流见 [examples/01](../examples/01-static-and-fullstack-deploy.md)
