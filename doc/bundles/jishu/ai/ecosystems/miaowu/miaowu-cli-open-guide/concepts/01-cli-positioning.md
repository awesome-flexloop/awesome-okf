---
type: concept
title: Meoo CLI 的定位：让本地 Agent 接管云端工作
description: 理解 meoo cli 在「本地 Agent—Meoo 云」之间的承上启下角色——支持哪些 Agent、覆盖哪些云端工作、四类适用场景与三类人群，以及它与网页端、开放平台 API 三者的分工边界
tags: [meoo, miaowu, cli, local-agent, vibe-coding]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
sources:
  - id: cli
    resource: https://docs.meoo.com/features/cli
    title: Meoo CLI 使用指南
  - id: cli-open-guide
    resource: https://docs.meoo.com/open/guides/cli
    title: CLI 开放集成接入
---

# Meoo CLI 的定位：让本地 Agent 接管云端工作

## 1. 一句话定位

meoo cli 是秒悟官方命令行工具，职责是让本地 agent 在写完前端代码后，**直接接管「数据库、用户登录、文件存储、百炼模型服务、部署上线」的所有云端工作**（F-001）。

这句话里有两个关键词：

- **本地 agent**：智能仍在你日常使用的 Coding Agent 里，CLI 只是它手中的工具；
- **云端工作**：Agent 原本够不到的「资源开通与发布」环节，由 CLI 桥接到 Meoo 云。

> 洞察（架构型）：传统 BaaS 把云能力做成控制台和 SDK，开发者要自己写胶水代码；Meoo CLI 把云能力做成**可被 Agent 调用的命令面**——人对 Agent 说意图，Agent 选择命令，CLI 完成云端动作。交互入口从「控制台表单」变成「对话」，但底层仍是同一套云资源。

## 2. 何时用：四类场景与三类人群

| 你的情况 | 对应场景（F-003） |
|---|---|
| 从 0 到 1 搭项目，要接数据库、上线、出分享链接 | 新项目一体化交付 |
| 本地已有静态页面，想同步到云端协作 | 静态页面同步 |
| 本地已有全栈项目，想保留自己的服务端架构上线 | 全栈项目平移 |
| 本地已有 SSR、API 服务、后台系统，想一键发布 | 服务型系统发布 |

三类目标读者（F-004）：

1. 有全栈交付需求的泛开发者；
2. vibe coding 爱好者——想把作品变成链接分享的创作者；
3. 设计师、产品经理、运营——快速产出落地页、H5 长图、活动页并与团队协同打磨。

前置判断很简单：**只要成果需要一个「能分享的线上链接」或「云端数据库/登录/存储」，CLI 就派得上用场。** 反过来，纯本地脚本、不需要发布的工具不在目标场景内。

## 3. 支持哪些 Agent

源页口径为「具备 Coding 能力的本地 agent」，列举六款（F-002）：Claude Code、Codex、Cursor、Qoder、Qoderwork、Cline，并以「等主流 agent」收尾，说明这不是封闭清单——任何能在终端执行命令、能读取安装话术的 Agent 理论上都可驱动。

团队接入场景下，官方 Skill 安装器会自动检测五款 Agent 的配置目录：Claude Code、Cursor、Trae、CodeBuddy、Qoder（F-051，见 [06](06-team-skill-cli-integration.md)）。两份清单措辞略有差异，以源页各自口径为准。

## 4. 它和网页端、开放平台 API 的分工

| 通道 | 谁在用 | 擅长什么 | 边界 |
|---|---|---|---|
| Meoo 网页端 | 人直接操作 | 可视化构建、二次修改、云服务后台 | 本地开发期间不要用它发布覆盖本地代码（F-019） |
| Meoo CLI（本束） | 本地/团队 Agent | 本地代码 → 云资源开通 → 部署发布的自动化动作 | 不替代网页端的可视化管理 |
| Open API | 接入方自研系统 | 把生成/云/发布能力编进自有产品与 CI | 需自行处理身份、签名、工具封装（F-043） |

三者关系还有一条「同步」通道：本地代码通过 `meoo sandbox push` / 「帮我把代码同步到meoo云端」进入 Meoo 云后，才能在网页端二次修改并使用扩容量、大模型、自定义域名、发布范围控制等平台能力（F-016、F-055）。

## 5. 两种分发形态，别装错

| 形态 | 安装物 | 面向 | 出处 |
|---|---|---|---|
| 公网 npm 包 | `npm install -g @aliyun-meoo/cli`（F-008） | 个人开发者，浏览器授权登录 | S1 |
| 接入版 tgz 包 | `npm install -g "/path/to/meoo-cli.tgz"`（F-050） | 团队 Agent/CI，用 `MEOO_TOKEN` 注入身份 | S3 |

个人故事线从 [02 安装与登录](02-cli-install-login.md) 开始；团队故事线直接跳到 [06](06-team-skill-cli-integration.md)。

## 6. 坑点与边界

- **CLI 不替你决定部署形态**：静态还是全栈要由人（或对 Agent 的话术）明确；项目有服务端进程时补一句「这个项目需要服务端进程，请使用全栈应用部署」（F-017），否则可能被当成静态应用处理。
- **本地与网页双轨编辑有覆盖风险**：正确顺序是先同步、再在网页改（F-019），详见 [04](04-local-agent-workflow.md)。
- **云服务开通不是即时生效**：命令成功只代表申请发出，数据库实例就绪有数分钟延迟（F-020）。
- **进阶路径另有入口**：要部署到自己的阿里云账号（BYOC）不是本页默认托管路径，见 [05](05-aliyun-byoc-deploy.md)。

## 7. 延伸阅读

- 下一步：[02 安装与浏览器授权登录](02-cli-install-login.md)
- 部署形态决策：[03 静态部署与全栈部署](03-deploy-static-vs-fullstack.md)
- 开放平台全景：[00 开放平台总览](00-open-platform-overview.md)
