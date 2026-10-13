---
okf_version: "0.2"
type: Concept
title: "fp32 数值契约（下）：exp2/log2/recip/rsqrt 的固定序列与 ulp 边界"
description: "四个近似函数各自的范围缩减、minimax 系数、魔数、Newton 次数、校正步与 ulp 边界；固定序列是 Python 模型、RTL 与 VPU slot 程序逐位一致的手段"
tags: [openTPU, fp32, minimax, Newton迭代, ulp, 数值契约]
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

openTPU 没有除法器、开方器，也没有超越函数单元。`RECIP`、`RSQRT`、`EXP2`、`LOG2` 四个 VOP 功能码（以及量化器内部对 `recip` 的调用）全部用**仅含 fp32 加/乘的固定运算序列**实现：魔数或 minimax 多项式给初值，Newton 迭代收敛，个别函数再加一个校正步。契约同时规定序列形状、系数的十六进制位、ulp 误差边界与精确点，写在 [isa.md L82-L121](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L82-L121)，Python 模型见 [fp32.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L175-L268)，RTL 见 [otpu_fp.sv 的 fp_exp2/fp_recip/fp_rsqrt/fp_log2](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu/otpu_fp.sv#L440-L534)。

## exp2：7 阶 minimax + 指数域拼接

范围处理：`x < -126` 返回 `+0`，`x >= 128` 返回 `+inf`（NaN 经链首 `x*1+-0` 变 canonical 后也走 `+inf`）。中段做范围缩减 `i = floor(x)`、`f = x - i2f(i)`，对 `2^f` 在 `[0,1]` 上用 **7 阶相对误差 minimax**（`C0 = 1`），Horner 求值后把整数 `i` 直接加到指数字段（[fp32.py L175-L190](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L175-L190)）：

```python
p = C7
for c in reversed(C0..C6):     # 每个 = 一次舍入 mul + 一次舍入 add
    p = add(mul(p, f), c)
result = bits(p) + (i << 23)   # 指数字段加 i
```

八个系数是 minimax 舍入到 fp32 后、再在 fp32 空间里沿 Horner 步骤搜索出的最小误差位：`3F800000 3F317218 3E75FDE9 3D63593E 3C1D8534 3AAFE2F6 3916C07C 37B3C7D6`（[fp32.py L20-L21](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L18-L21)，RTL 同名 localparam 逐位相同）。

误差分两档测量：`f` 精确的区域（`x >= 0` 与 `x <= -0.5`）**1.26 ulp**；`-0.5 < x < 0` 时 `x+1` 先舍入、`f` 不再精确，**1.61 ulp**。每个整数点精确（`f=0`），且整体单调（`p(1)=2`，多项式在每个 fp32 `f` 上非递减）。

## recip：魔数种子 + 两次 Newton + 校正步

边界先裁：`x == 0` 给 `+0`；`|x| >= 2^126`（含无穷）返回带 `x` 符号的 0——结果本应是亚正规并冲洗。后一条还保住一个模型级不变量：很负的 `x` 上 `silu(x) = x * recip(1 + exp2(-x*log2e))` 在 `-0` 处精确（此时 exp2 溢出为 inf）。

正常路径在尾数 `a ∈ [1,2)` 上进行（[fp32.py L230-L249](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L230-L249)）：

1. 种子 `y = bits(0x7EF311C3 - bits(a))`（经典 Quake 式魔数的倒数变体）；
2. 两次 Newton：`y = y * (2 - a*y)`；
3. **校正步**：`e = 1 - a*y; y = y*e + y`（一次舍入 mul 后一次舍入 add）；
4. 指数字段加 `127 - ex`，再补 `x` 的符号。

精度 **1.16 ulp**（`[1,2)` 内每个 fp32、其余指数采样），每个 2 的幂精确。

## rsqrt：魔数种子 + 两次 Newton + 校正步 + 指数域缩放

`x <= 0`（任何符号位置位，含 `-0`）与 `x = +inf` 一律返回 `+0`。正常路径先处理指数域：指数字段 `<= 2` 时在 `16x` 上算、结果再 `*4`；字段 `250..254` 时在 `x/16` 上算、结果再 `/4`；其余不缩放。不缩放时 `h = x/2` 会在字段 1 冲洗、`y*y` 会在字段 ≥252 冲洗（NaN 或误差大到 4 倍），缩放后这些步骤恰好精确，故其余输入逐位等同未缩放路径（[fp32.py L252-L268](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L252-L268)）：

1. 种子 `y = bits(0x5F3759DF - (bits(x') >> 1))`（Fast inverse square root 魔数）；
2. `h = 0.5 * x'`，两次 Newton：`y = y * (1.5 - h*(y*y))`；
3. 校正步：`e = 0.5 - h*(y*y); y = y*e + y`；
4. 指数字段加/减 2 还原缩放。

精度 **1.03 ulp**（`[1,4)` 内每个 fp32、其余指数采样），每个 4 的幂精确。

## log2：按 sqrt(2) 分奇偶指数 + 9 系数 minimax

边界：`±0 → -inf`，`x < 0` 与 NaN → canonical NaN，`+inf → +inf`。正常路径把 `x` 拆成 `x = 2^e * m`、`m ∈ [sqrt(1/2), sqrt(2))`：以尾数位阈值 `ge = f >= 0x3504F3`（sqrt(2) 的尾数位）决定指数奇偶，重构 `m` 后令 `t = m - 1`——这一减法**精确**。随后对 `log2(1+t)/t` 的 **9 系数 minimax**（t 的 8 阶）从 `C9` Horner 到 `C1`，最后 `q*t + i2f(e)`（[fp32.py L193-L212](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L193-L212)）。系数：`3FB8AA3B BF38AA38 3EF639EB BEB8AE27 3E9369C2 BE74ADF2 3E5CE48E BE543E8E 3E00DB73`。精度 **2.3 ulp**（`[0.5,4)` 内每个 fp32、其余指数采样）。

## 修复史：文档为什么保留「曾经错在哪」

契约文档不回避失败案例，两处修复史直接钉住曾经出错的输入（也是 [F-101](/references/facts.md) 所说「修复配反例」文化的一部分）：

- **exp2 的 Taylor 系数**：早期用 `ln2^k/k!` 展开，在 `f = 1` 附近偏差高达 **13 ulp**；改用相对误差 minimax 并在 fp32 空间搜索后落到 1.26/1.61 ulp（[isa.md L91-L92](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L91-L92)）。
- **recip(1) 曾为 0.99999994**：没有 FMA 时，纯 Newton 步 `y*(2-a*y)` 的驻点比 `1/a` 恰好低约 1 ulp，`a=1` 暴露为 `recip(1) = 0.99999994`。校正步 `y*e + y`（`e = 1 - a*y`）把驻点抬回 `1/a`（[isa.md L99-L100](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L99-L100)）。rsqrt 的校正步同构。

## 固定序列：三实现逐位一致的手段

这些函数之所以能在 Python 与 RTL 间逐位相等，靠的不是「同一个数学公式」，而是**同一条含舍入点的指令序列**：每一步 `a*b + c` 都明确拆成「一次舍入 mul、再一次舍入 add」，魔数与系数按位给定，连 `t = m - 1` 精确、结果靠改指数字段这类细节都写死。于是：

- fp32.py 用 numpy fp32 逐步复现序列；
- [otpu_fp.sv](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu/otpu_fp.sv#L440-L534) 里四个函数体就是同一串 `fp_add(fp_mul(…), …)` 调用；
- VPU 把它们编成 slot 程序（[otpu_vpu.sv L11-L14](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu/otpu_vpu.sv#L11-L15)）：EXP2/EXP2SUB 9 slot（减法+范围缩减+7 个 Horner 步）、RECIP 6（两次 Newton+校正）、RSQRT 10（`h=x/2`+两次 Newton+校正）、LOG2 10（`t=m-1`+8 Horner+`i2f(e)`）。

tests/test_fp.py 在全 fp32 网格与指数采样上核 ulp 与精确点，test_fp_rtl.py 再把 RTL 与主机/模型对拍。ulp 数字是这套已执行测试的契约值，不是数学证明。

## 相关概念

- [fp32 数值契约（上）：RNE+FTZ 与零/NaN 规则](/concepts/04-fp32-contract.md)
- [VOP 向量指令：20 个功能码与 VPU](/concepts/07-vop-vpu.md)
- [事实登记表 F-001~F-123](/references/facts.md)
