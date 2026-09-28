---
okf_version: "0.2"
type: bundle
title: "免费模型统一接入实录核验：token.inurl.link 与「0 元」真相"
description: "微信推广软文经 OKF v0.2 七阶段（R→I→E→V）转化——token.inurl.link 多厂商 Key 收拢与本地自动路由的逐条核验、2026-09 免费模型额度官方口径、BYOK 安全边界，以及「17 家 Key + 0 元」核心勘误。flagged。"
tags: [免费模型, BYOK, API聚合, 本地代理, 自动路由, 成本优化, 推广软文核验, GLM, LongCat, DeepSeek, flagged]
generated: { by: "reference_agent/trae-solo", at: "2026-09-16T20:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-16T20:30:00Z" }
reverified:
  - { by: "process:seven-concepts-v-site-refresh-g4", at: "2026-09-28T00:00:00Z", result: "flagged-maintained", facts: "F-071~F-087" }
  - { by: "process:seven-concepts-v-site-refresh-g5", at: "2026-09-28T12:00:00Z", result: "flagged-maintained", facts: "F-088~F-105", scope: "/app,/#why,/models#paid,/guide 四目标深度学习" }
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
>
> **🔁 2026-09-28 二次复核 G4（站点直证，F-071~F-087）：flagged 维持。** 定价与 3 密钥免费档未变、DeepSeek 仍在付费区（核心 ❌ 原样成立）；站点目录继续重复 Agnes/百度/LongCat 三处已勘误口径且 12 天未修正（F-079）。产品确有迭代（跨平台启动器、额度管理、免注册实时演示），但新增边界：付费目录 19→29（含 10 家隐藏/测试厂商经公开接口下发，F-077）、inurl-video/audio 分类当前空转（F-082）、四页加载主域 track.js 行为采集（F-084）。详见 [verification.md §7](references/verification.md)。

> **🔁 2026-09-28 三次复核 G5（四目标深度学习，F-088~F-105）：flagged 第三次维持（✅8/⚠️8/❌2）。** catalog 与 G4 **字节级同一文件**（SHA-256 `3F689C…BD0F1`），定价/三处勘误口径/隐藏厂商全部零迭代（F-088/F-089/F-092 ❌）。/app 界面证据新增：仪表盘四组件、**19 路由策略 + 5 档压缩 + Combo**（页面自认 MIT 开源网关 **OmniRoute** 同款，F-095/F-104）、自定义厂商三协议（F-096）、含个人收款码**人工核销**与「模拟支付成功」按钮并存的运营后台（F-097/F-098）；公开 news 首条标题摘要文不对题（F-100 ❌）；**/models#paid 付费卡整体落后当期旗舰 ≥1 大版本**（F-103）。详见 [verification.md §8](references/verification.md) 与 [omniroute-benchmark.md](references/omniroute-benchmark.md)。

> **📢 厂商/推广自述数据提示**：原文为微信公众号**推广软文**（文首含「免费AI Token额度·立即领取」广告、文末为注册转化链接）。文中「月省 550 元」「省 90%」「0.1 秒切换」「三周零花费」等成效数字均为作者/厂商自述，**无独立测量出处**；产品真实运营但运营主体匿名、本地代理闭源。读者应按「可研究、谨慎托付真实密钥」对待。

## 一句话结论

产品与架构**真实存在**、浏览器端加密承诺在代码层面兑现，但它是一款「免费增值 + 闭源本地代理 + 匿名个人运营」的小产品；「0 元」只在 **≤3 个免费厂商密钥、不含 DeepSeek、长上下文 ≤512K** 的收窄口径下成立。它示范的「OpenAI 兼容本地代理 + 多免费源故障切换」模式有独立参考价值，可用开源等价方案自建——G5 已核实机制最接近的 MIT 开源对照 **OmniRoute**（19 策略/Combo/RTK 压缩，inurl 面板自认同款），另有 LiteLLM、one-api/new-api。

## 内容导航

- [博文档案与产品核验总览](concepts/00-article-and-product.md)——软文判定、产品实测、信任画像、时间线勘误
- [免费模型额度事实与官方现状](concepts/01-free-model-landscape.md)——智谱/美团/百度/Agnes/通义/DeepSeek/Groq/OpenRouter 2026-09 口径
- [BYOK 统一令牌与本地代理架构](concepts/02-byok-unified-architecture.md)——请求路径、路由别名、E2EE 兑现边界与供应链风险
- [成本叙事、分层策略与决策边界](concepts/03-cost-strategy-boundaries.md)——账单可核性、修正版 90/10 策略、决策树
- [inurl 免费档接入配置演练（Cursor 视角）](examples/01-inurl-setup-walkthrough.md)——五步配置、排障表、安全操作清单；G5 增补路由变量、自定义厂商三协议、保活/停止（§6–§8）
- [开源对标：OmniRoute 本地 AI Gateway](references/omniroute-benchmark.md)——G5 新增信源专页（四源交叉，F-104）：19 策略/Combo/压缩机制对照、架构差异、中立性边界
- [信源与核验报告](references/index.md)——F-001~F-105 双份事实登记、P0 勘误四张清单、2026-09-28 二次复核 G4（§7）与三次复核 G5（§8）

## 已知边界（消费前必读）

1. **信源边界**：成效数字全部为推广文作者自述（F-008/F-025/F-033/F-038），非独立财务/性能测量；
2. **口径边界**：各厂商「赠送千万 tokens」均为 30–90 天一次性资源包；长期免费供给仅限速小模型档；
3. **信任边界**：产品无公司名/ICP/联系方式/开源仓库（F-056），闭源代理内嵌主密钥运行（F-053）——只宜录入低额度免费 Key；
4. **时效边界**：厂商额度与型号信息截点 **2026-09-16**；产品站点（页面/接口/目录/定价）经 **2026-09-28 G4/G5 两轮复核**——功能界面在迭代但 catalog 数据 G4→G5 字节级零迭代（F-088），免费层政策月级变动；`stale_after: 2026-12-31`，到期前复核；
5. **目录时效边界（G5）**：`/models#paid` 付费卡整体停留在 gpt-4o/claude-3.5/grok-2/gemini-1.5 一代，落后当期旗舰 ≥1 大版本（F-103）——选型付费模型必须回厂商官网核对，勿按站点卡片；
6. **支付运营边界（G5）**：收款含**个人收款码 + 管理员人工核销**，套餐页同时保留「模拟支付成功」测试按钮（F-097/F-098）——付款到账与售后为小规模手工流程，无自动化承诺；
7. **运营内容边界（G5）**：三处技术错误口径三审未改（F-092），无鉴权公开的 `/api/news` 首条标题与摘要文不对题（F-100）——目录与资讯仅可作入口索引，不可作事实源；
8. **界面证据边界（G5）**：19 路由策略、5 档压缩率（15/30/50/75%、RTK 60–90%）、仪表盘与后台均为**未注册前端界面/站点自述**（F-094/F-095），压缩率未经独立基准测试；OmniRoute 对照不构成抄袭/侵权判定（F-104）。

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
