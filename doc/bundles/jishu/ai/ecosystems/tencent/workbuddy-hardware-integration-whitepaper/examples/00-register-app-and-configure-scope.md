---
type: Example
title: "照做：注册应用并配置 scope"
description: "在 WorkBuddy 开放平台官网完成应用注册、登记回调地址 redirect_uri，并按业务需要勾选最小权限 scope，取得 client_id 与 client_secret，为 OAuth 授权与接口调用做准备。"
tags: [WorkBuddy, 智能硬件, 应用注册, scope, 接入示例, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: P0, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json" }
---

# 照做：注册应用并配置 scope

> 适用场景：你是准备接入 WorkBuddy 的硬件合作方开发者，需要在开放平台建好应用、拿到 `client_id` 与 `client_secret`、登记回调地址并勾选权限，之后才能进入 OAuth 授权与接口调用。开放平台暴露的四类能力与核心概念见[开放平台与核心概念](../concepts/04-open-platform-and-core-concepts.md)，授权流程见 [OAuth 2.0 授权流程](../concepts/05-oauth2-authorization-flow.md)。

## 前置条件

- **开放平台账号与企业实名**：硬件应用接入需先在开放平台注册入驻并完成企业实名认证（营业执照四要素核验；已有腾讯云 / 微信公众号企业实名的可扫码快速认证）（F-167，`准入条件`）。
- **官网入口可达**：官网入口为 <https://open.workbuddy.cn/>，在官网可完成「注册应用、获取凭证、下载对接文档、提交硬件接入意向」（F-114，**本次未核验（O1）**）。
- **回调地址**：事先确定一个 HTTPS 授权回调地址 `redirect_uri` 用于登记（F-121）。
- **能力清单**：明确本次接入要用到的能力（助理、任务、本机能力、积分），据此决定勾选哪些 scope（F-122）。
- **持久化位置**：安排合作方后端存放 `client_secret` 与后续个人票据（F-127）。

## 操作步骤

> 以下步骤**未在本机实跑，依据白皮书（F-114、F-120、F-121、F-122）**；本束未在开放平台注册任何应用、未申请真实凭证。

1. **进入官网**：打开 <https://open.workbuddy.cn/>，在开放平台完成注册应用、获取凭证、下载对接文档与提交硬件接入意向等操作（F-114，**未核验（O1）**）。〔**未在本机实跑，依据白皮书 F-114**〕
2. **注册应用**：在开放平台注册应用，取得 `client_id` 与 `client_secret`（F-120）。〔**未在本机实跑，依据白皮书 F-120**〕
3. **登记回调地址**：登记授权回调地址 `redirect_uri`（F-121）。〔**未在本机实跑，依据白皮书 F-121**〕
4. **勾选 scope**：按业务需要勾选权限范围（F-122）——基础四项为 `assistant.read`、`assistant.write`、`task.read`、`task.write`；如需本机能力再加 `local.execute` 与 `local.file.read`；如需积分再加 `credit.read`（F-122）。〔**未在本机实跑，依据白皮书 F-122**〕
5. **保密与登记**：把 `client_id` / `client_secret` 与 `redirect_uri` 登记到合作方后端配置，`client_secret` 不下发端侧（F-127）。〔**未在本机实跑，依据白皮书 F-120、F-127**〕

**凭证与回调地址登记示例**（值均为占位符，非真实凭证）：

```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "redirect_uri": "https://yourapp.example.com/callback"
}
```

**scope 勾选清单**（按需勾选，未勾选的能力对应接口将不可用）（F-122）：

```text
assistant.read     # 读取助理
assistant.write    # 创建 / 更新 / 删除 / 激活助理
task.read          # 读取任务与结果
task.write         # 创建 / 删除任务
local.execute      # 本机执行（仅在需要本机能力时勾选）
local.file.read    # 本机文件读取（仅在需要本机能力时勾选）
credit.read        # 积分（仅在需要积分时勾选）
```

## 结果判据

- **应用创建成功**：取得 `client_id` 与 `client_secret`（F-120）。白皮书**未给出**后台页面字段名与提示文案，实际操作以官网后台显示为准（F-113）。
- **回调地址生效**：`redirect_uri` 已登记，后续 OAuth 授权回调将回到该地址（F-121、F-123）。
- **权限就绪**：勾选的 scope 与后续调用接口一一对应——助理接口需 `assistant.read` / `assistant.write`（F-140），任务接口需 `task.read` / `task.write`（F-143），本机能力另需 `local.execute` / `local.file.read`（F-122、F-145）。
- **口径提示**：第 7～10 章所述全部接口清单、鉴权方式、示例代码与联调流程**均以官网开发者文档的最新版本为准**（F-113，`以官网为准`）。

## 限制与边界

- **未实跑声明**：本束**未在本机实跑**——未注册开放平台账号、未申请真实 `client_id` / `client_secret`、未登记任何真实回调地址；上述步骤均为白皮书转述（F-114、F-120、F-121、F-122）。
- **官网入口状态**：<https://open.workbuddy.cn/> 为白皮书指定入口，本束**未核验（O1）**，其页面结构与操作路径**以官网为准**（F-114）。
- **最小授权原则**：scope 应按能力**逐项最小授权**，票据由合作方后端保管、用户可随时撤销（F-158）；不要为图省事一次性勾选全部权限。
- **凭证不外泄**：`client_secret` 与个人票据应保存在合作方后端，**不建议下发到硬件端或前端**（F-127、F-156）。
- **准入前置**：企业实名认证、硬件量产或明确量产计划、数据安全与隐私保障能力及协议签署，是后续接入审核的条件（F-167、F-168、F-169）——详见[自助接入与审核](06-self-service-onboarding-and-review.md)。

> 下一步：[OAuth 授权并换取个人票据](01-oauth-authorize-and-exchange-token.md)；权限与接口的对应关系见[助理与任务接口](../concepts/06-assistant-and-task-apis.md)。
