---
okf_version: "0.2"
type: index
bundle: l1b3rt4s
version: 0.1.0
description: |
  L1B3RT4S 越狱提示词研究库知识包：34 个厂商 .mkd 越狱档案的攻击面测绘。
  覆盖仓库定位与档案形态（显式模板与隐写载体两大形态、内容三分层、攻守同构闭环）、
  攻击技术分类学 T1–T10（四族十类、指纹要素、代际演化）、防御视角反哺
  （类别级防御、tokenizer 与字符编码层观测、授权类条款弱点）、负责任披露与研究伦理、
  防御性红队评估工作流示例，以及完整档案编目参考。
  本束为研究性中性转述：只登记结构与类别机制，不收录任何可操作攻击载荷。
concepts:
  - mission-attack-research: 攻击面研究定位与档案形态（两大形态、内容三分层、攻守同构）
  - attack-taxonomy: 攻击技术分类学（T1–T10 四族十类、指纹表、代际演化）
  - defense-perspective: 防御视角反哺（类别级防御、tokenizer 观测、授权弱点补偿）
  - responsible-disclosure: 负责任披露与研究伦理（AGPL、披露渠道、法律边界）
references:
  - catalog: 档案编目参考（34 厂商 .mkd 全表、10 杂项文件、计数断言）
examples:
  - redteam-workflow: 防御性红队评估工作流（类别覆盖矩阵与观测指标）
---

# L1B3RT4S：越狱提示词研究库（防御视角档案）

L1B3RT4S 是红队研究者 elder-plinius 维护的公开仓库，以 34 个厂商/实体命名的 .mkd 文件逐厂商登记越狱攻击面，配套 7,895 条 glitch token 编目数据库（`*SPECIAL_TOKENS.json`）、`!` 前缀指令别名集与 Unicode 隐写载体文件群 (F-L1-008/009/014)。仓库 README 极简且无伦理章节 (F-L1-002)，以 AGPL-3.0 发布 (F-L1-004)。本知识包是这批档案的**防御视角研究性转述**：从攻击者视角回答“对齐防线在哪里、以何种方式失守”，并把观察到的手法提炼为可供防御方使用的类别体系（T1–T10）。

> ⚠️ **用途限定声明（先读）**：本束内容**仅用于 AI 安全研究与防御评估**。全部转述遵循研究性登记纪律——攻击技术一律采用学术分类命名，描述到“类别机制”层为止；不提供、不复现任何可操作的越狱载荷、注入模板或绕过手法；文中结构示意均为占位符骨架。指纹要素（divider 字样、开关声明、占位符）仅用于归因分析。请勿将本束内容用于绕过任何在役系统的安全策略，或违反上游许可与目标厂商服务条款的场景。

> **信任声明**
>
> - **信源**：elder-plinius/L1B3RT4S 上游仓库（https://github.com/elder-plinius/L1B3RT4S ），本地只读副本 `external/dao/action/elder-plinius/L1B3RT4S`，锚定 **git HEAD `64960b783249d36f76a48a33103cc4b168332b9b`**；工作树文件均为已删除状态，内容仅以 `git ls-tree` / `git show` / `git cat-file` 等只读命令读取，未执行任何改变工作树的命令 (F-L1-005/006)
> - **事实来源**：`.trae/specs/create-ai-security-okf-wiki/facts-l1b3rt4s.md`（55 条 F-L1-xxx 事实，2026-09-02 逐项核验）
> - **洞察来源**：`.trae/specs/create-ai-security-okf-wiki/insights.md`（7 条跨仓库洞察，本束重点消费洞察 1/3/6/7）
> - **生成时间**：2026-09-02 ｜ **维护者**：OKF Wiki Bot

## 档案速览

| 维度 | 数据 | 说明 |
|---|---|---|
| 文件总数 | 44 | 34 厂商 .mkd + 5 非厂商 .mkd + 2 JSON + 1 TXT + README + LICENSE (F-L1-008) |
| 厂商档案 | 34 | 覆盖模型厂商、AI 产品、浏览器/IDE 代理等多类实体 (F-L1-009) |
| 最大文件 | `TOKEN80M8.mkd` 23,448,666 字节 | 单行 emoji + Unicode Tag 隐写载体，可见文本近零 (F-L1-017) |
| 隐写载体群 | 4 个 | `TOKEN80M8`、`TOKENADE`、`README.md`（24,071 字节可见仅约 51 字符）、`#MOTHERLOAD.txt` (F-L1-003/013/017) |
| glitch token 数据库 | 7,895 token × 8 类行为 × 5 类分词器 | `*SPECIAL_TOKENS.json`，附学术/工业引源 (F-L1-014/015) |
| 组织层级 | 厂商 → 模型版本 → 条目 | 逐代际档案（如 GOOGLE 15 章节、OPENAI 21 条目）(F-L1-045) |
| 许可证 | AGPL-3.0 | 全文 34,523 字节，含第 13 条网络交互条款 (F-L1-004) |

## 快速导航

### 核心概念

- [攻击面研究定位与档案形态](concepts/mission-attack-research.md) — 仓库在公开红队资产谱系中的位置、两大交付形态、攻守同构闭环
- [攻击技术分类学（T1–T10）](concepts/attack-taxonomy.md) — 四族十类的机制、观测特征与学术参照，附分类树与指纹表
- [防御视角反哺](concepts/defense-perspective.md) — 类别级防御、tokenizer 层观测、授权类条款的结构性弱点
- [负责任披露与研究伦理](concepts/responsible-disclosure.md) — AGPL-3.0 含义、披露渠道惯例、法律与合规边界

### 示例

- [防御性红队评估工作流](examples/redteam-workflow.md) — 用 T1–T10 组织不产生攻击内容的防御评估

### 参考

- [档案编目参考](references/catalog.md) — 34 厂商 .mkd 全表 + 10 杂项文件 + 计数断言

## 攻击语法速记

本束的分析主轴是一句话（洞察 3）：**越狱攻击 = 少数模板骨架 × 编码混淆手法 × 虚构授权修辞的排列组合**。同一骨架跨厂商复用并有可归因指纹 (F-L1-046/047)，同一模板随目标代际演化出更强混淆 (F-L1-055)。因此防御的检测单元应是类别与行为不变量，而非关键词——展开见[防御视角反哺](concepts/defense-perspective.md)。

## 如何使用本束

1. **建立定位**：先读[攻击面研究定位与档案形态](concepts/mission-attack-research.md)，理解档案是什么、以什么形态组织、与守方档案 [CL4R1T4S](../cl4r1t4s/index.md) 是什么关系。
2. **掌握分类学**：[攻击技术分类学](concepts/attack-taxonomy.md)给出 T1–T10 的机制与观测特征，可用于把任何新样本归入已知语法族。
3. **转向防御**：[防御视角反哺](concepts/defense-perspective.md)与[防御性红队评估工作流](examples/redteam-workflow.md)面向防御工程师，重点是检测单元选取与评估矩阵落地。
4. **核查边界**：涉及披露、许可与法律问题时读[负责任披露与研究伦理](concepts/responsible-disclosure.md)；需要定位具体文件时查[档案编目参考](references/catalog.md)，所有论断均带 F-L1-xxx 编号可回溯。

## 相关知识包

- [CL4R1T4S：系统提示词透明档案](../cl4r1t4s/index.md) — 守方机制层，与本束构成攻守配对阅读
- [OBLITERATUS：拒绝行为消除研究工具包](../obliteratus/index.md) — 模型层干预，解释 T6 类双响应现象的权重级成因
- [AI 安全与红队研究分组](../index.md) — 三层知识线总览

```{toctree}
:hidden:
:maxdepth: 7

concepts/mission-attack-research.md
concepts/attack-taxonomy.md
concepts/defense-perspective.md
concepts/responsible-disclosure.md
examples/redteam-workflow.md
references/catalog.md
```
