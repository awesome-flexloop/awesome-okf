# 更新日志

## 2026-08-30

### 创建

- 新建知识包「门捷列夫元素周期律阅读教程」，执行 seven-concepts 知识沉淀流程 R（事实采集）→ I（洞察）→ E（批量生成），全部产出使用简体中文。
- **R 阶段**：实测 20 个信源 URL 可达后登记，分两类归档于 [references/original-sources.md](references/original-sources.md)（公版原典：archive.org《化学原理》英译本、Giunta 经典化学史转录、ChemTeam 发现论文转录）与 [references/modern-scholarship.md](references/modern-scholarship.md)（RSC、Britannica、Princeton/Gordin、OUP/Scerri 等权威解读）；采集事实 38 条，编号 F-001 至 F-038，见 [facts.md](facts.md)。
- **I 阶段**：沉淀 3 条四元组洞察（可证伪的定量预言、原子量作为序的代理、数据基础设施与独立重复发现），见 [insights.md](insights.md)。
- **E 阶段**：生成概念文档 6 篇、实践示例 2 篇，并覆盖束根 [index.md](index.md)（原桩文件 frontmatter 字段全部保留，status 仍为 draft，不写 verified）。

### 结构

- 束目录共 17 个文件：束根 4 个（index.md、facts.md、insights.md、log.md）+ concepts/ 7 个（index.md + 00 至 05）+ examples/ 3 个（index.md + 01、02）+ references/ 3 个（index.md + original-sources、modern-scholarship）。
- 链接关系：前驱束 [../dalton-new-system/index.md](../dalton-new-system/index.md)（道尔顿原子论）；中西对照 [../cantongqi/index.md](../cantongqi/index.md)（《周易参同契》）；阅读方法论迁移 [../../../think/laozi/boshu-reading/index.md](../../../guoxue/laozi/boshu-reading/index.md)（帛书《老子》）。
- 生命周期：信源访问日期 2026-08-30；`status: draft`；`stale_after: 2027-08-30`；`okf_version: "0.2"`。

### 已知限制

- archive.org《化学原理》全书 OCR 文本直链多次超时未取，原典引文以 Giunta/ChemTeam 的论文转录页为准（均为公版文本），《化学原理》仅登记书目页与卷次信息。
- en.wikisource.org 与 en.wikipedia.org 访问超时，未登记为信源；相关事实由 Britannica、RSC、Giunta 等可达信源交叉支撑。