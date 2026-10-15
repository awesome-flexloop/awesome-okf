---
type: Example
title: "照做：OAuth 2.0 授权并换取个人票据"
description: "按标准 OAuth 2.0 授权码 + PKCE 流程，引导用户跳转 WorkBuddy 授权页、回调取 code，再由合作方后端用 code 与 code_verifier 换取 access_token、refresh_token 与 openid。"
tags: [WorkBuddy, 智能硬件, OAuth, PKCE, access_token, 接入示例, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: P0, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json" }
---

# 照做：OAuth 2.0 授权并换取个人票据

> 适用场景：你的合作方 App 需要在用户点击「绑定 WorkBuddy」后完成账号绑定，取得调用开放接口所需的**个人票据**。WorkBuddy 采用标准 OAuth 2.0 授权码流程并支持 PKCE，用户在 WorkBuddy 侧完成登录与权限确认，合作方应用后端通过 code 换取票据，**全程不接触用户密码**（F-119）。流程全景见 [OAuth 2.0 授权流程](../concepts/05-oauth2-authorization-flow.md)。

## 前置条件

- **已有应用凭证**：已完成[注册应用并配置 scope](00-register-app-and-configure-scope.md)，持有 `client_id`、`client_secret` 与已登记的 `redirect_uri`（F-120、F-121）。
- **已确定 scope**：授权链接中携带的 scope 与业务所需能力一致，例如 `assistant.read assistant.write task.read task.write`（F-122、F-124）。
- **PKCE 材料**：本地生成 `code_challenge`（由 `code_verifier` 派生），并保留 `code_verifier` 供换票使用；`code_challenge_method` 取 `S256`（F-124、F-125）。
- **合作方后端**：具备可存放个人票据的服务端，因为票据**应保存在合作方 App 后端**（F-127）。
- **state 值**：生成一个随机 `state`，用于回调时校验以防范 CSRF（F-123、F-124）。

## 操作步骤

> 以下步骤**未在本机实跑，依据白皮书（F-119、F-123、F-124、F-125）**；本束未登记真实应用、未生成真实票据。

1. **引导用户跳转授权页**：合作方 App 引导用户跳转至 WorkBuddy 授权页，携带 `client_id`、`redirect_uri`、`scope`、`state`、`code_challenge`（F-123）。〔**未在本机实跑，依据白皮书 F-123**〕
2. **用户登录并确认权限**：用户在 WorkBuddy 侧登录并确认权限范围（F-123）。〔**未在本机实跑，依据白皮书 F-123**〕
3. **接收回调**：WorkBuddy 回调 `redirect_uri`，附带 `code` 与原始 `state`；后端须校验 `state` 与本地保存值一致（F-123）。〔**未在本机实跑，依据白皮书 F-123**〕
4. **后端换取个人票据**：合作方 App 后端用 `code`、`client_secret` 与 `code_verifier` 换取 `access_token`、`refresh_token` 与 `openid`（F-123、F-125）。〔**未在本机实跑，依据白皮书 F-123、F-125**〕
5. **保存并进入调用**：合作方 App 携带 `access_token` 调用 WorkBuddy API，绑定完成（F-123、F-132）。〔**未在本机实跑，依据白皮书 F-123、F-132**〕

### 授权页跳转链接（第 1 步）

```http
GET https://open.workbuddy.cn/oauth/authorize
  ?response_type=code
  &client_id=YOUR_CLIENT_ID
  &redirect_uri=https%3A%2F%2Fyourapp.example.com%2Fcallback
  &scope=assistant.read assistant.write task.read task.write
  &state=RANDOM_STATE
  &code_challenge=CODE_CHALLENGE
  &code_challenge_method=S256
```

参数 `response_type=code`、`client_id`、`redirect_uri`、`scope`、`state`、`code_challenge`、`code_challenge_method=S256`（F-124）。

### 使用授权码换取票据（第 4 步）

```http
POST https://open.workbuddy.cn/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=RECEIVED_CODE
&redirect_uri=https%3A%2F%2Fyourapp.example.com%2Fcallback
&client_id=YOUR_CLIENT_ID
&client_secret=YOUR_CLIENT_SECRET
&code_verifier=CODE_VERIFIER
```

参数 `grant_type=authorization_code`、`code`、`redirect_uri`、`client_id`、`client_secret`、`code_verifier`（F-125）。

## 结果判据

换票成功后，返回体应包含以下字段（值均为占位符，结构取自白皮书）（F-126）：

```json
{
  "access_token": "<access_token>",
  "refresh_token": "<refresh_token>",
  "token_type": "Bearer",
  "expires_in": 7200,
  "scope": "assistant.read assistant.write task.read task.write",
  "openid": "<openid>"
}
```

- **票据三件套到手**：`access_token`、`refresh_token` 与 `openid`（F-126）；`openid` 是合作方侧的用户唯一标识，用于数据隔离（F-118、F-131）。
- **鉴权格式**：后续所有请求在 HTTP Header 携带 `Authorization: Bearer <access_token>`，接口以用户身份操作、只返回该用户资产（F-132）。
- **有效期**：由 `expires_in` 指定，**默认 7200 秒**（F-126、F-152）；过期后需刷新，见[刷新与撤销票据](04-refresh-and-revoke-credentials.md)。
- **绑定完成**：五步走完，合作方 App 已可携带票据调用开放接口（F-123）。

## 限制与边界

- **未实跑声明**：本束**未在本机实跑**——未发起真实授权跳转、未收到真实 `code`、未进行真实换票；文中端点、参数与返回字段均依白皮书（F-119、F-123、F-124、F-125、F-126、F-127）。
- **PKCE 与 state 不可省**：`code_challenge_method` 固定为 `S256`（F-124）；`state` 必须原样回传并在后端校验，`code` 为一次性授权码。
- **票据只存后端**：个人票据应保存在合作方 App 后端，**不建议下发到硬件端或前端**；硬件与前端通过合作方后端间接调用 WorkBuddy API（F-127、F-156）。
- **失效处置**：接口返回 `401 invalid_token` 时应引导用户重新完成授权（F-130）；也可先尝试用 `refresh_token` 续期（F-155）。
- **口径提示**：授权页与换票接口的最终参数、字段与错误码**以官网开发者文档最新版本为准**（F-113，`以官网为准`）。

> 下一步：[创建并激活云端助理](02-create-and-activate-cloud-assistant.md)；前后端分工见[硬件后端反向代理姿势](05-hardware-backend-proxy-pattern.md)。
