# 更新日志

## 2026-08-31

### 创建
- 初始化 fangzhong-bajia-reading bundle（spec：.trae/specs/standards-tools/create-fangzhong-bajia-wiki/）
- R 阶段：四线并行调研（著录原文/亡佚辑佚/出土文献/现代解读），采集 58 条带信源事实（F-001～F-058），G1 质量门通过；ctext.org 拒绝自动化访问，著录线改用维基文库/颜师古注本/汉书新注/中华文库四信源交叉核对
- I 阶段：4 条四元组洞察（I-1 托名化石层 / I-2 数字矛盾即流传史 / I-3 亡佚文本双通道回流 / I-4 方技四分定位与两次重分类），G2 质量门通过
- 创建 8 篇概念文档、3 篇示例文档、4 篇信源文档

### 结构
- concepts/：00-yiwenzhi-fangji-lue, 01-eight-schools-catalog, 02-rongcheng-wuyin, 03-huangdi-school, 04-sanyangban-and-others, 05-fragments-chain, 06-excavated-texts, 07-modern-interpretations
- examples/：01-first-catalog-reading, 02-fragment-reading, 03-reading-plan
- references/：catalog-sources, fragment-sources, excavated-sources, modern-studies
- facts.md：58 条带信源事实（含 6 处【待核验】条目）
- insights.md：4 条四元组洞察 + 知识地图

### 方法说明
- 七概念链路：场景4 知识沉淀 R（调研）→ I（洞察）→ E（落地本 bundle）→ V（独立对抗评审）→ C（文件落盘收尾）
- 调研纠正的预设：任务原指定信源 ctext.org 拒绝自动化访问，按等效信源方案四源交叉核对；02-fragments-facts.md 原 F-015/F-016 与著录线重复已删除，自 F-017 起编号
- 无法坐实之处（卷数差异成因、异文版本依据、叶德辉辑录年份、老官山房中简帛定名等）一律以【待核验】标注，未作断言
### V 阶段独立对抗评审（2026-08-31）
- 四视角评审（事实准确性/新人可入门性/定位与边界/规范合规）：事实线外部实证 9 条（含"性情/情性"异文方向、医经 177 卷核算两处易错点均验证正确）；85 个相对链接 0 断链；toctree 22 文件全覆盖；边界声明在 15 篇子文档执行一致
- 修复 R-01（高）：F-034/F-035 将木简《杂禁方》特征误植于帛书《杂疗方》，致 concepts/06 表格内部矛盾——已按整理通说拆分更正（木简 11 支厌禁者系《杂禁方》；《杂疗方》为帛书、以房中养生方为主），并补入【待核验】汇总表
- 修复 R-02（低）：F-043 期刊名《传统文化与现代文化》更正为《传统文化与现代化》
- 提示级处置：F-030 补《却谷食气/去谷食气》整理用字差异按语；F-010 颜注信源列去掉无法支撑注文的白文信源 S1
- 评审后根 index status: draft → stable，verified 字段填充评审信息
