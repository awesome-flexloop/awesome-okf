# 更新日志

## 2026-08-30

### 创建
- 初始化 classics-reading bundle（spec：.trae/specs/standards-tools/create-sexology-classics-wiki/）
- R 阶段：三路并行网络调研，采集 104 条带信源事实（F-ANCIENT 30 条 / F-WEST 36 条 / F-CHINA-MODERN 38 条），G1 质量门通过
- 创建 9 篇概念文档、3 篇示例文档、5 篇信源文档
- 新建 think/sexology/ 分组入口；更新 think/index.md 与 bundles/index.md（287 束 / 33 组）

### 结构
- concepts/：00-reading-map, 01-ancient-china, 02-eastern-western-classics, 03-foundations, 04-modern-science, 05-feminism-construction, 06-china-modern, 07-translations, 08-censorship-power
- examples/：01-entry-path, 02-ancient-text-reading, 03-reading-plan
- references/：ancient-china-sources, western-classics-sources, china-modern-sources, institutions-journals, further-reading
- facts.md：104 条带信源事实（含【待核验】条目）
- insights.md：4 条四元组洞察 + 知识地图

### 方法说明
- 七概念链路：R（调研）→ I（洞察）→ E（落地本 bundle）→ V（独立对抗评审）→ C（文件落盘收尾）
- 调研纠正的两处预设：阮芳赋 1985 年主编《性知识手册》（非《性的知识》1980）；《肉蒲团》序年 1633 年（非 1657）
- 版本争议条目一律以【待核验】标注，未作断言
### 独立评审修复（V 阶段闭环）
- china-modern-sources.md：事实权威指向由 .temp 临时文件改为 bundle 内 facts.md（相对链接）
- 《房内考》译者署名裁定：经李零北大中文系官方页核验，1990 上海人民版署「郭小惠」、2007 商务版署「郭晓惠」，两版用字本不相同；F-ANCIENT-027 已改为分版表述
- 07-translations.md：福柯《性史》中译者名（佘碧平、张廷昱）补【译者署名待核验】标注
- 译名统一：全目录「蔼理士/霭理士」混用统一为「霭理士」（6 文件）
- examples/01-entry-path.md：篇首增加范围声明，厘清与 00-reading-map 四大范式自测的层级关系
- bundles/index.md 计数裁决：全量清点确认 289 束/35 组自洽（含并发新增 yangsheng 分组），维持不变
- 复跑质量门：gates.toctrees 通过、gates.utf8 通过（5859 文件）、Sphinx 构建复跑（解析阶段 100% 零 sexology 警告）
- 导航登记补全：.trae/specs/standards-tools/README.md 与 .trae/specs/README.md 看板登记本 spec
