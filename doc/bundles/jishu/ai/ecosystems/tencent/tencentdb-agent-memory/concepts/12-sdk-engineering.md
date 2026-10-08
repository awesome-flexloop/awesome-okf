---
type: Concept
title: "官方 SDK 与工程配套：TypeScript / Python 双语言与 CI"
description: "TS 与 Python 两套官方 SDK 的顶级导出均强制 team/agent/user 三元组，并由 PR CI、模板与测试脚本构成工程闭环。"
tags: [tencentdb-agent-memory, concept, sdk, typescript, python, ci]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-core-code
    resource: /references/01-source-code-map.md
    title: TencentDB-Agent-Memory 源码地图
  - id: s-sdk-ts
    resource: /references/05-sdk-ci.md
    title: 官方 TypeScript SDK
  - id: s-sdk-py
    resource: /references/05-sdk-ci.md
    title: 官方 Python SDK
  - id: s-ci
    resource: /references/05-sdk-ci.md
    title: PR 持续集成工作流
---

# 官方 SDK 与工程配套：TypeScript / Python 双语言与 CI

## 本篇看点

- 两套官方 SDK：TypeScript 包 `@tencentdb-agent-memory/memory-sdk-ts-v2`，Python 安装名 `tencentdb-agent-memory-sdk-python`（F-287、F-292）。
- 顶级导出均为 v3 严格隔离版本，客户端构造必须给齐 endpoint、apiKey、serviceId、teamId、agentId、userId 六参数（F-289、F-290、F-293）。
- Python 顶层保留 v2 兼容 `MemoryClient`，v3 子包另导出 `MemoryClient`、`MetadataClient`、`SkillClient`（F-293）。
- 工程配套含 PR CI、三类 issue 模板、vitest 测试与 tsdown 打包配置（F-297 ~ F-300）。本篇呼应洞察五「SDK 顶级强制三元组」。

## 1. TypeScript SDK

| 项 | 内容 | 事实 |
|---|---|---|
| 包名 | `@tencentdb-agent-memory/memory-sdk-ts-v2` | F-287 |
| v3 模块 | `src/v3/` 下 12 个文件 | F-288 |
| 顶级导出 | v3 严格 isolation 版本 | F-289 |
| 兼容别名 | `.../v2/v3` 子路径保留为向后兼容别名 | F-289 |
| 随附文档 | README / README_CN、CHANGELOG、`AGENT_GUIDE.typescript.zh-CN.md` | F-291 |

`src/v3/` 共 12 个文件，事实清单登记的文件/目录名为（F-288）：

| 类别 | 文件 |
|---|---|
| 核心 | client、http、types、index |
| Skill | skill-client、skill-types |
| Metadata | metadata-client、metadata-types |
| Memory Prompt | memory-prompt-client/types |
| Generation Log | memory-generation-log-client/types |

v3 客户端构造六参数为 endpoint、apiKey、serviceId、teamId、agentId、userId，其中后三项即 v3 严格 isolation 必填三元组（F-290）。示意片段（import 路径取自 F-287，参数名取自 F-290）：

```ts
// 顶级导出即 v3 严格 isolation 客户端；旧代码可用 .../v2/v3 别名（F-289）
import { MemoryClient } from '@tencentdb-agent-memory/memory-sdk-ts-v2';

const memory = new MemoryClient({
  endpoint: 'http://127.0.0.1:8420', // MemoryCore 端口（F-022）
  apiKey: 'sk-mem-...',              // admin key 前缀（F-035）
  serviceId: '<your-service-id>',
  teamId: '<your-team-id>',
  agentId: '<your-agent-id>',
  userId: '<your-user-id>',
});
```

> 说明：TS 侧客户端对应 `src/v3/` 的 client 模块（F-288）；`MemoryClient` 类名为 Python v3 子包明确导出的同名类（F-293），此处按双 SDK 一致的构造六参数（F-290）示意。

## 2. Python SDK

| 项 | 内容 | 事实 |
|---|---|---|
| 安装名 | `tencentdb-agent-memory-sdk-python` | F-292 |
| 包名 | `tencentdb_agent_memory` | F-293 |
| 顶层默认导出 | v2 兼容 `MemoryClient` | F-293 |
| v3 子包导出 | `MemoryClient`、`MetadataClient`、`SkillClient` | F-293 |
| 随附文档 | `AGENT_GUIDE.python.zh-CN.md` 与双语 README / CHANGELOG | F-296 |

v3 子包五个模块（F-294）：`skill_client`、`metadata_client`、`memory_prompt`、`memory_generation_log`、`client`。通用层含四个基础模块（F-295）：`errors`、`cos`、`_v3_http`、`_http`。

```python
# 新代码直接用 v3 子包；顶层 MemoryClient 为 v2 兼容（F-293）
from tencentdb_agent_memory.v3 import MemoryClient, MetadataClient, SkillClient

memory = MemoryClient(
    endpoint='http://127.0.0.1:8420',  # MemoryCore 端口（F-022）
    apiKey='sk-mem-...',               # admin key 前缀（F-035）
    serviceId='<your-service-id>',
    teamId='<your-team-id>',
    agentId='<your-agent-id>',
    userId='<your-user-id>',
)
```

构造参数名与 TS 一致，均为 endpoint、apiKey、serviceId、teamId、agentId、userId（F-290）；`MetadataClient`、`SkillClient` 为 v3 子包另两个导出类（F-293）。

## 3. 为什么顶级导出强制三元组

v3 契约把 team_id + agent_id + user_id 升为强制三元组，缺失即 422，三项可来自 body 或 `x-tdai-team-id` / `x-tdai-agent-id` / `x-tdai-user-id` 请求头（F-153）。SDK 在顶级导出处固定三元组，使隔离在客户端初始化时就写死，而非每个调用点手传（洞察五）：

```text
应用初始化（一次）
  endpoint / apiKey / serviceId
  teamId + agentId + userId   ← 构造期强制（F-290）
        │
        ▼
SDK 每次请求自动携带三元组（body 或 x-tdai-* 头，F-153）
        │
        ▼
Core 校验：缺任一项 → 422（F-153）
```

旧代码的迁移路径也被保留：TS 走 `.../v2/v3` 子路径别名（F-289），Python 顶层继续提供 v2 兼容 `MemoryClient`（F-293）。

## 4. CI、模板、测试与打包工具

| 类别 | 内容 | 事实 |
|---|---|---|
| CI | `.github/workflows/pr-ci.yml`，PR 时触发 | F-297 |
| issue 模板 | `bug_report`、`feature_request`、`question` 三类 | F-298 |
| PR 模板 | `PULL_REQUEST_TEMPLATE.md` | F-298 |
| MemoryCore 测试 | 使用 vitest（`vitest.config.ts`） | F-299 |
| MemoryProxy 测试 | opencode 相关测试 2 个（`__tests__/`） | F-299 |

MemoryCore 的 scripts 还含运维验证脚本：`verify-clear-vs-archive.ts`、`verify-tcvdb-clear.ts`、`probe-vdb-capacity.ts`、`probe-vdb-reclaimable.ts`、`cleanup-vdb-test-dbs.ts`（F-299）。

仓库与组件工程文件（F-300）：

| 位置 | 文件 |
|---|---|
| 仓库根 | `.github/ISSUE_TEMPLATE`、`CONTRIBUTING(_CN).md`、`LICENSE` |
| MemoryCore | `tsdown.config.ts`（打包）、`vitest.config.ts` |
| MemoryKnowledge | `tsdown.config.ts`、`drizzle.config.ts` |

## 延伸阅读

- [TencentDB Agent Memory 核心洞察 · 洞察五](../spec/insights.md)
- [TencentDB Agent Memory 事实清单 F-287~F-300](../spec/facts.md)
- [SDK 结构与 CI 摘要](../references/05-sdk-ci.md)
- [10 · MemoryPanel/Hub 团队操作台与 ACL](10-panel-acl.md)
- [11 · 部署拓扑：三容器、卷与端口](11-deploy-topology.md)
