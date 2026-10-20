# 更新日志

## 2026-10-20

**新增**：XERJ 源码学习知识包首次入库（`jishu/ai/frameworks/xerj/`）。

- **信源**：仓库 `xerj-org/xerj`，commit `51ff219276d7e55d9d85b4938e8b94f235f9d099`（`git describe` = `v1.0.0-rc.97-38-g51ff2192`），采集时工作树无未提交改动。规模与各 crate 行数由脚本计数，路径稳定性判定见 `references/source.md`。
- **事实**：206 条编号事实（F-001～F-206），分 10 组（定位与规模 / crate 架构 / autoindex / MCP / 检索路径 / 向量与嵌入 / 记忆与第二大脑 / 兼容性与基准 / 参考编码 / 文档漂移），每条标注仓库相对路径与行号。
- **洞察**：6 条四元组洞察（ES 兼容是传输层 / `semantic` 是名字不是能力 / 机器可读面比人读面更新 / autoindex 是独立客户端 / 内容驱动识别 + 字段来源标记 / 参考编码受记忆门控），见 `references/insights.md`。
- **概念文档 9 篇**：`00-overview`、`01-getting-started`、`02-autoindex-pipeline`、`03-mcp-agent-surface`、`04-search-query-path`、`05-vector-and-hybrid`、`06-agent-memory-and-brain`、`07-es-compat-and-benchmarks`、`08-reference-coding`。
- **示例 4 篇**：`01-autoindex-to-query`、`02-mcp-integration`、`03-retrieval-mode-selection`、`04-migration-from-elasticsearch`。
- **登记的事实漂移**（已记入事实清单 J 组）：仓库 `AGENTS.md` 与 `README.md` 写「13 个 MCP 工具」，代码与已发布 schema 实际为 17 个；`README.md` 写「8 个检测器」，注册表实际 9 个；`docs/WHY_XERJ.md` 写「13 个格式族」，代码侧为 25 个抽取器模块 / 28 个 `Family` 变体。
- **索引变更**：`jishu/ai/frameworks/index.md` 新增本束行与 toctree 条目；`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md` 的递归束数与分组计数同步更新。
