---
type: Concept
title: "MemoryPanel/Hub：团队记忆操作台与 ACL 管控面"
description: "team-memory-control 面板以无状态透明代理承载 16 个 POST RPC action，并以可见性四值与两级角色落地多租户 ACL。"
tags: [tencentdb-agent-memory, concept, memory-panel, memory-hub, acl, oauth2]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-core-code
    resource: /references/01-source-code-map.md
    title: TencentDB-Agent-Memory 源码地图
  - id: s-deploy
    resource: /references/04-deploy-install.md
    title: 部署形态与一键安装
---

# MemoryPanel/Hub：团队记忆操作台与 ACL 管控面

## 本篇看点

- 面板包名 `team-memory-control` 0.1.0，对外是 `/api/v1/meta/*` 前缀的 POST RPC 面，且 meta-api 为无状态透明代理（F-247、F-248、F-249、F-250）。
- Hub 发布镜像 `agentmemory/memory-hub` 同时打包 Panel 与 Knowledge Service，一个容器暴露面板与知识两个端口（F-254、F-255）。
- ACL 由「可见性四值 + 两级角色 + Agent Loadout」构成，`private` 资产连团队管理员都不可见（F-046、F-047、F-048）。
- 2.0.2-beta.1 起兼容标准 OAuth2，登录身份与 `user_key` 自动打通（F-262）。本篇覆盖 F-247 ~ F-262，并结合 F-046/F-047 讲解 ACL，呼应洞察五。

## 1. Hub 镜像：Panel + Knowledge 一体分发

CHANGELOG 明确 Hub 镜像 `agentmemory/memory-hub` 同时包含 Panel 与 Knowledge Service（F-254）。容器名与端口、卷映射由 `start-memory-hub.sh` 固定（F-255）：

| 项 | 值 |
|---|---|
| 容器名 | `tdai-memory-hub` |
| 面板端口 | `${PANEL_PORT}:8125` |
| 知识端口 | `${KNOWLEDGE_PORT}:8424` |
| 卷 | `${PANEL_VOLUME}:/data/knowledge` |

```text
浏览器 / 管理员
   │  HTTP
   ▼
tdai-memory-hub  ── Panel（容器内 8125，POST RPC 管控面）
                 └─ Knowledge Service（宿主 8424 → 容器 8421，F-023）
                        │ REMOTE_INSTANCE_URL=http://memory-core:8420（F-256）
                        ▼
                    tdai-memory-core
```

## 2. 包清单、入口与 API 前缀

`MemoryPanel/package.json` 声明包名 `team-memory-control`、版本 0.1.0（F-247）：

| 类别 | 内容 | 事实 |
|---|---|---|
| 依赖 | hono、@hono/node-server、dotenv、jose、ulid、zod | F-247 |
| 脚本 | dev、build、start、test、openapi 生成 | F-247 |
| 入口 | `src/panel/index.ts`：加载配置、构建依赖与 Hono app | F-248 |
| API 前缀 | 日志声明为 `/api/v1/meta/*` | F-248 |
| API 说明文档 | 仓库根 `panel-api-doc.md` | F-261 |
| 本地镜像 | `docker/local/Dockerfile.local` | F-260 |

## 3. POST RPC：16 个 action 与无状态透明代理

API 为 POST RPC 风格；`analytics-actions.ts` 对接内核 Analytics，列出 config、spaces、`session-init/*`、`tool-calls/*`、`usage/*`、`usage-raw/list` 等 16 个 action，并区分 GET/POST；ClickHouse 未配置时返回 503（F-249）。

| 维度 | 事实 |
|---|---|
| 风格 | POST RPC（F-249） |
| action 总数 | 16 个（含 config、spaces、session-init/*、tool-calls/*、usage/*、usage-raw/list）（F-249） |
| 方法区分 | GET / POST 分别注册（F-249） |
| Analytics 缺失 | ClickHouse 未配置 → 503（F-249） |
| meta-api 形态 | 无状态透明代理（stateless）（F-250） |

OpenAPI 描述文件 `docs/api/meta-api.openapi.yaml` 由 `scripts/generate-meta-openapi.ts` 生成（F-252）。

## 4. 与 Core / Knowledge 的协作变量

| 变量 / 注入项 | 说明 | 事实 |
|---|---|---|
| `KNOWLEDGE_SERVICE_URL` | Knowledge 服务地址 | F-251 |
| `KNOWLEDGE_AUTH_TOKEN` | Knowledge 鉴权令牌 | F-251 |
| `KNOWLEDGE_TIMEOUT_MS` | Knowledge 调用超时 | F-251 |
| LLM binding 同步变量 | `.env.example` 中与 LLM 绑定同步相关 | F-251 |
| `REMOTE_INSTANCE_URL` | Hub 启动时注入 `http://memory-core:8420` | F-256 |
| 启动必填变量 | `MEMORY_HUB_IMAGE`、`PANEL_PORT`、`KNOWLEDGE_PORT`、`PANEL_VOLUME`、LLM 参数、`KNOWLEDGE_PUBLIC_BASE_URL` | F-257 |

## 5. ACL 模型：可见性四值 × 两级角色 × Loadout

可见性包含四个取值（F-046）：

| 取值 | 含义 |
|---|---|
| `private` | Owner 只读，团队管理员不可见 |
| `team` | 团队内可见 |
| `restricted` | User / Role / Agent ACL 控制 |
| `agent` | 同团队 Agent 定向装配 |

角色分两层（F-047）：全局 System Admin；团队内 Admin / Member；Owner 自动获得管理权。Agent Loadout 机制支持给不同 Agent 绑定不同资产、调整优先级与使用方式（F-048）。

```text
资产（记忆 / Skill / Wiki / CodeGraph）
   │ 可见性判定（F-046）
   ├─ private   → 仅 Owner（管理员亦不可见）
   ├─ team      → 团队成员
   ├─ restricted→ User / Role / Agent 三类 ACL 主体
   └─ agent     → 同团队指定 Agent（经 Loadout 装配，F-048）
身份：System Admin（全局） │ Admin / Member（团队内） │ Owner 自动管理权（F-047）
```

洞察五指出，多租户隔离是写进存储格式的，而非查询时补条件；面板侧的可见性管理与存储侧隔离列、行级 scope 校验共同构成不可绕过的 ACL 链（F-046、F-047）。

## 6. 管理功能与面板演进

Panel 提供团队 / Agent / 资产（Owner / 版本 / 状态 / 可见性）统一管理、Agent Loadout 配置、Wiki + CodeGraph 工坊、中英文切换（F-258）。2.0.1 面板还新增（F-259）：

| 演进项 | 事实 |
|---|---|
| 登录页点阵波纹动效 | F-259 |
| 团队编辑 / 删除入口整合进团队切换器 | F-259 |
| 管理员创建账号可自定义 User_Key | F-259 |
| 资产 ID 展示与一键复制 | F-259 |

2.0.1 另支持对话记忆搜索：跨会话语义与关键字检索、按权限控制可见范围、对单层记忆直接覆盖修改（F-016）。

## 7. OAuth2：企业身份接入

2.0.2-beta.1 起 Panel 登录侧兼容标准 OAuth2，可对接企业内部 OA/SSO，登录身份与 `user_key` 自动打通（F-262）；仓库提供对接骨架与 `authorize` / `token` / `userinfo` 端点配置项（F-011）。这与 Proxy 侧 `user_key` 换 `user_id` 的鉴权链路（F-233）配合，使企业身份与记忆资产可见性联动。

## 8. 工程脚本

`MemoryPanel/scripts/` 含授权端到端与安全类脚本（F-253）：

| 脚本 | 用途 |
|---|---|
| `e2e-knowledge-authz.sh` | Knowledge 授权端到端 |
| `e2e-skill-authz.sh` | Skill 授权端到端 |
| `secret-scan.sh` | 密钥扫描 |
| `install-git-hooks.sh` | Git hooks 安装 |
| `mock-memory-server.ts` | Mock 内存服务 |

## 延伸阅读

- [TencentDB Agent Memory 核心洞察 · 洞察五](../spec/insights.md)
- [TencentDB Agent Memory 事实清单 F-247~F-262](../spec/facts.md)
- [部署形态与一键安装](../references/04-deploy-install.md)
- [09 · MemoryProxy 代理与注入层](09-memory-proxy.md)
- [11 · 部署拓扑：三容器、卷与端口](11-deploy-topology.md)
