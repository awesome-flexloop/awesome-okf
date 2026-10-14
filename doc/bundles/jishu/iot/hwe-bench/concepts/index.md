# 概念地图：17 篇 HWE Bench 源码精读

本包对固定提交 `4a137bb`（2026-10-05）的 auto-arch-tournament（品牌名 HWE Bench）做源码级精读，17 篇按「循环与隔离 → 验证器四门 → 测量与接受 → 核与进化史 → 基准与 harness」五段组织，建议按序号 00→16 顺序阅读；每篇覆盖的 F 编号可在 [事实登记表](../references/facts.md) 逐条溯源，勘误见该表 K-1~K-6 台账。

| # | 概念 | 核心问题 | 对应 F |
|---|------|---------|--------|
| 00 | [HWE Bench 是什么：指向 RISC-V CPU 的自主研究循环](00-position-and-loop.md) | 七门短路循环长什么样？为什么说"the verifier"才是工件？ | F-001~F-010 |
| 01 | [假设即数据：JSON Schema、五类 hypothesis 与 ID 账本](01-hypothesis-schema.md) | 想法如何在写代码前先被机器校验？ | F-023~F-028/F-099/F-102 |
| 02 | [一轮编排：N 槽锦标赛、四个角色与门的短路顺序](02-round-orchestration.md) | K 个槽如何并行、收束、挑冠军？ | F-011~F-014/F-018/F-028~F-033 |
| 03 | [隔离与信任边界：git worktree、路径白名单与契约指纹](03-worktree-sandbox.md) | agent 为什么软化解题器的路在评测前就被堵死？ | F-021/F-022/F-035~F-044 |
| 04 | [RVFI NRET=2 契约：双通道退休顺序与不可焊死规则](04-rvfi-nret-contract.md) | 双发射退休迹如何排序？为什么要防 tie-dead？ | F-045/F-046/F-066/F-052 |
| 05 | [riscv-formal 分层：ALTOPS 替身、检查数三口径与空过分类](05-formal-altops.md) | 快速 formal 证明了什么、不证明什么？ | F-047~F-057/F-123 |
| 06 | [cosim 对拍：Verilator C++ 仿真器与 Python RV32IM ISS](06-cosim-iss.md) | 22% 反压下全 trace 对拍如何拦错？ | F-058~F-066 |
| 07 | [FPGA 门：3-seed 中位数、fitness 公式与反常量折叠夹具](07-fpga-fitness.md) | fitness 怎么算？夹具如何防综合器作弊？ | F-067~F-079 |
| 08 | [CoreMark 评测口径：canonical 2K、IPC 量纲与 holdout 五程序](08-coremark-measurement.md) | 2e-06 与 2.2264 为什么是同一个数？ | F-063/F-064/F-083~F-087 |
| 09 | [接受规则：严格大于、三结果类与搜索的单调形状](09-accept-rule-outcomes.md) | 门全过的 −73% 候选为什么必须丢弃？ | F-015/F-082/F-103~F-105 |
| 10 | [baseline CPU 走读：5 级按序 RV32IM 种子核与 bench 冻结夹具](10-baseline-cpu.md) | 起点核长什么样？301/283 两个基线如何区分？ | F-092~F-098 |
| 11 | [v1 进化史：9 个真胜场、63 次拒绝与 −73% 警戒线](11-v1-evolution.md) | 9h51m 里搜索轨迹如何单调爬坡？ | F-097~F-106 |
| 12 | [经验积累：append-only LESSONS.md、scribe 角色与 lessons 消融](12-scribe-lessons.md) | 经验文件到底贡献了多少？ | F-030/F-034/F-122 |
| 13 | [V1 基准方法学：预注册 15×3、成本门限与参照核政策](13-v1-bench-methodology.md) | 45 候选/rep 的实验如何锁口径？ | F-019/F-020/F-080~F-083/F-088~F-091 |
| 14 | [V1 排行榜：16 模型、失败模式谱与两个对照的崩溃](14-v1-leaderboard.md) | 983.2 与 282.8 之间差了什么？ | F-107~F-116 |
| 15 | [V2 演进：6×6 几何均值、holdout 主榜与三门正确性缺口](15-v2-holdout.md) | V2 为什么与 V1 不可比？ | F-117~F-125 |
| 16 | [自治 harness 可靠性工程：故障方向、误删事故与遥测重建](16-harness-reliability.md) | 为什么"假失败"是可以接受的失败？ | F-126/F-034/F-116/F-075 |

> **口径提示**：Fmax、iter/s、费用、tokens、时间等数字均为 HWE Bench 作者报告口径（正文逐处标注），本包不做第三方实测；本包为静态源码走读，未运行 EDA、仿真、形式求解或位流构建。V1 与 V2 数字按 [K-1](../references/facts.md) 裁决**不可直接比较**。

```{toctree}
:hidden:
:maxdepth: 2

00-position-and-loop
01-hypothesis-schema
02-round-orchestration
03-worktree-sandbox
04-rvfi-nret-contract
05-formal-altops
06-cosim-iss
07-fpga-fitness
08-coremark-measurement
09-accept-rule-outcomes
10-baseline-cpu
11-v1-evolution
12-scribe-lessons
13-v1-bench-methodology
14-v1-leaderboard
15-v2-holdout
16-harness-reliability
```
