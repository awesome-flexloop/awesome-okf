---
type: Example
title: "照做：OAuth 授权并调用 Open API"
description: "从准备工作起，走完 /authorize 引导授权、回调取 code、/token 换取 access_token 与 refresh_token、携带 Bearer 调用个人资料 API（云侧）与本地助理 API（PC 端本机）、刷新凭证、按返回码处理错误，并说明云端任务 / ACP / 会话产物形态；两处官方口径并列（签名填充 PSS 对 PKCS#1、凭证有效期 24h 对 expires_in: 3600）。"
tags: [WorkBuddy, 开放平台, Open API, OAuth2.1, access_token, refresh_token, 本地助理, 云端任务, ACP, 返回码, 口径并列, 接入示例, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-16" }
verified: { by: "process:seven-concepts-v", at: "2026-10-16" }
status: stable
stale_after: "2027-04-16"
sources:
  - { id: D9, resource: "https://open.workbuddy.cn/docs/third-party-app" }
  - { id: D10, resource: "https://open.workbuddy.cn/docs/openapi" }
---

# 照做：OAuth 授权并调用 Open API

> 适用场景：你已在开放平台创建一个第三方应用（硬件应用或 Buddy 应用），要让用户在 WorkBuddy 侧完成授权、第三方取得接口调用凭证（`access_token`）后调用 Open API（F-357、F-358）。本篇按官方「Open API 接口」页（D10）的叙述顺序，把「准备 → `/authorize` → 回调取码 → `/token` 换证 → 携带凭证调用 → 刷新 → 错误处理 → 云端 / ACP 场景」串成一条可照做的路径。机制与参数详解见[Open API 认证授权与返回码约定](../concepts/07-openapi-auth-and-conventions.md)与[Open API 接口目录与形态边界](../concepts/08-openapi-endpoint-catalog.md)；两处口径并列见[核验报告](../references/verification.md)。
>
> 信源纪律：本篇**未在本机实跑**任何授权跳转、换票、刷新或接口调用；未注册账号、未申请认证与资质、未调用任何真实接口。文档未写明处一律标「**官方未给**」。

## 前置条件

- **应用与凭证**：已注册开发者账号，并拥有一个已创建的第三方应用（如硬件应用或 Buddy 应用），获得相应的 `clientId` 与 `clientSecret`（F-357）。
- **回调与授权集合已配置**：`redirect_uri` 必须落在该应用配置的「OAuth 回调地址」集合内；`scope` 必须在「授权列表」集合内，不传则为应用的完整「授权列表」（F-361）。
- **密钥存放纪律**：`client_secret` 属应用密钥，**严禁在前端或客户端代码中暴露**，换取与刷新均须在服务端完成（F-365、F-369）。
- **端别认知**：本地助理 API 属 **PC 端本机**能力（与已连接 WorkBuddy 的 PC 端本地助理交互，F-377）；云端任务 / ACP 通道 / 会话产物属**云侧**（F-389、F-401、F-415）。
- **本机未实跑声明**：本机未发起任何授权跳转、未收到任何真实 `code`、未换取或刷新任何真实令牌。

## 操作步骤

> 以下每一步**未在本机实跑，依据官方文档（F-xxx）**；本束未注册账号、未调用任何真实接口。

1. **引导用户授权（`/authorize`）**：引导用户在浏览器中访问「第三方应用授权页」，携带 `response_type=code`、`client_id`、`redirect_uri`、`scope`、`state`；用户确认后该页重定向至 `redirect_uri` 并通过 `code` 参数返回授权码（F-359、F-360、F-361）。〔**未在本机实跑，依据官方文档 F-359、F-360、F-361**〕
2. **接收回调取授权码**：平台重定向 `redirect_uri` 并携带 `code` 与 `state`；`code` 一次性使用、有效期 10 分钟，应用须校验 `state` 与本地保存值一致以防范 CSRF（F-362、F-363）。〔**未在本机实跑，依据官方文档 F-362、F-363**〕
3. **`/token` 换取凭证**：`POST https://www.workbuddy.cn/openapi/v2/token`，`Content-Type: application/x-www-form-urlencoded`，请求体携带 `grant_type=authorization_code`、`code`、`client_id`、`client_secret`、`redirect_uri`（后者须与获取授权码阶段**字节级完全一致**），换取 `access_token` 与 `refresh_token`（F-364、F-365、F-366、F-367）。〔**未在本机实跑，依据官方文档 F-364、F-365、F-366、F-367**〕
4. **携带 Bearer 调用个人资料 API（云侧）**：`GET https://www.workbuddy.cn/openapi/v2/user/profile`，权限要求 `user.profile.readable`，用于获取用户的昵称和头像（F-372、F-373）。〔**未在本机实跑，依据官方文档 F-372、F-373**〕
5. **携带 Bearer 调用本地助理 API（PC 端本机）**：查询 PC 端本地助理在线状态、发送消息、查询消息历史（F-377、F-378、F-380、F-381、F-384、F-385、F-386）。〔**未在本机实跑，依据官方文档 F-377、F-378、F-380、F-381、F-384、F-386**〕
6. **刷新凭证**：`refresh_token` 过期后用 `POST https://www.workbuddy.cn/openapi/v2/token` 携带 `grant_type=refresh_token` 换取新令牌；刷新响应体字段与换取响应体一致（F-368、F-369、F-370）。〔**未在本机实跑，依据官方文档 F-368、F-369、F-370**〕
7. **按返回码规范处理错误**：所有 Open API 遵循统一的返回码规范，按 HTTP 状态码 + 业务码 + 排查建议定位问题（F-438、F-439）。〔**未在本机实跑，依据官方文档 F-438、F-439**〕
8. **云端任务 / ACP / 会话产物场景（云侧）**：创建云端任务拿 `link` 与 `token`，经 ACP 通道（SSE + JSON-RPC 2.0）与云端会话通信；产物经 SSE 增量推送或 REST 全量拉取（F-389、F-390、F-401、F-402、F-412、F-423）。〔**未在本机实跑，依据官方文档 F-389、F-390、F-401、F-402、F-412、F-423**〕

### 第 1 步示例：请求用户授权（逐字照抄）

请求示例（F-360）：

```
GET /openapi/v2/authorize?response_type=code&client_id=CLIENT_ID&redirect_uri=REDIRECT_URI&scope=SCOPE&state=STATE
HOST: https://www.workbuddy.cn
Accept: text/html
```

「第三方应用授权页」参数（逐字照抄，来源 F-361）：

| 名称 | 类型 | 必填 | 示例值 | 描述 |
| --- | --- | --- | --- | --- |
| response_type | String | 是 | code | 固定值 code，表示授权码模式 |
| client_id | String | 是 | app_7a3f2b... | 应用注册后获得的应用 ID |
| redirect_uri | String | 是 | https://example.com/callback | 回调重定向地址，需要在「硬件接入」或「Buddy 应用」中配置的「OAuth 回调地址」集合内 |
| scope | String | 否 | user.task.readable user.task.invokable | 用户权限范围，多个「scope」以空格分隔。必须在「硬件接入」或「Buddy 应用」中配置的「授权列表」集合内，不传则为应用的完整「授权列表」 |
| state | String | 建议 | a1b2c3_random_xyz | 随机字符串，用于防 CSRF 攻击和回调状态保持。回调时原样返回 |

### 第 2 步示例：回调响应（逐字照抄）

回调参数 2 项 `code`、`state`（F-362）；回调示例 `GET https://example.com/callback?code=auth_c0d3_xyz789&state=a1b2c3_random_xyz`（F-363）。

### 第 3 步示例：换取凭证（逐字照抄）

请求体（来源 F-365）：

| 名称 | 类型 | 必填 | 示例值 | 描述 |
| --- | --- | --- | --- | --- |
| grant_type | String | 是 | authorization_code | 固定值 authorization_code |
| code | String | 是 | auth_c0d3_xyz789 | 上一步获取的授权码，一次性使用 |
| client_id | String | 是 | cb_7a3f2b1c | 应用 ID |
| client_secret | String | 是 | sk_live_abc123... | 应用密钥，严禁在前端或客户端代码中暴露 |
| redirect_uri | String | 是 | https://example.com/callback | 必须与 /authorize 获取授权码阶段回调地址参数完全一致（字节级） |

响应示例（F-367）：

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "scope": "user.profile.readable user.task.readable",
  "open_id": "op_9f8e7d6c5b4a"
}
```

响应体 6 字段：`access_token`（访问令牌）、`token_type`（固定值 `Bearer`）、`expires_in`（Number，示例 `3600`，access_token 有效期，**单位秒**）、`refresh_token`（仅在 `authorization_code` 模式下返回）、`scope`、`open_id`（F-366）。

### 第 4 步示例：个人资料 API（**端别：云侧**）

`GET https://www.workbuddy.cn/openapi/v2/user/profile`，权限要求 `user.profile.readable`（F-372）。请求报文与响应报文（逐字照抄，F-372、F-373）：

```
GET /openapi/v2/user/profile HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer <access_token>
Accept: application/json
```

```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Cache-Control: private, no-store

{
"nickname": "张三",
"avatar": "https://example.com/avatar.png"
}
```

响应 `data` 字段（F-373）：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| nickname | String | 当前用户的昵称 |
| avatar | String | 当前用户的头像 |

### 第 5 步示例：本地助理 API（**端别：PC 端本机**）

本地助理 API 用于与**已连接 WorkBuddy 的 PC 端本地助理**进行消息交互（F-377）；响应为**统一包裹结构** `{"code":0,"msg":"success","request_id":"a1b2c3d4e5","data":{...}}`（F-379）。

**查询在线状态**：`GET https://www.workbuddy.cn/openapi/v2/localassistant`，权限要求 `user.localassistant.readable`（F-378）：

```
GET /openapi/v2/localassistant HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
```

响应 `data`：`online`（bool，当前用户的 PC 端本地助理是否在线，F-378）。

**发送消息**：`POST https://www.workbuddy.cn/openapi/v2/localassistant/message`，权限要求 `user.localassistant.invokable`，`Content-Type: application/json`（F-380）：

```
POST /openapi/v2/localassistant/message HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
Accept: application/json
Content-Length: 52

{"content":"帮我查一下今天的日程","msg_type":"text"}
```

请求 `body`（来源 F-381）：

| 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| content | string | 是 | 消息内容。msg_type 为 text 时为普通文本；msg_type 为 permission_response 时为序列化 JSON 字符串 |
| msg_type | string | 是 | 消息类型。允许 text（普通文本）与 permission_response（回答 AskQuestion / 工具审批） |

响应 `data`：`message_id`（string，新建消息的 ID，如 `msg-001`，F-384）。

**查询消息历史**：`GET https://www.workbuddy.cn/openapi/v2/localassistant/message`，权限要求 `user.localassistant.readable`（F-385）。查询参数（来源 F-386）：

| 参数 | 类型 | 含义 |
| --- | --- | --- |
| limit | int | 分页模式：每页条数，默认 20，**上限 100** |
| offset | int | 分页模式：偏移量，默认 0 |
| message_id | string | 增量模式：仅返回该消息之后产生的消息（用于轮询助理回复） |

传 `message_id` 时使用增量模式；不传时使用分页模式（F-386）。

### 第 6 步示例：刷新凭证

请求 `POST https://www.workbuddy.cn/openapi/v2/token`，`Content-Type: application/x-www-form-urlencoded`；请求体 4 项 `grant_type`（固定值 `refresh_token`）、`refresh_token`、`client_id`、`client_secret`（F-368、F-369）：
`grant_type=refresh_token&refresh_token=def50200a1b2...&client_id=app_7a3f2b1c&client_secret=sk_live_abc123...`（来源 F-369 示例值）。
刷新响应体字段与换取响应体**一致**（`access_token`、`token_type`、`expires_in`、`refresh_token`、`scope`、`open_id`）（F-370）。

### 第 7 步：返回码处理要点（来源 F-439，本机未实跑）

| HTTP 状态码 | 业务码 | 描述 | 排查建议 |
| --- | --- | --- | --- |
| 400 | invalid_grant | 授权码/refresh_token 失效或不匹配；核销码已用/过期/耗尽 | 重新走授权流换新码；核销类视为终态勿重试 |
| 401 | invalid_token | 鉴权未通过（缺 Bearer / 验签失败 / 缺 subject·client） | 确认鉴权三元组合法有效、token 未过期 |
| 403 | insufficient_scope | token scope 不满足端点要求 | 按 WWW-Authenticate 提示补足 scope |
| 429 | rate_limited | 请求数超过限制，收到 429 时按指数退避重试（1s → 2s → 4s） | 请求超频，降低调用频率、退避重试 |
| 500 | server_error / server error / InternalServerError | 服务内部错误 | 服务端错误，携带 request_id 联系开发者 |

以上 5 行为 F-439 规范表（共 24 行）中与授权/调用相关者，**本机未实跑，不对各码实际触发场景做验证**。

### 第 8 步：云端任务 / ACP / 会话产物（**端别：云侧**）

- **创建云端任务**：`POST https://www.workbuddy.cn/openapi/v2/tasks`，权限要求 `user.task.invokable`；支持与 WorkBuddy 移动端或小程序会话打通，返回 `task_id`、ACP `link` 与 `token`（F-390）；请求体 `prompt`（必填）、`name`（否），响应 `201 Created` 含 `task_id`、`status`、`name`、`link`、`token`、`expire_at`、`sandboxLink`、`sandboxDataLink`（F-391、F-392）。
- **ACP 通道**：基于 SSE 长连接 + JSON-RPC 2.0 的双通道模型；接收通道 `GET {link}` 带 `Authorization: Bearer {token}` 与 `Accept: text/event-stream`，响应头 `Acp-Connection-Id` 为本次连接标识；发送通道 `POST {link}` 回传 `Acp-Connection-Id`；ACP token 仅用于该通道鉴权，因底层沙箱环境差异**有效期存在不同（通常为 3 天、不过也有可能很短）**，遇 `401` 可用 `GET /tasks/{task_id}` 获取新 token（F-401、F-402）。此为**第三处独立有效期口径**，与下文 `access_token` 的两处口径**不是同一凭证**。
- **会话产物**：`_codebuddy.ai/artifact` 经 SSE 增量推送产物；产物 notification 示例 `artifact` 为 `{"type":"media","uri":"agent:///artifacts/output.png","mimeType":"image/png","size":102400}`（F-412）；Artifact 公共字段 `uri` 云端形如 `agent:///artifacts/plan.md`、本地形如 `file:///…`（F-423）。
  > **引述原文协议形态**：上述 `agent:///…` 与 `file:///…` 均为**官方文档描述的产品侧协议形态字面量（引述原文协议形态）**，**不是仓库文件路径**，也不构成本篇的 `file:///` 链接引用；此处照抄仅为忠实转述字段形态。

### 两处官方口径并列（不择一）

> 同一厂商文档内部存在以下两种口径，本节**并列表述、不择一、不替官方判定**（登记见[核验报告](../references/verification.md) 第四节）。

**① 签名填充算法：`PSS` 对 `PKCS#1`**

| 口径 | F 编号 | 来源页面 › 章节 | 原话摘要 |
| --- | --- | --- | --- |
| 口径一：`RSAwithSHA256、PSS 填充` | **F-308** | D9「生成密钥」 | 生成方式为浏览器本地生成非对称密钥对（RSA-2048，私钥 PKCS#8 PEM，签名算法 **RSAwithSHA256、PSS 填充**），私钥不经过平台服务端 |
| 口径二：`RS256、PKCS#1 v1.5 填充` | **F-346** | D9「PC端开发手册 › 签名生成：详细步骤」 | 签名算法为 **RS256，RSA PKCS#1 v1.5 填充、SHA-256 摘要**；使用与 kid 配套的 RSA-2048 私钥（PKCS#8 PEM）生成签名 |

**② 凭证有效期：`24 小时` 对 `expires_in: 3600`**

| 口径 | F 编号 | 来源页面 › 章节 | 原话摘要 |
| --- | --- | --- | --- |
| 口径一：`24 小时` | **F-285** | D9「授权认证 › Token 类型一览」 | access_token 用于调用 Open API 的凭证，**有效期 24 小时**，过期后需重新获取；refresh_token 用于刷新 access_token，**有效期 60 天**，需安全存储在服务端 |
| 口径二：`expires_in: 3600` | **F-366**（响应体示例另见 **F-367**） | D10「认证授权 API › 换取接口调用凭证（access_token）」 | 换取响应体含 `expires_in`（Number，**示例 3600**，access_token 有效期，**单位秒**；本页口径与 D9 的 24 小时不一致） |

> 两处**各自保留原话与各自来源页面，不合并、不换算**（口径一的 24 小时即 86,400 秒，口径二示例为 3,600 秒；文档**未声明**二者关系）。另：授权码 `code` 有效期另有明确口径 **一次性使用、10 分钟**（F-362）；ACP token 有效期为**第三处独立口径**（F-402）。

## 结果判据

> 本节判据均**取自官方文档描述的可观察迹象**；**本机无法闭环**——接口调用本次未实跑，授权与换票流程未真实走通，判据来自文档而非实测。

- **换票成功**：响应体包含 `access_token`、`token_type`（`Bearer`）、`expires_in`、`refresh_token`、`scope`、`open_id`（F-366、F-367）。
- **调用成功（云侧）**：携带 `Authorization: Bearer <access_token>` 调用个人资料 API，`data` 返回 `nickname` 与 `avatar`（F-373）。
- **调用成功（PC 端本机）**：本地助理 API 返回统一包裹结构，`data` 中含 `online`（F-379、F-378）或 `message_id`（F-384）。
- **刷新成功**：刷新响应体字段与换取响应体一致（F-370）。
- **异常定位**：按 HTTP 状态码 + 业务码 + 排查建议定位，如 `401 invalid_token`（鉴权未通过）、`403 insufficient_scope`、`429 rate_limited`（F-438、F-439）。
- **不可断言**：本束未实跑，**不构成功能可用性背书**；是否「已验证可用」须回源官方页面另行确认。

## 限制与边界

- **未实跑声明**：本篇**未在本机实跑**——未发起真实授权跳转、未收到真实 `code`、未换取或刷新任何真实令牌、未调用任何真实接口；文中端点、参数与示例值均来自官方文档（F-285、F-308、F-346、F-355～F-439）。
- **两处口径并列不择一**：签名填充（F-308 对 F-346）与凭证有效期（F-285 对 F-366）**并列表述、不择一、不替官方判定**；ACP token 有效期（F-402）为第三处独立口径。详见[核验报告](../references/verification.md) 第四节。
- **端与形态边界**：本地助理 API 属 **PC 端本机**，**不得当作云侧能力**（F-377）；云端任务、ACP 通道、会话产物属**云侧**（F-389、F-401、F-415）；创建云端任务支持与移动端或小程序会话打通（F-390），但**移动端开放时间点官方未给**（D9「第三方应用」页对端边界的原话仅表述为「后续开放」，F-291、F-292）。
- **官方未给（不得据名称或常识补全）**：**全局限流 / 配额数字**未给出（仅单接口分页上限有值：本地助理消息历史 `limit` 上限 100，F-386；云端任务列表 `size` 最大 100，F-395；产物列表 `limit` 取值 [1, 500]，F-420）；**审核时长**除 D9 分享应用给出「7 个工作日内」（F-294）外，其余各类均未给出；**token 撤销机制**未给；**`clientId` / `clientSecret` 的获取页面路径、生成与轮换机制**未给。
- **口径并列不换算**：`access_token` 有效期的 24 小时（F-285）与 `expires_in: 3600` 秒（F-366）两处**不合并、不换算**，须并列呈现并带核验时点 2026-10-16。
- **未采集页登记**：站点侧栏另有 `api-token`、`contact`、`developer-profile`、`legal-basis-and-examples`、`operations-data`、`service-categories-individual`、`service-categories-enterprise` 共 7 篇 `/docs/` 页**本次未采集，仅登记入口**，不得据其名称推断功能细节、字段、权限或门槛（见[核验报告](../references/verification.md) 第二节）。
- **`file:///` 使用边界**：除上文第 8 步对 Artifact `uri` 形态的**「引述原文协议形态」**标注处外，本篇不使用 `file:///`，亦不引用本机绝对路径与临时目录路径。
- **表述红线**：本篇不出现「已上线 / 已 GA / 已完成审核 / 功能已验证可用」；文档未写明 = **官方未给**，不等于默认无限制。

> 相关：概念篇[Open API 认证授权与返回码约定](../concepts/07-openapi-auth-and-conventions.md)、[Open API 接口目录与形态边界](../concepts/08-openapi-endpoint-catalog.md)；核验[核验报告](../references/verification.md)、[来源代号与 F 编号事实登记](../references/article-source.md)；平级束[WorkBuddy 官方站点与四区文档](../../workbuddy-official-docs/index.md)、[分享能力接入与推广管理](../../workbuddy-open-platform-sharing-and-promotion/index.md)。
