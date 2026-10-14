---
okf_version: "0.2"
type: Concept
title: "假设即数据：JSON Schema、五类 hypothesis 与 ID 账本"
description: "假设在 HWE Bench 中是受 JSON Schema 约束的数据：7 必填字段、rNsM ID 账本、五类枚举与文件级白名单，门在写代码前先拦形状"
tags: [HWE Bench, 假设Schema, JSON Schema, 假设账本]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-14T16:00:00+08:00"
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

## 七必填字段：假设先成为数据，才允许动代码

[hypothesis.schema.json](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/schemas/hypothesis.schema.json#L4) 把假设规定为一个 JSON 对象，7 个字段全部必填（F-023）。逐条看 schema 对形状的约束（L4-L30 亲验）：

- **id**：见下节的正则与账本；
- **title**：`minLength: 5`，拒绝四字以下的标题；
- **category**：五值枚举，见下节；
- **motivation** / **hypothesis**：各自 `minLength: 20`，动机与假设陈述都必须成段；
- **expected_impact**：对象，见后文的 integer 纪律；
- **changes**：数组且 `minItems: 1`，见后文的文件级白名单。

也就是说，「一句话想法」在形状层就不被接受；schema 不读语义，但强制假设具备可追溯的最小信息量。

## ID 正则：从文件名到 commit 的统一账本

id 必须匹配 `^hyp-[0-9]{8}-[0-9]{3}(-r[0-9]+s[0-9]+)?$`（F-024）：前半是日期加当日序号（如 `hyp-20260428-054`），运行时再带 `-r<轮>s<槽>` 后缀（如 `r20s2`）。这个 ID 同时充当 YAML 文件名、worktree 目录名、log.jsonl 行标识与合并 commit message 的关联键（F-018）；v1 冠军核在 core.yaml 记录的 source_id 就是 `hyp-20260428-054-r20s2`（F-096），假设因此成为一份可用 git 与日志交叉追溯的账本。

K 槽并行时，ID 不由各槽自取，而是编排器在每轮开始前统一预分配。[tournament.py L74-L93](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/tournament.py#L74-L93) 的注释写明，预分配修的是两个槽并发调用 `_next_id` 抢到同一序号的竞争；后缀可选的正则同时兼容旧的 `hyp-YYYYMMDD-NNN` 形态（亲验）。

```text
  hyp-20260428-054-r20s2
       |        |    |  |
       日期     序号 轮  槽  -> YAML 文件名 / worktree 目录 / log 行 / commit message
```

## 五类枚举：schema 给五类，v1 实跑只用三类

category 是五值枚举：`micro_opt` / `structural` / `extension` / `predictor` / `memory`（F-025）。但 v1 的 73 个假设实际只落在三类上：structural 25 个、micro_opt 24 个、predictor 24 个；memory 与 extension 一次都没有被使用（F-099）。每轮各槽的类别提示由编排器按槽位轮转给出（机制见[概念 02](/concepts/02-round-orchestration.md)）。

## integer 纪律：1.5 在生成任何代码之前就被拒

expected_impact 必填 `fitness_delta_pct` 与 `confidence`，后者取 `low`/`medium`/`high`；其中 `fitness_delta_pct` 在 schema 中声明为 **integer**（F-026）。这不是格式洁癖：v1 实有一例 r6s2 把它填成 1.5，结果在任何 RTL 生成之前就被 schema 拒绝，成为 9 个 broken 中唯一的 schema_error（F-102，log.jsonl L19）。

容错规范化对此刻意不松手：规范化函数只修 YAML 杂符与路径前缀，docstring 明确写着「deliberately do NOT coerce `expected_impact`」——这类失败是基准应当记录的真实模型行为，不能被糊过去（[hypothesis.py L345-L405](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/hypothesis.py#L345-L405)，F-028；亲验）。该失败实例见 [/examples/02-failure-gallery.md](/examples/02-failure-gallery.md)。

## changes[].file：写进 schema 的文件级白名单

changes 数组 `minItems=1`，每项必填 file 与 description；file 必须匹配 `^(rtl/[^.].*|test/test_[^/]+\.py)$`（F-027）。含义有两层：

1. 假设在**提案阶段**就得声明要动哪些文件，不能先改后说；
2. 声明得出的路径只能是 `rtl/` 下任意文件，或 `test/test_*.py` cocotb 测试——schema 字段描述直接写明其他路径会被运行时沙箱拒绝（F-027）。

模型若把路径写成长形式 `cores/<target>/rtl/foo.sv`，规范化函数会剥掉 `cores/<target>/` 前缀使其合法（同 F-028 亲验段）；但无论 schema 还是规范化，都不会放行 rtl/ 与测试之外的路径。这道白名单在运行时还有第二道强制执行，见[概念 03](/concepts/03-worktree-sandbox.md)。

## hypothesis 角色：1200s、YAML 容错与一次重试

schema 的对面是 hypothesis 角色（hypothesis.py，567 行）：产出 YAML、对白名单外改动做回滚、1200s 超时（方法学记 20 min）（F-028）。YAML 在送校验前先经过容错规范化（修复尾随杂括号、剥路径前缀，F-028 的 L345-L405）；agent 非零退出时**只重试一次**，且以追加方式保留第一次的流式日志作为排错证据（[hypothesis.py L480-L499](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/agents/hypothesis.py#L480-L499)，F-028；亲验）。

校验发生在单槽链路的 Phase 1b：`jsonschema.ValidationError`、`FileNotFoundError`、`yaml.YAMLError` 任一出现即判 `broken: schema_error`，而 worktree 在其后一个阶段才创建（[tournament.py L295-L308](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/tournament.py#L295-L308)，亲验）——坏假设不消耗任何 EDA 时间。

## 为什么这样设计，以及边界

把假设做成机器可验的数据，第一道门就前移到了跑代码之前：形状不合格的假设零 EDA 成本出局，且失败原因结构化、可在日志中分类计数（F-102 的 1 例 schema_error 与假设生成失败因此可区分）。

但 schema 只校验**形状**，不校验想法质量：v1 的 51 个 regression 全部 schema 合法、全门通过，只是 fitness 没有严格超过冠军（F-099）；甚至 -73.25% 的最差回归也带着合法假设过门（F-104）。想法好不好，由验证器与接受规则回答，不由 schema 回答——接受规则见[概念 09](/concepts/09-accept-rule-outcomes.md)。

## 相关概念

- [一轮编排：N 槽锦标赛、四个角色与门的短路顺序](/concepts/02-round-orchestration.md)
- [隔离与信任边界：git worktree、路径白名单与契约指纹](/concepts/03-worktree-sandbox.md)
- [接受规则：严格大于、三结果类与搜索的单调形状](/concepts/09-accept-rule-outcomes.md)
