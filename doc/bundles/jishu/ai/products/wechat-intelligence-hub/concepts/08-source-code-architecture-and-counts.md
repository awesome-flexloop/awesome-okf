---
type: Concept
title: "08 · 源码架构分层与计数口径"
description: "Reader 与情报产品的双 CLI 分层、模块职责地图、TOOL_SPECS 30 工具/266 字段与 README 29 项的口径差，以及四个不可混用的计数口径"
tags: [wechat-intelligence-hub, architecture, source-code, cli, counting, 口径勘误]
---

# 08 · 源码架构分层与计数口径

> 本篇的结构性目的：让读者在引用任何数量陈述前，先知道**那个数量是怎么数出来的**。首轮引用的「29 项只读工具、266 个输入字段」在本轮源码下出现了 1 项差异——差异本身不大，但**口径意识**必须补上。

## 1. 仓库地图：一个产品、两个可执行体

固定 commit `fb6a42c` 下 HEAD 跟踪 **126** 个文件（F-062），其中 Python 38 个（18 非测试 + 20 测试）、Markdown 43 个、Shell 12 个（F-063）。顶层结构（F-065）：

```
wechat-intelligence-hub/
├── projects/
│   ├── rion-wechat-reader/          ← 只读 Reader 核心（依赖层）
│   │   ├── rion_wechat_reader.py    （3,465 行：30 工具 + 36 子命令）
│   │   ├── rion_wechat_access.py    （954 行：实验性接入助手，非只读）
│   │   └── scripts/                 （capability_gap.py / live_parity.py）
│   └── wechat-intelligence-hub/     ← 情报产品（产品层）
│       ├── wechat_intelligence_hub.py（7,361 行：37 子命令）
│       ├── intelligence_views.py    （26 顶层函数：视图与草稿）
│       ├── report_bundle_flagship.py / report_bundle_html.py（渲染）
│       ├── report_security.py       （96 行：净化）
│       └── message_identity.py / message_time.py / opportunity_store.py /
│           wechat_deal_radar.py / maintenance.py
├── skills/
│   ├── wechat-cli/                  ← Skill 1：Reader 侧（接入与排障）
│   └── wechat-intelligence-hub/     ← Skill 2：产品侧（能力与交付）
├── providers/wxkey/                 ← 候选接入工具（实验性，默认不捆绑）
├── docs/                            ← USAGE.md、SECURITY.md、access-* 等
└── scripts/                         ← install.sh / validate.sh / build_release.py
```

**分层判据**：Reader 层负责**把数据取出来**（只读、索引、schema）；产品层负责**把数据变成情报**（状态判定、草稿、报告渲染）。首轮 [01](01-local-first-readonly-architecture.md) 描述的「四层结构」在源码中得到了目录级的对应。

## 2. 两个 CLI：不要混为一谈

首轮没有区分「工具」与「子命令」这两个词，本轮必须分清（F-076~F-079）：

| 口径 | 数量 | 含义 |
|------|------|------|
| Reader `TOOL_SPECS` | **30** | 工具目录中登记的能力项（Agent 工具面） |
| Reader CLI 子命令 | **36** | `build_parser` 中 `add_parser` 注册的子命令 |
| 情报产品 CLI 子命令 | **37** | `wechat_intelligence_hub.py` 的 `add_parser` 注册的子命令 |
| 两层 CLI 合计 | **73** | 跨两个可执行体，角色不同，**不可当作一个产品能力清单** |

两组差集说明了差异来源（F-077）：

- **仅 CLI 有**（10 个）：`version`、`tools`、`tool-schema`、`self-test`、`status`、`doctor`、`access-plan`、`setup`、`discover`、`import-access`、`init` —— 全部是**管理/自省类**命令，不是数据读取能力；
- **仅工具有**（4 个）：`history`、`timeline`、`sns-feed`、`sns-search` —— 通过通用调度暴露，没有独立子命令。

情报产品 CLI 的 37 个子命令则覆盖了完整业务面（F-078），从底层运维（`profile-init`、`vault-scan`、`wechat-scan`、`compat-check`）到内容生产（`daily`、`group-daily`、`render-bundle`、`brief`、`topic`）再到交互式查询（`home`、`person`、`reply`、`today`、`inbox`、`triage`、`opportunities`）与反馈闭环（`feedback-add`、`feedback-list`、`opportunity-sync`）。

**口径纪律**：「它有 73 个命令」是错的；「它有 30 个只读工具和 73 个 CLI 子命令」才是对的。

## 3. 266 对上了，29 对不上

首轮登记的 README 口径（两处一致）：「v0.9.2-preview.2 已覆盖旧 `wechat-cli 1.6.19` 的 **29 项只读工具、266 个输入字段**」（F-070）。

本轮源码事实（F-069、F-070）：

| 指标 | README 口径 | 源码口径 | 结论 |
|------|-------------|---------|------|
| 只读工具数 | 29 | **30** | ⚠️ **差 1 项** |
| 公开输入字段数 | 266 | **266** | ✅ 一致 |
| 去重后不同属性名 | — | **87** | ➖ 首轮无此口径 |

字段数完全对齐，工具数差 1 项。最合理的口径解释是：README 描述的是**与旧版 `wechat-cli 1.6.19` 对齐的公开接口子集**，而源码 `TOOL_SPECS` 是**当前源码全集**——tag 之后的 13 个提交里新增或改名了工具（`git diff v0.9.2-preview.2..HEAD` 显示 `rion_wechat_reader.py` 变更 +328 行）。

**本束不臆断具体是哪一项**。能确定的是两点：266 是可靠的（双口径独立复核一致，见下）；29 与 30 的差来自「对外对齐子集 vs 源码全集」的**口径差**，而非矛盾。

**方法论要点**：这是**计数断言验证**的典型价值——如果不做独立复核，"266"这个数字会显得比实际更权威。R 阶段用 `ast` 解析、V 阶段用正则与 `awk` 独立复核，两次都得 266 才写入本束。

## 4. 计数断言的双口径复核方法

本轮对所有数量陈述都做了双口径验证（详见 [../references/source-code-verification.md](../references/source-code-verification.md) §3）。方法要点：

| 断言 | R 阶段 | V 阶段独立手段 |
|------|---------|----------------|
| 工具数 30 | `ast` 取 `AnnAssign` → `Dict` 键数 | `awk` 提取块 + `grep -cE '^\s{4}"[a-z0-9-]+": \{'` |
| 字段数 266 | `ast` 求 `properties` 列表长度和 | 正则提取 `"properties": [...]` 内引号串计数 |

两个数字曾在此前工作中分别被记为 30 和 266（本轮首探时脚本因只处理 `ast.Assign` 而漏掉 `ast.AnnAssign`，返回 0；修正后恢复 266）。这提示一个具体做法：**AST 脚本必须同时处理 `Assign` 与 `AnnAssign`**，否则带类型注解的模块级常量会被整体漏掉——而漏掉的表现是"计数为 0"，比"计数偏差"更容易被误判为事实。

## 5. 版本锚点：一个容易被忽略的时点差

首轮把「当前版本 `v0.9.2-preview.2`」登记为事实（F-045）。本轮发现该表述需要补一层限定（F-060、F-061）：

| 项 | 值 |
|----|-----|
| 唯一 tag | `v0.9.2-preview.2` → `6b73940a`（2026-09-04 22:55:07 +0800） |
| 本轮源码基线 HEAD | `fb6a42c`（2026-10-17 03:53:01 +0800） |
| 差距 | **13 个提交** / 64 文件 / +5569 −202 行 |
| tag 之后新增的关键文件 | `docs/USAGE.md`(317)、`SECURITY.md`、`rion_wechat_access.py`(954)、`report_security.py`(96)、`providers/wxkey/` |

**这解释了首轮的一个谜团**：首轮判定「官方 README 只有语义对应、未逐字给出名称」时，读到的是 `main` 分支网页视图。而本轮在本地 commit 里，`docs/USAGE.md` 与 `SECURITY.md` **逐字**给出了四入口与检索五维度。两者不矛盾——**是信源快照不同**，不是官方文档前后矛盾。

这也是 G0 信源稳定性预检存在的理由：把信源钉在**不可变 commit** 上，后续复核才能引用同一份内容；只写「main 分支」则每次复核的对象都在漂移。

## 6. 可迁移模式

**模式 M6：对外文档的「接口数」与源码的「能力数」是两个口径，差距本身是信息。**

README 说 29、源码有 30，差的那 1 项不是笔误，而是「**对外承诺的稳定接口**」与「**当前实现的全部能力**」之间的差。这种差值本身就是有价值的产品信号：

- 差值小 → 对外接口稳定，源码演进未破坏兼容；
- 差值持续扩大 → 源码在跑在承诺前面，需要考虑是否收敛或更新文档；
- 差值为负 → 源码删了能力但文档未同步，是文档腐化的早期信号。

把这类差值**主动记录下来**（而不是抹平），是维持技术文档可信度的低成本手段。

下一站：[09-safety-and-adoption-boundaries-from-source.md](09-safety-and-adoption-boundaries-from-source.md)。
