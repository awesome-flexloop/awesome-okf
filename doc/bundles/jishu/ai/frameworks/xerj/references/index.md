# References 索引

本目录包含 XERJ 知识包的参考资料：事实清单、架构洞察、信源登记与领域背景。

## 事实清单

事实清单基于 commit `51ff219276d7e55d9d85b4938e8b94f235f9d099` 的源码采集，共 **206 条**编号事实（F-001～F-206），按模块分组（A 定位与规模 / B crate 架构 / C autoindex / D MCP / E 检索路径 / F 向量与嵌入 / G 记忆与第二大脑 / H 兼容性与基准 / I 参考编码 / J 文档漂移）。每条标注仓库相对路径与行号；数量类事实由脚本计数，不采信人工枚举。

| 文件 | 涵盖范围 | 事实数量 |
|---|---|---|
| [facts.md](facts.md) | 全模块编号事实（F-001～F-206） | 206 |

## 知识地图

| 文件 | 说明 |
|---|---|
| [insights.md](insights.md) | 六条架构洞察（四元组：陈述/证据/反常识/行动）、事实覆盖分配与三段式学习路径 |

## 信源登记

| 文件 | 说明 |
|---|---|
| [source.md](source.md) | 仓库身份与 commit 哈希、目录规模与各 crate 行数（脚本计数）、15 个关键文件清单、信源路径稳定性判定（G0） |
| [background-research.md](background-research.md) | 领域定位（AI 检索栈拼装现状、Rust 生态既有方案、许可证分档）、成本模型、研究过程与信源引用清单 |

```{toctree}
:maxdepth: 2

background-research
facts
insights
source
```
