# 示例索引：3 个贯穿式走读

三篇示例均从固定提交 `ffe997e` 的真实文件逐字摘引代码与命令，标注源码行号；不伪造运行输出，命令的预期输出给出处而非杜撰。

| # | 示例 | 走读内容 | 对应 F |
|---|------|---------|--------|
| 00 | [一次矩阵乘穿过六层（MLP swiglu_down）](00-matmul-through-six-layers.md) | 从 `kernels/mlp.py` 的 ol 调用到 MM 指令、isasim 整数累加与 MXU RTL | F-044/F-052/F-056/F-066/F-071 |
| 01 | [三种 backend 的位级对拍（validate --against）](01-bitexact-crosscheck.md) | validate.py 参数、四行对照表、top-1/KL 判据与退出码 | F-091~F-097 |
| 02 | [MoE 专家流的 WAITW + mailbox fence 协议](02-moe-mailbox-waitw.md) | mailbox.py 真实代码、WAITW 轮询语义与 offload 七步协议 | F-023/F-071/F-098/F-105 |

```{toctree}
:hidden:
:maxdepth: 2

00-matmul-through-six-layers
01-bitexact-crosscheck
02-moe-mailbox-waitw
```
