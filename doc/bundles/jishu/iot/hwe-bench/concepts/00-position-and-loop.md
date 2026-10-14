---
okf_version: "0.2"
type: Concept
title: "HWE Bench 是什么：指向 RISC-V CPU 的自主研究循环"
description: "HWE Bench 是指向 SystemVerilog RV32IM CPU 的自主研究循环：隔离 worktree 改 RTL，七门短路验证，只有严格更强的候选才合并"
tags: [HWE Bench, 项目定位, 自主研究循环, RISC-V]
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

## 缘起：autoresearch 的配方能不能换个赛道

README 在 "Why this exists" 一节自述立项动机：Karpathy 的 autoresearch 让 agent 循环两天在 nanochat 上找到 20 个训练时胜场（F-002）。作者的判断是，那一套之所以成立，是因为 Python 与梯度下降本就是 agent 的主场；本仓追问的是同一配方换到「它没理由擅长」的 SystemVerilog、形式验证与 FPGA 时序之后是否仍然成立（F-002）。

仓库名 auto-arch-tournament，研究对象是一个 SystemVerilog RV32IM CPU；品牌名与基准名才是 HWE Bench。

## 一句话机制：隔离 worktree 改 RTL，七门短路，严格更强才合并

README 开篇给出的机制是：每轮 agent 提出一个微架构假设，在隔离 git worktree 中实现，然后依次过门，只有在 CoreMark/MHz 上击败现任冠军的假设才被合并（F-001）。七门按固定顺序执行，任一门失败即短路：

```text
  hypothesis（YAML，schema 先校验形状）
        |
  verilator lint -> yosys synth -> bench make -> cosim build
                                                  |
  riscv-formal (BMC/SBY, bitwuzla) <--------------+
        |
  Verilator cosim vs. Python ISS（selftest + coremark）
        |
  3-seed FPGA P&R + CoreMark（fitness = Fmax 中位数 x iter/cycle x 1e6）
        |
  严格 > 现任冠军 ?  -- 是 --> ff-only 合并；否 --> 丢弃 worktree
```

七门顺序为 verilator lint→yosys 综合→bench make→cosim build→riscv-formal→Verilator/Python ISS 协同仿真→3-seed FPGA 加 CoreMark（F-001）。门的内部机制分别见概念 04-08，一轮的完整编排见[概念 02](/concepts/02-round-orchestration.md)。

## 作者报告的头条结果（先标口径）

README 报告了产出 `cores/v1/` 的那次运行（F-003，作者报告）：73 个假设、9h51m wall-clock；fitness 从 301 iter/s（2.23 CoreMark/MHz）增至 577 iter/s（2.91 CoreMark/MHz），fitness +92%，比 VexRiscv 公布的 2.30 CoreMark/MHz 高 +26%，同时 LUT 少 40%（F-003）。

这些数字全部是作者报告口径：来自作者在 README 与 `cores/v1/experiments/log.jsonl` 留存的单次运行，本束未复跑任何 EDA。README 的胜场表列了「10 个接受的胜场」，其中 0.0h 行是基线哨兵，真实架构胜场为 9 个（F-004）；该表只有 Δt/iter/s/CM/MHz/Fmax/假设名列，**没有 LUT 列**，同名博客表才额外含 LUT4 列（F-004）。日志的机械复算见[概念 11](/concepts/11-v1-evolution.md)，此处先预告：log.jsonl 共 74 行，即 73 个真假设加 1 行基线哨兵（F-097）。

## 论点：循环是大路货，活下来的是验证器

README 的核心论点逐字是："the loop isn't the moat — the loop is commodity. The artifact that survived 10 wins past 63 rejections wasn't the agent; it was the verifier."（F-005）。同次运行 73 个假设中 63 个被验证器拒绝，"That's the point."（F-006）。作者据此主张：真正编码「正确」含义的是 formal/cosim/FPGA 这套验证器，而不是循环本身。需要注意「63 rejected」是 README 的约数叙事，精确的结局分布以日志机械复算为准（K-2）。

## 品牌：HWE Bench 与 unbounded 主张

项目品牌名为 HWE Bench，站点 hwebench.com；CITATION.cff 题名为 "HWE Bench: An Unbounded Benchmark for LLM Hardware Development on RISC-V"，作者 Felipe Sens Bonetto，版本 v1，发布日期 2026-05-15（F-007）。配套战略文案是 "SWE-bench tops out at 100%. HWE Bench doesn't have a top."——fitness 不设饱和上限（F-007）。视觉识别刻意克制，一句带过：米底 `#FAF7F2`、墨色 `#1A1A1A`、唯一强调蓝 `#1F4380`，标题/正文/数据分别用 Source Serif 4、Inter、IBM Plex Mono（F-008）。

## 复现入口与本束的走读边界

复现目前仅支持 macOS：setup.sh 在非 Darwin 平台直接退出（F-009）。`bash setup.sh` 会把 Verilator、OSS CAD Suite（yosys、nextpnr-himbaechel、sby、bitwuzla）与 xPack riscv gcc 自举到仓库内 `.toolchain/`，已在 PATH 上的工具会被检测并复用（F-009）。README 给出的示例命令是 `make loop TARGET=v1 N=10 LUT=3000 COREMARK=400`（F-009）。

本束基于固定提交 `4a137bb1378834ca3664a1c971684777eb5f364a` 做静态走读：只读源码、日志与文档，未运行 lint、综合、形式验证、仿真或 FPGA 中任何一步；全文凡性能、频率、费用数字一律标注「作者报告」。

## 发布背景与许可

仓库研究目录留存了一条发布背景（作者报告）：MLCAD 2026 投稿 #48 被拒——175 篇有效投稿中录取 37 篇 regular 与 14 篇 short（21.1%/29.1%），三个评分是 0/0/-2；被评审的稿件是一个 17-run/6-config 快照（V0 为 283 iter/s、最佳 525）（F-010）。仓库许可证为 Apache-2.0（[LICENSE L1-L3](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/LICENSE#L1-L3)）。

## 相关概念

- [假设即数据：JSON Schema、五类 hypothesis 与 ID 账本](/concepts/01-hypothesis-schema.md)
- [一轮编排：N 槽锦标赛、四个角色与门的短路顺序](/concepts/02-round-orchestration.md)
- [FPGA 门：3-seed 中位数、fitness 公式与反常量折叠夹具](/concepts/07-fpga-fitness.md)
- [HWE Bench 事实登记表 F-001~F-126](/references/facts.md)
