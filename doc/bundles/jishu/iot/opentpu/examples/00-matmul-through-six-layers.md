---
okf_version: "0.2"
type: Example
title: "示例：一次矩阵乘穿过六层（MLP swiglu_down）"
description: "从 kernels/mlp.py 的一个 ol.dot 出发，逐层走到编译器指令、模拟器整数累加与四列脉动 DSP 链的静态走读"
tags: [openTPU, 示例, MLP, MM, MXU, ol, 编译器, 位精确]
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

本示例做一次「垂直切片」阅读：盯住 openTPU 的 MLP 块里 down 投影的一次矩阵乘，看它如何从 [kernels/mlp.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/kernels/mlp.py#L33-L149) 中一个普通的 Python 调用，逐层变成 ol 原语、8×32-bit 字的 MM 指令、模拟器里的精确整数累加，最后变成 RTL 四列脉动阵列上的 DSP48 cascade 链。六层链对应事实 F-066、F-071、F-044、F-052、F-056。

这是源码教程式的静态走读：本文不运行测试、不构建位流、也不使用 FPGA；所有片段均取自固定提交 `ffe997e` 的工作树。

## 起点：业务内核里的 down 投影

SwiGLU MLP 的数学是 `out = h + W_down(silu(W_gate xn) * (W_up xn))`。内核顶层 [`mlp`](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/kernels/mlp.py#L130-L149) 先把 RMSNorm 后的输入量化一次，然后交给 `swiglu_down`：

```python
@ol.jit
def mlp(h, gamma, w_gate, w_up, w_down, out, eps, chunk=None):
    sid = ol.program_id()
    x = ol.load(h)
    xs = ol.quantize(rmsnorm(x, ol.load(gamma), eps))   # stationary, reused by all gate/up MMs
    y = swiglu_down(xs, w_gate, w_up, w_down, chunk)
    ...
    ol.store(out[:, mine], x[:, mine] + y)
```

注意 `xs` 只量化一次，之后被所有 gate/up 矩阵乘复用——这是「驻留操作数」概念的来源。本示例跟踪的 down 投影在 [`swiglu_down`](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/kernels/mlp.py#L51-L68) 的内层循环里：

```python
for t in ol.static_range(S):
    cols = w_down[:, t * f_loc + c0:t * f_loc + c0 + C]
    at = a[:, t * C:(t + 1) * C]
    if y is None:
        y = ol.dot(at, cols)
    else:
        ol.dot(at, cols, acc=y)          # y += a_t . W_down[:, chunk of slice t]
```

**看什么**：这里没有任何手写指令。切片 `w_down[:, ...]` 是布局描述，`acc=y` 表达原位累加，数学形状 `[M,K] @ [N,K]^T` 一目了然；第一个 chunk 覆写、后续 chunk 累加的区别仅在 `acc=` 参数。

## 第一层 ol：dot 与 quantize 原语

[`ol.dot`](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L105-L117) 的真实签名把硬件能力直接摆在参数上：

```python
def dot(a, w: QTensor, acc: Tile | None = None, out: Tile | None = None,
        rowmax: bool = False, acc_scale: Tile | None = None) -> Tile:
    """a[M, K] @ w[N, K]^T with block-scaled int8 operands and fp32 accumulation."""
```

`a` 可以是 TMEM tile（即时量化）或 `ol.quantize()` 的结果；`acc` 原位累加、`out` 覆写；`rowmax` 对应 MM epilogue 免费随行最大；`acc_scale` 是 flash-attention 的累加器重缩放。配套的 [`ol.quantize`](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L79-L90) 把 TMEM 行量化进 ACT RAM，`rscale/cscale` 参数可把 RMSNorm 的 `x*r*gamma` 折叠进量化器（QACT RSCALE/CSCALE），免掉单独的向量遍。ol 的定位是「每次调用降为一或几条指令」（F-064/F-066/F-067）。

## 第二层编译器：原语到指令字段

[`Builder.dot`](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/compiler.py#L1710-L1789) 负责把原语调用变成指令。它先复用或新建驻留操作数（`st = a if isinstance(a, Stationary) else self.quantize(a, ...)`，对应一条 QACT），检查 `K == st.KB * D`，再对驻留操作数的每个 QACT 区间发一条 MM：

```python
ins = I.mm(sa + k0 * bpb, ssa, out.base + m0 * ors, N, k1 - k0, w.rs, ors, mc,
           ab + k0, w.srs, unit=unit, acc=acc is not None or not first,
           rmax=rowmax and last, wf=w.wf, pair=ppair, k0=kp, ...)
```

**看什么**：编译器的决策全在这一行附近——`unit`（无 scale 行）、首条覆写其余 `ACC`、`wf` 权重格式、4-bit 时的 `pair` 列复用与偶块对齐检查、`N+1` 的奇数行步长（让一行 M 个结果落到不同 TMEM bank）。内核里一句 `ol.dot(at, cols, acc=y)` 到这里就是字段填好的一条 `I.mm`。

## 第三层 ISA：QACT 与 MM 的 8×32-bit 字

指令构造器在 [isa.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L381-L420)，字段即契约（F-044、F-052）：

```python
def mm(sa, ssa, out, n, kb, rs, ors, m, ab, srs, unit=False, acc=False, rmax=False,
       ascale=None, wf=W8, pair=False, k0=0, rsc=False, ra=0, rb=0, rc=0, comment=""): ...

def qact(src, rows, ab, kb, srs, row=False, cscale=None, rscale=None, dup=False, ra=0,
         comment=""): ...
```

`sa` 是流操作数（权重）行的 DRAM 字节地址，`ssa` 是权重 scale 行，`out` 是 TMEM 输出；`N/KB/k0` 描述权重形状，`M/ab` 描述 ACT RAM 的行与起始块，`rs/ors/srs` 是三个步长；`flags` 装 `UNIT/ACC/RMAX/ASCALE/WF[5:4]/PAIR(bit6)/RSC(bit7)`。构造器里的 `_check` 就是规则：PAIR 要求 4-bit 权重且 `k0` 为偶，RSC 不能配 NVFP4，ASCALE 需要 UNIT+ACC。down 投影每 chunk 的第一条 MM 覆写 `y`，其余带 ACC——指令位上的差别只有一个 flag。

## 第四层 isasim：同一语义的精确整数累加

模拟器 [`Slice._mm`](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L458-L532) 是 ISA 的可执行规格。核心几行把「块尺度 int8、fp32 累加」落成精确整数运算：

```python
c = np.einsum("jkgi,nkgi->jnkg", act.reshape(...), wel[...].astype(np.float64)).astype(np.int64)
sh = W - dw[None, n0:n1] - da[:, None]                 # 组移位
B = np.where(sh >= 0, mw[...] << np.maximum(sh, 0), 0) # sh<0 的组丢弃
acc[:, n0:n1] = (B * c).sum(axis=(2, 3))               # 48-bit 精确
y = F.mul(F.mul(F.i2f(acc), sw[None, :]),
          F.mul(self.ascale[:M, ab][:, None], np.float32(2.0 ** -W)))
```

每组先求乘积和 `c`，按权重/激活偏移算移位 `sh` 与系数 `B`，沿块和组做整数累加；每个输出只在 epilogue 离开整数域一次：`i2f48` 后三次舍入乘法挂上权重行尺度 `Sw[n]` 与激活行尺度 `Sa[j]`（F-045）。`acc` 在 numpy 里是 int64，但契约保证 `|acc| < 2^47`。读到这里应回头核对：第三层指令的每个字段都能在这几行找到消费点。

## 第五层 RTL：四列脉动阵列上的 DSP 链

[otpu_mxu.sv](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/mxu/otpu_mxu.sv#L1-L44) 的开头注释就是微结构说明书（F-056）：权重 N 行×KB 块自 DRAM port B 经 FIFO 预取，scale 走 port A，每个 chunk 被最多 MCOLS 个驻留行复用；阵列由 `CLS = min(CL, D/8)` 个 DSP48 积的 cascade 链构成，链尾恰是一组的组和；列尾（otpu_mxce）收 8 个组和、 fabric 里做移位、沿 cascade 求和，在**第 9 颗 DSP** 里累加整行，全程 48-bit；结果进 FIFO，由 E 条 epilogue lane 做 `i2f48`（RNE）与两次乘法后写 TMEM。模拟器里的 `(B*c).sum(...)` 与硬件的 cascade 链是同一组算术的两种表述。生产配置 D=128、MCOLS=4、LANES=8，技术映射在 xc7k480t 上用 DSP48E1。

## 第六层：位流与主机

再往下，同一份 RTL 经 Vivado 综合进 Kintex-7 位流（板卡构建是 `make -C boards/ypcb-00338 bit`，本示例不执行）；主机侧只负责把量化好的权重映像放入片上 DRAM 并启动一次 run，sequencer 按程序序把 MM 派给 MXU。ol/编译器/模拟器/RTL 四者对「写进 TMEM 的每一位」必须一致——这正是 [docs/isa.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L1-L5) 声明的三方契约。

## 层间映射表

| 层 | 位置（ffe997e） | 这次矩阵乘的形态 | 阅读时重点核对 |
|---|---|---|---|
| 业务内核 | [mlp.py L51-L68](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/kernels/mlp.py#L51-L68)、[L130-L149](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/kernels/mlp.py#L130-L149) | `ol.dot(at, cols, acc=y)` | chunk 切片、首块覆写/其余累加、`xs` 只量化一次 |
| ol 原语 | [language.py L79-L117](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L79-L117) | `dot/quantize` 两个调用 | `acc/out/rowmax/acc_scale`、RSCALE/CSCALE 折叠 |
| 编译器 | [compiler.py L1710-L1789](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/compiler.py#L1710-L1789) | 每 QACT 区间一条 `I.mm` | K 对齐、unit/acc/wf/pair 决策、地址寄存器与行步长 |
| ISA | [isa.py L381-L420](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L381-L420) | QACT + MM，各 8 个 32-bit 字 | `sa/ssa/out/N/KB/M/ab` 与 flags；构造器 `_check` 即规则 |
| 模拟器 | [isasim.py L458-L532](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L458-L532) | numpy 精确整数累加 + fp32 epilogue | `c/sh/B`、`|acc|<2^47`、三次舍入乘法 |
| RTL | [otpu_mxu.sv L1-L44](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/mxu/otpu_mxu.sv#L1-L44) | 四列脉动 + DSP48 cascade | `CLS=min(CL,D/8)`、第 9 颗 DSP、48-bit、E lane |

建议的阅读动作：在模拟器的 `acc[:, n0:n1] = (B * c).sum(...)` 处打断点式心算，拿一个 chunk 的 `N/KB/M` 回推编译器那行 `I.mm(...)` 的实参，再到 RTL 注释里找同一组「组和→移位→列尾累加」的词。三层用词不同，数据流是同一条。

## 相关概念

- [/concepts/06-mm-and-mxu.md](/concepts/06-mm-and-mxu.md)：MM 字段、48-bit 累加界防护与四列脉动 MXU 的完整说明
- [/concepts/08-quantization-unit.md](/concepts/08-quantization-unit.md)：QACT/QST、行尺度 Sa/da 与 q8 公式
- [/concepts/11-ol-language-compiler.md](/concepts/11-ol-language-compiler.md)：ol 原语全集、仿射寻址与编译器融合
- [/references/facts.md](/references/facts.md)：F-044、F-052、F-056、F-066、F-071 事实条目
