---
okf_version: "0.2"
type: Concept
title: "ASIC 路径：NanGate45 + OpenROAD 流程与 PPA 数字"
description: "用不可制造的 FreePDK45 预测工艺包把同一份核 RTL 过 OpenROAD：小核已布线 419/339MHz、0.79W、0 DRC；板卡架构大核止于 CTS，是 PPA 参考与流片排练。"
tags: [openTPU, ASIC, NanGate45, FreePDK45, OpenROAD, ORFS, PPA]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T17:00:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-13T18:10:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: opentpu-facts
    resource: /references/facts.md
    title: "openTPU 事实登记表 F-001~F-123"
  - id: opentpu-pinned
    resource: "https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e"
    title: "openTPU 固定提交 ffe997e"
---

## 为什么先流一个「不能造」的工艺

NanGate45（FreePDK45）是开源生态常用的预测工艺包，**不可制造**。openTPU 走这条路径的目的在 [asic/nangate45/README.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/asic/nangate45/README.md) 与 [docs/asic.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/asic.md) 里说得很直白：拿一套全开源（OpenROAD + yosys + KLayout）的数字后端，得到面积/时钟/功耗的参考数字，并把它当作可制造 PDK 流片前的**排练**——验证核 RTL 在「RAM 是 macro、乘法是 generic 单元、存储端口在边界」的世界里仍然成立。

ASIC 顶 [rtl/asic/otpu_asic_top.sv](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/asic/otpu_asic_top.sv) 就是**一个 slice 加它的 collective 单元**，slice 自己的存储端口（port A 字读、SW 字节写、port B chunk、ready/valid/idle 握手）、run 控制与状态全部摆在边界上；DRAM 侧（PHY、控制器、通道交织）归平台，正如 LiteDRAM 归 YPCB 卡。这意味着「芯片」与「板卡」共享同一份核 RTL。

## 两个设计点：板卡架构与 shuttle 小核

target 文件 [nangate45.toml](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/nangate45.toml) 与 [nangate45-small.toml](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/nangate45-small.toml)：

- **nangate45（大核）= 板卡架构**：S=1、D=128、MCOLS=4、LANES=8、TMEM 64K 字、IMEM 32K 字、ACT 128 块、FIFO 1024、STREAM 开——因此 token-exact 的**同一套测试**直接适用；
- **nangate45-small（小核）**：D=32、MCOLS=2、4 lanes、64 KiB TMEM、1K 指令、256 MiB DRAM、VPU_CL=1、FIFO=64，可选特性全关，用于快速迭代流程，也是 shuttle 尺寸裸片的形状。

ASIC 微结构与 FPGA 的差别主要在存储：FPGA 上 TMEM 每个读端口保留一份副本（块 RAM 便宜）；ASIC 上 TMEM 改为 **LANES 个 1R1W macro 组的三份 banked 拷贝**（TMEM_IMPL=1，RPB/WPB=1），仲裁按拷贝与 bank 计数。文档给出的代价量化很克制：Qwen3-0.6B 一个 decode token，banked TMEM 为 4,819,205 周期、每读端口一份副本为 4,815,735 周期，**+0.07%**，结果完全相同；三份拷贝是 FPGA 六份的一半，但仍占大核综合面积的 38%。NanGate45 没有存储器编译器，macro 由 `tools/asic/fakeram.py` 按 bsg_fakeram45 格式生成抽象 macro，面积/时钟/功耗对 ORFS 的 24 个 fakeram45 macro（CACTI）拟合，1R1W 面积取 1RW 的 1.5 倍；工艺 RAM 经 `rtl/tech/asic` 的叶子单元替换。

## 流程与可复现性

工具链为 **OpenROAD-flow-scripts**（OpenROAD、OpenSTA、带 slang 的 yosys、KLayout 加 nangate45/fakeram45），参考运行**固定修订 f395e4b6**（OpenROAD 26Q4-110-g91e5f5ff2f、yosys 0.68+）。两种跑法：native（参考机 Ubuntu 26.04，ORFS 自身构建约 20 分钟/20 核；小核一次完整流程峰值约 15 GB 内存、81 分钟/20 核）或 ORFS 的 Docker 镜像（6.5 GB；prep 阶段仍需主机上带 slang 的 yosys）。`tools/asic/flow.py` 的 `points/all/run/report` 与 `tools/asic/paths.py` 生成 report.json、按单元/流水级分类的关键路径；约束为 2.5 ns（400 MHz）、利用率 35%、端口预算留周期的 20% 在片外。功耗全部是 OpenSTA 在默认翻转率下的 **vectorless 估算，作者报告**。

验证沿用位精确体系：RTL 测试套件（133 项）与 Qwen3-0.6B（int8、fp4 带 int8 头、fp4 PAIR）、Qwen3.5-0.8B（含/不含 DSTEP）在 RTL 上的模型 token，与 ASIC TMEM 配置和板卡配置下的 ISA 模拟器逐位一致（各 138 passed）。

## PPA 表（作者报告，docs/asic.md 原始口径）

| | nangate45-small（已布线，signoff 提取） | nangate45 大核（板卡架构，止于 CTS） |
|---|---|---|
| 裸片 | 2.65×2.65 = 7.02 mm² | 5.53×5.53 = 30.6 mm² |
| 标准单元 | 1.18 mm²，59 万实例（20.8%） | 4.36 mm²，202 万实例（18.3%） |
| macro | 27 个，233 KiB，1.31 mm² | 113 个，1126 KiB，6.62 mm² |
| reg-reg | 2.39 ns = **419 MHz**（2.5 ns 无违例） | 5.60 ns = 178 MHz（CTS 后 2.7 ns 时钟 skew） |
| 含端口 | 2.95 ns = **339 MHz**（单点 `sw_req`） | 6.40 ns = 156 MHz |
| 400 MHz 功耗 | **0.79 W**（时序 0.28/时钟 0.20/macro 0.16/组合 0.15，漏电 21 mW） | **3.34 W**（时序 1.09/时钟 0.93/macro 0.87/组合 0.46，漏电 82 mW） |
| 布线 | 16.2 m 连线，**0 DRC、0 antenna** | 未布线（全局布线拥塞，GRT-0116） |

同一小核用同日 native ORFS 复跑，结果在工具噪声内：**422 / 341 MHz、0.79 W、0 DRC**（`asic/nangate45/results/small/`）。注意区分两点：419/339 与 422/341 都是**小核**在两套 ORFS 环境下的数字；大核的 3.34 W 是「在 400 MHz 假设下」的 vectorless 功耗，其时序在 CTS 阶段仅到 178/156 MHz，且全局布线因 ACT RAM 32 个 macro 塞在裸片一角而拥塞（17.6 万 overflow 不收敛），文档明确「小核是当前 ASIC 参考点，大核是压力场景」。

## 已知瓶颈与展望

docs/asic.md「Open problems」把瓶颈排得很具体：含端口 339 MHz 的最差路径是 DMA 状态机经 SW 端口仲裁到 `sw_req` 的组合路径（12-27 级逻辑），平台适配器加一级寄存即可解开；reg-reg 最差路径是时序器派发足迹 `q_pr -> c_fp`（50 级）；其次是「停靠使能」设计带来的高扇出 grant（39-45 级）。fp 流水级自身逻辑并不受限（fmul/fadd 各级还有 0.66-1.35 ns 余量），文档估计在上述问题修掉后，更快的 fp 数据通路（如拆分乘法器）**从约 540 MHz 起**才开始兑现。其余遗留：macro 是 CACTI 拟合而非编译器产物、功耗待 VCD 实测翻转率、大核 floorplan 需降放置密度后重布。

## 相关概念

- [板卡与多 target：YPCB-00338、镜像演进、bcu1525、Lens 与 scoreboard](/concepts/14-board-and-targets.md)
- [位精确验证体系：validate 四行表、KL 判据与 78 文件测试金字塔](/concepts/16-verification-system.md)
- [MM 指令与四列脉动 MXU：48-bit 精确累加、epilogue 与 replay](/concepts/06-mm-and-mxu.md)
- [openTPU 事实登记表 F-001~F-123](/references/facts.md)
