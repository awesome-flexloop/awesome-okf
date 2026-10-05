---
type: Concept
title: "TencentDB Agent Memory 总览：定位、四件架构与部署形态"
description: "一篇看懂产品标语与技术三问、四组件与端口口径、三套版本号、PersonaMem 基准以及 Standalone/Service 两形态。"
tags: [tencentdb-agent-memory, concept, overview, architecture, deployment]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-core-code
    resource: /references/01-source-code-map.md
    title: TencentDB-Agent-Memory 源码地图
  - id: s-readme
    resource: /references/02-readme-changelog.md
    title: README 与 CHANGELOG 信源
---

# TencentDB Agent Memory 总览：定位、四件架构与部署形态

> **本篇看点**：TencentDB Agent Memory 以「让 Agent 沉淀经验，让人专注创造」为标语，把记忆问题归纳为「什么值得留下、谁可以使用、下一次怎样少拿但拿对」技术三问（F-019）。本篇并列登记端口与版本号的多套口径，梳理 MemoryCore、MemoryKnowledge、MemoryPanel/Hub、MemoryProxy 四件架构，以及 Standalone/Service 两种部署形态与镜像分发方式，全部事实取自学习截面 commit 8b86874（F-001）。

## 学习截面与开源背景

- 仓库远程地址为 `git@github.com:TencentCloud/TencentDB-Agent-Memory.git`，学习截面 HEAD 为 commit `8b86874a2daea49e3ff0fb53d699203146c5c77d`（提交时间 2026-09-29），位于分支 `feat/server_team`，采集时工作树干净（F-001）。
- 该截面对应的 `git describe` 为 `v2.0.2-beta.3-7-g8b86874`，即 tag v2.0.2-beta.3 之后第 7 个提交（F-002）。
- 仓库以 MIT License 开源，根目录提供 LICENSE、CONTRIBUTING_CN、INSTALL_CN、README_CN、CHANGELOG、ROADMAP_CN 等中文文档（F-003）。
- 仓库为 pnpm monorepo 形态，顶层有六个组件目录（F-004）：

| 目录 | 用途 |
|---|---|
| MemoryCore | 记忆核心（F-004、F-022） |
| MemoryKnowledge | 知识引擎（F-004、F-022） |
| MemoryPanel | 团队记忆操作台（F-004、F-022） |
| MemoryProxy | LLM 代理（F-004、F-022） |
| sdk | SDK 目录（F-004） |
| deploy | 部署脚本目录（F-004） |

- 运行环境要求 Node.js ≥ 22.16，README 标注的 npm 包名为 `@tencentdb-agent-memory/memory-tencentdb`（F-020）。
- ⚠️ 口径并列：CHANGELOG 的克隆命令写的是 `https://github.com/Tencent/TencentDB-Agent-Memory.git`，实际 remote 组织为 `TencentCloud`，两处组织名不同，学习截面以实际 remote 为准（F-018）。

## 产品定位：一句标语与技术三问

README_CN 的标语是「让 Agent 沉淀经验，让人专注创造」（F-019）。其技术三问为「什么值得留下、谁可以使用、下一次怎样少拿但拿对」，分别对应记忆抽取、权限可见性与召回预算三类工程问题（F-019）。CHANGELOG 声明其覆盖 MemoryCore、MemoryPanel、MemoryKnowledge、MemoryProxy、SDK 全部开源模块（F-005）。

## 四件架构与端口口径

系统由四个组件构成（F-022）：

| 组件 | 职责 | 端口口径 |
|---|---|---|
| MemoryCore | 记忆核心 | 端口 8420（F-022） |
| MemoryKnowledge | 知识引擎 | config 默认端口 8421；docker 部署映射宿主 8424 → 容器 8421（F-023） |
| MemoryPanel/Hub | 团队记忆操作台 | 容器内监听 8125；`.env.example` 本地裸跑默认写 8123（F-024） |
| MemoryProxy | LLM 代理 | 端口 8096（F-022） |

⚠️ 端口口径必须并列理解，不能单边取值（F-023、F-024）：

```text
MemoryKnowledge：8421 = 容器内监听口径（src/config.ts 默认）
                 8424 = docker 宿主映射口径（README 中两种说法并存）
MemoryPanel：    8123 = 本地裸跑默认口径（MemoryPanel/.env.example）
                 8125 = 容器内监听 / 部署映射口径（start-memory-hub.sh）
```

从接入视角看，四件的数据流为：Agent 只改 base URL 指向 Proxy，由 Proxy 回源记忆核心，客户端侧零安装（F-026、F-029）：

```text
coding Agent ──base URL 改指──▶ MemoryProxy（8096）──▶ MemoryCore（8420）
              不需要插件、Hook 或 MCP（F-026）
```

## 三套版本口径并存

产品版本、npm 版本、git tag 是三套互不一致的口径，需并列登记，不做单边取舍（F-021）：

| 口径 | 值 | 信源 |
|---|---|---|
| 产品宣传版本 | v2.0.0 | README（F-021） |
| npm 包 | `@tencentdb-agent-memory/memory-tencentdb-v2`，版本 `1.0.2-beta.1` | MemoryCore/package.json（F-021） |
| git 最新 tag | v2.0.2-beta.3 | 学习截面 git tag（F-021） |

补充两条版本史：首个公开版本为 2.0.0-beta.1（2026-07-21），SemVer 直接从 2.0.0-beta.1 起步（F-007）；该版本起 npm 包名迁移到 `-v2` 后缀（`memory-tencentdb-v2`、`memory-sdk-ts-v2`），而 Docker 镜像 tag 独立于 npm 版本，当次镜像发布为 `:1.0.0-beta.1`（F-008）。CHANGELOG 遵循 Keep a Changelog 格式与语义化版本，共登记 5 个版本（F-006）：

| 版本 | 发布日期 |
|---|---|
| 2.0.2-beta.1 | 2026-09-07（F-006） |
| 2.0.1 | 2026-08-25（F-006） |
| 2.0.1-beta.1 | 2026-08-13（F-006） |
| 2.0.0 | 2026-08-03（F-006） |
| 2.0.0-beta.1 | 2026-07-21（F-006） |

## PersonaMem Benchmark

README 给出的基准为 PersonaMem：不挂载记忆时得分 48%，启用记忆后 76%，相对提升 +59%（F-025）。该数字用于说明记忆层对 Agent 表现的增益，引用时须注明口径来自 README（F-025）。

## Standalone 与 Service 两种部署形态

| 维度 | Standalone | Service |
|---|---|---|
| 存储与状态 | SQLite / 本地文件 / 进程内状态 | TCVDB / COS / Redis（F-030） |
| 目标场景 | 单机使用 | K8s 多副本与多租户（F-030） |
| K8s 要点 | — | ConfigMap/Secret 注入环境变量，Deployment 设置 `TDAI_DEPLOY_MODE=service`，Service 暴露 3100 端口（F-031） |
| Docker 示例 | `docker run` 注入 LLM 参数、映射 8420:8420、挂载 tdai-data 卷，镜像 `agentmemory/hermes-memory:latest`（F-032） | — |

另有一个试验后端口径：2.0.2-beta.1 新增 MongoDB 存储后端（试验特性、可选、默认关闭），默认存储仍为 sqlite，一键入口为 `./start-all-mongo.sh`，未配置 `MONGODB_ENDPOINT` 时脚本拉起 `mongodb-atlas-local` 容器（F-009）；启用方式是在 .env 设置 `MEMORY_CORE_STORE_MODE=mongodb`，后续启动保持该后端、不静默回退 sqlite，且切换后端不迁移已有数据（F-010）。

## 镜像分发与一键部署

三个发布镜像均为多架构 linux/amd64 + linux/arm64，发布在 Docker Hub 公开可拉（F-033）：

| 镜像 | 角色 |
|---|---|
| `agentmemory/memory-core:latest` | 记忆核心（F-033） |
| `agentmemory/memory-hub:latest` | 团队操作台（F-033） |
| `agentmemory/memory-proxy:latest` | LLM 代理（F-033） |

部署脚本另存在腾讯内网镜像源 `mirrors.tencent.com/memory-team-control/*`（F-034）。一键部署流程为 `cp .env.example .env`、填入两组 LLM 参数、执行 `./start-all.sh`（F-035）；start-all 首次启动自动 init-admin、生成 `sk-mem-...` 并落盘 `.admin-key`，自检 `/v3/meta/auth/verify` 后打印可复制的 claude 启动命令（F-035）。重置时 `stop-all.sh --purge` 会清除 volume 与 admin key（F-036）。

## Proxy 零插件接入口径

Proxy 的接入方式被描述为「协议不变，把 Agent 的 base URL 指向 Proxy，不需要插件、Hook 或 MCP」（F-026）。客户端数量存在口径差：README 列出 7 个客户端（DeepSeek Harness、Claude Code、Codex、CodeBuddy、WorkBuddy、Hermes、OpenClaw，不含 OpenCode），INSTALL_CN 列出 8 类，OpenCode 为 2.0.1 起新增（F-027、F-028、F-013）。以 Claude Code 为例，接入需设置 `ANTHROPIC_BASE_URL=http://127.0.0.1:8096/claude-code/default` 与 `ANTHROPIC_AUTH_TOKEN`，并配置 `--model`（F-029）。

## 近期版本能力增量（择要）

| 版本 | 增量 |
|---|---|
| 2.0.2-beta.1 | 面板登录侧兼容标准 OAuth2，可对接企业内部 OA/SSO，仓库提供对接骨架与 `authorize`/`token`/`userinfo` 端点配置项（F-011）；数据分析与可观测性默认关闭，开启需 Proxy/Knowledge/Core 三个服务分别配置 ClickHouse，Panel 通过配置发现接口判断是否启用（F-012） |
| 2.0.1 | 新增 OpenCode、DeepSeek Harness（dsh）、Codex CLI、WorkBuddy 四款客户端接入（F-013）；支持会话中途一键重置绑定（换团队/Agent/任务）与对话内创建/更新任务（F-014）；冷启动创建团队或用户即自动生成默认 Agent，支持自定义模板与从 IDE 一键导入资产（F-015）；面板新增跨会话语义与关键字检索、按权限控制可见范围、单层记忆直接覆盖修改（F-016）；启动脚本支持交互式配置，自动预检 LLM 通路与端口占用（F-017） |

## 延伸阅读

- 下一篇：[01-four-layer-memory.md](01-four-layer-memory.md)——L0–L3 四层记忆模型与四类资产
- 信源：[源码地图](../references/01-source-code-map.md)、[README 与 CHANGELOG](../references/02-readme-changelog.md)、[部署安装](../references/04-deploy-install.md)
