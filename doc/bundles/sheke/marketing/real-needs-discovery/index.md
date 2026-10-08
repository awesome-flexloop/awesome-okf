---
okf_version: "0.2"
type: bundle
title: 如何找到真需求——需求发现方法论通识
description: "真需求与伪需求之辨的通识知识包——需要/欲望/需求三分、真需求三角与用户价值公式、问/看/算/试四条发现路径、Mom Test 与 JTBD 访谈、MVP 验证谱系与行为证据等级、Kano/ODI/RICE 排序工具、正反案例结构与名言勘误（68 条事实 + 8 条洞察 + 8 篇概念 + 4 篇实操 + 2 篇信源）"
tags: [真需求, 伪需求, 需求发现, 用户访谈, Mom Test, JTBD, MVP, 精益创业, 客户开发, Kano, 需求验证, 营销方法论]
generated: { by: "trae-agent/seven-concepts", at: "2026-10-01T00:00:00+08:00" }
status: stable
stale_after: 2027-10-01
sources:
  - id: classics-index
    resource: /references/01-classics-and-authorities.md
    title: 经典著作与权威出处索引（S1~S31）
  - id: verification
    resource: /references/02-source-verification.md
    title: 待核清单与勘误（P0 条目与未联网核验声明）
---

# 如何找到真需求——需求发现方法论通识

> **⚠️ 性质声明**：本 bundle 为**方法论通识教育知识包**，综合西方经典（科特勒、莱维特、Blank、Ries、Christensen、Ulrich 等）与中文谱系（梁宁、俞军、小米、拼多多实践等）的需求发现方法论。**本次调研基于模型训练知识整理，未执行联网核验**——语录原文、具体金额、出版月份等【P0】条目已集中列入 [待核清单](references/02-source-verification.md)，引用前须查原文。本包不构成经营建议或投资依据。

> **📌 勘误提示（流传口径 → 本 bundle 采用口径）**：① 福特**"如果我问顾客，他们会说要一匹更快的马"无可靠出处**，Quote Investigator 考证未见于福特任何著述（F-063）；② 乔布斯 1998 年 BusinessWeek 访谈原语**语境常被剪裁**——他反对的是"依赖焦点小组设计产品"，而非否定用户研究本身（F-064）。两条名言的误传史本身就是"需求认知极化"的案例（见 [洞察清单](insights.md) 第 5 条）。

"如何找到真需求"是产品、创业与营销的共同元问题。本知识包把分散在三十余部经典与实践案例中的方法组织为一条可执行的链路：**先立判别标准**（需要/欲望/需求三分、真需求三角、用户价值公式、行为证据等级），**再识别伪需求温床**（技术自恋、补贴伪高频、痒点错觉），**然后沿四条互补路径去发现**（问、看、算、试），**用排序工具决定先做什么**（Kano、ODI、RICE），**最后以正反案例与时代边界收束**（福特/乔布斯名言勘误、持续校准、伦理红线）。

本知识包按七概念方法论 R→I→E（叠加 F 本质剖析 + V 对抗审查）生成：68 条事实登记（F-001~F-068，八区），8 条四元组洞察，信源 31 项（S1~S31）全程编号溯源。

---

## 信源说明

| 信源 | 类型 | 覆盖范围 |
|------|------|---------|
| 西方经典著作（科特勒、莱维特、Blank、Ries、Christensen、Ulwick、Kano、von Hippel 等） | 骨架信源（经典著作与提出者官方文本） | 需求本体、问/看/算/试四路径方法论骨架（S1~S21） |
| 中文谱系（梁宁、俞军、小米/拼多多实践、案例媒体组） | 谱系信源（著作 + 公开实践 + 媒体报道） | 真需求三角、用户价值公式、中文正反案例（S22~S27、S30） |
| 考证与采访（Quote Investigator、BusinessWeek 1998） | 勘误信源 | 福特/乔布斯名言考证（S28、S29） |

完整信源登记与距离评估见 [references/01-classics-and-authorities.md](references/01-classics-and-authorities.md)，P0 待核与勘误见 [references/02-source-verification.md](references/02-source-verification.md)。

---

## 📚 知识结构总览

```
real-needs-discovery/
├── concepts/              # 核心概念文档（8篇）
│   ├── 00-what-is-real-need.md         # 本体：三分法、真需求三角、用户价值公式、证据等级
│   ├── 01-fake-need-taxonomy.md        # 伪需求三类温床与自检三问
│   ├── 02-discovery-method-map.md      # 问/看/算/试四路径地图与盲区
│   ├── 03-interview-playbook.md        # 问：Mom Test 三规则 + 客户开发四步
│   ├── 04-jtbd-framework.md            # 换：雇用隐喻 + 四力模型 + switch 访谈
│   ├── 05-validation-loop.md           # 试：BML 循环 + MVP 谱系 + 证据等级
│   ├── 06-need-prioritization.md       # 排序：Kano 五类 + ODI + RICE + PMF 检验
│   └── 07-cases-and-boundaries.md      # 正反案例结构 + 名言勘误 + 时代变量与伦理
├── examples/              # 实操材料（4篇）
│   ├── 01-interview-script-workshop.md # 坏问题→好问题改写工作坊
│   ├── 02-jtbd-switch-interview.md     # switch 访谈提纲与四力标注示范
│   ├── 03-one-week-validation-plan.md  # 一周需求验证计划模板
│   └── 04-need-self-check-list.md      # 需求自检清单（四道门 + 打分卡）
├── references/            # 信源登记簿（2篇）
│   ├── 01-classics-and-authorities.md  # S1~S31 信源登记与距离评估
│   └── 02-source-verification.md       # P0 待核清单、名言勘误、未联网核验声明
├── facts.md               # 68 条事实清单（F-001~F-068，八区）
├── insights.md            # 8 条四元组洞察 + 知识地图
├── index.md               # 本文件
└── log.md                 # 生成日志
```

---

## 🧭 分层导航

### 概念层（[concepts/](concepts/index.md)）

| 文档 | 核心内容 |
|------|---------|
| [什么是真需求](concepts/00-what-is-real-need.md) | 科特勒需要/欲望/需求三分（F-001）；俞军用户价值公式：新体验−旧体验−替换成本（F-005）；梁宁真需求三角：价值-共识-模式（F-007）；行为证据等级：付款>预付>留资>使用>口头>恭维 |
| [伪需求分类学](concepts/01-fake-need-taxonomy.md) | 三类温床：技术自恋（Juicero/Segway）、补贴伪高频（O2O/ofo）、痒点错觉（脸萌）；笨问题自检："撤掉补贴、停掉 PR、放三个月，还剩什么？" |
| [发现方法地图](concepts/02-discovery-method-map.md) | 问（访谈）、看（观察）、算（数据）、试（实验）四路径的适用阶段、各自盲区与双路径交叉原则（F-067） |
| [访谈 Playbook](concepts/03-interview-playbook.md) | Blank 客户开发四步与"走出办公室"（F-011~F-013）；Mom Test 三规则与恭维危险信号（F-014~F-015）；5 Whys 根因追问（F-020）；问题设计负面清单 |
| [JTBD 框架](concepts/04-jtbd-framework.md) | 用户"雇用"产品完成任务（F-016）；奶昔案例（F-017）；推动/拉动/习惯/焦虑四力（F-018）；任务的功能/情感/社会三分（F-019） |
| [验证闭环](concepts/05-validation-loop.md) | BML 循环与 MVP 定义（F-036~F-037）；MVP 五种形态与 pretotyping（F-038~F-041）；PR/FAQ 与不可规模化动作（F-042~F-043）；预售付费级信号（F-044）；pivot/persevere 决策（F-045） |
| [需求排序](concepts/06-need-prioritization.md) | Kano 五类与退化规律（F-028~F-029）；ODI 机会算法（F-030）；RICE 打分（F-031）；PMF 与 40% 检验、留存走平（F-032~F-034） |
| [案例与边界](concepts/07-cases-and-boundaries.md) | 正面案例共同结构（先有行为证据再放大）与反面案例共同结构（供给方自嗨）；福特/乔布斯名言勘误；需求漂移与持续校准；伦理边界 |

### 实操层（[examples/](examples/index.md)）

| 文档 | 核心内容 |
|------|---------|
| [访谈问题改写工作坊](examples/01-interview-script-workshop.md) | 10 个典型坏问题的改写示范与空白练习表 |
| [JTBD switch 访谈提纲](examples/02-jtbd-switch-interview.md) | 时间线还原 + 四力标注的完整访谈脚本 |
| [一周需求验证计划模板](examples/03-one-week-validation-plan.md) | 7 天排期表：假门/落地页/预售三选一，含证据等级达标线 |
| [需求自检清单](examples/04-need-self-check-list.md) | 四道门 + 伪需求三问 + 证据等级打分卡（go/no-go 评估表） |

### 信源层（[references/](references/index.md)）

| 文档 | 核心内容 |
|------|---------|
| [经典著作与权威出处索引](references/01-classics-and-authorities.md) | S1~S31 信源登记：书目信息、信源距离、获取路径 |
| [待核清单与勘误](references/02-source-verification.md) | P0 条目清单（语录/金额/月份）、福特与乔布斯名言勘误、未联网核验声明 |

### 事实与洞察

| 文档 | 核心内容 |
|------|---------|
| [事实清单](facts.md) | F-001~F-068 共 68 条，按"需求本体/问/看/算/试/正面案例/反面案例/边界"八区登记，三级可信度标注（P0 待核 / P1 高置信 / P2 分析判断） |
| [洞察清单](insights.md) | 8 条四元组洞察（陈述/证据/反常识点/行动启示）+ Mermaid 知识地图（四道门 + 四路径 + 持续校准环） |

---

## ✅ 信任与生命周期说明

- **文档版本**：基于模型训练知识整理生成（2026-10-01），**未执行联网核验**
- **覆盖事实**：共 68 条（F-001 ~ F-068，八个主题区）
- **核验情况**：骨架方法论事实为方法论共同体长期复用的稳定框架【P1】；语录原文、具体金额、出版月份等细节为【P0】待复核，已集中列入 [待核清单](references/02-source-verification.md)，正文按标注呈现、不作权威引用
- **status**：stable — 骨架层跨周期有效；P0 条目不进入论证链关键环节，不触发 flagged
- **stale_after**：2027-10-01 — 方法论骨架跨周期有效；案例数字与平台语境为时点快照（规则时点 2026-10）
- **方法论链路**：R（双谱系调研与事实登记）→ I（八区事实 → 8 条四元组洞察）→ E（信源先行 + 概念/实操成文）→ V（四视角对抗审查），详见 [log.md](log.md)

### 已知边界

1. **未联网核验**：全部内容基于模型训练知识整理。凡标注【P0】的条目（语录原文、具体金额、出版月份），在公开引用、教学或决策引用前必须查原文复核（清单见 references/02）。
2. **分析性组织为本包观点**【P2】：四路径划分（问/看/算/试）、证据等级排序、伪需求三温床、四道门等框架是本包对多家方法的综合组织，不是某一著作的原始分类；引用时应表述为"本知识包的组织框架"。
3. **案例数字为公开报道口径**：Dropbox/Airbnb/拼多多/ofo 等案例的金额与时间为媒体公开口径的时点快照，随时间与统计口径变化；教学可用，投资或经营决策不可直接用。
4. **中文谱系的转述边界**：梁宁《真需求》、俞军产品方法论等版权内容以公开出版信息与公开访谈为中介进行综合转述，不逐字转录原文；精确引语须查原书。
5. **视角偏向 2C 与互联网产品**：证据等级与验证节奏以消费者产品和互联网服务为中心语境；2B、硬科技、医药等长周期高合规行业的验证设计需另行调整。

---

**本知识包共收录 16 个内容文档（8 个概念 + 4 个实操 + 2 个信源 + 事实清单 + 洞察清单），外加 3 个子目录索引、根索引与生成日志，合计 21 个文件。**

同组相关：[sell-before-build-validation](../sell-before-build-validation/index.md)（需求验证的逆向顺序——本包"试"路径与证据等级的姊妹篇，发现→验证闭环）；[marketing-fundamentals](../marketing-fundamentals/index.md)（营销系统通识：STP、定位、4P/4C、AARRR、内容私域与合规）。

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
