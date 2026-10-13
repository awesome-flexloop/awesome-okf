# 概念地图：17 篇 openTPU 源码精读

本包对固定提交 `ffe997e9`（2026-10-12）的 openTPU monorepo 做源码级精读，17 篇按「机器 → 数值与算子 → 量化 → 软件栈 → 平台与验证」五段组织，建议按序号 00→16 顺序阅读；每篇覆盖的 F 编号可在 [事实登记表](../references/facts.md) 逐条溯源。

| # | 概念 | 核心问题 | 对应 F |
|---|------|---------|--------|
| 00 | [openTPU 是什么：一个可端到端读完的 AI 加速器 monorepo](00-project-and-six-layers.md) | 六层链路如何组成？「same bits」契约是什么？ | F-001~F-010 |
| 01 | [机器模型：slice、三层存储与顺序完成语义](01-machine-model.md) | 程序可见状态有哪些？生产配置参数是多少？ | F-011~F-017 |
| 02 | [指令系统：17 条指令、8×32-bit 字编码与寄存器约定](02-instruction-set.md) | 为什么是 17 条而不是 16 条？编码怎么布局？ | F-018~F-026 |
| 03 | [sequencer：顺序派发、WIN=16 足迹窗口与 HALT CHAIN 常驻程序](03-sequencer-and-chaining.md) | 指令怎么流动？常驻 decode 如何实现？ | F-024/F-074/F-079/F-088 |
| 04 | [fp32 数值契约（上）：RNE+FTZ、非完整 IEEE 754 与零/NaN 规则](04-fp32-contract.md) | 三端位一致的 fp32 语义边界在哪？ | F-031~F-034/F-039~F-041/F-043 |
| 05 | [fp32 数值契约（下）：exp2/log2/recip/rsqrt 的固定序列与 ulp 边界](05-elementary-functions.md) | 没有除法器怎么做倒数？误差契约是多少？ | F-035~F-038 |
| 06 | [MM 指令与四列脉动 MXU：48-bit 精确累加、epilogue 与 replay](06-mm-and-mxu.md) | 矩阵乘在硬件上如何精确累加？ | F-044~F-047/F-056/F-057 |
| 07 | [VOP 向量指令：20 个功能码、四种广播与归约/OUTER/ARGMAX](07-vop-vpu.md) | 一条向量指令如何覆盖 elementwise 到线性注意力？ | F-058~F-063 |
| 08 | [量化器：QACT/QST、行尺度 Sa/da 与 q8 公式](08-quantization-unit.md) | 量化为何是 ISA 一等公民？ | F-015/F-021/F-042/F-052/F-053 |
| 09 | [权重格式族：int8/int4/FP4/NVFP4 与 scale 行布局](09-weight-formats.md) | 4.25 bits/weight 如何实现？ | F-048/F-049/F-054/F-055 |
| 10 | [PAIR 列复用、RSC K-cache 与 DUP：4-bit 满速技巧](10-pair-rsc.md) | 4-bit 权重如何不浪费 MXU 列？ | F-047/F-050/F-051/F-053 |
| 11 | [ol 内核语言与编译器：原语、布局即 API、仿射寻址与融合](11-ol-language-compiler.md) | Python 内核如何变成 17 条指令的程序？ | F-064~F-074 |
| 12 | [STREAM/DSTEP 状态引擎、WAITW 轮询与 CAPS 能力位](12-stream-dstep-caps.md) | 状态不进 TMEM 如何做一步循环状态更新？ | F-023/F-027~F-030/F-098/F-120 |
| 13 | [主机软件栈：chat/serve、卡上批量与 MoE 专家流 offload](13-host-stack-serve-moe.md) | 大模型如何分块喂给小显存加速器？ | F-086~F-089/F-105~F-107 |
| 14 | [板卡与多 target：YPCB-00338、镜像演进、bcu1525、Lens 与 scoreboard](14-board-and-targets.md) | 同一份 RTL 如何面向 FPGA/ASIC 多目标？ | F-025/F-083~F-085/F-090/F-099/F-111~F-113/F-122/F-123 |
| 15 | [ASIC 路径：NanGate45 + OpenROAD 流程与 PPA 数字](15-asic-nangate45.md) | FPGA 设计走 ASIC 流程能得到什么？ | F-114~F-118 |
| 16 | [位精确验证体系：validate 四行表、KL 判据与 78 文件测试金字塔](16-verification-system.md) | 「same bits」如何被机械验证？ | F-091~F-101/F-108~F-110 |

> **口径提示**：性能、功耗、命中率等数字均为 openTPU 作者报告口径（正文逐处标注），本包不做第三方实测；本包为静态源码走读，未运行仿真、未构建位流、未使用板卡。

```{toctree}
:hidden:
:maxdepth: 2

00-project-and-six-layers
01-machine-model
02-instruction-set
03-sequencer-and-chaining
04-fp32-contract
05-elementary-functions
06-mm-and-mxu
07-vop-vpu
08-quantization-unit
09-weight-formats
10-pair-rsc
11-ol-language-compiler
12-stream-dstep-caps
13-host-stack-serve-moe
14-board-and-targets
15-asic-nangate45
16-verification-system
```
