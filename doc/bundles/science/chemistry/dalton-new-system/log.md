# 更新日志

## 2026-08-30

### 创建

- 初始化 dalton-new-system 知识包，基于公开网络调研生成：公版原著原文（Internet Archive 1808/1827 扫描本、Project Gutenberg eBook #74948、Le Moyne 学院 Giunta 教授经典化学文献摘录页、Smithsonian 图书馆目录）与现代权威资料（Britannica、Science History Institute、Nobel Prize 官网、Royal Society 官网、Nature、De Gruyter/IUPAC）
- 创建 6 篇概念文档、2 篇示例文档、2 篇信源文档
- 建立与前驱束 lavoisier-treatise、后继束 mendeleev-periodic-law 的互链，以及与 baopuzi 束的中西对照链接
- 全部登记 URL 经 WebFetch 实测可达（访问日期 2026-08-30）；en.wikipedia.org 与 en.wikisource.org 在生成环境中持续超时，未登记为信源

### 结构

- concepts/：00-why-read, 01-from-gases-to-atoms, 02-atomic-theory, 03-atomic-weights, 04-key-passages, 05-legacy
- examples/：01-multiple-proportions-reading, 02-reading-route
- references/：original-sources, modern-scholarship
- facts.md：39 条零推测事实，按 11 个主题分类成表
- insights.md：4 条四元组洞察 + 知识地图 + 学习路径推荐