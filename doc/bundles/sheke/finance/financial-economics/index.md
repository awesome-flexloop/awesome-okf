---
type: OKF
title: 金融经济通识知识包
description: 面向零基础读者的金融经济系统教程：金融体系功能、货币与信用、利率与估值、银行与金融机构、金融市场、宏观框架、货币政策、国际金融、风险与危机、中国金融监管、数字金融与金融素养；104 条事实双信源溯源（教科书/经典论文 + 中国官方/国际标准），含 4 篇可复算例与 6 条架构洞察。
tags: [finance, economics, 金融, 经济, 货币, 利率, 银行, 金融市场, 宏观经济学, 货币政策, 国际金融, 金融危机, 中国金融, 数字金融, 金融素养]
version: "1.0.0"
okf_version: "0.2"
sources:
  - id: classics
    resource: /references/01-classics-and-authorities.md
    title: 金融经济经典教科书、经典论文与权威信源索引
  - id: verification
    resource: /references/02-verification.md
    title: P0 核验报告与口径说明
  - id: facts-inventory
    resource: /facts.md
    title: 金融经济通识事实清单（104 条）
generated: { by: "lobsterai-agent/financial-economics", at: "2026-10-28T10:15:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-28T10:30:00+08:00" }
status: stable
stale_after: 2027-12-31
---

# 金融经济通识知识包

本知识包是一条「从金融体系总图到个人决策」的系统学习路径。它不追热点、不荐产品、不预测点位，而是把教科书级的机制、中国官方的制度事实与国际组织的监管标准放在同一张地图上，让你能读懂财经新闻背后的逻辑，也能识别「高收益低风险」话术的漏洞。

全部事实按「F 编号 + S 编号」双层溯源：**理论事实**挂 Mishkin、Bodie、Mankiw、Krugman、Hull 等教科书与经典论文；**制度事实**挂人民银行、国务院、证监会、金融监管总局、外汇局、统计局等官方文件；**国际标准**挂 BIS、IMF、FSB、OECD、FATF 等机构。共 104 条事实、45 个信源（S1–S45），P0 核验结论见 [核验报告](references/02-verification.md)。

> 阅读提示：本包讲的是**机制与框架**，不是实时数据。利率、汇率、GDP 增速、市值等会变化，具体数值请以官方最新发布为准；中国监管参数（首付比例、房贷利率下限等）按城市与周期动态调整，正文只写工具类型不写死具体比例。**本包为通识教育材料，不构成投资建议、法律意见或政策建议。**

## 快速导航

### [概念文档](concepts/index.md) — 11 篇核心概念

- [金融与经济：金融体系到底做什么](concepts/00-finance-and-economy.md) — 资金循环、六项功能、直接/间接融资、金融深化、金融化争议
- [货币、信用与货币创造](concepts/01-money-credit.md) — 货币四职能、M0/M1/M2、基础货币、货币乘数、贷款创造存款、货币数量论
- [利率、现值与资产定价基础](concepts/02-interest-valuation.md) — 费雪方程、复利、年金、NPV/IRR、债券定价、YTM、久期、期限结构
- [金融机构与银行体系](concepts/03-financial-institutions.md) — 资产负债表、期限转换、挤兑、存款保险、最后贷款人、巴塞尔 III、影子银行
- [金融市场与工具](concepts/04-financial-markets.md) — 货币/资本市场、一级/二级、股票/债券/外汇/衍生品、流动性、EMH、多层次资本市场
- [宏观经济学核心框架](concepts/05-macro-framework.md) — GDP、通胀、失业、潜在产出、AD-AS、财政乘数、索洛、菲利普斯曲线
- [货币政策与中央银行](concepts/06-monetary-policy.md) — 央行目标、三大工具、利率走廊、五条传导、泰勒规则、QE、双支柱、时滞
- [国际金融与开放经济](concepts/07-international-finance.md) — 汇率、PPP、利率平价、国际收支、外储、三元悖论、美元体系、SDR
- [金融风险与危机](concepts/08-risk-and-crisis.md) — 七类风险、杠杆、明斯基、泡沫、挤兑、2008 危机、系统性风险、宏观审慎
- [中国金融体系与监管](concepts/09-china-financial-system.md) — 一行一局一会、社融、LPR、资管新规、债市、科创板/北交所、外汇、地方债、e-CNY
- [数字金融与金融科技](concepts/10-digital-finance.md) — 移动支付、大科技信贷、加密资产、稳定币、CBDC、DeFi、FATF/MiCA、AI 风险
- [金融素养：把宏观框架落回个人决策](concepts/11-financial-literacy.md) — 三要素、资产负债表、实际收益、费用、分散化、行为偏差、防骗

### [实践示例](examples/index.md) — 4 篇可复算例

- [货币乘数与货币供给算例](examples/01-money-multiplier.md) — 基础货币 100 亿元下的乘数、M2、存款与准备金拆分，含敏感性表
- [现值、年金与债券定价算例](examples/02-tvm-bond-valuation.md) — 100 万元房贷月供、项目 NPV/IRR、三年期债券价格与久期近似
- [组合风险、分散化与 CAPM 算例](examples/03-portfolio-capm.md) — 两类资产组合的收益/方差/夏普比率、相关系数影响、CAPM 与阿尔法
- [杠杆、挤兑与危机推演算例](examples/04-leverage-bank-run.md) — 银行资本对贷款损失、存款流失与折价抛售的敏感度；明斯基阶段映射

### [信源参考](references/index.md) — 2 篇信源与核验文档

- [经典教科书、经典论文与权威信源索引](references/01-classics-and-authorities.md) — 四层信源（教科书/论文/国际标准/中国官方）与 11 篇概念的对应关系
- [P0 核验报告与口径说明](references/02-verification.md) — 日期、比率、制度安排、统计口径的核验结论、口径差异与单源项

### 工作文档

- [事实清单](facts.md) — 104 条事实（关键条目标【P0】）、S1–S45 信源登记、口径说明与放弃核验清单
- [架构洞察](insights.md) — 6 条四元组洞察与金融经济知识地图
- [更新日志](log.md)

## 快速开始

- **完全零基础**：[00 金融与经济](concepts/00-finance-and-economy.md) → [01 货币与信用](concepts/01-money-credit.md) → [02 利率与估值](concepts/02-interest-valuation.md) → [05 宏观框架](concepts/05-macro-framework.md)。
- **想看懂财经新闻**：[05 宏观框架](concepts/05-macro-framework.md) → [06 货币政策](concepts/06-monetary-policy.md) → [09 中国金融](concepts/09-china-financial-system.md) → [02 利率与估值](concepts/02-interest-valuation.md)。
- **想理解银行与危机**：[03 金融机构](concepts/03-financial-institutions.md) → [08 风险与危机](concepts/08-risk-and-crisis.md) → [杠杆与挤兑算例](examples/04-leverage-bank-run.md)。
- **想理解中国金融**：[09 中国金融](concepts/09-china-financial-system.md) → [06 货币政策](concepts/06-monetary-policy.md) → [01 货币与信用](concepts/01-money-credit.md)。
- **想理解数字金融**：[10 数字金融](concepts/10-digital-finance.md) → [04 金融市场](concepts/04-financial-markets.md) → [08 风险与危机](concepts/08-risk-and-crisis.md)。
- **只关心个人决策**：[02 利率与估值](concepts/02-interest-valuation.md) → [11 金融素养](concepts/11-financial-literacy.md) → [个人投资实操通识](../personal-investing/index.md)。

## 知识包立场

| 维度 | 本知识包的处理方式 |
|------|------------------|
| 内容性质 | 金融经济机制与中国制度框架的通识教程，面向零基础读者与需要宏观视角的职场人 |
| 事实与观点 | 104 条事实双信源溯源；理论挂教科书/论文，制度挂官方文件，国际标准挂 BIS/IMF/FSB/OECD/FATF；判断性内容入 insights.md 并与事实分层 |
| 时效处理 | 不写死 GDP、CPI、汇率、市值等实时数据；中国监管参数标注「以官方最新发布为准」；stale_after 设为 2027-12-31 |
| 争议处理 | 财政乘数、QE 效果、金融化、EMH、泡沫识别等标注「经验估计/学界争议」，不把假说写成定律 |
| 边界声明 | 不推荐任何金融产品、机构、股票、基金、债券或加密资产；不预测利率、汇率、股价、房价与经济增速 |
| 免责声明 | 通识教育不构成投资建议、法律意见或政策建议；具体决策请咨询持牌专业人士并核对官方文件 |

## 推荐学习路径

```text
建总图：00 金融与经济（六功能、直接/间接融资）
懂货币：01 货币与信用（M0/M1/M2、货币乘数、贷款创造存款）
会折现：02 利率与估值（复利、年金、债券、久期）
看机构：03 金融机构（资产负债表、挤兑、监管）
认市场：04 金融市场（股票/债券/外汇/衍生品、EMH）
搭宏观：05 宏观框架（GDP、通胀、失业、AD-AS）
懂政策：06 货币政策（工具、传导、QE、双支柱）
开视野：07 国际金融（汇率、收支、三元悖论）
识风险：08 风险与危机（杠杆、明斯基、2008）
落中国：09 中国金融（一行一局一会、社融、LPR、资管新规）
看数字：10 数字金融（支付、信贷、加密资产、CBDC）
回个人：11 金融素养（资产负债表、费用、行为偏差、防骗）
```

## 主题关联

- **与 [个人投资实操通识](../personal-investing/index.md) 的分工**：本包讲「金融系统如何运转」，该包讲「个人如何做投资决策」。本包的 02、05、06、08、11 是该包的理论背景；该包的资产配置、定投、行为纪律是本包的落地应用。
- **与 [庞氏骗局](../ponzi-scheme/index.md) 的分工**：本包讲信用、杠杆与危机机制；该包讲庞氏结构的识别、案例与救济。两者的连接点是「借新还旧」与「高收益低风险」的不可持续性。
- **与 [数字经济与数字资产](../../digital-economy/index.md) 的分工**：本包讲数字金融的金融机制与监管；该分组讲数字经济的测度、数据要素与数字资产制度。加密资产/稳定币/CBDC 的具体监管细节可交叉阅读。
- **与 [中国金融稳定报告](https://www.pbc.gov.cn) 的关系**：本包提供框架，官方报告提供最新数据与风险评估；两者配合使用，不用本包替代官方数据。

## 已知边界

1. 本包不覆盖会计、公司财务、保险精算、金融工程定价的完整技术细节；这些需要专门教材。
2. 中国监管架构与政策参数会变化；本包以 2026-10 前的公开文件为基准，引用前请核对官网最新文本。
3. 国际金融部分以主要经济体与美元体系为主，不覆盖每个国家的汇率制度细节。
4. 数字金融部分不构成对任何加密资产、稳定币、DeFi 协议或交易平台的投资/使用建议。
5. 本包不提供实时数据接口；高频数据请查人民银行、国家统计局、IMF、BIS、World Bank 等官方来源。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
