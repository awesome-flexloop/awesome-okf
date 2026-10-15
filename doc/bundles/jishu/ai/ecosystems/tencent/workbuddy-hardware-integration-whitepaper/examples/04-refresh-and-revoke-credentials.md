---
type: Example
title: "照做：刷新与撤销个人票据"
description: "票据默认 7200 秒过期，按 refresh_token 换取新票；同时说明用户后台撤销与合作方主动撤销两条路径、401 invalid_token 的处置，以及以 openid 为键的多用户数据隔离。"
tags: [WorkBuddy, 智能硬件, refresh_token, 撤销授权, openid, 接入示例, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: P0, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json" }
---

# 照做：刷新与撤销个人票据

> 适用场景：个人票据有有效期，过期后不能继续调用；同时用户或合作方都可能主动终止授权。本篇说明续期、撤销与失效处置三条路径。票据有效期与刷新撤销的机制说明见 [OAuth 2.0 授权流程](../concepts/05-oauth2-authorization-flow.md)。

## 前置条件

- **首次换票已完成**：持有换票返回的 `access_token`、`refresh_token` 与 `openid`（F-126）。
- **应用凭证**：`client_id` 与 `client_secret` 保存在合作方后端（F-120、F-127）。
- **有效期认知**：`expires_in` 默认 **7200 秒**，过期后用 `refresh_token` 换新票（F-152、F-126）。
- **多用户存储键**：以 `openid` 作为用户维度的存储与查询主键，同一 `openid` 对应的所有 WorkBuddy 资产（助理、任务）归属该用户（F-153）。

## 操作步骤

> 以下步骤**未在本机实跑，依据白皮书（F-128、F-129、F-152、F-155）**；本束未刷新或撤销任何真实票据。

1. **判断是否需要续期**：票据过期或接口返回 `401 invalid_token` 时，进入续期流程（F-130、F-155）。〔**未在本机实跑，依据白皮书 F-130、F-155**〕
2. **刷新票据**：`POST /oauth/token`，携带刷新参数换取新票（F-128）。〔**未在本机实跑，依据白皮书 F-128**〕
3. **用户后台撤销**：用户可在 WorkBuddy 后台随时撤销合作方应用授权，此后老票据立即作废（F-129）。〔**未在本机实跑，依据白皮书 F-129**〕
4. **合作方主动撤销**：合作方应用可调用 `POST /oauth/revoke` 主动撤销授权（F-129）。〔**未在本机实跑，依据白皮书 F-129**〕
5. **失效后兜底**：若续期后仍返回 401，说明用户已撤销授权或权限发生变化，应引导用户重新完成 OAuth 授权（F-155）。〔**未在本机实跑，依据白皮书 F-155**〕

### 示例：刷新票据

```http
POST https://open.workbuddy.cn/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&refresh_token=<refresh_token>
&client_id=YOUR_CLIENT_ID
&client_secret=YOUR_CLIENT_SECRET
```

参数 `grant_type=refresh_token`、`refresh_token`、`client_id`、`client_secret` 取自白皮书（F-128）。

### 示例：合作方主动撤销

```http
POST https://open.workbuddy.cn/oauth/revoke
# 端点来自白皮书（F-129）；其请求参数与返回结构白皮书未给出，以官网开发者文档为准
```

## 结果判据

- **续期成功**：刷新接口返回新的 `access_token`（结构同首次换票，含 `token_type=Bearer`、`expires_in`、`scope`、`openid`）（F-126、F-128）。
- **有效期判据**：新票有效期由 `expires_in` 指定，默认 7200 秒（F-152）。
- **撤销生效判据**：用户后台撤销后，**老票据立即作废**（F-129）；此后原票据调用将返回 401。
- **多用户隔离判据**：以 `openid` 为键可稳定地存取每个用户各自的助理与任务（F-153）。

## 限制与边界

- **未实跑声明**：本束**未在本机实跑**——未刷新任何票据、未调用撤销接口；上述步骤均为白皮书转述（F-128、F-129、F-152、F-153、F-155）。
- **撤销接口信息不全**：白皮书仅登记 `POST /oauth/revoke` 这一条主动撤销路径，**未给出其请求参数与返回结构**（F-129），不得据端点推断字段；具体**以官网开发者文档为准**（F-113，`以官网为准`）。
- **401 处置顺序**：先尝试 `refresh_token` 续期，仍返回 401 再引导重新授权（F-155）；不要把它当作可无限重试的错误。
- **票据存放纪律**：`refresh_token` 与 `access_token` 均属敏感凭据，应保存在合作方后端**不下发端侧**（F-127、F-156）。
- **用户可随时收回**：撤销是用户侧权利，合作方不应假设票据长期有效；应把「授权失效 → 重新引导授权」做成常规分支（F-129、F-155）。

> 相关：[OAuth 授权并换取个人票据](01-oauth-authorize-and-exchange-token.md)、[硬件后端反向代理姿势](05-hardware-backend-proxy-pattern.md)。
