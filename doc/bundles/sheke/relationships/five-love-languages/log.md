# 更新日志

## 2026-08-30

### 创建

- 初始化 five-love-languages 知识包（OKF v0.2），围绕盖瑞·查普曼《爱的五种语言》（The Five Love Languages, 1992）生成。
- 创建 5 篇概念文档、2 篇示例文档、2 篇信源文档，以及 facts.md（45 条事实、27 个信源）、insights.md（4 条四元组洞察 + Mermaid 知识地图）。
- R 阶段核验：作者教育与牧职背景（图书馆 Bowker 传记、经纪简介、公共电台访谈）、1992 年初版与 2015 修订版 ISBN、五种爱语英文原名与中文通行译名、三种大陆中译本版本信息（豆瓣图书条目 + 图书馆/书店著录双源）、销量与榜单的分时段营销口径、学界实证检验（Impett/Park/Muise 2024 综述等）。
- 争议公允呈现：概念 04 与 facts.md 第六节专门记录「框架基于牧灵辅导轶事、缺乏同行评审实证支持」的证据状态；未核验事实列入 facts.md 放弃清单。

### 结构

- concepts/：00-chapman-and-book、01-love-tank、02-five-languages、03-discovering-your-language、04-evaluation-and-boundaries
- examples/：01-love-language-reflection、02-reading-path
- references/：01-editions、02-further-reading
- facts.md：45 条零推测事实 + S1–S27 信源登记 + 放弃核验清单
- insights.md：4 条四元组洞察（核心判断/证据/迁移/边界）+ Mermaid 知识地图

### 版权处理

- 全部正文为原创中文转述；未复制原书测验题/量表；直引控制在单处 30 汉字以内并标注章节。
- 信源仅登记出版社、图书馆、学术期刊、主流媒体、正版图书平台页面，不含任何盗版站点。
## 2026-08-31

### 评审打磨（独立评审 V 阶段闭环）

- insights.md 四元组标签由「核心判断/证据/迁移/边界」重排并重标为规范范式「陈述/证据/反常识点/行动启示」（对齐 spec FR-6；单元格语义经逐条核对，边界行对应反常识点、迁移行对应行动启示，无语义损失）。
- references/01-editions.md、references/02-further-reading.md 的 frontmatter 补齐 sources 字段（分别 16 条、4 条，均取自 facts.md 文末 S1–S27 信源登记表），与其余知识包范式一致。
