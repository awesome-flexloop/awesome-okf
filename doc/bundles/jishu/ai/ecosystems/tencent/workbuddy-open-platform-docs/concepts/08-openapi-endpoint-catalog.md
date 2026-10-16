---
type: Concept
title: "Open API 接口目录与形态边界"
description: "D10「Open API 接口」页第二半的原子化概念文档：七类接口（认证授权 / 个人资料 / 本地助理 / 云端任务 / ACP 通道 / 会话产物 / 兑换码核销）总表与逐类小节，含每类端点路径、HTTP 方法、权限要求与关键请求/响应参数表；标注 PC 端本机与云侧的形态边界、ACP 的 SSE + JSON-RPC 2.0 机制与 _codebuddy.ai/ 私有扩展、会话产物分层与 Artifact 公共字段、兑换码核销 API"
tags: [WorkBuddy, 开放平台, Open API, 接口目录, 端与形态边界, ACP, 会话产物, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-16" }
verified: { by: "process:seven-concepts-v", at: "2026-10-16" }
status: stable
stale_after: "2027-04-16"
sources:
  - { id: D10, resource: "https://open.workbuddy.cn/docs/openapi" }
---

# Open API 接口目录与形态边界

> 本篇是 [D10 `/docs/openapi`](https://open.workbuddy.cn/docs/openapi) 页的**第二半原子化概念文档**，回答「七类接口各能做什么、权限与端/形态边界在哪」；认证准备、OAuth 2.1 换取凭证与返回码规范见 [Open API 认证授权与返回码约定](07-openapi-auth-and-conventions.md)。
> 信源为本束 F 编号事实表（F-001～F-439，逐条见 [来源代号与 F 编号事实登记](../references/article-source.md)）；**未在本机实跑**任何接口调用。

## 一、七类接口总表

接口按能力分为**认证授权、个人资料、本地助理、云端任务、ACP 通道、会话产物和兑换码核销**七类；开发者可先根据业务目标选择对应分类，再结合权限要求、请求参数和响应结构完成接入（F-355）。各类用途原文概括见 F-356。

| 分类 | 用途（原文概括） | 端点数量 | 端或形态归属 | 权限要求 |
| --- | --- | --- | --- | --- |
| 认证授权 API | 完成用户授权并换取访问凭证 | 2（`/authorize`、`/token`） | 浏览器授权页 + 服务端令牌端点 | 换取/刷新：权限要求无（`client_secret` 应用身份验证）；授权页面向用户 |
| 个人资料 API | 获取用户的昵称和头像、校验调用方提供的手机号 | 2（`/user/profile`、`/user/phoneverification`） | **云侧** Open API | user.profile.readable / user.contact.readable |
| 本地助理 API | 查询 PC 端本地助理状态、发送消息和查询消息历史 | 3（`/localassistant`、`/localassistant/message` 的 POST 与 GET） | **PC 端本机**（与已连接 WorkBuddy 的 PC 端本地助理交互） | user.localassistant.readable / user.localassistant.invokable |
| 云端任务 API | 创建、查询云端任务，并获取任务对应的 ACP 连接信息 | 3（`POST /tasks`、`GET /tasks`、`GET /tasks/{task_id}`） | **云侧** | user.task.invokable / user.task.readable |
| ACP 通道 | 建立云端任务的实时双向通信通道，并进行协议消息交互 | 2（SSE 接收通道 + POST 发送通道；**非 REST**） | **云侧** | ACP token（`Authorization: Bearer`） |
| 会话产物 | 查询云端会话产生的计划、任务、媒体和总结等产物 | 1（REST `GET {sandbox_url}/api/session/artifacts`）+ 1（SSE 扩展方法 `_codebuddy.ai/artifact`） | **云侧** | `task_ticket`（与 ACP 通道共用同一份） |
| 兑换码核销 API | 通过兑换码或卡券为当前授权用户发放积分 | 1（`POST /redemptions`） | **云侧** Open API | user.credit.exchange |

> **端点口径**：上表合计 **12 个 REST 端点**（`/token` 路径被换取与刷新两个接口复用，计 1），另加 **2 个 ACP 通道**（SSE 接收 + POST 发送，非 REST）与 **1 个 SSE 扩展方法**（`_codebuddy.ai/artifact`）。
> 表中「PC 端本机」与「云侧」的端归属引自官方文档原话（本地助理面向「已连接 WorkBuddy 的 PC 端本地助理」，F-377；云端任务、ACP 通道、会话产物均为云侧能力，F-389、F-401、F-415），见 [核验报告](../references/verification.md) 第三节口径 ③。

## 二、认证授权 API

完成用户授权并换取访问凭证。端点：`GET /openapi/v2/authorize`（F-359～F-361）与 `POST /openapi/v2/token`（换取 F-364～F-367、刷新 F-368～F-370）。参数表、响应体字段、凭证有效期两处口径并列与返回码规范**详见** [Open API 认证授权与返回码约定](07-openapi-auth-and-conventions.md)，本篇不重复。

## 三、个人资料 API

概述原话仅一句「个人资料API」（F-371）。

### 3.1 获取用户资料

`GET https://www.workbuddy.cn/openapi/v2/user/profile`；权限要求 `user.profile.readable`（F-372）。用于获取用户的昵称和头像。

响应 `data`（来源 F-373）：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| nickname | String | 当前用户的昵称 |
| avatar | String | 当前用户的头像 |

响应报文带 `Cache-Control: private, no-store`（F-373）。

### 3.2 验证用户联系方式

`POST https://www.workbuddy.cn/openapi/v2/user/phoneverification`；权限要求 `user.contact.readable`（F-374）。验证调用方提供的手机号是否与当前授权用户绑定的个人手机号一致；**接口只返回匹配结果，不会返回用户真实手机号或脱敏手机号**（F-374）。

手机号格式要求（来源 F-375）：中国大陆手机号支持 `13812345678` 或 `+8613812345678`；支持空格、短横线和括号等常见分隔形式；香港、澳门手机号必须明确携带 `+852` 或 `+853`；不接受未携带国家码的 8 位号码，避免地区歧义。

响应 `data`：`matched`（Boolean，手机号是否匹配，F-376）。

## 四、本地助理 API（PC 端本机）

概述：本地助理 API 用于与**已连接 WorkBuddy 的 PC 端本地助理**进行消息交互，包括查询在线状态、发送消息和查询消息历史（F-377）。**端归属：PC 端本机**。

### 4.1 查询本地助理在线状态

`GET https://www.workbuddy.cn/openapi/v2/localassistant`；权限要求 `user.localassistant.readable`（F-378）。查询当前用户的 PC 端本地助理是否在线。

响应 `data`：`online`（bool，当前用户的 PC 端本地助理是否在线，F-378）。

本地助理 API 的响应为**统一包裹结构**：`{"code":0,"msg":"success","request_id":"a1b2c3d4e5","data":{...}}`（F-379）。

### 4.2 发送消息给本地助理

`POST https://www.workbuddy.cn/openapi/v2/localassistant/message`；权限要求 `user.localassistant.invokable`；`Content-Type: application/json`（F-380）。向 PC 端本地助理发送消息，触发助理执行任务。

请求 `body`（来源 F-381）：

| 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| content | string | 是 | 消息内容。msg_type 为 text 时为普通文本；msg_type 为 permission_response 时为序列化 JSON 字符串 |
| msg_type | string | 是 | 消息类型。允许 text（普通文本）与 permission_response（回答 AskQuestion / 工具审批） |

`permission_response` 时 `content` 类型**仍为字符串**、内部承载序列化 JSON（F-382）；其内部 JSON 字段（来源 F-383）：

| 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| outcome | string | 是 | 选择结果。回答问卷时为 selected |
| requestId | string | 是 | 待回答的问卷或工具审批请求 ID，须与下行 permission 请求一致 |
| answers | object | 是 | 问卷答案。key 为 q_0、q_1…；单选值为字符串，多选值为字符串数组 |

响应 `data`：`message_id`（string，新建消息的 ID，如 `msg-001`，F-384）。

### 4.3 查询本地助理消息历史

`GET https://www.workbuddy.cn/openapi/v2/localassistant/message`；权限要求 `user.localassistant.readable`（F-385）。查询当前用户本地助理的消息历史，**支持分页查询和增量查询**。

查询参数（来源 F-386）：

| 参数 | 类型 | 含义 |
| --- | --- | --- |
| limit | int | 分页模式：每页条数，默认 20，**上限 100** |
| offset | int | 分页模式：偏移量，默认 0 |
| message_id | string | 增量模式：仅返回该消息之后产生的消息（用于轮询助理回复） |

传 `message_id` 时使用增量模式；不传时使用分页模式（F-386）。

响应 `data`：`messages`（array，消息列表，F-387）。`messages[]` 单条消息元素 7 字段（来源 F-388）：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| message_id | string | 消息 ID |
| role | string | 角色：user（用户）/ assistant（助理） |
| content | array | 消息内容，恒为数组（无值给 `[]`，不省 key） |
| msg_type | string | 消息类型，从下游 metadata 的 msgType 提取 |
| created_at | string | 创建时间（ISO8601，如 2026-07-30T10:00:00Z） |
| attachments | array | 附件列表，恒为数组（无值给 `[]`） |
| metadata | object | 元数据，恒为对象（无值给 `{}`） |

## 五、云端任务 API（云侧）

概述：云端任务 API 用于创建和查询云端任务，并返回 **ACP 连接地址和鉴权 token**，以便与云端会话建立实时通信（F-389）。**端归属：云侧**。

### 5.1 创建云端任务

`POST https://www.workbuddy.cn/openapi/v2/tasks`；权限要求 `user.task.invokable`（F-390）。**支持与 WorkBuddy 移动端或小程序会话打通**，返回 `task_id`、ACP `link` 和 `token`（F-390）。

请求体（来源 F-391）：

| 参数 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| prompt | string | 是 | 任务的初始指令，用于创建会话、生成标题与初始状态 |
| name | string | 否 | 任务名称；不传由服务端按 prompt 生成 |

响应 `201 Created`，响应体 7 字段（来源 F-392；查询接口响应体同构，F-400）：

| 字段 | 类型 | 必返 | 含义 |
| --- | --- | --- | --- |
| task_id | string | 是 | 任务 ID，实际对应 agentserver conversation ID |
| status | string | 是 | 任务/会话当前状态 |
| name | string | 否 | 任务或会话名称 |
| link | string | 否 | ACP 连接地址，用于连接任务沙箱 |
| token | string | 否 | ACP 网关鉴权凭据 |
| expire_at | integer | 否 | token 过期时间，Unix 秒级时间戳 |
| sandboxLink | string | 否 | 沙箱控制面访问地址 |
| sandboxDataLink | string | 否 | 沙箱数据面访问地址 |

### 5.2 status 字段枚举

创建与查询两处**重复出现**同一枚举，共 9 值（来源 F-393）：

| 状态 | 含义 |
| --- | --- |
| CREATING | 正在创建任务和沙箱 |
| idle | 空闲，等待执行 |
| planning | 正在规划 |
| working | 正在执行 |
| pending | 暂停或等待外部输入 |
| completed | 已完成 |
| failed | 执行失败 |
| archived | 已归档 |
| deleted | 已删除 |

### 5.3 查询云端任务列表

`GET https://www.workbuddy.cn/openapi/v2/tasks`；权限要求 `user.task.readable`（F-394）。返回任务基本信息和 ACP Link，**不返回 ACP Token 及其过期时间**（F-394）。

查询参数（来源 F-395）：

| 参数 | 类型 | 必填 | 默认值 | 含义 |
| --- | --- | --- | --- | --- |
| page | integer | 否 | 1 | 页码；非整数或小于 1 时按 1 处理 |
| size | integer | 否 | 20 | 每页数量；非整数或小于 1 时按 20 处理，最大为 100，超过 100 时按 100 处理 |

响应字段（来源 F-396）：`tasks[]`（含 `task_id`、`status`、`name`、`link`、`created_at`、`updated_at`）、`total`、`pagination`（含 `page` / `size` / `total`）。

列表接口**不会返回 `token` 和 `expire_at`**；如需获取任务的 ACP Token，请调用 `GET /openapi/v2/tasks/{task_id}`（F-397）。

### 5.4 查询云端任务

`GET https://www.workbuddy.cn/openapi/v2/tasks/{task_id}`；权限要求 `user.task.readable`；响应 `200 OK`（F-398）。可查询任务状态并**获取新的 ACP link/token**；创建任务后若响应暂时没有 `link` 或 `token`，可**轮询该接口直到补齐**（F-398）。

路径参数：`task_id`（string，必填，创建任务时返回的 `task_id`，F-399）。响应体字段与创建响应**一致**（F-400）。

## 六、ACP 通道（云侧）

### 6.1 发起对话与协议模型

创建或查询任务拿到 `link` 与 `token` 后，通过它们与云端会话通信（F-401）。ACP（Agent Client Protocol）**基于 SSE 长连接 + JSON-RPC 2.0**，采用**双通道模型**：一条 GET SSE 长连接用于接收服务端推送（流式回答、通知），POST 请求用于发送 JSON-RPC 调用，两者通过**同一个连接标识**关联（F-401）。

### 6.2 建连与鉴权

- **接收通道**：`GET {link}`，请求头带 `Authorization: Bearer {token}` 与 `Accept: text/event-stream`，建立 SSE 长连接；响应头中的 `Acp-Connection-Id` 是本次连接的标识（F-402）。
- **发送通道**：`POST {link}`，请求头带 `Authorization: Bearer {token}`、`Content-Type: application/json`，并**回传 `Acp-Connection-Id`** 以关联到上面的 SSE 连接；Body 为 JSON-RPC 请求，返回结果（含流式回答）经 SSE 通道异步推回（F-402）。
- **token**：仅用于 ACP 通道鉴权；因 Agent 底层沙箱环境差异，**有效期存在不同，通常为 3 天、不过也有可能很短**；遇 ACP 请求 `401`，可用 `GET /tasks/{task_id}` 获取新 token（F-402）。此为本束**第三处独立有效期口径**，与 `access_token` 的两处口径（见 [认证篇](07-openapi-auth-and-conventions.md) 2.6）**不是同一凭证**。

### 6.3 对话流程（JSON-RPC）

三步：`initialize`（协商协议版本与客户端能力，建连后首先调用一次）、`session/load`（加载已创建的会话，`params.sessionId` 传创建任务返回的 `task_id`）、`session/prompt`（发送提问，`params.prompt` 为 ContentBlock 数组，每个元素含 `type=text` 与 `text` 字段；追问时复用同一 `sessionId` 再次调用）（F-403）。

| 步骤 | 示例 params 要点 | F 编号 |
| --- | --- | --- |
| initialize | `protocolVersion` 为 1；`clientCapabilities` 的 `fs` 含 `readTextFile` / `writeTextFile` | F-404 |
| session/load | `sessionId`、`cwd`、`mcpServers` | F-405 |
| session/prompt | `sessionId`、`prompt` 为 ContentBlock 数组 | F-406 |

### 6.4 接收服务端消息

服务端经 SSE 回推两类 JSON-RPC 消息（F-407、F-408）：

| 类型 | 方法 | 用途 |
| --- | --- | --- |
| Notification | session/update | 流式增量：对话内容、工具调用、任务规划、会话状态 |
| Request（需应答） | session/request_permission | 需要用户交互的确认：工具执行授权、AskUserQuestion |
| Response（对 session/prompt） | — | 一轮 prompt 的最终结束标记：stopReason + usage |

- Notification（无 id）：单向推送，客户端不需要应答；Server-to-Client Request（有 id）：需客户端在超时前通过 SSE 关联的 `Acp-Connection-Id` 回一条 response（F-407）。
- **任务完成判定**：`session/prompt` 的 response 是「本轮结束」的**权威信号**；`result.stopReason` 表示结束原因，取值 `end_turn`、`max_tokens`、`max_turn_requests`、`refusal`、`cancelled`（F-409）。

### 6.5 扩展方法（`_codebuddy.ai/` 私有扩展）

除标准 ACP 方法外，服务端还会经 SSE 下推以 `_codebuddy.ai/` 为前缀的**扩展 JSON-RPC notification**，用于承载 ACP 标准协议未定义的会话资产（如产物、断点、命令等）（F-410）：这些消息遵循 JSON-RPC 2.0（无 id、无需应答）；客户端未识别的方法**可安全忽略**；不在 ACP 官方协议（`agentclientprotocol.com`）中定义，是 **WorkBuddy 云端对 ACP 的私有扩展**（F-410）。

当前对接方最需关注的扩展方法：`_codebuddy.ai/artifact`，用于产物（计划 / 任务清单 / 媒体 / 总结）**增量推送**（F-411）。

产物 notification 的 `params` 含 `sessionId`、`event` 与 `artifact`；示例 `event` 为 `created`，`artifact` 为 `{"type":"media","uri":"agent:///artifacts/output.png","mimeType":"image/png","size":102400}`（F-412）。三种 `event` 值（来源 F-413）：

| event | 含义 |
| --- | --- |
| created | 新增产物，artifact 为完整对象 |
| updated | 产物变更，artifact 为完整对象（整体覆盖，非 diff） |
| deleted | 产物移除，artifact 仅保证 type 与 uri 字段 |

客户端应以 `artifact.uri` 为主键做本地 `upsert` / `delete`；**重复收到 `created` 视为等价于 `updated`**（F-414）。

## 七、会话产物（云侧）

### 7.1 REST 拉取与 SSE 增量

SSE 通道推送的是**增量事件**；如需一次性获取会话内所有历史产物（如首屏渲染、状态恢复），可通过 REST 接口 `GET /api/session/artifacts` 拉取；**SSE 与 REST 数据同源**，二者可组合使用（首屏 REST 拉全量 + 后续 SSE 增量）（F-415）。

接口 `GET {sandbox_url}/api/session/artifacts`；鉴权方式 `Header: Authorization: Bearer {task_ticket}`；`Content-Type: application/json`（F-416）。

- `sandbox_url` 由「创建云端任务」/「查询云端任务」接口返回的 `link` 字段**去掉末尾 `/acp` 路径段**得到（F-417）。
- 鉴权凭证 `task_ticket` 与 **ACP 通道共用同一份**；`task_ticket` 过期返回 HTTP `401`，此时调用「查询云端任务」接口换取新的 `task_ticket` 后重试（F-418）。

请求示例三类（F-419）：拉取全部产物；仅拉取媒体类产物并分页（`?type=media&limit=50&offset=0`）；增量拉取（`?startMs=1730000000000`，配合本地记录的 `lastUpdatedAt`）。

查询参数（来源 F-420）：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| sessionId | string | 否 | 目标会话 ID。单 session 沙箱可省略（自动使用当前活跃会话）；多 session 场景必填 |
| type | string | 否 | 按产物类型过滤，允许值 plan / tasks / media / overview；省略则返回全部类型 |
| startMs | int64 | 否 | 仅返回 updatedAt >= startMs 的记录（epoch 毫秒）；省略或 0 表示不限下界 |
| endMs | int64 | 否 | 仅返回 updatedAt <= endMs 的记录（epoch 毫秒）；省略或 0 表示不限上界 |
| limit | int | 否 | 分页大小，取值 [1, 500]；省略或 0 表示不分页，一次返回全部 |
| offset | int | 否 | 分页偏移，取值 >= 0，默认 0 |

响应顶层（F-421）：`code`（int，0 表示成功）、`msg`（string）、`data.sessionId`、`data.artifacts`（array，Entry 数组）、`data.pagination`（含 `total` / `returned` / `limit` / `offset` / `hasMore`）、`data.filter`（本次请求生效的过滤条件回显）。

Entry 字段 `data.artifacts[]`（来源 F-422）：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| sessionId | string | 所属会话 ID |
| event | string | 产物最近一次变更事件，取值 created / updated / deleted |
| artifact | object | 产物本体（结构见 Artifact 字段） |
| md5 | string | 产物内容 md5（可选，用于去重/秒传） |
| url | string | 媒体类产物的直接访问 URL（可选，仅 artifact.type = media 时返回） |

### 7.2 Artifact 公共字段

来源 F-423：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| type | string | 判别式，取值 plan / tasks / media / overview |
| uri | string | 产物唯一标识。云端形如 agent:///artifacts/plan.md，本地形如 file:///…。跨消息以此为主键 |
| name | string | 资源名（如文件名） |
| title | string | 显示标题 |
| description | string | 描述文本 |
| mimeType | string | MIME 类型 |
| createdAt | int64 | 创建时间（epoch 毫秒） |
| updatedAt | int64 | 最近更新时间（epoch 毫秒） |

> **引述原文协议形态**：上表 `uri` 的云端形如 `agent:///artifacts/plan.md`、本地形如 `file:///…`（F-423），以及 6.5 的 `agent:///artifacts/output.png`（F-412），均为**官方文档描述的产品侧协议形态字面量**，**不是仓库文件路径**，也不构成本束的 `file:///` 链接引用；此处照抄仅为忠实转述字段形态。

### 7.3 Artifact 分类型字段

`type = plan`（计划文档，Markdown，F-424）：`text`（当前 Markdown 全文）、`version`（版本号，每次更新递增）、`previousText`（上一版全文，可用于展示 diff）、`enableEdit`（是否允许前端编辑回写）。

`type = tasks`（任务清单，F-425）：`tasks`（array，元素含 `id` / `content` / `status`（pending / in_progress / completed / cancelled）/ `order`）、`enableEdit`。

`type = media`（媒体文件，F-426）：`mimeType`（如 image/png / video/mp4 / audio/mpeg）、`size`（文件字节数）、`contentType`（粗分类：image / video / audio / document 等）、`width`、`height`。

`type = overview`（任务总结，Markdown，F-427）：`text`（总结 Markdown 全文）。

**媒体文件的下载**（F-428）：优先使用 Entry 层的 `url` 字段；若未提供，可将 `uri` 中的 `agent:///` 替换为 `{sandbox_url}/` 后请求（复用同一份 `task_ticket` 鉴权）。

### 7.4 错误响应与使用建议

错误响应（来源 F-429）：

| HTTP | code | 典型场景与说明 |
| --- | --- | --- |
| 200 | 0 | 成功 |
| 400 | 1 | 参数非法。典型消息：sessionId is required（多 session 未指定）；invalid type（超出白名单）；startMs / endMs / limit / offset 越界或类型错误 |
| 401 | — | task_ticket 缺失、无效或已过期。调用「查询云端任务」接口换新后重试 |
| 404 | 1 | 会话不存在（会话已结束或 sessionId 错误） |

错误响应体格式示例（F-430）：`{"code": 1, "msg": "invalid type: xxx (allowed: plan、tasks、media、overview)"}`。

使用建议 3 条（F-431）：首屏渲染（进入会话时调用一次 REST 接口拉取全量产物，按 `artifact.uri` 建立本地索引）；增量更新（订阅 SSE `_codebuddy.ai/artifact` 通知，按 `event` 对本地索引执行 `upsert` / `delete`）；会话恢复（REST 首屏加 SSE 增量的组合**天然幂等**，同 `uri` 直接覆盖即可）。

## 八、兑换码核销 API（云侧）

概述（F-432）：通过核销兑换码或卡券，为当前授权用户发放积分（credits）；接口支持**单码模式和双码模式**。

`POST https://www.workbuddy.cn/openapi/v2/redemptions`；权限要求 `user.credit.exchange`；`Content-Type: application/json`（F-433）。

请求 `body`（来源 F-435；场景 A 兑换码示例见 F-434）：

| 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| code | string | 单码模式必填 | 运营平台兑换码，如 CODE-OPER-8888；1-64 字符 |
| gift_key | string | 双码模式必填 | 云平台卡号（卡 key），如 GK-000001；6-64 字符 |
| gift_code | string | 双码模式必填 | 云平台卡密；8-64 字符 |
| request_id | string | 是 | 幂等/防重请求号，长度 8-64（示例为 UUID） |

响应字段（来源 F-436）：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| status | string | 核销结果状态，如 success |
| flow_no | string | 核销流水号，如 flow-2026072912345 |
| credits | int64 | 本次核销发放的积分 |
| open_id | string | 领取用户的 open_id（pairwise，按应用维度隔离） |

兑换码核销 API 的返回码表**仅一行**（来源 F-437）：`200 核销成功`。

## 九、端与形态边界汇总

| 端或形态 | 归属 | 关键接口 / 能力 | F 编号 |
| --- | --- | --- | --- |
| **PC 端本机** | 本机本地助理 | 查询在线状态、发送消息、查询消息历史 | F-377、F-378、F-380、F-385 |
| **云侧** | 开放平台云侧 Open API | 个人资料、云端任务、兑换码核销 | F-372、F-390、F-433 |
| **云侧** | 云端会话实时通道 | ACP 通道（SSE + JSON-RPC 2.0） | F-401、F-402、F-410 |
| **云侧** | 云端会话产物 | 产物 REST 拉取与 SSE 增量 | F-415、F-416、F-417 |
| **移动端会话打通** | 云侧能力，端侧规划态 | 创建云端任务支持与移动端或小程序会话打通 | F-390 |

> 「本地助理 API」为 **PC 端本机**能力，不得当作云侧能力；「云端任务 API」返回的 ACP 连接信息用于**云侧**会话；移动端「后续开放」类表述按原话保留为**规划态**，不升级为已支持（见 [核验报告](../references/verification.md) 第三节口径 ③）。

## 十、边界与未给

- **官方未给**：全局限流 / 配额数字（仅单接口分页上限有值：本地助理消息历史 `limit` 上限 100，F-386；云端任务列表 `size` 最大 100，F-395；产物列表 `limit` 取值 [1, 500]，F-420）；`sandboxLink` / `sandboxDataLink` 的用途细节与生命周期。
- **未在本机实跑**：本束未注册账号、未调用任何真实接口，上表所有示例值与端点均来自官方文档所述，**不构成功能可用性背书**。
- **未采集**：`api-token` 等 7 篇 `/docs/` 页本次未采集、仅登记入口，**不得据名称推断**（见 [边界、版本与已知缺口](10-boundaries-versions-and-known-gaps.md)）。
- **口径并列不择一**：`access_token` 有效期两处口径（F-285 对 F-366）见 [认证篇](07-openapi-auth-and-conventions.md) 2.6；ACP token 有效期为独立第三处（F-402）。

## 相关

- [Open API 认证授权与返回码约定](07-openapi-auth-and-conventions.md)（D10 第一半：准备工作、OAuth 2.1、返回码规范表）
- [边界、版本与已知缺口](10-boundaries-versions-and-known-gaps.md)（跨页汇总）
- [来源代号与 F 编号事实登记](../references/article-source.md)、[核验报告](../references/verification.md)、[页级采集与覆盖台账](../references/source-manifest.md)
