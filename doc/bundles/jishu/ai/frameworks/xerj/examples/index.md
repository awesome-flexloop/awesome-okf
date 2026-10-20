# Examples 索引

本目录是 XERJ 知识包的实战示例，按真实任务组织。

| 示例 | 覆盖内容 |
|---|---|
| [01 从一个文件夹到可查询索引](01-autoindex-to-query.md) | 端到端实操：起节点（数据目录别放在待索引树内）→ `--dry-run` 估计 → 决策门 `--approve` → 索引 → `autoindex map` 摸清数据 → 带 `_passage` 裁剪的查询 → 结构化聚合 → `xerj init` 交给智能体；附复盘清单 |
| [02 把智能体接到 XERJ 上](02-mcp-integration.md) | MCP 配置块、绝对路径陷阱、认证三层优先级与回环回退、`max_tokens` 硬预算、五个检索工具的调用形状、无 shell 时的纯 HTTP 路径、故障速查表 |
| [03 选择检索模式](03-retrieval-mode-selection.md) | 决策表：词法/语义/向量/混合各适合什么；混合的覆盖范围陷阱与历史教训；响应裁剪；三臂评测方法（客观判据、先验证测试、top-3 而非 top-1、报中位数）；`rerank` 红线 |
| [04 从 Elasticsearch 迁移的评估路径](04-migration-from-elasticsearch.md) | 三个零成本对照实验（含把 autoindex 指向真实 ES）、兼容面与 scroll 边界、记分卡与 4 处败因、迁移要自担的运维清单、并行—观测—收敛的推荐路径、评估清单 |

```{toctree}
:maxdepth: 2

01-autoindex-to-query
02-mcp-integration
03-retrieval-mode-selection
04-migration-from-elasticsearch
```
