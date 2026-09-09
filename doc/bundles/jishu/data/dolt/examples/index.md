# 示例索引（Examples）

本目录包含 Dolt 分层全景教程四篇实操示例，以源码对照形式呈现（当前环境未安装 `dolt`，每条命令附带源码文件锚点）。

## 示例列表

| 序号 | 文档 | 覆盖层级 | 核心内容 | 对应 F 编号 |
|------|------|---------|---------|------------|
| 00 | [CLI 核心工作流](00-cli-workflow.md) | CLI 命令层 | init/sql server/分支+提交/合并冲突/历史差异/远程操作/MCP 工具映射 | F-086~F-111 |
| 01 | [SQL 版本控制](01-sql-version-control.md) | SQL 版本控制层 | dprocedures/dfunctions/dtablefunctions 调用/历史表查询/系统表/事务控制 | F-112~F-153 |
| 02 | [分支合并工作流](02-branch-merge-workflow.md) | CLI + SQL 交叉 | 完整分支开发流程/三种冲突类型详解/回退操作 | F-112~F-156 |
| 03 | [系统表与测试](03-system-tables-and-testing.md) | 生态与工作流层 | dolt_status/log/diff 系统表/Schema 查询/Benchmark/导入导出/GraphQL | F-157~F-192 |

## 阅读路径建议

```
【按工作流学习】
00-cli-workflow（从零开始：init → sql server → 分支 → 提交 → 合并 → 远程）
    ↓
02-branch-merge-workflow（深入：完整分支开发 + 冲突处理 + 回退）
    ↓
01-sql-version-control（SQL 层：存储过程/函数/表函数 + 历史查询）
    ↓
03-system-tables-and-testing（系统表全景 + 测试基础设施）
```

```{toctree}
:hidden:
:maxdepth: 7

00-cli-workflow
01-sql-version-control
02-branch-merge-workflow
03-system-tables-and-testing
```
