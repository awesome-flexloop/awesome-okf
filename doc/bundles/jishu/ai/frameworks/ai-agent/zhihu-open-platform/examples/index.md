# Examples

- [01 - 从零到第一次成功调用](01-first-call-workflow.md) — 查额度（不消耗业务额度）→ 站内搜索 → 全网搜索 → 热榜 → 直答 → MCP 接入，标准库 Python 最小脚本、Claude Code/Cursor/Codex 三种 MCP 配置与 8 行排错清单
- [02 - 知识库 RAG 全链路实操](02-knowledge-rag-workflow.md) — 列库确认默认库 → multipart 同步上传 → 游标分页盘点 → 检索命中片段 → 用 `RecallContentID` 回连原文件，附可运行脚本、限流与排错
- [03 - 创作数据分析实操](03-creator-analytics-workflow.md) — 账号级统计取数与 Metrics/Audience/Followers 解读、单篇级 Date 语义与独有转粉指标、评论两段式抓取的 `NextOffset` 纪律、缺失不等于零的渲染处理
- [04 - 文档工具实战](04-document-tool-workflow.md) — PDF 解析上传—建任务—轮询—下载四步与 PPT 生成建任务—轮询—下载两步，逐字 curl 与响应 JSON、解析结果字段表、Python 脚本、幂等与额度纪律
- [05 - 额度治理实操](05-quota-governance.md) — 额度全景盘点 → 单项查询 → 调用前预检拦截 → 按任务类型分配预算，16 行价格表、9 个额度组分配建议、降级路径与 30001/30002 排错决策树

```{toctree}
:hidden:
:maxdepth: 7

01-first-call-workflow
02-knowledge-rag-workflow
03-creator-analytics-workflow
04-document-tool-workflow
05-quota-governance
```
