---
okf_version: "0.2"
type: Concept
title: "openTPU 是什么：一个可端到端读完的 AI 加速器 monorepo"
description: "openTPU 是一个可从 Python 矩阵乘一路读到 FPGA 连线的开源 AI 加速器小 monorepo：六层链、位精确契约与三档复现边界"
tags: [openTPU, 项目定位, 六层链, monorepo, 入门]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T16:00:00+08:00"
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

## 两问定位：它想回答什么

openTPU 在 README 开篇自我定位为 **"An open-source AI accelerator, developed by AI."**，并明确提出两个问题：AI agents 做硬件设计能走多远？它们能不能造出运行自身推理的芯片（[README L3-L7](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L3-L7)）。需要注意，「由 AI 开发」是仓库自述：公开仓库本身无法逐行证明作者归属，本束只按仓库自述表述，不替它做生成归属的事实断言。

对学习者而言，更重要的是它的第二个身份：**一个可以端到端读完的小 monorepo**。SystemVerilog 硬件、指令集、位精确模拟器、内核语言与编译器、驱动真实 PCIe 卡的主机软件全在一个仓库里，README 的原话是 "from a matmul in Python down to the wires"（[README L14-L20](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L14-L20)）。本教程基于固定提交 `ffe997e9a8b8607b07b3d1bb3c1132db0faf044e` 静态阅读，未运行测试、未构建位流、未使用 FPGA。

## 六层链：一次矩阵乘穿过的全部层次

README 用一张图说明整套系统（[README L129-L142](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L129-L142)）：

```text
  Kernels in ol              mlp, attention, full model layers
        |  @ol.jit
  Language + compiler        layouts, affine loop addressing, fusion
        |
  ISA                        8 x 32-bit words per instruction
        |
  ISA simulator  <======>  RTL          same bits, checked by the tests
  (Python)                 (SystemVerilog)
                            |  Vivado bitstream
                           FPGA card    Kintex-7 xc7k480t
                            |  PCIe
                           Host         otpu-chat, otpu-smi, otpu-lens
```

逐层看：

1. **ol 内核**：`opentpu/kernels/` 里的 attention、MLP、整模型层，用 `opentpu/language.py` 提供的原语书写，风格类似 triton.language/Gluon 的 SPMD 内核语言。
2. **语言与编译器**：`@ol.jit` 内核经 `opentpu/compiler.py` 降级，编译器负责张量布局、仿射循环寻址与算子融合，每次调用只降为一或几条机器指令。
3. **ISA**：指令定长 8×32-bit 字，一共 **17 条指令**（见 [02-instruction-set](/concepts/02-instruction-set.md)）。
4. **ISA 模拟器 ↔ RTL**：Python 模拟器 `opentpu/isasim.py` 与 SystemVerilog RTL 是同一契约的两个实现，图上特意标注 **"same bits, checked by the tests"**——同样的程序与同样的 DRAM 映像，运行后每个 slice 的 TMEM/DRAM 必须逐位相同。
5. **Vivado 位流 → FPGA 卡**：RTL 综合到浪潮 YPCB-00338 卡（Xilinx Kintex-7 xc7k480t）。
6. **PCIe 主机**：`otpu-chat`、`otpu-smi`、`otpu-lens` 等主机程序驱动真实板卡。

这条链的含义是：仓库里没有一块「看不懂的黑盒」。上层任何一个数值都可以逐层追到指令字段、模拟器实现和 RTL 连线；[示例 00](/examples/00-matmul-through-six-layers.md) 会带读者完整走一遍。

## 「same bits」：全仓围绕的一份契约

[docs/isa.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L1-L5) 开篇声明：它是 compiler.py、isasim.py 与 rtl/ 三者之间的契约，**"All three must agree on every bit written to TMEM or DRAM."** 契约不只规定指令编码，还规定存储语义、fp32 舍入方式、近似函数的固定运算序列、权重编码等一切落地位。模拟器因此被官方阅读路径称为 "the simulator, which is the spec"。

理解 openTPU 的正确顺序是先读契约、再读任一实现。位精确对拍如何在模型级落地（validate 四行表、0 ulp 板卡对拍），见 [16-verification-system](/concepts/16-verification-system.md)。

## 刻意简单的机器：没有 cache，没有隐藏调度

README 强调这台机器是**刻意简单**的（[README L144-L148](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L144-L148)）：sequencer 每周期发射一条指令给少数几个单元——DMA 搬数、矩阵单元乘 int8 权重、向量单元做 fp32 运算、量化器把结果转回 int8。无 cache、无隐藏调度，**每次数据搬运本身就是一条指令**，所以一次运行的 trace 能直接解释周期花在哪里（忙计算、等 DRAM、还是等依赖）。机器模型的细节见 [01-machine-model](/concepts/01-machine-model.md)，派发机制见 [03-sequencer-and-chaining](/concepts/03-sequencer-and-chaining.md)。

## 三档复现边界：Python、Verilator、真实板卡

README 的 "Try it" 给出清晰的三档门槛（[README L176-L191](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L176-L191)）：

- **纯 Python**：`pip install -e .`，配合 pytest/torch/transformers 即可跑测试；`otpu-chat --model lfm2 --backend isa` 在 ISA 模拟器上对话，笔记本即可。
- **RTL**：RTL 测试需要 Verilator 5（`opentpu/rtlsim.py` 依赖 fcntl，面向 Unix/WSL），可在模拟器层验证 SystemVerilog 与 Python 逐位一致。
- **真实板卡**：在 `boards/ypcb-00338` 下 `make bit` 构建位流，经 JTAG 加载，`sudo otpu-setup` 后 `otpu-chat --backend board`。README 原话是 "Everything except the card runs on a laptop"——大部分开发与学习不需要 FPGA。

## 许可与贡献契约

项目采用 Apache License 2.0（[README L345-L347](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L345-L347)）。贡献契约有两条硬规则（[README L339-L343](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L339-L343)）：改动 ISA、模拟器或 RTL 必须保持 `python3 -m pytest -q` 通过；性能声明必须说明测量方法。后者解释了为什么本束所有性能数字都标注「作者报告」并附镜像与日期——不同计时口径（512 prompt+64 greedy 主机 argmax 在环 vs 96 token 卡自选取流式）不可混用。

## 官方阅读路径：7 步

README 给出的阅读顺序（[README L311-L322](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L311-L322)）是：① docs/isa.md 契约；② opentpu/kernels/ + docs/compiler.md；③ opentpu/isasim.py（"the simulator, which is the spec"）；④ rtl/，起点 rtl/top/otpu_top.sv；⑤ 模型文档（lfm2/qwen35/llama/gemma4/benchmarks）；⑥ docs/board.md；⑦ docs/targets.md 多目标体系。本束概念页 00-16 基本沿这条路径展开，可与源码地图 [/references/source-code-map.md](/references/source-code-map.md) 对照阅读。

## 相关概念

- [机器模型：slice、三层存储与顺序完成语义](/concepts/01-machine-model.md)
- [指令系统：17 条指令、8×32-bit 字编码与寄存器约定](/concepts/02-instruction-set.md)
- [位精确验证体系：validate 四行表、KL 判据与测试金字塔](/concepts/16-verification-system.md)
- [openTPU 源码地图与信源固定](/references/source-code-map.md)
- [openTPU 事实登记表 F-001~F-123](/references/facts.md)
