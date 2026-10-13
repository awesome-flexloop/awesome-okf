---
okf_version: "0.2"
type: Concept
title: "位精确验证体系：validate 四行表、KL 判据与 78 文件测试金字塔"
description: "openTPU 用一份位级契约串起编译器/模拟器/RTL，再用 validate 四行表分开实现正确性与量化代价，配 78 个测试文件与 token 相同+logits 逐位的跨 backend 对拍。"
tags: [openTPU, 验证, validate, bit-exact, KL, 测试金字塔, golden]
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

## 验证的两层问题

openTPU 的验证体系刻意回答两个不同的问题：**实现对不对**（编译器、ISA 模拟器、RTL、板卡是否写出相同的位）与**量化好不好**（设备输出相对 fp32 原模型偏了多少）。前者是位级契约与跨 backend 对拍，后者是统计指标与四行对照表。主工具是 1005 行的 [tools/validate.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tools/validate.py)。本篇为静态阅读，未执行其中任何命令。

## golden 怎么构造：W+A 与 fp32 两套参照

golden 是同 checkpoint 的 Hugging Face transformers **fp32** CPU 前向，再加 openTPU 自己的量化：

- **权重 golden 是矩阵单元实际相乘的值**：用模型镜像同款量化器（quant.py）按所选格式（int8/int4/fp4/nvfp4/mix）量化，连两级块尺度都一致，而不是「原矩阵」；
- **激活在设备量化的位置每 128 个值 round 一次 int8**：每个 matmul 输入，以及 attention 里的 Q、K、V 与 softmax 权重；
- golden 自己的求和/归一化/指数在最后几位与设备不同，所以它无法精确复现设备的舍入——这正是需要「地板行」的原因。

设备三选一：`--backend isa`（模拟器）、`rtl`（Verilator，需 Verilator 5 与 Unix/WSL）、`board`（真实卡）。参数还包括 `--wformat/--head-format/--formats`、`--tokens`（默认 16）、`--resident`、`--weights-only/--no-fp32/--no-golden`、`--min-top1`（默认 0.8）、`--kl-ratio`（默认 3.0）、`--max-kl`（1e-3）、`--save/--json`。默认 8 个 prompt，每个 prompt 设备续出 token 后再把设备自己的 token 喂回 golden，保证每一步比较同一上下文。

## 四行表：每一行回答一个问题

汇总四行是整个方法的核心（README 验证节）：

| 行 | 比较 | 回答什么 |
|---|---|---|
| device vs W+A | 设备 vs 量化 golden | **主检查**：实现是否忠实执行了量化后的计算 |
| device vs fp32 | 设备 vs 原始 fp32 | 用户最终看到的总偏差 |
| W+A vs fp32 | 量化 golden vs fp32 | **纯量化代价**：与实现无关，换芯片也省不掉 |
| W+A~ vs W+A | golden 输入拨 1 个 fp32 ulp 后的自对照 | **地板**：数值问题对微小扰动本身有多敏感 |

指标为 top-1 一致率、mean/largest KL（nats/token，KL(golden‖device)）、最大 logit 差、最低 cosine。通过判据是 **top-1 ≥ 80% 且 mean KL ≤ 3×floor**（两个阈值都可用参数调）。要强调这是**本工具的版本约定，不是通用学术标准**——3 倍地板的含义随模型和格式而变，4-bit 时地板本身离 fp32 行很远。实测（作者报告，ISA 模拟器、8 默认 prompt×16 token）：设备对 W+A 的 KL 仅为地板的 **0.70-1.16 倍**，一次 run 在 16 核主机上 2-14 分钟，峰值内存 2.5 GB（LFM2.5-230M）到 16 GB（Gemma4 E2B）；README 有 11 行 KL 明细表。

## --against：位级对拍

`--against` 加第二设备，要求**token 完全相同且 logits 逐位一致**，按 run 汇总步数与最大 ulp。三档证据：

- **RTL 对 ISA**：`validate.py --model lfm2 --backend rtl --against isa --tokens 3`，16 核主机含 Verilator 构建约 **4 分钟**（作者报告）；
- **板卡对 ISA**：build 1025907f（2026-10-07），卡上 `otpu-lock -- ... --no-golden --save` 加锁保存，构建主机上 `--against card.npz`——这样卡主机不需要 16 GB 内存和 golden；
- 结果：Qwen3-0.6B、LFM2.5-230M、Qwen3.5-0.8B 三模型的 int8 与 4bit-int8head 共 **6 run，全部 token 相同、logits 逐位一致**，每 run 103-128 步、**0 ulp**；卡对量化 golden 的 KL 为地板的 0.94-1.39 倍、top-1 94.5%-97.7%。

注意边界：validate 只支持上述四个模型族（Qwen3-0.6B、LFM2.5-230M、Qwen3.5-0.8B、Gemma4 E2B base/instruct），**MoE 不支持**，MoE 走 chat/offload 与模拟器对拍（见[主机软件栈](/concepts/13-host-stack-serve-moe.md)）。

## 78 文件测试金字塔

tests/ 下 78 个 `test_*.py`，由快到慢、由小到大分层：

- **纯 Python 契约层**（数量最多）：test_isa、test_compiler、test_fp、test_quant、test_vops、test_kernels、test_stream、test_pair、test_mx、test_config_matrix、test_target、test_validate 等——编码、舍入、量化、编译器融合直接在 isa.py/fp32.py/compiler.py 上验；
- **Verilator RTL 层（10 个）**：test_fp_rtl、test_quant_rtl、test_rtl、test_stream_rtl、test_waitw_rtl、test_se_comp、test_se_tail、test_se_vpu、test_rtlsim_build、test_models_on_board_rtl——同一份位级契约落到 SystemVerilog；
- **板卡/主机层（12 个）**：test_board、test_host、test_host_runs、test_host_lock、test_ddr4、test_ddrcal、test_selfcal、test_i2c、test_setup_pcie、test_h2c_sweep、test_bpi_image、test_omarchy_test；
- **serve 相关（7 项口径）**：test_serve_api/batching/emu/kvio/scheduler/store 加 test_chatkv；
- **模型层（约 15 项）**：五模型族 test_qwen3/test_qwen35/test_lfm2/test_gemma4/test_llama，及 moe/mtp、prefill/tiled/batch/perf/offload 等。

贡献契约（README）规定：ISA、模拟器或 RTL 的变更必须让 `python3 -m pytest -q` 保持通过，性能声明必须说明测量方法。

## 两个模型级修复案例：反例文化

验证体系不只测「对的输入」，还把曾经出错的输入钉成回归。其一是 **Q K smoothing**：Qwen3-0.6B 的 k_norm 增益存在达中位 42 倍的 outlier 通道，而 K 按每 token/head/128 用一个尺度量化时，其余通道只剩几级幅值；修复把 outlier 的幅度以每通道 2 的幂从 K 移进 q（q·K 不变），配对文本上 int8 W+A 的 KL 从 0.059 降到 0.015、4-bit 从 0.221 降到 0.179（作者报告），板卡 int8 对 fp32 的 KL 也从 0.052 降到 0.012。其二是 **Gemma4 PLE**：golden 从 LM head 取 embedding 行，设备从每层 PLE 记录取，soft cap 之后再比 logits；E2B fp32 约 20 GB（HF 只载语言模型、不载 9.4 GB PLE 表，bf16 权重保持 bf16 逐矩阵拓宽），E2B run 峰值 16 GB；E4B-it 自 2026-10-09 起默认头与前 12 层 gate/up 走 4-bit——每 token 字节数不变，困惑度差 0.01% 而非 +3.2%，prompt 从 3-4 行降到 2 行。

## 收尾：位精确是证据，不是证明

模拟器自我定位为「the simulator, which is the spec」，但「卡与模拟器在已测 prompt 上 token 相同、logits 0 ulp」是**已执行测试上的证据，不是形式化证明**：token 相同也不必然意味着运算一致（logits 整体偏移后 argmax 可能不变），设备偏离 fp32 也不必然是硬件错（量化本就改变输出）。四行表的价值正是把这两件事拆开归因（见[架构洞察 I-1](/references/insights.md)）；而 recip(1)=0.99999994、exp2 Taylor 曾在 f=1 偏 13 ulp、WAITW 35B 连续 embed 乱序这些「修复配反例」案例（洞察 I-3），说明契约的每一条精度承诺背后都有一个能杀死 mutant 的固定点测试。

## 相关概念

- [fp32 数值契约（上）：RNE+FTZ、非完整 IEEE 754 与零/NaN 规则](/concepts/04-fp32-contract.md)
- [主机软件栈：chat/serve、卡上批量与 MoE 专家流 offload](/concepts/13-host-stack-serve-moe.md)
- [板卡与多 target：YPCB-00338、镜像演进、bcu1525、Lens 与 scoreboard](/concepts/14-board-and-targets.md)
- [示例：三种 backend 的位级对拍（validate --against）](/examples/01-bitexact-crosscheck.md)
- [示例：MoE 专家流的 WAITW + mailbox fence 协议](/examples/02-moe-mailbox-waitw.md)
- [架构洞察四元组](/references/insights.md)
- [openTPU 事实登记表 F-001~F-123](/references/facts.md)
