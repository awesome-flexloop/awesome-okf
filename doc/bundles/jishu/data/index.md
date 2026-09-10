---
okf_version: "0.2"
type: group
title: "📊 数据科学与科学计算生态"
description: "Python 数据科学生态核心库——数值计算、数据分析、可视化、Web 应用与数据存储"
---

# 📊 数据科学与科学计算生态

本域存放 Python 数据科学生态的核心知识包，以 PyData 组织为代表，覆盖科学计算基础、数据分析、可视化、Web 数据应用与高性能数据存储的完整技术栈。

## 域内分组导航

| 分组 | 一句话简介 |
|------|-----------|
| [📊 PyData 科学计算生态](pydata/index.md) | Python 科学计算与数据科学生态——NumPy/pandas/matplotlib/Plotly/Dash/PyTables |
| [🗄️ Dolt 版本化数据库](dolt/index.md) | Dolt——Git 式版本控制的 SQL 数据库：行级历史、分支/合并、MCP Server、MySQL 兼容 |
| [⌨️ dh DoltHub CLI](dolthub-cli/index.md) | dh——DoltHub 官方命令行接口：OAuth 认证、SQL 查询、表导入、分支/标签/Release、PR 协作 |
| [🤖 Dolt MCP Server](dolt-mcp/index.md) | dolt-mcp——把版本化 SQL 数据库交给 AI 的 MCP Server：三方言（Dolt/DoltgreSQL/DoltLite）、45 工具与安全注解、读写通道分离 |
| [🐘 DoltgreSQL PostgreSQL 兼容数据库](doltgresql/index.md) | DoltgreSQL——基于 Go 的 PostgreSQL 协议兼容版本化数据库：AST 转换层 + RootValue 扩展 + plpgsql 解释器；1.3.0 Beta，sqllogictest 91.17% |
| [🔗 DoltHub SQL 引擎栈](dolthub-stack/index.md) | DoltHub 三层 SQL 引擎栈：vitess SQL 解析器 → go-mysql-server 执行引擎 → doltlite-android 移动端绑定；85 条源码事实，4 个概念，3 个示例 |
| [🚗 Dolt Go Driver](driver/index.md) | dolthub/driver——内嵌 Dolt 的 Go database/sql/driver 实现：5 层接口、BackOff 重试、多语句 RuneStack 解析、24h 指标上报 |
| [🍃 DumbodB MongoDB Wire 兼容层](dumbodb/index.md) | dolthub/dumbodb——MongoDB 8.0 wire 协议兼容数据库：Backend/Database/Collection 三层接口、rootish 编码系统、BSON 编解码、VersioningBackend 40+方法 |
| [🐍 doltlite-python SQLite 版本控制 Loader](doltlite-python/index.md) | dolthub/doltlite-python——运行时符号劫持将 libdoltlite 注入 Python sqlite3 符号链：RTLD_GLOBAL/LD_PRELOAD/DYLD_INSERT_LIBRARIES、py3-none wheel、lockstep 版本管理；22 条源码事实，5 条洞察 |

```{toctree}
:hidden:
:maxdepth: 7

pydata/index
dolt/index
dolthub-cli/index
dolt-mcp/index
doltgresql/index
dolthub-stack/index
driver/index
dumbodb/index
doltlite-python/index
```
