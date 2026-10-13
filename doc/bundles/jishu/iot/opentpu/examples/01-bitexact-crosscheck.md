---
okf_version: "0.2"
type: Example
title: "示例：三种 backend 的位级对拍（validate --against）"
description: "走读 validate.py 如何让 isa/rtl/board 三种 backend 跑出相同 token 与逐位 logits：真实命令、四行汇总表、0 ulp 判据与前置条件"
tags: [openTPU, 示例, validate, 位精确, Verilator, 板卡对拍, 验证]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T17:20:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-13T18:10:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: opentpu-facts
    resource: /references/facts.md
    title: "openTPU 事实登记表 F-001~F-123"
  - id: opentpu-source-map
    resource: /references/source-code-map.md
    title: "openTPU 源码地图与信源固定"
  - id: opentpu-pinned
    resource: "https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e"
    title: "openTPU 固定提交 ffe997e"
---

[tools/validate.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tools/validate.py) 是 openTPU 验证体系的总入口：让一个「设备」（ISA 模拟器、Verilator 跑的 RTL、或真实板卡）跑贪心解码，再与 CPU golden 和另一个设备对拍。本示例只走读它的命令行与输出形态，对应事实 F-091~F-097。本文不执行其中任何命令——RTL 对拍需要 Verilator 5 与类 Unix 环境，板卡对拍需要加锁的真机；以下均为对固定提交 `ffe997e` 的静态阅读与仓库自述（README）整理。

## 三种 backend 与五条真实命令

`--backend` 的取值在 argparse 里限定为 `isa/rtl/board`（[validate.py L909](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tools/validate.py#L901-L932)），`--against` 再加第二设备，要求 token 相同且 logits 逐位一致。README 给出的命令即是标准用法（[README L213-L229](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L213-L229)）：

```sh
# 1) ISA 模拟器对 golden，默认 int8、默认 8 个 prompt、每 prompt 16 token
python3 tools/validate.py --model qwen3

# 2) 4-bit 权重层、LM head 保 int8
python3 tools/validate.py --model lfm2 --wformat fp4 --head-format int8

# 3) RTL 对 ISA 位级对拍：慢，只跑一个 prompt、3 个 token
#    （README：16 核主机含 Verilator 构建约 4 分钟，作者报告）
python3 tools/validate.py --model lfm2 --backend rtl --against isa --tokens 3 "The capital of France is"

# 4) 板卡对 ISA：在板卡主机上、otpu-lock 加锁后运行
otpu-lock -- python3 tools/validate.py --model qwen3 --backend board --against isa

# 5) 板卡与构建主机分离：卡上只存 run，另一台主机回放对拍
otpu-lock -- python3 tools/validate.py --model qwen3 --backend board --no-golden --save card.npz
python3 tools/validate.py --model qwen3 --against card.npz
```

**看什么**：命令 1、2 只有一个设备，回答「设备离量化 golden 多远」；命令 3、4、5 有 `--against`，回答的是硬问题——两种实现是否产出**同一段 token、每一步 logits 逐位相同**。第 5 条中 `--no-golden --save` 不在卡机上跑 Hugging Face，`.npz` 带到构建主机后，ISA 模拟器会按卡里保存的 Config 运行（argparse 帮助与 `_main` 中 `Config(**m["config"])` 的逻辑，[L962-L968](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tools/validate.py#L962-L968)）。

## 参数默认值：读 argparse 而不是凭印象

核对 [L901-L931](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tools/validate.py#L901-L931) 可确认：`--model` 默认 `qwen3`；`--wformat` 默认 `int8`，可选 `int8/int4/fp4/nvfp4/mix`；`--tokens` 默认 **16**；`--dev` 默认 `/dev/xdma0`；`--cfg` 默认走 `board`（`isasim.board_config`，即生产板卡参数 S=1 D=128 MCOLS=4），可切 `design`；判据常量在 [L93-L95](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tools/validate.py#L86-L95)：`MIN_TOP1=0.8`、`KL_RATIO=3.0`、`MAX_KL=1e-3`。另有 `--weights-only`（golden 不做激活量化，只保 top-1 界）、`--no-fp32`（跳过 fp32 行）、`--resident`（常驻 decode 程序）、`--json`（逐步结果供脚本消费）。退出码即结论：PASS=0、FAIL=1。

## 四行汇总表怎么读

每次 run 的汇总固定四行（[README L236-L241](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L236-L241)，F-093）：

| 行 | 回答的问题 |
|---|---|
| device vs W+A | 设备对量化 golden：**主检查**。权重是矩阵单元实际相乘的值，激活在设备量化处按每 128 值 round int8 |
| device vs fp32 | 设备对原始 checkpoint：量化+实现合计的端到端偏差 |
| W+A vs fp32 | 纯量化代价：不涉及硬件实现 |
| W+A~ vs W+A | 把 golden 输入拨 1 个 fp32 ulp 再对自己：**地板（floor）** |

为什么需要地板行：golden 在 CPU 上的求和、归一化、指数与设备的末位舍入不可能完全一致，一个 int8 值翻号就会逐层放大。健康设备与量化 golden 的距离，应当接近 golden 自身被拨 1 ulp 后的距离——README 实测 ISA 模拟器设备 KL 为 floor 的 0.70-1.16 倍（作者报告，8 默认 prompt×16 token）。通过判据是 top-1 ≥ 80% 且 mean KL ≤ 3×floor（`--min-top1/--kl-ratio`，工具版本约定而非通用数值标准）。

## --against 的判据：0 ulp 与「一 run 103-128 步」

`--against` 不走 KL，而是位级判据。输出行长这样（[L877-L883](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tools/validate.py#L877-L883)）：

```text
rtl vs isa: tokens the same in 1/1 prompts, logits bit-exact in 1/1
            (3 steps, max 0 ulp): ok
```

`same_tokens` 要求每一步贪心选出的 token id 全同；`bit_exact` 要求 logits 向量逐位相同；`max_ulp` 是两侧 logits 的最大 ulp 差，0 才是位精确。一次板卡对拍的步数由 prompt 长度决定：README 记录的板卡实测（build 1025907f，2026-10-07，作者报告，[L304-L309](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L304-L309)）为 Qwen3-0.6B、LFM2.5-230M、Qwen3.5-0.8B 三模型的 int8 与 4bit-int8head 共 **6 run，全部 token 相同、logits 逐位一致，每 run 103-128 步、0 ulp**；同 run 设备对量化 golden 的 KL 为 floor 的 0.94-1.39 倍、top-1 94.5%-97.7%。RTL 侧的代表 run 是命令 3：3 步、含 Verilator 构建约 4 分钟（作者报告，16 核主机）。

要注意两个口径不要混：`--against` 的 0 ulp 是**实现之间**的契约证据；四行表的 KL 是**模型级数值质量**。前者是「all three must agree on every bit」的执行证据，不是形式化证明。

## 前置条件与边界

- ISA 对 golden：`pip install -e .` 后需 torch/transformers 与对应 Hugging Face checkpoint；README 报告一 run 2-14 分钟（16 核），峰值内存 2.5GB（LFM2）到 16GB（Gemma4 E2B）。
- RTL backend：rtlsim.py 依赖 Verilator 5 与 `fcntl`（Unix/WSL）；`RTL_SOURCES` 列出的 20 个 .sv（分布在 vpu/mem/top/mxu/dma/seq，其中 tech/generic 仅 2 个）现场构建到 `build/verilator`；Windows 原生环境不在支持面内。
- board backend：真机、`sudo otpu-setup` 之后、用 `otpu-lock` 独占，XDMA 设备默认 `/dev/xdma0`；分离流程用 `--no-golden --save` + 回放 `.npz`。
- 模型面：Qwen3-0.6B、LFM2.5-230M、Qwen3.5-0.8B、Gemma4 E2B（base 与 instruct）；**MoE 模型 validate 不支持**，MoE offload 的验收走另一条模拟器/卡逐位一致口径。
- 本教程不运行这些命令；上面的时间、内存、KL 与 6 run 结果均为 README 作者报告。

## 相关概念

- [/concepts/16-verification-system.md](/concepts/16-verification-system.md)：golden 构造、KL 判据与 78 文件测试金字塔
- [/concepts/14-board-and-targets.md](/concepts/14-board-and-targets.md)：板卡、镜像、target 配置与 `make bit`
- [/examples/02-moe-mailbox-waitw.md](/examples/02-moe-mailbox-waitw.md)：validate 不覆盖的 MoE 路径如何验收
- [/references/facts.md](/references/facts.md)：F-091~F-097 事实条目
