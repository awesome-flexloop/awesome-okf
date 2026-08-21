# Bundle Update Log

## 2026-08-21

* **Enrich**: 基于 okf.md 全站内容（主页 /spec /quickstart /validator /skill 子页面）与 GitHub SPEC.md 完整原文补充 bundle 细节。
* **Update**: references/okf-spec.md 从 19 行中文摘要升级为 39KB 完整英文 v0.2 规范原文（1006 行，含 §1–§13 与 Appendix A 损益表示例）。
* **Add**: references/okf-annotated-v01.md — v0.1 注释版开发者指南信源登记，记录 v0.1 注释版相对 v0.2 的增量内容映射表。
* **Add**: concepts/design-principles.md — 三大设计原则（最小意见化/生产者-消费者独立/格式而非平台）中文转译。
* **Add**: concepts/practical-guidance.md — 10 条实践指南（type 治理、扩展字段、自动化索引脚本、断链即特性、结构化 Markdown 对 RAG 的重要性、log.md vs git log、Obsidian 对比、引用机制演进、目录放置建议、三规则验证）。
* **Add**: concepts/tooling-validator.md — OKF Validator 在线工具介绍（功能、使用方式、验证范围、与 validate.sh 对比）。
* **Add**: concepts/tooling-agent-skill.md — OKF Agent Skill 介绍（支持智能体、一键安装、SKILL.md 作用、validate.sh、CI 集成、Quickstart 使用示例）。
* **Add**: concepts/tooling-knowledge-catalog.md — Google Knowledge Catalog CLI 介绍（仓库结构、CLI 命令、npm 包、生态工具总览表）。
* **Add**: examples/saas-metrics-quickstart.md — 5 分钟 Quickstart 教程完整中文转译，包含 MRR/Churn/CAC/LTV 四个 SaaS 指标概念文件全文与 index.md/log.md。
* **Update**: 根 index.md、concepts/index.md、examples/index.md、references/index.md 更新索引分组与统计数字（27 个内容文档 = 20 概念 + 4 示例 + 3 信源/进程登记）。
* **Review**: 登记稳定进程 `process:seven-concepts-v`（references/processes/seven-concepts-v.md）—— 对抗审查进程的定义与复核路径，使各文档 `verified.by` 的 machine-confirmed 可独立复核。
* **Verify**: 全部 18 个核心内容文档（15 概念 + 3 示例）与信源登记的 `verified` 指向登记进程，`verified.at` 更新为本次对抗审查核验时刻（2026-08-21）。审查结论：全 bundle 格式合规、链接无误、忠实转译，均 `status: stable`；`stale_after: 2027-12-31` 保留作为 SPEC 未来修订的保守重新评估节点（解释见 index.md）。新增 7 个文档标记为 `draft`，待后续独立复核。
* **Fix**: 18 个概念/示例的 `sources[].resource` 与 `[^okf-spec]` 脚注统一改为 bundle-relative 引用 `references/okf-spec.md`，实现脱离仓库的自包含分发（P2）。

## 2026-08-20

* **Creation**: 建立 bundle 脚手架（concepts/examples/references 三目录）与唯一信源登记（OKF SPEC v0.2）。
* **Add**: R+A 阶段完成——concepts/ 下 15 个规范概念（§1-§13 中文转译）与 examples/ 下 3 个示例概念。
* **Add**: V 阶段完成——交叉链接修复与最终一致性检查通过。