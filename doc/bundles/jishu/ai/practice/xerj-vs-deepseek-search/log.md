# 更新日志

## 2026-10-20

**新增**：`jishu/ai/practice/xerj-vs-deepseek-search/` 束首次入库（12 个文件）。

- **主题**：XERJ 自建本地检索栈与 DeepSeek 托管搜索 API（Search / Fetch）的九轴对比。
- **事实**：42 条编号事实（F-001～F-042），分 X 组（XERJ 侧 15 条）、D 组（DeepSeek 侧 18 条）、C 组（对照 9 条）。DeepSeek 侧事实**逐条复核自在线官方文档**，XERJ 侧事实**跨束引用**既有 xerj 束的编号事实、不重复采集。
- **概念文档 5 篇**：`00-comparison-frame`（九轴框架与结论）、`01-corpus-ownership`（第一决策轴）、`02-context-cost-and-contracts`（上下文的两种控制法）、`03-failure-semantics-and-boundaries`（错误码作为契约）、`04-cost-model-and-selection`（成本曲线与决策树）。
- **示例 1 篇**：`01-composed-retrieval-pipeline`（组合检索回路实战）。
- **参考 3 篇**：`source.md`（信源登记 + 13 项复核表）、`facts.md`（事实清单）、`verification.md`（核验记录与引用纪律）。
- **核心结论**：两者不是竞品而是**语料两端**；「要检索的东西归谁」是第一决策轴；上下文成本控制是同一思想的两种实现；失败可诊断性存在实质差距（DeepSeek 的 404 合并五种成因）；成本曲线形状相反（固定 vs 线性惩罚重复）；可串联为「本地优先 → 公网兜底 → 固化回本地」的组合回路。
- **显式留白的边界**：F-033 与 F-040 标注为对照推论/架构建议，非任一方的官方立场；本束不含跨引擎同语料召回对比实验。
- **索引变更**：`jishu/ai/practice/index.md` 新增本束行与 toctree 条目（束数 22→23、目录数 20→21）；`doc/bundles/index.md` 计数同步（总束数 +1，jishu 束数 +1）。
