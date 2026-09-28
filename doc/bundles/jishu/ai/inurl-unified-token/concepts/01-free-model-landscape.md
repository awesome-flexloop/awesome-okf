---
type: Concept
title: "免费模型额度事实与官方现状"
description: "博文涉及的八类免费模型通道（智谱/美团/百度/Agnes/通义/DeepSeek/硅基流动/OpenRouter/Groq）逐条对照 2026-09 官方口径，含三项额度勘误与免费层共性限制。"
tags: [免费额度, GLM-4-Flash, LongCat, 千帆, Agnes, qwen-coder, DeepSeek, OpenRouter, 勘误]
sources:
  - id: zhipu
    resource: https://docs.bigmodel.cn/cn/guide/models/text/glm-4
    title: "智谱 GLM-4 官方文档"
  - id: longcat
    resource: https://www.meituan.com/news/NN260630164005904
    title: "美团 LongCat-2.0 发布官方新闻（2026-06-30）"
  - id: qianfan
    resource: https://cloud.baidu.com/doc/qianfan/s/wmh4sv6ya
    title: "千帆模型服务计费官方文档"
  - id: agnes
    resource: https://wiki.agnes-ai.com/zh-Hans/docs/agnes-25-flash
    title: "Agnes 2.5 Flash 官方文档"
  - id: qwen
    resource: https://help.aliyun.com/zh/model-studio/new-free-quota
    title: "百炼新人免费额度官方帮助"
  - id: deepseek
    resource: https://api-docs.deepseek.com/
    title: "DeepSeek API 官方文档"
  - id: openrouter
    resource: https://openrouter.ai/docs/api-reference/limits
    title: "OpenRouter Limits 官方文档"
---

# 免费模型额度事实与官方现状

> 以下所有「官方现状」截点为 **2026-09-16**（厂商政策侧）；**2026-09-28** 另对产品站点目录做二次复核（见 §5）。免费层政策变化极快——核验中已观察到半年内 LongCat 老模型整代下线、Agnes 模型换代、OpenRouter 免费名单轮换，落地前以各厂商控制台当日页面为准。

## 1. 博文通道 × 官方口径对照

| 博文说法（F 编号） | 官方现状（2026-09-16） | 结论 |
|--------------------|------------------------|------|
| 智谱 **GLM-4-Flash** 免费但高并发 429（F-013） | GLM-4-Flash-250414（128K）定价表仍标「免费版」；现主力免费型号已换为 **GLM-4.7-Flash（200K）**；并发按账号等级动态限流，超限错误码 1302/1305（即 429），社区实测免费档约 1 并发；新用户 2000 万 tokens 资源包、**90 天有效**（不是永久） | ✅ 属实 |
| 美团 **LongCat** 新用户送 1000 万、两周造完（F-014） | 1000 万确有出处：**2026-06-30 LongCat-2.0 发布**时实名新人资源包、**30 天有效**（内测用户另发 5000 万）；老 Flash 六模型已于 2026-05-29 下线；唯一在售的 LongCat-2.0（1.6T、原生 1M 上下文）已按量付费：折扣价输入 ¥2/输出 ¥8 每百万 tokens | ⚠️ 一次性礼包≠长期免费 |
| **百度**每月 100 万、月中见底（F-015） | 千帆 ModelBuilder：**每个模型独立 100 万 tokens、3 个月有效、到期不按月重置**；另有 **ERNIE-Speed/Lite/Tiny/ERNIE-3.5-8K 永久免费、不限总量、限 QPS≈50**（博文漏报） | ⚠️ 口径错误 + 漏报 |
| **Agnes AI** 百万上下文（F-030） | 免费 agnes-2.5-flash 与已废弃 2.0-flash 均为 **512K**；**1M 仅属于付费 agnes-2.5-pro（2026-08-01 发布）**；6–7 月灰度期的 1M 高峰期也降 512K | ⚠️ 免费拿不到 1M |
| 写代码自动路由 **qwen-coder**（F-024/F-034） | 官方型号 **qwen3-coder-plus / qwen3-coder-flash**（1M 上下文）；百炼新用户**每模型 100 万 tokens、90 天有效**；通义灵码个人版 IDE 插件长期免费 | ✅ 真实，但免费是一次性额度 |
| 写代码自动路由 **deepseek**（F-024/F-034） | DeepSeek 官方 API **收费**（V3/V4 明码标价、V4 峰谷计价），仅小额新人赠送；硅基流动免费层仅 ≤9B 小模型；OpenRouter 免费名单已无 DeepSeek；只有 AMD Cloud Token Factory、Hetzner 实验平台、WorkBuddy 积分等**限免活动**可免费调用 | ❌ 失实 |
| **Groq** 快但额度有限（F-016） | 免费层无需信用卡长期有效：主力模型 30 RPM / 1000 RPD / TPM 6K–30K；compound 系列低至 250 RPD | ✅ 属实 |
| **硅基流动**（F-011） | 新用户 16 元（$1）赠金；**≤9B 开源小模型永久免费**（限 RPM），DeepSeek 等大模型付费 | ✅ 属实 |
| **OpenRouter**（F-011） | `:free` 后缀机制仍在、约 20 个模型动态轮换；统一 **20 RPM**；累计充值 <$10 限 **50 请求/天**，≥$10 为 **1000 请求/天**；余额为负免费模型也报 402 | ✅ 属实，限制严格 |

## 2. 勘误聚焦：三个最容易被省钱文带偏的口径

### 2.1 「送 N 千万 tokens」是资源包，不是月度额度

LongCat 1000 万（30 天）、智谱 2000 万（90 天）、百炼每模型 100 万（90 天）、千帆每模型 100 万（3 个月）——四类常见说法**全部是一次性资源包**，到期或用完即止。把它们摊到「每月」是省钱类软文的共性放大手法。

### 2.2 「每月 100 万」与「永久免费」同时存在于百度

博文只讲了千帆 100 万资源包且重置周期错误，却漏掉了真正适合「日常白嫖」的 ERNIE-Speed/Lite/Tiny 系列——不限 token 总量、限 QPS。做免费层选型时应优先识别这类**限速不限量**模型，而非一次性礼包。

### 2.3 「百万上下文免费」在 2026-09 基本不成立

- Agnes：免费 512K，1M 进付费档；
- LongCat-2.0：1M 与商业化同步推出，按量付费；
- qwen3-coder 的 1M 随新人 100 万 tokens 资源包提供（90 天）。

长文档场景要么接受 512K 以下免费窗口，要么付费，不应按博文配置预期。

## 3. 免费层的四条共性约束（博文只讲了两条）

1. **速率/并发限制是常态**：智谱免费档约 1 并发（429）、Groq 30 RPM、OpenRouter 20 RPM——博文的「额度焦虑」真实存在（F-022），但解法不是赌单点，而是多通道 + 故障切换（见 [/concepts/02-byok-unified-architecture.md](/concepts/02-byok-unified-architecture.md)）；
2. **新人礼包一次性、与实名主体绑定**：同一身份证不可重复领取（百炼规则），不可持续；
3. **免费模型清单动态轮换**：OpenRouter :free、inurl /models 免费区都按月级变动；
4. **免费端点可能记录提示词**：OpenRouter 官方文档明示，敏感代码/私域内容不宜走免费通道。

## 4. 博文作者的「质量分层」核对

作者观点（F-034~F-037，📝 观点非事实）：普通 CRUD/脚本文档类任务免费模型够用、复杂推理才需付费——方向与社区共识一致；但其论据中「免费 deepseek 写代码」不成立（F-064），「比 GPT-3.5 中文好」无评测出处（F-035），「90% 的人 90% 时间不需要顶级推理」（F-037）无数据支撑。付费档对标也应更新为当期旗舰 **GPT-5.6 Sol / Claude Opus 5**，而非博文发布时已退役的 GPT-4o（F-069）。

## 5. 2026-09-28 站点目录复核：产品页不是免费政策事实源

> 厂商官方口径本次未重查（截点维持 2026-09-16）；本节仅复核 **inurl 站点自己的目录文案**在 12 天后是否修正。结论是：没有。

**① 三处已勘误口径原样保留（F-079 ❌）**

| /models 卡片文案（2026-09-28） | 本束权威口径 | 对应勘误 |
|-------------------------------|-------------|---------|
| Agnes「agnes-2.5-flash 支持百万级上下文」 | 免费档 512K，1M 仅付费 pro | F-062 |
| 百度千帆「新用户每月赠送 100 万 tokens」 | 每模型 100 万 / 3 个月，不按月重置 | F-061 |
| LongCat（免费条目，含 LongCat-2.0）「新用户注册送 1000 万、原生 1M」 | 一次性资源包 30 天；LongCat-2.0 现行按量付费 | F-059 |

**② 免费 17 家名单未变，但模型条目新旧混杂（F-080 ⚠️）**

- OpenRouter 免费模型已轮换为 `google/gemini-2.5-flash:free`、`meta-llama/llama-3.3-70b-instruct:free`（动态轮换属实）；
- 同期陈旧条目未清理：硅基流动免费通道仍列旧代 `deepseek-ai/DeepSeek-V2.5`；Agnes 仍挂官方已废弃的 agnes-2.0-flash；Gemini 免费层仍列 gemini-1.5/2.0-flash-exp（官方当期已更高代）。

**③ 计数口径的内外差（F-077/F-078 ⚠️）**：/models 页面计数牌与渲染卡片仍为「免费 17 / 付费 19」，但 `/api/catalog` 实际为 17 free + **29 paid**——多出的 10 家是 `public:false` 的预留/测试厂商（派欧云、Together、DeepInfra、Novita 及 localhost mock 等），不在页面显示却随公开接口下发。

**方法论结论**：聚合站目录承担的是「入口索引」角色，其额度/上下文/代际文案同时存在新旧混杂与营销放大，**免费模型事实仍应回溯各厂商官方文档**——本篇 §1–§3 的全部结论与 flagged 状态不因站点迭代而改变。

**④ G5 三次复核：陈旧信号扩展到付费区（F-103 ⚠️，持续 F-080）**

2026-09-28 G5 对 `/models#paid` 做卡片逐张核对（catalog 当日与 G4 字节级同一文件，F-088）：付费公开卡仍列 `gpt-4o` / `gpt-4o-mini` / `gpt-3.5-turbo`、`claude-3-5-sonnet-latest` / `claude-3-5-haiku-latest` / `claude-3-opus-latest`、`grok-2` / `grok-2-mini`、`gemini-1.5-flash` / `gemini-1.5-pro`（无 `-002` 后缀，该后缀在免费卡）/ `gemini-2.0-flash-exp`。对照 F-069 权威证据（GPT-4o 2026-02-13 退役、2026-09 当期旗舰 GPT-5.6 Sol、Claude Opus 5），**付费区目录整体落后官方当期 ≥ 1 个大版本**，与 ② 的免费区陈旧条目同源。这说明 G4「产品页不是政策事实源」的结论对**付费选型同样成立**：即便升级到 ¥990/¥2990 档（F-089），目录卡片也不保证对应厂商当期模型，付费决策必须回厂商官网核对在售型号。
