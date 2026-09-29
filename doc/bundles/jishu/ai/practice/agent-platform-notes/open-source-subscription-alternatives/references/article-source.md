---
type: Reference
title: "文章事实与官方补充"
description: "五个开源项目的定位、安装路径、成本主张与限制；原文数字均保留证据等级"
tags: [开源替代, 订阅成本, AI工具, 事实核验]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
status: flagged
stale_after: 2026-11-30
sources:
  - { id: article, resource: "https://mp.weixin.qq.com/s/RLsYjpbzUxdQU4U6ylTkTw" }
  - { id: orca, resource: "https://github.com/stablyai/orca" }
  - { id: gev, resource: "https://github.com/bilawalsidhu/gods-eye-view" }
  - { id: hyperframes, resource: "https://github.com/heygen-com/hyperframes" }
  - { id: scrapling, resource: "https://scrapling.readthedocs.io/en/latest/" }
  - { id: openseo, resource: "https://github.com/every-app/open-seo" }
---

# 文章事实与官方补充

## 信源距离

微信文章是第三方项目盘点；项目仓库和官方文档用于补充机制、许可证与安装路径；第三方价格页只用于识别价格口径，不升级为市场基准。文章正文约 11,887 字符（去重后），没有把图片或视频演示当作已复现实验。

## 双份事实登记

事实编号与 `.trae/specs/okf-wiki-ecosystem/open-source-subscription-alternatives-okf-wiki/facts.md` 一致。

| 编号 | 声明 | 来源 | 证据边界 |
| --- | --- | --- | --- |
| F-001 | 文章标题、作者、日期如规格事实表所记。 | article | 页面元信息已读 |
| F-002 | 文章覆盖五个项目。 | article | 结构事实 |
| F-003 | Orca 以 worktree 编排多个 CLI Agent。 | article、orca | 官方仓库与第三方说明支持 |
| F-004 | Orca 使用用户已有订阅，底层调用成本仍存在。 | article、orca | 未核算实际账单 |
| F-005 | Orca 支持 Design Mode、diff、SSH、移动端与 CLI。 | article、orca | 功能随版本变化 |
| F-006 | Orca 仓库与 MIT 许可证。 | article、orca | 以仓库当前文件为准 |
| F-007 | God's Eye View 聚合公开信号到 3D 地球。 | article、gev | 数据源与覆盖需逐层核验 |
| F-008 | God's Eye View 免密钥基础体验与付费服务并存。 | article、gev | 免密钥不等于零成本 |
| F-009 | God's Eye View 含延迟、模拟和估计图层。 | article、gev | 不能外推为实时情报 |
| F-010 | God's Eye View 仓库与许可证口径。 | article、gev | 许可证以仓库为准 |
| F-011 | HyperFrames 用 HTML 渲染 MP4。 | article、hyperframes | 官方定位支持 |
| F-012 | HyperFrames CLI 包含 init/preview/lint/render。 | article、hyperframes | 命令需按版本复核 |
| F-013 | HyperFrames 支持多种动画适配器。 | article、hyperframes | 具体清单会变化 |
| F-014 | HyperFrames Apache-2.0 与本地渲染路径。 | article、hyperframes | 云渲染另计费 |
| F-015 | HyperFrames Node 22+、FFmpeg、0.8.x 口径。 | article、hyperframes | 时效快照 |
| F-016 | Scrapling 是自适应 Python 抓取框架。 | article、scrapling | 官方文档支持 |
| F-017 | Scrapling 用 auto_save/adaptive 应对页面改版。 | article、scrapling | 误匹配率未测 |
| F-018 | Scrapling 提供多类 Fetcher 与 Spider。 | article、scrapling | 不能承诺绕过所有反爬 |
| F-019 | Scrapling 的安装前置与命令。 | article、scrapling | 未在本任务执行 |
| F-020 | Scrapling BSD-3-Clause。 | article、scrapling | 以发行元数据为准 |
| F-021 | OpenSEO 定位为 SEO 套件替代。 | article、openseo | 定位不等于等价 |
| F-022 | OpenSEO 覆盖 SEO 与 AI 可见性工作流。 | article、openseo | 数据深度由上游决定 |
| F-023 | OpenSEO 提供 MCP 与 Agent Skills。 | article、openseo | 客户端支持需复核 |
| F-024 | OpenSEO 依赖 DataForSEO key。 | article、openseo | 数据服务仍收费 |
| F-025 | OpenSEO 支持 Docker/Cloudflare 部署。 | article、openseo | 未在本任务部署 |
| F-026 | OpenSEO 仓库与 MIT 许可证。 | article、openseo | 以仓库当前文件为准 |
| F-027 | 文章给出爬虫 API 约 49 美元/月起。 | article | 单源价格对照 |
| F-028 | 文章给出 SEO 套件约 129–139 美元/月。 | article | 口径、地区和周期未统一 |
| F-029 | 文章给出视频工具 54.99 美元/月。 | article | 未指定产品 |
| F-030 | 文章给出 OpenSEO 10 美元/月加 API 与 28% 加价。 | article、openseo | 需查当前官方计划 |
| F-031 | 开源替代迁移而非消除成本。 | article | 作者总结与本教程抽象 |
| F-032 | 本次未独立复现全部数字、星标和成本。 | process | bundle 维持 flagged |

## 原文与教程的分界

项目机制、命令和成本拆解是基于公开仓库/文档的原创重组；没有把本文的星标、订阅价格或“替代”措辞写成普遍性能、节省或采购结论。
