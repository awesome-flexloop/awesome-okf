---
type: Concept
title: RFC 生命周期与团队治理
description: RFC 的 active/postponed 生命周期语义、lang/compiler/libs 三团队的分流准则、关键字保留与 2026 年库团队重组 RFC
tags: [rust, rfcs, governance, lifecycle, fcp, teams, keywords]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rfcs-source
    resource: /references/rfcs-source-map.md
---

# RFC 生命周期与团队治理

RFC 通过之后发生什么？本篇回答流程的「下半场」：active 的确切语义（008）、修正案规则（009）、postponed（010）、提交前准备（011）、许可证（012），以及 lang/compiler/libs 三团队截然不同的分流准则（025~033）。收尾于 0342-keywords（保留关键字的治理工具）与 3984（2026 年库团队重组 RFC，证明该流程至今活跃）。

## active 只是入场券

RFC 以 markdown 文件合并进 RFC 仓库后即为 "active"，作者可实现它并向 Rust 仓库提 PR（F-rfcs-008）。但 README 明文规定三个「不蕴含」：

- "active" **不是橡皮章**
- 不意味着功能最终合并
- 不蕴含实现优先级或开发人员分配

**RFC 通过 ≠ 官方承诺实现**——这是评估任何语言特性现状时最重要的纠偏。活跃 RFC 列表由 rfcbot.rs 追踪（见 [RFC 流程与模板](/concepts/00-rfc-process-and-template.md) 的 README 首行，F-rfcs-001）。

### 修正案与「不接受实质修改」

已接受的 RFC 不应被实质性修改，仅极小变更（very minor change，判定归 sub-team）可作为修正案提交；更重大的变更应写成新 RFC 并在原 RFC 上加注（F-rfcs-009）。

### postponed：无正式流程的重开

被 "postponed" 标签关闭的 RFC 表明团队在将来之前既不想评估也不想实现该特性；历史上 postponed 被用于推迟到 1.0 之后；**postponed 的 PR 可在时机合适时重开，无正式流程**（F-rfcs-010）。实例见 [异步与借用](/concepts/04-async-and-borrowing.md)：RFC 2592 自述为更早 futures RFC（PR 2418）的修订精简版——后者被推迟至 nightly 获得更多经验后重提（F-rfcs-109）。

更罕见的形态是「批准后部分拒绝」：RFC 3192 的头部声明 Provider 接口被 libs team 会议拒绝、剩余的 Demand 类型重命名为 Request（F-rfcs-125，详见 [编译器架构演进](/concepts/05-compiler-arch-evolution.md)）。

### 提交前准备与许可证

提交前的常见准备（F-rfcs-011）：官方 Zulip 服务器（rust-lang.zulipchat.com）、开发者讨论论坛（internals.rust-lang.org）、偶尔发 "pre-RFC"；本仓库的 issue 可用于讨论但团队不主动查看。

许可证状态（F-rfcs-012）：仓库正在按 Apache License 2.0 或 MIT 双许可的过渡过程中；详情指向 RFC 2044 及其 tracking issue（rust#43461）；除非明确声明，贡献按 Apache-2.0 定义双许可。

## 三团队分流：RFC 成本本身是架构决策的输入

RFC 仓库不是所有变更的必经之路——三团队的分流策略截然不同。

### lang 团队：几乎每个变更都需要 RFC

lang_changes.md 规定（F-rfcs-025）：语言层面**几乎每个变更**都需要 RFC；新 lint（或对现有 lint 的重大变更）视为语言变更；语言 RFC 由语言子团队管理并标记 `T-lang`；新 PR 在提交**一周内**完成初始 triage（分诊）——结果为指派 shepherding（ shepherd，守护人制度）/ 以 postponed 关闭 / 以「明确不该做」关闭。

lang 的修正案规则（F-rfcs-026）：小变更（本质 bug fix、与已接受 RFC 精神一致）通过 RFC PR 修正原 RFC；变更剧烈时创建独立新 RFC 并在原 RFC 加注释引用。判定指引：变更影响 RFC 多于一处（非局部）、影响原 RFC 对动机用例的适用性、存在多种新方案——任一成立则不算 minor。

### compiler 团队：主场是 MCP 而非 RFC

compiler_changes.md 明确：**「大多数超出简单 PR 范围的编译器决策使用 MCP 而非 RFC」**（F-rfcs-027）——MCP 链接指向 rust-lang/compiler-team issues。RFC 仓库自己不是编译器决策主场。

需要 RFC 的编译器变更（F-rfcs-028）：复杂设计空间且涉及其他团队的重大用户可见编译器变更（示例为 path sanitization，链至 rfcs PR 3127）、造成编译器/语言/库 stable 行为重大向后不兼容的其他变更。不需 RFC 的：bug 修复与错误消息改进、小重构、大型内部重构（需 MCP）、实现已有接受 RFC 的语言特性、新 lint（归 lang 团队，建议先在 clippy 试用后 uplift）、稳定编译器 flag 变更（需在某处 FCP）。

### libs 团队：do whatever is easiest

libs_changes.md 的哲学一反直觉（F-rfcs-030）："do whatever is easiest"——**若写 RFC 比实现工作量小，这本身就是需要 RFC 的信号**；预期争议可直接走 RFC；新 API 几乎必然值得 RFC（"new APIs almost certainly merit an RFC"）。

RFC 开销的事实数据（F-rfcs-029）：RFC 从发帖到落地**最少 2 周**，争议性变更实际可达数月量级；RFC 需要多数 subteam 审查与正式投票；RFC 不能按复杂度降级（"Full process always applies"）；而 PR 可被任何 rust-lang 贡献者 insta-merge（即时合并）、可经 bors/buildbot/trains 乐观接受。

libs 的 PR/RFC 判定清单（F-rfcs-031）：

| 走 PR | 走 RFC |
|-------|--------|
| bugfix、docfix | 新 API |
| 明显 API 空缺修补（对称类型补 API：`Vec<T> -> Box<[T]>` 推出 `String -> Box<str>`） | 稳定 API 语义变更 |
| 不稳定 API 微调 | 稳定 API 泛化（例 Pattern/Borrow） |
| 实现 Clone/Debug 等「明显」trait | 稳定 API 弃用 |
| | 非平凡 trait impl |

**insta-stable 陷阱**（F-rfcs-032）：以 unstable 合并的非 RFC PR 需有 feature gate 与 tracking issue，但 "trait impls and docs are insta-stable and thus have no tracking issue"——trait 实现与文档是即时稳定的、没有追踪 issue，因此对此类变更需要**更高审查强度**。

### libs 的稳定化周期

每个发布周期结束时 libs team 评估当前不稳定 API 并选择部分在下周期 FCP 稳定化（F-rfcs-033）；FCP 后 API 的三条路径：Stabilize / Deprecate / Extend the FCP（仍无法达成共识时考虑要求新 RFC 或以 "too controversial for std" 弃用）；beta 期发现新稳定 API 的问题时**强烈倾向于回退稳定**。

## 0342-keywords：保留关键字作为治理工具

RFC 342（Start Date 2014-10-07，Rust Issue rust#17862）保留 `abstract`、`final`、`override` 为可能的关键字（F-rfcs-162、F-rfcs-163）。

Motivation：意图为 Rust 添加更高效的继承机制（引用 RFC PR #245、#250 及 discuss 线程），任何实现都可能使用 `virtual`（已使用、保持保留）、`abstract`、`final`、`override`。Detailed design 全文只有一句："Make `abstract`, `final`, and `override` reserved keywords."（F-rfcs-163）。

全文 35 行、6 个二级章节、Unresolved questions 内容 "N/A"（F-rfcs-164）——**一篇 RFC 的全部内容可以是三个单词的保留**。这是「先占位、防未来破坏」的治理手法：在继承机制的提案远未成熟时，先锁住词汇空间，避免未来引入关键字时破坏现有代码。它的现代对应物是 Edition 机制（见 [标准库与生态演进](/concepts/06-std-ecosystem-evolution.md)）：新关键字（如 2388 的 `try`）经由新 edition 的 opt-in 获得，不再需要提前十年保留。

## 3984-libs-team-refactor：流程至今活跃

目录中编号最大的 RFC 3984（Feature Name: N/A，Start Date 2026-07-15，Rust Issue: N/A）提议**重新组织库团队**——重定义并重命名成员资格类别、改变团队成员选择方式、文档化成员与维护者期望、定义团队的 FCP 处理方式；Motivation 引用 team 仓库 PR 588（2021 年设定的现有结构）（F-rfcs-174）。

两点值得注意：其一，**团队治理本身也走 RFC**——组织架构变更与语言特性变更使用同一流程；其二，RFC 流程从 0002（2014-03-11，流程定义本身，F-rfcs-171）到 3984（2026-07-15）跨越十二年仍在活跃运转，是本知识包全部内容的治理底座。

## 相关概念

- [RFC 流程与模板](/concepts/00-rfc-process-and-template.md) — 流程的「上半场」：提交、编号与 FCP 机制
- [编译器架构演进](/concepts/05-compiler-arch-evolution.md) — 3192-dyno 的「先批准后部分拒绝」案例
- [异步与借用](/concepts/04-async-and-borrowing.md) — 2592 对 2418 的推迟-重提关系
- [标准库与生态演进](/concepts/06-std-ecosystem-evolution.md) — libs 准则适用的 std API 变更与 Edition 机制
- [rust-lang/rfcs 信源登记](/references/rfcs-source-map.md) — 三团队准则文件路径与 3984 元数据
