---
id: "examples-index"
x-toml-ref: "../../../../../../../../.meta/toml/projects/awesome-okf-xs/doc/bundles/jishu/data/doltgresql/examples/index.toml"
okf_version: "0.2"
type: toctree
---
# 示例索引（Examples）

本目录包含 DoltgreSQL 三篇实操示例，覆盖服务器启动、pg_catalog 虚拟表查询与 plpgsql 函数编写，以源码对照形式呈现。

## 示例列表

| 序号 | 文档 | 核心内容 | 对应 F 编号 |
|------|------|---------|------------|
| 00 | [启动 DoltgreSQL 服务器](00-server-launch.md) | RunOnDisk/RunInMemory 两种模式、环境变量配置、TLS 设置、连接字符串 | F-008~F-012、F-088~F-090 |
| 01 | [pg_catalog 虚拟表查询](01-pgcatalog-queries.md) | pg_type/pg_proc/pg_class/pg_namespace/pg_sequence/pg_aggregate/pg_cast 查询示例 | F-014、F-026~F-028、F-064、F-068、F-070、F-072 |
| 02 | [plpgsql 函数编写与调用](02-plpgsql-functions.md) | CREATE FUNCTION/LANGUAGE plpgsql、条件分支/循环/异常处理/集合返回函数/触发器 | F-105~F-120 |

## 阅读路径建议

```
【部署入手】
00-server-launch（启动服务器 → 连接 → 验证）
    ↓
【元数据探索】
01-pgcatalog-queries（查询 pg_catalog 虚拟表 → 理解类型系统）
    ↓
【高级特性】
02-plpgsql-functions（编写 plpgsql 函数 → 触发器 → 集合返回函数）
```

```{toctree}
:hidden:
:maxdepth: 7

00-server-launch
01-pgcatalog-queries
02-plpgsql-functions
```
