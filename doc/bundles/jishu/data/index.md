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

```{toctree}
:hidden:
:maxdepth: 7

pydata/index
dolt/index
dolthub-cli/index
dolt-mcp/index
doltgresql/index
```
