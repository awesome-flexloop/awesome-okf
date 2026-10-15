---
type: Example
title: "照做：发起任务并读取结果"
description: "用 asst_id 与 execution_target 通过任务接口发起一次执行，读取回复、工具链与产出物，并分页查询历史任务；同时说明 execution_target 切换云端与本机的差异。"
tags: [WorkBuddy, 智能硬件, Task, execution_target, 本机能力, 接入示例, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: P0, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json" }
---

# 照做：发起任务并读取结果

> 适用场景：助理已就绪，你要让它真正干活——发起一次任务、取回回复与产出物，并在后续会话里续接。Task 表示对指定助理发起的一次执行，返回回复内容、工具链、产出物与状态（F-116）。完整接口与 scope 对应见[助理与任务接口](../concepts/06-assistant-and-task-apis.md)。

## 前置条件

- **个人票据**：持有 `access_token`，并已在 Header 携带 `Authorization: Bearer <access_token>`（F-132）。
- **asst_id**：已完成[创建并激活云端助理](02-create-and-activate-cloud-assistant.md)，取得 `asst_id`（F-118、F-139）。
- **权限 scope**：创建与删除任务需 `task.write`；读取需 `task.read`（F-143）。
- **执行位置**：明确 `execution_target`——`cloud` 走云端执行环境，`local` 走用户本机 WorkBuddy 客户端（F-118、F-142）。
- **本机能力前置**（仅当 `execution_target=local`）：用户 PC 需安装 WorkBuddy 桌面客户端（当前覆盖 Mac 与 Windows），并勾选 `local.execute` 与 `local.file.read`；首次访问时客户端会向用户弹窗确认授权（F-145、F-147、F-157）。

## 操作步骤

> 以下步骤**未在本机实跑，依据白皮书（F-142、F-143、F-144、F-149）**；本束未发起任何真实任务。

1. **创建或续接任务**：`POST /tasks` 创建或续接任务（F-142）。〔**未在本机实跑，依据白皮书 F-142、F-144**〕
2. **读取单条任务详情**：`GET /tasks/{task_id}` 获取任务完整回复、工具链与产出物（F-142）。〔**未在本机实跑，依据白皮书 F-142、F-149**〕
3. **查询历史任务**：`GET /tasks` 按 `asst_id`、时间等筛选任务列表（F-142、F-149）。〔**未在本机实跑，依据白皮书 F-142、F-149**〕
4. **删除任务**：`DELETE /tasks/{task_id}` 删除任务（F-142）。〔**未在本机实跑，依据白皮书 F-142**〕

### 示例：创建翻译任务

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

请求体字段 `asst_id`、`execution_target`、`input` 取自白皮书示例（F-144）；端点见任务接口清单（F-142），Base URL 见通用规范（F-133）。`asst_xxx` 为占位符。

### 示例：读取任务详情与历史

```http
GET https://open.workbuddy.cn/openapi/v2/tasks/task_yyy
Authorization: Bearer <access_token>
```

```http
GET https://open.workbuddy.cn/openapi/v2/tasks?asst_id=asst_xxx&page=1
Authorization: Bearer <access_token>
```

端点与查询参数取自白皮书端到端示例（F-142、F-149）；分页参数 `page` 与 `page_size` 最大 50（F-135）。

## 结果判据

- **创建成功**：响应返回 `task_id`，可用于后续读取（F-142、F-149）；白皮书端到端示例给出 `{"task_id": "task_yyy", "reply": "你好，世界"}` 结构（F-149，**值为示例占位符**）。
- **换票与任务返回值对照**：端到端示例中，换票返回 `{access_token, openid, expires_in: 7200}`，任务返回 `{task_id, reply}`，历史查询为 `GET /tasks?asst_id=asst_xxx&page=1`（F-149）。
- **详情可读**：`GET /tasks/{task_id}` 返回完整回复、工具链与产出物（F-142、F-116）。
- **写入幂等**：写接口支持 `Idempotency-Key` 请求头（F-137）；限流按 `openid` 主体限流（F-138）。

## 限制与边界

- **未实跑声明**：本束**未在本机实跑**——未创建真实任务、未读取任何真实回复；端点、字段名与示例值均依白皮书（F-142、F-143、F-144、F-149）。
- **本机能力边界**：任务执行以**云端为主**；本机能力需用户 PC 安装 WorkBuddy 桌面客户端（当前覆盖 Mac 与 Windows），可读取本机文件、运行本机任务；**手机等移动设备暂不支持本机执行**（F-157）。Linux（含 Ubuntu）桌面版暂未覆盖（F-159）。
- **local 与云端调用方式一致**：本机能力调用方式与云端任务一致，只需将 `execution_target` 设为 `local`（F-146）；并不需要为 local 助理做 allocate（F-154）。
- **scope 对应**：缺少 `task.write` 无法创建 / 删除任务，缺少 `task.read` 无法读取（F-143）。
- **口径提示**：任务接口的完整字段、错误码与响应示例见随册 Swagger 文件，本束未取得该文件（F-189，`未取得`）；接口清单**以官网开发者文档最新版本为准**（F-113，`以官网为准`）。

> 下一步：[刷新与撤销票据](04-refresh-and-revoke-credentials.md)；端到端全流程见[端到端演练与常见问题](../concepts/07-end-to-end-walkthrough-and-faq.md)。
