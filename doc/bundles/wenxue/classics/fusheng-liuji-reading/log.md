# 更新日志

## 2026-08-30

### 创建
- 初始化 fusheng-liuji-reading bundle，基于公开信源调研整理
- 创建7篇概念文档、3篇示例文档、4篇信源文档
- 事实清单50条、核心洞察4条
- 应用 seven-concepts-cmd 知识沉淀链路 R(事实采集)→I(洞察)→E(概念示例萃取)→V(独立对抗审查)

### 结构
- concepts/：00-why-read, 01-author-and-era, 02-six-records-structure, 03-yun-niang, 04-textual-history, 05-forgery-case, 06-life-aesthetics
- examples/：01-close-reading, 02-reading-plan, 03-lost-records
- references/：01-primary-editions, 02-scholarship, 03-translations, 04-adaptations
- facts.md：50条零推测事实
- insights.md：4条四元组洞察+知识地图

### 对抗审查（2026-08-30）
- 独立审查 V 阶段完成，对照 AC-1..AC-6 复核
- 发现并修复 6 项问题：
  - P1-1：黄楚香误列为揭伪学者（实为作伪者）→ examples/02、03 修正
  - P1-2：蔡根祥证据链表格时间列重复 → concepts/05 修正为"年份未载"
  - P2-1："道光年间"残稿断代无据 → concepts/04、references/01 移除断代
  - P2-2：内容文档缺 verified 字段 → 15 个带 frontmatter 文档补齐
  - P2-3：根 index 缺 sources 字段 → 补 4 项信源
  - P2-4：examples 缺"相关概念" → 3 篇补齐
- 复验：gates.utf8（21 文件）、gates.toctrees（全部可达）通过
