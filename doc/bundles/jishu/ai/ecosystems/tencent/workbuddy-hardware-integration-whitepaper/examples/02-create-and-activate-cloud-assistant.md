---
type: Example
title: "照做：创建并激活云端助理"
description: "携带个人票据调用助理接口，创建 location=cloud 的云端助理并取得 asst_id，再调用 allocate 激活接口分配云端执行环境；同时区分 cloud 与 local 两种助理的激活差异。"
tags: [WorkBuddy, 智能硬件, Assistant, allocate, scope, 接入示例, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: P0, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json" }
---

# 照做：创建并激活云端助理

> 适用场景：拿到个人票据后，你需要先有一个**助理**作为任务的执行主体。所有任务调用都要先获得 `asst_id`；`cloud` 类型助理还需完成一次激活。助理与任务接口全貌见[助理与任务接口](../concepts/06-assistant-and-task-apis.md)。

## 前置条件

- **个人票据**：已完成 [OAuth 授权换票](01-oauth-authorize-and-exchange-token.md)，持有 `access_token`；所有请求在 Header 携带 `Authorization: Bearer <access_token>`（F-132）。
- **Base URL**：`https://open.workbuddy.cn/openapi/v2`（F-133）；请求与响应均为 JSON（F-134）。
- **权限 scope**：创建、更新、删除与激活需 `assistant.write`；读取需 `assistant.read`（F-140）。
- **助理定义**：明确 `name`（名称）、`location`（`cloud` 云端 / `local` 本机端）与 `instruction`（角色指令）等参数（F-115、F-139）。

## 操作步骤

> 以下步骤**未在本机实跑，依据白皮书（F-139、F-140、F-141）**；本束未创建任何真实助理。

1. **创建助理**：`POST /assistants`，支持 `location = local / cloud`（F-139）。〔**未在本机实跑，依据白皮书 F-139、F-141**〕
2. **取得 asst_id**：创建成功后返回 `asst_id`，后续任务调用都要用到它（F-139、F-118）。〔**未在本机实跑，依据白皮书 F-139**〕
3. **按需读取与维护**：`GET /assistants` 分页列出可用助理、`GET /assistants/{asst_id}` 获取详情、`PATCH /assistants/{asst_id}` 增量更新（未传字段保持原值）、`DELETE /assistants/{asst_id}` 删除（F-139）。〔**未在本机实跑，依据白皮书 F-139**〕
4. **激活云端助理**：`POST /assistants/{asst_id}/allocate` 激活云端（cloud）助理，分配云端执行环境（F-139）。〔**未在本机实跑，依据白皮书 F-139**〕

### 示例：创建云端翻译助理

```http
POST https://open.workbuddy.cn/openapi/v2/assistants
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "翻译助理",
  "location": "cloud",
  "instruction": "作为简洁高效的中英互译助理，翻译并保持原意"
}
```

请求体字段取自白皮书示例（F-141）；端点取自助理接口清单（F-139），Base URL 见通用规范（F-133）。

### 示例：激活云端助理

```http
POST https://open.workbuddy.cn/openapi/v2/assistants/asst_xxx/allocate
Authorization: Bearer <access_token>
```

端点 `POST /assistants/{asst_id}/allocate`（F-139）；`asst_xxx` 为占位符，请替换为第 2 步返回的真实 `asst_id`。

## 结果判据

- **创建成功**：响应返回 `asst_id`（F-139、F-118）——白皮书未给出完整响应体，字段以官网开发者文档为准（F-113、F-189）。
- **激活成功**：`POST /assistants/asst_xxx/allocate` 返回 `{"status": "ready"}`（F-148），表示云端执行环境已就绪。
- **写入类接口幂等**：写接口支持 `Idempotency-Key` 请求头（F-137），重试创建时可避免重复助理。
- **列表可读**：`GET /assistants` 为分页接口，采用 `page` 与 `page_size`（最大 50）（F-135）。

## 限制与边界

- **未实跑声明**：本束**未在本机实跑**——未创建真实助理、未调用真实 allocate 接口；端点、参数名与示例请求体均依白皮书（F-139、F-140、F-141）。
- **local 助理不需要激活**：`allocate` 仅适用于云端（`cloud`）助理；本机（`local`）助理依赖用户本机 WorkBuddy 客户端在线运行（F-154）。对 local 助理调用 allocate 属于误用。
- **scope 对应**：缺少 `assistant.write` 时，创建 / 更新 / 删除 / 激活均会失败；只读场景勾选 `assistant.read` 即可（F-140）。
- **本机能力边界**：本机能力为可选能力，需用户 PC 安装 WorkBuddy 桌面客户端（当前覆盖 Mac 与 Windows）（F-145、F-157）；相关参数与调用见[发起任务并读取结果](03-create-task-and-read-result.md)。
- **口径提示**：助理接口的完整字段、错误码与示例响应见随册 Swagger 文件，本束未取得该文件（F-189，`未取得`）；接口清单**以官网开发者文档最新版本为准**（F-113，`以官网为准`）。

> 下一步：[发起任务并读取结果](03-create-task-and-read-result.md)；云端与本机的执行位置概念见[开放平台与核心概念](../concepts/04-open-platform-and-core-concepts.md)。
