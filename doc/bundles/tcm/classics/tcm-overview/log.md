# 更新日志

## 2026-08-30

### 创建

- 初始化 tcm-overview bundle：中医典籍总览束，落位 tcm/classics/（tcm 域第二束）
- 内容文档 11 篇：concepts 6 篇、examples 2 篇、references 3 篇；另有束根 index.md 与 log.md 两个保留文件

### 方法

- seven-concepts-cmd 场景 4（知识沉淀）链路 R→I→E→V→C
- R 阶段登记事实 264 条（OV-001~047 / NGJ-001~043 / NJ-001~089 / SH-001~036 / BC-001~049），每条附信源 URL；本束正文引用其中总览谱系事实（OV）与内经异文登记（NGJ-027~043）
- I 阶段沉淀洞察 5 条（INS-001~005，陈述/证据/反常识/行动四元组完整）
- E 阶段萃取模式 3 个：双源逐字核读法（L2-validated）、托名辑复分层法（L2-validated）、谱系分级阅读法（L1-draft），完整落入 concepts/05（触发场景/核心步骤/反模式/检验标准/迁移示例/成熟度标注齐备）
- V 阶段：双源核对演示选 facts 登记异文（NGJ-027 耗/好、NGJ-038 白/帛·今/令）走完整七步流程

### 结构

- concepts/：00-genealogy-layering, 01-four-classics-guide, 02-philology-basics, 03-pseudepigrapha-dating, 04-graded-bibliography, 05-reading-methodology
- examples/：four-classics-reading-plan, dual-source-verification-demo
- references/：authoritative-sources, cross-references, methodology-records

### 合规

- 首屏医学免责声明（束根 index.md）："本知识包内容为古籍文献学习资料，非医疗建议；任何健康问题请咨询执业医师。文中方药剂量仅为文献记录。"
- "四大经典"组合争议多组并列登记不作裁决（OV-002~006）；《本草纲目》金陵本刊行年代两说并列（OV-024）；四经成书年代诸说并列（OV-007/009）
- 托名表述规范：禁用"神农曰/黄帝说"式表述，一律"某辑本作某/某本作某"（INS-001/INS-004 行动项）
- 束自包含：交叉引用仅用束内相对路径与 bundles/ 树内跨束相对路径（.md 后缀），不链接规划区路径；事实以登记编号 + 信源 URL 溯源
