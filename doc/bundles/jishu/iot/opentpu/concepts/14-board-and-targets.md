---
okf_version: "0.2"
type: Concept
title: "板卡与多 target：YPCB-00338、镜像演进、bcu1525、Lens 与 scoreboard"
description: "生产卡是浪潮 YPCB-00338（Kintex-7 + 双 DDR3）；targets/*.toml 四段描述让一份 RTL 构建到卡、在研板与 ASIC；Lens 与 scoreboard 分别回答周期去哪与改配置会怎样。"
tags: [openTPU, FPGA, YPCB-00338, target, bcu1525, Lens, scoreboard]
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

## 一张真实的 PCIe 卡与四个构建目标

openTPU 不是只在模拟器里跑的设计：生产目标是浪潮 **YPCB-00338** 卡，位流经 Vivado 生成、JTAG 烧录，主机经 XDMA PCIe 驱动。同时仓库用一份 `targets/*.toml` 体系把同一份 RTL 对四个目标构建：在产的 ypcb-00338、bring-up 中的 bcu1525，以及两个 NanGate45 ASIC 点（后者见 [ASIC 路径](/concepts/15-asic-nangate45.md)）。本篇只做静态源码与文档阅读，未构建位流、未使用 FPGA。

## YPCB-00338：规格全表

证据为 [targets/ypcb-00338.toml](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/ypcb-00338.toml) 与 README：

| 项 | 值 |
|---|---|
| FPGA | Xilinx Kintex-7 **xc7k480tffg1156-2**（DSP48E1） |
| 存储 | 2×DDR3-1066，每 slice 4 GiB，64 字节 beat，峰值 **17.1 GB/s** |
| 控制器 | LiteDRAM（WL7DDRPHY）；镜像启动时核内小 CPU 约 **12 秒**自校准两通道、无需主机参与；target 同时置 hostcal=true（CAPS bit27，主机亦可经 CSR 用 `otpu-memcal` 校准） |
| 主机链路 | XDMA PCIe **Gen2 x8** |
| 核时钟 | **133.33 MHz**（128 字节端口恰好匹配两个 DDR3 通道） |
| 架构 | S=1、D=128、MCOLS=4、ACT_BLOCKS=128、ACT_ROWS=16、LANES=8、IMEM 32K 字、TMEM 64K 字；PAIR/DSTEP/STREAM=true |
| 微结构 | 四列 systolic MXU（MXU_IMPL=2，CL=16，E=4）、VPU_CL=2、WIN=16、FIFO_DEPTH=1024、TRACE_DEPTH=16384、CHASH 通道交织 |
| 时序余量 | 生产镜像 **WNS +0.032 ns / WHS +0.016 ns**（勉强收敛，作者报告） |
| 主机 | opentpu 机：Intel Core i7-4790 |

## 镜像演进：se-cand3 → deploy_champ → build B

- **se-cand3**（旧生产镜像）：Xilinx MIG 控制器、两列 MXU、120.755 MHz；
- **deploy_champ_e698dcd7**（2026-09-29 晚起生产）：LiteDRAM、四列脉动 MXU、stream engine，133.33 MHz，即上表；
- **deploy_fused133c_79c5707a**（build B，09-30 起生产）：同架构，LFM2-2.6B/SmolLM3/Phi decode 快 8-9%、Gemma4 E2B 快 10%，解码期 DRAM 利用率 91-94%（旧镜像 82-87%）。

两代镜像的对照（作者报告，同一 perf.py 口径）：**decode 差距 ≤2.3%**——decode 本就 DRAM bound，两版都跑到峰值的 82-85%；**prefill 快 1.3x（Qwen3.5）到 2.0x（LFM2 4-bit）**，这是四列阵列与新控制器的主要收益面。所有性能数字引用时应带镜像名与日期。

## 多 target 体系：一个 TOML 派生一切

每个构建目标是一个 TOML，分四段（[target.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/target.py#L84-L181) 加载时逐段校验）：

- `[target]`：name、kind（[target.py L44](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/target.py#L44) 枚举为 `fpga`/`asic`/`sim`；ffe997e 的 4 个 target TOML 仅使用 fpga（ypcb/bcu1525）与 asic（nangate45 两档），`sim` 为纯模拟器档位）、platform_id（经 CFG_PLATFORM 寄存器上报，主机用 `by_platform()` 反查）；
- `[arch]`：**程序可见**参数（S/D/MCOLS/ACT_BLOCKS/ACT_ROWS/TMEM_WORDS/IMEM_WORDS/DRAM_BYTES/LANES/PAIR/DSTEP/STREAM），键必须恰好覆盖模拟器 `Config` 的字段，架构经 `arch_hash` 入 CFG_HASH；
- `[uarch]`：**仅时序**的 RTL 参数（MXU_IMPL/CL/E、VPU_CL、ULANES、TMEM_IMPL、RPB/WPB、WIN、FIFO_DEPTH、TRACE_DEPTH、PQ_WIN、CHASH），程序看不见；
- `[tech]` 与 `[platform]`：工艺族/器件，板级 core_mhz、内存类型与通道、beat、PCIe。

`Target.load/current/config/rtl_params/sources/build_config` 从这一个文件派生 RTL 参数、Vivado generics、模拟器配置与主机期望；`OTPU_TARGET` 选择目标（默认 ypcb-00338），模拟器另有 `OTPU_MCOLS/OTPU_LANES/OTPU_ACT_ROWS/OTPU_PAIR/OTPU_DSTEP/OTPU_STREAM` 环境覆盖。这样旧设计点（09-23 设计稿的 S=2/MCOLS=8/WIN=32）只作为历史规格留在 docs，生产参数以 target 为唯一事实源。

## bcu1525：在研的双 slice 大板

[bcu1525.toml](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/bcu1525.toml) 是 bring-up **计划，尚未建成**：Virtex UltraScale+ **xcvu9p-fsgd2104-2L-e（VU9P，DSP48E2）**，4 个 DDR4 RDIMM 槽（板文件配 16 GiB/条的 MTA18ASF2G72PZ，XDMA Gen3 x16），架构 **S=2**（4 通道，每 slice 两个）、D=128、MCOLS=4；开发构建先 100 MHz、DDR4-1600（条为 DDR4-2400）。两个 slice 经 collective 单元协作：**GATHER** 要求所有 slice 以相同 dst/rows/cols/drs/seg 执行，对每一片 `s`、每个行 r 与列 c，把 `T_s[src + r*srs + c]` 写进**所有片**的 `T_all[dst + s*seg + r*drs + c]`——即一次 all-gather，源范围与目的范围不得重叠；**BAR** 是片间屏障，等待所有 slice 到达。slice 之间除 GATHER/BAR 外不共享任何资源（各自私有 DRAM、TMEM、ACT RAM 与执行单元）。RTL 顶层为多 slice 的 `otpu_top.sv` 加 `otpu_coll.sv`，ol 侧对应 `ol.all_gather/all_reduce`。生产 YPCB 是 S=1，因此 collective 路径主要在模拟器测试与 bcu1525 上获得真实形态。

## Lens：trace 里周期去哪了

[opentpu/lens.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/lens.py) 把一次 run 录成 gzip JSON 的 `.otpuprof`，三种 **kind**：`rtl`（周期精确 trace）、`isa`（模拟器执行指令配分析式串行时序）、`board`（卡上计数器快照）。浏览器应用（lens_app.html 随包，亦可导出独立 HTML）给 roofline、时间线、复刻数据搬运的 floorplan 与逐指令/逐源码行表，颜色区分忙、等 DRAM、等依赖——这正是「无 cache、无隐藏调度」机器的可解释性兑现。卡上 trace 缓冲深度 TRACE_DEPTH=16384，经 `otpu-lens`/hwlens 取回。

## scoreboard：配置的 what-if 模型

[tools/scoreboard.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tools/scoreboard.py) 是四类**等权工作负载**（2026-10-11 口径：单用户 decode、prefill、多用户批量 decode、MoE）的硬件 what-if 模型：逐层按「DRAM 字节/带宽」与「MXU 周期」取大值，加上 DeltaNet 递归与每行标定开销，常量拟合 YPCB 计数器并经 RTL co-simulation 校核。子命令有 `report/compare/whatifs/validate/boards/models/fit`；旋钮包括 `--mcols/--act-rows/--mxu-pump/--tmem-words/--rows/-S/--mhz/--mem` 等。它不替代实测，而是让「改 MCOLS、加 slice、换 DDR4」这类决策在构建前先过一遍量化比较。

## 构建位流

`make -C boards/ypcb-00338 bit`（= `MCOLS=4 ./run_vivado.sh 1066`）产出 otpu.bit、otpu.mcs（支持 **BPI flash** 部署）与 reports/；可覆写 MCOLS/VPU_CL/DDR/BUILD_ID/CORE_MHZ。前提是 **Vivado 2026.1 且有覆盖 xc7k480t 的许可**（免费版不含该器件，需付费或 30 天评估许可）；一次构建约 1.5-3 小时，收敛后先看 `build/vivado/reports/SUMMARY.txt` 的 WNS/WHS。boards/ 下含 ypcb-00338 与 bcu1525 两套板工程。

## 相关概念

- [ASIC 路径：NanGate45 + OpenROAD 流程与 PPA 数字](/concepts/15-asic-nangate45.md)
- [位精确验证体系：validate 四行表、KL 判据与 78 文件测试金字塔](/concepts/16-verification-system.md)
- [sequencer：顺序派发、WIN=16 足迹窗口与 HALT CHAIN 常驻程序](/concepts/03-sequencer-and-chaining.md)
- [主机软件栈：chat/serve、卡上批量与 MoE 专家流 offload](/concepts/13-host-stack-serve-moe.md)
- [openTPU 事实登记表 F-001~F-123](/references/facts.md)
