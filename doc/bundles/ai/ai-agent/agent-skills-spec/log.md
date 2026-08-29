# 变更日志（Changelog）

本文件记录 agent-skills-spec 知识束的版本变更。格式遵循语义化版本：主版本号对应结构或覆盖范围的重大变化，次版本号对应内容增补，修订号对应勘误。

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
