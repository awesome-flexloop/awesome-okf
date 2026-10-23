# Concepts

- [00 - 平台全景：能力地图与文档导航](00-platform-overview.md) — 10 大产品域与 31 篇文档的对应关系、三种接入方式的分工、9 个额度组的归属、16 项服务价格概览
- [01 - 鉴权、额度与计费](01-auth-and-quota.md) — Bearer + 秒级 `X-Request-Timestamp` 双头校验与 10 分钟窗口、`GET /api/v1/quota` 响应字段、按成功调用计费与每日重置不结转、排错决策表
- [02 - 搜索与热榜](02-search-and-hotlist.md) — `zhihu_search` 三段式 SortBy 与 10 条上限、`global_search` Filter 表达式与 20 条上限、`hot_list` 静默回退、API↔Skill 参数名映射
- [03 - 直答 zhida](03-zhida.md) — 三档模型能力差异、仅三字段生效的白名单、SSE 帧与 `: keep-alive` 心跳、`finish_reason=error` 识别
- [04 - 问题发现](04-question-discovery.md) — 问题推荐与问题回答两接口、`Query` 省略与空串的语义分叉、回答摘要的三重否定表述、五条翻页铁律
- [05 - 创作能力](05-creator-capability.md) — 本人身份约束与已发布边界、账号级 19 项 vs 单篇级 25 项 Metrics、缺失字段不补零的阅读铁律
- [06 - 直答知识库](06-knowledge-base.md) — 列表/内容列表/上传/检索四接口、16 种扩展名、同步上传不可重试、Cursor 分页与两侧命名体例并存
- [07 - 小工具](07-document-tools.md) — PDF 解析三步与 PPT 生成两步、`task_status` 状态机、`Idempotency-Key` 幂等语义、`expires_at_ms` 毫秒时间戳
- [08 - 用户数据与 OAuth](08-user-data-oauth.md) — OAuth 授权码四步换令牌、`X-OAuth-Token` 切换数据主体、5 个 user 接口、收藏夹两段式调用链与同名 UrlToken 类型冲突
- [09 - 接入面](09-integration-surfaces.md) — 统一 MCP 服务四客户端配置、5 组官方 Skill 包、Zhihu CLI 凭证语义、5 条官方安全边界

```{toctree}
:hidden:
:maxdepth: 7

00-platform-overview
01-auth-and-quota
02-search-and-hotlist
03-zhida
04-question-discovery
05-creator-capability
06-knowledge-base
07-document-tools
08-user-data-oauth
09-integration-surfaces
```
