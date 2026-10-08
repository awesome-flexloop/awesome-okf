# 更新日志

## 2026-09-02

**Migration**: 从 SpecWeave docs/knowledge/learning/02-agent-engineering-methodology/ 六板块整合迁入（00/01/02 分类批次）

* 板块章节化：01-paradigms → concepts/paradigms/、02-prompt-coding（剩余）→ concepts/prompt-coding/、03-methodology → concepts/methodology/、05-evaluation → concepts/evaluation/、06-performance → concepts/performance/、ai-engineering-notes（剩余）+ deep-learning-atomic-design → concepts/engineering-notes/
* 全部章节文档重建 frontmatter 为 OKF v0.2（type/title/description/tags/generated/status/sources 溯源至 learning 源路径）；各级目录 index.md 统一生成导航与 toctree；adversarial-review-wiki 知识图谱（HTML/TOML）随迁 references
* 隐私清洗：个人工作区路径替换为占位符；session ID/token 消耗/执行时长扫描零命中；ai-engineering-notes/00-overview 保留板块总览
* 舍弃：分类根与板块根 README.md/index.md 原文（导航元数据，index 统一重建）、各主题 log.md（工作流元数据）、同名种子索引页（harness-engineering-wiki.md 等 4 个）
* 排除（已并入其他束，避免影子内容）：02-prompt-coding/agent-skills-wiki（10 文件，三源合并回填至 jishu/ai/ai-agent/agent-skills-spec）、02-prompt-coding/book-to-skill-wiki（13 文件，已合并至 jishu/ai/ai-agent/book-to-skill）、ai-engineering-notes 的 octo-platform-wiki.md 与 anthropic-financial-services-wiki.md（按台账 §5 归 03 分类处置）
