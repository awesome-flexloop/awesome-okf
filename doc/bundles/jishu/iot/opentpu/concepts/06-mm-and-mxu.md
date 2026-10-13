---
okf_version: "0.2"
type: Concept
title: "MM 指令与四列脉动 MXU：48-bit 精确累加、epilogue 与 replay"
description: "MM 的字段与 flags、组整数和与位移 B、48-bit 精确累加界防护、三次舍入 epilogue、RMAX/ASCALE，以及四列脉动 MXU 的 DSP cascade、第九颗 DSP、E=4 lane 与 replay 透明性"
tags: [openTPU, MM指令, MXU, 脉动阵列, DSP48, 整数累加]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T16:20:00+08:00"
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

MM（opcode `0x20`）是 openTPU 唯一的矩阵乘指令：权重行从 DRAM 流入，ACT RAM 里的量化激活作驻留操作数，每个输出先在硬件里累加成**一个精确整数**，再经一次 fp32 epilogue 落成 TMEM 中的 fp32。契约见 [isa.md MM 节](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L178-L225)，构造器是 [isa.py 的 mm()](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L381-L406)，RTL 是 [rtl/mxu/otpu_mxu.sv](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/mxu/otpu_mxu.sv#L1-L44)。

## 字段与 flags 全表

MM 仍是 8×32-bit 定长编码，立即数字段如下（[isa.md L180-L197](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L180-L197)）：

| 字段 | 位置 | 含义 |
|---|---|---|
| `sa` | R[ra]+w1，字节 | 流操作数（权重）行起点，D 字节对齐 |
| `ssa` | R[rb]+w2，字节 | 权重 scale 行起点（ASCALE 时改义为 TMEM 地址） |
| `out` | R[rc]+w3，字 | TMEM 输出起点 |
| `N` / `KB` / `k0` | w4[15:0]/[23:16]/[31:24] | 权重行数 / K 维块数 / scale 行内首块号 |
| `rs` | w5，字节 | 权重行跨度 |
| `ors` / `M` / `ab` | w6[15:0]/[23:16]/[31:24] | 输出行跨度（字）/ 输出行数 / 首个 ACT RAM 块 |
| `srs` | w7，字节 | scale 行跨度 |

flags：bit0 `UNIT`（无 scale 行，`Sw=1, dw=0, m=1`）、bit1 `ACC`（累加进 out）、bit2 `RMAX`（随行最大）、bit3 `ASCALE`（需 UNIT+ACC，flash-attention 重缩放）、bits[5:4] `WF`（0 int8 / 1 int4 / 2 FP4 / 3 NVFP4）、bit6 `PAIR`、bit7 `RSC`（[isa.py L19-L29](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L19-L31)）。构造器把约束做成 `ValueError`：PAIR 必须 4-bit 且 `k0` 偶，RSC 不得与 NVFP4 同用，ASCALE 必须 UNIT+ACC。形状约束：`N≥1、KB≥1、0<M≤ACT_ROWS`；RMAX/ASCALE/PAIR 需 `M≤MCOLS`（PAIR 要 `2M≤MCOLS`）；`M>MCOLS` 时流操作数行必须放进 MXU 的 chunk FIFO（int8 为 KB 个 chunk、4-bit 为 `ceil(KB/2)`，板卡 FIFO 深 1024）。

## 48-bit 精确整数累加

核心伪码（[isa.md L203-L218](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L199-L225)）：

```text
W = 16 (int8) | 11 (int4/fp4) | 13 (nvfp4)      # 移位窗口
c   = Σ_{i∈g} ACT[r][(ab+k)·D+i] · w[i]          # 每组一个精确整数和
sh  = W - dw(n,k,g) - da[r][ab+k][b]             # 权重偏移 + 激活偏移
acc += (sh ≥ 0 ? m(n,k,g) << sh : 0) * c         # |acc| < 2^47
y   = (i2f(acc) * Sw[n]) * (Sa[j][ab] * 2^-W)    # 每个输出一次：三次舍入乘法
```

组（group）是 `D/4` 元素的子块（NVFP4 为 `D/8`）。`c` 是 int8/int4 乘积的精确整数和；权重值带的幂次偏移 `dw`、激活行尺度记录里的子块偏移 `da` 合成为左移 `sh`，乘上权重乘子 `m` 得 `B = m<<sh`。模拟器用 int64 逐组算这条式（[isasim.py `_mm` L510-L522](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L510-L522)），`sh<0` 的组直接置 0。

界防护保证累加始终精确（[isa.md L220-L224](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L220-L224)）：组和 `|c| < 2^19`（int8；4-bit `< 2^16`），`B < 2^17`，每条 int8 MM 至多 `4*255` 个组，整行 `|acc| < 2^47`——48 位有符号累加器不溢出。两偏移之和超过 W（`sh<0`）的组尺度低于行最大尺度的 `2^-W`，丢弃不计；格式扫描实测这类组至多 **7e-5**（docs/mx_mxu.md 3.3，作者契约文档给出的测量）。另一条一致性约束：一条 MM 的块 `ab..ab+KB-1` 必须持有同一个 `Sa`（同一次 QACT 写入），模拟器发现不同即报错。

## epilogue：三次舍入乘法与 RMAX/ASCALE

整数累加结束后，每个输出只做一次 fp32 收尾：`i2f(acc)`（RNE 整数转 fp32），再乘权重行尺度 `Sw[n]`，再乘激活行尺度 `Sa[j][ab]*2^-W`——三次舍入乘法、逐级 FTZ。`ACC` 时 `y = T[out] + y`；`ASCALE`（须 UNIT+ACC）时 `y = T[out+j·ors+n] * T[ssa+j] + y`，先乘后加，正是 **flash-attention 的重缩放校正步**，免一条 VOP 向量遍。`RMAX` 把每行输出的最大值从 n=0 折叠写到 `T[out + M·ors + j]`——softmax 需要的行最大值由 MXU epilogue **免费随行产出**（[isasim.py L524-L532](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L523-L532)）。

## RTL：四列脉动阵列与第九颗 DSP

生产配置（[targets/ypcb-00338.toml](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/ypcb-00338.toml#L26-L40)）是 `MCOLS=4`、`MXU_IMPL=2`（脉动式）、`MXU_CL=16`、`MXU_E=4`、`FIFO_DEPTH=1024`。[otpu_mxu.sv 头注释](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/mxu/otpu_mxu.sv#L1-L44)描述的数据路径：

- **预取**：权重 N 行×KB 块走 DRAM port B，每周期一个 D 字节 chunk，经 FIFO 预取；scale 行走 port A（32 字节线）；每个 chunk 在最多 MCOLS 条驻留行间复用；
- **脉动积链**：一条 chain 是 `CLS = min(CL, D/8)` 个 DSP48 积的 cascade，生产点 CL=16、D=128，故 CLS=16，每个链尾恰好吐出一个组和；
- **列尾单元 otpu_mxce**（[rtl/tech/xilinx7/otpu_tech_dsp.sv L55-L65](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/tech/xilinx7/otpu_tech_dsp.sv#L55-L65)）：一组**九颗 DSP48E1**——前 8 颗各接一个组的链尾，`B = m<<sh` 在 fabric 里移位（提前两周期），积沿 cascade 逐级相加（0-3 与 4-7 两组错一个周期，p3、p7 两级寄存，133.33MHz 收敛）；**第 9 颗**在行首把 X 置 0、之后累加 PCIN，逐块累加整行，全程留在 cascade 上；
- 列间错拍一个周期，行和去斜对齐后写入结果 FIFO，PAIR 的两半在此相加。

## epilogue lane：i2f48 RNE 与 E=4

drain 每周期从结果 FIFO 取队头行至多 E 个结果（遇 TMEM bank 冲突则少取）进共享 lane。lane 模块 [otpu_mx_lane](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/mxu/otpu_mxu.sv#L1511-L1565) 每结果过一次：`i2f48`（符号/幅值→前导零→规格化→24 位偶舍入，`|x|<2^47` 故无溢出无亚正规，4 级），再两级 `otpu_fmul` 完成 `*Sw` 与 `*Sa'`，之后是 TMEM 写或 ACC/ASCALE 的读-改-写。结果 FIFO 之后的所有流水级只在拿到 TMEM grant 时前进。

## 技术映射：DSP48E1 / DSP48E2 / generic

同一套脉动结构按 target 换工艺细胞：7 系列（xc7k480t）用 [rtl/tech/xilinx7 的 DSP48E1](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/tech/xilinx7/otpu_tech_dsp.sv#L1-L6)，UltraScale+（VU9P）用 [xilinxus 的 DSP48E2](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/tech/xilinxus)，ASIC 路径用 [generic 行为模型](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/tech/generic)（Verilator 对拍也选它）。模拟器与测试只认位结果，不认底层是哪颗 DSP。

## replay：硬件重放流数据，程序看不见

当 `M > MCOLS`（生产点 ACT_ROWS=16、MCOLS=4），同一条权重流被消费 `G = ceil(M/MCOLS)` 次：组 0 从 FIFO 弹出但不释放，后续组重读同一批 FIFO 项，最后一组才释放，权重从 DRAM 只流一次（行须放进 FIFO：`KB ≤ DEPTH`）；drain 的 TMEM 地址每组步进 `MCOLS*ors`（[otpu_mxu.sv L34-L39](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/mxu/otpu_mxu.sv#L34-L39)）。这是微结构重放，不是语义重试——ISA 契约保证结果不依赖 MCOLS/ACT_ROWS/LANES，模拟器换任何 Config 算出的位都相同（[isasim.py Config L27-L32](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L18-L36)）。

## 相关概念

- [量化器：QACT/QST 与行尺度 Sa/da](/concepts/08-quantization-unit.md)
- [权重格式族：int8/int4/FP4/NVFP4](/concepts/09-weight-formats.md)
- [PAIR 列复用、RSC K-cache 与 DUP](/concepts/10-pair-rsc.md)
- [事实登记表 F-001~F-123](/references/facts.md)
