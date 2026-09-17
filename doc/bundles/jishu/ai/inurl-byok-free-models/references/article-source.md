---
okf_version: "0.2"
type: reference
title: 博文原文事实清单
description: 微信公众号推广文《同事偷偷用这个网站，一年省下5000块 Token 费用》原文事实采集，F-001 至 F-035 编号，含 P0 核验结果
tags: [byok, inurl, 免费模型, agnes, glm-4-flash, siliconflow, longcat, 厂商自宣]
generated:
  by: trae-agent
  at: "2026-09-16T20:30:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-16T20:30:00+08:00"
status: flagged
stale_after: "2026-12-16"
sources:
  - id: blog-article
    resource: /references/article-source.md
  - id: weixin-blog
    url: https://mp.weixin.qq.com/s/xbpFUmp2s87BUbcFagwQ0A
  - id: inurl-official
    url: https://token.inurl.link/
  - id: agnes-wiki
    url: https://wiki.agnes-ai.com/zh-Hans/docs/agnes-25-flash
  - id: zhipu-glm4
    url: https://docs.bigmodel.cn/cn/guide/models/text/glm-4
  - id: siliconflow-docs
    url: https://docs.siliconflow.cn/cn/userguide/rate-limits/rate-limit-and-upgradation
  - id: longcat-docs
    url: https://longcat.chat/platform/docs/zh/
  - id: meituan-longcat2
    url: https://tech.meituan.com/2026/06/30/LongCat2.0.html
---

# 博文原文事实清单（F 编号双份登记）

> **信源**：微信公众号「风信旗」文章《同事偷偷用这个网站，一年省下5000块 Token 费用》（作者：检校千牛卫，2026-09-04 22:00，标原创，IP 属地河南）
> **推文链接**：https://mp.weixin.qq.com/s/xbpFUmp2s87BUbcFagwQ0A
> **采集时间**：2026-09-16（browser_use 直取 `#js_content`，正文 2090 字符，无表格/代码块/图注，3 张设计卡片配图）
> **信源距离**：**厂商自宣（营销软文）**——全文为 token.inurl.link 导流，成效数字默认 P0
> **双份一致性**：本清单 F-001~F-035 与主仓库 spec `.trae/specs/okf-wiki-ecosystem/inurl-byok-free-models-blog-okf-wiki/facts.md` 编号集合一致
> 类型：O=客观叙述　S=厂商自述　V=作者观点　T=转述/传闻；核验：✅ 通过 / ⚠️ 部分准确 / ❌ 错误或查无 / 📝 观点不核验

---

## 一、博文元信息与叙事框架

| F编号 | 类 | 博文口径 | 核验 | 说明 |
|-------|----|----------|------|------|
| F-001 | O | 标题《同事偷偷用这个网站，一年省下5000块 Token 费用》；封面标"TOKEN 省钱实战 2026.08" | ✅ | 博文元数据 |
| F-002 | O | 公众号"风信旗"，作者"检校千牛卫"，原创，IP 河南 | ✅ | 博文元数据 |
| F-003 | O | 发布于 2026-09-04 22:00 | ✅ | 搜狗微信索引未见本篇（见 F-029） |
| F-004 | O | 原文 URL mp.weixin.qq.com/s/xbpFUmp2s87BUbcFagwQ0A | ✅ | 公开可访问 |
| F-005 | V | "大多数人把 AI 当订阅制 SaaS，每月乖乖交会员" | 📝 | 作者观点，无数据 |
| F-006 | V | "会玩的人把各家免费、低价通道串成流水线" | 📝 | 作者观点 |
| F-007 | T | "同事年度账单"一年省下 5000 块 Token 费用；"省下来的都是净利润" | ❌ | P0 成效数字：无账单、无测算、全网及官网查无出处；BYOK 不产生该价差（F-029） |
| F-008 | V | "涨价是真的，但'用不起'是假象" | 📝 | 营销判断，未给具体涨价事实 |

## 二、inurl · 聚合 APIToken 产品声明（厂商自述）

| F编号 | 类 | 博文口径 | 核验 | 说明 |
|-------|----|----------|------|------|
| F-009 | S | 产品"inurl · 聚合 APIToken"，域名 token.inurl.link | ✅ | 站点真实在线（F-026） |
| F-010 | S | 与"API 中转"不同的路：BYOK（自带密钥）· 端到端加密 · 永不中转 | ✅/⚠️ | 官网定位可证实；"永不中转"为闭源承诺（F-028） |
| F-011 | S | 统一令牌：OpenAI/Anthropic/Gemini/DeepSeek 等 Key 收拢成一枚，代码只认一个 | ✅ | 官网原文+教程页扩展厂商列表（F-027） |
| F-012 | S | 密钥浏览器本地主密钥加密（AES-256-GCM + PBKDF2），云端只存密文，官方看不到明文 | ✅/⚠️ | 前端代码印证算法；"云端不解密"服务端闭源无法证真（F-027） |
| F-013 | S | 双份 escrow 托管，忘密码凭恢复密语找回 | ✅ | 代码实测双份密文+找回流程（F-027） |
| F-014 | S | 本地 Agent 代理、永不中转：本机发起调用、云端零厂商请求、厂商看到 Key 直连、不会被判共享代理封号 | ⚠️ | 仅厂商单源；代理闭源；"不封号"绝对化承诺（F-028） |
| F-015 | S | OpenAI/DeepSeek/Mistral/Anthropic/Gemini 格式互转、流式归一 | ⚠️ | 仅官网自述，无第三方实测 |
| F-016 | S/V | "密钥从不离开你的设备；云端库泄露攻击者也只能拿到无法还原的密文" | ⚠️/📝 | 本地加密可印证；"无法还原"为推论性承诺 |

## 三、4 个免费模型声明

| F编号 | 类 | 博文口径 | 核验 | 说明 |
|-------|----|----------|------|------|
| F-017 | S | Agnes AI（美国·完全免费·OpenAI 兼容）：Sapiens AI 出品全模态免费网关；agnes-2.5-flash 支持百万级上下文；注册即送 Key；适合长文档长对话 | ❌/⚠️ | 三处硬伤：国籍应为**新加坡**（F-030）；上下文官方 **512K**（F-031）；免费为阶段性 $0+20 RPM 限制（F-032）。模型真实/兼容/注册可用 ✅ |
| F-018 | S | 智谱 GLM-4-Flash（中国·完全免费·OpenAI 兼容）：按量计费 ¥0，中文理解强 | ✅ | 250414 仍在线免费、128K、OpenAI 兼容（F-033） |
| F-019 | S | 硅基流动免费通道：新老用户都有免费 Token，可零成本体验 Qwen/DeepSeek/GLM 等开源模型 | ✅/⚠️ | 免费 9B 级开源小模型全员 0 元；无 GLM-4-Flash、DeepSeek 满血版付费；赠金口径见 F-034 |
| F-020 | S | 美团 LongCat：自研万亿参数 MoE；注册送 1000 万 Tokens；原生 1M 上下文 | ⚠️ | 仅 LongCat-2.0 万亿/1M；1000 万须实名领取、30 天有效、限时（F-035） |
| F-021 | V | 4 个免费 Key 收进 token.inurl.link 即"永不涨价的模型弹药库" | 📝 | 作者观点；免费政策均可被厂商调整（F-032/F-034/F-035） |

## 四、行动号召与结尾

| F编号 | 类 | 博文口径 | 核验 | 说明 |
|-------|----|----------|------|------|
| F-022 | V | 用统一令牌串免费/付费/自家 Key、按成本自动路由；"省下的会员费够买好几顿火锅" | 📝 | 纯口号，无操作步骤 |
| F-023 | V | "大厂涨的是他们的价格，创作权不该被绑票……把密钥握在自己手里、用免费模型补日常消耗" | 📝 | 作者观点 |
| F-024 | O | CTA：token.inurl.link/app?tab=register；官网 token.inurl.link | ✅ | 可访问 |
| F-025 | O | 账号定位"持续分享 AI 省钱实战与工具干货" | ✅ | 账号自述；同号另两篇系列软文（F-029） |

## 五、核验补充事实（F-026 ~ F-035）

| F编号 | 官方/第三方核验口径 | 结果 | 信源（2026-09-16 访问） |
|-------|----------------------|------|--------------------------|
| F-026 | inurl.link 2018-12-14 注册（万网，Cloudflare NS，隐私遮蔽）；站点无 ICP 备案、无公司名、无隐私政策/条款、无联系方式，含个人化支付宝付费入口，个人/极小团队特征 | ✅ 查证 | RDAP rdap.org/domain/inurl.link；urlscan.io；官网 |
| F-027 | 前端代码实测：PBKDF2(SHA-256, 100000 迭代) deriveKey→AES-GCM 256 浏览器端加解密；注册生成 escrow_pw+escrow_rec 双份密文 POST /api/escrow；教程页另支持通义/智谱/Kimi/豆包/MiniMax/Groq/OpenRouter/自定义 | ✅ 查证 | token.inurl.link/app 前端脚本；/guide |
| F-028 | 本地代理 localhost:3003/v1（local-agent.js）；byok-launch.bat/.sh 内嵌令牌与主密钥、自动拉取程序（需 Node.js 18+）；闭源无公开仓库，网络行为不可审计；GitHub/Gitee/npm 无相关项目 | ✅ 查证 | /guide；GitHub/Gitee/npm API |
| F-029 | 第三方独立证据为零：除自有域名与"风信旗"文章外无报道/评测/讨论；同号另两篇软文（09-09、09-15）；"5000 块"官网/软文/全网均无；BYOK 下用户仍按厂商原价付费，最多省中转加价 | ✅ 查证 | Bing/百度/搜狗、GitHub/Gitee/npm、两篇微信原文 |
| F-030 | Agnes AI 是**新加坡 Sapiens Technology Pte. Ltd.**（非美国）的公开品牌；创始人 Bruce Yang（NUS）；PRNewswire 2025-05-01 稿；Tech in Asia 2026-03 报融资 2000 万美元 | ✅ 查证 | PRNewswire 302443885；techinasia.com；App Store 主体 |
| F-031 | agnes-2.5-flash 官方 **512K 上下文/65.5K 输出**（2026-07-13 全量上线）；1M 属已废弃 2.0-flash 临时窗口（6 月已回退 256K）；免费层第三方实测 20 RPM/1000 RPD；OpenRouter 443 模型中无该系 | ✅ 查证 | wiki.agnes-ai.com/zh-Hans/docs/agnes-25-flash；dev.to 百供应商压测；本库 agnes-ai bundle 同证 512K |
| F-032 | Agnes 2.5-flash 当前 $0 系**阶段性优惠**（刊例价输入 $0.05/输出 $0.15 每 MTok）；免费文本名义 30/实际 20 RPM；付费 Token Plan 与 2.5-pro（$0.45/$0.90）、视频计费并存，免费层无 SLA | ✅ 查证 | wiki.agnes-ai.com pricing/tokenplan/faqs |
| F-033 | GLM-4-Flash-250414 仍免费（128K/输出 16K）；限速按在途并发 V0=200、V1-V3=1000/2000/3000，不公布 QPS/RPM；OpenAI 兼容 open.bigmodel.cn/api/paas/v4/；下线的是 GLM-4.5-Flash（2026-01-30→路由 GLM-4.7-Flash/200K） | ✅ 查证 | docs.bigmodel.cn glm-4/equity-explain/openai；zhipuai.cn/zh/news/148 |
| F-034 | 硅基流动免费模型对全体实名用户长期 0 元（Pro/ 前缀为收费）；现行激励为实名手动领 **¥16（$1）券、180 天有效、活动至 2026-12-31**（¥14 系 2025 旧政）；免费档 9B 级开源（Qwen3-8B、DeepSeek-R1-Distill-Qwen-7B 约 30 RPM、glm-4-9b-chat），**无 GLM-4-Flash、DeepSeek 满血付费**；OpenAI 兼容 api.siliconflow.cn/v1 | ✅ 查证 | siliconflow.cn 公告 2026-01-15/06-04；docs.siliconflow.cn |
| F-035 | LongCat-2.0（2026-06-30）总参 **1.6T**、平均激活约 **48B**（33-56B）、LSA 注意力**正式 1M 窗口/输出 128K**；OpenAI 兼容 api.longcat.chat/openai；1000 万 Tokens 须**实名领取、30 天有效**（另有 ¥9.9/5000 万、¥399/10 亿包），限时活动以页面为准；Flash 系列 560B/128K 老模型 2026-05-29 停调；官方未公开 RPM/TPM | ✅ 查证 | meituan.com NN260630164005904；tech.meituan.com LongCat2.0；longcat.chat 文档；arxiv 2509.01322 |

---

## 博文结构留档（PART 骨架）

| 章节 | 标题 | 性质 |
|------|------|------|
| PART 01（WHY） | 涨价是真的，但"用不起"是假象 | 叙事铺垫，无具体涨价事实 |
| PART 02（HOW） | 破局关键：把钥匙握在自己手里 | inurl 四项功能介绍（F-011~F-016） |
| PART 03（FREE） | 先薅为敬：4 个完全免费的模型 | F-017~F-020 |
| PART 04（ACTION） | 搭一条自己的管道 | 仅口号一段，无操作步骤 |
| LAST（END） | 写在最后 | 观点升华 + 注册 CTA（F-023/F-024） |

> 正文 6 个 URL：4 条 `inurl.link/<agnes-ai|bigmodel|siliconflow|longcat>` 导流短链 + 注册页 + 官网，均为产品自有/导流域名，无第三方信源链接。
