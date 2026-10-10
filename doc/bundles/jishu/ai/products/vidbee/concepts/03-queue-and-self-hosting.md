---
type: Concept
title: 下载队列、RSS 与自托管边界
status: stable
verified: {by: "process:seven-concepts-v", at: "2026-10-10"}
stale_after: 2026-12-31
source: ../references/article-source.md
sources:
  - {id: facts, resource: "../references/article-source.md"}
  - {id: release-readme, resource: "https://github.com/nexmoe/VidBee/blob/v2.1.0/README.md"}
  - {id: main-readme, resource: "https://github.com/nexmoe/VidBee/blob/feeea6b2b5f451e62774c87c25f3056d583f494f/README.md"}
generated: {by: "process:okf-wiki-agent", at: "2026-10-10"}
---

# 下载队列、RSS 与自托管边界

批量下载、频道和播放列表会把一次任务扩展为持续输入。VidBee 提供队列状态、暂停恢复和重试，以及 RSS 关键词过滤、标签和单独保存规则。[F-020、F-022](../references/article-source.md)

## 先限制输入

RSS 是订阅源提供更新条目的格式，VidBee 用其发现新的下载目标。先准备合法可访问的订阅源，再在当前构建的订阅管理入口添加；具体按钮和轮询设置本包未核验。本节是能力与验收边界说明，不是完整 RSS 配置教程。[F-022](../references/article-source.md)

本教程建议首次 RSS 配置保持手动审核，并使用“只取最新”避免导入历史积压；确认订阅内容、权限和空间后再开启自动下载。原文提出 RSSHub，但本包未验证其集成或源站可用性。[F-022、F-029](../references/article-source.md)

“1000+ 站点支持”表示项目列出的覆盖范围。访问控制、内容变更、区域限制和源站政策仍可能让某个 URL 不可下载；不得把失败的私有页面作为绕过权限的理由。[F-008](../references/article-source.md)

视频容器是文件封装格式，不能单凭 MP4/MKV 选项推定画质、编码器或播放器兼容性。标题、封面、章节和字幕写入都受源信息可用性影响。[F-023、F-024](../references/article-source.md)

## 自托管的已确认入口

发布版 README 包含 `packages/downloader-core`、Fastify API/oRPC/SSE 和 TanStack Start Web 客户端说明。以下命令仅作为官方入口参考，需要在 VidBee 仓库、已具备对应运行环境时使用；本次没有部署。[F-009、F-025](../references/article-source.md)

先获取官方仓库并检出 `v2.1.0`，按该版本 README 准备依赖，再参考下列启动片段。存储说明另绑定 SHA `feeea6b2b5f451e62774c87c25f3056d583f494f`，不能与发布标签无条件混用。这些片段不是完整部署流程；环境版本、依赖安装、卷配置及实际 HTTP 就绪响应都须在目标环境另行验收。

```bash
pnpm run start:web
```

官方仓库还给出：

```bash
docker compose up -d --build
docker compose down
```

示例默认 API 端口 3100、Web 端口 3000；不能据端口号认定服务已就绪。若已有其他容器环境，应先看该环境的部署规范，不直接把 Docker 示例当成已验证的 Podman 配方。

## 文件位于服务器

当前固定 main README 说明下载保存于 `/data/downloads`，`/data/vidbee` 保存 `vidbee.db`、设置、模型等。Web 操作服务端文件系统，想保存到浏览器所在电脑需要相应下载动作。此细节来自开发快照，发布包或旧卷的迁移行为需要再核对。[F-026](../references/article-source.md)

**旧目录条件不可省略：** 若已有 SQLite 位于 `/data/downloads/.vidbee`，继续使用旧目录，直到 `/data/vidbee/vidbee.db` 存在。备份前先确认实际活动数据库路径，不只备份新目录；不要为切换路径随意创建空数据库。[F-026](../references/article-source.md)

本教程建议把媒体与状态数据分别持久化，备份前停止写入或采用一致性备份方案；删除容器不应等于删掉唯一数据副本。对 cookies、凭证和转录限制访问，禁止将管理端口直接暴露到公网后假定已有认证。官方 README 的启动片段不能充当完整安全部署设计。

组织共享或敏感材料部署的准入条件是：明确认证、每用户访问隔离、目录权限、凭证管理与审计责任。**内网部署不等于这些条件已成立。** 本包未核验 VidBee 是否提供完整多租户与审计能力；条件无法证明时，不按企业共享服务批准上线。

资源与恢复验收由部署者负责：分别预算媒体、模型、状态数据和备份容量，设定本环境低空间停采阈值；这是运维要求，不是宣称应用自带阈值功能。启用自动下载前，用非敏感小样本核对停止输入、积压处理及备份恢复，恢复后检查转录、元数据和活动数据库，不能只看容器启动成功。

## 扩展使用边界

浏览器扩展适合接入浏览流程，但官方新指南明确不在扩展中运行本地 ASR；桌面辅助字幕和 Overview 还需要兼容构建。核对版本、连接路径与功能可用性，再决定是否能复用已有桌面安装。[F-036](../references/article-source.md)

新 Transcript/Overview 桌面桥接晚于 v2.1.0，不能假定该正式版支持，转录库本身仍标记 Experimental。[F-036](../references/article-source.md)

可迁移的设计思路是保存已完成转录并允许更换 AI 处理：下次修订摘要时先复用已核对文字，不必重新获取媒体。它是本教程从工作流抽出的建议，实际缓存和重跑能力仍以工具版本为准。
