# 示例索引（Examples）

本目录收录 dolt-mcp 的实操示例——以 MCP `tools/call` 请求形态演示如何用 dolt-mcp 让 AI 安全操作版本化数据库。

## 骨架判定说明

- **一问**（有读者可照做的安装/配置/调用流程？）：是——README 与源码提供完整 CLI/JSON 调用范式（F-160）。
- **二问**（经实测、有版本/输入输出/步骤顺序？）：官方集成测试（integration_tests）提供真实工具调用 JSON、seed 数据与断言（F-150~F-156）。
- **结论**：设 examples/。所有示例严格取材源码工具参数表与集成测试事实，不虚构输出。

## 示例列表

| 序号 | 文档 | 核心内容 |
|------|------|---------|
| 00 | [query 与 exec：读/写双通道调用实操](00-query-and-exec.md) | query 只读 SELECT 与 exec 写入的 tools/call 请求、三方言 SQL 差异、错误场景对照 |
| 01 | [AI 驱动的分支-提交-合并版本控制工作流](01-branch-commit-merge-workflow.md) | 从建分支到合并回 main 的完整版本控制工具链演练 |

```{toctree}
:hidden:
:maxdepth: 2

00-query-and-exec
01-branch-commit-merge-workflow
```
