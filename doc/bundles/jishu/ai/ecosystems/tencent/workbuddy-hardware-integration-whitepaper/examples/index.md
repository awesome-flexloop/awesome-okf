# 操作用例

本目录收录本束的 7 篇操作演练，覆盖从「注册应用并配置权限」到「上架审核」的可照做接入链路，对应白皮书第三部分（§7–§10）与 §12 提供的技术接入与落地流程。所有步骤均转述白皮书描述，**本束未在本机实跑**——未在 WorkBuddy 开放平台注册应用、未申请真实 `client_id` / `client_secret`、未调用任何真实接口、未提交任何真实上架审核；示例中的凭据与响应值一律为占位符。

> 阅读前提：开放平台四类能力与核心概念见[开放平台与核心概念](../concepts/04-open-platform-and-core-concepts.md)，OAuth 2.0 授权机制见 [OAuth 2.0 授权流程](../concepts/05-oauth2-authorization-flow.md)；文中出现的端点、参数名、scope 名与字段名均可回溯 F 编号，见[事实登记](../references/article-source.md)。官网入口 <https://open.workbuddy.cn/> 本束**未核验（O1）**；接口清单、鉴权方式与示例代码**均以官网开发者文档最新版本为准**（F-113）。

## 场景导览

| 场景 | 一句话说明 | 适用读者 |
|---|---|---|
| [00 注册应用并配置 scope](00-register-app-and-configure-scope.md) | 在开放平台注册应用、登记 `redirect_uri` 并按业务勾选最小权限 scope，取得 `client_id` / `client_secret` | 准备接入、需先拿到应用凭证的开发者 |
| [01 OAuth 授权并换取个人票据](01-oauth-authorize-and-exchange-token.md) | 走 OAuth 2.0 授权码 + PKCE：跳转授权页 → 回调取 `code` → 后端换 `access_token` / `refresh_token` / `openid` | 负责账号绑定与后端换票的开发者 |
| [02 创建并激活云端助理](02-create-and-activate-cloud-assistant.md) | `POST /assistants` 创建 `cloud` 助理取得 `asst_id`，再 `allocate` 激活云端执行环境 | 负责助理生命周期管理的开发者 |
| [03 发起任务并读取结果](03-create-task-and-read-result.md) | 用 `asst_id` 与 `execution_target` 发起任务，读取回复与产出物，分页查询历史 | 负责任务调用与结果呈现的开发者 |
| [04 刷新与撤销个人票据](04-refresh-and-revoke-credentials.md) | `expires_in` 默认 7200 秒，用 `refresh_token` 续期；说明用户撤销 / 主动撤销两条路径与 401 处置 | 负责凭据生命周期与多用户隔离的开发者 |
| [05 硬件后端的反向代理姿势](05-hardware-backend-proxy-pattern.md) | 硬件本体不持有票据，由合作方后端代理调用 API，硬件只做输入 / 呈现 / 播报 | 硬件端与服务端架构负责人 |
| [06 自助接入与上架审核](06-self-service-onboarding-and-review.md) | 两条落地路径、三阶段样板节奏（PoC / MVP / GA）、准入审核与品牌使用分档 | 项目负责人、PMO 与合规 / 运营负责人 |

```{toctree}
:hidden:
:maxdepth: 1

00-register-app-and-configure-scope
01-oauth-authorize-and-exchange-token
02-create-and-activate-cloud-assistant
03-create-task-and-read-result
04-refresh-and-revoke-credentials
05-hardware-backend-proxy-pattern
06-self-service-onboarding-and-review
```
