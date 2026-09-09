# 示例索引（Examples）

本目录包含 `dh` CLI 的四个实操示例，覆盖认证、SQL、表导入与 PR 协作流。命令均源自 README 与命令定义，读者可直接照做。

## 示例列表

| 序号 | 文档 | 核心内容 |
|------|------|---------|
| 00 | [认证操作示例](00-authentication.md) | login/status/logout、DH_TOKEN、自定义 client ID |
| 01 | [SQL 查询示例](01-sql-queries.md) | 读查询（--ref/--file/stdin/--json）、异步写查询 |
| 02 | [表导入示例](02-table-import.md) | CSV/JSON 导入、主键、更新模式、--no-wait |
| 03 | [Pull Request 协作工作流示例](03-pr-workflow.md) | 建分支 → 写数据 → PR → 评论 → 合并 → 标签/Release |

## 阅读路径建议

```
00-authentication（先完成登录）
    ↓
01-sql-queries（会查数据）
    ↓
02-table-import（会导数据）
    ↓
03-pr-workflow（会协作）
```

```{toctree}
:hidden:
:maxdepth: 7

00-authentication
01-sql-queries
02-table-import
03-pr-workflow
```
