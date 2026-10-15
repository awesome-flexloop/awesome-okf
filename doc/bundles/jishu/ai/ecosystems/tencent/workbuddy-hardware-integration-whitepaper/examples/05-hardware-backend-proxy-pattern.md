---
type: Example
title: "照做：硬件后端的反向代理接入姿势"
description: "硬件本体不持有个人票据，由合作方后端代为调用 WorkBuddy API：硬件只负责语音输入、卡片呈现与语音播报，业务编排在后端完成；附凭据隔离与最小授权要点。"
tags: [WorkBuddy, 智能硬件, 反向代理, 凭据安全, scope, 接入示例, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: P0, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json" }
---

# 照做：硬件后端的反向代理接入姿势

> 适用场景：眼镜、耳机、桌宠等**硬件本体**要接入 WorkBuddy。白皮书给出的接入姿势是——硬件本体通过**合作方后端间接调用** WorkBuddy API，**个人票据不下发到端侧**；硬件负责语音输入、卡片呈现与语音播报，业务编排由合作方后端完成（F-150、F-127）。端云协同分工见[开放平台与核心概念](../concepts/04-open-platform-and-core-concepts.md)。

## 前置条件

- **合作方后端**：一个可保存个人票据的服务端，并具备与 WorkBuddy 通信的能力；票据应保存在合作方 App 后端（F-127）。
- **硬件本体**：具备语音采集 / 播报 / 显示能力的终端，能向合作方后端发起自定义请求（F-150）。
- **凭据已就绪**：后端已完成 [OAuth 授权换票](01-oauth-authorize-and-exchange-token.md)，持有 `access_token` 与 `openid`（F-126）。
- **映射关系**：后端需维护「硬件设备 ↔ `openid`」的绑定关系，用户身份基于 OAuth 授权后颁发的 `openid` 唯一标识（F-074、F-153）。
- **最小授权**：后端持有票据的前提下，scope 按能力逐项最小授权（F-158）。

## 操作步骤

> 以下步骤**未在本机实跑，依据白皮书（F-127、F-150、F-156）**；本束未部署任何硬件或后端。

1. **硬件侧采集与呈现**：硬件负责语音输入、卡片呈现与语音播报，不承载业务逻辑（F-150）。〔**未在本机实跑，依据白皮书 F-150**〕
2. **硬件请求合作方后端**：硬件把输入发往合作方后端的自定义接口（非 WorkBuddy 端点，路径由合作方自定）。〔**未在本机实跑，依据白皮书 F-150、F-127**〕
3. **后端完成业务编排**：后端决定调用哪个助理、发起什么任务，并组装请求（F-150）。〔**未在本机实跑，依据白皮书 F-150**〕
4. **后端代理调用 WorkBuddy**：后端携带后端的票据调用 WorkBuddy API，个人票据**不下发端侧**（F-127、F-150）。〔**未在本机实跑，依据白皮书 F-127、F-150**〕
5. **结果回端呈现**：后端把任务回复或产出物摘要返回硬件，由硬件播报 / 呈现（F-150）。〔**未在本机实跑，依据白皮书 F-150**〕

### 第 2 步：硬件 → 合作方后端（自定义接口）

```http
POST https://your-backend.example.com/hardware/ask
# 该端点属合作方自有，不对应 WorkBuddy 端点；仅示意「硬件只做输入/呈现」的分工（F-150）
```

### 第 4 步：合作方后端 → WorkBuddy API

```http
POST https://open.workbuddy.cn/openapi/v2/tasks
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "asst_id": "asst_xxx",
  "execution_target": "cloud",
  "input": "翻译：hello world"
}
```

Header 与请求体依白皮书通用规范与任务接口（F-132、F-133、F-142、F-144）；票据由后端持有（F-127）。

## 结果判据

- **票据隔离达成**：端侧任何环节都不持有 `access_token` / `refresh_token`，凭据仅出现在合作方后端（F-127、F-150）。
- **职责边界达成**：硬件只承担输入、呈现与播报；业务编排在后端完成（F-150）。
- **调用链路成立**：后端以 `Authorization: Bearer <access_token>` 调用开放接口，接口只返回该用户资产（F-132）。
- **失效可处置**：后端在收到 401 时按[刷新与撤销票据](04-refresh-and-revoke-credentials.md)续期或引导重新授权（F-155）。

## 限制与边界

- **未实跑声明**：本束**未在本机实跑**——未部署硬件、未搭建后端、未发生任何真实代理调用；步骤与分工均依白皮书（F-127、F-150、F-156）。
- **不建议硬件直连**：白皮书明确**不建议**硬件端直接调用 API，个人票据应保存在合作方后端、由硬件通过后端反向代理调用，以避免凭据泄露与合规风险（F-156）。
- **数据安全边界**：MCP / Connector 类接入按权限范围（scope）逐项最小授权，票据由合作方后端保管，用户可随时撤销；合作方数据仅在用户授权的任务上下文中被调用，具体使用边界**以授权协议与隐私政策为准**（F-158）。
- **身份主键**：多设备 / 多用户场景以 `openid` 作为用户维度主键做数据隔离，同一 `openid` 的助理与任务归属该用户（F-153）；用户身份基于 OAuth 授权的 `openid` 唯一标识（F-074）。
- **口径提示**：接口清单与鉴权细节**以官网开发者文档最新版本为准**（F-113，`以官网为准`）。

> 相关：[OAuth 授权并换取个人票据](01-oauth-authorize-and-exchange-token.md)、[发起任务并读取结果](03-create-task-and-read-result.md)、[端到端演练与常见问题](../concepts/07-end-to-end-walkthrough-and-faq.md)。
