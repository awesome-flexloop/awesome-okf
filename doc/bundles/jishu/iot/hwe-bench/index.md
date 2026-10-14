---
okf_version: "0.2"
type: bundle
title: "HWE Bench 源码精读：让 LLM 自主进化 RISC-V CPU 的验证器工程（4a137bb）"
description: "auto-arch-tournament（HWE Bench）固定提交 4a137bb 的源码教程束——17 篇概念精读自主研究循环/假设 schema/worktree 沙箱/RVFI/riscv-formal/cosim/FPGA fitness/CoreMark 口径/接受规则/v1 进化史/V1 排行榜/V2 holdout/harness 可靠性，3 篇贯穿示例，事实 F-001~F-126 全部 pinned 溯源，附 K-1~K-6 口径勘误台账"
tags: [HWE Bench, auto-arch-tournament, 源码精读, 自主研究循环, LLM基准, RISC-V, RVFI, riscv-formal, cosim, CoreMark, FPGA, Gowin, 防作弊, 验证器工程, holdout]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-14T18:00:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: hwe-pinned
    resource: "https://github.com/FeSens/auto-arch-tournament/tree/4a137bb1378834ca3664a1c971684777eb5f364a"
    title: "HWE Bench 固定提交 4a137bb（2026-10-05，site: V2 results page）"
    author: "FeSens"
    accessibility: "public"
  - id: hwe-facts
    resource: "/references/facts.md"
    title: "HWE Bench 事实登记表 F-001~F-126"
---

# HWE Bench 源码精读：让 LLM 自主进化 RISC-V CPU 的验证器工程

> ⚠️ **性质声明**：本包是对开源仓库 [FeSens/auto-arch-tournament](https://github.com/FeSens/auto-arch-tournament)（品牌名 **HWE Bench**，hwebench.com）固定提交 `4a137bb1378834ca3664a1c971684777eb5f364a`（2026-10-05）的**静态源码教程**，经 **source-code-to-okf-wiki 链路（G0 信源固定 → R → I → E → V → C）** 生成。全部事实逐条带 pinned 源码行号，见 [事实登记表](references/facts.md)。
>
> **三条口径边界**：① Fmax、iter/s、费用、tokens、时间、录取/评审等数字均为 **HWE Bench 作者报告口径**（正文逐处标注「作者报告」），本包不做第三方实测；② 本包为静态走读，**未运行 verilator/yosys/sby/nextpnr 等任何 EDA、仿真或形式求解，未构建位流、未使用板卡**；③ 源码工作树只读，未修改上游任何文件。
>
> **口径裁决（K 台账）**：V1 与 V2 数字**不可直接比较**（K-1）；博客「10 胜/50 回归」与日志机械复算「9 真胜/51 回归」之差为基线哨兵归属（K-2）；formal 检查数有 53/95+/~105 三个口径（K-4）；V1 random「135 次」含播种 bug 口径（K-6）。详见事实表 K-1~K-6。

## 这是什么

HWE Bench 把 Karpathy autoresearch 配方搬到 agent 不擅长的领域：LLM coding agent 在隔离 git worktree 里改 SystemVerilog RTL，依次通过 verilator lint→yosys 综合→程序构建→cosim 构建→riscv-formal 形式验证→Verilator/Python ISS 协同仿真→3-seed FPGA 布局布线与 CoreMark 测量七道短路门，只有 fitness **严格超过**现任冠军的候选才被 ff-only 合并。作者报告的 v1 开发运行：73 个假设、9h51m，fitness 301→577 iter/s（+92%），比 VexRiscv 公布的 2.30 CoreMark/MHz 高 +26%、LUT 少 40%；同次 63 个假设被验证器拒绝。仓库的核心论点逐字是："the loop isn't the moat — the loop is commodity…it was the verifier."

与同组 [openTPU 束](../opentpu/index.md)（AI 设计的加速器静态架构）互补：openTPU 回答「AI 设计的芯片长什么样」，本包回答「**怎样一套验证器才敢让 AI 自己改芯片**」——schema 预校验、路径沙箱与契约指纹、RVFI 双通道路由、ALTOPS 分层 formal、22% 反压 cosim、CRC 自校与反常量折叠 FPGA 夹具、严格接受规则、holdout 五程序，以及长时无人值守 harness 的「故障方向」工程。

## 结构总览

```text
hwe-bench/
├── index.md                 ← 本文件（性质声明 + 分层导航）
├── log.md                   ← 生成日志（G0→R→I→E→V 过程、计数与勘误记录）
├── concepts/                ← 17 篇源码精读（五段）
│   ├── index.md             ← 概念地图
│   ├── 00-03                ← 循环与隔离：定位 / 假设 schema / 一轮编排 / worktree 沙箱
│   ├── 04-07                ← 验证器四门：RVFI 契约 / formal 分层 / cosim / FPGA fitness
│   ├── 08-09                ← 测量与接受：CoreMark 口径 / 接受规则
│   ├── 10-12                ← 核与进化史：baseline 走读 / v1 九胜场 / scribe 经验
│   └── 13-16                ← 基准与 harness：V1 方法学 / V1 排行榜 / V2 holdout / 可靠性
├── examples/                ← 3 篇贯穿式走读
│   ├── index.md
│   ├── 00-cold-div-reincarnation.md   ← 同一想法两度：cosim 之死 → +15.7% 胜场
│   ├── 01-opus-983-rep.md             ← 983.2 rep 拆解：46 iters/9 接受/$123.62
│   └── 02-failure-gallery.md          ← 失败样本集与「拦截点→假失败」总表
└── references/              ← 信源先行四件套
    ├── index.md
    ├── source-code-map.md   ← G0 固定记录、模块地图、C01-C20 计数台账
    ├── facts.md             ← F-001~F-126（十组 A-J + K-1~K-6 勘误台账，pinned 链接）
    ├── insights.md          ← I-1~I-6 架构洞察四元组
    └── verification.md      ← V 阶段验证报告（G1-G5 证据，V 阶段回填）
```

## 分层导航

- **建立全景**：[00 HWE Bench 是什么](concepts/00-position-and-loop.md) → [01 假设 schema](concepts/01-hypothesis-schema.md) → [02 一轮编排](concepts/02-round-orchestration.md) → [03 worktree 与沙箱](concepts/03-worktree-sandbox.md)。
- **吃透验证器四门**：[04 RVFI NRET 契约](concepts/04-rvfi-nret-contract.md) → [05 formal 与 ALTOPS](concepts/05-formal-altops.md) → [06 cosim 对拍](concepts/06-cosim-iss.md) → [07 FPGA 与 fitness](concepts/07-fpga-fitness.md)。
- **理解测量与接受**：[08 CoreMark 评测口径](concepts/08-coremark-measurement.md) → [09 接受规则与三结果类](concepts/09-accept-rule-outcomes.md)。
- **读进化史**：[10 baseline CPU 走读](concepts/10-baseline-cpu.md) → [11 v1 进化史](concepts/11-v1-evolution.md) → [12 scribe 与经验积累](concepts/12-scribe-lessons.md)。
- **看基准与 harness**：[13 V1 基准方法学](concepts/13-v1-bench-methodology.md) → [14 V1 排行榜](concepts/14-v1-leaderboard.md) → [15 V2 演进与 holdout](concepts/15-v2-holdout.md) → [16 harness 可靠性工程](concepts/16-harness-reliability.md)。
- **跟着走一遍**：[示例地图](examples/index.md)——Cold DIV 两次生命、983.2 rep 拆解、失败样本集。
- **要溯源/质疑时**：[概念地图](concepts/index.md)、[参考资料索引](references/index.md)、[事实登记表](references/facts.md)、[架构洞察四元组](references/insights.md)、[验证报告](references/verification.md)。

## 信任与生命周期

| 维度 | 裁决 |
|------|------|
| status | **draft**（静态源码精读，事实 pinned 可溯源；性能/费用数字保持作者报告口径，待独立复现） |
| 信源距离 | 一手源码（固定提交 4a137bb，Apache-2.0；formal/riscv-formal 为 ISC）+ 项目文档/研究日记同提交；V2 数字来自同提交 site/v2.html 静态文本 |
| 事实规模 | F-001~F-126 共 126 条（A-J 十组）+ K-1~K-6 勘误台账；C01-C20 计数台账；I-1~I-6 四元组；73 假设分布由 Python 全量解析独立复算 |
| 不可比项 | V1 榜（开源 timer/CoreMark/报最佳）与 V2 榜（厂商 timer/5 隐藏程序/6 runs 几何均值）数字严禁跨版本比较 |
| stale_after | **2027-04-30**；上游发布新版结果页、V2 数据被独立复现、或 E3 holdout 结论更新时触发提前复核 |

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
