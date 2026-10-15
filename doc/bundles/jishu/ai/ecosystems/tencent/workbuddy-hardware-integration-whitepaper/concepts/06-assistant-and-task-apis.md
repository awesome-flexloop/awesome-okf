---
type: Concept
title: "助理与任务接口：通用规范、scope 与调用方式"
description: "WorkBuddy 开放接口的鉴权与六条通用规范、助理与任务两组端点及其 scope 对应关系，以及本机能力的额外权限与授权方式。"
tags: [WorkBuddy, 智能硬件, 接口调用, scope, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: P0, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json" }
---

# 助理与任务接口：通用规范、scope 与调用方式

本篇回答一个明确问题：拿到个人票据之后，合作方后端怎样合规地调用 WorkBuddy 开放接口——用哪个 Header、守哪些通用约定、助理与任务两组端点各要什么 scope、本机能力如何开启。事实取材白皮书第 9 章（F-132 ~ F-147）。**时效口径先行**：白皮书明示第 7–10 章的接口清单、鉴权方式、示例代码与联调流程均以官网开发者文档的最新版本为准（F-113，`以官网为准`），本篇只是白皮书快照的归纳，不是接口规范的最终解释。

## 鉴权：统一 Header 与「只返回该用户资产」

所有接口调用统一在 HTTP Header 携带 `Authorization: Bearer <access_token>`；接口均以用户身份操作，**只返回该用户的资产**（F-132）。票据代表的是终端用户本人，而不是合作方应用本身；这条边界与「个人票据应保存在合作方 App 后端、不建议下发到硬件端或前端」（F-127）共同构成本束反复强调的安全底座。

## 通用规范（6 条）

| 规范项 | 约定 | 事实 |
| --- | --- | --- |
| Base URL | `https://open.workbuddy.cn/openapi/v2` | F-133 |
| 数据格式 | 请求与响应均为 JSON | F-134 |
| 分页 | 参数 `page` 与 `page_size`，最大 50 | F-135 |
| 错误 | HTTP 状态码 4xx 或 5xx，响应体含 `errcode` 与 `errmsg` | F-136 |
| 幂等 | 写接口支持 `Idempotency-Key` 请求头 | F-137 |
| 限流 | 按 openid 主体限流 | F-138 |

两点实务含义：限流「按 openid 主体」（F-138）意味着配额按终端用户维度计，而非按合作方应用维度计；分页上限 50（F-135）则要求大规模拉取历史任务时自行翻页，不能期望一次取全。

## 助理接口（6 条）

助理是用户拥有的 AI 角色，所有任务调用都需先取得 `asst_id`；cloud 类型助理还需完成一次激活（F-115、F-139）。

| 方法与端点 | 作用 | 事实 |
| --- | --- | --- |
| `POST /assistants` | 创建助理，支持 `location = local / cloud` | F-139 |
| `GET /assistants` | 分页列出当前用户可用助理 | F-139 |
| `GET /assistants/{asst_id}` | 获取助理详情 | F-139 |
| `PATCH /assistants/{asst_id}` | 增量更新，未传字段保持原值 | F-139 |
| `DELETE /assistants/{asst_id}` | 删除助理 | F-139 |
| `POST /assistants/{asst_id}/allocate` | 激活云端（cloud）助理，分配云端执行环境 | F-139 |

所需权限：`assistant.read` 用于读取；`assistant.write` 用于创建、更新、删除与激活（F-140）。scope 的申请与勾选发生在 OAuth 授权前置准备阶段，详见 [授权登录流程](05-oauth2-authorization-flow.md)。

创建云端翻译助理的示例请求体（F-141，字段原样保留）：

```json
{
  "name": "翻译助理",
  "location": "cloud",
  "instruction": "作为简洁高效的中英互译助理，翻译并保持原意"
}
```

## 任务接口（4 条）

任务表示一次针对助理的执行（F-116）。

| 方法与端点 | 作用 | 事实 |
| --- | --- | --- |
| `POST /tasks` | 创建或续接任务 | F-142 |
| `GET /tasks` | 按 `asst_id`、时间等筛选任务列表 | F-142 |
| `GET /tasks/{task_id}` | 获取任务完整回复、工具链与产出物 | F-142 |
| `DELETE /tasks/{task_id}` | 删除任务 | F-142 |

所需权限：`task.read` 用于读取；`task.write` 用于创建与删除（F-143）。

`execution_target` 决定任务在哪里执行：`cloud` 走云端执行环境，`local` 走用户本机 WorkBuddy 客户端（F-118）。创建任务的示例请求体（F-144）：

```json
{
  "asst_id": "asst_xxx",
  "execution_target": "cloud",
  "input": "翻译：hello world"
}
```

## 本机能力：额外 scope 与用户侧授权弹窗

本机能力属**可选**能力，仅在需要本机执行与文件读取的场景启用（F-145）。启用后额外需要两项权限：`local.execute`（本机执行）与 `local.file.read`（本机文件读取）（F-145）。调用方式与云端任务一致，只需把 `execution_target` 设为 `local`（F-146）——也就是说，接口形态不变，仅切换执行位置。

安全上还有一道用户侧的门：本机客户端在首次访问时向用户弹窗确认（可选择一次授权或记住授权），用户可随时在托盘退出授权（F-147）。它与 F-127 的「票据不出后端」纪律共同保证：凭据留在后端，本机能力由用户自行开关。

## 调用顺序与依赖

三组操作存在明确的先后依赖，不能颠倒：所有任务调用都必须先取得 `asst_id`（F-115、F-139），也就是先经 `POST /assistants` 创建助理；若要在云端执行，还需再调 `POST /assistants/{asst_id}/allocate` 完成一次激活、分配云端执行环境（F-139）。由此，典型调用顺序是「建助理 → （按需）激活 → 发任务 → 读结果」；而本机（local）路径不需要 allocate，只需把 `execution_target` 设为 `local`、并依赖用户本机客户端保持在线（F-146）。PATCH 的「增量更新」语义（未传字段保持原值，F-139）则意味着改助理时只提交需要变更的字段即可，无需回传全量对象。

## 收尾提示

本篇端点为白皮书第 9 章快照。白皮书同时声明：完整字段、错误码与示例响应见随册文件 `assistant-openapi.html`（Swagger UI 交互版，本束登记「未取得」，见 [术语与附录](10-glossary-and-appendix.md)），且接口以官网开发者文档最新版本为准（F-113、F-189，`以官网为准`）。照做级演练见 [端到端六步与 FAQ](07-end-to-end-walkthrough-and-faq.md) 与 [示例索引](../examples/index.md)；逐条出处见 [事实登记](../references/article-source.md) 与 [核验报告](../references/verification.md)。
