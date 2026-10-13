---
okf_version: "0.2"
type: concept
title: "openTPU：让 AI agent 去设计一颗跑 AI 的芯片"
description: "本周头条——openTPU 开源推理加速器的存在、硬件、自报性能与作者三大判断；验证为何是架构问题、朴素设计何以成为递归迭代前提、性能数字的审慎边界"
tags: [openTPU, AI芯片, 硬件设计, AI agent, 推理加速器, Kintex-7, FPGA]
generated:
  by: "seven-concepts-cmd"
  at: "2026-10-13T13:20:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: mp-weekly-03
    resource: "https://mp.weixin.qq.com/s/yD0epaC9Xm16UVZYojqWOA"
    title: "嵌入式周报·第三期"
---

# openTPU：让 AI agent 去设计一颗跑 AI 的芯片

## 这是什么（F-001、F-002、F-004、F-006）

**openTPU** 是本周（2026-10-05~11）嵌入式头条——作者 **FeSens** 用「AI agent 递归迭代」方法设计出的**开源推理加速器**，从 SystemVerilog RTL 到编译器到 profiler 全在一个仓库，跑在一张 **Kintex-7 FPGA** 卡上（板卡 Inspur YPCB-00338，FPGA xc7k480t，双通道 DDR3）。它复用了 FeSens 此前「AI 设计 RISC-V 核」（auto-arch-tournament）的方法。

相较于一颗可编程芯片，openTPU 更大的意义在于**整条链都可本地运行**（F-006）：RTL、仿真器、编译器、模型都能在笔记本上跑，代码全面开源、**Apache-2.0** 许可，且规模小到单人可通读——这使它成为理解「一个推理引擎从指令到 token 全过程」的低门槛自学材料。

> 💡 **归属与许可**：仓库 github.com/FeSens/openTPU 实存（[V1](../references/verification.md#一核验结论总表)），README 自述 "developed by AI…Runs Qwen3/LFM2.5/Qwen3.5 on a Kintex-7 PCIe card"，标注 Apache-2.0。掉板卡型号（YPCB-00338 / XC7K480T / 双通道 2×2GiB DDR3）经 hackaday 独立登记确认（[V3](../references/verification.md)），DDR3-1066 频率为作者对板卡规格的自报。

## 作者自报的性能（F-005、F-009）

| 模型 | 精度 | 作者自报吞吐 |
|------|------|------------|
| LFM2.5-230M | 4bit | **85.8 tok/s** |
| Qwen3-0.6B | 4bit | 31.3 tok/s |
| Qwen3.5-2B | 4bit | 12.09 tok/s |
| Gemma 4 E2B | 4bit | 12.14 tok/s |
| Qwen3.5-35B-A3B（MoE，专家从主机流式下发） | 4bit | 3.95 tok/s |

**这些数字必须这样读**（F-009）：**全部为作者自报，尚无独立复现，也没有和 GPU 的同条件对比**。85.8 tok/s 是在 230M 小模型、4bit、纯 decode 场景下取得的；Qwen3.5-35B 的 3.95 tok/s 依赖把**专家权重从主机流式下发**，这是这条路上真实存在的带宽瓶颈，不能当成「35B 跑在 FPGA 上」。第三方观测口径不一（[V3](../references/verification.md) 记 openTPU 数字口径有 82.1 与 85.8 两种）。"250+ HN 分"（F-003）未被独立证实，观测峰值约 144，"曾登首页"属实。

---

## 作者三大判断（F-007、F-008、F-010、F-011）

以下为周报作者（自媒体观点，`author_claim`）的独立分析，非硬事实：

### 判断一：把「验证」做成架构问题，不是流程问题（F-007）

绝大多数开源加速器项目的死法是 **RTL 和仿真器的行为慢慢分叉，最后没人知道哪边是对的**。openTPU 的做法是把 **bit-exact 仿真器写在规范的位置上**——它不是测试工具，而是**判官**：硬件必须和它逐位一致，跑出的 token 也必须和它逐 token 一致。这条约束比任何文档都硬。

> 类比：这相当于把"测试即规范"前移，让验证从"事后流程"变成"架构约束"。这与现代芯片验证中 formal / golden reference 的思想一脉相承，但 openTPU 把它精简到能跑在一个 agent 迭代循环里。

### 判断二：朴素是被当成设计目标写下来的（F-008）

「没有 cache、没有隐藏调度」听起来像缺点，但这正是**能被递归迭代的前提**：设计空间小到 agent 每次改动都能快速验证。如果这颗芯片上了 cache 和乱序调度，同一套方法大概立刻失灵。

> 核心洞察（作者）：**能不能被 AI 设计，取决于设计空间是否收敛得足够快**。这不是说朴素芯片更好，而是说"AI 可设计性"本身是一个设计目标，需要主动把搜索空间压到可验证的规模。

### 判断三与趋势：从 PPT 到可复现（F-010、F-011）

openTPU 的「RTL + bit-exact 仿真器 + 自定义 kernel 语言 + profiler」四件套是可直接读的自学材料。趋势上，作者此前「AI 设计 RISC-V 核」的实验，现在用同一套方法做出了能跑真实模型的加速器——**「用 agent 做硬件设计」正从 PPT 阶段进入可复现阶段**。

---

## 工程启示

1. **验证是判官，不是助手**：把 golden reference 放在规范位，比维护两套"看起来都对"的实现可靠得多（F-007）。
2. **可设计性是可压出来的**：复杂永远有诱惑，但收敛得快的设计空间才是 agent 能迭代的前提（F-008）。
3. **自报数字要分层消费**：功能跑通（存在）与性能达标（自报）是两回事；没有同条件对比的性能数字，只能当方向参考（F-009）。

## 边界提示

- openTPU 的吞吐数据、HW 分数均未经独立复现（[@1 残余不确定性](../references/verification.md#三残余不确定性)）。
- 本概念基于周报转述 + 仓库/项目页核验，未逐行阅读 openTPU 源码；如需机制级理解，请直接读仓库。

```{toctree}
:hidden:
:maxdepth: 1

../references/index
```