---
okf_version: "0.2"
type: Example
title: "示例：失败样本集：3 次沙箱越权、1 个 1.5、1 个 −73.25% 与 135 次零接受"
description: "按拦截点分组陈列 v1 与 V1 bench 的真实失败记录：沙箱、schema、正确但更差、cosim、placement 与两个对照组"
tags: [HWE Bench, 示例, 失败模式, 沙箱, 接受规则]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-14T17:40:00+08:00"
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

本示例把失败本身当展品：从固定提交 `4a137bb1378834ca3664a1c971684777eb5f364a` 的 v1 log.jsonl 与 V1 bench 排行榜里，按**拦截点**分组取出真实记录——3 次评测前沙箱越权、1 个写代码前被 schema 拒绝的 1.5、3 个门全过却被比较闸拦下的大回归（最差 −73.25%）、5 个死于 cosim 的实现、4 个没布上线的存储结构，以及两个无 LLM 对照组的 135 次与 42 次失败。每组回答三件事：怎么发生的、哪个门/规则起了作用、它是不是一次「假失败」。

这是静态走读：记录逐字摘引（长 JSON 只保留说明问题的字段并注明省略），未运行任何门或复跑 rep；fitness/Fmax 等数字均为作者报告，计数以 pinned 日志的 Python 解析为准（F-097/K-2）。

## 沙箱组：三次 test/_helpers.py，全部评测前拒绝

三条 broken 记录分别摘自 [L11](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L11)/[L26](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L26)/[L71](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L71)，下列数组为汇编展示、每行只保留四字段：

```json
[
  { "id": "hyp-20260428-004-r4s0",  "title": "Hot-Bit ALU Result Mux",
    "outcome": "broken", "error": "sandbox_violation: agent touched off-limits paths: ['test/_helpers.py']" },
  { "id": "hyp-20260428-019-r9s0",  "title": "Hot-Cold ALU Opcode Split",
    "outcome": "broken", "error": "sandbox_violation: agent touched off-limits paths: ['test/_helpers.py']" },
  { "id": "hyp-20260428-064-r24s0", "title": "Unsigned Multiplier With Signed High Correction",
    "outcome": "broken", "error": "sandbox_violation: agent touched off-limits paths: ['test/_helpers.py']" }
]
```

三个想法各不相同，犯错方式完全一样：想在白名单外新建共享测试辅助文件。拦截是双重的——schema 的 `changes[].file` 正则只放行 `rtl/**` 与 `test/test_*.py`（F-027），运行时沙箱再以 CONTRACT_PATHS 白名单与契约文件指纹兜底，任何不一致在**任何评测运行之前**直接判 `broken: sandbox_violation`（F-022/F-039/F-041/F-044）。博客同段叙述称 "Two separate hypotheses"（[blog L71](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/docs/auto-arch-tournament-blog-post.md#L71)），日志实测为三次，以日志为准（F-044）。机制全景见 [/concepts/03-worktree-sandbox.md](/concepts/03-worktree-sandbox.md)。

## schema 组：一个 1.5，代码一行都没生成

r6s2 是全表唯一的 schema 失败（[L19](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L19)，原行仅 10 字段）：

```json
{
  "id": "hyp-20260428-012-r6s2",
  "title": "experiments/hypotheses/hyp-20260428-012-r6s2.yaml",
  "outcome": "broken",
  "error": "schema_error: 1.5 is not of type 'integer'\n\nFailed validating 'type' in schema['properties']['expected_impact']['properties']['fitness_delta_pct']:\n    {'type': 'integer'}\n\nOn instance['expected_impact']['fitness_delta_pct']:\n    1.5"
}
```

`fitness_delta_pct` 声明为 integer，填 1.5 在假设阶段就被 JSON Schema 拒绝，实现代理根本没被调用（F-026/F-102）。title 字段落成 YAML 路径本身，也说明这份产出未通过规范化解析。作者评语：这类东西没有 schema，就会变成管线后段一次静默类型强转（[blog L73](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/docs/auto-arch-tournament-blog-post.md#L73)）。schema 的字段级规则见 [/concepts/01-hypothesis-schema.md](/concepts/01-hypothesis-schema.md)。

## 「正确但更差」组：门全过的 −73.25%

最危险的失败不是 broken，而是全门通过的烂设计。r24s2（[L73](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L73)，字段有精简）：

```json
{
  "id": "hyp-20260428-066-r24s2",
  "title": "Registered Lookahead JALR Target Predictor",
  "category": "predictor",
  "outcome": "regression",
  "formal_passed": true,
  "cosim_passed": true,
  "fmax_mhz": 52.99,
  "fitness": 154.53,
  "delta_pct": -73.25,
  "lut4": 6378
}
```

它发生在峰值 577 已锁定之后的 round 24：formal 与 cosim 全过、RTL 行为正确，但 Fmax 中位数塌到 52.99 MHz、fitness 154.53，比现任冠军低 73.25%。接受规则无 target 时是严格 `>`，regression 只丢 worktree 不合入（F-015/F-082），于是被「与基线比较」闸拦下（F-104）。博客的反事实评注逐字："Accepted into trunk, that one mistake undoes every previous win in a single round."（[blog L72](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/docs/auto-arch-tournament-blog-post.md#L72)）。同组还有两条次差（F-105，精简自 [L27](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L27)/[L14](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L14)）：

| 槽位 | 想法 | formal/cosim | fitness | delta |
|---|---|---|---:|---:|
| r9s1 | Store-Slot-Aware Fetch Skid Queue | true/true | 166.23 | −58.19% |
| r5s0 | Explicit MEM Byte-Lane Steering | true/true | 166.75 | −48.61% |

接受规则视角见 [/concepts/09-accept-rule-outcomes.md](/concepts/09-accept-rule-outcomes.md)。

## cosim 组：5 个实现死在对拍门

9 个 broken 中 5 个死于 cosim（F-065/F-102），error 精确到程序：

| 行 | 槽位 | 想法 | error |
|---|---|---|---|
| [L2](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L2) | r1s0 | Move DIV/REM off the single-cycle ALU path | cosim_failed: selftest.elf |
| [L8](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L8) | r3s0 | Operand-Aware Load-Use Interlock | cosim_failed: selftest.elf |
| [L54](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L54) | r18s1 | Decode-Exact Load-Use Interlock | cosim_failed: selftest.elf |
| [L66](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L66) | r22s1 | Replay-Assisted ALU Pair Dual Issue | cosim_failed: selftest.elf |
| [L57](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L57) | r19s1 | Backend-Stall Shadow I-Fetch Prefetcher | cosim_failed: coremark.elf |

前四个死在 selftest 普通 ELF 的全 RVFI trace 对拍，第五个连过 selftest 却死在 coremark.elf 的 CRC/迹门（两段短路口径 F-061）。r1s0 是本集唯一「死后成名」的案例——约两小时后改写为 r6s0 拿下 +15.7%，完整故事见 [/examples/00-cold-div-reincarnation.md](/examples/00-cold-div-reincarnation.md)。对拍机制见 [/concepts/06-cosim-iss.md](/concepts/06-cosim-iss.md)。

## placement 组：4 个 structural 存储尝试只活 0-1 个种子

4 条 placement_failed 全部是 structural 类存储结构（F-103），日志 seeds 数组为 None 即该种子未布通：

| 行 | 槽位 | 想法 | seeds（MHz） |
|---|---|---|---|
| [L9](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L9) | r3s1 | Two-Entry Retiring Store Buffer | [None, None, None] |
| [L45](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L45) | r15s1 | Two-Entry Pending Store Slot | [None, None, None] |
| [L48](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L48) | r16s1 | Same-Cycle Store Slot Refill | [None, None, None] |
| [L72](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L72) | r24s1 | Replay-Fed Memory Plus ADDI Pair Issue | [49.43, None, None] |

规则是 3 个 nextpnr 种子至少 2 个布局成功才给分；单幸存者的中位数不被承认（F-068/F-071）。r24s1 最直白：唯一布通的种子也只有 49.43 MHz，另两个直接失败——这不是坏运气，是设计在该器件上的物理现实。3-seed 与中位数口径见 [/concepts/07-fpga-fitness.md](/concepts/07-fpga-fitness.md)。

## 对照组的失败：135 次零接受与一次 42 连坏

无 LLM 对照组的失败承担「门到底有没有在工作」的举证。V1 random-mutation 三 rep、每 rep 46 iters（1 次基线 retest + 45 候选），候选全部首败，失败类只有一种（[L159-L163](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/LEADERBOARD.md#L159-L163)）：

```text/markdown
### `random-mutation`
| Class | Count |
|---|---|
| `formal_failed` | 135 |
```

per-rep 三行（[L219-L221](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/LEADERBOARD.md#L219-L221)）均为 1 acc/0 rej/45 brk、282.8 → 282.8。但这 135 的**计数口径被播种污染**：V2 披露 V1 random 实为 "3 draws repeated 45 times"（[v2.html L364-L365](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/site/v2.html#L364-L365)）；修复后 V2 的 135 次独立抽取仍是 0 接受——117 次挂 formal、12 次挂 cosim、6 次过全门但 no-op（[v2.html L242-L247](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/site/v2.html#L242-L247)，F-121）。引用裁决（K-6）：**「盲改不产生胜场」的结论成立，但证据应引 V2 独立抽取版，不引 V1 的 135 重复计数。**

static 对照则展示了一次 harness 侧事故：rep1 = 1acc/3rej/42 hypothesis_gen_failed，rep2 = 1acc/45rej/0brk（[L222-L223](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/LEADERBOARD.md#L222-L223)，F-113）。static 是不产假设、不改 RTL 的空操作桩（F-031），健康形态应如 rep2：过门后以不变 fitness 被记 45 regression；rep1 的 42 连坏是桩/环境事故（F-113 标 INCIDENT），不解读为模型能力。harness 故障方向与遥测见 [/concepts/16-harness-reliability.md](/concepts/16-harness-reliability.md)。

## 总表：失败类型 → 拦截点 → 是否假失败

| 失败类型 | 拦截点（门/规则） | 记录 | 是否假失败 |
|---|---|---|---|
| 沙箱越权 ×3 | 文件白名单 + 契约指纹，评测前 | L11/L26/L71 | 否，真实越权（F-044） |
| schema 1.5 ×1 | JSON Schema integer 校验，动代码前 | L19 | 否（F-026/F-102） |
| 门全过的大回归 ×3 | 与现任冠军严格 `>` 比较 | L73/L27/L14 | 否，「正确但更差」必须丢（F-104/F-105） |
| cosim 失败 ×5 | selftest/coremark 全 trace 对拍 | L2/L8/L54/L57/L66 | 否；r1s0 修实现后胜（F-065） |
| placement ×4 | ≥2/3 种子布通才计分 | L9/L45/L48/L72 | 否，器件物理现实（F-103） |
| V1 random formal ×135 | riscv-formal | L159-L163 | 失败真实，计数口径污染（K-6）；以 V2 135 独立抽取为准（F-121） |
| static rep1 hyp_gen ×42 | （无门可拦）对照桩事故 | L222 | 是 harness 侧事故，rep2 恢复即反证（F-113） |

读这张表的要点：前六行都是真拒绝而非误杀——验证器的设计取向是「宁可假失败、不可假通过」，故障方向只能产生假失败、不能产生假通过（F-005 的 verifier 论点，事故方向分析见 F-126 与 [/concepts/16-harness-reliability.md](/concepts/16-harness-reliability.md)）；唯一需要加注的是测量口径（K-6）与 harness 事故（F-113/F-126），它们影响证据表述，不改变结论方向。

## 相关概念与示例

- [/concepts/03-worktree-sandbox.md](/concepts/03-worktree-sandbox.md)：白名单、指纹与「评测前拒绝」
- [/concepts/05-formal-altops.md](/concepts/05-formal-altops.md)：random 135 次首挂的 formal 门证明了什么
- [/concepts/09-accept-rule-outcomes.md](/concepts/09-accept-rule-outcomes.md)：三结果类与 −73% 为什么必须丢
- [/concepts/14-v1-leaderboard.md](/concepts/14-v1-leaderboard.md)：失败模式谱与两个对照的完整排行口径
- [/concepts/15-v2-holdout.md](/concepts/15-v2-holdout.md)：135 次独立抽取与 V1/V2 不可比
- [/concepts/16-harness-reliability.md](/concepts/16-harness-reliability.md)：故障方向、事故标注与遥测重建
- [/examples/00-cold-div-reincarnation.md](/examples/00-cold-div-reincarnation.md)：cosim 组 r1s0 的后文——同一想法如何改写为 +15.7% 胜场
- [/examples/01-opus-983-rep.md](/examples/01-opus-983-rep.md)：同一份 LEADERBOARD 的胜方视角——983.2 rep 如何把 22% pass-rate 与 +248% 增益并列读
- [/examples/index.md](/examples/index.md)：HWE Bench 束示例索引与三篇的阅读路径
