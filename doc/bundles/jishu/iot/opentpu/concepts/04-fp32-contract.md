---
okf_version: "0.2"
type: Concept
title: "fp32 数值契约（上）：RNE+FTZ、非完整 IEEE 754 与零/NaN 规则"
description: "openTPU 的 fp32 不是完整 IEEE 754：RNE+FTZ、零符号五条、canonical NaN、全序比较、P=64 部分和与 q8，由 isa.md、fp32.py、otpu_fp.sv 三方逐位约定"
tags: [openTPU, fp32, IEEE754, 数值契约, RNE, FTZ]
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

openTPU 的 TMEM 存 fp32（raw IEEE bits），VOP 的算术、MM 的 epilogue、量化器里的倒数都跑在一套自定的 fp32 语义上。这套语义写在 [docs/isa.md 的 Arithmetic 节](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L57-L133)，Python 侧的位精确模型是 [opentpu/fp32.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L1-L10)，RTL 侧是 [rtl/vpu/otpu_fp.sv](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu/otpu_fp.sv#L1-L4)。

读这套契约先要校准「精确」二字：这里的精确是指**精确遵循项目自己写下的位级规则**，而不是「正确舍入到数学真值」。除法与开方根本没有正确舍入版本（见下篇），加法乘法也刻意不实现完整 IEEE 754。三个实现只要对同一输入产出相同的 32 位，就是正确——契约的强度来自对拍测试，而不是标准符合性声明。

## RNE + FTZ：唯一舍入方向与非规格数冲洗

`add`、`sub`、`mul` 按 roundTiesToEven（偶舍入）舍入，同时**输入输出两端都冲洗非规格数**（flush to zero）：非规格输入按带符号 0 处理，非规格结果替换为带符号 0（[isa.md L59-L63](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L59-L63)）。

有一个容易被 FTZ 吞掉的边界：乘法结果若按 IEEE 舍入到非规格网格后恰好上舍入到最小正规数 `2^-126`，则**保留**。文档给的例子是 `0.5 * 0x00FFFFFF = 2^-126`，并特意注明「乘法器不得先在 24 位处舍入」。RTL 在 [fp_mul_s2](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu/otpu_fp.sv#L156-L181) 里落地这条：对 `e0 == 0`（乘积落在 `[2^-127, 2^-126)`）的情形，仅当 24 位截断尾数全 1 时输出 `0x00800000`，否则冲洗为带符号 0。

## 零的符号：五条规则

RNE 下零和的符号遵循 IEEE，文档把规则列成五条（[isa.md L64-L67](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L64-L67)）：

1. 精确抵消为 `+0`：`x - x`、`x + (-x)`、`(+0) + (-0)`；
2. `(-0) + (-0) = -0`；
3. `(-0) - (+0) = -0`；
4. `x + (-0) = x` 对任意 `x` 成立——各单元用 `v*1 + -0` 作恒等步（stream engine 空闲 stage 也跑它，对任何冲洗值都精确）；
5. 因冲洗而变零的和，零的符号取**精确和**的符号。

fp32.py 的 `chain_sum` 从 `+0` 起步（[L74](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L66-L84)），所以 `-0 + -0 + …` 串行求和得到 `+0`；这些规则由 tests/test_fp.py 与 test_fp_rtl.py 在 RTL 上对照主机 IEEE 加法器检查。

## 刻意不完整的 IEEE 754

[isa.md L68-L73](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L68-L73) 明确声明「This is not a conforming IEEE 754 implementation, by design」，裁剪项有四类：

- **只有 RNE 一个方向**：没有向零/向正/向负舍入，也没有舍入模式寄存器；
- **非规格数冲洗**；
- **没有异常标志**：上溢直接给 `±inf`，非法操作直接给 canonical NaN，不设置任何 status bit；
- **除法、开方及其他函数是下文的近似序列**，不是正确舍入运算。

这是面积与可移植性的交换：一份没有模式寄存器、没有异常通道、没有非规格通路的运算器，才能同时在 Kintex-7 DSP、通用行为模型和 Python 里做到逐位同构。

## canonical NaN 与「分指令」的 NaN 规则

系统不期望收到 NaN 输入，但一旦内部产生 NaN，它**必须**是 canonical `0x7FC00000`（[otpu_fp.sv L20](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu/otpu_fp.sv#L20)）。各指令对 NaN 并不统一，规则按硬件行为逐一定义（[isa.md L72-L79](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L72-L79)）：

| 操作 | NaN 行为 |
|---|---|
| `add` / `sub` / `mul` | 给 canonical NaN |
| `ftz`、`max` / `min`、`abs`、COPY、FILL | **保留 NaN 原有位** |
| 比较 `a > b` | 按 sign-magnitude 原始位全序（符号位置位的 NaN 比 `-inf` 还小） |
| `exp2(NaN)` | `+inf` |
| `recip(NaN)` | 带该 NaN 符号的 0（末尾符号翻转所致） |
| `rsqrt(NaN)` | 符号位置位的 NaN → `+0`；其余 → NaN |
| `log2(NaN)` | canonical NaN |
| `q8(NaN)` | `0` |

Python 侧 `_canon()` 负责把任何算术结果中的 NaN 统一成 canonical（[fp32.py L56-L63](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L56-L63)），因为 numpy 产出的 NaN 位模式随平台变化。

## sign-magnitude 全序比较

`a > b` 比较的是冲洗后值的全序：`-inf < … < -0 < +0 < … < +inf < NaN`，键函数直接由符号位与幅值位构造（[fp32.py `_key` L110-L113](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L110-L121)，RTL 对应 `fp_gt`/`fkey`）。全序的工程收益在规约：因为任意两个值都可比，**max/min 规约与求值顺序无关**，硬件可以放心用树折叠，`chain_max` 直接取 `argmax(_key(a))` 即得与折叠树相同的位。ARGMAX 里 `-0 < +0` 的 tie-break 也建立在这条序上。

## P=64 部分和折叠树：让流水线加法器跑满

VOP 的行和（RSUM/RSSQ/RDOT）不用朴素的串行累加，而是定义成一个适配流水线加法器的形状 `isum_P`，P 是 2 的幂且取 **64**（[isa.md L125-L131](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L125-L131)）：

- 部分和 `p[q] = +0 + x[q] + x[q+64] + …`，严格从左到右，每次都是 fp32 `add`；
- 再对 64 个部分和做折叠树：每轮 `p[i] = p[i] + p[i+n/2]`；
- 行用 `+0` 填充到 64 列的倍数，且填充项**真的参与加法**——一个冲洗成 `-0` 的部分和由此被翻成 `+0`。

```python
RED_PARTIALS = 64      # VOP RSUM/RSSQ: 交错部分和，再过折叠树
MM_PARTIALS  = 4       # MM：K 块间交错部分和，再折叠（MM 本身是整数精确和）
```

常量见 [fp32.py L124-L125](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L124-L145)。与浮点规约形成对照的是 **MM 的整数和是精确的**，不走这条近似通路。

## q8：half-to-even 与饱和

量化落整数的最后一步 `q8(x)` 规则很短（[isa.md L132-L133](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L132-L133)）：偶舍入到整数、饱和到 `[-127, 127]`（注意不是 int8 的 -128）、NaN 给 0。NaN→0 的来源是量化公式里「零乘以无穷 `inv`」的组（[fp32.py L167-L172](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L167-L172)）。

## 契约如何在 RTL 落地

[otpu_fp.sv](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu/otpu_fp.sv#L1-L4) 开头写明：函数全部是组合逻辑，且与 fp32.py 位精确；复合函数（exp2/recip/rsqrt/log2）是 `fp_add`/`fp_mul` 的**固定序列**。基础算子被拆成流水级：`fp_mul_s1/s2` 两级、`fp_add_s1..s4` 四级，[otpu_fpipe.sv](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu/otpu_fpipe.sv#L1-L9) 再用它们拼成流水线的 `otpu_fmul`（LAT≥2）、`otpu_fadd`（LAT≥4）、`otpu_fmadd`（两次舍入）与 `otpu_fmma`（三次舍入）。每一级都随 TMEM grant 整体停顿，语义上仍是顺序完成的一次 `add`/`mul`。

需要说明边界：以上「位精确」是仓库测试在既定环境中反复对拍出来的证据，本教程只对固定提交 `ffe997e` 做静态阅读，未运行这些测试、未构建位流、也未使用 FPGA。

## 相关概念

- [fp32 数值契约（下）：四个近似函数的固定序列与 ulp 边界](/concepts/05-elementary-functions.md)
- [VOP 向量指令：20 个功能码与 VPU](/concepts/07-vop-vpu.md)
- [位精确验证体系：validate 与测试金字塔](/concepts/16-verification-system.md)
- [事实登记表 F-001~F-123](/references/facts.md)
