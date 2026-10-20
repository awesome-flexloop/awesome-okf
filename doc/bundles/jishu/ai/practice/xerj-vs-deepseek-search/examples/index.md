# Examples 索引

本目录是 XERJ × DeepSeek Search/Fetch 对比知识包的实战示例。

| 示例 | 覆盖内容 |
|---|---|
| [01 组合检索回路实战](01-composed-retrieval-pipeline.md) | 一个同时含「内部日志」与「公网最新文档」的任务，如何走「本地优先 → 公网兜底 → 固化回本地」的组合回路；两侧的具体请求（`_passage` 裁剪的本地 `_search`、带搜索语法的 Search、只对选中 URL 的 Fetch、`autoindex` 固化）、成本账、失败处理速查表 |

```{toctree}
:maxdepth: 2

01-composed-retrieval-pipeline
```
