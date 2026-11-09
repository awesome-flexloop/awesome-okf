---
type: Example
title: 扩展骨架：自定义类型、算子与 Pass 的最小结构
description: 按官方扩展指南梳理 tvm-tirx 扩展包的最小工程结构：Python 快速验证与 Rust 正式实现两条路径，以及类型/算子/Pass 的注册位置
tags: [tvm-tirx, 扩展, 插件, rust, python, pass, 类型注册]
generated: { by: seven-concepts-cmd/1.1.0, at: 2026-11-09T00:00:00+08:00 }
verified: { by: process:seven-concepts-v, at: 2026-11-09T00:00:00+08:00 }
status: stable
stale_after: 2027-02-09
sources:
  - id: tvm-tirx-docs
    resource: https://tvm.apache.org/tirx/advanced/defining_ir_extensions.html
  - id: tvm-tirx-docs-rust
    resource: https://tvm.apache.org/tirx/advanced/extending_ir_in_rust.html
---

# 扩展骨架

> 文中 `[F-xxx]` 为编号事实，来源见 [facts.md](../references/facts.md)。本示例基于官方扩展指南整理 [F-027]。

## 1. 目标与路径选择

目标：给 TIRx 增加一个**复数类型**、四个**算子**、一个把它们 lower 成标量算术的 **Pass**。

官方给了两条路径 [F-027]：

| 路径 | 适用阶段 | 优点 | 代价 |
|------|----------|------|------|
| Python 包 | 先验证想法 | 无需构建，改完即跑 | 大程序上较慢 |
| Rust 包 | 正式实现 | 快、内存安全 | 需要构建工具链 |

两者可以安装**同名同 API 的包**（示例中都是 `my_ext`），因此上层程序无需改动。

## 2. 目录结构

```text
my_ext/
├── pyproject.toml
├── python/
│   └── my_ext/
│       └── __init__.py        # Python 实现：类型/算子/Pass
├── rust/
│   └── src/
│       └── lib.rs             # Rust 实现：同样的类型/算子/Pass
└── examples/
    └── run_example.py         # 使用方
```

官方仓库的示例位于 `examples/extension_guides/`，Python 版本可以直接安装运行 [F-027]：

```bash
uv pip install --no-deps ./examples/extension_guides/python
python examples/extension_guides/run_example.py
```

## 3. 定义类型

Python 侧（官方文档片段）[F-027]：

```python
import tvm_ffi
from tvm_tirx import ir
from tvm_ffi import py_class

@py_class("my_ext.ComplexType")
class ComplexType(ir.Type):
    """实部与虚部共享同一标量类型的复数。"""
    dtype: ir.PrimType

tvm_ffi.get_global_func("ir.expose_type")("my_ext.ComplexType")
```

Rust 侧（官方文档片段的结构）[F-027]：

```rust
#[rs_object(type_key = "my_ext.ComplexType", final, immutable)]
pub struct ComplexTypeObj {
    base_: TypeObj,
    pub dtype: PrimType,
}

#[derive(Clone, tvm_ffi::derive::ObjectRef)]
#[object_ref(parent = Type)]
pub struct ComplexType {
    data_: tvm_ffi::ObjectArc<ComplexTypeObj>,
}
```

关键约定：

- `type_key` 必须以扩展命名空间开头（如 `my_ext.`），避免与核心或其他扩展冲突；
- 对象不可变（`immutable`），引用类型与对象类型分离；
- `#[object_ref(parent = Type)]` 让 `ComplexType` 能隐式转换为 `Type`，供类型推断返回。

## 4. 定义算子

算子有两种挂载形态 [F-014]：

| 形态 | 用途 | 示例 |
|------|------|------|
| `Call` | 类似 intrinsic 的调用 | `my_ext.complex_add(a, b)` |
| `RegionStmt` | 带额外语义的词法区域 | kernel launch、流水线区域 |

实现步骤（概念层面）：

1. 注册算子名与签名；
2. 定义类型推断规则（输入 `ComplexType` → 输出 `ComplexType`）；
3. 定义 lower 规则（把 `complex_add` 分解为实部/虚部的标量加减）。

> 具体注册 API 随版本演进，请以官方扩展指南为准 [F-027]。

## 5. 定义 Pass

Pass 的职责是把扩展类型/算子 lower 成核心已有的标量算术：

```text
my_ext.complex_add(a, b)
  ↓ LowerComplex Pass
prim.Add(a.re, b.re), prim.Add(a.im, b.im)
```

一个合格的扩展 Pass 应满足：

- **幂等**：对已 lower 的程序再次运行不产生变化；
- **局部**：只处理自己认识的节点，遇到未知节点保持原样；
- **可组合**：不假设自己一定是流水线中的第一个或最后一个。

## 6. 使用与验证

```python
# 安装扩展后
import my_ext
from tvm_tirx.script import tirx as T

@T.function
def kernel(a: T.Tensor((128,), my_ext.ComplexType), b: T.Tensor((128,), my_ext.ComplexType)):
    ...
```

验证清单：

- [ ] 类型能被 `format_tree` 正确显示；
- [ ] 算子能通过 TVMScript 打印并重新解析；
- [ ] Pass 前后数值等价（用标量实现做对拍）；
- [ ] 与核心节点混用时，`structural_map` 等工具仍可用；
- [ ] 扩展包在干净环境可独立安装（不依赖本地路径）。

## 7. 常见坑

| 坑 | 表现 | 规避 |
|----|------|------|
| 命名冲突 | 与核心或其他扩展同名 | 统一 `my_ext.` 前缀 |
| 只实现 Python | Rust/C++ 侧不可用 | 需要跨语言时同步实现或明确边界 |
| 忘记类型推断 | 编译到一半报类型错误 | 为每个算子写类型规则 |
| Pass 不幂等 | 多次运行结果漂移 | 处理前先判断是否已 lower |
| 直接依赖内部结构 | 核心小改即断 | 只用公开的结构化 API |

## 8. 延伸阅读

- 动态扩展的设计动因：[04-dynamic-extension](../concepts/04-dynamic-extension.md)
- 跨语言 ABI：[03-tvm-ffi-cross-language](../concepts/03-tvm-ffi-cross-language.md)
- 官方完整示例：文档站 *Extending TIRx: everything is a plugin* 与 *Getting Started with Rust Extensions* [F-027]
