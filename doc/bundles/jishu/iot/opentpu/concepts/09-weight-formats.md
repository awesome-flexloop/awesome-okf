---
okf_version: "0.2"
type: Concept
title: "权重格式族：int8/int4/FP4/NVFP4 与 scale 行布局"
description: "MM 的 WF 字段裁决四种流式权重格式：E2M1 码值、三种 scale 行逐字节布局、w·m·2^-dw·Sw 解码式与 4.25 bits/weight 的真实构成"
tags: [openTPU, 权重格式, FP4, NVFP4, MXFP4, 量化, MM]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T16:40:00+08:00"
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

## WF 四档与 E2M1 码值

MM 的 flags[5:4] 是 WF（weight format）字段，四个取值定义在 [isa.py L25-L27](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L25-L27)：`W8=0` int8、`W4I=1` int4、`W4F=2` FP4（E2M1）、`WNV=3` NVFP4。配套的移位窗口 `MX_W = {0:16, 1:11, 2:11, 3:13}` 决定累加时哪些低幅组被丢弃（见 [06-mm-and-mxu.md](/concepts/06-mm-and-mxu.md)）。

int8 行每元素 1 字节；三种 4-bit 格式都是**两元素塞一字节**：一块 D 个元素只占 D/2 字节，偶数下标元素在低 nibble、奇数在高 nibble（[isa.md L230-L236](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L230-L236)）。nibble 的解释分两种：int4 是二补码整数 `w = c - 16*c[3]`，范围 -8..7（码表 `DEC_INT4`，[quant.py L264](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L264)）；E2M1 则把码值**乘 2** 使用——幅度码取自集合 `{0, 1, 2, 3, 4, 6, 8, 12}`，对应浮点值 `{0, .5, 1, 1.5, 2, 3, 4, 6}`，bit3 是符号位（`DEC_FP4` 与 `E2M1` 表，[quant.py L39-L40](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L39-L40)、[L265](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L265)）。「乘 2」这个约定很关键：存储的 E2M1 矩阵本身自带一半尺度，所以 fp4 打包时行尺度要减半（`sw = Sw * 0.5`，[quant.py L363-L365](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L363-L365)），NVFP4 行则带 16 倍尺度。

## scale 行的逐字节布局

每个权重行 n 的 scale 行从 `ssa + n*srs` 开始：先是该行的 fp32 尺度 `Sw[n]`（一个小端字），随后是各 K 块的偏移与乘数，MM 的块 k 对应该行的 k0+k 块。三种布局来自 [isa.md L238-L255](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L238-L255)，与 [quant.py 的 scale_bytes L292-L308](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L292-L308) 逐字对应：

| WF | 头部 | 每块占用 | 对齐 |
|---|---|---|---|
| 0 int8 | `Sw`（4 字节） | 1 字节 `dw`（位于 `4 + k0 + k`），`m = 1` | ssa/srs 为 4 的倍数；行长 `4 + 4*ceil(KB/4)` |
| 1 int4 / 2 fp4 | `Sw` + 1 个保留字（8 字节） | 1 个字（4 字节）：低 8 位 `dw`，随后每 6 位一个子块乘数 `m`（4 个，位 `8+6b`，范围 0..63） | 8 字节；行长 `8 + 8*ceil(KB/2)` |
| 3 nvfp4 | `Sw` + 3 个保留字（16 字节） | 2 个字（8 字节）：8 个 E4M3 尺度字节，每个管 D/8 个元素 | 16 字节；行长 `16 + 16*ceil(KB/2)` |

NVFP4 的 E4M3 字节 `s`（符号位必为 0）这样解码：`E = s[6:3]`、`M = s[2:0]`，乘数 `m = E ? 8+M : M`，偏移 `dw = 15 - max(E, 1)`。硬件把 0x7F 读作 15·2^0 而非 NaN（[quant.py L817-L861](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L817-L861) 的导入器注释明确利用了这点）。

## 解码式与「4.25 bits」的构成

把一个权重还原成实数，公式很短（[isa.md L248-L250](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L248-L250)）：

```text
weight = w * m * 2^-dw * Sw[n]        # NVFP4: E4M3 值 m*2^(max(E,1)-10) 再乘 2^-5·Sw
```

即「每行一个 fp32 尺度 + 其下按块的幂次偏移」两级结构（文档称之为 MX 风格）。Python 侧 `unpack_scales`（[quant.py L428-L449](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L428-L449)）与 `dequantize_mxu`（[L460-L473](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L460-L473)）就是这张表的逆运算，且非正规 Sw 按 0 冲洗——与 MXU epilogue 的 FTZ 一致。

因此「4-bit」从来不是「全模型 4 位」。以 fp4 为例：每权重 4 个值位，加上每 128 元素摊一份的两级尺度，作者报告的存储口径是 **4.25 bits/weight**（[README L115-L118](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L115-L118)；docs/quant.md 的格式族表给 int8 8.25、MXFP4 4.25、NVFP4 4.5、bf16 块尺度的 int4 族 4.25-5，[docs/quant.md L130-L134](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/quant.md#L130-L134)）。文档实测结论是 fp4 以接近 NVFP4（4.5 bits）的质量明显优于 MXFP4（同为 4.25 bits，[docs/quant.md L10-L14](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/quant.md#L10-L14)，作者报告）。

## NVFP4/MXFP4 的精确导入

checkpoint 侧若已是标准格式，不必重新量化：`import_nvfp4(codes, e4m3_scales, tensor_scale)` 与 `import_mxfp4(codes, e8m0)` 把外部矩阵**精确**换入 MXU 布局，无法精确表达时抛 `NotExact`（[quant.py L768-L814](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L768-L814)、[L817-L861](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L817-L861)）。MXFP4（OCP，每 32 元素一个 E8M0）按指数跨度裁决：一个 K 块内四个子块指数跨度 ≤5 则落成 fp4（`m = 2^(e_b - e_min)`），跨行跨度 ≤17 则落成尾数为 0 的 nvfp4，再大就 NotExact。表示本身始终精确，被窗口丢弃的只是 MM 累加中低于行顶 W 个八度假说的组。

## LM head 保 int8 与提速机制

所有混合格式方案里 **LM head 一律保 int8**（docs/formats.md 的选档规则明写「The LM head stays int8 in every mix」）；大模型还存在按层选格式的混合布局（如 Gemma4 E4B-it 默认让头与前 12 层 gate/up 走 4-bit），总之不能写成「全模型 4bit」。提速的机理也不是算力翻倍，而是**减 DRAM 流量**：decode 每 token 要把全部权重流式读一遍，天然带宽受限，权重字节下降约 1/3。作者报告的收益是 decode +40%（Qwen3.5）到 +45%（Qwen3、LFM2），口径为 README 结果表（[README L115-L118](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L115-L118)）；让 4-bit 在 MXU 上跑满速则要靠 PAIR 列复用，见 [10-pair-rsc.md](/concepts/10-pair-rsc.md)。

## quant.py 关键 API

- `quantize_mxu(W, fmt, D=128) -> (rows, srows)`：产出行字节与 scale 行，分行处理（[L510-L523](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L510-L523)）；
- `pack4 / unpack4`：nibble 与字节互转，低 nibble 在前（[L275-L284](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L275-L284)）；
- `e2m1_code / e4m3`：RNE 落到 E2M1/E4M3 码格（[L69-L116](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L69-L116)）；
- `dequantize_mxu`、`fake_w`、`MXW / mx_matmul`：float64 仿真，连 MM 的丢组规则都复刻，供 validate 与格式扫描作 golden。

## 相关概念

- [量化器：QACT/QST、行尺度 Sa/da 与 q8 公式](/concepts/08-quantization-unit.md)
- [PAIR 列复用、RSC K-cache 与 DUP](/concepts/10-pair-rsc.md)
- [MM 指令与四列脉动 MXU](/concepts/06-mm-and-mxu.md)
