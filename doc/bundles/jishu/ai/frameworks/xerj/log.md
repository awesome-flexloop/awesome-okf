# 更新日志

## 2026-10-20（第二轮 · 官方文档站增量）

**新增信源**：XERJ 官方文档站 `https://xerj.org/docs/`（版本 v1.0.0-rc.97，46 页），以仓库内落地快照 `landing/docs/` 为事实来源，登记见 `references/docs-source.md`。

- **事实**：新增 156 条编号事实（F-207～F-362），分 7 组（K 查询与聚合 / L 摄取存储压缩集群 / M 配置环境安全 / N 运维备份升级排障 / O ES 兼容面与语义差异 / P 智能体表面与 Corpus Hub / Q 向量量化），每条标注页面与来源。
- **洞察**：新增 6 条（洞察 7～12），见 `references/insights-docs.md`：
  1. 配置文件里最危险的不是缺键，而是「接了线但没接线」；
  2. 集群模式今天给的是「选主环」，不是「数据副本」；
  3. 诚实被编码进了响应体，而不只是写进文档；
  4. 量化换的是精度，不是内存（#392）；
  5. 文档站的「每个页面都有源码指针」本身就是可追溯性设计；
  6. 文档的「诚实」与「漂移」共存，而漂移可被机械检出。
- **概念文档 5 篇**：`09-query-types-and-aggregations`（50 种查询 / 62 种聚合 / 2 种显式拒绝）、`10-analyzers-and-ingest`（4 分析器 / 4 摄取路径）、`11-storage-compression-clustering`（三文件段 / WAL 三档 / 9 列编码 / 集群四项「不提供」）、`12-config-and-environment`（24 段配置面 / 16 个未接线键 / 环境变量优先级）、`13-operations-and-troubleshooting`（systemd / 双探针 / 备份四式 / 六类症状）。
- **示例 1 篇**：`05-official-docs-map`（46 页导航地图、10 recipe + 5 playbook 选型、Corpus Hub 两条通道与许可证三档、四处漂移的复核清单）。
- **参考 3 篇**：`docs-source.md`（信源登记）、`facts-docs.md`（事实清单 + 交叉核验记录）、`insights-docs.md`（洞察）。
- **登记的第二轮文档漂移**（共四处，均已回源码核验并记录处置）：站点导航写「32 种查询」而正文与代码是 50 种；CLI 页写 `--config` 默认 `./xerj.toml` 而代码无此回退；迁移页写 1,371/1,374 而 README 徽章写 1,366/1,369；原生 API 页的 `_explain` 路径与迁移页的 `/v1/explain-plan` 不一致。
- **登记的两处覆盖面缺口**：文档键表只覆盖 12 个配置段而代码有 24 段、`xerj.default.toml` 交付 13 段，10 个键在 default toml 里却不在键表中；至少 16 个键被接受并校验但行为不变。
- 编号续接，既有 9 篇概念与 4 篇示例**未重写**（按多轮增量扩展规范：只追加，不重排、不改结论）。
- 索引变更：束内 `index.md` / `concepts/index.md` / `examples/index.md` / `references/index.md` 与 `log.md` 追加；**束数与分组计数不变**，父级索引无需调整。

## 2026-10-20（第一轮 · 源码与上游自述）

**新增**：XERJ 源码学习知识包首次入库（`jishu/ai/frameworks/xerj/`）。

- **信源**：仓库 `xerj-org/xerj`，commit `51ff219276d7e55d9d85b4938e8b94f235f9d099`（`git describe` = `v1.0.0-rc.97-38-g51ff2192`），采集时工作树无未提交改动。规模与各 crate 行数由脚本计数，路径稳定性判定见 `references/source.md`。
- **事实**：206 条编号事实（F-001～F-206），分 10 组（定位与规模 / crate 架构 / autoindex / MCP / 检索路径 / 向量与嵌入 / 记忆与第二大脑 / 兼容性与基准 / 参考编码 / 文档漂移），每条标注仓库相对路径与行号。
- **洞察**：6 条四元组洞察（ES 兼容是传输层 / `semantic` 是名字不是能力 / 机器可读面比人读面更新 / autoindex 是独立客户端 / 内容驱动识别 + 字段来源标记 / 参考编码受记忆门控），见 `references/insights.md`。
- **概念文档 9 篇**：`00-overview`、`01-getting-started`、`02-autoindex-pipeline`、`03-mcp-agent-surface`、`04-search-query-path`、`05-vector-and-hybrid`、`06-agent-memory-and-brain`、`07-es-compat-and-benchmarks`、`08-reference-coding`。
- **示例 4 篇**：`01-autoindex-to-query`、`02-mcp-integration`、`03-retrieval-mode-selection`、`04-migration-from-elasticsearch`。
- **登记的事实漂移**（已记入事实清单 J 组）：仓库 `AGENTS.md` 与 `README.md` 写「13 个 MCP 工具」，代码与已发布 schema 实际为 17 个；`README.md` 写「8 个检测器」，注册表实际 9 个；`docs/WHY_XERJ.md` 写「13 个格式族」，代码侧为 25 个抽取器模块 / 28 个 `Family` 变体。
- **索引变更**：`jishu/ai/frameworks/index.md` 新增本束行与 toctree 条目；`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md` 的递归束数与分组计数同步更新。
