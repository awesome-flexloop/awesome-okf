---
id: "concepts-index"
x-toml-ref: "../../../../../../../../.meta/toml/projects/awesome-okf-xs/doc/bundles/jishu/data/doltgresql/concepts/index.toml"
okf_version: "0.2"
type: toctree
---
# 概念索引（Concepts）

本目录包含 DoltgreSQL 知识包六篇核心概念文档，按"产品定位→架构设计→类型系统→AST转换→集合管理→plpgsql执行"五层递进，覆盖从产品认知到核心机制实现的完整链路。

## 概念列表

### 第一层：产品定位与架构

| 序号 | 文档 | 核心内容 | 对应 F 编号 |
|------|------|---------|------------|
| 00 | [DoltgreSQL 概述与产品定位](00-overview.md) | 版本（1.3.0 Beta）、性能基准（5.2x 慢于原生 Postgres）、sqllogictest 91.17% 正确率、已知限制、适用场景 | F-001~F-006、F-020、F-072~F-076 |
| 01 | [三层架构与数据流](01-architecture.md) | PG 解析层（pg_query_go）→ AST 转换层（server/ast/）→ GMS 执行层（go-mysql-server）；Listener/Handler 接口；RunOnDisk/RunInMemory 两种启动模式 | F-007~F-018、F-081~F-090 |

### 第二层：核心机制

| 序号 | 文档 | 核心内容 | 对应 F 编号 |
|------|------|---------|------------|
| 02 | [RootValue 扩展与 RootObject 集合](02-rootvalue-and-collections.md) | RootValue 核心结构、11 种 root object collection（Sequences/Types/Functions/Triggers 等）、contextValues 缓存机制、差异写回流程 | F-061~F-080 |
| 03 | [AST 转换机制](03-ast-conversion.md) | pg_query_go → tree.Node → vitess.Statement 全链路；nodeExpr（979 行最复杂）/nodeSelect/nodeInsert/nodeCreateTable；表达式映射规则与未支持特性清单 | F-036~F-060 |
| 04 | [类型系统与 pg_type](04-type-system.md) | DoltgresType 100+ 字段、TypeCategory 16 种枚举大类、BaseTypeDefinition I/O 函数、数组/复合/枚举/伪类型处理、pg_type 虚拟表 31 列 | F-021~F-035 |
| 05 | [plpgsql 解释器与函数系统](05-plpgsql-and-functions.md) | OpCode 23 种操作码（控制流/数据操作/变量操作/循环/返回/异常/动态 SQL）、InterpretedFunction 接口、RoutineParam、globalFunctionRegistry | F-105~F-120 |

## 阅读路径建议

```
【入门路径】
00-overview（认识产品全貌 + 已知限制）
    ↓
01-architecture（理解三层架构与数据流）
    ↓
02-rootvalue-and-collections（掌握版本化存储的核心机制）

【深入路径】（源码阅读导向）
03-ast-conversion（AST 转换层：最复杂的 979 行 nodeExpr）
    ↓
04-type-system（类型系统：100+ 字段 + 16 种 TypeCategory）
    ↓
05-plpgsql-and-functions（plpgsql 解释器：23 种 OpCode）

【快速参考】
- 只想了解产品定位 → 00
- 想理解三层架构 → 00 → 01
- 想深入源码阅读 → 02 → 03 → 04 → 05
- 想了解 plpgsql 实现 → 05
```

## 概念依赖关系

```
00-overview
    └── 01-architecture（产品层依赖架构层）
          ├── 02-rootvalue-and-collections（架构层依赖集合管理）
          │     ├── 04-type-system（类型系统依赖集合管理）
          │     └── 03-ast-conversion（AST 转换依赖集合管理）
          │           └── 05-plpgsql-and-functions（plpgsql 依赖类型系统）
```

```{toctree}
:hidden:
:maxdepth: 7

00-overview
01-architecture
02-rootvalue-and-collections
03-ast-conversion
04-type-system
05-plpgsql-and-functions
```
