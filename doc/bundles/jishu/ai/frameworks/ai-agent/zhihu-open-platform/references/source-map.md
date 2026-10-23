---
type: reference
title: "官方文档页与本束页面映射表"
description: "知乎数据开放平台 31 篇官方文档与本知识包 17 个页面之间的双向映射：官方栏目与页面 key 的归属、正向与反向覆盖清单、采集方式说明，以及与既有 zhihu-cli 束的分工边界。"
tags: [zhihu, open-platform, source-map, provenance, reference]
generated: { by: "process:seven-concepts-cmd+official-docs-to-okf-wiki", at: "2026-10-23T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-23T00:00:00+08:00" }
status: stable
stale_after: 2027-04-23
sources:
  - id: zhihu-docs
    resource: https://developer.zhihu.com/docs
    title: 知乎数据开放平台官方文档（31 篇全量采集）
---

# 官方文档页与本束页面映射表

本表登记知乎数据开放平台 31 篇官方文档与本知识包 17 个页面的双向对应关系。官方文档按栏目组织，`key` 是页面唯一标识；页面代码：`00`~`09` 指 `concepts/` 下的概念页，`E01`~`E05` 指 `examples/` 下的示例页，`R1`/`R2` 指 `references/` 下的两页；代码与相对路径见文末定义。

## 官方文档页 → 本束页面

|#|官方栏目|官方页面标题|key|文档 URL|本束对应页|
|---|---|---|---|---|---|
|1|开始使用|Bearer 鉴权说明|authorization|https://developer.zhihu.com/docs?key=authorization|[01][c01]、[00][c00]|
|2|开始使用|Zhihu CLI 介绍|zhihu_cli|https://developer.zhihu.com/docs?key=zhihu_cli|[09][c09]、[01][c01]、[00][c00]|
|3|开始使用|知乎 MCP|unified_mcp|https://developer.zhihu.com/docs?key=unified_mcp|[09][c09]、[00][c00]|
|4|开始使用|额度查询 API|quota|https://developer.zhihu.com/docs?key=quota|[01][c01]、[00][c00]|
|5|开始使用|服务价格|billing_price|https://developer.zhihu.com/docs?key=billing_price|[01][c01]、[00][c00]|
|6|知乎搜索|知乎搜索 API|zhihu_search|https://developer.zhihu.com/docs?key=zhihu_search|[02][c02]|
|7|知乎搜索|知乎搜索 Skill|zhihu_search_skill|https://developer.zhihu.com/docs?key=zhihu_search_skill|[02][c02]、[09][c09]|
|8|全网搜索|全网搜索 API|global_search|https://developer.zhihu.com/docs?key=global_search|[02][c02]|
|9|全网搜索|全网搜索 Skill|global_search_skill|https://developer.zhihu.com/docs?key=global_search_skill|[02][c02]、[09][c09]|
|10|直答|直答 API|zhida|https://developer.zhihu.com/docs?key=zhida|[03][c03]|
|11|直答|直答 Skill|zhida_skill|https://developer.zhihu.com/docs?key=zhida_skill|[03][c03]、[09][c09]|
|12|热榜|知乎热榜 API|hot_list|https://developer.zhihu.com/docs?key=hot_list|[02][c02]|
|13|热榜|知乎热榜 Skill|hot_list_skill|https://developer.zhihu.com/docs?key=hot_list_skill|[02][c02]、[09][c09]|
|14|问题发现|问题推荐 API|question_recommendations|https://developer.zhihu.com/docs?key=question_recommendations|[04][c04]|
|15|问题发现|问题回答 API|question_answers|https://developer.zhihu.com/docs?key=question_answers|[04][c04]|
|16|创作能力|我的创作全文 API|user_content_detail|https://developer.zhihu.com/docs?key=user_content_detail|[05][c05]|
|17|创作能力|我的创作评论 API|user_content_comments|https://developer.zhihu.com/docs?key=user_content_comments|[05][c05]|
|18|创作能力|账号创作数据 API|creator_account_stats|https://developer.zhihu.com/docs?key=creator_account_stats|[05][c05]|
|19|创作能力|单篇创作数据 API|creator_content_stats|https://developer.zhihu.com/docs?key=creator_content_stats|[05][c05]|
|20|知识库|知识库列表 API|knowledge_bases|https://developer.zhihu.com/docs?key=knowledge_bases|[06][c06]|
|21|知识库|知识库内容列表 API|knowledge_base_items|https://developer.zhihu.com/docs?key=knowledge_base_items|[06][c06]|
|22|知识库|知识库文件上传 API|knowledge_file_upload|https://developer.zhihu.com/docs?key=knowledge_file_upload|[06][c06]|
|23|知识库|知识库检索 API|knowledge_search|https://developer.zhihu.com/docs?key=knowledge_search|[06][c06]|
|24|小工具|PDF 解析 API|pdf_parse|https://developer.zhihu.com/docs?key=pdf_parse|[07][c07]|
|25|小工具|PPT 生成 API|ppt_generation|https://developer.zhihu.com/docs?key=ppt_generation|[07][c07]|
|26|知乎用户数据|知乎 OAuth 应用集成|zhihu_oauth_integrated|https://developer.zhihu.com/docs?key=zhihu_oauth_integrated|[08][c08]|
|27|知乎用户数据|用户内容 API|user_contents|https://developer.zhihu.com/docs?key=user_contents|[08][c08]|
|28|知乎用户数据|用户关注 API|user_followees|https://developer.zhihu.com/docs?key=user_followees|[08][c08]|
|29|知乎用户数据|用户收藏 API|user_collections|https://developer.zhihu.com/docs?key=user_collections|[08][c08]|
|30|知乎用户数据|用户收藏夹列表 API|user_favlists|https://developer.zhihu.com/docs?key=user_favlists|[08][c08]|
|31|知乎用户数据|收藏夹内容 API|favlist_contents|https://developer.zhihu.com/docs?key=favlist_contents|[08][c08]|

## 本束页面 → 官方页面

|本束页面|覆盖的官方页面 key 数|覆盖清单|
|---|---|---|
|[00-platform-overview.md][c00]|5|authorization、zhihu_cli、unified_mcp、quota、billing_price|
|[01-auth-and-quota.md][c01]|4|authorization、quota、billing_price、zhihu_cli|
|[02-search-and-hotlist.md][c02]|6|zhihu_search、zhihu_search_skill、global_search、global_search_skill、hot_list、hot_list_skill|
|[03-zhida.md][c03]|2|zhida、zhida_skill|
|[04-question-discovery.md][c04]|2|question_recommendations、question_answers|
|[05-creator-capability.md][c05]|4|user_content_detail、user_content_comments、creator_account_stats、creator_content_stats|
|[06-knowledge-base.md][c06]|4|knowledge_bases、knowledge_base_items、knowledge_file_upload、knowledge_search|
|[07-document-tools.md][c07]|2|pdf_parse、ppt_generation|
|[08-user-data-oauth.md][c08]|6|zhihu_oauth_integrated、user_contents、user_followees、user_collections、user_favlists、favlist_contents|
|[09-integration-surfaces.md][c09]|6|unified_mcp、zhihu_cli、zhihu_search_skill、global_search_skill、zhida_skill、hot_list_skill|
|[01-first-call-workflow.md][e01]|7|authorization、quota、zhihu_search、global_search、hot_list、zhida、unified_mcp|
|[02-knowledge-rag-workflow.md][e02]|5|knowledge_bases、knowledge_base_items、knowledge_file_upload、knowledge_search、quota|
|[03-creator-analytics-workflow.md][e03]|5|user_content_detail、user_content_comments、creator_account_stats、creator_content_stats、quota|
|[04-document-tool-workflow.md][e04]|4|pdf_parse、ppt_generation、authorization、quota|
|[05-quota-governance.md][e05]|10|quota、billing_price、authorization、zhihu_search、global_search、hot_list、zhida、question_recommendations、knowledge_search、creator_account_stats|
|[facts.md][rf1]|31|全部 31 篇（见上表第 1 列）|
|[source-map.md][rs2]|31|全部 31 篇（见上表第 1 列）|

## 官方栏目 → 本束归属

|官方栏目|篇数|归属本束页面|归属理由（一句话）|
|---|---|---|---|
|开始使用（guide）|5|00、01、09|鉴权、额度、计费与接入面构成平台级契约|
|知乎搜索（zhihu-search）|2|02、09|站内检索规格与其 Skill 封装同属一册|
|全网搜索（global-search）|2|02、09|站外检索规格与其 Skill 封装同属一册|
|直答（zhida）|2|03、09|直答 API 契约与其 Skill 封装单列一册|
|热榜（hot-list）|2|02、09|热榜接口与其 Skill 封装并入检索能力册|
|问题发现（question-discovery）|2|04|问题推荐与回答摘要共用「问题发现」额度|
|创作能力（creator）|4|05|本人内容与创作统计四接口共用同一额度|
|知识库（knowledge-base）|4|06|四个接口串成上传、盘点与检索的 RAG 链路|
|小工具（tools）|2|07|PDF 解析与 PPT 生成共用异步任务模型与日额度|
|知乎用户数据（zhihu-user-data）|6|08|用户接口以 OAuth 凭证切换数据主体|

## 采集方式

官方文档站为前端渲染 SPA，正文由 `GET https://developer.zhihu.com/console/api/v3/docs` 返回的目录树携带，节点含 `key`/`title`/`type`/`content`/`children`；31 篇正文取自该接口的 `content` 字段，逐篇精读后登记事实，采集日期 2026-10-23。

## 官方文档栏目原始 key 清单

`guide`、`zhihu-search`、`global-search`、`zhida`、`hot-list`、`question-discovery`、`creator`、`knowledge-base`、`tools`、`zhihu-user-data`，共 10 个栏目、31 篇页面。

## 与既有 zhihu-cli 束的关系

同级目录另有 [zhihu-cli](../../zhihu-cli/index.md) 束，收录 Zhihu CLI 的 235 条事实与 55 项 P0 核验。两束并存不混写：zhihu-cli 束以 CLI 命令、MCP over SSE 架构与凭证存放为主线，本束以 31 篇官方文档全集为主线；引用 CLI 结论须写明来自哪一束，Zhihu CLI 条目以官方 `zhihu_cli` 页为唯一出处。

[c00]: ../concepts/00-platform-overview.md
[c01]: ../concepts/01-auth-and-quota.md
[c02]: ../concepts/02-search-and-hotlist.md
[c03]: ../concepts/03-zhida.md
[c04]: ../concepts/04-question-discovery.md
[c05]: ../concepts/05-creator-capability.md
[c06]: ../concepts/06-knowledge-base.md
[c07]: ../concepts/07-document-tools.md
[c08]: ../concepts/08-user-data-oauth.md
[c09]: ../concepts/09-integration-surfaces.md
[e01]: ../examples/01-first-call-workflow.md
[e02]: ../examples/02-knowledge-rag-workflow.md
[e03]: ../examples/03-creator-analytics-workflow.md
[e04]: ../examples/04-document-tool-workflow.md
[e05]: ../examples/05-quota-governance.md
[rf1]: facts.md
[rs2]: source-map.md
