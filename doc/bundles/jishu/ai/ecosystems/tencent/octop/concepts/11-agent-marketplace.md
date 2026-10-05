---
type: Concept
title: "专家市场、子代理库与 MBTI 人格"
description: "experts 九文件分工与 18 个内置专家、published 与 SkillHub market 双发布链路、subagents 双语模板库（zh 272/en 217）与 divisions.json、16 型 MBTI 人格装载、唯一内置技能 skill-manager。"
tags: [octop, experts, marketplace, subagents, mbti, persona, skills]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: "Octop 源码事实清单 F-243~F-253、F-272~F-275"
---

# 专家市场、子代理库与 MBTI 人格

"新建 Agent"在 Octop 里有三个内容来源：内置的**专家库**（experts/library）、远端的 **SkillHub 专家市场**、以及随包分发的**子代理模板库**（subagents/library）；再叠加一层 **MBTI 人格**渲染，Agent 就有了身份、专长与说话风格。本章梳理这四个子系统的边界与装载机制。

## experts/ 九文件分工

`src/octop/infra/agents/experts/` 顶层恰有 9 个 Python 文件（2026-10-04 经 Glob 实测），按职责分三层：

| 文件 | 职责（据模块 docstring 与关键常量，F-243~F-249） |
|------|------|
| catalog.py | 专家目录核心：manifest 文件名 `"manifest.json"`、工作区路径 `.octop/manifest.json`、ExpertQuickPrompt/ExpertSummary/Expert 三个 dataclass、`ExpertCatalog(library_root, extra_roots=None)` 扫描装载（F-243、F-244、F-245） |
| default_agent.py | 默认专家：`DEFAULT_EXPERT_ID = "general-assistant"`、setup 向导用 `"main"`；默认 backend 为 local_shell + virtual_mode（F-247） |
| avatar.py | 头像：`MAX_AVATAR_BYTES = 5MB`、目录 `.octop`，接受 png/jpg/jpeg/webp/gif，下载 UA `"octop-avatar/1.0"`（F-247） |
| publish.py | 导出快照：排除 10 类路径与 `.env`/`credentials.json`，memory.sqlite 前缀处理，slug 冲突追加 -2（F-248） |
| published_creation.py | 本地已发布专家的"发布/刷新/安装/下架"（模块 docstring 逐字 "Publish / refresh / install / unpublish user expert templates."，2026-10-04 源码核实） |
| skillhub_market.py | SkillHub 远端市场客户端：前缀 `skillhub-skillset-`、HTTP 超时 30、分页 100、最多 20 页、列表缓存 300s、14 个场景排序、8 种错误 kind（F-249） |
| market_creation.py | 从 SkillHub 模板建 Agent（docstring："Create agents from SkillHub-backed expert market templates."，2026-10-04 源码核实） |
| manifest_generator.py | 用内置生成技能为市场专家补写欢迎语/快捷提示（超时 45s，轻量模型提示词含 flash/mini/haiku 等，2026-10-04 源码核实） |
| composer_files.py | 创建时把 prompt/技能补丁打到新 seed 的工作区（补丁上限 80 文件、单文件 1MB，2026-10-04 源码核实） |

## 18 个内置专家 manifest

`experts/library/` 经 Glob 实测 18 个 manifest.json（2026-10-04 与 F-246 双重核实）。装载时 `list_summaries` 跳过 id=="default"，排序把 general-assistant 钉在首位（键 `(0 if s.id == "general-assistant" else 1, s.id)`），兜底欢迎语为"说出你的想法，我来帮忙"（F-245）。按领域分组：

| 分组 | id（逐字） |
|------|-----------|
| 通用与编排 | general-assistant、default、multi-agent-orchestrator、superpowers-methodology |
| 研发与云运维 | ai-coding-coach、ops-engineer、tencentcloud-api、wechat-ops、cvm-ai-doctor、cvm-cluster-doctor |
| 医疗学习 | clinical-learning-subscription |
| 内容/资讯/知识 | news-trend、office-automation、karpathy-knowledge-base |
| 生活与理财 | meituan-living-assistant、parenting-companion、stock-assistant |
| 安全 | ai-safety-guardian |

来源：F-246（id 逐字）；分组为教程性归纳。另有 35 个 id 的 `_FALLBACK_BUNDLED_AVATAR_IDS` 兜底头像集（F-243）。

### 专家数据结构与装载时序

目录扫描的结果不是松散 dict，而是三层 frozen dataclass（F-244）：

- `ExpertQuickPrompt`：快捷提示，含中英 title/description/prompt 六字段，默认 color `#e8f4ff`；
- `ExpertSummary`：列表页用的 13 字段摘要；
- `Expert`：完整对象，在 summary 之外再带 files、prompt_files、quick_prompts。

manifest 的查找有固定顺序：先读工作区 `.octop/manifest.json`，再退到库目录下的 `manifest.json`（读取顺序元组二者并列）（F-243）。一次"从专家建 Agent"的装载时序大致是：

```
ExpertCatalog.refresh() 扫描含 manifest.json 的子目录        (F-245)
  → list_summaries()：跳过 default，general-assistant 置顶   (F-245)
  → build_create_spec_from_expert() 转成 AgentCreateSpec      (见 10-agent-teams.md)
  → seed 工作区 → composer_files 打 prompt/技能补丁           (composer_files.py)
  → market 来源先经 manifest_generator 补欢迎语/快捷提示      (manifest_generator.py)
  → avatar.materialize_remote_icon_url 落头像                 (F-247)
```

生成器补元数据时有明确的字符预算：工作流 6000、技能摘录 500、标签 64、专家描述 220、提示词 180（manifest_generator.py，2026-10-04 源码核实）。

## 双发布链路：published 与 market

两条"把一个专家变成可复用模板"的路径并存，存储位置与 ID 形态完全不同：

```
本地产出工作区
   │
   ├─ publish.py 导出（排除 .git/__pycache__/inbound/uploads/sessions/
   │     media/logs 等 10 类路径与 .env、credentials.json）           (F-248)
   ├─ published_creation.py → published_experts 仓库
   │     slug 冲突时 resolve_published_expert_slug 追加 -2           (F-248)
   │
   └─ SkillHub 远端 skillset → skillhub_market.py
         安装 ID 前缀 "skillhub-skillset-"
         14 场景：ecommerce/finance/content-creation/lifestyle/...    (F-249)
         market_creation.py 下载落库 → manifest_generator 补元数据
```

市场侧的容错是封闭枚举 `SkillHubMarketErrorKind`：not_found、invalid_slug、upstream_timeout、upstream_bad_payload、package_invalid、package_too_large、upstream_failed、ssl_error（F-249）。

## 子代理模板库：双语 272/217 与 divisions.json

子代理（subagent）是比专家更轻的"可调用角色模板"，模板就是磁盘上的 Markdown：模块 docstring 逐字 "Templates live on disk under ``library/<locale>/<division>/*.md``"（F-250）。实测计数（2026-10-04 PowerShell 与 F-251 双核实）：

| locale | .md 文件数 | 一级分类目录 | 元数据 |
|--------|-----------|--------------|--------|
| zh | 272 | 19 | divisions.json ×1 |
| en | 217 | 16 | divisions.json ×1 |

每 locale 读自己的 `library/<locale>/divisions.json`（F-250）；`DivisionMeta` 携带 id/label/icon/color/available_locales，`SubagentSummary` 携带 slug/division/name/emoji/color 等，`SubagentDefinition` 另含 content/contents 与 name_for/description_for/content_for 多语言取用方法（F-250）。回退语言 `FALLBACK_LOCALE = "en"`，未翻译名占位符 `"TODO_TRANSLATE"`（F-250）；i18n 改造前的平铺旧布局仍有回退扫描（F-251）。

## MBTI 人格：16 型 dataclass 注册器

人格不再是磁盘上的散装 Markdown——旧 `personas/*.md` 目录已移除，改为带双语字段的数据类（F-274）。`mbti_profiles.py` 模块 docstring 逐字 "Built-in MBTI personality profiles for the 16 types."，经 Select-String `code="[A-Z]{4}"` 命中恰 16 条（F-252）：

- 三个 frozen dataclass：`MBTIDimensions`（ei/sn/tf/jp 四组维度分）、`MBTIBehaviorMapping`（answer_style/casual_chat/conflict/creativity/emotion/planning 及 _zh 共 12 字段）、`MBTIProfile`（code/双语名/昵称/摘要/描述词/维度/行为/color/symbol 共 12 字段）（F-252）。
- 规范顺序固定：INTJ,INTP,ENTJ,ENTP,INFJ,INFP,ENFJ,ENFP,ISTJ,ISFJ,ESTJ,ESFJ,ISTP,ISFP,ESTP,ESFP；例如 INTJ 中文名"建筑师"、color `#6366F1`、symbol `♜`（F-252）。
- 装载：`render_persona_template(profile)` 把 profile 渲进模板；`PersonaLoader` 带缓存；`resolve_persona_code` 在 persona_mbti 参数非空时直接 `.upper()`，否则读 config（F-253）。
- 生效面：MBTI 码存在 agents 行 `persona_mbti` 列，启动时渲染进该 Agent 的 SOUL.md，system_prompt 追加在 persona **之后**；列为 NULL/空串时回落内置 `_DEFAULT_PERSONA_TEMPLATE`（首行 "# Persona: Default"，占位符 {agent_name}/{user_display}/{custom}）（F-274、F-253）。

## 唯一内置技能：skill-manager

内置技能根常量 `OCTOP_BUILTIN_SKILLS_ROOT = "_builtin_skills"`；经目录实测（2026-10-04）builtin_skills 下**只有 skill-manager 一个技能目录**，含 SKILL.md 与 scripts/manage_skills.py（F-272）。其调用命令经模板 token 替换落地：

```
python "{{OCTOP_BUILTIN_SKILLS}}/skill-manager/scripts/manage_skills.py" <command>
```

同步函数 `sync_octop_builtin_skills(workspace)` 扫描包内含 SKILL.md 的子目录复制进工作区，并删除已退役技能——`RETIRED_BUILTIN_SKILLS = ("install-skill",)`（F-272）。工作区替换用三个字节 token：`{{OCTOP_WORKSPACE}}`、`{{OCTOP_SKILLS}}`、`{{OCTOP_BUILTIN_SKILLS}}`（F-272）。

## docs 声明面

源码行为之外，两份文档构成对用户的正式声明，使用时应与源码互相印证：

- **docs/expert-teams.md**：声明主持人持独立工作区/记忆/通道、成员保持普通专家身份可单聊可跨团；创建团队至少 2 名成员（不含主持人）；主持人仅持 agent_list、异步 ask_agent、记忆/时间类工具，不挂文件系统/浏览器/搜索/MCP/技能/插件；编制落在工作区 `.octop/manifest.json`（F-273）。与 [10-agent-teams.md](10-agent-teams.md) 的源码实现一一对应。
- **docs/personas.md**：声明 persona_mbti 列、SOUL.md 渲染时机、system_prompt 追加顺序、空值回落，并列出全部 16 个 MBTI 码（F-274）。
- **docs/agent-call-agent.md / agent-delegation.md**：声明 `@` Agent 等于进主 stream 前做同步 call_peer 注入 system；ask_agent 两 mode（sync 默认 / background 入 harness inbox）；旧的 `agent_delegations` 表、DelegationRepo、`/delegate` slash **已移除**，状态改由 harness inbox 内存队列管理（F-275）。

## 相关概念

- [/concepts/10-agent-teams.md](10-agent-teams.md) —— 团队成员即普通专家，编制写 manifest
- [/concepts/02-agent-runtime.md](02-agent-runtime.md) —— 专家装载成 HarnessAgent 的运行时过程
- [/concepts/06-cli-commands.md](06-cli-commands.md) —— /agent、/skills 等市场操作入口
