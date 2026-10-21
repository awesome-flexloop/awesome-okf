---
okf_version: "0.2"
type: concept
title: 接入实操与八问排障（API / WorkBuddy）
description: 免费调用资格三检、OpenAI 兼容 API 直连、腾讯 WorkBuddy 五步配置、官方 Q&A 八问排障对照表，以及泛化到任意 OpenAI 兼容编程工具的接入法
tags: [unisound, u2-flash, openai-compatible, anthropic-compatible, workbuddy, troubleshooting, access-key, maas]
generated:
  by: trae-seven-concepts-cmd
  at: "2026-10-21T17:30:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-21T18:00:00+08:00"
status: stable
stale_after: 2026-11-15
sources:
  - id: model-hub
    url: https://maas.unisound.com/model-hub/u2-flash
  - id: workbuddy-doc
    url: https://maas.unisound.com/docs/toolAI/workbuddy
  - id: feishu-qa
    url: https://kcn0mpv7063o.feishu.cn/wiki/MVgSwGLRXi6VDik9nLHciUSunZc
  - id: workbuddy-official
    url: https://workbuddy.ai/
---

# 接入实操与八问排障

> 本篇为**操作层（How）**：内容汇编自官方模型页、官方 WorkBuddy 教程与官方 Q&A（rev.490），**非作者一手实测**；字段值、URL 均逐字取自官方页面（F 编号可溯源）。随官方文档迭代，字段名称可能微调。
> 凭证、密钥属敏感信息：本篇所有 Key 均以占位符表示，请勿把真实 Key 提交进仓库或贴入社群。

## 一、资格三检（动手前 3 分钟）

按官方 Q&A，绝大多数"调不通"在这三步即可定位（F-018/F-019/F-022）：

1. **实名认证**：电脑端登录 https://maas.unisound.com/admin/account/verify 完成实名认证。**手机端暂不支持调用模型**（F-018）。
2. **余额非负**：打开控制台-账户总览（资产总览）。余额为负时 U2Flash 被锁——典型成因是新用户用赠送的**其他模型资源包**调了其他模型产生欠费；少量充值结清欠费即可恢复（F-020）。免费期也要查这一项。
3. **模型名逐字**：`u2-flash`，全小写、中划线。拼写错误同样报 `model_not_found`。

> 建议：免费期内不要在该账户上随意调用其他模型，避免"送的资源包用超 → 欠费 → 免费模型反被锁"（F-020，本活动最反直觉的坑）。

## 二、凭证选择：用哪个 Key

| Key 形态 | 来源 | 免费期建议 |
|----------|------|------------|
| `sk-xxxxx` | 控制台 API Key 管理页创建，对应按量付费/资源包（F-014） | **优先使用**：活动价三档为 ¥0，无需订阅即可零元调用（依据 F-003/F-014 的组合推断，官方未逐字写明"免费期必须用 sk-"） |
| `tp-xxxxx` | 订阅管理页购买 Token Plan 后获取（F-014） | 仅在你已订阅 Token Plan 时使用；免费月无需为调用 U2Flash 新购订阅 |

> V6 留存项：Anthropic 兼容端点（`/anthropic`，F-009）在 WorkBuddy 中的具体配置字段官方教程**未给示例**，接入时按工具的 Anthropic 自定义提供商表单自行尝试；本篇不臆造字段。

## 三、API 直连（OpenAI 兼容）

官方示例结构（F-010）：

```bash
curl https://maas-api.unisound.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $UNISOUND_API_KEY" \
  -d '{
    "model": "u2-flash",
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }'
```

- Base URL（给 SDK 用）：`https://maas-api.unisound.com/v1`（F-009）。
- 因接口为 OpenAI 兼容协议，OpenAI Python/Node SDK 设置 `base_url` 与 `api_key` 后即可调用；模型名传 `u2-flash`。
- 也可直接在平台 Playground（`/playground/text?modelId=u2-flash`）先验证账户可用性，再配置工具（F-027）。

## 四、WorkBuddy 五步配置（官方教程）

WorkBuddy 是**腾讯**出品的 AI 工作平台（官网自述 "an all-in-one AI workspace from Tencent"，F-013；与本库 [WorkBuddy 官方文档束](../../../ecosystems/tencent/workbuddy-official-docs/index.md) 同一产品），云知声在其自定义模型生态中是供应商之一。

1. **下载安装**：从 https://workbuddy.ai 获取 Mac ARM64 / Mac x64 / Windows 客户端（也有在线版）（F-012）。
2. **打开自定义模型**：模型设置中选择添加/编辑自定义供应商（提供商选"自定义/Custom"）。
3. **填四字段**（F-015，官方教程截图口径）：
   - 接口地址（API Endpoint）：`https://maas-api.unisound.com/v1/chat/completions`
   - API Key：填你的 `sk-` Key
   - 模型名称：`u2-flash`
   - 供应商：自定义 / Custom
4. **高级开关**（F-016）：按 U2Flash 的模型参数说明勾选"工具调用""图片输入""推理模式（思考开关）"。
5. **保存并对话验证**；失败先走第六节排障表，再考虑升级到最新版 WorkBuddy（F-021）。

配置成功后，还可在 WorkBuddy 中安装平台预置的 U2-ASR、U2-TTS、U2-TTS-Clone、U1-OCR（含医疗版）等 Skill（F-017）。

### Base URL 两种写法（勘误 E-2，不是配错）

| 写法 | 出处 | 适用 |
|------|------|------|
| `https://maas-api.unisound.com/v1` | 官方模型页（F-009） | 要求填 **base URL** 的工具/SDK |
| `https://maas-api.unisound.com/v1/chat/completions` | 官方 WorkBuddy 教程页（F-015） | 要求填**完整请求 URL** 的工具 |

官方 Q&A 明确：调不通时把两种样式**互换尝试**（F-021）。

## 五、泛化：接入"所有主流编程工具"

公告称可接入 WorkBuddy 在内的所有主流编程工具（F-001），其技术基础是 U2Flash 提供 **OpenAI / Anthropic 双兼容协议**（F-009）。因此任何支持"自定义 OpenAI 兼容端点"的编程工具（各类 AI IDE、命令行 Agent、网关）都可按下表同法接入（F-030）：

| 工具侧字段 | 填入值 |
|------------|--------|
| Provider/供应商 | OpenAI Compatible / 自定义 |
| Base URL | `https://maas-api.unisound.com/v1`（若工具要求完整 URL 则追加 `/chat/completions`） |
| API Key | 控制台创建的 `sk-` Key |
| Model | `u2-flash` |

## 六、官方 Q&A 八问排障对照表

| # | 现象 | 官方口径（Q&A rev.490） | 依据 |
|---|------|--------------------------|------|
| 1 | 在哪"领取"免费？ | 无需领取：电脑端完成实名认证后按公告接入即可，手机端暂不支持 | F-018 |
| 2 | `the model u2-flash does not exist or you do not have access to it` | 查控制台-账户总览，**余额为负则无法调用**，保证余额非负 | F-019 |
| 3 | 为什么余额会变负？ | 新用户赠送其他模型资源包，调用其他模型导致欠费；少量充值清欠即可 | F-020 |
| 4 | 已认证、余额非负，WorkBuddy 仍调不通 | ① WorkBuddy 升至最新版；② 两种 Base URL 互换 | F-021 |
| 5 | 免费了为什么还扣"额度"？ | 先扣此前领取的 1 亿存量 token，扣完才走免费额度 | F-023 |
| 6 | 怎么获得 5 亿 token？ | 填群公告问卷（问卷星），活动结束后发到所填手机号 | F-025 |
| 7 | 5 亿 token 全模型通用吗？ | **仅限 U2-Flash 单模型** | F-026 |
| 8 | 404 `model_not_found` | 两个原因：未实名认证 / 余额为负 | F-022 |

**问卷隐私提示（V4）**：第 6/7 问的问卷需留手机号，属厂商营销留资，建议使用副号/小号填写；5 亿 token 为厂商活动承诺，范围、时点与价值边界见 [02 篇](02-token-economics-and-funnel.md)。

---

**上一篇**：[00 · 活动事实与模型规格](00-free-month-event.md) ｜ **下一篇**：[02 · 计费机制、免费漏斗与限免淘金法](02-token-economics-and-funnel.md)
