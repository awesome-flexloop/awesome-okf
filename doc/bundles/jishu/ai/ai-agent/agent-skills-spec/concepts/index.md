# 概念导航（Concepts）

本目录收录 agent-skills-spec 知识束的 11 篇概念文档，按学习路径排序（入门 → 核心 → 高级 → 案例）：先认识技能的物理形态与加载原理，再深入字段规范与创作方法，最后进入评估、优化、客户端集成与参考实现四个高级主题，并以生产级技能库实践案例与 Google 工程文化术语收尾。

| 文件 | 标题 | 层级 | 核心内容 |
|---|---|---|---|
| [00-skill-anatomy.md](00-skill-anatomy.md) | 技能解剖：目录结构与 SKILL.md 组成 | 入门 | 目录结构、frontmatter+正文两段式、scripts/references/assets 约定、文件引用、validate 命令 |
| [01-progressive-disclosure.md](01-progressive-disclosure.md) | 渐进式披露：三层加载契约与生命周期 | 入门→核心 | 三层 token 预算、Discovery→Activation→Execution、500 行上限的由来 |
| [02-frontmatter-fields.md](02-frontmatter-fields.md) | Frontmatter 全字段规范：规范约束与校验器实现对照 | 核心 | 六字段逐项约束 × validator 规则双栏对照、name 五规则、i18n 差异点 |
| [03-authoring-principles.md](03-authoring-principles.md) | 创作原则与最佳实践：上下文经济学与指令设计模式 | 核心 | 两条创建路径、add-what-agent-lacks、五种内容模式、脚本工程附录（uvx/PEP 723/stderr 分离） |
| [04-eval-driven-iteration.md](04-eval-driven-iteration.md) | Eval 驱动迭代：把 ML 实验方法用于技能治理 | 高级 | evals.json、双臂对照、断言分级、grading/benchmark/feedback、五条模式分析、迭代闭环 |
| [05-description-optimization.md](05-description-optimization.md) | Description 优化：触发机制与防过拟合实验 | 高级 | 触发机制、四写作原则、触发率测量（3 次/0.5 阈值）、near-miss 负例、60/40 切分 |
| [06-client-integration.md](06-client-integration.md) | 客户端生态与集成：发现、披露、激活与长会话管理 | 高级 | 46 客户端名录、三层加载契约、.agents/skills/ 惯例、扫描上界、宽松校验四规则、双激活路径 |
| [07-skills-ref-reference-implementation.md](07-skills-ref-reference-implementation.md) | skills-ref 参考实现：最小完整闭环的架构样本 | 高级 | 8 个公开 API 签名、validator 校验规则与错误消息、parser 四类 ParseError、CLI 三子命令、to_prompt XML |
| [08-scripts-guide.md](08-scripts-guide.md) | 脚本使用指南：一次性命令、自包含脚本与面向智能体的设计 | 高级 | uvx/npx 版本固定、PEP 723/Deno/Bun/Ruby 四种自包含模式、面向智能体六原则（非交互/--help/错误消息/结构化输出/幂等/退出码） |
| [09-osmani-agent-skills-practice.md](09-osmani-agent-skills-practice.md) | 实践案例：Addy Osmani agent-skills 生产级技能库 | 案例 | 六阶段生命周期、20 核心技能索引、7 斜杠命令机制、五大实战应用场景 |
| [10-google-engineering-culture.md](10-google-engineering-culture.md) | Google 工程文化术语详解 | 案例 | Hyrum 定律、Beyonce 规则、Chesterton 栅栏、测试金字塔、左移、主干开发、DAMP 胜过 DRY、代码即负债 |

```{toctree}
:hidden:
:maxdepth: 2

00-skill-anatomy
01-progressive-disclosure
02-frontmatter-fields
03-authoring-principles
04-eval-driven-iteration
05-description-optimization
06-client-integration
07-skills-ref-reference-implementation
08-scripts-guide
09-osmani-agent-skills-practice
10-google-engineering-culture
```
