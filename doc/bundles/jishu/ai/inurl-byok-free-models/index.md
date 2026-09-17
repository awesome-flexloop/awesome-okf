---
okf_version: "0.2"
type: bundle
title: "inurl BYOK 密钥聚合与四个免费模型（推广文核验）"
description: "微信公众号推广文经 OKF v0.2 七阶段转化——inurl 聚合 APIToken 的 BYOK 统一令牌、端到端加密与本地代理机制核验，及 Agnes/GLM-4-Flash/硅基流动/LongCat 四个免费模型官方口径对照。flagged：标题省钱数字无出处、Agnes 国籍与上下文两处硬错。非操作教程。"
tags: [byok, inurl, api-token, 密钥管理, 免费模型, agnes, glm-4-flash, siliconflow, longcat, 厂商自宣, flagged]
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
    url: https://mp.weixin.qq.com/s/xbpFUmp2s87BUbcFagwQ0A
  - id: inurl-official
    url: https://token.inurl.link/
  - id: agnes-wiki
    url: https://wiki.agnes-ai.com/zh-Hans/docs/agnes-25-flash
  - id: agnes-pr
    url: https://www.prnewswire.com/apac/news-releases/sapiensai-launches-agnes--singapores-homegrown-answer-to-deepseek-302443885.html
  - id: zhipu-glm4
    url: https://docs.bigmodel.cn/cn/guide/models/text/glm-4
  - id: siliconflow-docs
    url: https://docs.siliconflow.cn/cn/userguide/rate-limits/rate-limit-and-upgradation
  - id: meituan-longcat2
    url: https://tech.meituan.com/2026/06/30/LongCat2.0.html
  - id: longcat-docs
    url: https://longcat.chat/platform/docs/zh/
---

# inurl BYOK 密钥聚合与四个免费模型（推广文核验）

> **⚠️ 状态：`flagged`** — 博文标题核心数字"一年省下 5000 块 Token 费用"查无出处且与商业模式不符（F-007）；Agnes AI 存在两处事实硬错（**国籍应为新加坡而非美国**；**agnes-2.5-flash 上下文官方为 512K 而非百万**）；主推产品运营主体匿名、全网第三方独立证据为零。完整勘误见 [references/verification.md](references/verification.md)，2026-12-16 前安排复核。

> **🏷️ 厂商自述数据提示** — 本 bundle 信源为 token.inurl.link 的导流推广文（厂商自宣）。产品安全承诺（"永不中转/云端零请求/不会封号"）仅见于其官网与闭源客户端，无第三方审计；文中所有"省钱"叙事均不构成独立事实。涉及额度/能力的数字已全部改以四家模型厂商**官方页面 2026-09-16 口径**呈现。

> **类型**：技术综述/资讯盘点（**非操作教程，无 examples/**）——原文 PART 04 仅为口号，无代码、无配置步骤、无实测数据，不满足"操作可复现性两问"。

## 本文概要

2026 年 9 月，公众号「风信旗」以"一年省 5000 块"为钩子推广「inurl · 聚合 APIToken」——一个 BYOK（自带密钥）路线的多厂商 Key 聚合工具，并附 4 个免费模型（Agnes AI、智谱 GLM-4-Flash、硅基流动、美团 LongCat）导流链接。本 bundle 经 OKF v0.2 七阶段工作流（R 事实采集 → P0 权威核验 → I 三层拆分 → E 信源先行 → V 对抗审查）完成转化，回答三个问题：

1. **产品事实**：inurl 的统一令牌/本地加密/escrow/本地代理各有几分证据？（[concepts/00](concepts/00-byok-token-landscape.md)）
2. **机制与风险**：BYOK 与 API 中转架构差在哪？加密机制如何工作？闭源运营下信任边界是什么？（[concepts/01](concepts/01-bring-your-own-key-security.md)）
3. **免费资源核实**：4 个模型 2026-09 真实免费政策、上下文、领取前提与限速是什么？（[concepts/02](concepts/02-four-free-models.md)）

## 核心勘误摘要

| # | 博文口径 | 核验结论 | F 编号 |
|---|---------|---------|--------|
| 1 | 一年省下 5000 块 Token 费用（同事年度账单） | ❌ 全网及官网查无出处；BYOK 不经手 token 售卖，不产生该价差 | F-007/F-029 |
| 2 | Agnes AI（**美国**） | ❌ 实为**新加坡** Sapiens Technology | F-017/F-030 |
| 3 | agnes-2.5-flash **百万级**上下文 | ❌ 官方 **512K**；1M 属已废弃 2.0 临时窗口 | F-017/F-031 |
| 4 | Agnes"完全免费" | ⚠️ 阶段性 $0 优惠 + 20 RPM，付费档并存 | F-032 |
| 5 | LongCat 注册送 1000 万、万亿参数、1M 上下文 | ⚠️ 均属实但需限定：**实名领取/30 天/限时**；万亿与 1M 仅属 LongCat-2.0 | F-035 |
| 6 | 硅基免费体验 Qwen/DeepSeek/GLM | ⚠️ 免费为 9B 级开源版，无 GLM-4-Flash、DeepSeek 满血付费；现行 ¥16 券 | F-034 |
| 7 | inurl"永不中转/不封号"、主体可查 | ⚠️ 仅闭源自述；无备案/无公司/无第三方证据 | F-014/F-026/F-029 |
| — | 智谱 GLM-4-Flash ¥0 完全免费 | ✅ 属实（128K，V0 并发 200） | F-018/F-033 |

## 文档结构

### concepts/ — 概念解析

| 文档 | 主题 |
|------|------|
| [00-byok-token-landscape.md](concepts/00-byok-token-landscape.md) | 事实层：博文叙事、产品事实卡、信源距离三层模型、匿名运营风险 |
| [01-bring-your-own-key-security.md](concepts/01-bring-your-own-key-security.md) | 机制层：BYOK vs 中转架构图、AES-256-GCM/PBKDF2/双份 escrow 原理、使用前自查清单 |
| [02-four-free-models.md](concepts/02-four-free-models.md) | 资源层：4 个免费模型官方口径对照（2026-09-16 时点） |

### references/ — 信源登记

| 文档 | 说明 |
|------|------|
| [article-source.md](references/article-source.md) | 博文事实清单（F-001 至 F-035，与主仓库 spec 双份一致） |
| [verification.md](references/verification.md) | P0 核验报告：勘误四张清单、信源分级、残留不确定性 |

## 主题关联

- [🔑 inurl 统一令牌与免费模型省钱实录核验](../inurl-unified-token/index.md)：**同产品姊妹束**——同公众号 2026-09-02《一个程序员的省钱实录：从月付 500 到 0 元》的转化（另一信源，70 条事实），聚焦免费档厂商数量限制（3 个）、付费档位与接入配置演练；与本束（09-04 文章，聚焦 BYOK 机制与 4 家免费模型核验）互补
- [📊 2026免费大模型API汇总（40家平台）](../free-llm-api-roundup/index.md)：知乎博文转化的免费平台全景盘点（23 国内 + 17 国际）——本 bundle 是其"4 家精选 + 聚合工具"视角的姊妹篇，该 bundle 当前同为 `flagged`（部分平台额度已变动）
- [💥 Token经济大爆发](../token-economy-explosion/index.md)：Token 调用量宏观与 ATH/Token Hub 政策背景，解释"省钱叙事"的行业语境
- [🤖 Agnes AI 大模型生态](../agnes-ai/index.md) / [🎬 Agnes AI 与 Pavo 创作平台](../agnes-pavo/index.md)：Agnes 官方 API 模型目录的完整源码式教程与创作平台实践（agnes-2.5-flash 512K 上下文的本库权威记录）
- [💳 DeepSeek-V4 免费方案与 API 定价](../deepseek-pricing/index.md)：免费额度 + 峰谷定价的另一类省钱路径参照

## 已知边界

- **厂商自宣信源**：产品功能与安全承诺无第三方独立证据，运营主体匿名；本 bundle 不构成对该工具的使用推荐或安全背书。
- **额度时效**：所有免费额度/赠金为 2026-09-16 官方页面口径，Agnes 明示"阶段性优惠"、LongCat 为限时活动、硅基活动至 2026-12-31；`stale_after: 2026-12-16`。
- **未做动态验证**：未注册 inurl、未运行其本地代理做抓包审计，"零云端请求"仅停留在客户端代码静态层面。
- **LongCat 活动状态**：1000 万 Tokens 活动页需登录，未登录无法确认当前仍可领取。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
