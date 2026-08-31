# 更新日志

## 2026-08-31

### V 阶段对抗抽查与通读计划扩展（session: sc-20260831-zhuangzi-waipian）
- 抽查外/杂篇全文 3 篇与 ctext.org《续古逸丛书》本逐字比对：《秋水》（河伯北海若、濠梁辩）、《外物》（外物不可必、涸辙之鲋、七十二钻无遗策）、《山木》（材与不材、物物而不物于物）——文本整体忠实，名段逐字一致
- 修正异文归属措辞：F-059 与 09 卷末异文补记原称"ctext 简体版作'黄帝、神农'"，经核 ctext 繁体底本原文即作"此黃帝、神農之法則也"；"神农、黄帝"序见于郭象注本系统整理本（《庄子校诠》等）与《吕氏春秋·必己》平行引文——两序皆有传世依据，改登记为"底本差异"而非"简体版差异"，本文仍从郭象本作"神农、黄帝"
- examples/03-reading-plan.md 由内篇七篇通读计划扩展为三十三篇完整路径：新增「三十三篇篇目总表」、阶段四（外篇 15 篇，概念 08→09，《秋水》《知北游》精读）、阶段五（杂篇 11 篇，概念 10→11，《天下》《外物》《寓言》优先、疑伪四篇 F-031～F-033 分层提示）；所有篇目/分层主张回溯 F-021～F-035、F-050～F-065；frontmatter sources 增补概念 08-11，显式标注"通读向导非逐字总录"边界

### 补全外篇、杂篇全文
- 新增 4 篇概念文档：08-waipian-full-text-1（外篇前八篇：骈拇至刻意）、09-waipian-full-text-2（外篇后七篇：缮性至知北游）、10-zapian-full-text-1（杂篇前五篇：庚桑楚至寓言）、11-zapian-full-text-2（杂篇后六篇：让王至天下）
- 全部原文以郭象注三十三篇本系统为底本，与 ctext.org《续古逸丛书》本《南华真经》数字底本逐字核对，关键异文在卷末「异文补记」登记
- 分卷策略：外篇 15 篇分二卷、杂篇 11 篇分二卷，沿用内篇分卷先例；卷末附叉链目录
- facts.md 新增「十、外篇与杂篇异文登记」F-057~F-065（56 → 65 条）

### 导航更新
- concepts/index.md：概念文档 8 → 12 篇，新增「外篇与杂篇全文」分表与 toctree
- bundle index.md：核心概念 8 → 12 篇，文本边界更新为三十三篇全文
- 04-waipian-and-zapian.md：新增「2.1 全文分卷阅读」交叉引用

## 2026-08-30

### 创建
- 初始化 chuang-tzu bundle，基于公共领域经典《庄子》（《南华经》）原文与历代解读生成
- 创建 8 篇概念文档、3 篇示例文档、3 篇信源文档
- 建立与 laozi 系 bundle 的交叉引用（老庄道家经典阅读体系）

### 结构
- concepts/：00-what-is-zhuangzi, 01-text-versions, 02-authorship, 03-neipian-full-text, 04-waipian-and-zapian, 05-core-concepts, 06-famous-fables, 07-commentaries
- examples/：01-xiaoyaoyou-reading, 02-qiwulun-reading, 03-reading-plan
- references/：core-texts, commentaries, cross-ref
- facts.md：56 条零推测事实（含异文登记 F-054~F-056）
- insights.md：4 条核心洞察

### 方法论
- 采用 seven-concepts 场景4（知识沉淀）R→I→E→V→C 链路
- 内篇七篇原文经中华文库、ctext.org 双源逐字核对，关键异文显式标注