# Claude 系统提示词发布史 Wiki 更新日志

## 2026-09-02 — 初始版本

**初始版本发布**，覆盖 Anthropic 官方系统提示词发布页全部 18 个模型子页、30 个日期条目（2024-07-12 → 2026-09-01），共 13 个文档文件。

### 采集与核验

- **信源**：`platform.claude.com/docs/en/release-notes/system-prompts/`（overview + 18 个模型子页），通过 `.md` 原文端点全量落盘（约 465KB raw markdown）
- **采集通道**：直连 curl 遇间歇性地域拦截（"App unavailable in region"），对失败子页采用带退避的 8 轮重试全部拿下；zh-CN 路径稳定受限，以 en 版为内容基线
- **事实登记**：61 条 F 编号事实（F-OV 6 + F-3X 15 + F-40 13 + F-45 13 + F-46 14），全部关键引文逐字摘录并标注源文件行号
- **抽查核验**：6/6 通过（more than a mere tool、fable_safeguards_routing、responding_to_mistakes_and_criticism、1929 版权豁免线、end of January 2025、human→person 术语迁移——事实文件与官方原文双向比对）
- **版本对比方法**：同一模型多日期条目采用逐行 diff 实测，不依赖官方加粗标注（实测其标注执行不严）

### 新增内容

- **concepts（7 篇）**：
  - 00-overview：公开机制与政策边界（会话注入机制、API 排除声明、固定快照机制、页面体系）
  - 01-lineage-matrix：18 模型 × 30 条目全景矩阵（含 Mermaid 时间线、篇幅实测附录）
  - 02-era-3x：3.x 时代 8 条目（单段文本 → XML 分节 → 人格化转折）
  - 03-era-4x-launch：4.0/4.1 时代 7 条目（模板化架构、身份插槽、规则大扩张）
  - 04-era-45：4.5 代 8 条目（九章节架构统一、三模型同日演进）
  - 05-era-fixed-snapshot：固定快照时代 7 条目（4.6 → Fable 5.1，含 export controls 事件叙事、safeguards routing）
  - 06-evolution：设计思想演进分析（四代形态、模板化、人格化曲线、产品信息层膨胀、安全合规模块化、约束减法、活文档属性、8 条实践启示）
- **references（2 篇）**：source-index（18 官方子页清单 + .md 端点采集方法）、entry-registry（61 条 F 编号索引 + 跨主题速查）
- **组织级文档**：index.md（束入口）、concepts/index.md、references/index.md、log.md

### 方法论

- 使用 seven-concepts 知识沉淀链路（R 事实采集 → I 演进洞察 → E 入库萃取 → V 对抗审查收尾）
- 洞察层产出 7 条"现象/证据/根因/影响"四元组（insights），全部落进 06-evolution 并有 F 编号支撑
- 官方原文笔误（如 "but as as a request"、"can't or won't with"）按指纹用途逐字保留并登记，未做"修正"

### 已知边界

- zh-CN 官方翻译页因区域访问受限未纳入逐字比对，中文解读为原创转述
- 官方页面为活文档（旧条目就地更新、新模型持续上线），本文以 2026-09-02 快照为准
