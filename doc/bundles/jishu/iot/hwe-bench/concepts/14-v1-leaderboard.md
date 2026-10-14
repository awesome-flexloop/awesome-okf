---
okf_version: "0.2"
type: Concept
title: "V1 排行榜：16 模型、失败模式谱与两个对照的崩溃"
description: "V1 主榜 16 个模型行的读法：榜首 Opus 983.2(n=1)、第二梯队、两个无 LLM 对照的 282.8、失败模式谱、p 值全「—」的统计诚实与播种勘误"
tags: [HWE Bench, V1排行榜, 失败模式, 对照实验, Wilcoxon]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-14T17:00:00+08:00"
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

## 主表怎么读

bench/LEADERBOARD.md 主表 16 个模型行，按完成 rep 的 fitness 均值排序（F-107）。每个 (模型, rep) 都是一次从冻结 bench 夹具核出发的完整 15×3 锦标赛。列含义（[LEADERBOARD.md L13-L15](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/LEADERBOARD.md#L13-L15)）：

- **Fitness mean ± std**：跨完成 rep 的 CoreMark iter/s 均值与总体标准差（pstdev），n=1 时显式标 `(n=1)`；
- **Best / LUT4 / Fmax / IPC**：最佳 rep 中最佳条目（fitness 等于 Best 的那条）的 FPGA 侧细节，展示模型选择的面积-频率权衡；
- **acc/rej/brk**：每 rep 平均有多少 iter 落为 accepted 改进 / rejected 回归 / broken；
- **Iters→best**：达峰轮次；**Pass-rate**：候选通过率；**s/iter**：每候选平均墙钟秒；**$ cost**：runtime 上报费用字段。

表底参照基线：LUT4 9563、Fmax 127 MHz、IPC≈0.79、fitness 282.8（夹具基线 282.82，F-095、F-110）。

## 榜首与梯队（数字均为作者报告）

- **榜首 `claude-opus-5_5_xhigh`：983.2 (n=1)**，3128 LUT4、302.2 MHz、IPC 3.25、acc 10 / rej 13 / brk 23、42 iter 达峰、pass-rate 22%、735 s/iter（F-107）。只有一个完成 rep，因此没有 std——这是全表最强单点，但样本量也是最薄的之一。
- **第二梯队**：`gpt-5_4_xhigh` 485.8±28.1（best 513.8）、`gpt-5_5_xhigh` 468.3±52.8（best 525.0，全组 best 最高）、`gpt-5_6-terra` 442.3±55.8（best 515.7）（F-108）。
- **最慢与最贵**：`gpt-5_4-mini` 362.3±23.7 但 **1973 s/iter** 为全表最慢（F-108）；费用侧 `kimi-k2_6` 339.5±8.3 对应 $28.44、`gemini-3_1-pro` 339.4±12.6 对应 $83.53（F-109）；`gemini-3_5-flash` **0 个完成 rep（1 failed）**，主表无数（F-109）。
- **$0.00 的读法**：多行数费用为 $0.00，但费用是 runtime 上报字段；Opus rep1 遥测显示 api_equivalent 估算 $123.62、OAuth 实付 $0.00（F-126），即 $0 表示订阅/OAuth 口径下未计费，不代表零成本。

## 两个无 LLM 对照：同一 282.8 的两种崩溃

random-mutation（随机单行变异）与 static（无 LLM 空操作桩）的 fitness 都是 **282.8±0.0**，精确等于夹具基线——两个对照都没能移动分数（F-110）。但崩溃方式截然不同：

- **random 每 rep 恒为 1 acc / 0 rej / 45 brk**：45 个候选全部首败于门，acc=1 是每 rep 开头那次 baseline retest 哨兵（F-110、F-113）。
- **static 是一对事故对**：rep1 = 1 acc / 3 rej / **42 hypothesis_gen_failed（标注 INCIDENT）**；rep2 = 1 acc / 45 rej / 0 brk（[LEADERBOARD.md L219-L223](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/LEADERBOARD.md#L219-L223)，F-113）。空操作桩本应全部走「门全过但不胜」的 regression，rep1 却批量产不出假设 YAML——对照组的 harness 事故被显式标 INCIDENT 并保留在表上，而不是被悄悄重跑。

## per-rep 46 iters 与 Opus rep1 完整拆解

Per-rep 明细表每个完成 rep 都是 **46 iters = 45 个候选 + 1 次 baseline retest**（F-112）。榜首行（[LEADERBOARD.md L182](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/LEADERBOARD.md#L182)，F-112）：

```text
claude-opus-5_5_xhigh rep1: 282.8 → 983.2   Δ = +248%
46 iters | 10 acc / 13 rej / 23 brk | wall 563.3 min
23 broken = 22 hypothesis_gen_failed（假设代理撞到 20 min 上限）
           + 1 formal_failed（r13s2，真实反例）
```

日记记载该 rep 从 282.82 起步、终值/最佳 983.24（+247.7%），round 14 达峰，9 个接受提交全部 confined to `cores/bench/rtl/` 与 cocotb 测试（F-112，[diary 2026-09-26 L42-L48](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/research/diary/2026-09-26.md#L42-L48)）。逐轮拆解见 [/examples/01-opus-983-rep.md](/examples/01-opus-983-rep.md)。

## 失败模式谱

Failure modes 节按 orchestrator 的 broken-class 标签分组计数（F-114，[LEADERBOARD.md L55-L69](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/LEADERBOARD.md#L55-L69)）：`formal_failed`（编译过但形式验证出反例）、`implementation_compile_failed`（Verilator lint 死）、`hypothesis_gen_failed`（代理没在预分配路径写出 YAML）、`cosim_failed`（与 ISS 对拍发散）、`placement_failed`（nextpnr 布不下）、`make_failed_during_execution`（ tally 时 `*.sby` 零任务，多为检查目录被破坏）。谱的两端：

- **random-mutation：formal_failed 135**（旧口径）；**static：hypothesis_gen_failed 42**（F-114）；
- **Opus：22 hyp_gen_failed + 1 formal_failed**——最强模型的主要失败不是写错 RTL，而是有 22 次没在时限内交出合格假设 YAML（F-112、F-114）。

## 统计诚实：p 值全「—」与 provenance 缺口

配对表把每个模型与 static 按共享 rep 编号配对做双侧 Wilcoxon，但 **n_pairs 只有 1-2，p 值列全部为「—」**（[LEADERBOARD.md L35-L53](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/LEADERBOARD.md#L35-L53)，F-111）。方法学的纪律是 n<5 不报 p（F-083）：表只呈现效应量（如 Opus vs static mean Δ +700.42、random 0/2 wins 且 Δ=+0.00），把「功效不足」本身如实暴露，而非用稀疏样本硬算一个 p。

数据底盘 `bench/results.jsonl` 共 **41 行 = 37 done + 4 failed**、27 字段；但 provenance（fixture_ref / fixture_commit 等）**只有最后两行 L40/L41 携带**——早期 rep 跑在 provenance 机制上线之前（F-115）。这一时序缺口也应计入对 V1 数据的解读；runner 侧的 provenance 记录与克隆剥离机制见 F-116，其故障处置详见 [16-harness-reliability](/concepts/16-harness-reliability.md)。

## K-6：random 135 的播种污染

V1 的 random 对照「135 次 formal_failed」存在播种 bug：135 次尝试实为 **3 个 draws 各重复 45 次**，并非 135 次独立变异（F-124、K-6）。因此：

- 「随机盲改全部首败 formal」这一定性观察成立（3 个变异各自复现 45 次同样失败）；
- 但「135 次独立盲改零接受」的独立样本结论**不能沿用 V1 这个数**；V2 修复播种后改跑 135 次独立抽取（117 formal / 12 cosim / 6 全门但 no-op，0 接受，F-121），独立样本口径以 V2 为准，见 [15-v2-holdout](/concepts/15-v2-holdout.md)。

## 边界与口径

- 主表数字全部为「作者报告」：由 bench runner 在作者机器上跑 41 个 rep 产出，本束只做静态解析与口径核对，未独立复跑。
- n=1 行（如榜首 Opus 983.2 与若干只完成单 rep 的行，F-107、F-111）无离散度信息，排名差距小于 rep 间波动时不可过度解读；6-run 几何均值与预注册检验要等 V2。
- V1 fitness 基于开源 nextpnr timer 与 CoreMark 单程序，与 V2 不同对象，严禁跨版本横比（K-1）。

## 相关概念

- [V1 基准方法学：预注册 15×3、成本门限与参照核政策](/concepts/13-v1-bench-methodology.md)
- [V2 演进：6×6 几何均值、holdout 主榜与三门正确性缺口](/concepts/15-v2-holdout.md)
- [自治 harness 可靠性工程：故障方向、误删事故与遥测重建](/concepts/16-harness-reliability.md)
- [示例：Opus 983 rep 拆解](/examples/01-opus-983-rep.md)
