---
okf_version: "0.2"
type: Example
title: "示例：同一想法的两次生命：r1s0 cosim 之死与 r6s0 Cold DIV/REM +15.7%"
description: "跟踪同一个除法器想法的两次尝试：r1s0 死于 selftest cosim，约两小时后 r6s0 冷多周期单元拿下 +15.7% 并留下 div_unit.sv"
tags: [HWE Bench, 示例, cosim, v1 进化史, 除法器]
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

本示例跟踪 v1 自主进化运行里同一个微架构想法的两次落地：把 RV32M 的 DIV/REM 移出单周期 ALU 关键路径。第一次是 round 1 slot 0 的 "Move DIV/REM off the single-cycle ALU path"，没见到 FPGA 就死于 selftest 协同仿真（log.jsonl L2）；约两小时后，同一动机改写为 round 6 slot 0 的 "Cold Multi-Cycle DIV/REM Unit"，formal/cosim 双过并成为 +15.7% 的突破胜场（L17，F-101）。要看的不是胜场本身，而是这条「失败 → 改写 → 胜场」轨迹上，哪个门拦住了第一次、编排器配置为什么允许同一个想法复活。

这是静态走读：全部材料取自固定提交 `4a137bb1378834ca3664a1c971684777eb5f364a` 的 log.jsonl 与 v1 RTL，未运行仿真、形式求解或 FPGA 综合；Fmax/fitness/LUT/时间均为作者报告口径（F-003/F-100）。

## 时间线：开局第 1 轮与约两小时后

v1 日志共 74 行 = 73 个真假设 + L1 一行基线哨兵（F-097）。哨兵落 2026-04-28T02:16:49Z，retest fitness 301.04（F-098）。紧接着 round 1 的三个槽里，slot 0 就是除法器想法；broken 行没有时间戳字段，同轮邻居落 02:39-02:44Z。第二次落 L17，时间戳 04:24:16Z（本地解析亲验）——与博客 "two hours later" 的口径一致（[blog L70](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/docs/auto-arch-tournament-blog-post.md#L70)，F-101）。两次尝试是两个不同的假设 ID：`hyp-20260427-001-r1s0` 与 `hyp-20260428-010-r6s0`（ID 正则与 rNsM 后缀见 F-024）。

## 第一次生命：r1s0 死于 selftest 对拍

下面是 log.jsonl [L2](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L2) 的精简摘引（原行 13 字段，省略 motivation/hypothesis/changes 等长字段）：

```json
{
  "id": "hyp-20260427-001-r1s0",
  "title": "Move DIV/REM off the single-cycle ALU path",
  "category": "micro_opt",
  "expected_impact": { "fitness_delta_pct": 15, "confidence": "medium" },
  "outcome": "broken",
  "formal_passed": false,
  "cosim_passed": false,
  "error": "cosim_failed: selftest.elf",
  "round_id": 1,
  "slot": 0
}
```

它是 v1 运行 9 个 broken 中 4 个 selftest cosim 失败之一（F-065/F-102）。值得注意的是，r1s0 的 `changes` 清单已经列了后来第二次尝试的同样五个文件——`rtl/alu.sv`、新增 `rtl/div_unit.sv`、`rtl/ex_stage.sv`、`rtl/hazard_unit.sv`、`rtl/core.sv`。也就是说，连「要新建一个独立 div_unit」这一步都在第一次的计划里；被否掉的不是这个文件布局。

## 被否掉的是实现，动机文本没有错

r1s0 的 motivation 逐字要点是：32 位组合除法器 "very likely to dominate LUT depth and area"，而 CoreMark 计时区是 "multiply-heavy and effectively division-free"——为冷路径保持单周期 DIV/REM，等于让每条指令替除法器付时序代价。假设文本提出用迭代除法单元加 EX-stage interlock，并要求保持 divide-by-zero 与 INT_MIN/-1 语义。这是一个标准的时序优化动机，后来的九个胜场与 V2 textbook 编辑都证明它方向正确（V2 页称换迭代除法器是 "the first move most agents make"，35 个 round-1 接受设计中 34 个改除法器，F-120）。

静态对比两次假设文本能看见实现纪律上的差别：r6s0 的文本明确要求除算期间 "inject bubbles into EX/MEM while the divider is busy so older instructions retire exactly once"，并在 changes 里要求向 EX/MEM 驱动 valid=0 气泡而不是保持上一条指令，"avoiding duplicate RVFI retirement and duplicate regfile writes"。selftest 全 trace 对拍恰是抓这类退休纪律错误的门（F-058/F-061）；r1s0 具体错在哪一行 RTL，日志没有记录，本文不反推。

## 第二次生命：Cold Multi-Cycle DIV/REM Unit

L17（[log.jsonl L17](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L17)）精简摘引如下（原行 25 字段，省略长文本字段）：

```json
{
  "id": "hyp-20260428-010-r6s0",
  "title": "Cold Multi-Cycle DIV/REM Unit",
  "category": "micro_opt",
  "expected_impact": { "fitness_delta_pct": 6, "confidence": "medium" },
  "outcome": "improvement",
  "formal_passed": true,
  "cosim_passed": true,
  "fmax_mhz": 159.92,
  "fitness": 375.43,
  "delta_pct": 15.7,
  "lut4": 5888,
  "ff": 2227,
  "seeds": [159.92, 157.98, 165.51],
  "timestamp": "2026-04-28T04:24:16.990069"
}
```

数字读法（均为作者报告）：三种子 Fmax 中位数 159.92 MHz（F-068/F-072），fitness 375.43，对时任冠军 r2s2 的 324.48 严格高出 15.7%（严格 `>` 接受规则，F-015）。两个意外：第一，这一跳的自报预期只有 +6%，比第一次那张失败申请的 +15% 更保守；第二，LUT4 从上一任冠军的 10,192（[L7](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L7)，本地解析亲验）降到 5,888。博客原话：agent 事先不知道这会同时砍掉约一半 LUT，"It found out by doing it and watching the synthesizer."（[blog L60](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/docs/auto-arch-tournament-blog-post.md#L60)，F-101）。

## 为什么验证器配置允许这种「复活」

同一个想法能在两小时后原样再来一遍，靠的是四条结构性安排，而不是模型记仇或记分：

1. **每槽一个独立 worktree**。候选在隔离 worktree 里实现，失败只销毁该 worktree，主干不动；接受才允许 `git merge --ff-only`（F-035/F-038，见 [/concepts/03-worktree-sandbox.md](/concepts/03-worktree-sandbox.md)）。r1s0 的坏 RTL 没有任何机会留在树上。
2. **失败不产生黑名单**。假设 ID 由编排器按轮预分配，rNsM 后缀只标识位置，历史 broken 不扣信用分、不禁止同主题（F-014/F-024，见 [/concepts/02-round-orchestration.md](/concepts/02-round-orchestration.md)）。
3. **锦标赛每轮发全新槽位**。K 个槽每轮重新 fan-out、类别轮转，搜索预算为「想法」反复买单，直到它被正确实现或被更好的候选挤出（F-014/F-018）。
4. **门只裁决这次提交**。error 字段指向具体失败点 `selftest.elf`，裁决对象是 worktree 里的实现物；schema 里没有「除法器想法已失败」这种状态（F-082 三结果类）。

作者的总结是："Without the cosim gate the broken first attempt would have shipped."（[blog L70](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/docs/auto-arch-tournament-blog-post.md#L70)）——门挡住第一次，编排允许第二次，两者合在一起才产生胜场。

## 物证：冠军核里的 div_unit.sv

第二次尝试最终固化在 v1 冠军核中：v1 的 rtl/ 有 16 个 .sv，比 baseline 多出 div_unit、store_slot 等文件（F-094）。[cores/v1/rtl/div_unit.sv](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/rtl/div_unit.sv#L1-L5) 的文件头注释（pinned 逐字）就是 r6s0 假设的实现注脚：

```systemverilog
// rtl/div_unit.sv
//
// Iterative RV32M divider/remainder unit. The EX stage starts it only for
// DIV/DIVU/REM/REMU and bubbles EX/MEM until done, keeping the cold divider
// off the one-cycle ALU result path.
```

同一文件内还保留 `RISCV_FORMAL_ALTOPS` 替身分支，让快速 formal 证明停顿/路由纪律而把真算术交给 cosim 与独立测试（F-050，见 [/concepts/05-formal-altops.md](/concepts/05-formal-altops.md)）。在 V1 bench 榜首 Opus rep1 的胜场链上，r1s1 第一条接受设计又是同一个除法器思路（作者报告 fitness 359.0、+26.9%，见 [/concepts/14-v1-leaderboard.md](/concepts/14-v1-leaderboard.md)），可作为本故事的跨运行回响。

## 可迁移的教训

- **门拒绝的是实现，不是想法**。读 error 字段时应把「坏想法」和「这次没做对」分开；后者的正确动作是带更细纪律的改写，而不是换方向。
- **「失败 - 改写 - 胜场」是搜索轨迹的标准动作而非异常**。九胜场中最大的一跳 +15.7% 正出自这条路径（F-100/F-101）；设计评估系统时应为同主题重试保留槽位与干净工作树。
- **预测的置信度与结果是两回事**：+15% 的申请死于 selftest，+6% 的申请拿到 +15.7% 外加 LUT 腰斩；expected_impact 只是必填字段，不参与接受裁决（F-026）。

## 相关概念与示例

- [/concepts/02-round-orchestration.md](/concepts/02-round-orchestration.md)：K 槽锦标赛、类别轮转与假设 ID 预分配
- [/concepts/03-worktree-sandbox.md](/concepts/03-worktree-sandbox.md)：失败 worktree 销毁、快进合并与不污染主干
- [/concepts/06-cosim-iss.md](/concepts/06-cosim-iss.md)：selftest 全 trace 对拍为什么能拦住 r1s0
- [/concepts/07-fpga-fitness.md](/concepts/07-fpga-fitness.md)：3-seed 中位数与 fitness 公式
- [/concepts/11-v1-evolution.md](/concepts/11-v1-evolution.md)：9 个真胜场的完整时间线与计数勘误
- [/examples/01-opus-983-rep.md](/examples/01-opus-983-rep.md)：同一个冷除法器想法在 bench rep 的胜场链里再次出现——R1 首胜与 983.2 的完整账目
- [/examples/02-failure-gallery.md](/examples/02-failure-gallery.md)：r1s0 的 cosim_failed 与沙箱、schema、−73.25% 等失败样本一起按拦截点分组陈列
- [/examples/index.md](/examples/index.md)：HWE Bench 束示例索引与三篇的阅读路径
