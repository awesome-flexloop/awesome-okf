---
okf_version: "0.2"
type: example
id: "examples-pgcatalog-queries"
title: "pg_catalog 虚拟表查询"
x-toml-ref: "../../../../../../../../.meta/toml/projects/awesome-okf-xs/doc/bundles/jishu/data/doltgresql/examples/01-pgcatalog-queries.toml"
description: "pg_type/pg_proc/pg_class/pg_namespace/pg_sequence 等核心系统表的 SQL 查询示例，展示 PostgreSQL 协议兼容性"
tags: [doltgresql, example]
generated:
  at: "2026-09-09"
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: stable
stale_after: "2027-03-09"
sources:
  - path: "server/tables/pgcatalog/pg_type.go"
    type: source-code
    title: "server/tables/pgcatalog/pg_type.go"
    distance: 1
  - path: "core/rootvalue.go"
    type: source-code
    title: "core/rootvalue.go"
    distance: 1
  - id: pgcatalog-source
    resource: /references/source.md
    title: "DoltgreSQL 源码事实登记"
---
# pg_catalog 虚拟表查询

> 本文档展示 DoltgreSQL 中 pg_catalog schema 下的核心虚拟表查询，覆盖类型、函数、类、命名空间、序列等 PostgreSQL 元数据。

---

## 示例 1：pg_type — 类型系统元数据

### 查询所有基础类型

```sql
-- 查看所有数值类型（F-027：pg_type 虚拟表含 31 列）
SELECT oid, typname, typcategory, typinput, typoutput
FROM pg_type
WHERE typcategory = 'N'  -- NumericTypes
ORDER BY typname;

-- 查看类型分类统计（F-022：16 种 TypeCategory）
SELECT typcategory, COUNT(*) AS type_count
FROM pg_type
GROUP BY typcategory
ORDER BY type_count DESC;

-- 查看数组类型（支持多维数组，NDims 追踪）
SELECT typname, typlem, typlen
FROM pg_type
WHERE typlen = -1  -- 变长类型
  AND typcategory = 'A'  -- ArrayTypes
ORDER BY typname;
```

### 源码锚点

| 查询 | 源码位置 | 说明 |
|------|---------|------|
| pg_type 虚拟表 | [server/tables/pgcatalog/pg_type.go L1](../../../../../external/dao/action/DoltHub/doltgresql/server/tables/pgcatalog/pg_type.go) | `PgTypeHandler` 实现 `tables.Handler` 接口（F-014） |
| 双索引查找 | [server/tables/pgcatalog/pg_type.go L30](../../../../../external/dao/action/DoltHub/doltgresql/server/tables/pgcatalog/pg_type.go) | `pg_type_oid_index` + `pg_type_typname_nsp_index`（F-026） |
| 缓存机制 | [server/tables/pgcatalog/pg_type.go L50](../../../../../external/dao/action/DoltHub/doltgresql/server/tables/pgcatalog/pg_type.go) | `cachePgTypes()` 首次访问时缓存全部条目（F-028） |
| TypeCategory | [server/types/type.go L50](../../../../../external/dao/action/DoltHub/doltgresql/server/types/type.go) | 16 种枚举：NumericTypes/StringTypes/BooleanTypes 等（F-022） |

### 预期输出示例

```
 oid  | typname  | typcategory | typinput          | typoutput
------+----------+-------------+-------------------+-------------------
 20   | int8     | N           | int8in            | int8out
 21   | int2     | N           | int2in            | int2out
 23   | int4     | N           | int4in            | int4out
 700   | float4   | N           | float4in          | float4out
 701   | float8   | N           | float8in          | float8out
1700   | numeric  | N           | numeric_in        | numeric_out
```

---

## 示例 2：pg_proc — 函数/过程元数据

### 查询内置函数

```sql
-- 查看所有已注册的函数（F-117：globalFunctionRegistry 全局单例）
SELECT n.nspname AS schema, p.proname AS function_name,
       pg_get_function_arguments(p.oid) AS arguments,
       t.typname AS return_type
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname IN ('pg_catalog', 'public')
ORDER BY n.nspname, p.proname;

-- 查找特定函数
SELECT proname, pg_get_function_arguments(oid), pg_get_function_result(oid)
FROM pg_proc
WHERE proname = 'sum';
```

### 源码锚点

| 查询 | 源码位置 | 说明 |
|------|---------|------|
| 函数注册表 | [server/types/function_registry.go L1](../../../../../external/dao/action/DoltHub/doltgresql/server/types/function_registry.go) | `globalFunctionRegistry` 全局单例（F-117） |
| RoutineParam | [server/node/create_function.go L10](../../../../../external/dao/action/DoltHub/doltgresql/server/node/create_function.go) | Mode/Name/Type/HasDefault/Default 五字段（F-118） |
| CreateFunction | [server/node/create_function.go L30](../../../../../external/dao/action/DoltHub/doltgresql/server/node/create_function.go) | 十个字段包括 FunctionName/ReturnType/Parameters 等（F-119） |

---

## 示例 3：pg_class — 表/视图/索引关系

### 查询用户表

```sql
-- 查看所有表（F-072：Relation 集合管理系统表关系）
SELECT c.relname AS table_name,
       c.relkind AS relation_type,  -- 'r'=table, 'v'=view, 'i'=index
       n.nspname AS schema_name
FROM pg_class c
JOIN pg_namespace n ON c.relnamespace = n.oid
WHERE n.nspname IN ('pg_catalog', 'public')
  AND c.relkind = 'r'
ORDER BY n.nspname, c.relname;

-- 查看表的列信息
SELECT c.relname AS table_name, a.attname AS column_name,
       t.typname AS data_type, a.attnotnull AS not_null
FROM pg_class c
JOIN pg_namespace n ON c.relnamespace = n.oid
JOIN pg_attribute a ON a.attrelid = c.oid
JOIN pg_type t ON a.atttypid = t.oid
WHERE n.nspname = 'public'
  AND a.attnum > 0
  AND NOT a.attisdropped
ORDER BY c.relname, a.attnum;
```

### 源码锚点

| 查询 | 源码位置 | 说明 |
|------|---------|------|
| Relation 集合 | [core/relations/collection.go L1](../../../../../external/dao/action/DoltHub/doltgresql/core/relations/collection.go) | 管理表/视图关系映射，支持 pg_class 查询（F-072） |
| pg_class 虚拟表 | [server/tables/pgcatalog/](../../../../../external/dao/action/DoltHub/doltgresql/server/tables/pgcatalog/) | 通过 Handler 接口实现为内存虚拟表（F-014） |

---

## 示例 4：pg_namespace — 命名空间

### 查询所有 schema

```sql
-- 查看所有命名空间
SELECT oid, nspname, nspowner
FROM pg_namespace
ORDER BY nspname;

-- 查看 public schema 的详情
SELECT n.oid, n.nspname, COUNT(c.relname) AS table_count
FROM pg_namespace n
LEFT JOIN pg_class c ON c.relnamespace = n.oid AND c.relkind = 'r'
GROUP BY n.oid, n.nspname
HAVING n.nspname IN ('pg_catalog', 'public');
```

---

## 示例 5：pg_sequence — 序列对象

### 查询序列

```sql
-- 查看所有序列（F-064：Sequence 含 8 个字段）
SELECT s.seqname AS sequence_name,
       pg_get_serial_sequence(s.seqname) AS associated_column,
       s.seqmin AS min_value,
       s.seqmax AS max_value,
       s.seqincrement AS increment,
       s.seqstart AS start_value,
       s.seqcache AS cache_size
FROM pg_sequence s
ORDER BY s.seqname;

-- 创建并使用序列
CREATE SEQUENCE public.emp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

SELECT nextval('public.emp_id_seq');
```

### 源码锚点

| 查询 | 源码位置 | 说明 |
|------|---------|------|
| Sequence 结构 | [core/sequences/collection.go L1](../../../../../external/dao/action/DoltHub/doltgresql/core/sequences/collection.go) | ID/Owner/CurrentValue/MinValue/MaxValue/Increment/StartedWith/Cache 八字段（F-064） |
| Sequence 集合 | [core/sequences/collection.go](../../../../../external/dao/action/DoltHub/doltgresql/core/sequences/collection.go) | 实现 Collection 接口的泛型集合（F-064） |

---

## 示例 6：pg_aggregate — 聚合函数

```sql
-- 查看所有聚合函数
SELECT aggname AS aggregate_name,
       pg_get_function_arguments(aggfnoid) AS arguments,
       pg_get_function_result(aggfnoid) AS return_type
FROM pg_aggregate a
JOIN pg_proc p ON a.aggfnoid = p.oid
ORDER BY aggname;

-- 测试聚合函数
SELECT COUNT(*) AS total_rows,
       AVG(salary) AS avg_salary,
       MAX(salary) AS max_salary,
       MIN(salary) AS min_salary
FROM employees;
```

### 源码锚点

| 查询 | 源码位置 | 说明 |
|------|---------|------|
| Aggregate 集合 | [core/aggregates/collection.go L1](../../../../../external/dao/action/DoltHub/doltgresql/core/aggregates/collection.go) | 管理聚合函数定义，含状态类型和转移函数（F-070） |

---

## 示例 7：pg_cast — 类型转换

```sql
-- 查看所有类型转换规则（F-068）
SELECT c.oid, t1.typname AS source_type, t2.typname AS target_type,
       castfunc::regproc AS function_name,
       c.castcontext AS context
FROM pg_cast c
JOIN pg_type t1 ON c.castsource = t1.oid
JOIN pg_type t2 ON c.casttarget = t2.oid
ORDER BY t1.typname, t2.typname;

-- 手动类型转换
SELECT '123'::int AS as_integer,
       42::text AS as_text,
       '3.14'::numeric AS as_numeric;
```

### 源码锚点

| 查询 | 源码位置 | 说明 |
|------|---------|------|
| Cast 集合 | [core/casts/collection.go L1](../../../../../external/dao/action/DoltHub/doltgresql/core/casts/collection.go) | 源类型→目标类型→转换函数（F-068） |
| 类型转换表达式 | [server/ast/expr.go L53](../../../../../external/dao/action/DoltHub/doltgresql/server/ast/expr.go) | `nodeTypeCast()` 转换 CAST 表达式（F-053） |

---

## pg_catalog 虚拟表全景

| 虚拟表 | 列数 | 说明 | 源码 |
|--------|------|------|------|
| `pg_type` | 31 | 类型元数据 | [pg_type.go](../../../../../external/dao/action/DoltHub/doltgresql/server/tables/pgcatalog/pg_type.go) |
| `pg_proc` | 40+ | 函数/过程元数据 | server/tables/pgcatalog/pg_proc.go |
| `pg_class` | 50+ | 表/视图/索引关系 | server/tables/pgcatalog/pg_class.go |
| `pg_namespace` | 4 | 命名空间（schema） | server/tables/pgcatalog/pg_namespace.go |
| `pg_sequence` | 8 | 序列对象 | [core/sequences/collection.go](../../../../../external/dao/action/DoltHub/doltgresql/core/sequences/collection.go) |
| `pg_aggregate` | 10+ | 聚合函数 | server/tables/pgcatalog/pg_aggregate.go |
| `pg_cast` | 6 | 类型转换规则 | [core/casts/collection.go](../../../../../external/dao/action/DoltHub/doltgresql/core/casts/collection.go) |
| `pg_operator` | 15+ | 运算符定义 | server/tables/pgcatalog/pg_operator.go |

> **注意**：所有 pg_catalog 虚拟表通过 `tables.Handler` 接口实现为内存虚拟表，不实际存储于 Dolt 表中（F-014）。`cachePgTypes()` 等缓存机制避免重复查询 RootValue（F-028）。

> **注意**：当前环境未安装 `doltgresql` 二进制，本文档以源码锚点形式呈现，供查阅实现细节。
