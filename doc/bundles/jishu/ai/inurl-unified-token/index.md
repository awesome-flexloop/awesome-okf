---
okf_version: "0.2"
type: bundle
title: "免费模型统一接入实录核验：token.inurl.link 与「0 元」真相"
description: "微信推广软文经 OKF v0.2 七阶段（R→I→E→V）转化——token.inurl.link 多厂商 Key 收拢与本地自动路由的逐条核验、2026-09 免费模型额度官方口径、BYOK 安全边界，以及「17 家 Key + 0 元」核心勘误。flagged。"
tags: [免费模型, BYOK, API聚合, 本地代理, 自动路由, 成本优化, 推广软文核验, GLM, LongCat, DeepSeek, flagged]
generated: { by: "reference_agent/trae-solo", at: "2026-09-16T20:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-16T20:30:00Z" }
status: flagged
stale_after: 2026-12-31
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/dSTvvOjPIRpbSJHIqxi0gw
    title: "一个程序员的省钱实录：从月付 500 到 0 元（风信旗/检校千牛卫，2026-09-02）"
    author: "风信旗/检校千牛卫"
    last_modified: 2026-09-02
  - id: product
    resource: https://token.inurl.link/
    title: "inurl · 聚合 APIToken 官网"
  - id: product-guide
    resource: https://token.inurl.link/guide
    title: "inurl 官方使用教程"
  - id: zhipu
    resource: https://docs.bigmodel.cn/cn/guide/models/text/glm-4
    title: "智谱 GLM-4 官方文档"
  - id: longcat
    resource: https://www.meituan.com/news/NN260630164005904
    title: "美团 LongCat-2.0 发布官方新闻"
  - id: qianfan
    resource: https://cloud.baidu.com/doc/qianfan/s/wmh4sv6ya
    title: "千帆模型服务计费官方文档"
  - id: openai
    resource: https://help.openai.com/en/articles/9624314
    title: "OpenAI Model Release Notes"
  - id: anthropic
    resource: https://www.anthropic.com/news/claude-opus-5
    title: "Claude Opus 5 发布新闻"
---

# 免费模型统一接入实录核验：token.inurl.link 与「0 元」真相

> **⚠️ 状态：`flagged`** —— 博文主结论「17 家免费 Key 全量托管、月付 500 → 0 元干完所有活」存在核心口径冲突与失实：
>
> - **E1（核心）**：产品免费档**仅允许 3 个厂商密钥**（10 个需 ¥9.9/月、无限需 ¥29.9/月），「17 家」实为其模型页免费厂商计数（F-050/F-051/F-070）；
> - **E2**：自动路由主推的 **DeepSeek 官方收费**，产品自己也将其归在付费区（F-064）；
> - **E3**：博文发布当日（2026-09-02）推荐的 GPT-4o 已退役 7 个月，当期旗舰为 GPT-5.6 Sol / Claude Opus 5（F-069）。
>
> 另有 LongCat 政策与「2026-03 零成本」时间线互斥（F-060）、百度额度口径错误（F-061）、Agnes 免费档实为 512K（F-062）。完整核验见 [references/verification.md](references/verification.md)。

> **📢 厂商/推广自述数据提示**：原文为微信公众号**推广软文**（文首含「免费AI Token额度·立即领取」广告、文末为注册转化链接）。文中「月省 550 元」「省 90%」「0.1 秒切换」「三周零花费」等成效数字均为作者/厂商自述，**无独立测量出处**；产品真实运营但运营主体匿名、本地代理闭源。读者应按「可研究、谨慎托付真实密钥」对待。

## 一句话结论

产品与架构**真实存在**、浏览器端加密承诺在代码层面兑现，但它是一款「免费增值 + 闭源本地代理 + 匿名个人运营」的小产品；「0 元」只在 **≤3 个免费厂商密钥、不含 DeepSeek、长上下文 ≤512K** 的收窄口径下成立。它示范的「OpenAI 兼容本地代理 + 多免费源故障切换」模式有独立参考价值，可用开源等价方案（LiteLLM、one-api/new-api）自建。

## 内容导航

- [博文档案与产品核验总览](concepts/00-article-and-product.md)——软文判定、产品实测、信任画像、时间线勘误
- [免费模型额度事实与官方现状](concepts/01-free-model-landscape.md)——智谱/美团/百度/Agnes/通义/DeepSeek/Groq/OpenRouter 2026-09 口径
- [BYOK 统一令牌与本地代理架构](concepts/02-byok-unified-architecture.md)——请求路径、路由别名、E2EE 兑现边界与供应链风险
- [成本叙事、分层策略与决策边界](concepts/03-cost-strategy-boundaries.md)——账单可核性、修正版 90/10 策略、决策树
- [inurl 免费档接入配置演练（Cursor 视角）](examples/01-inurl-setup-walkthrough.md)——五步配置、排障表、安全操作清单
- [信源与核验报告](references/index.md)——F-001~F-070 双份事实登记与 P0 勘误四张清单

## 已知边界（消费前必读）

1. **信源边界**：成效数字全部为推广文作者自述（F-008/F-025/F-033/F-038），非独立财务/性能测量；
2. **口径边界**：各厂商「赠送千万 tokens」均为 30–90 天一次性资源包；长期免费供给仅限速小模型档；
3. **信任边界**：产品无公司名/ICP/联系方式/开源仓库（F-056），闭源代理内嵌主密钥运行（F-053）——只宜录入低额度免费 Key；
4. **时效边界**：所有额度、定价与型号信息截点 **2026-09-16**，免费层政策月级变动；`stale_after: 2026-12-31`，到期前复核。

## 主题关联

- [📊 2026免费大模型API汇总（40家平台）](../free-llm-api-roundup/index.md)——同主题姊妹束（同为 flagged）：免费额度总盘与全平台选型，本束聚焦「聚合代理 + 单篇软文核验」；
- [🔑 inurl BYOK 密钥聚合与四个免费模型](../inurl-byok-free-models/index.md)——**同产品姊妹束**：同公众号 2026-09-04《一年省下5000块 Token 费用》的转化（35 条事实），聚焦 BYOK 安全机制（AES-256-GCM/PBKDF2/escrow/信任边界）与 Agnes/GLM-4-Flash/硅基/LongCat 四家官方口径，与本束（09-02 文章，免费档限制与接入演练）互补；
- [🐦 EchoBird 百灵鸟桌面管理工具](../echobird/index.md)——同形态「模型枢纽 + 本地代理」的桌面产品对照；
- [💳 DeepSeek-V4 免费方案与 API 定价](../deepseek-pricing/index.md)——DeepSeek 免费/付费官方口径补充；
- [🗜️ 上下文优化（Context Optimization）](../context-optimization/index.md)——与「多源聚合」正交的另一降本路径。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
