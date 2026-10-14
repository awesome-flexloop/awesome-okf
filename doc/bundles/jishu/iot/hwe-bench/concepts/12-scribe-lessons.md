---
okf_version: "0.2"
type: Concept
title: "经验积累：append-only LESSONS.md、scribe 角色与 lessons 消融"
description: "scribe 是 231 行的 append-only 角色，每轮只许追加一条教训；V2 消融显示 lessons 文件在该设置下无显著贡献"
tags: [HWE Bench, scribe, LESSONS.md, 运维经验, 消融实验]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-14T16:40:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-14T19:30:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: hwe-facts
    resource: /references/facts.md
    title: "HWE Bench 事实登记表 F-001~F-126"
  - id: hwe-pinned
    resource: "https://github.com/FeSens/auto-arch-tournament/tree/4a137bb1378834ca3664a1c971684777eb5f364a"
    title: "HWE Bench 固定提交 4a137bb"
---

## 是什么：scribe 是「只追加经验」的第四角色

四个 agent 角色里，hypothesis 出假设、implement 改 RTL，**scribe 只负责写教训**：它从每轮的结局与 RTL diff 里蒸馏一句话，追加到 `cores/<target>/LESSONS.md`（F-030，[scribe.py L1-L8](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/scribe.py#L1-L8)）。scribe.py 共 231 行，硬约束有两条（F-030）：

- **唯一副作用是一次 append**：可写面被正则 `^cores/<target>/LESSONS\.md$` 限死（[L40-L42](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/scribe.py#L40-L42)），碰任何其他路径都会被 `git checkout HEAD --` 回滚并抛 PermissionError（[L196-L212](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/scribe.py#L196-L212)）；
- **240s 超时**（`SCRIBE_TIMEOUT_SEC = 240`，[L24](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/scribe.py#L24)）。注释记录了调参史：120s 曾在教训已落盘后杀掉 agent，使 scribe_skipped 标志与事实不符，240s 是成功轮次的实测上限加余量（[L16-L23](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/scribe.py#L16-L23)）。

## 怎么实现：append-only 是被代码强制的，不是提示词请求

「只追加不改写历史」不是一句 prompt 叮嘱，而是落盘后校验（[L214-L229](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/scribe.py#L214-L229)）：读后文本必须**以旧文本开头**；若 scribe 重写了 LESSONS.md，文件恢复旧内容并抛 PermissionError，注释原话是 "we'd rather lose the lesson than silently lose history"。函数 docstring 解释了为什么历史不能改写：追加契约是 hypothesis prompt 与 git 历史共同依赖的前提（[L136-L141](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/scribe.py#L136-L141)）——后一轮 agent 读到的第 N 条教训，必须与提交历史里第 N 轮留下的内容逐字一致，否则教训账本与代码账本对不上账。若文件原本不存在则新建且只含那一条；若 scribe 什么都没写，函数返回 None、不产生副作用。它自己的 .scribe.log 与 last-message 文件在沙箱检查前必被清除，以免污染下一轮假设侧沙箱（[L168-L194](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/scribe.py#L168-L194)）；若它误触 log.jsonl，回滚会跳过日志以保住同事务内在途 append（[L200-L209](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/scribe.py#L200-L209)）。

prompt 本身（[L67-L130](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/scribe.py#L67-L130)）要求**至多一条** bullet，格式 `YYYY-MM-DD <id> (<outcome>, <delta_pct>): <one-sentence lesson>`；教训要写「为什么」且可泛化，不得写一次性笔误；原因不清、纯笔误、重复旧教训时必须 SKIP（不写任何文件）。prompt 给出的正反例很能说明口味：好教训形如「双发射没有 2W 寄存器堆会制造 WAW 冒险，被 riscv-formal 的 reg 检查抓到」「64 项 BHT 让 CoreMark 退步——默认不跳转分支在这个分支画像上已调好」——点名具体 RTL 构造与 gotcha；坏教训是只复述发生了什么。嵌入 prompt 的 RTL diff 上限 8000 字符，注释说明 30KB 全量 diff 与 8KB 摘要的教训含量相同（[L26-L29](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/scribe.py#L26-L29)）。

与另两个 LLM 角色相比，scribe 的写面和时长都小得多：hypothesis 1200s、implement 1800s 且是唯一可写 rtl/ 与 test/test_*.py 的角色（F-028/F-029），scribe 240s 且只能动一个 Markdown；static/random 两个无 LLM 对照则不产生教训（F-031/F-032）。

## 触发时机：每槽 append_log 之后

scribe 在**每个槽位 append_log 之后**被调用，运行在 orchestrator 的 `_LOG_LOCK` 之内（scribe.py 文件头 docstring 亲述，[L4-L7](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/scribe.py#L4-L7)；编排侧 append_log+scribe 步骤见源码地图 orchestrator 条目）。即教训的写入与账本行的写入在同一事务附近完成，先有结局行、再有教训句，下一轮 hypothesis 才能读到历史。一轮编排中四角色的相对位置见 [02-round-orchestration](/concepts/02-round-orchestration.md)。

它拿到的输入严格限定为该槽日志条目加 diff（函数 docstring 列明，[L143-L149](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/scribe.py#L143-L149)）：id/title/category/outcome/delta_pct/error、嵌套 hypothesis 对象、implement 角色的 implementation_notes，以及 `_capture_slot_diff` 抓到的 RTL diff；hypothesis-gen 失败、没有 worktree 时 diff 为空字符串。它不读 formal 报告、不读 FPGA 日志，因此教训的视野本就被设计成「结局 + 代码改动」，而不是全量评测证据。

## 沉淀了什么：research/lessons.md 的两条运维规则

需要区分两个文件：scribe 的运行时产物是 `cores/<target>/LESSONS.md`，固定提交的 cores/ 下并不存在该文件（本地镜像递归清点亲验——它是运行时生成、随克隆剥离的文件）；真正沉淀进仓库的是 [research/lessons.md L2-L18](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/research/lessons.md#L2-L18)，只有两条日期命名的运维规则（F-034）：

1. **2026-07-16，机械式 prompt parser 会轮流坏**：random/static 各有一份私有的同 bug 左匹配 parser，burn-in N=2 抓到了 random 的、N=1 放过了 static 的，后者烧掉一个生产 E1a rep。由此固化三条规则：机械 agent 共用一个加固 parser；每个 prompt-parsing agent 以 **N≥2 轮 burn-in**；集成测试用 hypothesis.py 构造**真实 round-2 prompt** 断言 id 抽取，让这一类 bug 无法再次出货。
2. **2026-09-23，agent 运行时读到的是宿主而不只是克隆**：Codex 的 workspace-write 沙箱只限写不限读且放行 /tmp；默认 CODEX_HOME 会暴露操作者记忆，login shell 会带入无关 PATH。由此固化三条规则：每个克隆独立 CODEX_HOME（关记忆、无 login shell）；发布成果与研究文件从克隆中剥离；新运行首 rep 实时监看 shell 命令是否访问克隆外路径——三次停摆都是监看发现的，不是门发现的。

两条规则有一个共同形状：它们都不是 RTL 设计经验，而是**让无人值守的自治运行不被自身环境欺骗**的工艺纪律；教训来自烧掉的生产 rep，再被写回 runner 与 prompt 本身。

## 为什么克隆时要主动剥离：防训练泄漏

第二条规则中的「剥离」由 bench runner 机械执行（F-116）：克隆时剥离成果/研究目录、删 tag、造无父根提交并 gc（runner.py L267-L398），fixture 为 orphan 提交+tag 成对重建，遥测则从 git 全引用+reflog 事后重建 log.jsonl。这样每个被测模型拿到的起跑线都不含前人（含更聪明模型）留下的 LESSONS 与成果文件，「读历史」不构成跨模型信息泄漏。完整可靠性设计见 [16-harness-reliability](/concepts/16-harness-reliability.md)。

## V2 lessons 消融：1.02x 与它的解读边界

经验文件到底有没有用？V2 做了受控实验（作者报告，F-122，[v2.html L248-L252](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/site/v2.html#L248-L252)）：GPT-6.1 Sol **不带 lessons 文件再跑 6 次**，full vs no lessons = **1.02x，95% CI 0.91-1.14，p=0.68**，区间排除了 lessons 文件带来 **>14%** 增益的可能，结论为 "Not distinguishable"。

解读边界必须同时给出：

- 该结论只针对**该模型（GPT-6.1 Sol）、该 bench 版本、6 runs 的功效**，换模型、换口径都需要重新实验；
- 6 runs 只能分辨约 20% 差距、分辨不了层内 6-10%（F-119），CI 0.91-1.14 与小效应相容，它排除的是「>14% 的大增益」而非任何效应；
- 它不能泛化为「经验积累无用」，更不能否定两条运维规则的价值——它们防的是 harness 事故与训练泄漏，本来就不直接产生分数。

V2 排名口径的整体变化见 [15-v2-holdout](/concepts/15-v2-holdout.md)。

## 边界

- scribe 产出的是**运维/工艺经验**（模式、gotcha、设计约束），不是 RTL 事实：它不参与 formal/cosim/FPGA 任何一道门，formal 与契约指纹也不覆盖它写的句子；RTL 事实以门与日志为准。
- 「无显著贡献」是统计口径结论而非机制证明：消融只覆盖一个模型设置，且 CI 上界 1.14 并未排除小效应。

## 相关概念

- [一轮编排：N 槽锦标赛、四个角色与门的短路顺序](/concepts/02-round-orchestration.md)
- [V2 演进：6×6 几何均值、holdout 主榜与三门正确性缺口](/concepts/15-v2-holdout.md)
- [自治 harness 可靠性工程：故障方向、误删事故与遥测重建](/concepts/16-harness-reliability.md)
