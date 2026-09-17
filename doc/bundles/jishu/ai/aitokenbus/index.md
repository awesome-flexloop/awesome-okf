---
okf_version: "0.2"
type: bundle
title: "AITokenBus：AI Token 共享与交换平台（自宣发布资讯核验）"
description: "独立开发者唐霜 2026-07-22 自宣上线的 Token 共享/交换平台：共享池分包、Token 市场、TC 站内积分、免费矿池、GPU 贡献与请求路由。经 2026-09-16 实地核验，核心功能确有实现，但供给薄弱、无备案主体与协议，qwen-3.8 版本号时间错位。产品自述资讯，非操作教程。"
tags: [aitokenbus, token-sharing, token-market, token-coin, api-gateway, 独立开发者, 自宣核验, 合规风险]
generated:
  by: "process:blog-article-to-okf-wiki (Trae AI)"
  at: 2026-09-16
verified:
  by: "process:seven-concepts-v"
  at: 2026-09-16
status: stable
stale_after: 2026-12-31
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: wechat-blog
    url: https://mp.weixin.qq.com/s/wtGxzSy0PvhoVAdhH-4fxw
  - id: author-blog
    url: https://www.tangshuang.net/9822
  - id: platform
    url: https://aitokenbus.24x7.to
  - id: glm-release
    url: https://docs.bigmodel.cn/cn/update/new-releases
  - id: kimi-k3
    url: https://www.kimi.com/blog/kimi-k3
  - id: qwen38-std
    url: http://www.stdaily.com/web/gdxw/2026-08/03/content_558298.html
---

# AITokenBus：AI Token 共享与交换平台

> ⚠️ **厂商/个人开发者自述内容**：本知识包的一手信源是平台创建者本人（唐霜）的自宣发布文，全渠道**零独立第三方信源**。2026-09-16 经浏览器实地核验：平台真实在线、核心功能（共享池/市场/TC/免费池/GPU 节点/路由）确有实现；但"免费无限""ollama 接入""自动故障切换"等表述与实测存在差距，且平台**无运营主体、无 ICP 备案、无用户协议/隐私政策**。阅读与使用前请先看 [概念 02：边界与风险](concepts/02-risks-and-boundaries.md)。
>
> 📰 **内容性质：产品自述发布资讯，非操作教程**（无版本化、可复现的安装/配置/实测流程，不设 examples）。运营数据为 2026-09-16 单次快照，`stale_after: 2026-12-31`。

AITokenBus（https://aitokenbus.24x7.to ）是一个把模型厂商订阅套餐与 API 额度在用户之间"**分包共享、挂售交换、闲时贡献**"的 C2C 中转平台，2026 年 7 月由独立开发者唐霜自宣上线（前身为其博客记录的 AICodingBus）。用户把厂商 API 地址与 Key 托管建池、经邀请链接分包给团队；分包可挂到 Token 市场用站内积分 **Token Coin（TC）** 交易（如 glm → TC → K3）；闲置 GPU 经自研 SUMU 客户端捐赠推理算力赚 TC；另设有 0 TC 的官方免费矿池与按内容类型分流的请求路由。TC 无法币出入金、不可转让，仅站内流通。

## 内容导航

- [概念 00：平台总览——发布事实与实测现状](concepts/00-platform-overview.md)
- [概念 01：Token 共享与交换机制——共享池、市场与 TC 经济模型](concepts/01-token-sharing-mechanism.md)
- [概念 02：边界与风险——营销宣称、合规缺口与模式定位](concepts/02-risks-and-boundaries.md)
- [参考：博文事实清单（F-001~F-037）](references/article-source.md)
- [参考：P0 独立核验报告与勘误](references/verification.md)
- [更新日志](log.md)

## 核验结论速览（12 项 P0）

| 结论 | 项目 |
|------|------|
| ✅ 通过（7） | 平台在线、共享池+邀请、Token 市场+TC、TC 收支闭环、多协议 API、glm-5.2、kimi-k3 |
| ⚠️ 部分成立（4） | 免费池（真实但仅 2 节点/35 模型中 1 可用）、ollama 接入（实为自研 SUMU）、自动 failover（仅池内备用模型）、TC 属性承诺（行为一致但无协议文本） |
| ❌ 勘误/风险（2） | **qwen-3.8 时间错位**（2026-08-03 才发布、官方 ID 为 `qwen3.8-*`，非核心声明，正文已按正确值呈现）；零独立信源+无备案主体 |

核心产品声明经独立核验基本成立，故状态为 `stable`；❌ 项均非主结论证伪，不触发 flagged，但附强边界声明。

## 已知边界

1. **自宣信源**：全部说法源自创建者本人，无媒体报道、无开源仓库、无工商/备案信息（F-032/F-036）。
2. **供给极早期**：市场 8 个微型挂售、矿池 71 注册节点仅 2 在线、免费池 1/35 模型可用（2026-09-16 快照）；"免费无限"无 SLA。
3. **合规灰色地带**：托管/转售厂商 API Key 可能违反厂商服务条款，存在封号、Key 泄露与责任连带风险；无隐私政策约束数据使用。
4. **版本时效**：博文 qwen-3.8 系发布时间错位；GLM/Kimi 版本也在快速演进（核验日 GLM 已到 5.3）。
5. **未核验部分**：注册后的建池、结算、路由、节点全链路未实测（核验未注册账号）。

## 主题关联

- [💥 Token 经济大爆发：46.7 万亿周调用量](../token-economy-explosion/index.md)——宏观 Token 商品化与中美调用量竞争背景；本束是该趋势下的微观 C2C 产品样本。
- [🚀 国产 Token 出海：低价算力如何碾压全球市场](../domestic-model-token-export/index.md)——OpenRouter 官方结算的 B2B 网关路径，与 AITokenBus 的 C2C 额度再分配形成对照。
- [📊 2026 免费大模型 API 汇总（40 家平台）](../free-llm-api-roundup/index.md)——官方免费额度的正规获取渠道，可作为"免费池"诉求的低风险替代。

```{toctree}
:maxdepth: 2

concepts/index
references/index
log
```
