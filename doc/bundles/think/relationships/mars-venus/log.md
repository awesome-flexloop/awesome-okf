# 更新日志

## 2026-08-30

### 创建
- 初始化 mars-venus 知识包，围绕约翰·格雷《男人来自火星，女人来自金星》（1992）生成批判性阅读 bundle
- 创建 5 篇概念文档、2 篇示例文档、2 篇信源文档，以及 facts.md（45 条事实）与 insights.md（4 条洞察 + 知识地图）
- 所有 P0 事实（作者身份与教育背景、出版年与出版社、销量/榜单口径、Hyde 2005 论文卷期页码与关键数字、中译本版本信息）均经 WebSearch/WebFetch 双信源核验
- 写作原则：书中主张一律标注“该书主张/该书称”，实证结论给出学术信源；销量等争议数字按信源口径分列；无法核验的数字列入 facts.md 末尾“放弃的未核验事实”清单

### 结构
- concepts/：00-book-and-phenomenon, 01-mars-venus-metaphor, 02-communication-and-needs, 03-scholarly-criticism, 04-critical-reading
- examples/：01-critical-application, 02-reading-cautions
- references/：01-editions, 02-further-reading
- facts.md：45 条零推测事实（3 列：编号/事实/信源）
- insights.md：4 条四元组洞察（核心判断/证据/迁移/边界）+ Mermaid 知识地图

### 核验要点
- 原版：HarperCollins 1992 年首版（精装 ISBN 0-06-016848-X）；通行平装 ISBN 9780060574215
- 销量口径分列：1500 万册（维基/卫报/HarperCollins 早期口径）、3000 万册+40 语言（Hyde 2005 引格雷方口径）、5000 万册+50 语言（HarperCollins 官网现口径，为作者全部著作）
- 榜单口径分列：121 周（维基引 CNN）、超过四年（大英百科）、140 周（1996 年杂志评论时点）；中文版宣传“158 周”未获权威旁证，列为放弃事实
- 作者教育背景：1982 年获哥伦比亚太平洋大学（CPU，未获认证、现已停办的函授机构）博士学位；学士/硕士学位授予机构资料说法不一
- 批评核心文献：Hyde (2005) American Psychologist 60(6):581–592；Carothers & Reis (2013) JPSP 104(2):385–407；Zell et al. (2015) American Psychologist 70(1):10–20
## 2026-08-31

### 评审打磨（独立评审 V 阶段闭环）

- insights.md 四元组标签由「核心判断/证据/迁移/边界」重排并重标为规范范式「陈述/证据/反常识点/行动启示」（对齐 spec FR-6；单元格语义经逐条核对，无语义损失）。
