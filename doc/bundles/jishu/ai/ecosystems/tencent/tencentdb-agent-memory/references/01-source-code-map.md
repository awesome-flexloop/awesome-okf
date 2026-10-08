---
type: Reference
title: "TencentDB-Agent-Memory 源码地图信源（commit 8b86874）"
description: "学习截面的仓库元信息（remote、commit、tag、分支）、四组件目录地图、关键文件清单与机械计数复核记录，是全部代码类事实的锚点信源。"
tags: [tencentdb-agent-memory, reference, source-code, architecture, map]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-repo
    resource: https://github.com/TencentCloud/TencentDB-Agent-Memory
    title: TencentDB-Agent-Memory 仓库（commit 8b86874，v2.0.2-beta.3-7-g8b86874）
---

# TencentDB-Agent-Memory 源码地图信源

## 信源元信息

| 项目 | 内容 |
|------|------|
| 信源 ID | s-repo / s-core-code / s-know-code / s-proxy-code / s-panel-code |
| URL | https://github.com/TencentCloud/TencentDB-Agent-Memory |
| 学习截面 | commit `8b86874a2daea49e3ff0fb53d699203146c5c77d` |
| 分支 | feat/server_team |
| git describe | v2.0.2-beta.3-7-g8b86874 |
| 提交信息 | Merge PR #1552（2026-09-29 16:48） |
| 采集日期 | 2026-10-04 |
| 本地路径 | external/dao/runtime/tencent/TencentDB-Agent-Memory（本仓 external 稳定信源区） |
| 许可证 | MIT |
| 对应事实 | F-001 ~ F-004、F-057 ~ F-300 |

> ⚠️ CHANGELOG 克隆命令中的 URL 为 `github.com/Tencent/TencentDB-Agent-Memory`（F-018），与实际 remote 的组织名 TencentCloud 不同，本束以实际 remote 为准。

## 顶层结构

| 路径 | 角色 | 关键计数 |
|------|------|---------|
| MemoryCore/ | 记忆核心（L0-L3、网关、Skill、offload、存储） | TypeScript 主体，src/ 下 20+ 子模块 |
| MemoryKnowledge/ | 知识引擎（Wiki + CodeGraph + MCP） | src/ 11 个路由/存储/引擎子目录，MCP 12 工具 |
| MemoryProxy/ | LLM 双协议代理（context-proxy 包） | src/ 约 130 个 .ts 文件（含测试） |
| MemoryPanel/ | 团队操作台（team-memory-control 包） | Hono 应用，API 前缀 /api/v1/meta/* |
| sdk/memory-core/ | 官方 SDK | typescript（src + src/v3）、python（含 v2/v3 子包） |
| deploy/global-images/ | 三件套一键部署 | start-all + 3 个分组件脚本 + _lib.sh + .env.example |

## MemoryCore 关键目录地图

- `src/core/record/`：l1-extractor、l1-dedup、l1-writer、l1-reader（F-061~F-065）
- `src/core/conversation/`：l0-recorder（F-066）
- `src/core/scene/`：scene-extractor、scene-index、scene-format、scene-derive、scene-navigation（F-081~F-084）
- `src/core/persona/`：persona-trigger（F-085）
- `src/core/profile/`：profile-scope、profile-sync（F-086/F-087）
- `src/core/memory-prompt/`：resolver、composer、types（F-088~F-092）
- `src/core/skill/`：11 个文件 + queue/ 子目录（F-131~F-144）
- `src/core/store/`：factory、store-pool、isolation、search-utils、bm25-*、sqlite/、tcvdb/（F-107~F-121）
- `src/gateway/`：v2-router、server、config、skill-handlers、knowledge-handlers、memory-prompt-schemas 等（F-151~F-163）
- `src/offload/` + `src/offload_server/` + `src/offload-client/`：上下文压缩/卸载三套件（F-173~F-187）
- `src/metadata/`：元数据面 router/store/utils（F-097~F-099）
- `openclaw-plugin/`、`pi-plugin/`：两类插件打包（F-149/F-150）
- `bin/`：4 个 .mjs 可执行入口（F-060）

## 机械计数复核记录（V 阶段留痕）

| 计数项 | 数值 | 复核方式 |
|--------|------|---------|
| CHANGELOG 版本条目 | 5 | Read CHANGELOG.md 全文，逐条登记（F-006） |
| V3_ALLOWED_SUBPATHS | 18（5+5+5+3） | 事实登记于 v2-router（F-154），V 阶段 Grep 复核 |
| /v3/skill/* 端点数 | 17 | Grep skill-handlers.ts:1155-1171 路由表逐个数（F-145） |
| MCP 工具数 | 12（code 8 + wiki 4） | 阅读 mcp/tools.ts（F-202） |
| agent 适配器数 | 8 | Glob agent-adapters/*.ts（F-220） |
| 注入器数 | 8 | Glob injection/injectors/*.ts（F-225） |
| mem 命令数 | 6 | Glob mem-command/commands/*.ts（F-234） |
| Knowledge DDL 表数 | 5 | 阅读 db/schema.ts（F-195） |
| Wiki ingest-v2 模块数 | 14 | Glob engines/wiki/ingest-v2/*.ts（F-207） |
| Skill 路由端点 | 17（同上） | create/update/patch/delete/get/get-by-name/list/search/versions/files×3/export/listing/extract/conversation×2 |

## 使用边界

- 本束所有「文件:行号」锚点基于 commit 8b86874 截面；分支前进后行号可能漂移，以文件内符号名为准复核。
- 学习截面位于 feat/server_team 分支而非正式 release tag（最近 tag 为 v2.0.2-beta.3，后差 7 个提交），引用时应标注截面性质。
