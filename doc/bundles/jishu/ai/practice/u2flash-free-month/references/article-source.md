---
okf_version: "0.2"
type: reference
title: 信源事实清单（云知声 U2Flash 免费月活动）
description: 群公告、官方模型页、官方 WorkBuddy 接入教程与官方飞书 Q&A 的 F-001 至 F-030 事实采集与核验登记，含信源距离预判与勘误标注
tags: [unisound, u2-flash, free-month, facts, maas, workbuddy]
generated:
  by: trae-seven-concepts-cmd
  at: "2026-10-21T17:30:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-21T18:00:00+08:00"
status: stable
stale_after: 2026-11-15
sources:
  - id: group-announcement
    resource: 云知声 U2Flash 用户社群群公告文本（2026-10-21 采集，无公开 URL）
  - id: model-hub
    url: https://maas.unisound.com/model-hub/u2-flash
  - id: workbuddy-doc
    url: https://maas.unisound.com/docs/toolAI/workbuddy
  - id: feishu-qa
    url: https://kcn0mpv7063o.feishu.cn/wiki/MVgSwGLRXi6VDik9nLHciUSunZc
  - id: workbuddy-official
    url: https://workbuddy.ai/
  - id: questionnaire
    url: https://v.wjx.cn/vm/rFQdEcw.aspx
---

# 信源事实清单（云知声 U2Flash 免费月）

> **目标信源**：云知声用户社群"免费月"群公告（2026-09-30 前后发布，2026-10-21 采集）
> **信源构成**：S1 社群群公告原文（厂商营销文案，无公开 URL）；S2 官方模型页；S3 官方 WorkBuddy 接入教程；S4 官方飞书《问题Q&A》（抓取时 revision_id=490）；S5 WorkBuddy 官网（实体归属核验）
> **采集时间**：2026-10-21（S2/S3/S5 经 WebFetch 取证，S4 经 lark-cli 读取全文）
> **信源距离预判**：S1 为**厂商自宣营销文案**（"无限制，无限量""5 亿 token"默认 P0）；S2/S3/S4 为云知声**官方一手信源**，是价格、规格、限流、端点、排障口径的权威源；S5 用于核验 WorkBuddy 出品方
> **核验方式**：P0 声明逐项与官方页面对表；同一官方族内多文档口径差异单列勘误；无第三方信源可佐证的赠品承诺标"厂商自述"。详见 [verification.md](verification.md)

---

## 完整 F 编号清单（F-001 至 F-030，连续无跳号）

### A. 信源与活动主体

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|----------|------|----------|
| F-001 | 群公告称 9.30–10.31 期间 U2Flash 全量免费，文案"无限制，无限量！畅开蹬！"，"一键领取"链接指向模型页 maas.unisound.com/model-hub/u2-flash（S1） | P0 | ✅ 活动事实与 S2 一致；"无限量"口径见 F-028 |
| F-002 | 官方模型页标注"限时免费·活动期间新老用户均免费调用"，横幅活动时间 2026.09.30–2026.10.31（S2） | P0 | ✅ 官方页直接取证 |
| F-003 | 活动价：输入 ¥0/M tokens（原价 ¥1）、缓存命中 ¥0/M（原价 ¥0.2）、输出 ¥0/M（原价 ¥2），原价均为划线价（S2） | P0 | ✅ 官方定价表 |
| F-004 | 模型 ID `u2-flash`，作者云知声；模型页页面更新时间 2026-09-14（S2） | P1 | ✅ 官方页 |
| F-005 | 官方定位（厂商自述）：聚焦 Agent 与 Coding 场景，支持复杂推理、代码生成、任务执行、长上下文，面向复杂工程开发/长程任务/多步 Agent 工作流（S2） | P1 | ⚠️ 厂商自述，无第三方评测佐证 |
| F-006 | 《问题Q&A》为 kcn0mpv7063o 域飞书 wiki，2026-10-21 抓取时 revision_id=490，处于高频迭代（S4） | P2 | ✅ 官方文档元数据 |

### B. 价格、规格与限流

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|----------|------|----------|
| F-007 | 规格：最大输入 512K tokens、上下文 512K tokens、最大输出 128K tokens（S2） | P0 | ✅ 官方参数卡 |
| F-008 | 限流：RPM 100；TPM 10,000,000（S2） | P0 | ✅ 官方参数卡 |
| F-009 | 双协议端点：OpenAI 兼容 `https://maas-api.unisound.com/v1`；Anthropic 兼容 `https://maas-api.unisound.com/anthropic`（S2） | P0 | ✅ 官方模型页 |
| F-010 | 官方调用示例：`POST {base_url}/v1/chat/completions`，Header `Authorization: Bearer <api_key>`，请求体 `model: u2-flash` 的 OpenAI Chat 结构（S2） | P0 | ✅ 官方代码示例 |
| F-011 | 两条计费/凭证路径：按量付费与模型资源包（`sk-` Key）、Token Plan 订阅（`tp-` Key）；控制台设订阅管理与 Token Plan 页（S2/S3） | P1 | ✅ 官方双源 |

### C. 接入凭证与工具侧

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|----------|------|----------|
| F-012 | WorkBuddy 官网 workbuddy.ai 提供 Mac ARM64、Mac x64、Windows 客户端与在线版入口（S3） | P1 | ✅ 官方教程页 |
| F-013 | WorkBuddy 官网自述 "an all-in-one AI workspace from Tencent"，与本库 ecosystems/tencent 下 WorkBuddy 各束为同一产品；云知声在该关系中为模型供应商侧（S5） | P0 | ✅ 官网直接取证 |
| F-014 | 两类凭证：按量 Key 形如 `sk-xxxxx`（API Key 管理页创建）；Token Plan Key 形如 `tp-xxxxx`（订阅管理页获取）（S3） | P0 | ✅ 官方教程页 |
| F-015 | WorkBuddy 配置四字段：提供商选"自定义/Custom"；端点 `https://maas-api.unisound.com/v1/chat/completions`；填 API Key；模型名 `u2-flash`（S3） | P0 | ✅ 官方教程页；端点两口径见 F-029 |
| F-016 | 高级选项"工具调用""图像输入""推理模式"按目标模型参数说明勾选；模型 ID 须逐字填 `u2-flash`（S3） | P1 | ✅ 官方教程页 |
| F-017 | 平台预置 U2-ASR、U2-TTS、U2-TTS-Clone、U1-OCR（含医疗版）等模型 Skill，可在 WorkBuddy 安装调用（S3） | P2 | ✅ 官方教程页单源 |

### D. 资格与排障（官方 Q&A）

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|----------|------|----------|
| F-018 | Q&A#1：无需领取，登录即可；须电脑端【控制台-实名认证】完成实名（/admin/account/verify）；手机端暂不支持调用模型（S4） | P0 | ✅ 官方 Q&A 单源 |
| F-019 | Q&A#2：报 "model u2-flash does not exist or you do not have access to it" 时查控制台-账户总览；余额为负无法调用（S4） | P0 | ✅ 官方 Q&A 单源 |
| F-020 | Q&A#3：负余额成因——新用户赠送**其他模型**资源包，调用其他模型产生欠费即锁 U2Flash；少量充值清欠即可恢复（S4） | P0 | ✅ 官方 Q&A 单源 |
| F-021 | Q&A#4：已认证且余额非负仍调不通：WorkBuddy 升至最新版，或两种 Base URL（`/v1/chat/completions` 与 `/v1`）互换（S4） | P0 | ✅ 官方 Q&A 单源 |
| F-022 | Q&A#8：404 `model_not_found` 两因：未实名认证 / 账户余额为负（S4） | P0 | ✅ 官方 Q&A 单源 |

### E. 赠品、扣费顺序与营销口径

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|----------|------|----------|
| F-023 | Q&A#5：账户若有此前领取的 1 亿 U2Flash token，消耗顺序为先扣 1 亿存量、再扣免费额度——免费期仍显示扣"额度"的原因（S4） | P0 | ✅ 官方 Q&A 单源 |
| F-024 | 公告原文"活动结束后在得5亿！填写即送！"+问卷星链接 v.wjx.cn/vm/rFQdEcw.aspx；"在得"应为"再得"（S1） | P0 | ⚠️ 错字勘误 E-3 |
| F-025 | Q&A#6：5 亿 token 于 10.31 活动结束后发放到问卷填写的手机号（S1/S4） | P0 | ⚠️ 厂商自述承诺，无条款页佐证 |
| F-026 | Q&A#7：赠送 5 亿 token 仅限 U2-Flash 单模型调用，不可用于全平台模型（S4） | P0 | ⚠️ 厂商自述，范围以官方 Q&A 为准 |

### F. 核验补充

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|----------|------|----------|
| F-027 | 模型页"立即体验"指向 `/playground/text?modelId=u2-flash`；另有 API 文档页 `/docs/api/text/openai-compatible`、工具接入索引页 `/docs/toolAI/u2claw`（S2） | P2 | ✅ 官方页链接 |
| F-028 | **勘误 E-1**：公告"无限制，无限量"与官方限流（RPM 100、TPM 1000 万，F-008）矛盾；"无限量"应理解为"不限总量/不计费"，调用仍受速率限制，以官方模型页参数为准（S1/S2） | P0 | ❌ 口径矛盾，正文采官方参数 |
| F-029 | **勘误 E-2**：官方族内 Base URL 两口径并存——模型页 `/v1`、教程页 `/v1/chat/completions`、Q&A 指引互换；差异是 base URL 与完整请求 URL 的层级差，非配置错误（S2/S3/S4） | P0 | ✅ 三源互证 |
| F-030 | "可接入所有主流编程工具"的基础是 OpenAI/Anthropic 双兼容协议（F-009）；云知声=供应商侧、WorkBuddy=腾讯产品侧（F-013）；支持自定义 OpenAI 兼容端点的工具均可同法接入（S1/S2/S5） | P1 | ✅ 官方信息关系归纳 |

---

## 信源距离与采信说明

1. **官方一手占比高**：30 条事实中 27 条来自云知声官方页面/官方 Q&A/被接入方官网，价格、规格、限流、端点、凭证、排障六类核心声明无需依赖第三方转述。
2. **厂商自宣单列**：模型能力定位（F-005）与 5 亿 token 赠送（F-025/F-026）为厂商自述，正文保留但显著标注，不作为独立结论。
3. **营销文案不静默照搬**：公告"无限量"（F-028）、错字"在得"（F-024）已进勘误台账，正文呈现官方参数口径与更正后语义。
4. **单源边界**：全部排障规则（F-018～F-023）目前仅见官方 Q&A 单一信源（rev.490，高频迭代），引用时携带文档版本与抓取日期。
