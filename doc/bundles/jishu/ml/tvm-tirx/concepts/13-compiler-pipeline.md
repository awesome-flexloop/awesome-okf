---
type: Concept
title: 编译流水线——确定性 lowering 的真实顺序
description: 基于 compilation_pipeline.py 还原 tvm-tirx 的默认 lowering：TileDispatch → LowerTensorLayouts → 化简 → FlattenTensor → NarrowDataType → 向量化 → 展开 → CSE → VerifyMemory → LowerThreadAllreduce → finalize，并说明「无搜索式调优」的准确含义
tags: [tvm-tirx, 编译流水线, lowering, pass, vectorize, cse, verify-memory, nvrtc]
generated: { by: seven-concepts-cmd/1.1.0, at: 2026-11-09T00:00:00+08:00 }
verified: { by: process:seven-concepts-v, at: 2026-11-09T00:00:00+08:00 }
status: stable
stale_after: 2027-02-09
sources:
  - id: pipeline
    resource: https://github.com/apache/tvm-tirx/blob/cdc7a37793e449917faa2dcaa66df1bb61df2ba5/python/tvm_tirx/tirx/compilation_pipeline.py
  - id: compiling-doc
    resource: https://github.com/apache/tvm-tirx/blob/cdc7a37793e449917faa2dcaa66df1bb61df2ba5/docs/programming_guides/compiling.rst
---

# 编译流水线

> 文中 `[F-xxx]` 为编号事实，来源见 [facts.md](../references/facts.md)。
> **快照**：commit `cdc7a377`（2026-11-08）[F-100]。

## 1. 先修正一句流行说法

官方博客说「`tirx.compile` 不施加额外启发式优化，直接把程序交给 LLVM」[F-022]。源码显示这句话需要更精确的表述 [F-110]：

- **没有**搜索式/代价模型式的调优（没有 auto-schedule、autotuning、layout 搜索）；
- **有**一条固定的、确定性的 lowering 流水线（dispatch、layout 降低、化简、向量化、展开、CSE、内存校验等）。

两者不矛盾：前者说「不做搜索」，后者说「做确定性降级」。把「无启发式」理解成「零 pass」会误判调试与性能行为。

## 2. 默认流水线（源码顺序）

`tvm_tirx.tirx.compilation_pipeline.tirx_pipeline()` 依次执行 [F-110]：

```text
1. bind target
2. TileDispatch
3. (可选) PrintIR  —— 环境变量 TVM_TIRX_PRINT_AFTER_DISPATCH_OPS
4. LowerTensorLayouts
5. StmtSimplify
6. FlattenTensor
7. NarrowDataType(32)
8. VectorizeLoop        —— 可由 tirx.disable_vectorize 关闭
9. UnrollLoop
10. StmtSimplify
11. CommonSubexprElim   —— 可由 tirx.disable_cse_tir 关闭
12. VerifyMemory
13. LowerThreadAllreduce
14. finalize_tir_pipeline()（host/device finalize）
```

| 阶段 | 作用（按名称与文档） | 可观测点 |
|------|----------------------|----------|
| TileDispatch | 把 tile primitive 调用降成具体指令与循环/寻址 [F-076] | `TVM_TIRX_PRINT_AFTER_DISPATCH_OPS` 打印 dispatch 后 IR |
| LowerTensorLayouts | 把 layout 声明降低为物理坐标/存储访问 [F-109] | `format_tree` / `script()` 对比前后 |
| StmtSimplify | 语句级化简 | IR 文本变化 |
| FlattenTensor | 展平张量维度 | 索引表达式变化 |
| NarrowDataType(32) | 收窄整数位宽到 32 位 | dtype 变化 |
| VectorizeLoop | 循环向量化（可关） | 生成向量指令 |
| UnrollLoop | 循环展开 | 代码体积/循环消失 |
| CommonSubexprElim | 公共子表达式消除（可关） | 重复表达式合并 |
| VerifyMemory | 内存访问校验 | 非法访问报错 |
| LowerThreadAllreduce | 线程级 allreduce 降低 | 协作指令生成 |

> 表中「作用」只写名称与文档能直接支持的含义；各 pass 的内部算法不在本次核验范围。

## 3. 编译入口与目标配置

```python
import tvm_tirx
from tvm_tirx.target import Target

target = Target({
    "kind": "cuda",
    "arch": "sm_75",
    "backend_config": {"cuda": {"nvrtc": ["--use_fast_math"]}},
})
ex = tvm_tirx.compile(add_one, target=target)
```

来源事实 [F-121]：

- `arch` 指定 GPU 架构；离线构建必须显式给；
- CUDA 默认使用 **NVRTC**；`backend_config.cuda.nvrtc` 是传给 NVRTC 的参数列表；
- `device_entry(..., backend_config={...})` 可覆盖 target 设置，且参数列表是**整体替换**而非追加；
- `ex.mod.imports[0].inspect_source("cuda")` 可查看生成的 CUDA 源码。

## 4. 检查中间程序

| 方法 | 返回 | 用途 |
|------|------|------|
| `add_one.script()` | TVMScript 文本 | 看参数类型、索引、边界检查 [F-121] |
| `add_one.show()` | 直接打印同一表示 | 快速查看 [F-121] |
| `tvm_tirx.ir.format_tree(add_one)` | 字段树 | 看 AST 结构 [F-063] |
| `ex.mod.imports[0].inspect_source("cuda")` | CUDA 源码 | 看 device code [F-121] |

## 5. 调试配方

```text
① 程序是否能打印？        script()/format_tree
② dispatch 是否选对指令？  TVM_TIRX_PRINT_AFTER_DISPATCH_OPS=1
③ layout 是否正确降低？   对比 LowerTensorLayouts 前后的 IR
④ 是否被向量化/展开？     打印最终 IR 或 inspect_source
⑤ 内存访问是否合法？      VerifyMemory 是否报错
⑥ 生成代码是否符合预期？  inspect_source("cuda")
```

## 6. 与「Agent 快速迭代」的关系

这条流水线是**固定顺序**的，因此对 Agent 友好 [F-110]：

- 同一输入得到同一 pass 序列，便于 diff；
- 关闭向量化/CSE 的开关让 Agent 可以做对照实验；
- `prepare_only=True` 可停在 finalize 前，单独检查 lowering 结果；
- dispatch 后可打印 IR，定位「哪一步改变了程序」。

代价是：它不会自动为你搜索最优调度。性能仍取决于 tile primitive 选择、layout 与后端指令——这正是上层 harness/Agent 可以发挥的空间。

## 7. 常见误解

| 误解 | 事实 |
|------|------|
| 「compile 不做任何优化」 | 有确定性 lowering（向量化、展开、CSE 等）[F-110] |
| 「compile 会自动调优」 | 没有搜索式调优；性能由程序与 dispatch 决定 [F-022] |
| 「pass 顺序无关紧要」 | 顺序固定：dispatch → layout → 化简 → 展平 → 向量化 → 展开 → CSE → 校验 [F-110] |
| 「CUDA 一定走 nvcc」 | 默认 NVRTC，可用 `backend_config` 传参 [F-121] |
