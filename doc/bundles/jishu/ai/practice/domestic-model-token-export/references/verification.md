# P0 权威核验报告

> 核验日期：2026-09-09 | bundle 状态：**flagged**（因 F-004 核心错误 + F-007 内部矛盾）

## 核验方法

对博文中的每条 P0 声明进行独立权威信源比对，包括：官方定价页、权威数据平台、政府/国际组织公告。

---

## F-001：Claude Opus 4.x 输入价格 $5/MTok ✅

| 项目 | 内容 |
|------|------|
| 博文口径 | Claude Opus 4.x 输入 $5/百万Token |
| 权威信源 | Anthropic 官方定价页（claude.ai/pricing / docs.anthropic.com/en/docs/model-reference） |
| 核验结果 | **正确**。Claude Opus 4 输入定价为 $5/MTok（输出 $25/MTok），与博文一致。 |

---

## F-002：GPT-4 系列输入 $3/MTok ⚠️

| 项目 | 内容 |
|------|------|
| 博文口径 | GPT-4 系列输入 $3/百万Token |
| 权威信源 | OpenAI 官方定价页 |
| 核验结果 | **表述模糊**。GPT-4 系列各型号定价差异大：GPT-4 Turbo 输入 $10/MTok，GPT-4o 输入 $2.5/MTok，GPT-4.1 输入 $2/MTok。$3/MTok 无法对应任何单一型号。博文可能是在粗略估算或笔误。 |
| 修正建议 | 明确具体模型名称和型号版本，或在首次出现时标注"大致范围"。 |

---

## F-003：OpenRouter 中国模型 Token 份额超美国 ✅

| 项目 | 内容 |
|------|------|
| 博文口径 | OpenRouter 中国模型 Token 份额约63%，超过美国 |
| 权威信源 | macgpu.com（2026-07-01）、Superpower Daily（2026-08-27）、OpenRouter 官方博客 |
| 核验结果 | **基本正确，口径需澄清**。2026年6月数据：① 前10名中中国厂商（DeepSeek/小米/MiniMax/腾讯/Qwen）合计约 46%；② 含 Moonshot(Kimi)等全量中国模型约 60-63%。美国模型（Google/OpenAI/Anthropic）合计约 30%。两个数字都是真实的，但统计口径不同。 |

---

## F-004：WTO 电子商务关税暂停令"豁免期延长" ❌【核心错误】

| 项目 | 内容 |
|------|------|
| 博文口径 | WTO 电子商务关税暂停令"豁免期延长" |
| 权威信源 | [USTR 2026-03-30](https://www.ustr.gov/about/policy-offices/press-office/press-releases/2026/march/press-release-regarding-wtos-14th-ministerial-conference)、[EU Trade 2026-03-30](https://policy.trade.ec.europa.eu/news/outcome-14th-wto-ministerial-conference-2026-03-30_en)、[PwC 2026-04-02](https://www.pwc.com/gx/en/tax/newsletters/tax-policy-bulletin/assets/pwc-wto-e-commerce-developments.pdf) |
| 核验结果 | **❌ 错误，方向完全相反**。2026年3月26-30日在喀麦隆雅温得举行的 MC14 上，巴西和土耳其阻止了延长动议，WTO 电子商务关税暂停令（自1998年MC2确立，已运行28年）**未获延期，于2026年3月30日首次失效**。66个成员（占全球贸易70%）另达成诸边《电子商务协定》 interim implementation，但多边暂停令本身已失效。 |
| 影响评估 | 博文用此论据支持"中国利用规则窗口期低价出海"，若规则未延长反而失效，则中国模型面临的关税风险从"政策不确定"变为"可能已被征税"，逻辑链条需重新审视。 |

---

## F-005：杰文斯悖论定义 ✅

| 项目 | 内容 |
|------|------|
| 博文口径 | 提高资源利用效率反而导致总消耗量上升，出自1865年Jevons《煤炭问题》 |
| 权威信源 | William Stanley Jevons《The Coal Question: An Inquiry into the Progress of the Nation, and the Probable Exhaustion of our Coal-Mines》(1865) |
| 核验结果 | **正确**。杰文斯悖论（Jevons Paradox）即：技术进步提高资源利用效率后，单位产出的资源消耗下降，但总消耗量反而上升（因为需求扩大）。博文对该概念的引用准确。 |

---

## F-009：Stripe 收购 OpenRouter ✅

| 项目 | 内容 |
|------|------|
| 博文口径 | 2026年8月16日 Bloomberg 报道，Stripe 收购 OpenRouter，70亿+美元 |
| 权威信源 | [Bloomberg 2026-08-16](https://www.bloomberg.com/news)、[Artur Markus 分析](https://www.arturmarkus.com/stripe-acquires-ai-gateway-openrouter-for-7-billion-5-4x-valuation-jump-in-three-months/)、[Axios 2026-08-19](https://explainx.ai/blog/stripe-acquires-openrouter-7-billion-august-2026) |
| 核验结果 | **基本正确**。Bloomberg 2026-08-16 报道 Stripe 以超过70亿美元收购 OpenRouter。Axios 2026-08-19 引用 Stripe 投资者信件，称交易金额可能超过80亿美元（大部分为股票）。OpenRouter 2026年5月刚完成 Series B，估值13亿美元，三个月内估值翻5倍以上。Stripe 称此为"史上最大收购"。 |

---

## 勘误四张清单

### ① 日期/版本表

| 项目 | 博文口径 | 权威核验 | 差异等级 |
|------|---------|---------|---------|
| WTO 关税暂停令 | "豁免期延长" | 2026年3月MC14未获延期，28年来首次失效 | ❌ 核心错误 |
| GPT-4 输入价格 | "$3/百万Token" | 应明确为 GPT-4o（$2.5/MTok输入）或 GPT-4.1（$2/MTok） | ⚠️ 模糊 |

### ② 成效数字溯源表

无厂商自宣成效数字（本文为分析评论，非厂商软文），不涉及。

### ③ 口径对照表

| 声明 | 博文口径 | 建议修正口径 |
|------|---------|-------------|
| 中国模型份额 | "约63%" / "近50%" 两个数字混用 | 区分统计口径：①前10名中国厂商合计~46%；②含Moonshot等全量中国模型~60-63% |
| DeepSeek V3.2 Token | 正文745B vs 表格845B | 以正文为准，标注数据时点 |
| MiniMax M2.5 Token | 2.57T | 注明为周数据，对比时用同期口径 |

### ④ 引文逐字核对表

无官方引文，不涉及。

---

## 权威数据补充（非博文来源，用于 bundle 正文）

| 数据项 | 数值 | 来源 |
|--------|------|------|
| 2025年6月美国模型OpenRouter份额 | ~70% | OpenRouter + Exponential View（Bloomberg 引用） |
| 2026年6月美国模型OpenRouter份额 | ~30% | 同上 |
| 2026年6月中国模型OpenRouter份额 | ~60-63% | macgpu.com（2026-07-01）、Superpower Daily（2026-08-27） |
| WTO 电子商务关税暂停令生效时间 | 1998年 MC2 | [WTO官方](https://www.wto.org/english/tratop_e/ecom_e/mindec1_e.htm) |
| WTO 关税暂停令失效时间 | 2026年3月30日 MC14 | [USTR 2026-03-30](https://www.ustr.gov/about/policy-offices/press-office/press-releases/2026/march/press-release-regarding-wtos-14th-ministerial-conference) |
| Stripe 收购 OpenRouter 宣布时间 | 2026年8月16日 | Bloomberg |
| Stripe 收购 OpenRouter 价格 | >$70亿（Axios称可能>$80亿） | Bloomberg / Axios |
| OpenRouter 用户规模 | ~800万开发者 | OpenRouter 官方 + Stripe 投资者信件 |
| OpenRouter 模型数量 | 400+ | OpenRouter 官方 |
| Claude Opus 4.8 质量指数 | 61.4（#1） | Artificial Analysis 2026年5月 |
| DeepSeek V4 Flash 日均Token | 619B（2026年6月） | officechai.com / macgpu.com |
