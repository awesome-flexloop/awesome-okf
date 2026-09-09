# 实战示例

ScholarClaw 调用演练，共 2 篇：覆盖唯一的异步长任务（博客生成三步法）与核心的学术搜索完整调用流程。

* [博客生成三步法调用时序](blog-three-step-pipeline.md) — 为 ArXiv 论文生成博客：分步调用（提交→轮询→取结果）与 `blog.sh` 同步封装两种方式的完整命令序列与响应解读。
* [一次学术搜索的完整调用](scholar-search-walkthrough.md) — 调研"多模态学习"：查询分析（`--analyze-only`）、带参数搜索、上下文追问的命令序列与 `QueryAnalysis`/`ScholarSearchResponse` 响应结构解读。

```{toctree}
:hidden:
:maxdepth: 7

blog-three-step-pipeline
scholar-search-walkthrough
```
