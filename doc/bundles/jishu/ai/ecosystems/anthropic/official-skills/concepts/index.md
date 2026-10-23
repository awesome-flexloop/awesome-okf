# Anthropic Skills 概念文档

- [Skills生态概览](00-overview.md) — Skills 是什么、与 Commands/Agents/Hooks 的关系、触发机制、19 个 Skills 分类总览、安装使用方法
- [SKILL.md格式规范](01-skill-format.md) — Skill 目录结构、YAML frontmatter 字段详解、description 编写最佳实践、Markdown body 组织方式、资源引用约定、打包分发
- [Skill Creator工具详解](02-skill-creator.md) — 元技能 skill-creator 的 5 步创建流程、3 个专业评估代理、eval-viewer 报告、description improver、评估方法论
- [Claude API Skill详解](03-claude-api-skill.md) — claude-api Skill 多语言覆盖、API 漂移警告、默认配置、"Never guess SDK usage"原则
- [Skill 编写规范与可复用模式](04-authoring-patterns.md) — frontmatter 字段决策、description 三种强度、正文四种内容模式、资源目录分工、脚本黑盒契约、评估闭环
- [文档处理类 Skills 详解](05-document-skills.md) — docx/pdf/pptx/xlsx/doc-coauthoring：共享 office/ 子树、XML 原地编辑、三层 QA、公式重算、读者测试
- [设计与创意类 Skills 详解](06-design-skills.md) — algorithmic-art/canvas-design/theme-factory/frontend-design/brand-guidelines/slack-gif-creator/web-artifacts-builder
- [API 与开发工具类 Skills 详解](07-dev-skills.md) — claude-api/mcp-builder/skill-creator/webapp-testing：TRIGGER+SKIP 探测、reference 加载时机、双跑评估、侦察—动作
- [沟通与写作类 Skills 详解](08-communication-skills.md) — internal-comms/academy-guide/discernment-nudge：薄壳路由、正向推荐规则、反触发清单

```{toctree}
00-overview
01-skill-format
02-skill-creator
03-claude-api-skill
04-authoring-patterns
05-document-skills
06-design-skills
07-dev-skills
08-communication-skills
```
