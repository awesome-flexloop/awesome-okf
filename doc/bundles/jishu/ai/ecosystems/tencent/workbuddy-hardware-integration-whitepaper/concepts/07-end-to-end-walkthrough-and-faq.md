---
type: Concept
title: "端到端演练与常见问题：六步链路、硬件姿势与 FAQ"
description: "从绑定账号到完成任务的白皮书六步端到端流程、硬件端票据不下发的接入姿势，以及十问十答的边界答疑（含 §10 交叉引用勘误）。"
tags: [WorkBuddy, 智能硬件, 端到端, 常见问题, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: P0, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json" }
---

# 端到端演练与常见问题：六步链路、硬件姿势与 FAQ

本篇回答：一个用户从「绑定 WorkBuddy」到「通过翻译助理完成任务」的完整链路怎么走、硬件本体在其中处于什么位置，以及白皮书第 11 章十问给开发者划了哪些边界。事实取材白皮书第 10–11 章（F-148 ~ F-160）。接口口径仍以官网开发者文档最新版本为准（F-113，`以官网为准`）。

## 端到端六步链路

白皮书给出的端到端示例是一个「绑定 WorkBuddy 账号 → 用翻译助理完成翻译」的最小闭环，分六步（F-148）：

1. **用户在合作方 App 点击「绑定 WorkBuddy」**（F-148）：合作方 App 引导浏览器跳转至 WorkBuddy 授权页。
2. **用户完成授权，合作方后端换取个人票据**（F-148）：后端拿 code 换票，返回 `{ "access_token": "...", "openid": "o_xxx", "expires_in": 7200 }`（F-149）。
3. **创建云端助理**（F-148）：`POST /assistants → { "asst_id": "asst_xxx" }`（F-149）。
4. **激活云端助理**（F-148）：`POST /assistants/asst_xxx/allocate → { "status": "ready" }`（F-149）。
5. **发起翻译任务**（F-148）：`POST /tasks`，请求 `{ "asst_id": "asst_xxx", "execution_target": "cloud", "input": "翻译：hello world" }`，返回 `{ "task_id": "task_yyy", "reply": "你好，世界" }`（F-149）。
6. **读取任务详情或历史**（F-148）：`GET /tasks/task_yyy` 取单条详情，`GET /tasks?asst_id=asst_xxx&page=1` 取该助理下的历史任务（F-149）。

上述第 3–5 步的接口与 scope 细节见 [助理与任务接口](06-assistant-and-task-apis.md)，第 1–2 步的授权与换票见 [授权登录流程](05-oauth2-authorization-flow.md)。

### 勘误 E-3：白皮书 §10 第 1 步的内部交叉引用错误

白皮书 §10 第 1 步原文写「合作方 App 按 **6.3 节**所述构造授权链接」，但该白皮书**没有 6.3 节**；授权链接（`GET https://open.workbuddy.cn/oauth/authorize`，参数含 `response_type=code`、`client_id`、`redirect_uri`、`scope`、`state`、`code_challenge`、`code_challenge_method=S256`）的实际位置是 **§8.3**（F-124）。本束按 §8.3 归位，并把该处登记为白皮书的内部交叉引用错误（勘误 E-3），以免读者按错误的节号去找。

## 硬件端的接入姿势

眼镜、耳机、桌宠等硬件本体通过合作方后端间接调用 WorkBuddy API，**个人票据不下发到端侧**；硬件负责语音输入、卡片呈现与语音播报，业务编排由合作方后端完成（F-150）。这与「票据应保存在合作方 App 后端」的纪律一致（F-127）：硬件只是交互末端，真正的凭据与应用逻辑都留在后端。

## 常见问题（十问）

| 问题 | 答复 | 事实 |
| --- | --- | --- |
| 如何判断适合的合作模式？ | 参照第 4 章三个问题（谁进谁、品牌与入口归属、用户与数据归属），答完即可归入四种模式之一 | F-151 |
| 个人票据有效期多久？ | 由 `expires_in` 指定，默认 7200 秒；过期后可用 refresh_token 换新票，用户主动撤销后立即失效 | F-152 |
| 合作方侧如何隔离多用户数据？ | 用响应中的 openid 作为用户维度的存储与查询主键；同一 openid 对应的助理与任务归该用户 | F-153 |
| 本机（local）助理需要激活吗？ | 不需要；allocate 仅适用于 cloud 助理，local 助理依赖用户本机客户端在线运行 | F-154 |
| 接口返回 401 怎么处理？ | 先尝试用 refresh_token 续期；仍返回 401 说明用户已撤销授权或权限发生变化，应引导重新完成 OAuth 授权 | F-155 |
| 硬件端能直接调用 API 吗？ | 不建议；票据应保存在合作方后端，硬件通过后端反向代理调用，以避免凭据泄露与合规风险 | F-156 |
| 本机能力的边界在哪？ | 执行以云端为主；本机能力需 PC 安装 WorkBuddy 桌面客户端（当前覆盖 Mac 与 Windows），可读本机文件、跑本机任务；手机等移动设备暂不支持本机执行 | F-157 |
| MCP / Connector 数据安全如何保障？ | 按 scope 逐项最小授权，票据由合作方后端保管，用户可随时撤销；合作方数据仅在用户授权的任务上下文中被调用，边界以授权协议与隐私政策为准 | F-158 |
| 支持哪些操作系统与平台？ | 桌面客户端当前覆盖 Mac 与 Windows；Linux（含 Ubuntu）桌面版暂未覆盖，可在官网登记，平台按需求量评估排期 | F-159 |
| 推广与分佣机制是怎样的？ | 随商务协议约定，在开放平台提交合作意向后由商务团队一对一对接 | F-160 |

最后一问涉及推广与分佣，属 **`商务框架性参考`**（F-160）：白皮书只给「随协议约定 + 商务一对一对接」的框架，不披露具体比例；商业化分层与结算口径另见 [联合运营与服务水平](09-joint-operations-and-service-levels.md)。

## 本篇要点回顾

- 链路骨架是「授权换票 → 建助理 → 激活 → 发任务 → 读结果」六步（F-148），各步返回值形状见 F-149。
- 票据只留后端、硬件只做输入与呈现（F-150、F-127）。
- 十问覆盖模式选择、票据生命周期、多用户隔离、401 处理、本机边界、平台覆盖与商务机制（F-151 ~ F-160）。
- 注意 §10 的「6.3 节」为白皮书内部交叉引用错误，实际为 §8.3（F-124，勘误 E-3）。

跨篇导航：[OAuth 授权](05-oauth2-authorization-flow.md)、[接口调用](06-assistant-and-task-apis.md)、[示例索引](../examples/index.md)；逐条出处见 [事实登记](../references/article-source.md) 与 [核验报告](../references/verification.md)。
