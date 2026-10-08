---
type: Reference
title: "README 与 CHANGELOG 信源：产品定位、版本时间线与口径差异"
description: "根 README_CN 的产品定位与四组件/四资产表述、CHANGELOG 五个版本的完整时间线、ROADMAP 规划项，以及包名/版本/端口/客户端数量等口径差异的并列登记。"
tags: [tencentdb-agent-memory, reference, readme, changelog, roadmap, versioning]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-readme
    resource: README_CN.md
    title: 仓库根 README（中文）
  - id: s-changelog
    resource: CHANGELOG.md
    title: 变更日志
  - id: s-roadmap
    resource: ROADMAP_CN.md
    title: 中文路线图
---

# README / CHANGELOG / ROADMAP 信源

## 信源元信息

| 项目 | 内容 |
|------|------|
| 信源 ID | s-readme、s-changelog、s-roadmap |
| 文件 | README_CN.md、CHANGELOG.md、ROADMAP_CN.md、README.md、ROADMAP.md |
| 采集日期 | 2026-10-04（截面 commit 8b86874） |
| 对应事实 | F-005~F-027、F-037~F-056、F-241 |

## README 产品表述（要点登记）

- 标语「让 Agent 沉淀经验，让人专注创造」；技术三问「什么值得留下、谁可以使用、下一次怎样少拿但拿对」（F-019）。
- 四组件与端口：MemoryCore 8420、MemoryKnowledge、MemoryPanel/Hub、MemoryProxy 8096（F-022）。
- 四层记忆：L0 Conversation（JSONL 按天）→ L1 Atom（persona/episodic/instruction）→ L2 Scenario（scene_blocks MD + META + heat）→ L3 Core/Persona（F-037~F-040）。
- 四资产：Chat Memory / Skill / Wiki（Karpathy LLM Wiki 灵感）/ CodeGraph（致谢 colbymchenry/codegraph 与 Hermes Agent skill 复用）（F-041~F-045）。
- 可见性 private/team/restricted/agent 四值；全局 System Admin + 团队 Admin/Member 两层角色（F-046/F-047）。
- PersonaMem benchmark：48% → 76%（+59%）（F-025）。
- Proxy「协议不变，不需要插件、Hook 或 MCP」；7 客户端（F-026/F-027）。

## CHANGELOG 版本时间线（5 个版本，原文锚点）

| 版本 | 日期 | 核心内容 |
|------|------|---------|
| 2.0.2-beta.1 | 2026-09-07 | MongoDB 试验后端（不静默回退、不自动迁移）；Skill 体验修复；OAuth2 OA 登录；ClickHouse 可观测默认关闭；召回/降级修复（F-009~F-012） |
| 2.0.1 | 2026-08-25 | 新增 OpenCode/dsh/Codex/WorkBuddy 接入；会话内重置与任务指令；默认 Agent 冷启动；Skill 在线编辑；面板对话记忆搜索；交互式部署预检（F-013~F-017） |
| 2.0.1-beta.1 | 2026-08-13 | 默认 Agent + 预置 Skill；Wiki 并发构建与失败重试；Skill 导出/检索；Codex/WorkBuddy/dsh proxy 接入（dsh aux 短路 + headless bypass）（F-241） |
| 2.0.0 | 2026-08-03 | 四资产首次完整开源；Memory Hub；双协议 Proxy；三件套一键部署；官方 TS/Python SDK |
| 2.0.0-beta.1 | 2026-07-21 | 首次公开发布；npm 包迁移 -v2 后缀；镜像 tag :1.0.0-beta.1（F-007/F-008） |

## ROADMAP 登记

- README 标注的 v2.0.1 规划方向：零配置冷启动、Wiki 加速、自定义 Prompt、Skill 导出、Codex IDE Plan（F-052）。
- ROADMAP_CN.md:13-71「下个版本 · v2.0.1」清单：Agent 模版、`mem:` 指令增强、记忆可编辑、L0/L1 记忆搜索、Cursor 支持（F-053）。
- 交叉观察：CHANGELOG 2.0.1（2026-08-25）已落地其中部分项（会话内指令、记忆搜索、冷启动），Cursor 支持在学习截面的 CHANGELOG 中未见发布记录。

## 口径差异并列登记（不做单边取舍）

| 议题 | 口径 A | 口径 B | 出处 |
|------|--------|--------|------|
| 产品/npm/git 版本 | README：v2.0.0 | package.json：memory-tencentdb-v2 @ 1.0.2-beta.1；git tag：v2.0.2-beta.3-7-g8b86874 | F-021 |
| Knowledge 端口 | config 默认 8421 / 容器 EXPOSE 8421 | 部署宿主映射 8424 | F-023 |
| Panel 端口 | .env.example 本地默认 8123 | 容器内/部署 8125 | F-024 |
| 客户端数量 | README：7 个 | INSTALL_CN：8 类（多 OpenCode，2.0.1 起新增） | F-027/F-028 |
| 默认数据目录 | README：~/.memory-tencentdb/memory-tdai | l0-recorder.ts 注释：~/.openclaw/memory-tdai/conversations/ | F-054/F-055 |
| 仓库组织名 | remote：TencentCloud | CHANGELOG 克隆命令：Tencent | F-018 |
| Standalone 镜像名 | 文档示例：agentmemory/hermes-memory:latest | 部署脚本：agentmemory/memory-core:latest | F-032/F-033 |

## 说明

- CHANGELOG 遵循 Keep a Changelog 1.1.0 中文约定与 SemVer（CHANGELOG.md:3-5），覆盖五个模块（F-005）。
- 2.0.2-beta.1 明确标注 MongoDB 与数据分析均为「可选/试验、默认关闭」，引用时不得省略该限定。
