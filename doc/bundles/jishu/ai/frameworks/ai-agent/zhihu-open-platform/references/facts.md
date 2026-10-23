---
type: reference
title: "事实登记 F-001~F-120"
description: "知乎数据开放平台官方文档的编号事实底账：120 条事实逐条标注来源页面 key、事实陈述与原文依据位置，覆盖接口路径、参数边界、响应字段、错误码、额度与计费口径、接入方式与安全纪律。"
tags: [zhihu, open-platform, facts, provenance, reference]
generated: { by: "process:seven-concepts-cmd+official-docs-to-okf-wiki", at: "2026-10-23T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-23T00:00:00+08:00" }
status: stable
stale_after: 2027-04-23
sources:
  - id: zhihu-docs
    resource: https://developer.zhihu.com/docs
    title: 知乎数据开放平台官方文档（31 篇全量采集）
---

# 事实登记 F-001~F-120

31 篇官方文档的编号事实底账，F-001~F-120 连续无缺号，每条标注来源 key 与原文依据位置。key 对应 `https://developer.zhihu.com/docs?key=<key>`；表中路径省略域名（开发者平台 `https://developer.zhihu.com`，OAuth `https://openapi.zhihu.com`）。官方未给出的信息列于文末「文档缺口登记」，不计入本表。

## 事实表

| 编号 | 事实陈述 | 来源 key | 依据位置 |
|------|---------|---------|---------|
|F-001|`Authorization: Bearer <your_access_secret>`；服务端校验 `X-Request-Timestamp`|authorization|请求头|
|F-002|`X-Request-Timestamp` 为秒级 Unix 时间戳；`Content-Type` 固定 `application/json`|authorization|请求头|
|F-003|Access Secret 在 `https://developer.zhihu.com/profile` 获取，作 Bearer Token 使用|authorization|Secret|
|F-004|`GET /api/v1/quota` 查询额度，该查询不消耗业务额度|quota|请求|
|F-005|`Authorization` 与 `X-Request-Timestamp` 必填；时间戳与服务端时间相差不超过 10 分钟|quota|请求头|
|F-006|`APIIDs` 选填 String，多个 API ID 以逗号分隔，只能出现一次|quota|参数表|
|F-007|不传 `APIIDs` 时返回已配置的可展示额度，未接入配置的 API 被省略|quota|说明|
|F-008|可查询 9 个 API ID：`global_search`、`zhihu_search`、`hot_list`、`question_discovery`、`zhida_openai`、`tools`、`knowledge`、`user_data`、`creator`|quota|额度表|
|F-009|响应含 `APIID`、`APIName`、`TotalQuota`、`TotalUsed`、`RemainingQuota`（Int64）|quota|响应表|
|F-010|按成功调用次数计费，含税价以「元／千次」展示，不足千次按实际次数计|billing_price|说明 1|
|F-011|鉴权失败、参数错误、触发限流等未成功的请求不计费；流式服务输出有效内容后计一次|billing_price|说明 2|
|F-012|免费额度用完后依次从体验余额、充值余额支付，单次调用不拆分两种余额|billing_price|说明 3|
|F-013|用 OAuth 授权查询其他用户数据时，费用归属发起调用的开发者账号|billing_price|说明 4|
|F-014|每日免费额度按北京时间 00:00 重置且不结转；部分服务共用额度组，多个 Access Secret 共用额度|billing_price|免费额度|
|F-015|单价：全网搜索 12、知乎搜索 20、知乎热榜 10、直答 Agent 20、问题回答 20（元／千次）|billing_price|价格表|
|F-016|`GET /api/v1/content/zhihu_search`；`Query` 必填且不能为空|zhihu_search|接口|
|F-017|`Count` 默认 10、最大 10；`Count <= 0` 回退为 10，`Count > 10` 截断为 10|zhihu_search|参数表|
|F-018|`SortBy` 格式 `字段:方向:(最小值,最大值)`，字段可选 `CommentCount`、`VoteUpCount`，方向 `asc`/`desc`，裸字段默认降序|zhihu_search|参数表|
|F-019|`SortBy` 区间含两端边界，空端表示不限，边界为非负 int64 整数，最小值不得大于最大值|zhihu_search|说明|
|F-020|`Data` 含 `HasMore`（固定 `false`）、`SearchHashId`、`Items`、`EmptyReason`；Item 共 15 项，含 `Title`、`ContentType`、`Url`|zhihu_search|响应表|
|F-021|错误码 `0` 成功、`10001` 参数错误、`20001` 鉴权失败、`30001` 频率限制、`90001` 内部错误|zhihu_search|错误码|
|F-022|下载 `https://developer.zhihu.com/download/zhihu_search_skills.zip`；`query` 必填，`count` 默认 10、范围 1-10|zhihu_search_skill|下载/参数|
|F-023|响应含 `Code`、`Message`、`Data.HasMore`、`Data.SearchHashId`、`Data.EmptyReason`、`Data.Items`|zhihu_search_skill|响应表|
|F-024|`GET /api/v1/content/global_search`；`Query` 必填，`Count` 默认 10 最大 20|global_search|接口|
|F-025|`SearchDB` 默认 `all`，取 `all`（全部索引库）、`realtime`（仅实时库）、`static`（仅静态库）|global_search|SearchDB|
|F-026|`Filter` 支持 `host`（站点域名，String）与 `publish_time`（发布时间，秒级时间戳，Int64）|global_search|字段表|
|F-027|`host` 支持 `==`、`!=`，字符串值须用双引号，`host=="zhihu.com"` 及其子域名不受支持|global_search|操作符|
|F-028|`publish_time` 支持 `==`、`!=`、`>`、`>=`、`<`、`<=`，数字值不带引号；`AND`、`OR` 须大写且 `AND` 优先级更高|global_search|操作符|
|F-029|`POST /v1/chat/completions`；正式支持的请求字段仅 `model`、`messages`、`stream`|zhida|接口说明|
|F-030|`model` 必填，取 `zhida-fast-1p5`、`zhida-thinking-1p5`、`zhida-agent`；`stream` 默认 `false`|zhida|参数表|
|F-031|`messages` 为 Array[Message]，每项含必填 `role`、`content`|zhida|Message|
|F-032|`stream=false` 响应类型 `application/json`，`stream=true` 为 `text/event-stream`|zhida|接口|
|F-033|非流式响应含 `id`、`object`、`created`、`model`、`choices`，`choices[].message` 含 `reasoning_content`、`content`|zhida|响应示例|
|F-034|流式以 `data: {...}` 推送、`data: [DONE]` 结束，`choices[].delta` 含 `role`、`reasoning_content`、`content`|zhida|流式示例|
|F-035|`model` 缺失返回 `missing_required_parameter`；仅 `zhida-fast-1p5`、`zhida-thinking-1p5` 支持 role、content 传参|zhida|注意事项|
|F-036|下载 `https://developer.zhihu.com/download/zhida_skills.zip`；`query` 必填，`model` 默认 `zhida-fast-1p5`|zhida_skill|下载/参数|
|F-037|`stream` 默认 `false`；`output` 非流式用 `json`，流式可用 `sse` 或 `text`，`output=sse` 结束事件为 `data: [DONE]`|zhida_skill|参数/流式|
|F-038|响应含 `id`、`object`、`created`（Int64）、`model`、`choices`；`output=text` 输出回答正文|zhida_skill|响应表|
|F-039|`GET /api/v1/content/hot_list`；`Limit` 默认 30 最大 30，超出范围回退为 30|hot_list|接口|
|F-040|`Data` 含 `Total`（Int64）与 `Items`，Item 含 `Title`、`Url`、`ThumbnailUrl`、`Summary`|hot_list|响应表|
|F-041|`ThumbnailUrl` 与 `Summary` 始终返回、无数据时值为 `""`；当前仅返回问题与文章两类热榜内容|hot_list|说明|
|F-042|错误码 `0` 成功、`20001` 鉴权失败、`30001` 频率限制、`90001` 内部错误|hot_list|错误码|
|F-043|下载 `https://developer.zhihu.com/download/hot_list_skills.zip`；`limit` 默认 30、范围 1-30|hot_list_skill|下载/参数|
|F-044|响应含 `Code`、`Message`、`Data.Total`（Int64）、`Data.Items` 及 `Title`、`Url`、`ThumbnailUrl`、`Summary`|hot_list_skill|响应表|
|F-045|下载 `https://developer.zhihu.com/download/global_search_skills.zip`；`query` 必填、`count` 默认 10 范围 1-20|global_search_skill|下载/参数|
|F-046|`filter` 为高级筛选表达式；`search_db` 可选 `all`、`realtime`、`static`，默认 `all`|global_search_skill|参数表|
|F-047|响应字段与全网搜索 API 的 `Items` 一致，含 `AuthorityLevel`、`EditTime`（Int64）；失败时返回错误信息并以非零状态结束|global_search_skill|响应表|
|F-048|Zhihu CLI 是开放平台面向 AI Agent 的官方命令行工具，能力一览共 13 项|zhihu_cli|首段/能力表|
|F-049|Skill 包地址 `https://developer-cdn.zhihu.com/zhihu-cli/releases/stable/skill/zhihu-cli-skill.zip`|zhihu_cli|使用 1|
|F-050|凭证由 Agent 经标准输入交给 CLI，存入 macOS Keychain、Windows Credential Manager 或 Linux Secret Service，不写入 Skill 文件夹|zhihu_cli|使用 2|
|F-051|验证阶段检查安装状态、版本兼容性、凭证有效性并发起一次最小内容请求，内容为空不影响验证|zhihu_cli|使用 3|
|F-052|CLI 不接受 OAuth Token、用户 ID 或其他代查参数，只查 Access Secret 所属账号|zhihu_cli|边界 1|
|F-053|更新不会静默执行，更新服务不接收 Access Secret、查询内容或个人数据|zhihu_cli|边界 4|
|F-054|知乎 MCP 服务地址 `https://developer.zhihu.com/api/mcp/v1`，支持 Codex、WorkBuddy、Claude Code、Cursor|unified_mcp|准备工作|
|F-055|Codex 配置写入 `~/.codex/config.toml`（Windows `%USERPROFILE%\.codex\config.toml`），节名 `[mcp_servers.zhihu]`|unified_mcp|Codex|
|F-056|WorkBuddy 用 `mcpServers.zhihu` 且 `type` 为 `streamableHttp`；Cursor 配置为 `~/.cursor/mcp.json`|unified_mcp|WB+Cursor|
|F-057|Claude Code 命令 `claude mcp add --transport http --scope user --header "Authorization: Bearer your_access_secret" zhihu`|unified_mcp|Claude 1|
|F-058|MCP 暴露工具 `zhihu_search`、`global_search`、`hot_list`、`zhida`|unified_mcp|示例表|
|F-059|`GET /api/v1/user/question_recommendations`；`Query` 选填，去除首尾空白后不能为空|question_recommendations|请求|
|F-060|`Count` 默认 5、范围 1-20；`?Count=5` 为画像推荐，`?Query=人工智能&Count=5` 为主题推荐，`?Query=` 返回 `10001`|question_recommendations|参数/说明|
|F-061|`Data.Items` 每项仅含 `Title` 与 `Url`；条目可能不足 `Count` 或为空，不支持分页|question_recommendations|响应表|
|F-062|与问题回答共用「问题发现」额度，默认每租户每自然日 100 次，低额度用户 10 次；错误码含 `30002`、`30003`|question_recommendations|末段/错误码|
|F-063|`GET /api/v1/content/question_answers`；`QuestionUrl` 必填（完整知乎问题 URL）|question_answers|请求|
|F-064|`Offset` 默认 0 不能为负，`Limit` 默认 20、范围 1-50|question_answers|参数表|
|F-065|`Data.Items[]` 含 `ContentType`（固定 `answer`）、`ContentToken`、`Url`、`Summary`；`Summary` 不额外生成 AI 摘要|question_answers|响应表|
|F-066|分页字段 `Paging.IsEnd`、`Paging.NextOffset`、`Paging.Totals`；无效或无摘要的回答被过滤，`Totals` 可能含被过滤项|question_answers|分页说明|
|F-067|`GET /api/v1/user/content_detail`；`ContentUrl` 必填，取当前用户创作的回答、文章、想法或视频链接|user_content_detail|接口|
|F-068|`Data` 含 `ContentType`（`answer`/`article`/`pin`/`zvideo`）、`ContentToken`、`Url`、`Title`、`Body`|user_content_detail|响应表|
|F-069|支持 `/answer/{id}`、`/question/{id}/answer/{id}`、`/p/{id}`、`/pin/{id}`、`/zvideo/{id}`；视频仅返回关联正文|user_content_detail|响应段|
|F-070|仅支持当前 Access Secret 所属账号，不接受 OAuth 身份切换；与本人评论、账号统计、单篇统计共用「创作能力」额度，每租户每自然日 200 次|user_content_detail|额度段|
|F-071|`GET /api/v1/user/content_comments`；`ContentUrl` 必填，`Offset` 默认 0，`Limit` 默认 20、范围 1-50|user_content_comments|接口|
|F-072|`Order` 取 `score`（按热度）、`reverse`（时间倒序）、`ascending`（时间正序），默认 `score`|user_content_comments|参数表|
|F-073|`Data.Items[]` 含根评论 `Comment` 与 `Children[]`，两级共用 `ID`、`ReplyID`、`RootID`、`CreatedAt`、`Content`、`LikeCount`|user_content_comments|响应表|
|F-074|`Children` 仅为上游附带的子评论，不保证完整；`Paging.IsEnd` 为 Bool，`Totals` 与 `NextOffset` 为可选 Int64|user_content_comments|响应段|
|F-075|`GET /api/v1/user/creator_account_stats`；`ContentType` 取 `all`/`answer`/`article`/`pin`/`zvideo` 默认 `all`|creator_account_stats|接口|
|F-076|`StartDate`、`EndDate` 格式 `YYYY-MM-DD`，须成对提供且 `EndDate` 不得早于 `StartDate`|creator_account_stats|参数表|
|F-077|`Data` 含 `ContentType`、`Metrics`、`Audience`、`CreationCounts`、`Followers`、`FollowerDetails`|creator_account_stats|响应表|
|F-078|`CreationCounts` 含 `Answer`、`Article`、`Video`、`Follower` 四个 Int64；`Audience` 含 `Status`、`Reason` 与 `Source`、`Gender`、`Age` 等数组|creator_account_stats|字段表|
|F-079|`GET /api/v1/user/creator_content_stats`；`ContentUrl` 必填，`StartDate`、`EndDate` 格式 `YYYY-MM-DD` 成对提供|creator_content_stats|接口|
|F-080|`Data.Items[]` 含 `ContentType`（`answer`/`article`/`pin`/`zvideo`）、`ContentToken`、`Url`、`Title`、`Metrics`|creator_content_stats|响应表|
|F-081|`Metrics` 含 `Date`、`ViewCount`、`UpvoteCount`、`ClickRate`、`PageShowUV`、`NewFollowerCount` 等字段|creator_content_stats|Metrics 表|
|F-082|`GET /api/v1/knowledge/bases`，API ID `knowledge_bases`；`Scope` 取 `all`/`created`/`subscribed` 默认 `all`|knowledge_bases|接口|
|F-083|`Data.Items` 每项含 `KnowledgeBaseID`、`Name`、`Relation`、`IsDefault`、`Visibility`、`UpdatedAt`|knowledge_bases|字段表|
|F-084|`Relation` 取 `created`、`subscribed` 或 `both`；`Visibility` 取 `private` 或 `public`|knowledge_bases|字段表|
|F-085|`GET /api/v1/knowledge/bases/{KnowledgeBaseID}/items`（API ID `knowledge_base_items`）；`KnowledgeBaseID` 必填|knowledge_base_items|接口|
|F-086|Query `Cursor` 为上一页返回的不透明游标，调用方不解析不修改；`Limit` 默认 20、范围 1..20|knowledge_base_items|参数表|
|F-087|`Data` 含 `Items`、`Total`（Int64）、`HasMore`（Boolean）、`NextCursor`；以 `HasMore` 判断是否继续分页|knowledge_base_items|Data 表|
|F-088|`KnowledgeItem` 含 `RecallContentID`、`ContentType`（`unknown`/`file`/`answer`/`article`）、`Title`、`Abstract`|knowledge_base_items|字段表|
|F-089|`POST /api/v1/knowledge/files`，API ID `knowledge_file_upload`，Content-Type `multipart/form-data`|knowledge_file_upload|接口|
|F-090|Form `File` 必填且内容不能为空，单文件最大 `100 MB`；`KnowledgeBaseID` 选填，不传时用默认知识库|knowledge_file_upload|表单|
|F-091|扩展名支持 `pdf, md, txt, ppt, pptx, xlsx, xls, docx, doc, webp, png, jpg, mobi, epub, csv, azw3`，忽略大小写|knowledge_file_upload|扩展名|
|F-092|文件名须为合法 UTF-8 且不含 NUL、换行或控制字符，清理后不超过 255 个 UTF-8 字节|knowledge_file_upload|文件名|
|F-093|该接口为同步接口，取消请求不代表上传解析同步取消，不要对超时或未知结果自动重试；错误码含 `40005`、`40006`|knowledge_file_upload|表下说明|
|F-094|`POST /api/v1/knowledge/search`，API ID `knowledge_search`，Content-Type `application/json`；Body `Query` 必填|knowledge_search|接口|
|F-095|`KnowledgeBaseIDs` 与 `RecallScopes` 条件必填、默认 `[]`，至少一个非空；取 `personal`/`subscription`/`public`|knowledge_search|Body|
|F-096|`Limit` 默认 10、范围 1..10，按文档结果数而非片段数计算；`Data.Items[]` 含 `Content`、`DocName`、`OriginUrl`|knowledge_search|Body|
|F-097|上传接口 `POST /resources/v1/files`，Content-Type `multipart/form-data`，Form `file` 必填、仅支持 PDF、最大 100MB|pdf_parse|上传接口|
|F-098|上传后的文件需在 24 小时内用于创建任务；上传不消耗小工具免费额度，另有按租户计算的日请求限流，普通用户默认 10 次|pdf_parse|上传说明|
|F-099|`POST /api/v1/pdf-parse/tasks`，Body `file_id` 必填；支持 `Idempotency-Key`，同键同参数重复调用返回同一 `task_id`|pdf_parse|创建段|
|F-100|幂等重放时响应 Header 含 `Idempotent-Replayed: true`；查询 `GET /api/v1/pdf-parse/tasks/{task_id}` 返回 `task_id`、`task_status`、`result`、`error`|pdf_parse|响应/查询|
|F-101|`task_status` 取 `pending`、`running`、`succeeded`、`failed`；`result` 含 `url`、`expires_at_ms` 毫秒；`error` 含 `code`|pdf_parse|结果表|
|F-102|`POST /api/v1/ppt-generation/tasks`，Body `resource_url` 与 `num_pages`（Int32，范围 6 到 21）均必填|ppt_generation|接口|
|F-103|`resource_url` 支持 `https://www.zhihu.com/question/{question_id}/answer/{answer_id}`、`https://www.zhihu.com/answer/{answer_id}`、`https://zhuanlan.zhihu.com/p/{article_id}`|ppt_generation|参数表|
|F-104|查询 `GET /api/v1/ppt-generation/tasks/{task_id}` 返回 `task_id`、`task_status`、`result`、`error`；`result` 含 `url`|ppt_generation|查询段|
|F-105|PPT 生成与 PDF 解析共用小工具日额度，普通用户每天 10 次、低额度用户每天 2 次，任务成功时计入 1 次|ppt_generation|表下说明|
|F-106|错误码含 `10001` 参数错误、`20001` 鉴权失败、`30001` 频率限制、`30002` 额度不足、`40001` 幂等键冲突、`40003` 活跃任务数超限、`90001` 内部错误|ppt_generation|错误码表|
|F-107|申请 `app_id` 与 `app_key`，邮箱 `openplatform@zhihu.com`；材料含应用名称、图标、回调 `redirect_uri`、申请人信息与用户权限（A.邮箱 B.手机 C.公开内容）|zhihu_oauth_integrated|前置准备|
|F-108|采用标准 OAuth 2.0 Authorization Code Flow；授权页 `https://openapi.zhihu.com/authorize?redirect_uri={redirect_uri}&app_id={app_id}&response_type=code`|zhihu_oauth_integrated|授权流程|
|F-109|换 Token 接口 `POST https://openapi.zhihu.com/access_token`；参数 `app_id`、`app_key`、`grant_type`（固定 `authorization_code`）、`redirect_uri`、`code` 均必填|zhihu_oauth_integrated|接口|
|F-110|响应字段 `access_token`、`token_type`（如 `Bearer`）、`expires_in`（long，单位秒），示例 `3600`；交换与使用在应用后端完成|zhihu_oauth_integrated|响应表|
|F-111|`GET /api/v1/user/contents`；Header 含可选 `X-OAuth-Token`，不传查本人、传入查该凭证对应用户|user_contents|接口|
|F-112|`ContentType` 必填取 `all`/`answer`/`article`/`zvideo`/`pin`/`question`；`Offset` 默认 0；`Limit` 默认 20 最大 50|user_contents|参数表|
|F-113|`SortField` 取 `like_count`、`ts` 默认 `ts`；`SortOrder` 取 `asc`、`desc` 默认 `desc`；`Paging` 含 `IsEnd`|user_contents|参数表|
|F-114|错误码 `0`、`10001` 参数错误、`20001` 鉴权失败、`30001` 频率限制、`30002` 配额限制、`90001` 内部错误|user_contents|错误码|
|F-115|`GET /api/v1/user/followees`；Header 含可选 `X-OAuth-Token`；`Offset` 默认 0，`Limit` 默认 20 最大 50|user_followees|接口|
|F-116|`Data.Items[]` 含 `Fullname`、`UrlToken`、`Url`、`Headline`、`Gender`（Int16：`0` 未知或保密 / `1` 女性 / `2` 男性）|user_followees|字段表|
|F-117|`GET /api/v1/user/collections`，取公开范围内的近期收藏内容；`Limit` 默认 20|user_collections|接口说明|
|F-118|`Data.Items[]` 为 `CollectionContentItem`，`ContentType` 为小写枚举 `answer`/`article`/`zvideo`/`pin`/`question`；`Favlists` 元素含 `UrlToken`、`Title`，`Author` 含 `Name`、`UrlToken`、`Url`|user_collections|字段表|
|F-119|`GET /api/v1/user/favlists` 取收藏夹列表；`Limit` 默认 20；`Data.Items[]` 为 `FavlistItem`，含 `UrlToken`、`Url`、`Title`|user_favlists|字段表|
|F-120|`GET /api/v1/user/favlist_contents` 取夹内内容；`FavlistUrlToken` 必填、`Offset` 默认 0、`Limit` 默认 20；`Paging` 含 `IsEnd`、`NextOffset`、`Totals`|favlist_contents|分页表|

## 文档缺口登记

以下信息在官方文档中明确未给出，不计入 F-001~F-120。

| 缺口项 | 涉及接口 | 官方口径 |
|---------|---------|---------|
| 各接口具体超时时间 | 全部接口 | 仅给出 `30001` 与 10 分钟时间戳窗口，未标注超时秒数 |
| 接口级 QPS 数值 | 全部接口 | 以 `30001` 与自然日额度描述限流，未给出每秒请求数上限 |
| `Limit` 上限 | `user_collections`、`user_favlists`、`favlist_contents` | 只给出默认值 20，未给出最大值 |
| 翻页入参 | `global_search` | 响应仅含 `HasMore`，未提供 `Offset`/`Cursor` 等翻页参数 |
| 具体错误码 | 四份 Skill 页 | 仅说明失败时返回错误信息并以非零状态结束，未给出错误码表 |
| `created` 字段单位 | `zhida`、`zhida_skill` | 示例为 `1740470400`、`1753632000`，字段说明未标注单位 |
| `zhida-agent` 上下文传参 | `zhida` | 注意事项仅列出 `zhida-fast-1p5`、`zhida-thinking-1p5` 支持 role、content 传参 |
| 价格表与 `APIID` 映射 | `billing_price`、`quota` | 价格表按中文服务名列示，额度表按 API ID 列示，未给出对应关系 |
| 「获取用户信息」接口规格 | `zhihu_oauth_integrated` | 授权流程提及接口名称，未给出请求方式、URL 与响应字段 |
| `expires_in` 之外的信息 | `zhihu_oauth_integrated` | 响应仅含 `access_token`、`token_type`、`expires_in`，未提及刷新与撤销方式 |
| 检索片段数上限 | `knowledge_search` | 说明 `Limit` 按文档结果数计算，未给出单个文档 `Content` 的片段数上限 |

## 采集与时效

| 项目 | 值 |
|------|-----|
| 采集来源 URL | `https://developer.zhihu.com/docs` |
| 采集日期 | 2026-10-23 |
| 采集方式 | SPA 前端渲染，正文由 `GET /console/api/v3/docs` 返回的目录树携带（节点含 `key`/`title`/`type`/`content`/`children`） |
| 文档总数 | 31 篇，正文逐字精读 |
| 状态 | `stable` |
| `stale_after` | 2027-04-23 |
