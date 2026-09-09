---
type: concept
title: "技能系统与注册机制"
description: "SKILL.md 单文件技能约定、skills.config.json 注册表（order/enabled）、SkillManager 同步/下载/升级/自动路由全生命周期，以及目录计数与注册表计数互相校验的一致性机制。"
tags: [lobsterai, skill, skillmd, registry, skillmanager]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:vendor-grep", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: LobsterAI 源码事实清单（R 阶段，基线 2026.9.4）
  - id: insights
    resource: /references/insights.md
    title: LobsterAI 架构洞察（I 阶段，基线 2026.9.4）
---

# 技能系统与注册机制

LobsterAI 的技能体系采用「文件即技能」的去中心化注册：**目录结构即技能本体，注册表只携带运行时旋钮**。这套设计以极低的机制成本换取了可扩展性与可校验性。

## 一、SKILL.md：单文件技能约定

每个技能一个子目录、一份 `SKILL.md`。`SKILLs/` 下共 29 个 `SKILL.md`（Glob `SKILLs/*/SKILL.md` 计数，F-la-065）。SKILL.md 的 frontmatter 约定四个字段（F-la-067）：

```yaml
---
name: web-search
description: 搜索网页并总结结果
official: true
version: 1.0.2
---
```

- `name`：技能 ID（与目录名一致）；
- `description`：能力描述，同时是自动路由的素材；
- `official`：是否官方内置；
- `version`：语义化版本。

kits IPC 处理器中以常量固化目录与文件名约定：`SKILLS_DIR_NAME = 'SKILLs'`、`SKILL_FILE_NAME = 'SKILL.md'`（F-la-036）——技能发现逻辑只需在 userData 的 `SKILLs` 目录下逐级查找 `SKILL.md` 即可。

## 二、skills.config.json：只存运行时旋钮的注册表

`SKILLs/skills.config.json` 顶层 `version` 为 1，`defaults` 含 29 个条目，与 SKILL.md 数量一一对应（F-la-066）；每个条目仅含 `order` 与 `enabled` 两个字段：

```json
{
  "version": 1,
  "description": "Default skill configuration for LobsterAI",
  "defaults": {
    "docx": { "order": 10, "enabled": true },
    "web-search": { "order": 15, "enabled": true },
    "skin-creator": { "order": 214, "enabled": false }
  }
}
```

注册表**不复制**技能的元数据（名称、描述都在 SKILL.md 里），只记录"排序"与"启停"两类运行时差异。显式 `enabled: false` 的条目仅两个：`skin-creator`（order 214）与 `technology-news-search`（order 224），其余 27 个默认启用（F-la-069）。

### order 编号暴露的隐性拓扑

29 条 order 全清单（F-la-068）按数值分段呈现清晰的分类结构：

| order 段 | 技能 | 类别 |
|---|---|---|
| 10-100 | docx、web-search、xlsx、pptx、pdf、remotion、develop-web-game、playwright、create-plan、canvas-design、frontend-design | 文档与开发类 |
| 110-122 | stock-analyzer、stock-announcements、stock-explorer、content-planner、article-writer、daily-trending | 内容与股票类 |
| 200-224 | local-tools、weather、imap-smtp-email、seedance、seedream、skin-creator、films-search、music-search、technology-news-search | 本地工具与媒体类 |
| 298-300 | youdaonote、skill-vetter、skill-creator | 技能治理三件套 |

治理类技能（技能审查 skill-vetter、技能创建 skill-creator）被刻意排在最高段——order 既是排序键也是分类编码。

## 三、SkillManager：全生命周期管理

`SkillManager`（`src/main/skills/skillManager.ts`）的 12 个方法覆盖技能全生命周期（F-la-033）：

| 阶段 | 方法 |
|---|---|
| 内置分发 | `syncBundledSkillsToUserData`（把随包技能同步到用户数据目录，实现"内置技能随包分发、用户态技能独立演化"的双层结构） |
| 查询 | `listSkills`、`getSkillConfig`、`setSkillConfig` |
| OpenClaw 协同 | `detectSkillsFromOpenClaw`、`syncSkillsFromOpenClaw`（从运行时反向同步技能清单） |
| 路由 | `buildAutoRoutingPrompt`（基于技能 description 构建自动路由提示词） |
| 市场 | `downloadSkill`、`upgradeSkill`、`confirmPendingInstall`（安装需确认，防供应链偷袭） |
| 运行态 | `setSkillEnabled`、`startWatching`（目录监听，外部变更即时感知） |

配套导出 `SkillRecord` 类型；`skills/index.ts` 仅重导出 `OpenClawSkillReport` 类型与 `updatePluginSkillIdsFromReport` 函数（F-la-034），把 OpenClaw 同步报告收敛为单一入口。渲染层经 `skills:*` 通道族操作（`skills:list`、`skills:download`、`skills:setEnabled` 等，F-la-037）。

## 四、一致性校验：29 = 29

README 声称"28 built-in skills"，而 Glob 实测 `SKILLs/*/SKILL.md` 为 29 个、`skills.config.json` 的 `defaults` 也是 29 条——README 声明过期（F-la-007）。这个偏差恰好演示了该设计的自校验能力：

> **目录 Glob 计数 == 注册表条目数**

两条独立计数路径（文件系统清点 vs JSON 注册表）互相印证，任何一条漂移（文档过期、注册遗漏、文件丢失）都会暴露为计数不等。将这条一致性断言纳入 CI，即可同时拦截文档过期与注册遗漏。

## 设计启示

1. 用「每技能一目录 + 单约定文件」替代中心清单，注册表只存运行时差异（启用/排序）；
2. 目录与文件名约定固化为常量（`SKILLS_DIR_NAME`/`SKILL_FILE_NAME`），发现逻辑与约定解耦；
3. 安装类操作保留人工确认环节（`confirmPendingInstall`）；
4. CI 中加入「目录 Glob 计数 == 注册表条目数」断言，低成本高覆盖。

## 相关概念

- [/concepts/06-agent-preset-system.md](06-agent-preset-system.md)
- [/concepts/02-ipc-channel-contracts.md](02-ipc-channel-contracts.md)
