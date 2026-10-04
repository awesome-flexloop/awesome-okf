---
type: Reference
title: "官方 SDK 与工程配套信源"
description: "TypeScript/Python SDK 的包名、v3 模块结构与严格 isolation 构造要求，以及 CI 工作流、issue 模板、测试与运维验证脚本等工程配套事实。"
tags: [tencentdb-agent-memory, reference, sdk, typescript, python, ci]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-sdk-ts
    resource: sdk/memory-core/typescript/**
    title: TypeScript SDK
  - id: s-sdk-py
    resource: sdk/memory-core/python/**
    title: Python SDK
  - id: s-ci
    resource: .github/workflows/pr-ci.yml
    title: PR 持续集成
---

# SDK 与工程配套信源

## 信源元信息

| 项目 | 内容 |
|------|------|
| 路径 | sdk/memory-core/typescript、sdk/memory-core/python、.github/、MemoryCore/scripts/ |
| 采集日期 | 2026-10-04（commit 8b86874） |
| 对应事实 | F-287 ~ F-300 |

## TypeScript SDK

- 包名 `@tencentdb-agent-memory/memory-sdk-ts-v2`（F-287）。
- src/v3 共 12 个文件：client、http、index、types、skill-client/skill-types、metadata-client/metadata-types、memory-prompt-client/types、memory-generation-log-client/types（F-288）。
- 顶级导出即 v3 严格 isolation 版本；`.../v2/v3` 子路径保留为向后兼容别名（F-289）。
- v3 构造参数：endpoint、apiKey、serviceId、teamId、agentId、userId（F-290）。
- 随包文档：双 README、CHANGELOG、AGENT_GUIDE.typescript.zh-CN.md（F-291）。

```ts
import { MemoryClient, SkillClient, MetadataClient } from "@tencentdb-agent-memory/memory-sdk-ts-v2";
const memory = new MemoryClient({ endpoint, apiKey, serviceId, teamId, agentId, userId });
```

## Python SDK

- 安装名 `tencentdb-agent-memory-sdk-python`（F-292）。
- 顶层 `tencentdb_agent_memory` 默认导出 v2 兼容 MemoryClient；v3 子包导出 MemoryClient、MetadataClient、SkillClient（F-293）。
- v3 子包模块：skill_client、metadata_client、memory_prompt、memory_generation_log、client（F-294）。
- 通用层：errors、cos、_v3_http、_http（F-295）；附 AGENT_GUIDE.python.zh-CN.md（F-296）。

```python
from tencentdb_agent_memory import MemoryClient                  # v2 兼容
from tencentdb_agent_memory.v3 import MemoryClient, MetadataClient, SkillClient
```

## CI 与协作配套

- .github/workflows/pr-ci.yml：PR 触发的持续集成（F-297）。
- Issue 模板三类：bug_report.yml、feature_request.yml、question.yml；另有 PR 模板（F-298）。
- MemoryCore/pi-plugin/openclaw-plugin 等使用 vitest；MemoryProxy 仓库内含 opencode 相关测试 2 个（F-299）。
- 打包配置：MemoryCore/MemoryKnowledge 使用 tsdown；MemoryKnowledge 使用 drizzle ORM（drizzle.config.ts）；API 类型经 kubb 生成（F-105/F-300）。

## 运维/验证脚本登记（MemoryCore/scripts/）

- 迁移导出：migrate-v2-to-v3/（含 README）、bin/migrate-sqlite-to-tcvdb.mjs、bin/export-tencent-vdb.mjs、bin/read-local-memory.mjs、bin/seed-v2.mjs。
- TCVDB 容量：probe-vdb-capacity.ts、probe-vdb-reclaimable.ts、cleanup-vdb-test-dbs.ts、verify-tcvdb-clear.ts。
- 归档语义：verify-clear-vs-archive.ts；E2E：start-e2e-gateway.ts、e2e-memory-prompt-vdb-cos.ts；Mongo L0 基准：bench-l0-mongo/（7 文件）。
- 插件安装：install-openclaw-plugin.sh、install-hermes-plugin.sh（F-299/F-188）。

## 引用纪律

- SDK 包名存在 v2 后缀迁移历史（F-008），引用安装命令时以 2.0.0 CHANGELOG 与子包 package.json 双证为准。
- Python 顶层 MemoryClient 为 v2 兼容别名，多租户隔离场景必须使用 v3 子包，与网关三元组强制要求一致（F-153/F-293）。
