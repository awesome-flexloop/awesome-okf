---
okf_version: "0.2"
type: Concept
title: "ol 内核语言与编译器：原语、布局即 API、仿射寻址与融合"
description: "ol 是 triton/Gluon 风格的 slice 级 SPMD 语言，每次调用降为一或几条机器指令；编译器用仿射地址、布局描述符与少量融合把内核 trace 成程序"
tags: [openTPU, ol, 内核语言, 编译器, compiler, DSL, SPMD]
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

## ol 是什么

ol（`import opentpu.language as ol`）是写内核的 Python 内嵌 DSL，定位写在文件头：triton.language / Gluon 风格、slice 间 SPMD，并且「Everything the hardware does is visible here: each call lowers to one or a few instructions」（[language.py L1-L18](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L1-L18)）。后一句是它与通用张量库的分界：没有隐藏算子、没有运行时调度，`ol.load` 就是 LD、`ol.quantize` 就是 QACT、`ol.dot` 就是一或几条 MM。内核在编译期被 trace 成 8×32-bit 字的指令序列，机器的刻意简单（无 cache、无乱序）因此一路暴露到语言层。

`__all__` 给出 36 个原语与类型名（另含 `LOG2E`、`LN2` 两个常量，[language.py L29-L34](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L29-L34)），按职责分八组：

- **自省**：`program_id / num_programs / block_size（=D）/ tmem_words / mxu_columns（=MCOLS）`；
- **存储**：`load / store / quantize / stationary / quantize_into`；
- **矩阵**：`dot`；
- **算术与归约**：`exp2 / log2 / recip / rsqrt / abs / maximum / minimum / max / sum / sumsq / outer`，构造类 `full / zeros / empty`；
- **集合**：`all_gather / all_reduce`；
- **控制**：`range / static_range / release / jit`；
- **KV**：`kv_append`；
- **状态引擎**：`deltanet_step / state_step / has_dstep / has_stream`（见 [12-stream-dstep-caps.md](/concepts/12-stream-dstep-caps.md)）；
- 外加类型 `Tensor / QTensor / KVDesc / Tile / CompileError`。

## dot：acc、out 与 acc_scale

`ol.dot(a, w, acc=None, out=None, rowmax=False, acc_scale=None)` 的签名即 MM 的能力表（[language.py L105-L117](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L105-L117)）：`a[M,K] @ w[N,K]^T`，块尺度 int8 操作数、fp32 累加；`a` 可以是 TMEM tile（即时量化）或 `ol.quantize` 的驻留结果。`acc=y` 原位累加（MM ACC），`out=y` 覆写指定 tile（软件流水的双缓冲之一）；`ol.max(dot(...), axis=1)` 由 MXU epilogue 的 RMAX 免费得到；`acc_scale=alpha` 则先把累加器逐行乘 alpha 再加新积——flash-attention 的重缩放步，落在 MM ASCALE 上。配套的 `ol.quantize(a*v[None,:], rscale=..., cscale=...)` 把列尺度、RMSNorm 的 `x*r*gamma` 折叠进 QACT（详见 [08-quantization-unit.md](/concepts/08-quantization-unit.md)）。

## 硬件循环与 static_range

ol 区分两种循环（[language.py L330-L351](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L330-L351)）：`ol.range(n)` 映射到 LOOP 指令，**body 只 trace 一次**，跨迭代携带的值靠 `.set()` 传递；`ol.static_range` 就是普通展开。`ol.release(var)` 声明内核不再使用运行时值 var，其参数寄存器可被地址复用——这对应 R15-k 起的参数寄存器分配（见下）。`ol.kv_append(kv, h, pos, k, v)` 则把 QST ROW/普通 scale 行、V 转置、半宽头等 KV 布局细节封成一个原语（[language.py L355-L387](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L355-L387)）。

## kernels 七模块

内核库在 `opentpu/kernels/`，七个业务模块各守一类模型结构（真实签名）：

- **attention.py**：`attention_decode(q, kv, out, n_q_heads, n_kv_heads, seq_len, block)` 与 `attention_layer(h, gamma, wq, wk, wv, wo, cos, sin, kv, out, n_q_heads, n_kv_heads, pos, block, eps)`，配套 `Bucket/Blocks/RowMasks/RowTiles/TileSeq` 做分块；
- **mlp.py**：`swiglu_down(xs, w_gate, w_up, w_down, chunk=None, act=silu, loop=False)` 与 `mlp(h, gamma, w_gate, w_up, w_down, out, eps, chunk=None)`——gate/up 下一块在流时 VPU 算当前块；
- **lib.py**：`rmsnorm(x, gamma, eps)`、`silu/sigmoid/gelu_tanh/softcap/softplus/rope/rope_rows` 八个向量例程；
- **layouts.py**：`head_parallel_attention_weights(wq, wk, wv, wo, n_q_heads, n_kv_heads, d, S)` 决定多 slice 的头排布；
- **mailbox.py**：`wait_served(mbox, comment=..., timeout=TIMEOUT)`、`post(mbox, ids)`——MoE fence 协议；
- **gather.py**：`onehot(D, M, fmt)`、`table(data, gscale, n, k, fmt, D)`、`gather_row/gather_record`，把 embedding/表查找编成分块 MM；
- **deltanet.py**：`head_step(St, k, v, q, decay, beta, w, o, fused=True, prefetch=None)` 与 `gated_deltanet_step(state, q, k, v, a, b, A_log, dt_bias, state_out, out, fused=True)`。

## compiler.py：仿射寻址、布局即 API 与融合

编译器 1929 行，核心类型在 [compiler.py L32-L1928](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/compiler.py#L32-L1928)：`Affine` 是「常数 + 运行时变量整数系数」的地址表达式（`div_exact` 强制对齐，如 D 字节边界）；`Tensor` 是 DRAM fp32 描述符（base/shape/strides，切片只改仿射基址）；`QTensor` 是流式权重描述符（data/scale/rs/srs/wf/k0/rsc/parts/tiles，列分块只移 k0 不改尺度地址）；`Tile` 是 TMEM tile——二维累加器刻意拿到奇数行 stride（列数+1），使 MXU 一行结果落到不同 bank，这就是「布局即 API」：描述符的形状决定指令的步长字段，而不是运行时 reshape。`Builder`（L712-L1868）负责排放指令与 TMEM 安置。

融合都在「刚发射的指令」上做 peephole，不改写数值语义：`fuse_cscale` 把无名临时量上的列乘折进 QACT CSCALE；`fuse_exp2_sub` 把新鲜临时量上的 `exp2(a-b)` 就地改写成一条 EXP2SUB（[compiler.py L1263-L1271](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/compiler.py#L1263-L1271)）；`fuse_sum_products` 把 `sum(a*b)` / `sum(a*a)` 认成 RDOT/RSSQ，不 trace 乘积 tile；`fuse_mm_rmax` 接 RMAX；`retarget` 消除新鲜临时量的拷贝。

## @ol.jit、trace_fit 与参数寄存器

`@ol.jit` 就是 `compiler.jit`，返回 `Kernel`（[compiler.py L1884-L1929](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/compiler.py#L1884-L1929)）；`Kernel.trace(cfg, sid, bound)` 执行一次 Python 函数体收集指令，`trace_fit` 先按 next-fit 安置 TMEM，报「TMEM exhausted」再以 best-fit 重试，产物是 `Builder`，最终装进 `Compiled`（每 slice 程序、store 记录与 DRAM 布局）。运行时参数的寄存器分配有固定方向：第 k 个不同 `(var, c)` 占 `R15-k`，地址寄存器从 R1 向上增长，`ol.release` 归还，只有将不够时才复用/搬运（`arg_reg(k) = 15 - k`，[compiler.py L111-L114](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/compiler.py#L111-L114)；与 ISA 的 R8-R15=ARG 约定见 [03-sequencer-and-chaining.md](/concepts/03-sequencer-and-chaining.md)）。指令编码本身见 [02-instruction-set.md](/concepts/02-instruction-set.md)。本篇为静态阅读：未运行测试、未构建位流、未使用 FPGA。

## 相关概念

- [指令系统：17 条指令与寄存器约定](/concepts/02-instruction-set.md)
- [sequencer：顺序派发与 HALT CHAIN](/concepts/03-sequencer-and-chaining.md)
- [STREAM/DSTEP 状态引擎与 CAPS 能力位](/concepts/12-stream-dstep-caps.md)
- [示例：一次矩阵乘穿过六层](/examples/00-matmul-through-six-layers.md)
- [示例：三种 backend 的位级对拍](/examples/01-bitexact-crosscheck.md)
