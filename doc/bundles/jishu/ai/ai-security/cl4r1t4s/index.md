---
okf_version: "0.2"
type: index
bundle: cl4r1t4s
version: 0.1.0
description: |
  CL4R1T4S 档案知识包：26 家 AI 厂商被提取的系统提示词全景研究。
  覆盖仓库定位与透明性主张、26 目录 73 文件的厂商档案全景、
  系统提示词四层结构与标记语法解剖、防御性提示工程教训、
  伦理与研究框架、跨厂商安全护栏结构对比，以及完整档案编目参考。
  本束为研究性转述：只登记结构与元信息，不逐字复制提示词正文。
concepts:
  - mission-transparency: 仓库定位与透明性主张（shadow-puppet 隐喻、公开理由、贡献规范）
  - vendor-landscape: 厂商档案全景（26 目录 73 文件、版本日期规律、特殊结构）
  - prompt-anatomy: 系统提示词解剖学（四层结构模型与标记语法分化）
  - defense-lessons: 防御性提示工程教训（护栏范式、关键词黑名单局限、类别级防御）
  - ethics-research-framing: 伦理与研究框架（转述边界、学术谱系、合规使用）
references:
  - catalog: 档案编目参考（26 厂商目录 73 文件全表与版本日期注记）
examples:
  - compare-guardrails: 跨厂商安全护栏结构对比分析（结构层面，不含护栏正文）
---

# CL4R1T4S：AI 系统提示词透明度档案

CL4R1T4S（读作 claritas，拉丁语“清晰”）是 GitHub 上一个公开档案仓库，定位为“AI SYSTEMS TRANSPARENCY AND OBSERVABILITY FOR ALL”，收录来自 OpenAI、Google、Anthropic、xAI、Perplexity、Cursor、Windsurf、Devin、Manus、Replit 等 26 家厂商的 73 个被提取的系统提示词、指南与工具定义文件 (F-C4-001) (F-C4-007) (F-C4-009)。它的价值不在于“泄露”本身，而在于把原本不可见的“提示词脚手架”变成了可比较、可编目、可研究的结构化对象——本知识包正是对这批档案的结构学研究成果。

## 设计哲学

- **透明即信任前提**：仓库的核心引语是“要信任输出，必须先理解输入”（In order to trust the output, one must understand the input）。未读过系统提示词的用户，面对的不是中立智能，而是一个“皮影戏人偶”（shadow-puppet） (F-C4-002)。
- **档案化而非评论化**：仓库本体只做编目收集（模型名/版本、提取日期、可选笔记），不做逐篇解读；结构分析交由本知识包这类二级研究产出完成 (F-C4-004)。
- **攻守同源**：这批“守方视角”的透明度档案与同一研究者的越狱档案 L1B3RT4S 构成同一对抗循环的两个切面——防御条款与攻击入口互为镜像，阅读任何一侧都需要另一侧校准 (洞察 1)。
- **最小引用纪律**：本束全程遵循研究性登记纪律——只记录章节结构、标记语法、段落位置与行号锚点，正文引用不超过 2 行脱敏短句。

## 信任声明

> **来源与可信度**
> - 上游源码位置：`external/dao/action/elder-plinius/CL4R1T4S`（本地克隆，对应 https://github.com/elder-plinius/CL4R1T4S ，AGPL-3.0 许可，快照 git HEAD `93b0ae6fb503db6642e58f9d6352db973a900cdc`）(F-C4-006)
> - 事实来源：`.trae/specs/create-ai-security-okf-wiki/facts-cl4r1t4s.md`（70 条 F-C4-xxx 事实编号，行数统计与结构骨架登记于 2026-09-02 逐项核验）
> - 生成时间：2026-09-02
> - 维护者：OKF Wiki Bot
> - 洞察来源：`.trae/specs/create-ai-security-okf-wiki/insights.md`（7 条跨仓库洞察，本束重点消费洞察 1/3/4/7）

> **用途限定**
> 本知识包用于防御研究、提示词工程教学与 AI 治理观察，**不提供**任何可操作的越狱载荷、注入模板或绕过手法。文中所有结构示意均为脱敏骨架，涉及正文的位置只给出章节名与行号。请勿将本束内容用于违反上游许可或目标厂商服务条款的场景。

## 快速导航

### 核心概念

- [仓库定位与透明性主张](concepts/mission-transparency.md) — shadow-puppet 隐喻与“为什么要公开”
- [厂商档案全景](concepts/vendor-landscape.md) — 26 目录 73 文件的版图与命名规律
- [系统提示词解剖学](concepts/prompt-anatomy.md) — 四层结构模型与标记语法分化
- [防御性提示工程教训](concepts/defense-lessons.md) — 从 26 家厂商提炼的护栏写法与盲区
- [伦理与研究框架](concepts/ethics-research-framing.md) — 转述边界与合规使用

### 示例

- [跨厂商安全护栏结构对比](examples/compare-guardrails.md) — 结构层面的对比分析方法示范

### 参考

- [档案编目参考](references/catalog.md) — 26 厂商目录 73 文件全表

## 档案全景速览

| 维度 | 数据 | 说明 |
|------|------|------|
| 厂商目录数 | 26 | 目录名全部大写，含带空格的 VERCEL V0 (F-C4-007) |
| 档案文件数 | 73 | 另有根级 README.md 与 LICENSE，合计 75 (F-C4-009) |
| 扩展名分布 | .txt 33 / .md 32 / .mkd 3 / .json 2 / 无扩展名 3 | .mkd 为仓库独有用法 (F-C4-010) |
| 单文件规模 | 2 行 ~ 8093 行 | 超过 1500 行的文件共 8 个 (F-C4-012) |
| 最大单体组合 | Codex_Desktop 5.6-Sol 共 12363 行 | SystemPrompt 4270 行 + Tools 8093 行 (F-C4-070) |
| 含防注入/防越狱条款 | 9 个文件 | XAI 3 个 + ANTHROPIC 6 个 (F-C4-051) |
| 许可证 | AGPL-3.0 | GNU Affero General Public License v3 (F-C4-006) |

## 如何使用本束

1. **建立全局认知**：先读 [仓库定位与透明性主张](concepts/mission-transparency.md) 与 [厂商档案全景](concepts/vendor-landscape.md)，理解档案从哪来、覆盖多广。
2. **学习结构学**：[系统提示词解剖学](concepts/prompt-anatomy.md) 给出四层结构模型，可用于快速拆解任何一份新获取的系统提示词。
3. **对照防御实践**：[防御性提示工程教训](concepts/defense-lessons.md) 与 [跨厂商护栏对比](examples/compare-guardrails.md) 面向提示词安全设计者，重点看护栏位置与表述范式的差异。
4. **查阅与溯源**：需要定位某个具体档案时使用 [档案编目参考](references/catalog.md)；所有论断均带 F-C4-xxx 事实编号，可回溯到事实清单与原始文件行号。

```{toctree}
:hidden:
:maxdepth: 7

concepts/mission-transparency.md
concepts/vendor-landscape.md
concepts/prompt-anatomy.md
concepts/defense-lessons.md
concepts/ethics-research-framing.md
examples/compare-guardrails.md
references/catalog.md
```
