---
okf_version: "0.2"
type: bundle
title: "openTPU 源码精读：一颗 17 条指令的 AI 加速器（ffe997e）"
description: "openTPU 固定提交 ffe997e 的源码教程束——17 篇概念精读机器模型/ISA/fp32 契约/MXU/VPU/量化/ol 编译器/STREAM/主机栈/板卡与 ASIC/验证体系，3 篇贯穿示例，事实 F-001~F-123 全部 pinned 溯源"
tags: [openTPU, 源码精读, AI加速器, ISA, MXU, VPU, fp32, 量化, FP4, FPGA, Kintex-7, ASIC, NanGate45, OpenROAD, 位精确验证]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T17:40:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: opentpu-pinned
    resource: "https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e"
    title: "openTPU 固定提交 ffe997e（2026-10-12，docs-only 提交）"
    author: "FeSens"
    accessibility: "public"
  - id: opentpu-facts
    resource: "/references/facts.md"
    title: "openTPU 事实登记表 F-001~F-123"
---

# openTPU 源码精读：一颗 17 条指令的 AI 加速器

> ⚠️ **性质声明**：本包是对开源仓库 [FeSens/openTPU](https://github.com/FeSens/openTPU) 固定提交 `ffe997e9a8b8607b07b3d1bb3c1132db0faf044e`（2026-10-12）的**静态源码教程**，经 **source-code-to-okf-wiki v1.5.0 链路（G0 信源固定 → R → I → E → V → C）** 生成。全部事实逐条带 pinned 源码行号，见 [事实登记表](references/facts.md)。
>
> **三条口径边界**：① 性能/功耗/命中率/带宽利用率等数字均为 **openTPU 作者报告口径**（正文逐处标注「作者报告」及其镜像/日期标签），本包不做第三方实测；② 本包为静态走读，**未运行仿真、未构建位流、未使用 FPGA/板卡**；③ 源码工作树只读，未修改上游任何文件。
>
> **E 阶段三处勘误已在事实表留痕**：F-026 BAR 定义锚点（isa.py L133，非 L167）；F-062 isasim ops 字典实为 14 条（非 13）；F-117 ASIC PPA 归属（419/339MHz、0.79W 属 nangate45-small；板卡架构大核仅到 CTS、178/156MHz、未布线，3.34W 为 400MHz 假设 vectorless）。

## 这是什么

openTPU 是一个可以端到端读完的 AI 加速器 monorepo：刻意简单的 **17 条指令** ISA、四列脉动 MXU、自定 fp32 数值契约、把量化做成 ISA 一等公民（FP4 权重 4.25 bits/weight），上层有 ol 内核语言与编译器、chat/serve 主机栈与 MoE 专家流 offload；同一份 RTL 跑在 Kintex-7 生产板卡（YPCB-00338）上，也走过 NanGate45 ASIC 流程，并有 Python 位精确模型 ↔ Verilator ↔ 板卡三端「same bits」验证体系。

与同组 [《嵌入式周报·第三期》的 openTPU 概念页](../embedded-weekly-03/concepts/00-ai-designed-chip.md)（二手综述、F-053~F-072）互补：本包是**对上游源码的一手精读**，并对概念页转引的数字在 pinned 提交上逐条复核。

## 结构总览

```text
opentpu/
├── index.md                 ← 本文件（性质声明 + 分层导航）
├── log.md                   ← 生成日志（G0→R→I→E→V 过程、计数与勘误记录）
├── concepts/                ← 17 篇源码精读（五段）
│   ├── index.md             ← 概念地图
│   ├── 00-03                ← 全景与机器：六层 / 机器模型 / ISA / sequencer
│   ├── 04-07                ← 数值与算子：fp32 契约 / 初等函数 / MXU / VPU
│   ├── 08-10                ← 量化：量化器 / 权重格式 / PAIR·RSC
│   ├── 11-13                ← 软件栈：ol 编译器 / STREAM 状态引擎 / 主机栈与 MoE
│   └── 14-16                ← 平台与验证：板卡多 target / ASIC / 验证体系
├── examples/                ← 3 篇贯穿式走读
│   ├── index.md
│   ├── 00-matmul-through-six-layers.md  ← 一次矩阵乘穿过六层
│   ├── 01-bitexact-crosscheck.md        ← validate 三 backend 位级对拍
│   └── 02-moe-mailbox-waitw.md          ← MoE 专家流 WAITW+mailbox fence
└── references/              ← 信源先行四件套
    ├── index.md
    ├── source-code-map.md   ← G0 固定记录、模块地图、C01-C32 计数台账
    ├── facts.md             ← F-001~F-123（十组 A-J，pinned 链接）
    ├── insights.md          ← I-1~I-5 架构洞察四元组
    └── verification.md      ← V 阶段验证报告（G1-G5 证据）
```

## 分层导航

- **建立全景**：[00 openTPU 是什么](concepts/00-project-and-six-layers.md) → [01 机器模型](concepts/01-machine-model.md) → [02 指令系统](concepts/02-instruction-set.md) → [03 sequencer 与 CHAIN](concepts/03-sequencer-and-chaining.md)。
- **吃透数值与算子**：[04 fp32 契约（上）](concepts/04-fp32-contract.md) → [05 初等函数（下）](concepts/05-elementary-functions.md) → [06 MM 与 MXU](concepts/06-mm-and-mxu.md) → [07 VOP 与 VPU](concepts/07-vop-vpu.md)。
- **理解量化为何是 ISA 一等公民**：[08 量化器](concepts/08-quantization-unit.md) → [09 权重格式族](concepts/09-weight-formats.md) → [10 PAIR/RSC/DUP](concepts/10-pair-rsc.md)。
- **看软件如何落到硬件**：[11 ol 语言与编译器](concepts/11-ol-language-compiler.md) → [12 STREAM/DSTEP/CAPS](concepts/12-stream-dstep-caps.md) → [13 主机栈与 MoE](concepts/13-host-stack-serve-moe.md)。
- **平台与质量体系**：[14 板卡与多 target](concepts/14-board-and-targets.md) → [15 ASIC NanGate45](concepts/15-asic-nangate45.md) → [16 位精确验证体系](concepts/16-verification-system.md)。
- **跟着做一遍**：[示例地图](examples/index.md)——矩阵乘穿六层、validate 对拍、MoE fence 协议。
- **要溯源/质疑时**：[概念地图](concepts/index.md)、[参考资料索引](references/index.md)、[事实登记表](references/facts.md)、[验证报告](references/verification.md)。

## 信任与生命周期

| 维度 | 裁决 |
|------|------|
| status | **draft**（静态源码精读，事实 pinned 可溯源；性能/PPA 数字保持作者报告口径，待独立复现） |
| 信源距离 | 一手源码（固定提交 ffe997e，Apache-2.0）+ 项目文档同提交 |
| 事实规模 | F-001~F-123 共 123 条；C01-C32 计数台账（git/Select-String 双工具复核） |
| stale_after | **2027-04-30**；上游发布新版本、板卡结果被第三方复现、或 ASIC 大核布线收敛时触发提前复核 |

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
