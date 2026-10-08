---
type: Concept
title: "MemoryProxy：协议不变的 LLM 代理与记忆注入层"
description: "MemoryProxy 以 OpenAI/Anthropic 双协议加 8 个客户端适配器承接会话引导、记忆注入与 mem 指令，Agent 侧零插件接入。"
tags: [tencentdb-agent-memory, concept, memory-proxy, llm-proxy, injection]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-core-code
    resource: /references/01-source-code-map.md
    title: TencentDB-Agent-Memory 源码地图
  - id: s-proxy-doc
    resource: /references/03-api-references.md
    title: MemoryProxy v3 管理接口文档
---

# MemoryProxy：协议不变的 LLM 代理与记忆注入层

## 本篇看点

- Proxy 是「重业务侧车」而非透明管道：双协议（OpenAI/Anthropic）+ 8 个客户端适配器，把 N×M 插件矩阵改写成「N 个协议适配器 × 1 套记忆业务内核」（F-219、F-220）。
- 它在转发链路上完成首轮会话引导、逐轮边界标记注入、会话内 `mem` 指令、频控与计费上报，Agent 侧无需插件、Hook 或 MCP（F-232、F-224、F-234、F-240、F-245）。
- 记忆读写全部走 memory-bridge 白名单回源 Core，Proxy 自身只持有会话、绑定与 hook 缓存等状态（F-222、F-223、F-237）。
- 本篇覆盖事实 F-217 ~ F-246，并呼应洞察一「以『协议不变』替代插件生态」。

## 1. 定位：Agent 零安装，差异收敛到 Proxy

官方接入方式被描述为「协议不变，把 Agent 的 base URL 指向 Proxy，不需要插件、Hook 或 MCP」（F-026、F-245）；Claude Code 只需设置 `ANTHROPIC_BASE_URL=http://127.0.0.1:8096/claude-code/default` 与 `ANTHROPIC_AUTH_TOKEN`（F-029）。新增客户端靠 Proxy 侧升级获得，例如 2.0.1 新增的 OpenCode、dsh、Codex CLI、WorkBuddy（F-013）。

```text
coding agent ──(OpenAI / Anthropic 协议，含 SSE 流式)──▶ MemoryProxy :8096
                                                  │ 适配器：会话/鉴权/注入/mem 指令
                                                  ▼
                                 MemoryCore :8420（白名单回源读写）
```

## 2. 包、启动与监听

| 项 | 值 | 事实 |
|---|---|---|
| 包名 / 版本 | `context-proxy` / `0.1.0` | F-217 |
| 关键依赖 | `hono@^4.7.10` | F-217 |
| 启动命令 | `node --import tsx/esm src/index.ts` | F-217 |
| 默认监听 | `0.0.0.0:8096` | F-218 |
| 配置文件形态 | `config.example.yaml`（解析于 `src/config.ts`） | F-218 |

## 3. 双协议与 8 个客户端适配器

Proxy 同时讲两套 LLM 协议并支持 SSE 流式（F-219，实现于 `src/handler.ts`、`anthropicHandler.ts`、`directHandler.ts`）：

| 协议面 | 路径 | 事实 |
|---|---|---|
| OpenAI 兼容 | `/v1/chat/completions` | F-219 |
| Anthropic 兼容 | `/v1/messages` | F-219 |

`src/agent-adapters/`（含 `index.ts` 共 10 个文件）工厂注册 8 个适配器（F-220）：

| # | 适配器 | # | 适配器 |
|---|---|---|---|
| 1 | `claude-code` | 5 | `dsh` |
| 2 | `codebuddy` | 6 | `opencode` |
| 3 | `codex` | 7 | `pi` |
| 4 | `workbuddy` | 8 | `default` |

`AgentAdapter` 接口含 `classifyRequest`、`extractUserText` 两个方法（F-220）。

## 4. 路由面：对外五组路由

`src/server.ts` 注册的路由（F-221）：

| 路由 | 用途（据命名与相关模块） | 事实 |
|---|---|---|
| `/health` | 健康检查 | F-221 |
| `/whoami` | 身份查询 | F-221 |
| `/direct/*` | 直连旁路 | F-221 |
| `/skill-bridge/*` | Skill 桥接 | F-221 |
| `/memory-bridge/*` | 记忆读写桥 | F-221 |

memory-bridge 白名单 6 个子路径（F-222，`src/memory/memory-bridge.ts`）与回源 Core 的 6 个端点（F-223，`src/tdai/client.ts`、`src/skill/core-client.ts`）如下（两列各列 6 项，不表示一一对应）：

| # | memory-bridge 白名单子路径（F-222） | 回源 Core 端点（F-223） |
|---|---|---|
| 1 | `atomic/search` | `/v3/skill/conversation/add`（Skill 写回） |
| 2 | `atomic/query` | `/v3/meta/auth/verify`（鉴权核验） |
| 3 | `conversation/search` | `/v3/atomic/search`（L1 原子记忆检索） |
| 4 | `conversation/query` | `/v3/conversation/search`（会话检索） |
| 5 | `scenario/ls` | `/v3/scenario/ls`（场景列表） |
| 6 | `scenario/read` | `/v3/scenario/read`（场景读取） |

## 5. 注入体系：6 个边界标记、8 个注入器、六模块管线

注入内容以 6 个边界标记原文包裹（F-224，`src/injection/injectors/`）：

| # | 边界标记原文 | # | 边界标记原文 |
|---|---|---|---|
| 1 | `<tdai_recalled_l1_memories>` | 4 | `<l2_scene_index>` |
| 2 | `<tdai_profile_memory>` | 5 | `<tdai_memory_tools>` |
| 3 | `<l3_core_memory>` | 6 | `<memory-tools-guide>` |

8 个注入器（F-225）：

| 类别 | 注入器 |
|---|---|
| Core 记忆 | `tdai-l1-recall`、`tdai-profile-memory`、`tdai-fixed-asset` |
| 工具挂载 | `tdai-tools`、`skill-tools`、`knowledge-tools` |
| Skill / 反思 | `skill`、`asset-reflection` |

注入管线由 registry、provider、pipeline、observer、context、prewarm 六个模块组成（F-226，`src/injection/`）；序列化按协议分 `openai.ts` 与 `anthropic.ts` 两套适配器，Agent 画像含 codebuddy、workbuddy、pi、claude-code 四套（F-227）。

```text
请求 → registry 选定注入器 → provider 回源取数 → pipeline 在边界标记内拼装
     → openai.ts / anthropic.ts 序列化（observer/prewarm/context 协作）→ 转发上游
```

## 6. 环境变量与 v3 管理接口

4 个关键环境变量（F-228，`src/config.ts` 与部署配置）：

| 变量 | 说明 |
|---|---|
| `TDAI_MEMORY_SYSTEM_USER_ID` | 系统用户 ID |
| `TDAI_MEMORY_SYSTEM_USER_KEY` | 系统用户 Key |
| `TDAI_PROXY_ADMIN_API_KEY` | Proxy 管理接口 Key |
| `PROXY_DB_PATH` | SQLite 路径，Docker 默认 `/data/tdai-memory-proxy/proxy.db` |

v3 管理接口共 6 个，登记于 `v3-api-memoryproxy-doc.md`（章节：公共约定 / 接口目录 / 实例销毁 / 频控 / Session）（F-229）：

| # | 接口 | # | 接口 |
|---|---|---|---|
| 1 | `/v3/instance/proxy-destroy` | 4 | `/v3/admin/rate-limits`（PUT） |
| 2 | `/v3/admin/rate-limits`（GET） | 5 | `/v3/admin/rate-limits`（DELETE） |
| 3 | `/v3/session/refresh-cache` | 6 | `/v3/session/force-archive-skill` |

频控实现于 `src/rate-limit/`，含 `guard.ts`、`usage.ts`、`redis-store.ts`（F-230）。

## 7. 会话体系、鉴权链路与 mem 指令

`src/session/` 共 13 个文件，含 store、registrar、session-key、preset、context-injector、client-capabilities、restore-space-id 等，并按客户端分子目录 `claude-code/`、`codebuddy/`、`codex/`、`workbuddy/`、`dsh/`、`opencode/`（F-231）。

| 机制 | 说明 | 事实 |
|---|---|---|
| sessionInit 首轮引导 | 通过 AskUserQuestion 让用户选 team/agent/task，Proxy 持久化绑定 | F-232 |
| 鉴权换发 | `x-tdai-user-key` → 内核 `/v3/meta/auth/verify` 换 `user_id`，按用户维度控制资产可见性（`src/auth.ts`、`src/meta/client.ts`） | F-233 |

会话内 `mem` 指令实现于 `src/mem-command/`，含 parser、pre-intercept、pending-store、task-draft-generator、response-builder 五个模块，共 6 个命令（F-234）：

| # | 命令 | # | 命令 |
|---|---|---|---|
| 1 | `create-task` | 4 | `session-reset` |
| 2 | `update-task` | 5 | `help` |
| 3 | `sync` | 6 | `create-skill` |

## 8. Skill 桥接、存储抽象与本地状态库

Skill 桥接模块 `src/skill/` 含 skill-bridge、handler-glue、core-client、normalize-conversation、version-pin-repo、kv-version-pin-repo（F-235）。

存储抽象 `src/storage/` 含三种存储实现 sqlite-storage、fs-storage、cos-storage，配套 memory-storage、factory、per-key-mutex、key-utils 与 cos-types（F-236）。

`src/db/`（11 个文件）含 sessionRepo、binding-repo、hookCacheRepo，并提供 redis/kv 双实现与 schema（F-237）；`src/tdai/` 子模块含 recorder、pending-writes、identity、capabilities、client、types（F-238）。

## 9. 客户端特殊处理与旁路

| 模块 | 职责 | 事实 |
|---|---|---|
| `workbuddyHandler.ts` / `codexHandler.ts` / `auxiliaryHandler.ts` | 特有请求处理器 | F-239 |
| `extraction-gate.ts`、`guard-adapter.ts` | 请求门控 | F-239 |
| dsh aux 短路 | compaction / title-gen 辅助请求短路，另有 CLI headless bypass | F-241 |
| `turnSeq.ts`、`trace-archive.ts`、`instance-upstream-cache.ts` | 轮次序号、追踪归档、上游缓存 | F-242 |
| `systemUser.ts`、`systemUserPassthrough.ts` | 系统用户身份透传 | F-243 |

## 10. 可观测、计费与分发

可观测/计费集成含 `pricing.ts`、`credit-reporter.ts`、`clickhouse.ts`、`langfuse.ts`、`opik.ts`、`judge-client.ts`、`requestLog.ts`（F-240，位于 `src/` 根与 `src/report/`）。

| 项 | 内容 | 事实 |
|---|---|---|
| Dockerfile | EXPOSE 8096，使用 tini entrypoint | F-244 |
| README 原文要求 | coding agent 的 upstream 指向 proxy，path 中带 spaceId；强调「无需插件/hook/MCP」 | F-245 |
| scripts | `setup-claude-code.sh`、`proxy.sh`、`qa/task-e2e.sh`、`qa/codex-init.sh` | F-246 |

## 延伸阅读

- [TencentDB Agent Memory 核心洞察 · 洞察一](../spec/insights.md)
- [TencentDB Agent Memory 事实清单 F-217~F-246](../spec/facts.md)
- [MemoryProxy v3 管理接口文档](../references/03-api-references.md)
- [10 · MemoryPanel/Hub 团队操作台与 ACL](10-panel-acl.md)
- [11 · 部署拓扑：三容器、卷与端口](11-deploy-topology.md)
