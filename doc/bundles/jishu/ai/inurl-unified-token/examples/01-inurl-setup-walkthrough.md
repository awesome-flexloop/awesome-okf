---
type: Example
title: "inurl 免费档接入配置演练（Cursor 视角）"
description: "依据官方 /guide 的五步流程整理的本地代理接入演练：注册、密钥库、本地代理、Cursor 三参数、对话验证与排障；含免费档 3 密钥约束与闭源代理安全操作清单。"
tags: [接入演练, Cursor, localhost:3003, 免费档, 风险操作清单]
sources:
  - id: product-guide
    resource: https://token.inurl.link/guide
    title: "inurl 官方使用图文教程（步骤来源）"
  - id: product-app
    resource: https://token.inurl.link/app
    title: "inurl 注册/控制台"
  - id: verification
    resource: /references/verification.md
    title: "本束 P0 核验报告"
---

# inurl 免费档接入配置演练（Cursor 视角）

> **⚠️ 阅读前提（flagged 信源警示）**
>
> 1. 本篇步骤整理自产品**官方教程**与博文描述，本束生产者**未注册、未运行该代理**，不构成推荐；
> 2. 免费档（¥0）**只允许录入 3 个厂商密钥**——博文「17 家 + 0 元」不成立（勘误 E1，F-070）；
> 3. 本地代理闭源、运行时下载、启动器内嵌令牌与主密钥（F-053）；运营主体匿名（F-056）。**只建议录入低额度、可随时作废的免费 Key**；
> 4. 页面/接口状态以 2026-09-16 实测为准（F-044/F-047），实际界面可能已变化。

## 1. 前置条件

- 已持有至少 1 个免费模型厂商的 API Key（推荐从「限速不限量/免费档稳定」的厂商起步，如智谱 BigModel、Groq、百度千帆 ERNIE 免费模型，额度现状见 [/concepts/01-free-model-landscape.md](/concepts/01-free-model-landscape.md)）；
- 本机有 Node.js（手动启动方式需要；一键启动器为 Windows `byok-launch.bat`）；
- 客户端支持自定义 OpenAI 兼容端点（Cursor、OpenWebUI、WorkBuddy 等；WorkBuddy 是**第三方**客户端，非该产品组件，F-055）。

## 2. 五步流程（对应官方教程）

1. **注册账户**：打开 `https://token.inurl.link/app`，邮箱 + 密码（注册表单含选填邀请码；Cloudflare 人机验证组件已集成但实测当日处于关闭状态，F-054）；
2. **离线保存两类凭证**：注册成功页只显示一次——🔑 **统一令牌（Unified Token）**（登录 + 本地代理凭证）与 🛡️ **恢复密语（Recovery Secret）**（忘密码时恢复密钥库）。站点声称端到端加密、云端无明文、无法代为找回（F-023，前端双份 escrow 实现经核验属实，F-052）；
3. **录入厂商 Key**：在控制台密钥库添加厂商密钥（浏览器端经 PBKDF2 派生 AES-GCM-256 加密后上传，云端只存密文，F-052）。**免费档最多 3 个厂商**；
4. **启动本地代理**：下载并运行 `byok-launch.bat`（或手动 `AGENT_TOKEN=你的令牌 AGENT_MASTERKEY=你的主密钥 node local-agent.js`，F-047）；控制台会轮询本机 `/v1/metrics` 显示代理状态；
5. **客户端填入三参数**（以 Cursor 为例，F-028）：
   - Base URL：`http://localhost:3003/v1`
   - API Key：统一令牌
   - Model：`inurl-code`（代码）／`inurl`（日常文本）／`inurl-image`（画图）

## 3. 逻辑模型名速查

| Model 填什么 | 路由行为 |
|--------------|---------|
| `inurl` / `inurl-text` | 文本对话默认池（旧名 `auto` 仍兼容） |
| `inurl-code` | 仅在带代码能力标签、且你已录入 Key 的厂商间选 |
| `inurl-image` / `inurl-video` / `inurl-audio` | 对应多模态厂商 |

- 故障切换：厂商返回 429/5xx 自动切下一家（F-048）；切换耗时「0.1 秒」为博文自述、未证实（F-025）；
- 想限定池：设环境变量 `AUTO_MODELS` / `AUTO_PROVIDER_ORDER`；
- **注意路由结果与免费的关系**：目录中 `deepseek/*` 属付费 19 家（F-050），代理能调通不代表免费——是否计费由对应厂商账户决定。

## 4. 验证与排障

| 现象 | 含义（官方教程/前端逻辑） | 处理 |
|------|--------------------------|------|
| 浏览器访问 `http://localhost:3003/v1/models` 能返回模型 JSON | 代理在跑且 OpenAI 兼容层正常（F-047） | — |
| 客户端报 401「令牌失效」 | 统一令牌错误或过期 | 重新核对/在控制台重建 |
| 控制台提示「本地代理版本过旧（缺少 /v1/metrics）」 | 代理版本落后于控制台 | 重新运行新版 `byok-launch.bat` |
| 某模型 429 | 对应厂商免费档限流（如智谱约 1 并发，F-058） | 等待窗口，或扩充已录入的免费厂商池（受 3 个上限约束） |
| 模型不在池内 | 路由只在**已录入 Key** 的厂商间进行（F-049） | 先在密钥库添加对应厂商 |

## 5. 安全操作清单（强烈建议逐条遵守）

- [ ] 只录入**免费、低额度、可随时吊销重置**的厂商 Key；付费大额 Key 不入该库（F-053）；
- [ ] 运行 `byok-launch.bat` / `local-agent.js` 前，先用文本编辑器通读脚本，确认无异常外发行为；
- [ ] 统一令牌与恢复密语离线保存（密码管理器），二者任一泄露都可能使密钥库被离线恢复；
- [ ] 不向其发送敏感代码、私域文档与隐私数据（免费通道/聚合层的数据策略不可控）；
- [ ] 定期在各厂商控制台检查 Key 的用量日志，发现异常立即吊销；
- [ ] 若不能接受闭源代理，改用开源等价方案自建（LiteLLM、one-api/new-api 等 OpenAI 兼容网关），架构模式见 [/concepts/02-byok-unified-architecture.md](/concepts/02-byok-unified-architecture.md)。
