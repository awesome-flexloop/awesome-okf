# 更新日志

## 2026-09-02

**Migration**: 从 SpecWeave docs/knowledge/learning/ 迁入 awesome-okf-xs（07 分类）

* 章节文档 frontmatter 重写为 OKF v0.2（type/title/description/tags/sources/generated/status/stale_after）
* 隐私清洗：个人文件系统路径替换为占位符；中文内嵌引号转全角
* 舍弃：源侧 README.md/index.md（导航）、log.md、seven-concepts-report.md、retrospective*/verification-report*（隐私元数据）

## 2026-09-02（时效核验）

**Verification**: WebSearch 核验官方定价页（api-docs.deepseek.com/zh-cn/quick_start/pricing，2026-09-02 抓取）

* 官方现行平价制（百万 tokens）：V4-Flash 输入缓存命中 0.02 元 / 未命中 1 元 / 输出 2 元；V4-Pro 缓存命中 0.025 元 / 未命中 3 元 / 输出 6 元；上下文 1M、输出最大 384K；deepseek-chat 与 deepseek-reasoner 两个模型名将弃用，分别映射 V4-Flash 非思考/思考模式
* 束内 `03-api-pricing-comparison.md` 的“2026-08-17 起峰谷定价（V4-Pro 高峰输出 27 元/空闲 13.5 元等）”**未能在官方页面复现**，按内容保真原则保留原文并标注待复核；引用该束定价数据时请以官方页面为准
* 历史脉络（官方脚注）：缓存命中价降至首发 1/10 自 2026-04-26 生效；V4-Pro 2.5 折已于 2026-05-31 到期并永久化为 1/4 定价
