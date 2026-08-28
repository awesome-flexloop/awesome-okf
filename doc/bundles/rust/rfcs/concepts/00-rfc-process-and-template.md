---
type: Concept
title: RFC 流程与模板
description: rust-lang/rfcs 仓库的变更提案流程、RFC 编号即 PR 编号的机制、0000 模板的 9 章双解释文体与目录统计
tags: [rust, rfcs, rfc-process, governance, template]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rfcs-source
    resource: /references/rfcs-source-map.md
---

# RFC 流程与模板

RFC（request for comments，意见征求）流程为 Rust 变更（如新特性）提供一致且受控的路径，使所有利益相关者对项目方向有信心（F-rfcs-002）。本仓库是这一流程的正式载体：每一个语言层面的重大决策都以 markdown 文件的形式沉淀在 `text/` 目录中。本篇是整个知识包的「文体透镜」——理解了流程与模板，后续各主题篇中出现的 RFC 结构、头部字段与章节组织就都有了统一坐标系。

## RFC 流程的定义

RFC 流程的源头是 RFC 0002（`text/0002-rfc-process.md`，Start Date 2014-03-11）——它本身就是流程的定义文件，表述为"为新特性进入语言与标准库提供一致且受控的路径"（F-rfcs-171）。流程至今仍在活跃使用：仓库中编号最大的 RFC 3984（2026 年的库团队重组提案）依然遵循同一机制。

流程对「substantial」（实质重大）变更的要求（F-rfcs-003）：

- 非 bugfix 的语言语义或语法变更
- 移除语言特性（含 feature-gated 的）
- `std` 的大型新增

无需 RFC 的变更（F-rfcs-004）：

- 改变形状但不改变含义的改写/重组
- 严格改善客观数值质量标准的添加（警告移除、提速、平台覆盖等）
- 仅被 Rust 开发者（而非用户）注意到的添加
- `std` 小型新增（仅需 ACP，即 API Change Proposal，见 std-dev-guide 的 feature-lifecycle 页）

## 提交流程与编号机制

README 规定的四步流程（F-rfcs-005）：

1. fork 仓库
2. 复制 `0000-template.md` 为 `text/0000-my-feature.md`
3. 填写并提交 PR（pull request，拉取请求）
4. 以 PR 编号重命名文件前缀（`0000-` 改为该编号）并更新文件顶部 "RFC PR" 链接

最反直觉的一条规则是：**提交时不预先分配 RFC 编号，编号即 PR 编号，RFC 被接受时文件相应重命名**（F-rfcs-006）。仓库没有独立编号机构——「RFC 3137」先是「PR #3137」，被接受后才固化为文件名。

这一机制的直接后果可以从目录统计读出（F-rfcs-165、F-rfcs-167）：

- `text/` 顶层实存 639 个 `.md` 文件（递归含子目录共 648 个）
- 文件编号横跨 `0001-private-fields` 到 `3984-libs-team-refactor`
- 639 个文件对 3984 个编号位，约 84% 的编号位置没有对应文件

每个编号空洞大致对应一个被关闭的 PR——**编号空洞本身就是提案存活率的化石记录**。从精读样本看，编号与 Start Date 大体单调对应（RFC 114 为 2014-07、RFC 3137 为 2021-05、RFC 3984 为 2026-07），因此可以用编号粗定位提案所处的时代。

命名模式统一为 4 位零填充编号 + 连字符 + 小写 kebab-case（短横线小写）描述名，如 `3137-let-else.md`、`0135-where.md`（F-rfcs-168）。多章节 RFC 用同名子目录存放额外页面：当前 `text/` 下存在 3 个子目录——`2856-project-groups`、`3392-leadership-council`、`3606-temporary-lifetimes-in-tail-expressions`（F-rfcs-166）。仓库根目录（排除 `.git/`）总文件数 665（F-rfcs-169）。

## FCP：最终评论期

FCP（final comment period，最终评论期）是 RFC 决策的核心机制（F-rfcs-007）：

1. subteam（子团队）成员提出 "motion for final comment period"（进入最终评论期的动议）并附处置意见（merge/close/postpone 三选一）
2. 进入 FCP 前，所有 subteam 成员必须 sign off（签署同意）
3. FCP 持续**十个日历日**（至少 5 个工作日），并在 This Week in Rust 等处公布
4. FCP 期间出现实质性新论点可取消 FCP，使 RFC 回到开发模式

FCP 结束后才进入合并或关闭。RFC 合并进仓库后的生命周期语义（active、修正案、postponed）详见 [RFC 生命周期与团队治理](/concepts/07-rfc-lifecycle-governance.md)。

## 模板：4 个元数据字段

`0000-template.md` 的头部仅 4 个字段（F-rfcs-013）：

| 字段 | 含义 | 示例 |
|------|------|------|
| Feature Name | 唯一标识符 | `my_awesome_feature` |
| Start Date | 提案日期（YYYY-MM-DD） | `2021-05-31` |
| RFC PR | 本 RFC 的 PR 链接 | `rust-lang/rfcs#3137` |
| Rust Issue | 实现追踪 issue 链接 | `rust-lang/rust#87335` |

头部格式本身是演化中的历史文献（F-rfcs-170）：2014 年的 RFC（0114、0160、0132、0214 等）仅 Start Date/RFC PR/Rust Issue 三字段且无锚点链接定义；2015-02 起（0911 起）增加 Feature Name 字段；较晚的 RFC（3137 等）章节头带 `[summary]: #summary` 式锚点链接定义。读 2014~2015 年的 RFC 要宽容格式差异。

## 模板：9 章节与「双解释」文体

正文共 9 个章节（F-rfcs-014）：Summary、Motivation、Guide-level explanation、Reference-level explanation、Drawbacks、Rationale and alternatives、Prior art、Unresolved questions、Future possibilities。

文体上最独特的是「双解释」设计——作者必须同时扮演两种角色：

- **Guide-level explanation**：像功能已包含在语言中那样向其他 Rust 程序员讲解，主要靠示例（F-rfcs-015）。实现导向 RFC（编译器内部）该节聚焦编译器贡献者视角；政策 RFC 该节提供政策示例驱动的介绍。
- **Reference-level explanation**：模板自述 "This is the technical portion of the RFC"——详尽到与其他特性的交互清晰、实现方式清楚、角落案例以示例剖析（F-rfcs-016）。

其余章节同样带有「诚实条款」：Drawbacks 与 Unresolved questions 必须真实填写（哪怕内容是 "None."，见 0050-assert 与 0214-while-let 的实例）；Prior art 节可含其他语言先例、其他社区做法、发表论文，但模板预先封死了「Swift 有所以我们要有」式论证——**其他语言的先例本身不足以构成 RFC 的动机**（F-rfcs-017）。

由此得到读 RFC 的标准顺序：**Summary 定位 → Motivation 估值 → Guide 建直觉 → Reference 核细节 → Drawbacks/Alternatives 求平衡**。

## 目录统计速览

作为本知识包信源的完整统计（详见[信源登记](/references/rfcs-source-map.md)）：

| 统计项 | 值 | 事实编号 |
|--------|-----|---------|
| text/ 顶层 .md | 639 个 | F-rfcs-165 |
| 递归 .md（含 3 个子目录） | 648 个 | F-rfcs-165、F-rfcs-166 |
| 编号范围 | 0001 ~ 3984 | F-rfcs-167 |
| 命名模式 | 4 位零填充 + kebab-case | F-rfcs-168 |
| 仓库总文件（排除 .git） | 665 个 | F-rfcs-169 |
| 头部格式演变 | 2014 三字段 → 2015 增 Feature Name → 晚期锚点链接 | F-rfcs-170 |

## 相关概念

- [RFC 生命周期与团队治理](/concepts/07-rfc-lifecycle-governance.md) — RFC 合并后的生命周期（active/修正案/postponed）与三团队分流准则
- [语言演进：表达式与模式](/concepts/01-lang-evolution-expr-pattern.md) — 以模板文体精读的第一批 RFC 实例
- [类型系统演进](/concepts/02-type-system-evolution.md) — 精读数量最多的主题家族
- [rust-lang/rfcs 信源登记](/references/rfcs-source-map.md) — 基线 commit、目录统计与 26 篇精读清单
