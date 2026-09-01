---
type: Concept
title: MIR 与借用检查：THIR→MIR 构建与 NLL
description: MIR 数据结构为何住在 rustc_middle、rustc_mir_build 如何从 THIR 构建 MIR、rustc_borrowck 的 NLL 与 Polonius 借用检查体系
tags: [rust, rustc, mir, borrowck]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rustc-source
    resource: /references/rustc-source-map.md
---

# MIR 与借用检查：THIR→MIR 构建与 NLL

## 数据 / 构建 / 改写：三个 crate 的分工

又一个打破直觉的坐标事实：**MIR crate 不定义 MIR**。`pub struct Body<'tcx>`、`Local`、`LocalDecl`、`BasicBlock`、`BasicBlockData` 全部定义于 rustc_middle/src/mir/mod.rs：

| 结构 | 行号 | 含义 |
|------|------|------|
| `Body<'tcx>` | L206 | 一个函数体的完整 MIR |
| `Local` | L866 | 局部变量句柄 |
| `LocalKind` | L889 | 局部变量类别 |
| `LocalDecl<'tcx>` | L967 | 局部变量声明（类型、可变性等） |
| `LocalInfo<'tcx>` | L1074 | 局部变量的补充信息 |
| `BasicBlock` | L1300 | 基本块句柄 |
| `BasicBlockData<'tcx>` | L1319 | 基本块内容（语句序列 + 终结器） |

同理，THIR（Type-checked HIR，类型检查后的高层 IR）的 `pub struct Thir<'tcx>` 定义于 rustc_middle/src/thir.rs:63——也在 rustc_middle。三个 crate 的分工是：

- **rustc_middle**：MIR/THIR 的**数据**；
- **rustc_mir_build**：THIR→MIR 的**构建**；
- **rustc_mir_transform**：MIR 上的**改写**（pass，见[下一概念文档](/concepts/07-mir-optimization-codegen.md)）。

## rustc_mir_build：从 THIR 到 MIR

rustc_mir_build/src/lib.rs 的模块：builder、check_tail_calls、check_unsafety、diagnostics 与 `pub mod thir`，外加老朋友 `pub fn provide`(L19)。builder 是构建主战场；check_tail_calls 与 check_unsafety 表明尾调用与 unsafe 语义检查嵌在构建期；`thir` 模块则提供 THIR 侧的产出。

MIR 是"控制流图 + 直面求值语义"的表示：函数体变成基本块网络，每个块是语句序列加一个终结器（跳转/返回/发散）。这种形态正是借用检查所需的数据形状。

## rustc_borrowck：借用检查本体

rustc_borrowck/src/lib.rs 的模块清单几乎是一张借用检查术语表：borrow_set、borrowck_errors、constraints、dataflow、def_use、diagnostics、handle_placeholders、implied_bounds、nll、path_utils、place_ext、places_conflict、polonius、prefixes、region_infer、renumber、root_cx、session_diagnostics、type_check、universal_regions、used_muts、consumers(pub)。

两个关键函数：`pub fn provide`(L110) 把借用检查注册进 query 系统，`fn mir_borrowck`(L117) 是主入口。

**NLL（Non-Lexical Lifetimes，非词法生命周期）** 的痕迹遍布模块表：`nll` 模块本体、`region_infer`（区域推断）、`constraints`（约束收集）、`universal_regions`（普遍区域）、`implied_bounds`（隐式边界）。NLL 的核心思想——借用何时生效取决于控制流而非词法作用域——正是由这些模块协作实现：借用检查被转化为对 MIR 控制流图上的区域约束求解。

模块表里还有一个实验分支：`polonius`——下一代借用检查器的原型实现。`places_conflict`、`prefixes`、`path_utils`、`place_ext` 则是 place（存储位置）代数，即"两个路径是否可能指向同一位置"的判定基础设施。

## rustc_mir_dataflow：数据流分析框架

借用检查的底层机械是 MIR 上的数据流分析。rustc_mir_dataflow/src/lib.rs 的 pub 模块：debuginfo、impls、move_paths、points、rustc_peek、value_analysis；私有模块：drop_flag_effects、framework、un_derefer；并定义 `pub struct MoveDataTypingEnv<'tcx>`(L36)。

`framework` 是通用的数据流分析骨架（尽管是私有模块——它只服务于本 crate），`move_paths` 与 `drop_flag_effects` 服务 drop 语义的精确追踪，`value_analysis` 支持值的抽象解释。这些是 NLL 与 drop 检查共享的地基。

## 在流水线中的位置

```text
HIR + ty 层类型信息
   │  rustc_hir_typeck（类型检查，见 HIR 篇）
   ▼
THIR（rustc_middle/src/thir.rs）
   │  rustc_mir_build（构建 + 尾调用/unsafe 检查）
   ▼
MIR（rustc_middle/src/mir/mod.rs）
   │  rustc_borrowck（NLL 借用检查）
   │  rustc_mir_dataflow（数据流分析）
   ▼
rustc_mir_transform（优化 pass 群，见下一篇）
```

## 相关概念

- [类型系统与 trait 求解](/concepts/05-type-system-trait-solving.md) — MIR 构建所需的类型信息来源
- [MIR 优化与代码生成](/concepts/07-mir-optimization-codegen.md) — 借用检查通过后的 pass 流与后端
- [rustc 基础设施](/concepts/09-rustc-infrastructure.md) — mir_borrowck 等 query 的注册与缓存机制
- [rustc 编译器信源登记](/references/rustc-source-map.md) — MIR 域各结构体的精确行号坐标
