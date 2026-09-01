---
type: Concept
title: rustc 基础设施：span、query 系统、元数据与名称解析
description: 编译器的四块横切地基：rustc_span 的 Span 与 Symbol、rustc_middle/rustc_query_impl 的 query 系统、rustc_metadata 的 rmeta 格式、rustc_resolve 的名称解析
tags: [rust, rustc, span, query, metadata, resolver]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rustc-source
    resource: /references/rustc-source-map.md
---

# rustc 基础设施：span、query 系统、元数据与名称解析

## rustc_span：一切坐标的地基

诊断、增量缓存、宏卫生（hygiene）都依赖"这段代码来自哪"的精确定位。rustc_span/src/lib.rs 的 pub 模块：source_map、edition、hygiene、def_id、edit_distance、symbol、fatal_error、profiling；结构体 `Spanned<T>`(L97)、`SessionGlobals`(L114)、`MetavarSpansMap`(L200)、`RealFileName`(L305)；函数 `create_session_globals_then`(L144)、`with_session_globals`(L182)。

两个核心类型的落点有点出人意料：

- `pub struct Span` 定义于 **span_encoding.rs**:82（不在 lib.rs，也不在 span.rs）——文件名暗示 Span 有紧凑的位级编码，32 位里要塞下位置、上下文与标记位；
- `pub struct Symbol(SymbolIndex)` 定义于 symbol.rs:2674——字符串的驻留（interning）句柄，文件中还引用了 `PREDEFINED_SYMBOLS_COUNT` 常量（L3054），说明存在预定义符号表（编译器高频符号走快速通道）。

`def_id` 模块是跨 crate 的身份体系（DefId），`hygiene` 是宏卫生的数据所在，`SessionGlobals` 与 `with_session_globals` 管理会话级全局状态。

## query 系统：编译器的骨架引擎

### 唯一的定义点

全仓库只有**一处** `rustc_queries! {` 宏调用：compiler/rustc_middle/src/queries.rs:141。其上方注释说明每个 query 对应 `Providers` 结构的一个函数指针字段与 `tcx: TyCtxt` 上的方法。把这段宏体当作"编译器能力总清单"来读是官方隐含的阅读法。

### 缓存策略逐 query 声明

宏体内每个 query 携带自己的缓存修饰，示例：

| query | 策略 | 描述 |
|-------|------|------|
| `derive_macro_expansion` | cache_on_disk | "expanding a derive (proc) macro" |
| `trigger_delayed_bug` | — | 延迟触发 bug（测试用） |
| `registered_attr_tools` | arena_cache | 注册的属性工具 |
| `registered_lint_tools` | — | 注册的 lint 工具 |
| `early_lint_checks` | — | "perform lints prior to AST lowering" |
| `env_var_os` | eval_always | "get the value of an environment variable" |
| `resolutions` | — | "getting the resolver outputs" |
| `resolver_for_lowering_raw` | eval_always + no_hash | lowering 用的原始解析器输出 |

`eval_always` 的语义值得咀嚼：`env_var_os` 查询环境变量，**绝不能被缓存**（否则改环境变量不生效），而"每次求值"正是它的正确形态。缓存策略不是性能装饰，而是语义声明。

### 执行层：rustc_middle/src/query/ 与 rustc_query_impl

query 目录的分工：

- **caches.rs**：`DefaultCache<K,V>`(L43)、`SingleCache<V>`(L86)、`DefIdCache<V>`(L128)——按 key 形态选择缓存结构；
- **calls.rs**：`TyCtxtAt<'tcx>`(L16)、`TyCtxtEnsureOk`(L31)、`TyCtxtEnsureResult`(L37)、`TyCtxtEnsureDone`(L43)——调用态包装（"确保已计算"族的四种语义）；
- **job.rs**：`QueryJobId`(L15)、`QueryJob<'tcx>`(L19)、`QueryState<'tcx,K>`(L76)、`QueryStackFrame<'tcx>`(L90)、`QueryCycle<'tcx>`(L102)——任务与**循环检测**（QueryCycle 即 ICE 报告里"query cycle"的真身）；
- 另有 keys.rs（`LocalCrate`(L26) 等 key 抽象）、erase.rs、on_disk_cache、query_api、modifiers、into_query_key。

rustc_query_impl 是执行引擎：src/lib.rs 的 `pub fn query_system<'tcx>`(L29) 与 `pub fn provide`(L50)（后者向 `rustc_middle::util::Providers` 注册）；私有模块 dep_kind_vtables、diagnostics、execution、handle_cycle_error、incremental、job、query_vtables、self_profile 揭示其职责：job 调度、循环错误处理、增量复用（on-disk 缓存）、自我剖析（self_profile）。

## rustc_metadata：crate 间通信格式

编译器之间的"对话语言"由 rustc_metadata 承载。其 src/lib.rs 私有模块：dependency_format、eii、foreign_modules、host_dylib、native_libs、rmeta；pub 模块：creader、diagnostics、fs、locator。

rmeta（rust metadata）格式的版本纪律写在 rmeta/mod.rs：

```rust
const METADATA_VERSION: u8 = 10;                                        // L63
pub const METADATA_HEADER: &[u8] = &[b'r', b'u', b's', b't', 0, 0, 0, METADATA_VERSION];  // L70
```

L212 的注释补上规则："If you do modify this struct, also bump the `METADATA_VERSION` constant."——元数据结构的任何改动必须升版本号，否则旧 rmeta 会被误读。

## rustc_resolve：名称解析

名称解析把标识符绑定到定义。rustc_resolve/src/lib.rs 的私有模块：build_reduced_graph、check_unused、def_collector、diagnostics、effective_visibilities、ident、imports、late、macros；pub 模块 `rustdoc`；结构体 `ModuleData<'ra>`(L678)、`Module<'ra>`(L718)、`LocalModule<'ra>`(L723)、`ExternModule<'ra>`(L728)。

模块表透露了架构：**早期/晚期两遍**（`late` 是晚期解析的主战场）、**导入处理**（imports）、**缩减图构建**（build_reduced_graph，把名字挂进模块树）、**未使用检查**（check_unused——unused import 警告的来源）。`rustdoc` 是 pub 模块的原因：rustdoc 需要借用解析器做 intra-doc 链接解析。

## 这些地基如何互相咬合

一次编译的横切视角：

1. rustc_lexer 产出 token，**rustc_span** 的 Span 附着其上（见[解析与宏展开](/concepts/03-parsing-macro-expansion.md)）；
2. **rustc_resolve** 解析名字，产出 resolutions query 的输出；
3. 每一步计算经由 **query 系统**调度、缓存、检测循环；
4. 编译本 crate 之外的依赖从 **rustc_metadata** 读取 rmeta；
5. 所有错误经由 DiagCtxt 汇报（见[诊断与错误体系](/concepts/11-diagnostics-error-system.md)）。

## 相关概念

- [编译器流水线总览](/concepts/02-compiler-pipeline-overview.md) — query 心智模型的首次引入
- [诊断与错误体系](/concepts/11-diagnostics-error-system.md) — Span 的最大消费方
- [类型系统与 trait 求解](/concepts/05-type-system-trait-solving.md) — TyCtxt 与 query 系统的交点
- [rustc 编译器信源登记](/references/rustc-source-map.md) — 基础设施各 crate 的关键坐标
