# 更新日志

## 2026-10-28

### 创建

- 初始化 `financial-economics` 知识包（OKF v0.2），作为 `sheke/finance` 分组的金融经济通识底座，与 `personal-investing`（个人决策）、`pipeline-story`（收入管道）、`ponzi-scheme`（防骗）形成「系统—个人—观念—风险」四束分工。
- 创建 11 篇概念文档、4 篇教学算例、2 篇信源/核验文档，以及 `facts.md`（104 条事实、S1–S45 信源）、`insights.md`（6 条四元组洞察 + Mermaid 知识地图）、根 `index.md` 与三处子索引。

### 结构

- `concepts/`：00-finance-and-economy、01-money-credit、02-interest-valuation、03-financial-institutions、04-financial-markets、05-macro-framework、06-monetary-policy、07-international-finance、08-risk-and-crisis、09-china-financial-system、10-digital-finance、11-financial-literacy。
- `examples/`：01-money-multiplier（货币乘数与 M2 敏感性）、02-tvm-bond-valuation（房贷/NPV/债券/久期）、03-portfolio-capm（组合风险/夏普/CAPM）、04-leverage-bank-run（杠杆/挤兑/折价抛售）。
- `references/`：01-classics-and-authorities（四层信源索引）、02-verification（P0 核验与口径说明）、index（阅读顺序）。
- `facts.md`：12 个主题小节，F-001–F-104 连续编号；S1–S45 信源登记；口径说明；放弃核验清单。
- `insights.md`：6 条四元组洞察（功能与金融化 / 货币与宽信用 / 利率与久期 / 银行脆弱性与监管 / 宏观政策边界 / 数字金融与素养）+ 知识地图。

### R 阶段（事实采集与信源分层）

- 理论事实：Mishkin《货币金融学》、Bodie《投资学》、Mankiw《宏观经济学》、Krugman《国际经济学》、Hull《衍生品》为骨架；King & Levine (1993)、Diamond & Dybvig (1983)、Fama (1970)、Solow (1956)、Friedman/Phelps (1968)、Taylor (1993)、Bernanke (2020)、Minsky (1986)、Kindleberger (1978)、Kahneman & Tversky (1979)、Odean (1998/1999) 为论文源头。
- 制度事实：人民银行（货币层次、社融、LPR、资管新规、e-CNY）、国务院（存款保险）、证监会/上交所/北交所（多层次资本市场）、金融监管总局/外汇局/统计局/财政部（监管架构、外汇、核算、地方债与房地产金融）。
- 国际标准：BIS（Basel III、外汇调查、BigTech/DeFi）、IMF（WEO、BPM6、SDR）、FSB（G-SII、稳定币）、FATF（旅行规则）、OECD/INFE（金融素养）、欧盟 MiCA。

### V 阶段（核验与一致性）

- P0 核验：日期、比率、制度安排、统计口径、历史节点逐类对照；结论见 `references/02-verification.md`。关键节点包括：存款保险 2015-05-01/50 万元、Basel III 2010/2017、资管新规 2018-04-27、科创板 2019-07-22、北交所 2021-11-15、人民币入 SDR 2016-10-01 与 2022 权重 12.28%、e-CNY 白皮书 2021-07、2021-09-24 虚拟货币通知。
- 口径留痕：M1 2025 年口径修订、社融与 M2 的区别、「全球第一/第二」排名的时间性、财政乘数与 QE 效果的争议、房地产金融参数的动态性。
- 已知边界：不写实时数据；不荐产品；不预测利率/汇率/股价/房价/增速；中国监管参数以官方最新发布为准。
- 索引接入：`sheke/finance/index.md` total_bundles 3→4；`sheke/index.md` finance 组行 3→4 束并更新描述；`bundles/index.md` total_bundles 687→688、sheke 域 82→83 束、finance 组行 3→4。
- 门禁：`python scripts/check-bundles-index.py` 通过（9 域 / 63 组 / 688 束，五面一致）；`python scripts/check-toctrees.py` 通过（零断链、零孤立内容）。

### V 修复（2026-10-28）

- 示例 02 IRR 试算表原值有误：21% 时 NPV 应为约 +1.08、22% 时约 −0.58，IRR≈21.65%；已修正表格与插值行。
- F-001 信源由 S1、S2 收敛为 S1；F-008 由 S4、S6 收敛为 S4；F-015 由 S1、S7 改为 S1、S6（S6 为 BoE 2014 原始文献）。
- F-097 一处英文术语改为中文「敏感性递减」。
- 05 篇修正「三驾马车」表述；07 篇删除一处误标 F 编号；10 篇将英文投顾缩写改为中文；11 篇修正一处繁体字与一处英文标题词。
- 复核：25 个 .md 全部 UTF-8 严格解码；F-001–F-104 连续无跳号；全部相对链接可达；无 `file:///`、无本机绝对路径。
- Sphinx dummy build 未运行：当前 Python 环境未安装 sphinx（ModuleNotFoundError），以两条仓库门禁 + 手动等效清单替代；未声称 Sphinx 通过。

### 待复核

- 中国监管架构、货币统计口径、国际监管框架若在 2027-12-31 前发生重大变化，优先复核 F-012、F-032、F-077–F-088、F-095–F-096。
- 本包未做逐条网页原文抓取；P0 以教科书/官方文件对照为主，具体法律与合规判断应以官方最新文本为准。
