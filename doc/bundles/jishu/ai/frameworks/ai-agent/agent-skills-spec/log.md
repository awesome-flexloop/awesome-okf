# 变更日志（Changelog）

本文件记录 agent-skills-spec 知识束的版本变更。格式遵循语义化版本：主版本号对应结构或覆盖范围的重大变化，次版本号对应内容增补，修订号对应勘误。

## v1.1.0 (2026-09-02)

**Merge**: 从 SpecWeave docs/knowledge/learning/ 三源合并回填独有内容（learning→bundles 迁移重复对 #2：01-agent-protocols-interfaces/agent-skills-wiki 17 文件 + 02-agent-engineering-methodology/02-prompt-coding/agent-skills-wiki 10 文件 + 分类根散文件 agent-skills-open-standard-wiki.md）

* **Add**: concepts/08-scripts-guide.md —— 脚本使用指南（一次性命令版本固定、PEP 723/Deno/Bun/Ruby 自包含脚本、面向智能体设计六原则），源自 01 侧 06-scripts-guide.md，为既有 03 篇脚本工程附录的完整展开
* **Add**: concepts/09-osmani-agent-skills-practice.md —— Addy Osmani agent-skills 生产级技能库实践案例（六阶段生命周期、20 技能索引、7 斜杠命令、五大应用场景），整合自 02 侧 00/01/02/03/06 五章（02 侧同名主题为 Addy Osmani 技能库，与既有规范主题互补不重叠）
* **Add**: concepts/10-google-engineering-culture.md —— Google 工程文化 8 术语详解，源自 02 侧 04-google-engineering-culture.md
* **Add**: references/quick-reference.md —— 快速参考卡（SKILL.md 模板、验证命令、名称规则、检查清单），源自 01 侧 14-quick-reference.md
* **Add**: references/osmani-extended-resources.md —— 实践案例延伸学习资源，源自 02 侧 07-resources.md（剔除个人工作区指涉）
* **重复确认（01 侧 15 章逐章比对）**：00 概述≈根索引、01/02/03/05/07/08/09/12 章已被既有 8 篇概念+2 示例覆盖（既有内容以 68 条源码事实为基线更精确）、04 章与 examples/01 重叠、13 章与 references 重叠；10 章文件引用规范（相对路径+一层深度）已被 00-skill-anatomy「文件引用约定」节完整覆盖（F-014/F-022）；11 章「与本项目对比」为个人工作区语境，其 Unicode/i18n 技术发现已被既有 02-frontmatter-fields「i18n 差异点」（F-059/F-068）覆盖，均未重复迁入
* **重复确认（02 侧 8 章）**：05-specweave-comparison 为个人工作区对比分析，未迁入；index/README 为导航元数据，未迁入
* **重复确认（散文件）**：agent-skills-open-standard-wiki.md 为 01 侧原子化索引页（无独有正文），登记于此不迁入
* **Update**: 根 index.md、concepts/index.md、references/index.md 更新导航与 toctree（8→11 概念、2→4 参考）

## v1.0.0 (2026-08-29)

首次发布。经 source-code-to-okf-wiki 工作流三阶段生成：

- **R 阶段（事实采集）**：从 `external/libs/ai/agentskills/agentskills/` 仓库提取 68 条事实（F-001 ~ F-068），信源覆盖 docs/ 下 12 个规范/指南文件与 skills-ref/ 下 12 个源码/测试文件；产物为 `.trae/specs/agentskills-okf-wiki/facts.md`。
- **I 阶段（洞察与知识地图）**：产出 5 条核心洞察（description 路由函数、规范极小/生态承接、双校验两极、eval 治理姿态、最小完整闭环）与 concepts/examples/references 三层知识地图；产物为 `.trae/specs/agentskills-okf-wiki/insights.md`。
- **E 阶段（批量生成，本版本）**：按信源先行纪律分四批生成 17 个文件——先 references/ 信源登记表，再 concepts/ 8 篇（学习路径编号 00-07），再 examples/ 2 篇，最后索引与日志。

### 交付物

| 批次 | 文件 |
|---|---|
| 1（信源） | references/spec-sources.md、references/skills-ref-sources.md |
| 2（概念） | concepts/00-skill-anatomy ~ 07-skills-ref-reference-implementation 共 8 篇 |
| 3（示例） | examples/01-first-skill-roll-dice.md、examples/02-skills-ref-cli.md |
| 4（索引） | index.md、concepts/index.md、examples/index.md、references/index.md、log.md |

### 生成约束与自查记录

- 全部交叉链接使用 `/` 开头的 bundle-relative 路径，无 `../` 依赖；
- 每篇文档的 frontmatter 携带 `generated`（R→I→E 流程）与 `verified`（七概念核对流程）溯源字段，`sources` 指向 references/ 登记表；
- 被引用的 API（`validate`、`read_properties`、`to_prompt`、`find_skill_md`、`parse_frontmatter`、`validate_metadata`、`SkillProperties`、`ParseError`、`ValidationError`、CLI 三子命令、常量 `MAX_SKILL_NAME_LENGTH`/`MAX_DESCRIPTION_LENGTH`/`MAX_COMPATIBILITY_LENGTH`/`ALLOWED_FIELDS`）均已对照 skills-ref 源码逐一核实存在且签名一致；
- 未修改 `external/` 下任何文件。
