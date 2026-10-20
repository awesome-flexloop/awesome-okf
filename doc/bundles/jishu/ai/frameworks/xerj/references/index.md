# References 索引

本目录包含 XERJ 知识包的参考资料：事实清单、架构洞察、信源登记与领域背景。事实与洞察分两轮：第一轮来自源码与上游自述，第二轮来自官方文档站。

## 事实清单

事实清单基于源码与官方文档采集，每条标注来源路径与行号，零推测。**数量类事实一律由脚本计数，不采信人工枚举。**

| 文件 | 涵盖范围 | 事实数量 |
|---|---|---|
| [facts.md](facts.md) | **第一轮**（源码 + 上游自述）：定位与规模 / crate 架构 / autoindex / MCP / 检索路径 / 向量与嵌入 / 记忆与第二大脑 / 兼容性与基准 / 参考编码 / 文档漂移（F-001～F-206） | 206 |
| [facts-docs.md](facts-docs.md) | **第二轮**（官方文档站 46 页）：查询与聚合 / 分析器与摄取 / 存储压缩集群 / 配置环境安全 / 运维备份升级排障 / ES 兼容面 / 智能体表面与 Hub（F-207～F-362）+ 交叉核验记录 | 156 |

## 知识地图

| 文件 | 说明 |
|---|---|
| [insights.md](insights.md) | **第一轮**六条架构洞察（四元组：陈述/证据/反常识/行动）、事实覆盖分配与三段式学习路径 |
| [insights-docs.md](insights-docs.md) | **第二轮**六条增量洞察（洞察 7～12）：接了线但没接线 / 集群给的是选主环不是副本 / 诚实被编码进响应体 / 量化换精度不换内存 / 文档站的源码指针即可追溯性 / 诚实与漂移共存；附两轮合并的学习路径 |

## 信源登记

| 文件 | 说明 |
|---|---|
| [source.md](source.md) | **第一轮信源**：仓库身份与 commit 哈希、目录规模与各 crate 行数（脚本计数）、15 个关键文件清单、信源路径稳定性判定（G0） |
| [docs-source.md](docs-source.md) | **第二轮信源**：xerj.org/docs/ 与本地落地快照 `landing/docs/` 的对应关系、版本锚点、46 页清单、页面→本束文档对照、采信规则 |
| [background-research.md](background-research.md) | 领域定位（AI 检索栈现状、Rust 生态既有方案、许可证分档）、成本模型与研究过程 |

```{toctree}
:maxdepth: 2

background-research
docs-source
facts
facts-docs
insights
insights-docs
source
```
