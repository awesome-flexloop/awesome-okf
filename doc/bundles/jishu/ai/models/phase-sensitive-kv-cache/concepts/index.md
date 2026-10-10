# 概念文档（concepts）

- [00-相位敏感性概览](00-phase-sensitivity-overview.md) — 分块 KV Cache 压缩、相位、相位敏感性的定义与全貌
- [01-代码补全与 NIAH 检索](01-code-completion-and-niah.md) — DeepSeek-V4 系列的两类实证：周期性反转的代码补全与 128K 大海捞针
- [02-机理：压缩内核与相位专门化](02-mechanism-kernel-and-specialization.md) — 从头预训练 kernel 家族、因果干预、压缩门控与梯度流理论
- [03-评估启示与边界](03-evaluation-implications.md) — 跨相位评测建议、后训练缓解、与既有评估体系的衔接

```{toctree}
:hidden:
:maxdepth: 2

00-phase-sensitivity-overview
01-code-completion-and-niah
02-mechanism-kernel-and-specialization
03-evaluation-implications
```