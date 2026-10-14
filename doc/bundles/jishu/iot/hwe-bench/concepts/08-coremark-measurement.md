---
okf_version: "0.2"
type: Concept
title: "CoreMark 评测口径：canonical 2K、IPC 量纲与 holdout 五程序"
description: "CoreMark 在 HWE Bench 既是过门程序也是优化信号：canonical 2K 配置、iter/cycle 量纲勘误、22% 停顿模型与 E3 五程序留存口径"
tags: [HWE Bench, CoreMark, 测量口径, holdout, EEMBC]
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

## 是什么：CoreMark 在这里扮演两个角色

在 HWE Bench 里，CoreMark 不只是一个跑分程序。它同时是：① cosim/FPGA 两门要跑的**被测负载**（coremark.elf 的 CRC 必须对，selftest 之外的第二道对拍短路，见 F-061）；② agent 每轮看到的**优化信号**——fitness 的最终形状就是 CoreMark iter/s（F-073）。正因为它既是裁判用的尺子又是选手能看到的靶子，仓库把它的配置、量纲与「不许针对留存集优化」的纪律全部固定下来，相关防作弊设计见 [07-fpga-fitness](/concepts/07-fpga-fitness.md)。

## canonical 2K：为什么配置必须锁死

bench/programs/Makefile 把三个旋钮钉死为 **COREMARK_SIZE=2000、-O3、ITERATIONS=10**（F-063）。Makefile 注释（[programs/Makefile L4-L18](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/programs/Makefile#L4-L18)）说明了两条理由：

- 2000 数据规模与 -O3 是 **EEMBC 公布口径**，与 VexRiscv 等公开 CoreMark 数字直接可比；注释明确默认值就是为了 "directly comparable to public CoreMark results"。
- 评测器的五 CRC 常量「assume exactly these defaults」——配置漂移会让 CRC 门与分数同时失真（F-069）。

注释还保留了历史口径：旧 V0 基线用过 6000 数据规模/-O2（6000 让 matrix/list/state 工作集大约 3 倍，更难靠寄存器驻留刷分），只能通过显式覆盖变量复现（[programs/Makefile L7-L16](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/programs/Makefile#L7-L16)）。canonical 口径之外跑出来的数，不能与排行榜数字混用。

## 裸机件：最小的 CoreMark 移植层

程序在裸金属 RV32IM 上运行，配套件共五样（F-064）：coremark/baremetal/core_portme.{c,h}、crt0.S（9 行）、link.ld（11 行）、selftest.S（157 行，行数为本地镜像亲验）。其中：

- [crt0.S](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/programs/crt0.S#L1-L9) 只有装栈指针、清零 a0/a1、`call main`、`ebreak` 收尾；
- [link.ld](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/programs/link.ld#L1-L11) 规定 FLASH 128K（0x0 起）、RAM 64K（0x20000 起），栈顶取 RAM 末端；
- [core_portme.c L5-L11](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/programs/coremark/baremetal/core_portme.c#L5-L11) 定义 UART 0x10000000 与 BENCH_START/STOP 两个 MMIO 计时标记（0x10000100/0x10000104）；程序内 `get_time` 返回 0、`time_in_secs` 固定返回 10 以满足 CoreMark 的 ≥10 秒合法性门，真正的周期数由仿真器在标记括号外测量（[core_portme.c L57-L68](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/programs/coremark/baremetal/core_portme.c#L57-L68)），初始化与 printf 时间因此被排除在计时窗口外（F-078）。

## 量纲勘误：ipc_coremark=2e-06 到底是什么

这是本口径最容易读错的一处（F-083 勘误）：log.jsonl 的原始字段 **ipc_coremark 存的是 iter/cycle 绝对值**，基线哨兵实测为 `2e-06`（F-098），它不是 2.2264，也不是写错了小数点。换算关系是：

```text
iter/cycle × 1,000,000 = CoreMark/MHz        # 1 MHz = 1e6 cycles/s
2e-06 是日志存储精度下的舍入显示；展开即 2.2264 CoreMark/MHz
fitness = fmax_median × iter_per_cycle × 1,000,000   # F-073
```

以 baseline retest 为例（作者报告）：127.03 MHz × 2.2264 ≈ 282.82 iter/s（F-095）。读 log 时必须先做 ×1e6，公式在 fpga.py 的实际位置与方法学文档引用行号之间还有一处文档漂移（K-5）。

## 22% 停顿：测量模型本身就是口径的一部分

CoreMark 周期数不是在零等待总线上测的。仿真器用 xorshift7 在 imem+dmem 上注入约 **22% 随机反压**，明确对标 VexRiscv 回归模型的 iStall/dStall，flags 固定为 `["--bench", "--istall", "--dstall"]`（F-059、F-070）。fpga.py 注释给出对照（作者报告）：V0 在零等待幻想总线上是 "2.87 CM/MHz"，带上停顿是 "2.21"，后者才是诚实的微架构数（F-059）。因此引用任何 CoreMark/MHz 都必须带上「同停顿模型」这个前提——V2 进一步把停顿生成器纳入被计时电路，口径再次变化（F-124，见 [15-v2-holdout](/concepts/15-v2-holdout.md)）。

## holdout 五程序：reps、geomean 与 all_validated

E3 留存集是五个**与 CoreMark 不同的真实内核**（F-084）：dhrystone、aha-mont64、crc32、matmult-int、edn。SIM 调用复用 fitness 路径的同一 50M cycle 上限与同一停顿模型（[holdout.py L36-L40](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/holdout.py#L36-L40)），保证留存周期数与 CoreMark 周期数可比。各核重复次数按校准设定，并不相等（F-086，v0_expected.json，作者报告）：

| 内核 | reps | cycles | iter_s |
|---|---|---|---|
| dhrystone | 6000 | 3,389,923 | 224,836.97 |
| aha-mont64 | 200 | 2,896,973 | 8,769.84 |
| crc32 | 90 | 3,073,181 | 3,720.15 |
| matmult-int | 15 | 1,560,047 | 1,221.41 |
| edn | 50 | 2,915,936 | 2,178.20 |

汇总纪律有三条（F-085）：geomean 只对 validated 核计算，用 mean-of-logs 实现、不依赖 numpy；没有任何核 validated 时为 0.0；`all_validated` 要求五核全过，任意一核失败都不算全通过。V0 期望值 geomean 为 **7212.331561429864**（作者报告，F-086）。

## E3 预注册：≥50% 保持率与 "never"

E3 预注册把「非过拟合」写成一条可证伪规则（F-087）：中位数冠军必须在 holdout geomean 上**保持 ≥50% 的 CoreMark 增益**，才允许声称 "not merely workload overfitting"；并且逐字规定 "No re-optimization against held-out kernels, ever"——留存核永远留存，未来 bench 版本也不许拿来再优化。预注册还专门纠正了一次调度口误：edn reps=50 而不是 25（F-087）。

## 边界与口径

- CoreMark 本身在 V2 中**保留为训练/优化信号**，但排名改用 5 个隐藏程序打分（F-124）；因此 V1 的 CoreMark 单程序排名与 V2 held-out 数字严禁直接比较（K-1）。
- 本页所有 iter/s、CM/MHz、cycles 数字均为「作者报告」口径，来自固定提交的日志/期望文件，本束未重跑任何 EDA 或仿真。
- 测量口径还可能被夹具漏洞击穿：ready tie 常量折叠问题（F-079）与严格接受规则如何配合，见 [09-accept-rule-outcomes](/concepts/09-accept-rule-outcomes.md)；cosim 侧的 CRC 短路细节见 [06-cosim-iss](/concepts/06-cosim-iss.md)。

## 相关概念

- [FPGA 门：3-seed 中位数、fitness 公式与反常量折叠夹具](/concepts/07-fpga-fitness.md)
- [cosim 对拍：Verilator C++ 仿真器与 Python RV32IM ISS](/concepts/06-cosim-iss.md)
- [接受规则：严格大于、三结果类与搜索的单调形状](/concepts/09-accept-rule-outcomes.md)
- [V2 演进：6×6 几何均值、holdout 主榜与三门正确性缺口](/concepts/15-v2-holdout.md)
