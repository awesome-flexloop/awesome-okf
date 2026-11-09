---
type: Concept
title: 示例索引：从跑通到扩展
description: tvm-tirx 知识包示例层导航——quickstart、结构特化、扩展骨架三个实操文档的目标与前置条件
tags: [tvm-tirx, 示例, 索引, quickstart]
generated: { by: seven-concepts-cmd/1.1.0, at: 2026-11-09T00:00:00+08:00 }
verified: { by: process:seven-concepts-v, at: 2026-11-09T00:00:00+08:00 }
status: stable
stale_after: 2027-02-09
sources:
  - id: tvm-tirx-docs
    resource: https://tvm.apache.org/tirx/get_started/quick_start.html
---

# 示例索引

| 示例 | 目标 | 前置 | 预计产出 |
|------|------|------|----------|
| [quickstart-add-one](quickstart-add-one.md) | 跑通 CPU/CUDA 编译、调用、导出与 C++ 加载 | Python 3.10+、PyTorch；CUDA 版需 CUDA 13+ | 一个可调用的 `Executable` 与 `.so` |
| [structural-specialization](structural-specialization.md) | 用结构遍历把动态维度特化为常量 | 完成 quickstart | 特化后的新 IR 树 |
| [extension-skeleton](extension-skeleton.md) | 理解扩展包的最小结构 | 读完 [04-dynamic-extension](../concepts/04-dynamic-extension.md) | Python/Rust 扩展骨架 |
| [layout-mapping](layout-mapping.md) | 手算 layout：元素 57 落到哪些 warp/lane/reg | 读完 [09-layout-and-dispatch](../concepts/09-layout-and-dispatch.md) | 可运行的纯 Python 映射脚本 |

> 示例代码以官方文档为基准；API 处于 beta，实际运行请以所装版本的文档为准 [F-005]。

```{toctree}
:hidden:
:maxdepth: 7

quickstart-add-one
structural-specialization
extension-skeleton
layout-mapping
```
