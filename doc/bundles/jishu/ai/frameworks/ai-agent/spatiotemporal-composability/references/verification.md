---
type: Reference
title: "P0 核验报告与对抗审查记录"
description: "论文元信息、实证数字、规则数、定理名的权威核验结果，四处口径勘误，以及七概念 V 阶段四视角审查与修正记录"
tags: [spatiotemporal-composability, verification, p0, adversarial-review, errata]
generated: { by: "process:seven-concepts-cmd/knowledge", at: "2026-11-21T09:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T09:10:00+08:00" }
status: stable
stale_after: 2027-02-28
sources:
  - id: arxiv-abs
    resource: https://arxiv.org/abs/2608.25512
    title: arXiv 元数据页
  - id: arxiv-pdf
    resource: https://arxiv.org/pdf/2608.25512v1
    title: 论文 v1 全文 PDF
---

# P0 核验报告与对抗审查记录

## 1. 信源距离预判

| 信源 | 距离层级 | 在本包的用途 |
|---|---|---|
| arXiv:2608.25512 v1 PDF 全文 | 作者一手 | 全部 F 编号事实的唯一权威依据 |
| arXiv abs 元数据页 | 官方发布 | 提交时间、页数、作者、DOI、分类 |
| BestHub《DeepSeek Harness Open-Source》 | 第三方综述 | 仅作为**待核验转述**，其口径须回原文对照 |
| Pith 论文页 | 第三方自动摘要（仅标摘要，未读全文） | 仅用于交叉确认摘要逐句，不作事实依据 |
| 本库 `cordis/references/background-paper.md` | 内部既有教程 | 版本差异比对、查重与分工判定 |
| 本库 `cordis/references/cordis-sources.md` | 内部源码教程 | 交叉引用落点，不作本包事实依据 |

> 该论文为**方法/工具型预印本**，非厂商自宣稿，成效数字风险不适用。P0 集中在：元信息、实证数字及其口径、规则与定理的**名称与数量**、版本差异。

## 2. P0 核验清单

| 编号 | 待核验声明 | 核验源 | 结果 | 说明 |
|---|---|---|---|---|
| P0-01 | 标题 / arXiv 编号 / 版本 | abs + PDF p1 | ✅ | 与 F-001 一致 |
| P0-02 | 作者为 3 人，机构为北大与 DeepSeek-AI | abs 作者列表 + PDF p1 | ✅ | 检索结果中曾出现「and 3 other authors」的 PDF 链接替代文本，属模板措辞；以作者列表与 PDF 首页为准 |
| P0-03 | v1 提交 2026-08-26 | abs submission history | ✅ | 精确时间戳见 F-003 |
| P0-04 | 92 pages / 1 figure / 2 tables | abs Comments | ✅ | PDF 提取文本含 87+ 页注释，与 92 页口径不冲突（含封面、目录与参考文献） |
| P0-05 | 学科与 ACM 分类 | abs | ✅ | F-005 |
| P0-06 | DOI | abs | ✅ | F-006 |
| P0-07 | VSCode 87 个 / 7 个 / 数据日期 2026-06-09 | PDF §1.2.1 及脚注 1 | ✅ | 原文为**个数**而非百分比，且带明确取数日期；见勘误 E-01 |
| P0-08 | 演算共九条规则 | PDF §4.2 + Figure 1 说明 | ✅ | 二手解读的「五个原语」不成立；见勘误 E-02 |
| P0-09 | 元定理名称与数量 | PDF §4.3.1–4.3.5 | ✅ | 二手解读的五项清单与原文定理编号不一一对应；见勘误 E-03 |
| P0-10 | 既有包「草稿 2026-08-13 / 88 页」 | 仓库文件 + abs | ⚠️ | 属**版本差异**（早期草稿 vs arXiv v1），非事实错误；见 E-04 |
| P0-11 | Koishi 4000+ 插件 / 四年 | PDF §5.3 | ✅ | 同时须登记作者自述的 Threats to validity（F-065） |
| P0-12 | Cordis v3 / v4 关系 | PDF §5.3 脚注 4 | ✅ | Koishi 当前用 v3，论文呈现 v4 |
| P0-13 | 二手解读中的 Harness 产品数据 | 第三方文章 | — | 不在论文内，**未纳入本包事实体系**；避免把产品资讯污染成论文结论 |

合计：✅ 11 项、⚠️ 1 项、❌ 0 项核心声明失败；1 项不纳入范围。故本包 `status: stable`，无需 `flagged`。

## 3. 勘误登记（四处口径差异）

| 编号 | 转述口径 | 论文原文口径 | 类别 | 本包处置 |
|---|---|---|---|---|
| E-01 | 「87% 的 100 个热门扩展含可执行代码」 | 「按安装量前 100 的扩展中**87 个**含可执行代码；仅**7 个**声明对非内置扩展的 `extensionDependencies`」，数据取自 2026-06-09 Marketplace | 数值口径转述（百分比化、丢失取数日期与第二项数据） | 正文写「87 个 / 100」「7 个 / 100」并标日期，见 F-013–F-015 |
| E-02 | 「演算定义五个原语操作：insert / retire / remove / load / unload」 | 九条规则：O-Insert、O-Retire、O-Remove、L-Begin、L-Iter、L-Finish、L-Divert、L-Leave、L-Unload；Figure 1 画八条 | 结构失真（把生命周期状态名误作规则名） | 正文按九条列出并解释八条图的原因，见 F-047 |
| E-03 | 「五个元定理：Preservation / Temporal / Spatial / Progress / Confluence」，另列「Terminal Recovery」为 loader 依赖 | 分节为五个**小节**；具体结果含 Theorem 64、68、Corollary 69、70、71、73、80 及 Lemma 66、75、77、78、79 | 命名层级混用（小节名 ≠ 定理名） | 正文按编号列出，并区分小节与定理，见 F-051–F-056 |
| E-04 | 既有包记录「草稿 2026-08-13、约 88 页」 | arXiv v1 为 2026-08-26、92 页 | 版本差异 | 本包按 v1 写，既有包保持原状不改；在 index 与学习路径中说明两者分工 |

> 勘误落实检查：E-01、E-02、E-03 涉及的正文位置均使用原文口径；无一处照抄转述数字或名称。

## 4. V 阶段：四视角对抗审查

> deep 档强制四视角覆盖。以下为审查意见与**实际采纳的修正**，非表演式通过。

| 视角 | 具体攻击点 | 处置 |
|---|---|---|
| 🔴 魔鬼代言人 | 「92 页形式化论文的教程会不会把作者的**假设**写成**保证**？Theorem 73 与 80 都有前提（≺ 无环、totality、名字集有限），若教程只写结论就是虚假升级」 | ✅ **采纳**：`08-metatheory.md` 每条定理单列「前提」与「不保证什么」，并把 Confluence 排除 failed fiber（F-057）写入 |
| 🔴 魔鬼代言人 | 「`witness` 运行时不校验（F-059）意味着整套保证依赖组件作者自觉，这与『结构性保证』的宣传矛盾」 | ✅ **采纳**：`04-revertible-effects.md` 与 `11-learning-path.md` 显式写出「运行时不校验见证」，并把「结构性保证 ≠ 自动验证」列为常见误读 |
| 🟢 新人视角 | 「`𝔈*Γ`、`∂Γ`、`≃S` 等符号第一次见就劝退；教程没有 Hello World 级入口」 | ✅ **采纳**：`00-overview.md` 增加「先用一个定时器注册的 6 行伪代码建立直觉」，全部形式符号延后到第 4 篇之后；`11-learning-path.md` 给出三档阅读路线 |
| 🟢 新人视角 | 「看完知道理论很好，但不知道和本库已有的 `cordis/` 包有什么关系、该先读哪个」 | ✅ **采纳**：根 index 与各概念页写明分工与互链；`11-learning-path.md` 给出「本包 → cordis → deepseek-harness」顺序 |
| 🟠 老板视角 | 「Koishi 4000+ 插件是单生态、单语言、观察性证据，作者自己在 Threats to validity 里承认不是对照实验，教程若当『已验证有效』就是过度宣称」 | ✅ **采纳**：`09-implementation-cordis.md` 明确标注证据等级；根 index 信任声明同步 |
| 🟠 老板视角 | 「预印本活跃修订，教程没有到期复核机制会静默过时」 | ✅ **采纳**：全包 `stale_after: 2027-02-28`，`log.md` 登记复核动作，index 顶部加版本提示块 |
| 🔵 未来视角 | 「论文把自我演化 Agent Harness 列为**未来**验证方向（F-072），容易被读成『已在 DSH 上验证』」 | ✅ **采纳**：`10-boundaries-and-related-work.md` 与 index 均写明「论文为动机举例与未来方向，非已完成的实证」 |
| 🔵 未来视角 | 「既有的 `background-paper.md` 会在未来被更新，两个包若都讲概念会长期漂移」 | ✅ **采纳**：本包不复制既有包的概念引子，改为互链并登记 E-04 版本差异 |

审查意见 8 条，采纳 8 条并逐项落到文件；无「写得很好」类空泛意见。

## 5. 机械门禁清单（V 阶段执行结果）

| 检查项 | 判据 | 结果 |
|---|---|---|
| 双份 F 编号一致 | 正则 `^\|\s*F-(\d{3})\s*\|` 分别提取两份文件，集合相等、连续 F-001…F-072 | 待收尾脚本复核 |
| 三级 toctree 完整 | 根 / 子目录 index 均含 `{toctree}`，条目逐一可达 | 待收尾脚本复核 |
| 相对链接可达 | 全部 Markdown 相对链接逐一 Test-Path，无 `file:///` | 待收尾脚本复核 |
| UTF-8 严格 roundtrip | 全部新增 .md 以 strict UTF-8 解码无乱码、无 BOM | 待收尾脚本复核 |
| 行尾 | 本仓 `eol=lf`，新增文件统一 LF | 待收尾脚本复核 |
| frontmatter 合规 | 每个非保留 `.md` 含可解析 YAML 且 `type` 非空 | 待收尾脚本复核 |
| 敏感信息零残留 | 无家目录绝对路径、无凭据 | 待收尾脚本复核 |

> 上表「待收尾」项在 C 阶段由收尾脚本统一复核并把结果回填到 [log.md](../log.md)，未复核前不宣称通过。
